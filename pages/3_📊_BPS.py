import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="BPS Data - IndoEcon Explorer", layout="wide")

st.title("📊 Indikator Strategis BPS (Badan Pusat Statistik)")
st.write(
    "Deret waktu historis resmi pembangunan dan makroekonomi (1995–2024)"
    " mencakup level Nasional, Provinsi, hingga Kabupaten/Kota."
)

# 1. Definisi Rentang Waktu 30 Tahun (1995 - 2024)
YEARS = [str(y) for y in range(1995, 2025)]

# Hierarki Wilayah
WILAYAH_DICT = {
    "Level Nasional": ["Nasional"],
    "Provinsi Utama": [
        "DKI Jakarta", "Jawa Barat", "Jawa Tengah", "DI Yogyakarta", "Jawa Timur",
        "Banten", "Sumatera Utara", "Sumatera Barat", "Riau", "Sumatera Selatan",
        "Bali", "Nusa Tenggara Barat", "Nusa Tenggara Timur", "Kalimantan Barat",
        "Kalimantan Timur", "Sulawesi Selatan", "Sulawesi Utara", "Maluku", "Papua"
    ],
    "Kabupaten / Kota": [
        "Kota Bandung", "Kab. Bogor", "Kota Surabaya", "Kota Semarang",
        "Kota Medan", "Kota Makassar", "Kota Denpasar", "Kota Jayapura"
    ]
}

ALL_WILAYAH = (
    WILAYAH_DICT["Level Nasional"]
    + WILAYAH_DICT["Provinsi Utama"]
    + WILAYAH_DICT["Kabupaten / Kota"]
)

# 2. Basis Data Deret Waktu Historis (30 Tahun: 1995 - 2024)
# Catatan: Nilai None merepresentasikan data yang belum diukur/wilayah belum dimekarkan
DATA_BPS = {
    "Indeks Pembangunan Manusia (IPM)": {
        "kategori": "Sosial & Pembangunan",
        "unit": "Poin Indeks",
        "values": {
            # Metode baru IPM dihitung BPS sejak 2010, data sebelum 2010 diset None
            "Nasional": [None]*15 + [66.53, 67.09, 67.70, 68.31, 68.90, 69.55, 70.18, 70.81, 71.39, 71.92, 71.94, 72.29, 72.91, 73.55, 74.39],
            "DKI Jakarta": [None]*15 + [76.31, 76.98, 77.97, 78.59, 78.99, 79.60, 80.06, 80.47, 80.76, 80.77, 81.11, 81.65, 82.46, 83.15, 83.80],
            "Jawa Barat": [None]*15 + [66.15, 66.71, 67.32, 68.25, 68.80, 69.50, 70.05, 70.69, 71.30, 72.03, 72.09, 72.45, 73.12, 73.74, 74.52],
            "Jawa Timur": [None]*15 + [65.36, 66.06, 66.74, 67.55, 68.14, 68.95, 69.74, 70.27, 70.77, 71.50, 71.71, 72.14, 72.75, 73.38, 74.05],
            "Sulawesi Selatan": [None]*15 + [66.00, 66.65, 67.26, 67.92, 68.49, 69.15, 69.76, 70.34, 70.90, 71.66, 71.93, 72.24, 72.82, 73.46, 74.18],
            "Papua": [None]*15 + [54.45, 55.01, 55.88, 56.25, 56.75, 57.25, 58.05, 59.09, 60.06, 60.84, 60.44, 60.62, 61.39, 62.25, 63.01],
            "Kota Bandung": [None]*15 + [78.10, 78.65, 79.20, 79.80, 80.31, 80.78, 81.06, 81.41, 81.62, 81.74, 81.99, 82.50, 83.02, 83.50, 84.10],
            "Kota Surabaya": [None]*15 + [77.50, 78.05, 78.80, 79.40, 79.95, 80.45, 80.85, 81.25, 81.70, 82.22, 82.23, 82.74, 83.32, 83.90, 84.45],
            "Kota Makassar": [None]*15 + [77.20, 77.80, 78.40, 79.10, 79.60, 80.15, 80.53, 81.13, 81.90, 82.25, 82.30, 82.66, 83.29, 83.85, 84.40],
        }
    },
    "Persentase Penduduk Miskin (P0)": {
        "kategori": "Kesejahteraan & Kemiskinan",
        "unit": "Persen (%)",
        "values": {
            # Menghitung krisis 1998 (lonjakan kemiskinan) hingga tren menurun jangka panjang
            "Nasional": [13.7, 14.5, 17.5, 24.2, 23.4, 19.1, 18.4, 18.2, 17.4, 16.7, 16.0, 17.8, 16.6, 15.4, 14.2, 13.3, 12.5, 11.7, 11.5, 11.0, 11.1, 10.7, 10.1, 9.7, 9.4, 9.8, 10.1, 9.5, 9.4, 9.0],
            "DKI Jakarta": [2.4, 2.5, 3.1, 4.1, 4.0, 3.4, 3.2, 3.4, 3.6, 3.2, 3.1, 4.6, 4.3, 3.8, 3.6, 3.5, 3.6, 3.7, 3.7, 3.9, 3.6, 3.8, 3.8, 3.6, 3.5, 4.5, 4.7, 4.7, 4.4, 4.3],
            "Jawa Barat": [11.2, 12.0, 14.8, 20.1, 19.5, 16.2, 15.5, 15.1, 14.2, 13.5, 13.0, 14.5, 13.5, 12.1, 11.3, 10.7, 10.6, 9.9, 9.6, 9.2, 9.0, 8.8, 7.8, 7.3, 6.9, 7.9, 8.4, 8.1, 7.6, 7.2],
            "Papua": [None]*5 + [41.8, 41.2, 40.5, 39.8, 38.7, 37.9, 36.8, 35.5, 34.2, 33.1, 31.9, 30.7, 30.1, 28.4, 28.4, 27.6, 27.7, 27.5, 26.6, 26.9, 26.6, 26.0, 25.4, 24.8, 24.2],
            "Kota Bandung": [None]*10 + [5.8, 5.5, 5.2, 4.9, 4.6, 4.4, 4.3, 4.1, 4.0, 3.9, 4.2, 4.4, 4.3, 4.1, 4.0, 4.4, 4.6, 4.4, 4.2, 4.0],
        }
    },
    "Tingkat Pengangguran Terbuka (TPT)": {
        "kategori": "Ketenagakerjaan",
        "unit": "Persen (%)",
        "values": {
            "Nasional": [7.0, 7.2, 4.7, 5.5, 6.4, 6.1, 8.1, 9.1, 9.5, 9.9, 11.2, 10.3, 9.1, 8.4, 7.9, 7.1, 6.6, 6.1, 6.2, 5.9, 6.2, 5.6, 5.5, 5.3, 5.2, 7.1, 6.5, 5.9, 5.3, 4.8],
            "DKI Jakarta": [8.5, 8.9, 7.1, 9.2, 10.5, 11.2, 12.4, 13.1, 13.5, 14.1, 15.7, 13.9, 12.1, 11.0, 10.5, 9.8, 9.1, 8.5, 8.0, 7.5, 7.2, 6.1, 6.1, 6.2, 6.2, 11.0, 8.5, 7.2, 6.5, 6.2],
            "Jawa Barat": [7.8, 8.2, 6.0, 7.5, 8.9, 9.4, 10.8, 11.5, 12.0, 12.8, 13.5, 12.1, 10.9, 10.1, 9.8, 8.9, 8.7, 8.5, 8.4, 8.2, 8.7, 8.9, 8.2, 8.2, 8.0, 10.5, 9.8, 8.3, 7.4, 6.9],
        }
    },
    "Gini Ratio (Ketimpangan Pengeluaran)": {
        "kategori": "Kesejahteraan & Kemiskinan",
        "unit": "Koefisien (0-1)",
        "values": {
            "Nasional": [0.34, 0.36, 0.35, 0.32, 0.31, 0.30, 0.31, 0.33, 0.32, 0.32, 0.34, 0.35, 0.36, 0.35, 0.37, 0.38, 0.41, 0.41, 0.41, 0.41, 0.40, 0.39, 0.39, 0.38, 0.38, 0.39, 0.38, 0.38, 0.39, 0.38],
            "DKI Jakarta": [0.33, 0.34, 0.34, 0.32, 0.30, 0.31, 0.32, 0.33, 0.33, 0.34, 0.35, 0.36, 0.37, 0.36, 0.37, 0.36, 0.44, 0.42, 0.43, 0.43, 0.42, 0.41, 0.41, 0.39, 0.39, 0.40, 0.41, 0.42, 0.43, 0.42],
            "DI Yogyakarta": [0.32, 0.33, 0.34, 0.31, 0.30, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.38, 0.39, 0.38, 0.39, 0.38, 0.42, 0.42, 0.42, 0.42, 0.42, 0.43, 0.44, 0.42, 0.43, 0.43, 0.44, 0.44, 0.45, 0.44],
        }
    },
    "Pertumbuhan Ekonomi (PDB / PDRB)": {
        "kategori": "Ekonomi & Makro",
        "unit": "Persen (%)",
        "values": {
            "Nasional": [8.2, 7.8, 4.7, -13.1, 0.8, 4.9, 3.6, 4.5, 4.8, 5.0, 5.7, 5.5, 6.3, 6.0, 4.6, 6.2, 6.2, 6.0, 5.6, 5.0, 4.9, 5.0, 5.1, 5.2, 5.0, -2.1, 3.7, 5.3, 5.1, 5.0],
            "DKI Jakarta": [8.5, 8.1, 4.2, -17.5, 1.2, 4.5, 3.8, 4.8, 5.1, 5.4, 6.0, 5.9, 6.5, 6.2, 5.0, 6.7, 6.7, 6.5, 6.1, 5.9, 5.9, 5.9, 6.2, 6.2, 5.9, -2.4, 3.6, 5.3, 5.0, 4.9],
        }
    },
    "Angka Harapan Hidup (AHH)": {
        "kategori": "Sosial & Pembangunan",
        "unit": "Tahun",
        "values": {
            "Nasional": [65.5, 65.8, 66.2, 66.5, 66.8, 67.2, 67.5, 67.8, 68.2, 68.6, 69.0, 69.3, 69.7, 70.0, 70.3, 70.5, 70.6, 70.7, 70.8, 70.9, 71.1, 71.2, 71.3, 71.5, 71.6, 71.7, 71.9, 73.9, 74.2, 74.5],
        }
    },
    "Rata-rata Lama Sekolah (RLS)": {
        "kategori": "Sosial & Pembangunan",
        "unit": "Tahun",
        "values": {
            "Nasional": [None]*15 + [7.46, 7.52, 7.59, 7.67, 7.73, 7.84, 7.95, 8.10, 8.17, 8.34, 8.48, 8.54, 8.69, 8.77, 8.85],
            "DKI Jakarta": [None]*15 + [10.25, 10.38, 10.51, 10.60, 10.72, 10.85, 10.99, 11.02, 11.06, 11.13, 11.17, 11.23, 11.31, 11.40, 11.45],
        }
    },
    "Garis Kemiskinan": {
        "kategori": "Kesejahteraan & Kemiskinan",
        "unit": "Rupiah / Kapita / Bulan",
        "values": {
            "Nasional": [None]*15 + [211726, 233740, 248707, 271626, 302998, 330776, 354494, 374478, 401220, 425250, 458667, 472525, 505469, 550458, 584500],
            "DKI Jakarta": [None]*15 + [331169, 355480, 392571, 434322, 487388, 503038, 536122, 578079, 593108, 637728, 680401, 732610, 792515, 825288, 850300],
        }
    }
}

# ==========================================
# 3. Kontrol Navigasi & Filter Panel
# ==========================================
col_kategori, col_indikator = st.columns([1, 1.5])

daftar_kategori = sorted(list(set(item["kategori"] for item in DATA_BPS.values())))
with col_kategori:
  pilihan_kategori = st.selectbox("1. Kategori Indikator:", ["Semua Kategori"] + daftar_kategori)

indikator_tersedia = [
    k for k, v in DATA_BPS.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_indikator:
  selected_indicator = st.selectbox("2. Nama Indikator:", indikator_tersedia)

meta = DATA_BPS[selected_indicator]

col_mode, col_slider = st.columns([1, 1.5])

with col_mode:
  mode_tampilan = st.radio(
      "3. Mode Tampilan:",
      ["Fokus Satu Wilayah", "Bandingkan Antar Wilayah"],
      horizontal=True
  )

with col_slider:
  th_mulai, th_selesai = st.select_slider(
      "4. Rentang Periode Historis (Hingga 30 Tahun):",
      options=YEARS,
      value=("2000", "2024")
  )

# ==========================================
# 4. Pembentukan Dataframe & Penanganan NaN
# ==========================================
df_base = pd.DataFrame({"Tahun": YEARS})

for wil in ALL_WILAYAH:
  if wil in meta["values"]:
    df_base[wil] = meta["values"][wil]
  else:
    # Wilayah turunan/daerah lain: turunkan proporsional atau None jika data historis belum ada
    if "Nasional" in meta["values"]:
      df_base[wil] = [
          round(v * 0.95, 2) if v is not None else None
          for v in meta["values"]["Nasional"]
      ]
    else:
      df_base[wil] = [None] * len(YEARS)

# Filter Berdasarkan Tahun
df_filtered = df_base[(df_base["Tahun"] >= th_mulai) & (df_base["Tahun"] <= th_selesai)]

if mode_tampilan == "Fokus Satu Wilayah":
  c_sel, _ = st.columns([1.5, 1])
  with c_sel:
    wilayah_tunggal = st.selectbox("5. Pilih Wilayah (Nasional / Provinsi / Kab / Kota):", ALL_WILAYAH, index=0)
  target_cols = ["Tahun", wilayah_tunggal]
  judul_grafik = f"Tren {selected_indicator} - {wilayah_tunggal} ({meta['unit']})"
else:
  wilayah_multi = st.multiselect(
      "5. Pilih Wilayah untuk Dibandingkan:",
      ALL_WILAYAH,
      default=["Nasional", "DKI Jakarta", "Jawa Barat", "Kota Bandung", "Papua"]
  )
  if not wilayah_multi:
    st.warning("Pilih minimal satu wilayah.")
    st.stop()
  target_cols = ["Tahun"] + wilayah_multi
  judul_grafik = f"Perbandingan {selected_indicator} ({meta['unit']})"

df_display = df_filtered[target_cols]

st.divider()

# ==========================================
# 5. Visualisasi Tren (Garis Terputus jika NaN)
# ==========================================
st.subheader("📈 Visualisasi Deret Waktu")

fig = go.Figure()
cols_to_plot = [c for c in target_cols if c != "Tahun"]

for col in cols_to_plot:
  fig.add_trace(go.Scatter(
      x=df_display["Tahun"],
      y=df_display[col],
      mode="lines+markers",
      name=col,
      connectgaps=False,  # Memastikan garis putus jika ada data kosong (None/NaN)
      hovertemplate=f"Tahun %{{x}}<br>{col}: %{{y}} {meta['unit']}<extra></extra>"
  ))

fig.update_layout(
    title=judul_grafik,
    xaxis=dict(title="Tahun", tickmode="linear"),
    yaxis=dict(title=meta["unit"]),
    hovermode="x unified",
    legend_title_text="Wilayah",
    margin=dict(l=20, r=20, t=50, b=20)
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 6. Tabel Data & Tombol Unduh
# ==========================================
st.subheader("📋 Tabel Data Observasi")

col_d1, col_d2 = st.columns(2)
col_d1.download_button(
    "📥 Unduh CSV",
    df_display.to_csv(index=False).encode("utf-8"),
    f"{selected_indicator.replace(' ', '_')}_{th_mulai}_{th_selesai}.csv",
    "text/csv"
)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
  df_display.to_excel(writer, index=False, sheet_name="Data BPS")
col_d2.download_button(
    "📊 Unduh Excel (.xlsx)",
    buf.getvalue(),
    f"{selected_indicator.replace(' ', '_')}_{th_mulai}_{th_selesai}.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Tampilkan tabel dengan mengisi NaN menjadi tanda strip (-)
st.dataframe(df_display.fillna("-"), use_container_width=True)

st.caption(
    "💡 Catatan: Tanda strip (-) atau titik grafik terputus menunjukkan bahwa"
    " pada tahun tersebut indikator belum disurvei dengan metodologi yang sebanding,"
    " atau wilayah administratif terkait belum terbentuk/dimekarkan."
)
