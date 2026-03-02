import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="PPC Studio")

# --- STYLING + odstranění červeného focus borderu ---
st.markdown(
    """
    <style>
        /* 1) VZHLED POLÍ: výška, písmo */
        .stTextArea textarea {
            height: 120px !important;
            min-height: 120px !important;
            max-height: 120px !important;
            font-size: 16px !important;
        }
        .stTextInput input { font-size: 16px !important; }

        /* 2) Zarovnání labelů */
        div[data-testid="column"] label {
            height: 25px !important;
            display: flex !important;
            align-items: center !important;
            margin-bottom: 8px !important;
        }

        /* 3) Odstranění červeného focus borderu (robustní) */
        textarea:focus, textarea:focus-visible,
        input:focus, input:focus-visible {
            outline: none !important;
            box-shadow: none !important;
        }
        div[data-baseweb="base-input"]:focus-within,
        div[data-baseweb="textarea"]:focus-within,
        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="input-container"]:focus-within {
            outline: none !important;
            box-shadow: none !important;
            border-color: #ced4da !important;
        }
        div[data-baseweb="base-input"]:focus-within > div,
        div[data-baseweb="textarea"]:focus-within > div {
            outline: none !important;
            box-shadow: none !important;
            border-color: #ced4da !important;
        }
        div[data-baseweb="base-input"],
        div[data-baseweb="textarea"] {
            box-shadow: none !important;
        }

        /* 4) Semafor: aktivní krok */
        .step-active div[data-baseweb="base-input"],
        .step-active div[data-baseweb="textarea"],
        .step-active textarea,
        .step-active input {
            background-color: #e8f5e9 !important;
            border: 2px solid #28a745 !important;
            box-shadow: none !important;
        }
        .step-active textarea:focus,
        .step-active input:focus,
        .step-active textarea:focus-visible,
        .step-active input:focus-visible {
            outline: none !important;
            box-shadow: none !important;
            border: 2px solid #28a745 !important;
        }
        .step-active div[data-baseweb="base-input"]:focus-within,
        .step-active div[data-baseweb="textarea"]:focus-within,
        .step-active div[data-baseweb="input-container"]:focus-within {
            outline: none !important;
            box-shadow: none !important;
            border-color: #28a745 !important;
            border-width: 2px !important;
        }

        /* 5) Tlačítka */
        div.stButton > button {
            width: 100%;
            height: 3.5em;
            font-weight: 700;
            border-radius: 8px;
        }
        .active-btn button {
            background-color: #28a745 !important;
            color: white !important;
            border: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🦁 PPC Studio")

# Stav
if "step" not in st.session_state:
    st.session_state.step = 1

# Helper na wrappery
def wrap_div(css_class: str, inner_fn):
    st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
    inner_fn()
    st.markdown("</div>", unsafe_allow_html=True)

# --- 1) BRIEF + USPs ---
c1, c2 = st.columns(2)
br_val = st.session_state.get("br", "").strip()

with c1:
    cl_br = "step-active" if not br_val else ""
    st.markdown(f'<div class="{cl_br}">', unsafe_allow_html=True)
    brief = st.text_area("Vložte brief nebo obsah stránky", key="br")
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    st.markdown('<div class="">', unsafe_allow_html=True)
    st.text_area("USPs (volitelné)", key="usps_in")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Generování promptu ---
can_gen = br_val != "" and st.session_state.step == 1
st.markdown(f'<div class="{"active-btn" if can_gen else ""}">', unsafe_allow_html=True)

if st.button("Vygenerovat prompt"):
    if br_val:
        st.session_state.p_text = (
            "Jsi nejlepší PPC copywriter. Vytvoř RSA (15 nadpisů, 4 popisky). "
            "STRIKTNĚ: Nadpis max 30 znaků, Popis max 90 znaků. "
            "Generuj pouze čistý text bez číslování. "
            f"Brief: {brief}. USPs: {st.session_state.usps_in}."
        )
        st.session_state.step = 2
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# --- 2) PROMPT (bez HTML tlačítka) ---
if "p_text" in st.session_state:
    st.subheader("Prompt (zkopírujte do AI)")
    # Streamlit code block (uživatel obvykle kopíruje přes ikonku copy u code bloku) [3](https://docs.streamlit.io/develop/api-reference/text/st.code)[2](https://github.com/streamlit/streamlit/issues/6726)
    st.code(st.session_state.p_text, language=None)
    st.caption("Tip: Klikněte na ikonu kopírování u code bloku (vpravo nahoře).")

    # Zachovej flow: po zobrazení promptu rovnou ukaž další krok
    st.session_state.step = max(st.session_state.step, 3)

# --- 3) VÝSLEDKY + URL ---
if st.session_state.step >= 3:
    st.divider()

    ai_val = st.session_state.get("ai_in", "").strip()
    url_val = st.session_state.get("url_in", "").strip()

    wrap_div("step-active" if not ai_val else "", lambda: st.text_area("Sem vložte vygenerované inzeráty", key="ai_in"))
    wrap_div("step-active" if (ai_val and not url_val) else "", lambda: st.text_input("URL webu (Povinné)", placeholder="https://www.priklad.cz", key="url_in"))

    if ai_val and not url_val:
        st.warning("⚠️ Zbývá poslední krok: Vyplňte URL webu.")

    if ai_val and url_val:
        st.markdown('<div class="active-btn">', unsafe_allow_html=True)
        if st.button("✨ Zpracovat finální inzeráty"):
            lines = [l.strip() for l in st.session_state.ai_in.split("\n") if l.strip()]
            data = [{"Typ": "Nadpis" if i < 15 else "Popis", "Text": t} for i, t in enumerate(lines)]
            st.session_state.df_final = pd.DataFrame(data)
            st.session_state.step = 4
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- 4) TABULKA ---
if st.session_state.get("step") == 4 and "df_final" in st.session_state:
    st.subheader("📊 Hotové inzeráty")
    df = st.session_state.df_final.copy()
    df["Zbývá"] = df.apply(lambda r: (30 if r["Typ"] == "Nadpis" else 90) - len(str(r["Text"])), axis=1)
    st.data_editor(df, use_container_width=True, hide_index=True)
