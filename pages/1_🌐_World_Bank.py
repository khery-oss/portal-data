import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="World Bank Data Explorer - Indonesia", layout="wide")

st.title("🌐 World Bank Open Data Explorer - Indonesia")
st.write(
    "Eksplorasi ribuan indikator resmi **World Bank (World Development Indicators)** "
    "khusus untuk Indonesia secara otomatis dan real-time."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# =============================================================================
# 1. LOAD KATALOG INDIKATOR — 100% LIVE DARI WDI API
# =============================================================================
@st.cache_data(ttl=86400, show_spinner=False)
def load_all_indicators():
    """Katalog WDI live. Gagal = exception (tidak ikut di-cache), bukan daftar kosong."""
    base = "https://api.worldbank.org/v2/indicator?source=2&format=json&per_page=3000"
    res = requests.get(base, headers=HEADERS, timeout=25)
    if res.status_code != 200:
        raise RuntimeError(f"HTTP {res.status_code} dari server World Bank.")
    data = res.json()
    if not isinstance(data, list) or len(data) < 2 or not data[1]:
        raise RuntimeError("Respons katalog kosong atau bentuknya tidak dikenali.")
    items = list(data[1])
    for halaman in range(2, int(data[0].get("pages", 1)) + 1):
        rp = requests.get(f"{base}&page={halaman}", headers=HEADERS, timeout=25)
        if rp.status_code != 200:
            raise RuntimeError(f"HTTP {rp.status_code} pada halaman {halaman} katalog.")
        items.extend(rp.json()[1] or [])
    indicators = []
    for item in items:
        ind_id = item.get("id")
        ind_name = item.get("name")
        if ind_id and ind_name:
            indicators.append({
                "id": ind_id,
                "name": ind_name,
                "sourceNote": item.get("sourceNote", ""),
                "sourceOrg": item.get("sourceOrganization", "World Bank")
            })
    return indicators

try:
    with st.spinner("Menghubungkan ke katalog World Development Indicators..."):
        all_indicators = load_all_indicators()
except Exception as e:
    st.error(f"Gagal memuat katalog indikator: {e}")
    st.stop()

# =============================================================================
# 2. PENCARIAN BEBAS
# =============================================================================
st.subheader("1. Pencarian Indikator")

# Keyword preset per topik
TOPIC_PRESETS = {
    "— Pilih Topik Cepat (opsional) —": "",
    # Makroekonomi
    "💰 GDP & Pertumbuhan Ekonomi": "gdp growth",
    "📉 Inflasi & Harga": "inflation",
    "🏦 Keuangan & Perbankan": "credit bank interest",
    "💸 Perdagangan & Ekspor": "export import trade",
    "📊 Kemiskinan & Ketimpangan": "poverty gini",
    "💼 Fiskal & Utang": "tax revenue debt",
    "🏙️ Urbanisasi & Populasi": "urban population",
    "🔬 Teknologi & Inovasi": "technology research",
    # ILO — Ketenagakerjaan
    "👷 Pengangguran (ILO)": "unemployment",
    "💼 Angkatan Kerja (ILO)": "labor force participation",
    "🏭 Penyerapan Kerja (ILO)": "employment",
    "⚠️ Pekerja Rentan (ILO)": "vulnerable employment",
    "📦 Sektor Kerja (ILO)": "employment agriculture industry services",
    # UNESCO — Pendidikan
    "📚 Partisipasi Sekolah (UNESCO)": "school enrollment",
    "✏️ Literasi & Melek Huruf (UNESCO)": "literacy",
    "👩‍🏫 Rasio Murid-Guru (UNESCO)": "pupil teacher",
    "💰 Anggaran Pendidikan (UNESCO)": "education expenditure",
    "🎓 Kelulusan & Putus Sekolah (UNESCO)": "completion dropout",
    # Kesehatan & Lingkungan
    "🏥 Kesehatan": "mortality health",
    "⚡ Energi": "energy electricity",
    "🌿 Iklim & Lingkungan": "co2 emission forest",
    "👩 Gender": "female gender women",
}

col_preset, col_search = st.columns([1, 2])

with col_preset:
    preset = st.selectbox("⚡ Topik Cepat:", list(TOPIC_PRESETS.keys()))

with col_search:
    query = st.text_input(
        "🔍 Atau ketik kata kunci (bisa diedit):",
        value=TOPIC_PRESETS[preset],
        placeholder="Contoh: gdp · inflation · poverty · unemployment · export · debt · co2 · forest",
    ).strip()

if not query:
    st.info("Ketik kata kunci untuk mulai mencari indikator. Contoh: **gdp**, **inflation**, **poverty**, **unemployment**, **export**, **debt**.")
    st.stop()

query_tokens = query.lower().split()
results = [
    ind for ind in all_indicators
    if any(
        token in ind["name"].lower() or token in ind["id"].lower()
        for token in query_tokens
    )
]
results = sorted(results, key=lambda x: (len(x["name"]), x["name"]))

if not results:
    st.warning(f"Tidak ditemukan indikator untuk kata kunci **'{query}'**. Coba kata kunci lain.")
    st.stop()

st.success(f"Ditemukan **{len(results)}** indikator untuk kata kunci **'{query}'**.")

# =============================================================================
# 3. PILIH INDIKATOR
# =============================================================================
selected_ind = st.selectbox(
    "Pilih Indikator:",
    options=results,
    format_func=lambda item: item["name"]
)

kode_indikator = selected_ind["id"]
link_resmi = f"https://data.worldbank.org/indicator/{kode_indikator}?locations=ID"

with st.expander("ℹ️ Definisi & Metodologi Resmi", expanded=False):
    st.markdown(f"**Kode Indikator:** `{kode_indikator}`")
    st.markdown(f"**Organisasi Sumber:** {selected_ind['sourceOrg']}")
    note = selected_ind.get("sourceNote", "")
    st.markdown(f"**Definisi:** {note if note else 'Tidak ada deskripsi rinci.'}")
    st.markdown(f"🔗 [Lihat di World Bank]({link_resmi})")

def tarik_data_idn(kode: str):
    """Semua halaman data Indonesia untuk satu indikator. Mengembalikan (meta, items).
    Error API, jumlah baris tidak lengkap, atau baris negara lain ditolak dengan exception."""
    url = f"https://api.worldbank.org/v2/country/IDN/indicator/{kode}?format=json&per_page=1000"
    r = requests.get(url, headers=HEADERS, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} dari server World Bank.")
    payload = r.json()
    if not isinstance(payload, list) or not payload or not isinstance(payload[0], dict):
        raise RuntimeError("Bentuk respons tidak dikenali.")
    meta = payload[0]
    if "message" in meta:
        pesan = meta["message"]
        if isinstance(pesan, list):
            pesan = "; ".join(str(m.get("value", m)) if isinstance(m, dict) else str(m) for m in pesan)
        raise RuntimeError(f"API World Bank menolak permintaan: {pesan}")
    items = list(payload[1] or []) if len(payload) > 1 else []
    for halaman in range(2, int(meta.get("pages", 1)) + 1):
        rp = requests.get(f"{url}&page={halaman}", headers=HEADERS, timeout=20)
        if rp.status_code != 200:
            raise RuntimeError(f"HTTP {rp.status_code} pada halaman {halaman}.")
        pj = rp.json()
        items.extend((pj[1] if len(pj) > 1 else None) or [])
    total = meta.get("total")
    if total is not None and len(items) != int(total):
        raise RuntimeError(
            f"Jumlah baris terkumpul ({len(items)}) tidak sama dengan total di API ({total}). Data ditolak."
        )
    for it in items:
        iso = it.get("countryiso3code")
        if iso and iso != "IDN":
            raise RuntimeError(f"Baris negara {iso} muncul pada penarikan Indonesia. Data ditolak.")
    return meta, items

# =============================================================================
# 4. PENARIKAN DATA INDONESIA — 100% LIVE
# =============================================================================
st.subheader("2. Penarikan Data Indonesia")

if st.button("📊 Ambil Data Indonesia", type="primary"):
    with st.spinner(f"Mengunduh data untuk '{selected_ind['name']}'..."):
        try:
            meta_resp, items_api = tarik_data_idn(kode_indikator)
            records = []

            for item in items_api:
                thn = item.get("date")
                val = item.get("value")
                if thn is not None and val is not None:
                    try:
                        records.append({
                            "Tahun": int(thn),
                            "nilai_raw": float(val)
                        })
                    except (ValueError, TypeError):
                        continue

            if not records:
                st.warning(
                    f"Indikator **'{selected_ind['name']}'** terdaftar di World Bank "
                    "namun data untuk Indonesia belum tersedia. Silakan pilih indikator lain."
                )
                st.stop()

            # Satuan mengikuti nama indikator resmi World Bank (tanpa tebakan)
            val_col = "Nilai"
            df = (
                pd.DataFrame(records)
                .rename(columns={"nilai_raw": val_col})
                .sort_values(by="Tahun", ascending=True)
                .reset_index(drop=True)
            )
            df["Indikator"] = selected_ind["name"]
            df["Kode Indikator"] = kode_indikator
            df["Organisasi Sumber"] = selected_ind["sourceOrg"]
            if meta_resp.get("lastupdated"):
                df["Pembaruan WDI"] = meta_resp["lastupdated"]

            if df["Tahun"].duplicated().any():
                st.warning(
                    "Ada lebih dari satu nilai untuk tahun yang sama. Semua baris ditampilkan apa adanya, "
                    "tanpa diratakan."
                )

            st.success(f"Berhasil menarik **{len(df)}** observasi tahunan untuk Indonesia!")
            st.divider()

            st.markdown(f"🔗 **Halaman Resmi World Bank:** [{selected_ind['name']}]({link_resmi})")

            # Tombol Download
            col1, col2 = st.columns(2)
            col1.download_button(
                "📥 Unduh CSV",
                df.to_csv(index=False).encode("utf-8"),
                f"{kode_indikator}_indonesia.csv",
                "text/csv",
                on_click="ignore"
            )
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="World Bank Data")
            col2.download_button(
                "📊 Unduh Excel (.xlsx)",
                buffer.getvalue(),
                f"{kode_indikator}_indonesia.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                on_click="ignore"
            )

            # Visualisasi Plotly
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["Tahun"],
                y=df[val_col],
                mode="lines+markers",
                name="Indonesia (World Bank)",
                line=dict(width=2.5, color="#009688"),
                marker=dict(size=7),
                hovertemplate="Tahun %{x}<br>Nilai: %{y:,}<extra></extra>"
            ))
            fig.update_layout(
                xaxis=dict(title="Tahun", tickmode="linear"),
                yaxis=dict(title=selected_ind["name"]),
                hovermode="x unified",
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("📋 Tabel Angka Lengkap"):
                tabel = df.sort_values(by="Tahun", ascending=False)
                st.dataframe(
                    pd.DataFrame({
                        "Tahun": tabel["Tahun"],
                        "Nilai": tabel[val_col].map(lambda v: repr(float(v))),
                    }),
                    use_container_width=True,
                    hide_index=True
                )

        except Exception as e:
            st.error(f"Gagal mengambil data dari server World Bank: {e}")
