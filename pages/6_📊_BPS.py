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

# API Key diambil langsung secara privat dari Secrets pengembang (tanpa meminta ke pengunjung web)
bps_api_key = st.secrets.get("BPS_API_KEY", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# =============================================================================
# CEK KETERSEDIAAN KONFIGURASI SISTEM
# =============================================================================
if not bps_api_key:
    st.error(
        "⚙️ Kunci WebAPI BPS belum dikonfigurasi di pengaturan sistem (`st.secrets['BPS_API_KEY']`). "
        "Silakan masukkan kunci di dashboard Streamlit Cloud pengembang."
    )
    st.stop()

# =============================================================================
# PENARIKAN DATA LIVE DARI ENDPOINT INDIKATOR STRATEGIS RESMI BPS
# =============================================================================
st.subheader("1. Observasi Indikator Strategis Resmi")

if st.button("📊 Ambil Data Indikator Strategis BPS", type="primary"):
    with st.spinner("Menghubungi server resmi WebAPI BPS Jakarta..."):
        # Endpoint resmi Indikator Strategis Nasional BPS (Domain 0000 = Nasional)
        api_url = f"https://webapi.bps.go.id/v1/api/list/model/indicator/lang/ind/domain/0000/key/{bps_api_key}/"
        
        try:
            res = requests.get(api_url, headers=HEADERS, timeout=25)
            
            if res.status_code == 200:
                payload = res.json()
                
                if payload.get("data-availability") == "available":
                    raw_data = payload.get("data", [])
                    
                    # BPS mengembalikan list di mana elemen kedua adalah daftar data
                    items = []
                    if isinstance(raw_data, list) and len(raw_data) > 1 and isinstance(raw_data[1], list):
                        items = raw_data[1]
                    elif isinstance(raw_data, list):
                        items = raw_data
                    
                    records = []
                    for item in items:
                        if isinstance(item, dict):
                            nama = item.get("title") or item.get("name") or item.get("indicator_name")
                            val = item.get("value")
                            unit = item.get("unit", "-")
                            periode = item.get("period") or item.get("release_date") or "-"
                            
                            if nama and val is not None:
                                records.append({
                                    "Indikator Strategis": str(nama).strip(),
                                    "Nilai Terkini": val,
                                    "Satuan": str(unit).strip(),
                                    "Periode Data": str(periode).strip()
                                })
                    
                    if records:
                        df_bps = pd.DataFrame(records)
                        st.success(f"Berhasil menarik {len(df_bps)} indikator strategis resmi secara langsung dari server BPS RI!")
                        st.divider()

                        # Pencarian & Filter Cepat untuk Pengguna
                        cari = st.text_input("🔍 Cari Indikator (misal: Inflasi, Kemiskinan, Pengangguran, PDRB):", "")
                        if cari.strip():
                            df_tampil = df_bps[df_bps["Indikator Strategis"].str.contains(cari, case=False, na=False)]
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

                        # Tampilkan Tabel Resmi
                        st.dataframe(df_tampil, use_container_width=True, hide_index=True)
                    else:
                        st.warning("Server BPS merespons, namun daftar indikator kosong.")
                else:
                    st.warning("Server BPS mengindikasikan data sedang tidak tersedia saat ini.")
            else:
                st.error(f"Gagal menghubungi server BPS (Kode Status: {res.status_code}).")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data BPS: {e}")
