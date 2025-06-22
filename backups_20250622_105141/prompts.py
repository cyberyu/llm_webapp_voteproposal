# prompts.py

import csv
import os

def create_category_prompt(proposal_text):
    return f'''You are an AI assistant specialized in analyzing corporate proposals and categorizing them accurately.
The proposal text needs to be assigned to exactly one category from the predefined list below.

Categories:
1. Board of Directors - Proposals related to board composition, independence, diversity, elections
2. Compensation - Proposals about executive compensation, employee benefits, pay equity
3. Corporate Actions - Proposals regarding mergers, acquisitions, divestitures, restructuring
4. Corporate Governance - Proposals concerning company policies, ethical guidelines, transparency
5. Corporate Structure - Proposals about company structure, ownership, spin-offs, liquidations
6. Shareholder Equity - Proposals concerning dividends, share repurchases, capital allocation
7. Shareholder Rights - Proposals about voting procedures, shareholder meetings, proxy access

Instructions:
1. Analyze the key themes and focus of the proposal text.
2. Compare these themes against the descriptions of each category.
3. Select the single most appropriate category that best encompasses the proposal's main focus.
4. Provide a brief explanation of your reasoning before giving the final answer.

Output format (plain text, no asterisks or markdown):
Reasoning: <your step-by-step analysis>
Selected Category: <Category Number> - <Category Name>

Proposal Text (analyze this proposal):
{proposal_text}
'''

def create_subcategory_prompt(proposal_text, category, subcategories):
    return f'''You are an AI assistant specialized in detailed classification of corporate proposals.
The proposal has already been categorized under: {category}
Now you must identify the most specific sub-category within this main category.

Subcategories:
{subcategories}

Instructions:
1. Review the proposal text carefully, focusing on specific details and nuances.
2. Consider how the proposal relates to each available sub-category option.
3. Select the single most appropriate sub-category that best captures the specific focus of the proposal.
4. Provide a brief explanation of your reasoning before giving the final answer.

Output format (plain text, no asterisks or markdown):
Reasoning: <your step-by-step analysis>
Selected Sub-Category: <Sub-Category Name>

Proposal Text (analyze this proposal):
{proposal_text}
'''

def get_openai_api_key():
    key_path = os.path.join(os.path.dirname(__file__), 'openai_key.csv')
    with open(key_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get('key') and row['key'].startswith('sk-'):
                return row['key']
    raise RuntimeError('OpenAI API key not found in openai_key.csv')

def get_openai_client():
    from openai import OpenAI
    return OpenAI(
        api_key = get_openai_api_key()
    )

def make_request_llm(prompt, user_content, client, model="gpt-4.1-nano"):
    import time
    retries = 2
    for _ in range(retries):
        try:
            response = client.responses.create(
                model=model,
                instructions=prompt,
                input=user_content,
            )
            response_text = response.output[0].content[0].text
            return response_text
        except Exception as e:
            print("Exception occurred:", e)
            time.sleep(10)
    print("Failed to retrieve data after 2 retries.")
    return "Not able to answer at the moment"

def find_match(prompt, user_content, client):
    try:
        return make_request_llm(prompt, user_content, client, model="gpt-4.1-nano")
    except Exception as e:
        print("Error:", e)
        return "Not able to answer at the moment"

def find_match_mini(prompt, user_content, client):
    try:
        return make_request_llm(prompt, user_content, client, model="gpt-4.1-mini")
    except Exception as e:
        print("Error:", e)
        return "Not able to answer at the moment"

