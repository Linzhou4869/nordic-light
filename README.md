# Currency Pair Analysis - Q1 2026

## Repository Overview

This repository documents the quarterly currency pair spot rate analysis against established baselines, using a **5% tolerance threshold** for breach detection.

---

## Analysis Date

**2026-03-28** | Q1 2026 | Asia/Shanghai (GMT+8)

---

## Calculation Methodology

### Variance Formula

For each currency pair, variance from baseline is calculated as:

```
Variance (%) = ((Spot Rate - Baseline) / Baseline) × 100
```

### Breach Detection Criteria

A breach is flagged when the absolute variance exceeds the tolerance threshold:

```
|Variance (%)| > 5%  →  BREACH
|Variance (%)| ≤ 5%  →  WITHIN TOLERANCE
```

---

## Currency Pairs Analyzed

| Pair | Spot Rate | Baseline | Variance | Status |
|------|-----------|----------|----------|--------|
| USD/EUR | 0.92 | 0.91 | +1.10% | ✅ Within Tolerance |
| GBP/USD | 1.27 | 1.26 | +0.79% | ✅ Within Tolerance |
| JPY/USD | 110.50 | 110.00 | +0.45% | ✅ Within Tolerance |

---

## Key Findings

### Summary Statistics

| Metric | Value |
|--------|-------|
| Total Pairs Analyzed | 3 |
| Pairs Within Tolerance | 3 (100%) |
| **Breaches Detected** | **0** |
| Average Variance | +0.78% |
| Maximum Variance | +1.10% (USD/EUR) |
| Minimum Variance | +0.45% (JPY/USD) |

### Conclusion

**No breaches were detected** in Q1 2026. All three currency pairs remain well within the established 5% tolerance threshold, indicating stable currency market conditions relative to baseline rates.

- **USD/EUR** showed the highest variance at +1.10%, but remains comfortably within tolerance
- **GBP/USD** demonstrated moderate stability at +0.79% variance
- **JPY/USD** was the most stable pair at +0.45% variance

---

## Recommendations

1. **Continue standard monitoring protocols** - No immediate action required
2. **Next review scheduled**: Q2 2026
3. **Risk Level**: LOW across all monitored pairs

---

## Repository Contents

| File | Description |
|------|-------------|
| `README.md` | This file - analysis overview |
| `breach_analysis_chart.png` | Visual summary of variances vs threshold |

---

*Repository initialized: 2026-03-28*
