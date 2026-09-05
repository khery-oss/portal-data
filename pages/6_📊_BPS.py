import io
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="BPS Explorer - IndoEcon", layout="wide")

st.title("📊 BPS (Badan Pusat Statistik RI) - Tabel Publikasi Resmi")
st.markdown(
    "Portal observasi publikasi statistik resmi langsung dari **WebAPI BPS RI** secara *real-time* (*100% Live API*)."
)

bps_api_key = st.secrets.get("BPS_API_KEY", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

if not bps_api_key:
    st.error("⚙️ Kunci WebAPI BPS belum terdeteksi di secrets pengembang (`st.secrets['BPS_API_KEY']`).")
    st.stop()

st.subheader("1. Penarikan Katalog Rilis Publikasi BPS")

if st.button("📊 Muat Daftar Publikasi BPS (Live API)", type="primary"):
    with st.spinner("Menghubungi server BPS dan mengambil katalog tabel publikasi..."):
        all_records = []
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
                                table_id = str(it.get("table_id", "")).strip()
                                if title and table_id:
                                    all_records.append({
                                        "ID Tabel": table_id,
                                        "Judul Publikasi Statistik": str(title).strip()
                                    })
                    else:
                        break
            except Exception:
                break

        if all_records:
            st.session_state["bps_table_catalog"] = pd.DataFrame(all_records).drop_duplicates(subset=["ID Tabel"])

if "bps_table_catalog" in st.session_state:
    df_cat = st.session_state["bps_table_catalog"]
    st.success(f"Berhasil memuat {len(df_cat)} judul publikasi resmi dari BPS!")
    st.divider()

    st.subheader("2. Pilih & Baca Isi Tabel Langsung")
    
    opsi_tabel = {f"[{row['ID Tabel']}] {row['Judul Publikasi Statistik']}": row['ID Tabel'] for _, row in df_cat.iterrows()}
    pilihan_label = st.selectbox("Pilih Tabel untuk Ditampilkan:", list(opsi_tabel.keys()))
    selected_id = opsi_tabel[pilihan_label]

    if st.button("🔍 Buka Isi Tabel", type="secondary"):
        with st.spinner(f"Menarik konten tabel ID {selected_id} langsung dari server BPS..."):
            detail_url = f"https://webapi.bps.go.id/v1/api/view/model/statictable/lang/ind/domain/0000/var/{selected_id}/key/{bps_api_key}/"
            try:
                r_detail = requests.get(detail_url, headers=HEADERS, timeout=25)
                if r_detail.status_code == 200:
                    dt_payload = r_detail.json()
                    if dt_payload.get("data-availability") == "available":
                        data_item = dt_payload.get("data", {})
                        tabel_html = data_item.get("table", "")
                        
                        if tabel_html:
                            st.success("Tabel berhasil dimuat langsung dari server BPS!")
                            
                            # Ekstraksi tabel HTML ke DataFrame pandas jika format sesuai
                            try:
                                dfs = pd.read_html(tabel_html)
                                if dfs:
                                    df_parsed = dfs[0]
                                    
                                    c1, c2 = st.columns(2)
                                    c1.download_button(
                                        "📥 Unduh CSV",
                                        df_parsed.to_csv(index=False).encode("utf-8"),
                                        f"BPS_Tabel_{selected_id}.csv",
                                        "text/csv"
                                    )
                                    buf = io.BytesIO()
                                    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                                        df_parsed.to_excel(writer, index=False)
                                    c2.download_button(
                                        "📊 Unduh Excel (.xlsx)",
                                        buf.getvalue(),
                                        f"BPS_Tabel_{selected_id}.xlsx",
                                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    )
                                    st.dataframe(df_parsed, use_container_width=True)
                            except Exception:
                                # Jika format HTML kompleks, render tampilan web aslinya langsung
                                st.components.v1.html(tabel_html, height=500, scrolling=True)
                        else:
                            st.warning("Konten tabel tidak ditemukan pada data balikan BPS.")
                    else:
                        st.warning("Respon server BPS: data tabel tidak tersedia.")
                else:
                    st.error(f"Gagal menghubungi server BPS (Kode Status: {r_detail.status_code}).")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses konten tabel: {e}")
