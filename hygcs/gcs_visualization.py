"""
GCS Visualization Functions

Plotting suite for hysteresis analysis and phase classification.
(cc-by) Version 0.5 (2025-12-02) conrad.jackisch@tbt.tu-freiberg.de, antita.sanchez@mineral.tu-freiberg.de
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Optional, Dict
import warnings

# Import classification function for multi-compound plots
from gcs_classification import classify_geochemical_phase

# =============================================================================
# COLOR SCHEMES (V4 ORIGINAL)
# =============================================================================

phase_colors = {
    'C': '#999999',     # Chemostatic - gray
    'R': '#D55E00',     # Recession - orange
    'V': '#d1bf8f',     # Variable - tan
    'F': '#f781bf',     # Flushing - pink
    'D': '#0072B2',     # Dilution - blue
    'L': '#009E73',     # Loading - green
    '': '#FFFFFF'       # Empty - white
}

phase_names = {
    'F': 'Flushing',
    'L': 'Loading',
    'C': 'Chemostatic',
    'D': 'Dilution',
    'R': 'Recession',
    'V': 'Variable'
}

hyphase_colors = {
    'low flow': '#FEDF57',
    'declining': '#51B848',
    'flush': '#1F77B4'
}


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_line_style_from_hi_class(seg: pd.Series, method: str = 'zuecco') -> str:
    """
    Determine line style from hysteresis classification.

    Parameters
    ----------
    seg : pd.Series
        Segment data with hysteresis classifications
    method : str
        Which HI method to use ('zuecco', 'lloyd', 'harp')

    Returns
    -------
    str
        Plotly dash style: 'solid', '2px 1px', or '1px 1px'
    """
    if method == 'zuecco':
        zuecco_class = seg.get('window_zuecco_class', -1)
        if zuecco_class == -1:
            hi = seg.get('window_HI_zuecco', 0.0)
            return 'solid' if hi > 0.1 else ('2px 1px' if hi < -0.1 else '1px 1px')
        else:
            if 1 <= zuecco_class <= 4:
                return 'solid'
            elif 5 <= zuecco_class <= 8:
                return '2px 1px'
            else:
                return '1px 1px'

    elif method == 'lloyd':
        direction_str = str(seg.get('window_direction', 'unknown')).lower()
        if 'counter' in direction_str or 'anticlockwise' in direction_str:
            return '2px 1px'
        elif 'clockwise' in direction_str:
            return 'solid'
        else:
            hi = seg.get('window_HI_lloyd', 0.0)
            return 'solid' if hi > 0.1 else ('2px 1px' if hi < -0.1 else '1px 1px')

    elif method == 'harp':
        area = seg.get('window_HI_harp', 0.0)
        if abs(area) < 10:
            return '1px 1px'
        return 'solid' if area > 0 else '2px 1px'

    return '1px 1px'


def calculate_log_thickness(hi_values: np.ndarray,
                            min_thickness: float = 3,
                            max_thickness: float = 8) -> np.ndarray:
    """
    Calculate log-normalized line thickness for visualization.

    Parameters
    ----------
    hi_values : array-like
        Absolute hysteresis index values
    min_thickness, max_thickness : float
        Thickness range

    Returns
    -------
    np.ndarray
        Thickness values scaled between min and max
    """
    hi_abs = np.abs(np.asarray(hi_values))

    if len(hi_abs) == 0:
        return np.array([])

    # Suppress warnings for log calculations
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=RuntimeWarning)
        scale_factor = 100
        log_transformed = np.log10(1 + hi_abs * scale_factor)

    has_variance = np.any(hi_abs > 1e-10)
    if not has_variance:
        return np.full(len(hi_values), min_thickness)

    log_min = np.min(log_transformed[hi_abs > 1e-10])
    log_max = np.max(log_transformed)

    if log_max - log_min < 1e-10:
        return np.full(len(hi_values), (min_thickness + max_thickness) / 2)

    normalized = np.zeros_like(log_transformed)
    mask = hi_abs > 1e-10
    normalized[mask] = (log_transformed[mask] - log_min) / (log_max - log_min)

    thickness = min_thickness + (max_thickness - min_thickness) * normalized
    thickness[np.isnan(thickness)] = min_thickness

    return np.clip(thickness, min_thickness, max_thickness)


def _add_phase_legend(fig: go.Figure) -> None:
    """Add phase color legend to figure (helper to avoid duplication)."""
    for phase_code, color in phase_colors.items():
        if phase_code and phase_code in phase_names:
            fig.add_trace(
                go.Scatter(
                    x=[None], y=[None],
                    mode='lines',
                    line=dict(color=color, width=4),
                    name=phase_names[phase_code],
                    showlegend=True
                )
            )


def _plot_hysteresis_segment(fig: go.Figure,
                             seg: pd.Series,
                             thickness: float,
                             line_style_method: str,
                             hi_col: str,
                             row: int,
                             col: int) -> None:
    """
    Add single hysteresis segment to figure (helper to avoid duplication).

    Parameters
    ----------
    fig : go.Figure
        Figure to add trace to
    seg : pd.Series
        Segment with start_flow, end_flow, start_conc, end_conc
    thickness : float
        Line thickness
    line_style_method : str
        Method for determining dash style
    hi_col : str
        HI column name for hover info
    row, col : int
        Subplot position
    """
    dash = get_line_style_from_hi_class(seg, method=line_style_method)
    hi_val = seg[hi_col]

    fig.add_trace(
        go.Scatter(
            x=[seg['start_flow'], seg['end_flow']],
            y=[seg['start_conc'], seg['end_conc']],
            mode='lines',
            line=dict(
                color=phase_colors.get(seg['geochemical_phase'], 'gray'),
                width=thickness,
                dash=dash
            ),
            showlegend=False,
            hovertemplate=f"<b>{seg['geochemical_phase']}</b><br>HI: {hi_val:.3f}<extra></extra>"
        ),
        row=row, col=col
    )


def _plot_data_points_with_load(fig: go.Figure,
                                site_data: pd.DataFrame,
                                ccol: str,
                                qcol: str,
                                compound: str,
                                row: int,
                                col: int,
                                show_legend: bool = False) -> None:
    """
    Plot data points with load-informed sizing and HydPhase colors (helper to avoid duplication).

    Parameters
    ----------
    fig : go.Figure
        Figure to add traces to
    site_data : pd.DataFrame
        Site data with HydPhase column
    ccol, qcol : str
        Concentration and flow column names
    compound : str
        Compound name for hover
    row, col : int
        Subplot position
    show_legend : bool
        Whether to show legend for this trace
    """
    if 'HydPhase' not in site_data.columns:
        return

    # Calculate load for sizing
    site_data['load'] = site_data[ccol] * site_data[qcol] * 86.4
    load_95 = site_data['load'].quantile(0.95)
    load_5 = site_data['load'].quantile(0.05)
    load_range = max(load_95 - load_5, 1e-10)

    for phase in site_data['HydPhase'].dropna().unique():
        phase_data = site_data[site_data['HydPhase'] == phase]
        sizes = 8 + 20 * np.clip((phase_data['load'] - load_5) / load_range, 0, 1)

        fig.add_trace(
            go.Scatter(
                x=phase_data[qcol],
                y=phase_data[ccol],
                mode='markers',
                marker=dict(
                    size=sizes,
                    color=hyphase_colors.get(phase, 'gray'),
                    line=dict(width=1, color='white')
                ),
                name=phase,
                showlegend=show_legend,
                hovertemplate=f'<b>{compound} - {phase}</b><br>Q: %{{x:.2f}}<br>C: %{{y:.3f}}<extra></extra>'
            ),
            row=row, col=col
        )


# =============================================================================
# MAIN PLOTTING FUNCTIONS
# =============================================================================

def create_hysteresis_plot(data: pd.DataFrame,
                          sites: List[str],
                          ccol: str,
                          qcol: str,
                          compound: str,
                          conc_unit: str = 'mg L⁻¹',
                          flow_unit: str = 'L s⁻¹',
                          hi_method: str = 'zuecco',
                          show_timeline: bool = True,
                          line_style_method: str = 'zuecco') -> go.Figure:
    """
    Create hysteresis plot for a single compound.

    Parameters
    ----------
    data : pd.DataFrame
        Classification results from classify_geochemical_phase()
    sites : list of str
        Sites to plot
    ccol, qcol : str
        Concentration and flow column names
    compound : str
        Compound name for labeling
    conc_unit, flow_unit : str
        Units for labeling
    hi_method : str
        Hysteresis method for line thickness ('zuecco', 'lloyd', 'harp')
    show_timeline : bool
        Whether to show timeline subplot
    line_style_method : str
        Hysteresis method for line style ('zuecco', 'lloyd', 'harp')

    Returns
    -------
    go.Figure
        Hysteresis plot figure
    """
    analysis_df = data.copy()

    if len(analysis_df) == 0:
        fig = go.Figure()
        fig.add_annotation(text="No data available for analysis", x=0.5, y=0.5)
        return fig

    # Create subplots
    n_sites = len(sites)
    if show_timeline:
        fig = make_subplots(
            rows=2, cols=n_sites,
            row_heights=[0.8, 0.2],
            subplot_titles=[f'Site {s}' for s in sites] + [''] * n_sites,
            vertical_spacing=0.1
        )
    else:
        fig = make_subplots(rows=1, cols=n_sites, subplot_titles=[f'Site {s}' for s in sites])

    # V5: Use window-scale hysteresis
    hi_col = f'window_HI_{hi_method}'
    if hi_col not in analysis_df.columns:
        raise ValueError(f'{hi_col} not found. Ensure data is from classify_geochemical_phase().')

    # Plot each site
    for idx, site in enumerate(sites):
        col = idx + 1
        site_analysis = analysis_df[analysis_df['site_id'] == site]

        if len(site_analysis) < 1:
            continue

        hi_values = site_analysis[hi_col].values
        thicknesses = calculate_log_thickness(hi_values)

        for i, seg in site_analysis.iterrows():
            thickness = thicknesses[i - site_analysis.index[0]]

            # Hysteresis loop
            _plot_hysteresis_segment(fig, seg, thickness, line_style_method, hi_col, row=1, col=col)

            # Timeline
            if show_timeline:
                dash = get_line_style_from_hi_class(seg, method=line_style_method)
                fig.add_trace(
                    go.Scatter(
                        x=[seg['start_date'], seg['end_date']],
                        y=[seg['start_conc'], seg['end_conc']],
                        mode='lines',
                        line=dict(
                            color=phase_colors.get(seg['geochemical_phase'], 'gray'),
                            width=2,
                            dash=dash
                        ),
                        showlegend=False
                    ),
                    row=2, col=col
                )

    # Update axes
    fig.update_xaxes(type='log', title_text=f'Flow ({flow_unit})', row=1)
    fig.update_yaxes(type='log', title_text=f'{compound} ({conc_unit})', row=1, col=1)

    if show_timeline:
        fig.update_xaxes(title_text='Date', row=2)
        fig.update_yaxes(title_text=f'C ({conc_unit})', row=2, col=1)

    # Add legend
    _add_phase_legend(fig)

    fig.update_layout(
        title=f'{compound} Hysteresis Analysis ({hi_method.title()} method)',
        height=600 if show_timeline else 400,
        width=400 * n_sites,
        showlegend=True,
        legend=dict(orientation='v', x=1.02, y=1),
        template='none'
    )

    return fig


def create_multi_compound_hysteresis_plot(data: pd.DataFrame,
                                         Qx: pd.DataFrame,
                                         sites: List[str],
                                         ccols: List[str],
                                         compounds: List[str],
                                         conc_units: List[str],
                                         qcol: str,
                                         flow_unit: str = 'L s⁻¹',
                                         hi_method: str = 'zuecco',
                                         cxmin: Optional[List[float]] = None,
                                         cxmax: Optional[List[float]] = None,
                                         qxmin: Optional[float] = None,
                                         qxmax: Optional[float] = None,
                                         line_style_method: str = 'zuecco') -> go.Figure:
    """
    Create multi-compound hysteresis comparison plot.

    Each compound is analyzed with its own concentration ranges.

    Parameters
    ----------
    data : pd.DataFrame
        Input data
    Qx : pd.DataFrame
        High-resolution discharge timeseries
    sites : list
        Sites to plot
    ccols : list
        Concentration columns (one per compound)
    compounds : list
        Compound names for labeling
    conc_units : list
        Units for each compound
    qcol : str
        Flow column name
    flow_unit : str
        Flow unit
    hi_method : str
        Hysteresis method for line thickness
    cxmin, cxmax : list of float, optional
        Concentration ranges per compound
    qxmin, qxmax : float, optional
        Flow range (shared)
    line_style_method : str
        Hysteresis method for line style

    Returns
    -------
    go.Figure
        Multi-panel plot
    """
    n_compounds = len(ccols)
    n_sites = len(sites)

    # Create subplot structure
    subplot_titles = []
    for comp in compounds:
        for site in sites:
            subplot_titles.append(f'{comp} - {site}')
        for _ in sites:
            subplot_titles.append('')

    fig = make_subplots(
        rows=n_compounds * 2,
        cols=n_sites,
        row_heights=[0.85, 0.15] * n_compounds,
        subplot_titles=subplot_titles,
        vertical_spacing=0.03,
        horizontal_spacing=0.05
    )

    # Determine flow range (shared)
    if qxmin is None or qxmax is None:
        all_flows = data[qcol].dropna()
        if len(all_flows) > 0:
            qxmin = all_flows.min() * 0.8 if qxmin is None else qxmin
            qxmax = all_flows.max() * 1.2 if qxmax is None else qxmax
        else:
            qxmin, qxmax = 0.1, 100

    # Process each compound
    for comp_idx, (ccol, compound, conc_unit) in enumerate(zip(ccols, compounds, conc_units)):
        compound_data = data.dropna(subset=[ccol, qcol])

        # Determine concentration range for THIS compound
        if cxmin is None or len(cxmin) <= comp_idx:
            comp_cmin = compound_data[ccol].min() * 0.8
        else:
            comp_cmin = cxmin[comp_idx]

        if cxmax is None or len(cxmax) <= comp_idx:
            comp_cmax = compound_data[ccol].max() * 1.2
        else:
            comp_cmax = cxmax[comp_idx]

        # Analyze hysteresis for THIS compound
        classified = classify_geochemical_phase(compound_data, sites, flow_highres=Qx,
                                                ccol=ccol, qcol=qcol, use_highres=True)

        hi_col = f'window_HI_{hi_method}'

        # Process each site
        for site_idx, site in enumerate(sites):
            h_row = comp_idx * 2 + 1
            t_row = comp_idx * 2 + 2
            col = site_idx + 1

            site_data = compound_data[compound_data['site_id'] == site].copy()
            site_analysis = classified[classified['site_id'] == site]

            if len(site_data) < 2:
                continue

            # Plot data points with load-informed sizing
            _plot_data_points_with_load(fig, site_data, ccol, qcol, compound,
                                       h_row, col, show_legend=(comp_idx == 0 and site_idx == 0))

            # Calculate thicknesses
            hi_values = site_analysis[hi_col].values
            thicknesses = calculate_log_thickness(hi_values)
            thicknesses[np.isnan(thicknesses)] = 1.0

            # Plot hysteresis segments
            for i, seg in site_analysis.iterrows():
                thickness = thicknesses[i - site_analysis.index[0]]

                # Hysteresis loop
                _plot_hysteresis_segment(fig, seg, thickness, line_style_method, hi_col, h_row, col)

                # Timeline
                dash = get_line_style_from_hi_class(seg, method=line_style_method)
                fig.add_trace(
                    go.Scatter(
                        x=[seg['start_date'], seg['end_date']],
                        y=[seg['start_conc'], seg['end_conc']],
                        mode='lines',
                        line=dict(
                            color=phase_colors.get(seg['geochemical_phase'], 'gray'),
                            width=2,
                            dash=dash
                        ),
                        showlegend=False
                    ),
                    row=t_row, col=col
                )

            # Update axes with compound-specific ranges
            fig.update_xaxes(type='log', range=[np.log10(qxmin), np.log10(qxmax)], row=h_row, col=col)
            fig.update_yaxes(type='log', range=[np.log10(comp_cmin), np.log10(comp_cmax)],
                           title_text=f'{compound} ({conc_unit})' if site_idx == 0 else '',
                           row=h_row, col=col)
            fig.update_yaxes(range=[comp_cmin, comp_cmax], row=t_row, col=col)

    # Add x-axis labels only on bottom
    for col in range(1, n_sites + 1):
        fig.update_xaxes(title_text=f'Flow ({flow_unit})', row=n_compounds * 2 - 1, col=col)

    # Add legends
    _add_phase_legend(fig)

    fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines',
                            line=dict(color='gray', width=3, dash='solid'),
                            name='Positive HI'))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines',
                            line=dict(color='gray', width=3, dash='2px 1px'),
                            name='Negative HI'))

    fig.update_layout(
        title=f'Multi-Compound Hysteresis Analysis ({hi_method.title()} method)<br>' +
              '<sub>Each compound analyzed with its own concentration range</sub>',
        height=450 * n_compounds,
        width=350 * n_sites + 200,
        showlegend=True,
        legend=dict(x=1.01, y=1),
        template='none'
    )

    return fig


def _add_diagnostic_scatter(fig: go.Figure,
                           phase_data: pd.DataFrame,
                           x_col: str,
                           y_col: str,
                           phase: str,
                           row: int,
                           col: int,
                           symbol: str = 'circle',
                           opacity: float = 1.0,
                           size: int = 8,
                           show_legend: bool = True) -> None:
    """Helper to add diagnostic scatter trace (avoid duplication)."""
    fig.add_trace(
        go.Scatter(
            x=phase_data[x_col],
            y=phase_data[y_col],
            mode='markers',
            marker=dict(
                size=size,
                color=phase_colors.get(phase, 'gray'),
                symbol=symbol,
                opacity=opacity,
                line=dict(width=1 if symbol == 'circle' else 2,
                         color='white' if symbol == 'circle' else phase_colors.get(phase, 'gray'))
            ),
            name=phase_names.get(phase, phase) if show_legend else f'{phase} (unlabeled)',
            legendgroup=phase,
            showlegend=show_legend
        ),
        row=row, col=col
    )


def create_diagnostic_plot(results: pd.DataFrame,
                          manual_labels: Optional[pd.DataFrame] = None,
                          title: str = "Geochemical Phase Classification Diagnostic",
                          show_unlabeled: bool = True) -> go.Figure:
    """
    Create two-panel diagnostic plot for phase classification.

    Left: CVc/CVq vs C-Q Slope
    Right: ΔQ vs ΔC phase space

    Parameters
    ----------
    results : pd.DataFrame
        Classification results
    manual_labels : pd.DataFrame, optional
        Manual labels for validation
    title : str
        Plot title
    show_unlabeled : bool
        Show segments without manual labels (faded)

    Returns
    -------
    go.Figure
        Two-panel diagnostic plot
    """
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=['CVc/CVq vs C-Q Slope', 'ΔQ vs ΔC Phase Space'],
        horizontal_spacing=0.12
    )

    # Prepare data
    if manual_labels is not None:
        merged = pd.merge(
            results,
            manual_labels[['site_id', 'date', 'manual_phase']],
            left_on=['site_id', 'end_date'],
            right_on=['site_id', 'date'],
            how='left'
        )
        labeled = merged[merged['manual_phase'].notna()].copy()
        unlabeled = merged[merged['manual_phase'].isna()].copy()
        labeled['correct'] = labeled['geochemical_phase'] == labeled['manual_phase']
    else:
        labeled = results.copy()
        unlabeled = pd.DataFrame()
        labeled['correct'] = True

    slope_col = 'cq_slope_loglog'

    # Panel 1: CVc/CVq vs Slope
    if show_unlabeled and len(unlabeled) > 0:
        for phase in unlabeled['geochemical_phase'].unique():
            phase_data = unlabeled[unlabeled['geochemical_phase'] == phase]
            _add_diagnostic_scatter(fig, phase_data, 'CVc_CVq', slope_col, phase,
                                   1, 1, opacity=0.2, size=6, show_legend=False)

    for phase in labeled[labeled['correct']]['geochemical_phase'].unique():
        phase_data = labeled[(labeled['geochemical_phase'] == phase) & labeled['correct']]
        _add_diagnostic_scatter(fig, phase_data, 'CVc_CVq', slope_col, phase, 1, 1)

    if 'manual_phase' in labeled.columns:
        misclass = labeled[~labeled['correct']]
        if len(misclass) > 0:
            for phase in misclass['geochemical_phase'].unique():
                phase_data = misclass[misclass['geochemical_phase'] == phase]
                _add_diagnostic_scatter(fig, phase_data, 'CVc_CVq', slope_col, phase,
                                       1, 1, symbol='x', size=10, show_legend=False)

    # Panel 2: ΔQ vs ΔC (similar structure)
    if show_unlabeled and len(unlabeled) > 0:
        for phase in unlabeled['geochemical_phase'].unique():
            phase_data = unlabeled[unlabeled['geochemical_phase'] == phase]
            _add_diagnostic_scatter(fig, phase_data, 'flow_diff', 'conc_diff', phase,
                                   1, 2, opacity=0.2, size=6, show_legend=False)

    for phase in labeled[labeled['correct']]['geochemical_phase'].unique():
        phase_data = labeled[(labeled['geochemical_phase'] == phase) & labeled['correct']]
        _add_diagnostic_scatter(fig, phase_data, 'flow_diff', 'conc_diff', phase, 1, 2, show_legend=False)

    if 'manual_phase' in labeled.columns:
        misclass = labeled[~labeled['correct']]
        if len(misclass) > 0:
            for phase in misclass['geochemical_phase'].unique():
                phase_data = misclass[misclass['geochemical_phase'] == phase]
                _add_diagnostic_scatter(fig, phase_data, 'flow_diff', 'conc_diff', phase,
                                       1, 2, symbol='x', size=10, show_legend=False)

    # Add reference lines
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=1, col=2)
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5, row=1, col=2)

    # Update axes
    fig.update_xaxes(title_text="CVc/CVq", row=1, col=1)
    fig.update_yaxes(title_text="C-Q Slope (log-log)", row=1, col=1)
    fig.update_xaxes(title_text="ΔQ", row=1, col=2)
    fig.update_yaxes(title_text="ΔC", row=1, col=2)

    fig.update_layout(
        title=title,
        height=500,
        width=1200,
        showlegend=True,
        legend=dict(x=1.02, y=1),
        template='none'
    )

    return fig


def create_phase_sequence_plot(results: pd.DataFrame,
                               sites: List[str],
                               gccol: str = 'geochemical_phase') -> go.Figure:
    """
    Create timeline showing phase transitions per site.

    Parameters
    ----------
    results : pd.DataFrame
        Classification results
    sites : list of str
        Sites to plot
    gccol : str
        Column holding classified phase name

    Returns
    -------
    go.Figure
        Timeline plot with phase colors
    """
    fig = go.Figure()

    for site in sites:
        site_data = results[results['site_id'] == site].sort_values('start_date')

        for _, row in site_data.iterrows():
            phase = row[gccol]
            fig.add_trace(
                go.Scatter(
                    x=[row['start_date'], row['end_date']],
                    y=[site, site],
                    mode='lines',
                    line=dict(color=phase_colors.get(phase, 'gray'), width=15),
                    showlegend=False,
                    hovertemplate=(
                        f"<b>{phase_names.get(phase, phase)}</b><br>"
                        f"Start: {row['start_date']}<br>"
                        f"End: {row['end_date']}<br>"
                        f"Confidence: {row.get('phase_confidence', 0):.2f}<extra></extra>"
                    )
                )
            )

    # Add legend
    _add_phase_legend(fig)

    fig.update_layout(
        title='Geochemical Phase Sequence Timeline',
        xaxis_title='Date',
        yaxis_title='Site',
        yaxis=dict(categoryorder='array', categoryarray=sites[::-1]),
        height=100 + 60 * len(sites),
        showlegend=True,
        legend=dict(orientation='h', y=1.3),
        template='none'
    )

    return fig


def create_hysteresis_timeline(results: pd.DataFrame,
                               sites: List[str],
                               compound: str,
                               hi_method: str = 'zuecco') -> go.Figure:
    """
    Create timeline visualization of hysteresis behaviors.

    Parameters
    ----------
    results : pd.DataFrame
        Classification results from classify_geochemical_phase()
    sites : list of str
        Sites to plot
    compound : str
        Compound name for title
    hi_method : str
        Hysteresis method

    Returns
    -------
    go.Figure
        Timeline plot
    """
    if len(results) == 0:
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5)
        return fig

    fig = go.Figure()
    hi_col = f'window_HI_{hi_method}'

    for site in sites:
        site_df = results[results['site_id'] == site]

        for _, seg in site_df.iterrows():
            hi_val = seg.get(hi_col, 0)
            dash = 'solid' if hi_val > 0.1 else ('2px 1px' if hi_val < -0.1 else '1px 1px')

            fig.add_trace(
                go.Scatter(
                    x=[seg['start_date'], seg['end_date']],
                    y=[site, site],
                    mode='lines',
                    line=dict(
                        color=phase_colors.get(seg['geochemical_phase'], 'gray'),
                        width=20,
                        dash=dash
                    ),
                    showlegend=False,
                    hovertemplate=(
                        f"<b>{phase_names.get(seg['geochemical_phase'], seg['geochemical_phase'])}</b><br>"
                        f"HI: {hi_val:.3f}<br>"
                        f"Confidence: {seg.get('phase_confidence', 0):.2f}<br>"
                        f"Duration: {(seg['end_date'] - seg['start_date']).days} days<extra></extra>"
                    )
                )
            )

    # Add legend
    _add_phase_legend(fig)

    fig.update_layout(
        title=f'{compound} Hysteresis Behavior Timeline',
        xaxis_title='Date',
        yaxis_title='Site',
        yaxis=dict(categoryorder='array', categoryarray=sites[::-1]),
        height=100 + 60 * len(sites),
        showlegend=True,
        legend=dict(orientation='h', y=1.1),
        template='none'
    )

    return fig


def create_hysteresis_summary_stats(results: pd.DataFrame,
                                    sites: List[str],
                                    ccol: str,
                                    hi_method: str = 'zuecco') -> pd.DataFrame:
    """
    Generate summary statistics for hysteresis behavior.

    Parameters
    ----------
    results : pd.DataFrame
        Classification results from classify_geochemical_phase()
    sites : list of str
        Sites to analyze
    ccol : str
        Compound column name
    hi_method : str
        Hysteresis method

    Returns
    -------
    pd.DataFrame
        Summary with phase frequencies, durations, and HI statistics
    """
    if len(results) == 0:
        return pd.DataFrame()

    hi_col = f'window_HI_{hi_method}'
    summary = []

    for site in sites:
        site_df = results[results['site_id'] == site]

        if len(site_df) == 0:
            continue

        total_segments = len(site_df)
        date_range = site_df['end_date'].max() - site_df['start_date'].min()

        for phase in site_df['geochemical_phase'].unique():
            phase_df = site_df[site_df['geochemical_phase'] == phase]
            durations = (phase_df['end_date'] - phase_df['start_date']).dt.total_seconds() / 86400

            summary.append({
                'site_id': site,
                'compound': ccol,
                'phase': phase,
                'phase_name': phase_names.get(phase, phase),
                'count': len(phase_df),
                'percentage': len(phase_df) / total_segments * 100,
                'mean_duration_days': durations.mean(),
                'total_duration_days': durations.sum(),
                f'mean_hi_{hi_method}': phase_df[hi_col].mean(),
                f'std_hi_{hi_method}': phase_df[hi_col].std(),
                'mean_confidence': phase_df['phase_confidence'].mean(),
                'monitoring_days': date_range.days,
                'total_segments': total_segments
            })

    return pd.DataFrame(summary)


# =============================================================================
# MODULE METADATA
# =============================================================================

__all__ = [
    'phase_colors',
    'phase_names',
    'hyphase_colors',
    'get_line_style_from_hi_class',
    'calculate_log_thickness',
    'create_hysteresis_plot',
    'create_multi_compound_hysteresis_plot',
    'create_diagnostic_plot',
    'create_phase_sequence_plot',
    'create_hysteresis_timeline',
    'create_hysteresis_summary_stats'
]

print("gcs_visualization.py: plotting functions for GCS")
