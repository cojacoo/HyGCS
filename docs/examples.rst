Examples
========

Example Jupyter notebooks demonstrating HyGCS functionality.

Available Notebooks
-------------------

demo_gcs_core_function.ipynb
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Comprehensive hysteresis method demonstration**

This notebook provides an in-depth tutorial on:

1. **Single Event Analysis**

   - Loading example datasets
   - Calculating HARP, Zuecco, and Lloyd/Lawler metrics
   - Interpreting results from each method
   - Comparing method outputs

2. **Visual Analysis**

   - HARP C-Q loop visualization with peak markers
   - Zuecco differential area plots
   - Lloyd/Lawler percentile sampling plots

3. **Comparative Analysis**

   - Analyzing multiple datasets
   - Creating summary comparison tables
   - Multi-panel hysteresis loop plots

4. **Method Comparison**

   - Understanding convergent evidence
   - Identifying method disagreements
   - Interpreting complex patterns

**Data:**
   Uses reference datasets from HARP and Zuecco packages (hysteresis_examples.xlsx)

**Best for:**
   Learning the three hysteresis methods and understanding how they complement each other.

test_gcs.ipynb
~~~~~~~~~~~~~~

**Real-world GCS classification demonstration**

This notebook demonstrates time series classification on real mine drainage monitoring data:

1. **Data Loading**

   - Real geochemical monitoring data (test_gc.csv)
   - High-resolution hydrological data (test_hyd.csv)

2. **Classification Workflow**

   - Running ``classify_geochemical_phase()`` on multiple sites
   - Interpreting classification results
   - Examining confidence scores

3. **Visualization**

   - Phase sequence timelines across sites
   - Diagnostic plots (CVc/CVq vs C-Q slope)
   - Hysteresis plots colored by phase
   - Multi-compound comparison plots

4. **Summary Statistics**

   - Phase percentages by site
   - Temporal pattern analysis
   - C-Q slope time series

**Data:**
   Real monitoring data from legacy mine sites analyzing PLI (Pollution Load Index)
   and individual metals (Cd, Zn, Fe).

**Best for:**
   Understanding how to apply GCS to real monitoring data and interpret results.

Running the Notebooks
---------------------

Install Jupyter
~~~~~~~~~~~~~~~

If you haven't already::

    pip install jupyter notebook ipywidgets

Launch Jupyter
~~~~~~~~~~~~~~

From the HyGCS directory::

    jupyter notebook

Navigate to ``examples/`` and open the desired notebook.

Or launch directly::

    jupyter notebook examples/demo_gcs_core_function.ipynb

Interactive Execution
~~~~~~~~~~~~~~~~~~~~~

The notebooks are designed to be run cell-by-cell. Each cell can be executed with
``Shift+Enter``. Follow the narrative flow and experiment with parameters.

Example Workflows
-----------------

Workflow 1: Analyze Single Storm Event
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    import hygcs as gcs
    import pandas as pd

    # Load event data
    event = pd.read_csv('my_storm_event.csv')

    # Calculate all hysteresis metrics
    metrics = gcs.calculate_all_hysteresis_metrics(
        event,
        time_col='datetime',
        discharge_col='Q',
        concentration_col='NO3'
    )

    # Interpret convergence
    harp_area = metrics['harp_metrics']['area']
    zuecco_hi = metrics['zuecco_metrics']['h_index']
    lloyd_hi = metrics['lloyd_metrics']['mean_HInew']

    print(f"HARP area: {harp_area:.3f}")
    print(f"Zuecco h-index: {zuecco_hi:.3f}")
    print(f"Lloyd HInew: {lloyd_hi:.3f}")

    # Check agreement
    if all([x > 0 for x in [harp_area, zuecco_hi, lloyd_hi]]):
        print("✓ All methods agree: Clockwise hysteresis")
    elif all([x < 0 for x in [zuecco_hi, lloyd_hi]]):
        print("✓ Methods agree: Counter-clockwise hysteresis")
    else:
        print("⚠ Methods disagree: Complex pattern, investigate")

Workflow 2: Multi-Site Classification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # Load monitoring data
    pcd = pd.read_csv('monitoring_data.csv')
    pcd['date'] = pd.to_datetime(pcd['date'])

    # Define sites
    sites = pcd['site_id'].unique()

    # Classify
    classified = gcs.classify_geochemical_phase(
        pcd,
        sites=sites,
        ccol='concentration',
        qcol='discharge',
        use_highres=False
    )

    # Summary by site
    for site in sites:
        site_data = classified[classified['site_id'] == site]

        print(f"\n{site}:")
        print(f"  Total segments: {len(site_data)}")
        print(f"  Mean confidence: {site_data['phase_confidence'].mean():.2f}")

        # Phase distribution
        phase_counts = site_data['geochemical_phase'].value_counts()
        for phase, count in phase_counts.items():
            pct = 100 * count / len(site_data)
            print(f"  {phase}: {count} ({pct:.1f}%)")

Workflow 3: Multi-Compound Comparison
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # Prepare compound list
    compounds = ['NO3', 'DOC', 'Ca']

    # Run classification for each compound
    results = {}
    for compound in compounds:
        classified = gcs.classify_geochemical_phase(
            pcd,
            sites=['Site1'],
            ccol=compound,
            qcol='Q',
            use_highres=False
        )
        results[compound] = classified

    # Create multi-compound hysteresis plot
    fig = gcs.create_multi_compound_hysteresis_plot(
        pcd, None,  # No high-res Q
        sites=['Site1'],
        ccols=compounds,
        compounds=compounds,
        conc_units=['mg/L', 'mg/L', 'mg/L'],
        qcol='Q',
        hi_method='zuecco'
    )
    fig.show()

Workflow 4: CVc/CVq Analysis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # Compute CVc/CVq for different window sizes
    windows = [5, 10, 20]

    for w in windows:
        cvc_cvq = gcs.compute_cvc_cvq_windows(
            pcd,
            qcol='Q',
            ccol='NO3',
            window=w
        )

        print(f"\nWindow = {w} samples:")
        print(f"  Mean CVc/CVq: {cvc_cvq['CVc_CVq'].mean():.2f}")

        # Classify behavior
        chemostatic = (cvc_cvq['CVc_CVq'] < 1).sum()
        chemodynamic = (cvc_cvq['CVc_CVq'] >= 1).sum()

        pct_chemostatic = 100 * chemostatic / len(cvc_cvq)
        print(f"  Chemostatic: {pct_chemostatic:.1f}%")
        print(f"  Chemodynamic: {100 - pct_chemostatic:.1f}%")

Expected Outputs
----------------

From demo_gcs_core_function.ipynb
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- HARP, Zuecco, Lloyd metrics for 4 example datasets
- Interactive C-Q loop plots for each method
- Comparative summary table
- Multi-panel hysteresis visualization

From test_gcs.ipynb
~~~~~~~~~~~~~~~~~~~

- Classified time series DataFrame with phases and confidence
- Phase sequence timeline plot showing temporal evolution
- Diagnostic scatter plot in CVc/CVq vs C-Q slope space
- Hysteresis loops colored by geochemical phase
- Multi-compound comparison showing different analytes
- Summary statistics tables

Troubleshooting
---------------

Notebook Won't Open
~~~~~~~~~~~~~~~~~~~

Ensure Jupyter is installed::

    pip install jupyter notebook

Plots Don't Display
~~~~~~~~~~~~~~~~~~~

For Plotly in Jupyter, you may need::

    pip install ipywidgets
    jupyter nbextension enable --py widgetsnbextension

Then restart Jupyter.

Module Import Errors
~~~~~~~~~~~~~~~~~~~~

Ensure HyGCS is installed or on your Python path::

    import sys
    sys.path.append('../hygcs')
    import gcs

Missing Data Files
~~~~~~~~~~~~~~~~~~

Ensure you're in the ``examples/`` directory or adjust file paths::

    data = pd.read_csv('examples/test_gc.csv')

Further Resources
-----------------

- :doc:`quickstart` - Quick start guide with simple examples
- :doc:`api_core` - API reference for all functions
- :doc:`scientific_background` - Detailed method descriptions

Next Steps
----------

After working through the examples:

1. Try on your own data
2. Experiment with parameters
3. Compare method outputs
4. Validate against known events
5. Consult the API reference for advanced usage
