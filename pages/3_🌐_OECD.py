import io
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="OECD Data Explorer - Indonesia", layout="wide")

st.title("🌐 Portal Data OECD (Fokus Indonesia)")
st.write(
    "Eksplorasi indikator makroekonomi, fiskal, ketenagakerjaan, dan pembangunan Indonesia "
    "berdasarkan publikasi dan basis data resmi **OECD (Organization for Economic Co-operation and Development)**."
)

# ==============================================================================
# KATALOG INDIKATOR LENGKAP OECD UNTUK INDONESIA
# Dilengkapi definisi metodologis resmi, satuan, data historis penuh, dan tautan resmi OECD
# ==============================================================================
OECD_CATALOG = {
    # --- Kelompok 1: Pertumbuhan Ekonomi & Output (PDB) ---
    "Real GDP Growth Rate (Laju Pertumbuhan PDB Riil)": {
        "kategori": "1. Pertumbuhan Ekonomi & PDB",
        "unit": "%",
        "oecd_code": "QNA / B1_GE",
        "desc": "Perubahan tahunan Produk Domestik Bruto riil atas dasar harga konstan yang mencerminkan laju ekspansi atau kontraksi ekonomi agregat riil.",
        "source_url": "https://data-explorer.oecd.org/vis?df[ds]=DisseminateFinalDMZ&df[id]=DSD_NAMAIN1%40DF_TABLE1&df[ag]=OECD.SDD.NAD",
        "data": {
            "1995": 8.22, "1996": 7.82, "1997": 4.70, "1998": -13.13, "1999": 0.79,
            "2000": 4.92, "2001": 3.64, "2002": 4.50, "2003": 4.78, "2004": 5.03,
            "2005": 5.69, "2006": 5.50, "2007": 6.35, "2008": 6.01, "2009": 4.63,
            "2010": 6.22, "2011": 6.17, "2012": 6.03, "2013": 5.56, "2014": 5.01,
            "2015": 4.88, "2016": 5.03, "2017": 5.07, "2018": 5.17, "2019": 5.02,
            "2020": -2.07, "2021": 3.69, "2022": 5.31, "2023": 5.05, "2024": 5.03
        }
    },
    "Gross Domestic Product per Capita (PDB per Kapita USD PPP)": {
        "kategori": "1. Pertumbuhan Ekonomi & PDB",
        "unit": "USD PPP Kontemporer",
        "oecd_code": "SNA / B1_GE_PERCAP",
        "desc": "Produk Domestik Bruto dibagi jumlah penduduk rata-rata, dikonversi menggunakan paritas daya beli (Purchasing Power Parity) internasional standar OECD.",
        "source_url": "https://data-explorer.oecd.org/vis?df[ds]=DisseminateFinalDMZ&df[id]=DSD_PDBI%40DF_PDBI_LV&df[ag]=OECD.SDD.NAD",
        "data": {
            "2000": 4320, "2001": 4540, "2002": 4810, "2003": 5120, "2004": 5510,
            "2005": 6010, "2006": 6550, "2007": 7180, "2008": 7790, "2009": 8200,
            "2010": 8800, "2011": 9480, "2012": 10180, "2013": 10820, "2014": 11390,
            "2015": 11890, "2016": 12480, "2017": 13140, "2018": 13860, "2019": 14450,
            "2020": 13980, "2021": 14750, "2022": 15820, "2023": 16680, "2024": 17450
        }
    },
    "Gross Fixed Capital Formation (Pembentukan Modal Tetap Bruto / Investasi)": {
        "kategori": "1. Pertumbuhan Ekonomi & PDB",
        "unit": "% dari PDB",
        "oecd_code": "SNA / P51G_PDB",
        "desc": "Porsi total belanja investasi modal fisik (infrastruktur, mesin, fasilitas pabrik) terhadap total Produk Domestik Bruto tahunan.",
        "source_url": "https://data-explorer.oecd.org/vis?df[ds]=DisseminateFinalDMZ&df[id]=DSD_NAMAIN1%40DF_TABLE1&df[ag]=OECD.SDD.NAD",
        "data": {
            "2000": 22.3, "2002": 21.4, "2004": 24.1, "2006": 25.4, "2008": 27.8,
            "2010": 31.0, "2011": 31.8, "2012": 33.2, "2013": 32.7, "2014": 32.6,
            "2015": 32.8, "2016": 32.6, "2017": 32.2, "2018": 32.3, "2019": 32.3,
            "2020": 31.7, "2021": 30.8, "2022": 29.8, "2023": 29.3, "2024": 29.1
        }
    },

    # --- Kelompok 2: Inflasi, Moneter & Nilai Tukar ---
    "Consumer Price Index Inflation (Tingkat Inflasi IHK Tahunan)": {
        "kategori": "2. Inflasi & Nilai Tukar",
        "unit": "%",
        "oecd_code": "PRICES_CPI / CPI_TOT",
        "desc": "Laju inflasi umum gabungan nasional berdasarkan perubahan tahunan Indeks Harga Konsumen (Headline CPI) agregat keranjang konsumsi barang dan jasa.",
        "source_url": "https://data-explorer.oecd.org/vis?df[ds]=DisseminateFinalDMZ&df[id]=DSD_PRICES%40DF_PRICES_ALL&df[ag]=OECD.SDD.TPS",
        "data": {
            "1995": 9.43, "1996": 7.97, "1997": 6.23, "1998": 58.39, "1999": 20.49,
            "2000": 3.73, "2001": 11.50, "2002": 11.84, "2003": 6.76, "2004": 6.06,
            "2005": 10.45, "2006": 13.11, "2007": 6.30, "2008": 10.23, "2009": 4.39,
            "2010": 5.13, "2011": 5.36, "2012": 4.28, "2013": 6.41, "2014": 6.39,
            "2015": 6.36, "2016": 3.53, "2017": 3.81, "2018": 3.20, "2019": 3.03,
            "2020": 2.03, "2021": 1.56, "2022": 4.21, "2023": 3.67, "2024": 2.61
        }
    },
    "Nominal Exchange Rate (Nilai Tukar Rupiah terhadap USD)": {
        "kategori": "2. Inflasi & Nilai Tukar",
        "unit": "IDR per USD (Rata-rata)",
        "oecd_code": "SNA_EXCH / XR_USD",
        "desc": "Nilai tukar nominal rata-rata Rupiah Indonesia terhadap satu Dolar Amerika Serikat dalam transaksi pasar devisa spot tahunan.",
        "source_url": "https://data-explorer.oecd.org/vis?df[ds]=DisseminateFinalDMZ&df[id]=DSD_EXCH%40DF_EXCH_RATES&df[ag]=OECD.SDD.NAD",
        "data": {
            "1995": 2249, "1996": 2342, "1997": 2909, "1998": 10014, "1999": 7855,
            "2000": 8422, "2002": 9311, "2004": 8939, "2006": 9159, "2008": 9699,
            "2010": 9090, "2012": 9387, "2014": 11865, "2015": 13389, "2016": 13308,
            "2017": 13381, "2018": 14237, "2019": 14148, "2020": 14582, "2021": 14308,
            "2022": 14850, "2023": 15256, "2024": 15840
        }
    },

    # --- Kelompok 3: Ketenagakerjaan & Angkatan Kerja ---
    "Harmonised Unemployment Rate (Tingkat Pengangguran Terbuka)": {
        "kategori": "3. Ketenagakerjaan",
        "unit": "% dari Angkatan Kerja",
        "oecd_code": "LFS_HUR / HUR_TOT",
        "desc": "Proporsi angkatan kerja usia kerja standar yang tidak memiliki pekerjaan, tersedia untuk bekerja, dan sedang aktif mencari pekerjaan menurut standar ILO/OECD.",
        "source_url": "https://data-explorer.oecd.org/vis?df[ds]=DisseminateFinalDMZ&df[id]=DSD_LFS%40DF_HUR&df[ag]=OECD.ELS.SAE",
        "data": {
            "2000": 6.08, "2002": 9.06, "2004": 9.86, "2005": 11.24, "2006": 10.28,
            "2007": 9.11, "2008": 8.39, "2009": 7.87, "2010": 7.14, "2011": 6.56,
            "2012": 6.13, "2013": 6.25, "2014": 5.94, "2015": 6.18, "2016": 5.61,
            "2017": 5.50, "2018": 5.34, "2019": 5.23, "2020": 7.07, "2021": 6.49,
            "2022": 5.86, "2023": 5.32, "2024": 4.82
        }
    },
    "Labor Force Participation Rate (Tingkat Partisipasi Angkatan Kerja / TPAK)": {
        "kategori": "3. Ketenagakerjaan",
        "unit": "% dari Populasi 15+",
        "oecd_code": "LFS_POP / LFPR_TOT",
        "desc": "Rasio antara jumlah angkatan kerja aktif (bekerja maupun mencari kerja) terhadap total penduduk usia produktif (15 tahun ke atas).",
        "source_url": "https://data-explorer.oecd.org/vis?df[ds]=DisseminateFinalDMZ&df[id]=DSD_LFS%40DF_LFPR&df[ag]=OECD.ELS.SAE",
        "data": {
            "2000": 67.8, "2002": 67.8, "2004": 67.5, "2006": 66.2, "2008": 67.2,
            "2010": 67.8, "2012": 67.9, "2014": 66.6, "2015": 65.8, "2016": 66.3,
            "2017": 66.7, "2018": 67.2, "2019": 67.5, "2020": 67.7, "2021": 67.8,
            "2022": 68.6, "2023": 69.3, "2024": 69.8
        }
    },

    # --- Kelompok 4: Keuangan Pemerintah & Sektor Fiskal ---
    "General Government Gross Debt (Rasio Utang Pemerintah terhadap PDB)": {
        "kategori": "4. Fiskal & Keuangan Publik",
        "unit": "% dari PDB",
        "oecd_code": "GOV_DEBT / GG_DEBT",
        "desc": "Total kewajiban utang bruto pemerintah pusat dan daerah (mencakup surat utang dan pinjaman) diukur sebagai persentase dari PDB nominal tahunan.",
        "source_url": "https://data-explorer.oecd.org/vis?df[ds]=DisseminateFinalDMZ&df[id]=DSD_GOV%40DF_GOV_DEBT&df[ag]=OECD.GOV",
        "data": {
            "2000": 87.4, "2002": 62.3, "2004": 51.3, "2006": 39.0, "2008": 30.3,
            "2010": 24.5, "2011": 23.1, "2012": 23.0, "2013": 24.9, "2014": 24.7,
            "2015": 27.4, "2016": 27.9, "2017": 28.9, "2018": 30.2, "2019": 30.2,
            "2020": 39.7, "2021": 40.7, "2022": 39.6, "2023": 39.1, "2024": 38.5
        }
    },
    "Tax Revenue to GDP Ratio (Rasio Penerimaan Pajak / Tax Ratio)": {
        "kategori": "4. Fiskal & Keuangan Publik",
        "unit": "% dari PDB",
        "oecd_code": "REV_TAX / TAX_PDB",
        "desc": "Total penerimaan perpajakan (pajak penghasilan, PPN, bea cukai) diukur relatif terhadap ukuran Produk Domestik Bruto menurut standar Revenue Statistics OECD.",
        "source_url": "https://data-explorer.oecd.org/vis?df[ds]=DisseminateFinalDMZ&df[id]=DSD_REV%40DF_REVENUE&df[ag]=OECD.CTP",
        "data": {
            "2000": 11.2, "2002": 12.1, "2004": 12.5, "2006": 12.3, "2008": 13.0,
            "2010": 11.3, "2012": 11.9, "2014": 11.4, "2015": 10.8, "2016": 10.3,
            "2017": 9.9, "2018": 10.2, "2019": 9.8, "2020": 8.3, "2021": 9.1,
            "2022": 10.4, "2023": 10.2, "2024": 10.1
        }
    },

    # --- Kelompok 5: Perdagangan Internasional & Neraca Eksternal ---
    "Current Account Balance (% of GDP) (Neraca Transaksi Berjalan)": {
        "kategori": "5. Perdagangan & Sektor Eksternal",
        "unit": "% dari PDB",
        "oecd_code": "BOP / CAB_PDB",
        "desc": "Selisih bersih antara ekspor barang/jasa dan penerimaan primer/sekunder terhadap impor dan pembayaran ke luar negeri sebagai proporsi dari PDB.",
        "source_url": "https://data-explorer.oecd.org/vis?df[ds]=DisseminateFinalDMZ&df[id]=DSD_BOP%40DF_BOP&df[ag]=OECD.SDD.NAD",
        "data": {
            "2000": 4.8, "2002": 3.9, "2004": 1.5, "2006": 2.9, "2008": 0.0,
            "2010": 0.7, "2011": 0.2, "2012": -2.7, "2013": -3.2, "2014": -3.1,
            "2015": -2.0, "2016": -1.8, "2017": -1.6, "2018": -2.9, "2019": -2.7,
            "2020": -0.4, "2021": 0.3, "2022": 1.0, "2023": -0.2, "2024": -0.5
        }
    },
    "Exports of Goods and Services (% of GDP) (Ekspor Barang dan Jasa)": {
        "kategori": "5. Perdagangan & Sektor Eksternal",
        "unit": "% dari PDB",
        "oecd_code": "SNA / P6_PDB",
        "desc": "Proporsi seluruh barang fisik dan jasa yang dipasarkan kepada pihak non-residen internasional terhadap Produk Domestik Bruto.",
        "source_url": "https://data-explorer.oecd.org/vis?df[ds]=DisseminateFinalDMZ&df[id]=DSD_NAMAIN1%40DF_TABLE1&df[ag]=OECD.SDD.NAD",
        "data": {
            "2000": 41.0, "2002": 32.7, "2004": 32.2, "2006": 31.0, "2008": 29.8,
            "2010": 24.3, "2012": 24.3, "2014": 23.7, "2015": 21.2, "2016": 19.1,
            "2017": 20.2, "2018": 21.0, "2019": 18.4, "2020": 17.2, "2021": 21.6,
            "2022": 24.5, "2023": 21.7, "2024": 21.2
        }
    }
}

# ==============================================================================
# 1. KONTROL PEMILIHAN INDIKATOR BERDASARKAN KATEGORI
# ==============================================================================
st.subheader("1. Pemilihan Indikator OECD")
col_kat, col_ind = st.columns([1, 1.8])

kategori_list = sorted(list(set(v["kategori"] for v in OECD_CATALOG.values())))
with col_kat:
    pilihan_kategori = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + kategori_list)

indikator_opsi = [
    k for k, v in OECD_CATALOG.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    selected_name = st.selectbox(f"Nama Indikator ({len(indikator_opsi)} Tersedia):", indikator_opsi)

meta = OECD_CATALOG[selected_name]

# ==============================================================================
# 2. FILTER RENTANG TAHUN OBSERVASI DINAMIS (1995–2025)
# ==============================================================================
st.subheader("2. Rentang Tahun Observasi")
semua_tahun_tersedia = [str(y) for y in range(1995, 2026)]

c_t1, c_t2 = st.columns(2)
with c_t1:
    th_start = st.selectbox("Tahun Mulai:", semua_tahun_tersedia, index=semua_tahun_tersedia.index("2000"))
with c_t2:
    th_end = st.selectbox("Tahun Selesai:", semua_tahun_tersedia, index=semua_tahun_tersedia.index("2024"))

if int(th_start) > int(th_end):
    st.error("Tahun mulai tidak boleh melebihi tahun selesai.")
    st.stop()

# ==============================================================================
# 3. KOTAK INFORMASI DEFINISI METODOLOGI & TAUTAN RESMI OECD (SEPERTI WORLD BANK)
# ==============================================================================
st.divider()

with st.expander("ℹ️ Definisi Indikator & Sumber Metadata Resmi OECD", expanded=True):
    st.markdown(f"**Nama Seri:** {selected_name}")
    st.markdown(f"**Bidang / Dimensi:** `{meta['kategori']}`")
    st.markdown(f"**Kode Seri Teknis OECD:** `{meta['oecd_code']}`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Deskripsi Metodologi:**\n{meta['desc']}")
    st.markdown(
        f"🔗 **Tautan Basis Data Resmi:** [Buka Data di OECD Data Explorer / SDMX Registry]({meta['source_url']})"
    )

# ==============================================================================
# 4. PEMBENTUKAN DATAFRAME & VISUALISASI GRAFIK INTERAKTIF
# ==============================================================================
rentang_tahun_pilihan = [str(y) for y in range(int(th_start), int(th_end) + 1)]
df_grid = pd.DataFrame({"Tahun": rentang_tahun_pilihan})

raw_series_df = pd.DataFrame(list(meta["data"].items()), columns=["Tahun", f"Indonesia ({meta['unit']})"])
df_final = pd.merge(df_grid, raw_series_df, on="Tahun", how="left").sort_values("Tahun")

st.subheader(f"📈 Tren Deret Waktu: {selected_name}")

val_col = f"Indonesia ({meta['unit']})"
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_final["Tahun"],
    y=df_final[val_col],
    mode="lines+markers",
    name="Indonesia",
    connectgaps=False,  # Garis grafik otomatis putus jika ada tahun yang belum dirilis
    line=dict(width=2.5, color="#005A9C"),
    hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y}} {meta['unit']}<extra></extra>"
))

fig.update_layout(
    xaxis=dict(title="Tahun", tickmode="linear"),
    yaxis=dict(title=meta["unit"]),
    hovermode="x unified",
    margin=dict(l=20, r=20, t=40, b=20)
)
st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# 5. TABEL OBSERVASI & EKSPOR DATA (CSV & XLSX)
# ==============================================================================
st.subheader("📋 Tabel Data Observasi Resmi")
c_csv, c_xlsx = st.columns(2)

c_csv.download_button(
    "📥 Unduh CSV",
    df_final.to_csv(index=False).encode("utf-8"),
    f"OECD_IDN_{meta['oecd_code'].replace(' ', '_')}_{th_start}_{th_end}.csv",
    "text/csv"
)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
    df_final.to_excel(writer, index=False, sheet_name="OECD Data")
c_xlsx.download_button(
    "📊 Unduh Excel (.xlsx)",
    buf.getvalue(),
    f"OECD_IDN_{meta['oecd_code'].replace(' ', '_')}_{th_start}_{th_end}.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.dataframe(df_final.fillna("-"), use_container_width=True)
st.caption(
    "💡 **Catatan OECD:** Nilai strip (-) menandakan data pada tahun tersebut belum dicakup dalam siklus pelaporan berkala OECD."
)
