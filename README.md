# Movies Data Analysis Dashboard

An interactive Streamlit dashboard built from your `movies_dataset.csv` dataset —
covers genre distribution, popularity leaders, vote categories, and release
year trends, with sidebar filters for genre, year range, and vote category.

## Setup in VS Code

1. Open this folder in VS Code (`File > Open Folder...`).
2. Open a terminal in VS Code (`` Ctrl+` `` / `` Cmd+` ``).
3. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Make sure `movies_dataset.csv` is in the same folder as `app.py`.
6. Run the dashboard:
   ```bash
   streamlit run app.py
   ```
   It will open automatically in your browser at `http://localhost:8501`.

## Files

- `app.py` — the dashboard app
- `movies_dataset.csv` — your dataset
- `requirements.txt` — Python dependencies

## Customizing

- Colors: change the `ACCENT` and `PALETTE` variables near the top of `app.py`.
- Add more charts: follow the pattern of the existing `st.columns()` /
  `px.<chart_type>()` blocks.
- The data cleaning in `load_data()` mirrors the steps from your original
  notebook (dropping unused columns, casting release date, quartile-based
  vote categories, exploding multi-genre rows).
