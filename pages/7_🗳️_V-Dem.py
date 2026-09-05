import io
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="V-Dem Explorer - IndoEcon", layout="wide")

st.title("🗳️ V-Dem (Varieties of Democracy) - Institusi & Demokrasi")
st.markdown(
    "Eksplorasi mendalam indeks kualitas demokrasi, tata kelola pemerintahan, korupsi, dan institusi politik Indonesia "
    "berbasis basis data resmi **V-Dem Institute** yang disinkronkan langsung dengan *Codebook* penjelas."
)

# =============================================================================
# 1. MEMUAT DATASET V-DEM & CODEBOOK
# =============================================================================
@st.cache_data(show_spinner=True)
def load_vdem_data():
    try:
        df_idn = pd.read_csv("vdem_data_IDN.csv", low_memory=False)
        return df_idn
    except Exception as e:
        st.error(f"Gagal membaca file `vdem_data_IDN.csv`: {e}")
        return None

@st.cache_data(show_spinner=False)
def load_codebook():
    try:
        df_cb = pd.read_csv("vdem_codebook.csv")
        df_cb.columns = df_cb.columns.str.strip().str.lower()
        return df_cb
    except Exception:
        return None

with st.spinner("Memuat basis data V-Dem dan menyelaraskan dengan Codebook..."):
    df_idn = load_vdem_data()
    df_codebook = load_codebook()

if df_idn is None or df_idn.empty:
    st.error(
        "⚠️ File dataset V-Dem (`vdem_data_IDN.csv`) tidak ditemukan atau data Indonesia tidak terdeteksi.\n\n"
        "Pastikan file tersebut sudah diunggah ke root folder repository GitHub kamu."
    )
    st.stop()

# Buat kamus penjelasan dari Codebook secara fleksibel
codebook_dict = {}
if df_codebook is not None:
    col_var = next((c for c in df_codebook.columns if 'var' in c), None)
    col_desc = next((c for c in df_codebook.columns if 'desc' in c or 'def' in c), None)
    
    if col_var and col_desc:
        for _, row in df_codebook.iterrows():
            codebook_dict[str(row[col_var]).strip()] = str(row[col_desc]).strip()

# =============================================================================
# 2. PEMILIHAN INDIKATOR (UTAMA vs PENCARIAN BEBAS)
# =============================================================================
st.subheader("1. Pemilihan Indikator V-Dem & Sinkronisasi Codebook")

# Daftar Indikator Utama / Kurasi Pilihan Peneliti
CURATED_VDEM = {
    "Indeks Demokrasi Liberal (Liberal Democracy Index)": "v2x_libdem",
    "Indeks Demokrasi Elektoral (Electoral Democracy Index)": "v2x_polyarchy",
    "Indeks Demokrasi Partisipatif (Participatory Democracy Index)": "v2x_partipdem",
    "Indeks Demokrasi Deliberatif (Deliberative Democracy Index)": "v2x_delibdem",
    "Indeks Demokrasi Egaliter (Egalitarian Democracy Index)": "v2x_egaldem",
    "Indeks Korupsi Publik (Public Sector Corruption Index)": "v2excrptps",
    "Indeks Korupsi Eksekutif (Executive Corruption Index)": "v2exorrpt",
    "Indeks Kebebasan Pers & Alternatif Informasi (Freedom of Expression)": "v2x_freexp",
    "Indeks Kebebasan Berorganisasi (Freedom of Association)": "v2x_frassoc_thick",
    "Indeks Supremasi Hukum (Rule of Law Index)": "v2x_rule",
    "Indeks Akuntabilitas Publik Vertikal (Vertical Accountability)": "v2x_veracc"
}

mode_pilihan = st.radio(
    "Pilih Metode Pencarian Indikator:",
    ["⭐ Indikator Utama (Kurasi Cepat)", "🔍 Eksplorasi Penuh (Semua Variabel Database)"],
    horizontal=True
)

# Daftar kolom teks/meta yang BUKAN merupakan indikator numerik waktu
exclude_cols = [
    "country_name", "country_text_id", "country_id", "year", "historical_date", 
    "project", "historical", "histname", "codingstart", "codingend", "COWcode",
    "codingstart_contemp", "codingend_contemp", "codingstart_hist", "codingend_hist",
    "gapstart1", "gapstart2", "gapstart3", "gapend1", "gapend2", "gapend3", "gap_index",
    "lpname", "slpname", "tlpname", "v2elregnam", "v2ellocnam", "v2juhcname", "v2lgnameup", "v2lgnamelo"
]

if mode_pilihan == "⭐ Indikator Utama (Kurasi Cepat)":
    valid_curated = {k: v for k, v in CURATED_VDEM.items() if v in df_idn.columns}
    if not valid_curated:
        valid_curated = CURATED_VDEM
    
    selected_name = st.selectbox("Pilih Indikator Utama V-Dem:", list(valid_curated.keys()))
    selected_indicator = valid_curated[selected_name]
else:
    available_indicators = [
        c for c in df_idn.columns 
        if c not in exclude_cols and pd.api.types.is_numeric_dtype(df_idn[c])
    ]
    search_term = st.text_input("🔍 Cari Indikator Bebas (ketik kata kunci, misal: libdem, corruption, freedom, rule, suffrage):", "")
    filtered_indicators = [
        ind for ind in available_indicators
        if not search_term.strip() or search_term.lower() in ind.lower() or search_term.lower() in codebook_dict.get(ind, "").lower()
    ]
    if not filtered_indicators:
        st.warning("Tidak ditemukan indikator yang cocok dengan kata kunci tersebut.")
        st.stop()
    selected_indicator = st.selectbox(f"Pilih dari {len(filtered_indicators)} Indikator Tersedia:", filtered_indicators)

# Ambil deskripsi dari codebook
indicator_description = codebook_dict.get(
    selected_indicator, 
    codebook_dict.get(selected_indicator.lower(), "Definisi rinci untuk variabel ini dapat merujuk langsung pada dokumen resmi Codebook V-Dem Institute.")
)

with st.expander("📖 Penjelasan & Metadata dari Codebook V-Dem", expanded=True):
    st.markdown(f"**Nama Variabel (Kode):** `{selected_indicator}`")
    st.markdown(f"**Definisi / Deskripsi dari Codebook:**\n> {indicator_description}")
    st.markdown("🔗 **Sumber Dokumen:** [V-Dem Codebook & Methodology](https://www.v-dem.net/data/reference-documents/)")

# =============================================================================
# 3. PENARIKAN & VISUALISASI RUNTUN WAKTU INDONESIA (TANPA BATAS TAHUN)
# =============================================================================
st.subheader("2. Visualisasi Runtun Waktu Historis Indonesia")
st.caption("Menampilkan seluruh riwayat tahun penuh yang tercatat di dalam dataset V-Dem untuk Indonesia.")

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
