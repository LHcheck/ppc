import streamlit as st
import pandas as pd

# ==============
# Config
# ==============
APP_TITLE = "🦁 PPC Studio"
PAGE_TITLE = "PPC Studio"

TEXTAREA_HEIGHT_PX = 120
LABEL_HEIGHT_PX = 25
LABEL_MARGIN_BOTTOM_PX = 8

HEADLINE_LIMIT = 30
DESC_LIMIT = 90
HEADLINE_COUNT = 15
DESC_COUNT = 4

st.set_page_config(layout="wide", page_title=PAGE_TITLE)

# ==============
# CSS (sjednocené)
# ==============
st.markdown(
    f"""
    <style>
      .stTextArea textarea {{
        height: {TEXTAREA_HEIGHT_PX}px !important;
        min-height: {TEXTAREA_HEIGHT_PX}px !important;
        max-height: {TEXTAREA_HEIGHT_PX}px !important;
        font-size: 16px !important;
      }}
      .stTextInput input {{ font-size: 16px !important; }}

      div[data-testid="column"] label {{
        height: {LABEL_HEIGHT_PX}px !important;
        display: flex !important;
        align-items: center !important;
        margin-bottom: {LABEL_MARGIN_BOTTOM_PX}px !important;
      }}

      /* remove red focus border (BaseWeb) */
      textarea:focus, textarea:focus-visible,
      input:focus, input:focus-visible {{
        outline: none !important;
        box-shadow: none !important;
      }}
      div[data-baseweb="base-input"]:focus-within,
      div[data-baseweb="textarea"]:focus-within,
      div[data-baseweb="input"]:focus-within,
      div[data-baseweb="input-container"]:focus-within {{
        outline: none !important;
        box-shadow: none !important;
        border-color: #ced4da !important;
      }}
      div[data-baseweb="base-input"]:focus-within > div,
      div[data-baseweb="textarea"]:focus-within > div {{
        outline: none !important;
        box-shadow: none !important;
        border-color: #ced4da !important;
      }}
      div[data-baseweb="base-input"],
      div[data-baseweb="textarea"] {{
        box-shadow: none !important;
      }}

      /* semafor */
      .step-active div[data-baseweb="base-input"],
      .step-active div[data-baseweb="textarea"],
      .step-active textarea,
      .step-active input {{
        background-color: #e8f5e9 !important;
        border: 2px solid #28a745 !important;
        box-shadow: none !important;
      }}

      /* buttons */
      div.stButton > button {{
        width: 100%;
        height: 3.5em;
        font-weight: 700;
        border-radius: 8px;
      }}
      .active-btn button {{
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ==============
# Helpers
# ==============
def wrap(css_class: str, render_fn):
    st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
    render_fn()
    st.markdown("</div>", unsafe_allow_html=True)

def filled(key: str) -> bool:
    return bool(st.session_state.get(key, "").strip())

def parse_lines(text: str):
    return [l.strip() for l in (text or "").split("\n") if l.strip()]

# ==============
# Optional dependency: st-copy
# ==============
COPY_AVAILABLE = True
try:
    from st_copy import copy_button  # [1](https://www.mostlypython.com/deploying-simple-streamlit-apps/)[2](https://streamlit.io/)
except Exception:
    COPY_AVAILABLE = False

# ==============
# UI
# ==============
st.title(APP_TITLE)

if "step" not in st.session_state:
    st.session_state.step = 1

# ---- Step 1: Brief + USPs ----
c1, c2 = st.columns(2)
with c1:
    wrap("step-active" if not filled("br") else "", lambda: st.text_area(
        "Vložte brief nebo obsah stránky",
        key="br",
        height=TEXTAREA_HEIGHT_PX,
    ))

with c2:
    wrap("", lambda: st.text_area(
        "USPs (volitelné)",
        key="usps_in",
        height=TEXTAREA_HEIGHT_PX,
    ))

can_generate = filled("br") and st.session_state.step == 1
wrap("active-btn" if can_generate else "", lambda: None)

if st.button("Vygenerovat prompt"):
    if filled("br"):
        brief = st.session_state.br.strip()
        usps = st.session_state.usps_in.strip()
        st.session_state.p_text = (
            "Jsi nejlepší PPC copywriter. Vytvoř RSA (15 nadpisů, 4 popisky). "
            f"STRIKTNĚ: Nadpis max {HEADLINE_LIMIT} znaků, Popis max {DESC_LIMIT} znaků. "
            "Generuj pouze čistý text bez číslování. "
            f"Brief: {brief}. USPs: {usps}."
        )
        st.session_state.step = 2
        st.rerun()

# ---- Step 2: Prompt (stejná šířka jako Brief/USPs) + copy ----
if "p_text" in st.session_state:
    # levý sloupec = stejná šířka jako Brief/USPs
    left, right = st.columns(2)
    with left:
        st.text_area(
            "Prompt (zkopírujte do AI)",
            value=st.session_state.p_text,
            key="prompt_display",
            height=TEXTAREA_HEIGHT_PX,
            disabled=True,
        )

        if not COPY_AVAILABLE:
            st.error(
                "Kopírování není aktivní – chybí balíček `st-copy` nebo je starý Streamlit.\n"
                "Zkontrolujte `requirements.txt`: streamlit>=1.45, pandas, st-copy."
            )
        else:
            # copy_button vrací True/False/None [1](https://www.mostlypython.com/deploying-simple-streamlit-apps/)
            copied = copy_button(
                st.session_state.p_text,
                tooltip="Zkopírovat prompt",
                copied_label="Copied",
                icon="st",
                key="copy_prompt",
            )
            if copied is True:
                st.session_state.step = 3
                st.rerun()
            elif copied is False:
                st.warning("Kopírování selhalo (omezení prohlížeče/clipboard). Zkuste znovu.")

    with right:
        # prázdno = zachová šířky jako v kroku 1
        st.empty()

# ---- Step 3: až po kopírování ----
if st.session_state.step >= 3:
    st.divider()

    wrap("step-active" if not filled("ai_in") else "", lambda: st.text_area(
        "Sem vložte vygenerované inzeráty",
        key="ai_in",
        height=TEXTAREA_HEIGHT_PX,
    ))

    ai_ok = filled("ai_in")
    wrap("step-active" if (ai_ok and not filled("url_in")) else "", lambda: st.text_input(
        "URL webu (Povinné)",
        placeholder="https://www.priklad.cz",
        key="url_in",
    ))

    if ai_ok and not filled("url_in"):
        st.warning("⚠️ Zbývá poslední krok: Vyplňte URL webu.")

    if ai_ok and filled("url_in"):
        wrap("active-btn", lambda: None)
        if st.button("✨ Zpracovat finální inzeráty"):
            lines = parse_lines(st.session_state.ai_in)
            data = [{"Typ": "Nadpis" if i < HEADLINE_COUNT else "Popis", "Text": t} for i, t in enumerate(lines)]
            df = pd.DataFrame(data)
            df["Zbývá"] = df.apply(
                lambda r: (HEADLINE_LIMIT if r["Typ"] == "Nadpis" else DESC_LIMIT) - len(str(r["Text"])),
                axis=1
            )
            st.session_state.df_final = df
            st.session_state.step = 4
            st.rerun()

# ---- Step 4 ----
if st.session_state.get("step") == 4 and "df_final" in st.session_state:
    st.subheader("📊 Hotové inzeráty")
    st.data_editor(st.session_state.df_final, use_container_width=True, hide_index=True)
