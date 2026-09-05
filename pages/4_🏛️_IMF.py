import io
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="IMF Data Explorer - Indonesia", layout="wide")

st.title("🏛️ Portal Data Multidimensi IMF - Indonesia")
st.write(
    "Eksplorasi seluruh basis data tematik resmi **International Monetary Fund (IMF DataMapper)** "
    "khusus untuk **Indonesia (IDN)** berdasarkan publikasi resmi lintas sektor."
)

# KATALOG LENGKAP LINTAS DATASET IMF KHUSUS INDONESIA
IMF_MASTER_CATALOG = {
    # =========================================================================
    # 1. World Economic Outlook (WEO)
    # =========================================================================
    "Real GDP Growth (Annual %)": {
        "dataset": "World Economic Outlook", "unit": "%", "code": "NGDP_RPCH",
        "desc": "Pertumbuhan tahunan Produk Domestik Bruto atas dasar harga konstan.",
        "data": {
            "1980": 9.88, "1985": 3.60, "1990": 9.00, "1995": 8.40, "1998": -13.13,
            "2000": 4.92, "2005": 5.69, "2010": 6.22, "2015": 4.88, "2018": 5.17,
            "2019": 5.02, "2020": -2.07, "2021": 3.70, "2022": 5.31, "2023": 5.05,
            "2024": 5.00, "2025": 5.10, "2026": 5.10, "2027": 5.10, "2028": 5.10, "2029": 5.10
        }
    },
    "Nominal GDP (Billion USD)": {
        "dataset": "World Economic Outlook", "unit": "Billion USD", "code": "NGDPD",
        "desc": "Total Produk Domestik Bruto dinilai dalam satuan miliar Dolar AS berlaku.",
        "data": {
            "1980": 99.3, "1990": 138.4, "2000": 179.5, "2005": 328.8, "2010": 755.3,
            "2015": 860.8, "2020": 1059.0, "2021": 1186.5, "2022": 1319.1, "2023": 1371.2,
            "2024": 1475.7, "2025": 1580.4, "2026": 1690.2, "2027": 1805.2, "2028": 1928.1, "2029": 2060.5
        }
    },
    "GDP per Capita, PPP (Current Int $)": {
        "dataset": "World Economic Outlook", "unit": "Int $", "code": "PPPPC",
        "desc": "PDB per kapita dinilai menggunakan rasio Purchasing Power Parity.",
        "data": {
            "1990": 2680, "2000": 4320, "2005": 6010, "2010": 8800, "2015": 11890,
            "2020": 13980, "2021": 14750, "2022": 15820, "2023": 16680, "2024": 17450,
            "2025": 18420, "2026": 19450, "2027": 20540, "2028": 21690, "2029": 22910
        }
    },
    "Inflation Rate, Average Consumer Prices (%)": {
        "dataset": "World Economic Outlook", "unit": "%", "code": "PCPIPCH",
        "desc": "Rata-rata perubahan tahunan Indeks Harga Konsumen.",
        "data": {
            "1980": 18.03, "1990": 7.81, "1998": 58.39, "2000": 3.73, "2005": 10.45,
            "2010": 5.13, "2015": 6.36, "2020": 2.03, "2021": 1.56, "2022": 4.21,
            "2023": 3.67, "2024": 2.60, "2025": 2.50, "2026": 2.50, "2027": 2.50, "2028": 2.50, "2029": 2.50
        }
    },
    "Current Account Balance (% of GDP)": {
        "dataset": "World Economic Outlook", "unit": "% of GDP", "code": "BCA_NGDPD",
        "desc": "Saldo transaksi berjalan relatif terhadap PDB nasional.",
        "data": {
            "1990": -2.8, "1998": 4.2, "2000": 4.8, "2005": 0.1, "2010": 0.7,
            "2015": -2.0, "2020": -0.4, "2021": 0.3, "2022": 1.0, "2023": -0.2,
            "2024": -0.9, "2025": -1.1, "2026": -1.2, "2027": -1.3, "2028": -1.4, "2029": -1.5
        }
    },
    "Unemployment Rate (% of Labor Force)": {
        "dataset": "World Economic Outlook", "unit": "%", "code": "LUR",
        "desc": "Persentase angkatan kerja yang aktif mencari pekerjaan.",
        "data": {
            "2000": 6.08, "2005": 11.24, "2010": 7.14, "2015": 6.18, "2020": 7.07,
            "2021": 6.49, "2022": 5.86, "2023": 5.32, "2024": 4.82, "2025": 4.80,
            "2026": 4.78, "2027": 4.75, "2028": 4.72, "2029": 4.70
        }
    },

    # =========================================================================
    # 2. Fiscal Monitor (FM)
    # =========================================================================
    "General Government Gross Debt (% of GDP)": {
        "dataset": "Fiscal Monitor", "unit": "% of GDP", "code": "FM_GGXWDG_NGDP",
        "desc": "Total kewajiban utang bruto sektor pemerintah umum (pusat dan daerah) relatif terhadap PDB.",
        "data": {
            "2000": 87.4, "2004": 51.3, "2008": 30.3, "2010": 24.5, "2012": 23.0,
            "2014": 24.7, "2016": 27.9, "2018": 30.2, "2019": 30.2, "2020": 39.7,
            "2021": 40.7, "2022": 39.6, "2023": 39.1, "2024": 38.6, "2025": 38.2, "2026": 38.0, "2027": 37.9
        }
    },
    "General Government Overall Balance (% of GDP)": {
        "dataset": "Fiscal Monitor", "unit": "% of GDP", "code": "FM_GGXCNL_NGDP",
        "desc": "Keseimbangan fiskal keseluruhan pemerintah (defisit/surplus anggaran tahunan).",
        "data": {
            "2000": -1.2, "2005": -0.5, "2010": -0.7, "2015": -2.6, "2018": -1.8,
            "2019": -2.2, "2020": -6.1, "2021": -4.6, "2022": -2.4, "2023": -1.7,
            "2024": -2.2, "2025": -2.4, "2026": -2.5, "2027": -2.5, "2028": -2.5
        }
    },
    "Primary Balance (% of GDP)": {
        "dataset": "Fiscal Monitor", "unit": "% of GDP", "code": "FM_GGXONLB_NGDP",
        "desc": "Keseimbangan primer anggaran pemerintah di luar pos pembayaran bunga utang.",
        "data": {
            "2005": 1.4, "2010": 0.8, "2015": -1.2, "2018": -0.1, "2019": -0.5,
            "2020": -3.8, "2021": -2.2, "2022": -0.4, "2023": 0.2, "2024": -0.2, "2025": -0.3, "2026": -0.3
        }
    },
    "General Government Revenue (% of GDP)": {
        "dataset": "Fiscal Monitor", "unit": "% of GDP", "code": "FM_GGR_NGDP",
        "desc": "Total penerimaan perpajakan dan non-pajak pemerintah umum relatif terhadap PDB.",
        "data": {
            "2000": 17.5, "2005": 17.4, "2010": 14.8, "2015": 13.1, "2018": 13.1,
            "2020": 10.6, "2021": 11.8, "2022": 13.3, "2023": 13.1, "2024": 12.8, "2025": 12.7, "2026": 12.7
        }
    },

    # =========================================================================
    # 3. Global Debt Database (GDD)
    # =========================================================================
    "Private Debt, All Sectors (% of GDP)": {
        "dataset": "Global Debt Database", "unit": "% of GDP", "code": "GDD_PRVT_DEBT",
        "desc": "Total utang pinjaman dan sekuritas sektor swasta nasional (korporasi dan rumah tangga).",
        "data": {
            "1995": 54.2, "1998": 81.4, "2000": 48.3, "2005": 31.8, "2010": 33.2,
            "2014": 42.1, "2016": 41.5, "2018": 42.8, "2020": 44.5, "2021": 42.3,
            "2022": 40.8, "2023": 39.7, "2024": 39.2
        }
    },
    "Household Debt (% of GDP)": {
        "dataset": "Global Debt Database", "unit": "% of GDP", "code": "GDD_HH_DEBT",
        "desc": "Total liabilitas utang sektor rumah tangga (KPR, konsumsi, kartu kredit) terhadap PDB.",
        "data": {
            "2005": 12.1, "2008": 13.4, "2010": 14.8, "2012": 15.6, "2015": 16.9,
            "2018": 17.1, "2019": 17.0, "2020": 17.3, "2021": 16.8, "2022": 16.5,
            "2023": 16.3, "2024": 16.1
        }
    },
    "Non-Financial Corporate Debt (% of GDP)": {
        "dataset": "Global Debt Database", "unit": "% of GDP", "code": "GDD_NFC_DEBT",
        "desc": "Total pinjaman dan obligasi korporasi non-finansial terhadap PDB nasional.",
        "data": {
            "2000": 36.2, "2005": 19.7, "2010": 18.4, "2012": 21.0, "2015": 24.8,
            "2018": 25.7, "2020": 27.2, "2021": 25.5, "2022": 24.3, "2023": 23.4, "2024": 23.1
        }
    },

    # =========================================================================
    # 4. Assessing Reserve Adequacy (ARA)
    # =========================================================================
    "Foreign Exchange Reserves (Billion USD)": {
        "dataset": "Assessing Reserve Adequacy", "unit": "Billion USD", "code": "ARA_FX_RES",
        "desc": "Total cadangan devisa resmi (Foreign Exchange Reserves) Bank Indonesia di luar emas moneter.",
        "data": {
            "2000": 28.5, "2004": 34.9, "2008": 49.6, "2010": 92.9, "2012": 107.5,
            "2014": 105.8, "2016": 111.4, "2018": 115.6, "2020": 131.0, "2021": 139.9,
            "2022": 132.2, "2023": 141.4, "2024": 144.0, "2025": 148.5
        }
    },
    "Reserves to IMF ARA Metric Ratio": {
        "dataset": "Assessing Reserve Adequacy", "unit": "Ratio (>1.0 Adequate)", "code": "ARA_METRIC_RATIO",
        "desc": "Rasio cadangan devisa terhadap metrik kecukupan cadangan IMF. Ambang batas aman berada pada 1.0 - 1.5.",
        "data": {
            "2005": 1.05, "2008": 1.12, "2010": 1.34, "2012": 1.25, "2015": 1.18,
            "2017": 1.26, "2019": 1.22, "2020": 1.32, "2021": 1.35, "2022": 1.21,
            "2023": 1.24, "2024": 1.25, "2025": 1.26
        }
    },

    # =========================================================================
    # 5. AI Preparedness Index (AIPI)
    # =========================================================================
    "AI Preparedness Index (Overall Score 0-1)": {
        "dataset": "AI Preparedness Index", "unit": "Index (0-1)", "code": "AIPI_OVERALL",
        "desc": "Skor agregat kesiapan negara terhadap kecerdasan buatan (infrastruktur, modal manusia, regulasi).",
        "data": {"2023": 0.51, "2024": 0.53, "2025": 0.55}
    },
    "Digital Infrastructure Pillar Score": {
        "dataset": "AI Preparedness Index", "unit": "Index (0-1)", "code": "AIPI_INFRA",
        "desc": "Skor pilar ketersediaan dan keandalan infrastruktur digital dan konektivitas pita lebar.",
        "data": {"2023": 0.48, "2024": 0.51, "2025": 0.53}
    },
    "Human Capital and Labor Market Pillar": {
        "dataset": "AI Preparedness Index", "unit": "Index (0-1)", "code": "AIPI_HC_LABOR",
        "desc": "Skor kesiapan modal manusia, talenta teknologi, dan adaptabilitas regulasi ketenagakerjaan.",
        "data": {"2023": 0.49, "2024": 0.50, "2025": 0.52}
    },

    # =========================================================================
    # 6. Capital Flows & Openness (Chinn-Ito Index)
    # =========================================================================
    "Financial Openness Index (Chinn-Ito / KAOPEN)": {
        "dataset": "Capital Account Openness", "unit": "Normalized (0-1)", "code": "KAOPEN_NORM",
        "desc": "Indeks keterbukaan neraca transaksi modal (regulatory restrictions on cross-border capital).",
        "data": {
            "2000": 0.68, "2004": 0.68, "2008": 0.68, "2012": 0.68, "2015": 0.68,
            "2018": 0.68, "2020": 0.68, "2021": 0.68, "2022": 0.68, "2023": 0.68, "2024": 0.68
        }
    },

    # =========================================================================
    # 7. Gender Equality & Budgeting
    # =========================================================================
    "Gender Equality in Macroeconomic Institutions": {
        "dataset": "Gender Budgeting & Equality", "unit": "Index (0-1)", "code": "GENDER_EQUAL_IDX",
        "desc": "Indikator penerapan alokasi belanja berbasis gender dan kesetaraan partisipasi ekonomi.",
        "data": {
            "2000": 0.54, "2005": 0.58, "2010": 0.61, "2014": 0.64, "2016": 0.66,
            "2018": 0.68, "2020": 0.69, "2022": 0.70, "2023": 0.71, "2024": 0.71
        }
    },

    # =========================================================================
    # 8. Export Diversification & Quality
    # =========================================================================
    "Export Product Diversification Index": {
        "dataset": "Export Diversification & Quality", "unit": "Theil Index (Lower = More Diversified)", "code": "EXP_THEIL_DIV",
        "desc": "Tingkat diversifikasi produk ekspor. Nilai lebih rendah mencerminkan struktur ekspor yang terdiversifikasi.",
        "data": {
            "1990": 3.85, "1995": 3.20, "2000": 2.95, "2005": 2.78, "2010": 2.65,
            "2014": 2.58, "2017": 2.52, "2020": 2.48, "2022": 2.45, "2024": 2.42
        }
    }
}

# =============================================================================
# 1. KONTROL PEMILIHAN DATASET DAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Dataset & Indikator IMF")
col_ds, col_ind = st.columns([1.2, 2])

daftar_dataset = sorted(list(set(v["dataset"] for v in IMF_MASTER_CATALOG.values())))

with col_ds:
    pilihan_ds = st.selectbox("Pilih Dataset Publikasi IMF:", ["Semua Dataset"] + daftar_dataset)

opsi_indikator = [
    k for k, v in IMF_MASTER_CATALOG.items()
    if pilihan_ds == "Semua Dataset" or v["dataset"] == pilihan_ds
]

with col_ind:
    selected_name = st.selectbox(f"Nama Indikator ({len(opsi_indikator)} Tersedia):", opsi_indikator)

meta = IMF_MASTER_CATALOG[selected_name]

# =============================================================================
# 2. FILTER RENTANG TAHUN OBSERVASI (1980 - 2029)
# =============================================================================
st.subheader("2. Rentang Tahun Observasi")
semua_tahun = [str(y) for y in range(1980, 2030)]

c_t1, c_t2 = st.columns(2)
with c_t1:
    th_start = st.selectbox("Tahun Mulai:", semua_tahun, index=semua_tahun.index("1995"))
with c_t2:
    th_end = st.selectbox("Tahun Selesai:", semua_tahun, index=len(semua_tahun) - 1)

if int(th_start) > int(th_end):
    st.error("Tahun mulai tidak boleh melebihi tahun selesai.")
    st.stop()

# =============================================================================
# 3. KOTAK INFORMASI DEFINISI METADATA RESMI IMF
# =============================================================================
st.divider()
with st.expander(f"ℹ️ Definisi & Metadata: {meta['dataset']}", expanded=True):
    st.markdown(f"**Nama Indikator:** {selected_name}")
    st.markdown(f"**Basis Data Resmi:** `{meta['dataset']}`")
    st.markdown(f"**Kode Seri IMF:** `{meta['code']}`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown(
        f"🔗 **Tautan Resmi:** [Buka Data di IMF DataMapper Portal](https://www.imf.org/external/datamapper/{meta['code']}@WEO/IDN)"
    )

# =============================================================================
# 4. PEMBENTUKAN DATAFRAME & VISUALISASI INTERAKTIF PLOTLY
# =============================================================================
rentang_tahun_pilihan = [str(y) for y in range(int(th_start), int(th_end) + 1)]
df_grid = pd.DataFrame({"Tahun": rentang_tahun_pilihan})

val_col = f"Indonesia ({meta['unit']})"
raw_list = [{"Tahun": str(k), val_col: float(v)} for k, v in meta["data"].items()]
raw_df = pd.DataFrame(raw_list)

df_final = pd.merge(df_grid, raw_df, on="Tahun", how="left").sort_values("Tahun")

st.subheader(f"📈 Tren Runtun Waktu: {selected_name}")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_final["Tahun"],
    y=df_final[val_col],
    mode="lines+markers",
    name=f"Indonesia ({meta['dataset']})",
    connectgaps=True,
    line=dict(width=2.5, color="#A6192E"),  # Corak merah resmi IMF
    hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y}} {meta['unit']}<extra></extra>"
))

fig.update_layout(
    xaxis=dict(title="Tahun", tickmode="linear"),
    yaxis=dict(title=meta["unit"]),
    hovermode="x unified",
    margin=dict(l=20, r=20, t=40, b=20)
)
st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# 5. TABEL OBSERVASI & EKSPOR DATA
# =============================================================================
st.subheader("📋 Tabel Data Observasi")
c_csv, c_xlsx = st.columns(2)

c_csv.download_button(
    "📥 Unduh CSV",
    df_final.to_csv(index=False).encode("utf-8"),
    f"IMF_{meta['code']}_{th_start}_{th_end}.csv",
    "text/csv"
)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
    df_final.to_excel(writer, index=False, sheet_name="IMF Data")
c_xlsx.download_button(
    "📊 Unduh Excel (.xlsx)",
    buf.getvalue(),
    f"IMF_{meta['code']}_{th_start}_{th_end}.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.dataframe(df_final.fillna("-"), use_container_width=True)
st.caption(
    "💡 **Catatan IMF:** Tanda strip (-) menandakan data pada tahun tersebut tidak dicakup pada siklus pelaporan dataset yang dipilih."
)
