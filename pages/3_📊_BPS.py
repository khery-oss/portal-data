import math
import io
import requests
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ──────────────────────────────────────────────────────────────────────────────
# KONSTANTA
# ──────────────────────────────────────────────────────────────────────────────

BASE_URL  = "https://webapi.bps.go.id/v1/api/list"
DOMAIN    = "0000"
LANG      = "ind"
YEAR_MIN  = 1971   # tahun terdini yang relevan secara umum di BPS
YEAR_MAX  = 2030   # batas atas aman untuk slider UI

# ──────────────────────────────────────────────────────────────────────────────
# UTILITAS TAHUN
# ──────────────────────────────────────────────────────────────────────────────

def tahun_to_th(tahun: int) -> int:
    """Konversi tahun Masehi ke ID internal BPS (th = tahun - 1900)."""
    return tahun - 1900


def th_to_tahun(th: int) -> int:
    """Konversi ID internal BPS kembali ke tahun Masehi."""
    return th + 1900


def build_th_param(tahun_awal: int, tahun_akhir: int) -> str:
    """
    Bangun parameter `th` untuk endpoint data BPS.
    Format rentang: '{th_awal}:{th_akhir}'
    """
    return f"{tahun_to_th(tahun_awal)}:{tahun_to_th(tahun_akhir)}"


# ──────────────────────────────────────────────────────────────────────────────
# LAYER HTTP — satu titik akses, penanganan error terpusat
# ──────────────────────────────────────────────────────────────────────────────

def _get(url: str, timeout: int = 20) -> dict:
    """
    GET ke endpoint BPS, kembalikan dict JSON mentah.
    Lempar RuntimeError dengan pesan diagnostik asli jika gagal.
    """
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}") from e
    except requests.exceptions.ConnectionError as e:
        raise RuntimeError(f"Koneksi gagal ke BPS: {e}") from e
    except requests.exceptions.Timeout:
        raise RuntimeError("Timeout: server BPS tidak merespons dalam batas waktu.")
    except Exception as e:
        raise RuntimeError(f"Error tak terduga: {e}") from e


# ──────────────────────────────────────────────────────────────────────────────
# LAYER KATALOG (dengan cache Streamlit)
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_all_subjects(api_key: str) -> list[dict]:
    """
    Tarik seluruh subjek BPS secara dinamis dengan iterasi pagination.
    Merespons struktur array bersarang khusus dari WebAPI BPS.
    """
    subjects: list[dict] = []
    page = 1

    while True:
        url = (
            f"{BASE_URL}/model/subject/domain/{DOMAIN}"
            f"/page/{page}/key/{api_key}/"
        )
        data = _get(url)

        # BPS menggunakan indikator data-availability
        if data.get("data-availability") != "available":
            break

        # BPS meletakkan list data di indeks ke-1 array 'data'
        raw_data = data.get("data", [])
        if len(raw_data) > 1:
            items = raw_data[1]
        else:
            break

        for item in items:
            # Key asli dari BPS adalah 'sub_id' dan 'title'
            subjects.append({
                "subject_id": str(item.get("sub_id", "")),
                "label": item.get("title", "Tanpa Judul"),
            })

        # Ambil total halaman dari metadata di indeks ke-0
        metadata = raw_data[0] if len(raw_data) > 0 else {}
        total_pages = int(metadata.get("pages", 1))

        if page >= total_pages:
            break
        
        page += 1

    return subjects


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_variables(api_key: str, subject_id: str, max_pages: int = 5) -> list[dict]:
    """
    Tarik variabel/indikator untuk subjek tertentu.
    """
    variables: list[dict] = []

    for page in range(1, max_pages + 1):
        url = (
            f"{BASE_URL}/model/var/domain/{DOMAIN}"
            f"/subject/{subject_id}/page/{page}/key/{api_key}/"
        )
        data = _get(url)

        if data.get("data-availability") != "available":
            break

        raw_data = data.get("data", [])
        if len(raw_data) > 1:
            items = raw_data[1]
        else:
            break

        for item in items:
            # Key asli dari BPS adalah 'var_id' dan 'title'
            variables.append({
                "var_id": str(item.get("var_id", "")),
                "label": item.get("title", "Tanpa Judul"),
            })

        metadata = raw_data[0] if len(raw_data) > 0 else {}
        total_pages = int(metadata.get("pages", 1))

        if page >= total_pages:
            break

    return variables


# ──────────────────────────────────────────────────────────────────────────────
# LAYER DATA DERET WAKTU
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_timeseries(
    api_key:     str,
    var_id:      str,
    tahun_awal:  int,
    tahun_akhir: int,
) -> tuple[pd.DataFrame, dict]:
    """
    Tarik data deret waktu dari endpoint model/data BPS.
    """
    th_param = build_th_param(tahun_awal, tahun_akhir)
    url = (
        f"{BASE_URL}/model/data/lang/{LANG}/domain/{DOMAIN}"
        f"/var/{var_id}/th/{th_param}/key/{api_key}/"
    )
    raw = _get(url)

    # 1. Perbaikan Logika Pengecekan Status (Sesuai Standar BPS)
    availability = raw.get("data-availability", "")
    if availability not in ("available", "list-available"):
        msg = raw.get("message", raw.get("msg", "Data tidak tersedia di database BPS untuk tahun tersebut."))
        raise RuntimeError(f"{msg}")

    # 2. Perbaikan Struktur Pembacaan JSON (Komponen ada di Root, bukan di dalam 'data')
    datacontent = raw.get("datacontent", {})
    if not datacontent:
         raise RuntimeError("Respons API berhasil, namun tabel data (datacontent) kosong.")

    vervar_list = raw.get("vervar", [])
    tahun_list  = raw.get("tahun", [])
    turvar_list = raw.get("turvar", [])
    turtahun_list = raw.get("turtahun", [{"val": "0", "label": "Tahunan"}])

    if not tahun_list:
        raise RuntimeError("BPS tidak mengembalikan parameter tahun pada rentang yang diminta.")

    # 3. Iterasi Pola Kunci Komposit Dinamis BPS
    records = []
    
    # Fallback/Dummy iterasi agar loop berjalan meskipun dimensi rincian kosong
    v_iter = vervar_list if vervar_list else [{"val": "", "label": "Nasional"}]
    t_iter = tahun_list if tahun_list else [{"val": "", "label": ""}]
    tv_iter = turvar_list if turvar_list else [{"val": "", "label": ""}]
    tth_iter = turtahun_list if turtahun_list else [{"val": "", "label": ""}]

    for v in v_iter:
        for tv in tv_iter:
            for th in t_iter:
                for tth in tth_iter:
                    # Rumus kunci komposit (Composite Key) khas BPS: vervar + var_id + turvar + tahun + turtahun
                    # Kita juga buat key cadangan (key2) jika BPS merotasi posisi var_id
                    key1 = f"{v.get('val','')}{var_id}{tv.get('val','')}{th.get('val','')}{tth.get('val','')}"
                    key2 = f"{var_id}{tv.get('val','')}{th.get('val','')}{tth.get('val','')}{v.get('val','')}"
                    
                    raw_val = datacontent.get(key1, datacontent.get(key2, None))
                    
                    # Ekstraksi dan Pembersihan
                    if raw_val is not None:
                        nilai = _parse_nilai(raw_val)
                        
                        # Ambil nama kategori dan bersihkan HTML tag <b> yang sering disisipkan BPS
                        kategori_utama = v.get("label", "Nasional").replace("<b>", "").replace("</b>", "").strip()
                        
                        # Gabungkan dengan rincian (Contoh: "ACEH - Laki-laki")
                        if tv.get("label"):
                            kategori_utama = f"{kategori_utama} - {tv['label']}"
                            
                        records.append({
                            "Tahun": int(th.get("label", 0)),
                            "Kategori": kategori_utama,
                            "Nilai": nilai,
                        })

    if not records:
        raise RuntimeError("Data berhasil ditarik, namun pola kunci pemetaan matriks BPS tidak dikenali oleh sistem.")

    df_raw = pd.DataFrame(records)

    # 4. Pivot tabel untuk UI
    df_pivot = (
        df_raw
        .drop_duplicates(subset=["Tahun", "Kategori"])
        .pivot(index="Tahun", columns="Kategori", values="Nilai")
        .sort_index()
    )
    df_pivot.index.name = "Tahun"
    df_pivot.columns.name = None

    return df_pivot, raw


def _parse_nilai(raw_val) -> float | None:
    """
    Konversi nilai dari datacontent BPS ke float.
    Kembalikan None (→ NaN di DataFrame) jika nilai kosong, '-', atau tidak bisa diparse.
    Tidak ada estimasi atau substitusi — nilai kosong tetap kosong.
    """
    if raw_val is None:
        return None
    s = str(raw_val).strip()
    if s in ("", "-", "N/A", "n/a", "null", "NULL"):
        return None
    # Bersihkan pemisah ribuan (titik) dan desimal (koma) gaya Indonesia
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


# ──────────────────────────────────────────────────────────────────────────────
# KOMPONEN UI PEMBANTU
# ──────────────────────────────────────────────────────────────────────────────

def render_timeseries_chart(df: pd.DataFrame, judul_var: str) -> None:
    """Render grafik tren deret waktu Plotly dengan connectgaps=False."""
    fig = go.Figure()

    for col in df.columns:
        fig.add_trace(go.Scatter(
            x            = df.index.astype(str),
            y            = df[col],
            mode         = "lines+markers",
            name         = col,
            connectgaps  = False,   # garis terputus di nilai NaN — ATURAN KETAT
            hovertemplate= "<b>%{x}</b><br>%{y:,.2f}<extra>%{fullData.name}</extra>",
        ))

    fig.update_layout(
        title       = judul_var,
        xaxis_title = "Tahun",
        yaxis_title = "Nilai",
        legend      = dict(orientation="h", yanchor="bottom", y=-0.35),
        hovermode   = "x unified",
        height      = 480,
        margin      = dict(l=40, r=20, t=50, b=120),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_table(df: pd.DataFrame) -> None:
    """
    Tampilkan DataFrame dengan nilai NaN diformat sebagai '-'
    untuk kejelasan bahwa data memang tidak tersedia dari BPS.
    """
    df_display = df.copy()
    # Format angka ribuan, NaN → '-'
    for col in df_display.columns:
        df_display[col] = df_display[col].apply(
            lambda x: f"{x:,.2f}" if pd.notna(x) else "-"
        )
    st.dataframe(df_display, use_container_width=True)


def render_download_buttons(df: pd.DataFrame, var_label: str) -> None:
    """Tombol unduh CSV dan Excel (.xlsx)."""
    safe_label = "".join(c if c.isalnum() or c in " _-" else "_" for c in var_label)[:50]

    col_csv, col_xlsx = st.columns(2)

    # ── CSV ──
    csv_bytes = df.to_csv().encode("utf-8-sig")
    col_csv.download_button(
        label        = "⬇ Unduh CSV",
        data         = csv_bytes,
        file_name    = f"BPS_{safe_label}.csv",
        mime         = "text/csv",
        use_container_width=True,
    )

    # ── Excel ──
    xlsx_buf = io.BytesIO()
    with pd.ExcelWriter(xlsx_buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Data BPS")
    xlsx_bytes = xlsx_buf.getvalue()

    col_xlsx.download_button(
        label        = "⬇ Unduh Excel (.xlsx)",
        data         = xlsx_bytes,
        file_name    = f"BPS_{safe_label}.xlsx",
        mime         = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# HALAMAN UTAMA
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    st.set_page_config(
        page_title = "BPS Live — Dashboard Analitik Ekonomi",
        page_icon  = "📊",
        layout     = "wide",
    )

    st.title("📊 Dashboard Analitik Ekonomi — Data Live BPS RI")
    st.caption(
        "Semua data ditarik real-time dari WebAPI resmi BPS (domain nasional 0000). "
        "Nilai kosong dari server ditampilkan apa adanya, tanpa estimasi atau interpolasi."
    )

    # ── Autentikasi ──
    try:
        api_key = st.secrets["BPS_APP_ID"]
    except (KeyError, FileNotFoundError):
        st.error(
            "**API Key tidak ditemukan.** "
            "Tambahkan `BPS_APP_ID` ke file `.streamlit/secrets.toml`:\n\n"
            "```toml\nBPS_APP_ID = \"kunci-api-bps-anda\"\n```"
        )
        st.stop()

    # ─────────────────────────────────────────────────────────────────────────
    # PANEL FILTER (sidebar)
    # ─────────────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("🔍 Filter Data")

        # ── 1. Subjek BPS ──
        st.subheader("Subjek")
        with st.spinner("Memuat daftar subjek dari BPS…"):
            try:
                subjects = fetch_all_subjects(api_key)
            except RuntimeError as e:
                st.error(f"Gagal memuat subjek BPS:\n\n`{e}`")
                st.stop()

        if not subjects:
            st.error("Tidak ada subjek yang dikembalikan oleh BPS.")
            st.stop()

        subject_options = {s["label"]: s["subject_id"] for s in subjects}
        selected_subject_label = st.selectbox(
            "Pilih Subjek BPS",
            options=list(subject_options.keys()),
            index=0,
        )
        selected_subject_id = subject_options[selected_subject_label]

        # ── 2. Variabel/Indikator ──
        st.subheader("Indikator / Variabel")
        with st.spinner(f"Memuat variabel untuk subjek '{selected_subject_label}'…"):
            try:
                variables = fetch_variables(api_key, selected_subject_id)
            except RuntimeError as e:
                st.error(f"Gagal memuat variabel BPS:\n\n`{e}`")
                st.stop()

        if not variables:
            st.warning("Tidak ada variabel yang tersedia untuk subjek ini.")
            st.stop()

        var_options = {v["label"]: v["var_id"] for v in variables}
        selected_var_label = st.selectbox(
            "Pilih Indikator",
            options=list(var_options.keys()),
            index=0,
        )
        selected_var_id = var_options[selected_var_label]

        # ── 3. Rentang Tahun ──
        st.subheader("Rentang Tahun")
        tahun_awal  = st.number_input(
            "Tahun Awal",
            min_value = YEAR_MIN,
            max_value = YEAR_MAX - 1,
            value     = 2015,
            step      = 1,
        )
        tahun_akhir = st.number_input(
            "Tahun Akhir",
            min_value = int(tahun_awal) + 1,
            max_value = YEAR_MAX,
            value     = 2024,
            step      = 1,
        )

        st.divider()
        tarik_data = st.button("🔄 Tarik Data dari BPS", use_container_width=True, type="primary")

    # ─────────────────────────────────────────────────────────────────────────
    # AREA KONTEN UTAMA
    # ─────────────────────────────────────────────────────────────────────────
    if not tarik_data:
        st.info(
            "Pilih subjek, indikator, dan rentang tahun di panel kiri, "
            "lalu klik **Tarik Data dari BPS**."
        )
        return

    # ── Ambil data ──
    with st.spinner(
        f"Mengambil data '{selected_var_label}' ({tahun_awal}–{tahun_akhir}) dari BPS…"
    ):
        try:
            df, raw_response = fetch_timeseries(
                api_key      = api_key,
                var_id       = selected_var_id,
                tahun_awal   = int(tahun_awal),
                tahun_akhir  = int(tahun_akhir),
            )
        except RuntimeError as e:
            st.error(f"**Gagal mengambil data dari BPS:**\n\n`{e}`")
            with st.expander("Tampilkan respons mentah BPS (diagnostik)"):
                try:
                    # Coba tampilkan respons mentah jika tersedia
                    th_param = build_th_param(int(tahun_awal), int(tahun_akhir))
                    url_diag = (
                        f"{BASE_URL}/model/data/lang/{LANG}/domain/{DOMAIN}"
                        f"/var/{selected_var_id}/th/{th_param}/key/{api_key}/"
                    )
                    raw_diag = _get(url_diag)
                    st.json(raw_diag)
                except Exception as e2:
                    st.write(str(e2))
            return

    # ── Informasi indikator ──
    st.subheader(selected_var_label)
    st.caption(
        f"Subjek: **{selected_subject_label}** | "
        f"Var ID: `{selected_var_id}` | "
        f"Rentang: {tahun_awal}–{tahun_akhir} | "
        f"Sumber: WebAPI BPS RI (Domain `{DOMAIN}`)"
    )

    if df.empty or df.isnull().all().all():
        st.warning(
            "BPS mengembalikan data kosong untuk kombinasi variabel dan rentang tahun ini. "
            "Coba perluas rentang tahun atau pilih variabel lain."
        )
        with st.expander("Respons mentah BPS"):
            st.json(raw_response)
        return

    # ── Grafik tren ──
    render_timeseries_chart(df, selected_var_label)

    # ── Statistik ringkas ──
    with st.expander("📈 Statistik Deskriptif"):
        st.dataframe(df.describe().applymap(lambda x: f"{x:,.2f}" if pd.notna(x) else "-"),
                     use_container_width=True)

    # ── Tabel observasi ──
    st.subheader("Tabel Observasi")
    render_table(df)

    # ── Unduh ──
    st.subheader("Unduh Data")
    render_download_buttons(df, selected_var_label)

    # ── Ekspander respons mentah (transparansi) ──
    with st.expander("🔎 Respons JSON mentah dari BPS (untuk verifikasi)"):
        st.json(raw_response)


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
