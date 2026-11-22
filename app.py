import html as _html
import importlib
import sys
from pathlib import Path

import base64
from pathlib import Path

import streamlit as st
from huggingface_hub import snapshot_download

LOGO_PATH = Path(__file__).parent / "assets" / "logo.png"

# ==========================================
# Page configuration
# ==========================================
st.set_page_config(
    page_title="HeadlineGuard BD | Bangla Clickbait Detection",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

REPO_ID = "Archmage64/HeadlineguardBD"
LOGO_PATH = Path(__file__).parent / "assets" / "logo.png"

EXAMPLES = [
    (
        "Sensational headline",
        "এই ভিডিও দেখলে আপনার চোখ কপালে উঠবে, যা ঘটল বিশ্বাস করতে পারবেন না!",
        "",
    ),
    (
        "Standard news",
        "নতুন শিক্ষাবর্ষে সারা দেশে বিনামূল্যে পাঠ্যবই বিতরণ শুরু",
        "রোববার থেকে দেশের প্রাথমিক ও মাধ্যমিক স্তরের শিক্ষার্থীদের হাতে নতুন বই তুলে দেওয়া শুরু হয়েছে।",
    ),
    (
        "Curiosity gap",
        "জনপ্রিয় অভিনেত্রীর গোপন সত্য ফাঁস, কারণ জানলে হতবাক হবেন",
        "",
    ),
]


def html(markup: str) -> None:
    """Render HTML safely through st.markdown (strips indentation so it is never read as a code block)."""
    cleaned = "\n".join(line.strip() for line in markup.strip().splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


def logo_data_uri() -> str:
    if not LOGO_PATH.exists():
        return ""
    data = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


# ==========================================
# Styles (matches the project presentation: deep green, red accent, mint cards, Fira Sans)
# ==========================================
html(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Sans:wght@400;500;600;700;800&family=Hind+Siliguri:wght@400;500;600;700&display=swap');

/* Light palette (default) */
:root {
    --bg: #F3F8F5;
    --surface: #FFFFFF;
    --mint: #E3F0E8;
    --line: #CFE2D6;
    --text: #0B2A20;
    --head: #08402E;
    --muted: #4A6358;
    --ink: #0E7A52;
    --ink-soft: rgba(14, 122, 82, 0.12);
    --bad: #C62828;
    --bad-soft: #FDECEA;
    --good: #0E7A52;
    --good-soft: #E3F0E8;
    --red: #C62828;
}

html, body, .stApp, .stMarkdown, .stTextArea textarea, .stButton button, label, p, li {
    font-family: 'Fira Sans', 'Hind Siliguri', system-ui, sans-serif;
}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: var(--bg);
    color: var(--text);
}
.block-container { max-width: 1080px; padding-top: 2rem; padding-bottom: 3rem; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

/* ---------- Masthead (deck cover) ---------- */
.mast {
    background: #08402E;
    border-bottom: 8px solid var(--red);
    border-radius: 24px;
    padding: 2.2rem 2.4rem 2rem;
    margin-bottom: 2rem;
}
.mast-top { display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.1rem; }
.mast-brand { display: flex; align-items: center; gap: 0.9rem; flex-wrap: wrap; }
.mast-logo {
    height: 70px; width: auto; display: block;
    background: rgba(255, 246, 244, 0.96);
    padding: 0.35rem 0.55rem; border-radius: 12px;
}
.mast-tag {
    background: #FFF6F4; color: var(--red) !important;
    font-size: 0.78rem; font-weight: 700; letter-spacing: 0.12em;
    padding: 0.4rem 1rem; border-radius: 999px;
}
.mast-status {
    display: inline-flex; align-items: center; gap: 0.5rem;
    border: 2px solid #4FA283; border-radius: 999px;
    padding: 0.3rem 0.9rem; font-size: 0.85rem; font-weight: 600; white-space: nowrap;
    color: #DDEFE4 !important;
}
.mast-status i { width: 9px; height: 9px; border-radius: 50%; background: #6FD3A8; display: inline-block; }
.mast h1 {
    font-family: 'Fira Sans', 'Hind Siliguri', sans-serif;
    font-weight: 800;
    font-size: clamp(2.4rem, 5.5vw, 4rem);
    line-height: 1.02;
    letter-spacing: -0.02em;
    margin: 0 0 0.8rem 0;
    padding: 0;
    color: #FFF6F4 !important;
}
.mast h1 span { color: #FF9C8A !important; }
.mast p { margin: 0; max-width: 36rem; font-size: 1.1rem; line-height: 1.55; color: #BFDCCB !important; }
.chips { display: flex; flex-wrap: wrap; gap: 0.6rem; margin-top: 1.3rem; }
.chips span {
    border: 2px solid #4FA283; border-radius: 999px; padding: 0.25rem 0.9rem;
    font-size: 0.85rem; font-weight: 600; color: #DDEFE4 !important;
}
@media (max-width: 700px) { .mast { padding: 1.5rem 1.3rem; } }

/* ---------- Form ---------- */
[data-testid="stForm"] {
    border: 2px solid var(--line);
    border-radius: 24px;
    background: var(--surface);
    padding: 1.8rem 2rem 1.5rem;
}
.section-title {
    font-size: 1.3rem; font-weight: 700; color: var(--head);
    border-left: 6px solid var(--red); padding-left: 0.8rem; margin: 0 0 1.1rem 0;
}
.stTextArea textarea {
    border-radius: 16px;
    border: 2px solid var(--line);
    font-size: 1.08rem; line-height: 1.65;
}
.stTextArea textarea:focus { border-color: var(--ink); box-shadow: 0 0 0 3px var(--ink-soft); }
.stTextArea label p { font-weight: 600; font-size: 0.95rem; }

div[data-testid="stFormSubmitButton"] > button {
    background: var(--red); color: #fff; border: none; border-radius: 999px;
    font-weight: 700; font-size: 1.02rem; padding: 0.65rem 2.2rem;
    transition: background 0.15s ease, transform 0.15s ease;
}
div[data-testid="stFormSubmitButton"] > button:hover { background: #A81F1F; color: #fff; transform: translateY(-1px); }
div[data-testid="stFormSubmitButton"] > button:focus-visible { outline: 3px solid var(--ink-soft); outline-offset: 2px; }

/* Example buttons (deck pills) */
.stButton > button {
    border-radius: 999px; border: 2px solid var(--line); background: var(--mint); color: var(--head);
    font-size: 0.95rem; font-weight: 600; transition: border-color 0.15s ease, background 0.15s ease;
}
.stButton > button:hover { border-color: var(--ink); background: var(--ink-soft); color: var(--head); }
.hint { font-size: 0.78rem; font-weight: 700; letter-spacing: 0.12em; color: var(--muted); margin: 1.6rem 0 0.5rem 0; text-transform: uppercase; }

/* ---------- Verdict (deck class cards) ---------- */
.verdict {
    display: grid; grid-template-columns: auto 1fr; gap: 1.4rem; align-items: center;
    margin-top: 1.8rem; padding: 1.6rem 1.9rem;
    border-radius: 24px; border-left: 14px solid;
}
.verdict.bad { border-color: var(--bad); background: var(--bad-soft); }
.verdict.good { border-color: var(--good); background: var(--good-soft); }
.stamp {
    width: 76px; height: 76px; border-radius: 50%; border: 3px solid; display: grid; place-items: center;
    font-size: 2rem; transform: rotate(-8deg); background: var(--surface);
}
.bad .stamp { border-color: var(--bad); }
.good .stamp { border-color: var(--good); }
.verdict h2 {
    font-size: 1.9rem; font-weight: 800; letter-spacing: -0.01em; margin: 0 0 0.25rem 0; padding: 0;
}
.bad h2 { color: var(--bad); }
.good h2 { color: var(--good); }
.verdict p { margin: 0; color: var(--muted); line-height: 1.5; }
@media (max-width: 560px) { .verdict { grid-template-columns: 1fr; } }

/* ---------- Gauge ---------- */
.gauge { margin: 1.4rem 0 0.6rem 0; padding: 1.3rem 1.6rem 1.1rem; border: 2px solid var(--line); border-radius: 24px; background: var(--surface); }
.gauge-top { display: flex; justify-content: space-between; font-size: 0.88rem; font-weight: 500; color: var(--muted); margin-bottom: 1rem; }
.track {
    position: relative; height: 14px; border-radius: 7px;
    background: linear-gradient(90deg, #2E9E74 0%, #F5C84B 50%, #C62828 100%);
}
.pin {
    position: absolute; top: -8px; width: 5px; height: 30px; margin-left: -2px; border-radius: 3px;
    background: var(--head); box-shadow: 0 0 0 3px var(--surface);
}
.tick { position: absolute; top: -6px; height: 26px; border-left: 3px dashed var(--bad); }
.gauge-legend { display: flex; flex-wrap: wrap; gap: 0.4rem 1.6rem; margin-top: 1.2rem; font-size: 0.86rem; color: var(--muted); }
.gauge-legend b { color: var(--head); font-weight: 700; }

[data-testid="stMetric"] { background: var(--surface); border: 2px solid var(--line); border-top: 8px solid var(--ink); border-radius: 20px; padding: 0.9rem 1.2rem 1rem; }
[data-testid="stMetricLabel"] p { font-size: 0.9rem; font-weight: 500; color: var(--muted); }
[data-testid="stMetricValue"] { font-weight: 800; color: var(--head); }

/* ---------- How it works (deck cards) ---------- */
.steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 2.6rem; }
.step { background: var(--surface); border: 2px solid var(--line); border-top: 8px solid var(--ink); border-radius: 20px; padding: 1.2rem 1.4rem 1.3rem; }
.step:nth-child(2) { border-top-color: var(--red); }
.step b { font-size: 1.1rem; font-weight: 700; color: var(--head); display: flex; align-items: center; gap: 0.7rem; margin-bottom: 0.5rem; }
.step span { font-size: 0.95rem; line-height: 1.5; color: var(--muted); }
.step em {
    font-style: normal; font-weight: 700; font-size: 0.95rem; color: #fff;
    background: var(--red); width: 1.9rem; height: 1.9rem; border-radius: 50%;
    display: inline-grid; place-items: center; flex: none;
}
@media (max-width: 700px) { .steps { grid-template-columns: 1fr; } }

/* ---------- Sidebar (deep green, like the dark slides) ---------- */
[data-testid="stSidebar"] { background: #08402E; border-right: 6px solid var(--red); }
[data-testid="stSidebar"] * { color: #F3F8F5; }
[data-testid="stSidebar"] [data-testid="stImage"] img { background: #FFFFFF; border-radius: 20px; padding: 10px 14px; margin-bottom: 0.6rem; }
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #BFDCCB !important; }
.dev {
    border: 2px solid #2E9E74; border-radius: 20px; padding: 1.1rem 1.2rem; margin-bottom: 1rem; background: #0F5A41;
}
.dev-name { font-weight: 700; font-size: 1.08rem; margin: 0; color: #FFF6F4 !important; }
.dev-role { font-size: 0.84rem; color: #BFDCCB !important; margin-bottom: 0.7rem; }
.dev a { display: block; font-size: 0.9rem; font-weight: 600; text-decoration: none; padding: 0.15rem 0; color: #9FE0C2 !important; }
.dev a:hover { text-decoration: underline; }

.foot { text-align: center; color: var(--muted); font-size: 0.85rem; padding: 2rem 0 0.5rem; margin-top: 2.4rem; border-top: 2px solid var(--line); }
.foot a { color: var(--ink); text-decoration: none; font-weight: 700; }

@media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
"""
)


# ==========================================
# Theme
# ==========================================
st.session_state.setdefault("theme", "Light")
_theme = st.session_state.get("theme", "Light")

if _theme == "Dark":
    html(
        """
        <style>
        :root {
            --bg: #08402E;
            --surface: #0F5A41;
            --mint: #0C4D37;
            --line: #2A7F60;
            --text: #F3F8F5;
            --head: #F3F8F5;
            --muted: #BFDCCB;
            --ink: #6FD3A8;
            --ink-soft: rgba(111, 211, 168, 0.18);
            --bad: #FF9C90;
            --bad-soft: rgba(255, 156, 144, 0.16);
            --good: #6FD3A8;
            --good-soft: rgba(111, 211, 168, 0.16);
            color-scheme: dark;
        }
        [data-testid="stSidebar"] { background: #062F22; }
        .dev { background: #08402E; }
        .stTextArea textarea, div[data-baseweb="input"] > div, div[data-baseweb="base-input"] > input {
            background: rgba(0, 0, 0, 0.22) !important;
            color: #F3F8F5 !important;
        }
        [data-testid="stMain"] p, [data-testid="stMain"] label, [data-testid="stMain"] li,
        [data-testid="stMetricLabel"] p, [data-testid="stMetricValue"] {
            color: inherit;
        }
        .stCaption, [data-testid="stCaptionContainer"] { color: var(--muted) !important; }
        .stButton > button { color: #F3F8F5; }
        .stButton > button:hover { color: #F3F8F5; }
        </style>
        """
    )
else:
    html(
        """
        <style>
        :root { color-scheme: light; }
        .stTextArea textarea, div[data-baseweb="input"] > div, div[data-baseweb="base-input"] > input {
            background: #FFFFFF !important;
            color: #0B2A20 !important;
            border-color: #CFE2D6 !important;
        }
        .stTextArea textarea::placeholder,
        div[data-baseweb="input"] input::placeholder,
        div[data-baseweb="base-input"] input::placeholder {
            color: #5f6f67 !important;
            opacity: 1 !important;
            -webkit-text-fill-color: #5f6f67 !important;
        }
        [data-testid="stMain"] p, [data-testid="stMain"] label, [data-testid="stMain"] li,
        [data-testid="stMetricLabel"] p {
            color: inherit;
        }
        .stCaption, [data-testid="stCaptionContainer"] { color: var(--muted) !important; }
        .stButton > button { color: #08402E; }
        </style>
        """
    )


# ==========================================
# Predictor cache
# ==========================================
@st.cache_resource(show_spinner="Loading the model...")
def get_predictor():
    try:
        token = st.secrets.get("HF_TOKEN")
    except Exception:
        token = None
    model_path = snapshot_download(repo_id=REPO_ID, repo_type="model", token=token)
    sys.path.insert(0, model_path)
    return importlib.import_module("predict")


def load_example(headline_text: str, opening_text: str) -> None:
    st.session_state["headline"] = headline_text
    st.session_state["opening"] = opening_text


# ==========================================
# Sidebar
# ==========================================
with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width="stretch")
    st.markdown("### HeadlineGuard BD")
    st.caption("Bangla clickbait screening")
    st.radio(
        "Appearance",
        ["Light", "Dark"],
        horizontal=True,
        key="theme",
        help="Switch between light and dark mode.",
    )
    html(
        """
        <div class="dev">
            <div class="dev-name">H. M. Ahsan Habib Kushal</div>
            <div class="dev-role">Developer and Contrastive Learning, NLP researcher</div>
            <a href="https://github.com/AhsanCS64" target="_blank">GitHub profile</a>
            <a href="https://github.com/AhsanCS64/HeadlineGuard_BD" target="_blank">Source code</a>
            <a href="https://huggingface.co/Archmage64/HeadlineguardBD" target="_blank">Hugging Face model</a>
            <a href="mailto:kushalahsan@gmail.com">kushalahsan@gmail.com</a>
        </div>
        """
    )
    st.markdown("#### About the model")
    st.markdown(
        "- Fine-tuned Transformer for Bangla\n"
        "- Two modes: headline only, or headline plus article opening\n"
        "- Repository: [`Archmage64/HeadlineguardBD`](https://huggingface.co/Archmage64/HeadlineguardBD)"
    )


# ==========================================
# Masthead
# ==========================================
_logo = logo_data_uri()
_logo_html = (
    f'<img class="mast-logo" src="{_logo}" alt="HeadlineGuard BD logo">'
    if _logo
    else ""
)
html(
    f"""
    <div class="mast">
        <div class="mast-top">
            <div class="mast-brand">
                {_logo_html}
                <span class="mast-tag">BANGLA CLICKBAIT DETECTION</span>
            </div>
            <div class="mast-status"><i></i>Model ready</div>
        </div>
        <h1>HeadlineGuard <span>BD</span></h1>
        <p>Check whether a Bangla news headline is clickbait. Add the first lines of the article for a more context-aware result.</p>
        <div class="chips"><span>BanglaBERT</span><span>TF-IDF + Linear SVM</span><span>Ensemble learning</span></div>
    </div>
    """
)

# ==========================================
# Input form
# ==========================================
st.session_state.setdefault("headline", "")
st.session_state.setdefault("opening", "")

with st.form("prediction_form"):
    html('<div class="section-title">Headline to check</div>')

    headline = st.text_area(
        "Bangla headline (বাংলা শিরোনাম) *",
        key="headline",
        height=100,
        placeholder="যেমন: নতুন শিক্ষাবর্ষের পাঠ্যবই বিতরণ শুরু...",
        help="Paste the Bengali news headline you want to check.",
    )
    opening = st.text_area(
        "Article opening, first 1–2 sentences (খবরের প্রথম ১–২টি বাক্য, ঐচ্ছিক)",
        key="opening",
        height=130,
        placeholder="খবরের প্রথম ১–২টি বাক্য এখানে পেস্ট করুন (ঐচ্ছিক, তবে ফলাফল আরও নির্ভরযোগ্য হয়)...",
        help="Optional. With the opening sentences, the model also checks the headline against the story.",
    )
    submitted = st.form_submit_button("Check headline", type="primary")

html('<div class="hint">No headline at hand? Try an example</div>')
cols = st.columns(len(EXAMPLES))
for i, (label, ex_headline, ex_opening) in enumerate(EXAMPLES):
    with cols[i]:
        st.button(
            label,
            key=f"example_{i}",
            on_click=load_example,
            args=(ex_headline, ex_opening),
            width="stretch",
        )

# ==========================================
# Results
# ==========================================
if submitted:
    if not headline.strip():
        st.error("Enter a Bangla headline to check (অনুগ্রহ করে একটি শিরোনাম দিন)।")
    else:
        try:
            predictor = get_predictor()
            result = predictor.predict(headline.strip(), opening.strip() if opening else "")

            route = "Headline + opening" if result.get("mode") == "lead" else "Headline only"
            raw_label = str(result.get("label", ""))
            score = float(result.get("score", 0.0))
            threshold = float(result.get("threshold", 0.5))
            label_lower = raw_label.lower()

            is_clickbait = (
                "clickbait" in label_lower and "non" not in label_lower and "not" not in label_lower
            ) or (score >= threshold and "non" not in label_lower)

            safe_label = _html.escape(raw_label)
            if is_clickbait:
                html(
                    f"""
                    <div class="verdict bad">
                        <div class="stamp">🚨</div>
                        <div>
                            <h2>{safe_label}</h2>
                            <p>This text uses patterns common in clickbait or sensational framing.</p>
                        </div>
                    </div>
                    """
                )
            else:
                html(
                    f"""
                    <div class="verdict good">
                        <div class="stamp">✅</div>
                        <div>
                            <h2>{safe_label}</h2>
                            <p>This text reads like standard, informative news reporting.</p>
                        </div>
                    </div>
                    """
                )

            # Gauge: only drawn when score and threshold sit on a 0–1 scale
            if 0.0 <= score <= 1.0 and 0.0 <= threshold <= 1.0:
                html(
                    f"""
                    <div class="gauge">
                        <div class="gauge-top"><span>Less clickbait-like</span><span>More clickbait-like</span></div>
                        <div class="track">
                            <div class="tick" style="left:{threshold * 100:.1f}%"></div>
                            <div class="pin" style="left:{score * 100:.1f}%"></div>
                        </div>
                        <div class="gauge-legend">
                            <span>Solid marker: <b>score {score:.3f}</b></span>
                            <span>Dashed line: <b>decision threshold {threshold:.3f}</b></span>
                        </div>
                    </div>
                    """
                )

            c1, c2, c3 = st.columns(3)
            c1.metric("Model score", f"{score:.4f}")
            c2.metric("Decision threshold", f"{threshold:.4f}")
            c3.metric("Mode used", route)

            st.caption(
                "The score is measured against the decision threshold. It is not necessarily a calibrated probability."
            )

        except Exception:
            import traceback

            traceback.print_exc()
            st.error("The check failed. Open the app logs for details, then try again.")

# ==========================================
# How it works + footer
# ==========================================
html(
    """
    <div class="steps">
        <div class="step"><b><em>1</em>Paste the headline</b><span>Use any Bangla news headline. It is required.</span></div>
        <div class="step"><b><em>2</em>Add the opening</b><span>Optional. The first one or two sentences let the model compare headline and story.</span></div>
        <div class="step"><b><em>3</em>Read the verdict</b><span>See the label and where the score falls against the decision threshold.</span></div>
    </div>
    <div class="foot">
        Built by <a href="https://github.com/AhsanCS64" target="_blank">H. M. Ahsan Habib Kushal</a>
        &nbsp;|&nbsp; HeadlineGuard BD &copy; 2026
    </div>
    """
)