Scientific Background
=====================

This page provides detailed scientific context for the methods implemented in HyGCS.

Hysteresis in C-Q Relationships
--------------------------------

Hysteresis occurs when the relationship between concentration (C) and discharge (Q)
differs between rising and falling flow limbs, creating a loop in C-Q space.

Direction and Interpretation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Clockwise Hysteresis**
   Concentration peaks before discharge peaks. Indicates:
      - Flushing of readily available material
      - Transport-limited export
      - Proximal sources
      - High connectivity during rising limb

**Counter-Clockwise Hysteresis**
   Concentration peaks after discharge peaks. Indicates:
      - Progressive mobilization
      - Source-limited export
      - Distal sources
      - Delayed connectivity

**Figure-8 or Complex Patterns**
   Multiple loops or mixed patterns. Indicates:
      - Multiple source contributions
      - Changing transport pathways
      - Complex hydrological response
      - Need for multi-method analysis

Implemented Hysteresis Methods
-------------------------------

HyGCS implements three complementary methods for hysteresis analysis.

HARP Method (Roberts et al., 2023)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Hysteresis Analysis of Rising and falling Peaks**

Empirical classification based on:
   - Peak timing difference (ΔT = T_C - T_Q)
   - Loop area
   - Residual (end-state deviation)

**Strengths:**
   - Intuitive interpretation
   - Clear process identification
   - Named classification system

**Limitations:**
   - Requires clear peaks
   - Qualitative rather than quantitative
   - May struggle with complex patterns

**Reference:**

Roberts, M.E. et al. (2023). Hysteresis Analysis of Rising and falling Peaks (HARP):
A new method to identify changing sediment and hydrological connectivity.
Hydrological Processes.

Zuecco Index (Zuecco et al., 2016)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Integration-Based Hysteresis Index**

Calculates h-index by integrating differential areas between rising and falling limbs:

.. math::

   h = \sum_{i} (A_{rise,i} - A_{fall,i})

where areas are computed between Q percentiles.

**9-Class System:**

========  ============================  ==================
Class     h-index Range                 Description
========  ============================  ==================
0         Near zero                     Linear/no hysteresis
1-4       Positive (varying magnitude)  Clockwise variants
5-8       Negative (varying magnitude)  Counter-clockwise variants
========  ============================  ==================

**Strengths:**
   - Quantitative magnitude assessment
   - Detects complex/mixed patterns
   - Robust to noise

**Limitations:**
   - Requires interpolation
   - Classification thresholds somewhat arbitrary

**Reference:**

Zuecco, G. et al. (2016). A versatile index to characterize hysteresis between
hydrological variables at the runoff event timescale. Hydrological Processes,
30(9), 1449-1466.

Lloyd/Lawler Methods (2016, 2006)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Percentile-Based Indices**

Samples C at 9 Q percentiles (0.1, 0.2, ..., 0.9) on rising and falling limbs.

**HInew (Lloyd 2016) - Recommended:**

.. math::

   HI_{new} = \frac{C_{rise} - C_{fall}}{C_{mid}}

- Symmetric range: [-1, 1]
- C_mid = (C_rise + C_fall) / 2

**HIL (Lawler 2006) - Original:**

.. math::

   HI_L = \begin{cases}
   (C_{rise} / C_{fall}) - 1 & \text{if } C_{rise} > C_{fall} \\
   (-1 / (C_{rise} / C_{fall})) + 1 & \text{otherwise}
   \end{cases}

- Asymmetric range
- More sensitive at extremes

**Strengths:**
   - Standard in literature
   - Percentile-based (robust to outliers)
   - HInew facilitates comparison

**Limitations:**
   - Requires both rising and falling limbs
   - May miss complex patterns

**References:**

- Lloyd, C.E.M. et al. (2016). Using hysteresis analysis of high-resolution
  water quality monitoring data. Hydrology and Earth System Sciences, 20, 2705-2719.
- Lawler, D.M. et al. (2006). Turbidity dynamics during spring storm events.
  Science of the Total Environment, 360, 109-126.

CVc/CVq Framework
-----------------

Coefficient of Variation Approach (Musolff et al., 2015)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Distinguishes chemostatic from chemodynamic behavior using variability ratios:

.. math::

   \frac{CV_c}{CV_q} = \frac{\sigma_C / \mu_C}{\sigma_Q / \mu_Q}

**Interpretation:**

**CVc/CVq > 1** (Chemodynamic)
   Concentration varies more than flow. Indicates:
      - Variable source contributions
      - Transport-dependent export
      - Event-driven dynamics
      - Hysteretic behavior likely

**CVc/CVq < 1** (Chemostatic)
   Concentration buffered relative to flow. Indicates:
      - Consistent source strength
      - Concentration-discharge equilibrium
      - Hysteresis less pronounced
      - Stable biogeochemical processes

**Implementation in HyGCS:**

Computed on rolling windows (typically 5-10 samples) to capture temporal dynamics.

**Reference:**

Musolff, A. et al. (2015). Catchment controls on solute export.
Advances in Water Resources, 86, 133-146.

C-Q Relationships
-----------------

Power-Law Model (Thompson et al., 2011)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The C-Q relationship is commonly modeled as:

.. math::

   C = aQ^b

Taking logarithms:

.. math::

   \log(C) = \log(a) + b \cdot \log(Q)

where:
   - **a** = intercept (baseline concentration)
   - **b** = slope (mechanistic indicator)

**Slope Interpretation:**

**b > 0.15** (Dilution/Flushing)
   Concentration increases with flow. Indicates:
      - Transport-limited export
      - Flushing of accumulated material
      - Proximal sources activated
      - Increasing connectivity

**b < -0.15** (Enrichment/Loading)
   Concentration decreases with flow. Indicates:
      - Dilution of point sources
      - Source-limited export
      - Groundwater contribution dominant
      - Decreasing connectivity

**|b| < 0.1** (Chemostatic)
   Weak C-Q relationship. Indicates:
      - Buffered system
      - Consistent source strength
      - Concentration-discharge equilibrium
      - Weak flow dependency

**Reference:**

Thompson, S.E. et al. (2011). Comparative hydrology across AmeriFlux sites:
The variable roles of climate, vegetation, and groundwater.
Water Resources Research, 47(10).

Geochemical Phase Classification
---------------------------------

HyGCS implements a hierarchical 6-phase classification system developed by
Sanchez et al. (2025, in review) that integrates:

1. Window-scale hysteresis indices
2. C-Q slope (power-law exponent)
3. CVc/CVq variability ratios
4. Flow dynamics (rising/falling, peaks)
5. Temporal context (phase transitions)

The 6 Phases
~~~~~~~~~~~~

**F - Flushing**

Characteristics:
   - Steep concentration decline during high flow
   - Positive C-Q slope (b > 0.15)
   - High CVc/CVq (chemodynamic)
   - Clockwise hysteresis common
   - Concentration in high percentile, declining

Process interpretation:
   Rapid mobilization of accumulated material during high-flow events.
   Transport-limited export with strong connectivity.

**L - Loading**

Characteristics:
   - Concentration rising to maximum
   - Negative C-Q slope (b < -0.15)
   - Rising concentration trajectory
   - Counter-clockwise hysteresis possible
   - Concentration increasing with or before flow

Process interpretation:
   Accumulation phase with progressive source mobilization.
   Enrichment before peak flow arrival.

**C - Chemostatic**

Characteristics:
   - Low hysteresis magnitude
   - Flat C-Q slope (|b| < 0.1)
   - Low CVc/CVq (< 1)
   - Stable concentration
   - Low variability

Process interpretation:
   Buffered system with consistent source strength.
   Concentration-discharge equilibrium maintained.

**D - Dilution**

Characteristics:
   - Post-flush recovery
   - Declining flow
   - Declining concentration
   - Follows flushing phase
   - Medium to low connectivity

Process interpretation:
   Recovery after flushing event. Sources depleted,
   system returning to baseflow conditions.

**R - Recession**

Characteristics:
   - Late cycle, both flow and concentration declining
   - Low CVc/CVq
   - Low hysteresis
   - Days since peak > threshold
   - Low connectivity

Process interpretation:
   Baseflow-dominated conditions. Limited source availability
   and weak connectivity.

**V - Variable**

Characteristics:
   - Ambiguous patterns
   - Mixed signatures
   - Low confidence classification
   - Transitional behavior

Process interpretation:
   Complex or mixed processes not fitting other categories.
   May indicate multiple overlapping processes or
   insufficient data.

Percentile-Based Thresholds
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The classification uses percentile-based thresholds rather than absolute values,
making it compound-agnostic and adaptable to different concentration ranges.

**Advantages:**
   - Works across different compounds (metals, nutrients, etc.)
   - Adapts to site-specific conditions
   - Robust to concentration scale differences
   - Reduces need for parameter tuning

**Thresholds Computed:**
   - Flow percentiles (33rd, 67th for low/medium/high)
   - Concentration change percentiles (25th, 75th)
   - C-Q slope absolute thresholds (±0.15, ±0.1)
   - CVc/CVq ratio (typically 1.0 threshold)

Window-Scale Hysteresis
~~~~~~~~~~~~~~~~~~~~~~~

Unlike traditional event-scale hysteresis, HyGCS computes hysteresis indices
on moving windows (typically 10-20 points) around each classified segment.

**Why window-scale?**
   - Captures local temporal dynamics
   - Avoids artifacts from full time series loops
   - More appropriate for long-term monitoring data
   - Detects changing patterns over time

Hierarchical Rule System
~~~~~~~~~~~~~~~~~~~~~~~~~

Rules are checked in priority order to avoid ambiguity:

1. **Strong signatures** (F, L) - checked first
2. **Moderate signatures** (C, D, R) - checked next
3. **Default to V** if no clear pattern

Confidence scoring based on:
   - Number of rules triggered
   - Agreement between indicators (hysteresis, slope, CVc/CVq)
   - Data quality (sufficient points, valid metrics)
   - Consistency with temporal context (previous phases)

Critical Perspective
--------------------

Knapp & Musolff (2024) - Critical Assessment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Important considerations for C-Q analysis:

**Multi-Method Validation**
   No single method is perfect. Convergent evidence from multiple methods
   increases confidence. When methods disagree, investigate further.

**Contextual Interpretation**
   Hysteresis and C-Q slopes reveal patterns but not mechanisms directly.
   Must combine with:
      - Site knowledge (geology, land use, hydrology)
      - Process understanding (biogeochemistry, transport)
      - Additional data (tracers, high-frequency monitoring)

**Data Requirements**
   Quality and quantity of data matter:
      - Temporal resolution affects pattern detection
      - Sampling bias can create artifacts
      - Outliers and measurement errors propagate
      - Need adequate coverage of flow range

**Limitations of Classification**
   Automated classification is a tool, not truth:
      - Low confidence classifications need investigation
      - Phase boundaries are fuzzy, not discrete
      - Complex systems may not fit simple categories
      - Always validate against known reference periods

**Reference:**

Knapp, J.L.A. & Musolff, A. (2024). Mind the gap: A critical perspective
on concentration-discharge relationships. Hydrological Processes.
https://doi.org/10.1002/hyp.15328

Best Practices
--------------

1. **Use Multiple Methods**

   Always compare HARP, Zuecco, and Lloyd/Lawler results. Agreement → confidence.

2. **Validate with Known Events**

   Test on reference events with known behavior to calibrate interpretation.

3. **Check Data Quality**

   - Remove obvious outliers
   - Ensure Q and C are synchronized
   - Verify sufficient temporal coverage
   - Examine gaps and missing data

4. **Consider Temporal Context**

   - Seasonal patterns
   - Antecedent conditions
   - Long-term trends
   - Event sequencing

5. **Integrate Process Knowledge**

   - Site characteristics (geology, land use)
   - Known sources and pathways
   - Historical behavior
   - Expert knowledge

6. **Report Uncertainty**

   - Confidence scores
   - Method agreement/disagreement
   - Data limitations
   - Alternative interpretations

7. **Avoid Over-Interpretation**

   Hysteresis reveals patterns, not mechanisms directly.
   Use as hypothesis-generating tool, not definitive proof.

See Also
--------

- :doc:`api_core` - Implementation details
- :doc:`api_classification` - Classification algorithm
- :doc:`quickstart` - Practical usage examples
