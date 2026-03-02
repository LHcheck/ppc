import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="PPC Studio")

# --- STYLING + odstranění červeného focus borderu ---
st.markdown(
    """
    <style>
        /* =========================================================
           1) VZHLED POLÍ: výška, písmo
           ========================================================= */
        .stTextArea textarea {
            height: 120px !important;
            min-height: 120px !important;
            max-height: 120px !important;
            font-size: 16px !important;
        }
        .stTextInput input {
            font-size: 16px !important;
        }

        /* =========================================================
           2) Zarovnání labelů ve sloupcích
           ========================================================= */
        div[data-testid="column"] label {
            height: 25px !important;
            display: flex !important;
            align-items: center !important;
            margin-bottom: 8px !important;
        }

        /* =========================================================
           3) ODSTRANĚNÍ ČERVENÉHO FOCUS BORDERU (Streamlit/BaseWeb)
           - Streamlit používá BaseWeb wrappery, které kreslí focus přes :focus-within
           - proto přepisujeme jak textarea/input, tak BaseWeb kontejnery
           ========================================================= */
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
            border-color: #ced4da !important; /* neutrální šedá místo červené */
        }

        /* Některé verze kreslí border na vnitřní wrapper (přetluč i child div) */
        div[data-baseweb="base-input"]:focus-within > div,
        div[data-baseweb="textarea"]:focus-within > div {
            outline: none !important;
            box-shadow: none !important;
            border-color: #ced4da !important;
        }

        /* Preventivně vypnout shadow i mimo focus-within (některé verze) */
        div[data-baseweb="base-input"],
        div[data-baseweb="textarea"] {
            box-shadow: none !important;
        }

        /* =========================================================
           4) SEMAFOR: aktivní zelený krok
           ========================================================= */
        .step-active div[data-baseweb="base-input"],
        .step-active div[data-baseweb="textarea"],
        .step-active textarea,
        .step-active input {
            background-color: #e8f5e9 !important;
            border: 2px solid #28a745 !important;
            box-shadow: none !important;
        }

        /* Když je step-active, focus zůstane zelený */
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

        /* =========================================================
           5) TLAČÍTKA
           ========================================================= */
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

        /* =========================================================
           6) PROMPT BOX (volitelné)
           ========================================================= */
        .prompt-box {
            background: #f8f9fa;
            border: 2px solid #dee2e6;
            padding: 15px;
            border-radius: 10px;
            font-weight: 700;
            margin-bottom: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🦁 PPC Studio")

# -------------------------------------------------
# Stav aplikace
# -------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1

# -------------------------------------------------
# 1) KROK: Brief + USPs
# -------------------------------------------------
c1, c2 = st.columns(2)
br_val = st.session_state.get("br", "").strip()

with c1:
    cl_br = "step-active" if not br_val else ""
    st.markdown(f'<div class="{cl_br}">', unsafe_allow_html=True)
    brief = st.text_area("Vložte brief nebo obsah stránky", key="br")
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    # wrapper kvůli pixel-perfect zarovnání
    st.markdown('<div class="">', unsafe_allow_html=True)
    st.text_area("USPs (volitelné)", key="usps_in")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# Generování promptu
# -------------------------------------------------
can_gen = br_val != "" and st.session_state.step == 1
btn_p_cl = "active-btn" if can_gen else ""
st.markdown(f'<div class="{btn_p_cl}">', unsafe_allow_html=True)

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

# -------------------------------------------------
# 2) KROK: Prompt + kopírování
# -------------------------------------------------
if "p_text" in st.session_state:
    p1, p2 = st.columns(2)

    with p1:
        st.text_area(
            "Prompt (zkopírujte do AI)",
            value=st.session_state.p_text,
            key="prompt_display",
            disabled=True,
        )

    with p2:
        btn_cp_cl = "active-btn" if st.session_state.step == 2 else ""
        st.markdown(f'<div class="{btn_cp_cl}">', unsafe_allow_html=True)

        if st.button("📋 Zkopírovat prompt"):
            # Pozn.: Streamlit-only kopírování do clipboardu bývá omezené prohlížečem.
            # Zde zachováváme tvé původní chování: po kliknutí pokračujeme do další části.
            st.session_state.step = 3
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# 3) KROK: Výsledky + URL
# -------------------------------------------------
if st.session_state.step >= 3:
    st.divider()

    ai_val = st.session_state.get("ai_in", "").strip()
    url_val = st.session_state.get("url_in", "").strip()

    cl_ai = "step-active" if not ai_val else ""
    st.markdown(f'<div class="{cl_ai}">', unsafe_allow_html=True)
    ai_text = st.text_area("Sem vložte vygenerované inzeráty", key="ai_in")
    st.markdown("</div>", unsafe_allow_html=True)

    cl_url = "step-active" if (ai_val and not url_val) else ""
    st.markdown(f'<div class="{cl_url}">', unsafe_allow_html=True)
    st.text_input("URL webu (Povinné)", placeholder="https://www.priklad.cz", key="url_in")
    st.markdown("</div>", unsafe_allow_html=True)

    if ai_val and not url_val:
        st.warning("⚠️ Zbývá poslední krok: Vyplňte URL webu.")

    if ai_val and url_val:
        st.markdown('<div class="active-btn">', unsafe_allow_html=True)

        if st.button("✨ Zpracovat finální inzeráty"):
            lines = [l.strip() for l in ai_text.split("\n") if l.strip()]
            data = [{"Typ": "Nadpis" if i < 15 else "Popis", "Text": t} for i, t in enumerate(lines)]
            st.session_state.df_final = pd.DataFrame(data)
            st.session_state.step = 4
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------
# 4) FINÁLNÍ TABULKA
# -------------------------------------------------
if st.session_state.get("step") == 4 and "df_final" in st.session_state:
    st.subheader("📊 Hotové inzeráty")
    df = st.session_state.df_final.copy()
    df["Zbývá"] = df.apply(
        lambda r: (30 if r["Typ"] == "Nadpis" else 90) - len(str(r["Text"])),
        axis=1,
    )
    st.data_editor(df, use_container_width=True, hide_index=True)
