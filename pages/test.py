import time
import requests
import streamlit as st

st.set_page_config(page_title="Tes BPS WebAPI v3", layout="wide")
st.title("Tes BPS WebAPI v3")

try:
    KEY = st.secrets["BPS_API_KEY"]
except Exception:
    st.error("BPS_API_KEY belum ada di secrets.")
    st.stop()

BASE = "https://webapi.bps.go.id/v1/api/list"
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def panggil(**params):
    try:
        r = requests.get(BASE, params={"key": KEY, **params}, headers=H, timeout=60)
        return r.status_code, r.json()
    except Exception as e:
        return None, {"galat": type(e).__name__}

def semua_halaman(**params):
    kode, js = panggil(page=1, **params)
    d = js.get("data") if isinstance(js, dict) else None
    if kode != 200 or not (isinstance(d, list) and len(d) == 2):
        return kode, js, []
    baris, meta = list(d[1]), d[0]
    for p in range(2, int(meta.get("pages", 1)) + 1):
        time.sleep(0.3)
        k2, j2 = panggil(page=p, **params)
        d2 = j2.get("data") if isinstance(j2, dict) else None
        if k2 != 200 or not (isinstance(d2, list) and len(d2) == 2):
            return k2, j2, baris
        baris.extend(d2[1])
    return kode, js, baris

def petakan(js, var):
    dc = js.get("datacontent")
    dc = dc if isinstance(dc, dict) else {}
    ver = [x["val"] for x in (js.get("vervar") or [])] or [0]
    tur = [x["val"] for x in (js.get("turvar") or [])] or [0]
    th = [x["val"] for x in (js.get("tahun") or [])]
    tt = [x["val"] for x in (js.get("turtahun") or [])] or [0]
    kunci, tabrakan = {}, 0
    for v in ver:
        for t in tur:
            for y in th:
                for z in tt:
                    k = f"{v}{var}{t}{y}{z}"
                    if k in kunci:
                        tabrakan += 1
                    kunci[k] = 1
    cocok = sum(1 for k in dc if k in kunci)
    return (f"vervar {len(js.get('vervar') or [])} turvar {len(js.get('turvar') or [])} "
            f"tahun {len(th)} turtahun {len(js.get('turtahun') or [])} | datacontent {len(dc)} "
            f"cocok {cocok} tak-cocok {len(dc) - cocok} tabrakan {tabrakan}")

def ringkas_data(kode, js):
    if not isinstance(js, dict):
        return f"HTTP {kode}"
    pesan = str(js.get("message") or "")[:90].replace(KEY, "***")
    return f"HTTP {kode} {js.get('status')} {js.get('data-availability') or ''} {pesan}"

if st.button("Jalankan tes", type="primary"):
    st.header("A. Pemetaan dan jumlah periode per variabel")
    var_uji = [70, 182, 195, 198, 42, 53, 58]
    for kata in ("inflasi", "produk domestik bruto"):
        k, js, baris = semua_halaman(model="var", domain="0000", keyword=kata)
        st.text(f"keyword '{kata}': HTTP {k}, {len(baris)} variabel; tiga pertama: {[(b['var_id'], b['title'][:50]) for b in baris[:3]]}")
        var_uji += [b["var_id"] for b in baris[:2]]
        time.sleep(0.3)
    for var in dict.fromkeys(var_uji):
        k, js, baris = semua_halaman(model="th", domain="0000", var=var)
        th_ids = [b["th_id"] for b in baris]
        if not th_ids:
            st.text(f"var {var}: tidak ada periode | {ringkas_data(k, js)}")
            continue
        time.sleep(0.3)
        ka, ja = panggil(model="data", domain="0000", var=var, th=";".join(str(t) for t in th_ids))
        info_a = petakan(ja, var) if ka == 200 and isinstance(ja, dict) and ja.get("datacontent") is not None else ""
        time.sleep(0.3)
        kb, jb = panggil(model="data", domain="0000", var=var, th=f"{min(th_ids)}:{max(th_ids)}")
        dc_b = len(jb.get("datacontent") or {}) if isinstance(jb, dict) else 0
        st.text(f"var {var} | periode {len(th_ids)} ({baris[0]['th']}..{baris[-1]['th']}) | A(;) {ringkas_data(ka, ja)} | {info_a} | B(:) {ringkas_data(kb, jb)} datacontent {dc_b}")
        if isinstance(ja, dict) and ja.get("turtahun"):
            st.text(f"   turtahun: {[x.get('label') for x in ja['turtahun']][:6]} | tahun contoh: {[x.get('label') for x in (ja.get('tahun') or [])][:3]} | unit: {(ja.get('var') or [{}])[0].get('unit')} | decimal: {(ja.get('var') or [{}])[0].get('decimal')} | last_update: {ja.get('last_update')}")
        time.sleep(0.3)

    st.header("B. Penyaringan katalog")
    for label, prm in [
        ("keyword=kemiskinan", dict(keyword="kemiskinan")),
        ("keyword=Kemiskinan", dict(keyword="Kemiskinan")),
        ("keyword=miskin", dict(keyword="miskin")),
        ("keyword=poverty", dict(keyword="poverty")),
        ("subject=23", dict(subject=23)),
        ("subject=23 + keyword=kemiskinan", dict(subject=23, keyword="kemiskinan")),
        ("subject=30 + keyword=kemiskinan", dict(subject=30, keyword="kemiskinan")),
        ("lang=eng keyword=poverty", dict(lang="eng", keyword="poverty")),
    ]:
        k, js = panggil(model="var", domain="0000", page=1, **prm)
        d = js.get("data") if isinstance(js, dict) else None
        if k == 200 and isinstance(d, list) and len(d) == 2:
            st.text(f"{label}: total {d[0].get('total')} | halaman {d[0].get('pages')} | judul pertama: {(d[1][0]['title'][:70] if d[1] else '-')} | sub_id baris: {sorted({r.get('sub_id') for r in d[1]})}")
        else:
            st.text(f"{label}: {ringkas_data(k, js)}")
        time.sleep(0.3)

    st.header("C. Bentuk galat")
    k, js = panggil(model="data", domain="0000", var=70, th=999)
    st.text(f"th=999: {ringkas_data(k, js)} | kunci: {list(js.keys()) if isinstance(js, dict) else ''}")
    time.sleep(0.3)
    k, js = panggil(model="data", domain="0000", var=999999, th=114)
    st.text(f"var=999999: {ringkas_data(k, js)}")
    time.sleep(0.3)
    kode, js = panggil(model="var", domain="0000")
    d = js.get("data") if isinstance(js, dict) else None
    if isinstance(d, list) and len(d) == 2 and d[1]:
        st.text(f"kunci satu baris katalog: {list(d[1][0].keys())}")
