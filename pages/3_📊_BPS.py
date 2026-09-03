import io
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="BPS Data - IndoEcon Explorer", layout="wide")

st.title("📊 Indikator Strategis BPS (Badan Pusat Statistik)")
st.write(
    "Data resmi indikator pembangunan sosial dan ekonomi Indonesia dari"
    " Badan Pusat Statistik (BPS)."
)

# Basis Data Terkurasi Resmi BPS (Tingkat Nasional & Provinsi)
# Data mencakup deret waktu historis resmi rilis BPS
DATA_BPS = {
    "Indeks Pembangunan Manusia (IPM)": {
        "unit": "Poin Indeks",
        "data": [
            {"Tahun": "2019", "Nasional": 71.92, "Jawa Barat": 72.03, "DKI Jakarta": 80.76, "Jawa Timur": 71.50, "Jawa Tengah": 71.73, "Sumatera Utara": 71.74, "Aceh": 71.90, "Papua": 60.84},
            {"Tahun": "2020", "Nasional": 71.94, "Jawa Barat": 72.09, "DKI Jakarta": 80.77, "Jawa Timur": 71.71, "Jawa Tengah": 71.87, "Sumatera Utara": 71.77, "Aceh": 71.99, "Papua": 60.44},
            {"Tahun": "2021", "Nasional": 72.29, "Jawa Barat": 72.45, "DKI Jakarta": 81.11, "Jawa Timur": 72.14, "Jawa Tengah": 72.16, "Sumatera Utara": 72.00, "Aceh": 72.18, "Papua": 60.62},
            {"Tahun": "2022", "Nasional": 72.91, "Jawa Barat": 73.12, "DKI Jakarta": 81.65, "Jawa Timur": 72.75, "Jawa Tengah": 72.79, "Sumatera Utara": 72.71, "Aceh": 72.80, "Papua": 61.39},
            {"Tahun": "2023", "Nasional": 73.55, "Jawa Barat": 73.74, "DKI Jakarta": 82.46, "Jawa Timur": 73.38, "Jawa Tengah": 73.36, "Sumatera Utara": 73.49, "Aceh": 73.35, "Papua": 62.25},
            {"Tahun": "2024", "Nasional": 74.39, "Jawa Barat": 74.52, "DKI Jakarta": 83.15, "Jawa Timur": 74.05, "Jawa Tengah": 74.01, "Sumatera Utara": 74.15, "Aceh": 73.98, "Papua": 63.01}
        ]
    },
    "Persentase Penduduk Miskin (P0)": {
        "unit": "Persen (%)",
        "data": [
            {"Tahun": "2019", "Nasional": 9.41, "Jawa Barat": 6.91, "DKI Jakarta": 3.47, "Jawa Timur": 10.37, "Jawa Tengah": 10.58, "Sumatera Utara": 8.83, "Aceh": 15.32, "Papua": 27.53},
            {"Tahun": "2020", "Nasional": 9.78, "Jawa Barat": 7.88, "DKI Jakarta": 4.53, "Jawa Timur": 11.09, "Jawa Tengah": 11.41, "Sumatera Utara": 8.75, "Aceh": 14.99, "Papua": 26.64},
            {"Tahun": "2021", "Nasional": 10.14, "Jawa Barat": 8.40, "DKI Jakarta": 4.72, "Jawa Timur": 11.40, "Jawa Tengah": 11.79, "Sumatera Utara": 9.01, "Aceh": 15.33, "Papua": 26.86},
            {"Tahun": "2022", "Nasional": 9.54, "Jawa Barat": 8.06, "DKI Jakarta": 4.69, "Jawa Timur": 10.38, "Jawa Tengah": 10.93, "Sumatera Utara": 8.42, "Aceh": 14.64, "Papua": 26.56},
            {"Tahun": "2023", "Nasional": 9.36, "Jawa Barat": 7.62, "DKI Jakarta": 4.44, "Jawa Timur": 10.35, "Jawa Tengah": 10.77, "Sumatera Utara": 8.15, "Aceh": 14.45, "Papua": 26.03},
            {"Tahun": "2024", "Nasional": 9.03, "Jawa Barat": 7.23, "DKI Jakarta": 4.30, "Jawa Timur": 9.79, "Jawa Tengah": 10.47, "Sumatera Utara": 7.99, "Aceh": 14.23, "Papua": 25.42}
        ]
    },
    "Tingkat Pengangguran Terbuka (TPT)": {
        "unit": "Persen (%)",
        "data": [
            {"Tahun": "2019", "Nasional": 5.23, "Jawa Barat": 7.99, "DKI Jakarta": 6.22, "Jawa Timur": 3.92, "Jawa Tengah": 4.44, "Sumatera Utara": 5.41, "Aceh": 6.20, "Papua": 3.65},
            {"Tahun": "2020", "Nasional": 7.07, "Jawa Barat": 10.46, "DKI Jakarta": 10.95, "Jawa Timur": 5.84, "Jawa Tengah": 6.48, "Sumatera Utara": 6.91, "Aceh": 6.59, "Papua": 4.28},
            {"Tahun": "2021", "Nasional": 6.49, "Jawa Barat": 9.82, "DKI Jakarta": 8.51, "Jawa Timur": 5.74, "Jawa Tengah": 5.95, "Sumatera Utara": 6.33, "Aceh": 6.30, "Papua": 3.33},
            {"Tahun": "2022", "Nasional": 5.86, "Jawa Barat": 8.31, "DKI Jakarta": 7.18, "Jawa Timur": 5.49, "Jawa Tengah": 5.57, "Sumatera Utara": 6.16, "Aceh": 6.17, "Papua": 2.83},
            {"Tahun": "2023", "Nasional": 5.32, "Jawa Barat": 7.44, "DKI Jakarta": 6.53, "Jawa Timur": 4.88, "Jawa Tengah": 5.13, "Sumatera Utara": 5.89, "Aceh": 6.03, "Papua": 2.67},
            {"Tahun": "2024", "Nasional": 4.82, "Jawa Barat": 6.91, "DKI Jakarta": 6.21, "Jawa Timur": 4.19, "Jawa Tengah": 4.39, "Sumatera Utara": 5.10, "Aceh": 5.75, "Papua": 2.41}
        ]
    },
    "Gini Ratio (Ketimpangan Pengeluaran)": {
        "unit": "Koefisien Gini (0-1)",
        "data": [
            {"Tahun": "2019", "Nasional": 0.380, "Jawa Barat": 0.398, "DKI Jakarta": 0.391, "Jawa Timur": 0.364, "Jawa Tengah": 0.358, "Sumatera Utara": 0.315, "Aceh": 0.317, "Papua": 0.394},
            {"Tahun": "2020", "Nasional": 0.385, "Jawa Barat": 0.403, "DKI Jakarta": 0.399, "Jawa Timur": 0.366, "Jawa Tengah": 0.359, "Sumatera Utara": 0.314, "Aceh": 0.319, "Papua": 0.395},
            {"Tahun": "2021", "Nasional": 0.381, "Jawa Barat": 0.406, "DKI Jakarta": 0.409, "Jawa Timur": 0.364, "Jawa Tengah": 0.368, "Sumatera Utara": 0.313, "Aceh": 0.324, "Papua": 0.396},
            {"Tahun": "2022", "Nasional": 0.381, "Jawa Barat": 0.412, "DKI Jakarta": 0.416, "Jawa Timur": 0.371, "Jawa Tengah": 0.374, "Sumatera Utara": 0.312, "Aceh": 0.291, "Papua": 0.406},
            {"Tahun": "2023", "Nasional": 0.388, "Jawa Barat": 0.425, "DKI Jakarta": 0.431, "Jawa Timur": 0.387, "Jawa Tengah": 0.369, "Sumatera Utara": 0.311, "Aceh": 0.300, "Papua": 0.408},
            {"Tahun": "2024", "Nasional": 0.379, "Jawa Barat": 0.421, "DKI Jakarta": 0.423, "Jawa Timur": 0.368, "Jawa Tengah": 0.365, "Sumatera Utara": 0.309, "Aceh": 0.296, "Papua": 0.397}
        ]
    }
}

# Panel Pemilihan
col1, col2 = st.columns(2)

with col1:
  indikator_pilihan = st.selectbox(
      "1. Pilih Indikator Strategis:", list(DATA_BPS.keys())
  )

meta_indikator = DATA_BPS[indikator_pilihan]
df_raw = pd.DataFrame(meta_indikator["data"])

# Daftar wilayah yang tersedia di dataset
daftar_wilayah = [col for col in df_raw.columns if col != "Tahun"]

with col2:
  wilayah_terpilih = st.multiselect(
      "2. Pilih Wilayah untuk Dibandingkan:",
      daftar_wilayah,
      default=["Nasional", "DKI Jakarta", "Jawa Barat", "Papua"],
  )

if not wilayah_terpilih:
  st.warning("Pilih minimal satu wilayah untuk menampilkan grafik dan tabel.")
  st.stop()

# Bentuk dataframe terfilter
df_display = df_raw[["Tahun"] + wilayah_terpilih]

st.divider()

# Visualisasi Grafik Interaktif
st.subheader(f"📈 Tren {indikator_pilihan}")
df_melted = df_display.melt(
    id_vars=["Tahun"], var_name="Wilayah", value_name="Nilai"
)

fig = px.line(
    df_melted,
    x="Tahun",
    y="Nilai",
    color="Wilayah",
    markers=True,
    labels={"Nilai": meta_indikator["unit"]},
    title=f"{indikator_pilihan} ({meta_indikator['unit']})",
)
fig.update_layout(hovermode="x unified", legend_title_text="Wilayah")
st.plotly_chart(fig, use_container_width=True)

# Tabel Data & Opsi Ekspor
st.subheader("📋 Tabel Data")
col_dl1, col_dl2 = st.columns(2)

col_dl1.download_button(
    "📥 Unduh CSV",
    df_display.to_csv(index=False).encode("utf-8"),
    f"{indikator_pilihan.replace(' ', '_')}.csv",
    "text/csv",
)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
  df_display.to_excel(writer, index=False, sheet_name="Data BPS")
col_dl2.download_button(
    "📊 Unduh Excel (.xlsx)",
    buf.getvalue(),
    f"{indikator_pilihan.replace(' ', '_')}.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.dataframe(df_display, use_container_width=True)
st.caption(
    "Sumber Data: Publikasi Resmi Badan Pusat Statistik (BPS) Republik"
    " Indonesia."
)
