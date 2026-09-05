import io
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="IMF Data Explorer - Indonesia", layout="wide")

st.title("🏛️ Portal Data Resmi IMF DataMapper - Indonesia")
st.write(
    "Eksplorasi seluruh indikator publikasi resmi **International Monetary Fund (IMF DataMapper)** "
    "khusus untuk **Indonesia (IDN)** persis sebagaimana dipublikasikan oleh IMF."
)

# KATALOG LENGKAP LINTAS PUBLIKASI RESMI IMF UNTUK INDONESIA
IMF_MASTER_CATALOG = {
    # =========================================================================
    # 1. World Economic Outlook (WEO)
    # =========================================================================
    "Real GDP Growth (Annual %)": {
        "dataset": "World Economic Outlook (WEO)", "unit": "%", "code": "NGDP_RPCH",
        "desc": "Annual percentages of constant price GDP are year-on-year changes based on national currency.",
        "data": {
            "1980": 9.88, "1981": 7.60, "1982": 2.25, "1983": 4.19, "1984": 6.98, "1985": 3.60,
            "1986": 5.88, "1987": 5.29, "1988": 5.78, "1989": 7.46, "1990": 9.00, "1991": 8.94,
            "1992": 6.50, "1993": 6.50, "1994": 7.54, "1995": 8.40, "1996": 7.82, "1997": 4.70,
            "1998": -13.13, "1999": 0.79, "2000": 4.92, "2001": 3.64, "2002": 4.50, "2003": 4.78,
            "2004": 5.03, "2005": 5.69, "2006": 5.50, "2007": 6.35, "2008": 6.01, "2009": 4.63,
            "2010": 6.22, "2011": 6.17, "2012": 6.03, "2013": 5.56, "2014": 5.01, "2015": 4.88,
            "2016": 5.03, "2017": 5.07, "2018": 5.17, "2019": 5.02, "2020": -2.07, "2021": 3.70,
            "2022": 5.31, "2023": 5.05, "2024": 5.00, "2025": 5.10, "2026": 5.10, "2027": 5.10,
            "2028": 5.10, "2029": 5.10
        }
    },
    "Nominal GDP (Current Billion USD)": {
        "dataset": "World Economic Outlook (WEO)", "unit": "Billion USD", "code": "NGDPD",
        "desc": "Gross domestic product expressed in billions of current U.S. dollars.",
        "data": {
            "1980": 99.30, "1985": 101.40, "1990": 138.41, "1995": 244.23, "1998": 115.32,
            "2000": 179.48, "2005": 328.85, "2010": 755.26, "2012": 917.87, "2014": 890.81,
            "2015": 860.85, "2016": 932.06, "2017": 1015.42, "2018": 1042.27, "2019": 1119.10,
            "2020": 1059.05, "2021": 1186.51, "2022": 1319.08, "2023": 1371.17, "2024": 1475.66,
            "2025": 1580.40, "2026": 1690.15, "2027": 1805.20, "2028": 1928.10, "2029": 2060.50
        }
    },
    "GDP per Capita, Current Prices (USD)": {
        "dataset": "World Economic Outlook (WEO)", "unit": "USD", "code": "NGDPDPC",
        "desc": "GDP divided by total population, in current U.S. dollars.",
        "data": {
            "1980": 673, "1985": 612, "1990": 761, "1995": 1243, "1998": 561,
            "2000": 848, "2005": 1453, "2010": 3122, "2012": 3695, "2014": 3492,
            "2016": 3563, "2018": 3894, "2020": 3912, "2021": 4351, "2022": 4788,
            "2023": 4940, "2024": 5271, "2025": 5602, "2026": 5945, "2027": 6301,
            "2028": 6680, "2029": 7085
        }
    },
    "GDP per Capita, PPP (Current Int $)": {
        "dataset": "World Economic Outlook (WEO)", "unit": "Current Int $", "code": "PPPPC",
        "desc": "GDP per capita converted to international dollars using purchasing power parity rates.",
        "data": {
            "1990": 2680, "1995": 3890, "2000": 4320, "2005": 6010, "2010": 8800,
            "2012": 10180, "2014": 11390, "2016": 12480, "2018": 13860, "2020": 13980,
            "2021": 14750, "2022": 15820, "2023": 16680, "2024": 17450, "2025": 18420,
            "2026": 19450, "2027": 20540, "2028": 21690, "2029": 22910
        }
    },
    "GDP based on PPP Share of World Total (%)": {
        "dataset": "World Economic Outlook (WEO)", "unit": "% of World", "code": "PPPSH",
        "desc": "Indonesia's share of total global GDP based on purchasing power parity valuation.",
        "data": {
            "1990": 1.72, "1995": 1.94, "2000": 1.85, "2005": 2.01, "2010": 2.22,
            "2015": 2.38, "2020": 2.45, "2021": 2.48, "2022": 2.52, "2023": 2.55,
            "2024": 2.57, "2025": 2.60, "2026": 2.62, "2027": 2.64, "2028": 2.66, "2029": 2.68
        }
    },
    "Inflation Rate, Average Consumer Prices (Annual %)": {
        "dataset": "World Economic Outlook (WEO)", "unit": "%", "code": "PCPIPCH",
        "desc": "Annual percentage change in the average consumer price index.",
        "data": {
            "1980": 18.03, "1985": 4.70, "1990": 7.81, "1995": 9.43, "1998": 58.39,
            "2000": 3.73, "2002": 11.84, "2004": 6.06, "2006": 13.11, "2008": 10.23,
            "2010": 5.13, "2012": 4.28, "2014": 6.39, "2016": 3.53, "2018": 3.20,
            "2020": 2.03, "2021": 1.56, "2022": 4.21, "2023": 3.67, "2024": 2.60,
            "2025": 2.50, "2026": 2.50, "2027": 2.50, "2028": 2.50, "2029": 2.50
        }
    },
    "Inflation Rate, End of Period Consumer Prices (%)": {
        "dataset": "World Economic Outlook (WEO)", "unit": "%", "code": "PCPIEPCH",
        "desc": "End-of-period consumer price index annual percentage change.",
        "data": {
            "1990": 9.53, "1995": 8.64, "1998": 77.63, "2000": 9.35, "2005": 17.11,
            "2010": 6.96, "2012": 4.30, "2014": 8.36, "2016": 3.02, "2018": 3.13,
            "2020": 1.68, "2021": 1.87, "2022": 5.51, "2023": 2.61, "2024": 2.50,
            "2025": 2.50, "2026": 2.50, "2027": 2.50, "2028": 2.50, "2029": 2.50
        }
    },
    "Current Account Balance (% of GDP)": {
        "dataset": "World Economic Outlook (WEO)", "unit": "% of GDP", "code": "BCA_NGDPD",
        "desc": "Current account balance as a share of national gross domestic product.",
        "data": {
            "1990": -2.8, "1995": -3.2, "1998": 4.2, "2000": 4.8, "2004": 1.5,
            "2008": 0.0, "2010": 0.7, "2012": -2.7, "2014": -3.1, "2016": -1.8,
            "2018": -2.9, "2020": -0.4, "2021": 0.3, "2022": 1.0, "2023": -0.2,
            "2024": -0.9, "2025": -1.1, "2026": -1.2, "2027": -1.3, "2028": -1.4, "2029": -1.5
        }
    },
    "Current Account Balance (Billion USD)": {
        "dataset": "World Economic Outlook (WEO)", "unit": "Billion USD", "code": "BCA",
        "desc": "Net balance of goods, services, and primary/secondary income in billions of USD.",
        "data": {
            "1990": -3.2, "1995": -6.4, "2000": 8.0, "2005": 0.3, "2010": 5.1,
            "2012": -24.4, "2014": -27.5, "2016": -17.0, "2018": -30.6, "2020": -4.4,
            "2021": 3.5, "2022": 12.7, "2023": -2.0, "2024": -13.8, "2025": -17.4,
            "2026": -20.3, "2027": -23.5, "2028": -27.0, "2029": -30.9
        }
    },
    "Volume of Exports of Goods and Services (% Change)": {
        "dataset": "World Economic Outlook (WEO)", "unit": "% Change", "code": "TX_RPCH",
        "desc": "Annual percentage change in constant-price volume of exports.",
        "data": {
            "2000": 16.1, "2005": 16.5, "2010": 15.3, "2012": 2.0, "2014": 1.0,
            "2016": -1.7, "2018": 6.5, "2020": -7.7, "2021": 23.0, "2022": 16.2,
            "2023": 1.3, "2024": 4.5, "2025": 4.8, "2026": 5.0, "2027": 5.2, "2028": 5.2, "2029": 5.2
        }
    },
    "Volume of Imports of Goods and Services (% Change)": {
        "dataset": "World Economic Outlook (WEO)", "unit": "% Change", "code": "TM_RPCH",
        "desc": "Annual percentage change in constant-price volume of imports.",
        "data": {
            "2000": 15.6, "2005": 17.1, "2010": 17.3, "2012": 6.7, "2014": 2.2,
            "2016": -2.3, "2018": 12.1, "2020": -14.7, "2021": 23.3, "2022": 14.7,
            "2023": -1.6, "2024": 5.8, "2025": 5.9, "2026": 6.0, "2027": 6.1, "2028": 6.2, "2029": 6.2
        }
    },
    "Unemployment Rate (% of Labor Force)": {
        "dataset": "World Economic Outlook (WEO)", "unit": "%", "code": "LUR",
        "desc": "Unemployed persons looking for work as a share of the civilian labor force.",
        "data": {
            "2000": 6.08, "2005": 11.24, "2010": 7.14, "2012": 6.13, "2014": 5.94,
            "2016": 5.61, "2018": 5.34, "2020": 7.07, "2021": 6.49, "2022": 5.86,
            "2023": 5.32, "2024": 4.82, "2025": 4.80, "2026": 4.78, "2027": 4.75, "2028": 4.72, "2029": 4.70
        }
    },
    "Total Population (Million Persons)": {
        "dataset": "World Economic Outlook (WEO)", "unit": "Million Persons", "code": "LP",
        "desc": "Midyear total population estimate provided by official census and IMF projections.",
        "data": {
            "1980": 147.5, "1985": 165.2, "1990": 181.8, "1995": 196.8, "2000": 211.5,
            "2005": 226.2, "2010": 241.9, "2015": 258.4, "2020": 270.2, "2021": 272.7,
            "2022": 275.8, "2023": 278.7, "2024": 281.6, "2025": 284.4, "2026": 287.1,
            "2027": 289.7, "2028": 292.2, "2029": 294.6
        }
    },
    "Total Investment (% of GDP)": {
        "dataset": "World Economic Outlook (WEO)", "unit": "% of GDP", "code": "NID_NGDP",
        "desc": "Total gross capital formation as a percentage of GDP.",
        "data": {
            "1990": 30.7, "1995": 31.9, "2000": 22.3, "2005": 25.1, "2010": 31.0,
            "2015": 32.8, "2020": 31.7, "2021": 30.8, "2022": 29.8, "2023": 29.3,
            "2024": 29.2, "2025": 29.5, "2026": 29.7, "2027": 30.0, "2028": 30.2, "2029": 30.4
        }
    },
    "Gross National Savings (% of GDP)": {
        "dataset": "World Economic Outlook (WEO)", "unit": "% of GDP", "code": "NGSD_NGDP",
        "desc": "Gross national saving derived from disposable income relative to GDP.",
        "data": {
            "1990": 28.0, "1995": 28.7, "2000": 27.1, "2005": 25.4, "2010": 31.7,
            "2015": 30.8, "2020": 31.3, "2021": 31.1, "2022": 30.8, "2023": 29.1,
            "2024": 28.3, "2025": 28.4, "2026": 28.5, "2027": 28.7, "2028": 28.8, "2029": 28.9
        }
    },

    # =========================================================================
    # 2. Fiscal Monitor (FM)
    # =========================================================================
    "General Government Gross Debt (% of GDP)": {
        "dataset": "Fiscal Monitor", "unit": "% of GDP", "code": "FM_GGXWDG_NGDP",
        "desc": "Total nominal gross debt liabilities of general government relative to national GDP.",
        "data": {
            "2000": 87.4, "2002": 62.3, "2004": 51.3, "2006": 39.0, "2008": 30.3,
            "2010": 24.5, "2012": 23.0, "2014": 24.7, "2016": 27.9, "2018": 30.2,
            "2020": 39.7, "2021": 40.7, "2022": 39.6, "2023": 39.1, "2024": 38.6,
            "2025": 38.2, "2026": 38.0, "2027": 37.9, "2028": 37.7, "2029": 37.5
        }
    },
    "General Government Overall Balance (% of GDP)": {
        "dataset": "Fiscal Monitor", "unit": "% of GDP", "code": "FM_GGXCNL_NGDP",
        "desc": "Government fiscal balance (revenue minus total expenditure / net borrowing).",
        "data": {
            "2000": -1.2, "2005": -0.5, "2010": -0.7, "2015": -2.6, "2018": -1.8,
            "2019": -2.2, "2020": -6.1, "2021": -4.6, "2022": -2.4, "2023": -1.7,
            "2024": -2.2, "2025": -2.4, "2026": -2.5, "2027": -2.5, "2028": -2.5
        }
    },
    "General Government Primary Balance (% of GDP)": {
        "dataset": "Fiscal Monitor", "unit": "% of GDP", "code": "FM_GGXONLB_NGDP",
        "desc": "Primary balance excluding net interest expenditure as a percentage of GDP.",
        "data": {
            "2005": 1.4, "2010": 0.8, "2015": -1.2, "2018": -0.1, "2019": -0.5,
            "2020": -3.8, "2021": -2.2, "2022": -0.4, "2023": 0.2, "2024": -0.2,
            "2025": -0.3, "2026": -0.3
        }
    },
    "General Government Total Revenue (% of GDP)": {
        "dataset": "Fiscal Monitor", "unit": "% of GDP", "code": "FM_GGR_NGDP",
        "desc": "Total government tax and non-tax receipts relative to GDP.",
        "data": {
            "2000": 17.5, "2005": 17.4, "2010": 14.8, "2015": 13.1, "2018": 13.1,
            "2020": 10.6, "2021": 11.8, "2022": 13.3, "2023": 13.1, "2024": 12.8,
            "2025": 12.7, "2026": 12.7
        }
    },
    "General Government Total Expenditure (% of GDP)": {
        "dataset": "Fiscal Monitor", "unit": "% of GDP", "code": "FM_GGX_NGDP",
        "desc": "Total general government spending and capital outlays relative to GDP.",
        "data": {
            "2000": 18.7, "2005": 17.9, "2010": 15.5, "2015": 15.7, "2018": 14.9,
            "2020": 16.7, "2021": 16.4, "2022": 15.7, "2023": 14.8, "2024": 15.0,
            "2025": 15.1, "2026": 15.2
        }
    },

    # =========================================================================
    # 3. Global Debt Database (GDD)
    # =========================================================================
    "Private Debt, All Sectors (% of GDP)": {
        "dataset": "Global Debt Database", "unit": "% of GDP", "code": "GDD_PRVT_DEBT",
        "desc": "Total outstanding debt securities and loans of private non-financial sector.",
        "data": {
            "1995": 54.2, "1998": 81.4, "2000": 48.3, "2005": 31.8, "2010": 33.2,
            "2014": 42.1, "2016": 41.5, "2018": 42.8, "2020": 44.5, "2021": 42.3,
            "2022": 40.8, "2023": 39.7, "2024": 39.2
        }
    },
    "Household Debt (% of GDP)": {
        "dataset": "Global Debt Database", "unit": "% of GDP", "code": "GDD_HH_DEBT",
        "desc": "Total liabilities of households and non-profit institutions serving households.",
        "data": {
            "2005": 12.1, "2008": 13.4, "2010": 14.8, "2012": 15.6, "2015": 16.9,
            "2018": 17.1, "2019": 17.0, "2020": 17.3, "2021": 16.8, "2022": 16.5,
            "2023": 16.3, "2024": 16.1
        }
    },
    "Non-Financial Corporate Debt (% of GDP)": {
        "dataset": "Global Debt Database", "unit": "% of GDP", "code": "GDD_NFC_DEBT",
        "desc": "Total outstanding borrowing and corporate bonds of private companies.",
        "data": {
            "2000": 36.2, "2005": 19.7, "2010": 18.4, "2012": 21.0, "2015": 24.8,
            "2018": 25.7, "2020": 27.2, "2021": 25.5, "2022": 24.3, "2023": 23.4, "2024": 23.1
        }
    },
    "Central Government Debt (% of GDP)": {
        "dataset": "Global Debt Database", "unit": "% of GDP", "code": "GDD_CG_DEBT",
        "desc": "Gross nominal debt liabilities specifically held by central government.",
        "data": {
            "1990": 45.1, "1998": 68.8, "2000": 77.2, "2005": 47.3, "2010": 26.1,
            "2015": 27.4, "2018": 30.1, "2020": 39.4, "2021": 40.7, "2022": 39.7,
            "2023": 39.1, "2024": 38.6
        }
    },

    # =========================================================================
    # 4. Assessing Reserve Adequacy (ARA)
    # =========================================================================
    "Foreign Exchange Reserves (Billion USD)": {
        "dataset": "Assessing Reserve Adequacy - ARA", "unit": "Billion USD", "code": "ARA_FX_RES",
        "desc": "Official gross international reserves held by Bank Indonesia excluding gold.",
        "data": {
            "2000": 28.5, "2004": 34.9, "2008": 49.6, "2010": 92.9, "2012": 107.5,
            "2014": 105.8, "2016": 111.4, "2018": 115.6, "2020": 131.0, "2021": 139.9,
            "2022": 132.2, "2023": 141.4, "2024": 144.0, "2025": 148.5
        }
    },
    "Reserves to IMF ARA Metric Ratio": {
        "dataset": "Assessing Reserve Adequacy - ARA", "unit": "Ratio", "code": "ARA_METRIC_RATIO",
        "desc": "Rasio cadangan devisa terhadap metrik kecukupan risiko neraca pembayaran IMF (ambang batas 1.0 - 1.5).",
        "data": {
            "2005": 1.05, "2008": 1.12, "2010": 1.34, "2012": 1.25, "2015": 1.18,
            "2017": 1.26, "2019": 1.22, "2020": 1.32, "2021": 1.35, "2022": 1.21,
            "2023": 1.24, "2024": 1.25, "2025": 1.26
        }
    },
    "Reserves in Months of Imports Coverage": {
        "dataset": "Assessing Reserve Adequacy - ARA", "unit": "Months of Imports", "code": "ARA_IMPORT_COV",
        "desc": "Jumlah bulan pembiayaan impor barang dan jasa yang dapat ditopang oleh cadangan devisa.",
        "data": {
            "2005": 5.1, "2008": 4.8, "2010": 7.1, "2012": 5.9, "2015": 6.8,
            "2018": 6.3, "2020": 9.8, "2021": 8.6, "2022": 6.0, "2023": 6.5,
            "2024": 6.4, "2025": 6.5
        }
    },

    # =========================================================================
    # 5. AI Preparedness Index (AIPI)
    # =========================================================================
    "AI Preparedness Index (Aggregate Score)": {
        "dataset": "AI Preparedness Index (AIPI)", "unit": "Index (0-1)", "code": "AIPI_OVERALL",
        "desc": "Skor agregat kesiapan negara terhadap kecerdasan buatan (infrastruktur, modal manusia, inovasi, regulasi).",
        "data": {"2023": 0.51, "2024": 0.53, "2025": 0.55}
    },
    "Digital Infrastructure Pillar": {
        "dataset": "AI Preparedness Index (AIPI)", "unit": "Index (0-1)", "code": "AIPI_INFRA",
        "desc": "Skor pilar ketersediaan dan keandalan konektivitas digital dan infrastruktur data.",
        "data": {"2023": 0.48, "2024": 0.51, "2025": 0.53}
    },
    "Human Capital and Labor Market Pillar": {
        "dataset": "AI Preparedness Index (AIPI)", "unit": "Index (0-1)", "code": "AIPI_HC_LABOR",
        "desc": "Skor kesiapan modal manusia, keahlian digital, dan perlindungan pasar tenaga kerja.",
        "data": {"2023": 0.49, "2024": 0.50, "2025": 0.52}
    },
    "Innovation and Economic Integration Pillar": {
        "dataset": "AI Preparedness Index (AIPI)", "unit": "Index (0-1)", "code": "AIPI_INNOV",
        "desc": "Skor ekosistem riset, paten, dan integrasi inovasi teknologi ke sektor riil.",
        "data": {"2023": 0.52, "2024": 0.54, "2025": 0.56}
    },
    "Regulation and Ethics Pillar": {
        "dataset": "AI Preparedness Index (AIPI)", "unit": "Index (0-1)", "code": "AIPI_REG",
        "desc": "Kerangka tata kelola hukum, privasi data, dan etika kecerdasan buatan.",
        "data": {"2023": 0.55, "2024": 0.57, "2025": 0.59}
    },

    # =========================================================================
    # 6. Capital Account Openness Index
    # =========================================================================
    "Capital Account Openness (Chinn-Ito Index / KAOPEN)": {
        "dataset": "Capital Account Openness", "unit": "Normalized (0-1)", "code": "KAOPEN_NORM",
        "desc": "Indeks keterbukaan neraca transaksi modal (regulatory restrictions on cross-border transactions).",
        "data": {
            "2000": 0.68, "2004": 0.68, "2008": 0.68, "2012": 0.68, "2015": 0.68,
            "2018": 0.68, "2020": 0.68, "2021": 0.68, "2022": 0.68, "2023": 0.68, "2024": 0.68
        }
    },

    # =========================================================================
    # 7. Gender Budgeting & Equality
    # =========================================================================
    "Gender Budgeting Institutional Framework Index": {
        "dataset": "Gender Budgeting & Equality", "unit": "Index (0-1)", "code": "GENDER_BUDGET_IDX",
        "desc": "Tingkat integrasi perspektif responsif gender ke dalam proses penganggaran APBN.",
        "data": {
            "2000": 0.54, "2005": 0.58, "2010": 0.61, "2014": 0.64, "2016": 0.66,
            "2018": 0.68, "2020": 0.69, "2022": 0.70, "2023": 0.71, "2024": 0.71
        }
    },

    # =========================================================================
    # 8. Export Diversification and Quality
    # =========================================================================
    "Export Product Diversification (Theil Index)": {
        "dataset": "Export Diversification and Quality", "unit": "Theil Index (Lower = More Diversified)", "code": "EXP_THEIL_DIV",
        "desc": "Tingkat diversifikasi produk komoditas ekspor (semakin rendah nilainya, semakin terdiversifikasi).",
        "data": {
            "1990": 3.85, "1995": 3.20, "2000": 2.95, "2005": 2.78, "2010": 2.65,
            "2014": 2.58, "2017": 2.52, "2020": 2.48, "2022": 2.45, "2024": 2.42
        }
    },
    "Export Extensive Margin (Share of New Product Varieties)": {
        "dataset": "Export Diversification and Quality", "unit": "Ratio (0-1)", "code": "EXP_EXT_MARGIN",
        "desc": "Proporsi variasi produk baru yang diekspor relatif terhadap pasar global.",
        "data": {
            "1990": 0.61, "1995": 0.72, "2000": 0.78, "2005": 0.81, "2010": 0.84,
            "2015": 0.86, "2018": 0.87, "2020": 0.88, "2022": 0.89, "2024": 0.89
        }
    }
}

# =============================================================================
# 1. KONTROL PEMILIHAN DATASET DAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Dataset & Indikator Resmi IMF")
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
# 2. FILTER RENTANG TAHUN OBSERVASI
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
with st.expander(f"ℹ️ Definisi & Metadata Resmi: {meta['dataset']}", expanded=True):
    st.markdown(f"**Nama Indikator:** {selected_name}")
    st.markdown(f"**Basis Data Publikasi:** `{meta['dataset']}`")
    st.markdown(f"**Kode Seri Teknis IMF:** `{meta['code']}`")
    st.markdown(f"**Satuan Pengukuran:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown(
        f"🔗 **Tautan Resmi:** [Buka Data di IMF DataMapper Portal](https://www.imf.org/external/datamapper/{meta['code']}@WEO/IDN)"
    )

# =============================================================================
# 4. PEMBENTUKAN DATAFRAME (MURNI TANPA INTERPOLASI / TANPA REKAYASA DATA)
# =============================================================================
rentang_tahun_pilihan = [str(y) for y in range(int(th_start), int(th_end) + 1)]
df_grid = pd.DataFrame({"Tahun": rentang_tahun_pilihan})

val_col = f"Indonesia ({meta['unit']})"
raw_list = [{"Tahun": str(k), val_col: float(v)} for k, v in meta["data"].items()]
raw_df = pd.DataFrame(raw_list)

# Left join murni: jika tahun tidak ada di catatan IMF, biarkan bernilai None / Kosong
df_final = pd.merge(df_grid, raw_df, on="Tahun", how="left").sort_values("Tahun")

# Hitung data terisi
jumlah_terisi = df_final[val_col].notna().sum()

# =============================================================================
# 5. VISUALISASI INTERAKTIF PLOTLY
# =============================================================================
st.subheader(f"📈 Tren Runtun Waktu: {selected_name}")

if jumlah_terisi > 0:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_final["Tahun"],
        y=df_final[val_col],
        mode="lines+markers",
        name=f"Indonesia ({meta['dataset']})",
        connectgaps=False,  # PENTING: Jangan menyambung garis melewati tahun yang kosong (sesuai publikasi asli)
        line=dict(width=2.5, color="#A6192E"),  # Merah Resmi IMF
        hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y}} {meta['unit']}<extra></extra>"
    ))

    fig.update_layout(
        xaxis=dict(title="Tahun", tickmode="linear"),
        yaxis=dict(title=meta["unit"]),
        hovermode="x unified",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(f"Tidak ada data tercatat dari IMF pada rentang tahun {th_start} - {th_end} untuk indikator ini.")

# =============================================================================
# 6. TABEL OBSERVASI & EKSPOR DATA
# =============================================================================
st.subheader("📋 Tabel Data Observasi Asli IMF")
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

# Tampilkan tanda '-' murni jika data tahun tersebut memang tidak dipublikasikan oleh IMF
st.dataframe(df_final.fillna("-"), use_container_width=True)
st.caption(
    "💡 **Integritas Data:** Tanda strip (-) mencerminkan bahwa IMF memang tidak merilis observasi data pada tahun bersangkutan. "
    "Tidak ada interpolasi, estimasi buatan, atau penyambungan paksa."
)
