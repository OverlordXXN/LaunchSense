import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Kickstarter Success Predictor", layout="wide")

st.title("Kickstarter Project Viability Analyzer")
st.markdown("Enter your project parameters below to get success predictions and goal optimization.")

API_BASE_URL = "http://localhost:8000"

@st.cache_data(ttl=3600)
def fetch_categories_map():
    """Fetches the dataset-derived category/subcategory structure from the backend API."""
    try:
        resp = requests.get(f"{API_BASE_URL}/categories", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.warning(f"Failed to load dynamic categories from API: {e}. Using fallback.")
        return {
            "Technology": ["Web", "Hardware", "Gadgets"],
            "Games": ["Tabletop Games", "Video Games"],
            "Art": ["Painting", "Digital Art"]
        }

categories_map = fetch_categories_map()
# Sort categories alphabetically for better UX
sorted_categories = sorted(list(categories_map.keys()))

# Create main Dashboard Layout
main_col1, main_col2 = st.columns([1, 2], gap="large")

with main_col1:
    st.header("Project Inputs")
    st.markdown("Configure your campaign metrics.")
    
    col1, col2 = st.columns(2)
    with col1:
        goal = st.number_input("Goal (USD)", min_value=1.0, value=5000.0, step=100.0, help="Amount you are trying to raise.")
        category = st.selectbox("Category", sorted_categories)
        subcat_options = sorted(categories_map.get(category, []))
        subcategory = st.selectbox("Subcategory", subcat_options)

    with col2:
        launch_month = st.selectbox("Launch Month", list(range(1, 13)), help="1=Jan, 12=Dec")
        launch_day_of_week = st.selectbox("Launch Day", list(range(0, 7)), help="0=Monday, 6=Sunday")
        campaign_duration = st.slider("Duration (days)", min_value=7, max_value=60, value=30)
        
    st.write("") # Spacer
    submit_button = st.button("Predict Success", type="primary", use_container_width=True)

with main_col2:
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
            # LAYER 1: Prediction
            st.header("Prediction")
            with st.spinner("Analyzing project parameters..."):
                predict_resp = requests.post(f"{API_BASE_URL}/predict", json=payload, timeout=10)
                predict_resp.raise_for_status()
                predict_data = predict_resp.json()
                
                prob = predict_data.get("success_probability", 0) * 100
                pred_class = predict_data.get("predicted_class", "Unknown")
                
                mcol1, mcol2 = st.columns(2)
                mcol1.metric("Predicted Success Probability", f"{prob:.2f}%")
                mcol2.metric("Predicted Outcome", pred_class)
                
                # Human-readable insight
                if prob >= 70:
                    st.success("This project structure looks highly viable! Proceed to optimization for final tweaks.")
                elif prob >= 40:
                    st.info("This project has moderate chances. Review the feature breakdown below to see what is holding it back.")
                else:
                    st.error("This project structure is risky. Consider drastically altering the goal, duration, or timing.")
                
            st.divider()

            # LAYER 2: Goal Optimization
            st.header("Optimization")
            with st.spinner("Optimizing funding goal..."):
                optimize_resp = requests.post(f"{API_BASE_URL}/optimize", json=payload, timeout=10)
                optimize_resp.raise_for_status()
                opt_data = optimize_resp.json()
                
                rec_goal = opt_data.get("recommended_goal", 0)
                exp_prob = opt_data.get("expected_success_probability", 0) * 100
                improve = opt_data.get("improvement_over_original", 0) * 100
                
                ocol1, ocol2, ocol3 = st.columns(3)
                ocol1.metric("Recommended Goal", f"${rec_goal:,.0f}")
                ocol2.metric("Expected Probability", f"{exp_prob:.2f}%")
                ocol3.metric("Improvement Potential", f"+{improve:.2f}%" if improve > 0 else f"{improve:.2f}%")
                
                goal_analysis = opt_data.get("goal_analysis", [])
                if goal_analysis:
                    with st.expander("View Probability Curve"):
                        df_goals = pd.DataFrame(goal_analysis)
                        df_goals["goal"] = pd.to_numeric(df_goals["goal"])
                        df_goals["probability"] = pd.to_numeric(df_goals["probability"]) * 100
                        df_goals = df_goals.set_index("goal")
                        
                        st.line_chart(df_goals["probability"])
                        st.caption("How likelihood of success drops as your requested funding goal increases.")
                
            st.divider()
            
            # LAYER 3: Feature Explanation (Waterfall)
            st.header("Why this prediction?")
            st.write("Understand how individual parameters positively or negatively swung the AI's final decision over the category's base rate.")
            
            contributions = predict_data.get("feature_contributions", {})
            if contributions:
                import math
                import matplotlib.pyplot as plt
                
                final_prob = prob / 100.0
                p = max(min(final_prob, 0.9999), 0.0001)
                final_log_odds = math.log(p / (1 - p))
                
                total_impact = sum(contributions.values())
                base_log_odds = final_log_odds - total_impact
                base_prob = 1 / (1 + math.exp(-base_log_odds))
                
                sorted_contribs = sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)
                
                names = ["Base Rate"]
                impacts = [base_prob]
                colors = ['#808080']  # Gray
                
                current_log_odds = base_log_odds
                current_prob = base_prob
                
                for name, impact in sorted_contribs:
                    new_log_odds = current_log_odds + impact
                    new_prob = 1 / (1 + math.exp(-new_log_odds))
                    prob_diff = new_prob - current_prob
                    
                    names.append(name.replace('_', '\n'))
                    impacts.append(prob_diff)
                    colors.append('#00cc66' if prob_diff > 0 else '#ff4d4d')
                    
                    current_log_odds = new_log_odds
                    current_prob = new_prob
                    
                names.append("Final\nProbability")
                impacts.append(current_prob)
                colors.append('#3366ff')  # Blue

                fig, ax = plt.subplots(figsize=(8, 4))
                running_totals = [0.0]
                current_total = base_prob
                
                for i in range(1, len(impacts)-1):
                    if impacts[i] < 0:
                        current_total += impacts[i]
                        running_totals.append(current_total)
                    else:
                        running_totals.append(current_total)
                        current_total += impacts[i]
                
                running_totals.append(0)
                ax.bar(names, [abs(x) for x in impacts], bottom=running_totals, color=colors, edgecolor='black')
                
                ax.set_ylim(0, 1.05)
                vals = ax.get_yticks()
                ax.set_yticklabels([f"{v*100:.0f}%" for v in vals])
                
                plt.xticks(rotation=45, ha='right', fontsize=9)
                plt.tight_layout()
                
                st.pyplot(fig)
            else:
                st.info("No feature contribution data returned from the API.")
                
            st.divider()
                
            # LAYER 4: Similar Projects Context
            st.header("Historical Context")
            st.write("Compare your idea against identical real-world campaigns from our dataset.")
            with st.spinner("Finding similar historical projects..."):
                sim_resp = requests.post(f"{API_BASE_URL}/similar-projects", json=payload, timeout=5)
                sim_resp.raise_for_status()
                sim_data = sim_resp.json()
                
                count = sim_data.get("similar_projects_found", 0)
                if count > 0:
                    conf = sim_data.get("confidence", "Unknown")
                    success_rate = sim_data.get("historical_success_rate", 0) * 100
                    avg_goal = sim_data.get("average_goal", 0)
                    avg_duration = sim_data.get("average_duration", 0)
                    
                    st.markdown(f"**{count:,}** mathematically similar historical projects found (`{conf}` confidence).")
                    
                    scol1, scol2, scol3 = st.columns(3)
                    scol1.metric("Historical Win Rate", f"{success_rate:.1f}%")
                    scol2.metric("Avg Competitor Goal", f"${avg_goal:,.0f}")
                    scol3.metric("Avg Duration", f"{avg_duration:.0f} days")
                    
                    if success_rate < prob:
                        st.caption("✅ Awesome! Your predicted chances are actually **higher** than what historically similar projects managed to achieve.")
                    else:
                        st.caption("⚠️ Your predicted chances are roughly **below** the historical average of your closest peers. Tighten your budget.")
                else:
                    st.warning("No substantially similar historical projects were found in the dataset.")
                    
        except requests.exceptions.ConnectionError:
            st.error("FastAPI server not detected. Please start the API using: `uvicorn src.api.app:app --reload`")
        except Exception as e:
            st.error(f"An error occurred while calling the API: {e}")
    
    else:
        st.info("Adjust your parameters on the left and click **Predict Success** to view the comprehensive analytics dashboard.")


