# 🛡️ HeadlineGuard BD

**Bangla clickbait detection for news headlines.**

HeadlineGuard BD checks whether a Bangla news headline is clickbait or sensational. You can give it just the headline, or add the first one or two sentences of the article so the model can compare the headline against the story.

[![Model on Hugging Face](https://img.shields.io/badge/🤗%20Model-Archmage64%2FHeadlineguardBD-yellow)](https://huggingface.co/Archmage64/HeadlineguardBD)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-ff4b4b)

---

## Why this exists

Clickbait headlines hide the actual news behind curiosity gaps, exaggeration and emotional bait. Most clickbait tooling is built for English. HeadlineGuard BD is built for Bangla, so editors, researchers and readers can screen headlines in the language they are written in.

## Features

- **Two detection modes.** Headline only, or headline plus article opening (lead-aware).
- **Score against a threshold.** The app shows the model score, the decision threshold and a gauge, so you can see how close a result is to the line.
- **Bangla-first interface.** Bangla input fields with a fonts setup that renders Bangla text cleanly.
- **One-click examples.** Try sample headlines without needing your own.
- **Light and dark theme support.**
- **Model hosted on Hugging Face.** The app downloads the model on first run and caches it.

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/AhsanCS64/HeadlineGuard_BD.git
cd HeadlineGuard_BD
```

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

If you don't have a `requirements.txt` yet, the app itself needs `streamlit` and `huggingface_hub`. The model's own `predict.py` may need more, typically `torch` and `transformers`.

### 3. Run the app

```bash
streamlit run app.py
```

Open the local URL Streamlit prints (usually http://localhost:8501).

### Hugging Face token (optional)

The model is downloaded from [`Archmage64/HeadlineguardBD`](https://huggingface.co/Archmage64/HeadlineguardBD). If the repository is public, you don't need a token. If you use a private copy, add a token in `.streamlit/secrets.toml`:

```toml
HF_TOKEN = "hf_your_token_here"
```

Never commit this file. Add `.streamlit/secrets.toml` to your `.gitignore`.

## How to use the app

1. **Paste a Bangla headline.** This is required.
2. **Optionally paste the article opening.** The first one or two sentences are enough.
3. **Select "Check headline".** You get a label, the model score and the decision threshold.

> **Reading the score:** The score is measured against the decision threshold. It is not necessarily a calibrated probability, so don't read 0.80 as "80% likely to be clickbait."

### Example

| Input | Mode | What to expect |
|---|---|---|
| `নতুন শিক্ষাবর্ষে সারা দেশে বিনামূল্যে পাঠ্যবই বিতরণ শুরু` | Headline only | Standard news |
| `এই ভিডিও দেখলে আপনার চোখ কপালে উঠবে, যা ঘটল বিশ্বাস করতে পারবেন না!` | Headline only | Clickbait-like |

## Use the model in your own code

The model repository ships a `predict` module. The Streamlit app loads it like this:

```python
import importlib
import sys
from huggingface_hub import snapshot_download

model_path = snapshot_download(repo_id="Archmage64/HeadlineguardBD", repo_type="model")
sys.path.insert(0, model_path)
predictor = importlib.import_module("predict")

result = predictor.predict(
    "এই ভিডিও দেখলে আপনার চোখ কপালে উঠবে!",  # headline
    "",                                         # article opening (optional, "" for headline-only mode)
)
print(result)
```

`predict` returns a dictionary with these keys:

| Key | Meaning |
|---|---|
| `label` | The predicted class |
| `score` | The model score |
| `threshold` | The decision threshold the score is compared against |
| `mode` | `lead` when an article opening was used, otherwise headline-only |

## Project structure

```text
HeadlineGuard_BD/
├── app.py            # Streamlit web app
├── requirements.txt  # Python dependencies
└── README.md
```

The model weights and `predict.py` live in the [Hugging Face repository](https://huggingface.co/Archmage64/HeadlineguardBD), not in this repo.

## Deploy

The app works on [Streamlit Community Cloud](https://streamlit.io/cloud) and Hugging Face Spaces. Set `HF_TOKEN` in the platform's secrets settings only if your model repository is private.

## Limitations

- The model is trained for **Bangla** text. Other languages and mixed-language headlines may give unreliable results.
- Clickbait is subjective. Treat the result as a **screening aid**, not a final judgement. A human editor should make the call for anything important.
- Very short, very long or unusually formatted headlines may not score well.
- Satire, opinion and entertainment headlines can look sensational without being deceptive.

## Roadmap

- [ ] Add a live demo link
- [ ] Publish dataset and evaluation details
- [ ] Batch checking (CSV upload)
- [ ] Browser extension for news sites

## Contributing

Issues and pull requests are welcome. If you find a headline the model gets wrong, open an issue with the headline, the article opening if you have it, and what you expected.

## Author

**H. M. Ahsan Habib**, developer and NLP researcher

- GitHub: [@AhsanCS64](https://github.com/AhsanCS64)
- Model: [Archmage64/HeadlineguardBD](https://huggingface.co/Archmage64/HeadlineguardBD)
- Email: kushalahsan@gmail.com

## License

Add your license here (for example MIT) and include a `LICENSE` file in the repository.
