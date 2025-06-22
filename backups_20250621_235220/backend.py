from fastapi import FastAPI, File, UploadFile, Form, Request, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import csv
import io
from typing import List, Dict
from prompts import create_category_prompt, create_subcategory_prompt, find_match, find_match_mini
import asyncio
import uuid
import subprocess
import os

app = FastAPI()

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add specific routes for HTML files BEFORE mounting static files
@app.get("/peeranalysis.html")
async def serve_peeranalysis():
    return FileResponse("peeranalysis.html")

@app.get("/webui.html") 
async def serve_webui():
    return FileResponse("webui.html")

@app.get("/detail.html")
async def serve_detail():
    return FileResponse("detail.html")

@app.get("/histrogram.html")
async def serve_histogram():
    return FileResponse("histrogram.html")

@app.get("/")
async def serve_index():
    # Serve webui.html as the default page if index.html doesn't exist
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    else:
        return FileResponse("webui.html")

# Mount static files at /static instead of /
app.mount("/static", StaticFiles(directory=".", html=True), name="static")

uploaded_data = []
progress_tracker = {}
progress_dict = {}

@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    raw = file.file.read()
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        content = raw.decode("cp1252")
    reader = csv.DictReader(io.StringIO(content))
    global uploaded_data
    uploaded_data = list(reader)
    return {"status": "success", "rows": len(uploaded_data)}

@app.get("/data")
def get_data():
    return uploaded_data

BATCH_SIZE = 10  # Tune this for your OpenAI API context window and rate limits

async def process_row(row, client, category_map):
    from prompts import create_category_prompt, create_subcategory_prompt, find_match
    import re
    proposal_text = ''
    for k, v in row.items():
        if k and k.strip().lower().replace('_', '').replace(' ', '') == 'proposal':
            proposal_text = v
            break
    if not proposal_text:
        proposal_text = next((v for v in row.values() if v), '')
    category_prompt = create_category_prompt(proposal_text)
    #print(category_prompt)
    category_response = await asyncio.to_thread(find_match, category_prompt, proposal_text, client)
    #print(category_response)
    match = re.search(r'Selected Category:\s*\d+\s*[-\.]?\s*(.+)', category_response)
    if match:
        category_name = match.group(1).strip()
        # Fix: match category_name to the correct key (number) in category_map by exact name, not substring
        category_num = None
        for num, subcats in category_map.items():
            # Use instruct.csv order for category names
            instruct_names = [
                'Board of Directors',
                'Compensation',
                'Corporate Actions',
                'Corporate Governance',
                'Corporate Structure',
                'Shareholder Equity',
                'Shareholder Rights'
            ]
            if category_name.lower() == instruct_names[int(num)-1].lower():
                category_num = num
                break
        if not category_num:
            category_num = '1'  # fallback to first
    else:
        match2 = re.search(r'(Board of Directors|Compensation|Corporate Actions|Corporate Governance|Corporate Structure|Shareholder Equity|Shareholder Rights)', category_response, re.IGNORECASE)
        if match2:
            category_name = match2.group(1).strip()
            instruct_names = [
                'Board of Directors',
                'Compensation',
                'Corporate Actions',
                'Corporate Governance',
                'Corporate Structure',
                'Shareholder Equity',
                'Shareholder Rights'
            ]
            category_num = None
            for num, _ in category_map.items():
                if category_name.lower() == instruct_names[int(num)-1].lower():
                    category_num = num
                    break
            if not category_num:
                category_num = '1'
        else:
            category_num = '1'
            category_name = 'Board of Directors'
    subcategories = category_map.get(category_num, '')
    subcategory_prompt = create_subcategory_prompt(proposal_text, f"{category_num} - {category_name}", subcategories)
    print(subcategory_prompt)
    subcategory_response = await asyncio.to_thread(find_match, subcategory_prompt, proposal_text, client)
    match2 = re.search(r'Selected Sub-Category: (.+)', subcategory_response)
    if match2:
        subcategory = match2.group(1).strip()
    else:
        subcategory = ''
    row['Nano_Category'] = category_name
    row['Nano_Subcategory'] = subcategory
    return {
        'proposal_text': proposal_text,
        'Nano_Category': category_name,
        'Nano_Subcategory': subcategory
    }

@app.post("/query")
async def query_llm(request: Request):
    from prompts import get_openai_client
    global uploaded_data
    client = get_openai_client()
    rows = uploaded_data
    category_map = {
        '1': 'Articles/ByLaws, Board Classification, Board Composition, Board Size, Cumulative Voting, Director Remuneration, Elections, Elections, Board Size, Indemnification/Liability, Independent Board Chairman, Majority Voting, Miscellaneous Board of Directors, Proxy Access, Quorum Requirements, Remove Directors/Board Members',
        '2': 'Articles/ByLaws, Bonus Plan, Cash/Stock Bonus Plan, Directors Fees, Employee Stock Purchase Program, Employment Agreements, Executive Pay Evaluation (Say on Pay), Golden Parachutes, Miscellaneous Compensation, Omnibus Stock Plan, Restricted Stock Plan, Stock Option Plans',
        '3': 'Acquisition Agreement, Articles/ByLaws, Assets, Corporate Actions, Dividend Reinvestment Plan, Investment Advisory Agreement, Investment Agreement/Policy, Merger Plan, Miscellaneous Corporate Actions, Reorganization Plan, Scheme Arrangement',
        '4': 'Audit Related, Company Name Change, Corporate Governance, Financial Statements, Meeting Management, Miscellaneous Corporate Governance',
        '5': 'Investment Advisory Agreement, Liquidation Plan, Miscellaneous Corporate Actions, Spin Off',
        '6': 'Allot Securities, Articles/ByLaws, Authorize Stock Decrease, Authorize Stock Increase, Capital Accumulation Plan, Class of Stock Elimination, Dividend Reinvestment Plan, Miscellaneous Shareholder Equity, New Class of Stock, Par Value, Repurchase Program, Share Capital, Shareholder Equity, Stock Conversion, Stock Issuance, Stock Splits/Reverse Stock Splits, Stock Terms Revision, Voting Rights, Warrants/Bonds/Notes',
        '7': 'Antitakeover Provisions, Articles/ByLaws, Control Share Acquisition, Directors/Board Removal, Meeting Management, Miscellaneous Shareholder Rights, Supermajority Voting, Voting Rights'
    }
    # Progress tracking
    job_id = str(uuid.uuid4())
    progress_dict[job_id] = {"current": 0, "total": len(rows), "done": False}
    all_results = []
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i+BATCH_SIZE]
        batch_results = await asyncio.gather(*[process_row(row, client, category_map) for row in batch])
        all_results.extend(batch_results)
        progress_dict[job_id]["current"] = min(i + BATCH_SIZE, len(rows))
    progress_dict[job_id]["done"] = True
    progress_dict[job_id]["current"] = len(rows)
    return {"results": all_results, "data": uploaded_data, "job_id": job_id}

async def process_row_mini(row, client, category_map):
    import re
    proposal_text = ''
    for k, v in row.items():
        if k and k.strip().lower().replace('_', '').replace(' ', '') == 'proposal':
            proposal_text = v
            break
    if not proposal_text:
        proposal_text = next((v for v in row.values() if v), '')
    category_prompt = create_category_prompt(proposal_text)
    category_response = await asyncio.to_thread(find_match_mini, category_prompt, proposal_text, client)
    match = re.search(r'Selected Category:\s*\d+\s*[-\.]?\s*(.+)', category_response)
    if match:
        category_name = match.group(1).strip()
        # Fix: match category_name to the correct key (number) in category_map by exact name, not substring
        category_num = None
        for num, subcats in category_map.items():
            # Use instruct.csv order for category names
            instruct_names = [
                'Board of Directors',
                'Compensation',
                'Corporate Actions',
                'Corporate Governance',
                'Corporate Structure',
                'Shareholder Equity',
                'Shareholder Rights'
            ]
            if category_name.lower() == instruct_names[int(num)-1].lower():
                category_num = num
                break
        if not category_num:
            category_num = '1'  # fallback to first
    else:
        # Updated regex to match new category names from instruct.csv
        match2 = re.search(r'(Board of Directors|Compensation|Corporate Actions|Corporate Governance|Corporate Structure|Shareholder Equity|Shareholder Rights)', category_response, re.IGNORECASE)
        if match2:
            category_name = match2.group(1).strip()
            instruct_names = [
                'Board of Directors',
                'Compensation',
                'Corporate Actions',
                'Corporate Governance',
                'Corporate Structure',
                'Shareholder Equity',
                'Shareholder Rights'
            ]
            category_num = None
            for num, _ in category_map.items():
                if category_name.lower() == instruct_names[int(num)-1].lower():
                    category_num = num
                    break
            if not category_num:
                category_num = '1'
        else:
            category_num = '1'
            category_name = 'Board of Directors'
    subcategories = category_map.get(category_num, '')
    subcategory_prompt = create_subcategory_prompt(proposal_text, f"{category_num} - {category_name}", subcategories)
    
    subcategory_response = await asyncio.to_thread(find_match_mini, subcategory_prompt, proposal_text, client)
    match2 = re.search(r'Selected Sub-Category: (.+)', subcategory_response)
    if match2:
        subcategory = match2.group(1).strip()
    else:
        subcategory = ''
    row['Mini_Category'] = category_name
    row['Mini_Subcategory'] = subcategory
    return {
        'proposal_text': proposal_text,
        'Mini_Category': category_name,
        'Mini_Subcategory': subcategory
    }

@app.post("/query_mini")
async def query_llm_mini(request: Request):
    from prompts import get_openai_client
    global uploaded_data
    client = get_openai_client()
    rows = uploaded_data
    category_map = {
        '1': 'Articles/ByLaws, Board Classification, Board Composition, Board Size, Cumulative Voting, Director Remuneration, Elections, Elections, Board Size, Indemnification/Liability, Independent Board Chairman, Majority Voting, Miscellaneous Board of Directors, Proxy Access, Quorum Requirements, Remove Directors/Board Members',
        '2': 'Articles/ByLaws, Bonus Plan, Cash/Stock Bonus Plan, Directors Fees, Employee Stock Purchase Program, Employment Agreements, Executive Pay Evaluation (Say on Pay), Golden Parachutes, Miscellaneous Compensation, Omnibus Stock Plan, Restricted Stock Plan, Stock Option Plans',
        '3': 'Acquisition Agreement, Articles/ByLaws, Assets, Corporate Actions, Dividend Reinvestment Plan, Investment Advisory Agreement, Investment Agreement/Policy, Merger Plan, Miscellaneous Corporate Actions, Reorganization Plan, Scheme Arrangement',
        '4': 'Audit Related, Company Name Change, Corporate Governance, Financial Statements, Meeting Management, Miscellaneous Corporate Governance',
        '5': 'Investment Advisory Agreement, Liquidation Plan, Miscellaneous Corporate Actions, Spin Off',
        '6': 'Allot Securities, Articles/ByLaws, Authorize Stock Decrease, Authorize Stock Increase, Capital Accumulation Plan, Class of Stock Elimination, Dividend Reinvestment Plan, Miscellaneous Shareholder Equity, New Class of Stock, Par Value, Repurchase Program, Share Capital, Shareholder Equity, Stock Conversion, Stock Issuance, Stock Splits/Reverse Stock Splits, Stock Terms Revision, Voting Rights, Warrants/Bonds/Notes',
        '7': 'Antitakeover Provisions, Articles/ByLaws, Control Share Acquisition, Directors/Board Removal, Meeting Management, Miscellaneous Shareholder Rights, Supermajority Voting, Voting Rights'
    }
    job_id = str(uuid.uuid4())
    progress_dict[job_id] = {"current": 0, "total": len(rows), "done": False}
    all_results = []
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i+BATCH_SIZE]
        batch_results = await asyncio.gather(*[process_row_mini(row, client, category_map) for row in batch])
        all_results.extend(batch_results)
        progress_dict[job_id]["current"] = min(i + BATCH_SIZE, len(rows))
    progress_dict[job_id]["done"] = True
    progress_dict[job_id]["current"] = len(rows)
    return {"results": all_results, "data": uploaded_data, "job_id": job_id}

@app.get("/progress/{job_id}")
def get_progress(job_id: str):
    prog = progress_dict.get(job_id)
    if not prog:
        return {"progress": 0, "done": True}
    percent = 0
    if prog["total"] > 0:
        percent = int(100 * prog["current"] / prog["total"])
    return {"progress": percent, "done": prog["done"]}

@app.post("/plot_hist_2025")
async def plot_hist_2025(background_tasks: BackgroundTasks):
    """
    Run plot_hist_2025_proposal.py in the webappvote conda environment as a background task.
    Returns a job_id for progress tracking (optional, for now just returns status).
    """
    def run_script():
        # Use conda run to ensure the correct environment
        subprocess.run([
            'conda', 'run', '-n', 'webappvote', '--no-capture-output',
            'python', 'plot_hist_2025_proposal.py'
        ], cwd=os.path.dirname(__file__))
    background_tasks.add_task(run_script)
    return {"status": "started"}

@app.get("/default-peer-analysis")
async def serve_default_peer_analysis():
    return FileResponse("df_peer_analysis_unfavorable_propsals.csv")

@app.get("/default-large-dataset") 
async def serve_default_large_dataset():
    return FileResponse("df_peer_analysis_large_dataset.csv")
