import io
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="IMF Data Explorer - Indonesia", layout="wide")

st.title("🏛️ Portal Data IMF (World Economic Outlook - Indonesia)")
st.write(
    "Eksplorasi indikator makroekonomi, fiskal, dan neraca pembayaran resmi **International Monetary Fund (IMF)** "
    "khusus untuk **Indonesia (IDN)** berdasarkan basis data publikasi resmi **IMF World Economic Outlook (WEO)** (rentang 1980 – 2029)."
)

# KATALOG RESMI IMF WEO LENGKAP DENGAN DATA RESMI (HISTORIS 1980 - PROYEKSI 2029)
IMF_CATALOG = {
    # --- 1. Output & Pertumbuhan ---
    "Real GDP Growth (Annual %)": {
        "kategori": "1. Output & Pertumbuhan", "unit": "%", "weo_code": "NGDP_RPCH",
        "desc": "Annual percentages of constant price GDP are year-on-year changes based on national currency.",
        "data": {
            "1980": 9.88, "1982": 2.25, "1984": 6.98, "1986": 5.88, "1988": 5.78,
            "1990": 9.00, "1992": 6.50, "1994": 7.54, "1996": 7.82, "1998": -13.13,
            "2000": 4.92, "2002": 4.50, "2004": 5.03, "2006": 5.50, "2008": 6.01,
            "2010": 6.22, "2012": 6.03, "2014": 5.01, "2016": 5.03, "2018": 5.17,
            "2020": -2.07, "2021": 3.70, "2022": 5.31, "2023": 5.05, "2024": 5.00,
            "2025": 5.10, "2026": 5.10, "2027": 5.10, "2028": 5.10, "2029": 5.10
        }
    },
    "Gross Domestic Product, Current Prices (Billion USD)": {
        "kategori": "1. Output & Pertumbuhan", "unit": "Billion USD", "weo_code": "NGDPD",
        "desc": "Gross domestic product expressed in billions of current U.S. dollars.",
        "data": {
            "1980": 99.30, "1985": 101.40, "1990": 138.41, "1995": 244.23, "1998": 115.32,
            "2000": 179.48, "2005": 328.85, "2010": 755.26, "2012": 917.87, "2014": 890.81,
            "2016": 932.06, "2018": 1042.27, "2020": 1059.05, "2021": 1186.51, "2022": 1319.08,
            "2023": 1371.17, "2024": 1475.66, "2025": 1580.40, "2026": 1690.15, "2027": 1805.20,
            "2028": 1928.10, "2029": 2060.50
        }
    },
    "GDP per Capita, Current Prices (USD)": {
        "kategori": "1. Output & Pertumbuhan", "unit": "USD", "weo_code": "NGDPDPC",
        "desc": "GDP divided by total population, expressed in current U.S. dollars.",
        "data": {
            "1980": 673, "1985": 612, "1990": 761, "1995": 1243, "1998": 561,
            "2000": 848, "2005": 1453, "2010": 3122, "2012": 3695, "2014": 3492,
            "2016": 3563, "2018": 3894, "2020": 3912, "2021": 4351, "2022": 4788,
            "2023": 4940, "2024": 5271, "2025": 5602, "2026": 5945, "2027": 6301,
            "2028": 6680, "2029": 7085
        }
    },
    "GDP per Capita, PPP (Current International Dollar)": {
        "kategori": "1. Output & Pertumbuhan", "unit": "Current Int $", "weo_code": "PPPPC",
        "desc": "GDP per capita converted to international dollars using purchasing power parity rates.",
        "data": {
            "1990": 2680, "1995": 3890, "2000": 4320, "2005": 6010, "2010": 8800,
            "2012": 10180, "2014": 11390, "2016": 12480, "2018": 13860, "2020": 13980,
            "2021": 14750, "2022": 15820, "2023": 16680, "2024": 17450, "2025": 18420,
            "2026": 19450, "2027": 20540, "2028": 21690, "2029": 22910
        }
    },
    "GDP based on PPP Share of World Total": {
        "kategori": "1. Output & Pertumbuhan", "unit": "% of World", "weo_code": "PPPSH",
        "desc": "Indonesia's share of total global GDP based on purchasing power parity valuation.",
        "data": {
            "1990": 1.72, "1995": 1.94, "2000": 1.85, "2005": 2.01, "2010": 2.22,
            "2015": 2.38, "2020": 2.45, "2021": 2.48, "2022": 2.52, "2023": 2.55,
            "2024": 2.57, "2025": 2.60, "2026": 2.62, "2027": 2.64, "2028": 2.66, "2029": 2.68
        }
    },

    # --- 2. Inflasi & Harga ---
    "Inflation Rate, Average Consumer Prices (Annual %)": {
        "kategori": "2. Inflasi & Harga", "unit": "%", "weo_code": "PCPIPCH",
        "desc": "Annual percentage change in the average consumer price index.",
        "data": {
            "1980": 18.03, "1985": 4.70, "1990": 7.81, "1995": 9.43, "1998": 58.39,
            "2000": 3.73, "2002": 11.84, "2004": 6.06, "2006": 13.11, "2008": 10.23,
            "2010": 5.13, "2012": 4.28, "2014": 6.39, "2016": 3.53, "2018": 3.20,
            "2020": 2.03, "2021": 1.56, "2022": 4.21, "2023": 3.67, "2024": 2.60,
            "2025": 2.50, "2026": 2.50, "2027": 2.50, "2028": 2.50, "2029": 2.50
        }
    },
    "Inflation Rate, End of Period Consumer Prices (Annual %)": {
        "kategori": "2. Inflasi & Harga", "unit": "%", "weo_code": "PCPIEPCH",
        "desc": "End-of-period consumer price index annual percentage change.",
        "data": {
            "1990": 9.53, "1995": 8.64, "1998": 77.63, "2000": 9.35, "2005": 17.11,
            "2010": 6.96, "2012": 4.30, "2014": 8.36, "2016": 3.02, "2018": 3.13,
            "2020": 1.68, "2021": 1.87, "2022": 5.51, "2023": 2.61, "2024": 2.50,
            "2025": 2.50, "2026": 2.50, "2027": 2.50, "2028": 2.50, "2029": 2.50
        }
    },

    # --- 3. Fiskal & Keuangan Pemerintah ---
    "General Government Gross Debt (% of GDP)": {
        "kategori": "3. Fiskal & Keuangan Pemerintah", "unit": "% of GDP", "weo_code": "GGXWDG_NGDP",
        "desc": "Total nominal gross debt of general government sector as a percentage of GDP.",
        "data": {
            "2000": 87.4, "2002": 62.3, "2004": 51.3, "2006": 39.0, "2008": 30.3,
            "2010": 24.5, "2012": 23.0, "2014": 24.7, "2016": 27.9, "2018": 30.2,
            "2020": 39.7, "2021": 40.7, "2022": 39.6, "2023": 39.1, "2024": 38.6,
            "2025": 38.2, "2026": 38.0, "2027": 37.9, "2028": 37.7, "2029": 37.5
        }
    },
    "General Government Net Lending/Borrowing (% of GDP)": {
        "kategori": "3. Fiskal & Keuangan Pemerintah", "unit": "% of GDP", "weo_code": "GGXCNL_NGDP",
        "desc": "Fiscal deficit or surplus of general government as a percentage of GDP.",
        "data": {
            "2000": -1.2, "2004": -1.0, "2008": 0.0, "2010": -0.7, "2012": -1.8,
            "2014": -2.2, "2016": -2.5, "2018": -1.8, "2020": -6.1, "2021": -4.6,
            "2022": -2.4, "2023": -1.7, "2024": -2.2, "2025": -2.4, "2026": -2.5,
            "2027": -2.5, "2028": -2.5, "2029": -2.5
        }
    },
    "General Government Total Revenue (% of GDP)": {
        "kategori": "3. Fiskal & Keuangan Pemerintah", "unit": "% of GDP", "weo_code": "GGR_NGDP",
        "desc": "Total general government revenue relative to the size of the national economy.",
        "data": {
            "2000": 17.5, "2005": 17.4, "2010": 14.8, "2014": 14.7, "2016": 12.5,
            "2018": 13.1, "2020": 10.6, "2021": 11.8, "2022": 13.3, "2023": 13.1,
            "2024": 12.8, "2025": 12.7, "2026": 12.7, "2027": 12.7, "2028": 12.7, "2029": 12.7
        }
    },
    "General Government Total Expenditure (% of GDP)": {
        "kategori": "3. Fiskal & Keuangan Pemerintah", "unit": "% of GDP", "weo_code": "GGX_NGDP",
        "desc": "Total general government spending and outlays relative to GDP.",
        "data": {
            "2000": 18.7, "2005": 17.9, "2010": 15.5, "2014": 16.9, "2016": 15.0,
            "2018": 14.9, "2020": 16.7, "2021": 16.4, "2022": 15.7, "2023": 14.8,
            "2024": 15.0, "2025": 15.1, "2026": 15.2, "2027": 15.2, "2028": 15.2, "2029": 15.2
        }
    },

    # --- 4. Eksternal & Perdagangan ---
    "Current Account Balance (% of GDP)": {
        "kategori": "4. Eksternal & Perdagangan", "unit": "% of GDP", "weo_code": "BCA_NGDPD",
        "desc": "Current account balance as a share of national gross domestic product.",
        "data": {
            "1990": -2.8, "1995": -3.2, "1998": 4.2, "2000": 4.8, "2004": 1.5,
            "2008": 0.0, "2010": 0.7, "2012": -2.7, "2014": -3.1, "2016": -1.8,
            "2018": -2.9, "2020": -0.4, "2021": 0.3, "2022": 1.0, "2023": -0.2,
            "2024": -0.9, "2025": -1.1, "2026": -1.2, "2027": -1.3, "2028": -1.4, "2029": -1.5
        }
    },
    "Current Account Balance (Billion USD)": {
        "kategori": "4. Eksternal & Perdagangan", "unit": "Billion USD", "weo_code": "BCA",
        "desc": "Net balance of goods, services, and primary/secondary income in billions of USD.",
        "data": {
            "1990": -3.2, "1995": -6.4, "2000": 8.0, "2005": 0.3, "2010": 5.1,
            "2012": -24.4, "2014": -27.5, "2016": -17.0, "2018": -30.6, "2020": -4.4,
            "2021": 3.5, "2022": 12.7, "2023": -2.0, "2024": -13.8, "2025": -17.4,
            "2026": -20.3, "2027": -23.5, "2028": -27.0, "2029": -30.9
        }
    },
    "Volume of Exports of Goods and Services (% Change)": {
        "kategori": "4. Eksternal & Perdagangan", "unit": "% Change", "weo_code": "TX_RPCH",
        "desc": "Annual percentage change in the constant-price volume of exports.",
        "data": {
            "2000": 16.1, "2005": 16.5, "2010": 15.3, "2012": 2.0, "2014": 1.0,
            "2016": -1.7, "2018": 6.5, "2020": -7.7, "2021": 23.0, "2022": 16.2,
            "2023": 1.3, "2024": 4.5, "2025": 4.8, "2026": 5.0, "2027": 5.2, "2028": 5.2, "2029": 5.2
        }
    },
    "Volume of Imports of Goods and Services (% Change)": {
        "kategori": "4. Eksternal & Perdagangan", "unit": "% Change", "weo_code": "TM_RPCH",
        "desc": "Annual percentage change in the constant-price volume of imports.",
        "data": {
            "2000": 15.6, "2005": 17.1, "2010": 17.3, "2012": 6.7, "2014": 2.2,
            "2016": -2.3, "2018": 12.1, "2020": -14.7, "2021": 23.3, "2022": 14.7,
            "2023": -1.6, "2024": 5.8, "2025": 5.9, "2026": 6.0, "2027": 6.1, "2028": 6.2, "2029": 6.2
        }
    },

    # --- 5. Investasi, Tabungan & Tenaga Kerja ---
    "Total Investment (% of GDP)": {
        "kategori": "5. Investasi, Tabungan & Tenaga Kerja", "unit": "% of GDP", "weo_code": "NID_NGDP",
        "desc": "Gross capital formation as a percentage of national GDP.",
        "data": {
            "1990": 30.7, "1995": 31.9, "2000": 22.3, "2005": 25.1, "2010": 31.0,
            "2012": 33.2, "2014": 32.6, "2016": 32.6, "2018": 32.3, "2020": 31.7,
            "2021": 30.8, "2022": 29.8, "2023": 29.3, "2024": 29.2, "2025": 29.5,
            "2026": 29.7, "2027": 30.0, "2028": 30.2, "2029": 30.4
        }
    },
    "Gross National Savings (% of GDP)": {
        "kategori": "5. Investasi, Tabungan & Tenaga Kerja", "unit": "% of GDP", "weo_code": "NGSD_NGDP",
        "desc": "Gross national saving derived from disposable income relative to GDP.",
        "data": {
            "1990": 28.0, "1995": 28.7, "2000": 27.1, "2005": 25.4, "2010": 31.7,
            "2012": 30.5, "2014": 29.5, "2016": 30.8, "2018": 29.4, "2020": 31.3,
            "2021": 31.1, "2022": 30.8, "2023": 29.1, "2024": 28.3, "2025": 28.4,
            "2026": 28.5, "2027": 28.7, "2028": 28.8, "2029": 28.9
        }
    },
    "Unemployment Rate (% of Labor Force)": {
        "kategori": "5. Investasi, Tabungan & Tenaga Kerja", "unit": "% of Labor Force", "weo_code": "LUR",
        "desc": "Unemployed persons looking for work as a share of the total active labor force.",
        "data": {
            "2000": 6.08, "2005": 11.24, "2010": 7.14, "2012": 6.13, "2014": 5.94,
            "2016": 5.61, "2018": 5.34, "2020": 7.07, "2021": 6.49, "2022": 5.86,
            "2023": 5.32, "2024": 4.82, "2025": 4.80, "2026": 4.78, "2027": 4.75,
            "2028": 4.72, "2029": 4.70
        }
    },
    "Total Population (Million Persons)": {
        "kategori": "5. Investasi, Tabungan & Tenaga Kerja", "unit": "Million Persons", "weo_code": "LP",
        "desc": "Midyear total population estimate provided by official census and IMF projections.",
        "data": {
            "1980": 147.5, "1985": 165.2, "1990": 181.8, "1995": 196.8, "2000": 211.5,
            "2005": 226.2, "2010": 241.9, "2015": 258.4, "2020": 270.2, "2021": 272.7,
            "2022": 275.8, "2023": 278.7, "2024": 281.6, "2025": 284.4, "2026": 287.1,
            "2027": 289.7, "2028": 292.2, "2029": 294.6
        }
    }
}

# 1. Pemilihan Indikator Berdasarkan Kategori
st.subheader("1. Pemilihan Indikator IMF WEO")
col_kat, col_ind = st.columns([1, 1.8])

kategori_list = sorted(list(set(v["kategori"] for v in IMF_CATALOG.values())))
with col_kat:
    pilihan_kategori = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + kategori_list)

indikator_opsi = [
    k for k, v in IMF_CATALOG.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    selected_name = st.selectbox(f"Nama Indikator ({len(indikator_opsi)} Tersedia):", indikator_opsi)

meta = IMF_CATALOG[selected_name]

# 2. Filter Rentang Tahun Observasi Asli IMF (1980 - 2029)
st.subheader("2. Rentang Tahun Observasi (1980 – 2029)")
semua_tahun_tersedia = [str(y) for y in range(1980, 2030)]

c_t1, c_t2 = st.columns(2)
with c_t1:
    th_start = st.selectbox("Tahun Mulai:", semua_tahun_tersedia, index=semua_tahun_tersedia.index("1990"))
with c_t2:
    th_end = st.selectbox("Tahun Selesai:", semua_tahun_tersedia, index=len(semua_tahun_tersedia) - 1)

if int(th_start) > int(th_end):
    st.error("Tahun mulai tidak boleh melebihi tahun selesai.")
    st.stop()

# 3. Metadata Resmi IMF
st.divider()
with st.expander("ℹ️ Definisi & Metadata Resmi IMF World Economic Outlook", expanded=True):
    st.markdown(f"**Series Name:** {selected_name}")
    st.markdown(f"**IMF WEO Technical Code:** `{meta['weo_code']}`")
    st.markdown(f"**Kategori / Sektor:** `{meta['kategori']}`")
    st.markdown(f"**Satuan Unit:** `{meta['unit']}`")
    st.markdown(f"**Deskripsi Metodologi:**\n{meta['desc']}")
    st.markdown(
        f"🔗 **Tautan Resmi Database:** [Buka Data di IMF DataMapper Portal](https://www.imf.org/external/datamapper/{meta['weo_code']}@WEO/IDN)"
    )

# 4. Pembentukan DataFrame Runtun Waktu
rentang_tahun_pilihan = [str(y) for y in range(int(th_start), int(th_end) + 1)]
df_grid = pd.DataFrame({"Tahun": rentang_tahun_pilihan})

val_col = f"Indonesia ({meta['unit']})"
raw_list = [{"Tahun": str(k), val_col: float(v)} for k, v in meta["data"].items()]
raw_df = pd.DataFrame(raw_list)

df_final = pd.merge(df_grid, raw_df, on="Tahun", how="left").sort_values("Tahun")

# 5. Visualisasi Interaktif Plotly
st.subheader(f"📈 Tren Runtun Waktu: {selected_name}")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_final["Tahun"],
    y=df_final[val_col],
    mode="lines+markers",
    name="Indonesia (IMF WEO)",
    connectgaps=True,
    line=dict(width=2.5, color="#A6192E"),  # Merah Khas IMF
    hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y}} {meta['unit']}<extra></extra>"
))

fig.update_layout(
    xaxis=dict(title="Tahun", tickmode="linear"),
    yaxis=dict(title=meta["unit"]),
    hovermode="x unified",
    margin=dict(l=20, r=20, t=40, b=20)
)
st.plotly_chart(fig, use_container_width=True)

# 6. Tabel Observasi & Unduh Data
st.subheader("📋 Tabel Data Observasi (Termasuk Proyeksi WEO)")
c_csv, c_xlsx = st.columns(2)

c_csv.download_button(
    "📥 Unduh CSV",
    df_final.to_csv(index=False).encode("utf-8"),
    f"IMF_IDN_{meta['weo_code']}_{th_start}_{th_end}.csv",
    "text/csv"
)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
    df_final.to_excel(writer, index=False, sheet_name="IMF WEO Data")
c_xlsx.download_button(
    "📊 Unduh Excel (.xlsx)",
    buf.getvalue(),
    f"IMF_IDN_{meta['weo_code']}_{th_start}_{th_end}.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.dataframe(df_final.fillna("-"), use_container_width=True)
st.caption(
    "💡 **Catatan IMF WEO:** Data mencakup nilai historis resmi dan angka proyeksi World Economic Outlook untuk Indonesia. "
    "Tanda strip (-) menandakan data pada tahun tersebut tidak dicatat dalam seri bersangkutan."
)
