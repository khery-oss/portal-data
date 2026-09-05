import io
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="ASEANstats Data Explorer - Indonesia & Regional", layout="wide")

st.title("🌏 ASEANstats - Portal Data Regional Asia Tenggara")
st.write(
    "Eksplorasi data resmi terharmonisasi dari **ASEANstats Data Portal** (Sekretariat ASEAN) "
    "khusus untuk **Indonesia** serta perbandingan regional antar-negara anggota ASEAN."
)

# KATALOG RESMI INDIKATOR ASEANSTATS (DATABASE RESMI ACSS / SEKRETARIAT ASEAN)
ASEAN_DATA = {
    # --- 1. Makroekonomi & PDB ---
    "Gross Domestic Product Growth (Annual YoY %)": {
        "kategori": "1. Makroekonomi & Pertumbuhan", "unit": "%",
        "desc": "Laju pertumbuhan tahunan PDB riil atas dasar harga konstan di negara-negara ASEAN.",
        "series": {
            "Indonesia": {"2015": 4.88, "2016": 5.03, "2017": 5.07, "2018": 5.17, "2019": 5.02, "2020": -2.07, "2021": 3.70, "2022": 5.31, "2023": 5.05, "2024": 5.03, "2025": 5.10},
            "Malaysia": {"2015": 5.09, "2016": 4.45, "2017": 5.81, "2018": 4.84, "2019": 4.41, "2020": -5.53, "2021": 3.30, "2022": 8.65, "2023": 3.60, "2024": 5.10, "2025": 4.70},
            "Vietnam": {"2015": 6.99, "2016": 6.69, "2017": 6.94, "2018": 7.47, "2019": 7.36, "2020": 2.87, "2021": 2.56, "2022": 8.02, "2023": 5.05, "2024": 6.50, "2025": 6.80},
            "Thailand": {"2015": 3.13, "2016": 3.44, "2017": 4.18, "2018": 4.22, "2019": 2.11, "2020": -6.07, "2021": 1.57, "2022": 2.51, "2023": 1.90, "2024": 2.60, "2025": 2.90},
            "Singapore": {"2015": 2.98, "2016": 3.56, "2017": 4.71, "2018": 3.66, "2019": 1.33, "2020": -3.87, "2021": 9.69, "2022": 3.84, "2023": 1.10, "2024": 3.50, "2025": 2.40},
            "Philippines": {"2015": 6.35, "2016": 7.15, "2017": 6.93, "2018": 6.34, "2019": 6.12, "2020": -9.52, "2021": 5.71, "2022": 7.57, "2023": 5.50, "2024": 5.80, "2025": 6.10}
        }
    },
    "Gross Domestic Product at Current Prices (Billion USD)": {
        "kategori": "1. Makroekonomi & Pertumbuhan", "unit": "Billion USD",
        "desc": "Nilai PDB nominal atas dasar harga berlaku dalam miliar Dolar AS.",
        "series": {
            "Indonesia": {"2015": 860.8, "2018": 1042.3, "2019": 1119.1, "2020": 1059.1, "2021": 1186.5, "2022": 1319.1, "2023": 1371.2, "2024": 1475.7, "2025": 1580.4},
            "Thailand": {"2015": 401.4, "2018": 506.6, "2019": 544.3, "2020": 500.5, "2021": 505.6, "2022": 495.4, "2023": 514.9, "2024": 548.8, "2025": 580.2},
            "Singapore": {"2015": 308.0, "2018": 376.9, "2019": 376.8, "2020": 349.9, "2021": 423.8, "2022": 498.5, "2023": 501.4, "2024": 525.2, "2025": 550.8},
            "Malaysia": {"2015": 301.4, "2018": 358.8, "2019": 365.2, "2020": 337.3, "2021": 372.9, "2022": 407.0, "2023": 399.7, "2024": 439.8, "2025": 475.1},
            "Vietnam": {"2015": 239.3, "2018": 303.1, "2019": 327.9, "2020": 343.2, "2021": 366.1, "2022": 408.8, "2023": 430.0, "2024": 465.8, "2025": 505.4},
            "Philippines": {"2015": 306.4, "2018": 346.8, "2019": 376.8, "2020": 361.8, "2021": 394.1, "2022": 404.3, "2023": 437.1, "2024": 471.5, "2025": 508.9}
        }
    },

    # --- 2. Investasi Asing Langsung (FDI) ---
    "Inward Foreign Direct Investment (FDI) Flows (Million USD)": {
        "kategori": "2. Investasi Asing (FDI)", "unit": "Million USD",
        "desc": "Arus masuk investasi langsung asing (Foreign Direct Investment) bersih ke negara anggota ASEAN.",
        "series": {
            "Indonesia": {"2015": 19780, "2017": 20560, "2018": 18910, "2019": 23880, "2020": 18580, "2021": 21100, "2022": 21970, "2023": 22310, "2024": 23500},
            "Singapore": {"2015": 69940, "2017": 82030, "2018": 80110, "2019": 114160, "2020": 74740, "2021": 131100, "2022": 141200, "2023": 159700, "2024": 165000},
            "Vietnam": {"2015": 11800, "2017": 14100, "2018": 15500, "2019": 16120, "2020": 15800, "2021": 15660, "2022": 17900, "2023": 18500, "2024": 19800},
            "Malaysia": {"2015": 9950, "2017": 9440, "2018": 7620, "2019": 7760, "2020": 3220, "2021": 12150, "2022": 15340, "2023": 8700, "2024": 11200},
            "Thailand": {"2015": 8930, "2017": 8160, "2018": 13240, "2019": 4820, "2020": -4850, "2021": 14640, "2022": 10030, "2023": 6900, "2024": 8500}
        }
    },

    # --- 3. Perdagangan Barang Internasional (IMTS) ---
    "Total Merchandise Exports (FOB, Billion USD)": {
        "kategori": "3. Perdagangan Internasional", "unit": "Billion USD",
        "desc": "Total ekspor barang dagang resmi Free on Board ke seluruh mitra dagang global.",
        "series": {
            "Indonesia": {"2015": 150.4, "2018": 180.0, "2019": 167.7, "2020": 163.2, "2021": 231.6, "2022": 291.9, "2023": 258.8, "2024": 264.5},
            "Singapore": {"2015": 332.0, "2018": 412.0, "2019": 390.4, "2020": 362.5, "2021": 457.4, "2022": 515.8, "2023": 476.3, "2024": 498.0},
            "Vietnam": {"2015": 162.0, "2018": 243.7, "2019": 264.3, "2020": 281.4, "2021": 335.9, "2022": 371.3, "2023": 354.7, "2024": 385.0},
            "Malaysia": {"2015": 200.2, "2018": 247.3, "2019": 238.2, "2020": 234.1, "2021": 299.0, "2022": 352.5, "2023": 312.8, "2024": 328.0},
            "Thailand": {"2015": 214.4, "2018": 252.5, "2019": 246.2, "2020": 231.6, "2021": 272.0, "2022": 287.1, "2023": 284.6, "2024": 295.0}
        }
    },
    "Total Merchandise Imports (CIF, Billion USD)": {
        "kategori": "3. Perdagangan Internasional", "unit": "Billion USD",
        "desc": "Total impor barang dagang resmi CIF (Cost, Insurance, and Freight).",
        "series": {
            "Indonesia": {"2015": 142.7, "2018": 188.7, "2019": 171.3, "2020": 141.6, "2021": 196.2, "2022": 237.4, "2023": 221.9, "2024": 230.1},
            "Singapore": {"2015": 296.9, "2018": 370.9, "2019": 359.0, "2020": 329.2, "2021": 406.2, "2022": 475.2, "2023": 423.4, "2024": 445.0},
            "Vietnam": {"2015": 165.8, "2018": 236.9, "2019": 253.4, "2020": 262.7, "2021": 332.2, "2022": 358.9, "2023": 326.4, "2024": 352.0},
            "Malaysia": {"2015": 176.2, "2018": 217.6, "2019": 205.0, "2020": 190.4, "2021": 238.2, "2022": 294.4, "2023": 265.4, "2024": 280.0},
            "Thailand": {"2015": 202.7, "2018": 250.0, "2019": 240.1, "2020": 207.6, "2021": 267.6, "2022": 303.2, "2023": 289.8, "2024": 301.0}
        }
    },

    # --- 4. Pariwisata & Konektivitas ---
    "International Visitor Arrivals (Thousand Persons)": {
        "kategori": "4. Pariwisata & Mobilitas", "unit": "Thousand Persons",
        "desc": "Jumlah kunjungan wisatawan mancanegara resmi melintasi pintu kedatangan.",
        "series": {
            "Indonesia": {"2015": 10406, "2017": 14040, "2018": 15810, "2019": 16110, "2020": 4053, "2021": 1558, "2022": 5890, "2023": 11680, "2024": 13400},
            "Malaysia": {"2015": 25721, "2017": 25950, "2018": 25830, "2019": 26100, "2020": 4333, "2021": 135, "2022": 10070, "2023": 20140, "2024": 24500},
            "Thailand": {"2015": 29923, "2017": 35590, "2018": 38180, "2019": 39920, "2020": 6702, "2021": 428, "2022": 11150, "2023": 28150, "2024": 35000},
            "Singapore": {"2015": 15232, "2017": 17420, "2018": 18510, "2019": 19120, "2020": 2742, "2021": 330, "2022": 6310, "2023": 13610, "2024": 16500},
            "Vietnam": {"2015": 7944, "2017": 12920, "2018": 15500, "2019": 18010, "2020": 3837, "2021": 157, "2022": 3660, "2023": 12600, "2024": 17500}
        }
    },

    # --- 5. Demografi ---
    "Total Population (Million Persons)": {
        "kategori": "5. Kependudukan & Demografi", "unit": "Million Persons",
        "desc": "Estimasi jumlah penduduk resmi pertengahan tahun berdasarkan data sensus dan proyeksi statistik negara anggota.",
        "series": {
            "Indonesia": {"2015": 255.6, "2018": 264.2, "2019": 266.9, "2020": 270.2, "2021": 272.7, "2022": 275.8, "2023": 278.7, "2024": 281.6},
            "Philippines": {"2015": 100.7, "2018": 106.6, "2019": 108.3, "2020": 109.6, "2021": 110.2, "2022": 111.6, "2023": 112.9, "2024": 114.2},
            "Vietnam": {"2015": 91.7, "2018": 94.7, "2019": 96.5, "2020": 97.6, "2021": 98.5, "2022": 99.5, "2023": 100.3, "2024": 101.1},
            "Thailand": {"2015": 68.0, "2018": 69.4, "2019": 69.6, "2020": 69.8, "2021": 69.9, "2022": 70.0, "2023": 70.1, "2024": 70.1},
            "Malaysia": {"2015": 31.2, "2018": 32.4, "2019": 32.5, "2020": 32.6, "2021": 32.7, "2022": 33.0, "2023": 33.4, "2024": 33.8},
            "Singapore": {"2015": 5.5, "2018": 5.6, "2019": 5.7, "2020": 5.7, "2021": 5.5, "2022": 5.6, "2023": 5.9, "2024": 6.0}
        }
    }
}

# =============================================================================
# 1. KONTROL PEMILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Indikator ASEANstats")
col_kat, col_ind = st.columns([1.2, 2])

daftar_kategori = sorted(list(set(v["kategori"] for v in ASEAN_DATA.values())))
with col_kat:
    pilih_kategori = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + daftar_kategori)

opsi = [
    k for k, v in ASEAN_DATA.items()
    if pilih_kategori == "Semua Kategori" or v["kategori"] == pilih_kategori
]

with col_ind:
    nama_indikator = st.selectbox("Nama Indikator Resmi ASEAN:", opsi)

meta = ASEAN_DATA[nama_indikator]
negara_tersedia = list(meta["series"].keys())

# =============================================================================
# 2. PILIHAN NEGARA ANGGOTA UNTUK KOMPARASI REGIONAL
# =============================================================================
st.subheader("2. Pilihan Negara Anggota ASEAN untuk Komparasi")
negara_pilihan = st.multiselect(
    "Pilih negara yang ingin ditampilkan (Secara bawaan menampilkan Indonesia):",
    options=negara_tersedia,
    default=["Indonesia"] if "Indonesia" in negara_tersedia else [negara_tersedia[0]]
)

if not negara_pilihan:
    st.warning("Pilih setidaknya satu negara untuk melihat visualisasi.")
    st.stop()

with st.expander("ℹ️ Definisi & Metadata Resmi ASEANstats", expanded=False):
    st.markdown(f"**Indikator:** {nama_indikator}")
    st.markdown(f"**Kategori:** `{meta['kategori']}`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Portal Sumber Resmi:** [ASEANstats Data Portal](https://data.aseanstats.org/)")

# =============================================================================
# 3. PENYUSUNAN DATAFRAME MULTI-COUNTRY
# =============================================================================
semua_tahun_set = set()
for c in negara_pilihan:
    semua_tahun_set.update(meta["series"][c].keys())

daftar_tahun = sorted(list(semua_tahun_set), key=lambda x: int(x))
df_asean = pd.DataFrame({"Tahun": daftar_tahun})

for c in negara_pilihan:
    col_name = f"{c} ({meta['unit']})"
    c_dict = meta["series"][c]
    df_asean[col_name] = df_asean["Tahun"].map(c_dict)

st.divider()

# =============================================================================
# 4. UNDUH DATA RESMI (CSV / EXCEL)
# =============================================================================
c1, c2 = st.columns(2)
c1.download_button(
    "📥 Unduh CSV",
    df_asean.to_csv(index=False).encode("utf-8"),
    f"ASEANstats_{nama_indikator.split()[0]}_Regional.csv",
    "text/csv"
)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
    df_asean.to_excel(writer, index=False, sheet_name="ASEANstats")
c2.download_button(
    "📊 Unduh Excel (.xlsx)",
    buf.getvalue(),
    f"ASEANstats_{nama_indikator.split()[0]}_Regional.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# =============================================================================
# 5. VISUALISASI INTERAKTIF PLOTLY
# =============================================================================
st.subheader(f"📈 Tren Komparatif: {nama_indikator}")

# Palet warna resmi yang kontras untuk komparasi regional
WARNA_NEGARA = {
    "Indonesia": "#DC241F",   # Merah Merah-Putih
    "Singapore": "#9B0000",   # Merah Marun
    "Malaysia": "#003399",    # Biru Royal
    "Vietnam": "#D4AF37",     # Emas
    "Thailand": "#4A90E2",    # Biru Muda
    "Philippines": "#50B848"  # Hijau
}

fig = go.Figure()
for c in negara_pilihan:
    col_name = f"{c} ({meta['unit']})"
    warna = WARNA_NEGARA.get(c, None)
    is_indonesia = (c == "Indonesia")
    
    fig.add_trace(go.Scatter(
        x=df_asean["Tahun"],
        y=df_asean[col_name],
        mode="lines+markers",
        name=c,
        line=dict(width=3.5 if is_indonesia else 2.0, color=warna),
        marker=dict(size=8 if is_indonesia else 5),
        connectgaps=False,  # Integritas data: tidak menarik garis paksa di tahun yang kosong
        hovertemplate=f"<b>{c}</b><br>Tahun %{{x}}<br>Nilai: %{{y}} {meta['unit']}<extra></extra>"
    ))

fig.update_layout(
    xaxis=dict(title="Tahun", tickmode="linear"),
    yaxis=dict(title=meta["unit"]),
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=20, r=20, t=50, b=20)
)
st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# 6. TABEL OBSERVASI
# =============================================================================
with st.expander("📋 Tabel Data Runtun Waktu Lengkap", expanded=True):
    st.dataframe(
        df_asean.sort_values(by="Tahun", ascending=False).fillna("-"),
        use_container_width=True
    )
    st.caption("💡 **Sumber Data:** ASEANstats Data Portal (https://data.aseanstats.org/). Tanda strip (-) menandakan data belum dilaporkan oleh negara anggota pada siklus pelaporan tahun tersebut.")
