import datetime
import io
import re
import time

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
    "period", "flowCode", "cmdCode", "classificationCode",
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
def muat_katalog_hs() -> list:
    """Katalog komoditas HS, live dari file referensi Comtrade.
    Gagal = exception (tidak ikut di-cache), bukan daftar kosong."""
    r = _get_dengan_retry(HS_REF_URL)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} saat memuat katalog HS.")
    hasil = r.json().get("results", [])
    if not hasil:
        raise RuntimeError("Katalog HS kosong dari server.")
    return [
        {"id": x["id"], "text": x["text"], "level": x.get("aggrLevel")}
        for x in hasil if x.get("id") and x.get("text")
    ]


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
        "primaryValue": "Nilai (USD)",
        "netWgt": "Berat Bersih (kg)",
        "isNetWgtEstimated": "Berat Diestimasi",
        "isReported": "Dilaporkan Langsung",
        "isAggregate": "Agregat Comtrade",
    })
    kolom = ["Tahun", "Arah", "Kode", "Komoditas", "Klasifikasi", "Nilai (USD)",
             "Berat Bersih (kg)", "Berat Diestimasi", "Dilaporkan Langsung", "Agregat Comtrade"]
    return df[kolom].sort_values(["Kode", "Arah", "Tahun"]).reset_index(drop=True)


# =============================================================================
# 2. KATALOG
# =============================================================================
try:
    katalog = muat_katalog_hs()
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
        "📦 Per komoditas (HS, 1989 sampai terbaru)",
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
        "dan menolak hasil yang terpotong."
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
            thn_mulai = y1.number_input("Dari Tahun:", SITC_MIN[sitc], TAHUN_INI, 1967 if sitc == "S1" else SITC_MIN[sitc], 1, key=f"lg_y1_{sitc}")
            thn_akhir = y2.number_input("Sampai Tahun:", SITC_MIN[sitc], TAHUN_INI, TAHUN_INI, 1, key=f"lg_y2_{sitc}")
            if thn_mulai > thn_akhir:
                st.warning("Tahun awal tidak boleh lebih besar dari tahun akhir.")
            elif terpilih:
                kode_list = list(terpilih)
                jobs = [("HS", t) for t in range(int(thn_mulai), int(thn_akhir) + 1)]
                label_hasil = f"HS | {len(kode_list)} komoditas | {int(thn_mulai)}-{int(thn_akhir)}"
else:
    st.subheader("2. Pengaturan Deret Jangka Panjang")
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
    thn_mulai = y1.number_input("Dari Tahun:", SITC_MIN[sitc], TAHUN_INI, 1967 if sitc == "S1" else SITC_MIN[sitc], 1, key="lg_y1")
    thn_akhir = y2.number_input("Sampai Tahun:", SITC_MIN[sitc], TAHUN_INI, TAHUN_INI, 1, key="lg_y2")
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

    with st.expander("📋 Tabel Data Lengkap"):
        st.dataframe(df.sort_values(["Tahun", "Kode", "Arah"], ascending=[False, True, True]), use_container_width=True)
