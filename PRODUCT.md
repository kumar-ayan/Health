# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

General users exploring health information for education. Students and researchers are also supported by the project’s stated research purpose.

## Product Purpose

SmartHealthCare AI brings four health-related tools into one Streamlit application: symptom-based disease estimates, medicine similarity, heart-risk assessment, and a medical information assistant. Success means visitors can find the relevant tool and understand its output and limitations.

## Positioning

The application combines local datasets and pretrained artifacts for symptom and heart-risk estimates, similarity-based medicine browsing, and retrieval-augmented health information. These tools are experimental and have not been established as clinically validated.

## Operating Context

The app runs as a multipage Streamlit application. Its CSV data, model artifacts, PDFs, and FAISS index are stored in the project. Medibot uses a Groq API key for inference; its retrieval sources are local PDFs and the included index.

## Capabilities and Constraints

- The landing page links to four feature pages.
- The symptom and heart-risk pages use included models and data.
- The medicine page browses a local medicine catalogue and similarity model.
- Medibot requires `GROQ_API_KEY` for model inference.
- This project is for education and research, not diagnosis or treatment.
- Python 3.11.9 and Streamlit 1.46.1 are recorded in the project files.
- Do not invent clinical validation, accuracy, privacy, or performance claims.

## Brand Commitments

Preserve the product name SmartHealthCare AI and owner attribution Ayan. No color, type, or visual system is pinned by the user; the requested direction for this redesign is calm clinical editorial.

## Evidence on Hand

- `data/Disease-Prediction-and-Medical dataset/` and `models/first_feature_models/`
- `data/Drug reccomendation/` and `models/second_feature_models/`
- `models/third_feature_models/`
- `data/medibot data/` and `vectorstore/db_faiss/`
- `demo/` example scan images

The project contains no clinical validation evidence or user testimonials.

## Product Principles

- Make the next useful tool easy to find.
- Describe model outputs as estimates, not diagnoses.
- Keep health information concise and easy to scan.
- Do not claim more privacy, accuracy, or clinical value than the project can prove.
