import io
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="World Bank Data Explorer - Indonesia", layout="wide"
)

st.title("🌐 World Bank Open Data Explorer - Indonesia")
st.write(
    "Eksplorasi indikator resmi **World Bank** untuk Indonesia secara otomatis dan *real-time*."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 1. Ambil seluruh katalog indikator resmi World Bank (WDI)
@st.cache_data(ttl=86400)
def load_all_indicators():
    indicators = []
    url = "https://api.worldbank.org/v2/indicator?format=json&per_page=4000"
    try:
        res = requests.get(url, headers=HEADERS, timeout=20)
        data = res.json()
        if len(data) > 1 and data[1]:
            for item in data[1]:
                ind_id = item.get("id")
                ind_name = item.get("name")
                if ind_id and ind_name and not ind_id.startswith("6.") and not ind_id.startswith("7."):
                    indicators.append({
                        "id": ind_id,
                        "name": ind_name,
                        "sourceNote": item.get("sourceNote", ""),
                        "sourceOrg": item.get("sourceOrganization", "World Bank")
                    })
    except Exception:
        pass
    return indicators

with st.spinner("Menghubungkan ke katalog data World Bank..."):
    all_indicators = load_all_indicators()

# 2. Input pencarian fleksibel (Multi-token)
query = st.text_input(
    "🔍 Ketik topik/variabel (Bahasa Inggris, misal: 'gdp', 'inflation', 'poverty', 'debt', 'tax', 'education'):",
    value="gdp",
).strip()

if query and all_indicators:
    query_tokens = query.lower().split()
    results = [
        ind for ind in all_indicators
        if all(token in ind["name"].lower() or token in ind["id"].lower() for token in query_tokens)
    ]

    if results:
        st.success(
            f"Ditemukan {len(results)} indikator terkait kata kunci '{query}' pada database World Bank!"
        )

        # Mencegah tabrakan nama duplikat: Simpan objek indikator dalam list,
        # dan gunakan format_func agar dropdown HANYA menampilkan nama bersih tanpa kode API!
        selected_ind = st.selectbox(
            "Pilih Indikator Hasil Pencarian:",
            options=results,
            format_func=lambda item: item["name"]  # <-- Kode API disembunyikan sepenuhnya dari dropdown
        )

        kode_indikator = selected_ind["id"]

        # Tampilkan deskripsi & metodologi jika ada
        with st.expander("ℹ️ Definisi & Metodologi Resmi Indikator Ini"):
            st.markdown(f"**Organisasi Sumber:** {selected_ind['sourceOrg']}")
            st.markdown(f"**Definisi:** {selected_ind['sourceNote'] if selected_ind['sourceNote'] else 'Tidak ada deskripsi rinci.'}")

        if st.button("📊 Ambil Data Indonesia", type="primary"):
            with st.spinner("Mengunduh runtun waktu resmi dari server World Bank..."):
                data_url = f"https://api.worldbank.org/v2/country/IDN/indicator/{kode_indikator}?format=json&per_page=120"
                try:
                    r_data = requests.get(data_url, headers=HEADERS, timeout=15)
                    data_json = r_data.json()

                    records = []
                    if len(data_json) > 1 and data_json[1]:
                        for item in data_json[1]:
                            thn = item.get("date")
                            val = item.get("value")
                            if val is not None:
                                try:
                                    records.append(
                                        {"Tahun": int(thn), "Nilai": round(float(val), 2)}
                                    )
                                except (ValueError, TypeError):
                                    continue

                    if records:
                        df = pd.DataFrame(records).sort_values(by="Tahun", ascending=True)
                        link_resmi = f"https://data.worldbank.org/indicator/{kode_indikator}?locations=ID"

                        st.divider()
                        st.markdown(
                            f"🔗 **Halaman Resmi World Bank:** [{selected_ind['name']}]({link_resmi})"
                        )

                        # Tombol Unduh
                        col1, col2 = st.columns(2)
                        csv_data = df.to_csv(index=False).encode("utf-8")
                        col1.download_button(
                            label="📥 Unduh Data (CSV)",
                            data=csv_data,
                            file_name=f"{kode_indikator}_indonesia.csv",
                            mime="text/csv",
                        )

                        buffer = io.BytesIO()
                        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                            df.to_excel(writer, index=False, sheet_name="Data")
                        col2.download_button(
                            label="📊 Unduh Data (Excel .xlsx)",
                            data=buffer.getvalue(),
                            file_name=f"{kode_indikator}_indonesia.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )

                        # Visualisasi & Tabel
                        st.subheader("📈 Visualisasi Tren")
                        st.line_chart(df.set_index("Tahun")["Nilai"])

                        with st.expander("📋 Tabel Angka Lengkap"):
                            st.dataframe(
                                df.sort_values(by="Tahun", ascending=False),
                                use_container_width=True,
                            )
                    else:
                        st.warning(
                            "Indikator ini terdaftar di World Bank, namun observasi angka untuk Indonesia tidak tersedia pada seri ini. Silakan coba varian indikator lain."
                        )
                except Exception as e:
                    st.error(f"Gagal mengambil data dari server World Bank: {e}")
    else:
        st.warning(
            f"Tidak ditemukan indikator dengan kata kunci '{query}'. Gunakan istilah umum dalam bahasa Inggris."
        )
