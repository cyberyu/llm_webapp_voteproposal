#!/usr/bin/env python3
"""
Script to update the approval rates in Error_analysis_topissuers.html 
with the corrected rates from additional_issuers.html
"""

import re

def extract_issuer_approval_rates(filepath):
    """Extract issuer names and their approval rates from HTML file"""
    issuer_rates = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all issuer sections - handle both formats (with and without leading spaces)
    pattern = r'<h2>(.*?)</h2>.*?<li>(?:Failed Approval Rate|Approval Rate Range of Failed Proposals): (.*?)</li>'
    matches = re.findall(pattern, content, re.DOTALL)
    
    for issuer_name, approval_rate in matches:
        issuer_rates[issuer_name.strip()] = approval_rate.strip()
    
    return issuer_rates

def update_main_file():
    """Update the main HTML file with corrected approval rates"""
    
    # Extract corrected rates from additional issuers file
    corrected_rates = extract_issuer_approval_rates('additional_issuers.html')
    
    print("Corrected approval rates found:")
    for issuer, rate in corrected_rates.items():
        print(f"  {issuer}: {rate}")
    
    # Read the main file
    with open('Error_analysis_topissuers.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update each issuer's approval rate
    updates_made = 0
    
    for issuer_name, correct_rate in corrected_rates.items():
        # Look for the pattern: <h2>ISSUER_NAME</h2> followed by Failed Approval Rate or new label
        # Handle both leading spaces and no leading spaces in h2 tags
        pattern = f'(<h2>{re.escape(issuer_name)}</h2>.*?<li>(?:Failed Approval Rate|Approval Rate Range of Failed Proposals): )(.*?)(</li>)'
        
        def replace_rate(match):
            nonlocal updates_made
            current_rate = match.group(2)
            if current_rate != correct_rate:
                updates_made += 1
                print(f"Updated {issuer_name}: {current_rate} -> {correct_rate}")
            return match.group(1) + correct_rate + match.group(3)
        
        content = re.sub(pattern, replace_rate, content, flags=re.DOTALL)
    
    # Write the updated content back
    with open('Error_analysis_topissuers.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\nTotal updates made: {updates_made}")
    return updates_made

if __name__ == '__main__':
    update_main_file()
