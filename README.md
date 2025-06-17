# LLM Webapp Vote Proposal

A FastAPI + OpenAI web application for interactive CSV upload, editing, LLM-based category extraction, and advanced visualization of shareholder voting proposals.

## Features

- **CSV Upload & Table Display:** Upload one or two CSVs, view and join datasets, scrollable and sortable tables.
- **Dependent Dropdowns:** Filter and sort data using dynamic dropdowns.
- **LLM Extraction:** Extract categories/subcategories using OpenAI LLMs (nano/mini), with job-based progress tracking.
- **Visualization:** For each proposal, view a detailed PNG chart of share composition by cumulative shareholder percentile.
- **Multi-Select Comparison:** Select up to 3 rows to compare proposal illustrations side by side.
- **Export:** Download processed CSVs.
- **Secure API Key Handling:** OpenAI API key is stored in `openai_key.csv` (excluded from git).

## File Structure

- `backend.py` — FastAPI backend with endpoints for upload, data, LLM queries, and progress.
- `webui.html` — Main web UI for CSV upload, table, LLM extraction, and export.
- `detail.html` — Advanced UI for dual CSV join, row selection, and illustration comparison.
- `visual.py` — Efficient batch plotting of proposal illustrations (PNG) from CSV data.
- `prompts.py` — LLM prompt logic and OpenAI API key loading.
- `openai_key.csv` — **Not tracked by git.** Store your OpenAI API key here as:
  ```csv
  key
  sk-...
  ```
- `images/` — Output PNGs for each proposal (ignored by git if desired).

## Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/llm-webapp-voteproposal.git
   cd llm-webapp-voteproposal
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # Or manually: fastapi, uvicorn, openai, pandas, numpy, matplotlib
   ```
3. **Add your OpenAI API key:**
   - Create `openai_key.csv` in the project root:
     ```csv
     key
     sk-REPLACE_WITH_YOUR_OPENAI_KEY
     ```
4. **Run the backend:**
   ```bash
   uvicorn backend:app --reload
   ```
5. **Open the UI:**
   - Open `webui.html` or `detail.html` in your browser (or serve statically).

## Usage

- Upload a CSV to view and analyze proposals.
- (Optional) Upload a second CSV and join on a common key.
- Select up to 3 rows to compare proposal illustrations.
- Use LLM extraction for category suggestions.
- Export processed data as needed.

## Security
- Sensitive files (`*.csv`, `openai_key.csv`, `*.png`) are excluded from git by `.gitignore`.
- **Never commit your OpenAI API key.**

## License
MIT

---

For questions or contributions, open an issue or pull request on GitHub.
