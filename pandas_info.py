import pandas as pd
df = pd.read_csv('data/raw/kaggle/kickstarter_projects.csv')
with open('info.txt', 'w', encoding='utf-8') as f:
    df.info(buf=f)
    f.write('\n\n')
    f.write(df.head(2).to_string())
    f.write('\n\nMissing values:\n')
    f.write(df.isna().sum().to_string())
