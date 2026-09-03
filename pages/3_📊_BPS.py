import streamlit as st
import requests

st.title("🔍 Diagnostik Lanjutan WebAPI BPS")

api_key = st.secrets.get("BPS_APP_ID") or st.secrets.get("BPS_API_KEY")

if api_key:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Uji 1: Model 'subject' (Katalog Subjek Resmi BPS)
    url_subject = f"https://webapi.bps.go.id/v1/api/list/model/subject/domain/0000/key/{api_key}/"
    st.subheader("1. Uji Model `subject`")
    try:
        r1 = requests.get(url_subject, headers=headers, timeout=15)
        st.write(f"Status: `{r1.status_code}`")
        st.json(r1.json())
    except Exception as e:
        st.error(f"Gagal uji 1: {e}")

    # Uji 2: Model 'var' (Daftar Variabel Indikator)
    url_var = f"https://webapi.bps.go.id/v1/api/list/model/var/domain/0000/key/{api_key}/"
    st.subheader("2. Uji Model `var`")
    try:
        r2 = requests.get(url_var, headers=headers, timeout=15)
        st.write(f"Status: `{r2.status_code}`")
        st.json(r2.json())
    except Exception as e:
        st.error(f"Gagal uji 2: {e}")
