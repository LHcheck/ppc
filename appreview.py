import streamlit as st
import pandas as pd

# -----------------------------
# Konfigurace
# -----------------------------
APP_TITLE = "🦁 PPC Studio"
PAGE_TITLE = "PPC Studio"

TEXTAREA_HEIGHT_PX = 120
LABEL_HEIGHT_PX = 25
LABEL_MARGIN_BOTTOM_PX = 8
LABEL_OFFSET_PX = LABEL_HEIGHT_PX + LABEL_MARGIN_BOTTOM_PX

st.set_page_config(layout="wide", page_title=PAGE_TITLE)

# -----------------------------
# CSS
# -----------------------------
st.markdown(
    f"""
    <style>
      /* Jednotná výška textových polí */
      .stTextArea textarea {{
          height: {TEXTAREA_HEIGHT_PX}px !important;
          min-height: {TEXTAREA_HEIGHT_PX}px !important;
          max-height: {TEXTAREA_HEIGHT_PX}px !important;
          font-size: 16px !important;
      }}
      .stTextInput input {{
          font-size: 16px !important;
      }}

      /* Srovnání labelů ve sloupcích */
      div[data-testid="column"] label {{
          height: {LABEL_HEIGHT_PX}px !important;
          display: flex !important;
          align-items: center !important;
          margin-bottom: {LABEL_MARGIN_BOTTOM_PX}px !important;
      }}

      /* Odstranění červeného focus borderu (Streamlit/BaseWeb) */
      .stTextArea textarea:focus,
      .stTextInput input:focus {{
          outline: none !important;
          box-shadow: none !important;
          border: 1px solid #ced4da !important;
      }}
      div[data-baseweb="base-input"]:focus-within,
      div[data-baseweb="textarea"]:focus-within {{
          outline: none !important;
          box-shadow: none !important;
          border-color: #ced4da !important;
      }}
      div[data-baseweb="base-input"],
      div[data-baseweb="textarea"] {{
          box-shadow: none !important;
      }}

      /* Semafor: aktivní krok */
      .step-active div[data-baseweb="base-input"],
      .step-active div[data-baseweb="textarea"],
      .step-active textarea,
      .step-active input {{
          background-color: #e8f5e9 !important;
          border: 2px solid #28a745 !important;
          box-shadow: none !important;
      }}

      /* Tlačítka (původní Streamlit styl) */
      div.stButton > button {{
          width: 100%;
          height: 3.5em;
          font-weight: bold;
          border-radius: 8px;
      }}

      /* "Active" zelené tlačítko */
      .active-btn button {{
          background-color: #28a745 !important;
          color: white !important;
          border: none !important;
      }}

      /* ✅ Ujisti se, že i HTML copy tlačítko má stejný rozměr jako Streamlit button */
      .active-btn #copyBtn {{
          width: 100% !important;
          height: 3.5em !important;
          font-weight: bold !important;
          border-radius: 8px !important;
          background-color: #28a745 !important;
          color: white !important;
          border: none !important;
          cursor: pointer !important;
      }}

      /* Spacer pro zarovnání copy tlačítka s prompt fieldem */
      .label-spacer {{
          height: {LABEL_OFFSET_PX}px;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Helpery
# -----------------------------
def wrap_div(css_class: str, inner_fn):
    st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
    inner_fn()
    st.markdown("</div>", unsafe_allow_html=True)


def copy_button_component(text: str):
    """
    Jediné tlačítko 'Zkopírovat prompt' (bez dalších sekcí).
    Zobrazí malé potvrzení 'Copied' přímo pod tlačítkem.
    """
    safe = (
        (text or "")
        .replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
        .replace("</script>", "<\\/script>")
    )

    st.components.v1.html(
        f"""
        <div style="display:flex; flex-direction:column; gap:6px;">
          <button id="copyBtn">📋 Zkopírovat prompt</button>
          <div id="copyStatus" style="font-size:12px; min-height:16px; color:#6b7280;"></div>
        </div>

        <script>
          const text = `{safe}`;
          const btn = document.getElementById("copyBtn");
          const status = document.getElementById("copyStatus");

          async function copyModern() {{
            try {{
              await navigator.clipboard.writeText(text);
              return true;
            }} catch (e) {{
              return false;
            }}
          }}

          function copyFallback() {{
            try {{
              const ta = document.createElement('textarea');
              ta.value = text;
              ta.setAttribute('readonly', '');
              ta.style.position = 'fixed';
              ta.style.top = '0';
              ta.style.left = '0';
              ta.style.opacity = '0';
              document.body.appendChild(ta);
              ta.focus();
              ta.select();
              const ok = document.execCommand('copy');
              document.body.removeChild(ta);
              return ok;
            }} catch (e) {{
              return false;
            }}
          }}

          btn.addEventListener("click", async () => {{
            status.textContent = "";
            const okModern = await copyModern();
            const ok = okModern || copyFallback();

            if (ok) {{
              status.textContent = "Copied";
              status.style.color = "#16a34a";
            }} else {{
              status.textContent = "Copy failed";
              status.style.color = "#dc2626";
            }}
          }});
        </script>
        """,
        height=78,
    )

# -----------------------------
# UI
# -----------------------------
st.title(APP_TITLE)

if "step" not in st.session_state:
    st.session_state.step = 1

# --- 1) BRIEF + USPs ---
c1, c2 = st.columns(2)
brief_val = st.session_state.get("br", "").strip()

with c1:
    wrap_div(
        "step-active" if not brief_val else "",
        lambda: st.text_area("Vložte brief nebo obsah stránky", key="br"),
    )

with c2:
    wrap_div(
        "",
        lambda: st.text_area("USPs (volitelné)", key="usps_in"),
    )

# Generování promptu
can_generate = (brief_val != "") and (st.session_state.step == 1)
wrap_div("active-btn" if can_generate else "", lambda: None)

if st.button("Vygenerovat prompt"):
    if brief_val:
        st.session_state.p_text = (
            "Jsi nejlepší PPC copywriter. Vytvoř RSA (15 nadpisů, 4 popisky). "
            "STRIKTNĚ: Nadpis max 30 znaků, Popis max 90 znaků. "
            "Generuj pouze čistý text bez číslování. "
            f"Brief: {st.session_state.br}. USPs: {st.session_state.usps_in}."
        )
        st.session_state.step = 2
        st.rerun()

# Zavření wrapperu tlačítka
st.markdown("</div>", unsafe_allow_html=True)

# --- 2) PROMPT + COPY (bez dalších sekcí/tlačítek) ---
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
        st.markdown('<div class="label-spacer"></div>', unsafe_allow_html=True)

        # Stejný vzhled jako aktivní tlačítka
        st.markdown('<div class="active-btn">', unsafe_allow_html=True)
        copy_button_component(st.session_state.p_text)
        st.markdown("</div>", unsafe_allow_html=True)

        # po vygenerování promptu zůstáváme ve step 2; uživatel může pokračovat sám,
        # nebo se step posune automaticky až po dalším kroku (vložení AI textu)
        # pokud chceš posun kroku po kopii, dá se udělat jinak, ale bez dalšího tlačítka.

# --- 3) VÝSLEDKY + URL ---
if st.session_state.step >= 3:
    st.divider()

    ai_val = st.session_state.get("ai_in", "").strip()
    url_val = st.session_state.get("url_in", "").strip()

    wrap_div(
        "step-active" if not ai_val else "",
        lambda: st.text_area("Sem vložte vygenerované inzeráty", key="ai_in"),
    )

    wrap_div(
        "step-active" if (ai_val and not url_val) else "",
        lambda: st.text_input("URL webu (Povinné)", placeholder="https://www.priklad.cz", key="url_in"),
    )

    if ai_val and not url_val:
        st.warning("⚠️ Zbývá poslední krok: Vyplňte URL webu.")

    if ai_val and url_val:
        wrap_div("active-btn", lambda: None)

        if st.button("✨ Zpracovat finální inzeráty"):
            lines = [l.strip() for l in st.session_state.ai_in.split("\n") if l.strip()]
            data = [{"Typ": "Nadpis" if i < 15 else "Popis", "Text": t} for i, t in enumerate(lines)]
            st.session_state.df_final = pd.DataFrame(data)
            st.session_state.step = 4
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# --- 4) FINÁLNÍ TABULKA ---
if st.session_state.get("step") == 4 and "df_final" in st.session_state:
    st.subheader("📊 Hotové inzeráty")
    df = st.session_state.df_final.copy()

    df["Zbývá"] = df.apply(
        lambda r: (30 if r["Typ"] == "Nadpis" else 90) - len(str(r["Text"])),
        axis=1,
    )
    st.data_editor(df, use_container_width=True, hide_index=True)
