import io
import time

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="FRED - Portal Data Indonesia", layout="wide")
st.title("📈 Federal Reserve Economic Data (FRED) - Indonesia")
st.markdown(
    "Eksplorasi seri data ekonomi Indonesia dari **Federal Reserve Bank of St. Louis (FRED)** "
    "secara *real-time*. Seluruh hasil pencarian otomatis difilter khusus untuk seri yang berkaitan dengan **Indonesia**."
)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
BASE = "https://api.stlouisfed.org/fred"
MAX_RETRY = 3

# =============================================================================
# API KEY — dengan error handling ramah jika key tidak ada
# =============================================================================
try:
    FRED_API_KEY = st.secrets["FRED_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error(
        "⚠️ **FRED API Key tidak ditemukan.**\n\n"
        "Tambahkan `FRED_API_KEY` ke file `secrets.toml` atau Streamlit Cloud Secrets:\n"
        "```\nFRED_API_KEY = 'your_api_key_here'\n```\n"
        "Dapatkan API Key gratis di: https://fred.stlouisfed.org/docs/api/api_key.html"
    )
    st.stop()


# =============================================================================
# LAPISAN API
# =============================================================================
def aman(teks) -> str:
    """Pastikan kunci API tidak pernah tampil di halaman."""
    return str(teks).replace(FRED_API_KEY, "***")


def fred_get(path: str, **params) -> dict:
    """GET ke FRED dengan retry. Kunci dikirim lewat params, dan pesan error tidak pernah memuat URL."""
    p = {"api_key": FRED_API_KEY, "file_type": "json", **params}
    for percobaan in range(MAX_RETRY):
        terakhir = percobaan == MAX_RETRY - 1
        try:
            r = requests.get(f"{BASE}/{path}", params=p, headers=HEADERS, timeout=30)
        except requests.RequestException as e:
            if terakhir:
                raise RuntimeError(f"[Jaringan] {type(e).__name__}")
            time.sleep(2 * (percobaan + 1))
            continue
        if r.status_code == 429 or r.status_code >= 500:
            if terakhir:
                raise RuntimeError(f"[HTTP {r.status_code}] Server FRED menolak atau gagal merespons.")
            time.sleep(2 * (percobaan + 1))
            continue
        try:
            js = r.json()
        except ValueError:
            raise RuntimeError(f"[Format] HTTP {r.status_code}, respons bukan JSON.")
        if not isinstance(js, dict):
            raise RuntimeError("[Format] Bentuk respons tidak dikenali.")
        if "error_message" in js or r.status_code != 200:
            raise RuntimeError(
                f"[FRED {js.get('error_code', r.status_code)}] {aman(js.get('error_message', 'Permintaan ditolak.'))}"
            )
        return js


FIELD_SERI = [
    "id", "title", "frequency", "frequency_short", "units", "units_short",
    "seasonal_adjustment", "seasonal_adjustment_short", "observation_start",
    "observation_end", "last_updated", "notes", "popularity",
]


@st.cache_data(ttl=3600, show_spinner=False)
def cari_seri(teks: str) -> list:
    """Pencarian berhalaman (semua halaman). Dua jalur digabung berdasarkan ID seri:
    1) teks pencarian, divalidasi judul atau ID memuat 'indonesia';
    2) teks pencarian dengan tag 'indonesia' (menangkap seri yang judulnya tidak memuat kata itu).
    Gagal = exception (tidak ikut di-cache)."""
    hasil = {}
    for tag in (None, "indonesia"):
        offset = 0
        while True:
            prm = dict(search_text=teks, limit=1000, offset=offset, order_by="popularity", sort_order="desc")
            if tag:
                prm["tag_names"] = tag
            js = fred_get("series/search", **prm)
            bagian = js.get("seriess", [])
            total = int(js.get("count", 0))
            for s in bagian:
                if tag is None:
                    if "indonesia" not in f"{s.get('title', '')} {s.get('id', '')}".lower():
                        continue
                hasil.setdefault(s["id"], {k: s.get(k) for k in FIELD_SERI})
            offset += len(bagian)
            if not bagian or offset >= total:
                break
            time.sleep(0.5)
    return sorted(hasil.values(), key=lambda s: -int(s.get("popularity") or 0))


@st.cache_data(ttl=3600, show_spinner=False)
def tarik_observasi(series_id: str) -> list:
    """Semua observasi satu seri. Jumlah baris harus sama dengan count dari API, kalau tidak data ditolak."""
    semua, offset, total = [], 0, 0
    while True:
        js = fred_get("series/observations", series_id=series_id, limit=100000, offset=offset)
        bagian = js.get("observations", [])
        total = int(js.get("count", 0))
        semua.extend(bagian)
        offset += len(bagian)
        if not bagian or offset >= total:
            break
    if len(semua) != total:
        raise RuntimeError(
            f"Jumlah observasi terkumpul ({len(semua)}) tidak sama dengan count di API ({total}). Data ditolak."
        )
    return [{"date": o.get("date"), "value": o.get("value")} for o in semua]


# =============================================================================
# 1. PENCARIAN SERI — OTOMATIS FILTER INDONESIA
# =============================================================================
st.subheader("1. Pencarian Indikator FRED (Indonesia)")

col_search, col_hint = st.columns([2, 1])
with col_search:
    query_tambahan = st.text_input(
        "🔍 Tambahkan kata kunci topik (opsional):",
        placeholder="Contoh: exchange rate, inflation, interest rate, M2, GDP",
        value=""
    ).strip()

with col_hint:
    st.markdown("**Contoh topik yang tersedia:**")
    st.caption("exchange rate · inflation · interest rate · M2 · GDP · trade · bonds · rupiah")

# Gabungkan query: selalu sertakan "Indonesia" + kata kunci tambahan user
if query_tambahan:
    query_final = f"Indonesia {query_tambahan}"
else:
    query_final = "Indonesia"

try:
    with st.spinner(f"Mencari seri FRED untuk: '{query_final}'..."):
        seri_list = cari_seri(query_final)
except Exception as e:
    st.error(f"Gagal memuat katalog seri FRED: {aman(e)}")
    st.stop()

if not seri_list:
    st.warning(
        f"Tidak ditemukan seri FRED yang berkaitan dengan Indonesia untuk kata kunci **'{query_tambahan}'**.\n\n"
        "Coba kata kunci lain seperti: `exchange rate`, `inflation`, `interest rate`, `rupiah`, `trade`."
    )
    st.stop()

st.success(f"Ditemukan **{len(seri_list)}** seri data Indonesia di FRED.")
st.caption(
    "Termasuk seri yang dilaporkan pihak lain tentang Indonesia (misalnya statistik perdagangan, portofolio, "
    "dan paten AS). Pelapornya tertera di judul seri."
)

# =============================================================================
# 2. PEMILIHAN SERI
# =============================================================================
st.subheader("2. Pilih Seri Data")


def buat_label(s: dict) -> str:
    bagian = [
        s.get("title") or s["id"],
        f"Frekuensi: {s.get('frequency') or '-'}",
        f"Satuan: {s.get('units_short') or '-'}",
    ]
    if s.get("seasonal_adjustment_short"):
        bagian.append(s["seasonal_adjustment_short"])
    return " | ".join(bagian)


label_dasar = [buat_label(s) for s in seri_list]
jumlah_label = {}
for lb in label_dasar:
    jumlah_label[lb] = jumlah_label.get(lb, 0) + 1
# ID hanya ditambahkan pada label yang masih kembar, supaya tidak ada seri yang tertimpa
labels = [
    lb if jumlah_label[lb] == 1 else f"{lb} | {seri_list[i]['id']}"
    for i, lb in enumerate(label_dasar)
]

idx = st.selectbox("Pilih Seri Data FRED:", options=list(range(len(seri_list))), format_func=lambda i: labels[i])
selected_fred = seri_list[idx]
series_id = selected_fred["id"]

with st.expander("ℹ️ Detail Metadata & Sumber Resmi", expanded=False):
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown(f"**Judul Seri:** {selected_fred.get('title')}")
        st.markdown(f"**ID Seri:** `{series_id}`")
        st.markdown(f"**Frekuensi:** {selected_fred.get('frequency')}")
        st.markdown(f"**Satuan:** {selected_fred.get('units')}")
        st.markdown(f"**Penyesuaian Musiman:** {selected_fred.get('seasonal_adjustment') or '-'}")
    with col_m2:
        st.markdown(f"**Rentang Observasi:** {selected_fred.get('observation_start')} s.d. {selected_fred.get('observation_end')}")
        st.markdown(f"**Terakhir Diperbarui:** {selected_fred.get('last_updated') or '-'}")
        st.markdown(f"🔗 [Lihat di FRED](https://fred.stlouisfed.org/series/{series_id})")
    catatan = selected_fred.get('notes') or ''
    if catatan:
        st.markdown(f"**Catatan Metodologi:**\n{catatan}")

# =============================================================================
# 3. PENARIKAN DATA & OPSI RESAMPLE
# =============================================================================
st.subheader("3. Penarikan & Visualisasi Data")

frekuensi_asli = (selected_fred.get("frequency") or "").lower()
tampilkan_resample = any(f in frekuensi_asli for f in ["daily", "weekly", "harian", "mingguan", "business"])

# nama pilihan -> (aturan resample, keterangan di file, akhiran nama file)
AGREGASI = {
    "Bulanan (rata-rata)": ("ME", "Rata-rata bulanan", "bulanan"),
    "Kuartalan (rata-rata)": ("QE", "Rata-rata kuartalan", "kuartalan"),
    "Tahunan (rata-rata)": ("YE", "Rata-rata tahunan", "tahunan"),
}

col_opt1, col_opt2 = st.columns([1, 2])
with col_opt1:
    if tampilkan_resample:
        resample_pilihan = st.selectbox(
            "Agregasi Frekuensi:",
            ["Asli (tanpa agregasi)"] + list(AGREGASI.keys())
        )
    else:
        resample_pilihan = "Asli (tanpa agregasi)"
        st.caption(f"Frekuensi data: **{selected_fred.get('frequency', '-')}**")

if st.button("📊 Ambil Data FRED", type="primary"):
    with st.spinner(f"Mengambil seluruh observasi untuk '{selected_fred['title']}'..."):
        try:
            raw_obs = tarik_observasi(series_id)

            records_fred, kosong = [], 0
            for row in raw_obs:
                try:
                    records_fred.append({"Tanggal": row["date"], "Nilai": float(row["value"])})
                except (ValueError, TypeError, KeyError):
                    # Nilai "." berarti kosong di FRED; dihitung, tidak diubah menjadi angka
                    kosong += 1

            if not records_fred:
                st.warning("Data observasi tidak ditemukan atau seluruh nilai kosong untuk seri ini.")
                st.stop()

            df_fred = pd.DataFrame(records_fred)
            df_fred["Tanggal"] = pd.to_datetime(df_fred["Tanggal"])
            df_fred = df_fred.sort_values(by="Tanggal", ascending=True).reset_index(drop=True)

            # Agregasi hanya bila dipilih pengguna; tanpa pembulatan, dengan jumlah observasi per periode
            if resample_pilihan in AGREGASI:
                aturan, ket_agregasi, akhiran = AGREGASI[resample_pilihan]
                g = df_fred.set_index("Tanggal")["Nilai"].resample(aturan).agg(["mean", "count"])
                df_fred = (
                    g.rename(columns={"mean": "Nilai", "count": "Jumlah Observasi Periode"})
                    .reset_index()
                )
            else:
                ket_agregasi, akhiran = "Tanpa agregasi (data asli)", None

            df_fred["Agregasi"] = ket_agregasi
            df_fred["ID Seri"] = series_id
            df_fred["Judul Seri"] = selected_fred["title"]
            df_fred["Satuan"] = selected_fred.get("units")
            df_fred["Frekuensi Asli"] = selected_fred.get("frequency")

            satuan = selected_fred.get("units_short") or "Nilai"
            judul_seri = selected_fred["title"]
            nama_berkas = f"{series_id}_fred" + (f"_{akhiran}" if akhiran else "")

            st.success(f"Berhasil memuat **{len(df_fred)}** observasi dari FRED!")
            if kosong:
                st.caption(f"{kosong} observasi bernilai kosong di FRED (tanda '.') tidak ditampilkan.")
            st.divider()

            # Link resmi
            st.markdown(f"🔗 **Halaman Resmi FRED:** [{judul_seri}](https://fred.stlouisfed.org/series/{series_id})")

            # Tombol Download
            cf1, cf2 = st.columns(2)
            cf1.download_button(
                "📥 Unduh CSV",
                df_fred.to_csv(index=False).encode("utf-8"),
                f"{nama_berkas}.csv",
                "text/csv",
                on_click="ignore"
            )
            buf_fred = io.BytesIO()
            with pd.ExcelWriter(buf_fred, engine="openpyxl") as writer:
                df_fred.to_excel(writer, index=False, sheet_name="FRED Data")
            cf2.download_button(
                "📊 Unduh Excel (.xlsx)",
                buf_fred.getvalue(),
                f"{nama_berkas}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                on_click="ignore"
            )

            # Plotly Interaktif
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_fred["Tanggal"],
                y=df_fred["Nilai"],
                mode="lines+markers",
                name=judul_seri,
                line=dict(width=2.5, color="#1f77b4"),
                marker=dict(size=5),
                hovertemplate=f"%{{x|%d %b %Y}}<br>Nilai: %{{y:,}} {satuan}<extra></extra>"
            ))
            fig.update_layout(
                xaxis=dict(title="Tanggal", type="date"),
                yaxis=dict(title=satuan),
                hovermode="x unified",
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("📋 Tabel Data Lengkap"):
                tabel = df_fred.sort_values(by="Tanggal", ascending=False)
                tampil = pd.DataFrame({
                    "Tanggal": tabel["Tanggal"].dt.strftime("%Y-%m-%d"),
                    "Nilai": tabel["Nilai"].map(lambda v: "(kosong)" if pd.isna(v) else repr(float(v))),
                })
                if "Jumlah Observasi Periode" in tabel.columns:
                    tampil["Jumlah Observasi Periode"] = tabel["Jumlah Observasi Periode"]
                st.dataframe(tampil, use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Gagal mengambil data dari server FRED: {aman(e)}")
