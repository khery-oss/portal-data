import io
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="Data Download Hub - IE IndoEcon Explorer",
    page_icon="📥",
    layout="wide"
)

st.title("📥 Pusat Unduh Data Multi-Indikator")
st.markdown(
    "Unduh data lintas lembaga (*World Bank*, *FRED*, dll.) secara fleksibel. "
    "Anda dapat memilih beberapa indikator sekaligus, menggabungkannya ke dalam satu matriks waktu, "
    "dan mengekspornya lengkap dengan metadata sumber resmi."
)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# =============================================================================
# 1. PILIH SUMBER & INDIKATOR
# =============================================================================
st.subheader("1. Pilih Indikator yang Ingin Diunduh")

col_src1, col_src2 = st.columns(2)

with col_src1:
    st.markdown("🌐 **World Bank (WDI) - Indonesia**")
    wb_choices = {
        "PDB Riil (Constant LCU) [NY.GDP.MKTP.KN]": "NY.GDP.MKTP.KN",
        "Pertumbuhan PDB (% per tahun) [NY.GDP.MKTP.KD.ZG]": "NY.GDP.MKTP.KD.ZG",
        "Inflasi / IHK (% tahunan) [FP.CPI.TOTL.ZG]": "FP.CPI.TOTL.ZG",
        "Populasi Pengguna Internet (% dari total populasi) [IT.NET.USER.ZS]": "IT.NET.USER.ZS"
    }
    selected_wb = st.multiselect("Pilih indikator World Bank:", list(wb_choices.keys()))

with col_src2:
    st.markdown("📈 **FRED - Indikator Global & Moneter**")
    fred_choices = {
        "Nilai Tukar Rupiah per USD [DEXINUS]": "DEXINUS",
        "Suku Bunga Acuan The Fed [FEDFUNDS]": "FEDFUNDS",
        "Harga Minyak Mentah WTI [DCOILWTICO]": "DCOILWTICO"
    }
    selected_fred = st.multiselect("Pilih indikator FRED:", list(fred_choices.keys()))

# Ambil API Key FRED jika ada
fred_api_key = st.secrets.get("FRED_API_KEY", "DEMO_KEY")

# =============================================================================
# 2. PROSES PENGGABUNGAN DATA (MERGE DATA)
# =============================================================================
if st.button("🔄 Proses & Gabungkan Data", type="primary"):
    if not selected_wb and not selected_fred:
        st.warning("Silakan pilih minimal satu indikator dari World Bank atau FRED terlebih dahulu.")
        st.stop()
        
    with st.spinner("Menarik dan menyinkronkan data dari berbagai sumber..."):
        master_df = pd.DataFrame()
        metadata_source = []

        # --- Tarik Data World Bank ---
        for label in selected_wb:
            code = wb_choices[label]
            url = f"https://api.worldbank.org/v2/country/IDN/indicator/{code}?date=2000:2025&format=json"
            try:
                res = requests.get(url, headers=HEADERS, timeout=10)
                if res.status_code == 200:
                    json_data = res.json()
                    if len(json_data) > 1 and json_data[1]:
                        rows = [{"Tahun": item["date"], label: item["value"]} for item in json_data[1] if item["value"] is not None]
                        df_ind = pd.DataFrame(rows)
                        df_ind["Tahun"] = df_ind["Tahun"].astype(int)
                        
                        if master_df.empty:
                            master_df = df_ind
                        else:
                            master_df = pd.merge(master_df, df_ind, on="Tahun", how="outer")
                        metadata_source.append(f"{label}: World Bank (WDI)")
            except Exception as e:
                st.warning(f"Gagal mengambil indikator World Bank ({label}): {e}")

        # --- Tarik Data FRED ---
        for label in selected_fred:
            code = fred_choices[label]
            url = f"https://api.stlouisfed.org/fred/series/observations?series_id={code}&api_key={fred_api_key}&file_type=json"
            try:
                res = requests.get(url, headers=HEADERS, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    obs = data.get("observations", [])
                    rows = []
                    for o in obs:
                        try:
                            val = float(o["value"])
                            yr = int(o["date"][:4]) # Ambil tahunnya saja untuk penyelarasan tahunan
                            rows.append({"Tahun": yr, label: val})
                        except (ValueError, TypeError):
                            continue
                    if rows:
                        df_ind = pd.DataFrame(rows).groupby("Tahun", as_index=False).mean() # Rata-rata tahunan
                        if master_df.empty:
                            master_df = df_ind
                        else:
                            master_df = pd.merge(master_df, df_ind, on="Tahun", how="outer")
                        metadata_source.append(f"{label}: Federal Reserve Bank of St. Louis (FRED)")
            except Exception as e:
                st.warning(f"Gagal mengambil indikator FRED ({label}): {e}")

        if not master_df.empty:
            master_df = master_df.sort_values(by="Tahun", ascending=False).reset_index(drop=True)
            
            st.success(f"Berhasil menggabungkan {len(master_df.columns) - 1} indikator dari berbagai sumber!")
            
            st.subheader("2. Pratinjau Tabel Gabungan")
            st.dataframe(master_df, use_container_width=True)
            
            # Tampilkan informasi sitasi sumber di bawah tabel
            st.markdown("### 📚 Referensi Sumber Resmi untuk File Ini:")
            for src in metadata_source:
                st.markdown(f"- 📌 {src}")
            
            st.divider()
            
            # =============================================================================
            # 3. TOMBOL EKSPOR BERKELAS AKADEMIK
            # =============================================================================
            st.subheader("3. Unduh File Terpadu")
            
            col_dl1, col_dl2 = st.columns(2)
            
            # Siapkan metadata tambahan di baris bawah CSV/Excel jika diperlukan, atau ekspor murni tabel
            csv_bytes = master_df.to_csv(index=False).encode("utf-8")
            col_dl1.download_button(
                label="📥 Unduh Format CSV",
                data=csv_bytes,
                file_name="IndoEcon_MultiIndicator_Export.csv",
                mime="text/csv"
            )
            
            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
                master_df.to_excel(writer, index=False, sheet_name="Data_Terpadu")
                # Buat sheet kedua khusus catatan sumber agar rapi
                df_src = pd.DataFrame({"Indikator & Sumber Resmi": metadata_source})
                df_src.to_excel(writer, index=False, sheet_name="Metadata_Sumber")
                
            excel_bytes = output_excel.getvalue()
            col_dl2.download_button(
                label="📊 Unduh Format Excel (.xlsx - Berisi Sheet Sumber)",
                data=excel_bytes,
                file_name="IndoEcon_MultiIndicator_Export.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("Gagal memproses data. Pastikan memilih minimal satu indikator dengan benar.")
