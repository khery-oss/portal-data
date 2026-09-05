import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(page_title="BPS Explorer - IndoEcon", layout="wide")

st.title("📊 BPS (Badan Pusat Statistik RI) - Indikator Strategis Nasional")
st.markdown(
    "Eksplorasi indikator sosial-ekonomi resmi Indonesia dari **WebAPI BPS RI** secara *real-time* (*100% Live API*)."
)

# =============================================================================
# MANAJEMEN API KEY (SESUAI POLA FRED)
# =============================================================================
bps_api_key = st.secrets.get("BPS_API_KEY", "")

if not bps_api_key:
    with st.sidebar:
        st.subheader("🔐 Autentikasi BPS WebAPI")
        bps_api_key = st.text_input(
            "Masukkan BPS API Key:",
            type="password",
            help="Masukkan API key resmi BPS Anda. Kunci tidak akan disimpan di kode."
        )

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# KATALOG RESMI INDIKATOR STRATEGIS NASIONAL (DOMAIN 0000)
# Disertai parameter wajib: var, turvar, dan rentang tahun (th)
BPS_CATALOG = {
    "Persentase Penduduk Miskin Nasional (P0, %)": {
        "var": "23",
        "turvar": "0",
        "unit": "%",
        "kategori": "Kemiskinan & Ketimpangan",
        "desc": "Persentase penduduk miskin Indonesia berdasarkan Survei Sosial Ekonomi Nasional (Susenas)."
    },
    "Gini Ratio / Rasio Gini Nasional": {
        "var": "149",
        "turvar": "0",
        "unit": "Koefisien Gini",
        "kategori": "Kemiskinan & Ketimpangan",
        "desc": "Tingkat ketimpangan pengeluaran penduduk agregat (0 = merata sempurna, 1 = timpang sempurna)."
    },
    "Garis Kemiskinan Nasional (Rp/Kapita/Bulan)": {
        "var": "25",
        "turvar": "0",
        "unit": "Rp/Kapita/Bulan",
        "kategori": "Kemiskinan & Ketimpangan",
        "desc": "Batas minimum rupiah pengeluaran makanan dan non-makanan per kapita sebulan."
    },
    "Tingkat Pengangguran Terbuka (TPT) Nasional (%)": {
        "var": "543",
        "turvar": "0",
        "unit": "%",
        "kategori": "Ketenagakerjaan",
        "desc": "Tingkat pengangguran terbuka nasional berdasarkan Survei Angkatan Kerja Nasional (Sakernas)."
    },
    "Tingkat Partisipasi Angkatan Kerja (TPAK) Nasional (%)": {
        "var": "542",
        "turvar": "0",
        "unit": "%",
        "kategori": "Ketenagakerjaan",
        "desc": "Persentase angkatan kerja terhadap total penduduk usia kerja (15 tahun ke atas)."
    },
    "Indeks Pembangunan Manusia (IPM) Nasional": {
        "var": "498",
        "turvar": "0",
        "unit": "Indeks",
        "kategori": "Pembangunan Manusia",
        "desc": "Capaian pembangunan manusia berbasis umur panjang, pengetahuan, dan standar hidup layak."
    },
    "Angka Harapan Hidup saat Lahir (AHH) Nasional": {
        "var": "500",
        "turvar": "0",
        "unit": "Tahun",
        "desc": "Perkiraan rata-rata tahun hidup yang dapat dicapai bayi baru lahir."
    },
    "Rata-rata Lama Sekolah (RLS) Nasional": {
        "var_id": "501",
        "var": "501",
        "turvar": "0",
        "unit": "Tahun",
        "kategori": "Pembangunan Manusia",
        "desc": "Rata-rata lama bersekolah penduduk usia 25 tahun ke atas."
    }
}

# =============================================================================
# 1. KONTROL PEMILIHAN INDIKATOR
# =============================================================================
st.subheader("1. Pemilihan Indikator Resmi BPS")
col_kat, col_ind = st.columns([1.2, 2])

kategori_list = sorted(list(set(v["kategori"] for v in BPS_CATALOG.values())))
with col_kat:
    pilihan_kategori = st.selectbox("Kategori Bidang:", ["Semua Kategori"] + kategori_list)

opsi = [
    k for k, v in BPS_CATALOG.items()
    if pilihan_kategori == "Semua Kategori" or v["kategori"] == pilihan_kategori
]

with col_ind:
    selected_name = st.selectbox(f"Nama Indikator ({len(opsi)} Tersedia):", opsi)

meta = BPS_CATALOG[selected_name]

with st.expander("ℹ️ Definisi & Metadata Resmi BPS", expanded=False):
    st.markdown(f"**Indikator:** {selected_name}")
    st.markdown(f"**Kategori:** `{meta['kategori']}`")
    st.markdown(f"**Satuan:** `{meta['unit']}`")
    st.markdown(f"**Metodologi / Deskripsi:**\n{meta['desc']}")
    st.markdown("🔗 **Portal Sumber Resmi:** [WebAPI BPS RI](https://webapi.bps.go.id/)")

# =============================================================================
# 2. PENARIKAN DATA LIVE VIA WEBAPI BPS
# =============================================================================
st.subheader("2. Penarikan Data Runtun Waktu Nasional")

if not bps_api_key:
    st.warning("⚠️ BPS API Key belum ditemukan. Daftarkan di Streamlit Secrets (`BPS_API_KEY`) atau masukkan lewat sidebar.")
else:
    if st.button("📊 Ambil Data BPS Langsung", type="primary"):
        with st.spinner(f"Menghubungi server WebAPI BPS untuk indikator {selected_name}..."):
            # Format pemanggilan lengkap dengan domain 0000 (Pusat)
            api_url = (
                f"https://webapi.bps.go.id/v1/api/list/model/data/lang/ind/"
                f"domain/0000/var/{meta['var']}/key/{bps_api_key}/"
            )

            try:
                res = requests.get(api_url, headers=HEADERS, timeout=25)
                
                if res.status_code == 200:
                    payload = res.json()
                    
                    if payload.get("data-availability") == "available":
                        vervar_list = payload.get("vervar", [])
                        tahun_list = payload.get("tahun", [])
                        datacontent = payload.get("datacontent", {})

                        # Cari kode entitas wilayah INDONESIA
                        id_indonesia = None
                        for v in vervar_list:
                            if "INDONESIA" in str(v.get("label", "")).upper():
                                id_indonesia = str(v.get("val"))
                                break

                        map_tahun = {str(t["val"]): str(t["label"]).strip() for t in tahun_list}

                        records = []
                        for key_code, raw_val in datacontent.items():
                            if raw_val is None:
                                continue
                            try:
                                num_val = float(raw_val)
                            except (ValueError, TypeError):
                                continue

                            # Filter jika kunci diawali kode wilayah nasional
                            if id_indonesia and not key_code.startswith(id_indonesia):
                                continue

                            for th_id, th_label in map_tahun.items():
                                if th_id in key_code:
                                    try:
                                        th_int = int(th_label[:4])
                                        records.append({"Tahun": th_int, "Nilai": num_val})
                                    except ValueError:
                                        pass
                                    break

                        if records:
                            val_col = f"Nilai ({meta['unit']})"
                            df_raw = pd.DataFrame(records)
                            df_bps = df_raw.groupby("Tahun", as_index=False)["Nilai"].mean().round(2)
                            df_bps = df_bps.rename(columns={"Nilai": val_col}).sort_values(by="Tahun", ascending=True)

                            st.success(f"Berhasil menarik {len(df_bps)} observasi resmi dari server BPS!")
                            st.divider()

                            # Tombol Unduh
                            c1, c2 = st.columns(2)
                            c1.download_button(
                                "📥 Unduh CSV",
                                df_bps.to_csv(index=False).encode("utf-8"),
                                f"BPS_{meta['var']}_Data.csv",
                                "text/csv"
                            )
                            buf = io.BytesIO()
                            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                                df_bps.to_excel(writer, index=False, sheet_name="BPS Data")
                            c2.download_button(
                                "📊 Unduh Excel (.xlsx)",
                                buf.getvalue(),
                                f"BPS_{meta['var']}_Data.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                            # Visualisasi Plotly
                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=df_bps["Tahun"],
                                y=df_bps[val_col],
                                mode="lines+markers",
                                name="Indonesia",
                                line=dict(width=2.8, color="#00529B"),
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

                            with st.expander("📋 Tabel Data Runtun Waktu Lengkap"):
                                st.dataframe(df_bps.sort_values(by="Tahun", ascending=False), use_container_width=True)
                        else:
                            st.warning("Observasi runtun waktu nasional untuk indikator ini sedang disinkronisasi di server BPS.")
                    else:
                        st.warning("Server BPS merespons: data belum tersedia untuk parameter ini.")
                else:
                    st.error(f"Gagal menghubungi server BPS (Kode Status HTTP: {res.status_code}).")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat memproses data BPS: {e}")
