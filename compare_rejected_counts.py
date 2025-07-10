import pandas as pd

def parse_for_ratio(val):
    if isinstance(val, str):
        val = val.strip()
        if val.endswith('%'):
            try:
                pct = float(val.replace('%', ''))
                return pct / 100 if not pd.isna(pct) else None
            except:
                return None
    try:
        num = float(val)
        if pd.isna(num):
            return None
        if num > 1 and num <= 100:
            return num / 100
        return num
    except:
        return None

# Load v11
v11 = pd.read_csv('2025_Predictions_All_Issuers_v11.csv')
# Find the correct ForRatioAmongVoted_true column (case-insensitive)
for col in v11.columns:
    if col.strip().lower() == 'forratioamongvoted_true':
        forratio_col = col
        break
else:
    raise Exception('No ForRatioAmongVoted_true column found!')

# Count rejected proposals in v11
rejected_v11 = v11[v11[forratio_col] < 0.5]

# Print proposal text and share counts for each rejected proposal in v11
share_cols = [
    'true_for_shares',
    'true_against_shares',
    'true_abstain_shares',
    'true_unvoted_shares'
]
proposal_col = None
for col in v11.columns:
    if col.strip().lower() == 'proposal':
        proposal_col = col
        break
if not proposal_col:
    proposal_col = v11.columns[0]  # fallback to first column if not found

print("\nSample rejected proposals with share counts (v11):")
for idx, row in rejected_v11.head(20).iterrows():
    proposal_text = str(row[proposal_col]) if pd.notna(row[proposal_col]) else ''
    counts = []
    for col in share_cols:
        if col in row:
            counts.append(f"{col}: {row[col]}")
    print(f"- {proposal_text}  {{ " + ", ".join(counts) + " }}")

# Load v9
v9 = pd.read_csv('2025_Predictions_All_Issuers_v9.csv')
for col in v9.columns:
    if col.strip().lower() == 'forratioamongvoted_true':
        forratio_col_v9 = col
        break
else:
    raise Exception('No ForRatioAmongVoted_true column found in v9!')
# Count rejected proposals in v9
rejected_v9 = v9[v9[forratio_col_v9] < 0.5]
print(f"v9: Total rows: {len(v9)} | Rejected proposals: {len(rejected_v9)}")
