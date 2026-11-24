import time
from collections import Counter
import requests
import streamlit as st

st.set_page_config(page_title="Tes BPS WebAPI v4", layout="wide")
st.title("Tes BPS WebAPI v4")

try:
    KEY = st.secrets["BPS_API_KEY"]
except Exception:
    st.error("BPS_API_KEY belum ada di secrets.")
    st.stop()

BASE = "https://webapi.bps.go.id/v1/api/list"
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
LOG429 = []

def panggil(**params):
    for _ in range(6):
        try:
            r = requests.get(BASE, params={"key": KEY, **params}, headers=H, timeout=60)
            js = r.json()
        except Exception as e:
            return None, {"galat": type(e).__name__}
        if r.status_code == 429 and isinstance(js, dict):
            LOG429.append({k: js.get(k) for k in ("code", "retry_after", "message")})
            time.sleep(float(js.get("retry_after") or 5) + 0.5)
            continue
        return r.status_code, js
    return 429, {"message": "429 berulang"}

def halaman(**params):
    kode, js = panggil(page=1, **params)
    d = js.get("data") if isinstance(js, dict) else None
    if kode != 200 or not (isinstance(d, list) and len(d) == 2):
        return kode, js, [], None
    baris, meta = list(d[1]), d[0]
    for p in range(2, int(meta.get("pages", 1)) + 1):
        time.sleep(0.6)
        k2, j2 = panggil(page=p, **params)
        d2 = j2.get("data") if isinstance(j2, dict) else None
        if k2 != 200 or not (isinstance(d2, list) and len(d2) == 2):
            return k2, j2, baris, meta
        baris.extend(d2[1])
    return kode, js, baris, meta

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
                    tabrakan += k in kunci
                    kunci[k] = 1
    cocok = sum(1 for k in dc if k in kunci)
    tipe = dict(Counter(type(v).__name__ for v in dc.values()))
    return (f"vervar {len(js.get('vervar') or [])} turvar {len(js.get('turvar') or [])} tahun {len(th)} "
            f"turtahun {len(js.get('turtahun') or [])} | datacontent {len(dc)} cocok {cocok} tak-cocok {len(dc) - cocok} "
            f"tabrakan {tabrakan} | tipe nilai {tipe}")

if st.button("Jalankan tes", type="primary"):
    st.header("A. Pemetaan kunci (3 periode terbaru per variabel)")
    for var in [70, 182, 195, 198, 42, 53, 58, 1, 1890]:
        k, js, baris, _ = halaman(model="th", domain="0000", var=var)
        th_ids = [b["th_id"] for b in baris][:3]
        if not th_ids:
            st.text(f"var {var}: tidak ada periode (HTTP {k})")
            continue
        time.sleep(0.6)
        ka, ja = panggil(model="data", domain="0000", var=var, th=";".join(map(str, th_ids)))
        if ka == 200 and isinstance(ja, dict) and ja.get("datacontent") is not None:
            v0 = (ja.get("var") or [{}])[0]
            st.text(f"var {var} th={th_ids} | {petakan(ja, var)}")
            st.text(f"   judul: {str(v0.get('label'))[:70]} | unit: {v0.get('unit')} | decimal: {v0.get('decimal')} | "
                    f"turtahun: {[x.get('label') for x in ja.get('turtahun', [])][:4]} | "
                    f"vervar berlabel INDONESIA: {[x['label'] for x in ja.get('vervar', []) if 'INDONESIA' in str(x.get('label')).upper()][:2]} | "
                    f"last_update: {ja.get('last_update')} | availability: {ja.get('data-availability')}")
        else:
            st.text(f"var {var} th={th_ids}: HTTP {ka} {str((ja or {}).get('message'))[:120]}")
        if len(th_ids) == 3 and max(th_ids) - min(th_ids) == 2:
            time.sleep(0.6)
            kb, jb = panggil(model="data", domain="0000", var=var, th=f"{min(th_ids)}:{max(th_ids)}")
            st.text(f"   rentang titik-dua {min(th_ids)}:{max(th_ids)} -> HTTP {kb}, datacontent {len((jb or {}).get('datacontent') or {}) if isinstance(jb, dict) else 0}")
        time.sleep(0.6)

    st.header("B. Periode tanpa data dan galat")
    k, js = panggil(model="data", domain="0000", var=70, th=999)
    st.text(f"th=999: HTTP {k} | {({x: (js or {}).get(x) for x in ('status', 'data-availability', 'message')})}")
    time.sleep(0.6)
    k, js = panggil(model="data", domain="0000", var=999999, th=114)
    st.text(f"var=999999: HTTP {k} | {({x: (js or {}).get(x) for x in ('status', 'data-availability', 'message')})}")
    time.sleep(0.6)

    st.header("C. Subjek dan konsistensi katalog")
    k, js, baris, meta = halaman(model="subject", domain="0000")
    st.text(f"subjek: terkumpul {len(baris)} dari total {meta.get('total') if meta else None}")
    k, js, baris, meta = halaman(model="var", domain="0000", subject=30)
    st.text(f"variabel subject=30: terkumpul {len(baris)} dari total {meta.get('total') if meta else None}")

    st.header("D. Batas laju")
    n = 0
    awal = len(LOG429)
    t0 = time.time()
    while n < 80 and len(LOG429) == awal:
        r = requests.get(BASE, params={"key": KEY, "model": "th", "domain": "0000", "var": 70}, headers=H, timeout=60)
        n += 1
        if r.status_code == 429:
            js = r.json()
            LOG429.append({k: js.get(k) for k in ("code", "retry_after", "message")})
            break
        time.sleep(0.25)
    st.text(f"panggilan beruntun sebelum 429: {n} dalam {time.time() - t0:.1f} dtk | 429 terakhir: {LOG429[-1] if LOG429 else 'tidak ada'}")
    st.text(f"semua catatan 429 selama tes: {LOG429}")
