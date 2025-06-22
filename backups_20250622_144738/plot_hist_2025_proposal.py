import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# Load data
df = pd.read_csv('2025_proposal_35k.csv')

# Normalize column names for robustness
cols = {c.lower(): c for c in df.columns}
cat_col = cols.get('category', 'category')
subcat_col = cols.get('subcategory', 'subcategory')
forratio_true_col = cols.get('forratioamongvoted_true', 'ForRatioAmongVoted_true')
forratio_col = cols.get('forratioamongvoted', 'ForRatioAmongVoted')

groups = df.groupby([cat_col, subcat_col])

# Output directory
os.makedirs('hist_2025', exist_ok=True)

for (cat, subcat), group in groups:
    vals_true = group[forratio_true_col].dropna().astype(float)
    vals = group[forratio_col].dropna().astype(float)
    if len(vals_true) == 0 and len(vals) == 0:
        continue
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
    # ForRatioAmongVoted_true
    if len(vals_true) > 0:
        axes[0].hist(vals_true, bins=20, color='#4daf4a', alpha=0.85, edgecolor='black', range=(0, 1))
    axes[0].set_title('ForRatioAmongVoted_true')
    axes[0].set_xlabel('Value')
    axes[0].set_ylabel('Count')
    axes[0].set_xlim(0, 1)
    axes[0].axvline(x=0.5, color='red', linestyle='--', linewidth=2, alpha=0.8)
    axes[0].text(0.25, axes[0].get_ylim()[1]*0.9, 'Rejection', ha='center', fontsize=10, color='red')
    axes[0].text(0.75, axes[0].get_ylim()[1]*0.9, 'Approval', ha='center', fontsize=10, color='green')
    # ForRatioAmongVoted
    if len(vals) > 0:
        axes[1].hist(vals, bins=20, color='#1c7be4', alpha=0.85, edgecolor='black', range=(0, 1))
    axes[1].set_title('ForRatioAmongVoted')
    axes[1].set_xlabel('Value')
    axes[1].set_xlim(0, 1)
    axes[1].axvline(x=0.5, color='red', linestyle='--', linewidth=2, alpha=0.8)
    axes[1].text(0.25, axes[1].get_ylim()[1]*0.9, 'Rejection', ha='center', fontsize=10, color='red')
    axes[1].text(0.75, axes[1].get_ylim()[1]*0.9, 'Approval', ha='center', fontsize=10, color='green')
    # Main title
    fig.suptitle(f'Comparison of True Approval Ratio vs Predicted Approval Ratio\nCategory: {cat} | Subcategory: {subcat}', fontsize=14)
    plt.tight_layout(rect=[0, 0.03, 1, 0.92])
    # Save
    safe_cat = str(cat).replace('/', '_').replace(' ', '_')
    safe_subcat = str(subcat).replace('/', '_').replace(' ', '_')
    fname = f'hist_2025/hist_{safe_cat}__{safe_subcat}.png'
    plt.savefig(fname)
    plt.close(fig)
print('Done. All histograms saved to hist_2025/')
