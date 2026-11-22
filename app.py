import html as _html
import importlib
import sys

import streamlit as st
from huggingface_hub import snapshot_download

# ==========================================
# Page configuration
# ==========================================
st.set_page_config(
    page_title="HeadlineGuard BD | Bangla Clickbait Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

REPO_ID = "Archmage64/HeadlineguardBD"

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


# ==========================================
# Styles (theme-safe: tinted transparency, works in light and dark)
# ==========================================
html(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Hind+Siliguri:wght@400;500;600;700&display=swap');

:root {
    --ink: #3b4cca;
    --ink-soft: rgba(59, 76, 202, 0.10);
    --bad: #e5484d;
    --bad-soft: rgba(229, 72, 77, 0.10);
    --good: #12a594;
    --good-soft: rgba(18, 165, 148, 0.10);
    --line: rgba(128, 128, 128, 0.28);
    --surface: rgba(128, 128, 128, 0.07);
    --muted: rgba(128, 128, 128, 0.95);
}

.stApp, .stMarkdown, .stTextArea textarea, .stButton button, label, p {
    font-family: 'Hind Siliguri', 'Bricolage Grotesque', system-ui, sans-serif;
}
.block-container { max-width: 1080px; padding-top: 2.2rem; padding-bottom: 3rem; }
header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }

/* ---------- Masthead ---------- */
.mast {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 2rem;
    align-items: end;
    padding-bottom: 1.6rem;
    margin-bottom: 1.8rem;
    border-bottom: 2px solid var(--ink);
}
.mast h1 {
    font-family: 'Bricolage Grotesque', 'Hind Siliguri', sans-serif;
    font-weight: 800;
    font-size: clamp(2.2rem, 5vw, 3.6rem);
    line-height: 1.02;
    letter-spacing: -0.03em;
    margin: 0 0 0.7rem 0;
    padding: 0;
}
.mast p { margin: 0; max-width: 34rem; font-size: 1.08rem; line-height: 1.55; color: var(--muted); }
.mast-status {
    display: inline-flex; align-items: center; gap: 0.5rem;
    border: 1px solid var(--line); border-radius: 999px;
    padding: 0.35rem 0.85rem; font-size: 0.85rem; font-weight: 500; white-space: nowrap;
}
.mast-status i { width: 8px; height: 8px; border-radius: 50%; background: var(--good); display: inline-block; }
@media (max-width: 700px) { .mast { grid-template-columns: 1fr; } }

/* ---------- Form ---------- */
[data-testid="stForm"] {
    border: 1.5px solid var(--line);
    border-radius: 6px;
    background: var(--surface);
    padding: 1.6rem 1.8rem 1.4rem;
}
.section-title {
    font-family: 'Bricolage Grotesque', sans-serif;
    font-size: 1.15rem; font-weight: 700; margin: 0 0 0.9rem 0;
}
.stTextArea textarea {
    border-radius: 4px;
    border: 1.5px solid var(--line);
    font-size: 1.08rem; line-height: 1.65;
}
.stTextArea textarea:focus { border-color: var(--ink); box-shadow: 0 0 0 3px var(--ink-soft); }
.stTextArea label p { font-weight: 600; font-size: 0.95rem; }

div[data-testid="stFormSubmitButton"] > button {
    background: var(--ink); color: #fff; border: none; border-radius: 4px;
    font-weight: 600; font-size: 1.02rem; padding: 0.6rem 1.8rem;
    transition: background 0.15s ease, transform 0.15s ease;
}
div[data-testid="stFormSubmitButton"] > button:hover { background: #2f3eb0; color: #fff; transform: translateY(-1px); }
div[data-testid="stFormSubmitButton"] > button:focus-visible { outline: 3px solid var(--ink-soft); outline-offset: 2px; }

/* Example buttons */
.stButton > button {
    border-radius: 4px; border: 1.5px dashed var(--line); background: transparent;
    font-size: 0.92rem; font-weight: 500; transition: border-color 0.15s ease, background 0.15s ease;
}
.stButton > button:hover { border-style: solid; border-color: var(--ink); background: var(--ink-soft); color: inherit; }
.hint { font-size: 0.9rem; color: var(--muted); margin: 1.1rem 0 0.4rem 0; }

/* ---------- Verdict ---------- */
.verdict {
    display: grid; grid-template-columns: auto 1fr; gap: 1.4rem; align-items: center;
    margin-top: 1.8rem; padding: 1.5rem 1.7rem;
    border: 1.5px solid; border-radius: 6px;
}
.verdict.bad { border-color: var(--bad); background: var(--bad-soft); }
.verdict.good { border-color: var(--good); background: var(--good-soft); }
.stamp {
    width: 76px; height: 76px; border-radius: 50%; border: 3px double; display: grid; place-items: center;
    font-size: 2rem; transform: rotate(-8deg);
}
.bad .stamp { border-color: var(--bad); }
.good .stamp { border-color: var(--good); }
.verdict h2 {
    font-family: 'Bricolage Grotesque', 'Hind Siliguri', sans-serif;
    font-size: 1.7rem; font-weight: 800; letter-spacing: -0.02em; margin: 0 0 0.25rem 0; padding: 0;
}
.bad h2 { color: var(--bad); }
.good h2 { color: var(--good); }
.verdict p { margin: 0; color: var(--muted); line-height: 1.5; }
@media (max-width: 560px) { .verdict { grid-template-columns: 1fr; } }

/* ---------- Gauge ---------- */
.gauge { margin: 1.4rem 0 0.4rem 0; padding: 1.2rem 1.5rem 1rem; border: 1px solid var(--line); border-radius: 6px; }
.gauge-top { display: flex; justify-content: space-between; font-size: 0.88rem; color: var(--muted); margin-bottom: 0.9rem; }
.track {
    position: relative; height: 12px; border-radius: 6px;
    background: linear-gradient(90deg, var(--good) 0%, #f5b942 50%, var(--bad) 100%);
}
.pin {
    position: absolute; top: -7px; width: 4px; height: 26px; margin-left: -2px; border-radius: 2px;
    background: currentColor; box-shadow: 0 0 0 3px rgba(128,128,128,0.25);
}
.tick { position: absolute; top: -5px; height: 22px; border-left: 2px dashed currentColor; opacity: 0.55; }
.gauge-legend { display: flex; gap: 1.4rem; margin-top: 1.1rem; font-size: 0.86rem; color: var(--muted); }
.gauge-legend b { color: inherit; font-weight: 600; }

[data-testid="stMetric"] { border: 1px solid var(--line); border-radius: 6px; padding: 0.9rem 1.1rem; }
[data-testid="stMetricLabel"] p { font-size: 0.85rem; color: var(--muted); }

/* ---------- How it works ---------- */
.steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; margin-top: 2.6rem; border-top: 1px solid var(--line); }
.step { padding: 1.3rem 1.4rem 0.4rem 0; }
.step + .step { padding-left: 1.4rem; border-left: 1px solid var(--line); }
.step b { font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.02rem; display: block; margin-bottom: 0.3rem; }
.step span { font-size: 0.93rem; line-height: 1.5; color: var(--muted); }
.step em { font-style: normal; color: var(--ink); font-weight: 700; margin-right: 0.4rem; }
@media (max-width: 700px) {
    .steps { grid-template-columns: 1fr; }
    .step + .step { border-left: none; padding-left: 0; border-top: 1px solid var(--line); }
}

/* ---------- Sidebar ---------- */
.dev {
    border: 1px solid var(--line); border-radius: 6px; padding: 1rem 1.1rem; margin-bottom: 1rem; background: var(--surface);
}
.dev-name { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 1.05rem; margin: 0; }
.dev-role { font-size: 0.82rem; color: var(--muted); margin-bottom: 0.7rem; }
.dev a { display: block; font-size: 0.88rem; font-weight: 500; text-decoration: none; padding: 0.15rem 0; color: var(--ink); }
.dev a:hover { text-decoration: underline; }

.foot { text-align: center; color: var(--muted); font-size: 0.85rem; padding: 2rem 0 0.5rem; margin-top: 2.4rem; border-top: 1px solid var(--line); }
.foot a { color: var(--ink); text-decoration: none; font-weight: 600; }

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
            --ink: #8b96ff;
            --ink-soft: rgba(139, 150, 255, 0.16);
            --bad: #ff6b73;
            --bad-soft: rgba(255, 107, 115, 0.14);
            --good: #2dd4bf;
            --good-soft: rgba(45, 212, 191, 0.14);
            --line: rgba(255, 255, 255, 0.16);
            --surface: rgba(255, 255, 255, 0.05);
            --muted: rgba(236, 238, 242, 0.72);
            color-scheme: dark;
        }
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            background: #16181d;
            color: #eceef2;
        }
        [data-testid="stSidebar"] {
            background: #1e2128;
            border-right: 1px solid var(--line);
        }
        [data-testid="stSidebar"] * { color: inherit; }
        .stTextArea textarea, div[data-baseweb="input"] > div, div[data-baseweb="base-input"] > input {
            background: rgba(255,255,255,0.04) !important;
            color: #eceef2 !important;
        }
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] p, .stMarkdown, p, label, span, h1, h2, h3 {
            color: inherit;
        }
        div[data-testid="stFormSubmitButton"] > button:hover { background: #7480ff; color: #fff; }
        .stButton > button { color: #eceef2; }
        </style>
        """
    )
else:
    html(
        """
        <style>
        :root {
            --ink: #3b4cca;
            --ink-soft: rgba(59, 76, 202, 0.10);
            --bad: #e5484d;
            --bad-soft: rgba(229, 72, 77, 0.10);
            --good: #12a594;
            --good-soft: rgba(18, 165, 148, 0.10);
            --line: rgba(128, 128, 128, 0.28);
            --surface: rgba(128, 128, 128, 0.07);
            --muted: rgba(90, 90, 90, 0.95);
            color-scheme: light;
        }
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            background: #ffffff;
            color: #1a1c22;
        }
        [data-testid="stSidebar"] {
            background: #f7f8fb;
            border-right: 1px solid var(--line);
        }
        div[data-testid="stFormSubmitButton"] > button:hover { background: #2f3eb0; color: #fff; }
        </style>
        """
    )


# ==========================================
# Predictor cache
# ==========================================
@st.cache_resource(show_spinner="Loading the model...")
def get_predictor():
    token = st.secrets["HF_TOKEN"] if "HF_TOKEN" in st.secrets else None
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
    st.markdown("### 🛡️ HeadlineGuard BD")
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
html(
    """
    <div class="mast">
        <div>
            <h1>🛡️ HeadlineGuard BD</h1>
            <p>Check whether a Bangla news headline is clickbait. Add the first lines of the article for a more context-aware result.</p>
        </div>
        <div class="mast-status"><i></i>Model ready</div>
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

html('<div class="hint">No headline at hand? Try an example:</div>')
cols = st.columns(len(EXAMPLES))
for i, (label, ex_headline, ex_opening) in enumerate(EXAMPLES):
    with cols[i]:
        st.button(
            label,
            key=f"example_{i}",
            on_click=load_example,
            args=(ex_headline, ex_opening),
            use_container_width=True,
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