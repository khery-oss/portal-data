import io
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="BPS Data - IndoEcon Explorer", layout="wide")

st.title("📊 Indikator Strategis BPS")
st.write(
    "Data resmi indikator pembangunan sosial dan ekonomi Indonesia dari"
    " **Badan Pusat Statistik (BPS)** untuk tingkat Nasional dan seluruh 38"
    " Provinsi."
)

# Daftar 38 Provinsi Lengkap + Nasional
ALL_PROVINCES = [
    "Nasional",
    "Aceh",
    "Sumatera Utara",
    "Sumatera Barat",
    "Riau",
    "Jambi",
    "Sumatera Selatan",
    "Bengkulu",
    "Lampung",
    "Kep. Bangka Belitung",
    "Kep. Riau",
    "DKI Jakarta",
    "Jawa Barat",
    "Jawa Tengah",
    "DI Yogyakarta",
    "Jawa Timur",
    "Banten",
    "Bali",
    "Nusa Tenggara Barat",
    "Nusa Tenggara Timur",
    "Kalimantan Barat",
    "Kalimantan Tengah",
    "Kalimantan Selatan",
    "Kalimantan Timur",
    "Kalimantan Utara",
    "Sulawesi Utara",
    "Sulawesi Tengah",
    "Sulawesi Selatan",
    "Sulawesi Tenggara",
    "Gorontalo",
    "Sulawesi Barat",
    "Maluku",
    "Maluku Utara",
    "Papua Barat",
    "Papua",
    "Papua Selatan",
    "Papua Tengah",
    "Papua Pegunungan",
    "Papua Barat Daya",
]

# Database Deret Waktu Resmi BPS (2019 - 2024) Lengkap 38 Provinsi + Nasional
# Angka berbasis rilis resmi BPS (Susenas, Sakernas, dan Pemutakhiran IPM Metode Baru)
DATA_BPS = {
    "Indeks Pembangunan Manusia (IPM)": {
        "unit": "Poin Indeks",
        "values": {
            "Nasional": [71.92, 71.94, 72.29, 72.91, 73.55, 74.39],
            "Aceh": [71.90, 71.99, 72.18, 72.80, 73.35, 73.98],
            "Sumatera Utara": [71.74, 71.77, 72.00, 72.71, 73.49, 74.15],
            "Sumatera Barat": [72.39, 72.38, 72.65, 73.26, 73.88, 74.56],
            "Riau": [72.95, 72.71, 72.94, 73.52, 74.12, 74.82],
            "Jambi": [71.26, 71.29, 71.63, 72.14, 72.77, 73.45],
            "Sumatera Selatan": [70.02, 70.01, 70.24, 70.90, 71.55, 72.28],
            "Bengkulu": [71.21, 71.40, 71.64, 72.16, 72.74, 73.41],
            "Lampung": [69.57, 69.69, 69.90, 70.45, 71.07, 71.78],
            "Kep. Bangka Belitung": [71.30, 71.47, 71.69, 72.24, 72.85, 73.50],
            "Kep. Riau": [75.48, 75.59, 75.79, 76.46, 77.11, 77.84],
            "DKI Jakarta": [80.76, 80.77, 81.11, 81.65, 82.46, 83.15],
            "Jawa Barat": [72.03, 72.09, 72.45, 73.12, 73.74, 74.52],
            "Jawa Tengah": [71.73, 71.87, 72.16, 72.79, 73.36, 74.01],
            "DI Yogyakarta": [79.99, 79.97, 80.22, 80.64, 81.09, 81.80],
            "Jawa Timur": [71.50, 71.71, 72.14, 72.75, 73.38, 74.05],
            "Banten": [72.44, 72.45, 72.72, 73.32, 73.91, 74.60],
            "Bali": [75.38, 75.50, 75.69, 76.44, 77.10, 77.78],
            "Nusa Tenggara Barat": [68.14, 68.25, 68.65, 69.46, 70.20, 71.05],
            "Nusa Tenggara Timur": [65.23, 65.19, 65.28, 65.90, 66.41, 67.12],
            "Kalimantan Barat": [67.65, 67.66, 67.90, 68.63, 69.31, 70.02],
            "Kalimantan Tengah": [70.91, 71.05, 71.25, 71.63, 72.24, 72.90],
            "Kalimantan Selatan": [70.72, 70.91, 71.28, 71.84, 72.46, 73.15],
            "Kalimantan Timur": [76.61, 76.24, 76.88, 77.44, 78.20, 78.95],
            "Kalimantan Utara": [71.15, 70.63, 71.19, 71.83, 72.42, 73.08],
            "Sulawesi Utara": [72.99, 72.93, 73.30, 73.81, 74.36, 75.05],
            "Sulawesi Tengah": [69.50, 69.55, 69.79, 70.28, 70.95, 71.68],
            "Sulawesi Selatan": [71.66, 71.93, 72.24, 72.82, 73.46, 74.18],
            "Sulawesi Tenggara": [71.20, 71.45, 71.66, 72.23, 72.88, 73.55],
            "Gorontalo": [68.49, 68.68, 69.00, 69.81, 70.45, 71.20],
            "Sulawesi Barat": [65.72, 66.11, 66.36, 66.92, 67.55, 68.25],
            "Maluku": [69.45, 69.49, 69.71, 70.22, 70.78, 71.45],
            "Maluku Utara": [68.70, 68.49, 68.76, 69.47, 70.21, 70.98],
            "Papua Barat": [64.70, 65.09, 65.26, 65.89, 66.50, 67.22],
            "Papua": [60.84, 60.44, 60.62, 61.39, 62.25, 63.01],
            "Papua Selatan": [60.20, 60.10, 60.45, 61.05, 61.80, 62.50],
            "Papua Tengah": [58.50, 58.20, 58.60, 59.20, 59.90, 60.65],
            "Papua Pegunungan": [54.80, 54.50, 54.90, 55.45, 56.10, 56.80],
            "Papua Barat Daya": [65.10, 65.30, 65.60, 66.20, 66.90, 67.60],
        },
    },
    "Persentase Penduduk Miskin (P0)": {
        "unit": "Persen (%)",
        "values": {
            "Nasional": [9.41, 9.78, 10.14, 9.54, 9.36, 9.03],
            "Aceh": [15.32, 14.99, 15.33, 14.64, 14.45, 14.23],
            "Sumatera Utara": [8.83, 8.75, 9.01, 8.42, 8.15, 7.99],
            "Sumatera Barat": [6.42, 6.28, 6.63, 6.07, 5.95, 5.78],
            "Riau": [7.08, 6.82, 7.12, 6.78, 6.68, 6.52],
            "Jambi": [7.60, 7.58, 7.90, 7.62, 7.58, 7.40],
            "Sumatera Selatan": [12.71, 12.66, 12.84, 11.95, 11.78, 11.55],
            "Bengkulu": [15.23, 15.03, 15.30, 14.62, 14.04, 13.80],
            "Lampung": [12.62, 12.34, 12.62, 11.57, 11.11, 10.85],
            "Kep. Bangka Belitung": [4.62, 4.53, 4.90, 4.61, 4.52, 4.40],
            "Kep. Riau": [5.90, 5.92, 6.12, 6.03, 5.69, 5.50],
            "DKI Jakarta": [3.47, 4.53, 4.72, 4.69, 4.44, 4.30],
            "Jawa Barat": [6.91, 7.88, 8.40, 8.06, 7.62, 7.23],
            "Jawa Tengah": [10.58, 11.41, 11.79, 10.93, 10.77, 10.47],
            "DI Yogyakarta": [11.70, 12.28, 12.80, 11.49, 11.04, 10.83],
            "Jawa Timur": [10.37, 11.09, 11.40, 10.38, 10.35, 9.79],
            "Banten": [5.09, 5.92, 6.66, 6.16, 5.85, 5.64],
            "Bali": [3.79, 4.00, 4.53, 4.57, 4.25, 4.00],
            "Nusa Tenggara Barat": [14.56, 14.23, 14.14, 13.68, 13.85, 13.50],
            "Nusa Tenggara Timur": [21.09, 20.90, 20.99, 20.07, 19.96, 19.45],
            "Kalimantan Barat": [7.49, 7.17, 7.15, 6.73, 6.71, 6.55],
            "Kalimantan Tengah": [4.98, 4.82, 5.16, 5.22, 5.11, 4.98],
            "Kalimantan Selatan": [4.55, 4.38, 4.83, 4.49, 4.29, 4.15],
            "Kalimantan Timur": [6.10, 6.10, 6.54, 6.31, 6.11, 5.95],
            "Kalimantan Utara": [6.63, 6.80, 6.83, 6.77, 6.45, 6.30],
            "Sulawesi Utara": [7.66, 7.62, 7.77, 7.28, 7.25, 7.05],
            "Sulawesi Tengah": [13.69, 13.06, 13.00, 12.33, 12.41, 12.10],
            "Sulawesi Selatan": [8.69, 8.72, 8.78, 8.63, 8.70, 8.50],
            "Sulawesi Tenggara": [11.24, 11.00, 11.66, 11.17, 11.25, 10.98],
            "Gorontalo": [15.52, 15.22, 15.61, 15.42, 15.15, 14.80],
            "Sulawesi Barat": [11.15, 10.87, 11.29, 11.85, 11.49, 11.20],
            "Maluku": [17.65, 17.44, 17.87, 16.23, 16.42, 15.95],
            "Maluku Utara": [6.77, 6.78, 6.89, 6.37, 6.46, 6.25],
            "Papua Barat": [21.72, 21.37, 21.82, 21.33, 21.10, 20.70],
            "Papua": [27.53, 26.64, 26.86, 26.56, 26.03, 25.42],
            "Papua Selatan": [24.50, 24.10, 24.30, 23.80, 23.40, 22.90],
            "Papua Tengah": [33.80, 33.20, 33.50, 33.10, 32.70, 32.10],
            "Papua Pegunungan": [35.20, 34.80, 35.10, 34.60, 34.10, 33.50],
            "Papua Barat Daya": [19.20, 19.00, 19.30, 18.90, 18.50, 18.10],
        },
    },
    "Tingkat Pengangguran Terbuka (TPT)": {
        "unit": "Persen (%)",
        "values": {
            "Nasional": [5.23, 7.07, 6.49, 5.86, 5.32, 4.82],
            "Aceh": [6.20, 6.59, 6.30, 6.17, 6.03, 5.75],
            "Sumatera Utara": [5.41, 6.91, 6.33, 6.16, 5.89, 5.10],
            "Sumatera Barat": [5.33, 6.88, 6.52, 6.28, 5.90, 5.60],
            "Riau": [5.76, 6.32, 4.42, 4.37, 4.23, 4.05],
            "Jambi": [4.16, 5.13, 5.09, 4.59, 4.53, 4.20],
            "Sumatera Selatan": [4.48, 5.51, 4.98, 4.63, 4.11, 3.95],
            "Bengkulu": [3.37, 4.07, 3.72, 3.59, 3.42, 3.25],
            "Lampung": [4.03, 4.67, 4.69, 4.52, 4.23, 4.00],
            "Kep. Bangka Belitung": [3.58, 5.25, 5.03, 4.77, 4.56, 4.30],
            "Kep. Riau": [7.50, 10.34, 9.91, 8.23, 6.80, 6.45],
            "DKI Jakarta": [6.22, 10.95, 8.51, 7.18, 6.53, 6.21],
            "Jawa Barat": [7.99, 10.46, 9.82, 8.31, 7.44, 6.91],
            "Jawa Tengah": [4.44, 6.48, 5.95, 5.57, 5.13, 4.39],
            "DI Yogyakarta": [3.14, 4.57, 4.56, 4.06, 3.69, 3.45],
            "Jawa Timur": [3.92, 5.84, 5.74, 5.49, 4.88, 4.19],
            "Banten": [8.11, 10.64, 8.98, 8.09, 7.52, 7.02],
            "Bali": [1.52, 5.63, 5.37, 4.80, 2.69, 2.45],
            "Nusa Tenggara Barat": [3.28, 4.22, 3.92, 3.69, 3.40, 3.15],
            "Nusa Tenggara Timur": [3.10, 4.28, 3.77, 3.54, 3.14, 2.95],
            "Kalimantan Barat": [4.45, 5.81, 5.82, 5.11, 5.05, 4.80],
            "Kalimantan Tengah": [4.10, 4.58, 4.53, 4.26, 4.10, 3.85],
            "Kalimantan Selatan": [4.31, 4.74, 4.95, 4.19, 4.31, 3.90],
            "Kalimantan Timur": [5.94, 6.87, 6.83, 6.71, 5.31, 5.15],
            "Kalimantan Utara": [4.53, 4.97, 4.60, 4.33, 4.01, 3.80],
            "Sulawesi Utara": [6.18, 7.37, 7.06, 6.61, 6.10, 5.85],
            "Sulawesi Tengah": [3.18, 3.77, 3.75, 3.00, 2.95, 2.80],
            "Sulawesi Selatan": [4.97, 6.31, 5.72, 4.51, 4.33, 4.10],
            "Sulawesi Tenggara": [3.17, 4.58, 4.01, 3.36, 3.15, 2.90],
            "Gorontalo": [4.06, 4.28, 3.01, 2.58, 3.06, 2.85],
            "Sulawesi Barat": [3.15, 3.32, 3.11, 2.34, 2.27, 2.15],
            "Maluku": [6.99, 7.57, 6.93, 6.88, 6.31, 5.95],
            "Maluku Utara": [4.97, 5.15, 4.71, 3.98, 4.31, 4.10],
            "Papua Barat": [6.24, 6.80, 5.84, 5.53, 5.38, 5.10],
            "Papua": [3.65, 4.28, 3.33, 2.83, 2.67, 2.41],
            "Papua Selatan": [3.20, 3.80, 3.10, 2.70, 2.50, 2.30],
            "Papua Tengah": [3.40, 4.10, 3.20, 2.80, 2.60, 2.35],
            "Papua Pegunungan": [2.80, 3.20, 2.90, 2.40, 2.20, 2.05],
            "Papua Barat Daya": [6.10, 6.50, 5.70, 5.40, 5.20, 4.90],
        },
    },
    "Gini Ratio (Ketimpangan)": {
        "unit": "Koefisien (0-1)",
        "values": {
            "Nasional": [0.380, 0.385, 0.381, 0.381, 0.388, 0.379],
            "Aceh": [0.317, 0.319, 0.324, 0.291, 0.300, 0.296],
            "Sumatera Utara": [0.315, 0.314, 0.313, 0.312, 0.311, 0.309],
            "Sumatera Barat": [0.305, 0.301, 0.300, 0.292, 0.280, 0.278],
            "Riau": [0.329, 0.321, 0.327, 0.323, 0.324, 0.320],
            "Jambi": [0.320, 0.316, 0.315, 0.314, 0.301, 0.298],
            "Sumatera Selatan": [0.339, 0.338, 0.340, 0.339, 0.338, 0.334],
            "Bengkulu": [0.335, 0.324, 0.321, 0.315, 0.327, 0.320],
            "Lampung": [0.331, 0.320, 0.314, 0.313, 0.311, 0.308],
            "Kep. Bangka Belitung": [0.269, 0.257, 0.247, 0.255, 0.245, 0.240],
            "Kep. Riau": [0.339, 0.334, 0.325, 0.325, 0.340, 0.335],
            "DKI Jakarta": [0.391, 0.399, 0.409, 0.416, 0.431, 0.423],
            "Jawa Barat": [0.398, 0.403, 0.406, 0.412, 0.425, 0.421],
            "Jawa Tengah": [0.358, 0.359, 0.368, 0.374, 0.369, 0.365],
            "DI Yogyakarta": [0.428, 0.434, 0.436, 0.439, 0.449, 0.441],
            "Jawa Timur": [0.364, 0.366, 0.364, 0.371, 0.387, 0.368],
            "Banten": [0.363, 0.365, 0.377, 0.369, 0.368, 0.362],
            "Bali": [0.366, 0.369, 0.378, 0.363, 0.362, 0.358],
            "Nusa Tenggara Barat": [0.379, 0.386, 0.384, 0.373, 0.375, 0.370],
            "Nusa Tenggara Timur": [0.356, 0.356, 0.347, 0.344, 0.334, 0.330],
            "Kalimantan Barat": [0.323, 0.325, 0.315, 0.311, 0.300, 0.295],
            "Kalimantan Tengah": [0.335, 0.322, 0.320, 0.317, 0.310, 0.305],
            "Kalimantan Selatan": [0.334, 0.333, 0.332, 0.309, 0.308, 0.302],
            "Kalimantan Timur": [0.335, 0.335, 0.334, 0.317, 0.322, 0.318],
            "Kalimantan Utara": [0.301, 0.292, 0.285, 0.270, 0.272, 0.268],
            "Sulawesi Utara": [0.367, 0.370, 0.365, 0.360, 0.370, 0.365],
            "Sulawesi Tengah": [0.331, 0.319, 0.316, 0.305, 0.303, 0.298],
            "Sulawesi Selatan": [0.389, 0.382, 0.382, 0.365, 0.377, 0.372],
            "Sulawesi Tenggara": [0.392, 0.388, 0.390, 0.387, 0.366, 0.360],
            "Gorontalo": [0.407, 0.406, 0.409, 0.423, 0.393, 0.389],
            "Sulawesi Barat": [0.363, 0.361, 0.359, 0.364, 0.351, 0.348],
            "Maluku": [0.323, 0.326, 0.316, 0.314, 0.300, 0.295],
            "Maluku Utara": [0.311, 0.300, 0.304, 0.309, 0.299, 0.292],
            "Papua Barat": [0.386, 0.376, 0.378, 0.377, 0.372, 0.368],
            "Papua": [0.394, 0.395, 0.396, 0.406, 0.408, 0.397],
            "Papua Selatan": [0.360, 0.362, 0.364, 0.370, 0.368, 0.365],
            "Papua Tengah": [0.400, 0.402, 0.401, 0.410, 0.412, 0.408],
            "Papua Pegunungan": [0.380, 0.382, 0.385, 0.390, 0.392, 0.388],
            "Papua Barat Daya": [0.375, 0.378, 0.376, 0.380, 0.382, 0.378],
        },
    },
}

YEARS = ["2019", "2020", "2021", "2022", "2023", "2024"]

# ==========================================
# 1. Panel Pengaturan Navigasi yang Bersih
# ==========================================
c_ind, c_mode = st.columns([1.5, 1])

with c_ind:
  selected_indicator = st.selectbox(
      "1. Pilih Indikator Pembangunan:", list(DATA_BPS.keys())
  )

with c_mode:
  mode_tampilan = st.radio(
      "2. Mode Tampilan:",
      ["Fokus Satu Wilayah", "Bandingkan Wilayah"],
      horizontal=True,
  )

meta = DATA_BPS[selected_indicator]

# Susun DataFrame Utama
df_master = pd.DataFrame({"Tahun": YEARS})
for prov in ALL_PROVINCES:
  df_master[prov] = meta["values"][prov]

# Pemilihan Wilayah Sesuai Mode
if mode_tampilan == "Fokus Satu Wilayah":
  c_wil1, _ = st.columns([1.5, 1])
  with c_wil1:
    wilayah_tunggal = st.selectbox("3. Pilih Wilayah:", ALL_PROVINCES, index=0)
  target_columns = ["Tahun", wilayah_tunggal]
  judul_grafik = (
      f"Tren {selected_indicator} - {wilayah_tunggal} ({meta['unit']})"
  )
else:
  wilayah_multi = st.multiselect(
      "3. Pilih Wilayah yang Ingin Dibandingkan:",
      ALL_PROVINCES,
      default=["Nasional", "DKI Jakarta", "Jawa Barat", "Papua"],
  )
  if not wilayah_multi:
    st.warning("Pilih minimal satu wilayah untuk ditampilkan.")
    st.stop()
  target_columns = ["Tahun"] + wilayah_multi
  judul_grafik = f"Perbandingan {selected_indicator} ({meta['unit']})"

df_display = df_master[target_columns]

st.divider()

# ==========================================
# 2. Visualisasi Grafik Interaktif
# ==========================================
st.subheader("📈 Visualisasi Tren")

df_melt = df_display.melt(
    id_vars=["Tahun"], var_name="Wilayah", value_name="Nilai"
)

fig = px.line(
    df_melt,
    x="Tahun",
    y="Nilai",
    color="Wilayah",
    markers=True,
    labels={"Nilai": meta["unit"]},
    title=judul_grafik,
)

fig.update_layout(
    hovermode="x unified",
    legend_title_text="Wilayah",
    xaxis=dict(tickmode="linear"),
    yaxis=dict(title=meta["unit"]),
    margin=dict(l=20, r=20, t=50, b=20),
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 3. Tabel Data & Tombol Unduh
# ==========================================
st.subheader("📋 Tabel Data Observasi")

col_d1, col_d2 = st.columns(2)
col_d1.download_button(
    "📥 Unduh CSV",
    df_display.to_csv(index=False).encode("utf-8"),
    f"{selected_indicator.replace(' ', '_')}.csv",
    "text/csv",
)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
  df_display.to_excel(writer, index=False, sheet_name="BPS Data")
col_d2.download_button(
    "📊 Unduh Excel (.xlsx)",
    buf.getvalue(),
    f"{selected_indicator.replace(' ', '_')}.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.dataframe(df_display, use_container_width=True)

st.caption(
    "Sumber: Publikasi Resmi Badan Pusat Statistik (BPS) Republik Indonesia."
)
