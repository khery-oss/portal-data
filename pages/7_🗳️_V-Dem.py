import io
import re
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
# PANDUAN SETUP FILE (tampil hanya jika file belum ada)
# =============================================================================
with st.expander("📂 Panduan Setup File V-Dem (klik jika file belum tersedia)", expanded=False):
    st.markdown("""
    Modul ini membutuhkan **2 file CSV** yang diunggah ke root folder repository GitHub:

    **1. `vdem_data_IDN.csv`** — Dataset V-Dem khusus Indonesia
    - Unduh dataset lengkap dari: [V-Dem Institute](https://www.v-dem.net/data/the-v-dem-dataset/)
    - Filter hanya baris `country_text_id == 'IDN'` lalu simpan sebagai `vdem_data_IDN.csv`
    - Atau gunakan skrip Python berikut:
    ```python
    import pandas as pd
    df = pd.read_csv("V-Dem-CY-Full+Others-v14.csv", low_memory=False)
    df[df["country_text_id"] == "IDN"].to_csv("vdem_data_IDN.csv", index=False)
    ```

    **2. `vdem_codebook.csv`** — Codebook penjelas variabel V-Dem
    - Unduh dari: [V-Dem Codebook](https://www.v-dem.net/data/reference-documents/)
    - Konversi ke CSV dan simpan sebagai `vdem_codebook.csv`
    - Kolom minimal yang dibutuhkan: kolom nama variabel (mengandung kata `var`) dan kolom deskripsi (mengandung kata `desc` atau `def`)
    """)

# =============================================================================
# 1. MEMUAT DATASET V-DEM & CODEBOOK
# =============================================================================
@st.cache_data(show_spinner=False)
def load_vdem_data():
    try:
        df = pd.read_csv("vdem_data_IDN.csv", low_memory=False)
        return df
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Gagal membaca `vdem_data_IDN.csv`: {e}")
        return None

@st.cache_data(show_spinner=False)
def load_codebook():
    try:
        df_cb = pd.read_csv("vdem_codebook.csv")
        df_cb.columns = df_cb.columns.str.strip().str.lower()
        return df_cb
    except Exception:
        return None

with st.spinner("Memuat basis data V-Dem..."):
    df_idn = load_vdem_data()
    df_codebook = load_codebook()

if df_idn is None:
    st.error(
        "⚠️ File `vdem_data_IDN.csv` tidak ditemukan.\n\n"
        "Buka panduan setup di atas untuk instruksi cara menyiapkan file."
    )
    st.stop()

if df_idn.empty:
    st.error("File `vdem_data_IDN.csv` ditemukan namun tidak berisi data.")
    st.stop()

# =============================================================================
# BUAT KAMUS CODEBOOK — LEBIH ROBUST
# Coba beberapa kemungkinan nama kolom yang umum di berbagai versi codebook V-Dem
# =============================================================================
codebook_dict = {}
if df_codebook is not None:
    # Kandidat nama kolom variabel
    var_candidates = ["tag", "variable", "var_name", "name", "code"]
    col_var = next(
        (c for c in df_codebook.columns if any(kw in c for kw in var_candidates)),
        next((c for c in df_codebook.columns if "var" in c), None)
    )
    # Kandidat nama kolom deskripsi
    desc_candidates = ["description", "definition", "label", "question_text"]
    col_desc = next(
        (c for c in df_codebook.columns if any(kw in c for kw in desc_candidates)),
        next((c for c in df_codebook.columns if "desc" in c or "def" in c), None)
    )

    if col_var and col_desc:
        for _, row in df_codebook.iterrows():
            key = str(row[col_var]).strip()
            val = str(row[col_desc]).strip()
            if key and val and key != "nan":
                codebook_dict[key] = val
                codebook_dict[key.lower()] = val  # simpan versi lowercase juga

# =============================================================================
# 2. PEMILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Indikator V-Dem")

CURATED_VDEM = {
    "Indeks Demokrasi Liberal (Liberal Democracy Index)": "v2x_libdem",
    "Indeks Demokrasi Elektoral (Electoral Democracy Index)": "v2x_polyarchy",
    "Indeks Demokrasi Partisipatif (Participatory Democracy Index)": "v2x_partipdem",
    "Indeks Demokrasi Deliberatif (Deliberative Democracy Index)": "v2x_delibdem",
    "Indeks Demokrasi Egaliter (Egalitarian Democracy Index)": "v2x_egaldem",
    "Indeks Korupsi Publik (Public Sector Corruption Index)": "v2excrptps",
    "Indeks Korupsi Eksekutif (Executive Corruption Index)": "v2exorrpt",
    "Indeks Kebebasan Pers & Ekspresi (Freedom of Expression)": "v2x_freexp",
    "Indeks Kebebasan Berorganisasi (Freedom of Association)": "v2x_frassoc_thick",
    "Indeks Supremasi Hukum (Rule of Law Index)": "v2x_rule",
    "Indeks Akuntabilitas Vertikal (Vertical Accountability)": "v2x_veracc",
}

exclude_cols = {
    "country_name", "country_text_id", "country_id", "year", "historical_date",
    "project", "historical", "histname", "codingstart", "codingend", "COWcode",
    "codingstart_contemp", "codingend_contemp", "codingstart_hist", "codingend_hist",
    "gapstart1", "gapstart2", "gapstart3", "gapend1", "gapend2", "gapend3", "gap_index",
    "lpname", "slpname", "tlpname", "v2elregnam", "v2ellocnam", "v2juhcname",
    "v2lgnameup", "v2lgnamelo"
}

mode_pilihan = st.radio(
    "Pilih Metode Pencarian Indikator:",
    ["⭐ Indikator Utama (Kurasi Cepat)", "🔍 Eksplorasi Penuh (Semua Variabel Database)"],
    horizontal=True
)

if mode_pilihan == "⭐ Indikator Utama (Kurasi Cepat)":
    # Hanya tampilkan indikator yang benar-benar ada di file
    valid_curated = {k: v for k, v in CURATED_VDEM.items() if v in df_idn.columns}
    if not valid_curated:
        st.warning(
            "Indikator kurasi tidak ditemukan di file CSV. "
            "Pastikan file menggunakan format V-Dem standar, atau gunakan mode Eksplorasi Penuh."
        )
        st.stop()
    selected_name = st.selectbox("Pilih Indikator Utama V-Dem:", list(valid_curated.keys()))
    selected_indicator = valid_curated[selected_name]

else:
    available_indicators = [
        c for c in df_idn.columns
        if c not in exclude_cols and pd.api.types.is_numeric_dtype(df_idn[c])
    ]

    search_term = st.text_input(
        "🔍 Cari variabel (kode V-Dem atau kata kunci dari codebook):",
        placeholder="Contoh: libdem, corruption, freedom, suffrage, civil, rule",
        value=""
    ).strip()

    if search_term:
        filtered_indicators = [
            ind for ind in available_indicators
            if search_term.lower() in ind.lower()
            or search_term.lower() in codebook_dict.get(ind, "").lower()
            or search_term.lower() in codebook_dict.get(ind.lower(), "").lower()
        ]
    else:
        filtered_indicators = available_indicators

    if not filtered_indicators:
        st.warning("Tidak ditemukan indikator yang cocok. Coba kata kunci lain.")
        st.stop()

    selected_indicator = st.selectbox(
        f"Pilih dari {len(filtered_indicators)} indikator tersedia:",
        filtered_indicators
    )

# =============================================================================
# AMBIL DESKRIPSI DARI CODEBOOK
# =============================================================================
def format_math_text(text: str) -> str:
    superscript_map = {
        "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
        "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
        ".": "∙", "-": "⁻"
    }
    formatted = re.sub(
        r'\^([0-9.\-]+)',
        lambda m: "".join(superscript_map.get(c, c) for c in m.group(1)),
        text
    )
    formatted = formatted.replace(" * ", " × ")
    return formatted

indicator_description = (
    codebook_dict.get(selected_indicator)
    or codebook_dict.get(selected_indicator.lower())
    or "Definisi rinci untuk variabel ini dapat merujuk langsung pada dokumen resmi Codebook V-Dem Institute."
)
cleaned_description = format_math_text(indicator_description)

with st.expander("📖 Penjelasan & Metadata dari Codebook V-Dem", expanded=True):
    st.markdown(f"**Nama Variabel (Kode):** `{selected_indicator}`")
    st.markdown("**Definisi / Deskripsi dari Codebook:**")
    st.info(cleaned_description)
    st.markdown("🔗 **Sumber Dokumen:** [V-Dem Codebook & Methodology](https://www.v-dem.net/data/reference-documents/)")

# =============================================================================
# 3. VISUALISASI RUNTUN WAKTU
# =============================================================================
st.subheader("2. Visualisasi Runtun Waktu Historis Indonesia")
st.caption("Menampilkan seluruh riwayat tahun yang tercatat di dalam dataset V-Dem untuk Indonesia.")

if "year" not in df_idn.columns:
    st.error("Kolom `year` tidak ditemukan di file CSV. Pastikan format file V-Dem standar.")
    st.stop()

df_plot = (
    df_idn[["year", selected_indicator]]
    .dropna()
    .sort_values(by="year", ascending=True)
    .rename(columns={"year": "Tahun", selected_indicator: "Nilai Skor"})
)

if df_plot.empty:
    st.warning("Data untuk indikator ini tidak tersedia dalam file.")
    st.stop()

st.success(f"Berhasil memuat **{len(df_plot)}** observasi historis untuk Indonesia!")
st.divider()

# Filter rentang tahun
tahun_min = int(df_plot["Tahun"].min())
tahun_max = int(df_plot["Tahun"].max())

col_f1, col_f2 = st.columns(2)
with col_f1:
    tahun_mulai = st.number_input("Dari Tahun:", min_value=tahun_min, max_value=tahun_max, value=tahun_min, step=1)
with col_f2:
    tahun_akhir = st.number_input("Sampai Tahun:", min_value=tahun_min, max_value=tahun_max, value=tahun_max, step=1)

if tahun_mulai > tahun_akhir:
    st.warning("Tahun awal tidak boleh lebih besar dari tahun akhir.")
    st.stop()

df_filtered = df_plot[(df_plot["Tahun"] >= tahun_mulai) & (df_plot["Tahun"] <= tahun_akhir)]

# Tombol Unduh
c1, c2 = st.columns(2)
c1.download_button(
    "📥 Unduh CSV",
    df_filtered.to_csv(index=False).encode("utf-8"),
    f"VDem_Indonesia_{selected_indicator}.csv",
    "text/csv"
)
buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
    df_filtered.to_excel(writer, index=False, sheet_name="V-Dem Indonesia")
c2.download_button(
    "📊 Unduh Excel (.xlsx)",
    buf.getvalue(),
    f"VDem_Indonesia_{selected_indicator}.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Plotly Interaktif
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_filtered["Tahun"],
    y=df_filtered["Nilai Skor"],
    mode="lines+markers",
    name=f"Indonesia ({selected_indicator})",
    line=dict(width=2.8, color="#8B0000"),
    marker=dict(size=6),
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
    st.dataframe(df_filtered.sort_values(by="Tahun", ascending=False), use_container_width=True)
