import time
import requests
import pandas as pd
import streamlit as st
from collections import Counter

st.set_page_config(page_title="Tes UN SDG", layout="wide")
st.title("Tes struktur API UN SDG")

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept": "application/json"}
BASE = "https://unstats.un.org/sdgapi/v1/sdg"
KODE = ["SL_EMP_PCAP", "NY_GDP_PCAP", "SL_TLF_UEM", "SL_TLF_NEET", "SI_POV_DAY1", "SI_COV_POOR",
        "SI_DST_040P", "NV_IND_MANF", "GB_XPD_RSDV", "EN_ATM_CO2MVA", "EG_FEC_RNEW",
        "EG_EGY_PRIM", "SH_STA_MORT", "SH_DYN_MORT", "SE_PRE_PARTN"]

def get(url):
    r = requests.get(url, headers=H, timeout=40)
    return r

if st.button("Jalankan tes", type="primary"):
    # 1. Daftar seri live
    st.header("1. Series/List")
    r = get(f"{BASE}/Series/List")
    st.write(f"HTTP **{r.status_code}** | {len(r.content):,} byte")
    kode_live = set()
    try:
        js = r.json()
        st.write("Tipe:", type(js).__name__, "| jumlah:", len(js))
        contoh = js[:2] if isinstance(js, list) else str(js)[:400]
        st.json(contoh)
        if isinstance(js, list):
            kode_live = {x.get("code") for x in js if isinstance(x, dict)}
    except Exception as e:
        st.warning(f"{type(e).__name__}: {e}")
        st.text(r.text[:400])

    # 2. Ringkasan 15 kode
    st.header("2. Ringkasan per kode (areaCode=360, pageSize=500)")
    baris, detail = [], {}
    for k in KODE:
        try:
            rr = get(f"{BASE}/Series/Data?seriesCode={k}&areaCode=360&pageSize=500")
            js = rr.json() if rr.status_code == 200 else {}
            data = js.get("data") or []
            dim_keys = Counter()
            sensor = 0
            for d in data:
                for dk in (d.get("dimensions") or {}):
                    dim_keys[dk] += 1
                v = str(d.get("value"))
                if v.startswith("<") or v.startswith(">"):
                    sensor += 1
            baris.append({
                "kode": k, "http": rr.status_code, "ada_di_Series/List": (k in kode_live) if kode_live else "n/a",
                "totalElements": js.get("totalElements"), "totalPages": js.get("totalPages"),
                "baris_halaman_1": len(data), "kunci_dimensi": ",".join(dim_keys), "nilai_sensor": sensor,
                "kunci_respons": ",".join(js.keys())[:80],
            })
            detail[k] = data
        except Exception as e:
            baris.append({"kode": k, "http": f"ERR {type(e).__name__}"})
        time.sleep(1)
    st.dataframe(pd.DataFrame(baris), use_container_width=True)

    # 3. Isi dimensi dan atribut untuk 3 seri representatif
    st.header("3. Nilai dimensi dan atribut")
    for k in ["SL_TLF_UEM", "SI_POV_DAY1", "SL_EMP_PCAP"]:
        data = detail.get(k) or []
        st.subheader(k)
        if not data:
            st.write("Tidak ada data.")
            continue
        dims, attrs = {}, {}
        for d in data:
            for dk, dv in (d.get("dimensions") or {}).items():
                dims.setdefault(dk, Counter())[dv] += 1
            for ak, av in (d.get("attributes") or {}).items():
                attrs.setdefault(ak, Counter())[av] += 1
        st.write("Dimensi:", {dk: dict(c.most_common(8)) for dk, c in dims.items()})
        st.write("Atribut:", {ak: dict(c.most_common(8)) for ak, c in attrs.items()})
        st.write("Kunci satu baris:", list(data[0].keys()))
        st.write("Contoh baris (field kunci):", {x: data[0].get(x) for x in
                 ["geoAreaCode", "timePeriodStart", "value", "series", "seriesDescription"]})
