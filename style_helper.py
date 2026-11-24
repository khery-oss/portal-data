import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st


def _register_plotly_theme() -> None:
    """Mendaftarkan template Plotly global bergaya dark/light ledger."""
    pio.templates["atlas_ledger"] = go.layout.Template(
        layout=dict(
            font=dict(family="Geist, sans-serif", size=12, color="#64748B"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            colorway=["#2DD4BF", "#38BDF8", "#818CF8", "#F59E0B"],
            xaxis=dict(
                showgrid=True,
                gridcolor="rgba(148, 163, 184, 0.12)",
                zeroline=False,
                showline=False,
                tickfont=dict(family="Geist Mono, monospace", size=11, color="#64748B"),
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="rgba(148, 163, 184, 0.12)",
                zeroline=False,
                showline=False,
                tickfont=dict(family="Geist Mono, monospace", size=11, color="#64748B"),
            ),
            hoverlabel=dict(
                bgcolor="#0F172A",
                bordercolor="#334155",
                font=dict(family="Geist Mono, monospace", size=12, color="#F8FAFC"),
            ),
        )
    )
    pio.templates.default = "atlas_ledger"


def apply_custom_theme() -> None:
    """Menerapkan Geist/Geist Mono, tata letak compact global, template Plotly, dan warna adaptif Light/Dark."""
    _register_plotly_theme()
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600&family=Geist:wght@400;500;600;700&display=swap');

        /* 1. Ruang Kontainer Utama Rapat & Aman dari Header Atas Streamlit */
        .block-container {
            padding-top: 4rem !important;
            padding-bottom: 2rem !important;
            max-width: 1200px;
        }

        .stMainBlockContainer [data-testid="stVerticalBlock"] {
            gap: 0.85rem;
        }

        /* 2. Tipografi Global Ringkas (aman untuk ikon Material & grafik SVG) */
        html, body, .stApp, .stMarkdown, p, li, label, input, textarea, button {
            font-family: 'Geist', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        h1, h2, h3 {
            font-family: 'Geist', sans-serif !important;
            color: var(--text-color) !important;
            letter-spacing: -0.025em;
            font-weight: 700 !important;
        }

        h1 {
            font-size: 1.65rem !important;
            line-height: 1.2 !important;
            padding-top: 0.25rem !important;
            padding-bottom: 0.65rem !important;
        }

        h2 {
            font-size: 1.15rem !important;
            line-height: 1.3 !important;
            padding-top: 0.75rem !important;
            padding-bottom: 0.45rem !important;
        }

        h3 {
            font-size: 1.05rem !important;
            line-height: 1.35 !important;
            padding-top: 0.65rem !important;
            padding-bottom: 0.65rem !important;
        }

        .stMarkdown p, .stMarkdown li {
            font-size: 0.875rem !important;
            line-height: 1.5;
            color: color-mix(in srgb, var(--text-color) 82%, transparent);
        }

        [data-testid="stWidgetLabel"] p {
            font-size: 0.82rem !important;
            font-weight: 500;
            margin-bottom: 0.1rem !important;
        }

        code, pre, [data-testid="stMetricValue"], [data-testid="stCaptionContainer"] {
            font-family: 'Geist Mono', monospace !important;
            letter-spacing: -0.02em;
        }

        /* 3. Sidebar Compact & Adaptif */
        [data-testid="stSidebar"] {
            background-color: var(--secondary-background-color) !important;
            border-right: 1px solid color-mix(in srgb, var(--text-color) 14%, transparent);
        }

        [data-testid="stSidebarNavLink"] {
            padding-top: 0.3rem !important;
            padding-bottom: 0.3rem !important;
            font-size: 0.85rem !important;
        }

        /* 4. Kotak Input & Dropdown Lebih Ramping */
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div {
            background-color: var(--secondary-background-color) !important;
            border: 1px solid color-mix(in srgb, var(--text-color) 18%, transparent) !important;
            border-radius: 6px !important;
            min-height: 36px !important;
            font-size: 0.85rem !important;
        }

        /* 5. Kotak Alert (st.success / st.info / st.warning) Lebih Tipis */
        [data-testid="stAlert"],
        [data-testid="stAlertContainer"] {
            border-radius: 6px !important;
            padding-top: 0.45rem !important;
            padding-bottom: 0.45rem !important;
            border: 1px solid color-mix(in srgb, var(--text-color) 14%, transparent);
        }

        [data-testid="stAlert"] p,
        [data-testid="stAlert"] li {
            font-size: 0.85rem !important;
            line-height: 1.45;
        }

        /* 6. Expander Lebih Ramping */
        [data-testid="stExpander"] {
            background-color: var(--secondary-background-color) !important;
            border: 1px solid color-mix(in srgb, var(--text-color) 16%, transparent) !important;
            border-radius: 6px !important;
        }

        [data-testid="stExpander"] summary {
            padding: 0.45rem 0.75rem !important;
            font-size: 0.85rem !important;
        }

        /* 7. Garis Pemisah Lebih Tipis & Rapat */
        hr {
            margin-top: 0.05rem !important;
            margin-bottom: 0.85rem !important;
            border-color: color-mix(in srgb, var(--text-color) 12%, transparent) !important;
        }

/* 8. Tombol Primary & Tombol Unduh Biru Neon */
        button[kind="primary"],
        [data-testid="stBaseButton-primary"],
        [data-testid="stDownloadButton"] button {
            background-color: var(--primary-color) !important;
            color: #FFFFFF !important;
            border: 1px solid #38BDF8 !important;
            border-radius: 6px !important;
            min-height: 36px !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            box-shadow: 0 0 12px rgba(0, 140, 255, 0.45) !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease !important;
        }

        button[kind="primary"]:hover,
        [data-testid="stBaseButton-primary"]:hover,
        [data-testid="stDownloadButton"] button:hover {
            background-color: #0047D1 !important;
            transform: translateY(-1px);
            box-shadow: 0 0 18px rgba(0, 212, 255, 0.7) !important;
        }

        /* Label kecil uppercase Geist Mono di atas judul */
        .atlas-eyebrow {
            font-family: 'Geist Mono', monospace !important;
            font-size: 0.75rem;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            color: color-mix(in srgb, var(--text-color) 62%, transparent);
            margin-bottom: 0.2rem;
        }
        
        [data-testid="stDownloadButton"] button {
            width: 100% !important;
        }
        
        /* 9. Aksen Neon Khusus 3 Blok Beranda */
        /* A. Pedoman Penggunaan Akademis (Expander Neon Biru) */
        .st-key-pedoman_neon [data-testid="stExpander"] {
            border: 1px solid #38BDF8 !important;
            box-shadow: 0 0 14px rgba(0, 140, 255, 0.38) !important;
            transition: box-shadow 0.2s ease !important;
        }

        .st-key-pedoman_neon [data-testid="stExpander"]:hover {
            box-shadow: 0 0 22px rgba(0, 212, 255, 0.62) !important;
        }

        .st-key-pedoman_neon [data-testid="stExpander"] summary,
        .st-key-pedoman_neon [data-testid="stExpander"] summary p {
            color: #38BDF8 !important;
            font-weight: 600 !important;
            text-shadow: 0 0 10px rgba(56, 189, 248, 0.45);
        }

        /* B. Prinsip Integritas & Transparansi Data (Neon Hijau) */
        .st-key-integritas_neon {
            border: 1px solid #22C55E !important;
            border-radius: 8px !important;
            padding: 1.1rem 1.25rem !important;
            box-shadow: 0 0 14px rgba(34, 197, 94, 0.32) !important;
        }

        .st-key-integritas_neon h3 {
            color: #22C55E !important;
            text-shadow: 0 0 10px rgba(34, 197, 94, 0.45);
        }

        /* C. Kotak Saran (Neon Biru) */
        .st-key-saran_neon {
            border: 1px solid #38BDF8 !important;
            border-radius: 8px !important;
            padding: 1.1rem 1.25rem !important;
            box-shadow: 0 0 14px rgba(0, 140, 255, 0.35) !important;
        }

        .st-key-saran_neon h3 {
            color: #38BDF8 !important;
            text-shadow: 0 0 10px rgba(56, 189, 248, 0.45);
        }

        /* 10. Aksen Warna Beranda & 8 Kartu Modul */
        .st-key-beranda_hero h1,
        .st-key-beranda_hero h1 span {
            color: #6EE7B7 !important;
        }

        .st-key-beranda_arsitektur h3 {
            color: #FDBA74 !important;
        }

        /* Palet aksen per modul (1-4 mengikuti referensi, 5-8 pelengkap) */
        .st-key-card_wb       { --card-accent: #60A5FA; } /* Biru */
        .st-key-card_fred     { --card-accent: #6EE7B7; } /* Hijau Mint */
        .st-key-card_unsdg    { --card-accent: #C084FC; } /* Ungu */
        .st-key-card_bps      { --card-accent: #FCD34D; } /* Kuning Amber */
        .st-key-card_who      { --card-accent: #FB7185; } /* Merah Muda / Coral */
        .st-key-card_vdem     { --card-accent: #818CF8; } /* Indigo */
        .st-key-card_dse      { --card-accent: #22D3EE; } /* Cyan */
        .st-key-card_comtrade { --card-accent: #FB923C; } /* Oranye */

        /* Terapkan aksen ke judul kartu, ikon, dan tautan Buka Modul */
        [class*="st-key-card_"] h3,
        [class*="st-key-card_"] h3 span,
        [class*="st-key-card_"] [data-testid="stPageLink-NavLink"] p,
        [class*="st-key-card_"] [data-testid="stPageLink-NavLink"] span {
            color: var(--card-accent) !important;
        }

        /* Efek hover halus pada bingkai kartu mengikuti warna aksennya */
        [class*="st-key-card_"] {
            transition: border-color 0.2s ease !important;
        }

        [class*="st-key-card_"]:hover {
            border-color: color-mix(in srgb, var(--card-accent) 60%, transparent) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
