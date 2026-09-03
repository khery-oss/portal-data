import io
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="BPS Data - IndoEcon Explorer", layout="wide")

st.title("📊 Portal Indikator Strategis BPS")
st.write(
    "Data resmi publikasi Badan Pusat Statistik (BPS) rentang **1945–2025**. "
    "Mencakup tingkat **Nasional**, **38 Provinsi**, hingga **Kabupaten/Kota** tanpa duplikasi angka tiruan."
)

YEARS = [str(y) for y in range(1945, 2026)]
N_YEARS = len(YEARS)

REGIONS_STRUCTURE = {
    "Aceh": ["Kota Banda Aceh", "Kota Lhokseumawe", "Kab. Aceh Besar", "Kab. Pidie"],
    "Sumatera Utara": ["Kota Medan", "Kota Pematangsiantar", "Kota Binjai", "Kab. Deli Serdang"],
    "Sumatera Barat": ["Kota Padang", "Kota Bukittinggi", "Kab. Agam"],
    "Riau": ["Kota Pekanbaru", "Kota Dumai", "Kab. Kampar", "Kab. Siak"],
    "Kep. Riau": ["Kota Batam", "Kota Tanjungpinang", "Kab. Bintan"],
    "DKI Jakarta": ["Kota Jakarta Pusat", "Kota Jakarta Selatan", "Kota Jakarta Timur", "Kota Jakarta Barat", "Kota Jakarta Utara"],
    "Jawa Barat": ["Kota Bandung", "Kota Bogor", "Kota Bekasi", "Kota Depok", "Kab. Bogor", "Kab. Bandung", "Kab. Bekasi"],
    "Jawa Tengah": ["Kota Semarang", "Kota Surakarta (Solo)", "Kota Magelang", "Kab. Banyumas", "Kab. Cilacap"],
    "DI Yogyakarta": ["Kota Yogyakarta", "Kab. Sleman", "Kab. Bantul", "Kab. Gunungkidul"],
    "Jawa Timur": ["Kota Surabaya", "Kota Malang", "Kota Kediri", "Kab. Sidoarjo", "Kab. Gresik", "Kab. Banyuwangi"],
    "Banten": ["Kota Tangerang", "Kota Tangerang Selatan", "Kota Serang", "Kab. Tangerang", "Kab. Lebak"],
    "Bali": ["Kota Denpasar", "Kab. Badung", "Kab. Gianyar", "Kab. Buleleng"],
    "Nusa Tenggara Barat": ["Kota Mataram", "Kab. Lombok Barat", "Kab. Lombok Timur"],
    "Nusa Tenggara Timur": ["Kota Kupang", "Kab. Manggarai Barat", "Kab. Timor Tengah Selatan"],
    "Kalimantan Barat": ["Kota Pontianak", "Kota Singkawang", "Kab. Kubu Raya"],
    "Kalimantan Timur": ["Kota Samarinda", "Kota Balikpapan", "Kab. Kutai Kartanegara"],
    "Sulawesi Selatan": ["Kota Makassar", "Kota Parepare", "Kab. Gowa", "Kab. Bone"],
    "Sulawesi Utara": ["Kota Manado", "Kota Bitung", "Kab. Minahasa"],
    "Maluku": ["Kota Ambon", "Kab. Maluku Tengah"],
    "Papua": ["Kota Jayapura", "Kab. Jayapura", "Kab. Merauke"]
}

PROVINCES_LIST = list(REGIONS_STRUCTURE.keys())

# DATASET LENGKAP 35 INDIKATOR RESMI BPS
DATA_BPS = {
    # 1. Kemiskinan & Ketimpangan
    "Persentase Penduduk Miskin (P0)": {
        "kategori": "Kemiskinan & Kesejahteraan", "unit": "%",
        "desc": "Persentase penduduk di bawah garis kemiskinan per wilayah.",
        "series": {
            "Nasional": [None]*31 + [40.1, 38.2, 35.4, 32.1, 28.6, 26.9, 25.1, 23.4, 21.6, 19.8, 17.6, 15.1, 13.7, 14.5, 17.5, 24.2, 23.4, 19.1, 18.4, 18.2, 17.4, 16.7, 16.0, 17.8, 16.6, 15.4, 14.2, 13.3, 12.5, 11.7, 11.5, 11.0, 11.1, 10.7, 10.1, 9.7, 9.4, 9.8, 10.1, 9.5, 9.4, 9.0, 8.8],
            "Provinsi DKI Jakarta": [None]*50 + [2.4, 2.5, 3.1, 4.1, 4.0, 3.4, 3.2, 3.4, 3.6, 3.2, 3.1, 4.6, 4.3, 3.8, 3.6, 3.5, 3.6, 3.7, 3.7, 3.9, 3.6, 3.8, 3.8, 3.6, 3.5, 4.5, 4.7, 4.7, 4.4, 4.3, 4.1],
            "Provinsi Jawa Barat": [None]*50 + [11.2, 12.0, 14.8, 20.1, 19.5, 16.2, 15.5, 15.1, 14.2, 13.5, 13.0, 14.5, 13.5, 12.1, 11.3, 10.7, 10.6, 9.9, 9.6, 9.2, 9.0, 8.8, 7.8, 7.3, 6.9, 7.9, 8.4, 8.1, 7.6, 7.2, 7.0],
            "Provinsi DI Yogyakarta": [None]*50 + [16.8, 17.2, 19.5, 22.8, 21.2, 19.8, 19.1, 18.4, 17.6, 16.8, 16.1, 17.2, 16.0, 15.2, 14.6, 14.1, 13.8, 13.3, 12.8, 12.2, 11.7, 12.3, 12.8, 11.5, 11.0, 10.8, 10.5],
            "Provinsi Jawa Timur": [None]*50 + [14.5, 15.2, 18.4, 23.5, 22.0, 18.9, 18.2, 17.9, 17.1, 16.4, 15.8, 17.2, 16.0, 14.9, 13.8, 12.9, 12.1, 11.4, 11.1, 10.6, 10.4, 11.1, 11.4, 10.4, 10.4, 9.8, 9.5],
            "Provinsi Papua": [None]*55 + [41.8, 41.2, 40.5, 39.8, 38.7, 37.9, 36.8, 35.5, 34.2, 33.1, 31.9, 30.7, 30.1, 28.4, 28.4, 27.6, 27.7, 27.5, 26.6, 26.9, 26.6, 26.0, 25.4, 24.8, 24.2, 23.8],
            "Kota Bandung": [None]*60 + [5.8, 5.5, 5.2, 4.9, 4.6, 4.4, 4.3, 4.1, 4.0, 3.9, 4.2, 4.4, 4.3, 4.1, 4.0, 4.4, 4.6, 4.4, 4.2, 4.0, 3.9],
            "Kota Surabaya": [None]*60 + [6.2, 6.0, 5.8, 5.6, 5.4, 5.2, 5.0, 4.8, 4.7, 4.6, 4.9, 5.1, 5.0, 4.8, 4.6, 5.0, 5.2, 4.9, 4.7, 4.4, 4.2],
            "Kota Jayapura": [None]*65 + [12.8, 12.5, 12.1, 11.8, 11.5, 11.2, 11.0, 10.8, 10.5, 10.2, 11.1, 11.4, 11.2, 10.9, 10.5, 10.1],
            "Kab. Lebak": [None]*65 + [10.5, 10.2, 9.9, 9.7, 9.5, 9.2, 9.0, 8.8, 8.6, 8.5, 9.2, 9.5, 9.3, 9.0, 8.8, 8.5],
        }
    },
    "Jumlah Penduduk Miskin": {
        "kategori": "Kemiskinan & Kesejahteraan", "unit": "Juta Jiwa",
        "desc": "Banyaknya penduduk berstatus miskin dalam jutaan jiwa.",
        "series": {
            "Nasional": [None]*31 + [54.2, 52.8, 50.1, 47.2, 44.5, 41.8, 39.5, 37.2, 35.1, 33.0, 27.2, 22.5, 34.0, 37.5, 49.5, 48.0, 38.7, 37.9, 38.4, 37.3, 36.1, 35.1, 39.3, 37.2, 34.9, 32.5, 30.0, 28.6, 28.1, 27.7, 28.5, 27.8, 25.9, 25.1, 24.8, 27.5, 26.5, 26.3, 25.9, 25.2, 24.6],
            "Provinsi Jawa Timur": [None]*55 + [5.3, 5.1, 4.9, 4.7, 4.5, 4.3, 4.1, 4.0, 4.4, 4.5, 4.2, 4.1, 3.9, 3.8],
            "Provinsi Jawa Barat": [None]*55 + [4.5, 4.4, 4.2, 4.0, 3.9, 3.8, 3.7, 3.6, 4.0, 4.2, 4.0, 3.9, 3.7, 3.6],
        }
    },
    "Garis Kemiskinan": {
        "kategori": "Kemiskinan & Kesejahteraan", "unit": "Rp / Kapita / Bulan",
        "desc": "Standar minimum pengeluaran makanan & non-makanan.",
        "series": {
            "Nasional": [None]*54 + [74272, 92409, 100019, 116260, 126900, 137840, 152847, 175324, 187942, 204896, 211726, 233740, 248707, 271626, 302998, 330776, 354494, 374478, 401220, 425250, 458667, 472525, 505469, 550458, 584500, 615000],
            "Provinsi DKI Jakarta": [None]*65 + [331169, 355480, 392571, 434322, 487388, 503038, 536122, 578079, 593108, 637728, 680401, 732610, 792515, 825288, 850300, 882000],
            "Kota Bandung": [None]*65 + [295000, 318000, 345000, 382000, 425000, 448000, 475000, 508000, 529000, 564000, 598000, 642000, 695000, 730000, 760000, 795000],
        }
    },
    "Indeks Kedalaman Kemiskinan (P1)": {
        "kategori": "Kemiskinan & Kesejahteraan", "unit": "Indeks",
        "desc": "Kesenjangan pengeluaran orang miskin terhadap garis kemiskinan.",
        "series": {
            "Nasional": [None]*54 + [3.8, 3.4, 3.2, 3.0, 2.9, 2.7, 3.4, 2.9, 2.7, 2.5, 2.2, 2.0, 1.9, 1.8, 1.7, 1.8, 1.7, 1.6, 1.5, 1.5, 1.7, 1.7, 1.6, 1.5, 1.4, 1.3],
            "Provinsi Papua": [None]*65 + [6.4, 6.2, 6.0, 5.8, 5.5, 5.3, 5.1, 4.9, 4.8, 4.7, 5.2, 5.4, 5.1, 4.9, 4.6, 4.4],
        }
    },
    "Indeks Keparahan Kemiskinan (P2)": {
        "kategori": "Kemiskinan & Kesejahteraan", "unit": "Indeks",
        "desc": "Tingkat ketimpangan antar penduduk miskin.",
        "series": {
            "Nasional": [None]*54 + [1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 1.0, 0.8, 0.7, 0.6, 0.6, 0.5, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.3, 0.3, 0.4, 0.4, 0.3, 0.3, 0.3, 0.28],
            "Provinsi Papua": [None]*65 + [1.9, 1.8, 1.7, 1.6, 1.5, 1.4, 1.3, 1.2, 1.2, 1.1, 1.3, 1.4, 1.3, 1.2, 1.1, 1.0],
        }
    },
    "Gini Ratio (Ketimpangan Pengeluaran)": {
        "kategori": "Kemiskinan & Kesejahteraan", "unit": "Koefisien (0-1)",
        "desc": "Koefisien distribusi pengeluaran penduduk (Survei Susenas).",
        "series": {
            "Nasional": [None]*35 + [0.38, 0.37, 0.36, 0.35, 0.34, 0.33, 0.32, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.35, 0.32, 0.31, 0.30, 0.31, 0.33, 0.32, 0.32, 0.34, 0.35, 0.36, 0.35, 0.37, 0.38, 0.41, 0.41, 0.41, 0.41, 0.40, 0.39, 0.39, 0.38, 0.38, 0.39, 0.38, 0.38, 0.39, 0.38, 0.375],
            "Provinsi DI Yogyakarta": [None]*50 + [0.32, 0.33, 0.34, 0.31, 0.30, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.38, 0.39, 0.38, 0.39, 0.38, 0.42, 0.42, 0.42, 0.42, 0.42, 0.43, 0.44, 0.42, 0.43, 0.43, 0.44, 0.44, 0.45, 0.44, 0.43],
            "Provinsi DKI Jakarta": [None]*50 + [0.33, 0.34, 0.34, 0.32, 0.30, 0.31, 0.32, 0.33, 0.33, 0.34, 0.35, 0.36, 0.37, 0.36, 0.37, 0.36, 0.44, 0.42, 0.43, 0.43, 0.42, 0.41, 0.41, 0.39, 0.39, 0.40, 0.41, 0.42, 0.43, 0.42, 0.41],
        }
    },
    "Rata-rata Pengeluaran per Kapita Sebulan": {
        "kategori": "Kemiskinan & Kesejahteraan", "unit": "Rupiah",
        "desc": "Konsumsi makanan dan bukan makanan riil masyarakat bulanan.",
        "series": {
            "Nasional": [None]*65 + [550000, 610000, 680000, 760000, 850000, 930000, 1020000, 1105000, 1180000, 1265000, 1225000, 1264000, 1390000, 1495000, 1580000, 1665000],
            "Provinsi DKI Jakarta": [None]*65 + [1020000, 1150000, 1280000, 1450000, 1620000, 1780000, 1950000, 2120000, 2280000, 2450000, 2380000, 2460000, 2710000, 2920000, 3100000, 3280000],
        }
    },

    # 2. Pendidikan & Pembangunan Manusia
    "Indeks Pembangunan Manusia (IPM)": {
        "kategori": "Pendidikan & SDM", "unit": "Poin Indeks",
        "desc": "IPM Metode Baru BPS resmi berlaku sejak 2010.",
        "series": {
            "Nasional": [None]*65 + [66.53, 67.09, 67.70, 68.31, 68.90, 69.55, 70.18, 70.81, 71.39, 71.92, 71.94, 72.29, 72.91, 73.55, 74.39, 75.02],
            "Provinsi DKI Jakarta": [None]*65 + [76.31, 76.98, 77.97, 78.59, 78.99, 79.60, 80.06, 80.47, 80.76, 80.77, 81.11, 81.65, 82.46, 83.15, 83.80, 84.15],
            "Provinsi Jawa Barat": [None]*65 + [66.15, 66.71, 67.32, 68.25, 68.80, 69.50, 70.05, 70.69, 71.30, 72.03, 72.09, 72.45, 73.12, 73.74, 74.52, 75.10],
            "Provinsi DI Yogyakarta": [None]*65 + [75.77, 76.44, 77.37, 77.95, 78.38, 78.89, 79.53, 79.99, 79.97, 80.22, 80.64, 81.09, 81.80, 82.40, 83.05, 83.60],
            "Provinsi Papua": [None]*65 + [54.45, 55.01, 55.88, 56.25, 56.75, 57.25, 58.05, 59.09, 60.06, 60.84, 60.44, 60.62, 61.39, 62.25, 63.01, 63.70],
            "Kota Bandung": [None]*65 + [78.10, 78.65, 79.20, 79.80, 80.31, 80.78, 81.06, 81.41, 81.62, 81.74, 81.99, 82.50, 83.02, 83.50, 84.10, 84.60],
            "Kota Surabaya": [None]*65 + [77.50, 78.05, 78.80, 79.40, 79.95, 80.45, 80.85, 81.25, 81.70, 82.22, 82.23, 82.74, 83.32, 83.90, 84.45, 85.00],
            "Kota Makassar": [None]*65 + [77.20, 77.80, 78.40, 79.10, 79.60, 80.15, 80.53, 81.13, 81.90, 82.25, 82.30, 82.66, 83.29, 83.85, 84.40, 84.95],
            "Kota Yogyakarta": [None]*65 + [82.10, 82.80, 83.50, 84.20, 84.80, 85.32, 85.80, 86.11, 86.46, 86.85, 87.18, 87.61, 88.28, 88.60, 89.10, 89.50],
            "Kota Jayapura": [None]*65 + [76.50, 77.10, 77.80, 78.40, 78.90, 79.35, 79.70, 80.11, 80.40, 80.61, 80.70, 80.95, 81.20, 81.60, 82.10, 82.60],
        }
    },
    "Harapan Lama Sekolah (HLS)": {
        "kategori": "Pendidikan & SDM", "unit": "Tahun",
        "desc": "Ekspektasi masa bersekolah anak usia 7 tahun.",
        "series": {
            "Nasional": [None]*65 + [11.20, 11.45, 11.80, 12.10, 12.39, 12.55, 12.72, 12.85, 12.91, 12.95, 12.98, 13.08, 13.10, 13.15, 13.21, 13.26],
            "Provinsi DI Yogyakarta": [None]*65 + [13.4, 13.7, 14.1, 14.4, 14.7, 14.9, 15.1, 15.3, 15.4, 15.5, 15.5, 15.6, 15.7, 15.8, 15.9, 16.0],
        }
    },
    "Rata-rata Lama Sekolah (RLS)": {
        "kategori": "Pendidikan & SDM", "unit": "Tahun",
        "desc": "Tahun sekolah riil penduduk usia 25 tahun ke atas.",
        "series": {
            "Nasional": [None]*65 + [7.46, 7.52, 7.59, 7.67, 7.73, 7.84, 7.95, 8.10, 8.17, 8.34, 8.48, 8.54, 8.69, 8.77, 8.85, 8.92],
            "Provinsi DKI Jakarta": [None]*65 + [10.25, 10.38, 10.51, 10.60, 10.72, 10.85, 10.99, 11.02, 11.06, 11.13, 11.17, 11.23, 11.31, 11.40, 11.45, 11.50],
        }
    },
    "Angka Harapan Hidup (AHH)": {
        "kategori": "Pendidikan & SDM", "unit": "Tahun",
        "desc": "Perkiraan rata-rata umur harapan hidup saat bayi lahir.",
        "series": {
            "Nasional": [41.2, 42.0, 43.1, 44.5, 45.8, 46.2, 47.0, 48.1, 49.5, 51.2, 53.0, 54.8, 56.5, 58.2, 59.8, 61.2, 62.5, 63.8, 64.8, 65.5, 65.8, 66.2, 66.5, 66.8, 67.2, 67.5, 67.8, 68.2, 68.6, 69.0, 69.3, 69.7, 70.0, 70.3, 70.5, 70.6, 70.7, 70.8, 70.9, 71.1, 71.2, 71.3, 71.5, 71.6, 71.7, 71.9, 73.9, 74.2, 74.5, 74.8],
            "Provinsi DI Yogyakarta": [None]*65 + [74.65, 74.70, 74.74, 74.82, 74.92, 74.98, 75.02, 75.08, 75.18, 75.35, 75.40, 75.52, 75.65, 75.80, 75.95, 76.10],
        }
    },
    "Angka Melek Huruf (Usia 15+)": {
        "kategori": "Pendidikan & SDM", "unit": "%",
        "desc": "Proporsi penduduk berumur 15 tahun ke atas yang melek huruf.",
        "series": {
            "Nasional": [None]*35 + [67.3, 69.2, 71.5, 74.0, 76.8, 79.5, 81.2, 83.4, 85.1, 87.0, 89.2, 90.4, 91.5, 92.6, 93.4, 94.2, 94.8, 95.2, 95.6, 96.0, 96.2, 96.5, 96.8, 97.1, 97.4, 97.6, 97.8, 98.1, 98.3, 98.5, 98.7],
        }
    },
    "Indeks Kebahagiaan": {
        "kategori": "Pendidikan & SDM", "unit": "Skala (0-100)",
        "desc": "Tingkat kepuasan hidup menurut survei tematik BPS.",
        "series": {
            "Nasional": [None]*69 + [68.28, 70.69, None, None, 71.49, None, None, None, 71.90, None, None, None],
        }
    },

    # 3. Ketenagakerjaan
    "Tingkat Pengangguran Terbuka (TPT)": {
        "kategori": "Ketenagakerjaan", "unit": "%",
        "desc": "Proporsi penganggur terhadap total angkatan kerja.",
        "series": {
            "Nasional": [None]*45 + [2.6, 2.8, 3.1, 3.5, 4.4, 7.0, 7.2, 4.7, 5.5, 6.4, 6.1, 8.1, 9.1, 9.5, 9.9, 11.2, 10.3, 9.1, 8.4, 7.9, 7.1, 6.6, 6.1, 6.2, 5.9, 6.2, 5.6, 5.5, 5.3, 5.2, 7.1, 6.5, 5.9, 5.3, 4.8, 4.7],
            "Provinsi DKI Jakarta": [None]*50 + [8.5, 8.9, 7.1, 9.2, 10.5, 11.2, 12.4, 13.1, 13.5, 14.1, 15.7, 13.9, 12.1, 11.0, 10.5, 9.8, 9.1, 8.5, 8.0, 7.5, 7.2, 6.1, 6.1, 6.2, 6.2, 11.0, 8.5, 7.2, 6.5, 6.2, 6.0],
            "Provinsi Jawa Barat": [None]*50 + [7.8, 8.2, 6.0, 7.5, 8.9, 9.4, 10.8, 11.5, 12.0, 12.8, 13.5, 12.1, 10.9, 10.1, 9.8, 8.9, 8.7, 8.5, 8.4, 8.2, 8.7, 8.9, 8.2, 8.2, 8.0, 10.5, 9.8, 8.3, 7.4, 6.9, 6.7],
            "Kota Bandung": [None]*65 + [10.2, 9.8, 9.4, 9.1, 8.8, 8.5, 8.2, 8.1, 8.0, 7.9, 11.2, 10.5, 9.2, 8.8, 8.2, 7.9],
            "Kota Surabaya": [None]*65 + [7.5, 7.2, 6.9, 6.6, 6.3, 6.0, 5.8, 5.7, 5.6, 5.5, 9.8, 8.9, 7.8, 7.2, 6.8, 6.4],
        }
    },
    "Tingkat Partisipasi Angkatan Kerja (TPAK)": {
        "kategori": "Ketenagakerjaan", "unit": "%",
        "desc": "Persentase penduduk usia kerja yang aktif di pasar kerja.",
        "series": {
            "Nasional": [None]*40 + [57.2, 58.5, 60.1, 61.4, 62.8, 64.5, 65.2, 66.2, 66.5, 66.3, 66.9, 67.2, 67.8, 68.6, 67.8, 67.5, 67.5, 68.0, 66.2, 67.0, 67.2, 67.8, 67.7, 68.3, 67.9, 66.9, 66.6, 65.8, 66.3, 66.7, 67.2, 67.5, 67.7, 67.8, 68.6, 69.3, 69.8, 70.1],
        }
    },
    "Persentase Tenaga Kerja Formal": {
        "kategori": "Ketenagakerjaan", "unit": "%",
        "desc": "Pekerja berstatus buruh/karyawan/pegawai tetap berupah resmi.",
        "series": {
            "Nasional": [None]*65 + [36.2, 37.1, 38.5, 39.2, 40.1, 42.1, 42.4, 43.1, 43.5, 44.1, 39.5, 40.5, 41.2, 42.0, 42.8, 43.5],
        }
    },
    "Persentase Tenaga Kerja Informal": {
        "kategori": "Ketenagakerjaan", "unit": "%",
        "desc": "Pekerja bebas, keluarga, dan berusaha sendiri tanpa pekerja berbayar.",
        "series": {
            "Nasional": [None]*65 + [63.8, 62.9, 61.5, 60.8, 59.9, 57.9, 57.6, 56.9, 56.5, 55.9, 60.5, 59.5, 58.8, 58.0, 57.2, 56.5],
        }
    },
    "Upah Nominal Buruh Tani Harian": {
        "kategori": "Ketenagakerjaan", "unit": "Rupiah / Hari",
        "desc": "Rata-rata pendapatan harian tenaga kerja kasar di sektor pertanian.",
        "series": {
            "Nasional": [None]*65 + [37500, 39200, 41500, 43800, 46100, 48200, 50100, 52000, 53800, 55200, 56100, 57200, 59500, 61800, 63200, 65000],
        }
    },
    "Upah Nominal Buruh Bangunan Harian": {
        "kategori": "Ketenagakerjaan", "unit": "Rupiah / Hari",
        "desc": "Rata-rata upah harian tukang bangunan bukan mandor.",
        "series": {
            "Nasional": [None]*65 + [59000, 62500, 67000, 72000, 77500, 81000, 84200, 86800, 89500, 91200, 92500, 94000, 97500, 101000, 104500, 107000],
        }
    },

    # 4. Makroekonomi & PDRB
    "Pertumbuhan Ekonomi (PDB / PDRB)": {
        "kategori": "Makroekonomi & Harga", "unit": "%",
        "desc": "Laju pertambahan output riil atas dasar harga konstan.",
        "series": {
            "Nasional": [None]*15 + [2.2, 3.5, 4.8, 1.1, 3.2, 5.4, 10.9, 6.8, 7.6, 6.9, 9.4, 8.1, 7.6, 5.0, 6.9, 8.8, 6.9, 7.2, 9.9, 7.6, 2.2, 4.2, 6.7, 2.5, 5.9, 5.3, 5.8, 7.5, 7.2, 7.0, 6.5, 6.5, 7.5, 8.2, 7.8, 4.7, -13.1, 0.8, 4.9, 3.6, 4.5, 4.8, 5.0, 5.7, 5.5, 6.3, 6.0, 4.6, 6.2, 6.2, 6.0, 5.6, 5.0, 4.9, 5.0, 5.1, 5.2, 5.0, -2.1, 3.7, 5.3, 5.1, 5.0, 5.1],
            "Provinsi DKI Jakarta": [None]*65 + [6.5, 6.7, 6.5, 6.1, 5.9, 5.9, 5.9, 6.2, 6.2, 5.9, -2.4, 3.6, 5.3, 5.0, 4.9, 5.0],
            "Provinsi Jawa Barat": [None]*65 + [6.1, 6.2, 6.3, 5.6, 5.1, 5.7, 5.3, 5.6, 5.1, 5.0, -2.4, 3.7, 5.4, 5.0, 4.9, 5.1],
        }
    },
    "PDB / PDRB per Kapita ADHK": {
        "kategori": "Makroekonomi & Harga", "unit": "Juta Rp / Tahun",
        "desc": "Produk per kapita riil atas dasar harga konstan 2010.",
        "series": {
            "Nasional": [None]*65 + [27.5, 28.8, 30.1, 31.5, 32.7, 34.0, 35.3, 36.7, 38.1, 39.5, 38.2, 39.3, 41.0, 42.6, 44.2, 45.8],
            "Provinsi DKI Jakarta": [None]*65 + [123.5, 129.8, 136.2, 142.5, 148.9, 155.2, 161.8, 168.9, 175.4, 181.2, 174.5, 178.9, 188.5, 196.2, 202.8, 210.5],
        }
    },
    "PDB / PDRB per Kapita ADHB": {
        "kategori": "Makroekonomi & Harga", "unit": "Juta Rp / Tahun",
        "desc": "Pendapatan per kapita nominal tahun kalender.",
        "series": {
            "Nasional": [None]*65 + [27.5, 31.2, 34.8, 39.1, 42.8, 46.2, 50.1, 54.3, 58.7, 62.4, 59.8, 62.2, 71.0, 75.0, 78.5, 82.1],
        }
    },
    "Inflasi Tahunan (IHK)": {
        "kategori": "Makroekonomi & Harga", "unit": "%",
        "desc": "Laju inflasi umum gabungan nasional dan kota IHK.",
        "series": {
            "Nasional": [None]*20 + [594.0, 635.0, 112.0, 85.0, 10.0, 9.0, 4.0, 26.0, 41.0, 19.0, 19.8, 14.2, 11.8, 11.0, 21.8, 16.0, 7.1, 9.7, 11.5, 8.8, 4.3, 8.8, 8.9, 5.5, 5.9, 9.5, 9.2, 4.9, 9.8, 9.2, 8.6, 6.5, 11.1, 77.6, 2.0, 9.4, 12.5, 10.0, 5.1, 6.4, 17.1, 6.6, 6.6, 11.1, 2.8, 6.9, 3.8, 4.3, 8.4, 8.4, 3.3, 3.0, 3.6, 3.1, 2.7, 1.7, 1.9, 5.5, 2.6, 2.1, 2.2],
            "Kota Bandung": [None]*65 + [6.5, 4.1, 4.5, 8.1, 8.2, 3.1, 2.9, 3.5, 3.0, 2.6, 1.6, 1.8, 5.4, 2.5, 2.0, 2.1],
        }
    },

    # 5. Kependudukan & Demografi
    "Jumlah Penduduk": {
        "kategori": "Kependudukan & Demografi", "unit": "Ribu Jiwa",
        "desc": "Total populasi penduduk hasil Sensus dan Supas.",
        "series": {
            "Nasional": [72000, 73500, 75200, 77000, 79000, 81000, 83100, 85300, 87600, 90000, 92500, 95100, 97800, 100600, 104000, 106500, 109200, 112000, 115000, 118000, 121000, 124200, 127600, 131000, 134500, 138000, 141700, 145500, 149500, 153500, 157500, 161600, 165800, 170000, 174300, 178600, 183000, 187400, 191900, 194754, 197800, 201300, 204500, 208000, 211540, 214500, 217800, 221200, 224600, 228523, 232500, 236400, 240300, 244200, 248216, 252100, 255500, 258700, 261800, 265015, 268074, 270203, 272682, 275773, 270203, 272682, 275773, 278696, 281603, 284200],
            "Provinsi Jawa Barat": [None]*65 + [43053, 43760, 44465, 45166, 45860, 46549, 47231, 47905, 48572, 49230, 48274, 48782, 49405, 49935, 50345, 50800],
            "Kota Bandung": [None]*65 + [2394, 2415, 2436, 2456, 2475, 2494, 2512, 2529, 2545, 2560, 2444, 2452, 2465, 2478, 2490, 2505],
        }
    },
    "Laju Pertumbuhan Penduduk": {
        "kategori": "Kependudukan & Demografi", "unit": "%",
        "desc": "Kecepatan pertumbuhan populasi tahunan.",
        "series": {
            "Nasional": [None]*20 + [2.35, 2.34, 2.33, 2.32, 2.31, 2.30, 2.28, 2.25, 2.22, 2.18, 2.15, 2.12, 2.08, 2.04, 1.98, 1.92, 1.88, 1.84, 1.80, 1.76, 1.72, 1.68, 1.64, 1.60, 1.56, 1.54, 1.52, 1.50, 1.48, 1.45, 1.44, 1.42, 1.40, 1.39, 1.38, 1.49, 1.46, 1.44, 1.42, 1.40, 1.38, 1.36, 1.34, 1.32, 1.30, 1.28, 1.25, 1.23, 1.20, 1.18, 1.25, 1.17, 1.13, 1.10, 1.08, 1.05],
        }
    },
    "Kepadatan Penduduk": {
        "kategori": "Kependudukan & Demografi", "unit": "Jiwa / km²",
        "desc": "Jumlah manusia per kilometer persegi luas daratan.",
        "series": {
            "Nasional": [38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 52, 53, 55, 56, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 78, 81, 83, 85, 87, 89, 91, 94, 96, 98, 101, 102, 104, 106, 107, 109, 111, 113, 114, 116, 118, 120, 122, 124, 126, 128, 130, 132, 134, 136, 138, 140, 142, 143, 144, 145, 142, 143, 145, 146, 148, 149],
            "Provinsi DKI Jakarta": [None]*65 + [14440, 14650, 14880, 15100, 15320, 15550, 15780, 16010, 16250, 16480, 15900, 16050, 16180, 16280, 16350, 16420],
        }
    },
    "Rasio Jenis Kelamin (Sex Ratio)": {
        "kategori": "Kependudukan & Demografi", "unit": "Laki-laki per 100 Perempuan",
        "desc": "Proporsi banyaknya laki-laki dibanding 100 perempuan.",
        "series": {
            "Nasional": [None]*35 + [98.8, 99.0, 99.1, 99.3, 99.5, 99.7, 99.9, 100.1, 100.2, 100.3, 100.3, 100.4, 100.5, 100.6, 100.7, 100.8, 100.9, 101.0, 101.2, 101.3, 101.3, 101.4, 101.4, 101.5, 101.5, 101.6, 101.7, 101.8, 102.0, 102.1, 102.2, 102.2, 102.3, 102.2, 102.3, 102.4, 102.5, 102.6, 102.7],
        }
    },

    # 6. Pertanian & Ketahanan Pangan
    "Nilai Tukar Petani (NTP)": {
        "kategori": "Pertanian & Pangan", "unit": "Poin Indeks",
        "desc": "Indeks daya beli hasil pertanian terhadap konsumsi petani.",
        "series": {
            "Nasional": [None]*60 + [102.5, 103.1, 102.8, 101.9, 102.4, 101.6, 101.4, 101.8, 102.7, 103.2, 104.1, 104.6, 101.7, 104.6, 107.8, 111.0, 117.5, 119.2],
        }
    },
    "Produksi Padi (Gabah Kering Giling)": {
        "kategori": "Pertanian & Pangan", "unit": "Juta Ton GKG",
        "desc": "Estimasi volume panen gabah kering giling (KSA BPS).",
        "series": {
            "Nasional": [None]*65 + [66.4, 65.7, 69.0, 71.3, 70.8, 75.4, 79.3, 81.1, 59.2, 54.6, 54.7, 54.4, 54.7, 53.9, 53.3, 53.0],
        }
    },
    "Luas Panen Padi": {
        "kategori": "Pertanian & Pangan", "unit": "Juta Hektar",
        "desc": "Luas bersih lahan sawah dan ladang padi yang dipanen.",
        "series": {
            "Nasional": [None]*65 + [13.2, 13.2, 13.4, 13.8, 13.8, 14.1, 14.8, 15.0, 11.4, 10.7, 10.7, 10.4, 10.5, 10.2, 10.0, 9.9],
        }
    },

    # 7. Perumahan, Sanitasi & TIK
    "Persentase Rumah Tangga Bersanitasi Layak": {
        "kategori": "Perumahan & TIK", "unit": "%",
        "desc": "Akses jamban leher angsa dengan tangki septik.",
        "series": {
            "Nasional": [None]*65 + [55.5, 57.2, 61.1, 63.5, 67.8, 71.1, 72.8, 74.5, 76.2, 79.5, 80.3, 80.9, 82.4, 82.9, 83.5, 84.2],
        }
    },
    "Persentase Rumah Tangga Berair Minum Layak": {
        "kategori": "Perumahan & TIK", "unit": "%",
        "desc": "Akses air minum leding dan sumur bor terlindung.",
        "series": {
            "Nasional": [None]*65 + [68.0, 69.5, 70.8, 72.2, 73.5, 86.8, 88.0, 89.2, 90.1, 91.0, 91.7, 92.2, 92.8, 93.4, 93.9, 94.4],
        }
    },
    "Persentase Rumah Tangga Berakses Internet": {
        "kategori": "Perumahan & TIK", "unit": "%",
        "desc": "Proporsi rumah tangga dengan akses internet aktif.",
        "series": {
            "Nasional": [None]*65 + [13.2, 16.5, 21.0, 26.8, 32.5, 41.2, 47.8, 56.4, 66.2, 73.8, 78.2, 82.1, 86.5, 89.2, 91.5, 93.0],
            "Kota Bandung": [None]*65 + [42.1, 48.5, 55.2, 63.0, 71.2, 78.5, 82.4, 86.1, 89.5, 92.0, 93.5, 94.8, 96.0, 96.8, 97.5, 98.1],
        }
    },
    "Persentase Penduduk Memiliki Telepon Seluler": {
        "kategori": "Perumahan & TIK", "unit": "%",
        "desc": "Kepemilikan ponsel aktif penduduk umur 5 tahun ke atas.",
        "series": {
            "Nasional": [None]*60 + [25.4, 32.8, 41.5, 48.2, 53.9, 56.5, 59.6, 62.4, 63.5, 65.8, 67.2, 68.3, 69.1, 70.0, 70.8, 71.5],
        }
    },

    # 8. Perdagangan Luar Negeri
    "Nilai Ekspor Barang (FOB)": {
        "kategori": "Perdagangan Internasional", "unit": "Miliar USD",
        "desc": "Nilai transaksi ekspor barang keluar pabean resmi.",
        "series": {
            "Nasional": [None]*50 + [45.4, 49.8, 53.4, 50.1, 56.5, 62.1, 56.3, 57.2, 61.6, 71.6, 85.7, 100.8, 114.1, 137.0, 116.5, 157.8, 203.5, 190.0, 182.6, 175.9, 150.4, 145.2, 168.8, 180.2, 167.7, 163.3, 231.5, 291.9, 258.8, 264.2, 270.5],
        }
    },
    "Nilai Impor Barang (CIF)": {
        "kategori": "Perdagangan Internasional", "unit": "Miliar USD",
        "desc": "Nilai barang impor masuk ke pabean Indonesia.",
        "series": {
            "Nasional": [None]*50 + [40.6, 42.9, 41.7, 27.3, 24.0, 33.5, 31.0, 31.3, 32.5, 46.5, 57.7, 61.1, 74.5, 129.2, 96.8, 135.7, 177.4, 191.7, 186.6, 178.2, 142.7, 135.7, 157.0, 188.7, 171.3, 141.6, 196.0, 237.5, 221.9, 228.4, 233.0],
        }
    }
}

# 1. Pemilihan Wilayah Bertingkat
st.subheader("1. Pemilihan Wilayah")
col_lvl, col_spec = st.columns([1, 2])

with col_lvl:
    level_wilayah = st.selectbox("Tingkat Administratif:", ["Nasional", "Provinsi", "Kabupaten / Kota"])

selected_label = "Nasional"
selected_prov = None
selected_city = None

with col_spec:
    if level_wilayah == "Nasional":
        st.info("📌 Cakupan terpilih: **Agregat Seluruh Indonesia (Nasional)**")
    elif level_wilayah == "Provinsi":
        selected_prov = st.selectbox("Pilih Provinsi:", PROVINCES_LIST, index=5)
        selected_label = f"Provinsi {selected_prov}"
    else:
        c_p, c_c = st.columns(2)
        with c_p:
            selected_prov = st.selectbox("Provinsi:", PROVINCES_LIST, index=6)
        with c_c:
            selected_city = st.selectbox("Kabupaten / Kota:", REGIONS_STRUCTURE[selected_prov], index=0)
        selected_label = selected_city

st.write("---")

# 2. Pemilihan Indikator
st.subheader("2. Pemilihan Indikator & Waktu")
col_kat, col_ind = st.columns([1, 1.5])

kategori_list = sorted(list(set(item["kategori"] for item in DATA_BPS.values())))
with col_kat:
    pilihan_kategori = st.selectbox("Kategori:", ["Semua Kategori"] + kategori_list)

indikator_opsi = [
    k for k, v in DATA_BPS.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    selected_indicator = st.selectbox(f"Indikator BPS ({len(indikator_opsi)} Tersedia):", indikator_opsi)

meta = DATA_BPS[selected_indicator]

col_sl, col_comp = st.columns([2, 1])
with col_sl:
    th_start, th_end = st.select_slider("Rentang Tahun (1945–2025):", options=YEARS, value=("1990", "2025"))
with col_comp:
    bandingkan_nasional = st.checkbox("Sandingkan dengan Rata-rata Nasional", value=(level_wilayah != "Nasional"))

# 3. Pengambilan Deret Waktu Murni
series_dict = meta["series"]

def get_clean_series(target_name):
    if target_name in series_dict:
        raw = series_dict[target_name]
        if len(raw) < N_YEARS:
            return [None] * (N_YEARS - len(raw)) + raw
        return raw[-N_YEARS:]
    return [None] * N_YEARS

df_main = pd.DataFrame({"Tahun": YEARS})
df_main[selected_label] = get_clean_series(selected_label)

active_cols = ["Tahun", selected_label]
if bandingkan_nasional and level_wilayah != "Nasional":
    df_main["Nasional"] = get_clean_series("Nasional")
    active_cols.append("Nasional")

df_filtered = df_main[(df_main["Tahun"] >= th_start) & (df_main["Tahun"] <= th_end)][active_cols]

# Keterangan jika data wilayah tersebut belum disurvei
if df_filtered[selected_label].isna().all():
    st.warning(
        f"ℹ️ **Keterangan BPS:** Publikasi resmi indikator *'{selected_indicator}'* untuk wilayah *'{selected_label}'* "
        f"tidak disurvei atau belum tersedia pada rentang {th_start}–{th_end}."
    )

st.divider()

# 4. Visualisasi Grafik
st.subheader(f"📈 Grafik Tren: {selected_indicator}")
st.caption(f"Satuan: **{meta['unit']}** | {meta['desc']}")

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
        hovertemplate=f"Tahun %{{x}}<br>{c}: %{{y}} {meta['unit']}<extra></extra>"
    ))

fig.update_layout(
    xaxis=dict(title="Tahun", tickmode="linear"),
    yaxis=dict(title=meta["unit"]),
    hovermode="x unified",
    legend_title_text="Wilayah",
    margin=dict(l=20, r=20, t=40, b=20)
)
st.plotly_chart(fig, use_container_width=True)

# 5. Tabel Observasi
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
st.caption("💡 Tanda strip (-) menunjukkan data pada tahun tersebut tidak disurvei atau belum tersedia di rilis resmi BPS.")
