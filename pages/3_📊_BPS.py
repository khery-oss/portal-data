import io
import time
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="BPS Data Explorer - Live Catalog", layout="wide")

st.title("📊 Portal Data BPS Nasional (Live Catalog BPS)")
st.write(
    "Eksplorasi langsung seluruh katalog data resmi **Badan Pusat Statistik (BPS)** tingkat Nasional. "
    "Mencakup 52 Subjek dan lebih dari 1.700 variabel indikator resmi (1945–2025)."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

api_key = st.secrets.get("BPS_APP_ID") or st.secrets.get("BPS_API_KEY")
if not api_key:
    st.error("⚠️ Key BPS belum disetel di Streamlit Secrets (`BPS_APP_ID`).")
    st.stop()

DOMAIN = "0000"  # Agregat Nasional

# ==============================================================================
# 1. Mengambil Seluruh Subjek Resmi BPS (52 Subjek dari 6 Halaman)
# ==============================================================================
@st.cache_data(ttl=86400)
def fetch_all_bps_subjects():
    subjects = {}
    page = 1
    while True:
        url = f"https://webapi.bps.go.id/v1/api/list/model/subject/domain/{DOMAIN}/page/{page}/key/{api_key}/"
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            res = r.json()
            if res.get("status") == "OK" and len(res.get("data", [])) > 1:
                items = res["data"][1]
                for it in items:
                    cat_name = it.get("subcat", "Umum")
                    sub_title = it.get("title", "")
                    sub_id = it.get("sub_id")
                    label = f"[{cat_name}] {sub_title}"
                    subjects[label] = sub_id
                
                total_pages = res["data"][0].get("pages", 1)
                if page >= total_pages:
                    break
                page += 1
            else:
                break
        except Exception:
            break
    return subjects

# ==============================================================================
# 2. Mengambil Seluruh Variabel Indikator di Bawah Subjek Terpilih
# ==============================================================================
@st.cache_data(ttl=43200)
def fetch_variables_by_subject(sub_id):
    variables = {}
    page = 1
    while True:
        url = f"https://webapi.bps.go.id/v1/api/list/model/var/domain/{DOMAIN}/sub/{sub_id}/page/{page}/key/{api_key}/"
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            res = r.json()
            if res.get("status") == "OK" and len(res.get("data", [])) > 1:
                items = res["data"][1]
                for it in items:
                    v_title = it.get("title", "")
                    v_id = it.get("var_id")
                    v_unit = it.get("unit", "Tidak Ada Satuan")
                    v_notes = it.get("notes", "")
                    variables[f"{v_title} (ID: {v_id})"] = {
                        "id": v_id,
                        "unit": v_unit,
                        "notes": v_notes
                    }
                
                total_pages = res["data"][0].get("pages", 1)
                if page >= total_pages:
                    break
                page += 1
            else:
                break
        except Exception:
            break
    return variables

with st.spinner("Menghubungkan ke katalog resmi BPS..."):
    all_subjects = fetch_all_bps_subjects()

if not all_subjects:
    st.error("Gagal memuat katalog subjek dari server BPS. Silakan muat ulang beberapa saat lagi.")
    st.stop()

# ==============================================================================
# 3. Kontrol Pemilihan Taksonomi Resmi BPS
# ==============================================================================
st.subheader("1. Pilih Subjek & Indikator dari Katalog BPS")
col_s, col_v = st.columns([1, 2])

with col_s:
    selected_sub_label = st.selectbox(
        f"Subjek Resmi BPS ({len(all_subjects)} Subjek Tersedia):",
        options=sorted(list(all_subjects.keys()))
    )
    selected_sub_id = all_subjects[selected_sub_label]

with col_v:
    vars_in_sub = fetch_variables_by_subject(selected_sub_id)
    if vars_in_sub:
        selected_var_label = st.selectbox(
            f"Indikator / Tabel Dinamis BPS ({len(vars_in_sub)} Variabel Tersedia):",
            options=list(vars_in_sub.keys())
        )
        selected_var_info = vars_in_sub[selected_var_label]
        selected_var_id = selected_var_info["id"]
    else:
        st.warning("Tidak ada variabel indikator dinamis aktif pada subjek ini.")
        st.stop()

# ==============================================================================
# 4. Rentang Waktu Observasi (1945–2025)
# ==============================================================================
st.subheader("2. Rentang Waktu Observasi")
YEARS = [str(y) for y in range(1945, 2026)]

col_t1, col_t2 = st.columns(2)
with col_t1:
    th_start = st.selectbox("Tahun Mulai:", YEARS, index=YEARS.index("2010"))
with col_t2:
    th_end = st.selectbox("Tahun Selesai:", YEARS, index=YEARS.index("2024"))

if int(th_start) > int(th_end):
    st.error("Tahun mulai tidak boleh melebihi tahun selesai.")
    st.stop()

# ==============================================================================
# 5. Penarikan Data Multi-Tahun dari WebAPI BPS
# ==============================================================================
if st.button("📊 Muat Data Resmi BPS", type="primary"):
    selected_years = [str(y) for y in range(int(th_start), int(th_end) + 1)]
    # BPS membatasi maksimal 3 tahun per request di endpoint data
    batches = [selected_years[i:i + 3] for i in range(0, len(selected_years), 3)]

    records = []
    progress_bar = st.progress(0)
    status_txt = st.empty()

    for idx, b in enumerate(batches):
        th_param = ";".join(b) if len(b) > 1 else b[0]
        status_txt.text(f"Mengunduh blok data BPS periode {b[0]}–{b[-1]}...")
        
        data_url = f"https://webapi.bps.go.id/v1/api/list/model/data/domain/{DOMAIN}/var/{selected_var_id}/th/{th_param}/key/{api_key}/"
        try:
            r = requests.get(data_url, headers=HEADERS, timeout=25)
            res = r.json()
            if res.get("status") == "OK" and res.get("data-availability") != "list-not-available":
                datacontent = res.get("datacontent", {})
                vervar = {str(item["val"]): item["label"] for item in res.get("vervar", [])}
                tahun_dict = {str(item["val"]): str(item["label"]) for item in res.get("tahun", [])}

                for cell_key, val in datacontent.items():
                    if val is not None:
                        k_str = str(cell_key)
                        
                        # Ambil label rincian (vervar)
                        rincian_lbl = "Nasional"
                        for v_val, v_lbl in vervar.items():
                            if k_str.startswith(v_val):
                                rincian_lbl = v_lbl
                                break
                        
                        # Ambil label tahun
                        tahun_lbl = None
                        for t_val, t_lbl in tahun_dict.items():
                            if t_val in k_str:
                                tahun_lbl = t_lbl
                                break

                        if tahun_lbl and tahun_lbl in selected_years:
                            records.append({
                                "Tahun": tahun_lbl,
                                "Kategori / Rincian": rincian_lbl,
                                "Nilai": val
                            })
            time.sleep(0.1)
        except Exception:
            pass

        progress_bar.progress((idx + 1) / len(batches))

    status_txt.empty()
    progress_bar.empty()

    # Bentuk grid data lengkap 1945-2025 sesuai pilihan user
    df_grid = pd.DataFrame({"Tahun": selected_years})

    if records:
        df_raw = pd.DataFrame(records).drop_duplicates()
        df_pivot = df_raw.pivot(index="Tahun", columns="Kategori / Rincian", values="Nilai").reset_index()
        df_final = pd.merge(df_grid, df_pivot, on="Tahun", how="left").sort_values("Tahun")

        st.success(f"Data resmi berhasil dimuat: **{selected_var_label}**")
        if selected_var_info["unit"] != "Tidak Ada Satuan":
            st.caption(f"Satuan Resmi BPS: **{selected_var_info['unit']}**")

        st.divider()

        # Visualisasi Grafik
        st.subheader(f"📈 Tren Deret Waktu: {selected_var_label}")
        fig = go.Figure()
        
        value_cols = [c for c in df_final.columns if c != "Tahun"]
        for col in value_cols:
            fig.add_trace(go.Scatter(
                x=df_final["Tahun"],
                y=df_final[col],
                mode="lines+markers",
                name=col,
                connectgaps=False,  # Memutus grafik jika data tahun lampau belum ada survei
                hovertemplate=f"Tahun %{{x}}<br>{col}: %{{y}}<extra></extra>"
            ))

        fig.update_layout(
            xaxis=dict(title="Tahun", tickmode="linear"),
            yaxis=dict(title=selected_var_info["unit"] if selected_var_info["unit"] != "Tidak Ada Satuan" else "Nilai"),
            hovermode="x unified",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabel Observasi & Ekspor
        st.subheader("📋 Tabel Data Observasi")
        col_d1, col_d2 = st.columns(2)
        col_d1.download_button(
            "📥 Unduh CSV",
            df_final.to_csv(index=False).encode("utf-8"),
            f"BPS_{selected_var_id}_{th_start}_{th_end}.csv",
            "text/csv"
        )

        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
            df_final.to_excel(writer, index=False, sheet_name="Data BPS")
        col_d2.download_button(
            "📊 Unduh Excel (.xlsx)",
            buf.getvalue(),
            f"BPS_{selected_var_id}_{th_start}_{th_end}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.dataframe(df_final.fillna("-"), use_container_width=True)
        st.caption("💡 Tanda strip (-) menandakan bahwa pada tahun tersebut BPS belum merilis rekaman survei di basis data digital.")

    else:
        st.warning(
            f"Tabel indikator *'{selected_var_label}'* tercatat di katalog BPS, "
            f"tetapi server BPS tidak memiliki catatan angka pada rentang {th_start}–{th_end}."
        )
        st.info("Variabel ini mungkin hanya dirilis pada publikasi cetak tertentu atau periode surveinya berbeda. Silakan pilih indikator lainnya.")
