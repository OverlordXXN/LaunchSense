import csv

def analyze():
    with open('data/raw/kaggle/kickstarter_projects.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        print("Columns:", header)
        missing = {h: 0 for h in header}
        types_sample = {h: set() for h in header}
        count = 0
        for row in reader:
            count += 1
            for i, val in enumerate(row):
                if not val.strip():
                    missing[header[i]] += 1
                elif count <= 100:
                    try:
                        int(val)
                        types_sample[header[i]].add('int')
                    except ValueError:
                        try:
                            float(val)
                            types_sample[header[i]].add('float')
                        except ValueError:
                            types_sample[header[i]].add('string')
        
        print(f"\nTotal rows: {count}")
        print("\nMissing values:")
        for k, v in missing.items():
            print(f"{k}: {v}")
        
        print("\nInferred datatypes (from first 100 rows):")
        for k, v in types_sample.items():
            print(f"{k}: {', '.join(v)}")
        
analyze()
