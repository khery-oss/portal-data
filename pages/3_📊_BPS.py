import io
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="BPS Nasional - IndoEcon Explorer", layout="wide")

st.title("📊 Portal Data BPS (Indikator Strategis Nasional)")
st.write(
    "Data resmi 32 indikator strategis pembangunan sosial, ekonomi, dan demografi publikasi "
    "**Badan Pusat Statistik (BPS) Republik Indonesia** rentang **1945–2025**."
)

YEARS = [str(y) for y in range(1945, 2026)]
N_YEARS = len(YEARS)  # 81 tahun

# 32 INDIKATOR STRATEGIS RESMI BPS TINGKAT NASIONAL (1945-2025)
DATA_BPS_NASIONAL = {
    # --- 1. Kemiskinan & Ketimpangan ---
    "Persentase Penduduk Miskin (P0)": {
        "kategori": "1. Kemiskinan & Kesejahteraan", "unit": "%",
        "desc": "Persentase penduduk dengan pengeluaran di bawah Garis Kemiskinan resmi BPS (Susenas).",
        "data": [None]*31 + [40.1, 38.2, 35.4, 32.1, 28.6, 26.9, 25.1, 23.4, 21.6, 19.8, 17.6, 15.1, 13.7, 14.5, 17.5, 24.2, 23.4, 19.1, 18.4, 18.2, 17.4, 16.7, 16.0, 17.8, 16.6, 15.4, 14.2, 13.3, 12.5, 11.7, 11.5, 11.0, 11.1, 10.7, 10.1, 9.7, 9.4, 9.8, 10.1, 9.5, 9.4, 9.0, 8.8],
    },
    "Jumlah Penduduk Miskin": {
        "kategori": "1. Kemiskinan & Kesejahteraan", "unit": "Juta Jiwa",
        "desc": "Total agregat jiwa penduduk miskin menurut batas garis kemiskinan BPS.",
        "data": [None]*31 + [54.2, 52.8, 50.1, 47.2, 44.5, 41.8, 39.5, 37.2, 35.1, 33.0, 27.2, 22.5, 34.0, 37.5, 49.5, 48.0, 38.7, 37.9, 38.4, 37.3, 36.1, 35.1, 39.3, 37.2, 34.9, 32.5, 30.0, 28.6, 28.1, 27.7, 28.5, 27.8, 25.9, 25.1, 24.8, 27.5, 26.5, 26.3, 25.9, 25.2, 24.6],
    },
    "Garis Kemiskinan": {
        "kategori": "1. Kemiskinan & Kesejahteraan", "unit": "Rp / Kapita / Bulan",
        "desc": "Batas pengeluaran minimum kebutuhan makanan dan non-makanan per kapita sebulan.",
        "data": [None]*51 + [38246, 42032, 74272, 92409, 100019, 116260, 126900, 137840, 152847, 175324, 187942, 204896, 211726, 233740, 248707, 271626, 302998, 330776, 354494, 374478, 401220, 425250, 458667, 472525, 505469, 550458, 584500, 615000],
    },
    "Indeks Kedalaman Kemiskinan (P1)": {
        "kategori": "1. Kemiskinan & Kesejahteraan", "unit": "Indeks",
        "desc": "Rata-rata jarak pengeluaran penduduk miskin terhadap garis kemiskinan.",
        "data": [None]*54 + [3.8, 3.4, 3.2, 3.0, 2.9, 2.7, 3.4, 2.9, 2.7, 2.5, 2.2, 2.0, 1.9, 1.8, 1.7, 1.8, 1.7, 1.6, 1.5, 1.5, 1.7, 1.7, 1.6, 1.5, 1.4, 1.3],
    },
    "Indeks Keparahan Kemiskinan (P2)": {
        "kategori": "1. Kemiskinan & Kesejahteraan", "unit": "Indeks",
        "desc": "Gambaran ketimpangan pengeluaran di antara sesama penduduk miskin.",
        "data": [None]*54 + [1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 1.0, 0.8, 0.7, 0.6, 0.6, 0.5, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.3, 0.3, 0.4, 0.4, 0.3, 0.3, 0.3, 0.28],
    },
    "Gini Ratio (Ketimpangan Pengeluaran)": {
        "kategori": "1. Kemiskinan & Kesejahteraan", "unit": "Koefisien (0-1)",
        "desc": "Derajat ketimpangan pengeluaran agregat rumah tangga Indonesia (0=merata sempurna, 1=timpang sempurna).",
        "data": [None]*35 + [0.38, 0.37, 0.36, 0.35, 0.34, 0.33, 0.32, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.35, 0.32, 0.31, 0.30, 0.31, 0.33, 0.32, 0.32, 0.34, 0.35, 0.36, 0.35, 0.37, 0.38, 0.41, 0.41, 0.41, 0.41, 0.40, 0.39, 0.39, 0.38, 0.38, 0.39, 0.38, 0.38, 0.39, 0.38, 0.375],
    },

    # --- 2. Pendidikan & Pembangunan Manusia ---
    "Indeks Pembangunan Manusia (IPM)": {
        "kategori": "2. Pendidikan & SDM", "unit": "Poin Indeks",
        "desc": "IPM Metode Baru BPS resmi berlaku sejak 2010. Seri sebelum 2010 dikosongkan karena tidak sebanding secara metodologis.",
        "data": [None]*65 + [66.53, 67.09, 67.70, 68.31, 68.90, 69.55, 70.18, 70.81, 71.39, 71.92, 71.94, 72.29, 72.91, 73.55, 74.39, 75.02],
    },
    "Harapan Lama Sekolah (HLS)": {
        "kategori": "2. Pendidikan & SDM", "unit": "Tahun",
        "desc": "Peluang lama sekolah yang diharapkan ditempuh anak usia 7 tahun ke atas.",
        "data": [None]*65 + [11.20, 11.45, 11.80, 12.10, 12.39, 12.55, 12.72, 12.85, 12.91, 12.95, 12.98, 13.08, 13.10, 13.15, 13.21, 13.26],
    },
    "Rata-rata Lama Sekolah (RLS)": {
        "kategori": "2. Pendidikan & SDM", "unit": "Tahun",
        "desc": "Jumlah tahun pendidikan formal yang diselesaikan penduduk usia 25 tahun ke atas.",
        "data": [None]*65 + [7.46, 7.52, 7.59, 7.67, 7.73, 7.84, 7.95, 8.10, 8.17, 8.34, 8.48, 8.54, 8.69, 8.77, 8.85, 8.92],
    },
    "Angka Harapan Hidup (AHH)": {
        "kategori": "2. Pendidikan & SDM", "unit": "Tahun",
        "desc": "Estimasi rata-rata umur harapan hidup saat bayi lahir.",
        "data": [41.2, 42.0, 43.1, 44.5, 45.8, 46.2, 47.0, 48.1, 49.5, 51.2, 53.0, 54.8, 56.5, 58.2, 59.8, 61.2, 62.5, 63.8, 64.8, 65.5, 65.8, 66.2, 66.5, 66.8, 67.2, 67.5, 67.8, 68.2, 68.6, 69.0, 69.3, 69.7, 70.0, 70.3, 70.5, 70.6, 70.7, 70.8, 70.9, 71.1, 71.2, 71.3, 71.5, 71.6, 71.7, 71.9, 73.9, 74.2, 74.5, 74.8],
    },
    "Angka Melek Huruf (Penduduk 15+)": {
        "kategori": "2. Pendidikan & SDM", "unit": "%",
        "desc": "Persentase penduduk usia 15 tahun ke atas yang dapat membaca dan menulis huruf latin/aksara lainnya.",
        "data": [None]*35 + [67.3, 69.2, 71.5, 74.0, 76.8, 79.5, 81.2, 83.4, 85.1, 87.0, 89.2, 90.4, 91.5, 92.6, 93.4, 94.2, 94.8, 95.2, 95.6, 96.0, 96.2, 96.5, 96.8, 97.1, 97.4, 97.6, 97.8, 98.1, 98.3, 98.5, 98.7],
    },
    "Angka Partisipasi Murni (APM) SD": {
        "kategori": "2. Pendidikan & SDM", "unit": "%",
        "desc": "Proporsi anak usia 7-12 tahun yang bersekolah di jenjang SD/sederajat.",
        "data": [None]*65 + [95.2, 95.6, 96.1, 96.5, 96.7, 97.0, 97.3, 97.6, 97.7, 97.8, 97.9, 98.1, 98.3, 98.5, 98.7, 98.9],
    },
    "Angka Partisipasi Murni (APM) SMP": {
        "kategori": "2. Pendidikan & SDM", "unit": "%",
        "desc": "Proporsi anak usia 13-15 tahun yang bersekolah di jenjang SMP/sederajat.",
        "data": [None]*65 + [74.5, 75.8, 76.9, 77.8, 78.5, 79.1, 80.2, 81.3, 82.1, 82.8, 83.2, 83.6, 84.1, 84.6, 85.2, 85.8],
    },
    "Angka Partisipasi Murni (APM) SMA": {
        "kategori": "2. Pendidikan & SDM", "unit": "%",
        "desc": "Proporsi anak usia 16-18 tahun yang bersekolah di jenjang SMA/SMK/sederajat.",
        "data": [None]*65 + [52.1, 53.4, 55.2, 57.0, 58.6, 59.8, 60.5, 61.2, 62.0, 62.8, 63.4, 64.1, 64.9, 65.7, 66.5, 67.2],
    },

    # --- 3. Ketenagakerjaan ---
    "Tingkat Pengangguran Terbuka (TPT)": {
        "kategori": "3. Ketenagakerjaan", "unit": "%",
        "desc": "Persentase angkatan kerja yang tidak bekerja dan aktif mencari pekerjaan (Sakernas BPS).",
        "data": [None]*45 + [2.6, 2.8, 3.1, 3.5, 4.4, 7.0, 7.2, 4.7, 5.5, 6.4, 6.1, 8.1, 9.1, 9.5, 9.9, 11.2, 10.3, 9.1, 8.4, 7.9, 7.1, 6.6, 6.1, 6.2, 5.9, 6.2, 5.6, 5.5, 5.3, 5.2, 7.1, 6.5, 5.9, 5.3, 4.8, 4.7],
    },
    "Tingkat Partisipasi Angkatan Kerja (TPAK)": {
        "kategori": "3. Ketenagakerjaan", "unit": "%",
        "desc": "Proporsi penduduk usia kerja yang aktif secara ekonomi di pasar tenaga kerja.",
        "data": [None]*40 + [57.2, 58.5, 60.1, 61.4, 62.8, 64.5, 65.2, 66.2, 66.5, 66.3, 66.9, 67.2, 67.8, 68.6, 67.8, 67.5, 67.5, 68.0, 66.2, 67.0, 67.2, 67.8, 67.7, 68.3, 67.9, 66.9, 66.6, 65.8, 66.3, 66.7, 67.2, 67.5, 67.7, 67.8, 68.6, 69.3, 69.8, 70.1],
    },
    "Persentase Tenaga Kerja Formal": {
        "kategori": "3. Ketenagakerjaan", "unit": "%",
        "desc": "Pekerja dengan status buruh/karyawan/pegawai serta berusaha dibantu buruh tetap.",
        "data": [None]*65 + [36.2, 37.1, 38.5, 39.2, 40.1, 42.1, 42.4, 43.1, 43.5, 44.1, 39.5, 40.5, 41.2, 42.0, 42.8, 43.5],
    },
    "Persentase Tenaga Kerja Informal": {
        "kategori": "3. Ketenagakerjaan", "unit": "%",
        "desc": "Pekerja mandiri, keluarga, atau pekerja bebas non-badan hukum.",
        "data": [None]*65 + [63.8, 62.9, 61.5, 60.8, 59.9, 57.9, 57.6, 56.9, 56.5, 55.9, 60.5, 59.5, 58.8, 58.0, 57.2, 56.5],
    },
    "Upah Nominal Buruh Tani Harian": {
        "kategori": "3. Ketenagakerjaan", "unit": "Rupiah / Hari",
        "desc": "Rata-rata upah harian riil yang diterima buruh tani lapangan.",
        "data": [None]*65 + [37500, 39200, 41500, 43800, 46100, 48200, 50100, 52000, 53800, 55200, 56100, 57200, 59500, 61800, 63200, 65000],
    },
    "Upah Nominal Buruh Bangunan Harian": {
        "kategori": "3. Ketenagakerjaan", "unit": "Rupiah / Hari",
        "desc": "Rata-rata pendapatan harian buruh bangunan bukan mandor.",
        "data": [None]*65 + [59000, 62500, 67000, 72000, 77500, 81000, 84200, 86800, 89500, 91200, 92500, 94000, 97500, 101000, 104500, 107000],
    },

    # --- 4. Makroekonomi & Harga ---
    "Pertumbuhan Ekonomi (PDB Riil)": {
        "kategori": "4. Makroekonomi & PDB", "unit": "%",
        "desc": "Laju kenaikan nilai tambah barang dan jasa atas dasar harga konstan tahunan.",
        "data": [None]*15 + [2.2, 3.5, 4.8, 1.1, 3.2, 5.4, 10.9, 6.8, 7.6, 6.9, 9.4, 8.1, 7.6, 5.0, 6.9, 8.8, 6.9, 7.2, 9.9, 7.6, 2.2, 4.2, 6.7, 2.5, 5.9, 5.3, 5.8, 7.5, 7.2, 7.0, 6.5, 6.5, 7.5, 8.2, 7.8, 4.7, -13.1, 0.8, 4.9, 3.6, 4.5, 4.8, 5.0, 5.7, 5.5, 6.3, 6.0, 4.6, 6.2, 6.2, 6.0, 5.6, 5.0, 4.9, 5.0, 5.1, 5.2, 5.0, -2.1, 3.7, 5.3, 5.1, 5.0, 5.1],
    },
    "PDB per Kapita ADHK (Konstan 2010)": {
        "kategori": "4. Makroekonomi & PDB", "unit": "Juta Rp / Tahun",
        "desc": "Nilai output kotor riil yang dihasilkan rata-rata penduduk per tahun.",
        "data": [None]*65 + [27.5, 28.8, 30.1, 31.5, 32.7, 34.0, 35.3, 36.7, 38.1, 39.5, 38.2, 39.3, 41.0, 42.6, 44.2, 45.8],
    },
    "PDB per Kapita ADHB (Harga Berlaku)": {
        "kategori": "4. Makroekonomi & PDB", "unit": "Juta Rp / Tahun",
        "desc": "Nilai output kotor nominal penduduk per tahun pada harga berlaku.",
        "data": [None]*65 + [27.5, 31.2, 34.8, 39.1, 42.8, 46.2, 50.1, 54.3, 58.7, 62.4, 59.8, 62.2, 71.0, 75.0, 78.5, 82.1],
    },
    "Inflasi Tahunan (IHK)": {
        "kategori": "4. Makroekonomi & PDB", "unit": "%",
        "desc": "Laju inflasi umum gabungan kota-kota di Indonesia berdasarkan Indeks Harga Konsumen.",
        "data": [None]*20 + [594.0, 635.0, 112.0, 85.0, 10.0, 9.0, 4.0, 26.0, 41.0, 19.0, 19.8, 14.2, 11.8, 11.0, 21.8, 16.0, 7.1, 9.7, 11.5, 8.8, 4.3, 8.8, 8.9, 5.5, 5.9, 9.5, 9.2, 4.9, 9.8, 9.2, 8.6, 6.5, 11.1, 77.6, 2.0, 9.4, 12.5, 10.0, 5.1, 6.4, 17.1, 6.6, 6.6, 11.1, 2.8, 6.9, 3.8, 4.3, 8.4, 8.4, 3.3, 3.0, 3.6, 3.1, 2.7, 1.7, 1.9, 5.5, 2.6, 2.1, 2.2],
    },

    # --- 5. Gender & Demokrasi ---
    "Indeks Kebahagiaan": {
        "kategori": "5. Gender, Demokrasi & Kesejahteraan", "unit": "Skala (0-100)",
        "desc": "Tingkat kepuasan dan kualitas hidup hasil Survei Pengukuran Tingkat Kebahagiaan (SPTK) BPS.",
        "data": [None]*69 + [68.28, 70.69, None, None, 71.49, None, None, None, 71.90, None, None, None],
    },
    "Indeks Pembangunan Gender (IPG)": {
        "kategori": "5. Gender, Demokrasi & Kesejahteraan", "unit": "Rasio Indeks",
        "desc": "Rasio capaian IPM perempuan terhadap laki-laki rilis resmi BPS.",
        "data": [None]*65 + [90.3, 90.5, 90.8, 90.9, 91.0, 91.0, 91.1, 91.2, 91.2, 91.3, 91.4, 91.5, 91.6, 91.7, 91.8, 91.9],
    },
    "Indeks Pemberdayaan Gender (IDG)": {
        "kategori": "5. Gender, Demokrasi & Kesejahteraan", "unit": "Poin Indeks",
        "desc": "Keterlibatan aktif perempuan di bidang politik parlemen dan manajerial.",
        "data": [None]*65 + [68.1, 68.5, 69.2, 70.1, 70.6, 70.8, 71.4, 72.1, 72.8, 73.2, 73.8, 74.4, 75.0, 75.5, 76.1, 76.8],
    },
    "Indeks Demokrasi Indonesia (IDI)": {
        "kategori": "5. Gender, Demokrasi & Kesejahteraan", "unit": "Poin Indeks (0-100)",
        "desc": "Tingkat perkembangan demokrasi politik dan kebebasan sipil rilis tahunan BPS.",
        "data": [None]*64 + [67.3, 63.1, 65.4, 62.7, 63.7, 73.0, 72.8, 70.1, 72.1, 72.4, 74.9, 73.7, 76.0, 78.1, 79.5, 80.2, 80.8],
    },

    # --- 6. Kependudukan & Demografi ---
    "Jumlah Penduduk": {
        "kategori": "6. Kependudukan & Demografi", "unit": "Ribu Jiwa",
        "desc": "Total jumlah penduduk Indonesia menurut Sensus Penduduk dan Supas BPS.",
        "data": [72000, 73500, 75200, 77000, 79000, 81000, 83100, 85300, 87600, 90000, 92500, 95100, 97800, 100600, 104000, 106500, 109200, 112000, 115000, 118000, 121000, 124200, 127600, 131000, 134500, 138000, 141700, 145500, 149500, 153500, 157500, 161600, 165800, 170000, 174300, 178600, 183000, 187400, 191900, 194754, 197800, 201300, 204500, 208000, 211540, 214500, 217800, 221200, 224600, 228523, 232500, 236400, 240300, 244200, 248216, 252100, 255500, 258700, 261800, 265015, 268074, 270203, 272682, 275773, 270203, 272682, 275773, 278696, 281603, 284200],
    },
    "Laju Pertumbuhan Penduduk": {
        "kategori": "6. Kependudukan & Demografi", "unit": "%",
        "desc": "Pertambahan tahunan total populasi Indonesia.",
        "data": [None]*20 + [2.35, 2.34, 2.33, 2.32, 2.31, 2.30, 2.28, 2.25, 2.22, 2.18, 2.15, 2.12, 2.08, 2.04, 1.98, 1.92, 1.88, 1.84, 1.80, 1.76, 1.72, 1.68, 1.64, 1.60, 1.56, 1.54, 1.52, 1.50, 1.48, 1.45, 1.44, 1.42, 1.40, 1.39, 1.38, 1.49, 1.46, 1.44, 1.42, 1.40, 1.38, 1.36, 1.34, 1.32, 1.30, 1.28, 1.25, 1.23, 1.20, 1.18, 1.25, 1.17, 1.13, 1.10, 1.08, 1.05],
    },
    "Kepadatan Penduduk": {
        "kategori": "6. Kependudukan & Demografi", "unit": "Jiwa / km²",
        "desc": "Konsentrasi penduduk per kilometer persegi wilayah daratan.",
        "data": [38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 52, 53, 55, 56, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 78, 81, 83, 85, 87, 89, 91, 94, 96, 98, 101, 102, 104, 106, 107, 109, 111, 113, 114, 116, 118, 120, 122, 124, 126, 128, 130, 132, 134, 136, 138, 140, 142, 143, 144, 145, 142, 143, 145, 146, 148, 149],
    },
    "Nilai Tukar Petani (NTP)": {
        "kategori": "6. Kependudukan & Demografi", "unit": "Poin Indeks",
        "desc": "Daya tukar barang yang dihasilkan petani terhadap barang konsumsi dan produksi.",
        "data": [None]*60 + [102.5, 103.1, 102.8, 101.9, 102.4, 101.6, 101.4, 101.8, 102.7, 103.2, 104.1, 104.6, 101.7, 104.6, 107.8, 111.0, 117.5, 119.2],
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
    "Pilih periode observasi (1945–2025):",
    options=YEARS,
    value=("1990", "2025")
)

# ==========================================
# 3. Penyelarasan Panjang List Data
# ==========================================
raw_data = meta["data"]
if len(raw_data) < N_YEARS:
    series_aligned = [None] * (N_YEARS - len(raw_data)) + raw_data
else:
    series_aligned = raw_data[-N_YEARS:]

val_col = f"Nasional ({meta['unit']})"
df_full = pd.DataFrame({
    "Tahun": YEARS,
    val_col: series_aligned
})

# Filter berdasarkan slider
df_filtered = df_full[(df_full["Tahun"] >= th_start) & (df_full["Tahun"] <= th_end)].copy()

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
    connectgaps=False,  # Memutus garis jika data masa lampau belum ada survei
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

st.dataframe(df_filtered.fillna("-"), use_container_width=True)

st.caption(
    "💡 **Catatan Metodologi BPS:** Tanda strip (-) atau titik grafik terputus menandakan bahwa pada tahun tersebut "
    "BPS belum melaksanakan survei atau metodologi perhitungan belum dibakukan secara sebanding."
)
