import argparse
import pandas as pd
import numpy as np
from scipy import stats
#%%
%pip install jupyter
#%%

"""
Release impact tester (simple Python I/O) — WITH:
1) Fixed-N valid-day windows (n_before/n_after target = window_days)
2) Min/Max scanned dates (span needed to collect N valid days)
3) Excluded-day counts (how many days were skipped while collecting N valid days)
4) List-agg Drop Calendar Category Description across ALL scanned days
5) NEW: Weighted funnel rates (ratio-of-sums) across configurable numerators with Sessions as denominator

Key idea for fixed-N windows
----------------------------
For each release and window N:
- We scan day-by-day outward from release date until we collect EXACTLY N "valid" days per side.
- "Valid day" criteria differ slightly by section:
  A) Daily metric tests: metric must be present AND day not excluded
  B) Weighted rates: denominator (Sessions) must be present AND day not excluded
     (numerators missing on a valid day are treated as 0)

This makes n_before/n_after ~ N (unless we run out of data).
"""
#%%
# =============================
# USER INPUTS (edit these)
# =============================
CSV_PATH = "***/funnel_metrics_data_full_app.csv"

DATE_COL = "Event Date"

TECH_RELEASE_COL = "Tech Release Summary"

SALE_FLAG_COL = "Sale Day Flag (Yes / No)"
DROP_FLAG_COL = "Drop Day Flag (Yes / No)"
DROP_DESC_COL = "Drop Calendar Category Description"

DAILY_METRICS = [
    "CVR (est)",
    # "PDP rate (est)",
    # "PLP rate (est)",
    # "ATC rate (est)"
]

# NEW: Weighted funnel-rate section
# Add as many rates as you want: numerator column / sessions denominator
WEIGHTED_RATES = {
    "CVR_weighted": {"numerator": "Orders (est)", "denominator": "Sessions"},
    # "PDP_rate_weighted": {"numerator": "PDP Sessions", "denominator": "Sessions"},
    # "PLP_rate_weighted": {"numerator": "PLP Sessions", "denominator": "Sessions"},
    # "ATC_rate_weighted": {"numerator": "PLP Sessions", "denominator": "Sessions"},
}

WINDOWS = [14, 28] ## getting rid of these bc it is taking too long ## , 90, 180, 365]
ALPHA = 0.05

EXCLUDE_SALE_DROP_DAYS = True
EXCLUDE_BUFFER_DAYS = 1   # excludes +/- this many days around release date

# Optional: write results to CSV
WRITE_OUTPUT = True
OUTPUT_PATH = "***/release_impacts_out_NEW.csv"
#%%
# -----------------------------
# Helpers
# -----------------------------
def _is_yes(x) -> bool:
    if pd.isna(x):
        return False
    return str(x).strip().lower() == "yes"


def _to_number(s: pd.Series) -> pd.Series:
    """
    Coerce metrics to numeric:
    - strips $, commas, and % signs
    - invalid parses -> NaN
    """
    s = s.astype(str)
    s = s.str.replace(r"[\$,٪%]", "", regex=True).str.replace(",", "", regex=False)
    s = s.replace({"nan": np.nan, "None": np.nan, "": np.nan, " ": np.nan})
    return pd.to_numeric(s, errors="coerce")

def benjamini_hochberg(pvals: np.ndarray) -> np.ndarray:
    """
    BH-FDR adjustment.
    Why: multiple windows = multiple tests per (release, metric).
    Returns adjusted p-values in original order.
    """
    pvals = np.asarray(pvals, dtype=float)
    n = len(pvals)
    order = np.argsort(pvals)
    ranked = pvals[order]
    adj = ranked * n / (np.arange(1, n + 1))
    adj = np.minimum.accumulate(adj[::-1])[::-1]  # enforce monotonicity
    adj = np.clip(adj, 0, 1)
    out = np.empty_like(adj)
    out[order] = adj
    return out


def run_pre_post_test(before: np.ndarray, after: np.ndarray) -> tuple[str, float]:
    """
    Choose a simple test automatically:
    - Welch t-test if both groups >= 10 daily points (robust to unequal variance)
    - Mann–Whitney U if smaller sample sizes (non-parametric)
    """
    before = np.asarray(before, dtype=float)
    after = np.asarray(after, dtype=float)

    if len(before) >= 10 and len(after) >= 10:
        _, p = stats.ttest_ind(before, after, equal_var=False, nan_policy="omit")
        return "welch_t_test", float(p)

    # Mann-Whitney cannot handle NaNs; caller should dropna already
    _, p = stats.mannwhitneyu(before, after, alternative="two-sided")
    return "mann_whitney_u", float(p)


import pandas as pd

def _list_agg_unique(series: pd.Series, sep: str = " | "):
    if series is None:
        return None
    s = series.dropna().astype(str).str.strip()
    s = s[s != ""]
    if s.empty:
        return None
    return sep.join(sorted(s.unique()))
#%%

# =============================
# Precompute a daily table (FAST + consistent)  --- this is to help run times when iterating through different timeframe windows 
# =============================
def build_daily_table(df: pd.DataFrame, numeric_cols: list[str]) -> pd.DataFrame:
    """
    Builds one row per date with:
      - mean of each numeric column (safe if multiple rows/day; adjust if needed)
      - exclusion flags by date
      - list-agg drop descriptions by date
    """
    df = df.copy()
    df[DATE_COL] = pd.to_datetime(
        df[DATE_COL],
        format="%m/%d/%y",
        errors="coerce"
    )
    df = df.dropna(subset=[DATE_COL])
    df["_date"] = df[DATE_COL].dt.normalize()

    # Ensure numeric columns are numeric
    for c in numeric_cols:
        if c in df.columns:
            df[c] = _to_number(df[c])

    # Aggregate numeric columns to daily grain (mean is safe; for counts you may prefer sum)
    # If your source is already daily-grain, this does nothing harmful.
    agg_dict = {c: "mean" for c in numeric_cols if c in df.columns}

    daily = df.groupby("_date", as_index=False).agg(agg_dict) if agg_dict else df[["_date"]].drop_duplicates()

    # Exclusion flag per date (True if any row for that date is excluded)
    excl = df.groupby("_date", as_index=False).agg(is_excluded=("_exclude", "max"))

    # Drop description list-agg per date
    if DROP_DESC_COL in df.columns:
        desc = df.groupby("_date")[DROP_DESC_COL].apply(_list_agg_unique).reset_index().rename(columns={DROP_DESC_COL: "drop_desc_by_date"})
    else:
        desc = pd.DataFrame({"_date": daily["_date"], "drop_desc_by_date": None})

    out = daily.merge(excl, on="_date", how="left").merge(desc, on="_date", how="left")
    out = out.sort_values("_date").set_index("_date")
    return out

#%%
# =============================
# Fixed-N scanning collectors
# =============================
def collect_fixed_n_days_daily_metric(
    daily: pd.DataFrame,
    release_date: pd.Timestamp,
    metric_col: str,
    n_days: int,
    direction: str,
):
    """
    Collect exactly n_days valid days for DAILY metric tests.

    Valid day criteria:
      - day exists in daily table
      - is_excluded == False
      - metric_col not null
    """
    if direction not in ("before", "after"):
        raise ValueError("direction must be 'before' or 'after'")

    step = -1 if direction == "before" else 1
    cursor = release_date.normalize() + pd.Timedelta(days=step)

    included_vals = []
    scanned_dates = []
    scanned_desc_tokens = []

    skipped = 0
    scanned_total = 0

    min_date = daily.index.min() if len(daily.index) else None
    max_date = daily.index.max() if len(daily.index) else None

    while len(included_vals) < n_days:
        if min_date is not None and cursor < min_date and direction == "before":
            break
        if max_date is not None and cursor > max_date and direction == "after":
            break

        scanned_total += 1
        scanned_dates.append(cursor.date())

        if cursor in daily.index:
            row = daily.loc[cursor]
            # collect drop descriptions for ALL scanned days (context)
            d = row.get("drop_desc_by_date", None)
            if d:
                scanned_desc_tokens.extend([p.strip() for p in str(d).split("|") if p.strip()])

            metric_val = row.get(metric_col, np.nan)
            is_excl = bool(row.get("is_excluded", False))

            if (not is_excl) and pd.notna(metric_val):
                included_vals.append(float(metric_val))
            else:
                skipped += 1
        else:
            # day missing from daily table
            skipped += 1

        cursor = cursor + pd.Timedelta(days=step)

    min_scanned = min(scanned_dates) if scanned_dates else None
    max_scanned = max(scanned_dates) if scanned_dates else None
    desc_listagg = " | ".join(sorted(set(scanned_desc_tokens))) if scanned_desc_tokens else None

    return {
        "included_values": np.array(included_vals, dtype=float),
        "included_n": int(len(included_vals)),
        "min_date_scanned": min_scanned,
        "max_date_scanned": max_scanned,
        "excluded_days_count": int(skipped),
        "days_scanned_total": int(scanned_total),
        "drop_desc_listagg_all_scanned": desc_listagg,
    }
#%%
def collect_fixed_n_days_weighted_denominator(
    daily: pd.DataFrame,
    release_date: pd.Timestamp,
    denom_col: str,
    numer_cols: list[str],
    n_days: int,
    direction: str,
):
    """
    Collect exactly n_days valid days for WEIGHTED rate calculations.

    Valid day criteria:
      - day exists in daily table
      - is_excluded == False
      - denom_col not null and > 0 (Sessions)
    Numerators:
      - if missing on a valid day, treated as 0
    """
    if direction not in ("before", "after"):
        raise ValueError("direction must be 'before' or 'after'")

    step = -1 if direction == "before" else 1
    cursor = release_date.normalize() + pd.Timedelta(days=step)

    denom_vals = []
    numer_vals = {c: [] for c in numer_cols}

    scanned_dates = []
    scanned_desc_tokens = []

    skipped = 0
    scanned_total = 0

    min_date = daily.index.min() if len(daily.index) else None
    max_date = daily.index.max() if len(daily.index) else None

    while len(denom_vals) < n_days:
        if min_date is not None and cursor < min_date and direction == "before":
            break
        if max_date is not None and cursor > max_date and direction == "after":
            break

        scanned_total += 1
        scanned_dates.append(cursor.date())

        if cursor in daily.index:
            row = daily.loc[cursor]
            d = row.get("drop_desc_by_date", None)
            if d:
                scanned_desc_tokens.extend([p.strip() for p in str(d).split("|") if p.strip()])

            denom = row.get(denom_col, np.nan)
            is_excl = bool(row.get("is_excluded", False))

            if (not is_excl) and pd.notna(denom) and float(denom) > 0:
                denom_vals.append(float(denom))
                for c in numer_cols:
                    v = row.get(c, 0.0)
                    numer_vals[c].append(float(v) if pd.notna(v) else 0.0)
            else:
                skipped += 1
        else:
            skipped += 1

        cursor = cursor + pd.Timedelta(days=step)

    min_scanned = min(scanned_dates) if scanned_dates else None
    max_scanned = max(scanned_dates) if scanned_dates else None
    desc_listagg = " | ".join(sorted(set(scanned_desc_tokens))) if scanned_desc_tokens else None

    return {
        "denom_values": np.array(denom_vals, dtype=float),
        "numer_values": {c: np.array(v, dtype=float) for c, v in numer_vals.items()},
        "included_n": int(len(denom_vals)),
        "min_date_scanned": min_scanned,
        "max_date_scanned": max_scanned,
        "excluded_days_count": int(skipped),
        "days_scanned_total": int(scanned_total),
        "drop_desc_listagg_all_scanned": desc_listagg,
    }
#%%
def two_proportion_z_test(num_before, den_before, num_after, den_after) -> float:
    """
    Two-proportion z-test p-value (two-sided), pooled variance.
    """
    if den_before <= 0 or den_after <= 0:
        return np.nan
    p_pool = (num_before + num_after) / (den_before + den_after)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / den_before + 1 / den_after))
    if se == 0:
        return 1.0
    z = ((num_after / den_after) - (num_before / den_before)) / se
    return float(2 * (1 - stats.norm.cdf(abs(z))))

#%%
# -----------------------------
# Core analysis
# -----------------------------
"""
Compute pre/post tests for each (release, metric, window).

Parameters explained
--------------------
metrics:
  Which metric columns to test.
windows:
  List of day windows (e.g. [7, 14, 30, 60...]).
exclude_sale_drop_days:
  If True, remove "special" days from windows to reduce confounding.
exclude_buffer_days:
  Remove +/- N days around the release date (deployment artifacts).
alpha:
  Significance threshold for flags.

Returns
-------
Long / tidy DataFrame of results.
"""


# =============================
# Core analysis
# =============================
def analyze_release_impacts(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df[DATE_COL] = pd.to_datetime(
        df[DATE_COL],
        format="%m/%d/%y",
        errors="coerce"
    )
    df = df.dropna(subset=[DATE_COL]).sort_values(DATE_COL)

    # Calendar exclusions
    if EXCLUDE_SALE_DROP_DAYS:
        df["_is_sale_day"] = df[SALE_FLAG_COL].apply(_is_yes) if SALE_FLAG_COL in df.columns else False
        df["_is_drop_day"] = df[DROP_FLAG_COL].apply(_is_yes) if DROP_FLAG_COL in df.columns else False
        df["_exclude_calendar"] = df["_is_sale_day"] | df["_is_drop_day"]
    else:
        df["_exclude_calendar"] = False

    # Identify releases (non-null summary)
    releases = (
        df.loc[df[TECH_RELEASE_COL].notna(), [DATE_COL, TECH_RELEASE_COL]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    # Collect all numeric columns we might need in the daily table
    weighted_needed_cols = []
    for _, cfg in WEIGHTED_RATES.items():
        weighted_needed_cols.extend([cfg["numerator"], cfg["denominator"]])
    all_needed_numeric = sorted(set([c for c in (DAILY_METRICS + weighted_needed_cols) if c in df.columns]))

    # Coerce numeric columns to numeric now (prevents repeated coercion)
    for c in all_needed_numeric:
        df[c] = _to_number(df[c])

    all_rows = []

    # ==========================================================
    # SECTION A) Daily-metric tests (existing behavior)
    # ==========================================================
    for _, rel in releases.iterrows():
        release_date = rel[DATE_COL]
        release_name = rel[TECH_RELEASE_COL]

        # Buffer exclusion
        if EXCLUDE_BUFFER_DAYS > 0:
            buffer_start = release_date - pd.Timedelta(days=EXCLUDE_BUFFER_DAYS)
            buffer_end = release_date + pd.Timedelta(days=EXCLUDE_BUFFER_DAYS)
            df["_exclude_buffer"] = (df[DATE_COL] >= buffer_start) & (df[DATE_COL] <= buffer_end)
        else:
            df["_exclude_buffer"] = False

        df["_exclude"] = df["_exclude_calendar"] | df["_exclude_buffer"]

        # Build daily table ONCE per release (buffer changes per release)
        daily = build_daily_table(df, numeric_cols=all_needed_numeric)

        for metric in [m for m in DAILY_METRICS if m in df.columns]:
            for window in WINDOWS:
                pre = collect_fixed_n_days_daily_metric(daily, release_date, metric, window, "before")
                post = collect_fixed_n_days_daily_metric(daily, release_date, metric, window, "after")

                # Require enough points
                if pre["included_n"] < 3 or post["included_n"] < 3:
                    continue

                test_used, p_value = run_pre_post_test(pre["included_values"], post["included_values"])
                mean_before = float(np.mean(pre["included_values"]))
                mean_after = float(np.mean(post["included_values"]))
                pct_change = (mean_after - mean_before) / mean_before if mean_before != 0 else np.nan

                all_rows.append({
                    "analysis_type": "daily_metric",
                    "tech_release"
