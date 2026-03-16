import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Kickstarter Success Predictor", layout="wide")

st.title("Kickstarter Project Viability Analyzer")
st.markdown("Enter your project parameters below to get success predictions and goal optimization.")

API_BASE_URL = "http://localhost:8000"

# Hardcoded common categories for the demo
CATEGORIES = [
    "Technology", "Art", "Games", "Design", "Film & Video", 
    "Music", "Publishing", "Food", "Fashion", "Comics"
]
SUBCATEGORIES = [
    "Web", "Hardware", "Tabletop Games", "Video Games", "Painting", 
    "Documentary", "Nonfiction", "Restaurants", "Apparel", "Gadgets", "Comic Books"
]

# SECTION 1 — Project Inputs
st.header("Project Inputs")
with st.form("project_inputs_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        goal = st.number_input("Goal (USD)", min_value=1.0, value=5000.0, step=100.0)
        category = st.selectbox("Category", CATEGORIES)
        subcategory = st.selectbox("Subcategory", SUBCATEGORIES)

    with col2:
        launch_month = st.selectbox("Launch Month", list(range(1, 13)))
        launch_day_of_week = st.selectbox("Launch Day of Week (0=Mon, 6=Sun)", list(range(0, 7)))
        campaign_duration = st.slider("Campaign Duration (days)", min_value=7, max_value=60, value=30)
        
    submit_button = st.form_submit_button("Predict Success")

if submit_button:
    payload = {
        "goal": goal,
        "category": category,
        "subcategory": subcategory,
        "launch_month": launch_month,
        "launch_day_of_week": launch_day_of_week,
        "campaign_duration": campaign_duration
    }
    
    try:
        # SECTION 2 — Prediction Results
        st.header("Prediction Results")
        with st.spinner("Analyzing project parameters..."):
            predict_resp = requests.post(f"{API_BASE_URL}/predict", json=payload, timeout=10)
            predict_resp.raise_for_status()
            
            predict_data = predict_resp.json()
            
            prob = predict_data.get("success_probability", 0) * 100
            pred_class = predict_data.get("predicted_class", "Unknown")
            
            col1, col2 = st.columns(2)
            col1.metric("Predicted Success Probability", f"{prob:.2f}%")
            col2.metric("Predicted Class", pred_class)
            
        # SECTION 3 — Goal Optimization
        st.header("Goal Optimization")
        with st.spinner("Optimizing funding goal..."):
            optimize_resp = requests.post(f"{API_BASE_URL}/optimize", json=payload, timeout=10)
            optimize_resp.raise_for_status()
            
            opt_data = optimize_resp.json()
            
            rec_goal = opt_data.get("recommended_goal", 0)
            exp_prob = opt_data.get("expected_success_probability", 0) * 100
            improve = opt_data.get("improvement_over_original", 0) * 100
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Recommended Goal", f"${rec_goal:,.2f}")
            col2.metric("Expected Probability", f"{exp_prob:.2f}%")
            col3.metric("Improvement", f"+{improve:.2f}%" if improve >= 0 else f"{improve:.2f}%")
            
        # SECTION 4 — Feature Explanation
        st.header("Feature Contributions")
        contributions = predict_data.get("feature_contributions", {})
        
        if contributions:
            # Convert to DataFrame for visualization
            df_contrib = pd.DataFrame(list(contributions.items()), columns=["Feature", "Contribution"])
            df_contrib = df_contrib.sort_values(by="Contribution", ascending=True)
            
            # Create color list: positive in green, negative in red
            df_contrib['Color'] = df_contrib['Contribution'].apply(lambda x: '#00cc66' if x > 0 else '#ff4d4d')
            
            st.bar_chart(
                df_contrib, 
                x="Feature",
                y="Contribution",
                color="Color"
            )
        else:
            st.info("No feature contribution data returned from the API.")
            
    except requests.exceptions.ConnectionError:
        st.error("FastAPI server not detected. Please start the API using: `uvicorn src.api.app:app --reload`")
    except Exception as e:
        st.error(f"An error occurred while calling the API: {e}")

