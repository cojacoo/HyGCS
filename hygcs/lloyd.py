"""
Lawler and Lloyd Hysteresis Index Calculator

Python implementation of the hysteresis index method by Lawler et al. (2006) and Lloyd et al. (2015)

Lawler, D. M., Petts, G. E., Foster, I. D. L., and Harper, S. (2006): Turbidity dynamics during spring
storm events in an urban headwater river system: The Upper Tame, West Midlands, UK, Sci. Total Environ.,
360, 109–126, https://doi.org/10.1016/j.scitotenv.2005.08.032
Lloyd, C. E. M., Freer, J. E., Johnes, P. J., and Collins, A. L. (2016): Using hysteresis analysis of
high-resolution water quality monitoring data, including uncertainty, to infer controls on nutrient
and sediment transfer in catchments, Sci. Total Environ., 543, 388–404,
https://doi.org/10.1016/j.scitotenv.2015.11.028
Lloyd, C. E. M., Freer, J. E., Johnes, P. J., and Collins, A. L. (2016): Technical Note: Testing an
improved index for analysing storm discharge–concentration hysteresis, Hydrol. Earth Syst. Sci., 20,
625–632, https://doi.org/10.5194/hess-20-625-2016

This module calculates hysteresis indices and classification from time series
of two variables (typically discharge and concentration or similar).

Version 2.0 (2025-12-02) - CRITICAL BUG FIX
FIXED: Column indexing bug that caused KeyError when accessing limbs DataFrame

(cc) conrad.jackisch@tbt.tu-freiberg.de
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.signal import find_peaks
from sklearn.preprocessing import MinMaxScaler
import warnings

def calculate_lawlerlloyd_metrics(df_obs, time_col='Etime', discharge_col='Q', concentration_col='C'):
    """
    Calculate Lawler-Lloyd hysteresis index.

    Parameters
    ----------
    df_obs : pd.DataFrame
        Observed data with time, discharge, and concentration columns
    time_col, discharge_col, concentration_col : str
        Column names for time, discharge, and concentration

    Returns
    -------
    metrics_df : pd.DataFrame
        Lawler-Lloyd metrics:
        - mean_HI: Mean hysteresis index across percentiles
        - median_HI: Median hysteresis index
        - HI_range: Range of HI values (max - min)
        - mean_abs_HI: Mean of absolute HI values
    df_all : pd.DataFrame
        Processed time series data with:
        - Q, C: Original discharge and concentration values
        - QS, CS: Normalized (0-1) discharge and concentration
        - Qphase, Cphase: Rising/falling phase indicators
        - switchpoints: Peak markers (gQ, gC, lQ, lC)
        Plus HI percentile data stored in attrs:
        - attrs['HI_percentiles']: DataFrame with Hi, RLi, FLi at each QS percentile
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
    # *** CRITICAL FIX (v2.0): Explicitly set column names to integer indices ***
    limbs.columns = [0, 1]  # Use integer column names for compatibility

    # Calculate both Lawler (2006) and Lloyd (2016) HI methods at QS percentiles
    # Lawler et al. (2006) - Equations 1 & 2: Ratio-based method
    # Lloyd et al. (2016) - Equation 5: Difference-based method (normalized)

    percentiles = np.arange(0.1, 1.0, 0.1)
    HI_data = pd.DataFrame(index=percentiles, columns=['HIL', 'HInew', 'RLi', 'FLi'])

    for i in percentiles:
        # Sample limbs at QS percentile VALUE i (not index position!)
        if i in limbs.index:
            C_rise = limbs.loc[i, 0]
            C_fall = limbs.loc[i, 1]
        else:
            # Interpolate if exact percentile not in index
            C_rise = np.interp(i, limbs.index, limbs.iloc[:, 0])
            C_fall = np.interp(i, limbs.index, limbs.iloc[:, 1])

        # Store limb values
        HI_data.loc[i, 'RLi'] = C_rise
        HI_data.loc[i, 'FLi'] = C_fall

        # METHOD 1: Lawler et al. (2006) - Ratio method (Eq. 1 & 2 from Paper)
        if C_rise > C_fall:  # Clockwise
            if C_fall == 0:
                HI_data.loc[i, 'HIL'] = np.nan  # Undefined
            else:
                HI_data.loc[i, 'HIL'] = (C_rise / C_fall) - 1
        else:  # Anticlockwise
            if C_rise == 0:
                HI_data.loc[i, 'HIL'] = np.nan  # Undefined
            else:
                HI_data.loc[i, 'HIL'] = (-1 / (C_rise / C_fall)) + 1

        # METHOD 2: Lloyd et al. (2016) - Difference method (Eq. 5 from Technical Note (recommended method))
        C_mid = max(C_rise, C_fall)
        if C_mid == 0:
            HI_data.loc[i, 'HInew'] = 0
        else:
            HI_data.loc[i, 'HInew'] = (C_rise - C_fall) / C_mid

    # Calculate summary metrics for both methods
    # Suppress "Mean of empty slice" warnings when all values are NaN
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='Mean of empty slice')
        warnings.filterwarnings('ignore', category=RuntimeWarning)

        metric_df = pd.DataFrame({
            # Lawler method (ratio-based)
            'mean_HIL': [HI_data['HIL'].mean()],
            'median_HIL': [HI_data['HIL'].median()],
            'HIL_range': [HI_data['HIL'].max() - HI_data['HIL'].min()],
            # Lloyd new method (difference-based, recommended)
            'mean_HInew': [HI_data['HInew'].mean()],
            'median_HInew': [HI_data['HInew'].median()],
            'HInew_range': [HI_data['HInew'].max() - HI_data['HInew'].min()],
            'mean_abs_HInew': [HI_data['HInew'].abs().mean()]
        })

    # Store percentile data in attrs for plotting
    metric_df.attrs['HI_percentiles'] = HI_data

    return metric_df, df_all


def lloyd_plot(df_all, metrics):
    """
    Visualize Lawler-Lloyd hysteresis analysis in a two-panel plot:
    - Left: Hysteresis loop with rising/falling limbs
    - Right: HI index across discharge percentiles

    df_all :: Processed DataFrame from calculate_lawlerlloyd_metrics
    metrics :: Metrics DataFrame from calculate_lawlerlloyd_metrics
    returns :: fig -> can be shown, saved, or further be processed
    """
    from plotly.subplots import make_subplots

    # Extract Lloyd-specific data from attrs
    HI_percentiles = metrics.attrs.get('HI_percentiles')

    if HI_percentiles is None:
        raise ValueError("DataFrame missing Lloyd HI data. Ensure it comes from calculate_lawlerlloyd_metrics()")

    title = 'Lawler-Lloyd Hysteresis Analysis'
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Hysteresis Loop', 'HI Index vs Discharge Percentile'), horizontal_spacing=0.12)

    # Left plot: Hysteresis loop
    fig.add_trace(go.Scatter(x=df_all['QS'],y=df_all['CS'],mode='lines+markers',marker=dict(size=4, color='steelblue'),line=dict(color='steelblue'),name='Data'),row=1, col=1)
    # Add percentile markers on rising and falling limb
    fig.add_trace(go.Scatter(x=HI_percentiles.index,y=HI_percentiles['RLi'],mode='markers',marker=dict(size=8, symbol='circle', color='green'),name='Rising limb'),row=1, col=1)
    fig.add_trace(go.Scatter(x=HI_percentiles.index,y=HI_percentiles['FLi'],mode='markers',marker=dict(size=8, symbol='square', color='red'),name='Falling limb'),row=1, col=1)

    # Right plot: Both HI methods across percentiles Lloyd et al. (2016) new method (recommended)
    fig.add_trace(go.Scatter(x=HI_percentiles.index,y=HI_percentiles['HInew'],mode='lines+markers',marker=dict(size=6, color='purple'),line=dict(color='purple', width=2),name='HI<sub>new</sub> (Lloyd 2016)',fill='tozeroy',fillcolor='rgba(128,0,128,0.1)'),row=1, col=2)
    # Lawler et al. (2006) original method
    fig.add_trace(go.Scatter(x=HI_percentiles.index,y=HI_percentiles['HIL'],mode='lines+markers',marker=dict(size=5, color='orange'),line=dict(color='orange', width=1, dash='dot'),name='HI<sub>L</sub> (Lawler 2006)'),row=1, col=2)
    # Add zero line
    fig.add_hline(y=0, line_dash="solid", line_color="black", line_width=1, row=1, col=2)

    # Update axes
    fig.update_xaxes(title_text="Discharge (normalized)", row=1, col=1)
    fig.update_yaxes(title_text="Concentration (normalized)", row=1, col=1)
    fig.update_xaxes(title_text="Discharge Percentile", row=1, col=2)
    fig.update_yaxes(title_text="HI (-)", row=1, col=2)

    # Add annotation with metrics (showing recommended method)
    annotation_text = (
        f"<b>Lloyd (2016) - Recommended:</b><br>"
        f"Mean HI<sub>new</sub>: {metrics['mean_HInew'].values[0]:.4f}<br>"
        f"Median HI<sub>new</sub>: {metrics['median_HInew'].values[0]:.4f}<br>"
        f"<br><b>Lawler (2006) - Original:</b><br>"
        f"Mean HI<sub>L</sub>: {metrics['mean_HIL'].values[0]:.4f}<br>"
        f"Median HI<sub>L</sub>: {metrics['median_HIL'].values[0]:.4f}"
    )

    fig.add_annotation(text=annotation_text,xref="paper", yref="paper",x=0.98, y=0.98,xanchor='right', yanchor='top',showarrow=False,bgcolor="rgba(255,255,255,0.8)",bordercolor="black",borderwidth=1,font=dict(size=11))
    fig.update_layout(title=title,template='plotly_white',height=400,showlegend=True,legend=dict(x=0.01, y=0.99, xanchor='left', yanchor='top'))

    return fig
