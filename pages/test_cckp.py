import requests
import streamlit as st

st.title("🌡️ CCKP API Format Test — Round 3")
st.markdown("Cek struktur data tanpa filter negara dulu.")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

BASE = "https://cckpapi.worldbank.org/cckp/v2/cru-x0.5_timeseries_tas_annual_1901-2022_mean_historical_ensemble_all_p50_mean"

if st.button("🚀 Jalankan Test", type="primary"):

    # Test 1: Tanpa filter sama sekali — lihat struktur data mentah
    st.subheader("1. Tanpa filter — lihat data apa yang ada")
    url = f"{BASE}?_format=json"
    res = requests.get(url, headers=HEADERS, timeout=20)
    data = res.json()
    st.write(f"Total data points: {len(data.get('data', []))}")
    if data.get("data"):
        st.write("Sample 3 baris pertama:")
        st.json(data["data"][:3])
        st.write("Keys di setiap baris:")
        st.write(list(data["data"][0].keys()) if data["data"] else "kosong")
    else:
        st.warning("Data masih kosong tanpa filter juga")
    st.divider()

    # Test 2: Coba dengan iso parameter
    st.subheader("2. Berbagai parameter filter lain")
    params_tests = [
        {"iso": "IDN"},
        {"iso3": "IDN"},
        {"iso2": "ID"},
        {"location": "IDN"},
        {"region": "IDN"},
        {"geographyId": "IDN"},
        {"geography": "IDN"},
        {"areaCode": "IDN"},
    ]
    for params in params_tests:
        key = list(params.keys())[0]
        val = list(params.values())[0]
        try:
            res2 = requests.get(f"{BASE}?_format=json", params=params, headers=HEADERS, timeout=10)
            d2 = res2.json()
            count = len(d2.get("data", []))
            if count > 0:
                st.success(f"✅ **{key}={val}** → {count} data points!")
                st.json(d2["data"][:2])
            else:
                st.write(f"⚠️ {key}={val} → kosong")
        except Exception as e:
            st.error(f"❌ {key}={val} → {e}")
    st.divider()

    # Test 3: Coba endpoint yang berbeda — mungkin ada endpoint khusus per negara
    st.subheader("3. Endpoint alternatif per negara")
    alt_urls = [
        f"https://cckpapi.worldbank.org/cckp/v2/IDN/cru-x0.5_timeseries_tas_annual_1901-2022_mean_historical_ensemble_all_p50_mean?_format=json",
        f"https://cckpapi.worldbank.org/cckp/v2/country/IDN/cru-x0.5_timeseries_tas?_format=json",
        f"https://cckpapi.worldbank.org/cckp/v2/cru-x0.5_timeseries_tas_annual_1901-2022_mean_historical_ensemble_all_p50_mean/IDN?_format=json",
        f"https://cckpapi.worldbank.org/cckp/v2/countries/IDN/indicators/tas?_format=json",
    ]
    for url in alt_urls:
        try:
            res3 = requests.get(url, headers=HEADERS, timeout=10)
            d3 = res3.json() if res3.status_code == 200 else {}
            count = len(d3.get("data", []))
            if res3.status_code == 200 and count > 0:
                st.success(f"✅ DATA ADA! {url[-60:]}")
                st.json(d3["data"][:2])
            else:
                st.write(f"HTTP {res3.status_code} — kosong: `{url[-60:]}`")
        except Exception as e:
            st.error(f"❌ {url[-60:]}: {e}")
