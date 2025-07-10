#!/usr/bin/env python3

import csv
import os
from collections import defaultdict

def read_issuer_list():
    """Read the issuer distribution list"""
    issuer_file = "/home/syu2/Downloads/issuer_distribution_list.csv"
    issuers = []
    try:
        with open(issuer_file, 'r', encoding='utf-8') as f:
            for line in f:
                issuer = line.strip()
                if issuer and not issuer.startswith('//'):
                    issuers.append(issuer)
    except FileNotFoundError:
        print(f"File not found: {issuer_file}")
        return []
    return issuers

def analyze_issuer_data(filtered_csv_path, full_csv_path):
    """Analyze data for all issuers from both filtered CSV (for error analysis) and full CSV (for approval rates)"""
    issuer_data = defaultdict(lambda: {
        'proposals': [],
        'job_numbers': set(),
        'services': set(),
        'record_dates': set(),
        'mgmt_recs': set(),
        'total_proposals': 0,
        'rejected_proposals': 0,
        'approved_proposals': 0,
        'for_ratios': []  # Store ForRatioAmongVoted_true values for approval rate calculation
    })
    
    # First load the full dataset to get metadata and calculate correct approval counts
    print("Loading full analysis dataset for metadata and approval counts...")
    try:
        with open(full_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                issuer = row['issuer_name']
                
                # Store metadata from full dataset
                issuer_data[issuer]['job_numbers'].add(row['job_number'])
                issuer_data[issuer]['services'].add(row['service'])
                issuer_data[issuer]['record_dates'].add(row['record_date'])
                issuer_data[issuer]['mgmt_recs'].add(row['mgmt_rec'])
                
                # Calculate approval status based on ForRatioAmongVoted_true
                for_ratio_str = row.get('ForRatioAmongVoted_true', '')
                if for_ratio_str and for_ratio_str.strip():
                    try:
                        # Handle percentage format (e.g., "18.27%") and convert to decimal
                        if isinstance(for_ratio_str, str) and for_ratio_str.endswith('%'):
                            for_ratio = float(for_ratio_str.rstrip('%')) / 100.0
                        else:
                            for_ratio = float(for_ratio_str)
                        
                        # Count all proposals and their approval status
                        issuer_data[issuer]['total_proposals'] += 1
                        if for_ratio >= 0.5:
                            issuer_data[issuer]['approved_proposals'] += 1
                        else:
                            issuer_data[issuer]['rejected_proposals'] += 1
                    except (ValueError, TypeError):
                        pass  # Skip invalid values
                
    except FileNotFoundError:
        print(f"Full analysis file not found: {full_csv_path}")
    
    # Then load the filtered dataset for detailed proposal analysis (rejected proposals only)
    print("Loading filtered dataset for detailed proposal analysis...")
    try:
        with open(filtered_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                issuer = row['issuer_name']
                
                # Get ForRatioAmongVoted_true value for this proposal
                for_ratio_str = row.get('ForRatioAmongVoted_true', '')
                proposal_approved = False
                
                if for_ratio_str and for_ratio_str.strip():
                    try:
                        # Handle percentage format (e.g., "18.27%") and convert to decimal
                        if isinstance(for_ratio_str, str) and for_ratio_str.endswith('%'):
                            for_ratio = float(for_ratio_str.rstrip('%')) / 100.0
                        else:
                            for_ratio = float(for_ratio_str)
                        
                        # Determine approval status based on ForRatioAmongVoted_true >= 0.5
                        proposal_approved = for_ratio >= 0.5
                        
                        # Only add to for_ratios if rejected (for approval rate calculation)
                        if not proposal_approved:
                            issuer_data[issuer]['for_ratios'].append(for_ratio)
                    except (ValueError, TypeError):
                        pass  # Skip invalid values
                
                # Store detailed proposal data from filtered dataset
                issuer_data[issuer]['proposals'].append({
                    'proposal': row['proposal'],
                    'approved': proposal_approved,
                    'category': row.get('Category', 'Unknown'),
                    'subcategory': row.get('Subcategory', '')
                })
    
    except FileNotFoundError:
        print(f"Filtered file not found: {filtered_csv_path}")
        return {}
    
    return issuer_data

def generate_issuer_html(issuer_name, data):
    """Generate HTML content for a single issuer"""
    
    # Calculate approval rate range for failed proposals based on ForRatioAmongVoted_true values
    for_ratios = data['for_ratios']
    if for_ratios:
        # Calculate min and max ForRatio values (these represent approval rates for individual proposals)
        min_approval_ratio = min(for_ratios)
        max_approval_ratio = max(for_ratios)
        # Convert to percentages for display (this shows the approval rates of failed proposals)
        approval_rate_range = f"{(min_approval_ratio*100):.1f}%-{(max_approval_ratio*100):.1f}%"
    else:
        approval_rate_range = "N/A"
    
    # Get counts
    total = data['total_proposals']
    rejected = data['rejected_proposals']
    approved = data['approved_proposals']
    
    # Get unique values
    job_numbers = ', '.join(sorted(data['job_numbers']))
    services = [s for s in data['services'] if s and s != '']
    service_types = ', '.join(services) if services else 'No services found'
    record_dates = ', '.join(sorted(data['record_dates']))
    mgmt_recs = [m for m in data['mgmt_recs'] if m and m != '']
    mgmt_rec_text = ', '.join(mgmt_recs) if mgmt_recs else 'No Mgmt Rec'
    
    # Count categories
    categories = defaultdict(int)
    rejected_proposals = []
    for proposal in data['proposals']:
        if not proposal['approved']:
            categories[proposal['category']] += 1
            rejected_proposals.append(proposal['proposal'])
    
    # Generate HTML
    html = f"""
    <h2>{issuer_name}</h2>
    
    <h3>Statistics</h3>
    <ul>
        <li>Service Type: {service_types} ({job_numbers})</li>
        <li>Management Recommendations: {mgmt_rec_text}</li>
        <li>Total Proposals: {total}</li>
        <li>Approval Rate Range of Failed Proposals: {approval_rate_range}</li>
        <li>Rejected Count: {rejected}</li>
        <li>Approved Count: {approved}</li>
    </ul>
    
    <h3>Record Dates</h3>
    <p>{record_dates if record_dates else 'No record dates found'}</p>
    
    <h3>Job Numbers</h3>
    <p>{job_numbers if job_numbers else 'No job numbers found'}</p>
    
    <h3>Services & Management Recommendations</h3>
    <ul>
        <li>{'No services found for this issuer' if not services else f'Services: {service_types}'}</li>
        <li>{'No management recommendations found for this issuer' if not mgmt_recs else f'Management recommendations: {mgmt_rec_text}'}</li>
    </ul>
    
    <h3>Rejected Proposals Breakdown</h3>
    <ul>"""
    
    if categories:
        for category, count in categories.items():
            html += f"\n        <li>Category Summary: {category} ({count})</li>"
    else:
        html += "\n        <li>No rejected proposals</li>"
    
    html += """
    </ul>
    
    <h3>Rejected Proposals List</h3>
    <ul>"""
    
    if rejected_proposals:
        for proposal in rejected_proposals:
            html += f"\n        <li>{proposal}</li>"
    else:
        html += "\n        <li>No rejected proposals</li>"
    
    html += """
    </ul>
"""
    
    return html

def main():
    # Read issuer list
    print("Reading issuer list...")
    issuers = read_issuer_list()
    print(f"Found {len(issuers)} issuers to process")
    
    if not issuers:
        print("No issuers found, exiting")
        return
    
    # Print first few issuers for debugging
    print("First 5 issuers:", issuers[:5])
    
    # Analyze data
    print("Analyzing data...")
    filtered_csv = "/usr/project/llm_webapp_voteproposal/filtered_proposals.csv"
    full_csv = "/usr/project/llm_webapp_voteproposal/full_analysis_proposals.csv"
    issuer_data = analyze_issuer_data(filtered_csv, full_csv)
    print(f"Found data for {len(issuer_data)} issuers")
    
    # Generate HTML for each issuer (skip UPL LIMITED as it's already done)
    html_content = ""
    processed_count = 0
    for i, issuer in enumerate(issuers[1:]):  # Skip first issuer (UPL LIMITED)
        if issuer in issuer_data:
            print(f"Processing: {issuer}")
            
            # Add separator line before each issuer (except the first one)
            if i > 0:
                html_content += "\n<hr>\n"
            
            html_content += generate_issuer_html(issuer, issuer_data[issuer])
            html_content += "\n"
            processed_count += 1
        else:
            print(f"No data found for: {issuer}")
    
    print(f"Processed {processed_count} issuers")
    
    # Write to output file
    output_file = "/usr/project/llm_webapp_voteproposal/additional_issuers.html"
    print(f"Writing to {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated HTML content saved to: {output_file}")
    print(f"File size: {len(html_content)} characters")

if __name__ == "__main__":
    main()
