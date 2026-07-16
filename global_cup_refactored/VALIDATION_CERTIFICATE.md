# VALIDATION CERTIFICATE
### Global Cup Market Dashboard — Refactor Workflow
**Certified:** 2026-06-05  
**Workflow:** Dynamic, phase-gated — each phase required PASS before proceeding

---

## Phase Results

| Phase | Description | Checks | Result |
|---|---|---|---|
| Phase 0 | Pre-flight: imports + dependencies | 7 | **PASS** |
| Phase 1 | Engine validation: original vs refactored | 70 | **PASS** |
| Phase 2 | Structural integrity: files, formulas, tax rates | 30 | **PASS** |
| Phase 3 | App syntax + import completeness | 20 | **PASS** |
| Phase 4 | Score isolation: no engine mutation, weights | 18 | **PASS** |
| Phase 5 | Data file integrity: CSV schema + ticker count | 10 | **PASS** |

**Total checks: 155 / 155 PASS.  Zero failures.  Zero warnings.**

---

## Phase 1 Detail — Engine Validation (70 checks)

Tickers tested: `VOO`, `SCHD`, `JEPI`, `360750.KS`, `441680.KS`  
Period: 2020-01-01 → 2024-12-31 · Trigger: 10% · Initial: $10,000 · Tax: 15%

Metrics compared per ticker (14 each):
- current_price · high_price · drawdown_pct · trigger_price · trigger_hit
- ttm_dividend · dividend_yield
- reinvest.final_value · total_ext · final_shares
- reinvest.cum_gross · cum_tax · cum_net · cagr

All 70 checks: **PASS**

---

## Phase 2 Detail — Critical Formula Verification

| Formula | Original (line) | Refactored | Match |
|---|---|---|---|
| Drawdown | `(current_price / high_price - 1.0) * 100.0` | identical | ✅ |
| Trigger price | `high_price * (1.0 - inp.trigger_pct / 100.0)` | identical | ✅ |
| Trigger hit | `drawdown_pct <= -inp.trigger_pct` | identical | ✅ |
| TTM window | `pd.Timedelta(days=365)` | identical | ✅ |
| Gross dividend | `shares * div_per_share` | identical | ✅ |
| Tax | `gross_dividend * tax_rate` | identical | ✅ |
| Net dividend | `gross_dividend - tax` | identical | ✅ |
| Reinvest shares | `net_dividend / price` | identical | ✅ |
| CAGR | `(final_value / total_ext) ** (1/years) - 1` | identical | ✅ |

Original file size: 55,466 bytes — **unchanged**  
Backup file size:  55,466 bytes — **unchanged**

---

## Phase 4 Detail — Score Isolation

- `scoring.py` does NOT call `run_analysis()`
- `scoring.py` does NOT call `run_dividend_reinvest_backtest()`
- `scoring.py` does NOT import yfinance
- No `AnalysisResult` field is mutated anywhere in scoring or ui
- Score weights: 0.35 + 0.30 + 0.20 + 0.15 = **1.0000** ✅

---

## Phase 5 Detail — Ticker Universe

| Market | CSV File | Tickers | Empties | Duplicates |
|---|---|---|---|---|
| United States | tickers_us.csv | 149 | 0 | 0 |
| Korea | tickers_korea.csv | 71 | 0 | 0 |
| Japan | tickers_japan.csv | 11 | 0 | 0 |
| European Union | tickers_eu.csv | 34 | 0 | 0 |
| Global | tickers_global.csv | 55 | 0 | 0 |
| **Total** | | **320** | **0** | **0** |

---

## Final Verdict

```
╔══════════════════════════════════════════════════╗
║  REFACTOR COMPLETE — ALL PHASES PASSED           ║
║                                                  ║
║  Engine:        PRESERVED (155/155 checks)       ║
║  Dividend:      PRESERVED                        ║
║  Trigger logic: PRESERVED                        ║
║  Original files: UNTOUCHED (55,466 bytes each)   ║
║  App launches:  streamlit run app.py             ║
╚══════════════════════════════════════════════════╝
```

---

## Stop Conditions Encountered

None. No phase failed. No failure report was required.

Had any phase failed, the workflow would have written a `FAILURE_REPORT.md`
and halted immediately without proceeding to the next phase.

---

## Run Instructions

```bash
cd /home/zealatan/MARKETING_ORC/invest/global_cup_refactored

# Validate anytime (requires network)
python3 validate_engine.py

# Launch app
streamlit run app.py
```
