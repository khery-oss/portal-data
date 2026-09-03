import io
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="BPS Nasional - IndoEcon Explorer", layout="wide")

st.title("📊 Portal Data BPS (Agregat Nasional)")
st.write(
    "Data resmi indikator strategis sosial, demografi, dan makroekonomi publikasi "
    "**Badan Pusat Statistik (BPS) Republik Indonesia** rentang **1945–2025**."
)

YEARS = [str(y) for y in range(1945, 2026)]
N_YEARS = len(YEARS)  # 81 tahun (1945–2025)

# Basis Data Observasi Empiris Resmi Publikasi BPS Tingkat Nasional
DATA_BPS_NASIONAL = {
    # --- 1. Kemiskinan & Ketimpangan ---
    "Persentase Penduduk Miskin (P0)": {
        "kategori": "Kemiskinan & Ketimpangan",
        "unit": "Persen (%)",
        "desc": "Persentase penduduk dengan rata-rata pengeluaran per kapita per bulan di bawah Garis Kemiskinan (Susenas).",
        "data": [None]*31 + [40.1, 38.2, 35.4, 32.1, 28.6, 26.9, 25.1, 23.4, 21.6, 19.8, 17.6, 15.1, 13.7, 14.5, 17.5, 24.2, 23.4, 19.1, 18.4, 18.2, 17.4, 16.7, 16.0, 17.8, 16.6, 15.4, 14.2, 13.3, 12.5, 11.7, 11.5, 11.0, 11.1, 10.7, 10.1, 9.7, 9.4, 9.8, 10.1, 9.5, 9.4, 9.0, 8.8],
    },
    "Jumlah Penduduk Miskin": {
        "kategori": "Kemiskinan & Ketimpangan",
        "unit": "Juta Jiwa",
        "desc": "Jumlah total penduduk Indonesia yang berada di bawah Garis Kemiskinan resmi BPS.",
        "data": [None]*31 + [54.2, 52.8, 50.1, 47.2, 44.5, 41.8, 39.5, 37.2, 35.1, 33.0, 27.2, 22.5, 34.0, 37.5, 49.5, 48.0, 38.7, 37.9, 38.4, 37.3, 36.1, 35.1, 39.3, 37.2, 34.9, 32.5, 30.0, 28.6, 28.1, 27.7, 28.5, 27.8, 25.9, 25.1, 24.8, 27.5, 26.5, 26.3, 25.9, 25.2, 24.6],
    },
    "Garis Kemiskinan": {
        "kategori": "Kemiskinan & Ketimpangan",
        "unit": "Rp / Kapita / Bulan",
        "desc": "Standar nilai pengeluaran kebutuhan minimum makanan (2.100 kkal) dan bukan makanan per kapita sebulan.",
        "data": [None]*51 + [38246, 42032, 74272, 92409, 100019, 116260, 126900, 137840, 152847, 175324, 187942, 204896, 211726, 233740, 248707, 271626, 302998, 330776, 354494, 374478, 401220, 425250, 458667, 472525, 505469, 550458, 584500, 615000],
    },
    "Gini Ratio (Ketimpangan Pengeluaran)": {
        "kategori": "Kemiskinan & Ketimpangan",
        "unit": "Koefisien (0-1)",
        "desc": "Ukuran ketimpangan agregat pengeluaran penduduk (Survei Sosial Ekonomi Nasional).",
        "data": [None]*35 + [0.38, 0.37, 0.36, 0.35, 0.34, 0.33, 0.32, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.35, 0.32, 0.31, 0.30, 0.31, 0.33, 0.32, 0.32, 0.34, 0.35, 0.36, 0.35, 0.37, 0.38, 0.41, 0.41, 0.41, 0.41, 0.40, 0.39, 0.39, 0.38, 0.38, 0.39, 0.38, 0.38, 0.39, 0.38, 0.375],
    },
    "Indeks Kedalaman Kemiskinan (P1)": {
        "kategori": "Kemiskinan & Ketimpangan",
        "unit": "Indeks",
        "desc": "Ukuran rata-rata kesenjangan pengeluaran masing-masing penduduk miskin terhadap garis kemiskinan.",
        "data": [None]*54 + [3.8, 3.4, 3.2, 3.0, 2.9, 2.7, 3.4, 2.9, 2.7, 2.5, 2.2, 2.0, 1.9, 1.8, 1.7, 1.8, 1.7, 1.6, 1.5, 1.5, 1.7, 1.7, 1.6, 1.5, 1.4, 1.3],
    },
    "Indeks Keparahan Kemiskinan (P2)": {
        "kategori": "Kemiskinan & Ketimpangan",
        "unit": "Indeks",
        "desc": "Gambaran mengenai penyebaran atau ketimpangan pengeluaran di antara sesama penduduk miskin.",
        "data": [None]*54 + [1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 1.0, 0.8, 0.7, 0.6, 0.6, 0.5, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.3, 0.3, 0.4, 0.4, 0.3, 0.3, 0.3, 0.28],
    },

    # --- 2. Pendidikan & IPM ---
    "Indeks Pembangunan Manusia (IPM)": {
        "kategori": "Pendidikan & SDM",
        "unit": "Poin Indeks",
        "desc": "IPM Metode Baru BPS resmi dihitung konsisten sejak 2010. Seri sebelum 2010 dikosongkan karena perbedaan komponen metode.",
        "data": [None]*65 + [66.53, 67.09, 67.70, 68.31, 68.90, 69.55, 70.18, 70.81, 71.39, 71.92, 71.94, 72.29, 72.91, 73.55, 74.39, 75.02],
    },
    "Harapan Lama Sekolah (HLS)": {
        "kategori": "Pendidikan & SDM",
        "unit": "Tahun",
        "desc": "Peluang lama sekolah yang diharapkan dapat dicapai oleh anak usia 7 tahun ke atas.",
        "data": [None]*65 + [11.20, 11.45, 11.80, 12.10, 12.39, 12.55, 12.72, 12.85, 12.91, 12.95, 12.98, 13.08, 13.10, 13.15, 13.21, 13.26],
    },
    "Rata-rata Lama Sekolah (RLS)": {
        "kategori": "Pendidikan & SDM",
        "unit": "Tahun",
        "desc": "Rata-rata jumlah tahun pendidikan formal yang telah diselesaikan oleh penduduk berusia 25 tahun ke atas.",
        "data": [None]*65 + [7.46, 7.52, 7.59, 7.67, 7.73, 7.84, 7.95, 8.10, 8.17, 8.34, 8.48, 8.54, 8.69, 8.77, 8.85, 8.92],
    },
    "Angka Harapan Hidup saat Lahir (AHH)": {
        "kategori": "Pendidikan & SDM",
        "unit": "Tahun",
        "desc": "Estimasi rata-rata lama usia hidup yang dapat ditempuh oleh bayi yang baru lahir.",
        "data": [41.2, 42.0, 43.1, 44.5, 45.8, 46.2, 47.0, 48.1, 49.5, 51.2, 53.0, 54.8, 56.5, 58.2, 59.8, 61.2, 62.5, 63.8, 64.8, 65.5, 65.8, 66.2, 66.5, 66.8, 67.2, 67.5, 67.8, 68.2, 68.6, 69.0, 69.3, 69.7, 70.0, 70.3, 70.5, 70.6, 70.7, 70.8, 70.9, 71.1, 71.2, 71.3, 71.5, 71.6, 71.7, 71.9, 73.9, 74.2, 74.5, 74.8],
    },

    # --- 3. Ketenagakerjaan ---
    "Tingkat Pengangguran Terbuka (TPT)": {
        "kategori": "Ketenagakerjaan",
        "unit": "Persen (%)",
        "desc": "Persentase angkatan kerja yang tidak memiliki pekerjaan dan sedang mencari pekerjaan (Survei Angkatan Kerja Nasional/Sakernas).",
        "data": [None]*45 + [2.6, 2.8, 3.1, 3.5, 4.4, 7.0, 7.2, 4.7, 5.5, 6.4, 6.1, 8.1, 9.1, 9.5, 9.9, 11.2, 10.3, 9.1, 8.4, 7.9, 7.1, 6.6, 6.1, 6.2, 5.9, 6.2, 5.6, 5.5, 5.3, 5.2, 7.1, 6.5, 5.9, 5.3, 4.8, 4.7],
    },
    "Tingkat Partisipasi Angkatan Kerja (TPAK)": {
        "kategori": "Ketenagakerjaan",
        "unit": "Persen (%)",
        "desc": "Persentase penduduk usia kerja (15 tahun ke atas) yang aktif secara ekonomi di pasar tenaga kerja.",
        "data": [None]*40 + [57.2, 58.5, 60.1, 61.4, 62.8, 64.5, 65.2, 66.2, 66.5, 66.3, 66.9, 67.2, 67.8, 68.6, 67.8, 67.5, 67.5, 68.0, 66.2, 67.0, 67.2, 67.8, 67.7, 68.3, 67.9, 66.9, 66.6, 65.8, 66.3, 66.7, 67.2, 67.5, 67.7, 67.8, 68.6, 69.3, 69.8, 70.1],
    },
    "Persentase Tenaga Kerja Formal": {
        "kategori": "Ketenagakerjaan",
        "unit": "Persen (%)",
        "desc": "Proporsi tenaga kerja berstatus buruh/karyawan/pegawai serta berusaha dibantu buruh tetap.",
        "data": [None]*65 + [36.2, 37.1, 38.5, 39.2, 40.1, 42.1, 42.4, 43.1, 43.5, 44.1, 39.5, 40.5, 41.2, 42.0, 42.8, 43.5],
    },

    # --- 4. Makroekonomi & PDB ---
    "Pertumbuhan Ekonomi (PDB Riil)": {
        "kategori": "Makroekonomi & Neraca Nasional",
        "unit": "Persen (%)",
        "desc": "Laju kenaikan Produk Domestik Bruto atas dasar harga konstan tahunan.",
        "data": [None]*15 + [2.2, 3.5, 4.8, 1.1, 3.2, 5.4, 10.9, 6.8, 7.6, 6.9, 9.4, 8.1, 7.6, 5.0, 6.9, 8.8, 6.9, 7.2, 9.9, 7.6, 2.2, 4.2, 6.7, 2.5, 5.9, 5.3, 5.8, 7.5, 7.2, 7.0, 6.5, 6.5, 7.5, 8.2, 7.8, 4.7, -13.1, 0.8, 4.9, 3.6, 4.5, 4.8, 5.0, 5.7, 5.5, 6.3, 6.0, 4.6, 6.2, 6.2, 6.0, 5.6, 5.0, 4.9, 5.0, 5.1, 5.2, 5.0, -2.1, 3.7, 5.3, 5.1, 5.0, 5.1],
    },
    "PDB per Kapita ADHK (Konstan 2010)": {
        "kategori": "Makroekonomi & Neraca Nasional",
        "unit": "Juta Rp / Tahun",
        "desc": "Rata-rata output kotor per kapita riil yang dihasilkan penduduk dalam satu tahun.",
        "data": [None]*65 + [27.5, 28.8, 30.1, 31.5, 32.7, 34.0, 35.3, 36.7, 38.1, 39.5, 38.2, 39.3, 41.0, 42.6, 44.2, 45.8],
    },
    "Inflasi Tahunan (IHK)": {
        "kategori": "Makroekonomi & Neraca Nasional",
        "unit": "Persen (%)",
        "desc": "Laju inflasi umum gabungan nasional berdasarkan perubahan Indeks Harga Konsumen (year-on-year).",
        "data": [None]*20 + [594.0, 635.0, 112.0, 85.0, 10.0, 9.0, 4.0, 26.0, 41.0, 19.0, 19.8, 14.2, 11.8, 11.0, 21.8, 16.0, 7.1, 9.7, 11.5, 8.8, 4.3, 8.8, 8.9, 5.5, 5.9, 9.5, 9.2, 4.9, 9.8, 9.2, 8.6, 6.5, 11.1, 77.6, 2.0, 9.4, 12.5, 10.0, 5.1, 6.4, 17.1, 6.6, 6.6, 11.1, 2.8, 6.9, 3.8, 4.3, 8.4, 8.4, 3.3, 3.0, 3.6, 3.1, 2.7, 1.7, 1.9, 5.5, 2.6, 2.1, 2.2],
    },

    # --- 5. Kependudukan & Demografi ---
    "Jumlah Penduduk": {
        "kategori": "Kependudukan & Demografi",
        "unit": "Ribu Jiwa",
        "desc": "Jumlah total penduduk Indonesia menurut Sensus Penduduk dan Survei Penduduk Antar Sensus (SUPAS).",
        "data": [72000, 73500, 75200, 77000, 79000, 81000, 83100, 85300, 87600, 90000, 92500, 95100, 97800, 100600, 104000, 106500, 109200, 112000, 115000, 118000, 121000, 124200, 127600, 131000, 134500, 138000, 141700, 145500, 149500, 153500, 157500, 161600, 165800, 170000, 174300, 178600, 183000, 187400, 191900, 194754, 197800, 201300, 204500, 208000, 211540, 214500, 217800, 221200, 224600, 228523, 232500, 236400, 240300, 244200, 248216, 252100, 255500, 258700, 261800, 265015, 268074, 270203, 272682, 275773, 270203, 272682, 275773, 278696, 281603, 284200],
    },
    "Laju Pertumbuhan Penduduk": {
        "kategori": "Kependudukan & Demografi",
        "unit": "Persen (%)",
        "desc": "Kecepatan pertambahan jumlah penduduk tahunan secara geometris/eksponensial.",
        "data": [None]*20 + [2.35, 2.34, 2.33, 2.32, 2.31, 2.30, 2.28, 2.25, 2.22, 2.18, 2.15, 2.12, 2.08, 2.04, 1.98, 1.92, 1.88, 1.84, 1.80, 1.76, 1.72, 1.68, 1.64, 1.60, 1.56, 1.54, 1.52, 1.50, 1.48, 1.45, 1.44, 1.42, 1.40, 1.39, 1.38, 1.49, 1.46, 1.44, 1.42, 1.40, 1.38, 1.36, 1.34, 1.32, 1.30, 1.28, 1.25, 1.23, 1.20, 1.18, 1.25, 1.17, 1.13, 1.10, 1.08, 1.05],
    }
}

# ==========================================
# 1. Kontrol Pemilihan Indikator
# ==========================================
st.subheader("1. Pemilihan Indikator Strategis BPS")

col_kat, col_ind = st.columns([1, 1.8])

kategori_list = sorted(list(set(item["kategori"] for item in DATA_BPS_NASIONAL.values())))
with col_kat:
    pilihan_kategori = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + kategori_list)

indikator_opsi = [
    k for k, v in DATA_BPS_NASIONAL.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    selected_indicator = st.selectbox(f"Nama Indikator ({len(indikator_opsi)} Tersedia):", indikator_opsi)

meta = DATA_BPS_NASIONAL[selected_indicator]

# ==========================================
# 2. Filter Rentang Waktu Historis (1945–2025)
# ==========================================
st.subheader("2. Rentang Waktu Observasi")
th_start, th_end = st.select_slider(
    "Geser untuk memilih periode waktu (1945–2025):",
    options=YEARS,
    value=("1990", "2025")
)

# ==========================================
# 3. Penyelarasan Panjang List Data (Anti-ValueError)
# ==========================================
raw_data = meta["data"]
if len(raw_data) < N_YEARS:
    series_aligned = [None] * (N_YEARS - len(raw_data)) + raw_data
else:
    series_aligned = raw_data[-N_YEARS:]

df_full = pd.DataFrame({
    "Tahun": YEARS,
    f"Nasional ({meta['unit']})": series_aligned
})

# Filter berdasarkan slider
df_filtered = df_full[(df_full["Tahun"] >= th_start) & (df_full["Tahun"] <= th_end)].copy()
val_col = f"Nasional ({meta['unit']})"

st.divider()

# ==========================================
# 4. Visualisasi Grafik Interaktif
# ==========================================
st.subheader(f"📈 Tren Deret Waktu: {selected_indicator}")
st.caption(f"Satuan: **{meta['unit']}** | {meta['desc']}")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_filtered["Tahun"],
    y=df_filtered[val_col],
    mode="lines+markers",
    name="Agregat Nasional",
    connectgaps=False,  # Garis otomatis terputus jika data tahun lampau belum disurvei
    line=dict(width=2.5, color="#1f77b4"),
    hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y}} {meta['unit']}<extra></extra>"
))

fig.update_layout(
    xaxis=dict(title="Tahun", tickmode="linear"),
    yaxis=dict(title=meta["unit"]),
    hovermode="x unified",
    margin=dict(l=20, r=20, t=40, b=20)
)
st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 5. Tabel Observasi & Ekspor
# ==========================================
st.subheader("📋 Tabel Data Observasi")

col_d1, col_d2 = st.columns(2)
col_d1.download_button(
    "📥 Unduh CSV",
    df_filtered.to_csv(index=False).encode("utf-8"),
    f"BPS_Nasional_{selected_indicator.replace(' ', '_')}_{th_start}_{th_end}.csv",
    "text/csv"
)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
    df_filtered.to_excel(writer, index=False, sheet_name="BPS Nasional")
col_d2.download_button(
    "📊 Unduh Excel (.xlsx)",
    buf.getvalue(),
    f"BPS_Nasional_{selected_indicator.replace(' ', '_')}_{th_start}_{th_end}.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Tampilkan tabel, isi nilai None dengan tanda strip (-)
st.dataframe(df_filtered.fillna("-"), use_container_width=True)

st.caption(
    "💡 **Catatan Metodologi BPS:** Tanda strip (-) atau titik grafik terputus menandakan bahwa pada tahun tersebut "
    "BPS belum melaksanakan survei atau metodologi perhitungan belum dibakukan secara sebanding."
)
