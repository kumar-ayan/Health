# SmartHealthCare AI — Project Details

This document describes the project as it exists in the repository: its application pages, datasets, serialized artifacts, notebook workflows, runtime behavior, and known limitations. Training methods and metrics below are attributed to the checked-in notebooks; they have not been independently reproduced.

## 1. Project summary

SmartHealthCare AI is a Python and Streamlit multipage application that combines four health-information tools:

1. Symptom-based disease estimates with related reference information.
2. Medicine catalogue browsing and content-similarity recommendations.
3. A heart-disease probability estimate, feature explanations, and health-related utilities.
4. Medibot, a retrieval-augmented health-information chat assistant.

The project is maintained by Ayan and released under the MIT License. It is described as an educational and research project, not a clinically validated product. The home page now presents the tools as an editorial index and states those limits before entry. The shared visual direction and palette are recorded in `DESIGN.md` and `theme_config.py`.

## 2. Architecture and runtime

- **Application framework:** Streamlit 1.46.1, with `home.py` as the landing page and four modules under `pages/`.
- **Language and runtime:** Python 3.11.9 is recorded in `runtime.txt`.
- **Data processing:** pandas and NumPy.
- **Classical ML:** scikit-learn, category-encoders, imbalanced-learn, LightGBM, and related libraries.
- **Similarity search:** scikit-learn vectorization and cosine similarity; FAISS is used for Medibot document retrieval.
- **Charts and reports:** Plotly and ReportLab.
- **Image handling:** Pillow; DICOM loading attempts to use pydicom.
- **LLM integration:** LangChain with Groq for the Streamlit Medibot page. Separate command-line helpers use Hugging Face endpoints.

The app expects to be run from the project root because its data, pickle, image, and FAISS paths are relative. It uses Streamlit session state for page navigation and transient state such as histories, watchlists, goals, chat messages, and assessment results. Streamlit caches selected file loads and model resources with `st.cache_data` and `st.cache_resource`.

### Install and run

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run home.py
```

Medibot requires a Groq API key in `GROQ_API_KEY` (environment or `.env`):

```powershell
$env:GROQ_API_KEY = "your-groq-api-key"
streamlit run home.py
```

Without that key, the Medibot page reports the missing key and stops. The separate Hugging Face command-line helpers require `HF_TOKEN`.

## 3. Application pages and user flows

### Home — `home.py`

The homepage links to the four application modules. It explains that the tools are experimental and educational, and puts supplemental reference material inside an expander. Its current role is orientation and navigation; many older section-rendering functions remain in the file but are not part of the active home-page call path.

### Symptom explorer — `pages/1_Disease-Prediction-and-medical-recommendation.py`

The page has internal routes for **Home, Diagnose, Library, Insights, History, and About**. It loads symptom data and the serialized Random Forest, accepts symptoms from a searchable multiselect or comma-separated text, and fuzzy-matches typed symptoms against known symptom names. A match score of 80 or higher is accepted.

The app builds a one-row, binary symptom feature vector, asks the model for class probabilities when available, then combines model scores with a separate disease-profile score. Disease descriptions, precaution lists, medication strings, diet strings, and workout suggestions are looked up from CSV files. The UI includes a session-local diagnosis history and summary/insight screens.

The profile score is hand-coded. For each disease, it measures severity-weighted coverage of entered symptoms, symptom precision, and the fraction of the disease profile matched; the components receive weights 72, 20, and 8. The final rank score is 78% profile score and 22% model score. A separate severity label uses a fixed list of severe symptoms and symptom-count thresholds. These calculations are application heuristics, not additional trained models.

### Medicine catalogue — `pages/2_drug_recommendation.py`

The internal routes are **Home, Recommend, Symptoms, Compare, Detail, Insights, Watchlist, Interactions, A-Z Browser, and Dosage**. At startup, the page loads `medicine_dict.pkl` and `similarity.joblib`, rebuilds a DataFrame, and constructs the name-to-row index used to look up similarity values. `medicine.csv` supplies descriptions and a reason-to-medicine mapping.

- **Recommendations:** select a medicine and rank other rows by the precomputed cosine-similarity matrix.
- **Symptom matching:** a static symptom-to-reason mapping is intersected with the CSV’s `Reason` field. The function is named `ai_drugs_for_symptoms`, but its code makes no model or API call; it is a deterministic lookup.
- **Compare/detail/insights/A–Z:** display catalogue entries, descriptions, and similarity relationships.
- **Watchlist:** stored in Streamlit session state.
- **Interactions:** calculates similarity percentages and labels pairs high (75%+), moderate (50%+), or low. This is text similarity, not pharmacological drug-interaction detection.
- **Dosage:** general reference content; it is not an individualized dose calculator.

Some entries link out to pharmacy/search websites. The app itself does not fulfill medicine orders.

### Heart health — `pages/3_heart_Disease_Risk_Assesment.py`

The page loads `best_model.pkl` and `cbe_encoder.pkl`, then presents **Assessment, Insights, Tools, Wellness, History, About, and Scan Studio** tabs.

- **Assessment:** collects demographics, health history, BMI category, healthcare access, smoking, activity, alcohol, sleep, and related categorical answers. The CatBoost encoder transforms the form record to the model’s feature representation. The app returns class-1 `predict_proba` multiplied by 100 and presents it as a percentage.
- **Insights:** risk gauge, feature drivers, comparisons, and related charts. The page attempts SHAP explanations using a tree explainer; if that fails, it falls back to model feature importances, and then to uniform values if neither produces usable data.
- **Recommendations and what-if tools:** combine feature/risk thresholds and hand-coded rules with the feature-importance output. These are application logic, not separately trained models.
- **Wellness and other tools:** includes a BMI utility, lifestyle summaries, quiz, goals, notes, and Q&A/reference content. Goals, notes, quizzes, and history are held in session state.
- **Reports:** exports assessment details as PDF and JSON.
- **Scan Studio:** Pillow/NumPy image transforms such as autocontrast/contrast boost, edge filtering, false-color conversion, sharpening, inversion, and percentile normalization. Uploads are reduced to a maximum 2048 px edge for the six enhancement previews to keep high-resolution images viewable and limit memory use; the page reports the original resolution when it resizes a preview. This is image processing only; no image-classification or diagnostic model is used. DICOM support imports `pydicom` dynamically, but pydicom is not pinned in `requirements.txt`.

### Medibot — `pages/4_Medibot.py`

Medibot provides **Chat, Symptom Checker, Medications, Health Score, and Saved Answers** tabs, plus topic shortcuts, suggested questions, search, export, clear-chat, bookmarks, and voice input. Chat messages and bookmarks are session state; the Streamlit page does not write them to a persistent chat-history file. The UI retains at most 12 messages.

The symptom checker, medication reminders, and health score are static rules, UI state, or quiz logic; they are not ML diagnoses or actual scheduled notifications. Voice transcription uses Groq’s `whisper-large-v3-turbo` endpoint when configured, and may fall back to the browser Web Speech API.

## 4. Models and inference details

### 4.1 Symptom disease classifier

**Runtime artifact:** `models/first_feature_models/RandomForest.pkl` (about 7.2 MB).

The disease notebook (`Disease Prediction and recommendation/disease_prediction_system.ipynb`) describes a multiclass workflow over `Training.csv`. It label-encodes `prognosis`, splits 70%/30% with `random_state=20`, and compares a linear SVC, a 100-tree Random Forest (`random_state=42`), and a 100-estimator Gradient Boosting classifier. It evaluates predictions with accuracy, confusion matrices, and a classification report. The notebook then fits and pickles a Random Forest as `RandomForest.pkl`.

The notebook also contains later experimental code for a stratified split, scaling, and grid-search parameters. The checked-in code does not establish that this later experiment produced or replaced the deployed pickle. One early notebook cell contains a `pd.read_` typo; a later cell uses `pd.read_csv`.

**Inference path:** all symptom features start at zero; accepted symptoms set matching columns to one. `predict_proba` is converted to percentage-like class scores. If probability prediction fails, the app falls back to `predict` and assigns the returned class 100%. The ranked result then combines that score with the hand-built symptom-profile score described above.

**Important label-mapping check:** the notebook describes `LabelEncoder`, while the runtime maps integer class labels through a separately hard-coded `MODEL_DISEASE_MAP`. No fitted label encoder is loaded with the model. The class-index correspondence should be verified against the serialized model before results are relied upon; a mismatch would display the wrong disease name.

The training CSV has 4,920 rows, 132 symptom columns, and a `prognosis` target. Its header contains a duplicated `fluid_overload` column; pandas normally renames a duplicate on read (for example, `fluid_overload.1`). The file contains 41 disease categories. The artifact’s exact internal parameters and class order have not been independently inspected in this environment.

### 4.2 Medicine similarity

**Runtime artifacts:** `models/second_feature_models/medicine_dict.pkl` (about 1.3 MB) and `similarity.joblib` (about 16.4 MB).

The medicine notebook (`Drug Recommendation/Drug_Recommendation.ipynb`) drops rows with missing values, tokenizes `Description` and `Reason`, combines them as `tags`, lowercases and Porter-stems the text, then applies `CountVectorizer(stop_words="english", max_features=5000)`. It computes pairwise cosine similarity over the resulting vectors and saves the catalogue dictionary and similarity matrix. This is unsupervised content similarity; there is no labeled training target or supervised recommendation model.

At runtime, the selected row is removed from its own recommendations, and the highest remaining matrix values are returned. Correct operation depends on the serialized dictionary’s row order matching the matrix’s row/column order. The included `medicine.csv` has 9,720 records and columns `index`, `Drug_Name`, `Reason`, and `Description`.

### 4.3 Heart disease classifier

**Runtime artifacts:** `models/third_feature_models/best_model.pkl` (about 4.6 MB) and `cbe_encoder.pkl` (about 8.7 KB). The repository also has `best_model1.pkl` and `cbe_encoder1.pkl`; the application does not load those alternate files.

The notebooks describe preprocessing the 2022 Behavioral Risk Factor Surveillance System (BRFSS) data and predicting the target `heart_disease`, derived from whether a respondent reported ever being diagnosed with angina or coronary heart disease. The resulting task is classification of a reported/recorded history label; it is not a prospective clinical event model.

The modeling notebook uses 22 categorical input features covering demographic, medical-history, healthcare-access, lifestyle, BMI, and sleep variables. It converts `yes` target values to 1, applies `CatBoostEncoder`, and uses an 80%/20% split with `random_state=1981`. Models compared include logistic regression, Random Forest, LightGBM, XGBoost, Balanced Bagging, Easy Ensemble, Balanced Random Forest, and ensemble variants with LightGBM. Logistic regression uses scaled features; tree/ensemble approaches use the encoded feature table.

The notebook selects an Easy Ensemble with LightGBM base estimator. It runs five Optuna trials over LightGBM hyperparameters, with three-fold cross-validation scoring recall. It then fits and saves the tuned ensemble and encoder. Notebook markdown records class imbalance of roughly 418.3k negative and 26.8k positive observations, and reports pre-tuning and tuned metrics. The recorded tuned class-1 values are approximately 0.197 precision, 0.813 recall, 0.317 F1, and 0.884 ROC AUC. These are notebook-reported figures, not independently reproduced validation results.

**Caveats in the training notebook:** the CatBoost encoder is fit to the full feature/target set before the train/test split, which can leak target information across the evaluation boundary. The split is not shown as stratified despite the severe imbalance. The preprocessing notebook imputes missing categorical responses using random draws from observed category distributions; the shown code does not consistently set a random seed. Treat notebook scores cautiously and retrain/evaluate with a leakage-safe pipeline before making performance claims.

At runtime, class 1 probability is multiplied by 100. The UI applies its own labels: over 25% is moderate, over 40% high, and over 70% very high (otherwise low). These cutoffs are code-defined display bands, not clinical thresholds. No probability calibration is shown. Low positive-class precision in the notebook means many positive model calls may be false positives.

### 4.4 Medibot language and embedding models

The Streamlit implementation loads the local FAISS store at `vectorstore/db_faiss/` using `sentence-transformers/all-MiniLM-L6-v2` embeddings on CPU, retrieves up to six documents, and calls Groq `llama-3.3-70b-versatile` with temperature 0.4 through LangChain `RetrievalQA` using a “stuff” document chain. The source files are `Current Essentials of Medicine.pdf` and `Webster_s New World Medical Dictionary (1).pdf`. The repository includes `index.faiss` and `index.pkl` for retrieval.

The app manually prepends a recent user topic for a limited set of pronoun-led follow-up questions; the active Streamlit QA prompt does not pass a full conversational transcript to the LLM. The response prompt says to use retrieved text as support while also drawing on general model knowledge, and explicitly says not to diagnose personally. Sources are displayed from retrieved-document metadata. The displayed confidence badge is a UI heuristic, not a calibrated probability of answer correctness.

`medibot/create_memory_for_llm.py` and `medibot/connect_memory_with_llm.py` are separate command-line examples using Hugging Face’s `mistralai/Mistral-7B-Instruct-v0.3` endpoint and the same MiniLM embeddings. One helper stores up to 12 messages in `medibot_chat_history.json`; the other holds a shorter in-memory history. Neither file contains the build step that creates the checked-in FAISS index. The helper implementations should not be confused with the Streamlit page’s Groq model.

## 5. Data and other assets

| Path | Contents and observed size |
|---|---|
| `data/Disease-Prediction-and-Medical dataset/Training.csv` | 4,920 rows; binary symptom indicators and prognosis target; duplicate `fluid_overload` header. |
| `symptoms_df.csv` | 4,920 rows; disease plus four symptom fields and an unnamed index column. |
| `Symptom-severity.csv` | 133 symptom/weight rows; used for profile scoring and symptom insights. |
| `description.csv` | 41 disease descriptions. |
| `precautions_df.csv` | 41 disease rows with four precaution fields. |
| `medications.csv` | 41 disease rows with medication-list strings. |
| `diets.csv` | 41 disease rows with diet-list strings. |
| `workout_df.csv` | 410 disease/workout rows. |
| `data/Drug reccomendation/medicine.csv` | 9,720 catalogue records, including drug name, reason, and description. |
| `models/third_feature_models/brfss2022_data_wrangling_output.zip` | ZIP containing `brfss2022_data_wrangling_output.csv`, about 445,132 data rows. The heart page itself loads model/encoder artifacts, not this ZIP. |
| `data/medibot data/` | Two medical reference PDFs used as the documented source corpus for the included vector store. |
| `demo/` | CT, echocardiogram, MRI, and X-ray sample images plus Scan Studio instructions. These are examples, not model inputs for a scan classifier. |
| `utils/` | Logos, icons, and page artwork (`home2.png`, `medss.png`, `hri.png`, `dpi.png`, `dri.png`, `mbi.png`, variants, and CSS files). |

The heart-data notebook refers to a raw `brfss2022.csv` and a column-label table during preprocessing; those raw inputs are not listed in the repository. The ZIP contains the preprocessed output. The app’s disease and medicine modules use the CSV datasets directly.

## 6. Notebooks and reproducibility

- `Disease Prediction and recommendation/disease_prediction_system.ipynb`: disease data loading, label encoding, baseline model comparisons, Random Forest serialization, and sample predictions.
- `Drug Recommendation/Drug_Recommendation.ipynb`: text-tag preparation, stemming/vectorization, cosine-similarity construction, and artifact serialization.
- `heart_disease_risk_assessment/Data_Wrangling_pre_processing_notebook.ipynb`: BRFSS column renaming, selection, recoding, missing-value imputation, category creation, and CSV export.
- `heart_disease_risk_assessment/Exploratory_data_analysis.ipynb`: exploratory analysis, feature work, CatBoost encoding, and train/test setup.
- `heart_disease_risk_assessment/Modeling.ipynb`: model comparison, imbalance-handling ensembles, Optuna search, metric reporting, SHAP, and model/encoder export.

The notebooks include cloud/Colab-style paths and refer to data files not all present in the repository. Reproducing a pickle requires matching feature order, target encoding, data preparation, dependency versions, and random seeds. Pickle/joblib files are Python-version/library-sensitive. The repository contains no dedicated automated unit-test suite; `test_token.py` is a credential-check helper, not an application test.

## 7. Dependencies and configuration

`requirements.txt` pins the runtime stack, including Streamlit, pandas, NumPy, scikit-learn, category-encoders, imbalanced-learn, LightGBM, SHAP, LangChain integrations, FAISS CPU, sentence-transformers, Groq, Plotly, Pillow, and ReportLab. `constraints.txt` currently contains only a NetworkX constraint. The notebooks also import tools such as Optuna and XGBoost; those are not both explicitly pinned in the checked-in requirements file. `pydicom` is imported only when DICOM handling is invoked and is not declared in `requirements.txt`.

Important configuration:

- `GROQ_API_KEY`: required by Streamlit Medibot; also used by its voice transcription path.
- `HF_TOKEN`: required by the two separate Hugging Face CLI helpers, not by the regular Streamlit chat path.
- Optional local `.env`: loaded through `python-dotenv` in Medibot/helper code.

## 8. Safety, validity, privacy, and security notes

1. **No clinical validation is established here.** The repository contains no validation study or evidence that any output is clinically safe. Predictions, rankings, generated text, lifestyle scores, and recommendations are experimental.
2. **Do not interpret scores as diagnosis or calibrated risk.** The symptom model’s class scores are not shown to be calibrated probabilities. The heart target is an “ever diagnosed” response, while the UI calls its output a risk percentage and applies arbitrary display cutoffs.
3. **Similarity is not safety or equivalence.** The medicine matrix measures token-content similarity. The interaction view is also similarity-based, not a drug interaction database. Symptom-to-medicine mapping is hand-authored lookup logic.
4. **Medibot can be wrong.** It may use the LLM’s general medical knowledge beyond retrieved passages. Retrieved-source labels do not prove that a generated statement is supported by that source.
5. **External processing:** Medibot questions go to Groq for generation, and voice recordings are sent to Groq’s transcription endpoint when voice transcription is used. Do not enter identifying or sensitive health information unless the deployment’s data handling has been reviewed.
6. **Scan uploads:** image transformations run in the Python application process. A deployed app receives uploaded image bytes on its server; the demo guide’s claim that all processing is “in the browser” does not match the Pillow/NumPy implementation. DICOM metadata can contain patient identifiers.
7. **Credential exposure:** `pages/4_Medibot.py` interpolates the Groq key into browser-side JavaScript for direct voice transcription. A browser user can inspect that key. The repository also contains `test_token.py` with a hard-coded Hugging Face credential; this document intentionally does not reproduce it. Remove embedded credentials, rotate any valid exposed key, and use a server-side proxy/environment variable before public deployment.
8. **Serialized artifact trust:** app code loads pickle/joblib files and calls FAISS `load_local(..., allow_dangerous_deserialization=True)`. Only load artifacts from trusted sources; replacing these files with untrusted versions can execute code.
9. **Data provenance and licensing:** the repository lists local CSV/PDF assets but does not provide complete provenance/licensing documentation for every source dataset or medical reference. Verify redistribution rights before public distribution.

## 9. File map

```text
home.py                                      Landing page and home navigation
pages/1_Disease-Prediction-and-medical-recommendation.py
                                             Symptom disease estimates and reference lookups
pages/2_drug_recommendation.py               Medicine catalogue and similarity tools
pages/3_heart_Disease_Risk_Assesment.py       Heart assessment, reports, utilities, image transforms
pages/4_Medibot.py                           Groq + FAISS medical Q&A interface
theme_config.py                              Shared theme tokens and appearance toggle
data/                                        Local CSV data and PDF reference documents
models/                                      Serialized classifier, encoders, similarity artifacts
vectorstore/db_faiss/                        Prebuilt FAISS index and metadata
medibot/                                     Separate Hugging Face CLI examples
demo/                                        Sample imaging files and Scan Studio guide
utils/                                       Logos, illustrations, and legacy CSS assets
Disease Prediction and recommendation/       Disease workflow notebook
Drug Recommendation/                         Medicine-similarity notebook
heart_disease_risk_assessment/               Heart data prep, EDA, and modeling notebooks
requirements.txt, constraints.txt, runtime.txt
                                             Runtime and dependency declarations
README.md, PRODUCT.md, DESIGN.md, LICENSE     Usage, product context, design, and license
test_token.py                                Credential-check helper; not an app test
```

## 10. License

The repository includes the MIT License with copyright attributed to Ayan. The license does not by itself establish permission to redistribute third-party datasets, PDFs, images, or pretrained artifacts; check their individual terms.

## 11. Detailed request and data flow

This section follows the data from user input to display. It is useful when describing what actually runs, as distinct from notebook experiments or product wording.

### 11.1 Streamlit execution model

Each page is a Python script. Streamlit reruns that script when a widget changes or a form is submitted. The pages use `st.session_state` to retain selected values between reruns, while cached functions retain loaded objects between sessions/process runs according to Streamlit's cache behavior. The app does not have a separate web API server, database, user login, or durable user profile layer in the checked-in code.

Relative paths such as `data/...`, `models/...`, `utils/...`, and `vectorstore/...` are resolved from the current working directory. Launching Streamlit from another directory can therefore make assets appear missing. The cache decorators serve different purposes: `st.cache_resource` is used for objects intended to be shared, including models, encoders, and vector stores; `st.cache_data` is used for data or generated values such as parsed CSV content and HTML strings.

### 11.2 Symptom estimator: exact calculation sequence

1. `load_data()` reads the training table, symptom severity table, disease descriptions, precautions, medication/diet/workout tables, and the pickled classifier. It derives model feature columns from every `Training.csv` column except `prognosis`.
2. Symptom and disease names are normalized for matching: underscores are converted to spaces, repeated whitespace is collapsed, and case is lowered. Disease aliases handle a small number of spelling/spacing variants.
3. A typed symptom is passed to `thefuzz.process.extractOne` against the normalized symptom vocabulary. A result is accepted at score 80 or above; otherwise it is not silently treated as a valid model feature. Symptoms selected from the multiselect and accepted text matches are combined and deduplicated.
4. The model input is a DataFrame with one row and the model's symptom columns. Every cell begins at zero; the corresponding column is set to one for each selected symptom.
5. `predict_proba()` is used when available. The page maps each integer output class through `MODEL_DISEASE_MAP`, multiplies probabilities by 100 for display, and sorts them. If this path raises an exception, it tries `predict()` and reports the single class as 100%.
6. The app independently constructs disease symptom profiles from rows in `Training.csv`. Each disease's profile is the union of symptom columns present in rows assigned to that prognosis. A match is scored using severity-weighted coverage (72 points), input-symptom precision (20 points), and matched fraction of the disease profile (8 points).
7. For each candidate disease, the final rank is `0.78 * symptom_profile_score + 0.22 * model_score`. It sorts by final score, then profile score, then model score. The leading disease after this combined rank is displayed as the result; the top classifier disease is separately retained for the match summary.
8. Descriptive text and lists are joined by canonicalized disease names. The final screen can show description, precautions, medication strings, diet strings, and workout items. Missing table entries fall back to generic “not available” content or an empty list.
9. A display severity category is assigned from a manually maintained set of severe symptom names and a count threshold: at least two severe indicators or six total symptoms is Severe; one severe indicator or at least four total symptoms is Moderate; otherwise Mild. This is not a clinically validated triage score.

The model percentage and final match score have different meanings. The former originates in the model's `predict_proba`; the latter is a mixture with a hand-authored profile score. The UI may call both “confidence” or “match” in different places, so a report should specify which field is being discussed. Neither is shown to be calibrated against clinical outcomes.

### 11.3 Medicine recommender: exact similarity sequence

The active app loads two precomputed artifacts rather than vectorizing medicine descriptions at each request. It creates a DataFrame from `medicine_dict.pkl`, removes rows without `Drug_Name`, converts names to strings, and builds a name-to-row index. It loads `similarity.joblib` into a NumPy array. A selected medicine's row is copied, non-finite scores are replaced with negative infinity, its self-similarity is suppressed, and the largest remaining values are returned up to the requested count.

The artifact-producing notebook describes a content-based text pipeline:

1. Read `medicine.csv` and remove rows with missing fields (`dropna(inplace=True)`).
2. Prepare text from medicine descriptions and reasons as tags. The notebook lowercases and tokenizes text and uses NLTK's `PorterStemmer` to reduce word forms.
3. Vectorize tags with scikit-learn `CountVectorizer(stop_words='english', max_features=5000)`. Each row is represented by term counts in a shared vocabulary.
4. Calculate the dense pairwise cosine-similarity matrix across all vectors and serialize it with joblib. Serialize the catalogue DataFrame as a dictionary with pickle.

Cosine similarity indicates overlap in the representation, not that two products are interchangeable, equally effective, or safe to combine. Duplicate medicine names can also make the app's name-to-index dictionary retain only one matching row, while the similarity matrix is row-based; the notebook/app data should be checked for duplicate names when auditing recommendation correctness.

The symptom route is separate from this similarity calculation. `load_reason_drug_map()` loads or creates a mapping from symptom concepts to reason text. `ai_drugs_for_symptoms()` filters catalogue reason strings using that mapping and cached inputs. Despite its function name, it does not invoke a trained model or language model. The comparison screen uses matrix values to compare entries, and the “Interactions” route uses thresholds on those same values; it has no chemical ingredient graph, pharmacology knowledge base, or contraindication checker.

### 11.4 Heart estimate: exact data contract

The assessment form builds one dictionary with the following 22 categorical features. Exact key spelling matters because the fitted `CatBoostEncoder` and classifier expect the training schema:

| Feature key | Form meaning / representative choices |
|---|---|
| `gender` | female, male, nonbinary |
| `race` | Seven self-described race/ethnicity categories |
| `general_health` | excellent, very good, good, fair, poor |
| `health_care_provider` | one provider, more than one, none |
| `could_not_afford_to_see_doctor` | yes/no |
| `length_of_time_since_last_routine_checkup` | Recency category for routine checkup |
| `ever_diagnosed_with_heart_attack` | yes/no |
| `ever_diagnosed_with_a_stroke` | yes/no |
| `ever_told_you_had_a_depressive_disorder` | yes/no |
| `ever_told_you_have_kidney_disease` | yes/no |
| `ever_told_you_had_diabetes` | yes/no, no prediabetes, or pregnancy-related |
| `BMI` | Categorical BMI band selected/calculated in the form |
| `difficulty_walking_or_climbing_stairs` | yes/no |
| `physical_health_status` | zero, 1-13, or 14+ days not good |
| `mental_health_status` | zero, 1-13, or 14+ days not good |
| `asthma_Status` | never, current, former asthma |
| `smoking_status` | Smoking category |
| `binge_drinking_status` | yes/no |
| `exercise_status_in_past_30_Days` | yes/no |
| `age_category` | Thirteen age bands, 18-24 through 80+ |
| `sleep_category` | Categorized sleep-duration band |
| `drinks_category` | Categorized alcohol-consumption band |

On submission, the code creates a one-row DataFrame, calls `encoder.transform()`, attaches feature names (using the encoder API when dimensions match), and calls `model.predict_proba(encoded)[:, 1] * 100`. There is no second runtime preprocessing pipeline beyond that encoder in the page. Therefore, category spellings, feature names, column order, and artifact versions must remain compatible.

The page uses the same form data to generate explanatory and advice content. `build_feature_importance_df()` attempts `shap.TreeExplainer` on an estimator extracted from the fitted ensemble. It averages absolute SHAP values over the one submitted row and normalizes the values to sum to 100. If SHAP fails, it uses `feature_importances_`; if unavailable, it uses equal weights. Those values describe feature contribution under the model/explainer fallback used, not causal effects or changes in a person's real-world risk.

Hand-coded `RECOMMENDATION_RULES` check a subset of input fields (such as prior heart attack, stroke, age group, reported health, kidney disease, diabetes, and lifestyle factors) and attach recommendation copy. Other derived sections include a lifestyle score, a simulated “what if” profile, a heart-age estimate, a forecast visualization, goal tracking, notes, and Q&A. These are presentation utilities and rules around the classifier; they are not extra predictive models. The what-if path changes selected categorical inputs and re-runs the same model. The “heart age” calculation is app logic, not a validated medical age equation.

### 11.5 Medibot: retrieval and generation sequence

1. The page reads `GROQ_API_KEY`; if missing, it displays an error and stops before rendering the full page.
2. A background thread attempts to warm the vector-store and LLM caches. Exceptions are ignored during warmup and will appear when a user submits a query.
3. On first resource load, `HuggingFaceEmbeddings` loads `sentence-transformers/all-MiniLM-L6-v2` on CPU with batch size 32. `FAISS.load_local()` loads the checked-in local index and metadata from `vectorstore/db_faiss/`.
4. The retriever requests `TOP_K_RESULTS` documents (six in the current configuration). LangChain's `RetrievalQA` with `chain_type='stuff'` places retrieved text into one prompt context along with the question.
5. `ChatGroq` calls `llama-3.3-70b-versatile` with temperature 0.4. The prompt asks for accessible answers, says not to diagnose or prescribe for a particular person, and asks for emergency escalation for example red-flag symptoms. It also explicitly permits the model to answer using its general medical knowledge when retrieved context is incomplete; this means the response is not constrained to the two local PDFs.
6. Returned source documents are used to display source names/metadata. A separate heuristic labels confidence from source presence and text characteristics; it is not an evaluated correctness probability.
7. The active chat stores messages and bookmarks in Streamlit session state and trims displayed history to at most 12 messages. A helper prepends a recent topic for some follow-up questions; this is lightweight query rewriting, not a full transcript-aware conversational chain.

The two PDFs and FAISS files should be treated as a corpus plus precomputed index. The checked-in app does not show a repeatable ingestion command that rebuilds the index from the PDFs, nor an index manifest recording chunk size, overlap, embedding package version, or source checksums. A recreated index could therefore behave differently even with the same source PDFs.

## 12. Notebook workflows and the boundary between training and inference

### 12.1 Disease notebook

The disease notebook loads a table with 132 symptom feature columns and the `prognosis` target. In the initial workflow it encodes prognosis labels with scikit-learn `LabelEncoder`, makes a 70/30 split using `random_state=20`, then compares a linear-kernel SVC, a Random Forest with 100 trees and `random_state=42`, and Gradient Boosting with 100 estimators and `random_state=42`. The saved output named `RandomForest.pkl` is produced by fitting the Random Forest workflow. Notebook outputs show 1.0 accuracy for at least some baseline runs; that is a notebook output, not independently validated evidence of generalization.

Later notebook cells contain a separate stratified 70/30 split (`random_state=42`), feature scaling, cross-validation/grid-search imports, and parameter experiments. Their presence does not prove the app's pickle was produced from that later code. The runtime does not load the notebook's fitted LabelEncoder, which is why the hard-coded class map deserves a direct integrity check against the saved model's `classes_` and original encoder order.

### 12.2 Medicine notebook

The medicine notebook's output is a content-based recommendation system, not a supervised model. There is no target label or learned clinical outcome. Each medicine record is represented by word-count features and ranked by cosine distance/similarity. The app does not retrain that representation; it loads the two serialized outputs.

### 12.3 Heart notebooks

The preprocessing notebook starts from BRFSS 2022 material, changes column names, maps categorical codes, handles missing categories, derives variables such as BMI/sleep/drink groups, and writes a prepared table. Some imputations use random choice; unless a fixed seed is used in the relevant cell, this can yield different prepared data across runs.

The modeling notebooks encode categorical columns with `CatBoostEncoder`, split train/test data, compare several baseline and imbalance-aware classifiers, and tune an EasyEnsemble/lightgbm combination with a small Optuna search (`n_trials=5`, recall-oriented three-fold scoring). The notebooks report recall, precision, F1, and ROC AUC. The reported figures are outputs saved in notebook cells and are not recomputed here. A critical methodological concern is that the notebook fits the target encoder on the complete data before the split in the inspected workflow; fitting a supervised encoder before splitting can leak target information into validation/test features. The shown split also uses `random_state=1981` without an evident `stratify` argument. These issues can make reported scores optimistic or less representative of deployment.

### 12.4 No automatic training at app startup

The Streamlit pages load serialized artifacts; they do not train any of the three toolchains when a user opens the app. The training/evaluation process is represented by notebooks and existing artifacts. There is no checked-in orchestration script that validates raw data, retrains each artifact, evaluates it against a locked test set, and atomically deploys the new files.

## 13. Persistence, privacy, and network behavior by feature

| Feature/data | Where it goes or persists in the code | Practical interpretation |
|---|---|---|
| Disease symptom form and history | Streamlit session state | No database-backed account history is present; a session reset/restart may clear it. |
| Medicine watchlist | Streamlit session state | A temporary convenience list, not a persistent medication record. |
| Heart assessment, notes, goals, quiz | Streamlit session state; PDF/JSON can be downloaded | The result is not stored in a project database, but a deployed server processes submitted values. A downloaded report is user-managed data. |
| Medibot text question | Sent to Groq through LangChain for generation | Treat health text as third-party processed when using this feature. |
| Medibot source retrieval | Local FAISS index and local embedding model | The retrieval lookup is local to the app process; the generated question/context is then sent to Groq. |
| Medibot voice | Browser microphone permission; current custom JavaScript posts audio to Groq transcription endpoint | Audio leaves the browser. The current JavaScript also embeds the API key in the page source. |
| Scan Studio upload | Uploaded to the Streamlit Python process; transformed with Pillow/NumPy | It is not a browser-only image editor. DICOM headers can include identifiers. |
| External medicine links | Opens search/pharmacy websites | Those sites have their own tracking, privacy, stock, and clinical policies. |

Session-state data should not be described as private, durable storage. Streamlit session isolation and deployment logs/network configuration are host concerns not defined by the repository. The app does not show account authentication, encryption-at-rest for user records, retention controls, or a consent workflow for transmitting chat/voice data.

## 14. Artifact inventory and compatibility notes

The tracked model directory has three feature subdirectories. Approximate sizes below are filesystem observations and may vary if artifacts are replaced:

| Artifact | Approx. size | Runtime use |
|---|---:|---|
| `models/first_feature_models/RandomForest.pkl` | 7.18 MB | Loaded by the symptom estimator. |
| `models/second_feature_models/medicine_dict.pkl` | 1.31 MB | Loaded by the medicine catalogue. |
| `models/second_feature_models/similarity.joblib` | 16.37 MB | Loaded by the medicine recommender/comparison views. |
| `models/third_feature_models/best_model.pkl` | 4.59 MB | Loaded by the heart assessment. |
| `models/third_feature_models/cbe_encoder.pkl` | 8.7 KB | Loaded to transform heart form values. |
| `models/third_feature_models/best_model1.pkl` | 4.58 MB | Present, but not referenced by the active heart page. |
| `models/third_feature_models/cbe_encoder1.pkl` | 9.7 KB | Present, but not referenced by the active heart page. |
| `vectorstore/db_faiss/index.faiss` and `index.pkl` | Local index files | Loaded by Medibot. The pickle metadata is loaded through FAISS's dangerous-deserialization option. |

Python pickle and joblib are executable serialization formats, not neutral data formats. They rely on Python and compatible versions of the libraries/classes used to create them. Model artifacts should be distributed with provenance, exact training code/data references, feature schema, class mapping, library versions, and checksums. File existence and successful deserialization alone do not verify that an artifact is the intended or safe model.

## 15. Known gaps and audit questions for a written report

The following are concrete follow-up items if the project is to be evaluated or deployed beyond a demonstration:

1. Verify the disease classifier's output-label ordering against `MODEL_DISEASE_MAP`; archive the exact LabelEncoder classes alongside the model and add a consistency check.
2. Establish whether the disease notebook's later experiments changed the model or whether the artifact came from the earlier baseline cell. Record a model card with training data, split, metrics, and date.
3. Re-run disease evaluation on a leakage-resistant held-out set and inspect per-class support and errors; 100% notebook accuracy should be investigated rather than presented as proof of clinical accuracy.
4. For the heart workflow, fit the categorical encoder only on training folds and evaluate with stratification or a design justified for the BRFSS outcome. Use patient-level/time/geographic splits where relevant, and report calibration and subgroup performance as well as discrimination.
5. Rename heart outputs and interface language to distinguish prevalence/history classification from prospective risk prediction unless a prospective outcome and horizon are established.
6. Validate the medicine source data, deduplicate names, preserve a row identifier in catalogue and matrix, and avoid calling text similarity an interaction result.
7. Record the source, license, date, and checksum of every CSV, PDF, image, and model. Document the FAISS index-building recipe and re-indexing process.
8. Remove and rotate any valid credential found in repository history or current files. Move voice transcription to a server-side endpoint so browser code never receives a provider secret. Inspect git history as well as the current tree before calling a token “removed.”
9. Replace unsafe general-purpose pickle loads with signed/trusted artifacts or a safer format where possible; keep the FAISS metadata directory write-protected in production.
10. Document what user content is sent to each provider, add a clear consent notice, minimize identifiers, and configure provider/deployment retention appropriately.
11. Add input validation and error handling for missing model/data files, category/schema drift, malformed uploaded DICOM/images, and API timeouts. Add automated tests for feature order, label mapping, score calculations, and nonclinical utility logic.
12. Define emergency behavior consistently. A severity count heuristic or generated response is not a substitute for a validated triage pathway.

These are audit recommendations inferred from the checked-in implementation; they are not statements that all issues have already been resolved.

## 16. Glossary

- **Artifact:** A saved object loaded by the running app, such as a classifier, encoder, similarity matrix, or vector index.
- **CatBoost encoding:** A supervised categorical encoding method that replaces category labels with target-derived statistics. It must be fit only within the training data/fold to prevent leakage.
- **Class probability:** A model output associated with a class. It is not necessarily a calibrated probability of a real-world event.
- **Cosine similarity:** A geometric similarity score between numeric vectors. In this project it is based on overlapping medicine-description/reason terms.
- **FAISS:** A library for nearest-neighbor/vector similarity search. Here it stores and searches medical text embeddings.
- **Feature:** An input column used by a model, for example symptom presence or a categorical health-history value.
- **Label encoding:** Mapping category names to integer class identifiers. The mapping order has to match a classifier's trained output classes.
- **Leakage:** Information from a validation/test outcome entering model training or preprocessing, making evaluation appear stronger than it should.
- **RAG (retrieval-augmented generation):** Retrieve text passages, include them in a prompt, then ask a language model to write an answer. It does not guarantee the answer is supported by those passages.
- **Session state:** Per-user-session values held by Streamlit across script reruns; generally temporary, not a durable database.
- **SHAP:** A method for attributing a model output to its input features. It describes model behavior for the chosen explainer and data, not causation.

## 17. Source files reviewed for this description

The active runtime behavior is summarized from `home.py`, all four files in `pages/`, `theme_config.py`, the local CSV/PDF/model/vector-store paths, and the checked-in notebooks under `Disease Prediction and recommendation/`, `Drug Recommendation/`, and `heart_disease_risk_assessment/`. Configuration was summarized from `requirements.txt`, `constraints.txt`, and `runtime.txt`. The README, PRODUCT, DESIGN, and LICENSE files provide project-authored framing, but code behavior takes precedence where claims differ.

This report is a repository inspection, not a formal clinical, security, privacy, or statistical audit. Notebook outputs and model metrics have not been reproduced as part of writing this document. Exact metric values should be quoted only alongside the relevant notebook, split method, and caveats above.
