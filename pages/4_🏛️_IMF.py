import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="IMF Data Explorer - Indonesia", layout="wide")

st.title("🏛️ Portal Data IMF (World Economic Outlook - Indonesia)")
st.write(
    "Eksplorasi indikator makroekonomi, neraca pembayaran, dan proyeksi fiskal resmi **International Monetary Fund (IMF)** "
    "khusus untuk wilayah **Indonesia (IDN)** langsung via **IMF DataMapper API**."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# 1. Pemuatan Katalog Indikator Resmi WEO IMF
@st.cache_data(ttl=86400)
def load_imf_catalog():
    url = "https://www.imf.org/external/datamapper/api/v1/indicators"
    try:
        res = requests.get(url, headers=HEADERS, timeout=20)
        data = res.json()
        indicators = []
        raw_dict = data.get("indicators", {})
        for code, meta in raw_dict.items():
            indicators.append({
                "id": code,
                "label": meta.get("label", code),
                "description": meta.get("description", ""),
                "unit": meta.get("unit", ""),
                "dataset": meta.get("dataset", "WEO")
            })
        return indicators
    except Exception:
        return []

with st.spinner("Menghubungkan ke katalog IMF DataMapper..."):
    imf_catalog = load_imf_catalog()

# 2. Kotak Pencarian Indikator
st.subheader("1. Pemilihan Indikator IMF")
query_imf = st.text_input(
    "🔍 Cari topik makroekonomi IMF (misal: 'GDP', 'Inflation', 'Debt', 'Current account', 'Investment'):",
    value="GDP"
).strip()

if query_imf and imf_catalog:
    tokens = query_imf.lower().split()
    results = [
        ind for ind in imf_catalog
        if all(token in ind["label"].lower() or token in ind["id"].lower() for token in tokens)
    ]
    # Urutkan berdasarkan judul terpendek agar indikator utama muncul teratas
    results = sorted(results, key=lambda x: (len(x["label"]), x["label"]))

    if results:
        st.success(f"Ditemukan {len(results)} indikator resmi IMF untuk pencarian '{query_imf}'!")

        selected_ind = st.selectbox(
            "Pilih Indikator Resmi IMF:",
            options=results,
            format_func=lambda item: f"{item['label']} ({item['unit']})" if item['unit'] else item['label']
        )

        kode_imf = selected_ind["id"]

        with st.expander("ℹ️ Definisi & Metadata Resmi IMF", expanded=False):
            st.markdown(f"**Series Code:** `{kode_imf}`")
            st.markdown(f"**Database:** `{selected_ind['dataset']}`")
            st.markdown(f"**Satuan Pengukuran:** `{selected_ind['unit'] if selected_ind['unit'] else 'N/A'}`")
            st.markdown(f"**Deskripsi Resmi IMF:**\n{selected_ind['description'] if selected_ind['description'] else 'Tidak ada catatan deskripsi tambahan.'}")

        # 3. Penarikan Data Runtun Waktu untuk Indonesia (IDN)
        if st.button("📊 Ambil Data IMF Indonesia", type="primary"):
            with st.spinner(f"Menarik runtun waktu resmi IMF untuk {selected_ind['label']}..."):
                data_url = f"https://www.imf.org/external/datamapper/api/v1/{kode_imf}/IDN"
                try:
                    r = requests.get(data_url, headers=HEADERS, timeout=15)
                    data_json = r.json()

                    # Struktur DataMapper API: values -> {kode_indikator} -> IDN -> {tahun: nilai}
                    values_dict = data_json.get("values", {}).get(kode_imf, {}).get("IDN", {})

                    if values_dict:
                        records = []
                        for thn_str, val in values_dict.items():
                            try:
                                records.append({"Tahun": int(thn_str), "Nilai": round(float(val), 2)})
                            except (ValueError, TypeError):
                                continue

                        df_imf = pd.DataFrame(records).sort_values(by="Tahun", ascending=True)

                        st.divider()
                        st.markdown(
                            f"🔗 **Tautan Data Portal Resmi:** [IMF DataMapper - {selected_ind['label']}](https://www.imf.org/external/datamapper/{kode_imf}@WEO/IDN)"
                        )

                        # Tombol Unduh Data
                        c1, c2 = st.columns(2)
                        c1.download_button(
                            "📥 Unduh CSV",
                            df_imf.to_csv(index=False).encode("utf-8"),
                            f"IMF_{kode_imf}_IDN.csv",
                            "text/csv"
                        )
                        buf = io.BytesIO()
                        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                            df_imf.to_excel(writer, index=False, sheet_name="IMF Data")
                        c2.download_button(
                            "📊 Unduh Excel (.xlsx)",
                            buf.getvalue(),
                            f"IMF_{kode_imf}_IDN.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                        # Visualisasi Interaktif Plotly
                        satuan = selected_ind["unit"] if selected_ind["unit"] else "Nilai"
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df_imf["Tahun"],
                            y=df_imf["Nilai"],
                            mode="lines+markers",
                            name="Indonesia (IMF WEO)",
                            line=dict(width=2.5, color="#8B0000"),  # Corak Merah Khas IMF
                            hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y}} {satuan}<extra></extra>"
                        ))
                        fig.update_layout(
                            xaxis=dict(title="Tahun", tickmode="linear"),
                            yaxis=dict(title=satuan),
                            hovermode="x unified",
                            margin=dict(l=20, r=20, t=40, b=20)
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        with st.expander("📋 Tabel Runtun Waktu Lengkap (Termasuk Proyeksi WEO)"):
                            st.dataframe(
                                df_imf.sort_values(by="Tahun", ascending=False),
                                use_container_width=True
                            )
                    else:
                        st.warning("Indikator ini terdaftar di IMF, tetapi observasi data runtun waktu untuk Indonesia tidak tersedia.")
                except Exception as e:
                    st.error(f"Gagal mengambil data dari server IMF: {e}")
    else:
        st.warning(f"Tidak ada indikator IMF yang cocok dengan kata kunci '{query_imf}'.")
