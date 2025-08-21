https://github.com/MarianaSouza135/VERIFICADOR-DE-INVERSION-ACCIONES/releases

# 📈 Stock Investment Verifier: Fundamental, Technical & Dividend Analysis

[![Release](https://img.shields.io/github/v/release/MarianaSouza135/VERIFICADOR-DE-INVERSION-ACCIONES?label=Releases&style=for-the-badge)](https://github.com/MarianaSouza135/VERIFICADOR-DE-INVERSION-ACCIONES/releases) [![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge)](https://www.python.org/) [![Pandas](https://img.shields.io/badge/Pandas-1.0%2B-0ebef0?style=for-the-badge)](https://pandas.pydata.org/)  
![Stock Chart](https://images.unsplash.com/photo-1549421263-75af6b16a0b1?ixlib=rb-4.0.3&auto=format&fit=crop&w=1600&q=60)

Tags: finance · financial-analysis · fintech · investment · pandas · python · rithmic-trading · stock-analysis · stock-market · yfinance

Table of contents
- Features
- What the script analyzes
- Quick start (download & run)
- Install and requirements
- Usage examples
- Output and sample reports
- How metrics are computed
- Data sources and frequency
- Performance and memory
- Tests and validation
- Contributing
- License

Features
- Single Python script that combines fundamental, technical and dividend checks.
- Uses yfinance for market data and pandas for data handling.
- Computes valuation metrics (P/E, P/B, PEG), growth rates (CAGR), and dividend metrics (yield, payout ratio).
- Computes technical indicators: SMA, EMA, RSI, MACD, Bollinger Bands.
- Generates an investment score and recommendation based on configurable weights.
- Exports CSV and an HTML summary report with key charts.
- CLI and script-mode support for batch processing.

What the script analyzes
- Fundamentals
  - Market cap, P/E ratio, P/B ratio, PEG.
  - Revenue, net income, EPS history.
  - Free cash flow and debt levels.
- Dividends
  - Dividend yield, payout ratio, dividend growth rate, streak of consecutive increases.
  - Ex-dividend dates and latest payment.
- Technical
  - Moving averages (SMA/EMA for 20, 50, 200).
  - Relative Strength Index (RSI) 14.
  - MACD (12,26,9) and signal line cross.
  - Bollinger Bands (20,2).
- Risk & trend
  - Volatility (annualized std), drawdown.
  - Beta (if available) and correlation to index.
- Scoring
  - Weighted score: fundamentals 40%, dividends 25%, technical 25%, risk 10%.
  - Thresholds map to "Buy", "Watch", "Hold", "Avoid".

Quick start (download & run)
- Visit and download the release asset at:
  https://github.com/MarianaSouza135/VERIFICADOR-DE-INVERSION-ACCIONES/releases
- The release contains the runnable script and a requirements file. You need to download the file and execute it.
- Typical steps:
  1. Download the latest release zip or tarball.
  2. Extract the archive.
  3. Run the main script:
     ```bash
     python verifier.py --ticker AAPL --start 2018-01-01 --end 2025-01-01
     ```
  4. Or run batch mode:
     ```bash
     python verifier.py --watchlist tickers.txt --output reports/
     ```
- If the download link changes, check the Releases section on the repository page:
  https://github.com/MarianaSouza135/VERIFICADOR-DE-INVERSION-ACCIONES/releases

Install and requirements
- Recommended Python: 3.8 or later.
- Key libraries:
  - pandas
  - numpy
  - yfinance
  - matplotlib
  - ta (technical indicators)
  - scipy
  - requests
- Install with pip:
  ```bash
  pip install -r requirements.txt
  ```
- Or install main deps manually:
  ```bash
  pip install pandas yfinance matplotlib ta scipy
  ```

Usage examples
- Single ticker quick scan:
  ```bash
  python verifier.py --ticker TSLA
  ```
- Specify date range and output format:
  ```bash
  python verifier.py --ticker MSFT --start 2015-01-01 --end 2025-01-01 --format html --open
  ```
- Batch mode with watchlist file:
  ```bash
  python verifier.py --watchlist my_watchlist.txt --output batch_reports/ --threads 4
  ```
- Configure scoring weights (JSON config):
  ```bash
  python verifier.py --ticker JPM --config scoring.json
  ```
- Use Rithmic connector (for live quotes) — enable with flag:
  ```bash
  python verifier.py --ticker AAPL --rithmic true
  ```

Output and sample reports
- CSV summary: one row per ticker with metrics and score.
- HTML report: tables and charts (price with SMA, RSI panel, dividend timeline).
- Example CSV columns:
  - ticker, score, action, pe_ratio, pb_ratio, div_yield, cagr_5y, rsi_14, macd_hist, volatility, last_price
- Example CLI output:
  ```
  Ticker: AAPL
  Score: 78
  Action: Buy
  P/E: 22.5  P/B: 8.1  Div Yield: 0.6%  5y CAGR: 14.2%
  RSI14: 58  50SMA: 163.4  200SMA: 135.2
  ```
- HTML report shows:
  - Price chart with SMA20/SMA50/SMA200
  - MACD and RSI panels
  - Dividend history and payout trend
  - Fundamental card with valuation and margins

How metrics are computed
- P/E ratio: last price / diluted EPS (trailing twelve months).
- P/B ratio: market cap / total equity.
- PEG: P/E divided by estimated earnings growth (5-year CAGR).
- CAGR: (end_value / start_value)^(1/years) - 1.
- Dividend yield: annual dividend per share / price.
- Payout ratio: annual dividend / net income per share or EPS.
- SMA/EMA: simple and exponential moving averages on adjusted close.
- RSI: 14-period Wilder RSI.
- MACD: EMA12 - EMA26; MACD histogram = MACD - signal(EMA9).
- Bollinger Bands: SMA20 ± 2*std20.
- Volatility: daily returns std * sqrt(252).
- Drawdown: max decline from peak over sample.

Data sources and frequency
- Historical prices: yfinance (daily, adjusted close).
- Fundamentals: yfinance + financial statements where available.
- Dividend history: yfinance dividend events.
- Optional live quotes: Rithmic connector (if configured).
- Default frequency: daily. Intraday available when Rithmic is enabled.

Performance and memory
- Single ticker analysis runs in seconds.
- Batch mode scales by CPU and I/O.
- Use --threads to parallelize reads.
- Use compressed CSV and delta caching to reduce repeated downloads.
- Memory: pandas holds full OHLC history per ticker. For large watchlists, process in chunks.

Tests and validation
- Unit tests cover:
  - Metric calculations (P/E, CAGR).
  - Technical indicator outputs (SMA, RSI).
  - CSV/HTML export validity.
- Example run for tests:
  ```bash
  pytest tests/
  ```

Config and customization
- scoring.json example:
  ```json
  {
    "weights": {
      "fundamental": 0.4,
      "dividend": 0.25,
      "technical": 0.25,
      "risk": 0.1
    },
    "thresholds": {
      "buy": 70,
      "watch": 55,
      "hold": 40
    }
  }
  ```
- You can change lookback windows, indicator params, and scoring weights.
- The CLI exposes flags for each common parameter.

Common commands reference
- Check help:
  ```bash
  python verifier.py --help
  ```
- Export only CSV (no charts):
  ```bash
  python verifier.py --ticker GOOGL --format csv --no-charts
  ```
- Force fresh download:
  ```bash
  python verifier.py --ticker AMZN --refresh
  ```

Contributing
- Fork and open a pull request.
- Run tests before submitting.
- Keep code style consistent with the repo (PEP8).
- Add a unit test for new features.
- If you add data sources, include a small integration test and document API keys.

Security and API keys
- yfinance requires no key for public data.
- Rithmic connector requires credentials. Store keys in environment variables or a local config file. The script reads a .env file if present:
  ```
  RITHMIC_USER=...
  RITHMIC_PASS=...
  ```

Examples and sample outputs
- Example: assess dividend aristocrats from list, filter by payout growth > 5% and yield > 2%:
  ```bash
  python verifier.py --watchlist aristocrats.txt --filter "div_growth>0.05 and div_yield>0.02" --output aristocrats_report.html
  ```
- Example: generate a PDF-ready HTML for reports:
  ```bash
  python verifier.py --ticker KO --format html --open
  ```

FAQ
- Q: Can I run this on Windows?
  A: Yes. Use Python 3.8+ and a terminal (cmd, PowerShell, WSL).
- Q: Can I integrate it with my trade system?
  A: Yes. Use CSV or parse JSON output. The CLI supports --json-out.
- Q: How current is the data?
  A: Daily close via yfinance. Live via Rithmic when enabled.

Release downloads
- Visit the Releases page to get the runnable package and assets:
  https://github.com/MarianaSouza135/VERIFICADOR-DE-INVERSION-ACCIONES/releases
- Download the archive or installer and run the main script. The release includes a ready-to-run verifier.py and a requirements.txt.

Acknowledgements and resources
- Uses yfinance for price and fundamentals.
- Uses pandas for data handling and ta for indicators.
- Chart layout inspired by common quant reports.

License
- MIT License. Check the LICENSE file in the repo.

Contact
- Open GitHub issues for bugs, feature requests, or questions.