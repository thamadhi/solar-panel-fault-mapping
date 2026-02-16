# Table of Contents

-   [Group Members](#group-members)
-   [📌 Introduction](#-introduction)
-   [🔍 Summary of Key Features](#-summary-of-key-features)
-   [Components](#components)
    -   [Fault Detection](#fault-detection)
    -   [Fault Localization](#fault-localization)
    -   [Fault Severity](#fault-severity)
    -   [Fault Rectification](#fault-rectification)
    -   [Centralized Dashboard](#centralized-dashboard)
-   [🛠 Tech Stack](#-tech-stack)
-   [Project Management Methodology](#project-management-methodology)
-   [Folder Structure](#folder-structure)
-   [Models / Algorithms](#models--algorithms)
-   [Clone the repository](#clone-the-repository)
-   [Install dependencies](#install-dependencies)

# Group Members

| Member No. | IIT ID   | RGU ID  | Student Name                  |
|------------|----------|---------|-------------------------------|
| 1          | 20241004 | 2425445 | Tamadhi Liyanage              |
| 2          | 20241705 | 2506730 | Mohamed Razik Seyed Rumaiz    |
| 3          | 20232954 | 2425574 | R. M. Manuli Maneka Gokarella |
| 4          | 20241835 | 2506738 | Dion Rasmika                  |

## 📌 Introduction

This project develops an AI-driven system for automated detection, localisation, and diagnosis of solar photovoltaic (PV) systems. The system utilizies a multi-modal approach, combining both electrical and visual imagery to identify issues, assess the severity and provide actionable rectification guidance. This project iams to enhance the reliability and efficiency of solar farm operations by minimizing the diagnostic time, reduce downtime and preventing significant energy yield losses.

## 🔍 Summary of Key Features

The core features of the system are summarized as follows:

-   **Multimodal Fault Detection** using electrical time-series data and thermal (hotspot) imagery
-   **Precise Fault Localization** to identify the exact module or string with issues
-   **Severity Assessment** quantifying power loss and economic impact
-   **AI-Powered Rectification** with optimized repair recommendations
-   **Interactive Dashboard** enabling fault classification, confidence analysis, and decision support through an intuitive interface.

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

## 🛠 Tech Stack

-   **Backend**: Python
-   **Frontend**: Streamlit, CSS
-   **Computer Vision**: OpenCV
-   **Project Management**: Jira
-   **Frameworks & Libraries**:
    -   Scikit-learn (ML algorithms, preprocessing)
    -   TensorFlow (deep learning models)
    -   Google Colab (cloud-based notebooks)
    -   PyCharm, VS Code (IDE for development & debugging)
    -   Flask API (backend API integration)
    -   Windows OS / MacOS (for high-performance computing)
    -   LaTeX / MS Word / Notion (documentation)
    -   MLflow (model comparisons and performance tracking)
    -   SHAP (for model explainability)

## Project Management Methodology

The project follows Agile methodology with the Scrum framework, which is managed through Jira for sprint planning and task distribution. Regular stand-ups and sprint reviews ensure continuous monitoring and adaptability to changing requirements.

## Folder Structure

-   [solar-pv-fault-detection](./)
    -   [dashboard](./dashboard) - Main streamlit dashboard application
        -   [core](./dashboard/core) - Core files
        -   [handlers](./dashboard/handlers) - Main component handlers
        -   [models](./dashboard/models) - Business related classes
    -   [datasets](./datasets) - Electrical & image datasets
    -   [diagrams](./diagrams) - UML diagrams used for designing
    -   [docs](./docs) - Documents aligned with the project
    -   [manuals](./manuals) - Manuals used in simulating PV data
    -   [models](./models) - Pre-trained ML/DL models
    -   [src](./src) - Source code
        -   [detection](./src/fault-detection) - Fault detection feature
        -   [localization](./src/fault-localization) - Fault localization feature
        -   [severity](./src/fault-severity) - Fault severity analysis feature
        -   [rectification](./src/fault-rectification) - Rectification recommendation feature
    -   [tests](./tests) - Component tests
    -   [.Rhistory](./.Rhistory) - Rhistory
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
| Fault Localization  | CNN + LSTM                      |
| Fault Severity      | Random Forest                   |
| Fault Rectification | Decision Tree                   |

## Clone the repository

``` bash
git clone https://github.com/thamadhi/solar-panel-fault-mapping.git
cd solar-panel-fault-mapping
```

## Install dependencies

```         
pip install -r requirements.txt
```
