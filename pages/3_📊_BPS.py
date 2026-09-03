import streamlit as st
import requests

st.title("🔍 Diagnostik Langsung WebAPI BPS")

# Cek Secrets
api_key = st.secrets.get("BPS_APP_ID") or st.secrets.get("BPS_API_KEY")
st.write(f"Key ditemukan: `{api_key[:4]}...{api_key[-4:]}`" if api_key else "❌ Key tidak ada di Secrets!")

if api_key:
    # Uji 1: Endpoint List Subjek
    test_url = f"https://webapi.bps.go.id/v1/api/list/model/sub/domain/0000/key/{api_key}/"
    st.write(f"Menguji URL: `{test_url.replace(api_key, 'HIDDEN_KEY')}`")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        r = requests.get(test_url, headers=headers, timeout=15)
        st.write(f"**HTTP Status Code:** `{r.status_code}`")
        st.write("**Respons Mentah (Raw JSON):**")
        st.json(r.json())
    except Exception as e:
        st.error(f"Koneksi gagal total (Network/SSL/Timeout): {e}")
