@st.cache_data(ttl=60)
def get_bps_subjects():
    # Format lengkap endpoint subjek BPS
    url = f"https://webapi.bps.go.id/v1/api/list/model/sub/lang/ind/domain/{DOMAIN}/key/{BPS_APP_ID}/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        res = r.json()
        if res.get("status") == "OK" and len(res.get("data", [])) > 1:
            data_dict = {item["title"]: str(item["sub_id"]) for item in res["data"][1]}
            return data_dict, None
        else:
            # Tampilkan seluruh isi balasan BPS agar terbaca detail kendalanya
            raw_err = res.get("data") or res.get("message") or str(res)
            return {}, f"Respon BPS: {raw_err}"
    except Exception as e:
        return {}, f"Koneksi HTTP gagal: {str(e)}"
