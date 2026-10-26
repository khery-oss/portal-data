import io
import time

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="UN SDG Data Explorer - Indonesia", layout="wide")

st.title("🇺🇳 United Nations (UN) SDG - Portal Data Indonesia")
st.markdown(
    "Eksplorasi seri data **Global SDG Indicators Database** dari **United Nations Statistics Division (UNSD)** "
    "khusus untuk **Indonesia**, ditarik langsung (*100% Live API*). Katalog seri, judul goal, satuan, sumber, "
    "dan seluruh angka berasal dari API. Tidak ada daftar indikator tertulis di dalam kode, "
    "dan tidak ada rata-rata atau pembulatan."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

BASE = "https://unstats.un.org/sdgapi/v1/sdg"
AREA_IDN = 360                      # kode area M49 Indonesia
MAX_RETRY = 4
JEDA_DETIK = 1                      # jeda antar panggilan yang benar-benar ke server
UKURAN_HALAMAN_DATA = 500           # penarikan per seri
UKURAN_HALAMAN_PINDAI = (2000, 500) # penarikan seluruh data Indonesia; urutan = coba yang pertama dulu
KODE_TOTAL = ("BOTHSEX", "ALLAREA", "ALLAGE")  # kode dimensi "total" yang dikenali

# Keterangan kode atribut "Nature" (daftar kode SDMX). Kode di luar daftar ditampilkan apa adanya.
# Keterangan kode atribut "Nature" (sifat data). Kode di luar daftar ditampilkan apa adanya.
KETERANGAN_NATURE = {
    "C": ("Data negara",
          "Angka berasal dari statistik nasional (survei atau pencatatan resmi di Indonesia) dan diteruskan "
          "apa adanya oleh lembaga internasional."),
    "CA": ("Data negara yang disesuaikan",
           "Angka berasal dari statistik nasional, lalu disesuaikan oleh lembaga internasional agar "
           "definisinya sebanding antarnegara."),
    "E": ("Estimasi",
          "Angka diperkirakan oleh lembaga internasional karena data nasional tidak lengkap atau tidak tersedia "
          "untuk tahun tersebut."),
    "M": ("Hasil pemodelan",
          "Angka dihitung dengan model statistik oleh lembaga internasional, bukan hasil pengukuran langsung "
          "di Indonesia."),
    "G": ("Data pemantauan global",
          "Angka disusun oleh lembaga internasional yang ditunjuk untuk pemantauan global, dengan metodologi "
          "yang seragam untuk semua negara."),
}

# =============================================================================
# 1. LAPISAN API
# =============================================================================
def _get_json(url: str, timeout: int = 180):
    """GET dengan retry. Galat dibedakan: [Jaringan], [HTTP n], [Format]."""
    for percobaan in range(MAX_RETRY):
        terakhir = percobaan == MAX_RETRY - 1
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
        except requests.RequestException as e:
            if terakhir:
                raise RuntimeError(f"[Jaringan] {type(e).__name__}: {e}")
            time.sleep(2 * (percobaan + 1))
            continue
        if r.status_code == 429 or r.status_code >= 500:
            if terakhir:
                raise RuntimeError(f"[HTTP {r.status_code}] {r.text[:150]}")
            time.sleep(2 * (percobaan + 1))
            continue
        if r.status_code != 200:
            raise RuntimeError(f"[HTTP {r.status_code}] {r.text[:150]}")
        try:
            return r.json()
        except ValueError:
            raise RuntimeError("[Format] Respons server bukan JSON.")


def _unik(daftar) -> list:
    hasil = []
    for x in (daftar or []):
        if x is not None and str(x) not in hasil:
            hasil.append(str(x))
    return hasil


def _tahun(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def muat_katalog() -> list:
    """Katalog seri live dari Series/List. Gagal = exception (tidak ikut di-cache)."""
    js = _get_json(f"{BASE}/Series/List", timeout=60)
    if not isinstance(js, list) or not js:
        raise RuntimeError("[Format] Katalog seri kosong atau bentuknya tidak dikenali.")
    keluaran = []
    for x in js:
        kode = x.get("code")
        if not kode:
            continue
        keluaran.append({
            "code": kode,
            "description": x.get("description") or kode,
            "goal": _unik(x.get("goal")),
            "target": _unik(x.get("target")),
            "indicator": _unik(x.get("indicator")),
            "release": x.get("release"),
        })
    return keluaran


@st.cache_data(ttl=86400, show_spinner=False)
def muat_goal() -> dict:
    """Judul goal live dari Goal/List: {'1': 'End poverty ...', ...}."""
    js = _get_json(f"{BASE}/Goal/List", timeout=60)
    return {str(g["code"]): g.get("title", "") for g in js if g.get("code")}


@st.cache_data(ttl=604800, show_spinner=False)
def halaman_ketersediaan(halaman: int, ukuran: int, release_key: str) -> dict:
    """Satu halaman dari seluruh data Indonesia (tanpa filter seri), diringkas per seri.
    release_key hanya bagian dari kunci cache: data dipindai ulang saat UN merilis versi baru."""
    js = _get_json(f"{BASE}/Series/Data?areaCode={AREA_IDN}&pageSize={ukuran}&page={halaman}")
    data = js.get("data") or []
    ringkas = {}
    for d in data:
        if str(d.get("geoAreaCode")) != str(AREA_IDN):
            raise ValueError(f"Baris dengan kode area {d.get('geoAreaCode')} muncul pada penarikan Indonesia.")
        s = d.get("series")
        if not s:
            raise ValueError("Baris tanpa kode seri pada penarikan Indonesia.")
        t = _tahun(d.get("timePeriodStart"))
        r = ringkas.setdefault(s, [0, None, None])
        r[0] += 1
        if t is not None:
            r[1] = t if r[1] is None else min(r[1], t)
            r[2] = t if r[2] is None else max(r[2], t)
    time.sleep(JEDA_DETIK)
    return {
        "total": js.get("totalElements"),
        "halaman": js.get("totalPages"),
        "baris": len(data),
        "seri": ringkas,
    }


def pindai_ketersediaan(release_key: str) -> dict:
    """Membangun daftar seri yang punya data Indonesia dari penarikan berhalaman.
    Jumlah baris terkumpul harus sama dengan totalElements, kalau tidak hasil ditolak."""
    halaman1, ukuran, galat = None, None, None
    for u in UKURAN_HALAMAN_PINDAI:
        try:
            halaman1 = halaman_ketersediaan(1, u, release_key)
            ukuran = u
            break
        except Exception as e:
            galat = e
    if halaman1 is None:
        raise galat
    total_hal, total_baris = halaman1["halaman"], halaman1["total"]
    if not total_hal or total_baris is None:
        raise RuntimeError("[Format] totalPages atau totalElements tidak ada pada respons.")

    gabungan, terkumpul = {}, 0
    bar = st.progress(0.0, text="Memulai pemindaian...")
    for h in range(1, int(total_hal) + 1):
        bar.progress((h - 1) / int(total_hal), text=f"Memindai halaman {h} dari {total_hal} (ukuran halaman {ukuran})...")
        p = halaman_ketersediaan(h, ukuran, release_key)
        terkumpul += p["baris"]
        for s, (n, t0, t1) in p["seri"].items():
            if s not in gabungan:
                gabungan[s] = [n, t0, t1]
            else:
                g = gabungan[s]
                g[0] += n
                if t0 is not None:
                    g[1] = t0 if g[1] is None else min(g[1], t0)
                if t1 is not None:
                    g[2] = t1 if g[2] is None else max(g[2], t1)
    bar.empty()
    if terkumpul != int(total_baris):
        raise RuntimeError(
            f"Jumlah baris terkumpul ({terkumpul}) tidak sama dengan totalElements ({total_baris}). Hasil ditolak."
        )
    return gabungan


def _ringkas_baris(d: dict, kode: str) -> dict:
    if str(d.get("geoAreaCode")) != str(AREA_IDN):
        raise ValueError(f"Baris dengan kode area {d.get('geoAreaCode')} muncul pada penarikan Indonesia. Data ditolak.")
    if d.get("series") != kode:
        raise ValueError(f"Baris seri {d.get('series')} muncul pada penarikan seri {kode}. Data ditolak.")
    attr = d.get("attributes") or {}
    foot = d.get("footnotes")
    if isinstance(foot, list):
        foot = "; ".join(str(f) for f in foot)
    return {
        "tahun": _tahun(d.get("timePeriodStart")),
        "nilai": None if d.get("value") is None else str(d.get("value")),
        "sumber": d.get("source"),
        "catatan": foot,
        "batas_bawah": d.get("lowerBound"),
        "batas_atas": d.get("upperBound"),
        "periode_detail": d.get("time_detail"),
        "periode_dasar": d.get("basePeriod"),
        "cakupan_waktu": d.get("timeCoverage"),
        "satuan": attr.get("Units"),
        "nature": attr.get("Nature"),
        "status": attr.get("Observation Status"),
        "dimensi": d.get("dimensions") or {},
    }


@st.cache_data(ttl=86400, show_spinner=False)
def tarik_seri(kode: str, release_key: str) -> list:
    """Semua halaman satu seri untuk Indonesia. Jumlah baris harus sama dengan totalElements."""
    url = f"{BASE}/Series/Data?seriesCode={kode}&areaCode={AREA_IDN}&pageSize={UKURAN_HALAMAN_DATA}"
    js = _get_json(f"{url}&page=1")
    total, halaman = js.get("totalElements"), js.get("totalPages")
    if total is None or halaman is None:
        raise RuntimeError("[Format] totalElements atau totalPages tidak ada pada respons.")
    baris = list(js.get("data") or [])
    for h in range(2, int(halaman) + 1):
        time.sleep(JEDA_DETIK)
        baris.extend(_get_json(f"{url}&page={h}").get("data") or [])
    if len(baris) != int(total):
        raise RuntimeError(f"Jumlah baris terkumpul ({len(baris)}) tidak sama dengan totalElements ({total}). Data ditolak.")
    return [_ringkas_baris(d, kode) for d in baris]


def _ke_angka(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def susun_dataframe(rows: list):
    """Mengembalikan (df, kolom_dimensi). Nilai asli dipertahankan sebagai teks; tanpa pembulatan."""
    dims_df = pd.DataFrame([r["dimensi"] for r in rows])
    dim_cols = list(dims_df.columns)
    df = pd.DataFrame({
        "Tahun": pd.array([r["tahun"] for r in rows], dtype="Int64"),
    })
    for c in dim_cols:
        df[c] = dims_df[c].fillna("(tidak ada)").astype(str)
    df["Nilai Asli"] = [r["nilai"] for r in rows]
    df["Nilai (numerik)"] = [_ke_angka(r["nilai"]) for r in rows]
    df["Satuan"] = [r["satuan"] for r in rows]
    df["Sifat Data"] = [r["nature"] for r in rows]
    df["Status Observasi"] = [r["status"] for r in rows]
    df["Sumber"] = [r["sumber"] for r in rows]
    df["Catatan Kaki"] = [r["catatan"] for r in rows]
    df["Batas Bawah"] = [r["batas_bawah"] for r in rows]
    df["Batas Atas"] = [r["batas_atas"] for r in rows]
    df["Periode Detail"] = [r["periode_detail"] for r in rows]
    df["Periode Dasar"] = [r["periode_dasar"] for r in rows]
    df["Cakupan Waktu"] = [r["cakupan_waktu"] for r in rows]
    # Kolom yang seluruhnya kosong dari sumber tidak ditampilkan
    kosong = [c for c in ["Batas Bawah", "Batas Atas", "Periode Detail", "Periode Dasar", "Cakupan Waktu",
                          "Catatan Kaki", "Status Observasi"] if df[c].isna().all()]
    return df.drop(columns=kosong), dim_cols


# =============================================================================
# 2. MEMUAT KATALOG LIVE
# =============================================================================
try:
    katalog = muat_katalog()
except Exception as e:
    st.error(f"Gagal memuat katalog seri UN SDG: {e}")
    st.stop()

try:
    goal_map = muat_goal()
except Exception:
    goal_map = {}
    st.caption("Judul goal tidak berhasil dimuat; filter goal ditampilkan dengan nomor saja.")

peta_seri = {s["code"]: s for s in katalog}
release_key = "|".join(sorted({s["release"] for s in katalog if s.get("release")}))

# =============================================================================
# 3. KATALOG & KETERSEDIAAN DATA INDONESIA
# =============================================================================
st.subheader("1. Katalog Seri & Ketersediaan Data Indonesia")
st.markdown(
    f"Basis data global UN SDG memuat **{len(katalog)} seri** untuk semua negara. "
    "**Tidak semuanya punya data Indonesia.** Tekan tombol di bawah untuk memindai seri mana saja yang punya "
    "data Indonesia langsung dari API. Hasilnya dipakai bersama oleh semua pengunjung dan hanya perlu diulang "
    "saat UN merilis versi baru basis data."
)

if st.button("🔎 Pindai ketersediaan data Indonesia"):
    try:
        st.session_state["sdg_ketersediaan"] = {"release": release_key, "seri": pindai_ketersediaan(release_key)}
    except Exception as e:
        st.error(f"Pemindaian gagal: {e}. Katalog global tetap bisa dipakai tanpa filter ketersediaan.")

tersimpan = st.session_state.get("sdg_ketersediaan")
ketersediaan = tersimpan["seri"] if tersimpan and tersimpan["release"] == release_key else None

if ketersediaan is not None:
    n_idn = sum(1 for s in katalog if s["code"] in ketersediaan)
    st.success(f"Hasil pindai: **{n_idn}** dari {len(katalog)} seri punya data Indonesia (rilis `{release_key}`).")
    tak_terdaftar = [k for k in ketersediaan if k not in peta_seri]
    if tak_terdaftar:
        st.caption(f"{len(tak_terdaftar)} seri muncul di data Indonesia tetapi tidak ada di katalog: {', '.join(tak_terdaftar[:10])}")

def _urut_goal(g):
    return (0, int(g)) if g.isdigit() else (1, g)

c_goal, c_q = st.columns([1.2, 2])
goal_opsi = ["Semua Goal"] + sorted({g for s in katalog for g in s["goal"]}, key=_urut_goal)
pilihan_goal = c_goal.selectbox(
    "Goal SDG:", goal_opsi,
    format_func=lambda g: g if g == "Semua Goal" else (f"Goal {g}: {goal_map[g]}" if goal_map.get(g) else f"Goal {g}"),
)
query = c_q.text_input(
    "🔍 Cari seri (kata kunci Bahasa Inggris atau kode seri):",
    placeholder="Contoh: unemployment · poverty · mortality · SL_TLF_UEM · women",
).strip()
hanya_idn = st.checkbox(
    "Hanya tampilkan seri yang punya data Indonesia",
    value=ketersediaan is not None, disabled=ketersediaan is None,
)

token = query.lower().split()
terapkan_filter_idn = hanya_idn and ketersediaan is not None
hasil = [
    s for s in katalog
    if (pilihan_goal == "Semua Goal" or pilihan_goal in s["goal"])
    and all(t in f"{s['code']} {s['description']}".lower() for t in token)
    and (not terapkan_filter_idn or s["code"] in ketersediaan)
]
hasil.sort(key=lambda s: s["description"].lower())

if not hasil:
    st.warning("Tidak ada seri yang cocok. Ubah kata kunci, goal, atau matikan filter ketersediaan.")
    st.stop()

if ketersediaan is None:
    st.info(f"{len(hasil)} seri cocok di katalog global. Ketersediaan data Indonesia belum dipindai.")
else:
    st.caption(f"{len(hasil)} seri cocok.")

def label_seri(kode: str) -> str:
    teks = peta_seri[kode]["description"]
    if ketersediaan is not None and kode not in ketersediaan:
        teks += "  [tidak ada data Indonesia]"
    return teks

kode_pilih = st.selectbox("Pilih Seri:", [s["code"] for s in hasil], format_func=label_seri)
meta = peta_seri[kode_pilih]

with st.expander("ℹ️ Metadata & Sumber Resmi", expanded=False):
    st.markdown(f"**Seri:** {meta['description']}")
    st.markdown(f"**Kode Seri:** `{kode_pilih}`")
    goal_teks = ", ".join(f"Goal {g}" + (f" ({goal_map[g]})" if goal_map.get(g) else "") for g in meta["goal"])
    st.markdown(f"**Goal:** {goal_teks or '-'}")
    st.markdown(f"**Target:** {', '.join(meta['target']) or '-'}")
    st.markdown(f"**Indikator:** {', '.join(meta['indicator']) or '-'}")
    st.markdown(f"**Versi Rilis Basis Data:** `{meta.get('release') or '-'}`")
    if ketersediaan is not None and kode_pilih in ketersediaan:
        n, t0, t1 = ketersediaan[kode_pilih]
        st.markdown(f"**Observasi Indonesia (hasil pindai):** {n} baris, tahun {t0} sampai {t1}")
    st.markdown(
        "**Basis Data:** UN Global SDG Indicators Database, United Nations Statistics Division (UNSD)  \n"
        "🔗 [UNSD SDG Data Portal](https://unstats.un.org/sdgs/dataportal) · "
        "[Metadata Indikator](https://unstats.un.org/sdgs/metadata/)"
    )

# =============================================================================
# 4. PENARIKAN DATA (hasil disimpan di session_state)
# =============================================================================
st.subheader("2. Penarikan Data Indonesia")

if st.button("📊 Tarik Data Seri Ini", type="primary"):
    with st.spinner(f"Menarik seluruh halaman untuk {kode_pilih}..."):
        try:
            rows = tarik_seri(kode_pilih, release_key)
            st.session_state["sdg_hasil"] = {"kode": kode_pilih, "rows": rows}
        except Exception as e:
            st.session_state["sdg_hasil"] = None
            st.error(f"Gagal menarik data {kode_pilih}: {e}")

hasil_tarik = st.session_state.get("sdg_hasil")

if hasil_tarik:
    kode = hasil_tarik["kode"]
    rows = hasil_tarik["rows"]
    judul = peta_seri[kode]["description"] if kode in peta_seri else kode

    st.divider()
    st.markdown(f"**Hasil untuk seri `{kode}`:** {judul}")

    if not rows:
        st.warning("Seri ini tidak punya data Indonesia di basis data UN SDG.")
    else:
        df, dim_cols = susun_dataframe(rows)
        st.success(f"Berhasil menarik **{len(df)}** observasi dari API UN SDG.")

        # --- Pilihan dimensi: tanpa rata-rata, default ke kode total bila ada ---
        mask = pd.Series(True, index=df.index)
        dim_tetap = []
        if dim_cols:
            st.markdown("**Disagregasi (dimensi) pada seri ini.** Default memakai kode total bila ada; "
                        "bila tidak ada kode total, semua nilai dipilih. Tidak ada nilai yang dirata-ratakan.")
        kolom_w = st.columns(max(1, min(4, len(dim_cols)))) if dim_cols else []
        i = 0
        for c in dim_cols:
            nilai = sorted(df[c].unique())
            if len(nilai) == 1:
                dim_tetap.append(f"{c} = {nilai[0]}")
                continue
            total_ada = [k for k in KODE_TOTAL if k in nilai]
            bawaan = [total_ada[0]] if total_ada else nilai
            with kolom_w[i % len(kolom_w)]:
                pilih = st.multiselect(c, nilai, default=bawaan, key=f"dim_{kode}_{c}")
            i += 1
            mask &= df[c].isin(pilih)
        if dim_tetap:
            st.caption("Dimensi bernilai tunggal: " + " · ".join(dim_tetap))

        df_view = df[mask].copy()
        st.caption(f"Menampilkan {len(df_view)} dari {len(df)} observasi seri ini.")

        if df_view.empty:
            st.warning("Tidak ada observasi untuk kombinasi dimensi yang dipilih.")
        else:
            # --- Peringatan: nilai sensor dan duplikat ---
            n_nonangka = int(df_view["Nilai (numerik)"].isna().sum())
            if n_nonangka:
                st.warning(
                    f"{n_nonangka} observasi bernilai bukan angka murni (mis. diawali < atau >). "
                    "Nilai aslinya tampil di kolom *Nilai Asli* dan tidak digambar di grafik."
                )
            dup = df_view.duplicated(subset=["Tahun"] + dim_cols, keep=False)
            if dup.any():
                st.warning(
                    f"{int(dup.sum())} baris punya tahun dan kombinasi dimensi yang sama (kemungkinan sumber berbeda). "
                    "Semuanya tetap ditampilkan tanpa diratakan; di grafik dipisah menurut sumber."
                )

            # --- Unduh ---
            c1, c2, c3 = st.columns(3)
            c1.download_button("📥 Unduh CSV (tampilan terpilih)", df_view.to_csv(index=False).encode("utf-8"),
                               f"UN_SDG_{kode}_IDN.csv", "text/csv", key="dl_sdg_csv")
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as w:
                df_view.to_excel(w, index=False, sheet_name="UN SDG")
            c2.download_button("📊 Unduh Excel (tampilan terpilih)", buf.getvalue(), f"UN_SDG_{kode}_IDN.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_sdg_xl")
            c3.download_button("📥 Unduh CSV (semua dimensi)", df.to_csv(index=False).encode("utf-8"),
                               f"UN_SDG_{kode}_IDN_semua_dimensi.csv", "text/csv", key="dl_sdg_csv_all")

            # --- Grafik: satu garis per kombinasi dimensi ---
            satuan = " / ".join(sorted({str(s) for s in df_view["Satuan"].dropna().unique()})) or "Nilai"
            beda = [c for c in dim_cols if df_view[c].nunique() > 1]
            fig = go.Figure()
            kelompok = df_view.groupby(beda, dropna=False) if beda else [((), df_view)]
            for key, g in kelompok:
                key = key if isinstance(key, tuple) else (key,)
                nama_dasar = " · ".join(str(k) for k in key) if beda else kode
                g = g[g["Nilai (numerik)"].notna() & g["Tahun"].notna()]
                if g.empty:
                    continue
                bagian = [(None, g)]
                if g["Tahun"].duplicated().any():
                    g = g.assign(Sumber=g["Sumber"].fillna("(sumber tidak tercatat)"))
                    bagian = list(g.groupby("Sumber"))
                for sumber, gs in bagian:
                    nama = nama_dasar if sumber is None else f"{nama_dasar} [{sumber}]"
                    gs = gs.sort_values("Tahun")
                    fig.add_trace(go.Scatter(
                        x=gs["Tahun"].astype(int), y=gs["Nilai (numerik)"],
                        mode="lines+markers", name=nama,
                        line=dict(width=2.5), marker=dict(size=6),
                        hovertemplate=f"{nama}<br>Tahun %{{x}}<br>Nilai: %{{y}} {satuan}<extra></extra>",
                    ))
            fig.update_layout(
                xaxis=dict(title="Tahun", tickmode="linear"),
                yaxis=dict(title=satuan),
                hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- Sumber asli & keterangan kode ---
            with st.expander("📚 Sumber Asli & Keterangan Kode", expanded=True):
                st.markdown(
                    f"**Basis data:** UN Global SDG Indicators Database (UNSD), versi rilis `{release_key or '-'}`"
                )
                sumber_unik = [str(s) for s in df_view["Sumber"].dropna().unique()]
                if sumber_unik:
                    st.markdown("**Sumber data per observasi:**")
                    for s in sumber_unik:
                        st.markdown(f"- {s}")
                if "Catatan Kaki" in df_view.columns:
                    catatan = [str(s) for s in df_view["Catatan Kaki"].dropna().unique()]
                    if catatan:
                        st.markdown("**Catatan kaki:**")
                        for s in catatan:
                            st.markdown(f"- {s}")
                kode_nature = [str(s) for s in df_view["Sifat Data"].dropna().unique()]
                if kode_nature:
                    st.markdown("**Sifat Data (`Nature`), arti kode pada tampilan ini:**")
                    for k in kode_nature:
                        nama, arti = KETERANGAN_NATURE.get(
                            k, ("Kode di luar keterangan modul", "Lihat dokumentasi UNSD untuk artinya.")
                        )
                        st.markdown(f"- **`{k}` ({nama}).** {arti}")
                    st.caption(
                        "Cara membacanya: angka bersifat C dan CA paling dekat dengan statistik nasional. "
                        "Angka bersifat E dan M adalah turunan lembaga internasional, jadi sebaiknya disebut "
                        "sifatnya saat dikutip."
                    )
                    
            with st.expander("📋 Tabel Data Lengkap"):
                st.dataframe(df_view.sort_values("Tahun", ascending=False), use_container_width=True)
