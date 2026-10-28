# SmartHealthCare AI

SmartHealthCare AI is a Streamlit project that brings together four educational health tools: symptom based disease prediction, medicine similarity recommendations, heart risk assessment, and a medical information assistant.

The project is maintained by **Ayan**.

> **Medical notice:** This project is for education and research. Its predictions and generated responses are not diagnoses, treatment plans, or a substitute for a qualified healthcare professional.

## What’s included

- **Symptom exploration** — enter symptoms to view model generated disease predictions and related health information.
- **Medicine similarity** — browse medicine entries and find items with similar descriptions.
- **Heart risk assessment** — explore a risk estimate and related factors using the included model and data.
- **Medibot** — ask health information questions with retrieval augmented generation over local reference documents. Groq is used for model inference.
- **Local assets** — datasets, trained model files, reference PDFs, and example scan images are included in the project.

These features are experimental. Their results depend on the included datasets and models and have not been established as clinically validated tools.

## Run locally

Use Python 3.11.9, which is recorded in `runtime.txt`.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run home.py
```

### macOS or Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run home.py
```

Streamlit prints a local URL after the server starts. Keep the working directory at the project root so the app can find its data and model files.

## Medibot configuration

Set a Groq API key in the environment before starting the app to enable Medibot:

```powershell
$env:GROQ_API_KEY = "your-groq-api-key"
streamlit run home.py
```

```bash
export GROQ_API_KEY="your-groq-api-key"
streamlit run home.py
```

Without this key, the Medibot page reports that the service is unavailable. Do not commit API keys to the repository.

## Project layout

```text
home.py                                        Streamlit landing page
pages/                                         Four-page app modules
theme_config.py                                Shared theme and navigation styles
data/                                          CSV datasets and Medibot PDF sources
models/                                        Serialized model and similarity artifacts
vectorstore/db_faiss/                          FAISS index used by Medibot
demo/                                          Example scan images and instructions
medibot/                                       Helpers for building the reference index
heart_disease_risk_assessment/                 Model exploration notebooks
```

## Data and model files

The app loads files from these project directories:

- `data/Disease-Prediction-and-Medical dataset/`
- `data/Drug reccomendation/`
- `data/medibot data/`
- `models/first_feature_models/`
- `models/second_feature_models/`
- `models/third_feature_models/`
- `vectorstore/db_faiss/`

Keep these paths intact when moving or deploying the app. Some Medibot workflows also use Hugging Face credentials to rebuild the vector index; the included index is provided for local retrieval.

## Ownership and license

Copyright © 2026 Ayan. This project is released under the MIT License; see [LICENSE](LICENSE) for the license text.

## Contributing

Keep changes compatible with Python 3.11 and the existing Streamlit multipage structure. Do not include API keys, private health information, or unlicensed data in contributions.
