import io
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="BPS Explorer - IndoEcon", layout="wide")

st.title("📊 BPS (Badan Pusat Statistik RI) - Publikasi Statistik Resmi")
st.markdown(
    "Portal eksplorasi tabel data publikasi resmi dari **WebAPI BPS RI** secara *real-time* (*100% Live API*)."
)

# API Key dibaca aman dari secrets
bps_api_key = st.secrets.get("BPS_API_KEY", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

if not bps_api_key:
    st.error("⚙️ Kunci WebAPI BPS belum terdeteksi di `st.secrets['BPS_API_KEY']`.")
    st.stop()

st.subheader("1. Penarikan Katalog Tabel Statistik Resmi BPS")
st.write("Menghubungkan langsung ke endpoint publikasi tabel resmi BPS Pusat (Domain 0000).")

# Pilihan halaman katalog publikasi
halaman = st.selectbox("Pilih Halaman Katalog Publikasi:", [1, 2, 3, 4, 5], index=0)

if st.button("📊 Tarik Data Publikasi BPS (Live API)", type="primary"):
    with st.spinner(f"Menghubungi server BPS untuk katalog halaman {halaman}..."):
        api_url = f"https://webapi.bps.go.id/v1/api/list/model/statictable/lang/ind/domain/0000/page/{halaman}/key/{bps_api_key}/"

        try:
            res = requests.get(api_url, headers=HEADERS, timeout=25)
            if res.status_code == 200:
                payload = res.json()

                if payload.get("data-availability") == "available":
                    raw_data = payload.get("data", [])

                    items = []
                    if isinstance(raw_data, list) and len(raw_data) > 1 and isinstance(raw_data[1], list):
                        items = raw_data[1]
                    elif isinstance(raw_data, list):
                        items = raw_data

                    records = []
                    for item in items:
                        if isinstance(item, dict):
                            judul = item.get("title", "")
                            tgl = item.get("updt", "") or item.get("cr_date", "")
                            table_id = item.get("table_id", "")
                            link_unduh = item.get("excel", "")

                            if judul:
                                records.append({
                                    "ID Tabel": str(table_id),
                                    "Judul Publikasi Statistik": str(judul).strip(),
                                    "Pembaruan Terakhir": str(tgl).strip(),
                                    "Tautan Berkas Excel BPS": str(link_unduh).strip()
                                })

                    if records:
                        df_table = pd.DataFrame(records)
                        st.success(f"Berhasil menarik {len(df_table)} tabel publikasi resmi dari server BPS!")
                        st.divider()

                        # Pencarian Cepat
                        kata_kunci = st.text_input("🔍 Cari Judul Publikasi (misal: Inflasi, PDRB, Kemiskinan, Upah):", "")
                        if kata_kunci.strip():
                            df_tampil = df_table[df_table["Judul Publikasi Statistik"].str.contains(kata_kunci, case=False, na=False)]
                        else:
                            df_tampil = df_table

                        # Tombol Ekspor Data Katalog
                        c1, c2 = st.columns(2)
                        c1.download_button(
                            "📥 Unduh Daftar (CSV)",
                            df_tampil.to_csv(index=False).encode("utf-8"),
                            f"BPS_Katalog_Tabel_Hal_{halaman}.csv",
                            "text/csv"
                        )
                        buf = io.BytesIO()
                        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                            df_tampil.to_excel(writer, index=False, sheet_name="BPS Tables")
                        c2.download_button(
                            "📊 Unduh Daftar (.xlsx)",
                            buf.getvalue(),
                            f"BPS_Katalog_Tabel_Hal_{halaman}.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                        # Tampilan Data
                        st.dataframe(
                            df_tampil,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Tautan Berkas Excel BPS": st.column_config.LinkColumn(
                                    "Unduh Berkas Resmi BPS",
                                    help="Tautan langsung ke dokumen resmi yang diterbitkan server BPS"
                                )
                            }
                        )
                    else:
                        st.warning("Server BPS merespons dengan data kosong untuk halaman ini.")
                else:
                    st.warning("Respon server BPS: data publikasi tidak tersedia pada halaman ini.")
            else:
                st.error(f"Gagal menghubungi server BPS (Kode Status HTTP: {res.status_code}).")
        except Exception as e:
            st.error(f"Terjadi kendala koneksi ke server BPS: {e}")
