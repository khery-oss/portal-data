import requests
import streamlit as st

st.title("🔧 API Availability Test")
st.markdown("Test koneksi ke berbagai API dari Streamlit Cloud environment.")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

TESTS = {
    "ADB (Asian Development Bank)": [
        ("ADB KIAPI", "https://kiapi.adb.org/api/v1/indicator/list?format=json"),
        ("ADB Open Data CKAN", "https://data.adb.org/api/3/action/package_list"),
        ("ADB SDMX", "https://adb-sdmxws.adb.org/rest/dataflow/ADB/ADB_QEI/1.0?format=json"),
    ],
    "FAO (Food & Agriculture Organization)": [
        ("FAO FAOSTAT domains", "https://fenix.fao.org/faostat/api/v1/en/groupsanddomains"),
        ("FAO FAOSTAT data IDN", "https://fenix.fao.org/faostat/api/v1/en/data/QCL?area=101&element=5510&item=56&limit=5"),
        ("FAO API v2", "https://faostat.fao.org/api/v1/en/groupsanddomains"),
    ],
    "UNODC (UN Office on Drugs and Crime)": [
        ("UNODC dataunodc", "https://dataunodc.un.org/api/data?indicators=dp_doe_age_sex&countries=IDN&limit=5"),
        ("UNODC SDMX", "https://unodc.org/unodc/en/data-and-analysis/statistics.html"),
    ],
    "World Bank Climate Change (CCKP)": [
        ("CCKP v2 tas", "https://cckpapi.worldbank.org/cckp/v2/cru-x0.5_timeseries_tas_annual_mean_historical_ensemble_all_mean?_format=json&country=IDN"),
        ("CCKP v2 pr", "https://cckpapi.worldbank.org/cckp/v2/cru-x0.5_timeseries_pr_annual_mean_historical_ensemble_all_mean?_format=json&country=IDN"),
        ("CCKP v1", "https://climateknowledgeportal.worldbank.org/api/data/get-download-data/projection/mavg/pr/1991-2020/IDN"),
    ],
    "IMF (International Monetary Fund)": [
        ("IMF DataMapper GDP", "https://www.imf.org/external/datamapper/api/v1/NGDP_RPCH/IDN"),
        ("IMF DataMapper indicators", "https://www.imf.org/external/datamapper/api/v1/indicators"),
        ("IMF SDMX IFS", "https://dataservices.imf.org/REST/SDMX_JSON.svc/GetData/IFS/M.ID.FIMM_PA?startPeriod=2022&endPeriod=2023"),
    ],
}

if st.button("🚀 Jalankan Test Semua API", type="primary"):
    for lembaga, endpoints in TESTS.items():
        st.subheader(f"📡 {lembaga}")
        for name, url in endpoints:
            try:
                res = requests.get(url, headers=HEADERS, timeout=10)
                if res.status_code == 200:
                    st.success(f"✅ **{name}** — HTTP 200 OK")
                    st.caption(f"Sample response: `{res.text[:200]}`")
                else:
                    deny = res.headers.get("x-deny-reason", "-")
                    st.error(f"❌ **{name}** — HTTP {res.status_code} | deny-reason: {deny}")
            except Exception as e:
                st.error(f"❌ **{name}** — ERROR: {str(e)[:100]}")
        st.divider()
