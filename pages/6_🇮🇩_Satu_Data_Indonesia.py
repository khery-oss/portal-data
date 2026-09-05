import io
import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Satu Data Indonesia - IndoEcon", layout="wide")

st.title("🇮🇩 Satu Data Indonesia (SDI) - Portal Data Terbuka Nasional")
st.markdown(
    "Eksplorasi dataset resmi kementerian, lembaga pemerintah, dan BPS melalui "
    "**CKAN REST API Resmi Satu Data Indonesia (`data.go.id`)** secara *real-time* (*100% Live API*)."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

st.subheader("1. Pencarian Dataset Nasional")
c_query, c_rows = st.columns([3, 1])

with c_query:
    keyword = st.text_input(
        "Kata Kunci Pencarian:",
        value="inflasi",
        placeholder="Contoh: inflasi, kemiskinan, pdrb, beras, tenaga kerja..."
    )

with c_rows:
    limit = st.selectbox("Jumlah Hasil:", [10, 20, 30], index=0)

if st.button("🔍 Cari Dataset di SDI (Live API)", type="primary"):
    if not keyword.strip():
        st.warning("Silakan masukkan kata kunci pencarian.")
    else:
        with st.spinner(f"Menghubungi katalog API Satu Data Indonesia untuk kata kunci '{keyword}'..."):
            api_url = "https://katalog.data.go.id/api/3/action/package_search"
            params = {
                "q": keyword.strip(),
                "rows": limit
            }

            try:
                res = requests.get(api_url, params=params, headers=HEADERS, timeout=25)
                if res.status_code == 200:
                    payload = res.json()
                    if payload.get("success"):
                        results = payload.get("result", {}).get("results", [])
                        
                        records = []
                        for item in results:
                            title = item.get("title", "")
                            org = item.get("organization", {}).get("title", "Instansi Pemerintah")
                            notes = item.get("notes", "Tidak ada deskripsi.")
                            
                            # Ambil tautan sumber data (CSV/XLSX/PDF)
                            resources = item.get("resources", [])
                            res_links = []
                            for r in resources:
                                r_format = str(r.get("format", "")).upper()
                                r_url = r.get("url", "")
                                if r_url:
                                    res_links.append(f"[{r_format or 'LINK'}]({r_url})")

                            records.append({
                                "Judul Dataset": title,
                                "Instansi Produsen Data": org,
                                "Deskripsi Singkat": notes[:200] + "..." if len(notes) > 200 else notes,
                                "Berkas & Format Tersedia": " | ".join(res_links) if res_links else "Tautan internal",
                                "raw_resources": resources
                            })

                        if records:
                            st.session_state["sdi_results"] = records
                            st.success(f"Ditemukan {len(records)} dataset resmi langsung dari Portal Satu Data Indonesia!")
                        else:
                            st.warning(f"Tidak ada dataset yang cocok dengan kata kunci '{keyword}'. Coba kata kunci lain.")
                    else:
                        st.error("Permintaan API berhasil tetapi respons menyatakan tidak berhasil.")
                else:
                    st.error(f"Gagal menghubungi server Satu Data Indonesia (Status HTTP: {res.status_code}).")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses data: {e}")

# =============================================================================
# 2. TAMPILAN HASIL & DETAIL DATASET
# =============================================================================
if "sdi_results" in st.session_state:
    st.divider()
    st.subheader("2. Hasil Penelusuran Dataset")
    
    data_list = st.session_state["sdi_results"]
    df_display = pd.DataFrame([
        {
            "Judul Dataset": d["Judul Dataset"],
            "Instansi Produsen Data": d["Instansi Produsen Data"],
            "Deskripsi": d["Deskripsi Singkat"]
        }
        for d in data_list
    ])

    # Ekspor Hasil Katalog
    c1, c2 = st.columns(2)
    c1.download_button(
        "📥 Unduh Daftar Temuan (CSV)",
        df_display.to_csv(index=False).encode("utf-8"),
        "SDI_Hasil_Pencarian.csv",
        "text/csv"
    )
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df_display.to_excel(writer, index=False)
    c2.download_button(
        "📊 Unduh Daftar Temuan (.xlsx)",
        buf.getvalue(),
        "SDI_Hasil_Pencarian.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.dataframe(df_display, use_container_width=True)

    # Detail dan Pratinjau Dataset Terpilih
    st.subheader("3. Pratinjau & Unduh File Sumber")
    pilihan_judul = st.selectbox(
        "Pilih salah satu dataset untuk melihat berkas yang dapat diunduh:",
        [d["Judul Dataset"] for d in data_list]
    )

    selected_item = next(d for d in data_list if d["Judul Dataset"] == pilihan_judul)
    st.markdown(f"**Instansi:** {selected_item['Instansi Produsen Data']}")
    st.markdown(f"**Deskripsi Lengkap:**\n{selected_item['Deskripsi Singkat']}")

    resources = selected_item["raw_resources"]
    if resources:
        st.write("**Daftar Berkas Data Terlampir:**")
        for idx, res_item in enumerate(resources):
            f_format = str(res_item.get("format", "File")).upper()
            f_name = res_item.get("name") or f"Berkas Sumber #{idx+1}"
            f_url = res_item.get("url", "")
            
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"📄 **{f_name}** `[{f_format}]`")
            with col_b:
                if f_url:
                    st.link_button("🌐 Buka / Unduh", f_url)
    else:
        st.info("Dataset ini tidak memiliki lampiran berkas publik langsung.")
