Hysteresis Methods
==================

Individual hysteresis analysis modules implementing scientifically validated methods.

HARP Method
-----------

.. currentmodule:: hygcs.harp

.. autofunction:: calculate_harp_metrics

   Calculate hysteresis metrics using the HARP (Hysteresis Analysis of Rising and falling Peaks)
   method developed by Roberts et al. (2023).

   **Method Overview:**

   HARP uses empirical classification based on:
      - Peak timing difference between Q and C
      - Loop area and shape
      - Residual (end-state deviation)

   **Returns:**

   Tuple of (metrics_dict, dataframe):
      - ``metrics_dict``: Dictionary with area, residual, peak timings, classification
      - ``dataframe``: Processed data with normalized values and classifications

   **Reference:**

   Roberts, M.E. et al. (2023). HARP: A new method for hysteresis analysis.
   Hydrological Processes.

.. autofunction:: harp_plot

   Create HARP visualization showing C-Q loop with peak timing markers.

   Displays:
      - C-Q hysteresis loop
      - Peak Q and Peak C markers
      - Time progression coloring
      - Loop area shading

Zuecco Method
-------------

.. currentmodule:: hygcs.zuecco

.. autofunction:: calculate_zuecco_metrics

   Calculate hysteresis index using the Zuecco et al. (2016) integration method.

   **Method Overview:**

   Integration-based approach calculating differential areas between rising
   and falling limbs:
      - h-index: Sum of differential areas
      - 9-class classification system (0-8)
      - Quantifies magnitude and direction

   **Classification:**

   ========  ============================
   Class     Description
   ========  ============================
   0         Linear / no hysteresis
   1-4       Clockwise variants
   5-8       Counter-clockwise variants
   ========  ============================

   **Returns:**

   Tuple of (metrics_dict, dataframe):
      - ``metrics_dict``: h_index, hyst_class, min/max differential areas
      - ``dataframe``: Processed data with cumulative areas and classifications

   **Reference:**

   Zuecco, G. et al. (2016). A versatile index to characterize hysteresis
   between hydrological variables at the runoff event timescale.
   Hydrological Processes, 30(9), 1449-1466.

.. autofunction:: zuecco_plot

   Create Zuecco visualization showing C-Q loop with differential areas.

   Displays:
      - C-Q hysteresis loop
      - Rising/falling limb differentiation
      - Differential area shading
      - h-index annotation

Lloyd/Lawler Methods
--------------------

.. currentmodule:: hygcs.lloyd

.. autofunction:: calculate_lawlerlloyd_metrics

   Calculate hysteresis indices using percentile-based methods from
   Lloyd et al. (2016) and Lawler et al. (2006).

   **Method Overview:**

   Two complementary approaches:

   1. **HInew (Lloyd 2016) - RECOMMENDED**

      Difference-based method::

         HI = (C_rise - C_fall) / C_mid

      - Symmetric range: [-1, 1]
      - Better for comparisons
      - More interpretable

   2. **HIL (Lawler 2006) - ORIGINAL**

      Ratio-based method::

         HI = (C_rise / C_fall) - 1  if C_rise > C_fall
         HI = (-1 / (C_rise / C_fall)) + 1  otherwise

      - Asymmetric range
      - More sensitive at extremes

   Both methods sample at 9 discharge percentiles (0.1, 0.2, ..., 0.9).

   **Returns:**

   Tuple of (metrics_dict, dataframe):
      - ``metrics_dict``: mean/median HInew, mean/median HIL, ranges
      - ``dataframe``: Processed data with percentile samples and indices

   **References:**

   - Lloyd, C.E.M. et al. (2016). Using hysteresis analysis of high-resolution
     water quality monitoring data. Hydrology and Earth System Sciences, 20, 2705-2719.
   - Lawler, D.M. et al. (2006). Turbidity dynamics during spring storm events.
     Science of the Total Environment, 360, 109-126.

.. autofunction:: lloyd_plot

   Create Lloyd/Lawler visualization showing percentile samples and HI values.

   Displays:
      - C-Q hysteresis loop
      - Percentile sample points (rising/falling)
      - HInew and HIL indices
      - Hysteresis direction

Comparison and Selection
-------------------------

When to Use Each Method
~~~~~~~~~~~~~~~~~~~~~~~

**HARP**
   - Best for qualitative interpretation
   - Easy to understand (peak timing)
   - Good for identifying flushing vs. dilution
   - Use when process timing is important

**Zuecco**
   - Best for quantitative comparisons
   - Detects complex/mixed patterns
   - 9-class system captures subtle variations
   - Use for detailed pattern characterization

**Lloyd/Lawler (HInew)**
   - Best for standardized reporting
   - Symmetric range facilitates comparison
   - Standard in literature
   - Use for publication-quality quantification

Convergent Evidence
~~~~~~~~~~~~~~~~~~~

**High Confidence** - All three methods agree on direction and approximate magnitude

**Moderate Confidence** - Two methods agree, third differs slightly

**Low Confidence** - Methods disagree significantly

When methods disagree, this indicates:
   - Complex or mixed hysteresis pattern
   - Insufficient data points
   - Ambiguous event structure
   - Need for additional investigation

Usage Example
-------------

Compare All Three Methods::

    import hygcs as gcs

    # Calculate all methods
    metrics = gcs.calculate_all_hysteresis_metrics(
        data,
        time_col='datetime',
        discharge_col='Q',
        concentration_col='C'
    )

    # Extract results
    print("HARP:")
    print(f"  Area: {metrics['harp_metrics']['area']:.4f}")
    print(f"  Peak timing diff: {metrics['harp_metrics']['peaktime_C'] -
                                   metrics['harp_metrics']['peaktime_Q']:.2f} days")

    print("\nZuecco:")
    print(f"  h-index: {metrics['zuecco_metrics']['h_index']:.4f}")
    print(f"  Class: {metrics['zuecco_metrics']['hyst_class']}")

    print("\nLloyd/Lawler:")
    print(f"  HInew: {metrics['lloyd_metrics']['mean_HInew']:.4f}")
    print(f"  HIL: {metrics['lloyd_metrics']['mean_HIL']:.4f}")
    print(f"  Direction: {metrics['classifications']['lloyd_direction']}")

Visualize Each Method::

    # HARP visualization
    harp_m, harp_df = gcs.calculate_harp_metrics(data, ...)
    fig_harp = gcs.harp_plot(harp_df, harp_m)
    fig_harp.show()

    # Zuecco visualization
    zuecco_m, zuecco_df = gcs.calculate_zuecco_metrics(data, ...)
    fig_zuecco = gcs.zuecco_plot(zuecco_df, zuecco_m)
    fig_zuecco.show()

    # Lloyd visualization
    lloyd_m, lloyd_df = gcs.calculate_lawlerlloyd_metrics(data, ...)
    fig_lloyd = gcs.lloyd_plot(lloyd_df, lloyd_m)
    fig_lloyd.show()

Data Requirements
-----------------

All three methods require:
   - Minimum 5 data points (10-15 recommended)
   - Complete Q and C time series
   - No missing values during event
   - Identifiable rising and falling limbs

For best results:
   - 20-30 points covering full event
   - Well-sampled peaks
   - Synchronized Q and C measurements
   - Quality-controlled data (outliers removed)

See Also
--------

- :doc:`api_core` - Wrapper function ``calculate_all_hysteresis_metrics()``
- :doc:`quickstart` - Basic usage examples
- :doc:`scientific_background` - Detailed method descriptions
