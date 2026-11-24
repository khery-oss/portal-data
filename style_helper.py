import streamlit as st


def apply_custom_theme() -> None:
    """Menerapkan JetBrains Mono, aksen tombol neon, dan warna adaptif Light/Dark."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;500;600;700&display=swap');

        /* Font utama */
        html, body, .stApp, .stMarkdown, p, li, label, input, textarea, button {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Judul mengikuti warna tema aktif (putih di Dark, gelap di Light) */
        h1, h2, h3 {
            font-family: 'JetBrains Mono', monospace !important;
            color: var(--text-color) !important;
            letter-spacing: -0.03em;
            font-weight: 700 !important;
        }

        /* Paragraf sedikit lebih lembut, tetap adaptif di Light & Dark */
        .stMarkdown p, .stMarkdown li {
            color: color-mix(in srgb, var(--text-color) 82%, transparent);
        }

        /* Aksen monospace untuk angka metrik, caption, dan kode */
        code, pre, [data-testid="stMetricValue"], [data-testid="stCaptionContainer"] {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Sidebar adaptif dengan garis batas halus */
        [data-testid="stSidebar"] {
            background-color: var(--secondary-background-color) !important;
            border-right: 1px solid color-mix(in srgb, var(--text-color) 14%, transparent);
        }

        /* Kotak input dan filter adaptif */
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div {
            background-color: var(--secondary-background-color) !important;
            border: 1px solid color-mix(in srgb, var(--text-color) 18%, transparent) !important;
            border-radius: 6px;
        }

        /* Kotak st.info / st.warning adaptif (netral di Dark maupun Light) */
        [data-testid="stAlert"] {
            background-color: var(--secondary-background-color) !important;
            border: 1px solid color-mix(in srgb, var(--text-color) 16%, transparent) !important;
            border-radius: 8px !important;
        }

        [data-testid="stAlert"] p,
        [data-testid="stAlert"] li,
        [data-testid="stAlert"] strong {
            color: var(--text-color) !important;
        }

        /* Tombol Primary Biru Neon (Kontras tinggi di Light & Dark) */
        button[kind="primary"],
        [data-testid="stBaseButton-primary"] {
            background-color: var(--primary-color) !important;
            color: #FFFFFF !important;
            border: 1px solid #38BDF8 !important;
            font-weight: 600 !important;
            box-shadow: 0 0 14px rgba(0, 140, 255, 0.55) !important;
            transition: transform 0.15s ease, box-shadow 0.15s ease !important;
        }

        button[kind="primary"]:hover,
        [data-testid="stBaseButton-primary"]:hover {
            background-color: #0047D1 !important;
            transform: translateY(-1px);
            box-shadow: 0 0 22px rgba(0, 212, 255, 0.75) !important;
        }

        /* Label kecil uppercase monospace di atas judul */
        .atlas-eyebrow {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.78rem;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            color: color-mix(in srgb, var(--text-color) 62%, transparent);
            margin-bottom: 0.25rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
