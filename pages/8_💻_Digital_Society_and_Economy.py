import io
import os
import re
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(
    page_title="Digital Society & Economy - IE IndoEcon Explorer",
    page_icon="💻",
    layout="wide"
)

st.title("💻 Digital Society & Economy - Indonesia")
st.markdown(
    "Eksplorasi komprehensif **inklusi keuangan & pembayaran digital, infrastruktur & akses digital, "
    "dan tata kelola digital Indonesia** dari sumber resmi internasional."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

tab_findex, tab_ict, tab_dsp = st.tabs([
    "💳 Inklusi Keuangan & Pembayaran Digital",
    "💻 Infrastruktur & Akses Digital",
    "🛡️ Tata Kelola Digital (DSP)"
])

# =============================================================================
# TAB 1: WORLD BANK GLOBAL FINDEX — LIVE API
# =============================================================================
with tab_findex:
    st.subheader("💳 World Bank Global Findex Database (Indonesia)")
    st.markdown(
        "Indikator inklusi keuangan, kepemilikan akun, pembayaran digital, dan mobile money "
        "dari **World Bank Global Findex** via World Bank Data API — *100% Live API*."
    )

    @st.cache_data(ttl=86400, show_spinner=False)
    def load_findex_indicators():
        indicators = []
        # Source 33 = Global Financial Inclusion (Findex)
        url = "https://api.worldbank.org/v2/indicator?source=33&format=json&per_page=3000"
        try:
            res = requests.get(url, headers=HEADERS, timeout=25)
            if res.status_code != 200:
                return []
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
                        })
        except Exception:
            pass
        return indicators

    with st.spinner("Menghubungkan ke katalog World Bank Findex..."):
        findex_indicators = load_findex_indicators()

    if not findex_indicators:
        st.error("Gagal memuat katalog Findex. Periksa koneksi internet.")
    else:
        query_fin = st.text_input(
            "🔍 Cari indikator Findex:",
            placeholder="Contoh: account, mobile, payment, credit, digital, saved, borrowed",
            value="account",
            key="q_fin"
        ).strip()

        if query_fin:
            tokens_fin = query_fin.lower().split()
            results_fin = [
                ind for ind in findex_indicators
                if any(t in ind["name"].lower() or t in ind["id"].lower() for t in tokens_fin)
            ]
            results_fin = sorted(results_fin, key=lambda x: len(x["name"]))
        else:
            results_fin = sorted(findex_indicators, key=lambda x: len(x["name"]))

        if not results_fin:
            st.warning("Tidak ditemukan indikator Findex untuk kata kunci tersebut.")
        else:
            st.success(f"Ditemukan **{len(results_fin)}** indikator Findex.")

            sel_fin = st.selectbox(
                "Pilih Indikator Findex:",
                options=results_fin,
                format_func=lambda x: x["name"],
                key="sel_fin"
            )

            with st.expander("ℹ️ Metadata & Definisi", expanded=False):
                st.markdown(f"**Kode Indikator:** `{sel_fin['id']}`")
                st.markdown(f"**Sumber:** World Bank Global Findex Database")
                if sel_fin.get("sourceNote"):
                    st.markdown(f"**Definisi:** {sel_fin['sourceNote']}")
                st.markdown("🔗 [World Bank Global Findex](https://www.worldbank.org/en/publication/globalfindex)")

            if st.button("📊 Ambil Data Findex Indonesia", type="primary", key="btn_fin"):
                with st.spinner(f"Menarik data untuk '{sel_fin['name']}'..."):
                    try:
                        url_data = (
                            f"https://api.worldbank.org/v2/country/IDN/indicator/{sel_fin['id']}"
                            f"?format=json&per_page=1000"
                        )
                        res = requests.get(url_data, headers=HEADERS, timeout=20)
                        records = []
                        if res.status_code == 200:
                            payload = res.json()
                            if len(payload) > 1 and isinstance(payload[1], list):
                                for item in payload[1]:
                                    thn = item.get("date")
                                    val = item.get("value")
                                    if thn is not None and val is not None:
                                        try:
                                            records.append({"Tahun": int(thn), "nilai_raw": round(float(val), 4)})
                                        except (ValueError, TypeError):
                                            continue

                        if not records:
                            st.warning("Data untuk Indonesia belum tersedia pada indikator ini.")
                        else:
                            val_col = "Nilai (%)"
                            df_fin = (
                                pd.DataFrame(records)
                                .groupby("Tahun", as_index=False)["nilai_raw"]
                                .mean().round(2)
                                .rename(columns={"nilai_raw": val_col})
                                .sort_values("Tahun")
                            )
                            st.success(f"Berhasil menarik **{len(df_fin)}** observasi dari World Bank Findex!")
                            st.divider()

                            c1, c2 = st.columns(2)
                            c1.download_button("📥 Unduh CSV", df_fin.to_csv(index=False).encode("utf-8"),
                                f"Findex_IDN_{sel_fin['id']}.csv", "text/csv", key="dl_fin_csv")
                            buf = io.BytesIO()
                            with pd.ExcelWriter(buf, engine="openpyxl") as w:
                                df_fin.to_excel(w, index=False, sheet_name="Findex")
                            c2.download_button("📊 Unduh Excel (.xlsx)", buf.getvalue(),
                                f"Findex_IDN_{sel_fin['id']}.xlsx",
                                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                key="dl_fin_xl")

                            fig = go.Figure()
                            fig.add_trace(go.Scatter(
                                x=df_fin["Tahun"], y=df_fin[val_col],
                                mode="lines+markers", name="Indonesia (Findex)",
                                line=dict(width=2.5, color="#2ca02c"), marker=dict(size=7),
                                hovertemplate="Tahun %{x}<br>Nilai: %{y:.2f}%<extra></extra>"
                            ))
                            fig.update_layout(
                                xaxis=dict(title="Tahun", tickmode="linear"),
                                yaxis=dict(title="Nilai (%)"),
                                hovermode="x unified", margin=dict(l=20, r=20, t=30, b=20)
                            )
                            st.plotly_chart(fig, use_container_width=True)

                            with st.expander("📋 Tabel Lengkap"):
                                st.dataframe(df_fin.sort_values("Tahun", ascending=False), use_container_width=True)
                    except Exception as e:
                        st.error(f"Gagal mengambil data: {e}")

# =============================================================================
# TAB 2: ICT & DIGITAL INFRASTRUCTURE — LIVE API (WB WDI)
# =============================================================================
with tab_ict:
    st.subheader("💻 Infrastruktur & Akses Digital Indonesia")
    st.markdown(
        "Indikator akses internet, mobile, broadband, ekspor TIK, dan teknologi tinggi "
        "dari **World Bank World Development Indicators** — *100% Live API*."
    )

    @st.cache_data(ttl=86400, show_spinner=False)
    def load_ict_indicators():
        indicators = []
        url = "https://api.worldbank.org/v2/indicator?source=2&format=json&per_page=3000"
        try:
            res = requests.get(url, headers=HEADERS, timeout=25)
            if res.status_code != 200:
                return []
            data = res.json()
            if len(data) > 1 and data[1]:
                for item in data[1]:
                    ind_id = item.get("id", "")
                    ind_name = item.get("name", "")
                    ict_keywords = ["internet", "mobile", "broadband", "telecom", "ict",
                                    "technology", "digital", "secure server",
                                    "information", "communication", "ecommerce", "e-commerce"]
                    if ind_id and ind_name and any(
                        kw in ind_name.lower() or kw in ind_id.lower()
                        for kw in ict_keywords
                    ):
                        indicators.append({
                            "id": ind_id,
                            "name": ind_name,
                            "sourceNote": item.get("sourceNote", ""),
                            "sourceOrg": item.get("sourceOrganization", "World Bank")
                        })
        except Exception:
            pass
        return indicators

    with st.spinner("Menghubungkan ke katalog ICT World Bank..."):
        ict_indicators = load_ict_indicators()

    if not ict_indicators:
        st.error("Gagal memuat katalog indikator ICT.")
    else:
        query_ict = st.text_input(
            "🔍 Cari indikator digital & ICT (Bahasa Inggris):",
            placeholder="Contoh: internet · mobile · broadband · telecom · ICT · technology · secure · ecommerce",
            value="",
            key="q_ict"
        ).strip()

        if not query_ict:
            st.info("Ketik kata kunci untuk mencari indikator. Contoh: **internet**, **mobile**, **broadband**, **telecom**, **ICT**.")
        else:
            tokens_ict = query_ict.lower().split()
            results_ict = [
                ind for ind in ict_indicators
                if any(t in ind["name"].lower() or t in ind["id"].lower() for t in tokens_ict)
            ]
            results_ict = sorted(results_ict, key=lambda x: len(x["name"]))

            if not results_ict:
                st.warning("Tidak ditemukan indikator ICT untuk kata kunci tersebut.")
            else:
                st.success(f"Ditemukan **{len(results_ict)}** indikator digital/ICT.")

                sel_ict = st.selectbox(
                    "Pilih Indikator:",
                    options=results_ict,
                    format_func=lambda x: x["name"],
                    key="sel_ict"
                )

                with st.expander("ℹ️ Metadata & Definisi", expanded=False):
                    st.markdown(f"**Kode Indikator:** `{sel_ict['id']}`")
                    st.markdown(f"**Sumber:** {sel_ict['sourceOrg']}")
                    if sel_ict.get("sourceNote"):
                        st.markdown(f"**Definisi:** {sel_ict['sourceNote']}")
                    st.markdown(f"🔗 [Lihat di World Bank](https://data.worldbank.org/indicator/{sel_ict['id']}?locations=ID)")

                if st.button("📊 Ambil Data ICT Indonesia", type="primary", key="btn_ict"):
                    with st.spinner(f"Menarik data untuk '{sel_ict['name']}'..."):
                        try:
                            url_ict = (
                                f"https://api.worldbank.org/v2/country/IDN/indicator/{sel_ict['id']}"
                                f"?format=json&per_page=1000"
                            )
                            res = requests.get(url_ict, headers=HEADERS, timeout=20)
                            records = []
                            if res.status_code == 200:
                                payload = res.json()
                                if len(payload) > 1 and isinstance(payload[1], list):
                                    for item in payload[1]:
                                        thn = item.get("date")
                                        val = item.get("value")
                                        if thn is not None and val is not None:
                                            try:
                                                records.append({"Tahun": int(thn), "nilai_raw": round(float(val), 4)})
                                            except (ValueError, TypeError):
                                                continue

                            if not records:
                                st.warning("Data untuk Indonesia belum tersedia pada indikator ini.")
                            else:
                                name_lower = sel_ict["name"].lower()
                                if "%" in sel_ict["name"]:
                                    unit = "%"
                                elif "per 100" in name_lower:
                                    unit = "Per 100 Orang"
                                elif "per 1 million" in name_lower or "per million" in name_lower:
                                    unit = "Per 1 Juta Orang"
                                elif "usd" in name_lower or "current us$" in name_lower or "(cd)" in name_lower:
                                    unit = "USD"
                                else:
                                    unit = "Nilai"

                                val_col = f"Nilai ({unit})"
                                df_ict = (
                                    pd.DataFrame(records)
                                    .groupby("Tahun", as_index=False)["nilai_raw"]
                                    .mean().round(2)
                                    .rename(columns={"nilai_raw": val_col})
                                    .sort_values("Tahun")
                                )
                                st.success(f"Berhasil menarik **{len(df_ict)}** observasi!")
                                st.divider()

                                c1, c2 = st.columns(2)
                                c1.download_button("📥 Unduh CSV", df_ict.to_csv(index=False).encode("utf-8"),
                                    f"ICT_IDN_{sel_ict['id']}.csv", "text/csv", key="dl_ict_csv")
                                buf = io.BytesIO()
                                with pd.ExcelWriter(buf, engine="openpyxl") as w:
                                    df_ict.to_excel(w, index=False, sheet_name="ICT Data")
                                c2.download_button("📊 Unduh Excel (.xlsx)", buf.getvalue(),
                                    f"ICT_IDN_{sel_ict['id']}.xlsx",
                                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    key="dl_ict_xl")

                                fig = go.Figure()
                                fig.add_trace(go.Scatter(
                                    x=df_ict["Tahun"], y=df_ict[val_col],
                                    mode="lines+markers", name="Indonesia (WB WDI)",
                                    line=dict(width=2.5, color="#1f77b4"), marker=dict(size=7),
                                    hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y:,.2f}} {unit}<extra></extra>"
                                ))
                                fig.update_layout(
                                    xaxis=dict(title="Tahun", tickmode="linear"),
                                    yaxis=dict(title=unit),
                                    hovermode="x unified", margin=dict(l=20, r=20, t=30, b=20)
                                )
                                st.plotly_chart(fig, use_container_width=True)

                                with st.expander("📋 Tabel Lengkap"):
                                    st.dataframe(df_ict.sort_values("Tahun", ascending=False), use_container_width=True)
                        except Exception as e:
                            st.error(f"Gagal mengambil data: {e}")

# =============================================================================
# TAB 3: DIGITAL SOCIETY PROJECT (DSP) — CSV LOKAL
# =============================================================================
with tab_dsp:
    st.subheader("🛡️ Digital Society Project (DSP) - Tata Kelola & Kebebasan Digital")
    st.markdown(
        "Analisis disinformasi, sensor internet, pembatasan jaringan, dan kebebasan digital "
        "dari **Digital Society Project (DSP)** — data berbasis file CSV resmi DSP."
    )

    @st.cache_data(show_spinner=False)
    def load_dsp():
        paths = ["DSP_CY_IDN.csv", "data/DSP_CY_IDN.csv"]
        for p in paths:
            if os.path.exists(p):
                try:
                    return pd.read_csv(p, low_memory=False)
                except Exception as e:
                    st.error(f"Gagal membaca file DSP: {e}")
                    return None
        return None

    df_dsp = load_dsp()

    if df_dsp is None:
        st.info(
            "File `DSP_CY_IDN.csv` belum ditemukan di root folder repository. "
            "Buka panduan setup di atas untuk instruksi unduh dan persiapan file."
        )
    elif df_dsp.empty:
        st.error("File DSP ditemukan namun tidak berisi data.")
    else:
        DSP_MASTER = {
            "Penyebaran Informasi Palsu oleh Pemerintah (v2smgovdom)": {
                "base": "v2smgovdom",
                "desc": "Seberapa sering agen pemerintah menyebarkan informasi palsu/menyesatkan di media sosial.",
                "deriv": ["v2smgovdom_codelow", "v2smgovdom_codehigh", "v2smgovdom_sd", "v2smgovdom_mean"]
            },
            "Penyebaran Informasi Palsu oleh Partai Politik (v2smpardom)": {
                "base": "v2smpardom",
                "desc": "Frekuensi partai politik menyebarkan informasi menyesatkan untuk memengaruhi populasi.",
                "deriv": ["v2smpardom_codelow", "v2smpardom_codehigh", "v2smpardom_sd", "v2smpardom_mean"]
            },
            "Kapasitas Filter / Sensor Internet Pemerintah (v2smgovfilcap)": {
                "base": "v2smgovfilcap",
                "desc": "Kapasitas teknis pemerintah dalam menyensor informasi internet melalui pemblokiran situs.",
                "deriv": ["v2smgovfilcap_codelow", "v2smgovfilcap_codehigh", "v2smgovfilcap_sd", "v2smgovfilcap_mean"]
            },
            "Pemadaman Akses Internet oleh Pemerintah (v2smgovshut)": {
                "base": "v2smgovshut",
                "desc": "Frekuensi pemerintah mematikan akses domestik ke internet dalam praktiknya.",
                "deriv": ["v2smgovshut_codelow", "v2smgovshut_codehigh", "v2smgovshut_sd", "v2smgovshut_mean"]
            },
            "Perlindungan Hukum Privasi Pengguna (v2smprivex)": {
                "base": "v2smprivex",
                "desc": "Keberadaan kerangka hukum formal untuk melindungi privasi pengguna internet dan data pribadi.",
                "deriv": ["v2smprivex_codelow", "v2smprivex_codehigh", "v2smprivex_sd", "v2smprivex_mean"]
            },
            "Perlindungan Hukum Defamation & Ujaran Kebencian (v2smlawpr)": {
                "base": "v2smlawpr",
                "desc": "Sejauh mana kerangka hukum melindungi konten pencemaran nama baik atau ujaran kebencian daring.",
                "deriv": ["v2smlawpr_codelow", "v2smlawpr_codehigh", "v2smlawpr_sd", "v2smlawpr_mean"]
            }
        }

        # Filter hanya indikator yang benar-benar ada di file
        valid_dsp = {k: v for k, v in DSP_MASTER.items() if v["base"] in df_dsp.columns}

        if not valid_dsp:
            st.warning(
                "Tidak ada variabel DSP yang dikenali di file CSV. "
                "Pastikan file menggunakan format standar DSP."
            )
        else:
            sel_dsp = st.selectbox(
                "Pilih Indikator DSP:",
                list(valid_dsp.keys()),
                key="sel_dsp"
            )
            meta_dsp = valid_dsp[sel_dsp]
            var_code = meta_dsp["base"]
            available_deriv = [c for c in meta_dsp["deriv"] if c in df_dsp.columns]

            with st.expander("📖 Definisi & Metadata DSP", expanded=False):
                st.markdown(f"**Kode Variabel:** `{var_code}`")
                st.markdown(f"**Definisi:** {meta_dsp['desc']}")
                if available_deriv:
                    st.markdown(f"**Variabel Turunan Tersedia:** `{', '.join(available_deriv)}`")
                st.markdown("🔗 [Digital Society Project](https://www.digitalsocietyproject.net/)")

            if "year" not in df_dsp.columns:
                st.error("Kolom `year` tidak ditemukan di file DSP.")
            else:
                cols_to_use = ["year", var_code] + available_deriv
                df_plot_dsp = (
                    df_dsp[cols_to_use]
                    .dropna(subset=["year", var_code])
                    .sort_values("year")
                )

                if df_plot_dsp.empty:
                    st.warning("Data untuk indikator ini tidak tersedia.")
                else:
                    tahun_min = int(df_plot_dsp["year"].min())
                    tahun_max = int(df_plot_dsp["year"].max())

                    col_f1, col_f2 = st.columns(2)
                    with col_f1:
                        thn_mulai = st.number_input("Dari Tahun:", min_value=tahun_min, max_value=tahun_max, value=tahun_min, step=1, key="dsp_y1")
                    with col_f2:
                        thn_akhir = st.number_input("Sampai Tahun:", min_value=tahun_min, max_value=tahun_max, value=tahun_max, step=1, key="dsp_y2")

                    df_plot_dsp = df_plot_dsp[
                        (df_plot_dsp["year"] >= thn_mulai) & (df_plot_dsp["year"] <= thn_akhir)
                    ]

                    st.success(f"Memuat **{len(df_plot_dsp)}** observasi dari file DSP.")
                    st.divider()

                    c1, c2 = st.columns(2)
                    c1.download_button(
                        "📥 Unduh CSV",
                        df_plot_dsp.to_csv(index=False).encode("utf-8"),
                        f"DSP_{var_code}_Indonesia.csv", "text/csv", key="dl_dsp_csv"
                    )
                    buf_dsp = io.BytesIO()
                    with pd.ExcelWriter(buf_dsp, engine="openpyxl") as w:
                        df_plot_dsp.to_excel(w, index=False, sheet_name="DSP Data")
                    c2.download_button(
                        "📊 Unduh Excel (.xlsx)", buf_dsp.getvalue(),
                        f"DSP_{var_code}_Indonesia.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="dl_dsp_xl"
                    )

                    # Chart utama
                    fig_dsp = go.Figure()
                    fig_dsp.add_trace(go.Scatter(
                        x=df_plot_dsp["year"], y=df_plot_dsp[var_code],
                        mode="lines+markers", name=var_code,
                        line=dict(width=2.5, color="#d62728"), marker=dict(size=7),
                        hovertemplate="Tahun %{x}<br>Skor: %{y:.4f}<extra></extra>"
                    ))
                    fig_dsp.update_layout(
                        xaxis=dict(title="Tahun", tickmode="linear"),
                        yaxis=dict(title="Skor Estimasi"),
                        hovermode="x unified", margin=dict(l=20, r=20, t=30, b=20)
                    )
                    st.plotly_chart(fig_dsp, use_container_width=True)

                    # Chart variabel turunan (interval kepercayaan)
                    if available_deriv:
                        with st.expander("📈 Analisis Interval Kepercayaan & Variabel Turunan"):
                            fig_deriv = go.Figure()
                            colors = ["#d62728", "#ff7f0e", "#2ca02c", "#9467bd"]
                            all_cols = [var_code] + available_deriv
                            for i, col in enumerate(all_cols):
                                if col in df_plot_dsp.columns:
                                    fig_deriv.add_trace(go.Scatter(
                                        x=df_plot_dsp["year"], y=df_plot_dsp[col],
                                        mode="lines+markers", name=col,
                                        line=dict(width=2 if i == 0 else 1.5,
                                                  color=colors[i % len(colors)],
                                                  dash="solid" if i == 0 else "dot"),
                                        marker=dict(size=5),
                                        hovertemplate=f"{col}: %{{y:.4f}}<extra></extra>"
                                    ))
                            fig_deriv.update_layout(
                                xaxis=dict(title="Tahun", tickmode="linear"),
                                yaxis=dict(title="Nilai"),
                                hovermode="x unified",
                                margin=dict(l=20, r=20, t=30, b=20)
                            )
                            st.plotly_chart(fig_deriv, use_container_width=True)

                    with st.expander("📋 Tabel Data Lengkap"):
                        st.dataframe(df_plot_dsp.sort_values("year", ascending=False), use_container_width=True)
