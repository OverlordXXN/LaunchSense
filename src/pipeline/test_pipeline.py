import sys
from loader import load_kaggle_dataset
from normalization import unify_schemas

def load_and_normalize_dataset():
    print("Loading dataset...")
    df = load_kaggle_dataset('../../data/raw/kaggle/kickstarter_projects.csv')
    print(f"Loaded {len(df)} rows.")
    
    print("\nNormalizing dataset...")
    projects_df, project_snapshots_df = unify_schemas(historical_df=df)
    
    print(f"\nProjects DataFrame shape: {projects_df.shape}")
    print("Projects Columns:")
    print(projects_df.columns.tolist())
    print("\nProjects Head:")
    print(projects_df.head(2))
    
    print(f"\nProject Snapshots DataFrame shape: {project_snapshots_df.shape}")
    print("Snapshots Columns:")
    print(project_snapshots_df.columns.tolist())
    print("\nSnapshots Head:")
    print(project_snapshots_df.head(2))

if __name__ == '__main__':
    load_and_normalize_dataset()
