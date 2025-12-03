# HyGCS - Hydro-Geochemical Classification Suite

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

**A comprehensive Python toolkit for hysteresis analysis and geochemical phase classification in concentration-discharge (C-Q) relationships.**

> *Developed for analyzing water quality dynamics in catchments, mine drainage systems, and environmental monitoring networks.*

---

## 🎯 Key Features

### 1. **Multi-Method Hysteresis Analysis**
- **HARP** (Roberts et al., 2023) - Empirical classification based on peak timing and loop geometry
- **Zuecco Index** (Zuecco et al., 2016) - Integration-based index with 9-class classification
- **Lloyd/Lawler** (Lloyd et al., 2016) - Percentile-based indices with symmetric range

### 2. **CVc/CVq Variability Analysis**
- Coefficient of variation ratios (Musolff et al., 2015)
- Chemostatic vs. chemodynamic behavior detection
- Rolling window analysis for temporal dynamics

### 3. **C-Q Slope Analysis**
- Power-law exponent calculation (C = aQ^b)
- Log-log regression for mechanistic interpretation
- Connectivity and transport process identification

### 4. **Geochemical Phase Classification**
- **6-phase hierarchical classification system:**
  - **F (Flushing)**: Dilution-dominated, steep C decline during high Q
  - **L (Loading)**: Enrichment, C increase before peak Q
  - **C (Chemostatic)**: Buffered, low variability, flat C-Q slope
  - **D (Dilution)**: Post-flush recovery, declining flow
  - **R (Recession)**: Late cycle, low connectivity
  - **V (Variable)**: Ambiguous/mixed patterns
- Window-scale hysteresis integration
- Confidence scoring and diagnostic rules

### 5. **Comprehensive Visualization**
- Phase sequence timelines
- C-Q hysteresis loops with phase coloring
- Diagnostic plots (CVc/CVq vs. C-Q slope)
- Multi-compound comparison plots
- Load-informed data point sizing

---

## 📦 Installation

### From Source
```bash
git clone https://github.com/yourusername/HyGCS.git
cd HyGCS
pip install -e .
```

### Requirements
- Python >= 3.8
- pandas >= 1.3.0
- numpy >= 1.20.0
- scipy >= 1.7.0
- plotly >= 5.0.0
- scikit-learn >= 0.24.0

---

## 🚀 Quick Start

### Single Event Hysteresis Analysis

```python
import hygcs as gcs
import pandas as pd

# Load event data (Q and C time series for one storm/flush)
data = pd.read_csv('event_data.csv')

# Calculate all hysteresis metrics
metrics = gcs.calculate_all_hysteresis_metrics(
    data,
    time_col='datetime',
    discharge_col='Q',
    concentration_col='C'
)

# Extract results
harp = metrics['harp_metrics']
zuecco = metrics['zuecco_metrics']
lloyd = metrics['lloyd_metrics']

print(f"HARP Area: {harp['area']:.4f}")
print(f"Zuecco h-index: {zuecco['h_index']:.4f}")
print(f"Lloyd HInew: {lloyd['mean_HInew']:.4f}")
```

### Time Series Classification

```python
# Load monitoring time series (multiple cycles)
pcd = pd.read_csv('monitoring_data.csv')
pcd['date'] = pd.to_datetime(pcd['date'])

# Optional: Load high-resolution flow data
Qx = pd.read_csv('flow_hourly.csv', index_col=0, parse_dates=True)

# Run geochemical phase classification
classified = gcs.classify_geochemical_phase(
    pcd,
    sites=['Site1', 'Site2', 'Site3'],
    flow_highres=Qx,  # Optional but improves accuracy
    ccol='PLI',       # Concentration column
    qcol='Q_mLs',     # Flow column
    use_highres=True
)

# Visualize phase sequence
fig = gcs.create_phase_sequence_plot(classified, sites=['Site1', 'Site2'])
fig.show()

# Create diagnostic plot
fig_diag = gcs.create_diagnostic_plot(classified)
fig_diag.show()
```

### CVc/CVq Analysis

```python
# Compute rolling CVc/CVq windows
cvc_cvq = gcs.compute_cvc_cvq_windows(
    pcd,
    qcol='Q_mLs',
    ccol='PLI',
    window=5  # Number of samples per window
)

# Analyze chemostatic vs chemodynamic behavior
print(cvc_cvq[['site_id', 'end_date', 'CVc_CVq', 'cq_slope_loglog']].head())
```

---

## 📊 Example Outputs

### Hysteresis Loop Classification
![Hysteresis example](docs/figures/hysteresis_example.png)

### Phase Sequence Timeline
![Phase sequence](docs/figures/phase_sequence.png)

### Diagnostic Space
![Diagnostic plot](docs/figures/diagnostic_space.png)

---

## 📚 Documentation

- **[User Guide](docs/USER_GUIDE.md)** - Comprehensive usage instructions
- **[API Reference](docs/API_REFERENCE.md)** - Function documentation
- **[Examples](examples/)** - Jupyter notebooks with tutorials
- **[Restructuring Notes](docs/RESTRUCTURING_v0.5.md)** - v0.5 changes

---

## 🧪 Testing

Run the test suite:
```bash
cd tests/
python test_imports_v05.py
```

Run example notebooks:
```bash
jupyter notebook examples/demo_comprehensive_hysteresis_analysis.ipynb
jupyter notebook examples/test_gcs.ipynb
```

---

## 📖 Scientific Background

### Hysteresis Methods

1. **HARP** (Roberts et al., 2023)
   - *Hysteresis Analysis of Rising and falling Peaks*
   - Empirical classification based on peak timing and residuals
   - Reference: Roberts, M.E. et al. (2023), Hydrological Processes

2. **Zuecco Index** (Zuecco et al., 2016)
   - Integration-based hysteresis index
   - 9-class classification system
   - Reference: Zuecco, G. et al. (2016), Journal of Hydrology

3. **Lloyd/Lawler Methods** (Lloyd et al., 2016; Lawler et al., 2006)
   - Percentile-based approach
   - HInew recommended for standard comparisons
   - References:
     - Lloyd, C.E.M. et al. (2016), Hydrology and Earth System Sciences
     - Lawler, D.M. et al. (2006), Science of the Total Environment

### CVc/CVq Framework

- **Musolff et al. (2015)** - Coefficient of variation approach
  - CVc/CVq > 1: Chemodynamic (variable C behavior)
  - CVc/CVq < 1: Chemostatic (buffered C behavior)
  - Reference: Musolff, A. et al. (2015), Advances in Water Resources

### C-Q Relationships

- **Thompson et al. (2011)** - C-Q slope interpretation
  - b > 0: Dilution/flushing patterns
  - b < 0: Enrichment/loading patterns
  - b ≈ 0: Chemostatic buffering

### Critical Perspective

- **Knapp & Musolff (2024)** - Critical assessment of C-Q analysis
  - Importance of multi-method validation
  - Contextual interpretation required
  - Reference: Knapp, J.L.A. & Musolff, A. (2024), Hydrological Processes

---

## 🔬 Use Cases

- **Mine Drainage Monitoring** - Classification of geochemical phases in legacy mine systems
- **Catchment Hydrology** - Understanding nutrient and contaminant dynamics
- **Water Quality Assessment** - Long-term monitoring data analysis
- **Storm Event Analysis** - Single-event hysteresis characterization
- **Comparative Studies** - Multi-site or multi-compound analysis

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

**CC-BY 4.0** - This work is licensed under a Creative Commons Attribution 4.0 International License.

You are free to:
- **Share** - Copy and redistribute the material
- **Adapt** - Remix, transform, and build upon the material

Under the following terms:
- **Attribution** - Give appropriate credit, provide a link to the license

---

## ✍️ Authors

- **Conrad Jackisch** - conrad.jackisch@tbt.tu-freiberg.de
- **Anita Sanchez** - antita.sanchez@mineral.tu-freiberg.de

*TU Bergakademie Freiberg, Germany*

---

## 📝 Citation

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

## 🙏 Acknowledgments

This package integrates and extends methods from:
- [HARP R package](https://github.com/MelanieEmmajade/HARP) by Melanie Roberts
- [Hysteresis-Index-Zuecco](https://github.com/florianjehn/Hysteresis-Index-Zuecco) by Florian Jehn

Built with support from the mine drainage monitoring network at TU Bergakademie Freiberg.

---

## ⚠️ Disclaimer

This code is scientific and experimental. **Do not trust results without thorough validation.**

The package contains assumptions (e.g., time series in days, spline interpolations) that may not suit all use cases. Always:
- Validate against known reference events
- Compare multiple methods for convergent evidence
- Understand your data characteristics before interpretation
- Consider site-specific context

**When methods disagree → investigate further!**

---

## 📧 Contact

For questions, issues, or collaboration:
- **Email**: conrad.jackisch@tbt.tu-freiberg.de
- **Issues**: [GitHub Issues](https://github.com/yourusername/HyGCS/issues)

---

*Version 0.5 - December 2025*
