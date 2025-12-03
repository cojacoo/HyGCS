"""
HARP (Hysteresis Analysis of Residence time and Production) Metrics Calculator

Python translation of the original R code version 2.2 (July 2024)
by Melanie E. Roberts et al. https://github.com/MelanieEmmajade/HARP

Roberts, M.E. (2023). HARP Hysteresis Metrics - an R implementation (v1.0.0). 
    Zenodo. https://doi.org/10.5281/zenodo.8409091
Roberts, M.E., Kim, D., Lu, J. & Hamilton, D.P., HARP: A suite of parameters 
    to describe the hysteresis of streamflow and water quality constituents, 
    Journal of Hydrology, 2023, https://doi.org/10.1016/j.jhydrol.2023.130262

This module calculates hysteresis metrics from time series of discharge (Q)
and concentration (C) data for hydrochemical analysis.

(cc) conrad.jackisch@tbt.tu-freiberg.de
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from scipy.signal import find_peaks

# Optional intersection libraries
try:
    from shapely.geometry import LineString
    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False

try:
    import poly_point_isect as ppi
    HAS_PPI = True
except ImportError:
    HAS_PPI = False


def calculate_harp_metrics(df_obs, time_col='Etime', discharge_col='Q', concentration_col='C', intersection_method='auto'):
    """
    Calculate HARP metrics from discharge and concentration time series.

    Parameters
    ----------
    df_obs : pd.DataFrame
        Observed data with time, discharge, and concentration columns
    time_col, discharge_col, concentration_col : str
        Column names for time, discharge, and concentration
    intersection_method : str, default 'auto'
        'auto', 'shapely', 'bentley-ottmann', or 'simple'

    Returns
    -------
    metric_df : pd.DataFrame
        HARP metrics:
        - area: Total hysteresis area (magnitude) with sign of dominant portion
                Positive = diluting, Negative = enriching
        - residual: Change in scaled concentration (end - start)
                    Positive = enriching, Negative = diluting
        - area_lower/area_upper: Areas of lower/upper portions (if intersection found)
        - peak_Q/peak_C: Scaled peak timings (0-1)
        - peaktime_Q/peaktime_C: Absolute peak timings (days)
        - radius_equiv: Equivalent circle radius
    df_all : pd.DataFrame
        Processed data with scaled values and phase information
    """
    df_all = df_obs[[time_col, discharge_col, concentration_col]].copy()
    df_all.columns = ['Etime', 'Q', 'C']  # Rename to standard names

    # Prepare time index
    if pd.api.types.is_numeric_dtype(df_obs[time_col]):
        df_all.index = pd.to_timedelta(df_all['Etime'], unit='D')
    else:
        df_all.index = df_all['Etime'] - df_all['Etime'].iloc[0]

    # Resample and interpolate
    df_all = df_all.resample('1h').first().interpolate(method='linear', limit=None, limit_direction='forward')

    # Create numeric Etime from index for scaling
    df_all['Etime'] = df_all.index.total_seconds() / 86400.0  # Convert to days

    # Min-max scaling
    df_all[['EtimeS', 'QS', 'CS']] = MinMaxScaler().fit_transform(df_all[['Etime', 'Q', 'C']])

    # Find peaks and mark switchpoints
    df_all['switchpointsQ'] = ''
    df_all['switchpointsC'] = ''
    df_all.loc[df_all.index[find_peaks(df_all['Q'])[0]], 'switchpointsQ'] = 'lQ'
    df_all.loc[df_all.index[df_all['Q'].argmax()], 'switchpointsQ'] = 'gQ'
    df_all.loc[df_all.index[find_peaks(df_all['C'])[0]], 'switchpointsC'] = 'lC'
    df_all.loc[df_all.index[df_all['C'].argmax()], 'switchpointsC'] = 'gC'

    # Define phases based on discharge
    df_all['Qphase'] = 'rising'
    df_all.loc[df_all.index[df_all['Q'].argmax()]:, 'Qphase'] = 'falling'

    df_all['Cphase'] = 'rising'
    df_all.loc[df_all.index[df_all['C'].argmax()]:, 'Cphase'] = 'falling'

    # Create limbs using pandas approach (handle duplicates with groupby().mean())
    rising_limb = df_all.loc[df_all.Qphase == 'rising', ['QS', 'CS']].groupby('QS').mean()['CS']
    falling_limb = df_all.loc[df_all.Qphase == 'falling', ['QS', 'CS']].groupby('QS').mean()['CS']

    limbs = pd.concat([rising_limb, falling_limb], axis=1, sort=True).interpolate(method='linear')
    limbs.columns = [0, 1]  # Use integer column names for compatibility

    # Find intersection point
    xQS = _find_intersection(limbs, method=intersection_method)

    if xQS is not None:
        # Mark intersection
        xID = df_all.index[abs(df_all.QS - xQS).argmin()]
        df_all.loc[xID, 'switchpointsQ'] = 'X'
        df_all.loc[xID, 'switchpointsC'] = 'X'

        # Calculate areas for lower and upper portions (preserve signs)
        rising1 = df_all.loc[(df_all.QS <= xQS) & (df_all.Qphase == 'rising'), ['QS', 'CS']].groupby('QS').mean()['CS']
        falling1 = df_all.loc[(df_all.QS <= xQS) & (df_all.Qphase == 'falling'), ['QS', 'CS']].groupby('QS').mean()['CS']
        limbs1 = pd.concat([rising1, falling1], axis=1, sort=True).interpolate(method='linear')
        limbs1.columns = [0, 1]

        rising2 = df_all.loc[(df_all.QS > xQS) & (df_all.Qphase == 'rising'), ['QS', 'CS']].groupby('QS').mean()['CS']
        falling2 = df_all.loc[(df_all.QS > xQS) & (df_all.Qphase == 'falling'), ['QS', 'CS']].groupby('QS').mean()['CS']
        limbs2 = pd.concat([rising2, falling2], axis=1, sort=True).interpolate(method='linear')
        limbs2.columns = [0, 1]

        area1 = ((limbs1[0] - limbs1[1]) * limbs1.index.diff()).sum()
        area2 = ((limbs2[0] - limbs2[1]) * limbs2.index.diff()).sum()

        # Total area: magnitude sum with sign of larger portion
        total_area = abs(area1) + abs(area2)
        area_sign = np.sign(area1) if abs(area1) > abs(area2) else np.sign(area2)
        area = area_sign * total_area
    else:
        # No intersection found - calculate total area
        area = ((limbs[0] - limbs[1]) * limbs.index.diff()).sum()
        area1 = np.nan
        area2 = np.nan

    # Residual: change in concentration from start to finish
    residual = df_all['CS'].iloc[-1] - df_all['CS'].iloc[0]

    # Calculate equivalent circle radius
    radius = np.sqrt(abs(area) / np.pi)

    # Extract peak timing metrics
    peak_q_time = df_all.loc[df_all.switchpointsQ == 'gQ'].index[0]
    peak_c_time = df_all.loc[df_all.switchpointsC == 'gC'].index[0]

    metric_df = pd.DataFrame({
        'area': [area],
        'residual': [residual],
        'area_lower': [area1],
        'area_upper': [area2],
        'peak_Q': [df_all.loc[df_all.switchpointsQ == 'gQ', 'EtimeS'].values[0]],
        'peak_C': [df_all.loc[df_all.switchpointsC == 'gC', 'EtimeS'].values[0]],
        'peaktime_Q': [peak_q_time.days + peak_q_time.seconds / 86400.0],
        'peaktime_C': [peak_c_time.days + peak_c_time.seconds / 86400.0],
        'radius_equiv': [radius]
    })
    metric_df['dQpeak'] = metric_df['peak_Q']/metric_df['peaktime_Q']
    metric_df['dCpeak'] = metric_df['peak_C']/metric_df['peaktime_C']

    return metric_df, df_all


def _find_intersection(limbs, method='auto'):
    """Find intersection between rising and falling limbs."""
    # Auto-select method
    if method == 'auto':
        if HAS_SHAPELY:
            method = 'shapely'
        elif HAS_PPI:
            method = 'bentley-ottmann'
        else:
            method = 'simple'

    limbs_clean = limbs.dropna()
    if len(limbs_clean) < 2:
        return None

    if method == 'shapely':
        if not HAS_SHAPELY:
            raise ImportError("shapely not available. Install: pip install shapely")

        coords1 = np.column_stack([limbs_clean.index, limbs_clean[0]])
        coords2 = np.column_stack([limbs_clean.index, limbs_clean[1]])

        line1 = LineString(coords1)
        line2 = LineString(coords2)
        intersection = line1.intersection(line2)

        if intersection.is_empty:
            return None
        elif intersection.geom_type == 'Point':
            return intersection.x
        elif intersection.geom_type == 'MultiPoint':
            return np.median([pt.x for pt in intersection.geoms])
        return None

    elif method == 'bentley-ottmann':
        if not HAS_PPI:
            raise ImportError("poly_point_isect not available")

        try:
            result = ppi.isect_polygon(limbs_clean.values)
            if len(result) > 0:
                # Find closest point on the index
                return limbs_clean.index[abs(limbs_clean.mean(axis=1) - result[0][0]).argmin()]
        except:
            return None

    elif method == 'simple':
        # Find where limbs cross by checking sign changes
        diff = limbs_clean[0] - limbs_clean[1]
        sign_changes = np.where(np.diff(np.sign(diff)))[0]
        if len(sign_changes) > 0:
            # Return first crossing point
            return limbs_clean.index[sign_changes[0]]
        return None

    else:
        raise ValueError(f"Unknown method: {method}")


def draw_circle(radius, center_x=0.5, center_y=0.5, n_points=100):
    '''Generate circle coordinates for visualization.
    radius :: equiv radius from harp calculation
    center_x/center_y :: optional to center the circle in the plot
    npoints :: points on the circle
    
    returns :: x, y as coordinates'''
    t = np.linspace(0, 2 * np.pi, n_points)
    x = center_x + radius * np.cos(t)
    y = center_y + radius * np.sin(t)
    return x, y

def harp_plot(df_processed,metrics):
    '''Visualize hysteresis loop
    df_processed :: df_all output from calculate_harp_metrics
    metrics :: metrics output from calculate_harp_metrics
    returns :: fig -> can be shown, saved, or further be processed
    '''
    fig = go.Figure()

    # Plot data colored by time
    fig.add_trace(go.Scatter(x=df_processed['QS'],y=df_processed['CS'],mode='markers+lines',
        marker=dict(color=df_processed['Etime'], colorscale='Viridis', showscale=True,colorbar=dict(title='Time (days)')),
        name='Hysteresis loop'))

    # Add equivalent area circle
    circ_x, circ_y = draw_circle(metrics['radius_equiv'].values[0])
    fig.add_trace(go.Scatter(x=circ_x, y=circ_y,mode='lines',line=dict(color='pink', width=2, dash='dot'),
        name=f'Equiv. area (r={metrics["radius_equiv"].values[0]:.3f})'))

    # Mark intersection point if exists
    if 'X' in df_processed['switchpointsQ'].values:
        x_point = df_processed.loc[df_processed['switchpointsQ'] == 'X', 'QS']
        y_point = df_processed.loc[df_processed['switchpointsC'] == 'X', 'CS']
        fig.add_trace(go.Scatter(x=x_point, y=y_point,mode='markers',
            marker=dict(color='pink', size=12, symbol='x'),name='Intersection'))

    fig.update_layout(template='none',xaxis_title='Discharge (scaled)',yaxis_title='Concentration (scaled)',title='C-Q Hysteresis Loop')
    return fig