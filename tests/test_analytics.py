import os
import sys
import logging

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SRC_DIR, '..'))
sys.path.append(os.path.join(ROOT_DIR, 'src'))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

from analytics.analytics_engine import build_analytics_features

def test_analytics():
    df = build_analytics_features()

    if df.empty:
        print("Error: DataFrame is empty.")
        sys.exit(1)

    print("\n--- Analytics Feature Matrix Computed ---")
    print(f"Shape: {df.shape}")

    columns_to_inspect = [
        'name', 'category', 'goal', 'goal_realism_score',
        'category_success_rate', 'competition_density',
        'average_pledge_per_backer', 'is_successful'
    ]

    print("\nHead of computed ML features (selected columns):")
    print(df[columns_to_inspect].head(5).to_string())

    print("\nDescribe summary of new features:")
    feature_cols = [
        'category_success_rate', 'subcategory_success_rate',
        'goal_realism_score', 'competition_density',
        'average_pledge_per_backer'
    ]
    print(df[feature_cols].describe().to_string())

    print("\nSuccess distribution:")
    print(df["is_successful"].value_counts(normalize=True))


if __name__ == '__main__':
    test_analytics()