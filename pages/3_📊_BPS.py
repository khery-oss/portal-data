import io
import time
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="BPS Data Explorer - Nasional", layout="wide")

st.title("📊 Portal Data BPS Nasional (Live Catalog)")
st.write(
    "Eksplorasi seluruh indikator resmi **Badan Pusat Statistik (BPS)** tingkat Nasional "
    "secara dinamis langsung dari server WebAPI BPS (1945–2025)."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

if "BPS_APP_ID" in st.secrets:
    BPS_APP_ID = st.secrets["BPS_APP_ID"]
else:
    st.error("⚠️ Masukkan `BPS_APP_ID` di Streamlit Secrets terlebih dahulu.")
    st.stop()

DOMAIN = "0000"  # Agregat Nasional

# ==========================================
# 1. Ambil Seluruh Subjek Resmi dari BPS
# ==========================================
@st.cache_data(ttl=86400)
def get_bps_subjects():
    url = f"https://webapi.bps.go.id/v1/api/list/model/sub/lang/ind/domain/{DOMAIN}/key/{BPS_APP_ID}/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        res = r.json()
        if res.get("status") == "OK" and len(res.get("data", [])) > 1:
            return {item["title"]: str(item["sub_id"]) for item in res["data"][1]}
    except Exception:
        pass
    return {}

# ==========================================
# 2. Ambil Seluruh Variabel Berdasarkan Subjek
# ==========================================
@st.cache_data(ttl=43200)
def get_variables_by_subject(sub_id):
    # Tarik seluruh halaman variabel di bawah subjek ini
    all_vars = {}
    page = 1
    while True:
        url = f"https://webapi.bps.go.id/v1/api/list/model/var/lang/ind/domain/{DOMAIN}/sub/{sub_id}/page/{page}/key/{BPS_APP_ID}/"
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            res = r.json()
            if res.get("status") == "OK" and len(res.get("data", [])) > 1:
                items = res["data"][1]
                for it in items:
                    all_vars[f"{it['title']} (ID: {it['var_id']})"] = str(it["var_id"])
                
                total_pages = res["data"][0].get("pages", 1)
                if page >= total_pages or page >= 5:  # Batasi maks 5 halaman agar loading cepat
                    break
                page += 1
            else:
                break
        except Exception:
            break
    return all_vars

subjects = get_bps_subjects()

if not subjects:
    st.error("Gagal terhubung ke katalog subjek WebAPI BPS. Periksa App ID atau koneksi server BPS.")
    st.stop()

# ==========================================
# 3. Kontrol Navigasi Katalog
# ==========================================
col_sub, col_var = st.columns([1, 2])

with col_sub:
    selected_sub_title = st.selectbox(
        "1. Pilih Subjek / Bidang Statistik Resmi BPS:",
        list(subjects.keys())
    )
    selected_sub_id = subjects[selected_sub_title]

variables = get_variables_by_subject(selected_sub_id)

with col_var:
    if variables:
        selected_var_title = st.selectbox(
            f"2. Pilih Indikator BPS ({len(variables)} Variabel Ditemukan di Subjek Ini):",
            list(variables.keys())
        )
        selected_var_id = variables[selected_var_title]
    else:
        st.warning("Belum ada tabel variabel dinamis aktif di bawah subjek ini.")
        st.stop()

# ==========================================
# 4. Filter Waktu (1945–2025)
# ==========================================
YEARS = [str(y) for y in range(1945, 2026)]

col_t1, col_t2 = st.columns(2)
with col_t1:
    th_start = st.selectbox("3. Tahun Mulai:", YEARS, index=YEARS.index("2010"))
with col_t2:
    th_end = st.selectbox("4. Tahun Selesai:", YEARS, index=YEARS.index("2024"))

if int(th_start) > int(th_end):
    st.error("Tahun mulai tidak boleh lebih besar dari tahun selesai.")
    st.stop()

# ==========================================
# 5. Penarikan Data Multi-Tahun (Batching)
# ==========================================
if st.button("📊 Ambil Data Resmi BPS", type="primary"):
    all_selected_years = [str(y) for y in range(int(th_start), int(th_end) + 1)]
    # BPS membatasi parameter 'th' maks 3 tahun per request
    batches = [all_selected_years[i:i + 3] for i in range(0, len(all_selected_years), 3)]

    records = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, b in enumerate(batches):
        th_param = ";".join(b) if len(b) > 1 else b[0]
        status_text.text(f"Mengunduh blok tahun {b[0]}–{b[-1]} dari server BPS...")
        
        url = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/{DOMAIN}/var/{selected_var_id}/th/{th_param}/key/{BPS_APP_ID}/"
        try:
            res = requests.get(url, headers=HEADERS, timeout=25).json()
            if res.get("status") == "OK" and res.get("data-availability") != "list-not-available":
                datacontent = res.get("datacontent", {})
                vervar = {str(item["val"]): item["label"] for item in res.get("vervar", [])}
                tahun_dict = {str(item["val"]): item["label"] for item in res.get("tahun", [])}

                for k, val in datacontent.items():
                    if val is not None:
                        k_str = str(k)
                        # Identifikasi rincian/kategori dan tahun
                        lbl_rincian = "Nasional"
                        for v_val, v_lbl in vervar.items():
                            if k_str.startswith(v_val):
                                lbl_rincian = v_lbl
                                break
                        
                        lbl_tahun = None
                        for t_val, t_lbl in tahun_dict.items():
                            if t_val in k_str:
                                lbl_tahun = t_lbl
                                break

                        if lbl_tahun and lbl_tahun in all_selected_years:
                            records.append({
                                "Tahun": str(lbl_tahun),
                                "Rincian": lbl_rincian,
                                "Nilai": val
                            })
            time.sleep(0.1)  # Mencegah throttling API
        except Exception:
            pass

        progress_bar.progress((idx + 1) / len(batches))

    status_text.empty()
    progress_bar.empty()

    # Bentuk deret waktu lengkap (termasuk tahun yang kosong)
    df_grid = pd.DataFrame({"Tahun": all_selected_years})

    if records:
        df_raw = pd.DataFrame(records).drop_duplicates()
        # Pivot agar kategori menjadi kolom tersendiri
        df_pivot = df_raw.pivot(index="Tahun", columns="Rincian", values="Nilai").reset_index()
        df_final = pd.merge(df_grid, df_pivot, on="Tahun", how="left").sort_values("Tahun")

        st.success(f"Berhasil menarik data resmi untuk variabel: **{selected_var_title}**!")

        st.divider()

        # Visualisasi Grafik
        st.subheader(f"📈 Visualisasi Deret Waktu: {selected_var_title}")
        fig = go.Figure()
        
        value_columns = [col for col in df_final.columns if col != "Tahun"]
        for col in value_columns:
            fig.add_trace(go.Scatter(
                x=df_final["Tahun"],
                y=df_final[col],
                mode="lines+markers",
                name=col,
                connectgaps=False,  # Memutus garis secara alami jika data kosong/None
                hovertemplate=f"Tahun %{{x}}<br>{col}: %{{y}}<extra></extra>"
            ))

        fig.update_layout(
            xaxis=dict(title="Tahun", tickmode="linear"),
            yaxis=dict(title="Nilai Observasi"),
            hovermode="x unified",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Tabel Data & Ekspor
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
        st.caption(
            "💡 Catatan: Tanda strip (-) atau titik grafik terputus menunjukkan bahwa pada tahun tersebut "
            "BPS belum melaksanakan survei atau datanya tidak dialokasikan di basis data tabel dinamis BPS."
        )

    else:
        st.warning(
            f"Tabel variabel *'{selected_var_title}'* terdaftar di katalog BPS, "
            f"tetapi server BPS tidak memiliki rekaman angka pada rentang {th_start}–{th_end}."
        )
        st.info(
            "Kemungkinan data ini hanya dirilis BPS dalam publikasi laporan cetak/PDF, "
            "atau surveinya baru dimulai pada tahun yang berbeda. Silakan pilih indikator lainnya."
        )
