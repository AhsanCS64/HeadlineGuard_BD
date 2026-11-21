import importlib
import sys

import streamlit as st
from huggingface_hub import snapshot_download

REPO_ID = "Archmage64/HeadlineguardBD"


@st.cache_resource(show_spinner="Connecting to the model repository...")
def get_predictor():
    # For a private model repo, add HF_TOKEN in Streamlit Secrets.
    # Public model repos can be downloaded without a token.
    token = st.secrets["HF_TOKEN"] if "HF_TOKEN" in st.secrets else None

    model_path = snapshot_download(
        repo_id=REPO_ID,
        repo_type="model",
        token=token,
    )

    sys.path.insert(0, model_path)
    return importlib.import_module("predict")


st.title("HeadlineGuard BD")
st.write("Bangla clickbait screening from a headline and optional article opening.")

with st.form("prediction_form"):
    headline = st.text_area(
        "Bangla headline (required)",
        placeholder="নতুন শিক্ষাবর্ষের পাঠ্যবই বিতরণ শুরু",
    )
    opening = st.text_area(
        "Article opening (first 1–2 sentences, optional)",
        placeholder="Paste the article's opening here.",
    )
    submitted = st.form_submit_button("Analyze")

if submitted:
    if not headline.strip():
        st.error("Enter a Bangla headline.")
    else:
        try:
            predictor = get_predictor()
            result = predictor.predict(headline, opening)

            route = (
                "Headline + article opening"
                if result["mode"] == "lead"
                else "Headline only"
            )

            st.subheader(result["label"])
            st.write("Model used:", route)
            st.metric("Model score", f'{result["score"]:.4f}')
            st.write("Decision threshold:", result["threshold"])
            st.caption(
                "The score is a model score, not necessarily a calibrated probability."
            )
        except Exception:
            import traceback
            traceback.print_exc()
            st.error("Prediction failed. Check the app logs for details.")
