import pandas as pd

# Path to the CSV file
data_path = "2025_Predictions_All_Issuers_v11.csv"

# Load the CSV file
df = pd.read_csv(data_path)
print(df.shape)
# Apply the filter conditions
filtered = df[
    (df['mgmt_rec'] == 'F') &
    (df['proposal_type'] == 'MG') &
    (df['prediction_correct'] == False) &
    (df['approved'] == False)
]

# Output the filtered results to a new CSV file
filtered.to_csv("filtered_results.csv", index=False)

# Print the number of results and show the first few rows
print(f"Filtered rows: {len(filtered)}")
print(filtered.head())
