import re
import time
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Tes Referensi SITC Comtrade", layout="wide")
st.title("Tes referensi dan data komoditas SITC (pra-1989)")

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
REF = "https://comtradeapi.un.org/files/v1/app/reference"
DATA = "https://comtradeapi.un.org/public/v1/preview/C/A"
F = "reporterCode=360&partnerCode=0&partner2Code=0&motCode=0&customsCode=C00&flowCode=X,M"
JEDA = 3
MAX_RETRY = 5

def get(url):
    for _ in range(MAX_RETRY):
        r = requests.get(url, headers=H, timeout=60)
        if r.status_code == 429:
            m = re.search(r"in (\d+) second", r.text)
            time.sleep(int(m.group(1)) + 1 if m else 4)
            continue
        return r
    return r

def muat_ref(nama):
    r = get(f"{REF}/{nama}")
    info = {"file": nama, "http": r.status_code, "ukuran": len(r.content)}
    if r.status_code != 200:
        return info, None
    try:
        js = r.json()
    except ValueError:
        info["catatan"] = "bukan JSON: " + r.text[:100]
        return info, None
    if isinstance(js, dict):
        hasil = js.get("results")
        info["classCode"] = js.get("classCode")
        info["className"] = js.get("className")
        if isinstance(hasil, list):
            info["jumlah_entri"] = len(hasil)
            return info, hasil
        info["catatan"] = "kunci: " + str(list(js.keys()))[:150]
    elif isinstance(js, list):
        info["jumlah_entri"] = len(js)
        info["catatan"] = "bentuk daftar"
    return info, None

if st.button("Jalankan tes", type="primary"):
    # ---- Bagian 1: file referensi ----
    st.header("1. File referensi")
    kandidat = ["ListofReferences.json", "S1.json", "S2.json", "S3.json", "S4.json", "SS.json", "SITC.json"]
    katalog = {}
    ringkas = []
    for nama in kandidat:
        info, hasil = muat_ref(nama)
        ringkas.append(info)
        if hasil:
            katalog[nama] = hasil
        time.sleep(JEDA)
    st.dataframe(pd.DataFrame(ringkas), use_container_width=True)

    for nama, hasil in katalog.items():
        st.subheader(f"Isi {nama}")
        dfk = pd.DataFrame(hasil)
        kolom = [c for c in ["id", "text", "parent", "isLeaf", "aggrLevel"] if c in dfk.columns]
        st.write("Sebaran aggrLevel:", dfk["aggrLevel"].value_counts().sort_index().to_dict() if "aggrLevel" in dfk else "tidak ada")
        st.dataframe(dfk[kolom].head(12), use_container_width=True)
        palm = dfk[dfk["text"].str.contains("palm", case=False, na=False)][kolom].head(6)
        st.write("Entri berisi 'palm':")
        st.dataframe(palm, use_container_width=True)

    # ---- Bagian 2: data per komoditas SITC ----
    st.header("2. Data per komoditas SITC")
    uji = [("S1", "S1.json", 1975), ("S2", "S2.json", 1985)]
    for klas, nama_ref, tahun in uji:
        st.subheader(f"{klas}, tahun {tahun}")
        hasil = katalog.get(nama_ref)
        if not hasil:
            st.warning(f"{nama_ref} tidak tersedia, tes data {klas} dilewati.")
            continue
        dfk = pd.DataFrame(hasil)
        kode = []
        if "aggrLevel" in dfk:
            kode += dfk[dfk["aggrLevel"] == 3]["id"].astype(str).head(3).tolist()
        kode += dfk[dfk["text"].str.contains("palm", case=False, na=False)]["id"].astype(str).head(2).tolist()
        kode = list(dict.fromkeys(kode))
        st.write("Kode yang diuji:", kode)
        if not kode:
            st.warning("Tidak ada kode contoh yang bisa dipilih.")
            continue
        url = f"{DATA}/{klas}?{F}&period={tahun}&cmdCode={','.join(kode)}"
        st.code(url)
        r = get(url)
        try:
            js = r.json()
            data = js.get("data") or []
            st.write(f"HTTP **{r.status_code}** | count: **{js.get('count')}** | baris: **{len(data)}** | error: {js.get('error')}")
            if data:
                st.dataframe(pd.DataFrame([{k: d.get(k) for k in
                    ["period", "flowCode", "cmdCode", "classificationCode",
                     "primaryValue", "netWgt", "isReported", "isAggregate"]} for d in data]),
                    use_container_width=True)
            else:
                st.text(r.text[:300])
        except ValueError:
            st.write(f"HTTP **{r.status_code}**")
            st.text(r.text[:300])
        time.sleep(JEDA)
