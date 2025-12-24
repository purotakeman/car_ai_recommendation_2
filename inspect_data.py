import pandas as pd

def inspect():
    csv_paths = ["data/car_data_base.csv", "data/car_data.csv", "car_data_base.csv", "car_data.csv"]
    df = None
    for csv_path in csv_paths:
        try:
            df = pd.read_csv(csv_path, encoding="utf-8-sig")
            print(f"Loaded {csv_path}")
            break
        except:
            continue
    
    if df is not None:
        df.columns = df.columns.str.strip()
        print("Columns:", df.columns.tolist())
        target_cols = ['乗車定員', '自動車税(円)', '車種']
        existing_cols = [c for c in target_cols if c in df.columns]
        print(df[existing_cols].head(20))
        
        # Check for any non-integer seating capacity
        if '乗車定員' in df.columns:
            print("\nUnique values in 乗車定員:")
            print(df['乗車定員'].unique())
        
        # Check for Alphard records
        if '車種' in df.columns:
            alphards = df[df['車種'].str.contains('アルファード', na=False)]
            print(f"\nAlphard records found: {len(alphards)}")
            print(alphards.head())

if __name__ == "__main__":
    inspect()
