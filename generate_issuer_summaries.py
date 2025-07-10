#!/usr/bin/env python3
"""
Issuer Summary Automation Script

This script reads the issuer_distribution_list.csv file and simulates the 
"Show Summary" functionality from peeranalysis.html for each issuer.
It generates summaries by processing both the peer analysis dataset and 
the large dataset, then outputs a complete HTML file.
"""

import pandas as pd
import os
from datetime import datetime
import re
from collections import Counter

def parse_for_ratio(val):
    """Parse ForRatio values (handles both decimal and percentage formats)"""
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
            # If value is 45, treat as 0.45 (likely a percent without %)
            return num / 100
        return num
    except:
        return None

def escape_html(text):
    """Escape HTML special characters"""
    if pd.isna(text) or text is None:
        return ""
    text = str(text)
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;'))

def find_column(headers, patterns):
    """Find column by multiple possible patterns (case-insensitive)"""
    headers_lower = [h.lower() if h else '' for h in headers]
    for pattern in patterns:
        for i, header in enumerate(headers_lower):
            if pattern.lower() in header:
                return headers[i]
    return None

def format_approval_rate_range(rates):
    """Format approval rate range"""
    if not rates:
        return "N/A"
    rates = [r for r in rates if r is not None]
    if not rates:
        return "N/A"
    min_rate = min(rates)
    max_rate = max(rates)
    return f"{min_rate:.1%}-{max_rate:.1%}"

# Range of approval rates for failed proposals
def format_failed_approval_rate_range(rates):
    if not rates:
        return "N/A"
    rates = [r for r in rates if r is not None]
    if not rates:
        return "N/A"
    min_rate = min(rates)
    max_rate = max(rates)
    if min_rate == max_rate:
        return f"{min_rate:.1%}"
    return f"{min_rate:.1%}-{max_rate:.1%}"

def generate_issuer_summary(issuer, peer_df, large_df, norm_issuer=None):
    """Generate summary for a specific issuer"""
    print(f"\n=== Generating summary for: {issuer} ===")
    
    # Use normalized issuer name for filtering
    if norm_issuer is None:
        norm_issuer = normalize_issuer_name(issuer)
    peer_rows = peer_df[peer_df['__normalized_issuer__'] == norm_issuer] if '__normalized_issuer__' in peer_df.columns else pd.DataFrame()
    large_rows = large_df[large_df['__normalized_issuer__'] == norm_issuer] if '__normalized_issuer__' in large_df.columns else pd.DataFrame()
    
    # Debugging output
    print(f"  [DEBUG] {issuer} | normalized: {norm_issuer}")
    print(f"    Peer proposals: {len(peer_rows)} | Large dataset: {len(large_rows)}")
    if large_rows.empty and peer_rows.empty:
        print(f"No data found for {issuer}")
        return None
    
    # Find columns in peer dataset
    peer_headers = list(peer_df.columns)
    issuer_col = find_column(peer_headers, ['issuer', 'company', 'firm'])
    record_date_col = find_column(peer_headers, ['recorddate', 'record_date', 'record date', 'meetingdate', 'meeting_date'])
    job_number_col = find_column(peer_headers, ['job_number', 'jobnumber', 'job number'])
    service_col = find_column(peer_headers, ['service'])
    mgmt_rec_col = find_column(peer_headers, ['mgmt_rec', 'mgmt_recommendation'])
    proposal_col = find_column(peer_headers, ['proposal'])
    category_col = find_column(peer_headers, ['category_annotated']) or find_column(peer_headers, ['category'])
    subcategory_col = find_column(peer_headers, ['subcategory_annotated']) or find_column(peer_headers, ['subcategory'])
    
    # Find columns in large dataset
    large_headers = list(large_df.columns)
    large_issuer_col = find_column(large_headers, ['issuer', 'company', 'firm'])
    # Only use ForRatioAmongVoted_true (case-insensitive)
    large_for_ratio_col = None
    for col in large_headers:
        if col.strip().lower() == 'forratioamongvoted_true':
            large_for_ratio_col = col
            break
    if not large_for_ratio_col:
        raise ValueError("No 'ForRatioAmongVoted_true' column found in large dataset (case-insensitive match). Please check the column name.")
    
    print(f"Peer issuer column: {issuer_col}")
    print(f"Large issuer column: {large_issuer_col}")
    print(f"Large ForRatio column: {large_for_ratio_col}")
    
    # Get peer data for this issuer (using normalized column)
    # peer_rows = peer_df[peer_df[issuer_col] == issuer_name] if issuer_col else pd.DataFrame()
    # print(f"Peer rows found: {len(peer_rows)}")
    # Get large dataset data for this issuer (using normalized column)
    # large_rows = large_df[large_df[large_issuer_col] == issuer_name] if large_issuer_col else pd.DataFrame()
    # print(f"Large dataset rows found: {len(large_rows)}")
    # if len(peer_rows) == 0 and len(large_rows) == 0:
    #     print(f"No data found for {issuer_name}")
    #     return None
    
    # Extract basic info
    record_dates = []
    job_numbers = []
    services = []
    mgmt_recs = []
    
    if len(peer_rows) > 0:
        if record_date_col:
            record_dates.extend([str(d) for d in peer_rows[record_date_col].dropna().unique()])
        if job_number_col:
            job_numbers.extend([str(j) for j in peer_rows[job_number_col].dropna().unique()])
        if service_col:
            services.extend([str(s) for s in peer_rows[service_col].dropna().unique()])
        if mgmt_rec_col:
            mgmt_recs.extend([str(m) for m in peer_rows[mgmt_rec_col].dropna().unique()])
    
    # Calculate approval rates and counts from large dataset
    rejected_count = 0
    approved_count = 0
    approval_rates = []
    failed_approval_rates = []  # Store approval rates for failed proposals only

    if len(large_rows) > 0 and large_for_ratio_col:
        for _, row in large_rows.iterrows():
            for_ratio = parse_for_ratio(row[large_for_ratio_col])
            if for_ratio is not None:
                approval_rates.append(for_ratio)
                if for_ratio < 0.5:
                    rejected_count += 1
                    failed_approval_rates.append(for_ratio)
                elif for_ratio >= 0.5:
                    approved_count += 1
    
    # Get rejected proposals breakdown
    rejected_proposals = []
    rejected_categories = Counter()

    if len(large_rows) > 0 and large_for_ratio_col:
        large_category_col = find_column(large_headers, ['category'])
        # Robustly find the proposal text column (case-insensitive)
        proposal_cols = [col for col in large_headers if col.strip().lower() == 'proposal']
        if not proposal_cols:
            raise ValueError("No 'proposal' column found in large dataset (case-insensitive match). Please check the column name.")
        large_proposal_col = proposal_cols[0]
        share_cols = [
            'true_for_shares',
            'true_against_shares',
            'true_abstain_shares',
            'true_unvoted_shares'
        ]
        for _, row in large_rows.iterrows():
            for_ratio = parse_for_ratio(row[large_for_ratio_col])
            if for_ratio is not None and for_ratio < 0.5:
                proposal_text = str(row[large_proposal_col]).strip() if pd.notna(row[large_proposal_col]) else ''
                if len(proposal_text) > 200:
                    proposal_text = proposal_text[:200] + "..."
                # Add share counts in requested format, to be shown underneath in smaller text
                counts = []
                for col in share_cols:
                    if col in row:
                        try:
                            val = float(row[col])
                            val = int(round(val))
                        except (ValueError, TypeError):
                            val = row[col]
                        counts.append(f"{col}: {val}")
                if proposal_text:
                    html_proposal = escape_html(proposal_text)
                    html_counts = f'<div style="font-size: 0.85em; color: #555; margin-left: 1em;">' + ', '.join(counts) + '</div>' if counts else ''
                    rejected_proposals.append(f"{html_proposal}{html_counts}")
                if large_category_col and pd.notna(row[large_category_col]):
                    category = str(row[large_category_col]).strip()
                    rejected_categories[category] += 1
    
    # Format summary
    summary_parts = []
    
    # Basic statistics
    service_summary = ", ".join(set(services)) if services else "N/A"
    job_summary = ", ".join(set(job_numbers)) if job_numbers else "N/A"
    mgmt_summary = ", ".join(set(mgmt_recs)) if mgmt_recs else "N/A"
    
    if '(' in job_summary and service_summary != "N/A":
        service_summary = f"{service_summary} ({job_summary})"
        job_summary = job_summary  # Keep separate for job numbers section
    
    approval_rate_summary = format_approval_rate_range(approval_rates)
    failed_approval_rate_summary = format_failed_approval_rate_range(failed_approval_rates)

    summary_parts.append("    <h3>Statistics</h3>")
    summary_parts.append("    <ul>")
    summary_parts.append(f"        <li>Service Type: {service_summary}</li>")
    summary_parts.append(f"        <li>Management Recommendations: {mgmt_summary}</li>")
    summary_parts.append(f"        <li>Total Proposals: {rejected_count + approved_count}</li>")
    summary_parts.append(f"        <li>Range of Approval Rate of Failed Proposals: {failed_approval_rate_summary}</li>")
    summary_parts.append(f"        <li>Rejected Count: {rejected_count}</li>")
    summary_parts.append(f"        <li>Approved Count: {approved_count}</li>")
    summary_parts.append("    </ul>")
    
    # Record dates
    if record_dates:
        summary_parts.append("    <h3>Record Dates</h3>")
        summary_parts.append(f"    <p>{', '.join(sorted(set(record_dates)))}</p>")
    
    # Job numbers
    if job_numbers:
        summary_parts.append("    <h3>Job Numbers</h3>")
        summary_parts.append(f"    <p>{', '.join(sorted(set(job_numbers)))}</p>")
    
    # Services & Management Recommendations
    summary_parts.append("    <h3>Services & Management Recommendations</h3>")
    summary_parts.append("    <ul>")
    if services:
        summary_parts.append(f"        <li>Services: {', '.join(sorted(set(services)))}</li>")
    else:
        summary_parts.append("        <li>No services found for this issuer</li>")
    
    if mgmt_recs:
        summary_parts.append(f"        <li>Management recommendations: {', '.join(sorted(set(mgmt_recs)))}</li>")
    else:
        summary_parts.append("        <li>No management recommendations found for this issuer</li>")
    summary_parts.append("    </ul>")
    
    # Rejected proposals breakdown
    if rejected_categories:
        summary_parts.append("    <h3>Rejected Proposals Breakdown</h3>")
        summary_parts.append("    <ul>")
        for category, count in rejected_categories.most_common():
            summary_parts.append(f"        <li>Category Summary: {escape_html(category)} ({count})</li>")
        summary_parts.append("    </ul>")
    
    # Rejected proposals list
    if rejected_proposals:
        summary_parts.append("    <h3>Rejected Proposals List</h3>")
        summary_parts.append("    <ul>")
        for proposal in rejected_proposals[:20]:  # Limit to 20 proposals for readability
            summary_parts.append(f"        <li>{proposal}</li>")
        summary_parts.append("    </ul>")
    
    return "\n".join(summary_parts)

def normalize_issuer_name(name):
    if pd.isna(name) or name is None:
        return ''
    # Lowercase, strip, remove common punctuation
    return re.sub(r'[^a-z0-9]', '', str(name).lower().strip())

def main():
    """Main function to generate summaries for all issuers"""
    print("Starting issuer summary generation...")
    
    # Load the issuer list
    issuer_list_path = "/home/syu2/Downloads/issuer_distribution_list.csv"
    if not os.path.exists(issuer_list_path):
        print(f"Error: {issuer_list_path} not found!")
        return
    
    with open(issuer_list_path, 'r') as f:
        issuers = [line.strip() for line in f.readlines() if line.strip()]
    # Normalize issuer names in the list
    normalized_issuers = [normalize_issuer_name(issuer) for issuer in issuers]
    print(f"Found {len(issuers)} issuers to process")

    # DEBUG: Print sample issuer names from list
    print("Sample issuer names from issuer_distribution_list.csv:")
    for issuer in issuers[:10]:
        print(f"  '{issuer}'")

    # Load datasets
    peer_data_path = "/usr/project/llm_webapp_voteproposal/filtered_proposals.csv"
    large_data_path = "/usr/project/llm_webapp_voteproposal/2025_Predictions_All_Issuers_v11.csv"

    print("Loading peer analysis dataset...")
    peer_df = pd.read_csv(peer_data_path)
    print(f"Loaded peer dataset: {len(peer_df)} rows, {len(peer_df.columns)} columns")
    print("Loading large dataset...")
    large_df = pd.read_csv(large_data_path)
    print(f"Loaded large dataset: {len(large_df)} rows, {len(large_df.columns)} columns")
    # Normalize issuer columns in both DataFrames
    peer_headers = list(peer_df.columns)
    large_headers = list(large_df.columns)
    peer_issuer_col = None
    large_issuer_col = None
    for col in peer_headers:
        if 'issuer' in col.lower() or 'company' in col.lower() or 'firm' in col.lower():
            peer_issuer_col = col
            break
    for col in large_headers:
        if 'issuer' in col.lower() or 'company' in col.lower() or 'firm' in col.lower():
            large_issuer_col = col
            break
    if peer_issuer_col:
        peer_df['__normalized_issuer__'] = peer_df[peer_issuer_col].apply(normalize_issuer_name)
    if large_issuer_col:
        large_df['__normalized_issuer__'] = large_df[large_issuer_col].apply(normalize_issuer_name)

    # DEBUG: Print sample issuer names from large_df
    for pattern in ['issuer', 'company', 'firm']:
        for col in large_headers:
            if pattern in col.lower():
                large_issuer_col = col
                break
        if large_issuer_col:
            break
    if large_issuer_col:
        print(f"Sample issuer names from v11 dataset column '{large_issuer_col}':")
        for name in large_df[large_issuer_col].dropna().unique()[:10]:
            print(f"  '{str(name)}'")
    else:
        print("Could not find issuer column in v11 dataset!")

    # DEBUG: Print count of rejected proposals per issuer in v11
    for_ratio_col = None
    for col in large_headers:
        if 'forratio' in col.lower() and 'true' in col.lower():
            for_ratio_col = col
            break
    if large_issuer_col and for_ratio_col:
        print("\nRejected proposal counts per issuer in v11:")
        issuer_rejected_counts = large_df[large_df[for_ratio_col].apply(parse_for_ratio).lt(0.5, fill_value=False)].groupby(large_issuer_col).size()
        for issuer in issuers[:10]:
            count = issuer_rejected_counts.get(issuer, 0)
            print(f"  '{issuer}': {count} rejected proposals")

    # Normalize issuer names for matching
    issuers_normalized = [issuer.strip().lower() for issuer in issuers]
    if large_issuer_col:
        large_df['__issuer_normalized'] = large_df[large_issuer_col].astype(str).str.strip().str.lower()

    # Generate HTML header
    html_content = []
    html_content.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error Analysis - Top Issuers Summary</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.5;
            color: #000;
            background: white;
            padding: 20px;
        }
        
        h1 {
            font-size: 24px;
            margin-bottom: 20px;
        }
        
        h2 {
            font-size: 20px;
            font-weight: bold;
            margin: 20px 0 10px 0;
        }
        
        h3 {
            font-size: 16px;
            font-weight: bold;
            margin: 15px 0 5px 0;
        }
        
        ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        
        li {
            margin: 5px 0;
        }
        
        p {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <h1>Error Analysis - Top Issuers Summary</h1>
    """)
    
    # Replace loop over issuers with normalized matching
    processed_count = 0
    for i, issuer in enumerate(issuers):
        print(f"\nProcessing {i+1}/{len(issuers)}: {issuer}")
        norm_issuer = normalize_issuer_name(issuer)
        summary = generate_issuer_summary(
            issuer, peer_df, large_df, norm_issuer=norm_issuer
        )
        if summary:
            html_content.append(f"\n    <h2>{escape_html(issuer)}</h2>\n")
            html_content.append(summary)
            html_content.append("\n<hr>\n")
            html_content.append("\n<hr>\n")
            processed_count += 1
        else:
            print(f"Skipping {issuer} - no data found")
    
    # Close HTML
    html_content.append("""</body>
</html>""")
    
    # Write new file
    output_path = "/usr/project/llm_webapp_voteproposal/Error_analysis_topissuers.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_content))
    
    print(f"\n=== Summary Generation Complete ===")
    print(f"Processed {processed_count} issuers")
    print(f"Generated: {output_path}")
    
    # Compare with existing file
    existing_path = "/usr/project/llm_webapp_voteproposal/Error_analysis_topissuers_v11.html"
    if os.path.exists(existing_path):
        print(f"\nComparing with existing file: {existing_path}")
        
        with open(existing_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        with open(output_path, 'r', encoding='utf-8') as f:
            new_content = f.read()
        
        if existing_content.strip() == new_content.strip():
            print("✅ Files are identical - no changes needed")
            os.remove(output_path)  # Remove temporary file
        else:
            print("📝 Files differ - updating existing file")
            # Backup existing file
            backup_path = f"{existing_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(existing_path, backup_path)
            # Replace with new content
            os.rename(output_path, existing_path)
            print(f"✅ Updated {existing_path}")
            print(f"🔄 Backup saved as {backup_path}")
    else:
        # No existing file, rename new one
        os.rename(output_path, existing_path)
        print(f"✅ Created {existing_path}")

if __name__ == "__main__":
    main()
