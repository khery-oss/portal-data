import io
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="BPS Explorer - IndoEcon", layout="wide")

st.title("📊 BPS (Badan Pusat Statistik RI) - Indikator Strategis Nasional")
st.markdown(
    "Portal indikator sosial-ekonomi resmi **Tingkat Nasional (Indonesia)** langsung dari "
    "**WebAPI BPS RI** secara *real-time* (*100% Live API*)."
)

# Membaca API Key secara aman dari Secrets Streamlit Cloud (tidak meminta ke pengunjung)
bps_api_key = st.secrets.get("BPS_API_KEY", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

if not bps_api_key:
    st.error(
        "⚙️ Kunci WebAPI BPS belum dikonfigurasi di pengaturan sistem (`st.secrets['BPS_API_KEY']`). "
        "Silakan masukkan kunci di dashboard Streamlit Cloud pengembang."
    )
    st.stop()

st.subheader("1. Penarikan Seluruh Indikator Strategis Nasional")
st.write("Mengambil seluruh indikator makroekonomi, inflasi, kemiskinan, ketenagakerjaan, dan sosial terkini dari server BPS Pusat.")

if st.button("📊 Ambil Semua Indikator Strategis BPS (Live API)", type="primary"):
    with st.spinner("Mengunduh seluruh katalog indikator strategis langsung dari server BPS Jakarta..."):
        all_records = []
        
        # Iterasi halaman untuk menarik sebanyak mungkin indikator nasional resmi BPS
        for page in range(1, 6):
            api_url = f"https://webapi.bps.go.id/v1/api/list/model/indicator/lang/ind/domain/0000/page/{page}/key/{bps_api_key}/"
            
            try:
                res = requests.get(api_url, headers=HEADERS, timeout=20)
                if res.status_code == 200:
                    payload = res.json()
                    
                    if payload.get("data-availability") == "available":
                        data_block = payload.get("data", [])
                        
                        # Format list bersarang resmi respons WebAPI BPS
                        items = []
                        if isinstance(data_block, list) and len(data_block) > 1 and isinstance(data_block[1], list):
                            items = data_block[1]
                        elif isinstance(data_block, list):
                            items = data_block
                        
                        for item in items:
                            if isinstance(item, dict):
                                judul = (
                                    item.get("title") 
                                    or item.get("name") 
                                    or item.get("indicator_name") 
                                    or item.get("var")
                                )
                                nilai = item.get("value")
                                satuan = item.get("unit") or "-"
                                periode = item.get("period") or item.get("cdate") or item.get("release_date") or "-"
                                
                                if judul and nilai is not None:
                                    all_records.append({
                                        "Indikator Strategis": str(judul).strip(),
                                        "Nilai": str(nilai).strip(),
                                        "Satuan": str(satuan).strip(),
                                        "Periode Data / Rilis": str(periode).strip()
                                    })
                    else:
                        # Jika halaman sudah melebihi ketersediaan data, hentikan iterasi
                        break
                else:
                    break
            except Exception:
                break

        if all_records:
            df_bps = pd.DataFrame(all_records).drop_duplicates(subset=["Indikator Strategis"])
            st.success(f"Berhasil menarik {len(df_bps)} indikator strategis nasional resmi langsung dari server BPS RI!")
            st.divider()

            # Filter & Fitur Pencarian Cepat
            keyword = st.text_input(
                "🔍 Cari Indikator Spesifik (misal: Inflasi, Kemiskinan, Pengangguran, IPM, Ekspor):", 
                ""
            )
            if keyword.strip():
                df_tampil = df_bps[df_bps["Indikator Strategis"].str.contains(keyword, case=False, na=False)]
            else:
                df_tampil = df_bps

            # Tombol Unduh Data
            c1, c2 = st.columns(2)
            c1.download_button(
                "📥 Unduh CSV",
                df_tampil.to_csv(index=False).encode("utf-8"),
                "BPS_Indikator_Strategis_Nasional.csv",
                "text/csv"
            )
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                df_tampil.to_excel(writer, index=False, sheet_name="BPS Strategis")
            c2.download_button(
                "📊 Unduh Excel (.xlsx)",
                buf.getvalue(),
                "BPS_Indikator_Strategis_Nasional.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Tampilan Tabel Interaktif
            st.dataframe(df_tampil, use_container_width=True, hide_index=True)
        else:
            st.warning("Koneksi API berhasil, namun belum ada catatan data yang dikembalikan oleh server BPS.")
