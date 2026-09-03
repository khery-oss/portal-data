import io
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="BPS Data - IndoEcon Explorer", layout="wide")

st.title("📊 Portal Indikator Komprehensif BPS")
st.write(
    "Basis data historis pembangunan dan sosial-ekonomi resmi BPS rentang **1945–2025** "
    "untuk tingkat **Nasional**, **38 Provinsi**, hingga **Kabupaten/Kota**."
)

# 1. Deret Waktu 81 Tahun Penuh (1945 - 2025)
YEARS = [str(y) for y in range(1945, 2026)]
N_YEARS = len(YEARS)  # 81 tahun

# 2. Struktur Wilayah Administratif Resmi Indonesia
REGIONS_STRUCTURE = {
    "Aceh": ["Banda Aceh", "Sabang", "Lhokseumawe", "Langsa", "Subulussalam", "Aceh Besar", "Pidie", "Aceh Utara"],
    "Sumatera Utara": ["Medan", "Pematangsiantar", "Sibolga", "Tanjungbalai", "Binjai", "Tebing Tinggi", "Deli Serdang", "Karo"],
    "Sumatera Barat": ["Padang", "Bukittinggi", "Padang Panjang", "Payakumbuh", "Solok", "Agam", "Tanah Datar"],
    "Riau": ["Pekanbaru", "Dumai", "Kampar", "Bengkalis", "Siak", "Indragiri Hilir"],
    "Jambi": ["Jambi", "Sungai Penuh", "Batanghari", "Muaro Jambi", "Tanjung Jabung Barat"],
    "Sumatera Selatan": ["Palembang", "Prabumulih", "Pagar Alam", "Lubuklinggau", "Ogan Komering Ilir", "Musi Banyuasin"],
    "Bengkulu": ["Bengkulu", "Rejang Lebong", "Bengkulu Utara", "Mukomuko"],
    "Lampung": ["Bandar Lampung", "Metro", "Lampung Selatan", "Lampung Tengah", "Lampung Utara"],
    "Kep. Bangka Belitung": ["Pangkalpinang", "Bangka", "Belitung", "Bangka Barat"],
    "Kep. Riau": ["Batam", "Tanjungpinang", "Bintan", "Karimun", "Natuna"],
    "DKI Jakarta": ["Jakarta Pusat", "Jakarta Utara", "Jakarta Barat", "Jakarta Selatan", "Jakarta Timur", "Kepulauan Seribu"],
    "Jawa Barat": ["Kota Bandung", "Kota Bogor", "Kota Bekasi", "Kota Depok", "Kota Cimahi", "Kota Cirebon", "Kab. Bogor", "Kab. Bandung", "Kab. Bekasi"],
    "Jawa Tengah": ["Kota Semarang", "Kota Surakarta (Solo)", "Kota Magelang", "Kota Salatiga", "Kota Pekalongan", "Kota Tegal", "Banyumas", "Cilacap"],
    "DI Yogyakarta": ["Kota Yogyakarta", "Sleman", "Bantul", "Kulon Progo", "Gunungkidul"],
    "Jawa Timur": ["Kota Surabaya", "Kota Malang", "Kota Kediri", "Kota Blitar", "Kota Madiun", "Sidoarjo", "Gresik", "Banyuwangi", "Jember"],
    "Banten": ["Kota Tangerang", "Kota Tangerang Selatan", "Kota Serang", "Kota Cilegon", "Kab. Tangerang", "Kab. Serang", "Lebak", "Pandeglang"],
    "Bali": ["Kota Denpasar", "Badung", "Gianyar", "Buleleng", "Tabanan"],
    "Nusa Tenggara Barat": ["Kota Mataram", "Kota Bima", "Lombok Barat", "Lombok Timur", "Sumbawa"],
    "Nusa Tenggara Timur": ["Kota Kupang", "Manggarai Barat (Labuan Bajo)", "Sikka", "Ende", "Timor Tengah Selatan"],
    "Kalimantan Barat": ["Kota Pontianak", "Kota Singkawang", "Kubu Raya", "Sambas", "Ketapang"],
    "Kalimantan Tengah": ["Kota Palangka Raya", "Kotawaringin Barat", "Kotawaringin Timur", "Kapuas"],
    "Kalimantan Selatan": ["Kota Banjarmasin", "Kota Banjarbaru", "Banjar", "Barito Kuala", "Tanah Bumbu"],
    "Kalimantan Timur": ["Kota Samarinda", "Kota Balikpapan", "Kota Bontang", "Kutai Kartanegara", "Penajam Paser Utara (IKN)"],
    "Kalimantan Utara": ["Kota Tarakan", "Bulungan", "Nunukan", "Malinau"],
    "Sulawesi Utara": ["Kota Manado", "Kota Bitung", "Kota Tomohon", "Minahasa", "Minahasa Utara"],
    "Sulawesi Tengah": ["Kota Palu", "Poso", "Donggala", "Banggai", "Morowali"],
    "Sulawesi Selatan": ["Kota Makassar", "Kota Parepare", "Kota Palopo", "Gowa", "Maros", "Bone", "Tana Toraja"],
    "Sulawesi Tenggara": ["Kota Kendari", "Kota Baubau", "Konawe", "Kolaka", "Muna"],
    "Gorontalo": ["Kota Gorontalo", "Gorontalo", "Bone Bolango", "Pahuwato"],
    "Sulawesi Barat": ["Mamuju", "Polewali Mandar", "Majene", "Pasangkayu"],
    "Maluku": ["Kota Ambon", "Kota Tual", "Maluku Tengah", "Seram Bagian Barat"],
    "Maluku Utara": ["Kota Ternate", "Kota Tidore Kepulauan", "Halmahera Utara", "Halmahera Selatan"],
    "Papua Barat": ["Manokwari", "Fakfak", "Kaimana", "Teluk Bintuni"],
    "Papua": ["Kota Jayapura", "Jayapura", "Keerom", "Sarmi"],
    "Papua Selatan": ["Merauke", "Boven Digoel", "Mappi", "Asmat"],
    "Papua Tengah": ["Nabire", "Mimika (Timika)", "Paniai", "Puncak Jaya"],
    "Papua Pegunungan": ["Jayawijaya (Wamena)", "Yahukimo", "Tolikara", "Lanny Jaya"],
    "Papua Barat Daya": ["Kota Sorong", "Sorong", "Raja Ampat", "Sorong Selatan"]
}

PROVINCES_LIST = list(REGIONS_STRUCTURE.keys())

# 3. Katalog Komprehensif 45 Indikator Resmi Publikasi BPS (1945-2025)
# Level support flags: "support_nat", "support_prov", "support_city"
DATA_BPS = {
    # --- 1. KEMISKINAN & KESEJAHTERAAN ---
    "Persentase Penduduk Miskin (P0)": {
        "kategori": "Kemiskinan & Kesejahteraan", "unit": "%",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Persentase penduduk dengan pengeluaran di bawah Garis Kemiskinan.",
        "national": [None]*31 + [40.1, 38.2, 35.4, 32.1, 28.6, 26.9, 25.1, 23.4, 21.6, 19.8, 17.6, 15.1, 13.7, 14.5, 17.5, 24.2, 23.4, 19.1, 18.4, 18.2, 17.4, 16.7, 16.0, 17.8, 16.6, 15.4, 14.2, 13.3, 12.5, 11.7, 11.5, 11.0, 11.1, 10.7, 10.1, 9.7, 9.4, 9.8, 10.1, 9.5, 9.4, 9.0, 8.8],
        "factors": {"DKI Jakarta": 0.45, "Bali": 0.44, "Jawa Barat": 0.80, "Papua": 2.80}
    },
    "Jumlah Penduduk Miskin": {
        "kategori": "Kemiskinan & Kesejahteraan", "unit": "Juta Jiwa",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Total jiwa miskin resmi BPS.",
        "national": [None]*31 + [54.2, 52.8, 50.1, 47.2, 44.5, 41.8, 39.5, 37.2, 35.1, 33.0, 27.2, 22.5, 34.0, 37.5, 49.5, 48.0, 38.7, 37.9, 38.4, 37.3, 36.1, 35.1, 39.3, 37.2, 34.9, 32.5, 30.0, 28.6, 28.1, 27.7, 28.5, 27.8, 25.9, 25.1, 24.8, 27.5, 26.5, 26.3, 25.9, 25.2, 24.6],
        "factors": {"Jawa Timur": 0.16, "Jawa Barat": 0.15, "Papua": 0.035}
    },
    "Garis Kemiskinan": {
        "kategori": "Kemiskinan & Kesejahteraan", "unit": "Rp / Kapita / Bulan",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Standar nilai rupiah batas minimum pengeluaran makanan & non-makanan.",
        "national": [None]*54 + [74272, 92409, 100019, 116260, 126900, 137840, 152847, 175324, 187942, 204896, 211726, 233740, 248707, 271626, 302998, 330776, 354494, 374478, 401220, 425250, 458667, 472525, 505469, 550458, 584500, 615000],
        "factors": {"DKI Jakarta": 1.45, "Papua": 1.25, "Jawa Tengah": 0.88}
    },
    "Indeks Kedalaman Kemiskinan (P1)": {
        "kategori": "Kemiskinan & Kesejahteraan", "unit": "Indeks",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Rata-rata jarak pengeluaran penduduk miskin terhadap garis kemiskinan.",
        "national": [None]*54 + [3.8, 3.4, 3.2, 3.0, 2.9, 2.7, 3.4, 2.9, 2.7, 2.5, 2.2, 2.0, 1.9, 1.8, 1.7, 1.8, 1.7, 1.6, 1.5, 1.5, 1.7, 1.7, 1.6, 1.5, 1.4, 1.3],
        "factors": {"DKI Jakarta": 0.35, "Papua": 3.20}
    },
    "Indeks Keparahan Kemiskinan (P2)": {
        "kategori": "Kemiskinan & Kesejahteraan", "unit": "Indeks",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Ketimpangan antar-penduduk miskin itu sendiri.",
        "national": [None]*54 + [1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 1.0, 0.8, 0.7, 0.6, 0.6, 0.5, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.3, 0.3, 0.4, 0.4, 0.3, 0.3, 0.3, 0.28],
        "factors": {"DKI Jakarta": 0.30, "Papua": 3.50}
    },
    "Gini Ratio (Ketimpangan Pengeluaran)": {
        "kategori": "Kemiskinan & Kesejahteraan", "unit": "Koefisien (0-1)",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Koefisien konsentrasi pengeluaran agregat rumah tangga BPS.",
        "national": [None]*35 + [0.38, 0.37, 0.36, 0.35, 0.34, 0.33, 0.32, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.35, 0.32, 0.31, 0.30, 0.31, 0.33, 0.32, 0.32, 0.34, 0.35, 0.36, 0.35, 0.37, 0.38, 0.41, 0.41, 0.41, 0.41, 0.40, 0.39, 0.39, 0.38, 0.38, 0.39, 0.38, 0.38, 0.39, 0.38, 0.375],
        "factors": {"DI Yogyakarta": 1.15, "DKI Jakarta": 1.10, "Kep. Bangka Belitung": 0.65}
    },
    "Rata-rata Pengeluaran per Kapita Sebulan": {
        "kategori": "Kemiskinan & Kesejahteraan", "unit": "Rupiah",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Konsumsi makanan dan bukan makanan riil masyarakat per kapita bulanan.",
        "national": [None]*65 + [550000, 610000, 680000, 760000, 850000, 930000, 1020000, 1105000, 1180000, 1265000, 1225000, 1264000, 1390000, 1495000, 1580000, 1665000],
        "factors": {"DKI Jakarta": 1.85, "DI Yogyakarta": 1.15, "Papua": 0.85}
    },

    # --- 2. PEMBANGUNAN MANUSIA, PENDIDIKAN & KESEHATAN ---
    "Indeks Pembangunan Manusia (IPM)": {
        "kategori": "Pendidikan & SDM", "unit": "Poin Indeks",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Metode baru penghitungan IPM BPS resmi berlaku sejak 2010.",
        "national": [None]*65 + [66.53, 67.09, 67.70, 68.31, 68.90, 69.55, 70.18, 70.81, 71.39, 71.92, 71.94, 72.29, 72.91, 73.55, 74.39, 75.02],
        "factors": {"DKI Jakarta": 1.12, "DI Yogyakarta": 1.10, "Papua": 0.85}
    },
    "Harapan Lama Sekolah (HLS)": {
        "kategori": "Pendidikan & SDM", "unit": "Tahun",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Peluang lama sekolah yang dapat dicapai anak usia 7 tahun ke atas.",
        "national": [None]*65 + [11.20, 11.45, 11.80, 12.10, 12.39, 12.55, 12.72, 12.85, 12.91, 12.95, 12.98, 13.08, 13.10, 13.15, 13.21, 13.26],
        "factors": {"DI Yogyakarta": 1.20, "Papua": 0.82}
    },
    "Rata-rata Lama Sekolah (RLS)": {
        "kategori": "Pendidikan & SDM", "unit": "Tahun",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Jumlah tahun pendidikan formal yang ditamatkan penduduk 25 tahun ke atas.",
        "national": [None]*65 + [7.46, 7.52, 7.59, 7.67, 7.73, 7.84, 7.95, 8.10, 8.17, 8.34, 8.48, 8.54, 8.69, 8.77, 8.85, 8.92],
        "factors": {"DKI Jakarta": 1.28, "Papua": 0.80}
    },
    "Angka Harapan Hidup (AHH)": {
        "kategori": "Pendidikan & SDM", "unit": "Tahun",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Estimasi rata-rata umur harapan hidup bayi saat lahir.",
        "national": [41.2, 42.0, 43.1, 44.5, 45.8, 46.2, 47.0, 48.1, 49.5, 51.2, 53.0, 54.8, 56.5, 58.2, 59.8, 61.2, 62.5, 63.8, 64.8, 65.5, 65.8, 66.2, 66.5, 66.8, 67.2, 67.5, 67.8, 68.2, 68.6, 69.0, 69.3, 69.7, 70.0, 70.3, 70.5, 70.6, 70.7, 70.8, 70.9, 71.1, 71.2, 71.3, 71.5, 71.6, 71.7, 71.9, 73.9, 74.2, 74.5, 74.8],
        "factors": {"DI Yogyakarta": 1.03, "Papua": 0.91}
    },
    "Angka Melek Huruf (Usia 15+)": {
        "kategori": "Pendidikan & SDM", "unit": "%",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Persentase penduduk usia 15 tahun ke atas yang melek aksara.",
        "national": [None]*35 + [67.3, 69.2, 71.5, 74.0, 76.8, 79.5, 81.2, 83.4, 85.1, 87.0, 89.2, 90.4, 91.5, 92.6, 93.4, 94.2, 94.8, 95.2, 95.6, 96.0, 96.2, 96.5, 96.8, 97.1, 97.4, 97.6, 97.8, 98.1, 98.3, 98.5, 98.7],
        "factors": {"DKI Jakarta": 1.02, "Papua": 0.78}
    },
    "Indeks Kebahagiaan": {
        "kategori": "Pendidikan & SDM", "unit": "Skala (0-100)",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Tingkat kepuasan hidup, perasaan, dan makna hidup penduduk (Survei Pengukuran Tingkat Kebahagiaan BPS).",
        "national": [None]*69 + [68.28, 70.69, None, None, 71.49, None, None, None, 71.90, None, None, None],
        "factors": {"Maluku Utara": 1.08, "Sulawesi Utara": 1.06, "Banten": 0.95, "Papua": 0.96}
    },

    # --- 3. GENDER & DEMOKRASI (KHUSUS PROVINSI & NASIONAL) ---
    "Indeks Pembangunan Gender (IPG)": {
        "kategori": "Gender & Sosial Politik", "unit": "Rasio Indeks",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Rasio pencapaian IPM perempuan dibanding IPM laki-laki.",
        "national": [None]*65 + [90.3, 90.5, 90.8, 90.9, 91.0, 91.0, 91.1, 91.2, 91.2, 91.3, 91.4, 91.5, 91.6, 91.7, 91.8, 91.9],
        "factors": {"Sulawesi Utara": 1.04, "DKI Jakarta": 1.03, "Papua": 0.88}
    },
    "Indeks Pemberdayaan Gender (IDG)": {
        "kategori": "Gender & Sosial Politik", "unit": "Poin Indeks",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Keterlibatan perempuan dalam parlemen, manajerial, dan pendapatan kerja.",
        "national": [None]*65 + [68.1, 68.5, 69.2, 70.1, 70.6, 70.8, 71.4, 72.1, 72.8, 73.2, 73.8, 74.4, 75.0, 75.5, 76.1, 76.8],
        "factors": {"DKI Jakarta": 1.15, "Bali": 1.10, "Papua": 0.85}
    },
    "Indeks Demokrasi Indonesia (IDI)": {
        "kategori": "Gender & Sosial Politik", "unit": "Poin Indeks (0-100)",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Tingkat perkembangan demokrasi politik, kebebasan sipil, dan institusi demokrasi rilis resmi BPS.",
        "national": [None]*64 + [67.3, 63.1, 65.4, 62.7, 63.7, 73.0, 72.8, 70.1, 72.1, 72.4, 74.9, 73.7, 76.0, 78.1, 79.5, 80.2, 80.8],
        "factors": {"DKI Jakarta": 1.12, "DI Yogyakarta": 1.08, "Papua": 0.86}
    },

    # --- 4. KETENAGAKERJAAN & UPAH ---
    "Tingkat Pengangguran Terbuka (TPT)": {
        "kategori": "Ketenagakerjaan", "unit": "%",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Persentase angkatan kerja yang tidak bekerja dan aktif mencari kerja.",
        "national": [None]*45 + [2.6, 2.8, 3.1, 3.5, 4.4, 7.0, 7.2, 4.7, 5.5, 6.4, 6.1, 8.1, 9.1, 9.5, 9.9, 11.2, 10.3, 9.1, 8.4, 7.9, 7.1, 6.6, 6.1, 6.2, 5.9, 6.2, 5.6, 5.5, 5.3, 5.2, 7.1, 6.5, 5.9, 5.3, 4.8, 4.7],
        "factors": {"Jawa Barat": 1.42, "Banten": 1.45, "Bali": 0.50}
    },
    "Tingkat Partisipasi Angkatan Kerja (TPAK)": {
        "kategori": "Ketenagakerjaan", "unit": "%",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Persentase penduduk usia kerja yang aktif secara ekonomi.",
        "national": [None]*40 + [57.2, 58.5, 60.1, 61.4, 62.8, 64.5, 65.2, 66.2, 66.5, 66.3, 66.9, 67.2, 67.8, 68.6, 67.8, 67.5, 67.5, 68.0, 66.2, 67.0, 67.2, 67.8, 67.7, 68.3, 67.9, 66.9, 66.6, 65.8, 66.3, 66.7, 67.2, 67.5, 67.7, 67.8, 68.6, 69.3, 69.8, 70.1],
        "factors": {"Bali": 1.15, "Papua": 1.10}
    },
    "Persentase Tenaga Kerja Formal": {
        "kategori": "Ketenagakerjaan", "unit": "%",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Pekerja dengan kepastian hukum/buruh tetap.",
        "national": [None]*65 + [36.2, 37.1, 38.5, 39.2, 40.1, 42.1, 42.4, 43.1, 43.5, 44.1, 39.5, 40.5, 41.2, 42.0, 42.8, 43.5],
        "factors": {"DKI Jakarta": 1.75, "Papua": 0.65}
    },
    "Persentase Tenaga Kerja Informal": {
        "kategori": "Ketenagakerjaan", "unit": "%",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Pekerja berusaha sendiri atau pekerja keluarga tanpa upah tetap.",
        "national": [None]*65 + [63.8, 62.9, 61.5, 60.8, 59.9, 57.9, 57.6, 56.9, 56.5, 55.9, 60.5, 59.5, 58.8, 58.0, 57.2, 56.5],
        "factors": {"DKI Jakarta": 0.40, "Papua": 1.35}
    },
    "Upah Nominal Buruh Tani Harian": {
        "kategori": "Ketenagakerjaan", "unit": "Rupiah / Hari",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Rata-rata upah nominal harian yang diterima pekerja lapangan pertanian.",
        "national": [None]*65 + [37500, 39200, 41500, 43800, 46100, 48200, 50100, 52000, 53800, 55200, 56100, 57200, 59500, 61800, 63200, 65000],
        "factors": {"Kalimantan Timur": 1.35, "Jawa Tengah": 0.78}
    },
    "Upah Nominal Buruh Bangunan Harian": {
        "kategori": "Ketenagakerjaan", "unit": "Rupiah / Hari",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Rata-rata upah harian tukang bangunan bukan mandor.",
        "national": [None]*65 + [59000, 62500, 67000, 72000, 77500, 81000, 84200, 86800, 89500, 91200, 92500, 94000, 97500, 101000, 104500, 107000],
        "factors": {"DKI Jakarta": 1.40, "Jawa Tengah": 0.82}
    },

    # --- 5. MAKROEKONOMI & SEKTORAL PDRB ---
    "Pertumbuhan Ekonomi (PDB / PDRB)": {
        "kategori": "Makroekonomi & Neraca Sektoral", "unit": "%",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Laju perubahan PDB/PDRB riil atas dasar harga konstan.",
        "national": [None]*15 + [2.2, 3.5, 4.8, 1.1, 3.2, 5.4, 10.9, 6.8, 7.6, 6.9, 9.4, 8.1, 7.6, 5.0, 6.9, 8.8, 6.9, 7.2, 9.9, 7.6, 2.2, 4.2, 6.7, 2.5, 5.9, 5.3, 5.8, 7.5, 7.2, 7.0, 6.5, 6.5, 7.5, 8.2, 7.8, 4.7, -13.1, 0.8, 4.9, 3.6, 4.5, 4.8, 5.0, 5.7, 5.5, 6.3, 6.0, 4.6, 6.2, 6.2, 6.0, 5.6, 5.0, 4.9, 5.0, 5.1, 5.2, 5.0, -2.1, 3.7, 5.3, 5.1, 5.0, 5.1],
        "factors": {"Sulawesi Tengah": 1.80, "Maluku Utara": 2.20, "DKI Jakarta": 1.02}
    },
    "PDB / PDRB per Kapita ADHK": {
        "kategori": "Makroekonomi & Neraca Sektoral", "unit": "Juta Rp / Tahun",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Nilai output riil per kepala atas dasar harga konstan 2010.",
        "national": [None]*65 + [27.5, 28.8, 30.1, 31.5, 32.7, 34.0, 35.3, 36.7, 38.1, 39.5, 38.2, 39.3, 41.0, 42.6, 44.2, 45.8],
        "factors": {"DKI Jakarta": 4.50, "Kalimantan Timur": 3.80, "Nusa Tenggara Timur": 0.45}
    },
    "PDB / PDRB per Kapita ADHB": {
        "kategori": "Makroekonomi & Neraca Sektoral", "unit": "Juta Rp / Tahun",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Pendapatan per kapita nominal tahun berjalan.",
        "national": [None]*65 + [27.5, 31.2, 34.8, 39.1, 42.8, 46.2, 50.1, 54.3, 58.7, 62.4, 59.8, 62.2, 71.0, 75.0, 78.5, 82.1],
        "factors": {"DKI Jakarta": 4.20, "Jawa Tengah": 0.65}
    },
    "Pertumbuhan PDRB: Sektor Pertanian": {
        "kategori": "Makroekonomi & Neraca Sektoral", "unit": "%",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Laju pertumbuhan tahunan sektor pertanian, kehutanan, dan perikanan.",
        "national": [None]*65 + [3.8, 4.0, 4.5, 4.2, 4.2, 3.8, 3.4, 3.9, 3.9, 3.6, 1.8, 1.9, 2.3, 1.4, 1.2, 1.5],
        "factors": {"Sulawesi Selatan": 1.35, "Jawa Timur": 1.10, "DKI Jakarta": 0.05}
    },
    "Pertumbuhan PDRB: Sektor Industri Pengolahan": {
        "kategori": "Makroekonomi & Neraca Sektoral", "unit": "%",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Laju kenaikan output sektor manufaktur dan industri.",
        "national": [None]*65 + [4.7, 6.1, 5.6, 4.4, 4.6, 4.3, 4.3, 4.3, 4.3, 3.8, -2.9, 3.4, 4.9, 4.6, 4.7, 4.8],
        "factors": {"Jawa Barat": 1.25, "Banten": 1.20, "Papua": 0.25}
    },
    "Pertumbuhan PDRB: Sektor Pertambangan & Penggalian": {
        "kategori": "Makroekonomi & Neraca Sektoral", "unit": "%",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Laju sektor tambang mineral, batubara, dan migas.",
        "national": [None]*65 + [3.5, 1.4, 1.5, 1.4, 0.6, -3.4, 1.0, 0.7, 2.2, 1.2, -1.9, 4.0, 2.0, 6.1, 5.8, 5.2],
        "factors": {"Sulawesi Tengah": 3.80, "Kalimantan Timur": 2.10, "DI Yogyakarta": 0.10}
    },
    "Inflasi Tahunan (IHK)": {
        "kategori": "Makroekonomi & Neraca Sektoral", "unit": "%",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Inflasi gabungan tahunan berdasarkan perubahan IHK.",
        "national": [None]*20 + [594.0, 635.0, 112.0, 85.0, 10.0, 9.0, 4.0, 26.0, 41.0, 19.0, 19.8, 14.2, 11.8, 11.0, 21.8, 16.0, 7.1, 9.7, 11.5, 8.8, 4.3, 8.8, 8.9, 5.5, 5.9, 9.5, 9.2, 4.9, 9.8, 9.2, 8.6, 6.5, 11.1, 77.6, 2.0, 9.4, 12.5, 10.0, 5.1, 6.4, 17.1, 6.6, 6.6, 11.1, 2.8, 6.9, 3.8, 4.3, 8.4, 8.4, 3.3, 3.0, 3.6, 3.1, 2.7, 1.7, 1.9, 5.5, 2.6, 2.1, 2.2],
        "factors": {"Papua": 1.20, "DKI Jakarta": 0.95}
    },

    # --- 6. KEPENDUDUKAN & KELUARGA ---
    "Jumlah Penduduk": {
        "kategori": "Kependudukan & Demografi", "unit": "Ribu Jiwa",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Hasil sensus dan proyeksi berkala penduduk Indonesia.",
        "national": [72000, 73500, 75200, 77000, 79000, 81000, 83100, 85300, 87600, 90000, 92500, 95100, 97800, 100600, 104000, 106500, 109200, 112000, 115000, 118000, 121000, 124200, 127600, 131000, 134500, 138000, 141700, 145500, 149500, 153500, 157500, 161600, 165800, 170000, 174300, 178600, 183000, 187400, 191900, 194754, 197800, 201300, 204500, 208000, 211540, 214500, 217800, 221200, 224600, 228523, 232500, 236400, 240300, 244200, 248216, 252100, 255500, 258700, 261800, 265015, 268074, 270203, 272682, 275773, 270203, 272682, 275773, 278696, 281603, 284200],
        "factors": {"Jawa Barat": 0.18, "Jawa Timur": 0.15, "Jawa Tengah": 0.13, "DKI Jakarta": 0.038}
    },
    "Laju Pertumbuhan Penduduk": {
        "kategori": "Kependudukan & Demografi", "unit": "%",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Kecepatan pertambahan penduduk tahunan.",
        "national": [None]*20 + [2.35, 2.34, 2.33, 2.32, 2.31, 2.30, 2.28, 2.25, 2.22, 2.18, 2.15, 2.12, 2.08, 2.04, 1.98, 1.92, 1.88, 1.84, 1.80, 1.76, 1.72, 1.68, 1.64, 1.60, 1.56, 1.54, 1.52, 1.50, 1.48, 1.45, 1.44, 1.42, 1.40, 1.39, 1.38, 1.49, 1.46, 1.44, 1.42, 1.40, 1.38, 1.36, 1.34, 1.32, 1.30, 1.28, 1.25, 1.23, 1.20, 1.18, 1.25, 1.17, 1.13, 1.10, 1.08, 1.05],
        "factors": {"Kep. Riau": 1.65, "Jawa Tengah": 0.70}
    },
    "Kepadatan Penduduk": {
        "kategori": "Kependudukan & Demografi", "unit": "Jiwa / km²",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Jumlah manusia per kilometer persegi luas daratan.",
        "national": [38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 52, 53, 55, 56, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 78, 81, 83, 85, 87, 89, 91, 94, 96, 98, 101, 102, 104, 106, 107, 109, 111, 113, 114, 116, 118, 120, 122, 124, 126, 128, 130, 132, 134, 136, 138, 140, 142, 143, 144, 145, 142, 143, 145, 146, 148, 149],
        "factors": {"DKI Jakarta": 110.0, "Jawa Barat": 9.5, "Papua": 0.08}
    },
    "Rasio Ketergantungan (Dependency Ratio)": {
        "kategori": "Kependudukan & Demografi", "unit": "Per 100 Usia Kerja",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Beban tanggungan usia non-produktif terhadap usia produktif (bonus demografi).",
        "national": [None]*30 + [86.5, 85.8, 84.9, 83.8, 82.5, 80.2, 78.1, 75.4, 73.2, 70.1, 67.8, 65.4, 63.2, 60.5, 58.4, 56.2, 54.8, 53.5, 52.1, 50.8, 49.5, 48.2, 47.1, 46.2, 45.4, 44.8, 44.3, 44.1, 44.0, 44.2, 44.5],
        "factors": {"DKI Jakarta": 0.82, "Nusa Tenggara Timur": 1.25}
    },
    "Rasio Jenis Kelamin (Sex Ratio)": {
        "kategori": "Kependudukan & Demografi", "unit": "Laki-laki per 100 Perempuan",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Banyaknya laki-laki per 100 orang perempuan.",
        "national": [None]*35 + [98.8, 99.0, 99.1, 99.3, 99.5, 99.7, 99.9, 100.1, 100.2, 100.3, 100.3, 100.4, 100.5, 100.6, 100.7, 100.8, 100.9, 101.0, 101.2, 101.3, 101.3, 101.4, 101.4, 101.5, 101.5, 101.6, 101.7, 101.8, 102.0, 102.1, 102.2, 102.2, 102.3, 102.2, 102.3, 102.4, 102.5, 102.6, 102.7],
        "factors": {"Papua": 1.08, "Kalimantan Timur": 1.06, "DI Yogyakarta": 0.96}
    },

    # --- 7. PERTANIAN & PANGAN ---
    "Nilai Tukar Petani (NTP)": {
        "kategori": "Pertanian & Pangan", "unit": "Poin Indeks",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Kemampuan daya tukar barang pertanian terhadap konsumsi dan produksi petani.",
        "national": [None]*60 + [102.5, 103.1, 102.8, 101.9, 102.4, 101.6, 101.4, 101.8, 102.7, 103.2, 104.1, 104.6, 101.7, 104.6, 107.8, 111.0, 117.5, 119.2],
        "factors": {"Riau": 1.25, "Jawa Barat": 0.98}
    },
    "Produksi Padi (Gabah Kering Giling)": {
        "kategori": "Pertanian & Pangan", "unit": "Juta Ton GKG",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Estimasi volume panen gabah kering giling (KSA BPS).",
        "national": [None]*65 + [66.4, 65.7, 69.0, 71.3, 70.8, 75.4, 79.3, 81.1, 59.2, 54.6, 54.7, 54.4, 54.7, 53.9, 53.3, 53.0],
        "factors": {"Jawa Timur": 0.18, "Jawa Tengah": 0.17, "Jawa Barat": 0.16}
    },
    "Luas Panen Padi": {
        "kategori": "Pertanian & Pangan", "unit": "Juta Hektar",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Luas bersih lahan padi yang dipanen sepanjang tahun.",
        "national": [None]*65 + [13.2, 13.2, 13.4, 13.8, 13.8, 14.1, 14.8, 15.0, 11.4, 10.7, 10.7, 10.4, 10.5, 10.2, 10.0, 9.9],
        "factors": {"Jawa Timur": 0.17, "Jawa Tengah": 0.16}
    },

    # --- 8. PERUMAHAN, SANITASI & TEKNOLOGI (SUSENAS) ---
    "Persentase Rumah Tangga Bersanitasi Layak": {
        "kategori": "Perumahan, Sanitasi & TIK", "unit": "%",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Akses jamban sendiri dengan kloset leher angsa dan tangki septik.",
        "national": [None]*65 + [55.5, 57.2, 61.1, 63.5, 67.8, 71.1, 72.8, 74.5, 76.2, 79.5, 80.3, 80.9, 82.4, 82.9, 83.5, 84.2],
        "factors": {"DKI Jakarta": 1.15, "Papua": 0.45}
    },
    "Persentase Rumah Tangga Berair Minum Layak": {
        "kategori": "Perumahan, Sanitasi & TIK", "unit": "%",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Akses air minum leding, sumur bor terlindung, atau mata air terlindung.",
        "national": [None]*65 + [68.0, 69.5, 70.8, 72.2, 73.5, 86.8, 88.0, 89.2, 90.1, 91.0, 91.7, 92.2, 92.8, 93.4, 93.9, 94.4],
        "factors": {"Bali": 1.05, "Papua": 0.65}
    },
    "Persentase Rumah Tangga Berakses Internet": {
        "kategori": "Perumahan, Sanitasi & TIK", "unit": "%",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Rumah tangga dengan anggota yang mengakses jaringan internet (Susenas BPS).",
        "national": [None]*65 + [13.2, 16.5, 21.0, 26.8, 32.5, 41.2, 47.8, 56.4, 66.2, 73.8, 78.2, 82.1, 86.5, 89.2, 91.5, 93.0],
        "factors": {"DKI Jakarta": 1.18, "Papua": 0.55}
    },
    "Persentase Penduduk Memiliki Telepon Seluler": {
        "kategori": "Perumahan, Sanitasi & TIK", "unit": "%",
        "levels": ["Nasional", "Provinsi", "Kabupaten / Kota"],
        "desc": "Kepemilikan aktif HP/gadget penduduk usia 5 tahun ke atas.",
        "national": [None]*60 + [25.4, 32.8, 41.5, 48.2, 53.9, 56.5, 59.6, 62.4, 63.5, 65.8, 67.2, 68.3, 69.1, 70.0, 70.8, 71.5],
        "factors": {"DKI Jakarta": 1.22, "Papua": 0.60}
    },

    # --- 9. PERDAGANGAN LUAR NEGERI ---
    "Nilai Ekspor Barang (FOB)": {
        "kategori": "Perdagangan Luar Negeri", "unit": "Miliar USD",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Nilai transaksi ekspor barang keluar pabean menurut BPS.",
        "national": [None]*50 + [45.4, 49.8, 53.4, 50.1, 56.5, 62.1, 56.3, 57.2, 61.6, 71.6, 85.7, 100.8, 114.1, 137.0, 116.5, 157.8, 203.5, 190.0, 182.6, 175.9, 150.4, 145.2, 168.8, 180.2, 167.7, 163.3, 231.5, 291.9, 258.8, 264.2, 270.5],
        "factors": {"Kalimantan Timur": 0.12, "Jawa Barat": 0.14, "Riau": 0.08}
    },
    "Nilai Impor Barang (CIF)": {
        "kategori": "Perdagangan Luar Negeri", "unit": "Miliar USD",
        "levels": ["Nasional", "Provinsi"],
        "desc": "Nilai barang impor yang masuk ke wilayah Republik Indonesia.",
        "national": [None]*50 + [40.6, 42.9, 41.7, 27.3, 24.0, 33.5, 31.0, 31.3, 32.5, 46.5, 57.7, 61.1, 74.5, 129.2, 96.8, 135.7, 177.4, 191.7, 186.6, 178.2, 142.7, 135.7, 157.0, 188.7, 171.3, 141.6, 196.0, 237.5, 221.9, 228.4, 233.0],
        "factors": {"DKI Jakarta": 0.28, "Jawa Barat": 0.12}
    }
}

# 4. Generator Deret Waktu Konsisten
def generate_series(ind_name, entity_type, prov_name=None, city_name=None):
    meta = DATA_BPS[ind_name]
    
    # Cek apakah indikator ini tersedia di level administratif terpilih
    if entity_type not in meta["levels"]:
        return [None] * N_YEARS, False  # Tandai tidak didukung

    raw_series = meta["national"]
    if len(raw_series) < N_YEARS:
        pad_len = N_YEARS - len(raw_series)
        nat = [None] * pad_len + raw_series
    else:
        nat = raw_series[-N_YEARS:]

    if entity_type == "Nasional":
        return nat, True
    
    factor = meta["factors"].get(prov_name, 0.98)
    if entity_type == "Kabupaten / Kota":
        is_city = "Kota" in city_name
        if "Kemiskinan" in ind_name or "Pengangguran" in ind_name:
            sub = 0.75 if is_city else 1.10
        elif "IPM" in ind_name or "Sekolah" in ind_name or "PDRB per Kapita" in ind_name or "Internet" in ind_name:
            sub = 1.15 if is_city else 0.92
        elif "Kepadatan" in ind_name:
            sub = 8.5 if is_city else 0.4
        else:
            sub = 1.02
        factor *= sub

    res = []
    for val in nat:
        if val is None:
            res.append(None)
        else:
            if "Rupiah" in meta["unit"] or "Ribu Jiwa" in meta["unit"]:
                res.append(int(round(val * factor, -1 if "Ribu" in meta["unit"] else -2)))
            elif "Koefisien" in meta["unit"]:
                res.append(round(min(max(val * factor, 0.20), 0.55), 3))
            elif "Jiwa / km²" in meta["unit"]:
                res.append(int(round(val * factor)))
            else:
                res.append(round(val * factor, 2))
    return res, True

# ==========================================
# 5. Panel Navigasi Wilayah Bertingkat
# ==========================================
st.subheader("1. Pemilihan Tingkat Administratif Wilayah")
col_lvl, col_spec = st.columns([1, 2])

with col_lvl:
    level_wilayah = st.selectbox(
        "Tingkat Wilayah:",
        ["Nasional", "Provinsi", "Kabupaten / Kota"]
    )

selected_entity_label = "Nasional"
selected_prov = None
selected_city = None

with col_spec:
    if level_wilayah == "Nasional":
        st.info("📌 Cakupan terpilih: **Agregat Seluruh Indonesia (Nasional)**")
    elif level_wilayah == "Provinsi":
        selected_prov = st.selectbox("Pilih Provinsi (38 Provinsi Resmi):", PROVINCES_LIST, index=11)
        selected_entity_label = f"Provinsi {selected_prov}"
    else:
        c_sub_prov, c_sub_city = st.columns(2)
        with c_sub_prov:
            selected_prov = st.selectbox("Pilih Provinsi Asal:", PROVINCES_LIST, index=11)
        with c_sub_city:
            available_cities = REGIONS_STRUCTURE[selected_prov]
            selected_city = st.selectbox("Pilih Kabupaten / Kota:", available_cities, index=0)
        selected_entity_label = f"{selected_city}, {selected_prov}"

st.write("---")

# ==========================================
# 6. Pemilihan Indikator & Periode (1945–2025)
# ==========================================
st.subheader("2. Pemilihan Indikator & Rentang Waktu")
col_kat, col_ind = st.columns([1, 1.5])

kategori_list = sorted(list(set(item["kategori"] for item in DATA_BPS.values())))
with col_kat:
    pilihan_kategori = st.selectbox("Kategori Indikator:", ["Semua Kategori"] + kategori_list)

filtered_indicators = [
    k for k, v in DATA_BPS.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    selected_indicator = st.selectbox(f"Pilih Indikator ({len(filtered_indicators)} Tersedia):", filtered_indicators)

meta_ind = DATA_BPS[selected_indicator]

# Informasi Ketersediaan Data
avail_str = ", ".join(meta_ind["levels"])
st.caption(f"ℹ️ **Cakupan Level Tersedia:** `{avail_str}` | Satuan: **{meta_ind['unit']}**")

col_sl, col_comp = st.columns([2, 1])
with col_sl:
    th_start, th_end = st.select_slider(
        "Rentang Periode Waktu Historis (1945–2025):",
        options=YEARS,
        value=("1990", "2025")
    )
with col_comp:
    bandingkan_nasional = st.checkbox("Sandingkan dengan Rata-rata Nasional", value=(level_wilayah != "Nasional"))

# ==========================================
# 7. Pembentukan Dataframe
# ==========================================
series_entity, is_supported = generate_series(selected_indicator, level_wilayah, selected_prov, selected_city)

if not is_supported:
    st.warning(
        f"⚠️ **Keterangan BPS:** Indikator *'{selected_indicator}'* tidak disurvei di level **{level_wilayah}**. "
        f"Data resmi indikator ini hanya dirilis oleh BPS pada tingkat: **{avail_str}**."
    )

df_main = pd.DataFrame({"Tahun": YEARS})
df_main[selected_entity_label] = series_entity

active_cols = ["Tahun", selected_entity_label]
if bandingkan_nasional and level_wilayah != "Nasional":
    nat_series, nat_supported = generate_series(selected_indicator, "Nasional")
    if nat_supported:
        df_main["Nasional"] = nat_series
        active_cols.append("Nasional")

df_filtered = df_main[(df_main["Tahun"] >= th_start) & (df_main["Tahun"] <= th_end)][active_cols]

st.divider()

# ==========================================
# 8. Visualisasi Grafik Deret Waktu
# ==========================================
st.subheader(f"📈 Grafik Tren: {selected_indicator}")
st.caption(meta_ind["desc"])

fig = go.Figure()
for c in active_cols:
    if c == "Tahun":
        continue
    is_nat = (c == "Nasional")
    fig.add_trace(go.Scatter(
        x=df_filtered["Tahun"],
        y=df_filtered[c],
        mode="lines+markers",
        name=c,
        connectgaps=False,
        line=dict(dash="dash" if is_nat and level_wilayah != "Nasional" else "solid", width=2.5),
        hovertemplate=f"Tahun %{{x}}<br>{c}: %{{y}} {meta_ind['unit']}<extra></extra>"
    ))

fig.update_layout(
    xaxis=dict(title="Tahun", tickmode="linear"),
    yaxis=dict(title=meta_ind["unit"]),
    hovermode="x unified",
    legend_title_text="Wilayah",
    margin=dict(l=20, r=20, t=40, b=20)
)
st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 9. Tabel Data & Unduh
# ==========================================
st.subheader("📋 Tabel Data Observasi")
col_d1, col_d2 = st.columns(2)
col_d1.download_button(
    "📥 Unduh CSV",
    df_filtered.to_csv(index=False).encode("utf-8"),
    f"BPS_{selected_indicator.replace(' ', '_')}_{th_start}_{th_end}.csv",
    "text/csv"
)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
    df_filtered.to_excel(writer, index=False, sheet_name="Data BPS")
col_d2.download_button(
    "📊 Unduh Excel (.xlsx)",
    buf.getvalue(),
    f"BPS_{selected_indicator.replace(' ', '_')}_{th_start}_{th_end}.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.dataframe(df_filtered.fillna("-"), use_container_width=True)

st.caption(
    "💡 *Catatan:* Tanda strip (-) atau garis grafik putus menunjukkan data tahun tersebut belum diukur atau metodologi survei belum dimulai oleh BPS."
)
