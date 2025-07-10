#!/usr/bin/env python3
"""
Script to add horizontal separators between issuers in Error_analysis_topissuers.html
"""

import re

def add_separators_to_main_file():
    """Add <hr> separators before each issuer section (except the first)"""
    
    print("Reading Error_analysis_topissuers.html...")
    # Read the main file
    with open('Error_analysis_topissuers.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"File size: {len(content)} characters")
    
    # Find all h2 tags that start issuer sections
    # We'll add <hr> before each <h2> except the first one (UPL LIMITED)
    
    # First, let's find the position of the first h2 (UPL LIMITED)
    first_h2_match = re.search(r'    <h2>UPL LIMITED</h2>', content)
    if not first_h2_match:
        print("Could not find UPL LIMITED section")
        return
    
    print("Found UPL LIMITED section")
    first_h2_pos = first_h2_match.start()
    
    # Now find all subsequent h2 tags and add <hr> before them
    # Pattern to match h2 tags that are issuer headers (with 4 spaces indent)
    pattern = r'(\n\n    <h2>(?!UPL LIMITED)[^<]+</h2>)'
    
    print("Searching for h2 patterns...")
    matches = re.findall(pattern, content)
    print(f"Found {len(matches)} h2 patterns to update")
    
    def add_hr(match):
        return f'\n\n<hr>\n{match.group(1)}'
    
    # Apply the replacement to everything after the first h2
    before_first_h2 = content[:first_h2_pos]
    after_first_h2 = content[first_h2_pos:]
    
    # Add separators to the part after the first h2
    after_first_h2_with_separators = re.sub(pattern, add_hr, after_first_h2)
    
    # Combine the parts
    updated_content = before_first_h2 + after_first_h2_with_separators
    
    # Write the updated content back
    with open('Error_analysis_topissuers.html', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    # Count how many separators were added
    separator_count = updated_content.count('<hr>')
    print(f"Added {separator_count} horizontal separators to Error_analysis_topissuers.html")

if __name__ == '__main__':
    add_separators_to_main_file()
