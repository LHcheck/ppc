import streamlit as st
import pandas as pd
import io
import random

st.set_page_config(layout="wide", page_title="PPC Studio")

# --- FINÁLNÍ STYLING PRO PERFEKTNÍ SYMETRII ---
st.markdown("""
<style>
    /* 1) ODSTRANĚNÍ ČERVENÉHO FOCUS BORDERU (Streamlit/BaseWeb) */
    .stTextArea textarea:focus,
    .stTextInput input:focus {
        outline: none !important;
        box-shadow: none !important;
        border: 1px solid #ced4da !important;  /* neutrální */
    }

    /* BaseWeb wrapper - Streamlit často kreslí border/box-shadow tady */
    div[data-baseweb="base-input"]:focus-within,
    div[data-baseweb="textarea"]:focus-within {
        outline: none !important;
        box-shadow: none !important;
        border-color: #ced4da !important;       /* neutrální */
    }

    /* Některé verze Streamlitu dávají focus stín přes tento wrapper */
    div[data-baseweb="base-input"] {
        box-shadow: none !important;
    }

    /* 2) JEDNOTNÁ VÝŠKA A PÍSMO */
    .stTextArea textarea, .stTextInput input {
        height: 120px !important;
        min-height: 120px !important;
        max-height: 120px !important;
        font-size: 16px !important;
    }

    /* 3) SROVNÁNÍ LABELŮ (NADPISŮ POLÍ) */
    div[data-testid="column"] label {
        height: 25px !important;
        display: flex !important;
        align-items: center !important;
        margin-bottom: 8px !important;
    }

    /* 4) AKTIVNÍ ZELENÝ KROK (SEMAFOR) */
    .step-active div[data-baseweb="base-input"],
    .step-active div[data-baseweb="textarea"],
    .step-active textarea,
    .step-active input {
        background-color: #e8f5e9 !important;
        border: 2px solid #28a745 !important;
        box-shadow: none !important;
    }

    /* Step-active focus musí zůstat zelený (a žádný červený/box-shadow) */
    .step-active textarea:focus,
    .step-active input:focus {
        outline: none !important;
        box-shadow: none !important;
        border: 2px solid #28a745 !important;
    }
    .step-active div[data-baseweb="base-input"]:focus-within,
    .step-active div[data-baseweb="textarea"]:focus-within {
        outline: none !important;
        box-shadow: none !important;
        border-color: #28a745 !important;
        border-width: 2px !important;
    }

    /* 5) TLAČÍTKA */
    div.stButton > button {
        width: 100%;
        height: 3.5em;
        font-weight: bold;
        border-radius: 8px;
    }
    .active-btn button {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }

</style>
""", unsafe_allow_html=True)

st.title("🦁 PPC Studio")

# Inicializace stavu
if "step" not in st.session_state:
    st.session_state.step = 1

# --- 1. KROK: BRIEF A USPs ---
c1, c2 = st.columns(2)

br_val = st.session_state.get("br", "").strip()

with c1:
    # Zelená, pokud je prázdno
    cl_br = "step-active" if not br_val else ""
    st.markdown(f'<div class="{cl_br}">', unsafe_allow_html=True)
    brief = st.text_area("Vložte brief nebo obsah stránky", key="br")
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    # wrapper kvůli identické DOM struktuře (zarovnání)
    st.markdown('<div class="">', unsafe_allow_html=True)
    st.text_area("USPs (volitelné)", key="usps_in")
    st.markdown('</div>', unsafe_allow_html=True)

# Generování promptu
can_gen = br_val != "" and st.session_state.step == 1
btn_p_cl = "active-btn" if can_gen else ""
st.markdown(f'<div class="{btn_p_cl}">', unsafe_allow_html=True)

if st.button("Vygenerovat prompt"):
    if br_val:
        st.session_state.p_text = (
            "Jsi nejlepší PPC copywriter. Vytvoř RSA (15 nadpisů, 4 popisky). "
            "STRIKTNĚ: Nadpis max 30 znaků, Popis max 90 znaků. "
            "Generuj pouze čistý text bez číslování. "
            f"Brief: {st.session_state.br}. USPs: {st.session_state.usps_in}."
        )
        st.session_state.step = 2
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# --- 2. KROK: PROMPT + KOPÍROVÁNÍ ---
if "p_text" in st.session_state:
    p1, p2 = st.columns(2)

    with p1:
        st.text_area(
            "Prompt (zkopírujte do AI)",
            value=st.session_state.p_text,
            key="prompt_display",
            disabled=True
        )

    with p2:
        # ✅ OPRAVA 2: posun tlačítka dolů o výšku labelu + margin (25 + 8 = 33px)
        st.markdown('<div style="height:33px"></div>', unsafe_allow_html=True)

        btn_cp_cl = "active-btn" if st.session_state.step == 2 else ""
        st.markdown(f'<div class="{btn_cp_cl}">', unsafe_allow_html=True)

        if st.button("📋 Zkopírovat prompt"):
            safe_text = st.session_state.p_text.replace("`", "\\`")
            st.components.v1.html(
                f"<script>navigator.clipboard.writeText(`{safe_text}`);</script>",
                height=0
            )
            st.session_state.step = 3
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# --- 3. KROK: VÝSLEDKY A URL ---
if st.session_state.step >= 3:
    st.divider()
    ai_val = st.session_state.get("ai_in", "").strip()
    url_val = st.session_state.get("url_in", "").strip()

    # Inzeráty z Gemini
    cl_ai = "step-active" if not ai_val else ""
    st.markdown(f'<div class="{cl_ai}">', unsafe_allow_html=True)
    ai_text = st.text_area("Sem vložte vygenerované inzeráty", key="ai_in")
    st.markdown('</div>', unsafe_allow_html=True)

    # URL pole (Zelené jen když máme inzeráty, ale ne URL)
    cl_url = "step-active" if (ai_val and not url_val) else ""
    st.markdown(f'<div class="{cl_url}">', unsafe_allow_html=True)
    st.text_input("URL webu (Povinné)", placeholder="https://www.priklad.cz", key="url_in")
    st.markdown('</div>', unsafe_allow_html=True)

    if ai_val and not url_val:
        st.warning("⚠️ Zbývá poslední krok: Vyplňte URL webu.")

    if ai_val and url_val:
        st.markdown('<div class="active-btn">', unsafe_allow_html=True)
        if st.button("✨ Zpracovat finální inzeráty"):
            lines = [l.strip() for l in ai_text.split('\n') if l.strip()]
            data = [{"Typ": "Nadpis" if i < 15 else "Popis", "Text": t} for i, t in enumerate(lines)]
            st.session_state.df_final = pd.DataFrame(data)
            st.session_state.step = 4
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- FINÁLNÍ TABULKA ---
if st.session_state.get("step") == 4:
    st.subheader("📊 Hotové inzeráty")
    df = st.session_state.df_final
    df["Zbývá"] = df.apply(
        lambda r: (30 if r["Typ"] == "Nadpis" else 90) - len(str(r["Text"])),
        axis=1
    )
    st.data_editor(df, use_container_width=True, hide_index=True)
