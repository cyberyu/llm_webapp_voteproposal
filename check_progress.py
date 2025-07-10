#!/usr/bin/env python3
"""
Check progress on approval rate updates
"""

def check_progress():
    with open('/usr/project/llm_webapp_voteproposal/Error_analysis_topissuers.html', 'r') as f:
        content = f.read()
    
    # Count remaining 100.0%-100.0% entries
    remaining_100s = content.count('Failed Approval Rate: 100.0%-100.0%')
    print(f"Remaining 100.0%-100.0% entries: {remaining_100s}")
    
    # Count updated entries
    updated_rates = [
        "18.3%-20.8%",   # MBT BANCSHARES
        "9.8%-100.0%",   # POWERUP ACQUISITION
        "0.0%-0.0%",     # 1169032 BC LTD, AUKA CAPITAL, CORUS
        "37.4%-100.0%",  # OSR HOLDINGS
        "40.3%-100.0%",  # SHINHAN FINANCIAL
        "1.6%-100.0%",   # WINDFALL GEOTEK
        "33.6%-38.3%"    # VIRPAX PHARMACEUTICALS
    ]
    
    total_updated = 0
    for rate in updated_rates:
        count = content.count(f'Failed Approval Rate: {rate}')
        total_updated += count
        if count > 0:
            print(f"Found {count} entries with rate: {rate}")
    
    print(f"Total updated entries: {total_updated}")

if __name__ == '__main__':
    check_progress()
