#!/usr/bin/env python3
"""
Script to systematically update all approval rates in Error_analysis_topissuers.html
"""

# Manual mapping based on the additional_issuers.html file  
APPROVAL_RATE_MAPPING = {
    "MBT BANCSHARES, INC.": "18.3%-20.8%",
    "POWERUP ACQUISITION CORP.": "9.8%-100.0%",
    "1169032 BC LTD.": "0.0%-0.0%",
    "AUKA CAPITAL CORP.": "0.0%-0.0%",
    "OSR HOLDINGS, INC.": "37.4%-100.0%",
    "CORUS ENTERTAINMENT INC.": "0.0%-0.0%",
    "SHINHAN FINANCIAL GROUP": "40.3%-100.0%",
    "WINDFALL GEOTEK INC.": "1.6%-100.0%",
    "VIRPAX PHARMACEUTICALS, INC.": "33.6%-38.3%",
    "ALPHA STAR ACQUISITION CORPORATION": "1.1%-100.0%",
    "CHINA JO-JO DRUGSTORES, INC.": "4.7%-100.0%",
    "ICLICK INTERACTIVE ASIA GROUP LIMITED": "6.3%-6.3%",
    "METASPHERE LABS INC.": "16.0%-100.0%",
    "NAAS TECHNOLOGY INC.": "9.0%-13.1%",
    "PHOENIX MOTOR INC.": "20.8%-99.2%",
    "1847 HOLDINGS LLC": "13.7%-25.1%",
    "BRENMILLER ENERGY LTD.": "33.7%-89.5%",
    "DT CLOUD ACQUISITION CORPORATION": "38.5%-99.9%",
    "KERMODE RESOURCES LTD.": "23.4%-100.0%",
    "UTIME LIMITED": "39.7%-47.8%"
}

def update_all_approval_rates():
    """Update all approval rates in the main HTML file"""
    
    with open('/usr/project/llm_webapp_voteproposal/Error_analysis_topissuers.html', 'r') as f:
        content = f.read()
    
    updates_made = 0
    
    for issuer_name, correct_rate in APPROVAL_RATE_MAPPING.items():
        # Replace all instances of 100.0%-100.0% for this issuer
        pattern = f'(<h2>{issuer_name}</h2>.*?<li>Failed Approval Rate: )100\.0%-100\.0%(</li>)'
        
        import re
        matches = re.findall(pattern, content, re.DOTALL)
        if matches:
            content = re.sub(pattern, rf'\g<1>{correct_rate}\g<2>', content, flags=re.DOTALL)
            updates_made += len(matches)
            print(f"Updated {len(matches)} occurrences of {issuer_name}: 100.0%-100.0% -> {correct_rate}")
    
    # Write back to file
    with open('/usr/project/llm_webapp_voteproposal/Error_analysis_topissuers.html', 'w') as f:
        f.write(content)
    
    print(f"\nTotal updates made: {updates_made}")
    
    # Verify remaining 100.0%-100.0% entries
    remaining_100s = content.count('Failed Approval Rate: 100.0%-100.0%')
    print(f"Remaining 100.0%-100.0% entries: {remaining_100s}")

if __name__ == '__main__':
    update_all_approval_rates()
