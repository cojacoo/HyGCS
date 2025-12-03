"""
Zuecco Hysteresis Index Calculator

Python implementation of the hysteresis index method by Zuecco et al. (2016)
Original code by Florian Ulrich Jehn: https://github.com/florianjehn/Hysteresis-Index-Zuecco
Please note that the code is not exactly the same and h results deviate slightly from each other.
The classification appears to be consistent.

Florian Ulrich Jehn. (2019). zutn/Hysteresis-Index-Zuecco: First public version (1.0). Zenodo. https://doi.org/10.5281/zenodo.3441882
Zuecco, G., Penna, D., Borga, M., & van Meerveld, H. J. (2016). A versatile index to characterize hysteresis between hydrological 
variables in the frequency domain. Hydrological Processes, 30(9), 1554-1572. https://doi.org/10.1002/hyp.10681

This module calculates hysteresis indices and classification from time series
of two variables (typically discharge and concentration or soil moisture).

The method computes the difference between rising and falling limb areas
and classifies hysteresis patterns into 9 classes.

(cc) conrad.jackisch@tbt.tu-freiberg.de
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.signal import find_peaks
from sklearn.preprocessing import MinMaxScaler

def calculate_zuecco_metrics(df_obs, time_col='Etime', discharge_col='Q', concentration_col='C'):
    """
    Calculate Zuecco hysteresis index and classification.

    Parameters
    ----------
    df_obs : pd.DataFrame
        Observed data with time, discharge, and concentration columns
    time_col, discharge_col, concentration_col : str
        Column names for time, discharge, and concentration
    
    Returns
    -------
    metrics_df : pd.DataFrame
        Zuecco metrics:
        - h_index: Hysteresis index (sum of differential areas)
        - hyst_class: Hysteresis class (0-8)
        - min_diff_area: Minimum differential area
        - max_diff_area: Maximum differential area
    df_all : pd.DataFrame
        Processed time series data with:
        - Q, C: Original discharge and concentration values
        - QS, CS: Normalized (0-1) discharge and concentration
        - Qphase, Cphase: Rising/falling phase indicators
        - switchpoints: Peak markers (gQ, gC, lQ, lC)
        Plus x_fixed interpolation stored in attrs:
        - attrs['x_fixed_interp']: DataFrame with x_fixed, y_rise, y_fall, diff_area
    """
    # Validate input
    if ((discharge_col not in df_obs.columns) | (concentration_col not in df_obs.columns) | (time_col not in df_obs.columns)):
        raise ValueError(f"Columns '{discharge_col}' and/or '{concentration_col}' and/or '{time_col}' not found in dataframe")

    # Check for NaN values
    if df_obs[discharge_col].isna().any() or df_obs[concentration_col].isna().any():
        df_obs = df_obs.dropna()
        print('Input data contains NaN values. Rows dropped. Consider data preparation before processing.')

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
    df_all['switchpoints'] = ''
    df_all.loc[df_all.index[find_peaks(df_all['Q'])[0]], 'switchpoints'] = 'lQ'
    df_all.loc[df_all.index[find_peaks(df_all['C'])[0]], 'switchpoints'] = 'lC'
    df_all.loc[df_all.index[df_all['Q'].argmax()], 'switchpoints'] = 'gQ'
    df_all.loc[df_all.index[df_all['C'].argmax()], 'switchpoints'] = 'gC'

    # Define phases based on discharge
    df_all['Qphase'] = 'rising'
    df_all.loc[df_all.index[df_all['Q'].argmax()]:, 'Qphase'] = 'falling'

    df_all['Cphase'] = 'rising'
    df_all.loc[df_all.index[df_all['C'].argmax()]:, 'Cphase'] = 'falling'

    # Create limbs using original elegant pandas approach
    # Handle duplicates by taking mean of CS values at same QS
    rising_limb = df_all.loc[df_all.Qphase == 'rising', ['QS', 'CS']].groupby('QS').mean()['CS']
    falling_limb = df_all.loc[df_all.Qphase == 'falling', ['QS', 'CS']].groupby('QS').mean()['CS']

    limbs = pd.concat([rising_limb, falling_limb], axis=1, sort=True).interpolate(method='linear')
    limbs.columns = [0, 1]  # Use integer column names for compatibility

    # Define x_fixed points for Zuecco integration (default from original: 0.15 to 1.0)
    x_fixed = pd.Series(np.linspace(0.15, 1.0, 18))

    # Sample limbs at x_fixed points - limbs are already indexed by QS and interpolated
    limbs_fixed = limbs.reindex(x_fixed, method='nearest', tolerance=0.01, limit=1)
    limbs_fixed = limbs_fixed.interpolate(method='linear')
    limbs_fixed.columns = [0, 1]  # Ensure integer column names

    # Check if we have valid data at fixed points
    if limbs_fixed.isna().all().any():
        print("Warning: Some x_fixed points could not be interpolated. Using fallback method.")
        # Fallback: use simple interpolation across full range
        limbs_fixed = pd.DataFrame({
            0: np.interp(x_fixed, limbs.index, limbs[0]),
            1: np.interp(x_fixed, limbs.index, limbs[1])
        }, index=x_fixed)

    # Calculate differential areas between rising and falling limbs
    # Area of each trapezoid: (y1 + y2) * dx / 2
    diff_area = pd.Series(index=range(len(x_fixed) - 1), dtype=float)
    for j in range(len(x_fixed) - 1):
        dx = x_fixed.iloc[j + 1] - x_fixed.iloc[j]
        rise_trap = (limbs_fixed.iloc[j + 1, 0] + limbs_fixed.iloc[j, 0]) * dx / 2
        fall_trap = (limbs_fixed.iloc[j + 1, 1] + limbs_fixed.iloc[j, 1]) * dx / 2
        diff_area.iloc[j] = rise_trap - fall_trap

    # Hysteresis index: sum of differential areas
    h_index = diff_area.sum()
    h_index = h_index if np.isfinite(h_index) else 0

    # Get min/max for classification
    min_diff_area = diff_area.min() if len(diff_area) > 0 else np.nan
    max_diff_area = diff_area.max() if len(diff_area) > 0 else np.nan

    # Classify hysteresis pattern (use renamed columns)
    hyst_class = _find_hysteresis_class(
        df_all['Q'], df_all['C'],
        min_diff_area, max_diff_area, h_index
    )

    # Store results
    metric_df = pd.DataFrame({
        'h_index': [h_index],
        'hyst_class': [hyst_class],
        'min_diff_area': [min_diff_area],
        'max_diff_area': [max_diff_area]
    })

    # Store limbs_fixed data in attrs for plotting
    df_all.attrs['limbs_fixed'] = limbs_fixed
    df_all.attrs['diff_area'] = diff_area
    df_all.attrs['x_fixed'] = x_fixed

    return metric_df, df_all


def _find_hysteresis_class(
    x: pd.Series,
    y: pd.Series,
    min_diff_area: float,
    max_diff_area: float,
    h_index: float
) -> int:
    """
    Classify hysteresis pattern into one of 9 classes (0-8).

    Classes based on Zuecco et al. (2016):
    0: Linear (no hysteresis)
    1-4: Clockwise patterns
    5-8: Counter-clockwise patterns

    Returns
    -------
    hyst_class : int
        Hysteresis class (0-8)
    """
    pos_max_x = x.index.get_loc(x.idxmax())

    # Check rising limb
    min_y_rise = y.iloc[:pos_max_x + 1].min()
    max_y_rise = y.iloc[:pos_max_x + 1].max()
    change_max_y_rise = abs(max_y_rise - y.iloc[0])
    change_min_y_rise = abs(min_y_rise - y.iloc[0])

    if change_max_y_rise != change_min_y_rise:
        hyst_class = _determine_class(
            min_diff_area, max_diff_area, h_index,
            change_max_y_rise, change_min_y_rise
        )
    else:
        # Check falling limb
        min_y_fall = y.iloc[pos_max_x:].min()
        max_y_fall = y.iloc[pos_max_x:].max()
        change_max_y_fall = abs(max_y_fall - y.iloc[0])
        change_min_y_fall = abs(min_y_fall - y.iloc[0])

        if change_min_y_fall != change_max_y_fall:
            hyst_class = _determine_class(
                min_diff_area, max_diff_area, h_index,
                change_max_y_fall, change_min_y_fall
            )
        else:
            hyst_class = 0

    return hyst_class


def _determine_class(
    min_diff_area: float,
    max_diff_area: float,
    h_index: float,
    change_max_y: float,
    change_min_y: float
) -> int:
    """
    Determine specific hysteresis class based on area metrics.

    Returns
    -------
    hyst_class : int
        Hysteresis class (0-8)
    """
    if change_max_y > change_min_y:
        if min_diff_area > 0 and max_diff_area > 0:
            return 1
        elif min_diff_area < 0 and max_diff_area < 0:
            return 4
        elif min_diff_area <= 0 and max_diff_area > 0 and h_index >= 0:
            return 2
        elif min_diff_area < 0 and max_diff_area >= 0 and h_index < 0:
            return 3
        else:
            return 0  # linearity
    else:  # change_max_y < change_min_y
        if min_diff_area > 0 and max_diff_area > 0:
            return 5
        elif min_diff_area < 0 and max_diff_area < 0:
            return 8
        elif min_diff_area <= 0 and max_diff_area > 0 and h_index >= 0:
            return 6
        elif min_diff_area < 0 and max_diff_area >= 0 and h_index < 0:
            return 7
        else:
            return 0  # linearity


def zuecco_plot(df_all, metrics):
    """
    Visualize Zuecco hysteresis analysis results in a two-panel plot:
    - Left: Hysteresis loop with rising/falling limbs
    - Right: Differential area plot

    df_all :: Processed DataFrame from calculate_zuecco_metrics
    metrics :: Metrics DataFrame from calculate_zuecco_metrics
    returns :: fig -> can be shown, saved, or further be processed
    """
    from plotly.subplots import make_subplots

    # Extract Zuecco-specific data from attrs
    limbs_fixed = df_all.attrs.get('limbs_fixed')
    diff_area = df_all.attrs.get('diff_area')
    x_fixed = df_all.attrs.get('x_fixed')

    if limbs_fixed is None or diff_area is None:
        raise ValueError(
            "DataFrame missing Zuecco data. "
            "Ensure it comes from calculate_zuecco_metrics()"
        )

    title='Zuecco Hysteresis Analysis'
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Hysteresis Loop', 'Differential Area'), horizontal_spacing=0.12)

    # Left plot: Hysteresis loop
    fig.add_trace(go.Scatter(x=df_all['QS'],y=df_all['CS'],mode='lines+markers',marker=dict(size=4, color='steelblue'),line=dict(color='steelblue'),name='Data'),row=1, col=1)

    # Add rising limb (limbs_fixed[0])
    fig.add_trace(go.Scatter(x=x_fixed,y=limbs_fixed[0],mode='lines+markers',marker=dict(size=6, symbol='circle', color='green'),line=dict(color='green', dash='dot'),name='Rising limb'),row=1, col=1)

    # Add falling limb (limbs_fixed[1])
    fig.add_trace(go.Scatter(x=x_fixed,y=limbs_fixed[1],mode='lines+markers',marker=dict(size=6, symbol='square', color='red'),line=dict(color='red', dash='dot'),name='Falling limb'),row=1, col=1)

    # Right plot: Differential area
    x_fixed_plot = x_fixed[:len(diff_area)]

    fig.add_trace(go.Scatter(x=x_fixed_plot,y=diff_area.values,mode='lines+markers',marker=dict(size=6, color='red'),line=dict(color='red'),name='ΔA',fill='tozeroy',fillcolor='rgba(255,0,0,0.1)'),row=1, col=2)

    # Add zero line
    fig.add_hline(y=0, line_dash="solid", line_color="black", line_width=1,row=1, col=2)

    # Update axes
    fig.update_xaxes(title_text="x (normalized)", row=1, col=1)
    fig.update_yaxes(title_text="y (normalized)", row=1, col=1)
    fig.update_xaxes(title_text="x (normalized)", row=1, col=2)
    fig.update_yaxes(title_text="ΔA (-)", row=1, col=2)

    # Add annotation with metrics
    annotation_text = (
        f"<b>Hysteresis Index:</b> {metrics['h_index'].values[0]:.4f}<br>"
        f"<b>Class:</b> {int(metrics['hyst_class'].values[0])}"
    )

    fig.add_annotation(text=annotation_text,xref="paper", yref="paper",x=0.98, y=0.98,
        xanchor='right', yanchor='top',showarrow=False,
        bgcolor="rgba(255,255,255,0.8)",bordercolor="black",borderwidth=1,font=dict(size=11)
    )

    fig.update_layout(title=title,template='plotly_white',height=400,showlegend=True,legend=dict(x=0.01, y=0.99, xanchor='left', yanchor='top'))

    return fig
