import io
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="BPS Explorer - IndoEcon", layout="wide")

st.title("📊 BPS (Badan Pusat Statistik RI) - Tabel Publikasi Resmi")
st.markdown(
    "Eksplorasi tabel rilis resmi dan data statistik publikasi langsung dari "
    "**WebAPI BPS RI** secara *real-time* (*100% Live API*)."
)

bps_api_key = st.secrets.get("BPS_API_KEY", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

if not bps_api_key:
    st.error("⚙️ Kunci WebAPI BPS belum terdeteksi di secrets pengembang (`st.secrets['BPS_API_KEY']`).")
    st.stop()

st.subheader("1. Penarikan Katalog Rilis Resmi BPS")
st.write("Mengambil kompilasi tabel statistik publikasi terbaru yang diterbitkan oleh server BPS Pusat.")

if st.button("📊 Tarik Data Publikasi BPS Terbaru (Live API)", type="primary"):
    with st.spinner("Menghubungi server BPS dan mengunduh katalog publikasi resmi..."):
        all_records = []
        
        # Otomatis menarik 5 halaman teratas (sekitar 50 publikasi terbaru)
        for page_num in range(1, 6):
            api_url = f"https://webapi.bps.go.id/v1/api/list/model/statictable/lang/ind/domain/0000/page/{page_num}/key/{bps_api_key}/"
            try:
                res = requests.get(api_url, headers=HEADERS, timeout=20)
                if res.status_code == 200:
                    payload = res.json()
                    if payload.get("data-availability") == "available":
                        raw_data = payload.get("data", [])
                        items = raw_data[1] if isinstance(raw_data, list) and len(raw_data) > 1 else raw_data
                        
                        for it in items:
                            if isinstance(it, dict):
                                title = it.get("title", "")
                                if title:
                                    all_records.append({
                                        "ID Tabel": str(it.get("table_id", "")),
                                        "Judul Publikasi Statistik": str(title).strip(),
                                        "Pembaruan Terakhir": str(it.get("updt", "") or it.get("cr_date", "")).strip(),
                                        "Tautan Berkas Excel BPS": str(it.get("excel", "")).strip()
                                    })
                    else:
                        break
            except Exception:
                break

        if all_records:
            st.session_state["bps_table_data"] = pd.DataFrame(all_records).drop_duplicates(subset=["ID Tabel"])

if "bps_table_data" in st.session_state:
    df_bps = st.session_state["bps_table_data"]
    st.success(f"Berhasil memuat {len(df_bps)} tabel statistik resmi langsung dari server BPS RI!")
    st.divider()

    st.subheader("2. Filter & Pencarian Tabel")
    c_filter, c_search = st.columns([1.2, 2])
    
    with c_filter:
        topik = st.selectbox(
            "Filter Berdasarkan Topik Utama:",
            ["Semua Topik", "Inflasi & Harga", "Ekspor & Impor", "Kemiskinan & Sosial", "Pertanian & Industri", "Lainnya"]
        )

    with c_search:
        keyword = st.text_input("🔍 Cari Judul Publikasi Spesifik:", placeholder="Ketik kata kunci (misal: Bahan Baku, Beras, IHK)...")

    # Logika penyaringan topik
    df_filtered = df_bps.copy()
    
    if topik == "Inflasi & Harga":
        df_filtered = df_filtered[df_filtered["Judul Publikasi Statistik"].str.contains("inflasi|ihk|harga", case=False, na=False)]
    elif topik == "Ekspor & Impor":
        df_filtered = df_filtered[df_filtered["Judul Publikasi Statistik"].str.contains("ekspor|impor|perdagangan|barang modal", case=False, na=False)]
    elif topik == "Kemiskinan & Sosial":
        df_filtered = df_filtered[df_filtered["Judul Publikasi Statistik"].str.contains("miskin|gini|sosial|upah", case=False, na=False)]
    elif topik == "Pertanian & Industri":
        df_filtered = df_filtered[df_filtered["Judul Publikasi Statistik"].str.contains("tani|padi|beras|manufaktur|industri", case=False, na=False)]

    if keyword.strip():
        df_filtered = df_filtered[df_filtered["Judul Publikasi Statistik"].str.contains(keyword, case=False, na=False)]

    # Tombol Ekspor Daftar
    c1, c2 = st.columns(2)
    c1.download_button(
        "📥 Unduh Daftar (CSV)",
        df_filtered.to_csv(index=False).encode("utf-8"),
        "BPS_Katalog_Tabel.csv",
        "text/csv"
    )
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df_filtered.to_excel(writer, index=False, sheet_name="BPS Tables")
    c2.download_button(
        "📊 Unduh Daftar (.xlsx)",
        buf.getvalue(),
        "BPS_Katalog_Tabel.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Menampilkan Tabel dengan tautan unduh aktif
    st.dataframe(
        df_filtered,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Tautan Berkas Excel BPS": st.column_config.LinkColumn(
                "Unduh Berkas Resmi BPS",
                display_text="Unduh Excel (.xlsx)",
                help="Klik untuk mengunduh dokumen data resmi langsung dari server BPS"
            )
        }
    )
