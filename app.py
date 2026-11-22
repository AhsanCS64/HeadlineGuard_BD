import importlib
import sys
import streamlit as st
from huggingface_hub import snapshot_download

# ==========================================
# Page Configuration
# ==========================================
st.set_page_config(
    page_title="HeadlineGuard BD | Bangla Clickbait Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# Custom CSS for Modern, Professional Design
# ==========================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Hind Siliguri', sans-serif;
    }

    /* Top App Header */
    .app-header {
        padding: 1.2rem 0 1.8rem 0;
        border-bottom: 1px solid rgba(148, 163, 184, 0.2);
        margin-bottom: 2rem;
    }
    .app-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        color: #1d4ed8;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.3rem 0.75rem;
        border-radius: 9999px;
        margin-bottom: 0.6rem;
    }
    .app-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: var(--text-color, #0f172a);
        margin: 0 0 0.4rem 0;
    }
    .app-subtitle {
        font-size: 1rem;
        color: #64748b;
        margin: 0;
        max-width: 750px;
        line-height: 1.5;
    }

    /* Styled Form Container */
    [data-testid="stForm"] {
        background: rgba(248, 250, 252, 0.7);
        border: 1.5px solid #e2e8f0;
        border-radius: 16px;
        padding: 2rem 2.2rem;
        box-shadow: 0 4px 15px -3px rgba(0, 0, 0, 0.04);
        transition: all 0.2s ease;
    }
    [data-testid="stForm"]:hover {
        border-color: #cbd5e1;
    }

    /* Form Header */
    .form-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 1.2rem;
    }
    .form-header h3 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--text-color, #0f172a);
    }
    .form-header span {
        font-size: 0.82rem;
        color: #64748b;
    }

    /* Textareas and Inputs */
    .stTextArea textarea {
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        font-family: 'Hind Siliguri', 'Plus Jakarta Sans', sans-serif;
        font-size: 1rem;
        line-height: 1.6;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .stTextArea textarea:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
    }

    /* Submit Button */
    div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
        color: #ffffff;
        font-weight: 600;
        font-size: 1rem;
        border-radius: 10px;
        padding: 0.65rem 2rem;
        border: none;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
    }

    /* Results Card */
    .result-box {
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-top: 1.6rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .result-clickbait {
        background: rgba(239, 68, 68, 0.07);
        border: 1.5px solid #fca5a5;
        border-left: 6px solid #ef4444;
    }
    .result-legit {
        background: rgba(16, 185, 129, 0.07);
        border: 1.5px solid #86efac;
        border-left: 6px solid #10b981;
    }
    .result-label {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    .result-clickbait .result-label { color: #dc2626; }
    .result-legit .result-label { color: #059669; }

    /* Developer Profile Card */
    .dev-card {
        background: rgba(241, 245, 249, 0.65);
        border: 1px solid #cbd5e1;
        border-radius: 12px;
        padding: 1.1rem;
        margin-bottom: 1.2rem;
    }
    .dev-name {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-color, #0f172a);
        margin: 0;
    }
    .dev-sub {
        font-size: 0.8rem;
        color: #64748b;
        margin-bottom: 0.8rem;
    }
    .dev-links a {
        display: inline-block;
        color: #2563eb;
        text-decoration: none;
        font-size: 0.85rem;
        font-weight: 500;
        margin-right: 0.8rem;
        margin-bottom: 0.3rem;
    }
    .dev-links a:hover {
        text-decoration: underline;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2.5rem 0 1.5rem 0;
        color: #94a3b8;
        font-size: 0.85rem;
        border-top: 1px solid rgba(148, 163, 184, 0.2);
        margin-top: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# Predictor Cache
# ==========================================
REPO_ID = "Archmage64/HeadlineguardBD"


@st.cache_resource(show_spinner="Connecting to the model repository...")
def get_predictor():
    token = st.secrets["HF_TOKEN"] if "HF_TOKEN" in st.secrets else None
    model_path = snapshot_download(
        repo_id=REPO_ID,
        repo_type="model",
        token=token,
    )
    sys.path.insert(0, model_path)
    return importlib.import_module("predict")


# ==========================================
# Sidebar: Developer & App Info
# ==========================================
with st.sidebar:
    st.markdown("### 🛡️ HeadlineGuard BD")
    st.caption("Bangla Clickbait Screening Engine")

    st.markdown("---")
    st.markdown("#### 👨‍💻 Developer")
    st.markdown(
        """
        <div class="dev-card">
            <div class="dev-name">H. M. Ahsan Habib</div>
            <div class="dev-sub">Developer & NLP Researcher</div>
            <div class="dev-links">
                <a href="https://github.com/AhsanCS64" target="_blank">🐙 GitHub Profile</a><br>
                <a href="https://github.com/AhsanCS64/HeadlineGuard_BD" target="_blank">📁 Source Code</a><br>
                <a href="https://huggingface.co/Archmage64/HeadlineguardBD" target="_blank">🤗 Hugging Face Model</a><br>
                <a href="mailto:kushalahsan@gmail.com">✉️ kushalahsan@gmail.com</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### ℹ️ System Details")
    st.markdown(
        """
        - **Model:** Fine-tuned Transformer for Bangla
        - **Repository:** [`Archmage64/HeadlineguardBD`](https://huggingface.co/Archmage64/HeadlineguardBD)
        - **Pipeline:** Dual-mode (Headline only or Headline + Lead opening)
        """
    )


# ==========================================
# Main Header
# ==========================================
st.markdown(
    """
    <div class="app-header">
        <div class="app-badge">Bangla NLP Verification</div>
        <h1 class="app-title">🛡️ HeadlineGuard BD</h1>
        <p class="app-subtitle">
            Bangla clickbait and sensationalism screening from a news headline and optional article opening.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# Polished Input Form
# ==========================================
with st.form("prediction_form"):
    st.markdown(
        """
        <div class="form-header">
            <h3>📰 Content Analysis Form</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    headline = st.text_area(
        "Bangla headline (বাংলা শিরোনাম) *",
        placeholder="যেমন: নতুন শিক্ষাবর্ষের পাঠ্যবই বিতরণ শুরু...",
        help="Paste the Bengali news headline you want to analyze.",
    )

    opening = st.text_area(
        "Article opening — first 1–2 sentences (খবরের প্রথম ১–২টি বাক্য, ঐচ্ছিক)",
        placeholder="খবরের প্রথম ১–২টি বাক্য এখানে পেস্ট করতে পারেন (ঐচ্ছিক হলেও কনটেক্সট যাচাইয়ে সহায়ক)...",
        help="Optional: Providing the opening sentences enables lead-contextual screening.",
    )

    submitted = st.form_submit_button("🔍 Analyze Content", type="primary")


# ==========================================
# Results Section
# ==========================================
if submitted:
    if not headline.strip():
        st.error("⚠️ Please enter a Bangla headline (অনুগ্রহ করে একটি শিরোনাম প্রদান করুন)।")
    else:
        try:
            predictor = get_predictor()
            result = predictor.predict(headline.strip(), opening.strip() if opening else "")

            route = (
                "Headline + article opening"
                if result.get("mode") == "lead"
                else "Headline only"
            )

            raw_label = str(result.get("label", ""))
            score = float(result.get("score", 0.0))
            threshold = float(result.get("threshold", 0.5))

            is_clickbait = (
                "clickbait" in raw_label.lower()
                and "non" not in raw_label.lower()
                and "not" not in raw_label.lower()
            ) or (score >= threshold and "non" not in raw_label.lower())

            # Status Banner
            if is_clickbait:
                st.markdown(
                    f"""
                    <div class="result-box result-clickbait">
                        <div class="result-label">🚨 {raw_label}</div>
                        <div>The analyzed text exhibits traits associated with clickbait or sensational framing.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="result-box result-legit">
                        <div class="result-label">✅ {raw_label}</div>
                        <div>The analyzed text appears to be standard, informative news reporting.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Model score", f"{score:.4f}")
            with col2:
                st.metric("Decision threshold", f"{threshold:.4f}")
            with col3:
                st.metric("Model pipeline", route)

            st.caption(
                "Note: The score is a model score relative to the decision threshold, not necessarily a calibrated probability."
            )

        except Exception:
            import traceback
            traceback.print_exc()
            st.error("Prediction failed. Check the app logs for details.")


# ==========================================
# Footer
# ==========================================
st.markdown(
    """
    <div class="footer">
        Developed by <strong><a href="https://github.com/AhsanCS64" style="color: #2563eb; text-decoration: none;" target="_blank">H. M. Ahsan Habib</a></strong>
        &nbsp;|&nbsp; HeadlineGuard BD &copy; 2026
    </div>
    """,
    unsafe_allow_html=True,
)
