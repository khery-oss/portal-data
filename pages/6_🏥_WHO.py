import io
import time

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="WHO Explorer - IndoEcon", layout="wide")

st.title("🏥 WHO (World Health Organization) - Modal Manusia & Kesehatan")
st.markdown(
    "Eksplorasi indikator kesehatan publik dan modal manusia Indonesia dari "
    "**WHO Global Health Observatory (GHO) REST API** secara *real-time* (*100% Live API*). "
    "Katalog indikator, angka, dan rentang ketidakpastian seluruhnya berasal dari API, "
    "tanpa pembulatan dan tanpa pembatasan tahun."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

BASE = "https://ghoapi.azureedge.net/api"
MAX_RETRY = 3
BATAS_WAKTU = 45     # detik per percobaan
MAX_HALAMAN = 200    # pengaman terhadap rantai halaman yang tidak berujung
AKHIRAN_TOTAL = ("_BTSX", "_TOTL")  # kode dimensi "total" yang terbukti ada di GHO

KOLOM_WHO = [
    "TimeDim", "Dim1Type", "Dim1", "Dim2Type", "Dim2", "Dim3Type", "Dim3",
    "DataSourceDimType", "DataSourceDim", "Value", "NumericValue", "Low", "High", "Comments", "Date",
]


# =============================================================================
# 1. LAPISAN API
# =============================================================================
def get_dengan_retry(url: str, params: dict = None) -> requests.Response:
    """GET dengan pengulangan otomatis untuk timeout, koneksi putus, HTTP 429, dan HTTP 5xx.
    Jeda antar percobaan 2 lalu 4 detik. Gagal di percobaan terakhir = exception (tidak ikut di-cache)."""
    for percobaan in range(MAX_RETRY):
        terakhir = percobaan == MAX_RETRY - 1
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=BATAS_WAKTU)
        except requests.RequestException as e:
            if terakhir:
                raise RuntimeError(
                    f"Server WHO tidak merespons setelah {MAX_RETRY} percobaan ({type(e).__name__}). "
                    "Server mungkin sedang lambat, coba lagi beberapa saat."
                )
            time.sleep(2 * (percobaan + 1))
            continue
        if r.status_code == 429 or r.status_code >= 500:
            if terakhir:
                raise RuntimeError(
                    f"Server WHO menolak atau gagal merespons (HTTP {r.status_code}) "
                    f"setelah {MAX_RETRY} percobaan. Coba lagi beberapa saat."
                )
            time.sleep(2 * (percobaan + 1))
            continue
        return r


def ambil_semua(url: str, params: dict = None) -> list:
    """Mengumpulkan semua baris, mengikuti @odata.nextLink bila ada."""
    baris = []
    for _ in range(MAX_HALAMAN):
        r = get_dengan_retry(url, params)
        if r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code} dari server WHO.")
        try:
            js = r.json()
        except ValueError:
            raise RuntimeError("[Format] Respons server WHO bukan JSON.")
        if not isinstance(js, dict) or not isinstance(js.get("value"), list):
            raise RuntimeError("[Format] Bentuk respons server WHO tidak dikenali.")
        baris.extend(js["value"])
        url, params = js.get("@odata.nextLink"), None
        if not url:
            return baris
    raise RuntimeError("Jumlah halaman melebihi batas pengaman. Data ditolak.")


@st.cache_data(ttl=86400, show_spinner=False)
def muat_katalog() -> list:
    """Katalog indikator live dari endpoint Indicator. Gagal = exception (tidak ikut di-cache)."""
    items = ambil_semua(f"{BASE}/Indicator")
    hasil = [
        {"kode": x["IndicatorCode"], "nama": x["IndicatorName"]}
        for x in items if x.get("IndicatorCode") and x.get("IndicatorName")
    ]
    if not hasil:
        raise RuntimeError("Katalog indikator WHO kosong.")
    return hasil


@st.cache_data(ttl=3600, show_spinner=False)
def tarik_who(kode: str) -> list:
    """Semua baris Indonesia untuk satu indikator. Baris negara lain ditolak, bukan disaring diam-diam."""
    baris = ambil_semua(f"{BASE}/{kode}", {"$filter": "SpatialDim eq 'IDN'"})
    for b in baris:
        if b.get("SpatialDim") != "IDN":
            raise RuntimeError(f"Baris dengan kode wilayah {b.get('SpatialDim')} muncul pada penarikan Indonesia. Data ditolak.")
        if b.get("IndicatorCode") not in (None, kode):
            raise RuntimeError(f"Baris indikator {b.get('IndicatorCode')} muncul pada penarikan {kode}. Data ditolak.")
    return [{k: b.get(k) for k in KOLOM_WHO} for b in baris]


def susun_dataframe(rows: list):
    """Mengembalikan (df, kolom_dimensi). Angka apa adanya, tanpa pembulatan, tanpa rata-rata."""
    d = pd.DataFrame(rows)
    df = pd.DataFrame({"Tahun": pd.to_numeric(d["TimeDim"], errors="coerce").astype("Int64")})
    dim_cols = []
    for kol, kol_tipe in (("Dim1", "Dim1Type"), ("Dim2", "Dim2Type"), ("Dim3", "Dim3Type"),
                          ("DataSourceDim", "DataSourceDimType")):
        if kol not in d.columns or d[kol].isna().all():
            continue
        tipe = next(iter(d[kol_tipe].dropna().unique()), None) if kol_tipe in d.columns else None
        nama = str(tipe) if tipe else kol
        if nama in df.columns:
            nama = f"{nama} ({kol})"
        df[nama] = d[kol].fillna("(tidak ada)").astype(str)
        dim_cols.append(nama)
    df["Nilai (angka)"] = pd.to_numeric(d["NumericValue"], errors="coerce")
    df["Nilai (teks WHO)"] = d["Value"]
    df["Batas Bawah"] = pd.to_numeric(d["Low"], errors="coerce")
    df["Batas Atas"] = pd.to_numeric(d["High"], errors="coerce")
    df["Catatan"] = d["Comments"]
    df["Tanggal Rekaman API"] = d["Date"]
    kosong = [c for c in ["Nilai (teks WHO)", "Batas Bawah", "Batas Atas", "Catatan", "Tanggal Rekaman API"]
              if df[c].isna().all()]
    return df.drop(columns=kosong), dim_cols


# =============================================================================
# 2. KATALOG LIVE
# =============================================================================
try:
    with st.spinner("Menghubungkan ke katalog indikator WHO GHO..."):
        katalog = muat_katalog()
except Exception as e:
    st.error(f"Gagal memuat katalog indikator WHO: {e}")
    st.stop()

# =============================================================================
# 3. PENCARIAN & PEMILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pencarian Indikator WHO")
st.markdown(
    f"Katalog WHO GHO memuat **{len(katalog)} indikator** untuk semua negara. "
    "Tidak semuanya punya data Indonesia; hal itu baru diketahui saat data ditarik."
)

# Pintasan kata kunci pencarian (bukan daftar indikator)
TOPIK_CEPAT = {
    "— Pilih Topik Cepat (opsional) —": "",
    "⏳ Harapan Hidup": "life expectancy",
    "⚰️ Angka Kematian": "mortality",
    "🤱 Kesehatan Ibu": "maternal",
    "🥣 Stunting": "stunting",
    "💉 Imunisasi": "immunization",
    "🫁 Tuberkulosis": "tuberculosis",
    "🧑‍⚕️ Tenaga Kesehatan (Dokter)": "doctors",
    "🏥 Tempat Tidur Rumah Sakit": "hospital beds",
    "💧 Sanitasi": "sanitation",
    "⚖️ Obesitas": "obesity",
    "🏛️ Cakupan Kesehatan Semesta": "UHC",
}

c_preset, c_cari = st.columns([1, 2])
with c_preset:
    preset = st.selectbox("⚡ Topik Cepat:", list(TOPIK_CEPAT.keys()))
with c_cari:
    query = st.text_input(
        "🔍 Atau ketik kata kunci (nama indikator atau kode, Bahasa Inggris):",
        value=TOPIK_CEPAT[preset],
        placeholder="Contoh: life expectancy · maternal mortality · stunting · immunization · WHOSIS_000001",
    ).strip()

if not query:
    st.info("Ketik kata kunci untuk mencari indikator.")
    st.stop()

token = query.lower().split()
hasil_cari = [
    k for k in katalog
    if all(t in k["nama"].lower() or t in k["kode"].lower() for t in token)
]
hasil_cari.sort(key=lambda k: (len(k["nama"]), k["nama"]))

if not hasil_cari:
    st.warning(f"Tidak ditemukan indikator untuk kata kunci **'{query}'**. Coba kata kunci lain.")
    st.stop()

st.success(f"Ditemukan **{len(hasil_cari)}** indikator untuk kata kunci **'{query}'**.")

jumlah_nama = {}
for k in hasil_cari:
    jumlah_nama[k["nama"]] = jumlah_nama.get(k["nama"], 0) + 1
labels = [
    k["nama"] if jumlah_nama[k["nama"]] == 1 else f"{k['nama']} | {k['kode']}"
    for k in hasil_cari
]
idx = st.selectbox("Pilih Indikator:", list(range(len(hasil_cari))), format_func=lambda i: labels[i])
pilih = hasil_cari[idx]
kode_ind, nama_ind = pilih["kode"], pilih["nama"]

with st.expander("ℹ️ Metadata & Sumber Resmi WHO", expanded=False):
    st.markdown(f"**Indikator Resmi WHO:** {nama_ind}")
    st.markdown(f"**Kode Seri GHO:** `{kode_ind}`")
    st.markdown("**Cakupan Geografis:** Indonesia (IDN)")
    st.markdown("**Definisi & Metodologi:** katalog API hanya memuat nama indikator; definisi rinci tersedia di portal WHO.")
    st.markdown("🔗 **Portal Sumber Resmi:** [WHO Global Health Observatory](https://www.who.int/data/gho)")

# =============================================================================
# 4. PENARIKAN DATA (hasil disimpan di session_state)
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu Nasional (Indonesia)")
st.caption("Seluruh riwayat tahun yang tersedia di server WHO ditarik secara otomatis.")

if st.button("📊 Ambil Data WHO (Live API)", type="primary"):
    with st.spinner(f"Menarik data untuk '{nama_ind}'..."):
        try:
            st.session_state["who_hasil"] = {"kode": kode_ind, "nama": nama_ind, "rows": tarik_who(kode_ind)}
        except Exception as e:
            st.session_state["who_hasil"] = None
            st.error(f"Gagal menarik data {kode_ind}: {e}")

hasil = st.session_state.get("who_hasil")

if hasil:
    kode, nama, rows = hasil["kode"], hasil["nama"], hasil["rows"]
    st.divider()
    st.markdown(f"**Hasil untuk indikator `{kode}`:** {nama}")

    if not rows:
        st.warning(
            "Server WHO merespons, tetapi tidak ada data Indonesia untuk indikator ini. "
            "Silakan pilih indikator lain."
        )
    else:
        df, dim_cols = susun_dataframe(rows)
        df["Indikator"] = nama
        df["Kode Indikator"] = kode

        tahun_valid = df["Tahun"].dropna()
        rentang = f", tahun {int(tahun_valid.min())} sampai {int(tahun_valid.max())}" if not tahun_valid.empty else ""
        st.success(f"Berhasil menarik **{len(df)}** observasi dari server WHO{rentang}.")

        # --- Pilihan dimensi: tanpa rata-rata, default ke kode total bila ada ---
        mask = pd.Series(True, index=df.index)
        dim_tetap = []
        if dim_cols:
            st.markdown(
                "**Disagregasi (dimensi) pada indikator ini.** Default memakai kode total bila ada; "
                "bila tidak ada kode total, semua nilai dipilih. Tidak ada nilai yang dirata-ratakan."
            )
        kolom_w = st.columns(max(1, min(4, len(dim_cols)))) if dim_cols else []
        i = 0
        for c in dim_cols:
            nilai = sorted(df[c].unique())
            if len(nilai) == 1:
                dim_tetap.append(f"{c} = {nilai[0]}")
                continue
            total_ada = [v for v in nilai if v.upper().endswith(AKHIRAN_TOTAL)]
            bawaan = total_ada if total_ada else nilai
            with kolom_w[i % len(kolom_w)]:
                pilih_dim = st.multiselect(c, nilai, default=bawaan, key=f"who_dim_{kode}_{c}")
            i += 1
            mask &= df[c].isin(pilih_dim)
        if dim_tetap:
            st.caption("Dimensi bernilai tunggal: " + " · ".join(dim_tetap))

        df_view = df[mask].copy()
        st.caption(f"Menampilkan {len(df_view)} dari {len(df)} observasi indikator ini.")

        if df_view.empty:
            st.warning("Tidak ada observasi untuk kombinasi dimensi yang dipilih.")
        else:
            # --- Peringatan: baris tanpa angka dan baris ganda ---
            n_tanpa_angka = int(df_view["Nilai (angka)"].isna().sum())
            if n_tanpa_angka:
                st.warning(
                    f"{n_tanpa_angka} observasi tidak punya nilai numerik dari WHO. "
                    "Barisnya tetap tampil di tabel dan unduhan, tetapi tidak digambar di grafik."
                )
            dup = df_view.duplicated(subset=["Tahun"] + dim_cols, keep=False)
            if dup.any():
                st.warning(
                    f"{int(dup.sum())} baris punya tahun dan kombinasi dimensi yang sama. "
                    "Semuanya tetap ditampilkan tanpa diratakan."
                )

            # --- Unduh ---
            c1, c2, c3 = st.columns(3)
            c1.download_button("📥 Unduh CSV (tampilan terpilih)", df_view.to_csv(index=False).encode("utf-8"),
                               f"WHO_Indonesia_{kode}.csv", "text/csv", key="dl_who_csv", on_click="ignore")
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as w:
                df_view.to_excel(w, index=False, sheet_name="WHO Indonesia")
            c2.download_button("📊 Unduh Excel (tampilan terpilih)", buf.getvalue(), f"WHO_Indonesia_{kode}.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               key="dl_who_xl", on_click="ignore")
            c3.download_button("📥 Unduh CSV (semua dimensi)", df.to_csv(index=False).encode("utf-8"),
                               f"WHO_Indonesia_{kode}_semua_dimensi.csv", "text/csv",
                               key="dl_who_csv_all", on_click="ignore")

            # --- Grafik: satu garis per kombinasi dimensi ---
            beda = [c for c in dim_cols if df_view[c].nunique() > 1]
            fig = go.Figure()
            kelompok = df_view.groupby(beda, dropna=False) if beda else [((), df_view)]
            for key, g in kelompok:
                key = key if isinstance(key, tuple) else (key,)
                nama_garis = " · ".join(str(k) for k in key) if beda else "Indonesia (WHO GHO)"
                g = g[g["Nilai (angka)"].notna() & g["Tahun"].notna()].sort_values("Tahun")
                if g.empty:
                    continue
                rentang_teks = [
                    "" if pd.isna(lo) or pd.isna(hi) else f"Rentang WHO: {repr(float(lo))} sampai {repr(float(hi))}"
                    for lo, hi in zip(g.get("Batas Bawah", pd.Series([None] * len(g), index=g.index)),
                                      g.get("Batas Atas", pd.Series([None] * len(g), index=g.index)))
                ]
                fig.add_trace(go.Scatter(
                    x=g["Tahun"].astype(int), y=g["Nilai (angka)"],
                    mode="lines+markers", name=nama_garis,
                    line=dict(width=2.8), marker=dict(size=7),
                    customdata=rentang_teks,
                    hovertemplate=f"{nama_garis}<br>Tahun %{{x}}<br>Nilai: %{{y:,}}<br>%{{customdata}}<extra></extra>",
                ))
            fig.update_layout(
                xaxis=dict(title="Tahun", tickmode="linear"),
                yaxis=dict(title=nama),
                hovermode="x unified", margin=dict(l=20, r=20, t=30, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- Sumber data: sumber asli diambil dari kolom Catatan yang dikirim API ---
            with st.expander("📚 Sumber Data", expanded=False):
                st.markdown("**Basis data:** WHO Global Health Observatory (GHO) OData API.")
                sumber_asli = (
                    sorted({str(x) for x in df_view["Catatan"].dropna()}) if "Catatan" in df_view.columns else []
                )
                if sumber_asli:
                    st.markdown("**Sumber asli menurut API (kolom Catatan):**")
                    for sa in sumber_asli:
                        st.markdown(f"- {sa}")
                else:
                    st.markdown("API tidak mengirim catatan sumber untuk observasi yang ditampilkan.")
                if "Tanggal Rekaman API" in df_view.columns:
                    tgl = sorted({str(x) for x in df_view["Tanggal Rekaman API"].dropna()})
                    if tgl:
                        st.markdown("**Tanggal rekaman API:** " + ", ".join(tgl))

            with st.expander("📋 Tabel Runtun Waktu Lengkap"):
                tabel = df_view.drop(columns=["Indikator", "Kode Indikator"]).sort_values("Tahun", ascending=False)
                tampil = tabel.copy()
                for kol in ("Nilai (angka)", "Batas Bawah", "Batas Atas"):
                    if kol in tampil.columns:
                        tampil[kol] = tampil[kol].map(lambda v: "" if pd.isna(v) else repr(float(v)))
                st.dataframe(tampil, use_container_width=True, hide_index=True)
