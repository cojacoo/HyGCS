# HyGCS - Hydro-Geochemical Classification Suite

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Documentation Status](https://readthedocs.org/projects/hygcs/badge/?version=latest)](https://hygcs.readthedocs.io/en/latest/?badge=latest)

A comprehensive Python toolkit for hysteresis analysis and geochemical phase classification in concentration-discharge (C-Q) relationships.

Developed for analyzing water quality dynamics in catchments, mine drainage systems, and environmental monitoring networks.

---

## Key Features

**Multi-Method Hysteresis Analysis**
- HARP (Roberts et al., 2023) - Empirical classification based on peak timing and loop geometry
- Zuecco Index (Zuecco et al., 2016) - Integration-based index with 9-class classification
- Lloyd/Lawler (Lloyd et al., 2016) - Percentile-based indices with symmetric range

**CVc/CVq Variability Analysis**
- Coefficient of variation ratios (Musolff et al., 2015)
- Chemostatic vs. chemodynamic behavior detection
- Rolling window analysis for temporal dynamics

**C-Q Slope Analysis**
- Power-law exponent calculation (C = aQ^b)
- Log-log regression for mechanistic interpretation
- Connectivity and transport process identification

**Geochemical Phase Classification**

6-phase hierarchical classification system:
- F (Flushing): Dilution-dominated, steep C decline during high Q
- L (Loading): Enrichment, C increase before peak Q
- C (Chemostatic): Buffered, low variability, flat C-Q slope
- D (Dilution): Post-flush recovery, declining flow
- R (Recession): Late cycle, low connectivity
- V (Variable): Ambiguous/mixed patterns

**Comprehensive Visualization**
- Phase sequence timelines
- C-Q hysteresis loops with phase coloring
- Diagnostic plots (CVc/CVq vs. C-Q slope)
- Multi-compound comparison plots

---

## Installation

```bash
git clone https://github.com/yourusername/HyGCS.git
cd HyGCS
pip install -e .
```

Requirements: Python >= 3.8, pandas, numpy, scipy, plotly, scikit-learn, statsmodels

---

## Quick Start

### Single Event Hysteresis Analysis

```python
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
```

### Time Series Classification

```python
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
```

---

## Package Structure

```
HyGCS/
├── hygcs/                    # Main package
│   ├── gcs.py               # Main entry point
│   ├── gcs_core.py          # Core analysis functions
│   ├── gcs_classification.py # Phase classification
│   ├── gcs_visualization.py  # Plotting functions
│   ├── harp.py              # HARP method
│   ├── zuecco.py            # Zuecco method
│   └── lloyd.py             # Lloyd/Lawler method
├── examples/                # Demo notebooks and test data
├── docs/                    # Documentation source
├── README.md
├── GETTING_STARTED.md
└── setup.py
```

---

## Documentation

Full documentation is available at: **https://hygcs.readthedocs.io/**

- Installation guide
- Quick start tutorial
- API reference
- Scientific background
- Example notebooks
- Citation information

---

## Scientific Background

**Hysteresis Methods**

- HARP (Roberts et al., 2023) - Empirical classification based on peak timing
- Zuecco Index (Zuecco et al., 2016) - Integration-based index with 9-class system
- Lloyd/Lawler (Lloyd et al., 2016; Lawler et al., 2006) - Percentile-based indices

**CVc/CVq Framework**

- Musolff et al. (2015) - Coefficient of variation approach
- CVc/CVq > 1: Chemodynamic; CVc/CVq < 1: Chemostatic

**C-Q Relationships**

- Thompson et al. (2011) - Power-law exponent interpretation
- b > 0: Dilution/flushing; b < 0: Enrichment/loading; b ≈ 0: Chemostatic

**Critical Perspective**

- Knapp & Musolff (2024) - Multi-method validation and contextual interpretation required

---

## License

This work is licensed under a Creative Commons Attribution 4.0 International License (CC-BY 4.0).

You are free to share and adapt this work with appropriate attribution.

---

## Authors

- Conrad Jackisch - conrad.jackisch@tbt.tu-freiberg.de
- Anita Sanchez - antita.sanchez@mineral.tu-freiberg.de

TU Bergakademie Freiberg, Interdisciplinary Environmental Research Centre, Germany

*Parts of the code have been interactively checked and amended by using Claude Code Sonnet 4.5*

---

## Citation

If you use HyGCS in your research, please cite:

```bibtex
@software{hygcs2025,
  author = {Jackisch, Conrad and Sanchez, Anita},
  title = {HyGCS: Hydro-Geochemical Classification Suite},
  year = {2025},
  version = {0.5},
  url = {https://github.com/yourusername/HyGCS}
}
```

And the relevant methodology papers:
- Roberts, M.E. et al. (2023) - HARP method
- Zuecco, G. et al. (2016) - Zuecco index
- Lloyd, C.E.M. et al. (2016) - Lloyd/Lawler indices
- Musolff, A. et al. (2015) - CVc/CVq framework

---

## Acknowledgments

This package integrates and extends methods from:
- [HARP R package](https://github.com/MelanieEmmajade/HARP) by Melanie Roberts
- [Hysteresis-Index-Zuecco](https://github.com/florianjehn/Hysteresis-Index-Zuecco) by Florian Jehn

Built with support from the mine drainage monitoring network at TU Bergakademie Freiberg.

---

## Disclaimer

This code is scientific and experimental. Do not trust results without thorough validation.

The package contains assumptions (e.g., time series in days, spline interpolations) that may not suit all use cases. Always validate against known reference events, compare multiple methods for convergent evidence, and consider site-specific context.

When methods disagree, investigate further.

---

## Contact

For questions, issues, or collaboration:
- Email: conrad.jackisch@tbt.tu-freiberg.de
- Issues: [GitHub Issues](https://github.com/cojacoo/HyGCS/issues)

---

*Version 0.5 - December 2025*
