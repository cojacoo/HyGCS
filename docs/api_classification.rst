Classification Functions
========================

The ``gcs_classification`` module provides geochemical phase classification
using hierarchical rule-based logic with percentile thresholds.

.. currentmodule:: hygcs.gcs_classification

Main Classification Function
-----------------------------

.. autofunction:: classify_geochemical_phase

   **Main API function** for time series geochemical phase classification.

   Classifies monitoring data into 6 geochemical phases based on:
      - Window-scale hysteresis indices (HARP, Zuecco, Lloyd)
      - C-Q slope (power-law exponent)
      - CVc/CVq variability ratios
      - Flow dynamics (rising/falling limbs, peaks)
      - Temporal context (previous phases, trajectories)

   **The 6 Geochemical Phases:**

   **F (Flushing)**
      Rapid mobilization with steep concentration decline during high flow.
      Characterized by positive C-Q slope and dilution signature.

   **L (Loading)**
      Accumulation phase with concentration rising to maximum.
      Characterized by negative C-Q slope and enrichment.

   **C (Chemostatic)**
      Low hysteresis, stable behavior with minimal variability.
      Flat C-Q slope, low CVc/CVq ratio.

   **D (Dilution)**
      Post-flush recovery with declining flow and concentration.

   **R (Recession)**
      Late cycle, low connectivity, both flow and concentration declining.

   **V (Variable)**
      Ambiguous or mixed patterns that don't fit other categories.

   **Returns:**
      DataFrame with columns:
         - ``site_id``: Site identifier
         - ``start_date``, ``end_date``: Segment temporal bounds
         - ``geochemical_phase``: One of F, L, C, D, R, V
         - ``phase_confidence``: 0.0-1.0 confidence score
         - ``window_HI_zuecco``, ``window_HI_lloyd``, ``window_HI_harp``: Hysteresis indices
         - ``CVc_CVq``: Variability ratio
         - ``cq_slope_loglog``: Power-law exponent
         - ``Q_position``, ``C_position``: Percentile positions
         - ``highres_flow_phase``: Rising/falling/peak/low (if high-res Q provided)
         - Plus many other diagnostic columns

Segment Classification
----------------------

.. autofunction:: classify_segment_phase

   Classify a single segment into a geochemical phase using hierarchical rules.

   Called internally by ``classify_geochemical_phase()`` for each segment.
   Can be used directly if you have pre-computed segment features.

   **Returns:**
      Tuple of (phase, confidence, rules_triggered):
         - ``phase``: str, one of 'F', 'L', 'C', 'D', 'R', 'V'
         - ``confidence``: float, 0.0-1.0
         - ``rules_triggered``: list of str with diagnostic rule names

Simple C-Q Classification
--------------------------

.. autofunction:: classify_cq_behavior_simple

   Simple Williams (1989) style classification based on C-Q relationship.

   Provides basic dilution/enrichment/chemostatic classification without
   temporal or hysteresis information.

   **Returns:**
      One of: 'dilution', 'enrichment', 'chemostatic', 'variable'

   .. note::
      This is a simplified classifier. For comprehensive analysis, use
      ``classify_geochemical_phase()`` which integrates hysteresis and
      temporal dynamics.

Classification Logic
---------------------

The classification system uses hierarchical rules with percentile-based thresholds:

1. **Percentile Calculation**

   Thresholds are computed from the data distribution to be compound-agnostic:
      - Flow percentiles (33rd, 67th)
      - Concentration change percentiles (25th, 75th)
      - C-Q slope thresholds (±0.15, ±0.1)

2. **Hierarchical Rules**

   Rules are checked in priority order:
      - Strong signatures (Flushing, Loading) checked first
      - Moderate signatures (Chemostatic, Dilution, Recession) next
      - Variable assigned if no clear pattern

3. **Confidence Scoring**

   Based on:
      - Number of rules triggered
      - Agreement between indicators
      - Data quality (sufficient points, valid metrics)
      - Consistency with temporal context

4. **Multi-Method Integration**

   Zuecco index is primary (most robust), with Lloyd and HARP as fallbacks.

Scientific Basis
----------------

**Percentile-Based Thresholds**

Compound-agnostic classification using relative positions rather than
absolute concentrations. Adapts to different compounds and concentration ranges.

**C-Q Slope Integration**

Power-law exponent reveals mechanistic processes:
   - b > 0: Transport-limited (flushing)
   - b < 0: Source-limited (loading)
   - b ≈ 0: Chemostatic buffering

**Window-Scale Hysteresis**

Captures temporal dynamics correctly by computing hysteresis metrics
on moving windows around each segment, not on full time series.

**Hierarchical Rules**

Prioritizes phase detection to avoid ambiguity and improve classification
robustness across different monitoring scenarios.

Usage Examples
--------------

Basic Classification::

    import hygcs as gcs

    classified = gcs.classify_geochemical_phase(
        pcd,
        sites=['Site1', 'Site2'],
        ccol='PLI',
        qcol='Q_mLs',
        use_highres=False
    )

    print(classified[['site_id', 'geochemical_phase',
                      'phase_confidence']].head())

With High-Resolution Flow::

    # Hourly Q data improves accuracy
    Qx = pd.read_csv('flow_hourly.csv', index_col=0, parse_dates=True)

    classified = gcs.classify_geochemical_phase(
        pcd,
        sites=['Site1'],
        flow_highres=Qx,
        ccol='PLI',
        qcol='Q_mLs',
        use_highres=True
    )

Filter by Confidence::

    # Keep only high-confidence classifications
    high_conf = classified[classified['phase_confidence'] > 0.8]

    # Investigate low-confidence segments
    low_conf = classified[classified['phase_confidence'] < 0.7]
    print(low_conf[['site_id', 'geochemical_phase', 'CVc_CVq',
                    'cq_slope_loglog']])

See Also
--------

- :doc:`api_core` - Core analysis functions
- :doc:`api_visualization` - Visualization of classification results
- :doc:`quickstart` - Quick start guide with examples
- :doc:`scientific_background` - Detailed methodology
