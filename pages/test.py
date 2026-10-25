import re
import time
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Tes SITC Comtrade v2", layout="wide")
st.title("Tes katalog dan data komoditas SITC (v2)")

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

KOLOM_DATA = ["period", "flowCode", "cmdCode", "classificationCode",
              "primaryValue", "netWgt", "isReported", "isAggregate"]

if st.button("Jalankan tes", type="primary"):
    # ---- 1. ListofReferences: hanya baris berisi SITC ----
    st.header("1. ListofReferences (baris berisi SITC)")
    r = get(f"{REF}/ListofReferences.json")
    try:
        js = r.json()
        rows = js if isinstance(js, list) else js.get("results", js)
        dfl = pd.DataFrame(rows)
        mask = dfl.astype(str).apply(lambda c: c.str.contains("SITC", case=False)).any(axis=1)
        st.dataframe(dfl[mask], use_container_width=True)
    except Exception as e:
        st.warning(f"Tidak bisa diurai: {type(e).__name__}: {e}")
        st.text(r.text[:500])
    time.sleep(JEDA)

    # ---- 2. Katalog dan data per komoditas ----
    st.header("2. Katalog dan data per komoditas")
    uji = [("S1", 1975), ("S2", 1985), ("SS", 1975)]
    for klas, tahun in uji:
        st.subheader(f"{klas}, tahun {tahun}")
        rr = get(f"{REF}/{klas}.json")
        if rr.status_code != 200:
            st.warning(f"{klas}.json HTTP {rr.status_code}, dilewati.")
            continue
        dfk = pd.DataFrame(rr.json().get("results", []))
        if dfk.empty or "text" not in dfk.columns:
            st.warning("Katalog kosong atau tidak punya kolom 'text'.")
            st.write("Kolom:", list(dfk.columns))
            continue
        st.write("Kolom katalog:", list(dfk.columns))
        if "aggrLevel" in dfk.columns:
            st.write("Sebaran aggrLevel:", dfk["aggrLevel"].value_counts().sort_index().to_dict())
        kolom = [c for c in ["id", "text", "parent", "isLeaf", "aggrLevel"] if c in dfk.columns]
        palm = dfk[dfk["text"].str.contains("palm", case=False, na=False)][kolom].head(6)
        st.write("Entri berisi 'palm':")
        st.dataframe(palm, use_container_width=True)

        kode = []
        if "aggrLevel" in dfk.columns:
            kode += dfk[dfk["aggrLevel"] == 3]["id"].astype(str).head(3).tolist()
        kode += palm["id"].astype(str).head(2).tolist()
        kode = list(dict.fromkeys(kode))
        st.write("Kode yang diuji:", kode)
        if not kode:
            st.warning("Tidak ada kode contoh.")
            continue

        url = f"{DATA}/{klas}?{F}&period={tahun}&cmdCode={','.join(kode)}"
        st.code(url)
        rd = get(url)
        try:
            jd = rd.json()
            data = jd.get("data") or []
            st.write(f"HTTP **{rd.status_code}** | count: **{jd.get('count')}** | "
                     f"baris: **{len(data)}** | error: {jd.get('error')}")
            if data:
                st.dataframe(pd.DataFrame([{k: d.get(k) for k in KOLOM_DATA} for d in data]),
                             use_container_width=True)
            else:
                st.text(rd.text[:300])
        except ValueError:
            st.write(f"HTTP **{rd.status_code}**")
            st.text(rd.text[:300])
        time.sleep(JEDA)
