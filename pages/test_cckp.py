import requests
import streamlit as st

st.title("🌡️ CCKP API Format Test — Round 2")
st.markdown("Test geo_code sebagai path parameter, bukan query string.")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# Format hint dari API: /api/v1/{collection}_{type}_{var}_{product}_{agg}_{period}_{percentile}_{scenario}_{model}_{model-calc}_{grid}_{stat}/{geo_code}
# Tapi v2 endpoint pakai 11 parts (tanpa product), jadi:
# {collection}_{type}_{var}_{agg}_{period}_{stat}_{scenario}_{model-type}_{model}_{percentile}_{grid}/{geo_code}

# Geo codes yang mungkin untuk Indonesia
GEO_CODES = ["IDN", "idn", "ID", "360", "Indonesia"]

BASE_URLS = [
    "https://cckpapi.worldbank.org/cckp/v2/cru-x0.5_timeseries_tas_annual_1901-2022_mean_historical_ensemble_all_p50_mean",
    "https://cckpapi.worldbank.org/cckp/v2/cmip6_timeseries_tas_annual_2015-2100_mean_ssp245_ensemble_all_p50_mean",
    "https://cckpapi.worldbank.org/cckp/v2/cru-x0.5_timeseries_pr_annual_1901-2022_mean_historical_ensemble_all_p50_mean",
]

if st.button("🚀 Test Geo Code sebagai Path Parameter", type="primary"):
    for base in BASE_URLS:
        var_name = base.split("_")[2] if "_" in base else base
        st.subheader(f"Base: `...{base[-50:]}`")
        
        for geo in GEO_CODES:
            # Format 1: /{geo_code} di akhir path
            url1 = f"{base}/{geo}?_format=json"
            # Format 2: /{geo_code} + query
            url2 = f"{base}?_format=json&country={geo}"
            # Format 3: /country/{geo_code}
            url3 = f"{base}/country/{geo}?_format=json"

            for label, url in [
                (f"Path /{geo}", url1),
                (f"Query ?country={geo}", url2),
                (f"Path /country/{geo}", url3),
            ]:
                try:
                    res = requests.get(url, headers=HEADERS, timeout=15)
                    if res.status_code == 200:
                        data = res.json()
                        if data.get("metadata", {}).get("status") == "success" and data.get("data"):
                            st.success(f"✅ **DATA ADA!** {label}")
                            st.json({"sample": data["data"][:3], "total": len(data["data"])})
                            st.code(url)
                        elif data.get("metadata", {}).get("status") == "success":
                            st.warning(f"⚠️ Success tapi data kosong — {label}")
                        else:
                            msg = data.get("metadata", {}).get("message", "")
                            st.error(f"❌ API error — {label}: {str(msg)[:100]}")
                    else:
                        st.error(f"❌ HTTP {res.status_code} — {label}")
                except Exception as e:
                    st.error(f"❌ ERROR — {label}: {str(e)[:80]}")
        st.divider()
