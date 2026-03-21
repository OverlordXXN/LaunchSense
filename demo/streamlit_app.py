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
    import time
    for attempt in range(2):
        try:
            resp = requests.get(f"{API_BASE_URL}/categories", timeout=20)
            resp.raise_for_status()
            data = resp.json()
            
            mapping = data.get("mapping", data)
            source = data.get("source", "unknown")
            
            if source == "fallback":
                st.warning("⚠️ Could not load dynamic categories from the backend dataset. Using limited fallback options.")
                
            return mapping
        except Exception as e:
            if attempt < 1:
                time.sleep(1)
                continue
            st.warning(f"Failed to connect to dynamic categories API: {e}. Using offline fallback.")
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
        category = st.selectbox("Category", sorted_categories, index=None, placeholder="Search categories...")
        subcat_options = sorted(categories_map.get(category, [])) if category else []
        subcategory = st.selectbox("Subcategory", subcat_options, index=None, placeholder="Search subcategories...")

    with col2:
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        month_name = st.selectbox("Launch Month", months, index=4, help="Select the month your campaign will go live.")
        launch_month = months.index(month_name) + 1
        
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_name = st.selectbox("Launch Day", days, index=1, help="Select the day of the week your campaign will go live.")
        launch_day_of_week = days.index(day_name)
        campaign_duration = st.slider("Duration (days)", min_value=7, max_value=60, value=30)
        
    st.write("") # Spacer
    submit_button = st.button("Predict Success", type="primary", use_container_width=True, disabled=not (category and subcategory))

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
                confidence = predict_data.get("confidence_level", "Unknown")
                warnings = predict_data.get("warning_flags", [])
                
                # Surface dangerous API bounds
                if warnings:
                    for w in warnings:
                        st.warning(w)
                
                mcol1, mcol2, mcol3 = st.columns(3)
                mcol1.metric("Predicted Success Probability", f"{prob:.2f}%")
                mcol2.metric("Predicted Outcome", pred_class)
                mcol3.metric("Model Confidence", confidence)
                
                # Human-readable insight
                if prob >= 70:
                    st.success("This project structure looks highly viable! Proceed to optimization for final tweaks.")
                elif prob >= 40:
                    st.info("This project has moderate chances. Review the feature breakdown below to see what is holding it back.")
                else:
                    st.error("This project structure is risky. Consider drastically altering the goal, duration, or timing.")
                
                # Model disclaimer (Phase 15 UX)
                st.caption("Prediction based on modern Kickstarter trends (2020+)")
                
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
                    
                    if conf == "Low" or avg_goal <= 0:
                        st.caption("ℹ️ Historical data is sparse or low confidence for this specific setup. Use these averages purely as rough estimates.")
                    elif rec_goal > (avg_goal * 1.10):
                        st.caption("⚠️ Your recommended goal is higher than similar projects. This suggests your project may require stronger positioning or differentiation to succeed at this level.")
                    elif rec_goal < (avg_goal * 0.90):
                        st.caption("✅ Reducing your goal aligns with historical trends and improves your chances of success.")
                    else:
                        st.caption("✅ Your goal is well aligned with historical successful campaigns.")
                else:
                    st.warning("No substantially similar historical projects were found in the dataset.")
                    
            # LAYER 5: Scenario Comparison
            st.divider()
            st.header("Scenario Comparison")
            st.write("Test multiple goal values simultaneously to explicitly examine success probability decay.")
            
            compare_str = st.text_input("Alternative Goals (comma-separated USD)", value=f"{int(goal*0.5)}, {int(goal*0.75)}, {int(goal)}, {int(goal*1.25)}, {int(goal*1.5)}")
            
            if compare_str:
                try:
                    comp_goals = [float(g.strip()) for g in compare_str.split(',') if g.strip()]
                    comp_results = []
                    
                    with st.spinner("Calculating scenarios..."):
                        for cg in sorted(comp_goals):
                            cg_payload = payload.copy()
                            cg_payload["goal"] = cg
                            
                            c_resp = requests.post(f"{API_BASE_URL}/predict?include_contributions=false", json=cg_payload, timeout=5)
                            if c_resp.status_code == 200:
                                c_data = c_resp.json()
                                comp_results.append({
                                    "Goal": cg,
                                    "Probability": c_data.get("success_probability", 0) * 100
                                })
                                
                    if comp_results:
                        df_comp = pd.DataFrame(comp_results)
                        df_comp["GoalStr"] = df_comp["Goal"].apply(lambda x: f"${x:,.0f}")
                        df_comp = df_comp.set_index("GoalStr")
                        
                        st.line_chart(df_comp["Probability"])
                        
                except Exception as e:
                    st.warning(f"Failed to generate scenarios: {e}")
                    
        except requests.exceptions.ConnectionError:
            st.error("FastAPI server not detected. Please start the API using: `uvicorn src.api.app:app --reload`")
        except Exception as e:
            st.error(f"An error occurred while calling the API: {e}")
    
    else:
        st.info("Adjust your parameters on the left and click **Predict Success** to view the comprehensive analytics dashboard.")


