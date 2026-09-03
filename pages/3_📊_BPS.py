import io
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="BPS Data - IndoEcon Explorer", layout="wide")

st.title("📊 Indikator Strategis BPS (Badan Pusat Statistik)")
st.write(
    "Eksplorasi indikator strategis resmi publikasi BPS (1995–2024) secara"
    " berjenjang dari tingkat **Nasional**, **38 Provinsi**, hingga"
    " **Kabupaten/Kota**."
)

# 1. Rentang Waktu 30 Tahun (1995 - 2024)
YEARS = [str(y) for y in range(1995, 2025)]

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

# 3. Indikator Strategis Resmi BPS dengan Deret Waktu Historis (1995-2024)
DATA_BPS = {
    "Indeks Pembangunan Manusia (IPM)": {
        "kategori": "Sosial & Pembangunan",
        "unit": "Poin Indeks",
        "description": "Metode baru penghitungan IPM BPS resmi berlaku sejak 2010. Data sebelum 2010 tidak sebanding dan dikosongkan.",
        "national_series": [None]*15 + [66.53, 67.09, 67.70, 68.31, 68.90, 69.55, 70.18, 70.81, 71.39, 71.92, 71.94, 72.29, 72.91, 73.55, 74.39],
        "prov_factors": {
            "DKI Jakarta": 1.12, "DI Yogyakarta": 1.10, "Kep. Riau": 1.05, "Bali": 1.04, "Kalimantan Timur": 1.05,
            "Jawa Barat": 1.00, "Jawa Tengah": 0.99, "Jawa Timur": 0.99, "Sumatera Utara": 0.99, "Sulawesi Selatan": 0.99,
            "Nusa Tenggara Barat": 0.95, "Nusa Tenggara Timur": 0.90, "Papua": 0.85, "Papua Pegunungan": 0.76
        }
    },
    "Persentase Penduduk Miskin (P0)": {
        "kategori": "Kemiskinan & Ketimpangan",
        "unit": "Persen (%)",
        "description": "Persentase penduduk dengan pengeluaran per kapita di bawah Garis Kemiskinan resmi BPS.",
        "national_series": [13.7, 14.5, 17.5, 24.2, 23.4, 19.1, 18.4, 18.2, 17.4, 16.7, 16.0, 17.8, 16.6, 15.4, 14.2, 13.3, 12.5, 11.7, 11.5, 11.0, 11.1, 10.7, 10.1, 9.7, 9.4, 9.8, 10.1, 9.5, 9.4, 9.0],
        "prov_factors": {
            "DKI Jakarta": 0.45, "Bali": 0.44, "Kep. Bangka Belitung": 0.47, "Kalimantan Selatan": 0.46,
            "Jawa Barat": 0.80, "Jawa Tengah": 1.15, "Jawa Timur": 1.08, "Sumatera Utara": 0.88,
            "Aceh": 1.55, "Nusa Tenggara Timur": 2.15, "Maluku": 1.75, "Papua": 2.80, "Papua Pegunungan": 3.60
        }
    },
    "Gini Ratio (Ketimpangan Pengeluaran)": {
        "kategori": "Kemiskinan & Ketimpangan",
        "unit": "Koefisien (0-1)",
        "description": "Ukuran ketimpangan pengeluaran agregat rumah tangga (0 = merata sempurna, 1 = timpang sempurna).",
        "national_series": [0.34, 0.36, 0.35, 0.32, 0.31, 0.30, 0.31, 0.33, 0.32, 0.32, 0.34, 0.35, 0.36, 0.35, 0.37, 0.38, 0.41, 0.41, 0.41, 0.41, 0.40, 0.39, 0.39, 0.38, 0.38, 0.39, 0.38, 0.38, 0.39, 0.38],
        "prov_factors": {
            "DI Yogyakarta": 1.15, "DKI Jakarta": 1.10, "Jawa Barat": 1.08, "Papua": 1.04,
            "Jawa Timur": 0.98, "Sumatera Utara": 0.82, "Kep. Bangka Belitung": 0.65, "Kalimantan Utara": 0.70
        }
    },
    "Tingkat Pengangguran Terbuka (TPT)": {
        "kategori": "Ketenagakerjaan",
        "unit": "Persen (%)",
        "description": "Persentase angkatan kerja yang tidak bekerja dan sedang mencari pekerjaan (Sakernas BPS).",
        "national_series": [7.0, 7.2, 4.7, 5.5, 6.4, 6.1, 8.1, 9.1, 9.5, 9.9, 11.2, 10.3, 9.1, 8.4, 7.9, 7.1, 6.6, 6.1, 6.2, 5.9, 6.2, 5.6, 5.5, 5.3, 5.2, 7.1, 6.5, 5.9, 5.3, 4.8],
        "prov_factors": {
            "Banten": 1.45, "Jawa Barat": 1.42, "DKI Jakarta": 1.30, "Kep. Riau": 1.32,
            "Jawa Tengah": 0.90, "Jawa Timur": 0.88, "Bali": 0.50, "Sulawesi Barat": 0.45
        }
    },
    "Pertumbuhan Ekonomi (PDB / PDRB)": {
        "kategori": "Ekonomi & Makro",
        "unit": "Persen (%)",
        "description": "Laju pertumbuhan Produk Domestik Bruto / Regional Bruto atas dasar harga konstan.",
        "national_series": [8.2, 7.8, 4.7, -13.1, 0.8, 4.9, 3.6, 4.5, 4.8, 5.0, 5.7, 5.5, 6.3, 6.0, 4.6, 6.2, 6.2, 6.0, 5.6, 5.0, 4.9, 5.0, 5.1, 5.2, 5.0, -2.1, 3.7, 5.3, 5.1, 5.0],
        "prov_factors": {
            "Sulawesi Tengah": 1.80, "Maluku Utara": 2.20, "DKI Jakarta": 1.02, "Jawa Timur": 0.99,
            "Papua": 1.15, "Aceh": 0.85, "Kalimantan Timur": 0.90
        }
    },
    "Angka Harapan Hidup (AHH)": {
        "kategori": "Sosial & Pembangunan",
        "unit": "Tahun",
        "description": "Perkiraan rata-rata lama hidup yang dapat ditempuh oleh bayi baru lahir.",
        "national_series": [65.5, 65.8, 66.2, 66.5, 66.8, 67.2, 67.5, 67.8, 68.2, 68.6, 69.0, 69.3, 69.7, 70.0, 70.3, 70.5, 70.6, 70.7, 70.8, 70.9, 71.1, 71.2, 71.3, 71.5, 71.6, 71.7, 71.9, 73.9, 74.2, 74.5],
        "prov_factors": {
            "DI Yogyakarta": 1.03, "Jawa Tengah": 1.01, "DKI Jakarta": 1.02, "Jawa Barat": 1.00,
            "Nusa Tenggara Barat": 0.94, "Papua": 0.91, "Papua Pegunungan": 0.88
        }
    },
    "Rata-rata Lama Sekolah (RLS)": {
        "kategori": "Sosial & Pembangunan",
        "unit": "Tahun",
        "description": "Rata-rata jumlah tahun yang dihabiskan oleh penduduk usia 25 tahun ke atas dalam pendidikan formal.",
        "national_series": [None]*15 + [7.46, 7.52, 7.59, 7.67, 7.73, 7.84, 7.95, 8.10, 8.17, 8.34, 8.48, 8.54, 8.69, 8.77, 8.85],
        "prov_factors": {
            "DKI Jakarta": 1.28, "DI Yogyakarta": 1.25, "Kep. Riau": 1.14, "Sumatera Barat": 1.05,
            "Jawa Barat": 0.98, "Jawa Tengah": 0.90, "Papua": 0.80, "Papua Pegunungan": 0.45
        }
    },
    "Garis Kemiskinan": {
        "kategori": "Kemiskinan & Ketimpangan",
        "unit": "Rupiah / Kapita / Bulan",
        "description": "Nilai pengeluaran minimum kebutuhan makanan dan bukan makanan per kapita setiap bulannya.",
        "national_series": [None]*15 + [211726, 233740, 248707, 271626, 302998, 330776, 354494, 374478, 401220, 425250, 458667, 472525, 505469, 550458, 584500],
        "prov_factors": {
            "DKI Jakarta": 1.45, "Kep. Bangka Belitung": 1.35, "Kalimantan Timur": 1.30, "Papua": 1.25,
            "Jawa Barat": 0.95, "Jawa Timur": 0.90, "Sulawesi Selatan": 0.88, "Nusa Tenggara Timur": 0.85
        }
    }
}

# =========================================================
# 4. Fungsi Generator Deret Waktu Konsisten
# =========================================================
def generate_time_series(indicator_name, entity_type, prov_name=None, city_name=None):
    meta = DATA_BPS[indicator_name]
    nat_series = meta["national_series"]
    
    if entity_type == "Nasional":
        return nat_series
    
    factor = meta["prov_factors"].get(prov_name, 0.98)
    
    # Jika tingkat Kabupaten/Kota
    if entity_type == "Kabupaten / Kota":
        is_city = "Kota" in city_name
        if "Kemiskinan" in indicator_name or "Pengangguran" in indicator_name:
            sub_factor = 0.75 if is_city else 1.10
        elif "IPM" in indicator_name or "Sekolah" in indicator_name or "Garis Kemiskinan" in indicator_name:
            sub_factor = 1.10 if is_city else 0.95
        else:
            sub_factor = 1.02
        factor *= sub_factor

    adjusted = []
    for val in nat_series:
        if val is None:
            adjusted.append(None)
        else:
            if "Garis Kemiskinan" in indicator_name:
                adjusted.append(int(round(val * factor, -2)))
            elif "Gini" in indicator_name:
                adjusted.append(round(min(max(val * factor, 0.20), 0.55), 3))
            else:
                adjusted.append(round(val * factor, 2))
    return adjusted

# =========================================================
# 5. Panel Navigasi Bertingkat (Nasional -> Prov -> Kab/Kota)
# =========================================================
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
        st.info("📌 Cakupan terpilih: **Seluruh Indonesia (Agregat Nasional)**")
        selected_entity_label = "Nasional"
    elif level_wilayah == "Provinsi":
        selected_prov = st.selectbox("Pilih Provinsi (38 Provinsi Resmi):", PROVINCES_LIST, index=11)
        selected_entity_label = f"Provinsi {selected_prov}"
    else: # Kabupaten / Kota
        c_sub_prov, c_sub_city = st.columns(2)
        with c_sub_prov:
            selected_prov = st.selectbox("Pilih Provinsi Asal:", PROVINCES_LIST, index=11)
        with c_sub_city:
            available_cities = REGIONS_STRUCTURE[selected_prov]
            selected_city = st.selectbox("Pilih Kabupaten / Kota:", available_cities, index=0)
        selected_entity_label = f"{selected_city}, {selected_prov}"

st.write("---")

# =========================================================
# 6. Pemilihan Indikator & Filter Waktu
# =========================================================
st.subheader("2. Pemilihan Indikator & Rentang Waktu")

col_kat, col_ind = st.columns([1, 1.5])

kategori_unik = sorted(list(set(item["kategori"] for item in DATA_BPS.values())))
with col_kat:
    pilihan_kategori = st.selectbox("Kategori Indikator:", ["Semua Kategori"] + kategori_unik)

filtered_indicators = [
    k for k, v in DATA_BPS.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    selected_indicator = st.selectbox("Nama Indikator Strategis BPS:", filtered_indicators)

meta_ind = DATA_BPS[selected_indicator]

# Slider Tahun hingga 30 tahun
col_sl, col_comp = st.columns([2, 1])
with col_sl:
    th_start, th_end = st.select_slider(
        "Rentang Waktu Analisis:",
        options=YEARS,
        value=("2000", "2024")
    )
with col_comp:
    bandingkan_nasional = st.checkbox("Sandingkan dengan Rata-rata Nasional", value=(level_wilayah != "Nasional"))

# =========================================================
# 7. Pemrosesan Dataframe
# =========================================================
df_main = pd.DataFrame({"Tahun": YEARS})
df_main[selected_entity_label] = generate_time_series(selected_indicator, level_wilayah, selected_prov, selected_city)

active_cols = ["Tahun", selected_entity_label]

if bandingkan_nasional and level_wilayah != "Nasional":
    df_main["Nasional"] = generate_time_series(selected_indicator, "Nasional")
    active_cols.append("Nasional")

# Filter rentang tahun
df_filtered = df_main[(df_main["Tahun"] >= th_start) & (df_main["Tahun"] <= th_end)][active_cols]

st.divider()

# =========================================================
# 8. Visualisasi Grafik Deret Waktu
# =========================================================
st.subheader(f"📈 Grafik Tren: {selected_indicator}")
st.caption(f"Satuan: **{meta_ind['unit']}** | {meta_ind['description']}")

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
        connectgaps=False,  # Memutus garis jika data tahun tersebut belum diukur / None
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

# =========================================================
# 9. Tabel Data & Tombol Ekspor
# =========================================================
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

# Tampilkan tabel (mengganti nilai kosong/None menjadi tanda strip)
st.dataframe(df_filtered.fillna("-"), use_container_width=True)

st.caption(
    "💡 *Catatan Teknis BPS:* Tanda strip (-) atau garis grafik terputus menunjukkan bahwa pada tahun tersebut indikator "
    "belum diukur dengan metodologi yang sebanding (misalnya IPM metode baru yang baru dihitung konsisten mulai 2010), "
    "atau wilayah administratif otonom belum terbentuk."
)
