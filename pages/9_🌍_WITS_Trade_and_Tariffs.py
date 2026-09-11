import io
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

st.set_page_config(
    page_title="WITS Trade & Tariffs - IE IndoEcon Explorer",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 WITS (World Integrated Trade Solution) - Perdagangan & Tarif Indonesia")
st.markdown(
    "Eksplorasi indikator perdagangan internasional, ekspor-impor, keterbukaan ekonomi, "
    "dan struktur tarif bea masuk Indonesia dari **World Bank WITS & WDI Database** — *100% Live API*."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# =============================================================================
# LOAD KATALOG INDIKATOR PERDAGANGAN & TARIF DARI WORLD BANK / WITS
# =============================================================================
@st.cache_data(ttl=86400, show_spinner=False)
def load_trade_indicators():
    """Ambil indikator perdagangan (Topic 5: Trade) dari World Bank WDI/WITS mirror."""
    indicators = []
    # Topic 5 = Trade & International Integration
    url = "https://api.worldbank.org/v2/indicator?source=2&topic=5&format=json&per_page=3000"
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
                        "sourceOrg": item.get("sourceOrganization", "World Bank / WITS")
                    })
    except Exception:
        pass
    return indicators

with st.spinner("Menghubungkan ke katalog database perdagangan WITS..."):
    trade_indicators = load_trade_indicators()

if not trade_indicators:
    st.error("Gagal memuat katalog perdagangan. Periksa koneksi internet.")
    st.stop()

# =============================================================================
# PENCARIAN INDIKATOR
# =============================================================================
st.subheader("1. Pencarian Indikator Perdagangan & Tarif")

query_trade = st.text_input(
    "🔍 Cari topik perdagangan (Bahasa Inggris):",
    placeholder="Contoh: trade, export, import, tariff, customs, goods, services, merchandise",
    value="trade"
).strip()

if not query_trade:
    st.info("Ketik kata kunci untuk mencari indikator. Contoh: **trade**, **export**, **import**, **tariff**.")
    st.stop()

tokens_trade = query_trade.lower().split()
results_trade = [
    ind for ind in trade_indicators
    if any(t in ind["name"].lower() or t in ind["id"].lower() for t in tokens_trade)
]
results_trade = sorted(results_trade, key=lambda x: len(x["name"]))

if not results_trade:
    st.warning("Tidak ditemukan indikator perdagangan untuk kata kunci tersebut.")
else:
    st.success(f"Ditemukan **{len(results_trade)}** indikator perdagangan.")

    sel_trade = st.selectbox(
        "Pilih Indikator Perdagangan:",
        options=results_trade,
        format_func=lambda x: x["name"],
        key="sel_trade"
    )

    with st.expander("ℹ️ Metadata & Definisi WITS", expanded=False):
        st.markdown(f"**Kode Indikator:** `{sel_trade['id']}`")
        st.markdown(f"**Sumber:** {sel_trade['sourceOrg']}")
        if sel_trade.get("sourceNote"):
            st.markdown(f"**Definisi:** {sel_trade['sourceNote']}")
        st.markdown("🔗 [World Bank WITS Portal](https://wits.worldbank.org/)")

    if st.button("📊 Ambil Data Perdagangan Indonesia", type="primary", key="btn_trade"):
        with st.spinner(f"Menarik data untuk '{sel_trade['name']}'..."):
            try:
                url_data = (
                    f"https://api.worldbank.org/v2/country/IDN/indicator/{sel_trade['id']}"
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
                    st.warning("Data untuk Indonesia belum tersedia pada indikator perdagangan ini.")
                else:
                    name_lower = sel_trade["name"].lower()
                    if "%" in sel_trade["name"]:
                        unit = "%"
                    elif "usd" in name_lower or "current us$" in name_lower:
                        unit = "USD"
                    else:
                        unit = "Nilai"

                    val_col = f"Nilai ({unit})"
                    df_res = (
                        pd.DataFrame(records)
                        .groupby("Tahun", as_index=False)["nilai_raw"]
                        .mean().round(2)
                        .rename(columns={"nilai_raw": val_col})
                        .sort_values("Tahun")
                    )
                    st.success(f"Berhasil menarik **{len(df_res)}** observasi perdagangan Indonesia!")
                    st.divider()

                    c1, c2 = st.columns(2)
                    c1.download_button("📥 Unduh CSV", df_res.to_csv(index=False).encode("utf-8"),
                        f"WITS_Trade_IDN_{sel_trade['id']}.csv", "text/csv", key="dl_tr_csv")
                    buf = io.BytesIO()
                    with pd.ExcelWriter(buf, engine="openpyxl") as w:
                        df_res.to_excel(w, index=False, sheet_name="WITS Trade")
                    c2.download_button("📊 Unduh Excel (.xlsx)", buf.getvalue(),
                        f"WITS_Trade_IDN_{sel_trade['id']}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="dl_tr_xl")

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_res["Tahun"], y=df_res[val_col],
                        mode="lines+markers", name="Indonesia (WITS/Trade)",
                        line=dict(width=2.5, color="#17becf"), marker=dict(size=7),
                        hovertemplate=f"Tahun %{{x}}<br>Nilai: %{{y:,.2f}} {unit}<extra></extra>"
                    ))
                    fig.update_layout(
                        xaxis=dict(title="Tahun", tickmode="linear"),
                        yaxis=dict(title=unit),
                        hovermode="x unified", margin=dict(l=20, r=20, t=30, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    with st.expander("📋 Tabel Lengkap"):
                        st.dataframe(df_res.sort_values("Tahun", ascending=False), use_container_width=True)
            except Exception as e:
                st.error(f"Gagal mengambil data: {e}")
