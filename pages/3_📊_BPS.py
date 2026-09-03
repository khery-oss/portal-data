import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from io import BytesIO

# ==========================================
# KONFIGURASI & KONSTANTA UTAMA
# ==========================================
st.set_page_config(page_title="BPS Live Analytics", page_icon="📊", layout="wide")

DOMAIN = "0000" # Domain BPS Nasional
API_KEY = st.secrets.get("BPS_APP_ID", "")

if not API_KEY:
    st.error("🚨 **Kritis:** API Key BPS tidak ditemukan. Pastikan `BPS_APP_ID` telah diset di `secrets.toml`.")
    st.stop()

# ==========================================
# FUNGSI KONEKSI API & PARSING (CACHED)
# ==========================================

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_bps_subjects():
    """Mengambil katalog subjek BPS dengan iterasi pagination dinamis."""
    subjects = []
    base_url = f"https://webapi.bps.go.id/v1/api/list/model/subject/domain/{DOMAIN}/key/{API_KEY}/page/"
    
    try:
        # Panggil halaman 1 untuk mengetahui total halaman
        res = requests.get(base_url + "1/").json()
        if res.get("data-availability") == "available":
            data_arr = res.get("data", [])
            
            # Pastikan panjang array lebih dari 1 sebelum mengakses indeks [1]
            if len(data_arr) > 1:
                subjects.extend(data_arr[1])
                
            # Ambil total pages dari metadata di indeks [0]
            pages = data_arr[0].get("pages", 1) if len(data_arr) > 0 else 1
            
            # Iterasi sisa halaman
            for p in range(2, pages + 1):
                res_p = requests.get(base_url + f"{p}/").json()
                if res_p.get("data-availability") == "available":
                    data_arr_p = res_p.get("data", [])
                    if len(data_arr_p) > 1:
                        subjects.extend(data_arr_p[1])
        else:
            st.error(f"Error API Subjek: {res.get('message', 'Unknown Error')}")
    except Exception as e:
        st.error(f"Koneksi gagal: {e}")
        
    return subjects

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_bps_variables(sub_id, max_pages=5):
    """Mengambil katalog variabel berdasarkan subjek dengan batasan halaman (safe limit)."""
    variables = []
    base_url = f"https://webapi.bps.go.id/v1/api/list/model/var/domain/{DOMAIN}/subject/{sub_id}/key/{API_KEY}/page/"
    
    try:
        for p in range(1, max_pages + 1):
            res = requests.get(base_url + f"{p}/").json()
            if res.get("data-availability") == "available":
                # Data metadata BPS di model/var diletakkan pada index 1 array 'data'
                var_data = res.get("data", [])
                if len(var_data) > 1:
                    variables.extend(var_data[1])
            else:
                break # Berhenti jika halaman sudah kosong atau tidak tersedia
    except Exception as e:
        st.error(f"Koneksi gagal: {e}")
        
    return variables

def fetch_bps_data(var_id, start_year, end_year):
    """
    Mengambil data deret waktu murni dengan aturan parameter th BPS (Tahun - 1900).
    Melakukan flattening dari struktur multidimensi (datacontent).
    """
    # Aturan Kritis: th_id = tahun - 1900
    th_start = start_year - 1900
    th_end = end_year - 1900
    th_param = f"{th_start}:{th_end}"
    
    url = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/{DOMAIN}/var/{var_id}/th/{th_param}/key/{API_KEY}/"
    
    res = requests.get(url)
    if res.status_code != 200:
        st.error(f"HTTP Error {res.status_code}: Endpoint tidak dapat diakses.")
        return pd.DataFrame()
        
    data_json = res.json()
    
    if data_json.get("data-availability") != "list-available":
        st.warning(f"Respon BPS: {data_json.get('message', 'Data tidak tersedia untuk parameter yang diminta.')}")
        return pd.DataFrame()

    try:
        # Ekstraksi komponen multidimensi dari BPS
        datacontent = data_json["data"][0].get("datacontent", {})
        metadata = data_json["data"][1]
        
        vervar_list = metadata.get("vervar", [])
        turvar_list = metadata.get("turvar", [])
        tahun_list = metadata.get("tahun", [])
        turth_list = metadata.get("turth", [])
        
        records = []
        
        # Iterasi seluruh kemungkinan kombinasi dimensi
        for v_var in vervar_list:
            for t_var in turvar_list:
                for th in tahun_list:
                    for t_th in turth_list:
                        # Rumus komposit key BPS (Standar WebAPI): var + turvar + tahun + turth + vervar
                        komposit_key = f"{var_id}{t_var['val']}{th['val']}{t_th['val']}{v_var['val']}"
                        
                        # Ambil nilai murni tanpa interpolasi (Jika tidak ada, biarkan None)
                        val = datacontent.get(komposit_key, None)
                        
                        records.append({
                            "Tahun": int(th['label']),
                            "Periode": t_th['label'],
                            "Kategori (Vervar)": v_var['label'],
                            "Rincian (Turvar)": t_var['label'],
                            "Nilai": val
                        })
                        
        df = pd.DataFrame(records)
        df["Nilai"] = pd.to_numeric(df["Nilai"], errors="coerce") # Ubah ke numerik murni, error jadi NaN
        
        # Urutkan berdasarkan Tahun
        df = df.sort_values(by=["Tahun"])
        return df

    except KeyError as e:
        st.error(f"Gagal memparsing struktur JSON BPS: {e}. Kemungkinan format endpoint berubah.")
        return pd.DataFrame()

# ==========================================
# ANTARMUKA PENGGUNA (UI)
# ==========================================
st.title("📊 Dashboard Analitik Ekonomi (BPS WebAPI Live)")
st.markdown("""
Dashboard ini terkoneksi secara ***real-time*** ke WebAPI BPS RI. 
Integritas data dijaga ketat: **Tidak ada interpolasi data.** Nilai kosong di masa lampau disajikan apa adanya sebagai observasi putus (NaN).
""")
st.divider()

# --- BAGIAN FILTER BERJENJANG ---
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    with st.spinner("Memuat Subjek BPS..."):
        subjects_data = fetch_bps_subjects()
        if subjects_data:
            subject_dict = {f"{s['sub_id']} - {s['title']}": s['sub_id'] for s in subjects_data}
            selected_subject_str = st.selectbox("1. Pilih Subjek", options=list(subject_dict.keys()))
            selected_subject_id = subject_dict[selected_subject_str]
        else:
            st.selectbox("1. Pilih Subjek", ["- Kosong -"])
            selected_subject_id = None

with col2:
    if selected_subject_id:
        with st.spinner("Memuat Variabel..."):
            vars_data = fetch_bps_variables(selected_subject_id)
            if vars_data:
                var_dict = {f"{v['var_id']} - {v['title']}": v['var_id'] for v in vars_data}
                selected_var_str = st.selectbox("2. Pilih Indikator/Variabel", options=list(var_dict.keys()))
                selected_var_id = var_dict[selected_var_str]
            else:
                st.selectbox("2. Pilih Indikator/Variabel", ["- Tidak ada variabel di subjek ini -"])
                selected_var_id = None
    else:
        st.selectbox("2. Pilih Indikator/Variabel", ["- Tunggu Subjek -"])
        selected_var_id = None

with col3:
    col_yr1, col_yr2 = st.columns(2)
    with col_yr1:
        start_year = st.number_input("Tahun Awal", min_value=1950, max_value=2050, value=2015, step=1)
    with col_yr2:
        end_year = st.number_input("Tahun Akhir", min_value=1950, max_value=2050, value=2024, step=1)

# --- TOMBOL EKSEKUSI ---
if st.button("🚀 Tarik Data Real-Time", type="primary", use_container_width=True):
    if not selected_var_id:
        st.warning("Pilih indikator terlebih dahulu.")
    elif start_year > end_year:
        st.error("Tahun awal tidak boleh lebih besar dari tahun akhir.")
    else:
        with st.spinner(f"Menarik observasi untuk {start_year}-{end_year} via API..."):
            df = fetch_bps_data(selected_var_id, start_year, end_year)
            
            if not df.empty and not df['Nilai'].isna().all():
                st.success("Data berhasil ditarik dan diparsing dari server BPS!")
                
                # Buat label komposit untuk visualisasi (Kategori + Turunan + Periode)
                df['Grup'] = df['Kategori (Vervar)'] + " | " + df['Rincian (Turvar)'] + " (" + df['Periode'] + ")"
                
                tab1, tab2, tab3 = st.tabs(["📈 Visualisasi Tren", "🗃️ Tabel Data Mentah", "💾 Ekspor Data"])
                
                with tab1:
                    # GRAFIK: connectgaps=False sangat penting agar garis putus jika data BPS bernilai NaN
                    fig = go.Figure()
                    for grup_name, group_df in df.groupby('Grup'):
                        fig.add_trace(go.Scatter(
                            x=group_df['Tahun'], 
                            y=group_df['Nilai'],
                            mode='lines+markers',
                            name=grup_name,
                            connectgaps=False  # Strict Rule: Jangan estimasi missing value
                        ))
                        
                    fig.update_layout(
                        title=f"Tren: {selected_var_str.split(' - ', 1)[1]}",
                        xaxis_title="Tahun Observasi",
                        yaxis_title="Nilai Observasi",
                        hovermode="x unified",
                        template="plotly_white",
                        legend=dict(orientation="h", y=-0.2)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                with tab2:
                    # TABEL: Tampilkan NaN sebagai '-'
                    df_display = df.drop(columns=['Grup'])
                    st.dataframe(
                        df_display.style.format(na_rep='-'), # Strict Rule: Missing value tetap kosong
                        use_container_width=True,
                        hide_index=True
                    )
                    
                with tab3:
                    st.markdown("### Unduh Data Instan")
                    st.markdown("Pilih format berkas untuk mengekstrak tabel multidimensi BPS.")
                    
                    df_export = df.drop(columns=['Grup'])
                    
                    col_dl1, col_dl2 = st.columns(2)
                    
                    # 1. Download CSV
                    csv = df_export.to_csv(index=False).encode('utf-8')
                    with col_dl1:
                        st.download_button(
                            label="📥 Unduh Format CSV",
                            data=csv,
                            file_name=f"BPS_{selected_var_id}_{start_year}_{end_year}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    # 2. Download Excel (membutuhkan memori buffer)
                    excel_buffer = BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                        df_export.to_excel(writer, index=False, sheet_name='Data BPS')
                    with col_dl2:
                        st.download_button(
                            label="📥 Unduh Format Excel (.xlsx)",
                            data=excel_buffer.getvalue(),
                            file_name=f"BPS_{selected_var_id}_{start_year}_{end_year}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
            else:
                st.info("Kueri dieksekusi, namun tidak ada nilai angka yang dikembalikan oleh BPS pada rentang tahun dan variabel tersebut (semua observasi bernilai Null/-).")
