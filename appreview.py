import streamlit as st
import pandas as pd

# =============================
# Konfigurace
# =============================
APP_TITLE = "🦁 PPC Studio"
PAGE_TITLE = "PPC Studio"

TEXTAREA_HEIGHT_PX = 120
LABEL_HEIGHT_PX = 25
LABEL_MARGIN_BOTTOM_PX = 8

HEADLINE_LIMIT = 30
DESC_LIMIT = 90
HEADLINE_COUNT = 15
DESC_COUNT = 4
TOTAL_LINES = HEADLINE_COUNT + DESC_COUNT  # 19

st.set_page_config(layout="wide", page_title=PAGE_TITLE)

# =============================
# CSS (jedno místo, čistě)
# =============================
st.markdown(
    f"""
    <style>
      /* --- jednotné textarea --- */
      .stTextArea textarea {{
        height: {TEXTAREA_HEIGHT_PX}px !important;
        min-height: {TEXTAREA_HEIGHT_PX}px !important;
        max-height: {TEXTAREA_HEIGHT_PX}px !important;
        font-size: 16px !important;
      }}
      .stTextInput input {{
        font-size: 16px !important;
      }}

      /* --- zarovnání labelů ve sloupcích --- */
      div[data-testid="column"] label {{
        height: {LABEL_HEIGHT_PX}px !important;
        display: flex !important;
        align-items: center !important;
        margin-bottom: {LABEL_MARGIN_BOTTOM_PX}px !important;
      }}

      /* --- odstranění červeného focus borderu (robustně pro BaseWeb) --- */
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

      /* --- semafor: aktivní krok --- */
      .step-active div[data-baseweb="base-input"],
      .step-active div[data-baseweb="textarea"],
      .step-active textarea,
      .step-active input {{
        background-color: #e8f5e9 !important;
        border: 2px solid #28a745 !important;
        box-shadow: none !important;
      }}

      /* --- tlačítka --- */
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

# =============================
# Helpery (sjednocení komponent)
# =============================
def wrap(css_class: str, render_fn):
    """Obalí libovolný Streamlit prvek do divu pro styling (step-active/active-btn)."""
    st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
    render_fn()
    st.markdown("</div>", unsafe_allow_html=True)

def is_filled(key: str) -> bool:
    return bool(st.session_state.get(key, "").strip())

def parse_lines(text: str):
    return [l.strip() for l in (text or "").split("\n") if l.strip()]

def build_ads_df(lines):
    data = [{"Typ": "Nadpis" if i < HEADLINE_COUNT else "Popis", "Text": t} for i, t in enumerate(lines)]
    df = pd.DataFrame(data)
    df["Zbývá"] = df.apply(
        lambda r: (HEADLINE_LIMIT if r["Typ"] == "Nadpis" else DESC_LIMIT) - len(str(r["Text"])),
        axis=1
    )
    return df


# =============================
# UI
# =============================
st.title(APP_TITLE)

# stav
if "step" not in st.session_state:
    st.session_state.step = 1

# -------------------------------------------------
# 1) BRIEF + USPs (sjednoceně text_area + stejná výška)
# -------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    wrap("step-active" if not is_filled("br") else "", lambda: st.text_area(
        "Vložte brief nebo obsah stránky",
        key="br"
    ))

with c2:
    # USPs sjednocené: také text_area se stejnou výškou
    wrap("", lambda: st.text_area(
        "USPs (volitelné)",
        key="usps_in"
    ))

# -------------------------------------------------
# Tlačítko: generovat prompt
# -------------------------------------------------
can_generate = is_filled("br") and st.session_state.step == 1
wrap("active-btn" if can_generate else "", lambda: None)

if st.button("Vygenerovat prompt"):
    if is_filled("br"):
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

# -------------------------------------------------
# 2) PROMPT (stejný typ/rozměr jako Brief/USPs)
# + kopírování čistě Streamlit (bez .html)
# -------------------------------------------------
if "p_text" in st.session_state:
    # Prompt box: text_area disabled -> stejná výška jako ostatní textarea
    st.text_area(
        "Prompt (zkopírujte do AI)",
        value=st.session_state.p_text,
        key="prompt_display",
        disabled=True,
    )

    # Kopírování bez HTML: code block (většina verzí má copy ikonku)
    with st.expander("Kopírovat prompt"):
        st.code(st.session_state.p_text, language=None)
        st.caption("Tip: Použijte ikonu kopírování u code bloku (vpravo nahoře).")

    # Po vygenerování promptu už může pokračovat část 3
    st.session_state.step = max(st.session_state.step, 3)

# -------------------------------------------------
# 3) VÝSLEDKY + URL (sjednoceně)
# -------------------------------------------------
if st.session_state.step >= 3:
    st.divider()

    # AI výstup (textarea stejné výšky)
    wrap("step-active" if not is_filled("ai_in") else "", lambda: st.text_area(
        "Sem vložte vygenerované inzeráty",
        key="ai_in"
    ))

    # URL (text_input)
    ai_ok = is_filled("ai_in")
    wrap("step-active" if (ai_ok and not is_filled("url_in")) else "", lambda: st.text_input(
        "URL webu (Povinné)",
        placeholder="https://www.priklad.cz",
        key="url_in"
    ))

    if ai_ok and not is_filled("url_in"):
        st.warning("⚠️ Zbývá poslední krok: Vyplňte URL webu.")

    # -------------------------------------------------
    # Tlačítko: zpracovat finální inzeráty
    # -------------------------------------------------
    if ai_ok and is_filled("url_in"):
        wrap("active-btn", lambda: None)

        if st.button("✨ Zpracovat finální inzeráty"):
            lines = parse_lines(st.session_state.ai_in)

            # volitelná validace počtu řádků – nechávám jemně (bez blokace)
            if len(lines) < TOTAL_LINES:
                st.warning(f"⚠️ Našla jsem jen {len(lines)} řádků, očekává se {TOTAL_LINES} (15 nadpisů + 4 popisy). "
                           "I tak pokračuji, ale zkontrolujte výstup.")
            st.session_state.df_final = build_ads_df(lines)
            st.session_state.step = 4
            st.rerun()

# -------------------------------------------------
# 4) TABULKA
# -------------------------------------------------
if st.session_state.get("step") == 4 and "df_final" in st.session_state:
    st.subheader("📊 Hotové inzeráty")
    st.data_editor(st.session_state.df_final, use_container_width=True, hide_index=True)
