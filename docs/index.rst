HyGCS - Hydro-Geochemical Classification Suite
================================================

**A comprehensive Python toolkit for hysteresis analysis and geochemical phase classification in concentration-discharge (C-Q) relationships.**

Version 0.5 (December 2025)

.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.8+

.. image:: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg
   :target: https://creativecommons.org/licenses/by/4.0/
   :alt: License: CC BY 4.0

Overview
--------

HyGCS provides tools for analyzing water quality dynamics in catchments, mine drainage systems, and environmental monitoring networks. The package integrates scientifically validated methods for:

- **Multi-method hysteresis analysis** (HARP, Zuecco, Lloyd/Lawler)
- **CVc/CVq variability analysis** (Musolff et al., 2015)
- **C-Q slope calculation** (power-law exponents)
- **Geochemical phase classification** (6-phase hierarchical system)
- **Comprehensive visualization tools**

Key Features
------------

**1. Multi-Method Hysteresis Analysis**

- **HARP** (Roberts et al., 2023) - Empirical classification based on peak timing and loop geometry
- **Zuecco Index** (Zuecco et al., 2016) - Integration-based index with 9-class classification
- **Lloyd/Lawler** (Lloyd et al., 2016) - Percentile-based indices with symmetric range

**2. Geochemical Phase Classification**

Six-phase hierarchical system:

- **F (Flushing)**: Dilution-dominated, steep C decline during high Q
- **L (Loading)**: Enrichment, C increase before peak Q
- **C (Chemostatic)**: Buffered, low variability, flat C-Q slope
- **D (Dilution)**: Post-flush recovery, declining flow
- **R (Recession)**: Late cycle, low connectivity
- **V (Variable)**: Ambiguous/mixed patterns

**3. Visualization**

- Phase sequence timelines
- C-Q hysteresis loops with phase coloring
- Diagnostic plots (CVc/CVq vs. C-Q slope)
- Multi-compound comparison plots

Quick Start
-----------

Single Event Hysteresis Analysis::

    import hygcs as gcs
    import pandas as pd

    # Load event data
    data = pd.read_csv('event_data.csv')

    # Calculate all hysteresis metrics
    metrics = gcs.calculate_all_hysteresis_metrics(
        data,
        time_col='datetime',
        discharge_col='Q',
        concentration_col='C'
    )

    print(f"HARP Area: {metrics['harp_metrics']['area']:.4f}")
    print(f"Zuecco h-index: {metrics['zuecco_metrics']['h_index']:.4f}")
    print(f"Lloyd HInew: {metrics['lloyd_metrics']['mean_HInew']:.4f}")

Time Series Classification::

    # Load monitoring time series
    pcd = pd.read_csv('monitoring_data.csv')
    pcd['date'] = pd.to_datetime(pcd['date'])

    # Run geochemical phase classification
    classified = gcs.classify_geochemical_phase(
        pcd,
        sites=['Site1', 'Site2'],
        ccol='PLI',
        qcol='Q_mLs',
        use_highres=False
    )

    # Visualize results
    fig = gcs.create_phase_sequence_plot(classified, sites=['Site1'])
    fig.show()

Documentation Contents
----------------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   installation
   quickstart
   examples
   scientific_background

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api_core
   api_classification
   api_visualization
   api_hysteresis

.. toctree::
   :maxdepth: 1
   :caption: Additional Information

   license
   citation
   changelog

Scientific Background
---------------------

Hysteresis Methods
~~~~~~~~~~~~~~~~~~

**HARP** (Roberts et al., 2023)
   Hysteresis Analysis of Rising and falling Peaks - Empirical classification based on peak timing and residuals.

**Zuecco Index** (Zuecco et al., 2016)
   Integration-based hysteresis index with 9-class classification system.

**Lloyd/Lawler Methods** (Lloyd et al., 2016; Lawler et al., 2006)
   Percentile-based approach. HInew (difference method) recommended for standard comparisons.

CVc/CVq Framework
~~~~~~~~~~~~~~~~~

**Musolff et al. (2015)** - Coefficient of variation approach:

- CVc/CVq > 1: Chemodynamic (variable C behavior)
- CVc/CVq < 1: Chemostatic (buffered C behavior)

C-Q Relationships
~~~~~~~~~~~~~~~~~

**Thompson et al. (2011)** - C-Q slope interpretation:

- b > 0: Dilution/flushing patterns
- b < 0: Enrichment/loading patterns
- b ≈ 0: Chemostatic buffering

Critical Perspective
~~~~~~~~~~~~~~~~~~~~

**Knapp & Musolff (2024)** - Critical assessment emphasizing multi-method validation and contextual interpretation.

Authors
-------

- **Conrad Jackisch** - conrad.jackisch@tbt.tu-freiberg.de
- **Anita Sanchez** - antita.sanchez@mineral.tu-freiberg.de

*TU Bergakademie Freiberg, Germany*

License
-------

CC-BY 4.0 - Creative Commons Attribution 4.0 International License

You are free to share and adapt this work with appropriate attribution.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
