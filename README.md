# 🚀 LaunchSense --- AI Crowdfunding Success Simulator
> 🚀 End-to-end machine learning product for predicting and optimizing crowdfunding success.
## 🇬🇧 English

**LaunchSense** is an end-to-end machine learning system designed to
evaluate the viability of crowdfunding campaigns *before launch*.

It combines predictive modeling, optimization, explainability, and
historical benchmarking into a single interactive decision-making tool.

------------------------------------------------------------------------

### 🎯 Problem

Launching a crowdfunding campaign is high-risk.

Creators must decide: - What funding goal to set - How long to run the
campaign - When to launch

Most decisions are based on intuition rather than data.

------------------------------------------------------------------------

### 💡 Solution

LaunchSense provides:

-   🎯 Success Probability Prediction (ML-based)
-   📉 Goal Optimization Engine
-   🧠 Explainability (SHAP insights)
-   📊 Scenario Simulation
-   📚 Historical Benchmarking
-   ⚠️ Confidence & Risk Signals

------------------------------------------------------------------------

### 🔥 Key Insight

During development, a concept drift issue was identified:

Older crowdfunding data does not reflect current market conditions.

By redesigning the training strategy to focus on modern campaigns (\>=
2020):

Accuracy improved from \~67% → \~80%

------------------------------------------------------------------------

### 🧱 Architecture

Data Sources → Data Pipeline → ML Model → FastAPI → Streamlit UI

------------------------------------------------------------------------

### 🖥️ Features

-   Interactive UI (Streamlit)
-   Real-time predictions
-   Goal recommendation system
-   Probability curve simulation
-   SHAP-based explainability
-   Similar project comparison
-   Drift-aware modeling
-   Resilient API architecture

------------------------------------------------------------------------

### ▶️ Run Locally

``` bash
uvicorn src.api.app:app --reload
streamlit run demo/streamlit_app.py
```

------------------------------------------------------------------------

### 🛠 Tech Stack

Python · XGBoost · Pandas · FastAPI · Streamlit · SHAP

------------------------------------------------------------------------

### ⚠️ Disclaimer

This project is not affiliated with Kickstarter. Predictions are based
on historical data and should not be considered financial advice.

------------------------------------------------------------------------

## 🇪🇸 Español

**LaunchSense** es un sistema completo de machine learning diseñado para
evaluar la viabilidad de campañas de crowdfunding antes de su
lanzamiento.

------------------------------------------------------------------------

### 🎯 Problema

Lanzar una campaña de crowdfunding implica alto riesgo.

Las decisiones clave suelen basarse en intuición.

------------------------------------------------------------------------

### 💡 Solución

LaunchSense ofrece:

-   Predicción de éxito
-   Optimización del objetivo
-   Explicabilidad (SHAP)
-   Simulación de escenarios
-   Comparación histórica

------------------------------------------------------------------------

### 🔥 Insight clave

Se detectó concept drift:

Datos antiguos ≠ mercado actual

Entrenando con datos recientes:

Precisión: \~67% → \~80%

------------------------------------------------------------------------

### ▶️ Ejecución

``` bash
uvicorn src.api.app:app --reload
streamlit run demo/streamlit_app.py
```

------------------------------------------------------------------------

### ⚠️ Aviso

No afiliado a Kickstarter. Uso educativo/prototipo.
