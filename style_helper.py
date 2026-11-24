import streamlit as st


def apply_custom_theme() -> None:
    """Menerapkan tipografi dan gaya visual dark ledger ke halaman Streamlit."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

        /* Font utama (hindari selektor * atau span agar ikon Material Streamlit tidak rusak) */
        html, body, .stApp, .stMarkdown, p, li, label, input, textarea, button {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Judul tegas dengan jarak huruf rapat */
        h1, h2, h3 {
            font-family: 'Inter', sans-serif;
            color: #F8FAFC;
            letter-spacing: -0.025em;
            font-weight: 700;
        }

        /* Aksen monospace untuk angka metrik, caption, dan kode */
        code, pre, [data-testid="stMetricValue"], [data-testid="stCaptionContainer"] {
            font-family: 'JetBrains Mono', monospace;
        }

        /* Sidebar dengan garis batas tegas */
        [data-testid="stSidebar"] {
            background-color: #0E1520;
            border-right: 1px solid #1E293B;
        }

        /* Kotak filter/input (TextInput, Selectbox, Multiselect) */
        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div {
            background-color: #131B26;
            border: 1px solid #1E293B;
            border-radius: 6px;
        }

        /* Kotak alert/catatan (st.info, st.warning, dll.) bergaya banner gelap */
        [data-testid="stAlert"] {
            background-color: #111827;
            border: 1px solid #1E293B;
            border-radius: 8px;
            color: #CBD5E1;
        }

        /* Kelas opsional untuk label kecil uppercase monospace di atas judul */
        .atlas-eyebrow {
            font-family: 'JetBrains Mono', monospace;
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
