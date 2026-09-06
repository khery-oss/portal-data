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
# LOAD DATASET KHUSUS INDONESIA
# =============================================================================
@st.cache_data
def load_digital_data():
    path_findex = "WB_FINDEX_IDN.csv" if os.path.exists("WB_FINDEX_IDN.csv") else "data/WB_FINDEX_IDN.csv"
    path_unctad = "UNCTAD_DE_IDN.csv" if os.path.exists("UNCTAD_DE_IDN.csv") else "data/UNCTAD_DE_IDN.csv"
    path_dsp = "DSP_CY_IDN.csv" if os.path.exists("DSP_CY_IDN.csv") else "data/DSP_CY_IDN.csv"
    
    df_findex = pd.read_csv(path_findex) if os.path.exists(path_findex) else pd.DataFrame()
    df_unctad = pd.read_csv(path_unctad) if os.path.exists(path_unctad) else pd.DataFrame()
    df_dsp = pd.read_csv(path_dsp) if os.path.exists(path_dsp) else pd.DataFrame()
    
    return df_findex, df_unctad, df_dsp

df_fin, df_unc, df_dsp = load_digital_data()

# =============================================================================
# NAVIGASI TAB UTAMA (Tanpa Tab Codebook terpisah, digabung di tiap section)
# =============================================================================
tab_findex, tab_unctad, tab_dsp = st.tabs([
    "💳 Inklusi Keuangan (Findex)", 
    "🌐 Ekonomi Digital (UNCTAD)", 
    "🛡️ Tata Kelola & DSP"
])

# -----------------------------------------------------------------------------
# TAB 1: WORLD BANK GLOBAL FINDEX
# -----------------------------------------------------------------------------
with tab_findex:
    st.subheader("💳 World Bank Global Findex Database (Indonesia)")
    st.markdown("Analisis kepemilikan akun finansial, transaksi digital, dan pembayaran seluler masyarakat Indonesia.")
    
    if not df_fin.empty:
        indicator_col = "INDICATOR_LABEL" if "INDICATOR_LABEL" in df_fin.columns else "INDICATOR"
        indicators = df_fin[indicator_col].dropna().unique()
        
        selected_ind_fin = st.selectbox("Pilih Indikator Findex:", indicators, key="sel_fin")
        
        # Kotak Metadata / Penjelasan Singkat ala V-Dem
        with st.expander("ℹ️ Penjelasan Indikator & Metadata Findex"):
            st.markdown(f"**Indikator Terpilih:** `{selected_ind_fin}`")
            st.markdown("Sumber data: *World Bank Global Findex Database* (Survei representatif tingkat nasional mengenai inklusi keuangan).")
        
        df_filtered_fin = df_fin[df_fin[indicator_col] == selected_ind_fin].copy()
        
        if not df_filtered_fin.empty and "TIME_PERIOD" in df_filtered_fin.columns and "OBS_VALUE" in df_filtered_fin.columns:
            # Bersihkan dan konversi tipe data agar grafik tidak menumpuk aneh
            df_filtered_fin["TIME_PERIOD"] = pd.to_numeric(df_filtered_fin["TIME_PERIOD"], errors="coerce")
            df_filtered_fin["OBS_VALUE"] = pd.to_numeric(df_filtered_fin["OBS_VALUE"], errors="coerce")
            df_filtered_fin = df_filtered_fin.dropna(subset=["TIME_PERIOD", "OBS_VALUE"]).sort_values("TIME_PERIOD")
            
            if not df_filtered_fin.empty:
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
                
                with st.expander("📋 Lihat & Unduh Data Findex Ini"):
                    st.dataframe(df_filtered_fin, use_container_width=True)
                    st.download_button(
                        "📥 Unduh CSV",
                        df_filtered_fin.to_csv(index=False).encode("utf-8"),
                        "Findex_Indonesia_Data.csv",
                        "text/csv"
                    )
            else:
                st.warning("Format nilai waktu atau observasi tidak valid untuk digrafikkan.")
        else:
            st.warning("Data observasi tidak ditemukan untuk indikator tersebut.")
    else:
        st.info("File `WB_FINDEX_IDN.csv` belum ditemukan.")

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
        
        with st.expander("ℹ️ Penjelasan Indikator & Metadata UNCTAD"):
            st.markdown(f"**Indikator Terpilih:** `{selected_ind_unc}`")
            st.markdown("Sumber data: *UNCTADstat Digital Economy Repository*.")
        
        df_filtered_unc = df_unc[df_unc[ind_col_unc] == selected_ind_unc].copy()
        
        if not df_filtered_unc.empty and "TIME_PERIOD" in df_filtered_unc.columns and "OBS_VALUE" in df_filtered_unc.columns:
            df_filtered_unc["TIME_PERIOD"] = pd.to_numeric(df_filtered_unc["TIME_PERIOD"], errors="coerce")
            df_filtered_unc["OBS_VALUE"] = pd.to_numeric(df_filtered_unc["OBS_VALUE"], errors="coerce")
            df_filtered_unc = df_filtered_unc.dropna(subset=["TIME_PERIOD", "OBS_VALUE"]).sort_values("TIME_PERIOD")
            
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
            st.warning("Data observasi tidak tersedia.")
    else:
        st.info("File `UNCTAD_DE_IDN.csv` belum ditemukan.")

# -----------------------------------------------------------------------------
# TAB 3: DIGITAL SOCIETY PROJECT (DSP) DENGAN VARIABEL TURUNAN LENGKAP
# -----------------------------------------------------------------------------
with tab_dsp:
    st.subheader("🛡️ Digital Society Project (DSP) - Tata Kelola & Kebebasan Digital")
    st.markdown("Analisis disinformasi, sensor internet, pembatasan jaringan, serta variabel turunan estimasi kelembagaan.")
    
    if not df_dsp.empty:
        # Kamus lengkap variabel DSP beserta turunan metriknya (Low, High, SD, Mean, dll.)
        dsp_master = {
            "Penyebaran Informasi Palsu oleh Pemerintah (v2smgovdom)": {
                "base": "v2smgovdom", 
                "desc": "Seberapa sering agen pemerintah menyebarkan informasi palsu/menyesatkan di media sosial.",
                "deriv": ["v2smgovdom_codelow", "v2smgovdom_codehigh", "v2smgovdom_sd", "v2smgovdom_mean"]
            },
            "Penyebaran Informasi Palsu oleh Partai Politik (v2smpardom)": {
                "base": "v2smpardom", 
                "desc": "Frekuensi partai politik menyebarkan informasi menyesatkan untuk memengaruhi populasi.",
                "deriv": ["v2smpardom_codelow", "v2smpardom_codehigh", "v2smpardom_sd", "v2smpardom_mean"]
            },
            "Kapasitas Filter / Sensor Internet Pemerintah (v2smgovfilcap)": {
                "base": "v2smgovfilcap", 
                "desc": "Kapasitas teknis pemerintah dalam menyensor informasi internet melalui pemblokiran situs.",
                "deriv": ["v2smgovfilcap_codelow", "v2smgovfilcap_codehigh", "v2smgovfilcap_sd", "v2smgovfilcap_mean"]
            },
            "Pemadaman Akses Internet oleh Pemerintah (v2smgovshut)": {
                "base": "v2smgovshut", 
                "desc": "Frekuensi pemerintah mematikan akses domestik ke internet dalam praktiknya.",
                "deriv": ["v2smgovshut_codelow", "v2smgovshut_codehigh", "v2smgovshut_sd", "v2smgovshut_mean"]
            },
            "Perlindungan Hukum Privasi Pengguna (v2smprivex)": {
                "base": "v2smprivex", 
                "desc": "Keberadaan kerangka hukum formal untuk melindungi privasi pengguna internet dan data pribadi.",
                "deriv": ["v2smprivex_codelow", "v2smprivex_codehigh", "v2smprivex_sd", "v2smprivex_mean"]
            },
            "Perlindungan Hukum Defamation & Ujaran Kebencian (v2smlawpr)": {
                "base": "v2smlawpr", 
                "desc": "Sejauh mana kerangka hukum melindungi konten pencemaran nama baik atau ujaran kebencian daring.",
                "deriv": ["v2smlawpr_codelow", "v2smlawpr_codehigh", "v2smlawpr_sd", "v2smlawpr_mean"]
            }
        }
        
        selected_dsp_label = st.selectbox("Pilih Indikator Utama Tata Kelola DSP:", list(dsp_master.keys()), key="sel_dsp")
        info_meta = dsp_master[selected_dsp_label]
        var_code = info_meta["base"]
        
        # Kotak Codebook Interaktif (Mirip V-Dem di Gambar 2)
        with st.expander("📖 Penjelasan & Metadata dari Codebook DSP"):
            st.markdown(f"**Nama Variabel Utama (Kode):** `{var_code}`")
            st.markdown(f"**Definisi / Deskripsi:** {info_meta['desc']}")
            
            # Tampilkan variabel turunan jika ada di dataframe
            available_deriv = [col for col in info_meta["deriv"] if col in df_dsp.columns]
            if available_deriv:
                st.markdown(f"**Variabel Turunan / Metrik Pendukung yang Tersedia:** `{', '.join(available_deriv)}`")
            
            st.markdown("🔗 *Sumber Dokumen: Digital Society Project (DSP) Codebook & Methodology*")
        
        if var_code in df_dsp.columns and "year" in df_dsp.columns:
            # Ambil kolom utama + kolom turunan yang tersedia
            cols_to_plot = ["year", var_code] + [c for c in info_meta["deriv"] if c in df_dsp.columns]
            df_plot_dsp = df_dsp[cols_to_plot].dropna(subset=["year", var_code]).sort_values("year")
            
            fig_dsp = px.line(
                df_plot_dsp,
                x="year",
                y=var_code,
                markers=True,
                title=f"Runtun Waktu: {selected_dsp_label}",
                labels={"year": "Tahun", var_code: "Skor Estimasi / Indeks"},
                template="plotly_white"
            )
            fig_dsp.update_traces(line=dict(width=2.5, color="#d62728"), marker=dict(size=7))
            st.plotly_chart(fig_dsp, use_container_width=True, key="chart_dsp_main")
            
            # Jika ada variabel turunan (misalnya codelow/codehigh), tampilkan dalam sub-grafik atau perbandingan
            if len(available_deriv) > 0:
                with st.expander("📈 Analisis Variabel Turunan (Interval Kepercayaan / Error Bounds)"):
                    st.markdown("Menampilkan perbandingan nilai estimasi utama dengan batas bawah/atas atau parameter turunan terkait:")
                    fig_deriv = px.line(
                        df_plot_dsp,
                        x="year",
                        y=[var_code] + available_deriv,
                        markers=True,
                        title=f"Perbandingan Metrik Turunan untuk {var_code}",
                        labels={"year": "Tahun", "value": "Nilai Skor", "variable": "Metrik / Parameter"},
                        template="plotly_white"
                    )
                    st.plotly_chart(fig_deriv, use_container_width=True, key="chart_dsp_deriv")
            
            with st.expander("📋 Lihat Tabel Lengkap & Unduh Data DSP Ini"):
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
        st.info("File `DSP_CY_IDN.csv` belum ditemukan.")
