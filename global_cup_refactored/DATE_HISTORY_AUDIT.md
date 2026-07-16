# Date History Audit
**Date:** 2026-06-06

---

## Where `start_date` is created

**File:** `global_cup/ui.py` — `render_controls()`

```python
today = date.today()
default_start = today.replace(year=today.year - 5)   # DEFAULT: 5-year lookback
```

The user-editable text input (`Start date (YYYY-MM-DD)`) previously hidden under
"Advanced settings" expander. **Now always visible** (step 009 fix).

`_parse_date(raw_start, default_start)` converts the text input string to a `date`
object, falling back to `default_start` on parse failure.

---

## Where `start_date` is passed

1. `render_controls()` → returns `UserInput(start_date=start_date, end_date=end_date, ...)`
2. `app.py` passes `user_input` to `run_analysis(user_input)`
3. `run_analysis()` passes `inp.start_date` and `inp.end_date` to:
   - `download_price(ticker, start_date, end_date)`
   - `download_dividends(ticker, start_date, end_date)`

---

## Where yfinance download happens

**File:** `global_cup/data_loader.py`

```python
@st.cache_data(ttl=3600)
def download_price(ticker: str, start_date: date, end_date: date) -> pd.DataFrame:
    df = yf.download(
        ticker,
        start=start_date,
        end=end_date + timedelta(days=1),
        auto_adjust=False,
        progress=False,
        threads=False,
    )
```

- Uses explicit `start=` and `end=` — **no `period=` used**.
- Cache key is `(ticker, start_date, end_date)` — Streamlit `@st.cache_data` uses all
  function arguments as the cache key automatically.

---

## Where data is trimmed

`download_dividends()` filters dividends to `[start_date, end_date]` range.  
`get_close_series()` calls `dropna()` but does **not** trim by date.  
No other trimming exists.

---

## Hardcoded 2010 / 2020 search results

```
grep -R "2010" .   → global_cup/formatting.py comment only (docstring example "2020.0 → '2020'")
grep -R "2020" .   → global_cup/formatting.py docstring only
grep -R "period="  → not found in app code (only in validate_history_range.py for docs)
```

**No hardcoded date truncation exists in the codebase.**

---

## Root cause of "data starting around 2010" for VOO

**Not a bug.** VOO (Vanguard S&P 500 ETF) was listed on September 9, 2010.  
When a user requests start_date=2000-01-01, yfinance correctly returns data from
VOO's actual inception date (2010-09-09). This is the earliest available data.

**Confirmed by `validate_history_range.py`:**
```
VOO: actual_first = 2010-09-09 / actual_last = 2026-06-05 / 3,959 rows   ✅ OK
SPY: actual_first = 2000-01-03 / actual_last = 2026-06-05 / 6,646 rows   ✅ OK
QQQ: actual_first = 2000-01-03 / actual_last = 2026-06-05 / 6,646 rows   ✅ OK
```

---

## Summary

| Question | Answer |
|---|---|
| Hardcoded 2010 cutoff? | No |
| Hardcoded 2020 cutoff? | No |
| `period=` used instead of `start=`? | No — explicit start/end always |
| Cache key includes start+end? | Yes — Streamlit cache_data uses all args |
| Data trimmed anywhere? | Only dividends trimmed to requested range |
| VOO starting 2010 is a bug? | No — VOO inception was Sep 2010 |
| User can select 2000-01-01? | Yes — text input accepts any valid date |
