import html
import io
import re
import time

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="BPS Explorer - IndoEcon", layout="wide")

st.title("🏛️ BPS (Badan Pusat Statistik) - Statistik Resmi Indonesia")
st.markdown(
    "Eksplorasi tabel dinamis resmi **BPS - Statistics Indonesia** tingkat nasional melalui **BPS WebAPI** "
    "secara *real-time* (*100% Live API*). Katalog, angka, satuan, dan sumber seluruhnya berasal dari API, "
    "tanpa pembulatan dan tanpa pembatasan tahun."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# =============================================================================
# API KEY — dengan pesan ramah jika key tidak ada
# =============================================================================
try:
    BPS_API_KEY = st.secrets["BPS_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error(
        "⚠️ **BPS API Key tidak ditemukan.**\n\n"
        "Tambahkan `BPS_API_KEY` ke file `secrets.toml` atau Streamlit Cloud Secrets:\n"
        "```\nBPS_API_KEY = 'your_api_key_here'\n```\n"
        "Daftar gratis untuk mendapatkan API Key di: https://webapi.bps.go.id/developer/"
    )
    st.stop()

BASE = "https://webapi.bps.go.id/v1/api/list"
DOMAIN = "0000"          # domain nasional BPS
MAKS_TAHUN = 3           # batas API: jumlah periode (th) per panggilan data
JEDA_DETIK = 1.1         # jeda setelah setiap panggilan ke server (batas laju API sekitar 60 panggilan per menit)
BATAS_WAKTU = 45         # detik per percobaan
MAX_RETRY = 3
MAKS_429 = 3             # berapa kali menunggu retry_after sebelum menyerah


# =============================================================================
# 1. LAPISAN API
# =============================================================================
def aman(teks) -> str:
    """Pastikan kunci API tidak pernah tampil di halaman."""
    return str(teks).replace(BPS_API_KEY, "***")


def bps_get(**params) -> dict:
    """GET ke BPS WebAPI. Kunci dikirim lewat params; pesan error tidak memuat URL.
    Mengulang untuk timeout, koneksi putus, HTTP 5xx, dan menunggu retry_after saat HTTP 429."""
    p = {"key": BPS_API_KEY, **params}
    percobaan, n429 = 0, 0
    while True:
        try:
            r = requests.get(BASE, params=p, headers=HEADERS, timeout=BATAS_WAKTU)
        except requests.RequestException as e:
            percobaan += 1
            if percobaan >= MAX_RETRY:
                raise RuntimeError(
                    f"[Jaringan] Server BPS tidak merespons setelah {MAX_RETRY} percobaan ({type(e).__name__}). "
                    "Coba lagi beberapa saat."
                )
            time.sleep(2 * percobaan)
            continue
        try:
            js = r.json()
        except ValueError:
            js = None
        if r.status_code == 429:
            n429 += 1
            if n429 >= MAKS_429:
                raise RuntimeError("[BPS 429] Batas laju API BPS tercapai berulang kali. Coba lagi beberapa menit lagi.")
            tunggu = float(js.get("retry_after") or 60) if isinstance(js, dict) else 60.0
            time.sleep(tunggu + 1)
            continue
        if r.status_code >= 500:
            percobaan += 1
            if percobaan >= MAX_RETRY:
                raise RuntimeError(f"[HTTP {r.status_code}] Server BPS gagal merespons setelah {MAX_RETRY} percobaan.")
            time.sleep(2 * percobaan)
            continue
        if not isinstance(js, dict):
            raise RuntimeError(f"[Format] HTTP {r.status_code}, respons bukan JSON yang dikenali.")
        if r.status_code != 200 or str(js.get("status", "")).lower() == "error":
            raise RuntimeError(f"[BPS {r.status_code}] {aman(js.get('message') or 'Permintaan ditolak.')}")
        time.sleep(JEDA_DETIK)
        return js


def semua_halaman(**params) -> list:
    """Mengumpulkan semua halaman daftar. Jumlah baris harus sama dengan total dari API."""
    js = bps_get(page=1, **params)
    if js.get("data-availability") == "list-not-available":
        return []
    d = js.get("data")
    if not (isinstance(d, list) and len(d) == 2 and isinstance(d[1], list)):
        raise RuntimeError("[Format] Bentuk respons daftar tidak dikenali.")
    meta, baris = d[0], list(d[1])
    for halaman in range(2, int(meta.get("pages", 1)) + 1):
        jh = bps_get(page=halaman, **params)
        dh = jh.get("data")
        if not (isinstance(dh, list) and len(dh) == 2 and isinstance(dh[1], list)):
            raise RuntimeError(f"[Format] Halaman {halaman} tidak dikenali.")
        baris.extend(dh[1])
    total = meta.get("total")
    if total is not None and len(baris) != int(total):
        raise RuntimeError(f"Jumlah baris terkumpul ({len(baris)}) tidak sama dengan total di API ({total}). Data ditolak.")
    return baris


@st.cache_data(ttl=86400, show_spinner=False)
def muat_subjek() -> list:
    """Daftar subjek live. Gagal = exception (tidak ikut di-cache)."""
    baris = semua_halaman(model="subject", domain=DOMAIN)
    hasil = [
        {"id": b["sub_id"], "judul": b.get("title") or str(b["sub_id"]), "kategori": b.get("subcat")}
        for b in baris if b.get("sub_id") is not None
    ]
    if not hasil:
        raise RuntimeError("Daftar subjek BPS kosong.")
    return hasil


@st.cache_data(ttl=3600, show_spinner=False)
def cari_variabel(subjek_id: int, keyword: str) -> list:
    """Katalog variabel (tabel dinamis) live, disaring oleh API menurut subjek dan kata kunci."""
    prm = {"model": "var", "domain": DOMAIN}
    if subjek_id:
        prm["subject"] = subjek_id
    if keyword:
        prm["keyword"] = keyword
    baris = semua_halaman(**prm)
    return [
        {k: b.get(k) for k in ("var_id", "title", "sub_id", "sub_name", "notes", "unit")}
        for b in baris if b.get("var_id") is not None
    ]


@st.cache_data(ttl=3600, show_spinner=False)
def daftar_periode(var_id: int) -> list:
    """Semua periode (th_id, label) yang tersedia untuk satu variabel, urut dari terlama."""
    baris = semua_halaman(model="th", domain=DOMAIN, var=var_id)
    periode = sorted(((b["th_id"], str(b.get("th"))) for b in baris if b.get("th_id") is not None))
    return periode


def bongkar(js: dict, var_id: int) -> dict:
    """Memecah datacontent menjadi baris. Kunci dibentuk dari semua kombinasi dimensi dan dicocokkan persis;
    kunci yang tidak dikenali atau bertabrakan menyebabkan data ditolak, bukan ditebak."""
    info = (js.get("var") or [{}])[0]
    if info and info.get("val") is not None and int(info["val"]) != int(var_id):
        raise RuntimeError(f"Respons untuk variabel {info.get('val')} muncul pada penarikan variabel {var_id}. Data ditolak.")
    meta = {
        "var": info,
        "last_update": js.get("last_update"),
        "labelvervar": js.get("labelvervar"),
    }
    dc = js.get("datacontent")
    if not dc:
        return {"meta": meta, "rows": []}
    if not isinstance(dc, dict):
        raise RuntimeError("[Format] datacontent bukan kamus. Data ditolak.")
    ver = js.get("vervar") or [{"val": 0, "label": "(tidak ada)"}]
    tur = js.get("turvar") or [{"val": 0, "label": "(tidak ada)"}]
    thn = js.get("tahun") or []
    tth = js.get("turtahun") or [{"val": 0, "label": "(tidak ada)"}]
    peta = {}
    for v in ver:
        for t in tur:
            for y in thn:
                for urut, z in enumerate(tth):
                    kunci = f"{v['val']}{var_id}{t['val']}{y['val']}{z['val']}"
                    if kunci in peta:
                        raise RuntimeError("Kunci data bertabrakan antar kombinasi dimensi. Data ditolak.")
                    peta[kunci] = (v, t, y, z, urut)
    baris = []
    for kunci, nilai in dc.items():
        if kunci not in peta:
            raise RuntimeError(f"Kunci data {kunci} tidak dapat dipetakan ke dimensi. Data ditolak.")
        v, t, y, z, urut = peta[kunci]
        baris.append({
            "kode_vervar": v["val"], "vervar": v.get("label"),
            "kode_turvar": t["val"], "turvar": t.get("label"),
            "th_id": y["val"], "tahun": y.get("label"),
            "kode_turth": z["val"], "turtahun": z.get("label"), "urut_turth": urut,
            "nilai": nilai,
        })
    return {"meta": meta, "rows": baris}


@st.cache_data(ttl=3600, show_spinner=False)
def tarik_data(var_id: int, th_ids: tuple) -> dict:
    """Satu panggilan data: maksimal MAKS_TAHUN periode. Gagal = exception (tidak ikut di-cache)."""
    if len(th_ids) > MAKS_TAHUN:
        raise RuntimeError(f"Maksimal {MAKS_TAHUN} periode per panggilan.")
    js = bps_get(model="data", domain=DOMAIN, var=var_id, th=";".join(str(t) for t in th_ids))
    return bongkar(js, var_id)


def bersihkan_html(teks) -> str:
    """Mengubah HTML catatan BPS menjadi teks biasa. Isinya tidak diubah, hanya tag yang dibuang."""
    if not teks:
        return ""
    t = re.sub(r"(?i)<\s*li[^>]*>", "- ", str(teks))
    t = re.sub(r"(?i)<\s*br\s*/?>|</\s*p\s*>|</\s*li\s*>|</\s*ul\s*>|</\s*div\s*>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t\u00a0]+", " ", t)
    t = re.sub(r"\s*\n\s*", "\n", t)
    return t.strip()


def tarik_semua(var_id: int):
    """Menarik seluruh periode, tiga periode per panggilan. Mengembalikan (meta, baris, periode, kosong, gagal)."""
    periode = daftar_periode(var_id)
    if not periode:
        return None, [], periode, [], []
    label_th = dict(periode)
    th_ids = [p[0] for p in periode]
    kelompok = [tuple(th_ids[i:i + MAKS_TAHUN]) for i in range(0, len(th_ids), MAKS_TAHUN)]
    meta, baris, kosong, gagal = None, [], [], []
    bar = st.progress(0.0, text="Memulai penarikan...")
    for i, kel in enumerate(kelompok):
        tahun_teks = ", ".join(label_th[t] for t in kel)
        bar.progress(i / len(kelompok), text=f"Menarik periode {tahun_teks} ({i + 1}/{len(kelompok)})...")
        try:
            hasil = tarik_data(var_id, kel)
        except Exception as e:
            gagal.append((tahun_teks, aman(e)[:200]))
            continue
        meta = meta or hasil["meta"]
        baris.extend(hasil["rows"])
        if not hasil["rows"]:
            kosong.append(tahun_teks)
    bar.empty()
    return meta, baris, periode, kosong, gagal


def susun_dataframe(rows: list, meta: dict):
    """Mengembalikan (df, kolom_dimensi). Nilai apa adanya: tanpa pembulatan, tanpa rata-rata."""
    d = pd.DataFrame(rows).sort_values(["th_id", "urut_turth"], kind="stable").reset_index(drop=True)
    nama_ver = (meta or {}).get("labelvervar") or "Dimensi Vertikal"
    df = pd.DataFrame({
        nama_ver: d["vervar"].fillna("(tidak ada)").astype(str),
        "Variabel Turunan": d["turvar"].fillna("(tidak ada)").astype(str),
        "Tahun": d["tahun"].astype(str),
        "Periode": d["turtahun"].fillna("(tidak ada)").astype(str),
        "Nilai (angka)": pd.to_numeric(d["nilai"], errors="coerce"),
    })
    teks_asli = d["nilai"].map(lambda v: v if isinstance(v, str) else None)
    if teks_asli.notna().any():
        df["Nilai (teks asli)"] = teks_asli
    df["Kode Dimensi Vertikal"] = d["kode_vervar"]
    df["Kode Variabel Turunan"] = d["kode_turvar"]
    df["Kode Tahun (th_id)"] = d["th_id"]
    df["Kode Periode"] = d["kode_turth"]
    df["_urut"] = d["urut_turth"]
    return df, [nama_ver, "Variabel Turunan", "Periode"]


# =============================================================================
# 2. KATALOG LIVE & PEMILIHAN VARIABEL
# =============================================================================
try:
    with st.spinner("Memuat daftar subjek BPS..."):
        subjek = muat_subjek()
except Exception as e:
    st.error(f"Gagal memuat daftar subjek BPS: {aman(e)}")
    st.stop()

st.subheader("1. Pencarian Tabel Dinamis BPS (Nasional)")
st.markdown(
    "Pilih subjek, ketik kata kunci, atau keduanya. Pencarian dilakukan oleh server BPS dan hanya mencocokkan "
    "**judul berbahasa Indonesia** (contoh: *inflasi*, *kemiskinan*, *pengangguran*, *penduduk*)."
)

c_sub, c_kw = st.columns([1.2, 2])
peta_subjek = {s["id"]: s for s in subjek}
subjek_pilih = c_sub.selectbox(
    "Subjek:", [0] + [s["id"] for s in subjek],
    format_func=lambda i: "Semua Subjek" if i == 0 else f"{peta_subjek[i]['judul']} ({peta_subjek[i]['kategori']})",
)
keyword = c_kw.text_input("🔍 Kata kunci judul (Bahasa Indonesia):", placeholder="Contoh: inflasi · kemiskinan · pengangguran").strip()

if not subjek_pilih and not keyword:
    st.info("Pilih subjek atau ketik kata kunci untuk mulai mencari tabel.")
    st.stop()

try:
    with st.spinner("Mencari tabel di katalog BPS..."):
        hasil_cari = cari_variabel(int(subjek_pilih), keyword)
except Exception as e:
    st.error(f"Gagal memuat katalog tabel BPS: {aman(e)}")
    st.stop()

if not hasil_cari:
    st.warning(
        "Tidak ada tabel yang cocok. Pencarian hanya mencocokkan judul berbahasa Indonesia; "
        "coba kata kunci lain atau ganti subjek."
    )
    st.stop()

hasil_cari = sorted(hasil_cari, key=lambda v: (v["title"] or "").lower())
st.success(f"Ditemukan **{len(hasil_cari)}** tabel dinamis.")

jumlah_judul = {}
for v in hasil_cari:
    jumlah_judul[v["title"]] = jumlah_judul.get(v["title"], 0) + 1
labels = [
    v["title"] if jumlah_judul[v["title"]] == 1 else f"{v['title']} | ID {v['var_id']}"
    for v in hasil_cari
]
idx = st.selectbox("Pilih Tabel:", list(range(len(hasil_cari))), format_func=lambda i: labels[i])
pilih = hasil_cari[idx]
var_id, judul_var = int(pilih["var_id"]), pilih["title"]

with st.expander("ℹ️ Metadata & Catatan dari Katalog BPS", expanded=False):
    st.markdown(f"**Judul Tabel:** {judul_var}")
    st.markdown(f"**ID Variabel BPS:** `{var_id}`")
    st.markdown(f"**Subjek:** {pilih.get('sub_name') or '-'}")
    st.markdown(f"**Satuan:** {pilih.get('unit') or 'tidak dicantumkan oleh API'}")
    catatan_katalog = bersihkan_html(pilih.get("notes"))
    if catatan_katalog:
        st.markdown("**Catatan & sumber:**")
        st.text(catatan_katalog)

# =============================================================================
# 3. PENARIKAN DATA (hasil disimpan di session_state)
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu Nasional")
st.caption("Seluruh periode yang tersedia ditarik otomatis, tiga periode per panggilan sesuai batas API BPS.")

if st.button("📊 Ambil Data BPS (Live API)", type="primary"):
    try:
        meta, baris, periode, kosong, gagal = tarik_semua(var_id)
        st.session_state["bps_hasil"] = {
            "var_id": var_id, "judul": judul_var, "meta": meta, "rows": baris,
            "n_periode": len(periode), "kosong": kosong, "gagal": gagal,
        }
    except Exception as e:
        st.session_state["bps_hasil"] = None
        st.error(f"Gagal menarik data tabel {var_id}: {aman(e)}")

hasil = st.session_state.get("bps_hasil")

if hasil:
    st.divider()
    st.markdown(f"**Hasil untuk tabel `{hasil['var_id']}`:** {hasil['judul']}")

    if hasil["gagal"]:
        st.error(
            "⚠️ Deret **tidak lengkap**: periode berikut gagal ditarik dan tidak ada di tabel atau grafik. "
            "Klik tombol tarik lagi untuk mencoba ulang.\n\n"
            + "\n".join(f"- {t}: {m}" for t, m in hasil["gagal"])
        )
    if hasil["kosong"]:
        st.info("Periode tanpa data dari BPS: " + "; ".join(hasil["kosong"]))

    if not hasil["rows"]:
        if not hasil["gagal"]:
            st.warning("Server BPS merespons, tetapi tidak ada data untuk tabel ini pada periode yang tersedia.")
    else:
        meta = hasil["meta"] or {}
        df, dim_cols = susun_dataframe(hasil["rows"], meta)
        df["Indikator"] = hasil["judul"]
        df["ID Variabel"] = hasil["var_id"]
        nama_ver = dim_cols[0]
        st.success(f"Berhasil menarik **{len(df)}** observasi dari {hasil['n_periode']} periode tahun BPS.")

        # --- Pilihan dimensi: tanpa rata-rata ---
        mask = pd.Series(True, index=df.index)
        dim_tetap = []
        st.markdown(
            "**Dimensi pada tabel ini.** Default memilih baris berlabel *INDONESIA* bila ada pada dimensi vertikal; "
            "selain itu semua nilai dipilih. Tidak ada nilai yang dirata-ratakan."
        )
        kolom_w = st.columns(3)
        for i, c in enumerate(dim_cols):
            nilai = sorted(df[c].unique(), key=lambda x: str(x))
            if len(nilai) == 1:
                dim_tetap.append(f"{c} = {nilai[0]}")
                continue
            bawaan = nilai
            if c == nama_ver:
                nasional = [v for v in nilai if v.strip().upper() == "INDONESIA"]
                bawaan = nasional if nasional else nilai
            with kolom_w[i % 3]:
                pilih_dim = st.multiselect(c, nilai, default=bawaan, key=f"bps_dim_{hasil['var_id']}_{c}")
            mask &= df[c].isin(pilih_dim)
        if dim_tetap:
            st.caption("Dimensi bernilai tunggal: " + " · ".join(dim_tetap))

        df_view = df[mask].copy()
        st.caption(f"Menampilkan {len(df_view)} dari {len(df)} observasi tabel ini.")

        if df_view.empty:
            st.warning("Tidak ada observasi untuk kombinasi dimensi yang dipilih.")
        else:
            n_non = int(df_view["Nilai (angka)"].isna().sum())
            if n_non:
                st.warning(
                    f"{n_non} observasi tidak bernilai angka. Barisnya tetap tampil di tabel dan unduhan, "
                    "tetapi tidak digambar di grafik."
                )

            # --- Unduh ---
            kolom_unduh = [c for c in df_view.columns if c != "_urut"]
            c1, c2, c3 = st.columns(3)
            c1.download_button("📥 Unduh CSV (tampilan terpilih)", df_view[kolom_unduh].to_csv(index=False).encode("utf-8"),
                               f"BPS_{hasil['var_id']}.csv", "text/csv", key="dl_bps_csv", on_click="ignore")
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as w:
                df_view[kolom_unduh].to_excel(w, index=False, sheet_name="BPS")
            c2.download_button("📊 Unduh Excel (tampilan terpilih)", buf.getvalue(), f"BPS_{hasil['var_id']}.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               key="dl_bps_xl", on_click="ignore")
            c3.download_button("📥 Unduh CSV (semua dimensi)",
                               df[[c for c in df.columns if c != "_urut"]].to_csv(index=False).encode("utf-8"),
                               f"BPS_{hasil['var_id']}_semua_dimensi.csv", "text/csv",
                               key="dl_bps_csv_all", on_click="ignore")

            # --- Grafik: satu garis per kombinasi dimensi; periode turunan menjadi bagian sumbu waktu ---
            multi_periode = df_view["Periode"].nunique() > 1
            df_g = df_view[df_view["Nilai (angka)"].notna()].copy()
            if multi_periode:
                df_g["Waktu"] = df_g["Tahun"] + " " + df_g["Periode"]
                urutan = (
                    df_g.sort_values(["Kode Tahun (th_id)", "_urut"], kind="stable")["Waktu"].drop_duplicates().tolist()
                )
            else:
                tahun_angka = pd.to_numeric(df_g["Tahun"], errors="coerce")
                if tahun_angka.notna().all():
                    df_g["Waktu"] = tahun_angka.astype(int)
                    urutan = None
                else:
                    df_g["Waktu"] = df_g["Tahun"]
                    urutan = df_g.sort_values("Kode Tahun (th_id)", kind="stable")["Waktu"].drop_duplicates().tolist()

            beda = [c for c in [nama_ver, "Variabel Turunan"] if df_view[c].nunique() > 1]
            fig = go.Figure()
            kelompok = df_g.groupby(beda, dropna=False) if beda else [((), df_g)]
            for key, g in kelompok:
                key = key if isinstance(key, tuple) else (key,)
                nama_garis = " · ".join(str(k) for k in key) if beda else "Indonesia (BPS)"
                g = g.sort_values(["Kode Tahun (th_id)", "_urut"], kind="stable")
                fig.add_trace(go.Scatter(
                    x=g["Waktu"], y=g["Nilai (angka)"], mode="lines+markers", name=nama_garis,
                    line=dict(width=2.5), marker=dict(size=6),
                    hovertemplate=f"{nama_garis}<br>%{{x}}<br>Nilai: %{{y:,}}<extra></extra>",
                ))
            eks = dict(title="Periode" if multi_periode else "Tahun")
            if urutan is not None:
                eks.update(type="category", categoryorder="array", categoryarray=urutan, tickangle=-45)
            else:
                eks.update(tickmode="linear")
            fig.update_layout(
                xaxis=eks, yaxis=dict(title=hasil["judul"]),
                hovermode="x unified", margin=dict(l=20, r=20, t=30, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- Sumber ---
            with st.expander("📚 Sumber Data", expanded=False):
                st.markdown("**Basis data:** BPS WebAPI (webapi.bps.go.id), domain nasional.")
                v_info = meta.get("var") or {}
                st.markdown(f"**Subjek:** {v_info.get('subj') or '-'}")
                st.markdown(f"**Satuan:** {v_info.get('unit') or 'tidak dicantumkan oleh API'}")
                definisi = bersihkan_html(v_info.get("def"))
                if definisi:
                    st.markdown("**Definisi:**")
                    st.text(definisi)
                catatan = bersihkan_html(v_info.get("note"))
                if catatan:
                    st.markdown("**Catatan & sumber (dari API):**")
                    st.text(catatan)
                st.markdown(f"**Pembaruan data (last_update):** {meta.get('last_update') or '-'}")
                if v_info.get("decimal") is not None:
                    st.markdown(
                        f"**Petunjuk desimal BPS:** {v_info['decimal']} (hanya petunjuk tampilan dari BPS; "
                        "angka di tabel dan unduhan tidak dibulatkan)."
                    )
                st.markdown(
                    "🔗 [Portal BPS](https://www.bps.go.id/) · [BPS WebAPI](https://webapi.bps.go.id/developer/)"
                )

            with st.expander("📋 Tabel Runtun Waktu Lengkap"):
                tabel = df_view.sort_values(["Kode Tahun (th_id)", "_urut"], ascending=[False, True], kind="stable")
                tampil = tabel.drop(columns=["_urut", "Indikator", "ID Variabel"]).copy()
                tampil["Nilai (angka)"] = tampil["Nilai (angka)"].map(lambda v: "" if pd.isna(v) else repr(float(v)))
                st.dataframe(tampil, use_container_width=True, hide_index=True)
