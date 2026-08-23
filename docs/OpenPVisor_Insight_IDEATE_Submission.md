# OpenPVisor Insight

### The Solar Panel Fault Intelligence Platform

**Team Number:** CSX - XXX *(replace)*
**Team Name:** *[your team name]*
**University:** Informatics Institute of Technology
**Project Category:** Software / AI & Data
**IDEATE SUBMISSION**

> ⚠️ *Before submitting:* replace all `[bracketed placeholders]`, verify every statistic against its source, and complete Section 7 (Team).

---

## 1. PROBLEM DEFINITION & BACKGROUND

### 1.1 Problem Statement

Solar photovoltaic (PV) installations silently degrade. Faults such as hotspots, open circuits, short circuits, shadowing effects, and degraded strings develop invisibly behind panels, on rooftops, and across large solar farms. Unlike a broken streetlight, a faulty panel gives no outward sign — yet it bleeds energy yield every single day, accelerates cell degradation, and in the case of thermal hotspots can escalate into fire risk. Manual inspection requires technicians to physically access rooftops or walk multi-acre arrays with handheld infrared cameras, which is slow, expensive, weather-dependent, and often skipped entirely. Hence, an intelligent monitoring platform is needed that can detect, localise, grade, and prescribe fixes for PV faults automatically — using only the electrical sensor data and thermal imagery that solar systems already produce.

### 1.2 Problem Background

A solar array is typically warranted for 25 years, but field reliability studies consistently show that a meaningful share of installed capacity underperforms due to undetected faults rather than resource scarcity. Industry surveys of operating PV plants repeatedly find that a large fraction of systems operate below expected performance ratios, with fault classes such as hotspots, string outages, soiling, and inverter/DC mismatches among the leading contributors. A single undetected hotspot does not merely waste energy — it thermally stresses the cell and has been implicated in rooftop fire incidents worldwide.

Consider three recurring scenarios:

- A **grid-tied rooftop owner** notices a higher electricity bill months after pigeons nested under their panels — the shading fault has been silently costing money the entire time.
- A **solar farm operator** discovers during an annual manual inspection that one string of 32 modules has been running near-zero current for weeks — energy and revenue lost with no alarm ever raised.
- A **technician responding to a complaint** measures voltages with a multimeter and cannot tell whether the symptom is shadowing, an open circuit, or internal degradation — leading to guesswork replacements and repeat visits.

In high-growth solar markets such as Sri Lanka — where rooftop net-metering schemes and utility-scale plants are expanding rapidly — the inspection workforce simply does not scale with installed capacity. To close this gap, operators need software that turns the data they already collect (inverter readings, thermal photographs) into instant diagnosis: what is faulty, where exactly it is, how severe it is, and what to do about it.

### 1.3 Research Background

Research into PV condition monitoring highlights two persistent challenges. First, detection: classical threshold-based alarms fail to distinguish between environmental variation (irradiance, temperature) and true electrical faults, which is why machine-learning classifiers trained on labelled I-V curve data have become the state of the art for fault classification. Second, interpretation: operators do not act on a bare prediction — published work in explainable AI (e.g., SHAP feature attribution) shows that practitioners adopt model outputs far more readily when each decision is accompanied by human-readable reasoning.

Thermal imaging research establishes that hotspot signatures captured by standard IR cameras can be classified automatically by convolutional neural networks, and that per-string inverter telemetry can be mapped to specific faulty strings using sequence models. Separately, operations-research literature on maintenance scheduling demonstrates that pairing a diagnosed fault with a ranked set of corrective actions — weighing cost, downtime, and severity — materially reduces mean-time-to-repair compared with unaided technician judgement. OpenPVisor Insight brings these strands together in one operational tool built for emerging-market solar businesses.

### 1.4 In-Scope & Out-Scope

#### In-Scope

The OpenPVisor Insight platform will focus on delivering the below functionalities and areas of use.

**1) Functionalities**

a) **Usability** — a browser dashboard usable immediately after login; no installation, no special hardware beyond the sensors/images the system already produces. Multi-role accounts (Admin, Solar PV Operator, Technician, Standard viewer) control who sees what.

b) **Features**

- i) **Electrical Fault Detection** — upload inverter CSV readings (`vdc1, vdc2, idc1, idc2, irradiance, temperature`); a tuned Random Forest classifies the row as Normal, Shadowing, Open Circuit, Short Circuit or Hotspot-related fault, with a confidence score and per-row SHAP explanations.
- ii) **Thermal Fault Detection** — upload a thermal photograph of a panel; a convolutional neural network detects hotspot anomalies with confidence scoring.
- iii) **String Localisation** — from 32-string inverter data, a CNN-BiLSTM model identifies *which* strings are faulty (visualised as a colour-coded 32-string heatmap); from thermal images, it returns the faulty region with an annotated bounding-box overlay.
- iv) **Severity Analysis** — quantifies how serious a detected fault is, combining model confidence with SHAP feature-contribution magnitudes, banded Low / Medium / High / Critical.
- v) **Rectification Advisor** — given fault type, severity, weather and site context, recommends ranked corrective actions with estimated **cost (USD)** and **downtime (hours)**, highlighting the best-value action.
- vi) **AI Assistant** — a context-aware chatbot that answers questions about detected faults, thermal imagery, and I-V characteristics in natural language.
- vii) **Activity History & Analytics** — every analysis is logged; dashboards show totals, average confidence, daily trends, and fault-type distribution.

c) **Design** — clean green/teal design language with light and night modes, responsive from mobile (375px) to desktop, accessible role-aware navigation.

**2) Areas of Use**

- Routine health screening of rooftop installations from the office
- Post-commissioning and warranty-inspection evidence gathering
- Prioritising maintenance crews by severity instead of first-come-first-served
- Thermal drone-image triage for solar farm operators
- Training junior technicians via SHAP-based explanations

#### Out-Scope

Limitations: the platform diagnoses; it does not repair. It does not control hardware (no relay/actuation), does not perform continuous streaming ingestion (analysis is upload/batch based in this version), and its electrical models are trained for the monitored voltage/current ranges of typical grid-tied strings — extreme edge cases outside training distribution return lower confidence. Severity scoring is currently derived from classification confidence and SHAP magnitudes rather than the dedicated XGBoost severity regressor, which is planned for the next release. Out-of-scope deliverables also include long-term financial projections beyond the go-to-market phase and hardware manufacturing.

### 1.5 User Pain Points

1. **Invisible losses** — owners pay for a system that quietly underperforms; there is no symptom until the bill arrives.
2. **Dangerous, expensive inspections** — rooftop and remote-site inspections carry fall risks, travel costs, and weather downtime.
3. **Guesswork repairs** — without localisation and root-cause separation, technicians swap healthy components.
4. **No prioritisation** — operators with hundreds of sites lack a severity-ranked worklist.
5. **Black-box distrust** — existing tools output labels without justification; technicians won't act on opaque predictions.

---

## 2. PROPOSED SOLUTION

### 2.1 One-Line Pitch

An intelligent platform that detects solar panel faults, pinpoints the exact faulty strings or hotspot regions, grades severity, and prescribes costed repairs — in minutes, without a site visit.

### 2.2 Solution Overview

OpenPVisor Insight is a web platform with two halves.

**Intelligence layer (API).** A secured REST service hosts four ML pipelines: (1) a Random Forest classifier for electrical faults engineered from raw string voltages/currents, irradiance and temperature; (2) a deep CNN for thermal hotspot classification; (3) a CNN-BiLSTM pair that both names the fault and maps it to individual strings within a 32-string array, plus an annotated-overlay hotspot localiser for images; (4) a rectification engine that ranks corrective actions by expected value, attaching cost and downtime estimates to each recommendation. Every prediction can be explained through SHAP feature attributions shown directly in the UI.

**Experience layer (dashboard).** A modern Next.js application with role-aware navigation: batch CSV analysis with click-any-row explainability, thermal image scanning, interactive fault-string heatmaps, annotated image overlays, severity gauges, a rectification form producing a "Best Action" card with cost and downtime, activity history with trend and distribution analytics, PV system configuration, an integrated help centre, and a floating AI assistant that understands what is currently on screen. Night mode, a branded loading experience, and cursor-reactive UI make a traditionally dry engineering tool feel like a product.

Operators log in, drop a file, and receive a diagnosis with evidence in seconds. Everything is deployable as containers (Railway + Vercel) with CI gating every change.

### 2.3 Purpose & Impact

The main goal is to compress the fault-to-fix cycle of solar maintenance from weeks to minutes while making every diagnosis trustworthy.

This solves delayed fault discovery, dangerous manual inspections, and untargeted repair spending.

Expected benefits:

- **Recovered energy yield and revenue** from early fault interception.
- **Reduced inspection cost and technician risk** — triage happens remotely.
- **Faster, cheaper repairs** because localisation removes diagnostic guesswork.
- **Trustworthy AI** — every call is accompanied by feature-level evidence.

### 2.4 Ethical & Social Impact

**Data privacy:** the platform processes equipment telemetry and thermal imagery of panels — not people. Accounts hold only a username, email and role. No biometric or personal behavioural data is collected, stored, or shared.

**Environmental impact:** by maximising the output of already-installed solar assets, the platform increases clean-energy generation without manufacturing new hardware — directly supporting sustainability targets and national renewable-energy goals.

**Inclusivity and safety:** fewer physical climbs means fewer workplace injuries. Small operators gain access to diagnostic capability previously affordable only to large utilities, levelling the playing field in emerging markets.

**Positive social change:** cheaper, cleaner, more reliable solar power accelerates adoption away from fossil generation and builds local technical capability in AI-driven energy management.

### 2.5 Uniqueness & Special Features

| Capability | OpenPVisor Insight | Typical competitors |
|---|---|---|
| Electrical + thermal diagnosis in one tool | ✅ | Usually one or the other |
| String-level localisation with heatmap | ✅ | Plant-level alarms |
| SHAP explanation on every prediction | ✅ | Black-box label only |
| Costed rectification recommendations | ✅ | Not offered |
| Built-in AI assistant over live results | ✅ | None |
| Affordable SaaS for emerging markets | ✅ | Enterprise-priced |

**Explainable by default** — not just *what* is wrong, *why* (SHAP bars per row).
**End-to-end** — detect → locate → grade → prescribe, replacing four separate tools.
**Built for the market** — runs affordably on cloud containers; no proprietary hardware lock-in.

---

## 3. MARKET & INDUSTRY ANALYSIS

### 3.1 Target Audience & Market Size

**Primary User Segments:**

- **Solar EPCs & O&M service companies**
  - *Characteristics:* firms installing and maintaining rooftop/farm systems under service contracts.
  - *Needs:* fast remote triage, proof-of-service records, efficient crew routing.
  - *Behaviours:* adopt tools that cut truck rolls and protect contract margins.
- **Industrial & commercial rooftop owners** (factories, hotels, warehouses)
  - *Characteristics:* high daytime consumption, large roofs, net-metering agreements.
  - *Needs:* assurance their asset performs; early warning before revenue loss compounds.
  - *Behaviours:* pay for monitoring bundled with ROI reporting.

**Secondary User Segments:**

- **Utility-scale plant operators** needing drone-image triage workflows.
- **Insurers & financiers** seeking objective asset-health evidence.
- **Energy regulators / rural electrification programmes** monitoring subsidised installs.

**Market Size Estimate:**

- Global solar operations & maintenance spend is projected to grow strongly through 2030 as installed PV capacity multiplies; even fractional digitisation of O&M represents a multi-billion-dollar software opportunity. *(verify current figures at submission)*
- In Sri Lanka, potential early adopters include thousands of net-metered rooftop installations under the national rooftop solar programme, a growing industrial self-generation base, and utility-scale parks in the North and East.
- Estimated initial serviceable market of **[LKR X]** annually within the next five years. *(size with local installer count × avg. monitoring willingness-to-pay)*

### 3.2 Market Potential & Importance

Why this solution is relevant now:

- **Booming installed base** — every new panel added today is a future inspection job; manual inspection cannot scale at this growth rate.
- **Technician scarcity** — qualified solar engineers are concentrated in cities; remote diagnosis extends their reach.
- **AI maturity** — classifiers for PV faults and thermal imagery are proven in literature; packaging them into a usable product is the open gap.
- **Energy-security pressure** — economies facing fuel-import costs push hard toward solar; every recovered megawatt-hour matters.

Long-term sustainability & growth opportunities:

- **Monitoring-as-a-Service subscriptions** for installers' client portfolios.
- **Drone-partner integrations** — automated thermal flyover ingestion.
- **Regional expansion** to other emerging solar markets with similar grid topologies.
- **Data products** — anonymised fault-benchmark analytics for insurers and manufacturers.

### 3.3 Competitor Analysis & Differentiation

**Direct competitors:**

- Monitoring portals bundled with inverters (vendor-locked, alarm-only)
- Enterprise asset-management platforms priced for utilities
- Standalone thermal-inspection service providers (per-visit pricing)

**Indirect competitors:** manual multimeter+IR-camera inspections; periodic cleaning contracts with no diagnostics.

**Our Competitive Edge:**

| Feature | Our Solution | Competitors |
|---|---|---|
| Explainability (SHAP) per prediction | ✅ | ❌ black box |
| String-level localisation | ✅ | ❌ array-level |
| Costed repair recommendations | ✅ | ❌ |
| Vendor-neutral (any inverter CSV / any IR camera) | ✅ | ❌ locked ecosystems |
| Emerging-market pricing | ✅ | ❌ enterprise-only |

**Why we stand out:** Faster and smarter — evidence-backed diagnosis in seconds. Trustworthy — transparent reasoning builds technician buy-in. Scalable & affordable — pure software, containerised, priced for local businesses.

---

## 4. BUSINESS & FINANCIAL MODEL

### 4.1 Business Revenue Model & Cost Structure

*(Insert canvas/diagram here as in reference submission)*

**Revenue streams:**

1. **SaaS subscriptions** — tiered per-site or per-MW monthly pricing for installers/O&M firms (Starter / Professional / Fleet).
2. **Pay-per-analysis credits** — for occasional users (single thermal scans, one-off CSV audits).
3. **Enterprise contracts** — white-labelled deployments for utilities and large estates, with support SLAs.
4. **Future data products** — anonymised fleet-health benchmarking for insurers/lenders.

**Cost structure:** cloud hosting (containers scale cheaply), LLM API usage for the assistant, model retraining compute, sales/support salaries, and marketing. Margins improve as inference is cached and models are optimised.

### 4.2 Initial Go-to-Market Strategy

**Early Adoption Strategy:**

1. **Installer partnerships:** onboard 5–10 mid-sized Sri Lankan solar EPCs as design partners; free pilot in exchange for feedback and case-study rights.
2. **Flagship proof points:** publish before/after yield-recovery case studies (e.g., a factory roof where shadowing was costing X kWh/month).
3. **Channel plays:** bundle trials through inverter distributors and thermal-camera resellers who already visit these customers.
4. **Regulatory alignment:** position reports as evidence for net-metering compliance and insurance documentation.

**Marketing:**

- Sinhala/Tamil-language awareness content: *"Your solar roof may be losing money silently."*
- LinkedIn thought leadership on AI-driven O&M; demo videos comparing manual vs. platform diagnosis times.
- Presence at energy expos and SLSEA/industry workshops.

### 4.3 Partnerships & Funding Strategies

**Strategic partnerships:**

- Universities (e.g., [your institution]) for R&D and model validation on local datasets.
- Drone-service companies for thermal capture integration.
- Cloud/AI partner programmes for start-up credits (e.g., NVIDIA Inception, AWS Activate).
- Insurers exploring premium discounts for continuously-monitored assets.

**Funding roadmap:**

- **Phase 1 — Product hardening:** grants and incubators (ICTA Spiralation, SLASSCOM, university funds).
- **Phase 2 — Pilot portfolio:** CSR/corporate innovation budgets of industrial groups with big rooftop portfolios.
- **Phase 3 — Scale:** VC/impact investment targeting climate-tech; development-finance innovation grants.

**Government incentives leveraged:** renewable-energy digitalisation programmes, SME tech-adoption subsidies, export-services tax treatment for regional SaaS.

---

## 5. IMPLEMENTATION

### 5.1 Tech Stack (Overview)

- **Electrical diagnosis:** tuned Random Forest classifier over engineered features (string powers, voltage/current ratios) built from raw inverter readings; SHAP TreeExplainer supplies per-prediction attributions served to the UI.
- **Thermal diagnosis:** deep CNN (Keras) classifying hotspot presence/severity from uploaded thermal images.
- **Localisation:** CNN-BiLSTM pair processing 32-string inverter frames to classify fault type and identify faulty strings; a DenseNet121-family hotspot localiser returns bounding boxes and annotated overlays for images.
- **Rectification:** XGBoost-backed pipeline with a Q-value-ranked action recommender producing best-action, cost and downtime estimates.
- **API:** Python Flask REST service, JWT authentication with role claims, SQLite persistence (users, predictions, logs, chat history), CORS-enabled for the SPA, OpenAPI docs endpoint.
- **Frontend:** Next.js 16 (React 19) App Router, CSS-module design system with light/night themes, Recharts visualisations, lucide iconography, localStorage-backed session and activity log.
- **Assistant:** provider-agnostic LLM service (OpenAI / Gemini / Claude / Ollama) fed bounded page context server-side.
- **Delivery:** Docker images, GitHub Actions CI (ruff, pytest, frontend lint/build, image build), Railway (API) + Vercel (frontend).
- **Models/artefacts:** distributed via HuggingFace Hub, lazily downloaded and cached.

### 5.2 Impact on Stakeholders

- **Solar owners** — recovered yield, lower bills, documented asset health, reduced fire risk from hotspots.
- **O&M companies & technicians** — fewer blind truck rolls; severity-ranked schedules; explanations that teach juniors.
- **Installers/EPCs** — differentiation through post-install care; fewer warranty disputes thanks to logged evidence.
- **Insurers & financiers** — objective risk data; healthier financed assets.
- **Environment & society** — more clean energy from existing panels; safer rooftops; local high-skill jobs.
- **Investors & developers** — recurring SaaS revenue in a structurally growing market.

### 5.3 Real-World Scenarios & User Journey

*A factory in Kotugoda runs a 500 kW rooftop array under net metering.* Monthly production quietly drops 8%. No alarm exists for "slightly low," so nothing happens — for months.

Now introduce OpenPVisor Insight: the O&M contractor uploads last week's inverter export (CSV). Within seconds the dashboard flags **Shadowing** on specific rows with 92% confidence; clicking any flagged row shows SHAP attributions — voltage ratio depressed while irradiance was normal. Switching to Localisation, the 32-string heatmap highlights strings **S4 and S17** in red. The technician cross-checks with a recent drone thermal photo; the hotspot localiser draws the affected module region with a bounding box. Severity reads **Medium–High**. The Rectification advisor ranks actions: *"Trim vegetation / re-tension mounting"* (low cost, zero downtime) above *"Replace bypass diode"* — with costs and downtime attached, best action highlighted. The fix is scheduled once, correctly. Yield recovers; the case study becomes a sales asset.

*(Flow chart of the detect → localise → grade → prescribe process can be inserted here, mirroring the reference document.)*

### 5.4 Prototype Roadmap

**Phase 1: Research & Design (Months 1–2)** — *Completed*
Dataset curation and labelling; training/tuning RF, CNN, CNN-BiLSTM and XGBoost models; SHAP integration design; UX wireframes; architecture and security design (JWT roles).

**Phase 2: Core Build (Months 3–5)** — *Completed*
Flask API with all endpoints; Next.js dashboard parity for every Streamlit screen; assistant widget with history persistence; CI pipeline; containerised deployment to Railway + Vercel.

**Phase 3: Beta & Refinement (Months 6–7)**
Pilot with 3–5 design partners; collect real-world CSVs/images to broaden training distributions; dedicated severity endpoint exposing the XGBoost regressor; performance dashboards; hardening (rate limits, audit logs).

**Post-MVP Roadmap (Next 6–12 Months)**
- **v1.1:** continuous ingestion via inverter APIs; alerting (email/WhatsApp); report-PDF exports.
- **v1.2:** mobile capture app (photo → instant diagnosis); drone-flyover batch import.
- **v2.0:** fleet benchmarking analytics; insurer API; regional expansion.

---

## 6. ADDITIONAL AND SUPPORTIVE MATERIALS

**References** *(verify and format in IEEE style before submission; replace bracketed items with the exact sources you used)*

- International Energy Agency (IEA) / IEA-PVPS — Photovoltaics power-system programme reports on PV module reliability and failure modes.
- U.S. National Renewable Energy Laboratory (NREL) — PV module field-failure and reliability studies.
- Lundberg, L. et al. — *A Review of Large-Scale Photovoltaic System Production Fault Detection* (IEEE Access).
- Original SHAP paper — Lundberg & Lee (2017), *A Unified Approach to Interpreting Model Predictions*.
- YOLO/CNN thermal-inspection papers for PV hotspot detection (select 1–2 from your literature review).
- Sri Lanka Sustainable Energy Authority (SLSEA) — Rooftop solar programme statistics.
- Your own SRS/design documents (`docs/SRS_Group_22.pdf`, DSGP final report) for project-specific facts.

**Appendices available on request:** system architecture document, API specification (auto-generated `/docs`), test reports, Figma/UI screenshots, demo video.

---

## 7. TEAM

| # | Name | Role | Email | Contact |
|---|------|------|-------|---------|
| 1 | *[Leader name]* | Team Leader | [email] | [phone] |
| 2 | Mohamed Razik Seyed Rumaiz | Member | mrsrumaiz2007@gmail.com | 0778180881 |
| 3 | *[name]* | Member | [email] | [phone] |
| 4 | *[name]* | Member | [email] | [phone] |
| 5 | *[name]* | Member | [email] | [phone] |

*NICs to be added per submission template requirements.*

---

*Organized by the IEEE Student Branch of IIT in collaboration with the IEEE Computer Society Student Branch Chapter of IIT, IEEE Robotics and Automation Society Student Branch of IIT, IEEE Computational Intelligence Society Student Branch of IIT and the IEEE Women In Engineering Affinity Group of IIT — IDEATE SUBMISSION*
