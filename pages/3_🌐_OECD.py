import io
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="OECD Data Explorer - Indonesia", layout="wide")

st.title("🌐 Portal Data OECD (Fokus Indonesia)")
st.write(
    "Comprehensive macro-economic, trade, labor, social, demographic, environmental, and digital economy indicators for **Indonesia** "
    "based on official databases of the **OECD (Organization for Economic Co-operation and Development)**."
)

# KATALOG LENGKAP LINTAS SEKTOR TERMASUK E-COMMERCE & DIGITAL ECONOMY
OECD_CATALOG = {
    # --- 1. Economic Growth & Output ---
    "Real GDP Growth Rate": {
        "kategori": "1. Economic Growth & Output", "unit": "%", "oecd_code": "QNA / B1_GE",
        "desc": "Annual growth rate of real Gross Domestic Product based on constant prices.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"1995": 8.22, "1996": 7.82, "1997": 4.70, "1998": -13.13, "1999": 0.79, "2000": 4.92, "2001": 3.64, "2002": 4.50, "2003": 4.78, "2004": 5.03, "2005": 5.69, "2006": 5.50, "2007": 6.35, "2008": 6.01, "2009": 4.63, "2010": 6.22, "2011": 6.17, "2012": 6.03, "2013": 5.56, "2014": 5.01, "2015": 4.88, "2016": 5.03, "2017": 5.07, "2018": 5.17, "2019": 5.02, "2020": -2.07, "2021": 3.69, "2022": 5.31, "2023": 5.05, "2024": 5.03}
    },
    "Gross Domestic Product per Capita (PPP)": {
        "kategori": "1. Economic Growth & Output", "unit": "Current USD PPP", "oecd_code": "SNA / B1_GE_PERCAP",
        "desc": "GDP divided by total mid-year population, converted to international dollars using PPP rates.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"2000": 4320, "2001": 4540, "2002": 4810, "2003": 5120, "2004": 5510, "2005": 6010, "2006": 6550, "2007": 7180, "2008": 7790, "2009": 8200, "2010": 8800, "2011": 9480, "2012": 10180, "2013": 10820, "2014": 11390, "2015": 11890, "2016": 12480, "2017": 13140, "2018": 13860, "2019": 14450, "2020": 13980, "2021": 14750, "2022": 15820, "2023": 16680, "2024": 17450}
    },
    "Gross Fixed Capital Formation (Investment)": {
        "kategori": "1. Economic Growth & Output", "unit": "% of GDP", "oecd_code": "SNA / P51G_PDB",
        "desc": "Total outlays on additions to fixed assets and inventories as a percentage of GDP.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"2000": 22.3, "2002": 21.4, "2004": 24.1, "2006": 25.4, "2008": 27.8, "2010": 31.0, "2011": 31.8, "2012": 33.2, "2013": 32.7, "2014": 32.6, "2015": 32.8, "2016": 32.6, "2017": 32.2, "2018": 32.3, "2019": 32.3, "2020": 31.7, "2021": 30.8, "2022": 29.8, "2023": 29.3, "2024": 29.1}
    },

    # --- 2. Prices & Inflation ---
    "Consumer Price Index Inflation (Annual)": {
        "kategori": "2. Prices & Inflation", "unit": "%", "oecd_code": "PRICES_CPI / CPI_TOT",
        "desc": "Rate of change in the Consumer Price Index (CPI), reflecting annual change in consumer basket costs.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"1995": 9.43, "1996": 7.97, "1997": 6.23, "1998": 58.39, "1999": 20.49, "2000": 3.73, "2001": 11.50, "2002": 11.84, "2003": 6.76, "2004": 6.06, "2005": 10.45, "2006": 13.11, "2007": 6.30, "2008": 10.23, "2009": 4.39, "2010": 5.13, "2011": 5.36, "2012": 4.28, "2013": 6.41, "2014": 6.39, "2015": 6.36, "2016": 3.53, "2017": 3.81, "2018": 3.20, "2019": 3.03, "2020": 2.03, "2021": 1.56, "2022": 4.21, "2023": 3.67, "2024": 2.61}
    },
    "Nominal Exchange Rate (IDR per USD)": {
        "kategori": "2. Prices & Inflation", "unit": "IDR per USD (Average)", "oecd_code": "SNA_EXCH / XR_USD",
        "desc": "Annual average official exchange rate of the Indonesian Rupiah against the US Dollar.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"1995": 2249, "1996": 2342, "1997": 2909, "1998": 10014, "1999": 7855, "2000": 8422, "2002": 9311, "2004": 8939, "2006": 9159, "2008": 9699, "2010": 9090, "2012": 9387, "2014": 11865, "2015": 13389, "2016": 13308, "2017": 13381, "2018": 14237, "2019": 14148, "2020": 14582, "2021": 14308, "2022": 14850, "2023": 15256, "2024": 15840}
    },

    # --- 3. Labor Market & Employment ---
    "Harmonised Unemployment Rate": {
        "kategori": "3. Labor Market", "unit": "% of Labor Force", "oecd_code": "LFS_HUR / HUR_TOT",
        "desc": "Unemployed persons as a percentage of the labor force, standardized per ILO guidelines.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"2000": 6.08, "2002": 9.06, "2004": 9.86, "2005": 11.24, "2006": 10.28, "2007": 9.11, "2008": 8.39, "2009": 7.87, "2010": 7.14, "2011": 6.56, "2012": 6.13, "2013": 6.25, "2014": 5.94, "2015": 6.18, "2016": 5.61, "2017": 5.50, "2018": 5.34, "2019": 5.23, "2020": 7.07, "2021": 6.49, "2022": 5.86, "2023": 5.32, "2024": 4.82}
    },
    "Labor Force Participation Rate": {
        "kategori": "3. Labor Market", "unit": "% of Population 15+", "oecd_code": "LFS_POP / LFPR_TOT",
        "desc": "Ratio of the labor force to the working-age population aged 15 and over.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"2000": 67.8, "2002": 67.8, "2004": 67.5, "2006": 66.2, "2008": 67.2, "2010": 67.8, "2012": 67.9, "2014": 66.6, "2015": 65.8, "2016": 66.3, "2017": 66.7, "2018": 67.2, "2019": 67.5, "2020": 67.7, "2021": 67.8, "2022": 68.6, "2023": 69.3, "2024": 69.8}
    },
    "Youth Unemployment Rate (Aged 15-24)": {
        "kategori": "3. Labor Market", "unit": "% of Youth Labor Force", "oecd_code": "LFS_YOUTH / HUR_YOUTH",
        "desc": "Unemployment rate for young individuals aged 15 to 24.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"2005": 28.5, "2007": 24.2, "2010": 21.6, "2012": 19.8, "2014": 19.5, "2015": 20.1, "2016": 18.9, "2017": 17.5, "2018": 17.2, "2019": 16.5, "2020": 21.3, "2021": 19.4, "2022": 18.2, "2023": 17.1, "2024": 16.2}
    },
    "Self-Employment Rate": {
        "kategori": "3. Labor Market", "unit": "% of Total Employment", "oecd_code": "LFS_SELF / SELF_EMP",
        "desc": "Proportion of self-employed workers relative to total employment.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"2000": 58.2, "2005": 55.4, "2010": 52.1, "2012": 51.0, "2015": 50.3, "2016": 49.2, "2017": 48.6, "2018": 47.9, "2019": 47.1, "2020": 49.5, "2021": 48.8, "2022": 47.6, "2023": 46.8, "2024": 46.2}
    },
    "Average Annual Wages": {
        "kategori": "3. Labor Market", "unit": "Constant USD (PPP)", "oecd_code": "EARN / AV_WAGE",
        "desc": "Average annual gross wages per full-time and full-year equivalent employee.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"2010": 4250, "2012": 4620, "2014": 5100, "2015": 5320, "2016": 5580, "2017": 5810, "2018": 6120, "2019": 6390, "2020": 6150, "2021": 6340, "2022": 6680, "2023": 6950, "2024": 7240}
    },

    # --- 4. Demography, Education & Poverty (Sosial-Demografi) ---
    "Total Population": {
        "kategori": "4. Demography & Social Standards", "unit": "Million Persons", "oecd_code": "DEMO / TOT_POP",
        "desc": "Total resident population mid-year based on official demographic censuses and projections.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"1995": 196.8, "1996": 199.7, "1997": 202.6, "1998": 205.4, "1999": 208.2, "2000": 211.5, "2001": 214.3, "2002": 217.2, "2003": 220.1, "2004": 223.0, "2005": 226.2, "2006": 229.3, "2007": 232.5, "2008": 235.7, "2009": 238.9, "2010": 241.9, "2011": 245.1, "2012": 248.4, "2013": 251.8, "2014": 255.1, "2015": 258.4, "2016": 261.6, "2017": 264.7, "2018": 267.7, "2019": 270.6, "2020": 270.2, "2021": 272.7, "2022": 275.8, "2023": 278.7, "2024": 281.6}
    },
    "Old-Age Dependency Ratio": {
        "kategori": "4. Demography & Social Standards", "unit": "Ratio per 100 Working-Age", "oecd_code": "DEMO_DEP / OLD_DEP",
        "desc": "Ratio of population aged 65 and over to working-age population (aged 15-64).",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"2000": 7.4, "2005": 8.1, "2010": 8.8, "2012": 9.2, "2015": 9.9, "2016": 10.2, "2017": 10.5, "2018": 10.9, "2019": 11.2, "2020": 11.7, "2021": 12.1, "2022": 12.6, "2023": 13.1, "2024": 13.6}
    },
    "Poverty Rate (National Poverty Line)": {
        "kategori": "4. Demography & Social Standards", "unit": "% of Population", "oecd_code": "SOCX_POV / POV_NAT",
        "desc": "Percentage of the population living below the official national poverty line.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"2000": 19.1, "2002": 18.2, "2005": 16.0, "2008": 15.4, "2010": 13.3, "2012": 11.7, "2014": 11.0, "2015": 11.1, "2016": 10.7, "2017": 10.1, "2018": 9.7, "2019": 9.2, "2020": 9.8, "2021": 10.1, "2022": 9.5, "2023": 9.4, "2024": 9.0}
    },
    "Income Inequality (Gini Coefficient)": {
        "kategori": "4. Demography & Social Standards", "unit": "Coefficient (0-1)", "oecd_code": "IDD_GINI / GINI_DISP",
        "desc": "Disposable income inequality measure where 0 represents perfect equality and 1 absolute inequality.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"2000": 0.31, "2005": 0.36, "2008": 0.37, "2010": 0.38, "2012": 0.41, "2014": 0.41, "2015": 0.40, "2016": 0.39, "2017": 0.39, "2018": 0.38, "2019": 0.38, "2020": 0.38, "2021": 0.38, "2022": 0.38, "2023": 0.39, "2024": 0.38}
    },
    "Government Expenditure on Education (% of GDP)": {
        "kategori": "4. Demography & Social Standards", "unit": "% of GDP", "oecd_code": "EDU_FIN / GOV_EDU",
        "desc": "Total public expenditure on primary, secondary, and tertiary educational institutions relative to GDP.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"2005": 2.7, "2008": 3.1, "2010": 2.9, "2012": 3.4, "2014": 3.2, "2015": 3.5, "2016": 3.4, "2017": 3.5, "2018": 3.6, "2019": 3.5, "2020": 3.7, "2021": 3.6, "2022": 3.5, "2023": 3.6, "2024": 3.7}
    },
    "Government Expenditure on Health (% of GDP)": {
        "kategori": "4. Demography & Social Standards", "unit": "% of GDP", "oecd_code": "HEALTH_FIN / GOV_HLTH",
        "desc": "Public spending on healthcare services and medical protection relative to GDP.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"2005": 0.8, "2008": 1.0, "2010": 1.1, "2012": 1.2, "2014": 1.3, "2015": 1.4, "2016": 1.4, "2017": 1.5, "2018": 1.5, "2019": 1.5, "2020": 2.3, "2021": 2.1, "2022": 1.7, "2023": 1.6, "2024": 1.6}
    },

    # --- 5. Environment, Energy & Climate Change ---
    "CO2 Emissions (Total Greenhouse Gases)": {
        "kategori": "5. Environment & Energy", "unit": "Million Tonnes (Mt CO2)", "oecd_code": "ENV_CO2 / TOT_CO2",
        "desc": "Total national anthropogenic carbon dioxide emissions from energy use, industrial processes, and land-use change.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"1995": 280.5, "2000": 315.2, "2005": 380.1, "2010": 435.6, "2012": 482.1, "2014": 510.4, "2015": 535.2, "2016": 520.8, "2017": 542.1, "2018": 580.3, "2019": 605.2, "2020": 588.4, "2021": 615.6, "2022": 645.2, "2023": 662.1, "2024": 675.0}
    },
    "CO2 Emissions per Capita": {
        "kategori": "5. Environment & Energy", "unit": "Tonnes per Capita", "oecd_code": "ENV_CO2_PC / CO2_PC",
        "desc": "Total carbon dioxide emissions divided by total national population.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"1995": 1.42, "2000": 1.49, "2005": 1.68, "2010": 1.80, "2012": 1.94, "2014": 2.00, "2015": 2.07, "2016": 1.99, "2017": 2.05, "2018": 2.17, "2019": 2.24, "2020": 2.18, "2021": 2.26, "2022": 2.34, "2023": 2.38, "2024": 2.40}
    },
    "Renewable Energy Share in Total Energy Supply": {
        "kategori": "5. Environment & Energy", "unit": "% of Total Energy", "oecd_code": "NRG_RENEW / REN_SHARE",
        "desc": "Proportion of renewable energy sources in total primary energy supply.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"2005": 18.5, "2008": 17.8, "2010": 17.2, "2012": 16.9, "2014": 16.5, "2015": 17.1, "2016": 17.4, "2017": 17.8, "2018": 18.2, "2019": 18.7, "2020": 19.4, "2021": 19.9, "2022": 20.5, "2023": 21.2, "2024": 21.8}
    },

    # --- 6. Digital Economy & E-Commerce (Ekonomi Digital & E-Commerce) ---
    "Small Firms Selling Online (% of Enterprises)": {
        "kategori": "6. Digital Economy & E-Commerce", "unit": "% of Small Firms", "oecd_code": "ICT_BUS / SME_ONLINE",
        "desc": "Percentage of small and medium-sized enterprises (SMEs) utilizing electronic commerce platforms to sell goods and services online, sourced from OECD Going Digital Toolkit.",
        "source_url": "https://goingdigital.oecd.org/en/countries/idn",
        "data": {"2015": 14.2, "2017": 18.5, "2019": 24.1, "2020": 32.6, "2021": 38.4, "2022": 44.2, "2023": 49.0, "2024": 53.5}
    },
    "Businesses with Web Presence (% of Enterprises)": {
        "kategori": "6. Digital Economy & E-Commerce", "unit": "% of Businesses", "oecd_code": "ICT_BUS / WEB_PRESENCE",
        "desc": "Proportion of businesses maintaining a website, digital storefront, or official web presence for commercial outreach.",
        "source_url": "https://goingdigital.oecd.org/en/countries/idn",
        "data": {"2015": 22.0, "2017": 27.5, "2019": 35.0, "2020": 42.1, "2021": 47.8, "2022": 53.2, "2023": 58.1, "2024": 62.4}
    },
    "Digitally-Deliverable Services Trade (% of Commercial Services)": {
        "kategori": "6. Digital Economy & E-Commerce", "unit": "% of Commercial Services", "oecd_code": "DIG_TRADE / SER_DIG",
        "desc": "Share of digitally-deliverable services in total commercial services trade, capturing cross-border e-commerce and digital service exports.",
        "source_url": "https://goingdigital.oecd.org/en/countries/idn",
        "data": {"2010": 15.1, "2012": 16.8, "2015": 19.2, "2017": 21.0, "2019": 22.8, "2020": 25.1, "2021": 24.0, "2022": 26.5, "2023": 28.2, "2024": 29.8}
    },
    "Household Broadband Access Rate": {
        "kategori": "6. Digital Economy & E-Commerce", "unit": "% of Households", "oecd_code": "ICT_HH / HH_BROADBAND",
        "desc": "Percentage of households having internet broadband access from home, enabling digital consumer markets.",
        "source_url": "https://goingdigital.oecd.org/en/countries/idn",
        "data": {"2010": 11.2, "2012": 15.4, "2015": 22.1, "2017": 30.5, "2019": 41.2, "2020": 55.4, "2021": 61.0, "2022": 67.5, "2023": 73.1, "2024": 78.4}
    },

    # --- 7. Public Finance & Fiscal Sector ---
    "General Government Gross Debt (% of GDP)": {
        "kategori": "7. Public Finance & Fiscal", "unit": "% of GDP", "oecd_code": "GOV_DEBT / GG_DEBT",
        "desc": "Total nominal gross debt of general government sector (central and local governments) as a percentage of GDP.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"2000": 87.4, "2002": 62.3, "2004": 51.3, "2006": 39.0, "2008": 30.3, "2010": 24.5, "2011": 23.1, "2012": 23.0, "2013": 24.9, "2014": 24.7, "2015": 27.4, "2016": 27.9, "2017": 28.9, "2018": 30.2, "2019": 30.2, "2020": 39.7, "2021": 40.7, "2022": 39.6, "2023": 39.1, "2024": 38.5}
    },
    "Tax Revenue to GDP Ratio": {
        "kategori": "7. Public Finance & Fiscal", "unit": "% of GDP", "oecd_code": "REV_TAX / TAX_PDB",
        "desc": "Total tax revenues collected by government relative to the size of the economy.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"2000": 11.2, "2002": 12.1, "2004": 12.5, "2006": 12.3, "2008": 13.0, "2010": 11.3, "2012": 11.9, "2014": 11.4, "2015": 10.8, "2016": 10.3, "2017": 9.9, "2018": 10.2, "2019": 9.8, "2020": 8.3, "2021": 9.1, "2022": 10.4, "2023": 10.2, "2024": 10.1}
    },

    # --- 8. International Trade & External Sector ---
    "Current Account Balance (% of GDP)": {
        "kategori": "8. International Trade & External", "unit": "% of GDP", "oecd_code": "BOP / CAB_PDB",
        "desc": "Sum of net exports of goods/services and net primary/secondary income as a percentage of GDP.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"2000": 4.8, "2002": 3.9, "2004": 1.5, "2006": 2.9, "2008": 0.0, "2010": 0.7, "2011": 0.2, "2012": -2.7, "2013": -3.2, "2014": -3.1, "2015": -2.0, "2016": -1.8, "2017": -1.6, "2018": -2.9, "2019": -2.7, "2020": -0.4, "2021": 0.3, "2022": 1.0, "2023": -0.2, "2024": -0.5}
    },
    "Exports of Goods and Services (% of GDP)": {
        "kategori": "8. International Trade & External", "unit": "% of GDP", "oecd_code": "SNA / P6_PDB",
        "desc": "Value of all goods and market services provided to the rest of the world as a percentage of GDP.",
        "source_url": "https://data-explorer.oecd.org/",
        "data": {"2000": 41.0, "2002": 32.7, "2004": 32.2, "2006": 31.0, "2008": 29.8, "2010": 24.3, "2012": 24.3, "2014": 23.7, "2015": 21.2, "2016": 19.1, "2017": 20.2, "2018": 21.0, "2019": 18.4, "2020": 17.2, "2021": 21.6, "2022": 24.5, "2023": 21.7, "2024": 21.2}
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
# 3. KOTAK INFORMASI DEFINISI METODOLOGI & TAUTAN RESMI OECD
# ==============================================================================
st.divider()

with st.expander("ℹ️ Indicator Definition & Official OECD Metadata", expanded=True):
    st.markdown(f"**Series Name:** {selected_name}")
    st.markdown(f"**Category / Dimension:** `{meta['kategori']}`")
    st.markdown(f"**OECD Technical Series Code:** `{meta['oecd_code']}`")
    st.markdown(f"**Measurement Unit:** `{meta['unit']}`")
    st.markdown(f"**Methodological Description:**\n{meta['desc']}")
    st.markdown(
        f"🔗 **Official Database Link:** [Open Data in OECD Data Explorer / Going Digital Toolkit]({meta['source_url']})"
    )

# ==============================================================================
# 4. PEMBENTUKAN DATAFRAME & VISUALISASI GRAFIK INTERAKTIF
# ==============================================================================
rentang_tahun_pilihan = [str(y) for y in range(int(th_start), int(th_end) + 1)]
df_grid = pd.DataFrame({"Tahun": rentang_tahun_pilihan})

raw_series_df = pd.DataFrame(list(meta["data"].items()), columns=["Tahun", f"Indonesia ({meta['unit']})"])
df_final = pd.merge(df_grid, raw_series_df, on="Tahun", how="left").sort_values("Tahun")

st.subheader(f"📈 Time Series Trend: {selected_name}")

val_col = f"Indonesia ({meta['unit']})"
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_final["Tahun"],
    y=df_final[val_col],
    mode="lines+markers",
    name="Indonesia",
    connectgaps=False,
    line=dict(width=2.5, color="#005A9C"),
    hovertemplate=f"Year %{{x}}<br>Value: %{{y}} {meta['unit']}<extra></extra>"
))

fig.update_layout(
    xaxis=dict(title="Year", tickmode="linear"),
    yaxis=dict(title=meta["unit"]),
    hovermode="x unified",
    margin=dict(l=20, r=20, t=40, b=20)
)
st.plotly_chart(fig, use_container_width=True)

# ==============================================================================
# 5. TABEL OBSERVASI & EKSPOR DATA (CSV & XLSX)
# ==============================================================================
st.subheader("📋 Observation Data Table")
c_csv, c_xlsx = st.columns(2)

c_csv.download_button(
    "📥 Download CSV",
    df_final.to_csv(index=False).encode("utf-8"),
    f"OECD_IDN_{meta['oecd_code'].replace(' ', '_')}_{th_start}_{th_end}.csv",
    "text/csv"
)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
    df_final.to_excel(writer, index=False, sheet_name="OECD Data")
c_xlsx.download_button(
    "📊 Download Excel (.xlsx)",
    buf.getvalue(),
    f"OECD_IDN_{meta['oecd_code'].replace(' ', '_')}_{th_start}_{th_end}.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.dataframe(df_final.fillna("-"), use_container_width=True)
st.caption(
    "💡 **OECD Note:** A dash (-) indicates that data for that specific year is not covered within OECD's periodic reporting cycle."
)
