import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="BPS Data Explorer - Live Catalog", layout="wide")

st.title("📊 Portal Data BPS Nasional (Live WebAPI)")
st.write(
    "Eksplorasi seluruh indikator resmi **Badan Pusat Statistik (BPS)** tingkat Nasional "
    "secara *real-time* langsung dari server WebAPI BPS."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

api_key = st.secrets.get("BPS_APP_ID") or st.secrets.get("BPS_API_KEY")
if not api_key:
    st.error("⚠️ Key BPS belum ditemukan di Streamlit Secrets (`BPS_APP_ID`).")
    st.stop()

DOMAIN = "0000"  # Agregat Nasional

# ==============================================================================
# 1. Mengambil Seluruh Subjek Resmi BPS (52 Subjek Dinamis)
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
                    subjects[f"[{cat_name}] {sub_title}"] = sub_id
                
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
# 2. Mengambil Variabel Indikator Resmi di Bawah Subjek Terpilih
# ==============================================================================
@st.cache_data(ttl=43200)
def fetch_variables_by_subject(sub_id):
    variables = {}
    page = 1
    max_pages = 5
    while page <= max_pages:
        url = f"https://webapi.bps.go.id/v1/api/list/model/var/domain/{DOMAIN}/subject/{sub_id}/page/{page}/key/{api_key}/"
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            res = r.json()
            if res.get("status") == "OK" and len(res.get("data", [])) > 1:
                items = res["data"][1]
                if not items:
                    break
                for it in items:
                    v_title = it.get("title", "").strip()
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

with st.spinner("Menghubungkan ke katalog WebAPI BPS..."):
    all_subjects = fetch_all_bps_subjects()

if not all_subjects:
    st.error("Gagal terhubung ke katalog BPS. Pastikan koneksi atau kuota API tersedia.")
    st.stop()

# ==============================================================================
# 3. Kontrol Pemilihan Taksonomi Resmi BPS
# ==============================================================================
st.subheader("1. Pilih Subjek & Indikator Resmi BPS")
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
# 4. Rentang Waktu Observasi
# ==============================================================================
st.subheader("2. Rentang Waktu Observasi")
YEARS = [str(y) for y in range(1970, 2026)]

col_t1, col_t2 = st.columns(2)
with col_t1:
    th_start = st.selectbox("Tahun Mulai:", YEARS, index=YEARS.index("2015"))
with col_t2:
    th_end = st.selectbox("Tahun Selesai:", YEARS, index=YEARS.index("2024"))

if int(th_start) > int(th_end):
    st.error("Tahun mulai tidak boleh lebih besar dari tahun selesai.")
    st.stop()

# ==============================================================================
# 5. Penarikan Data (Menggunakan Translasi th_id Resmi BPS)
# ==============================================================================
if st.button("📊 Muat Data Resmi BPS", type="primary"):
    # Rumus resmi ID tahun WebAPI BPS: th_id = tahun - 1900
    th_id_start = str(int(th_start) - 1900)
    th_id_end = str(int(th_end) - 1900)
    th_param = f"{th_id_start}:{th_id_end}"

    with st.spinner(f"Mengambil data resmi untuk {selected_var_label}..."):
        data_url = f"https://webapi.bps.go.id/v1/api/list/model/data/domain/{DOMAIN}/var/{selected_var_id}/th/{th_param}/key/{api_key}/"
        
        try:
            r = requests.get(data_url, headers=HEADERS, timeout=25)
            res = r.json()
        except Exception as e:
            st.error(f"Koneksi HTTP Error: {e}")
            st.stop()

    if res.get("status") == "OK" and res.get("data-availability") != "list-not-available":
        datacontent = res.get("datacontent", {})
        vervar = {str(item["val"]): str(item["label"]) for item in res.get("vervar", [])}
        tahun_dict = {str(item["val"]): str(item["label"]) for item in res.get("tahun", [])}

        records = []
        for cell_key, val in datacontent.items():
            if val is not None:
                k_str = str(cell_key)

                # Ekstraksi label kategori rincian
                rincian_lbl = "Nasional"
                for v_val, v_lbl in vervar.items():
                    if k_str.startswith(v_val):
                        rincian_lbl = v_lbl
                        break

                # Ekstraksi label tahun
                tahun_lbl = None
                for t_val, t_lbl in tahun_dict.items():
                    if t_val in k_str:
                        tahun_lbl = t_lbl
                        break

                # Bersihkan label tahun ke 4 digit
                th_clean = "".join(filter(str.isdigit, str(tahun_lbl)))[:4] if tahun_lbl else None

                if th_clean and int(th_start) <= int(th_clean) <= int(th_end):
                    try:
                        num_val = float(str(val).replace(",", ".").strip())
                    except ValueError:
                        num_val = val

                    records.append({
                        "Tahun": th_clean,
                        "Kategori / Rincian": rincian_lbl,
                        "Nilai": num_val
                    })

        if records:
            df_raw = pd.DataFrame(records).drop_duplicates()
            df_pivot = df_raw.pivot_table(index="Tahun", columns="Kategori / Rincian", values="Nilai", aggfunc="first").reset_index()

            # Susun grid tahun lengkap
            selected_years_grid = [str(y) for y in range(int(th_start), int(th_end) + 1)]
            df_grid = pd.DataFrame({"Tahun": selected_years_grid})
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
                    connectgaps=False,
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
            st.caption("💡 Tanda strip (-) menandakan bahwa data pada tahun tersebut tidak dialokasikan di basis data rilis BPS.")

        else:
            st.warning(f"Tidak ada catatan angka untuk rentang {th_start}–{th_end} pada variabel ini.")
    else:
        st.warning(
            f"Tabel indikator *'{selected_var_label}'* terdaftar di katalog BPS, "
            f"tetapi server BPS tidak memiliki catatan angka untuk rentang tahun {th_start}–{th_end}."
        )
