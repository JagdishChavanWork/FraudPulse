import pandas as pd

# The file name you used in your notebook
INPUT_FILE_NAME = "AIML Dataset.csv"

# The name for your new, smaller sample file
OUTPUT_FILE_NAME = "AIML_Sample_10Pct.csv"

try:
    # 1. Load the entire large dataset (this must be run locally)
    df_large = pd.read_csv("E:\FraudPulse\Data\AIML Dataset.csv", low_memory=False)

    # 2. Sample 10% of the rows randomly for our analysis
    # We use random_state=42 for reproducibility.
    df_sample = df_large.sample(frac=0.1, random_state=42)

    # 3. Save the sampled data to a new CSV file
    df_sample.to_csv(OUTPUT_FILE_NAME, index=False)

    print(f"✅ Success! Created sample file: {OUTPUT_FILE_NAME}")
    print(f"The sample has {len(df_sample):,} rows (10% of the original).")
    
except FileNotFoundError:
    print(f"Error: Make sure '{INPUT_FILE_NAME}' is in the same directory as this script.")