import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="BPS Data Explorer - Nasional", layout="wide")

st.title("📊 BPS (Badan Pusat Statistik RI) - Indikator Strategis Nasional")
st.markdown(
    "Eksplorasi indikator sosial-ekonomi resmi tingkat **Nasional (Indonesia)** langsung dari "
    "**WebAPI BPS RI** secara *real-time* (*100% live API*)."
)

BPS_APP_ID = "a94870b1e82c1b3dfdb6d2935df375bc"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# KATALOG INDIKATOR STRATEGIS RESMI BPS PUSAT (DOMAIN 0000)
# Menggunakan endpoint /model/data/ dengan variabel nasional terdaftar
BPS_CATALOG = {
    # --- Kemiskinan & Ketimpangan ---
    "Persentase Penduduk Miskin Nasional (P0, %)": {
        "var_id": "23",
        "kategori": "Kemiskinan & Ketimpangan",
        "unit": "%",
        "desc": "Persentase penduduk miskin agregat nasional berdasarkan Survei Sosial Ekonomi Nasional (Susenas)."
    },
    "Gini Ratio / Rasio Gini Nasional": {
        "var_id": "149",
        "kategori": "Kemiskinan & Ketimpangan",
        "unit": "Koefisien Gini",
        "desc": "Tingkat ketimpangan pengeluaran penduduk Indonesia (0 = merata sempurna, 1 = timpang sempurna)."
    },
    "Garis Kemiskinan Nasional (Rp/Kapita/Bulan)": {
        "var_id": "25",
        "kategori": "Kemiskinan & Ketimpangan",
        "unit": "Rupiah",
        "desc": "Batas minimum rupiah untuk memenuhi kebutuhan pangan dan non-pangan per orang per bulan."
    },
    # --- Ketenagakerjaan ---
    "Tingkat Pengangguran Terbuka (TPT) Nasional (%)": {
        "var_id": "543",
        "kategori": "Ketenagakerjaan",
        "unit": "%",
        "desc": "Tingkat pengangguran terbuka nasional berdasarkan Survei Angkatan Kerja Nasional (Sakernas)."
    },
    "Tingkat Partisipasi Angkatan Kerja (TPAK) Nasional (%)": {
        "var_id": "542",
        "kategori": "Ketenagakerjaan",
        "unit": "%",
        "desc": "Proporsi penduduk usia 15 tahun ke atas yang aktif bekerja atau mencari pekerjaan."
    },
    # --- Pembangunan Manusia ---
    "Indeks Pembangunan Manusia (IPM) Nasional": {
        "var_id": "498",
        "kategori": "Pembangunan Manusia",
        "unit": "Indeks",
        "desc": "Indeks komposit kesehatan, pendidikan, dan standar hidup layak nasional."
    },
    "Angka Harapan Hidup saat Lahir (AHH) Nasional": {
        "var_id": "500",
        "kategori": "Pembangunan Manusia",
        "unit": "Tahun",
        "desc": "Rata-rata perkiraan usia yang dapat dicapai penduduk sejak lahir."
    },
    "Rata-rata Lama Sekolah (RLS) Nasional": {
        "var_id": "501",
        "kategori": "Pembangunan Manusia",
        "unit": "Tahun",
        "desc": "Rata-rata jumlah tahun pendidikan formal yang ditempuh penduduk usia 25 tahun ke atas."
    }
}

st.subheader("1. Pemilihan Indikator Nasional")
col_kat, col_ind = st.columns([1.2, 2])

kategori_list = sorted(list(set(v["kategori"] for v in BPS_CATALOG.values())))
with col_kat:
    pilihan_kategori = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + kategori_list)

opsi = [
    k for k, v in BPS_CATALOG.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    nama_indikator = st.selectbox(f"Nama Indikator ({len(opsi)} Tersedia):", opsi)

meta = BPS_CATALOG[nama_indikator]
var_id = meta["var_id"]

with st.expander("ℹ️ Definisi & Metadata Resmi BPS", expanded=False):
    st.markdown(f"**Indikator:** {nama_indikator}")
    st.markdown(f"**Variable ID:** `{var_id}`")
    st.markdown(f"**Kategori:** `{meta['kategori']}`")
    st.markdown(f"**Satuan:** `{meta['unit']}`")
    st.markdown(f"**Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Basis Data:** [WebAPI BPS RI](https://webapi.bps.go.id/)")

st.subheader("2. Penarikan Data Runtun Waktu Nasional")

if st.button("📊 Ambil Data BPS Langsung", type="primary"):
    with st.spinner(f"Menghubungi server WebAPI BPS untuk seri {nama_indikator}..."):
        # Endpoint data BPS Pusat (domain: 0000)
        api_url = f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/domain/0000/var/{var_id}/key/{BPS_APP_ID}/"

        try:
            res = requests.get(api_url, headers=HEADERS, timeout=25)
            if res.status_code == 200:
                payload = res.json()

                if payload.get("data-availability") == "available":
                    vervar_list = payload.get("vervar", [])
                    tahun_list = payload.get("tahun", [])
                    datacontent = payload.get("datacontent", {})

                    # Cari ID untuk agregat "INDONESIA" di vervar
                    id_indonesia = None
                    for item in vervar_list:
                        label = str(item.get("label", "")).strip().upper()
                        if label == "INDONESIA":
                            id_indonesia = str(item.get("val"))
                            break

                    # Mapping label tahun
                    map_tahun = {str(item["val"]): str(item["label"]).strip() for item in tahun_list}

                    records = []
                    for key_code, raw_val in datacontent.items():
                        if raw_val is None:
                            continue
                        try:
                            val_num = float(raw_val)
                        except (ValueError, TypeError):
                            continue

                        # Filter hanya observasi nasional (INDONESIA)
                        if id_indonesia and not key_code.startswith(id_indonesia):
                            continue

                        # Cari tahun yang cocok di kunci
                        matched_tahun = None
                        for th_id, th_label in map_tahun.items():
                            if th_id in key_code:
                                matched_tahun = th_label
                                break

                        if matched_tahun:
                            try:
                                thn_int = int(matched_tahun[:4])
                                records.append({"Tahun": thn_int, "Nilai": val_num})
                            except ValueError:
                                continue

                    if records:
                        val_col = f"Nilai ({meta['unit']})"
                        df_raw = pd.DataFrame(records)
                        # Agregasi rata-rata per tahun jika ada data semesteran
                        df_bps = df_raw.groupby("Tahun", as_index=False)["Nilai"].mean().round(2)
                        df_bps = df_bps.rename(columns={"Nilai": val_col}).sort_values(by="Tahun", ascending=True)

                        st.success(f"Berhasil menarik {len(df_bps)} observasi tahunan nasional langsung dari server WebAPI BPS!")
                        st.divider()

                        # Tombol Unduh Data
                        c1, c2 = st.columns(2)
                        c1.download_button(
                            "📥 Unduh CSV",
                            df_bps.to_csv(index=False).encode("utf-8"),
                            f"BPS_Nasional_{var_id}.csv",
                            "text/csv"
                        )
                        buf = io.BytesIO()
                        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                            df_bps.to_excel(writer, index=False, sheet_name="BPS Nasional")
                        c2.download_button(
                            "📊 Unduh Excel (.xlsx)",
                            buf.getvalue(),
                            f"BPS_Nasional_{var_id}.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

                        # Visualisasi Plotly
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df_bps["Tahun"],
                            y=df_bps[val_col],
                            mode="lines+markers",
                            name="Nasional (Indonesia)",
                            line=dict(width=3, color="#1F77B4"),
                            marker=dict(size=7),
                            hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y:,.2f}} {meta['unit']}<extra></extra>"
                        ))
                        fig.update_layout(
                            xaxis=dict(title="Tahun", tickmode="linear"),
                            yaxis=dict(title=meta["unit"]),
                            hovermode="x unified",
                            margin=dict(l=20, r=20, t=30, b=20)
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        with st.expander("📋 Tabel Data Runtun Waktu Nasional"):
                            st.dataframe(df_bps.sort_values(by="Tahun", ascending=False), use_container_width=True)
                    else:
                        st.warning("Data observasi nasional untuk indikator ini sedang diperbarui di server BPS.")
                else:
                    st.warning("Respon server BPS menyatakan data belum tersedia untuk parameter ini.")
            else:
                st.error(f"Gagal menghubungi server BPS (Kode Status HTTP: {res.status_code}).")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses data BPS: {e}")
