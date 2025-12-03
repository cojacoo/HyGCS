"""
GCS Classification Functions
=============================
Geochemical phase classification using percentile-based thresholds,
hysteresis indices, C-Q slopes, and high-resolution flow dynamics.

Scientific basis:
- Percentile-based thresholds for compound-agnostic classification
- C-Q slope reveals mechanistic processes:
  * Positive (b > 0): Dilution-dominated (flushing signature)
  * Negative (b < 0): Enrichment (loading signature)  
  * Near-zero (|b| < 0.1): Chemostatic buffering
- Window-scale hysteresis captures temporal dynamics
- Hierarchical rules prioritize phase detection

Implements hierarchical rule-based classification for 6 geochemical phases:
- Flushing (F): Rapid mobilization as steep concentration decline during high flow, positive C-Q slope
- Loading (L): Accumulation phase by concentration rising to maximum, negative C-Q slope
- Chemostatic (C): Low hysteresis, low-variability, stable behavior, flat C-Q slope
- Dilution (D): Post-flush recovery, declining flow
- Recession (R): Late cycle, low CVc/CVq, both declining
- Variable (V): Ambiguous/mixed patterns

Version 0.5 (2025-12-02) (cc-by) conrad.jackisch@tbt.tu-freiberg.de, antita.sanchez@mineral.tu-freiberg.de
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional

# Import from core module (renamed functions in v0.5)
from gcs_core import (
    compute_cvc_cvq_windows,
    compute_cq_slope,
    analyze_segment_flow_dynamics,
    compute_change_percentiles
)


def classify_segment_phase(
    row: pd.Series,
    percentiles: Dict
) -> Tuple[str, float, List[str]]:
    """
    Classify a single segment into one of 6 geochemical phases.

    Classification logic with high-resolution Q dynamics using percentile-based thresholds.

    Implements hierarchical rule-based classification for 6 geochemical phases:
    - Flushing (F): Steep concentration decline during high flow, positive C-Q slope
    - Loading (L): Concentration rising to maximum, negative C-Q slope
    - Chemostatic (C): Low hysteresis, stable behavior, flat C-Q slope
    - Dilution (D): Post-flush recovery, declining flow
    - Recession (R): Late cycle, low CVc/CVq, both declining
    - Variable (V): Ambiguous/mixed patterns

    row :: pd.Series Segment data with hysteresis, flow, temporal context, and C-Q slope
    percentiles :: dict Percentile thresholds for classification

    Returns :: tuple (phase, confidence, rules_triggered)
        - phase: str, one of 'F', 'L', 'C', 'D', 'R', 'V'
        - confidence: float, 0.0-1.0
        - rules_triggered: list of str, diagnostic information
    """

    # Extract variables
    hi_zuecco = row.get('window_HI_zuecco', 0.0)
    hi_lloyd = row.get('window_HI_lloyd', 0.0)
    hi_harp = row.get('window_HI_harp', 0.0)
    
    # Use Zuecco as primary (most robust), with fallback
    if not np.isnan(hi_zuecco):
        hi = hi_zuecco
    elif not np.isnan(hi_lloyd):
        hi = hi_lloyd
    elif not np.isnan(hi_harp):
        hi = hi_harp
    else:
        hi = 0.0

    q_pos = row.get('Q_position', 'medium')
    c_pos = row.get('C_position', 'medium')
    flow_diff = row.get('flow_diff', 0)
    conc_diff = row.get('conc_diff', 0)
    cvc_cvq = row.get('CVc_CVq', np.nan)

    # Extract C-Q slope
    cq_slope = row.get('cq_slope_loglog', np.nan)

    # High-res dynamics
    flow_phase = row.get('highres_flow_phase', 'unknown')
    days_since_peak = row.get('highres_days_since_peak', np.nan)
    q_level = row.get('highres_q_level', q_pos)

    # Temporal context
    hi_transition = row.get('HI_transition', 'stable')
    prev_c_pos = row.get('prev_C_position', 'none')
    prev_conc_diff = row.get('prev_conc_diff', 0)
    prev2_conc_diff = row.get('prev2_conc_diff', 0)
    c_trajectory = row.get('C_trajectory', 'stable')
    wai = row.get('WAI', np.nan)

    rules = []

    # ==================================================================================
    # PRIORITY 1: FLUSHING
    # Criteria: Steep C decline + High Q + Positive C-Q slope (dilution signature)
    # ==================================================================================

    current_steep = conc_diff < percentiles['dC_p08']
    prev_steep = prev_conc_diff < percentiles['dC_p08']
    prev2_steep = prev2_conc_diff < percentiles['dC_p08']

    q_at_peak = flow_phase in ['at_peak', 'rising', 'early_decline']
    q_high = q_level in ['high', 'medium'] or q_pos == 'high'

    c_was_high = prev_c_pos == 'high' or c_pos == 'high' or c_trajectory in ['steep_decline_from_high', 'steep_decline']

    # C-Q slope checks for flushing (positive = dilution)
    cq_slope_positive = not np.isnan(cq_slope) and cq_slope > 0.15

    # Current steep decline during high Q
    if current_steep and (q_at_peak or q_high):
        rules.extend(['current_steep_decline', 'q_high_or_peak'])
        
        # C-Q slope confirms dilution mechanism
        if cq_slope_positive:
            rules.append('positive_cq_slope_dilution')
            confidence = 0.95 if c_was_high else 0.90
        else:
            confidence = 0.92 if c_was_high else 0.85
            
        if c_was_high:
            rules.append('c_was_high')
            
        # WAI (water availability index) can boost confidence
        if not np.isnan(wai) and wai > 1.0:
            rules.append('high_wai_wet')
            confidence = min(0.98, confidence + 0.03)
            
        return 'F', confidence, rules

    # Aftermath: previous steep decline, Q still elevated
    if prev_steep and q_high and not np.isnan(days_since_peak) and days_since_peak < 15:
        rules.extend(['prev_steep_decline', 'q_high', 'recent_peak'])
        if abs(conc_diff) < percentiles['abs_dC_p75']:
            rules.append('aftermath_stable')
            confidence = 0.85 if cq_slope_positive else 0.80
            if cq_slope_positive:
                rules.append('positive_cq_slope_confirms')
            return 'F', confidence, rules

    # Extended aftermath: steep decline 2 segments ago
    if prev2_steep and q_at_peak:
        rules.extend(['prev2_steep_decline', 'q_at_peak'])
        confidence = 0.75 if cq_slope_positive else 0.70
        if cq_slope_positive:
            rules.append('positive_cq_slope')
        return 'F', confidence, rules

    # Very large (extreme) decline with any Q elevation
    if conc_diff < percentiles['dC_p01']:
        rules.append('extreme_decline')
        # Prioritize C-Q slope evidence
        if cq_slope_positive:
            rules.append('positive_cq_slope_strong')
            return 'F', 0.92, rules
        elif flow_diff > 0 or q_pos in ['high', 'medium']:
            rules.append('q_elevated')
            return 'F', 0.88, rules

    # ==================================================================================
    # PRIORITY 2: LOADING
    # Criteria: C rising to max + Negative C-Q slope (enrichment signature)
    # ==================================================================================

    c_high_rising = c_pos == 'high' and conc_diff > 0
    q_not_peaked = flow_phase not in ['at_peak', 'early_decline']

    # C-Q slope checks for loading (negative = enrichment)
    cq_slope_negative = not np.isnan(cq_slope) and cq_slope < -0.15

    if c_high_rising:
        rules.extend(['c_high', 'c_rising'])
        
        # Negative C-Q slope confirms enrichment/mobilization
        if cq_slope_negative:
            rules.append('negative_cq_slope_enrichment')
            if q_not_peaked:
                rules.append('q_not_peaked')
                confidence = 0.95
            else:
                confidence = 0.92
        else:
            # Without C-Q slope confirmation
            if q_not_peaked:
                rules.append('q_not_peaked')
                confidence = 0.90
            else:
                confidence = 0.80
                
        # WAI during dry conditions boosts loading confidence
        if not np.isnan(wai) and wai < -1.0:
            rules.append('low_wai_accumulation')
            confidence = min(0.98, confidence + 0.03)
            
        return 'L', confidence, rules

    # Large concentration increase
    if conc_diff > percentiles['dC_p90']:
        rules.append('large_c_increase')
        if flow_diff <= percentiles['dQ_p75']:
            rules.append('q_stable')
            confidence = 0.90 if cq_slope_negative else 0.85
            if cq_slope_negative:
                rules.append('negative_cq_slope_confirms')
            return 'L', confidence, rules
        
    # ==================================================================================
    # PRIORITY 3: CHEMOSTATIC
    # Criteria: Low HI + Stable + Flat C-Q slope (buffered system)
    # ==================================================================================

    in_post_flush = (prev_conc_diff < percentiles['dC_p25']) or \
                    (row.get('prev2_conc_diff', 0) < percentiles['dC_p08'])
    post_peak = flow_phase in ['post_peak', 'late_decline'] or \
                (not np.isnan(days_since_peak) and days_since_peak > 5 and days_since_peak < 30)

    # Check C-Q slope is near-zero (chemostatic signature)
    cq_slope_flat = np.isnan(cq_slope) or abs(cq_slope) < 0.1

    if abs(hi) < 0.12 and hi_transition == 'stable':
        rules.extend(['low_hi', 'stable_hi'])
        
        # Flat C-Q slope confirms chemostatic behavior
        if cq_slope_flat:
            rules.append('flat_cq_slope_chemostatic')
            
        if not (c_high_rising or (q_high and abs(conc_diff) > percentiles['abs_dC_p75'])):
            # Exclude post-flush recovery (that's Dilution, not Chemostatic)
            if not (in_post_flush and post_peak):
                rules.append('not_dynamic')
                # Higher confidence with flat C-Q slope
                confidence = 0.90 if cq_slope_flat else 0.85
                return 'C', confidence, rules

    # ==================================================================================
    # PRIORITY 4: DILUTION
    # Criteria: Post-flush recovery, Q declining, C stabilizing
    # ==================================================================================

    post_peak_phase = flow_phase in ['post_peak', 'late_decline', 'stable'] or \
                      (not np.isnan(days_since_peak) and days_since_peak > 5)
    q_declining_moderate = flow_diff < 0
    c_stable_or_recovering = abs(conc_diff) < percentiles['abs_dC_p75']
    prev_c_declining = prev_conc_diff < percentiles['dC_p25']
    prev2_c_declining = row.get('prev2_conc_diff', 0) < percentiles['dC_p08']
    c_depleted = c_pos in ['low', 'medium']

    # Post-flush recovery: Q declining, C stabilizing after recent flush
    if post_peak_phase and q_declining_moderate and c_stable_or_recovering:
        if prev_c_declining or prev2_c_declining:
            rules.extend(['post_peak', 'q_declining', 'c_stable', 'recent_flush'])
            if c_depleted:
                rules.append('c_depleted')
                return 'D', 0.85, rules
            return 'D', 0.75, rules

    # Alternative: Large Q drop with small C change post-peak
    if post_peak_phase and flow_diff < percentiles['dQ_p10'] and abs(conc_diff) < percentiles['abs_dC_p75']:
        rules.extend(['post_peak', 'large_q_drop', 'c_not_changing'])
        if prev_c_declining or prev2_c_declining:
            rules.append('recent_flush')
            return 'D', 0.80, rules

    # ==================================================================================
    # PRIORITY 5: RECESSION
    # Criteria: Late cycle, low CVc/CVq, both declining
    # ==================================================================================

    late_cycle = flow_phase in ['low', 'late_decline'] or q_level == 'low'
    both_declining = flow_diff < percentiles['dQ_p25'] and conc_diff < percentiles['dC_p25']

    if not np.isnan(cvc_cvq) and cvc_cvq < 0.8:
        rules.append('low_cvc_cvq')
        if flow_diff < percentiles['dQ_p25']:
            rules.append('q_declining')
            if late_cycle:
                rules.append('late_cycle')
                return 'R', 0.85, rules
            return 'R', 0.75, rules

    if both_declining and late_cycle:
        rules.extend(['both_declining', 'late_cycle'])
        return 'R', 0.70, rules

    # ==================================================================================
    # FALLBACK: VARIABLE
    # ==================================================================================

    rules.append('fallback_variable')

    if abs(conc_diff) < 30 and abs(flow_diff) < 30:
        conf = 0.60
    else:
        conf = 0.40

    return 'V', conf, rules


def classify_geochemical_phase(
    data: pd.DataFrame,
    sites: List[str],
    flow_highres: Optional[pd.DataFrame] = None,
    qcol: str = 'Q_mLs',
    ccol: str = 'PLI',
    water_avail_col: Optional[str] = 'scPDSI',
    window: int = 5,
    use_highres: bool = True,
    headex: float = 0.4,
    tailex: float = 0.2
) -> pd.DataFrame:
    """
    Classify geochemical phases using percentile-based thresholds and high-resolution Q data.

    This function integrates hysteresis analysis, CVc/CVq ratios, C-Q slopes, and
    high-resolution flow dynamics to classify segments into 6 geochemical phases:
    - Flushing (F): Rapid mobilization during high flow
    - Loading (L): Accumulation phase
    - Chemostatic (C): Stable, low-variability behavior
    - Dilution (D): Post-flush recovery
    - Recession (R): Late-cycle decline
    - Variable (V): Mixed/ambiguous behavior

    data :: pd.DataFrame Time series data with columns:: site_id, date, [qcol], [ccol]
    sites :: list of str Site IDs to analyze
    flow_highres :: pd.DataFrame, optional High-resolution (hourly) flow data with 'time' column and site columns
    qcol :: str Flow/discharge column name
    ccol :: str Concentration column name
    water_avail_col :: str, optional Water availability index column (e.g., scPDSI)
    window :: int Window size for CVc/CVq calculation
    use_highres :: bool Whether to use high-resolution flow dynamics (requires flow_highres)
    headex/tailex :: float Percentage of segment length extending segment before/after for window hysteresis

    Returns :: pd.DataFrame Classification results with columns:
        - Segment metadata (dates, flows, concentrations)
        - Behavior classification
        - C-Q slopes
        - CVc, CVq, CVc_CVq: Variability metrics
        - Window-scale hysteresis (window_HI_*)
        - geochemical_phase: 'F', 'L', 'C', 'D', 'R', 'V'
        - phase_confidence: 0.0-1.0
        - rules_triggered: Diagnostic information
        - highres_*: High-resolution flow metrics (if use_highres=True)
    """

    # Legacy compatibility of site naming
    SITE_MAPPING = {
        'B3': 'Site 3B',
        'B4': 'Site 3A',
        'A12': 'Site 2',
        'C4': 'Site 1'
    }

    print("[1/6] Building segment-wise data...")
    # analyze_segments only creates segment metadata (NO event-scale hysteresis)
    segments_df = _build_segments(data, sites, ccol, qcol)
    print(f"  Generated {len(segments_df)} segments")

    print("[2/6] Computing CVc/CVq and C-Q slopes...")
    cvc_cvq_df = compute_cvc_cvq_windows(data, qcol=qcol, ccol=ccol, window=window)

    print("[3/6] Merging data...")
    # Note renamed column cq_slope_loglog
    merged_df = pd.merge(
        segments_df,
        cvc_cvq_df[['site_id', 'end_date', 'CVc', 'CVq', 'CVc_CVq', 'cq_slope_loglog']],
        on=['site_id', 'end_date'],
        how='left'
    )

    # Handle duplicate cq_slope_loglog column from merge
    if 'cq_slope_loglog_x' in merged_df.columns and 'cq_slope_loglog_y' in merged_df.columns:
        # Prefer segment-based calculation (_x), fallback to window calculation (_y)
        merged_df['cq_slope_loglog'] = merged_df['cq_slope_loglog_x'].fillna(merged_df['cq_slope_loglog_y'])
        merged_df = merged_df.drop(columns=['cq_slope_loglog_x', 'cq_slope_loglog_y'])

    # Add WAI
    if water_avail_col and water_avail_col in data.columns:
        wai_map = data.set_index('date')[water_avail_col].to_dict()
        merged_df['WAI'] = merged_df['end_date'].map(wai_map)

    # Global percentiles for absolute Q and C levels
    q_quantiles = data[qcol].quantile([0.25, 0.50, 0.75])
    c_quantiles = data[ccol].quantile([0.25, 0.50, 0.75])

    percentiles = {
        'Q_p25': q_quantiles[0.25],
        'Q_p50': q_quantiles[0.50],
        'Q_p75': q_quantiles[0.75],
        'C_p25': c_quantiles[0.25],
        'C_p50': c_quantiles[0.50],
        'C_p75': c_quantiles[0.75]
    }

    # Calculate percentiles for CHANGES (ΔC and ΔQ)
    print("  Computing change distributions...")
    change_percentiles = compute_change_percentiles(data, sites, ccol, qcol)
    percentiles.update(change_percentiles)

    print(f"  ΔC thresholds: steep decline < {percentiles['dC_p08']:.1f} (p08), large increase > {percentiles['dC_p90']:.1f} (p90)")
    print(f"  ΔQ thresholds: moderate decline < {percentiles['dQ_p25']:.1f} (p25), increase > {percentiles['dQ_p75']:.1f} (p75)")

    merged_df['Q_position'] = merged_df['end_flow'].apply(
        lambda x: 'low' if x < percentiles['Q_p25'] else ('high' if x > percentiles['Q_p75'] else 'medium')
    )
    merged_df['C_position'] = merged_df['end_conc'].apply(
        lambda x: 'low' if x < percentiles['C_p25'] else ('high' if x > percentiles['C_p75'] else 'medium')
    )

    # High-resolution flow analysis (if enabled)
    if use_highres and flow_highres is not None:
        print("[4/6] Analyzing high-resolution Q dynamics and window hysteresis...")
        flow_highres['time'] = pd.to_datetime(flow_highres['time'])
        
        results = []
        for site in sites:
            site_df = merged_df[merged_df['site_id'] == site].sort_values('end_date').reset_index(drop=True)

            # High-res subset
            try:
                hres_dummy = flow_highres[site]
                qxcol = site
            except:
                hres_dummy = flow_highres[SITE_MAPPING[site]]
                qxcol = SITE_MAPPING[site]
                
            cdummy = data.loc[(data.site_id == site), ccol]
            cdummy.index = data.loc[(data.site_id == site), 'date']
            site_dyn = pd.concat([hres_dummy, cdummy], axis=1).interpolate(
                method='spline', order=2, limit=None, limit_direction='forward'
            ).dropna()

            if len(site_df) == 0:
                continue

            for i in range(len(site_df)):
                row = site_df.iloc[i].copy()

                # Define window for hysteresis calculation
                t_extent = pd.Timedelta(row['end_date'] - row['start_date']).days
                segment_start = pd.to_datetime(row['start_date']) - pd.Timedelta(days=int(t_extent * headex))
                segment_end = pd.to_datetime(row['end_date']) + pd.Timedelta(days=int(t_extent * tailex))

                try:
                    # Window-scale hysteresis calculated here
                    flow_dynamics = analyze_segment_flow_dynamics(
                        site_dyn.loc[segment_start:segment_end],
                        percentiles, ccol, qxcol
                    )
                except:
                    flow_dynamics = False

                if flow_dynamics:
                    for key, val in flow_dynamics.items():
                        row[f'highres_{key}'] = val
                else:
                    row['highres_flow_phase'] = 'unknown'
                    row['highres_days_since_peak'] = np.nan

                # Extended temporal context
                if i > 0:
                    prev = site_df.iloc[i - 1]
                    row['prev_behavior'] = prev['behavior']
                    row['prev_CVc_CVq'] = prev.get('CVc_CVq', np.nan)
                    row['prev_Q_position'] = prev['Q_position']
                    row['prev_C_position'] = prev['C_position']
                    row['prev_conc_diff'] = prev['conc_diff']
                    row['prev_flow_diff'] = prev['flow_diff']

                    # Simplified HI transition tracking
                    if flow_dynamics:
                        current_hi = flow_dynamics.get('window_HI_zuecco', np.nan)
                        prev_hi = prev.get('window_HI_zuecco', np.nan)
                        
                        if not np.isnan(prev_hi) and not np.isnan(current_hi):
                            if prev_hi > 0.01 and current_hi < -0.01:
                                row['HI_transition'] = 'pos_to_neg'
                            elif prev_hi < -0.01 and current_hi > 0.01:
                                row['HI_transition'] = 'neg_to_pos'
                            else:
                                row['HI_transition'] = 'stable'
                        else:
                            row['HI_transition'] = 'stable'
                    else:
                        row['HI_transition'] = 'stable'
                        
                    # Store current window HI values for next iteration
                    if flow_dynamics:
                        row['window_HI_zuecco'] = flow_dynamics.get('window_HI_zuecco', np.nan)
                        row['window_HI_lloyd'] = flow_dynamics.get('window_HI_lloyd', np.nan)
                        row['window_HI_harp'] = flow_dynamics.get('window_HI_harp', np.nan)

                else:
                    # First segment
                    row['prev_behavior'] = 'none'
                    row['prev_CVc_CVq'] = np.nan
                    row['prev_Q_position'] = 'none'
                    row['prev_C_position'] = 'none'
                    row['prev_conc_diff'] = 0
                    row['prev_flow_diff'] = 0
                    row['HI_transition'] = 'first'
                    
                    if flow_dynamics:
                        row['window_HI_zuecco'] = flow_dynamics.get('window_HI_zuecco', np.nan)
                        row['window_HI_lloyd'] = flow_dynamics.get('window_HI_lloyd', np.nan)
                        row['window_HI_harp'] = flow_dynamics.get('window_HI_harp', np.nan)

                # Two segments back
                if i > 1:
                    prev2 = site_df.iloc[i - 2]
                    row['prev2_conc_diff'] = prev2['conc_diff']
                    row['prev2_C_position'] = prev2['C_position']
                else:
                    row['prev2_conc_diff'] = 0
                    row['prev2_C_position'] = 'none'

                # Next segment
                if i < len(site_df) - 1:
                    next_seg = site_df.iloc[i + 1]
                    row['next_C_position'] = next_seg['C_position']
                else:
                    row['next_C_position'] = 'none'

                # C trajectory - using percentile-based thresholds
                conc_diff = row['conc_diff']
                c_pos = row['C_position']
                prev_c_pos = row.get('prev_C_position', 'none')

                if conc_diff < percentiles['dC_p08']:
                    if prev_c_pos == 'high':
                        row['C_trajectory'] = 'steep_decline_from_high'
                    else:
                        row['C_trajectory'] = 'steep_decline'
                elif conc_diff < percentiles['dC_p25']:
                    row['C_trajectory'] = 'gradual_decline'
                elif conc_diff > percentiles['dC_p90']:
                    row['C_trajectory'] = 'rising_to_max' if c_pos == 'high' else 'large_increase'
                elif conc_diff > percentiles['dC_p75']:
                    row['C_trajectory'] = 'moderate_increase'
                elif c_pos == 'high' and abs(conc_diff) < percentiles['abs_dC_p50']:
                    row['C_trajectory'] = 'at_maximum'
                else:
                    row['C_trajectory'] = 'stable'

                results.append(row)

        temporal_df = pd.DataFrame(results)
    else:
        print("[4/6] Skipping high-resolution Q analysis (use_highres=False or no data)")
        temporal_df = merged_df.copy()

        # Add minimal temporal context without highres
        for site in sites:
            site_mask = temporal_df['site_id'] == site
            site_df = temporal_df[site_mask].sort_values('end_date').reset_index(drop=True)

            for i in range(len(site_df)):
                idx = site_df.index[i]

                if i > 0:
                    prev_idx = site_df.index[i - 1]
                    temporal_df.loc[idx, 'prev_conc_diff'] = temporal_df.loc[prev_idx, 'conc_diff']
                    temporal_df.loc[idx, 'prev_C_position'] = temporal_df.loc[prev_idx, 'C_position']
                else:
                    temporal_df.loc[idx, 'prev_conc_diff'] = 0
                    temporal_df.loc[idx, 'prev_C_position'] = 'none'

                if i > 1:
                    prev2_idx = site_df.index[i - 2]
                    temporal_df.loc[idx, 'prev2_conc_diff'] = temporal_df.loc[prev2_idx, 'conc_diff']
                else:
                    temporal_df.loc[idx, 'prev2_conc_diff'] = 0

                # Set defaults for highres columns
                temporal_df.loc[idx, 'highres_flow_phase'] = 'unknown'
                temporal_df.loc[idx, 'highres_days_since_peak'] = np.nan
                temporal_df.loc[idx, 'HI_transition'] = 'stable'

    print("[5/6] Classifying with percentile-based logic + C-Q slopes...")

    phases = []
    confidences = []
    rules_list = []

    for idx, row in temporal_df.iterrows():
        # classify_segment_phase no longer needs hi_method parameter
        phase, conf, rules = classify_segment_phase(row, percentiles)
        phases.append(phase)
        confidences.append(conf)
        rules_list.append('|'.join(rules))

    temporal_df['geochemical_phase'] = phases
    temporal_df['phase_confidence'] = confidences
    temporal_df['rules_triggered'] = rules_list

    print(f"\n[6/6] Complete!")
    print(f"\nPhase distribution:")
    for phase, count in temporal_df['geochemical_phase'].value_counts().items():
        pct = count / len(temporal_df) * 100
        print(f"  {phase}: {count} ({pct:.1f}%)")

    return temporal_df


# =============================================================================
# SIMPLE C-Q BEHAVIOR CLASSIFIER (Williams 1989 / Evans & Davies 1998)
# =============================================================================

def classify_cq_behavior_simple(
    flow_diff: float,
    conc_diff: float,
    flow_range: Tuple[float, float],
    conc_range: Tuple[float, float],
    threshold_factor: float = 0.01
) -> str:
    """
    Simple C-Q behavior classifier based on segment changes.

    Based on Williams (1989) and Evans & Davies (1998).
    This is a simpler classification than the main GCS phase classifier above.

    Parameters
    ----------
    flow_diff : float
        Change in flow between points
    conc_diff : float
        Change in concentration between points
    flow_range : tuple
        (min, max) flow values for significance testing
    conc_range : tuple
        (min, max) concentration values for significance testing
    threshold_factor : float
        Relative threshold for significant change

    Returns
    -------
    str
        Behavior classification:
        - 'connectivity': Q↑ C↑ (mobilization)
        - 'dispersion': Q↑ C↓ (dilution dominates)
        - 'accumulation': Q↓ C↑ (evaporation/point sources)
        - 'recovery': Q↓ C↓ (system recovery)
        - 'quasi-chemostatic': Q changes, C stable
        - 'source variation': C changes, Q stable
        - 'static': No significant changes
    """

    flow_delta = flow_range[1] - flow_range[0]
    conc_delta = conc_range[1] - conc_range[0]

    # Determine if changes are significant
    is_flow_changing = abs(flow_diff) > (threshold_factor * flow_delta) if flow_delta > 1e-10 else False
    is_conc_changing = abs(conc_diff) > (threshold_factor * conc_delta) if conc_delta > 1e-10 else False

    if not is_flow_changing and not is_conc_changing:
        return 'static'
    elif is_flow_changing and not is_conc_changing:
        return 'quasi-chemostatic'
    elif not is_flow_changing and is_conc_changing:
        return 'source variation'
    else:
        # Both changing - determine relationship
        if flow_diff > 0 and conc_diff > 0:
            return 'connectivity'
        elif flow_diff < 0 and conc_diff < 0:
            return 'recovery'
        elif flow_diff > 0 and conc_diff < 0:
            return 'dispersion'
        else:
            return 'accumulation'


# =============================================================================
# PRIVATE HELPERS
# =============================================================================

def _build_segments(
    data: pd.DataFrame,
    sites: List[str],
    ccol: str,
    qcol: str
) -> pd.DataFrame:
    """
    V5 NEW FUNCTION: Build segment-wise data WITHOUT event-scale hysteresis.

    Replaces the incorrect analyze_hysteresis approach that duplicated 
    event-scale metrics across all segments.

    Returns segment metadata only:
    - Dates, flows, concentrations
    - Changes (ΔQ, ΔC)
    - Behavior classification
    - C-Q slopes

    NO hysteresis metrics here - those are calculated at window-scale
    in the high-res analysis.
    """
    analysis_data = data[data['site_id'].isin(sites)].copy()
    analysis_data = analysis_data.dropna(subset=[qcol, ccol, 'date'])

    if len(analysis_data) < 2:
        return pd.DataFrame()

    analysis_data = analysis_data.sort_values(['site_id', 'date'])

    # Calculate compound-specific ranges for behavior classification
    flow_range = (analysis_data[qcol].min(), analysis_data[qcol].max())
    conc_range = (analysis_data[ccol].min(), analysis_data[ccol].max())

    results = []

    for site in sites:
        site_data = analysis_data[analysis_data['site_id'] == site].reset_index(drop=True)

        if len(site_data) < 2:
            continue

        # Analyze segments (point-to-point)
        for i in range(len(site_data) - 1):
            p1, p2 = site_data.iloc[i], site_data.iloc[i + 1]

            # Calculate changes
            flow_diff = p2[qcol] - p1[qcol]
            conc_diff = p2[ccol] - p1[ccol]

            # Classify behavior (using simple Williams 1989 classifier)
            behavior = classify_cq_behavior_simple(flow_diff, conc_diff, flow_range, conc_range)

            # Build result - ONLY segment metadata
            result = {
                'site_id': site,
                'compound': ccol,
                'segment_id': i,
                'start_date': p1['date'],
                'end_date': p2['date'],
                'start_flow': p1[qcol],
                'end_flow': p2[qcol],
                'start_conc': p1[ccol],
                'end_conc': p2[ccol],
                'flow_diff': flow_diff,
                'conc_diff': conc_diff,
                'behavior': behavior,
                'cq_slope_loglog': compute_cq_slope(p1[qcol], p2[qcol], p1[ccol], p2[ccol], kind="loglog"),
                'cq_slope_linear': compute_cq_slope(p1[qcol], p2[qcol], p1[ccol], p2[ccol], kind="linear")
            }

            # Add HydPhase if available
            if 'HydPhase' in site_data.columns:
                result['start_hyphase'] = p1.get('HydPhase', 'unknown')
                result['end_hyphase'] = p2.get('HydPhase', 'unknown')

            results.append(result)

    return pd.DataFrame(results)


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    'classify_segment_phase',
    'classify_geochemical_phase',
    'classify_cq_behavior_simple'
]

print("gcs_classification.py: geochemical phase classification loaded")
