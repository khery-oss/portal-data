import requests
import streamlit as st
import json

st.title("🌡️ CCKP API Format Test")
st.markdown("Mencari format URL yang benar untuk World Bank Climate Knowledge Portal API.")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Semua kemungkinan format URL CCKP berdasarkan dokumentasi publik
CCKP_TESTS = {
    "Format A — 11 parts (tas/suhu)": "https://cckpapi.worldbank.org/cckp/v2/cru-x0.5_timeseries_tas_annual_1901-2022_mean_historical_ensemble_all_p50_mean?_format=json&country=IDN",
    "Format B — 11 parts (pr/hujan)": "https://cckpapi.worldbank.org/cckp/v2/cru-x0.5_timeseries_pr_annual_1901-2022_mean_historical_ensemble_all_p50_mean?_format=json&country=IDN",
    "Format C — climatology tas": "https://cckpapi.worldbank.org/cckp/v2/cru-x0.5_climatology_tas_timeseries_annual_1901-2022_mean_historical_ensemble_all_p50_mean?_format=json&country=IDN",
    "Format D — era5 tas": "https://cckpapi.worldbank.org/cckp/v2/era5_timeseries_tas_annual_1950-2020_mean_historical_ensemble_all_p50_mean?_format=json&country=IDN",
    "Format E — cmip6 projection": "https://cckpapi.worldbank.org/cckp/v2/cmip6_timeseries_tas_annual_2015-2100_mean_ssp245_ensemble_all_p50_mean?_format=json&country=IDN",
    "Format F — cmip6 pr projection": "https://cckpapi.worldbank.org/cckp/v2/cmip6_timeseries_pr_annual_2015-2100_mean_ssp245_ensemble_all_p50_mean?_format=json&country=IDN",
    "Format G — v1 endpoint tas": "https://cckpapi.worldbank.org/cckp/v1/cru-x0.5_timeseries_tas_annual_1901-2022_mean_historical_ensemble_all_p50_mean?_format=json&country=IDN",
    "Format H — 9 parts original": "https://cckpapi.worldbank.org/cckp/v2/cru-x0.5_timeseries_tas_annual_mean_historical_ensemble_all_mean?_format=json&country=IDN",
}

if st.button("🚀 Test Semua Format CCKP", type="primary"):
    for name, url in CCKP_TESTS.items():
        parts = url.split("?")[0].split("/")[-1].split("_")
        st.markdown(f"**{name}** ({len(parts)} parts)")
        try:
            res = requests.get(url, headers=HEADERS, timeout=15)
            if res.status_code == 200:
                try:
                    data = res.json()
                    if data.get("metadata", {}).get("status") == "error":
                        st.warning(f"⚠️ HTTP 200 tapi API error: {data['metadata'].get('message', '')[:200]}")
                        st.caption(f"Format hint: `{data['metadata'].get('format', '')}`")
                    else:
                        st.success(f"✅ HTTP 200 — DATA VALID!")
                        st.json(data)
                except:
                    st.warning(f"⚠️ HTTP 200 tapi response bukan JSON: {res.text[:200]}")
            else:
                st.error(f"❌ HTTP {res.status_code}")
        except Exception as e:
            st.error(f"❌ ERROR: {str(e)[:100]}")
        
        with st.expander("Lihat URL lengkap"):
            st.code(url)
        st.divider()
