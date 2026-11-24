import streamlit as st


def apply_custom_theme() -> None:
    """Menerapkan Space Grotesk, JetBrains Mono, dan tema dark ledger."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');

        /* Font utama Space Grotesk (tanpa menyentuh span global agar ikon aman) */
        html, body, .stApp, .stMarkdown, p, li, label, input, textarea, button {
            font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* Judul putih terang dan tegas */
        h1, h2, h3 {
            font-family: 'Space Grotesk', sans-serif !important;
            color: #F8FAFC !important;
            letter-spacing: -0.03em;
            font-weight: 700 !important;
        }

        /* Paragraf utama sedikit diredupkan agar hierarki judul menonjol */
        .stMarkdown p, .stMarkdown li {
            color: #CBD5E1;
        }

        /* Aksen monospace untuk angka metrik, caption, dan kode */
        code, pre, [data-testid="stMetricValue"], [data-testid="stCaptionContainer"] {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Sidebar dengan garis batas tegas */
        [data-testid="stSidebar"] {
            background-color: #0E1520 !important;
            border-right: 1px solid #1E293B;
        }

        /* Kotak input dan filter */
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div {
            background-color: #131B26 !important;
            border: 1px solid #1E293B !important;
            border-radius: 6px;
        }

        /* Paksa kotak st.info / st.warning menjadi gelap netral (hilangkan teks biru) */
        [data-testid="stAlert"] {
            background-color: #111827 !important;
            border: 1px solid #1E293B !important;
            border-radius: 8px !important;
        }

        [data-testid="stAlert"] p,
        [data-testid="stAlert"] li,
        [data-testid="stAlert"] strong {
            color: #CBD5E1 !important;
        }

        /* Label kecil uppercase monospace di atas judul */
        .atlas-eyebrow {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.78rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #94A3B8;
            margin-bottom: 0.25rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
