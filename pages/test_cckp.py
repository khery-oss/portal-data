import requests
import streamlit as st
import json

st.title("🌡️ CCKP API Format Test — Round 4")
st.markdown("Cek endpoint dasar CCKP untuk temukan struktur URL yang benar-benar return data.")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

if st.button("🚀 Jalankan Test", type="primary"):

    # Test 1: Coba endpoint root/index CCKP untuk lihat available endpoints
    st.subheader("1. Root endpoints — cari katalog yang tersedia")
    root_urls = [
        "https://cckpapi.worldbank.org/cckp/v2?_format=json",
        "https://cckpapi.worldbank.org/cckp/v2/index?_format=json",
        "https://cckpapi.worldbank.org/cckp/v2/variables?_format=json",
        "https://cckpapi.worldbank.org/cckp/v2/countries?_format=json",
        "https://cckpapi.worldbank.org/cckp/v2/datasets?_format=json",
        "https://cckpapi.worldbank.org/cckp/v2/indicators?_format=json",
    ]
    for url in root_urls:
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            st.write(f"HTTP {res.status_code}: `{url}`")
            if res.status_code == 200:
                try:
                    d = res.json()
                    st.success("✅ JSON response!")
                    st.json(d if len(str(d)) < 1000 else str(d)[:1000])
                except:
                    st.write(f"Non-JSON: {res.text[:300]}")
        except Exception as e:
            st.error(f"ERROR: {e}")
    st.divider()

    # Test 2: Coba format URL dari dokumentasi GitHub WB resmi
    # https://github.com/worldbank/CCKP
    st.subheader("2. Format URL dari GitHub WB CCKP resmi")
    github_urls = [
        # Format dari notebook contoh WB
        "https://cckpapi.worldbank.org/cckp/v2/cru-x0.5_timeseries_tas_annual_1901-2022_mean_historical_ensemble_all_p50_mean/IDN?_format=json",
        # Versi dengan iso3 di path sebelum parameter
        "https://cckpapi.worldbank.org/cckp/v2/cru-x0.5_timeseries_tas_annual_1901-2020_mean_historical_ensemble_all_p50_mean/IDN?_format=json",
        # Periode berbeda
        "https://cckpapi.worldbank.org/cckp/v2/cru-x0.5_timeseries_tas_annual_1950-2020_mean_historical_ensemble_all_p50_mean/IDN?_format=json",
        # Tanpa period range
        "https://cckpapi.worldbank.org/cckp/v2/cru-x0.5_timeseries_tas_annual_all_mean_historical_ensemble_all_p50_mean/IDN?_format=json",
        # ERA5 format
        "https://cckpapi.worldbank.org/cckp/v2/era5_timeseries_tas_annual_1950-2020_mean_historical_ensemble_all_p50_mean/IDN?_format=json",
    ]
    for url in github_urls:
        try:
            res = requests.get(url, headers=HEADERS, timeout=12)
            if res.status_code == 200:
                d = res.json()
                count = len(d.get("data", []))
                if count > 0:
                    st.success(f"✅ **DATA ADA! {count} points**")
                    st.json(d["data"][:3])
                    st.code(url)
                else:
                    st.write(f"⚠️ HTTP 200 kosong: `{url[-70:]}`")
                    # Tampilkan full response untuk debug
                    st.json(d)
            else:
                st.write(f"HTTP {res.status_code}: `{url[-70:]}`")
        except Exception as e:
            st.error(f"ERROR: {e}")
    st.divider()

    # Test 3: Coba WB climate API yang berbeda sama sekali
    st.subheader("3. API WB Climate alternatif")
    alt_apis = [
        # WB Climate Data API (berbeda dari CCKP)
        "https://climatedata.worldbank.org/api/v1/country/IDN/indicator/tas?_format=json",
        # CCKP lewat path berbeda
        "https://cckpapi.worldbank.org/api/v1/cru-x0.5_timeseries_tas_annual_1901-2022_mean_historical_ensemble_all_p50_mean/IDN?_format=json",
        # World Bank open data untuk climate
        "https://api.worldbank.org/v2/country/IDN/indicator/EN.ATM.CO2E.PC?format=json&per_page=10",
        "https://api.worldbank.org/v2/country/IDN/indicator/AG.LND.PRCP.MM?format=json&per_page=10",
        "https://api.worldbank.org/v2/country/IDN/indicator/EN.CLC.MDAT.ZS?format=json&per_page=10",
    ]
    for url in alt_apis:
        try:
            res = requests.get(url, headers=HEADERS, timeout=12)
            if res.status_code == 200:
                try:
                    d = res.json()
                    # WB API format
                    if isinstance(d, list) and len(d) > 1:
                        records = [i for i in d[1] if i.get("value")]
                        if records:
                            st.success(f"✅ WB API — {len(records)} records: `{url[-60:]}`")
                            st.json(records[:2])
                        else:
                            st.write(f"⚠️ WB API kosong: `{url[-60:]}`")
                    else:
                        count = len(d.get("data", [])) if isinstance(d, dict) else 0
                        if count > 0:
                            st.success(f"✅ {count} data points: `{url[-60:]}`")
                            st.json(d["data"][:2])
                        else:
                            st.write(f"⚠️ HTTP 200 kosong: `{url[-60:]}`")
                except:
                    st.write(f"Non-JSON HTTP 200: {res.text[:200]}")
            else:
                st.write(f"HTTP {res.status_code}: `{url[-60:]}`")
        except Exception as e:
            st.error(f"ERROR: {e}")
