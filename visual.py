import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def format_number(num):
    if abs(num) >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif abs(num) >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return f"{int(num)}"

def clean_key(key):
    key_str = str(key)
    if key_str.endswith('.0'):
        key_str = key_str[:-2]
    return key_str

def plot_stacked_area_and_summarize(agg, key):
    # agg: pre-aggregated DataFrame (grouped by ['final_key', 'account_hash_key', 'Target_encoded'])
    fk = key
    agg_fk = agg[agg['final_key'] == fk]
    # Precompute total shares per account_hash_key
    account_shares = agg_fk.groupby('account_hash_key', as_index=False)['shares_summable'].sum()
    account_shares = account_shares.sort_values('shares_summable', ascending=False)
    account_shares['cum_share'] = account_shares['shares_summable'].cumsum()
    total_share = account_shares['shares_summable'].sum()

    bins = np.linspace(0, total_share, 11)[1:]  # 10 bins
    area_data = []
    total_length = []
    group_counts = []
    group_shares = []
    group_accounts = []

    account_order = account_shares['account_hash_key'].tolist()
    account_target_shares = agg_fk.pivot_table(
        index='account_hash_key', columns='Target_encoded', values='shares_summable', fill_value=0
    )

    for i, b in enumerate(bins):
        cutoff_idx = np.searchsorted(account_shares['cum_share'].values, b, side='right')
        if cutoff_idx == 0:
            cutoff_idx = 1
        accounts_in_bin = account_order[:cutoff_idx]
        bin_shares = account_shares.iloc[:cutoff_idx]['shares_summable'].sum()
        total_length.append(bin_shares / total_share if total_share else 0)
        bin_target_shares = account_target_shares.loc[accounts_in_bin].sum()
        shares_1 = bin_target_shares.get(1, 0)
        shares_2 = bin_target_shares.get(2, 0)
        shares_0 = bin_target_shares.get(0, 0)
        total_bin_share = shares_1 + shares_2 + shares_0
        pct_1 = shares_1 / total_bin_share if total_bin_share else 0
        pct_2 = shares_2 / total_bin_share if total_bin_share else 0
        pct_0 = shares_0 / total_bin_share if total_bin_share else 0
        area_data.append([pct_1, pct_2, pct_0])
        group_counts.append([shares_1, shares_2, shares_0])
        group_shares.append([pct_1, pct_2, pct_0])
        acc_1 = (account_target_shares.loc[accounts_in_bin][1] > 0).sum() if 1 in account_target_shares.columns else 0
        acc_2 = (account_target_shares.loc[accounts_in_bin][2] > 0).sum() if 2 in account_target_shares.columns else 0
        acc_0 = (account_target_shares.loc[accounts_in_bin][0] > 0).sum() if 0 in account_target_shares.columns else 0
        group_accounts.append([acc_1, acc_2, acc_0])

    area_data = np.array(area_data)
    group_counts = np.array(group_counts)
    group_shares = np.array(group_shares)
    group_accounts = np.array(group_accounts)
    y = np.arange(1, 11)

    colors = ['#4daf4a', '#e41a1c', '#bbbbbb']  # For 1, 2, 0
    labels = ['For (1)', 'Against (2)', 'Unvoted (0)']

    fig, ax = plt.subplots(figsize=(15, 7))
    left = np.zeros(len(y))
    for i in range(3):
        ax.barh(y, area_data[:, i] * np.array(total_length), left=left, color=colors[i], label=labels[i])
        left += area_data[:, i] * np.array(total_length)

    ax.set_yticks(y)
    ax.set_yticklabels([f'{i*10}%' for i in range(1, 11)])
    ax.set_xlabel('Share Composition (True % of Total Shares)')
    ax.set_ylabel('Cumulative Shareholder Percentile')
    ax.set_title("Share Composition by Cumulative Shareholders for Proposal " + clean_key(fk))
    ax.legend(loc='upper right')
    ax.invert_yaxis()

    min_width_for_each = 0.08

    # Annotate shares counts and percentages
    for idx in range(len(y)):
        bar_total = np.sum(area_data[idx, :] * total_length[idx])
        widths = area_data[idx, :] * total_length[idx]
        if bar_total < 0.25:
            text = []
            for i in range(3):
                class_label = f"({i if i != 2 else 0})"
                if group_counts[idx, i] > 0:
                    text.append(f"{class_label} {format_number(group_counts[idx, i])}, {group_shares[idx, i]*100:.1f}%")
            ax.text(bar_total + 0.01, y[idx], ', '.join(text), va='center', fontsize=10)
        else:
            left_val = 0
            for i in range(3):
                class_label = f"({i if i != 2 else 0})"
                if widths[i] > min_width_for_each and group_counts[idx, i] > 0:
                    ax.text(left_val + widths[i]/2, y[idx], 
                            f"{class_label} {format_number(group_counts[idx, i])}, {group_shares[idx, i]*100:.1f}%", 
                            va='center', ha='center', color='black', fontsize=10)
                elif group_counts[idx, i] > 0:
                    ax.text(bar_total + 0.01, y[idx], 
                            f"{class_label} {format_number(group_counts[idx, i])}, {group_shares[idx, i]*100:.1f}%", 
                            va='center', ha='left', color=colors[i], fontsize=10)
                left_val += widths[i]

    # Annotate account counts at the right side of each bar
    for idx in range(len(y)):
        bar_total = np.sum(area_data[idx, :] * total_length[idx])
        acc_text = []
        for i in range(3):
            class_label = f"({i if i != 2 else 0})"
            if group_accounts[idx, i] > 0:
                acc_text.append(f"{class_label} {format_number(group_accounts[idx, i])}")
        if acc_text:
            ax.text(bar_total + 0.18, y[idx], " | ".join(acc_text), va='center', ha='left', color='dimgray', fontsize=10, fontweight='bold')

    plt.tight_layout()
    #plt.show()
    plt.savefig(f'images/{str(key)}.png')
    plt.close()    

def main():
    import os
    df = pd.read_csv('df_956_account_new.csv')  # changed to the correct input file
    # Ensure output directory exists
    os.makedirs('images', exist_ok=True)
    df['final_key'] = df['final_key'].replace('2268837.0_2268273.0__-1.0', '2268837.0')
    df['final_key'] = df['final_key'].astype(str)
    # Pre-aggregate once for all keys
    agg = df.groupby(['final_key', 'account_hash_key', 'Target_encoded'], as_index=False)['shares_summable'].sum()
    keys = agg['final_key'].dropna().unique()
    for key in keys:
        try:
            plot_stacked_area_and_summarize(agg, str(key))

        except Exception as e:
            print(f"Failed to plot for key {key}: {e}")

if __name__ == "__main__":
    main()

# Usage:
# summary_df = plot_stacked_area_and_summarize(df)
# print(summary_df)