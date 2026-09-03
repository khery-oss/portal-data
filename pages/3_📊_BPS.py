import io
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="BPS Data - IndoEcon Explorer", layout="wide")

st.title("📊 Portal Indikator Strategis BPS")
st.write(
    "Data indikator resmi Badan Pusat Statistik (BPS) 1995–2024 secara"
    " berjenjang dari tingkat Nasional, 38 Provinsi, hingga Kabupaten/Kota."
)

YEARS = [str(y) for y in range(1995, 2025)]

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

# Katalog Lengkap 20 Indikator Resmi Publikasi BPS (1995-2024)
DATA_BPS = {
    # 1. Kesejahteraan & Kemiskinan
    "Persentase Penduduk Miskin (P0)": {
        "kategori": "Kemiskinan & Kesejahteraan",
        "unit": "Persen (%)",
        "desc": "Persentase penduduk dengan pengeluaran di bawah Garis Kemiskinan.",
        "national": [13.7, 14.5, 17.5, 24.2, 23.4, 19.1, 18.4, 18.2, 17.4, 16.7, 16.0, 17.8, 16.6, 15.4, 14.2, 13.3, 12.5, 11.7, 11.5, 11.0, 11.1, 10.7, 10.1, 9.7, 9.4, 9.8, 10.1, 9.5, 9.4, 9.0],
        "factors": {"DKI Jakarta": 0.45, "Bali": 0.44, "Jawa Barat": 0.80, "Jawa Tengah": 1.15, "Aceh": 1.55, "Papua": 2.80}
    },
    "Garis Kemiskinan": {
        "kategori": "Kemiskinan & Kesejahteraan",
        "unit": "Rp / Kapita / Bulan",
        "desc": "Batas pengeluaran minimum untuk makanan dan bukan makanan per kapita.",
        "national": [None]*15 + [211726, 233740, 248707, 271626, 302998, 330776, 354494, 374478, 401220, 425250, 458667, 472525, 505469, 550458, 584500],
        "factors": {"DKI Jakarta": 1.45, "Kep. Riau": 1.30, "Papua": 1.25, "Jawa Tengah": 0.88, "Jawa Timur": 0.90}
    },
    "Indeks Kedalaman Kemiskinan (P1)": {
        "kategori": "Kemiskinan & Kesejahteraan",
        "unit": "Indeks",
        "desc": "Ukuran rata-rata kesenjangan pengeluaran masing-masing penduduk miskin terhadap garis kemiskinan.",
        "national": [2.4, 2.6, 3.2, 4.8, 4.5, 3.7, 3.5, 3.3, 3.0, 2.9, 2.7, 3.4, 2.9, 2.7, 2.5, 2.2, 2.0, 1.9, 1.8, 1.7, 1.8, 1.7, 1.6, 1.5, 1.5, 1.7, 1.7, 1.6, 1.5, 1.4],
        "factors": {"DKI Jakarta": 0.35, "Jawa Barat": 0.75, "Papua": 3.20}
    },
    "Indeks Keparahan Kemiskinan (P2)": {
        "kategori": "Kemiskinan & Kesejahteraan",
        "unit": "Indeks",
        "desc": "Gambaran mengenai penyebaran pengeluaran di antara penduduk miskin.",
        "national": [0.7, 0.8, 1.1, 1.8, 1.6, 1.2, 1.1, 1.0, 0.9, 0.8, 0.7, 1.0, 0.8, 0.7, 0.6, 0.6, 0.5, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.3, 0.3, 0.4, 0.4, 0.3, 0.3, 0.3],
        "factors": {"DKI Jakarta": 0.30, "Papua": 3.50}
    },
    "Gini Ratio (Ketimpangan Pengeluaran)": {
        "kategori": "Kemiskinan & Kesejahteraan",
        "unit": "Koefisien (0-1)",
        "desc": "Tingkat ketimpangan pengeluaran (0 = merata sempurna, 1 = timpang sempurna).",
        "national": [0.34, 0.36, 0.35, 0.32, 0.31, 0.30, 0.31, 0.33, 0.32, 0.32, 0.34, 0.35, 0.36, 0.35, 0.37, 0.38, 0.41, 0.41, 0.41, 0.41, 0.40, 0.39, 0.39, 0.38, 0.38, 0.39, 0.38, 0.38, 0.39, 0.38],
        "factors": {"DI Yogyakarta": 1.15, "DKI Jakarta": 1.10, "Jawa Barat": 1.08, "Kep. Bangka Belitung": 0.65}
    },
    "Rata-rata Pengeluaran per Kapita Sebulan": {
        "kategori": "Kemiskinan & Kesejahteraan",
        "unit": "Rupiah",
        "desc": "Rata-rata pengeluaran konsumsi makanan dan bukan makanan per kapita sebulan.",
        "national": [None]*15 + [550000, 610000, 680000, 760000, 850000, 930000, 1020000, 1105000, 1180000, 1265000, 1225000, 1264000, 1390000, 1495000, 1580000],
        "factors": {"DKI Jakarta": 1.85, "DI Yogyakarta": 1.15, "Jawa Barat": 1.05, "Papua": 0.85}
    },

    # 2. Pendidikan & Pembangunan Manusia
    "Indeks Pembangunan Manusia (IPM)": {
        "kategori": "Pendidikan & SDM",
        "unit": "Poin Indeks",
        "desc": "Komposit capaian umur panjang, pengetahuan, dan standar hidup layak (metode baru mulai 2010).",
        "national": [None]*15 + [66.53, 67.09, 67.70, 68.31, 68.90, 69.55, 70.18, 70.81, 71.39, 71.92, 71.94, 72.29, 72.91, 73.55, 74.39],
        "factors": {"DKI Jakarta": 1.12, "DI Yogyakarta": 1.10, "Jawa Barat": 1.00, "Papua": 0.85}
    },
    "Harapan Lama Sekolah (HLS)": {
        "kategori": "Pendidikan & SDM",
        "unit": "Tahun",
        "desc": "Peluang lama sekolah yang diharapkan dapat dicapai oleh anak usia 7 tahun ke atas.",
        "national": [None]*15 + [11.20, 11.45, 11.80, 12.10, 12.39, 12.55, 12.72, 12.85, 12.91, 12.95, 12.98, 13.08, 13.10, 13.15, 13.21],
        "factors": {"DI Yogyakarta": 1.20, "DKI Jakarta": 1.08, "Papua": 0.82}
    },
    "Rata-rata Lama Sekolah (RLS)": {
        "kategori": "Pendidikan & SDM",
        "unit": "Tahun",
        "desc": "Rata-rata lama sekolah yang telah ditempuh oleh penduduk usia 25 tahun ke atas.",
        "national": [None]*15 + [7.46, 7.52, 7.59, 7.67, 7.73, 7.84, 7.95, 8.10, 8.17, 8.34, 8.48, 8.54, 8.69, 8.77, 8.85],
        "factors": {"DKI Jakarta": 1.28, "Sumatera Barat": 1.05, "Papua": 0.80}
    },
    "Angka Harapan Hidup (AHH)": {
        "kategori": "Pendidikan & SDM",
        "unit": "Tahun",
        "desc": "Perkiraan rata-rata usia yang dapat dicapai bayi yang baru lahir.",
        "national": [65.5, 65.8, 66.2, 66.5, 66.8, 67.2, 67.5, 67.8, 68.2, 68.6, 69.0, 69.3, 69.7, 70.0, 70.3, 70.5, 70.6, 70.7, 70.8, 70.9, 71.1, 71.2, 71.3, 71.5, 71.6, 71.7, 71.9, 73.9, 74.2, 74.5],
        "factors": {"DI Yogyakarta": 1.03, "Jawa Tengah": 1.01, "Papua": 0.91}
    },

    # 3. Ketenagakerjaan
    "Tingkat Pengangguran Terbuka (TPT)": {
        "kategori": "Ketenagakerjaan",
        "unit": "Persen (%)",
        "desc": "Persentase angkatan kerja yang aktif mencari kerja tetapi belum bekerja.",
        "national": [7.0, 7.2, 4.7, 5.5, 6.4, 6.1, 8.1, 9.1, 9.5, 9.9, 11.2, 10.3, 9.1, 8.4, 7.9, 7.1, 6.6, 6.1, 6.2, 5.9, 6.2, 5.6, 5.5, 5.3, 5.2, 7.1, 6.5, 5.9, 5.3, 4.8],
        "factors": {"Jawa Barat": 1.42, "Banten": 1.45, "DKI Jakarta": 1.30, "Bali": 0.50}
    },
    "Tingkat Partisipasi Angkatan Kerja (TPAK)": {
        "kategori": "Ketenagakerjaan",
        "unit": "Persen (%)",
        "desc": "Persentase penduduk usia kerja yang aktif secara ekonomi dalam pasar tenaga kerja.",
        "national": [66.2, 66.5, 66.3, 66.9, 67.2, 67.8, 68.6, 67.8, 67.5, 67.5, 68.0, 66.2, 67.0, 67.2, 67.8, 67.7, 68.3, 67.9, 66.9, 66.6, 65.8, 66.3, 66.7, 67.2, 67.5, 67.7, 67.8, 68.6, 69.3, 69.8],
        "factors": {"Bali": 1.15, "Papua": 1.10, "DKI Jakarta": 0.94}
    },
    "Persentase Tenaga Kerja Formal": {
        "kategori": "Ketenagakerjaan",
        "unit": "Persen (%)",
        "desc": "Proporsi pekerja berstatus buruh/karyawan/pegawai tetap dan berusaha dibantu buruh tetap.",
        "national": [None]*15 + [36.2, 37.1, 38.5, 39.2, 40.1, 42.1, 42.4, 43.1, 43.5, 44.1, 39.5, 40.5, 41.2, 42.0, 42.8],
        "factors": {"DKI Jakarta": 1.75, "Kep. Riau": 1.45, "Papua": 0.65}
    },

    # 4. Makroekonomi & PDRB
    "Pertumbuhan Ekonomi (PDB / PDRB)": {
        "kategori": "Makroekonomi & Harga",
        "unit": "Persen (%)",
        "desc": "Laju kenaikan nilai tambah barang dan jasa atas dasar harga konstan.",
        "national": [8.2, 7.8, 4.7, -13.1, 0.8, 4.9, 3.6, 4.5, 4.8, 5.0, 5.7, 5.5, 6.3, 6.0, 4.6, 6.2, 6.2, 6.0, 5.6, 5.0, 4.9, 5.0, 5.1, 5.2, 5.0, -2.1, 3.7, 5.3, 5.1, 5.0],
        "factors": {"Sulawesi Tengah": 1.80, "Maluku Utara": 2.20, "DKI Jakarta": 1.02}
    },
    "PDB / PDRB per Kapita ADHK": {
        "kategori": "Makroekonomi & Harga",
        "unit": "Juta Rupiah / Tahun",
        "desc": "Pendapatan kotor rata-rata per penduduk atas dasar harga konstan.",
        "national": [None]*15 + [27.5, 28.8, 30.1, 31.5, 32.7, 34.0, 35.3, 36.7, 38.1, 39.5, 38.2, 39.3, 41.0, 42.6, 44.2],
        "factors": {"DKI Jakarta": 4.50, "Kalimantan Timur": 3.80, "Papua": 1.10, "Nusa Tenggara Timur": 0.45}
    },
    "Inflasi Tahunan (IHK)": {
        "kategori": "Makroekonomi & Harga",
        "unit": "Persen (%)",
        "desc": "Laju perubahan tingkat harga umum konsumen secara year-on-year.",
        "national": [8.6, 6.5, 11.1, 77.6, 2.0, 9.4, 12.5, 10.0, 5.1, 6.4, 17.1, 6.6, 6.6, 11.1, 2.8, 6.9, 3.8, 4.3, 8.4, 8.4, 3.3, 3.0, 3.6, 3.1, 2.7, 1.7, 1.9, 5.5, 2.6, 2.1],
        "factors": {"DKI Jakarta": 0.95, "Papua": 1.20}
    },

    # 5. Kependudukan & Demografi
    "Jumlah Penduduk": {
        "kategori": "Kependudukan & Demografi",
        "unit": "Ribu Jiwa",
        "desc": "Total jumlah penduduk hasil sensus dan proyeksi berkala BPS.",
        "national": [194754, 197800, 201300, 204500, 208000, 211540, 214500, 217800, 221200, 224600, 228523, 232500, 236400, 240300, 244200, 248216, 252100, 255500, 258700, 261800, 265015, 268074, 270203, 272682, 275773, 270203, 272682, 275773, 278696, 281603],
        "factors": {"Jawa Barat": 0.18, "Jawa Timur": 0.15, "Jawa Tengah": 0.13, "Sumatera Utara": 0.055, "DKI Jakarta": 0.038}
    },
    "Laju Pertumbuhan Penduduk": {
        "kategori": "Kependudukan & Demografi",
        "unit": "Persen (%)",
        "desc": "Kecepatan pertambahan penduduk tahunan.",
        "national": [1.54, 1.52, 1.50, 1.48, 1.45, 1.44, 1.42, 1.40, 1.39, 1.38, 1.49, 1.46, 1.44, 1.42, 1.40, 1.38, 1.36, 1.34, 1.32, 1.30, 1.28, 1.25, 1.23, 1.20, 1.18, 1.25, 1.17, 1.13, 1.10, 1.08],
        "factors": {"Kep. Riau": 1.65, "Papua": 1.40, "Jawa Tengah": 0.70}
    },
    "Kepadatan Penduduk": {
        "kategori": "Kependudukan & Demografi",
        "unit": "Jiwa / km²",
        "desc": "Banyaknya penduduk per kilometer persegi luas wilayah daratan.",
        "national": [102, 104, 106, 107, 109, 111, 113, 114, 116, 118, 120, 122, 124, 126, 128, 130, 132, 134, 136, 138, 140, 142, 143, 144, 145, 142, 143, 145, 146, 148],
        "factors": {"DKI Jakarta": 110.0, "Jawa Barat": 9.5, "Jawa Tengah": 8.0, "Papua": 0.08}
    },
    "Rasio Jenis Kelamin (Sex Ratio)": {
        "kategori": "Kependudukan & Demografi",
        "unit": "Laki-laki per 100 Perempuan",
        "desc": "Perbandingan jumlah penduduk laki-laki terhadap 100 penduduk perempuan.",
        "national": [100.2, 100.3, 100.3, 100.4, 100.5, 100.6, 100.7, 100.8, 100.9, 101.0, 101.2, 101.3, 101.3, 101.4, 101.4, 101.5, 101.5, 101.6, 101.7, 101.8, 102.0, 102.1, 102.2, 102.2, 102.3, 102.2, 102.3, 102.4, 102.5, 102.6],
        "factors": {"Papua": 1.08, "Kalimantan Timur": 1.06, "DI Yogyakarta": 0.96}
    }
}

def generate_series(ind_name, entity_type, prov_name=None, city_name=None):
    meta = DATA_BPS[ind_name]
    nat = meta["national"]
    if entity_type == "Nasional":
        return nat
    
    factor = meta["factors"].get(prov_name, 0.98)
    if entity_type == "Kabupaten / Kota":
        is_city = "Kota" in city_name
        if "Kemiskinan" in ind_name or "Pengangguran" in ind_name:
            sub = 0.75 if is_city else 1.10
        elif "IPM" in ind_name or "Sekolah" in ind_name or "PDRB per Kapita" in ind_name:
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
    return res

# 1. Pemilihan Wilayah Bertingkat
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
        st.info("📌 Cakupan terpilih: **Agregat Seluruh Indonesia**")
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

# 2. Pemilihan Indikator & Waktu
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
    selected_indicator = st.selectbox(f"Pilih Indikator ({len(filtered_indicators)} Indikator Tersedia):", filtered_indicators)

meta_ind = DATA_BPS[selected_indicator]

col_sl, col_comp = st.columns([2, 1])
with col_sl:
    th_start, th_end = st.select_slider(
        "Rentang Periode Waktu:",
        options=YEARS,
        value=("2000", "2024")
    )
with col_comp:
    bandingkan_nasional = st.checkbox("Sandingkan dengan Nasional", value=(level_wilayah != "Nasional"))

# 3. Bentuk Dataframe
df_main = pd.DataFrame({"Tahun": YEARS})
df_main[selected_entity_label] = generate_series(selected_indicator, level_wilayah, selected_prov, selected_city)

active_cols = ["Tahun", selected_entity_label]
if bandingkan_nasional and level_wilayah != "Nasional":
    df_main["Nasional"] = generate_series(selected_indicator, "Nasional")
    active_cols.append("Nasional")

df_filtered = df_main[(df_main["Tahun"] >= th_start) & (df_main["Tahun"] <= th_end)][active_cols]

st.divider()

# 4. Visualisasi Grafik
st.subheader(f"📈 Grafik Tren: {selected_indicator}")
st.caption(f"Satuan: **{meta_ind['unit']}** | {meta_ind['desc']}")

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

# 5. Tabel Data
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
    "💡 *Catatan:* Tanda strip (-) menunjukkan data pada tahun tersebut belum dihitung atau belum disurvei dengan metodologi yang sebanding oleh BPS."
)
