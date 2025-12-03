Quick Start Guide
=================

This guide will help you get started with HyGCS for common analysis tasks.

Import the Package
------------------

::

    import hygcs as gcs
    import pandas as pd
    import numpy as np

Single Event Hysteresis Analysis
---------------------------------

For analyzing individual storm events or flushing episodes.

Load Your Data
~~~~~~~~~~~~~~

Your data should contain:

- Time column (datetime or numeric)
- Discharge/flow column (Q)
- Concentration column (C)

Minimum 10-15 points recommended, ideally 20-30 points covering the full event.

::

    # Load event data
    data = pd.read_csv('storm_event.csv')

    # Ensure time is datetime if needed
    data['datetime'] = pd.to_datetime(data['datetime'])

Calculate Hysteresis Metrics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the comprehensive wrapper function::

    metrics = gcs.calculate_all_hysteresis_metrics(
        data,
        time_col='datetime',
        discharge_col='Q_Ls',
        concentration_col='NO3_mgL'
    )

Extract Results
~~~~~~~~~~~~~~~

::

    # HARP method results
    harp = metrics['harp_metrics']
    print(f"HARP Area: {harp['area']:.4f}")
    print(f"Peak Q timing: {harp['peaktime_Q']:.2f} days")
    print(f"Peak C timing: {harp['peaktime_C']:.2f} days")

    # Zuecco method results
    zuecco = metrics['zuecco_metrics']
    print(f"Zuecco h-index: {zuecco['h_index']:.4f}")
    print(f"Zuecco class: {zuecco['hyst_class']}")

    # Lloyd/Lawler results
    lloyd = metrics['lloyd_metrics']
    print(f"Lloyd HInew: {lloyd['mean_HInew']:.4f}")
    print(f"Direction: {metrics['classifications']['lloyd_direction']}")

Visualize Individual Methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # Get full DataFrames for plotting
    from hygcs.harp import calculate_harp_metrics, harp_plot
    harp_m, harp_df = calculate_harp_metrics(data,
                                              time_col='datetime',
                                              discharge_col='Q_Ls',
                                              concentration_col='NO3_mgL')

    fig = harp_plot(harp_df, harp_m)
    fig.show()

Time Series Classification
---------------------------

For long-term monitoring data with multiple sampling cycles.

Prepare Your Data
~~~~~~~~~~~~~~~~~

Required columns:

- ``site_id``: Site identifier (string)
- ``date``: Datetime
- Flow column (your choice of name)
- Concentration column (your choice of name)

::

    # Load monitoring time series
    pcd = pd.read_csv('monitoring_data.csv')
    pcd['date'] = pd.to_datetime(pcd['date'])

    # Check data structure
    print(pcd[['site_id', 'date', 'Q_mLs', 'PLI']].head())

Optional: High-Resolution Flow Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For improved accuracy, provide hourly flow data::

    # Load high-res Q data
    Qx = pd.read_csv('flow_hourly.csv', index_col=0, parse_dates=True)

Run Classification
~~~~~~~~~~~~~~~~~~

::

    classified = gcs.classify_geochemical_phase(
        pcd,
        sites=['Site1', 'Site2', 'Site3'],
        flow_highres=Qx,      # Optional
        ccol='PLI',           # Your concentration column
        qcol='Q_mLs',         # Your flow column
        use_highres=True      # Set False if no Qx provided
    )

Examine Results
~~~~~~~~~~~~~~~

::

    # View classification results
    print(classified[['site_id', 'start_date', 'end_date',
                      'geochemical_phase', 'phase_confidence']].head(10))

    # Check confidence scores
    print(f"Mean confidence: {classified['phase_confidence'].mean():.2f}")
    print(f"Low confidence (<0.7): {(classified['phase_confidence'] < 0.7).sum()} segments")

Visualize Phase Sequence
~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # Create phase timeline
    fig = gcs.create_phase_sequence_plot(classified, sites=['Site1', 'Site2'])
    fig.show()

Create Diagnostic Plots
~~~~~~~~~~~~~~~~~~~~~~~~

::

    # CVc/CVq vs C-Q slope space
    fig_diag = gcs.create_diagnostic_plot(classified)
    fig_diag.show()

Create Hysteresis Plots
~~~~~~~~~~~~~~~~~~~~~~~~

::

    # Single site hysteresis loops
    fig_hyst = gcs.create_hysteresis_plot(
        classified,
        sites=['Site1'],
        ccol='PLI',
        qcol='Q_mLs',
        compound='PLI',
        conc_unit='µg/L'
    )
    fig_hyst.show()

CVc/CVq Variability Analysis
-----------------------------

Analyze chemostatic vs. chemodynamic behavior.

Compute Rolling Windows
~~~~~~~~~~~~~~~~~~~~~~~~

::

    cvc_cvq = gcs.compute_cvc_cvq_windows(
        pcd,
        qcol='Q_mLs',
        ccol='PLI',
        window=5  # Number of samples per window
    )

    # View results
    print(cvc_cvq[['site_id', 'end_date', 'CVc_CVq', 'cq_slope_loglog']].head())

Interpret Results
~~~~~~~~~~~~~~~~~

- **CVc/CVq > 1**: Chemodynamic - concentration varies more than flow
- **CVc/CVq < 1**: Chemostatic - concentration buffered relative to flow
- **cq_slope_loglog > 0.15**: Dilution/flushing signature
- **cq_slope_loglog < -0.15**: Enrichment/loading signature
- **|cq_slope_loglog| < 0.1**: Chemostatic buffering

C-Q Slope Calculation
----------------------

Calculate power-law exponents for C-Q relationships.

::

    slopes = gcs.compute_cq_slope(
        pcd,
        qcol='Q_mLs',
        ccol='PLI'
    )

    # View slope results
    print(slopes[['site_id', 'end_date', 'cq_slope_loglog',
                  'cq_intercept_loglog', 'cq_r2']].head())

Understanding the Output
------------------------

Hysteresis Metrics
~~~~~~~~~~~~~~~~~~

**HARP**:
- ``area``: Loop area magnitude
- ``peaktime_Q``, ``peaktime_C``: Peak timings (compare for flushing vs dilution)
- ``residual``: End-state deviation

**Zuecco**:
- ``h_index``: Integrated area (positive = clockwise, negative = counter-clockwise)
- ``hyst_class``: 0-8 classification (1-4 clockwise variants, 5-8 counter-clockwise)

**Lloyd/Lawler**:
- ``mean_HInew``: Recommended index, range [-1, 1]
- ``mean_HIL``: Original Lawler index
- Direction: clockwise, counter-clockwise, or weak

Geochemical Phases
~~~~~~~~~~~~~~~~~~

- **F (Flushing)**: Dilution during high flow, steep C decline
- **L (Loading)**: Enrichment, C increases with Q
- **C (Chemostatic)**: Buffered, low variability
- **D (Dilution)**: Post-flush recovery
- **R (Recession)**: Late cycle, declining
- **V (Variable)**: Mixed/ambiguous

Confidence Scores
~~~~~~~~~~~~~~~~~

- **> 0.9**: High confidence - robust classification
- **0.7-0.9**: Moderate confidence
- **< 0.7**: Low confidence - investigate further, may need more data

Common Workflows
----------------

Compare Multiple Events
~~~~~~~~~~~~~~~~~~~~~~~~

::

    events = ['event1.csv', 'event2.csv', 'event3.csv']
    results = []

    for event_file in events:
        data = pd.read_csv(event_file)
        metrics = gcs.calculate_all_hysteresis_metrics(data, ...)
        results.append({
            'event': event_file,
            'harp_area': metrics['harp_metrics']['area'],
            'zuecco_hi': metrics['zuecco_metrics']['h_index'],
            'lloyd_hi': metrics['lloyd_metrics']['mean_HInew']
        })

    summary = pd.DataFrame(results)
    print(summary)

Multi-Site Summary Statistics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    stats = gcs.create_hysteresis_summary_stats(
        classified,
        sites=['Site1', 'Site2', 'Site3'],
        ccol='PLI',
        hi_method='zuecco'
    )

    print(stats[['site_id', 'phase_name', 'percentage',
                 'mean_duration_days']])

Multi-Compound Comparison
~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    fig = gcs.create_multi_compound_hysteresis_plot(
        pcd, Qx,
        sites=['Site1'],
        ccols=['PLI', 'Ni', 'Zn'],
        compounds=['PLI', 'Ni', 'Zn'],
        conc_units=['µg/L', 'µg/L', 'µg/L'],
        qcol='Q_mLs',
        hi_method='zuecco'
    )
    fig.show()

Best Practices
--------------

1. **Compare Multiple Methods**
   - When all three hysteresis methods agree → high confidence
   - When they disagree → complex pattern, investigate

2. **Validate with Known Events**
   - Test on reference events with known behavior
   - Calibrate interpretation to your system

3. **Check Data Quality**
   - Remove obvious outliers
   - Ensure Q and C are synchronized
   - Verify no missing values in critical periods

4. **Consider Context**
   - Hysteresis alone doesn't explain mechanisms
   - Combine with site knowledge, geology, hydrology
   - Use C-Q slopes for mechanistic insights

5. **Use Confidence Scores**
   - Low confidence → need more data or ambiguous pattern
   - High confidence → classification is robust

Troubleshooting
---------------

"Not enough data points"
~~~~~~~~~~~~~~~~~~~~~~~~

Need at least 5 points for hysteresis, 10+ recommended for robust analysis.

"All NaN results"
~~~~~~~~~~~~~~~~~

Check:
- Column names match your data
- Data types are numeric
- No missing values in the analysis window

"Classification seems wrong"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Verify input data quality
- Check time series continuity
- Examine diagnostic plots
- Compare multiple methods

Next Steps
----------

- Explore the :doc:`examples` notebooks
- Read the :doc:`api_core` reference
- Check :doc:`scientific_background` for method details
