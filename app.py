import streamlit as st
import pandas as pd
import requests
import io

st.set_page_config(page_title="Pencari Data World Bank Indonesia", layout="wide")

st.title("🇮🇩 World Bank Data Explorer - Indonesia")
st.write("Akses dan unduh data time-series resmi langsung dari **World Bank Open Data**.")

# Kamus Indikator Utama (Satu baris per entri agar bebas dari syntax error)
POPULAR_INDICATORS = {
    "Inflasi, IHK / Consumer Prices (annual %) [FP.CPI.TOTL.ZG]": "FP.CPI.TOTL.ZG",
    "Pertumbuhan PDB Riil / GDP Growth (annual %) [NY.GDP.MKTP.KD.ZG]": "NY.GDP.MKTP.KD.ZG",
    "PDB per Kapita (Current US$) [NY.GDP.PCAP.CD]": "NY.GDP.PCAP.CD",
    "Tingkat Pengangguran (% angkatan kerja) [SL.UEM.TOTL.ZS]": "SL.UEM.TOTL.ZS",
    "Tingkat Kemiskinan Rasio Nasional (% populasi) [SI.POV.NAHC]": "SI.POV.NAHC",
    "Pengguna Internet (% populasi) [IT.NET.USER.ZS]": "IT.NET.USER.ZS",
    "Investasi Asing Langsung / FDI Net Inflows (% PDB) [BX.KLT.DINV.WD.GD.ZS]": "BX.KLT.DINV.WD.GD.ZS",
    "Ekspor Barang & Jasa (% PDB) [NE.EXP.GNFS.ZS]": "NE.EXP.GNFS.ZS",
    "Impor Barang & Jasa (% PDB) [NE.IMP.GNFS.ZS]": "NE.IMP.GNFS.ZS",
    "Nilai Tukar Resmi / Exchange Rate (LCU per US$, rata-rata) [PA.NUS.FCRF]": "PA.NUS.FCRF",
    "Cadangan Devisa / Total Reserves inc. Gold (Current US$) [FI.RES.TOTL.CD]": "FI.RES.TOTL.CD",
    "Penerimaan Pajak / Tax Revenue (% PDB) [GC.TAX.TOTL.GD.ZS]": "GC.TAX.TOTL.GD.ZS"
}

# Mode Pemilihan
mode = st.radio(
    "Pilih Metode Pencarian Data:",
    ["Daftar Indikator Utama (Direkomendasikan)", "Ketik Kode Indikator Manual"],
    horizontal=True
)

kode_terpilih = None
nama_tampilan = ""

if mode == "Daftar Indikator Utama (Direkomendasikan)":
    nama_tampilan = st.selectbox("Pilih Indikator:", list(POPULAR_INDICATORS.keys()))
    kode_terpilih = POPULAR_INDICATORS[nama_tampilan]
else:
    st.info("Kamu bisa memasukkan kode indikator resmi World Bank apa saja (contoh: FP.CPI.TOTL.ZG, NY.GDP.MKTP.KD.ZG, dsb).")
    kode_manual = st.text_input("Masukkan Kode Indikator:", value="FP.CPI.TOTL.ZG").strip()
    if kode_manual:
        kode_terpilih = kode_manual
        nama_tampilan = f"Indikator [{kode_terpilih}]"

# Tombol Eksekusi
if kode_terpilih and st.button("📊 Tampilkan Data", type="primary"):
    with st.spinner(f"Menghubungi World Bank API untuk kode {kode_terpilih}..."):
        data_url = f"https://api.worldbank.org/v2/country/IDN/indicator/{kode_terpilih}?format=json&per_page=120"
        
        try:
            r = requests.get(data_url, timeout=15)
            data_json = r.json()
            
            records = []
            if len(data_json) > 1 and data_json[1]:
                indicator_name_api = data_json[1][0]["indicator"]["value"]
                for item in data_json[1]:
                    thn = item.get("date")
                    val = item.get("value")
                    if val is not None:
                        records.append({"Tahun": int(thn), "Nilai": float(val)})
                
                if records:
                    df = pd.DataFrame(records).sort_values(by="Tahun", ascending=True)
                    link_resmi = f"https://data.worldbank.org/indicator/{kode_terpilih}?locations=ID"
                    
                    st.divider()
                    st.success(f"✅ Berhasil mengambil data: **{indicator_name_api}**")
                    st.markdown(f"🔗 **Sumber Primer:** [Buka Halaman Resmi World Bank DataBank]({link_resmi})")
                    
                    # Tombol Download
                    col1, col2 = st.columns(2)
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    col1.download_button(
                        label="📥 Unduh Data (CSV)",
                        data=csv_data,
                        file_name=f"{kode_terpilih}_indonesia.csv",
                        mime="text/csv"
                    )
                    
                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name="Data")
                    col2.download_button(
                        label="📊 Unduh Data (Excel .xlsx)",
                        data=buffer.getvalue(),
                        file_name=f"{kode_terpilih}_indonesia.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    
                    # Visualisasi
                    st.subheader("📈 Tren Historis")
                    st.line_chart(df.set_index("Tahun")["Nilai"])
                    
                    # Tabel
                    with st.expander("📋 Tabel Angka Lengkap"):
                        st.dataframe(df.sort_values(by="Tahun", ascending=False), use_container_width=True)
                else:
                    st.warning(f"Indikator '{kode_terpilih}' terdaftar, tetapi tidak memiliki data untuk Indonesia.")
            else:
                st.error(f"Kode '{kode_terpilih}' tidak ditemukan di sistem World Bank.")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memanggil data: {e}")
