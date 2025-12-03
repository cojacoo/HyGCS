Core Analysis Functions
=======================

The ``gcs_core`` module provides fundamental analysis functions for hysteresis metrics,
CVc/CVq analysis, C-Q slopes, and statistical calculations.

.. currentmodule:: hygcs.gcs_core

Hysteresis Metrics
------------------

.. autofunction:: calculate_all_hysteresis_metrics

   Wrapper function that applies all three hysteresis methods (HARP, Zuecco, Lloyd/Lawler)
   to a single dataset. Returns a dictionary containing metrics from all methods plus
   classification results.

   **Returns:**
      Dictionary with keys:
         - ``harp_metrics``: HARP method results
         - ``zuecco_metrics``: Zuecco method results
         - ``lloyd_metrics``: Lloyd/Lawler method results
         - ``classifications``: Direction classifications
         - ``processed_data``: DataFrames from each method
         - ``error``: Error message if calculation failed

CVc/CVq Variability Analysis
-----------------------------

.. autofunction:: compute_cvc_cvq_windows

   Compute rolling window analysis of coefficient of variation ratios following
   Musolff et al. (2015). Calculates CVc/CVq to distinguish chemostatic from
   chemodynamic behavior.

   **Interpretation:**
      - CVc/CVq > 1: Chemodynamic (concentration varies more than flow)
      - CVc/CVq < 1: Chemostatic (concentration buffered relative to flow)

C-Q Slope Calculation
----------------------

.. autofunction:: compute_cq_slope

   Calculate C-Q slope using log-log regression: log(C) = log(a) + b·log(Q)
   where b is the power-law exponent.

   **Interpretation:**
      - b > 0.15: Dilution/flushing signature
      - b < -0.15: Enrichment/loading signature
      - |b| < 0.1: Chemostatic buffering

Flow Dynamics Analysis
----------------------

.. autofunction:: analyze_segment_flow_dynamics

   Analyze high-resolution flow data to determine flow phase (rising, falling, peak, low),
   days since peak, and flow level categories. Used for improved classification accuracy
   when hourly or sub-daily flow data is available.

Statistical Functions
---------------------

.. autofunction:: compute_change_percentiles

   Compute percentile-based thresholds for concentration and flow changes.
   Used in the classification system to determine phase boundaries in a
   compound-agnostic manner.

Notes
-----

**Data Requirements**

For hysteresis analysis:
   - Minimum 5 data points
   - Recommended 10-15 points for single events
   - 20-30 points for robust window-scale analysis

For time series classification:
   - Minimum 20-30 sampling points per site
   - Recommended 50+ points covering multiple cycles
   - High-resolution Q data (hourly) improves accuracy

**Scientific References**

- Musolff, A. et al. (2015). Catchment controls on solute export. Advances in Water Resources, 86, 133-146.
- Thompson, S. E. et al. (2011). Comparative hydrology across AmeriFlux sites. Water Resources Research, 47(10).

See Also
--------

- :doc:`api_hysteresis` - Individual hysteresis method functions
- :doc:`api_classification` - Geochemical phase classification
- :doc:`quickstart` - Usage examples
