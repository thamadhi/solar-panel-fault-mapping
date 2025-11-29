# Table of Contents
- [Group Members](#group-members)
- [📌 Introduction](#-introduction)
- [🔍 Summary of Key Features](#-summary-of-key-features)
- [Components](#components)
  - [Fault Detection](#fault-detection)
  - [Fault Localization](#fault-localization)
  - [Severity Analysis](#severity-analysis)
  - [Rectification Recommendation System](#rectification-recommendation-system)
  - [Centralized Dashboard](#centralized-dashboard)
- [🛠 Tech Stack](#-tech-stack)
- [Project Management Methodology](#project-management-methodology)
- [Folder Structure](#folder-structure)
- [Models / Algorithms](#models--algorithms)
- [Clone the repository](#clone-the-repository)
- [Install dependencies](#install-dependencies)

# Group Members

| Member No. | IIT ID   | RGU ID  | Student Name                       |
|------------|----------|---------|------------------------------------|
| 1          | 20241004 | -       | Tamadhi Liyanage                   |
| 2          | 20241705 | 2506730 | Mohamed Razik Seyed Rumaiz         |
| 3          | 20232954 | -       | R. M. Manuli Maneka Gokarella      |
| 4          | 20241835 | -       | Dion Rasmika                       |

## 📌 Introduction
This project develops an AI-driven system for automated detection, localisation, and diagnosis of solar photovoltaic (PV) systems. The system utilizies a multi-modal approach, combining both electrical and visual imagery to identify issues, assess the severity and provide actionable rectification guidance. This project iams to enhance the reliability and efficiency of solar farm operations by minimizing the diagnostic time, reduce downtime and preventing significant energy yield losses.

## 🔍 Summary of Key Features

The core features of the system are summarized as follows:

- **Multimodal Fault Detection** using electrical time-series data and thermal/EL imagery
- **Precise Fault Localization** to identify the exact module or string with issues
- **Severity Assessment** quantifying power loss and economic impact
- **AI-Powered Rectification** with optimized repair recommendations
- **Interactive Dashboard** for real-time monitoring and decision support

## Components

### Fault Detection
This component utilizes electrical data and drone imagery to identify various fault types including open-circuit, short-circuit, partial shading, and hotspot anomalies. It uses an ANN for electrical data and CNN for image analysis.

### Fault Localization
This component precisely locates the fault locations by fusing electrical pattern analysis with visual evidence from thermal and electroluminescence imagery. It produces an interactive fault map highlighting affected strings and modules.

### Severity Analysis
The component quantifies fault impact using regression models, predicting power degradation rates, energy losses, and financial implications. This allows prioritized maintenance scheduling based on how severe the fault is.

### Rectification Recommendation System
Using reinforcement learning optimization, this component provides actionable repair guidance by giving step-by-step instructions, required resources, safety protocols, and estimated downtime.

### Centralized Dashboard
A Streamlit-based dashboard provides a user-friendly interface for operators to monitor system health, view fault reports, analyze historical trends, and access maintenance recommendations.

## 🛠 Tech Stack
- **Backend**: Python
- **Frontend**: Streamlit
- **Computer Vision**: OpenCV
- **Project Management**: Jira
- **Frameworks & Libraries**:
  - Scikit-learn (ML algorithms, preprocessing)
  - TensorFlow / PyTorch (deep learning models)
  - Google Colab (cloud-based notebooks)
  - PyCharm (IDE for development & debugging)
  - FastAPI (backend API integration)
  - Windows OS / MacOS (for high-performance computing)
  - LaTeX / Word / Notion (documentation)

## Project Management Methodology
The project follows Agile methodology with the Scrum framework, which is managed through Jira for sprint planning and task distribution. Regular stand-ups and sprint reviews ensure continuous monitoring and adaptability to changing requirements.

## Folder Structure

* [solar-pv-fault-detection](./)
  * [data](./data) - Electrical & image datasets
  * [models](./models) - Pre-trained ML/DL models
  * [notebooks](./notebooks) - Colab notebooks
  * [src](./src) - Source code
    * [detection](./src/detection) - Fault detection feature
    * [localization](./src/localization) - Fault localization feature
    * [severity](./src/severity) - Fault severity analysis feature
    * [rectification](./src/rectification) - Rectification recommendation feature
  * [dashboard](./dashboard) - Streamlit app
  * [requirements.txt](./requirements.txt) - Python dependencies
  * [README.md](./README.md) - Project documentation


## Models / Algorithms
| Component                     | Model / Algorithm              |
|--------------------------------|-------------------------------|
| Fault Detection                | ANN / DenseNet                |
| Fault Localization             | CNN + LSTM                    |
| Severity                       | Decision Tree Regressor / Gradient Boosting |
| Rectification                  | Random Forest / Deep Q-Learning |

## Clone the repository
```bash
git clone https://github.com/thamadhi/solar-panel-fault-mapping.git
cd solar-pv-fault-detection
```

# Install dependencies
pip install -r requirements.txt
