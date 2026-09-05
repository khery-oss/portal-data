import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="BPS Data Explorer - Nasional", layout="wide")

st.title("📊 BPS (Badan Pusat Statistik RI) - Indikator Strategis")
st.markdown(
    "Eksplorasi indikator sosial-ekonomi resmi **Nasional (Indonesia)** langsung dari "
    "**WebAPI BPS RI** secara *real-time* (*100% Live API*)."
)

# =============================================================================
# MANAJEMEN KUNCI API AMAN (st.secrets ATAU INPUT FIELD)
# =============================================================================
api_key = ""
if "BPS_API_KEY" in st.secrets:
    api_key = st.secrets["BPS_API_KEY"]
else:
    with st.sidebar:
        st.subheader("🔐 Konfigurasi WebAPI BPS")
        api_key = st.text_input(
            "Masukkan BPS API Key:",
            type="password",
            help="Dapatkan gratis di https://webapi.bps.go.id/developer/"
        )

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# =============================================================================
# METODE 1: INDIKATOR STRATEGIS RESMI BPS (ENDPOINT /model/indicator/)
# =============================================================================
st.subheader("1. Penarikan Indikator Strategis Nasional")

if not api_key:
    st.info("💡 Kunci WebAPI BPS belum terdeteksi. Silakan atur di `st.secrets` atau masukkan di bilah samping (sidebar).")
else:
    if st.button("🚀 Ambil Indikator Strategis Terbaru dari BPS", type="primary"):
        with st.spinner("Menghubungi server resmi WebAPI BPS di Jakarta..."):
            # Endpoint resmi BPS untuk Indikator Strategis Nasional
            url = f"https://webapi.bps.go.id/v1/api/list/model/indicator/lang/ind/domain/0000/key/{api_key}/"
            
            try:
                res = requests.get(url, headers=HEADERS, timeout=25)
                if res.status_code == 200:
                    data_json = res.json()
                    
                    if data_json.get("data-availability") == "available":
                        # Data indikator berada di elemen kedua (list data)
                        raw_list = data_json.get("data", [])
                        if isinstance(raw_list, list) and len(raw_list) > 1 and isinstance(raw_list[1], list):
                            items = raw_list[1]
                        elif isinstance(raw_list, list):
                            items = raw_list
                        else:
                            items = []
                        
                        records = []
                        for item in items:
                            if isinstance(item, dict):
                                title = item.get("title", "") or item.get("indicator_name", "")
                                val = item.get("value", "")
                                unit = item.get("unit", "")
                                period = item.get("period", "") or item.get("release_date", "")
                                
                                if title and val:
                                    records.append({
                                        "Indikator Strategis": title,
                                        "Nilai": val,
                                        "Satuan": unit,
                                        "Periode / Rilis": period
                                    })
                                    
                        if records:
                            df_res = pd.DataFrame(records)
                            st.success(f"Berhasil menarik {len(df_res)} indikator strategis resmi secara langsung dari BPS!")
                            st.divider()

                            # Tombol Unduh
                            c1, c2 = st.columns(2)
                            c1.download_button(
                                "📥 Unduh CSV",
                                df_res.to_csv(index=False).encode("utf-8"),
                                "BPS_Indikator_Strategis.csv",
                                "text/csv"
                            )
                            buf = io.BytesIO()
                            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                                df_res.to_excel(writer, index=False, sheet_name="BPS Data")
                            c2.download_button(
                                "📊 Unduh Excel (.xlsx)",
                                buf.getvalue(),
                                "BPS_Indikator_Strategis.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                            st.dataframe(df_res, use_container_width=True)
                        else:
                            st.warning("Data dikembalikan oleh BPS, tetapi format rekaman kosong.")
                    else:
                        st.warning("Server BPS merespons: data tidak tersedia atau kuota kunci API sedang sibuk.")
                else:
                    st.error(f"Gagal menghubungi server BPS (Kode Status HTTP: {res.status_code}).")
            except Exception as e:
                st.error(f"Terjadi kendala koneksi ke server BPS: {e}")
