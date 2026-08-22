# Table of Contents

-   [Group Members](#group-members)
-   [📌 Introduction](#introduction)
-   [🔍 Summary of Key Features](#summary-of-key-features)
-   [Components](#components)
    -   [Fault Detection](#fault-detection)
    -   [Fault Localization](#fault-localization)
    -   [Fault Severity](#fault-severity)
    -   [Fault Rectification](#fault-rectification)
    -   [Centralized Dashboard](#centralized-dashboard)
-   [🛠 Tech Stack](#tech-stack)
-   [Project Management Methodology](#project-management-methodology)
-   [Folder Structure](#folder-structure)
-   [Models / Algorithms](#models-algorithms)
-   [Clone the repository](#clone-the-repository)
-   [Install dependencies](#install-dependencies)
-   [🐳 Docker](#-docker)
-   [📖 API Documentation](#-api-documentation)
-   [🔄 CI/CD](#-cicd)
-   [🪝 Pre-commit](#-pre-commit)

# Group Members

| Member No. | IIT ID   | RGU ID  | Student Name                  |
|------------|----------|---------|-------------------------------|
| 1          | 20241004 | 2425445 | Tamadhi Liyanage              |
| 2          | 20241705 | 2506730 | Mohamed Razik Seyed Rumaiz    |
| 3          | 20232954 | 2425574 | R. M. Manuli Maneka Gokarella |
| 4          | 20241835 | 2506738 | Dion Rasmika                  |

## 📌 Introduction

This project develops an AI-driven system for automated detection, localisation, and diagnosis of solar photovoltaic (PV) systems. The system utilizes a multi-modal approach, combining both electrical and visual imagery to identify issues, assess the severity and provide actionable rectification guidance. This project aims to enhance the reliability and efficiency of solar farm operations by minimizing the diagnostic time, reduce downtime and preventing significant energy yield losses.

## 🔍 Summary of Key Features

The core features of the system are summarized as follows:

-   **Multimodal Fault Detection** using electrical string data and thermal (hotspot) imagery
-   **Precise Fault Localization** to identify the exact module or string with issues
-   **Severity Assessment** quantifying power loss and economic impact
-   **AI-Powered Rectification** with optimized repair recommendations
-   **Interactive Dashboard** enabling fault classification, confidence analysis, and decision support through an intuitive interface.


## 📚 Datasets & Resources

### Public Datasets

| Dataset | Link |
|---------|------|
| Solar Panel Images | [Kaggle: Solar Panel Dataset](https://www.kaggle.com/datasets/pkdarabi/solarpanel) |
| Solar Panels Defect Detector Repo | [GitHub: P-Darabi](https://github.com/P-Darabi/SolarPanelsDefectDetector?tab=readme-ov-file) |
| Solar Augmented Dataset | [Kaggle: Solar Augmented Dataset](https://www.kaggle.com/datasets/gitenavnath/solar-augmented-dataset) |
| Electrical PV Fault Dataset | [GitHub: Clayton H Costa](https://github.com/clayton-h-costa/pv_fault_dataset) |

### Combined / Updated Image Dataset

| Dataset | Link |
|---------|------|
| Solar PV Single Hotspot Clean Images | [HuggingFace Dataset](https://huggingface.co/datasets/seyeddd/solar_pv_single_hotspot_clean_images) |

### Synthetic Data Generation Resources

- **Paper:** Generating Synthetic Time Series Photovoltaic Data with Real-World Physical Challenges and Noise for Use in Algorithm Test and Validation
  Authors: Matthew Muller, Kevin Anderson, Michael Deceglie (National Renewable Energy Laboratory)
  [Read PDF](https://docs.nrel.gov/docs/fy23osti/86459.pdf)

## Components

### Fault Detection

This component utilizes electrical data and thermal imagery to identify various fault types including open-circuit, short-circuit, shadowing, and hotspot anomalies. It uses a Random Forest for electrical data and a CNN for image analysis.

### Fault Localization

This component precisely locates the fault locations by fusing electrical pattern analysis with visual evidence from thermal imagery. It produces an interactive fault map highlighting affected strings and modules.

### Fault Severity

The component quantifies fault impact, predicting power degradation rates, energy losses, and financial implications. This allows prioritized maintenance scheduling based on how severe the fault is.

### Fault Rectification

Using decision trees, this component provides actionable repair guidance by giving step-by-step instructions, required resources, safety protocols, and estimated downtime.

### Centralized Dashboard

A Streamlit-based dashboard provides a user-friendly interface for operators to monitor system health, view fault reports, analyze historical trends, and access maintenance recommendations.

### AI Assistant

A floating "Solar PV AI Assistant" (bottom-right) answers questions about detected faults, fault types, severity, thermal imagery, I-V characteristics, model predictions, localization, and rectification recommendations. It is context-aware — each question receives a compact snapshot of the current page and recent predictions — and fully modular: it can connect to OpenAI, Gemini, Claude, a local Ollama instance, or any OpenAI-compatible endpoint via server-side environment variables (see `.env.example`). No provider is required to use the chat UI; without one it shows a friendly "not configured" message.

## 🛠 Tech Stack

### 💻 Backend
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask_API-000000?style=for-the-badge&logo=flask&logoColor=white)

### 🎨 Frontend
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![CSS](https://img.shields.io/badge/CSS-1572B6?style=for-the-badge&logo=css3&logoColor=white)

### 🤖 Machine Learning & Computer Vision
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)

### 📊 Explainability & Experiment Tracking
![SHAP](https://img.shields.io/badge/SHAP-Model%20Explainability-blue?style=for-the-badge)
![MLflow](https://img.shields.io/badge/MLflow-Experiment%20Tracking-0194E2?style=for-the-badge)

### 🗄 Data & Storage
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)

### 🛠 Development Tools
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Ruff](https://img.shields.io/badge/Ruff-D7FF64?style=for-the-badge&logo=ruff&logoColor=black)
![Pre-commit](https://img.shields.io/badge/Pre--commit-FAB040?style=for-the-badge&logo=pre-commit&logoColor=black)
![VSCode](https://img.shields.io/badge/VS_Code-007ACC?style=for-the-badge&logo=visual%20studio%20code&logoColor=white)
![PyCharm](https://img.shields.io/badge/PyCharm-000000?style=for-the-badge&logo=pycharm&logoColor=white)
![Google Colab](https://img.shields.io/badge/Google_Colab-F9AB00?style=for-the-badge&logo=googlecolab&logoColor=white)
![Git](https://img.shields.io/badge/Git-FF5733?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-121011?style=for-the-badge&logo=github&logoColor=white)

### 📡 API & Integration
![REST API](https://img.shields.io/badge/REST_API-009688?style=for-the-badge&logo=flask&logoColor=white)
![OpenAPI](https://img.shields.io/badge/OpenAPI_3-6BA539?style=for-the-badge&logo=swagger&logoColor=white)
![Swagger UI](https://img.shields.io/badge/Swagger_UI-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)

### 📋 Project Management
![Jira](https://img.shields.io/badge/Jira-0052CC?style=for-the-badge&logo=jira&logoColor=white)

### 📝 Documentation
![LaTeX](https://img.shields.io/badge/LaTeX-008080?style=for-the-badge&logo=latex&logoColor=white)
![Microsoft Word](https://img.shields.io/badge/MS_Word-2B579A?style=for-the-badge&logo=microsoftword&logoColor=white)
![Notion](https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=notion&logoColor=white)

### 💽 Operating Systems
![Windows](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![macOS](https://img.shields.io/badge/macOS-000000?style=for-the-badge&logo=apple&logoColor=white)


## Project Management Methodology

The project follows Agile methodology with the Scrum framework, which is managed through Jira for sprint planning and task distribution. Regular stand-ups and sprint reviews ensure continuous monitoring and adaptability to changing requirements.

## Folder Structure

-   [solar-pv-fault-detection](./)
    -   [src](./src) - Source code of the entire application
    -   [datasets](./datasets) - Electrical & image datasets
    -   [diagrams](./diagrams) - UML diagrams used for designing
    -   [docs](./docs) - Documents aligned with the project
    -   [manuals](./manuals) - Manuals used in simulating PV data
    -   [models](./models) - Pre-trained ML/DL models
    -   [notebooks](./notebooks) - Source code
        -   [detection](./notebooks/fault-detection) - Fault detection notebooks
        -   [localization](./notebooks/fault-localization) - Fault localization notebooks
        -   [severity](./notebooks/fault-severity) - Fault severity analysis notebooks
        -   [rectification](./notebooks/fault-rectification) - Rectification recommendation notebooks
    -   [tests](./tests) - Component tests
    -   [.Rhistory](./.Rhistory) - Rhistory
    -   [.github/workflows](./.github/workflows) - CI/CD (GitHub Actions)
    -   [Dockerfile](./Dockerfile) - Container image definition
    -   [compose.yml](./compose.yml) - Docker Compose orchestration
    -   [.dockerignore](./.dockerignore) - Files excluded from the image
    -   [.pre-commit-config.yaml](./.pre-commit-config.yaml) - Pre-commit hooks
    -   [README.md](./README.md) - Project documentation
    -   [.gitignore](./.gitignore) - Files to ignore
    -   [.CONTRIBUTING.md](./CONTRIBUTING.md) - Contributions
    -   [LICENSE](./LICENSE) - Project License
    -   [README.md](./README.md) - Project documentation
    -   [requirements.txt](./requirements.txt) - Python dependencies

## Models / Algorithms

| Component           | Model / Algorithm               |
|---------------------|---------------------------------|
| Fault Detection     | Random Forest / DenseNet201     |
| Fault Localization  | DenseNet121 + CNN Bi-LSTM       |
| Fault Severity      | Random Forest Regressor / YOLO  |
| Fault Rectification | Random Forest / Deep-Q Learning |


## 🚀 How to Run the Application

### Prerequisites
- Python 3.11+
- pip
- (Recommended) Virtual environment
- (Alternative) Docker + Docker Compose — see the [🐳 Docker](#-docker) section

> 💡 **Docker quick start:** if you have Docker installed you can skip the local
> environment entirely — `docker compose up -d` builds and starts both the API
> and the dashboard. Configure `.env` first (see the AI Assistant section below).

---

### 1️⃣ Clone the repository
```bash
git clone https://github.com/thamadhi/solar-panel-fault-mapping.git
cd solar-panel-fault-mapping
```

### 2️⃣ Create and activate a virtual environment

For mac:
```bash
python3.11 -m venv .venv
source .venv/bin/activate
```
For windows (PowerShell):
```bash
python3.11 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### ⚙️ Configure the AI Assistant (not required)

Copy `.env.example` to `.env`, pick a provider, and set its credentials:

```bash
AI_PROVIDER=openai        # openai | openai-compatible | gemini | claude | ollama
OPENAI_API_KEY=sk-...     # provider-specific key (kept on the server only)
```

The chat button always appears; without a configured provider it replies with a
"provider not configured" message. API keys are read exclusively on the Flask
backend and are never sent to the browser.


### ▶️ Running the Backend API (Flask)

Start the Flask API first from the project root in one terminal:

```bash
make run
```

or

```bash
python -m src.api
```

### ▶️ Running the Streamlit Dashboard

Open a new terminal, activate the same .venv, then run:

```bash
make app
```

or

```bash
streamlit run app.py
```

---

## 🐳 Docker

Both the Flask API and the Streamlit dashboard are containerized with Docker
Compose (`compose.yml`). One shared image (`Dockerfile`) is used; the dashboard
container just overrides the command.

> **Important:** Docker reads environment variables from `.env`. `.env` must be a
> plain `KEY=VALUE` file. If your local `.env` was created from an older
> `.env.example` that contained docstring/prose lines, remove those lines first
> — docker compose rejects them. See `.env.example`.

### Build & run

```bash
docker compose build        # build the image
docker compose up -d        # start API + dashboard in the background
docker compose down         # stop and remove containers
docker compose logs -f      # follow the logs
```

Or use the Makefile helpers:

```bash
make docker-build
make docker-up
make docker-down
make docker-logs
```

### Accessing the services

| Service   | URL                        | Port |
|-----------|----------------------------|------|
| Flask API | http://localhost:8000      | 8000 |
| API docs  | http://localhost:8000/docs | 8000 |
| Dashboard | http://localhost:8501      | 8501 |

### Data & models

- The SQLite database is persisted in the `pv_data` volume (`/app/data`), shared
  by both services.
- ML models are downloaded from HuggingFace on first use and cached in the
  `hf_cache` volume (`/app/.cache/huggingface`), so restarts don't re-download.

### Ollama inside Docker

Ollama is **not** bundled in the compose stack. A local Ollama running on your
host is reached from the API container via:

```bash
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

set in `.env` (macOS/Windows). For local non-Docker development the default
`http://localhost:11434` keeps working unchanged. If Ollama (or any AI provider)
is unavailable, the assistant falls back to its built-in offline knowledge base.

---

## 📖 API Documentation

The Flask REST API is documented with an **OpenAPI 3.0** specification, rendered
with **Swagger UI**.

- Interactive docs (Swagger UI): <http://localhost:8000/docs>
- Raw OpenAPI JSON: <http://localhost:8000/openapi.json>

The specification covers every real endpoint: authentication, electrical/thermal
fault detection, explainability, localisation, rectification, and the Solar PV AI
Assistant (chat + history). All protected endpoints are marked with a JWT bearer
security scheme; no credentials are ever embedded in the docs. Use the green
"Authorize" button in Swagger UI to paste a token returned by `POST /auth/login`.

---

## 🔄 CI/CD

Continuous integration is configured with **GitHub Actions**
(`.github/workflows/ci.yml`). It runs on every push to `main`/`master` and on
every pull request:

1. **Lint** — `ruff` static checks (config in `pyproject.toml`)
2. **Tests** — `pytest` (AI providers are mocked or use the offline fallback; no
   API keys, Ollama or large model downloads are needed in CI)
3. **Docker** — validates `docker compose config` and builds the Docker image

---

## 🪝 Pre-commit

Pre-commit hooks (`pre-commit-config.yaml`) enforce code quality on every commit:
trailing-whitespace/EOF fixes, YAML/JSON validation, merge-conflict detection,
large-file detection, and `ruff` linting.

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

or `make precommit`. Ruff is configured with per-file allowances for the
existing (pre-formatting) codebase so it stays green without rewriting it; new
files are checked against the full rule set.
