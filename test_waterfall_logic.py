# test_waterfall.py
import math

def calculate_waterfall_steps(final_prob, contributions):
    if not contributions: return [], [], [], []

    # 1. Back-calculate base log_odds
    p = max(min(final_prob, 0.9999), 0.0001)
    final_log_odds = math.log(p / (1 - p))
    total_impact = sum(contributions.values())
    base_log_odds = final_log_odds - total_impact
    base_prob = 1 / (1 + math.exp(-base_log_odds))

    # 2. Sort contributions by absolute impact descending
    sorted_contribs = sorted(contributions.items(), key=lambda x: abs(x[1]), reverse=True)

    names = ["Base\nProbability"]
    impacts = [base_prob]
    colors = ['#808080']  # Gray for base

    current_log_odds = base_log_odds
    current_prob = base_prob

    for name, impact in sorted_contribs:
        # Calculate new probability after this feature's impact
        new_log_odds = current_log_odds + impact
        new_prob = 1 / (1 + math.exp(-new_log_odds))
        
        prob_diff = new_prob - current_prob
        
        # We store the "name", the "prob_diff" size
        names.append(name.replace('_', '\n'))
        impacts.append(prob_diff)
        colors.append('#00cc66' if prob_diff > 0 else '#ff4d4d')
        
        current_log_odds = new_log_odds
        current_prob = new_prob
        
    # Append final
    names.append("Final\nPrediction")
    impacts.append(current_prob)  # height of final is the full prob
    colors.append('#3366ff')

    return names, impacts, colors

# Test data
contributions = {
    'goal': -0.1,
    'goal_realism_score': 0.2,
    'category_success_rate': 0.05,
    'subcategory_success_rate': 0.15,
    'competition_density': -0.05,
    'launch_month': 0.0,
    'launch_day_of_week': 0.0,
    'campaign_duration': -0.2
}
final_prob = 0.55

names, impacts, colors = calculate_waterfall_steps(final_prob, contributions)

print("Names:", names)
print("Impacts:", impacts)
print("Colors:", colors)
