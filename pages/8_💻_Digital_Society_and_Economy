import io
import os
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Digital Society & Economy - IE IndoEcon Explorer",
    page_icon="💻",
    layout="wide"
)

st.title("💻 Digital Society & Economy Module")
st.markdown(
    "Eksplorasi komprehensif mengenai **inklusi keuangan, ekonomi digital, tata kelola teknologi, "
    "dan kebebasan digital di Indonesia**, bersumber dari *World Bank Global Findex*, *UNCTAD*, dan *Digital Society Project (DSP)*."
)

# =============================================================================
# LOAD DATASET KHUSUS INDONESIA (DENGAN CACHE AGAR CEPAT)
# =============================================================================
@st.cache_data
def load_digital_data():
    # Sesuaikan path folder data jika diperlukan
    path_findex = "data/WB_FINDEX_IDN.csv"
    path_unctad = "data/UNCTAD_DE_IDN.csv"
    path_dsp = "data/DSP_CY_IDN.csv"
    
    df_findex = pd.read_csv(path_findex) if os.path.exists(path_findex) else pd.DataFrame()
    df_unctad = pd.read_csv(path_unctad) if os.path.exists(path_unctad) else pd.DataFrame()
    df_dsp = pd.read_csv(path_dsp) if os.path.exists(path_dsp) else pd.DataFrame()
    
    return df_findex, df_unctad, df_dsp

df_fin, df_unc, df_dsp = load_digital_data()

# =============================================================================
# NAVIGASI TAB UTAMA MODUL
# =============================================================================
tab_findex, tab_unctad, tab_dsp, tab_codebook = st.tabs([
    "💳 Inklusi Keuangan (Findex)", 
    "🌐 Ekonomi Digital (UNCTAD)", 
    "🛡️ Tata Kelola & DSP", 
    "📖 Kamus Data & Metodologi"
])

# -----------------------------------------------------------------------------
# TAB 1: WORLD BANK GLOBAL FINDEX
# -----------------------------------------------------------------------------
with tab_findex:
    st.subheader("💳 World Bank Global Findex Database (Indonesia)")
    st.markdown("Analisis kepemilikan akun finansial, transaksi digital, dan pembayaran seluler masyarakat Indonesia.")
    
    if not df_fin.empty:
        # Filter indikator yang tersedia
        indicator_col = "INDICATOR_LABEL" if "INDICATOR_LABEL" in df_fin.columns else "INDICATOR"
        indicators = df_fin[indicator_col].dropna().unique()
        
        selected_ind_fin = st.selectbox("Pilih Indikator Findex:", indicators, key="sel_fin")
        
        # Filter dataframe berdasarkan indikator pilihan
        df_filtered_fin = df_fin[df_fin[indicator_col] == selected_ind_fin]
        
        if not df_filtered_fin.empty and "TIME_PERIOD" in df_filtered_fin.columns and "OBS_VALUE" in df_filtered_fin.columns:
            df_filtered_fin = df_filtered_fin.sort_values("TIME_PERIOD")
            
            # Grafik Plotly
            fig_fin = px.line(
                df_filtered_fin,
                x="TIME_PERIOD",
                y="OBS_VALUE",
                markers=True,
                title=f"Tren Waktu: {selected_ind_fin}",
                labels={"TIME_PERIOD": "Tahun", "OBS_VALUE": "Nilai (%)"},
                template="plotly_white"
            )
            fig_fin.update_traces(line=dict(width=2.5, color="#2ca02c"), marker=dict(size=8))
            st.plotly_chart(fig_fin, use_container_width=True)
            
            # Tabel & Tombol Download
            with st.expander("📋 Lihat & Unduh Data Findex Ini"):
                st.dataframe(df_filtered_fin, use_container_width=True)
                
                col_d1, col_d2 = st.columns(2)
                col_d1.download_button(
                    "📥 Unduh CSV",
                    df_filtered_fin.to_csv(index=False).encode("utf-8"),
                    "Findex_Indonesia_Data.csv",
                    "text/csv"
                )
        else:
            st.warning("Data observasi tidak ditemukan untuk indikator tersebut.")
    else:
        st.info("File `WB_FINDEX_IDN.csv` belum ditemukan di folder `data/`. Silakan unggah file tersebut ke GitHub.")

# -----------------------------------------------------------------------------
# TAB 2: UNCTAD DIGITAL ECONOMY
# -----------------------------------------------------------------------------
with tab_unctad:
    st.subheader("🌐 UNCTAD Digital Economy Database (Indonesia)")
    st.markdown("Observasi kesiapan infrastruktur TIK, adopsi e-commerce, dan ekonomi digital.")
    
    if not df_unc.empty:
        ind_col_unc = "INDICATOR_LABEL" if "INDICATOR_LABEL" in df_unc.columns else "INDICATOR"
        indicators_unc = df_unc[ind_col_unc].dropna().unique()
        
        selected_ind_unc = st.selectbox("Pilih Indikator UNCTAD:", indicators_unc, key="sel_unc")
        
        df_filtered_unc = df_unc[df_unc[ind_col_unc] == selected_ind_unc]
        
        if not df_filtered_unc.empty and "TIME_PERIOD" in df_filtered_unc.columns and "OBS_VALUE" in df_filtered_unc.columns:
            df_filtered_unc = df_filtered_unc.sort_values("TIME_PERIOD")
            
            fig_unc = px.bar(
                df_filtered_unc,
                x="TIME_PERIOD",
                y="OBS_VALUE",
                title=f"Statistik Tahunan: {selected_ind_unc}",
                labels={"TIME_PERIOD": "Tahun", "OBS_VALUE": "Nilai Observasi"},
                template="plotly_white"
            )
            fig_unc.update_traces(marker_color="#1f77b4")
            st.plotly_chart(fig_unc, use_container_width=True)
            
            with st.expander("📋 Lihat & Unduh Data UNCTAD Ini"):
                st.dataframe(df_filtered_unc, use_container_width=True)
                st.download_button(
                    "📥 Unduh CSV",
                    df_filtered_unc.to_csv(index=False).encode("utf-8"),
                    "UNCTAD_Indonesia_Data.csv",
                    "text/csv",
                    key="dl_unc"
                )
        else:
            st.warning("Data observasi tidak tersedia untuk pilihan ini.")
    else:
        st.info("File `UNCTAD_DE_IDN.csv` belum ditemukan di folder `data/`.")

# -----------------------------------------------------------------------------
# TAB 3: DIGITAL SOCIETY PROJECT (DSP)
# -----------------------------------------------------------------------------
with tab_dsp:
    st.subheader("🛡️ Digital Society Project (DSP) - Tata Kelola & Kebebasan Digital")
    st.markdown("Analisis penyebaran disinformasi, sensor internet, pembatasan jaringan, dan regulasi hukum digital.")
    
    if not df_dsp.empty:
        # Variabel kunci DSP populer
        dsp_keys = {
            "Penyebaran Informasi Palsu oleh Pemerintah (v2smgovdom)": "v2smgovdom",
            "Penyebaran Informasi Palsu oleh Partai Politik (v2smpardom)": "v2smpardom",
            "Kapasitas Penyaringan / Sensor Internet Pemerintah (v2smgovfilcap)": "v2smgovfilcap",
            "Pemadaman Akses Internet oleh Pemerintah (v2smgovshut)": "v2smgovshut",
            "Perlindungan Hukum Privasi Pengguna (v2smprivex)": "v2smprivex",
            "Perlindungan Hukum terhadap Defamation & Ujaran Kebencian (v2smlawpr)": "v2smlawpr"
        }
        
        selected_dsp_label = st.selectbox("Pilih Indikator Tata Kelola DSP:", list(dsp_keys.keys()), key="sel_dsp")
        var_code = dsp_keys[selected_dsp_label]
        
        # Cek apakah kolom ada di dataframe
        if var_code in df_dsp.columns and "year" in df_dsp.columns:
            df_plot_dsp = df_dsp[["year", var_code]].dropna().sort_values("year")
            
            fig_dsp = px.line(
                df_plot_dsp,
                x="year",
                y=var_code,
                markers=True,
                title=f"Indeks Tahunan: {selected_dsp_label}",
                labels={"year": "Tahun", var_code: "Skor Estimasi / Indeks"},
                template="plotly_white"
            )
            fig_dsp.update_traces(line=dict(width=2.5, color="#d62728"), marker=dict(size=7))
            st.plotly_chart(fig_dsp, use_container_width=True)
            
            with st.expander("📋 Lihat Tabel & Unduh Data DSP Ini"):
                st.dataframe(df_plot_dsp, use_container_width=True)
                st.download_button(
                    "📥 Unduh CSV",
                    df_plot_dsp.to_csv(index=False).encode("utf-8"),
                    f"DSP_{var_code}_Indonesia.csv",
                    "text/csv",
                    key="dl_dsp"
                )
        else:
            st.warning(f"Kolom variabel `{var_code}` tidak ditemukan dalam file dataset DSP.")
    else:
        st.info("File `DSP_CY_IDN.csv` belum ditemukan di folder `data/`.")

# -----------------------------------------------------------------------------
# TAB 4: KAMUS DATA & METODOLOGI (MEMBACA digital_codebook.md)
# -----------------------------------------------------------------------------
with tab_codebook:
    st.subheader("📖 Kamus Data & Panduan Metodologi Resmi")
    st.markdown("Dokumentasi lengkap definisi variabel, skala pengukuran, dan sumber literatur.")
    
    codebook_path = "digital_codebook.md"
    if os.path.exists(codebook_path):
        with open(codebook_path, "r", encoding="utf-8") as cb_file:
            codebook_text = cb_file.read()
        st.markdown(codebook_text)
    else:
        st.warning(
            f"⚠️ File **`{codebook_path}`** belum ditemukan di direktori utama repository.\n\n"
            "Pastikan kamu membuat file teks bernama `digital_codebook.md` dan mengisinya dengan hasil ringkasan NotebookLM sebelumnya."
        )
