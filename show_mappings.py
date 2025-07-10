#!/usr/bin/env python3
"""
Simple script to extract and display issuer approval rate mappings
"""

import re

def extract_mappings():
    """Extract issuer-to-rate mappings from additional_issuers.html"""
    
    mappings = {}
    
    with open('/usr/project/llm_webapp_voteproposal/additional_issuers.html', 'r') as f:
        content = f.read()
    
    # Split by h2 tags to get each issuer section
    sections = re.split(r'<h2>(.*?)</h2>', content)[1:]  # Skip first empty part
    
    for i in range(0, len(sections), 2):
        if i + 1 < len(sections):
            issuer_name = sections[i].strip()
            section_content = sections[i + 1]
            
            # Find approval rate in this section
            rate_match = re.search(r'<li>Failed Approval Rate: (.*?)</li>', section_content)
            if rate_match:
                approval_rate = rate_match.group(1).strip()
                mappings[issuer_name] = approval_rate
    
    return mappings

if __name__ == '__main__':
    mappings = extract_mappings()
    print("Issuer -> Corrected Approval Rate mappings:")
    print("=" * 50)
    for issuer, rate in mappings.items():
        print(f"{issuer}: {rate}")
    print(f"\nTotal issuers: {len(mappings)}")
