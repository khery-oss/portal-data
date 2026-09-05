import io
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="World Bank Data Explorer - Indonesia", layout="wide"
)

st.title("🌐 World Bank Open Data Explorer - Indonesia")
st.write(
    "Eksplorasi ribuan indikator resmi **World Bank (World Development Indicators)** khusus untuk Indonesia secara otomatis."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 1. Ambil katalog indikator dari database utama World Development Indicators (Source 2)
@st.cache_data(ttl=86400)
def load_all_indicators():
    indicators = []
    # Source 2 adalah World Development Indicators (database resmi terlengkap untuk data negara)
    url = "https://api.worldbank.org/v2/indicator?source=2&format=json&per_page=3000"
    try:
        res = requests.get(url, headers=HEADERS, timeout=25)
        data = res.json()
        if len(data) > 1 and data[1]:
            for item in data[1]:
                ind_id = item.get("id")
                ind_name = item.get("name")
                if ind_id and ind_name:
                    indicators.append({
                        "id": ind_id,
                        "name": ind_name,
                        "sourceNote": item.get("sourceNote", ""),
                        "sourceOrg": item.get("sourceOrganization", "World Bank")
                    })
    except Exception:
        pass
    return indicators

with st.spinner("Menghubungkan ke katalog World Development Indicators..."):
    all_indicators = load_all_indicators()

# 2. Input pencarian fleksibel
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

    # Urutkan agar nama indikator yang lebih pendek/utama (seperti 'GDP growth') berada di urutan paling atas
    results = sorted(results, key=lambda x: (len(x["name"]), x["name"]))

    if results:
        st.success(
            f"Ditemukan {len(results)} indikator terkait kata kunci '{query}' pada database World Bank!"
        )

        # Dropdown bersih HANYA menampilkan nama indikator tanpa kode API
        selected_ind = st.selectbox(
            "Pilih Indikator Hasil Pencarian:",
            options=results,
            format_func=lambda item: item["name"]
        )

        kode_indikator = selected_ind["id"]

        with st.expander("ℹ️ Definisi & Metodologi Resmi Indikator Ini"):
            st.markdown(f"**Organisasi Sumber:** {selected_ind['sourceOrg']}")
            st.markdown(f"**Definisi:** {selected_ind['sourceNote'] if selected_ind['sourceNote'] else 'Tidak ada deskripsi rinci.'}")

        if st.button("📊 Ambil Data Indonesia", type="primary"):
            with st.spinner(f"Mengunduh runtun waktu resmi untuk {selected_ind['name']}..."):
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

                        st.subheader("📈 Visualisasi Tren")
                        st.line_chart(df.set_index("Tahun")["Nilai"])

                        with st.expander("📋 Tabel Angka Lengkap"):
                            st.dataframe(
                                df.sort_values(by="Tahun", ascending=False),
                                use_container_width=True,
                            )
                    else:
                        st.warning(
                            "Indikator ini terdaftar di World Bank, namun observasi angka khusus Indonesia tidak tersedia pada seri ini. Silakan pilih varian indikator lain."
                        )
                except Exception as e:
                    st.error(f"Gagal mengambil data dari server World Bank: {e}")
    else:
        st.warning(
            f"Tidak ditemukan indikator dengan kata kunci '{query}'. Gunakan istilah umum dalam bahasa Inggris."
        )
