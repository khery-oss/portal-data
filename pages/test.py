import time
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Tes FRED", layout="wide")
st.title("Tes struktur API FRED (Indonesia)")

try:
    KEY = st.secrets["FRED_API_KEY"]
except Exception:
    st.error("FRED_API_KEY tidak ada di secrets.")
    st.stop()

BASE = "https://api.stlouisfed.org/fred"
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def panggil(path, kunci=None, **params):
    p = {"api_key": kunci or KEY, "file_type": "json", **params}
    try:
        r = requests.get(f"{BASE}/{path}", params=p, headers=H, timeout=30)
        return r.status_code, r.json()
    except Exception as e:
        return None, {"exception": type(e).__name__}

def cari(teks, tag=None):
    semua, offset, total = [], 0, None
    while True:
        prm = dict(search_text=teks, limit=1000, offset=offset, order_by="popularity", sort_order="desc")
        if tag:
            prm["tag_names"] = tag
        kode, js = panggil("series/search", **prm)
        if kode != 200:
            return semua, total, (kode, {k: v for k, v in js.items() if k != "api_key"})
        total = js.get("count")
        bagian = js.get("seriess", [])
        semua.extend(bagian)
        offset += len(bagian)
        if not bagian or offset >= int(total):
            break
        time.sleep(0.6)
    return semua, total, None

if st.button("Jalankan tes", type="primary"):
    st.header("A. Pencarian 'Indonesia' (semua halaman)")
    semua, total, err = cari("Indonesia")
    if err:
        st.error(err)
        st.stop()
    judul_ind = [s for s in semua if "indonesia" in s.get("title", "").lower()]
    st.write(f"count dari API: **{total}** | terkumpul: **{len(semua)}** | judul memuat 'Indonesia': **{len(judul_ind)}**")
    bukan_for = [s for s in judul_ind if "for indonesia" not in s["title"].lower()]
    st.write(f"Judul memuat 'Indonesia' tetapi bukan pola 'for Indonesia': **{len(bukan_for)}**")
    st.dataframe(pd.DataFrame([{"id": s["id"], "title": s["title"], "freq": s.get("frequency_short"),
                                "units": s.get("units_short")} for s in bukan_for[:60]]), use_container_width=True)
    tanpa_kata = [s for s in semua if "indonesia" not in s.get("title", "").lower()]
    st.write(f"Hasil pencarian yang judulnya TIDAK memuat 'Indonesia': {len(tanpa_kata)}. Contoh:")
    st.write([s["title"] for s in tanpa_kata[:8]])

    st.header("B. Duplikat label dropdown (judul + frekuensi + satuan)")
    df = pd.DataFrame([{"title": s["title"], "freq": s.get("frequency"), "units": s.get("units_short"), "id": s["id"]}
                       for s in judul_ind])
    dup = df[df.duplicated(["title", "freq", "units"], keep=False)].sort_values("title")
    st.write(f"Baris yang labelnya kembar: **{len(dup)}**")
    st.dataframe(dup.head(30), use_container_width=True)

    st.header("C. Pencarian dengan tag_names=indonesia")
    time.sleep(1)
    semua_t, total_t, err_t = cari("Indonesia", tag="indonesia")
    if err_t:
        st.write("Gagal:", err_t)
    else:
        judul_t = [s for s in semua_t if "indonesia" in s.get("title", "").lower()]
        st.write(f"count: **{total_t}** | terkumpul: {len(semua_t)} | judul memuat 'Indonesia': {len(judul_t)}")
        st.write("Contoh judul tanpa kata Indonesia pada hasil tag:",
                 [s["title"] for s in semua_t if "indonesia" not in s.get("title", "").lower()][:8])

    st.header("D. Struktur observasi (seri 'for Indonesia' terpopuler)")
    seri = next((s for s in judul_ind if "for indonesia" in s["title"].lower()), None)
    if seri:
        kode, js = panggil("series/observations", series_id=seri["id"])
        st.write(seri["id"], "|", seri["title"])
        st.write("HTTP", kode, "| kunci:", list(js.keys()))
        st.write("count:", js.get("count"), "| limit:", js.get("limit"), "| len(observations):", len(js.get("observations", [])))

    st.header("E. Bentuk respons error (kunci palsu)")
    kode, js = panggil("series/search", kunci="x" * 32, search_text="Indonesia", limit=1)
    st.write("HTTP", kode, "| isi:", {k: v for k, v in js.items() if k != "api_key"})
