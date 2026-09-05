import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import io

st.set_page_config(page_title="FRED - Portal Data Indonesia", layout="wide")
st.title("📈 Federal Reserve Economic Data (FRED) - Indonesia")
st.markdown(
    "Eksplorasi seri data ekonomi Indonesia dari **Federal Reserve Bank of St. Louis (FRED)** "
    "secara *real-time*. Seluruh hasil pencarian otomatis difilter khusus untuk seri yang berkaitan dengan **Indonesia**."
)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

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
# 1. PENCARIAN SERI — OTOMATIS FILTER INDONESIA
# =============================================================================
st.subheader("1. Pencarian Indikator FRED (Indonesia)")

INDONESIA_KEYWORDS = ["indonesia"]

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

@st.cache_data(ttl=3600, show_spinner=False)
def search_fred(query: str, api_key: str):
    search_url = (
        f"https://api.stlouisfed.org/fred/series/search"
        f"?search_text={query}&api_key={api_key}&file_type=json&limit=100"
        f"&order_by=popularity&sort_order=desc"
    )
    try:
        res = requests.get(search_url, headers=HEADERS, timeout=15)
        data = res.json()
        seri_all = data.get("seriess", [])
        # Filter ketat: hanya tampilkan seri yang title/id-nya mengandung "indonesia" (case-insensitive)
        seri_filtered = [
            s for s in seri_all
            if any(kw in s.get("title", "").lower() or kw in s.get("id", "").lower() for kw in INDONESIA_KEYWORDS)
        ]
        return seri_filtered, None
    except Exception as e:
        return [], str(e)

with st.spinner(f"Mencari seri FRED untuk: '{query_final}'..."):
    seri_list, err = search_fred(query_final, FRED_API_KEY)

if err:
    st.error(f"Gagal terhubung ke server FRED: {err}")
    st.stop()

if not seri_list:
    st.warning(
        f"Tidak ditemukan seri FRED yang berkaitan dengan Indonesia untuk kata kunci **'{query_tambahan}'**.\n\n"
        "Coba kata kunci lain seperti: `exchange rate`, `inflation`, `interest rate`, `rupiah`, `trade`."
    )
    st.stop()

st.success(f"Ditemukan **{len(seri_list)}** seri data Indonesia di FRED.")

# =============================================================================
# 2. PEMILIHAN SERI
# =============================================================================
st.subheader("2. Pilih Seri Data")

fred_options = {
    f"{s['title']} | Frekuensi: {s.get('frequency', '-')} | Satuan: {s.get('units_short', '-')} | ({s['id']})": s
    for s in seri_list
}

selected_fred_label = st.selectbox("Pilih Seri Data FRED:", list(fred_options.keys()))
selected_fred = fred_options[selected_fred_label]
series_id = selected_fred["id"]

with st.expander("ℹ️ Detail Metadata & Sumber Resmi", expanded=False):
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown(f"**Judul Seri:** {selected_fred.get('title')}")
        st.markdown(f"**ID Seri:** `{series_id}`")
        st.markdown(f"**Frekuensi:** {selected_fred.get('frequency')}")
        st.markdown(f"**Satuan:** {selected_fred.get('units')}")
    with col_m2:
        st.markdown(f"**Rentang Observasi:** {selected_fred.get('observation_start')} s.d. {selected_fred.get('observation_end')}")
        st.markdown(f"**Terakhir Diperbarui:** {selected_fred.get('last_updated', '-')}")
        st.markdown(f"🔗 [Lihat di FRED](https://fred.stlouisfed.org/series/{series_id})")
    catatan = selected_fred.get('notes', '')
    if catatan:
        st.markdown(f"**Catatan Metodologi:**\n{catatan}")

# =============================================================================
# 3. PENARIKAN DATA & OPSI RESAMPLE
# =============================================================================
st.subheader("3. Penarikan & Visualisasi Data")

frekuensi_asli = selected_fred.get("frequency", "").lower()
tampilkan_resample = any(f in frekuensi_asli for f in ["daily", "weekly", "harian", "mingguan", "business"])

col_opt1, col_opt2 = st.columns([1, 2])
with col_opt1:
    if tampilkan_resample:
        resample_pilihan = st.selectbox(
            "Agregasi Frekuensi:",
            ["Asli (tanpa agregasi)", "Bulanan (rata-rata)", "Kuartalan (rata-rata)", "Tahunan (rata-rata)"]
        )
    else:
        resample_pilihan = "Asli (tanpa agregasi)"
        st.caption(f"Frekuensi data: **{selected_fred.get('frequency', '-')}**")

if st.button("📊 Ambil Data FRED", type="primary"):
    with st.spinner(f"Mengambil seluruh observasi untuk '{selected_fred['title']}'..."):
        obs_url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
        )
        try:
            r_obs = requests.get(obs_url, headers=HEADERS, timeout=20)
            obs_json = r_obs.json()

            if "error_message" in obs_json:
                st.error(f"FRED API Error: {obs_json['error_message']}")
                st.stop()

            raw_obs = obs_json.get("observations", [])

            records_fred = []
            for row in raw_obs:
                tgl = row.get("date")
                val_str = row.get("value")
                try:
                    records_fred.append({"Tanggal": tgl, "Nilai": float(val_str)})
                except (ValueError, TypeError):
                    # Skip nilai "." yang berarti missing di FRED
                    continue

            if not records_fred:
                st.warning("Data observasi tidak ditemukan atau seluruh nilai kosong untuk seri ini.")
                st.stop()

            df_fred = pd.DataFrame(records_fred)
            df_fred["Tanggal"] = pd.to_datetime(df_fred["Tanggal"])
            df_fred = df_fred.sort_values(by="Tanggal", ascending=True).reset_index(drop=True)

            # Resample jika dipilih
            if resample_pilihan == "Bulanan (rata-rata)":
                df_fred = df_fred.set_index("Tanggal").resample("ME").mean().round(4).reset_index()
            elif resample_pilihan == "Kuartalan (rata-rata)":
                df_fred = df_fred.set_index("Tanggal").resample("QE").mean().round(4).reset_index()
            elif resample_pilihan == "Tahunan (rata-rata)":
                df_fred = df_fred.set_index("Tanggal").resample("YE").mean().round(4).reset_index()

            satuan = selected_fred.get("units_short", "Nilai")
            judul_seri = selected_fred["title"]

            st.success(f"Berhasil memuat **{len(df_fred)}** observasi dari FRED!")
            st.divider()

            # Link resmi
            st.markdown(f"🔗 **Halaman Resmi FRED:** [{judul_seri}](https://fred.stlouisfed.org/series/{series_id})")

            # Tombol Download
            cf1, cf2 = st.columns(2)
            cf1.download_button(
                "📥 Unduh CSV",
                df_fred.to_csv(index=False).encode("utf-8"),
                f"{series_id}_fred.csv",
                "text/csv"
            )
            buf_fred = io.BytesIO()
            with pd.ExcelWriter(buf_fred, engine="openpyxl") as writer:
                df_fred.to_excel(writer, index=False, sheet_name="FRED Data")
            cf2.download_button(
                "📊 Unduh Excel (.xlsx)",
                buf_fred.getvalue(),
                f"{series_id}_fred.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
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
                hovertemplate=f"%{{x|%d %b %Y}}<br>Nilai: %{{y:,.4f}} {satuan}<extra></extra>"
            ))
            fig.update_layout(
                xaxis=dict(title="Tanggal", rangeslider=dict(visible=True), type="date"),
                yaxis=dict(title=satuan),
                hovermode="x unified",
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("📋 Tabel Data Lengkap"):
                st.dataframe(
                    df_fred.sort_values(by="Tanggal", ascending=False),
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Gagal mengambil data dari server FRED: {e}")
