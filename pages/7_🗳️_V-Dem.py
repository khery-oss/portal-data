import io
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="V-Dem Explorer - IndoEcon", layout="wide")

st.title("🗳️ V-Dem (Varieties of Democracy) - Institusi & Demokrasi")
st.markdown(
    "Eksplorasi indeks kualitas demokrasi, tata kelola pemerintahan, korupsi, dan institusi politik Indonesia "
    "berbasis basis data resmi **V-Dem Institute** yang disinkronkan langsung dengan *Codebook* penjelas."
)

# =============================================================================
# 1. MEMUAT DATASET V-DEM & CODEBOOK LOKAL SECARA EFISIEN
# =============================================================================
@st.cache_data(show_spinner=False)
def load_vdem_data():
    try:
        # Sesuaikan nama file CSV dataset V-Dem kamu di direktori proyek
        df = pd.read_csv("vdem_data.csv", low_memory=False)
        return df
    except Exception:
        return None

@st.cache_data(show_spinner=False)
def load_codebook():
    try:
        # Sesuaikan nama file CSV codebook V-Dem kamu di direktori proyek
        df_cb = pd.read_csv("vdem_codebook.csv")
        return df_cb
    except Exception:
        return None

with st.spinner("Memuat basis data V-Dem dan menyelaraskan dengan Codebook..."):
    df_vdem = load_vdem_data()
    df_codebook = load_codebook()

# Fallback jika file lokal belum diunggah ke folder repository
if df_vdem is None:
    st.error(
        "⚠️ File dataset V-Dem (`vdem_data.csv`) belum ditemukan di direktori repository GitHub kamu.\n\n"
        "**Cara Memperbaiki:**\n"
        "1. Unduh dataset V-Dem versi CSV dari situs resmi V-Dem.\n"
        "2. Unggah file tersebut dengan nama `vdem_data.csv` dan file codebook-nya sebagai `vdem_codebook.csv` ke dalam folder utama repository Streamlit Cloud kamu."
    )
    st.stop()

# Filter khusus untuk wilayah Indonesia (IDN atau Country Text ID)
col_country = "country_text_id" if "country_text_id" in df_vdem.columns else ("country_name" if "country_name" in df_vdem.columns else None)
if col_country:
    df_idn = df_vdem[df_vdem[col_country].isin(["IDN", "Indonesia"])]
else:
    df_idn = df_vdem.head(0)

if df_idn.empty:
    st.warning("Data untuk wilayah Indonesia tidak ditemukan di dalam berkas CSV yang diunggah.")
    st.stop()

# =============================================================================
# 2. SINKRONISASI VARIABEL DENGAN CODEBOOK
# =============================================================================
# Mendapatkan daftar kolom numerik/indikator yang tersedia
exclude_cols = ["country_name", "country_text_id", "country_id", "year", "historical_date", "codingstart", "codingend", "gapstart", "gapend"]
available_indicators = [c for c in df_idn.columns if c not in exclude_cols and pd.api.types.is_numeric_dtype(df_idn[c])]

# Buat kamus penjelasan dari Codebook jika tersedia, jika tidak gunakan nama kolom
codebook_dict = {}
if df_codebook is not None and "variable" in df_codebook.columns and "description" in df_codebook.columns:
    for _, row in df_codebook.iterrows():
        codebook_dict[str(row["variable"])] = str(row["description"])

st.subheader("1. Pemilihan Indikator & Sinkronisasi Codebook")

search_term = st.text_input("🔍 Cari Indikator V-Dem (ketik kata kunci, misal: libdem, corruption, freedom, rule):", "")

filtered_indicators = [
    ind for ind in available_indicators
    if not search_term.strip() or search_term.lower() in ind.lower() or search_term.lower() in codebook_dict.get(ind, "").lower()
]

if not filtered_indicators:
    st.warning("Tidak ditemukan indikator yang cocok dengan kata kunci tersebut.")
    st.stop()

selected_indicator = st.selectbox(
    f"Pilih dari {len(filtered_indicators)} Indikator Tersedia:",
    filtered_indicators
)

# Ambil deskripsi langsung dari codebook yang disinkronkan
indicator_description = codebook_dict.get(selected_indicator, "Penjelasan rinci untuk variabel ini dapat merujuk langsung pada dokumen Codebook V-Dem resmi.")

with st.expander("📖 Penjelasan & Metadata dari Codebook V-Dem", expanded=True):
    st.markdown(f"**Nama Variabel (Kode):** `{selected_indicator}`")
    st.markdown(f"**Definisi / Deskripsi dari Codebook:**\n> {indicator_description}")
    st.markdown("🔗 **Sumber Dokumen:** [V-Dem Codebook & Methodology](https://www.v-dem.net/data/reference-documents/)")

# =============================================================================
# 3. PENARIKAN & VISUALISASI RUNTUN WAKTU INDONESIA
# =============================================================================
st.subheader("2. Visualisasi Runtun Waktu Historis Indonesia")

# Ambil data tahun dan nilai indikator terpilih tanpa batasan tahun
df_plot = df_idn[["year", selected_indicator]].dropna().sort_values(by="year", ascending=True)
df_plot = df_plot.rename(columns={"year": "Tahun", selected_indicator: "Nilai Skor"})

if not df_plot.empty:
    st.success(f"Berhasil memuat {len(df_plot)} observasi runtun waktu historis untuk Indonesia!")
    st.divider()

    # Tombol Unduh Berkas
    c1, c2 = st.columns(2)
    c1.download_button(
        "📥 Unduh CSV",
        df_plot.to_csv(index=False).encode("utf-8"),
        f"VDem_Indonesia_{selected_indicator}.csv",
        "text/csv"
    )
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df_plot.to_excel(writer, index=False, sheet_name="V-Dem Indonesia")
    c2.download_button(
        "📊 Unduh Excel (.xlsx)",
        buf.getvalue(),
        f"VDem_Indonesia_{selected_indicator}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Plotly Interaktif Tanpa Batas Waktu
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_plot["Tahun"],
        y=df_plot["Nilai Skor"],
        mode="lines+markers",
        name=f"Indonesia ({selected_indicator})",
        line=dict(width=2.8, color="#8B0000"),
        marker=dict(size=7),
        hovertemplate="Tahun %{x}<br>Skor: %{y:,.4f}<extra></extra>"
    ))
    fig.update_layout(
        xaxis=dict(title="Tahun", tickmode="linear"),
        yaxis=dict(title="Nilai Skor Indikator"),
        hovermode="x unified",
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📋 Tabel Runtun Waktu Lengkap"):
        st.dataframe(df_plot.sort_values(by="Tahun", ascending=False), use_container_width=True)
else:
    st.warning("Data observasi untuk indikator ini belum tersedia dalam berkas untuk wilayah Indonesia.")
