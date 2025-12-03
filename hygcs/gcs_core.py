"""
GCS Core Analysis Functions
============================
Core functions for C-Q analysis including hysteresis metrics,
CVc/CVq ratios, C-Q slope calculations, and preparatory statistics.

(cc-by) Version 0.5 (2025-12-02) conrad.jackisch@tbt.tu-freiberg.de, antita.sanchez@mineral.tu-freiberg.de
"""

import pandas as pd
import numpy as np
import plotly.express as px
from typing import Tuple, Dict, List, Optional
import warnings

# Import individual hysteresis analysis modules
from harp import calculate_harp_metrics
from zuecco import calculate_zuecco_metrics
from lloyd import calculate_lawlerlloyd_metrics


# =============================================================================
# HYSTERESIS METRICS
# =============================================================================

def calculate_all_hysteresis_metrics(
    df: pd.DataFrame,
    time_col: str = 'date',
    discharge_col: str = 'Q',
    concentration_col: str = 'C'
) -> Dict[str, any]:
    """
    Calculate hysteresis metrics using all three methods (HARP, Zuecco, Lloyd).

    This function applies scientifically validated hysteresis analysis methods
    to time series data (typically a moving window around each segment).

    Parameters
    ----------
    df : pd.DataFrame
        Time series data containing discharge and concentration (length >= 5 recommended)
    time_col : str
        Column name for time values
    discharge_col : str
        Column name for discharge/flow values
    concentration_col : str
        Column name for concentration values

    Returns
    -------
    dict
        Dictionary containing:
        - harp_metrics: dict from calculate_harp_metrics()
        - zuecco_metrics: dict from calculate_zuecco_metrics()
        - lloyd_metrics: dict from calculate_lawlerlloyd_metrics()
        - classifications: dict with hysteresis direction classifications
        - processed_data: dict with processed DataFrames from each method
        - error: str if calculation failed
    """

    if len(df) < 3:
        return {
            'harp_metrics': {},
            'zuecco_metrics': {},
            'lloyd_metrics': {},
            'classifications': {},
            'processed_data': {},
            'error': 'Insufficient data points (need >= 3)'
        }

    try:
        # Calculate HARP metrics
        harp_metrics, harp_df = calculate_harp_metrics(
            df, time_col=time_col, discharge_col=discharge_col, concentration_col=concentration_col
        )

        # Calculate Zuecco metrics
        zuecco_metrics, zuecco_df = calculate_zuecco_metrics(
            df, time_col=time_col, discharge_col=discharge_col, concentration_col=concentration_col
        )

        # Calculate Lloyd metrics
        lloyd_metrics, lloyd_df = calculate_lawlerlloyd_metrics(
            df, time_col=time_col, discharge_col=discharge_col, concentration_col=concentration_col
        )

        # Create classifications based on each method
        classifications = {}

        # HARP classification (if available)
        if 'hyst_class' in harp_metrics.columns:
            classifications['harp_class'] = harp_metrics['hyst_class'].values[0]

        # Zuecco classification
        if 'hyst_class' in zuecco_metrics.columns:
            classifications['zuecco_class'] = int(zuecco_metrics['hyst_class'].values[0])

        # Lloyd classification (based on HInew recommended method)
        if 'mean_HInew' in lloyd_metrics.columns:
            mean_hinew = lloyd_metrics['mean_HInew'].values[0]
            if not np.isnan(mean_hinew):
                if mean_hinew > 0.1:
                    classifications['lloyd_direction'] = 'clockwise'
                elif mean_hinew < -0.1:
                    classifications['lloyd_direction'] = 'counter-clockwise'
                else:
                    classifications['lloyd_direction'] = 'weak'
            else:
                classifications['lloyd_direction'] = 'unknown'

        # Also classify Lawler method for comparison
        if 'mean_HIL' in lloyd_metrics.columns:
            mean_hil = lloyd_metrics['mean_HIL'].values[0]
            if not np.isnan(mean_hil):
                if mean_hil > 0.1:
                    classifications['lawler_direction'] = 'clockwise'
                elif mean_hil < -0.1:
                    classifications['lawler_direction'] = 'counter-clockwise'
                else:
                    classifications['lawler_direction'] = 'weak'
            else:
                classifications['lawler_direction'] = 'unknown'

        return {
            'harp_metrics': harp_metrics.to_dict('records')[0] if len(harp_metrics) > 0 else {},
            'zuecco_metrics': zuecco_metrics.to_dict('records')[0] if len(zuecco_metrics) > 0 else {},
            'lloyd_metrics': lloyd_metrics.to_dict('records')[0] if len(lloyd_metrics) > 0 else {},
            'classifications': classifications,
            'processed_data': {
                'harp': harp_df,
                'zuecco': zuecco_df,
                'lloyd': lloyd_df
            }
        }

    except Exception as e:
        return {
            'harp_metrics': {},
            'zuecco_metrics': {},
            'lloyd_metrics': {},
            'classifications': {},
            'processed_data': {},
            'error': f'Calculation failed: {str(e)}'
        }


# =============================================================================
# CVc/CVq AND C-Q SLOPE ANALYSIS
# =============================================================================

def compute_cvc_cvq_windows(df, qcol="Q_mLs", ccol="Zn_mgL", window=5):
    """
    Compute CVc/CVq ratios and C-Q slopes over rolling windows.

    Based on Musolff et al. (2015) for chemostatic vs chemodynamic behavior detection.
    https://doi.org/10.1016/j.advwatres.2015.09.026

    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with time series of concentration and flow measurements
    qcol : str
        Name of the flow column
    ccol : str
        Name of the concentration column
    window : int
        Number of measurements to use for rolling window analysis

    Returns
    -------
    pd.DataFrame
        DataFrame with CVc/CVq analysis for each window, including:
        - CVc, CVq: Coefficients of variation
        - CVc_CVq: Ratio (>1 = chemodynamic, <1 = chemostatic)
        - cq_slope_loglog: C-Q slope in log-log space (power-law exponent b)
    """
    df_sorted = df.sort_values(["site_id", "date"]).copy()
    rows = []
    for site, g in df_sorted.groupby("site_id"):
        g = g.reset_index(drop=True)
        for i in range(window - 1, len(g)):
            block = g.iloc[i - window + 1 : i + 1]

            mu_q = block[qcol].mean()
            sd_q = block[qcol].std(ddof=1)
            mu_c = block[ccol].mean()
            sd_c = block[ccol].std(ddof=1)

            CVq = sd_q / mu_q if mu_q != 0 else np.nan
            CVc = sd_c / mu_c if mu_c != 0 else np.nan
            ratio = CVc / CVq if (CVq not in [0, np.nan]) else np.nan

            # Calculate C-Q slope using log-log regression
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=RuntimeWarning)
                try:
                    figkx = px.scatter(y=np.log(block[ccol]), x=np.log(block[qcol]), trendline='ols', template='none')
                    results = px.get_trendline_results(figkx)
                    slope = results.loc[0].px_fit_results.params[1]
                except:
                    slope = np.nan

            rows.append({
                "site_id": site,
                "compound": ccol,
                "window_id": i - window + 1,
                "start_date": block["date"].min(),
                "end_date": block["date"].max(),
                "n_samples": len(block),
                "CVq": CVq,
                "CVc": CVc,
                "CVc_CVq": ratio,
                "cq_slope_loglog": slope
            })

    return pd.DataFrame(rows)


def compute_cq_slope(q1: float, q2: float, c1: float, c2: float, kind: str = 'loglog') -> float:
    """
    Compute the local C-Q slope for a segment between two consecutive points.

    Parameters
    ----------
    q1, q2 : float
        Discharge values at segment start and end.
    c1, c2 : float
        Concentration values at segment start and end.
    kind : {'loglog','linear'}, optional
        - 'loglog' returns Δlog(C) / Δlog(Q) (i.e., power-law slope b)
        - 'linear' returns ΔC / ΔQ

    Returns
    -------
    float
        The requested slope, or NaN if undefined.
    """
    if kind == 'linear':
        dq = q2 - q1
        if abs(dq) < 1e-12:
            return np.nan
        return (c2 - c1) / dq

    # default: log-log slope
    # guard against non-positive values (log undefined)
    if q1 <= 0 or q2 <= 0 or c1 <= 0 or c2 <= 0:
        return np.nan

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=RuntimeWarning)
        dlog10q = np.log10(q2) - np.log10(q1)
        if abs(dlog10q) < 1e-12:
            return np.nan
        dlog10c = np.log10(c2) - np.log10(c1)
        return dlog10c / dlog10q


# =============================================================================
# SEGMENT FLOW DYNAMICS ANALYSIS
# =============================================================================

def analyze_segment_flow_dynamics(
    segment_data: pd.DataFrame,
    percentiles: Dict,
    ccol: Optional[str] = None,
    qcol: Optional[str] = None
) -> Dict:
    """
    Analyze high-resolution Q dynamics within a segment, with window-scale hysteresis analysis.

    Integrates hourly discharge data to capture within-segment flow dynamics
    that may not be apparent from sampling-point averages. Calculates hysteresis
    metrics on the time window (not event-scale or point-to-point).

    Parameters
    ----------
    segment_data : pd.DataFrame
        High-resolution time series for the segment window
    percentiles : dict
        Global percentile thresholds for Q levels
    ccol : str, optional
        Name of concentration column
    qcol : str, optional
        Name of flow column

    Returns
    -------
    dict or None
        Dictionary containing:
        - peak_q: Maximum Q in segment
        - peak_time: When peak occurred
        - days_since_peak: Days from peak to segment end
        - days_to_peak: Days from segment start to peak
        - flow_phase: 'rising' | 'at_peak' | 'early_decline' | 'late_decline' | 'low'
        - peak_position: 'early' | 'middle' | 'late' in segment
        - q_trend: slope of Q over segment
        - q_acceleration: change in Q rate
        - q_level: 'low' | 'medium' | 'high'
        - q_range: Q variability within segment
        - window_HI_* : Window-scale hysteresis metrics (if ccol provided)
        Returns None if no data available
    """

    # Extract segment data
    if qcol is None:
        qcol = segment_data.columns[0]
        ccol = segment_data.columns[1]

    if len(segment_data) == 0 or segment_data[qcol].isna().all():
        return None

    segment_data = segment_data.dropna()

    if len(segment_data) < 2:
        return None

    q_values = segment_data[qcol].values
    c_values = segment_data[ccol].values if ccol else None
    times = segment_data.index.values

    # Find peak
    peak_idx = np.argmax(q_values)
    peak_q = q_values[peak_idx]
    peak_time_idx = segment_data.index[peak_idx]
    peak_time = times[peak_idx]

    # Calculate temporal position of peak
    segment_duration = pd.Timedelta(times[-1] - times[0]).total_seconds() / 86400  # days
    days_to_peak = pd.Timedelta(peak_time - times[0]).total_seconds() / 86400
    days_since_peak = pd.Timedelta(times[-1] - peak_time).total_seconds() / 86400

    if segment_duration > 0:
        peak_position_frac = days_to_peak / segment_duration
        if peak_position_frac < 0.33:
            peak_position = 'early'
        elif peak_position_frac > 0.67:
            peak_position = 'late'
        else:
            peak_position = 'middle'
    else:
        peak_position = 'middle'

    # Determine flow phase based on peak location and current position
    end_q = q_values[-1]
    start_q = q_values[0]

    # Compare end_q to percentiles
    if end_q > percentiles['Q_p75']:
        q_level = 'high'
    elif end_q < percentiles['Q_p25']:
        q_level = 'low'
    else:
        q_level = 'medium'

    # Flow phase logic
    if days_since_peak < 1:  # Peak within last day
        flow_phase = 'at_peak'
    elif days_since_peak < segment_duration * 0.3:  # Recent peak
        if end_q > percentiles['Q_p50']:
            flow_phase = 'early_decline'  # Declining but still high
        else:
            flow_phase = 'late_decline'
    elif days_to_peak < segment_duration * 0.3:  # Peak was early
        flow_phase = 'post_peak'
    elif peak_position == 'late' and end_q > start_q:
        flow_phase = 'rising'
    elif q_level == 'low':
        flow_phase = 'low'
    else:
        # Use trend
        if end_q > start_q * 1.1:
            flow_phase = 'rising'
        elif end_q < start_q * 0.9:
            if q_level == 'high':
                flow_phase = 'early_decline'
            else:
                flow_phase = 'late_decline'
        else:
            flow_phase = 'stable'

    # Calculate trend (linear fit)
    if len(q_values) > 2:
        x = np.arange(len(q_values))
        q_trend = np.polyfit(x, q_values, 1)[0]  # slope per hour
        q_trend_daily = q_trend * 24  # slope per day

        # Acceleration (change in trend)
        mid = len(q_values) // 2
        trend1 = np.polyfit(x[:mid], q_values[:mid], 1)[0] if mid > 1 else 0
        trend2 = np.polyfit(x[mid:], q_values[mid:], 1)[0] if len(x) - mid > 1 else 0
        q_acceleration = (trend2 - trend1) * 24  # per day
    else:
        q_trend_daily = (end_q - start_q) / max(1, segment_duration)
        q_acceleration = 0

    result = {
        'peak_q': peak_q,
        'peak_time': peak_time,
        'days_since_peak': days_since_peak,
        'days_to_peak': days_to_peak,
        'flow_phase': flow_phase,
        'peak_position': peak_position,
        'q_trend': q_trend_daily,
        'q_acceleration': q_acceleration,
        'q_level': q_level,
        'q_range': q_values.max() - q_values.min(),
        'start_q': start_q,
        'end_q': end_q
    }

    # Calculate HI on the time window (not event-scale)
    if ccol is not None and c_values is not None:
        segment_data_copy = segment_data.copy()
        segment_data_copy['date'] = segment_data_copy.index
        try:
            if len(segment_data_copy) >= 5:
                # Calculate WINDOW hysteresis metrics
                window_hyst = calculate_all_hysteresis_metrics(
                    segment_data_copy,
                    time_col='date',
                    discharge_col=qcol,
                    concentration_col=ccol
                )

                # Extract window-scale metrics
                harp_win = window_hyst.get('harp_metrics', {})
                zuecco_win = window_hyst.get('zuecco_metrics', {})
                lloyd_win = window_hyst.get('lloyd_metrics', {})
                class_win = window_hyst.get('classifications', {})

                # Store essential metrics
                result.update({
                    'window_HI_harp': harp_win.get('area', np.nan),
                    'window_HI_zuecco': zuecco_win.get('h_index', np.nan),
                    'window_HI_lloyd': lloyd_win.get('mean_HInew', np.nan),
                    'window_direction': class_win.get('lloyd_direction', 'unknown')
                })

        except Exception as e:
            # Silently skip if hysteresis calculation fails
            print(f'Window hysteresis analysis failed: {str(e)}')
            pass

    return result


# =============================================================================
# STATISTICAL THRESHOLDS
# =============================================================================

def compute_change_percentiles(
    data: pd.DataFrame,
    sites: List[str],
    ccol: str,
    qcol: str
) -> Dict[str, float]:
    """
    Calculate percentiles for concentration and flow changes (ΔC and ΔQ).

    These percentile-based thresholds make the classification compound-agnostic
    by adapting to the specific distribution of each compound's dynamics.

    Parameters
    ----------
    data : pd.DataFrame
        Time series data
    sites : list of str
        Sites to include
    ccol : str
        Concentration column
    qcol : str
        Flow column

    Returns
    -------
    dict
        Percentile thresholds for dC and dQ at various levels (p01, p05, p08, p10, p25, p50, p75, p90, p95)
    """

    changes = []
    for site in sites:
        site_data = data[data['site_id'] == site].sort_values('date')
        if len(site_data) > 1:
            conc_diffs = site_data[ccol].diff().dropna()
            flow_diffs = site_data[qcol].diff().dropna()
            changes.extend([
                {'conc_diff': cd, 'flow_diff': fd}
                for cd, fd in zip(conc_diffs, flow_diffs)
            ])

    changes_df = pd.DataFrame(changes)

    percentiles = {
        # Concentration change percentiles
        'dC_p01': changes_df['conc_diff'].quantile(0.01),
        'dC_p05': changes_df['conc_diff'].quantile(0.05),
        'dC_p08': changes_df['conc_diff'].quantile(0.08),  # Optimized for flushing detection
        'dC_p10': changes_df['conc_diff'].quantile(0.10),
        'dC_p25': changes_df['conc_diff'].quantile(0.25),
        'dC_p50': changes_df['conc_diff'].quantile(0.50),
        'dC_p75': changes_df['conc_diff'].quantile(0.75),
        'dC_p90': changes_df['conc_diff'].quantile(0.90),  # Large increase threshold
        'dC_p95': changes_df['conc_diff'].quantile(0.95),

        # Flow change percentiles
        'dQ_p05': changes_df['flow_diff'].quantile(0.05),
        'dQ_p10': changes_df['flow_diff'].quantile(0.10),
        'dQ_p25': changes_df['flow_diff'].quantile(0.25),
        'dQ_p50': changes_df['flow_diff'].quantile(0.50),
        'dQ_p75': changes_df['flow_diff'].quantile(0.75),
        'dQ_p90': changes_df['flow_diff'].quantile(0.90),

        # Absolute change percentiles (for stability detection)
        'abs_dC_p50': changes_df['conc_diff'].abs().quantile(0.50),
        'abs_dC_p75': changes_df['conc_diff'].abs().quantile(0.75),
        'abs_dQ_p50': changes_df['flow_diff'].abs().quantile(0.50),
        'abs_dQ_p75': changes_df['flow_diff'].abs().quantile(0.75),
    }

    return percentiles


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    'calculate_all_hysteresis_metrics',
    'compute_cvc_cvq_windows',
    'compute_cq_slope',
    'analyze_segment_flow_dynamics',
    'compute_change_percentiles'
]

print("gcs_core.py: core metrics and preparatory functions loaded")
