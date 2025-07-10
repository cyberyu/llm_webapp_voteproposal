#!/usr/bin/env python3
import re

# Test reading additional_issuers.html
print("Testing additional_issuers.html...")
try:
    with open('/usr/project/llm_webapp_voteproposal/additional_issuers.html', 'r') as f:
        content = f.read()
        print(f"File size: {len(content)} characters")
        
        # Find h2 tags
        h2_pattern = r'<h2>(.*?)</h2>'
        h2_matches = re.findall(h2_pattern, content)
        print(f"Found {len(h2_matches)} h2 tags")
        
        # Find approval rates
        rate_pattern = r'<li>Failed Approval Rate: (.*?)</li>'
        rate_matches = re.findall(rate_pattern, content)
        print(f"Found {len(rate_matches)} approval rates")
        
        # Show first few matches
        print("\nFirst 3 issuer names:")
        for i, name in enumerate(h2_matches[:3]):
            print(f"  {i+1}: '{name}'")
            
        print("\nFirst 3 approval rates:")
        for i, rate in enumerate(rate_matches[:3]):
            print(f"  {i+1}: '{rate}'")
            
except Exception as e:
    print(f"Error: {e}")
