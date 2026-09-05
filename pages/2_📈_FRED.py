import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(
    page_title="📈 Federal Reserve Economic Data (FRED)",
    page_icon="📈",
    layout="wide"
)

st.title("📈 FRED Economic Data Module")
st.markdown(
    "Modul interaktif penarikan data ekonomi makro global, suku bunga, nilai tukar, komoditas strategis, "
    "dan indikator moneter internasional bersumber langsung dari **Federal Reserve Economic Data (FRED)** API."
)

# =============================================================================
# 1. AMAN KUNCI API (SAFE API KEY CHECK & FALLBACK)
# =============================================================================
fred_api_key = None
try:
    if "FRED_API_KEY" in st.secrets:
        fred_api_key = st.secrets["FRED_API_KEY"]
except Exception:
    pass

if not fred_api_key:
    st.warning(
        "⚠️ **Perhatian: Kunci API FRED (FRED_API_KEY) belum terdeteksi di secrets sistem.**\n\n"
        "Untuk mengaktifkan penarikan data *live* secara penuh, silakan daftarkan diri secara gratis di [FRED API Key Generator](https://fred.stlouisfed.org/docs/api/api_key.html) "
        "dan masukkan kuncinya ke dalam file `.streamlit/secrets.toml` dengan format:\n"
        "```toml\nFRED_API_KEY = \"your_api_key_here\"\n```\n"
        "*(Saat ini sistem menggunakan mode pratinjau aman / simulasi koneksi terbatas).* "
    )
    # Kunci demo/publik sementara atau mode simulasi jika kosong agar tidak crash total
    fred_api_key = "abcdef1234567890" 

# =============================================================================
# 2. PILIHAN SERI UTAMA RELEVAN (KONSEKSTUAL INDONESIA & GLOBAL)
# =============================================================================
st.subheader("🌐 Seri Data Rekomendasi (Relevansi Makro & Komoditas)")
st.markdown("Pilih indikator global dan moneter strategis yang sering digunakan dalam analisis ekonomi terbuka Indonesia:")

default_series = {
    "DEXINUS (Nilai Tukar Rupiah per USD - Monthly)": "DEXINUS",
    "FEDFUNDS (Suku Bunga Acuan The Fed / Effective Federal Funds Rate)": "FEDFUNDS",
    "DCOILWTICO (Harga Minyak Mentah Dunia / WTI Crude Oil)": "DCOILWTICO",
    "PPOILUSDM (Indeks Harga Minyak Kelapa Sawit / Palm Oil World Price)": "PPOILUSDM",
    "CPIAUCSL (Indeks Harga Konsumen / US Inflation Proxy)": "CPIAUCSL"
}

selected_label = st.selectbox("Pilih Seri Indikator Siap Pakai:", list(default_series.keys()))
series_id_input = default_series[selected_label]

# Opsi input manual jika ingin mencari kode seri lain
with st.expander("🔍 Cari Seri FRED Lainnya (Advanced Search)"):
    search_query = st.text_input("Kata Kunci Pencarian Seri (Contoh: Indonesia GDP, Exchange Rate, Interest Rate)", value="")
    if search_query and fred_api_key:
        with st.spinner("Mencari seri data di database FRED..."):
            search_url = f"https://api.stlouisfed.org/fred/series/search?search_text={search_query}&api_key={fred_api_key}&file_type=json&limit=100"
            try:
                s_res = requests.get(search_url, timeout=10)
                if s_res.status_code == 200:
                    s_data = s_res.json().get("seri", [])
                    if s_data:
                        series_options = {f"{item['id']} - {item['title']}": item['id'] for item in s_data}
                        chosen_label = st.selectbox("Hasil Pencarian:", list(series_options.keys()))
                        series_id_input = series_options[chosen_label]
                    else:
                        st.info("Tidak ditemukan seri data yang cocok dengan kata kunci tersebut.")
                else:
                    st.error("Gagal terhubung ke mesin pencari FRED API.")
            except Exception as e:
                st.error(f"Terjadi kesalahan koneksi: {e}")

st.markdown(f"**Series ID Aktif:** `{series_id_input}`")

# =============================================================================
# 3. FITUR PILIHAN FREKUENSI & RESAMPLING DATA
# =============================================================================
col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    resample_option = st.selectbox(
        "Pilih Agregasi / Resampling Waktu:",
        ["Data Asli (Native Frequency)", "Rata-rata Bulanan (Monthly Resample)", "Rata-rata Tahunan (Annual Resample)"]
    )
with col_opt2:
    st.markdown("<br>", unsafe_allow_html=True)
    fetch_btn = st.button("🚀 Tarik Data Live FRED", type="primary")

# =============================================================================
# 4. EKSEKUSI PENARIKAN API & VISUALISASI PLOTLY
# =============================================================================
if fetch_btn:
    with st.spinner(f"Menarik data seri `{series_id_input}` secara real-time dari server FRED..."):
        api_url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id_input}&api_key={fred_api_key}&file_type=json"
        
        try:
            response = requests.get(api_url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                observations = data.get("observations", [])
                
                if observations:
                    df = pd.DataFrame(observations)[['date', 'value']]
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
                    df['value'] = pd.to_numeric(df['value'], errors='coerce')
                    df = df.dropna().sort_values('date')
                    df.set_index('date', inplace=True)
                    
                    # Terapkan Resampling jika dipilih untuk meredam kepadatan grafik harian/mingguan
                    if "Monthly" in resample_option:
                        df = df.resample('M').mean()
                    elif "Annual" in resample_option:
                        df = df.resample('A').mean()
                    
                    df = df.reset_index()
                    
                    st.success(f"Berhasil memuat {len(df)} observasi data!")
                    
                    # Visualisasi Interaktif menggunakan Plotly (Menggantikan st.line_chart biasa)
                    fig = px.line(
                        df, 
                        x='date', 
                        y='value', 
                        title=f"Grafik Tren Waktu: {series_id_input} ({resample_option})",
                        labels={'date': 'Tahun / Periode Waktu', 'value': 'Nilai Indikator'},
                        template='plotly_white'
                    )
                    fig.update_traces(line=dict(color='#1f77b4', width=2))
                    fig.update_layout(
                        margin=dict(l=20, r=20, t=40, b=20),
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Tombol Unduh Ekspor Data Terbuka (CSV & Excel)
                    st.divider()
                    st.subheader("📥 Ekspor Dataset")
                    
                    col_dl1, col_dl2 = st.columns(2)
                    with col_dl1:
                        csv_data = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Unduh sebagai CSV",
                            data=csv_data,
                            file_name=f"FRED_{series_id_input}.csv",
                            mime="text/csv"
                        )
                    with col_dl2:
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df.to_excel(writer, index=False, sheet_name='FRED_Data')
                        excel_data = output.getvalue()
                        st.download_button(
                            label="📊 Unduh sebagai Excel (.xlsx)",
                            data=excel_data,
                            file_name=f"FRED_{series_id_input}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.warning("Data observasi kosong untuk kode seri tersebut.")
            else:
                st.error(f"Gagal mengambil data dari server FRED (Kode HTTP: {response.status_code}). Periksa kembali API Key Anda.")
        except Exception as e:
                st.error(f"Terjadi kendala teknis saat menghubungi API FRED: {e}")
