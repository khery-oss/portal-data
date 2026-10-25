import datetime
import io
import re
import time
from urllib.parse import urlencode
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="Perdagangan Internasional - Indonesia", layout="wide")

st.title("🚢 Perdagangan Internasional Indonesia (UN Comtrade)")
st.markdown(
    "Eksplorasi ekspor dan impor Indonesia per komoditas dari **UN Comtrade** "
    "secara *real-time* (*100% Live API*). Data ditampilkan apa adanya dari sumber, "
    "tanpa pembulatan, rata-rata, atau penyambungan klasifikasi otomatis."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

BASE = "https://comtradeapi.un.org/public/v1/preview/C/A"
HS_REF_URL = "https://comtradeapi.un.org/files/v1/app/reference/HS.json"
REF_BASE = "https://comtradeapi.un.org/files/v1/app/reference"
SITC_MAKS = 1989  # tahun terakhir SITC pada mode per komoditas

REPORTER_IDN = 360
BATAS_BARIS = 500      # batas baris endpoint preview; hasil yang mencapai ini dianggap terpotong
KODE_PER_PANGGILAN = 100  # 100 kode x 2 arah = maksimal 200 baris, aman di bawah batas
JEDA_DETIK = 2         # jeda antar panggilan yang benar-benar ke server (bukan dari cache)
MAX_RETRY = 5
TAHUN_INI = datetime.date.today().year

HS_MIN, HS_MULAI_HS_DALAM_GABUNGAN = 1989, 1989
SITC_MIN = {"S1": 1962, "S2": 1979}
SITC_AKHIR = 1988      # tahun terakhir yang diambil dari SITC pada mode gabungan

KOLOM_SUMBER = [
    "period", "flowCode", "cmdCode", "classificationCode", "isOriginalClassification",
    "primaryValue", "netWgt", "isNetWgtEstimated", "isReported", "isAggregate",
]

# =============================================================================
# 1. LAPISAN API
# =============================================================================
def _get_dengan_retry(url: str) -> requests.Response:
    """GET dengan retry otomatis saat rate limit (HTTP 429)."""
    for _ in range(MAX_RETRY):
        r = requests.get(url, headers=HEADERS, timeout=60)
        if r.status_code == 429:
            m = re.search(r"in (\d+) second", r.text)
            time.sleep(int(m.group(1)) + 1 if m else 4)
            continue
        return r
    raise RuntimeError("Rate limit Comtrade (HTTP 429) tidak reda setelah beberapa percobaan.")


@st.cache_data(ttl=86400, show_spinner=False)
def muat_katalog(klasifikasi: str) -> list:
    """Katalog komoditas live untuk HS, S1, atau S2 dari file referensi Comtrade.
    Gagal = exception (tidak ikut di-cache). Nama kolom level berbeda antar file
    (aggrLevel di HS, aggrlevel di SITC), jadi keduanya dibaca."""
    r = _get_dengan_retry(f"{REF_BASE}/{klasifikasi}.json")
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} saat memuat katalog {klasifikasi}.")
    hasil = r.json().get("results", [])
    if not hasil:
        raise RuntimeError(f"Katalog {klasifikasi} kosong dari server.")
    keluaran = []
    for x in hasil:
        if not (x.get("id") and x.get("text")):
            continue
        lv = x.get("aggrLevel", x.get("aggrlevel"))
        try:
            lv = int(lv)
        except (TypeError, ValueError):
            lv = None
        keluaran.append({"id": str(x["id"]), "text": x["text"], "level": lv})
    return keluaran


def _validasi(data: list, tahun: int):
    """Filter ketat: hanya baris total (dunia, semua moda, semua bea cukai),
    dan tepat satu baris per (arah, komoditas). Pelanggaran = error, bukan diratakan."""
    terlihat = set()
    for d in data:
        if (
            d.get("reporterCode") != REPORTER_IDN
            or d.get("partnerCode") != 0
            or d.get("partner2Code") != 0
            or d.get("motCode") != 0
            or d.get("customsCode") != "C00"
            or d.get("flowCode") not in ("X", "M")
            or str(d.get("period")) != str(tahun)
        ):
            raise ValueError(
                f"Baris tidak sesuai filter total (tahun {tahun}, kode {d.get('cmdCode')}, "
                f"arah {d.get('flowCode')}). Data ditolak, bukan diratakan."
            )
        kunci = (d["flowCode"], d["cmdCode"])
        if kunci in terlihat:
            raise ValueError(
                f"Lebih dari satu baris untuk tahun {tahun}, kode {d['cmdCode']}, arah {d['flowCode']}. "
                "Data ditolak agar tidak terjadi penjumlahan ganda."
            )
        terlihat.add(kunci)


@st.cache_data(ttl=86400, show_spinner=False)
def tarik_satu_tahun(klasifikasi: str, tahun: int, kode: tuple) -> list:
    """Satu panggilan API = satu klasifikasi, satu tahun, sekelompok kode.
    Hanya hasil sukses yang di-cache; error tidak pernah disimpan."""
    url = (
        f"{BASE}/{klasifikasi}?reporterCode={REPORTER_IDN}&partnerCode=0&partner2Code=0"
        f"&motCode=0&customsCode=C00&flowCode=X,M&period={tahun}&cmdCode={','.join(kode)}"
    )
    r = _get_dengan_retry(url)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:150]}")
    js = r.json()
    if js.get("error"):
        raise RuntimeError(f"API error: {js['error']}")
    data = js.get("data") or []
    if len(data) >= BATAS_BARIS or (js.get("count") or 0) >= BATAS_BARIS:
        raise RuntimeError(
            f"Hasil mencapai batas {BATAS_BARIS} baris dan kemungkinan terpotong. Data ditolak."
        )
    _validasi(data, tahun)
    time.sleep(JEDA_DETIK)
    return [{k: d.get(k) for k in KOLOM_SUMBER} for d in data]


def tarik_banyak_tahun(jobs: list, kode_list: list):
    """jobs = [(klasifikasi, tahun), ...]. Mengembalikan (baris, tahun_kosong, tahun_gagal)."""
    potongan = [tuple(kode_list[i:i + KODE_PER_PANGGILAN]) for i in range(0, len(kode_list), KODE_PER_PANGGILAN)]
    semua, kosong, gagal = [], [], []
    bar = st.progress(0.0, text="Memulai penarikan...")
    total = len(jobs)
    for i, (klas, tahun) in enumerate(jobs):
        bar.progress(i / total, text=f"Menarik {klas} tahun {tahun} ({i + 1}/{total})...")
        sementara = []
        try:
            for ch in potongan:
                sementara.extend(tarik_satu_tahun(klas, tahun, ch))
            if sementara:
                semua.extend(sementara)
            else:
                kosong.append(tahun)
        except Exception as e:
            gagal.append((tahun, str(e)[:200]))
    bar.empty()
    return semua, kosong, gagal


def susun_dataframe(rows: list, peta_nama: dict) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["Tahun"] = df["period"].astype(int)
    df["Arah"] = df["flowCode"].map({"X": "Ekspor", "M": "Impor"})
    df["Kode"] = df["cmdCode"]
    df["Komoditas"] = df["cmdCode"].map(lambda c: peta_nama.get(c, c))
    df = df.rename(columns={
        "classificationCode": "Klasifikasi",
        "isOriginalClassification": "Klasifikasi Asli",
        "primaryValue": "Nilai (USD)",
        "netWgt": "Berat Bersih (kg)",
        "isNetWgtEstimated": "Berat Diestimasi",
        "isReported": "Dilaporkan Langsung",
        "isAggregate": "Agregat Comtrade",
    })
    kolom = ["Tahun", "Arah", "Kode", "Komoditas", "Klasifikasi", "Klasifikasi Asli",
             "Nilai (USD)", "Berat Bersih (kg)", "Berat Diestimasi",
             "Dilaporkan Langsung", "Agregat Comtrade"]
    return df[kolom].sort_values(["Kode", "Arah", "Tahun"]).reset_index(drop=True)

# =============================================================================
# 2. KATALOG
# =============================================================================
try:
    katalog = muat_katalog("HS")
except Exception as e:
    katalog = None
    st.error(f"Gagal memuat katalog komoditas HS dari Comtrade: {e}")

peta_nama = {k["id"]: k["text"] for k in katalog} if katalog else {}

# =============================================================================
# 3. KONTROL
# =============================================================================
st.subheader("1. Pilih Mode")
mode = st.radio(
    "Mode:",
    [
        "📦 Per komoditas, HS (1989 sampai terbaru)",
        "🏛️ Per komoditas, SITC (1962 sampai 1989)",
        "📈 Total perdagangan jangka panjang (SITC lalu HS)",
    ],
    horizontal=True,
)

with st.expander("ℹ️ Sumber, Cakupan & Catatan Metodologi", expanded=False):
    st.markdown(
        "- **Sumber:** UN Comtrade (endpoint publik *preview*), pelapor Indonesia (M49 = 360), mitra dagang: seluruh dunia.\n"
        "- **Nilai:** `primaryValue` apa adanya (USD). Secara konvensi ekspor tercatat FOB dan impor CIF.\n"
        "- **Klasifikasi:** kolom `Klasifikasi` menunjukkan revisi HS/SITC aslinya (H0 sampai H6, S1, S2). "
        "Kode 6 digit dapat berubah antarrevisi, dan tidak ada penyambungan otomatis.\n"
        "- **Flag:** `Agregat Comtrade` berarti angka dihitung Comtrade dari rincian, bukan dilaporkan langsung. "
        "Berat bernilai 0 dapat berarti tidak tersedia di sumber.\n"
        "- **Perbedaan dengan WDI:** angka total Comtrade dapat sedikit berbeda dari indikator World Bank WDI untuk tahun yang sama.\n"
        "- **Batas endpoint:** 1 periode per panggilan dan maksimal 500 baris. Modul menarik per tahun lalu menggabungkannya, "
        "dan menolak hasil yang terpotong.\n"
        "- **Verifikasi langsung:** buka [UN Comtrade Plus untuk Indonesia]"
        "(https://comtradeplus.un.org/TradeFlow?Frequency=A&Flows=X&CommodityCodes=TOTAL"
        "&Partners=0&Reporters=360&period=2022&AggregateBy=none&BreakdownMode=plus) "
        "dan bandingkan dengan tabel di modul. Reporter sudah diatur ke Indonesia (360) dan mitra dagang ke seluruh dunia; "
        "ubah tahun, arus, dan kode komoditas langsung di halaman tersebut. "
        "Situs membulatkan tampilan angka, sedangkan modul menampilkan nilai penuh dari API."
    )

jobs, kode_list, label_hasil = [], [], ""

if mode.startswith("📦"):
    if not katalog:
        st.stop()
    st.subheader("2. Pilih Komoditas")
    c1, c2 = st.columns([2, 1])
    with c1:
        query = st.text_input(
            "🔍 Cari komoditas (kode atau kata kunci Bahasa Inggris):",
            placeholder="Contoh: palm oil · coal · 1511 · 2701 · rubber · textile",
        ).strip()
    with c2:
        level = st.selectbox("Tingkat kode:", ["Semua", "2 digit (bab)", "4 digit (pos)", "6 digit (subpos)"])

    if not query:
        st.info("Ketik kata kunci atau kode HS untuk mencari komoditas.")
    else:
        token = query.lower().split()
        peta_level = {"2 digit (bab)": 2, "4 digit (pos)": 4, "6 digit (subpos)": 6}
        hasil_cari = [
            k for k in katalog
            if all(t in k["text"].lower() or t in k["id"].lower() for t in token)
            and (level == "Semua" or k["level"] == peta_level[level])
        ]
        if not hasil_cari:
            st.warning(f"Tidak ditemukan komoditas untuk '{query}'.")
        else:
            st.success(f"Ditemukan **{len(hasil_cari)}** entri.")
            terpilih = st.multiselect(
                "Pilih satu atau lebih komoditas:",
                options=[k["id"] for k in hasil_cari],
                format_func=lambda i: peta_nama.get(i, i),
            )
            st.subheader("3. Rentang Tahun")
            y1, y2 = st.columns(2)
            thn_mulai = y1.number_input("Dari Tahun:", HS_MIN, TAHUN_INI, HS_MIN, 1, key="hs_y1")
            thn_akhir = y2.number_input("Sampai Tahun:", HS_MIN, TAHUN_INI, TAHUN_INI, 1, key="hs_y2")
            if thn_mulai > thn_akhir:
                st.warning("Tahun awal tidak boleh lebih besar dari tahun akhir.")
            elif terpilih:
                kode_list = list(terpilih)
                jobs = [("HS", t) for t in range(int(thn_mulai), int(thn_akhir) + 1)]
                label_hasil = f"HS | {len(kode_list)} komoditas | {int(thn_mulai)}-{int(thn_akhir)}"

elif mode.startswith("🏛"):
    st.subheader("2. Pilih Revisi SITC dan Komoditas")
    st.caption(
        "Kode SITC **tidak sama** dengan kode HS (misalnya minyak sawit: 1511 di HS, 4222 di SITC Rev.1, "
        "4242 di SITC Rev.2). Tidak ada penyambungan otomatis antar klasifikasi. Untuk melanjutkan komoditas "
        "yang sama ke periode HS, cari kodenya sendiri di mode HS. Kolom *Klasifikasi Asli* menunjukkan "
        "apakah angka berasal dari klasifikasi aslinya atau hasil konversi Comtrade."
    )
    sitc_rev = st.selectbox(
        "Revisi SITC:",
        ["S1", "S2"],
        format_func=lambda s: "SITC Rev.1 (1962 sampai 1989, lengkap dua arah sejak 1967)" if s == "S1"
        else "SITC Rev.2 (1979 sampai 1989)",
        key="sitc_rev_pilih",
    )
    try:
        kat_sitc = muat_katalog(sitc_rev)
    except Exception as e:
        kat_sitc = None
        st.error(f"Gagal memuat katalog {sitc_rev} dari Comtrade: {e}")

    if kat_sitc:
        peta_nama = {k["id"]: k["text"] for k in kat_sitc}
        c1, c2 = st.columns([2, 1])
        with c1:
            query_s = st.text_input(
                "🔍 Cari komoditas (kode atau kata kunci Bahasa Inggris):",
                placeholder="Contoh: palm oil · rubber · coffee · 4222",
                key="q_sitc",
            ).strip()
        with c2:
            level_opsi = sorted({k["level"] for k in kat_sitc if k["level"] is not None})
            level_s = st.selectbox(
                "Tingkat kode:", ["Semua"] + level_opsi,
                format_func=lambda v: v if v == "Semua" else f"Level {v}",
                key="lv_sitc",
            )
        if not query_s:
            st.info("Ketik kata kunci atau kode SITC untuk mencari komoditas.")
        else:
            token_s = query_s.lower().split()
            hasil_s = [
                k for k in kat_sitc
                if all(t in k["text"].lower() or t in k["id"].lower() for t in token_s)
                and (level_s == "Semua" or k["level"] == level_s)
            ]
            if not hasil_s:
                st.warning(f"Tidak ditemukan komoditas untuk '{query_s}'.")
            else:
                st.success(f"Ditemukan **{len(hasil_s)}** entri.")
                terpilih_s = st.multiselect(
                    "Pilih satu atau lebih komoditas:",
                    options=[k["id"] for k in hasil_s],
                    format_func=lambda i: peta_nama.get(i, i),
                    key="ms_sitc",
                )
                st.subheader("3. Rentang Tahun")
                y1, y2 = st.columns(2)
                thn_mulai = y1.number_input("Dari Tahun:", SITC_MIN[sitc_rev], SITC_MAKS, SITC_MIN[sitc_rev], 1, key=f"sitc_y1_{sitc_rev}")
                thn_akhir = y2.number_input("Sampai Tahun:", SITC_MIN[sitc_rev], SITC_MAKS, SITC_MAKS, 1, key=f"sitc_y2_{sitc_rev}")
                if thn_mulai > thn_akhir:
                    st.warning("Tahun awal tidak boleh lebih besar dari tahun akhir.")
                elif terpilih_s:
                    kode_list = list(terpilih_s)
                    jobs = [(sitc_rev, t) for t in range(int(thn_mulai), int(thn_akhir) + 1)]
                    label_hasil = f"{sitc_rev} | {len(kode_list)} komoditas | {int(thn_mulai)}-{int(thn_akhir)}"
                    
    else:
    st.subheader("3. Pengaturan Deret Jangka Panjang")
    st.caption(
        "Total seluruh komoditas. Tahun sampai 1988 diambil dari SITC, tahun 1989 dan seterusnya dari HS. "
        "Dua klasifikasi ini **tidak disambung** dan ditandai terpisah di grafik."
    )
    sitc = st.selectbox(
        "Revisi SITC untuk tahun sebelum 1989:",
        ["S1", "S2"],
        format_func=lambda s: "SITC Rev.1 (data sejak 1962, lengkap dua arah sejak 1967)" if s == "S1"
        else "SITC Rev.2 (data sejak 1979)",
    )
    y1, y2 = st.columns(2)
    thn_mulai = y1.number_input("Dari Tahun:", SITC_MIN[sitc], TAHUN_INI, 1967 if sitc == "S1" else SITC_MIN[sitc], 1, key=f"lg_y1_{sitc}")
    thn_akhir = y2.number_input("Sampai Tahun:", SITC_MIN[sitc], TAHUN_INI, TAHUN_INI, 1, key=f"lg_y2_{sitc}")
    if thn_mulai > thn_akhir:
        st.warning("Tahun awal tidak boleh lebih besar dari tahun akhir.")
    else:
        kode_list = ["TOTAL"]
        jobs = [
            (sitc if t <= SITC_AKHIR else "HS", t)
            for t in range(int(thn_mulai), int(thn_akhir) + 1)
        ]
        label_hasil = f"TOTAL | {sitc} lalu HS | {int(thn_mulai)}-{int(thn_akhir)}"

# =============================================================================
# 4. PENARIKAN (hasil disimpan di session_state agar tidak hilang saat unduh)
# =============================================================================
if jobs and kode_list:
    perkiraan = len(jobs) * ((len(kode_list) - 1) // KODE_PER_PANGGILAN + 1) * (JEDA_DETIK + 1)
    st.caption(
        f"Perkiraan waktu penarikan pertama: ±{perkiraan // 60} menit {perkiraan % 60} detik "
        "(tahun yang sudah pernah ditarik diambil dari cache sementara)."
    )
    if st.button("📊 Tarik Data Comtrade", type="primary"):
        rows, kosong, gagal = tarik_banyak_tahun(jobs, kode_list)
        if not rows:
            st.session_state["comtrade_hasil"] = None
            st.warning("Tidak ada data yang berhasil ditarik untuk pilihan ini.")
            if gagal:
                st.error("Tahun gagal: " + "; ".join(f"{t} ({m})" for t, m in gagal))
        else:
            st.session_state["comtrade_hasil"] = {
                "df": susun_dataframe(rows, peta_nama),
                "kosong": kosong,
                "gagal": gagal,
                "label": label_hasil,
                "kode": kode_list,
                "long_run": mode.startswith("📈"),
            }

# =============================================================================
# 5. TAMPILAN HASIL
# =============================================================================
hasil = st.session_state.get("comtrade_hasil")
if hasil:
    df = hasil["df"]
    st.divider()
    st.success(f"Berhasil menarik **{len(df)}** observasi. ({hasil['label']})")

    if hasil["gagal"]:
        st.error(
            "⚠️ Deret **tidak lengkap**: tahun berikut gagal ditarik dan tidak ada di tabel atau grafik. "
            "Klik tombol tarik lagi untuk mencoba ulang.\n\n"
            + "\n".join(f"- {t}: {m}" for t, m in hasil["gagal"])
        )
    if hasil["kosong"]:
        st.info("Tahun tanpa data di sumber: " + ", ".join(str(t) for t in sorted(hasil["kosong"])))

    # Tahun dengan satu arah saja (sepihak) per kode
    sepihak = (
        df.groupby(["Kode", "Tahun"])["Arah"].nunique().reset_index()
        .query("Arah == 1")
    )
    if not sepihak.empty:
        rinci = []
        for kode, g in sepihak.groupby("Kode"):
            arah_ada = df[(df["Kode"] == kode) & (df["Tahun"].isin(g["Tahun"]))].groupby("Tahun")["Arah"].first()
            rinci.append(f"{kode}: " + ", ".join(f"{t} ({a} saja)" for t, a in arah_ada.items()))
        st.warning("Tahun dengan data satu arah saja:\n\n" + "\n\n".join(rinci))

    kode_tanpa_data = [k for k in hasil["kode"] if k not in set(df["Kode"])]
    if kode_tanpa_data:
        st.info("Kode tanpa data sama sekali pada rentang ini: " + ", ".join(kode_tanpa_data))

    c1, c2 = st.columns(2)
    c1.download_button(
        "📥 Unduh CSV", df.to_csv(index=False).encode("utf-8"),
        "Comtrade_Indonesia.csv", "text/csv", key="dl_ct_csv",
    )
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Comtrade Indonesia")
    c2.download_button(
        "📊 Unduh Excel (.xlsx)", buf.getvalue(), "Comtrade_Indonesia.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl_ct_xl",
    )

    fig = go.Figure()
    for (kode, arah), g in df.groupby(["Kode", "Arah"]):
        g = g.sort_values("Tahun")
        nama = f"{kode} {arah}" if kode != "TOTAL" else f"Total {arah}"
        fig.add_trace(go.Scatter(
            x=g["Tahun"], y=g["Nilai (USD)"], mode="lines+markers", name=nama,
            line=dict(width=2.5, dash="solid" if arah == "Ekspor" else "dash"),
            marker=dict(size=6),
            customdata=g["Klasifikasi"],
            hovertemplate=f"{nama}<br>Tahun %{{x}}<br>Nilai: %{{y:,.0f}} USD<br>Klasifikasi: %{{customdata}}<extra></extra>",
        ))
    if hasil["long_run"] and df["Tahun"].min() <= SITC_AKHIR < df["Tahun"].max():
        fig.add_vline(
            x=SITC_AKHIR + 0.5, line_dash="dot", line_color="gray",
            annotation_text="Pergantian klasifikasi: SITC → HS", annotation_position="top left",
        )
    fig.update_layout(
        xaxis=dict(title="Tahun"), yaxis=dict(title="Nilai (USD)"),
        hovermode="x unified", margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Tautan verifikasi dinamis ke UN Comtrade Plus (hanya tahun HS) ---
    tahun_hs = sorted(df.loc[df["Klasifikasi"].astype(str).str.startswith("H"), "Tahun"].unique())
    if tahun_hs:
        def url_comtrade(kode: str) -> str:
            q = {
                "Frequency": "A",
                "Flows": "X,M",
                "CommodityCodes": kode,
                "Partners": "0",
                "Reporters": "360",
                "period": ",".join(str(t) for t in tahun_hs),
                "AggregateBy": "none",
                "BreakdownMode": "plus",
            }
            return "https://comtradeplus.un.org/TradeFlow?" + urlencode(q, safe=",")

        with st.expander("🔗 Verifikasi langsung di UN Comtrade Plus", expanded=False):
            st.caption(
                "Tautan membuka UN Comtrade Plus dengan pelapor Indonesia, mitra dunia, "
                "arus ekspor dan impor, serta tahun HS yang sedang ditampilkan di atas. "
                "Tahun SITC (sebelum 1989) tidak tercakup. "
                "Situs UN Comtrade Plus dapat meminta pembuatan akun gratis untuk melihat tabel. "
                "Situs membulatkan tampilan angka, sedangkan modul menampilkan nilai penuh dari API."
            )
            for kode in sorted(df["Kode"].unique()):
                            nama_df = df.drop_duplicates("Kode").set_index("Kode")["Komoditas"]
            for kode in sorted(df["Kode"].unique()):
                st.markdown(f"- [{kode}]({url_comtrade(kode)}) {nama_df.get(kode, '')}")
    
    with st.expander("📋 Tabel Data Lengkap"):
        st.dataframe(df.sort_values(["Tahun", "Kode", "Arah"], ascending=[False, True, True]), use_container_width=True)
