import csv
from collections import defaultdict

def analyze_management_proposals(csv_file):
    categories = set()
    category_subcategories = defaultdict(set)
    
    # Try different encodings
    encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings_to_try:
        try:
            with open(csv_file, 'r', encoding=encoding) as file:
                reader = csv.DictReader(file)
                for row in reader:
                    proposal_type = row['Proposal Type'].strip()
                    if proposal_type == 'Management':
                        category = row['Proposal Category'].strip()
                        subcategory = row['Proposal Subcategory'].strip()
                        
                        categories.add(category)
                        category_subcategories[category].add(subcategory)
            print(f"Successfully read file with encoding: {encoding}")
            break
        except UnicodeDecodeError:
            print(f"Failed to read with encoding: {encoding}")
            continue
    else:
        print("Could not read file with any of the tried encodings")
        return
    
    # Sort categories and subcategories
    sorted_categories = sorted(list(categories))
    
    # Create the data structure
    category_types = sorted_categories
    sub_category_types = []
    
    for category in sorted_categories:
        subcats = sorted(list(category_subcategories[category]))
        sub_category_types.append(', '.join(subcats))
    
    # Print the results in the requested format
    print("data = {")
    print("    'category-types': [")
    for i, cat in enumerate(category_types):
        if i == len(category_types) - 1:
            print(f"        '{cat}'")
        else:
            print(f"        '{cat}',")
    print("    ],")
    print("    'sub-category-types': [")
    for i, subcats in enumerate(sub_category_types):
        if i == len(sub_category_types) - 1:
            print(f"        '{subcats}'")
        else:
            print(f"        '{subcats}',")
    print("    ]")
    print("}")
    
    # Also print detailed breakdown
    print("\n\nDetailed breakdown:")
    for category in sorted_categories:
        subcats = sorted(list(category_subcategories[category]))
        print(f"\n{category}:")
        for subcat in subcats:
            print(f"  - {subcat}")

if __name__ == "__main__":
    analyze_management_proposals('df_management_shareholder_train.csv')
