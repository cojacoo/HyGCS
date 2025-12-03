# HyGCS Package Contents

## 📦 Repository Structure

```
HyGCS/
├── hygcs/                          # Main Python package
│   ├── __init__.py                 # Package initialization
│   ├── gcs_v5.py                   # Main module entry point
│   ├── gcs_core.py                 # Core metrics & preparatory functions
│   ├── gcs_classification.py       # Phase classification system
│   ├── gcs_visualization.py        # Plotting functions
│   ├── harp.py                     # HARP hysteresis method
│   ├── zuecco.py                   # Zuecco hysteresis method
│   └── lloyd.py                    # Lloyd/Lawler hysteresis method
│
├── examples/                       # Jupyter notebook tutorials
│   ├── demo_comprehensive_hysteresis_analysis.ipynb  # HARP/Zuecco/Lloyd/CVc-CVq demo
│   └── test_gcs.ipynb             # GCS classification demo (with real data)
│
├── tests/                          # Testing suite
│   └── test_imports_v05.py        # Import coherency test
│
├── docs/                           # Documentation
│   ├── RESTRUCTURING_v0.5.md      # Version 0.5 changes
│   ├── VISUALIZATION_LINE_STYLE_UPDATE.md  # Visualization improvements
│   └── IMPORT_FIX.md              # Troubleshooting guide
│
├── README.md                       # Main documentation
├── GETTING_STARTED.md             # Quick start guide
├── LICENSE                         # CC-BY 4.0 license
├── setup.py                        # Package installation script
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
└── PACKAGE_CONTENTS.md            # This file
```

---

## 🔧 Core Package Components

### `hygcs/gcs_v5.py` - Main Module
- Package entry point
- Re-exports all public functions
- Version metadata

### `hygcs/gcs_core.py` - Core Functions (5 functions)
- `calculate_all_hysteresis_metrics()` - Orchestrates HARP/Zuecco/Lloyd
- `compute_cvc_cvq_windows()` - Rolling CVc/CVq analysis
- `compute_cq_slope()` - Point-to-point C-Q slope
- `analyze_segment_flow_dynamics()` - High-res Q analysis
- `compute_change_percentiles()` - Statistical thresholds

### `hygcs/gcs_classification.py` - Classification (3 functions)
- `classify_geochemical_phase()` - Main time series classifier (MAIN API)
- `classify_segment_phase()` - Single segment classification
- `classify_cq_behavior_simple()` - Williams (1989) simple classifier

### `hygcs/gcs_visualization.py` - Plotting (7 functions)
- `create_phase_sequence_plot()` - Phase timeline
- `create_hysteresis_plot()` - C-Q loops with phase colors
- `create_multi_compound_hysteresis_plot()` - Multi-compound comparison
- `create_diagnostic_plot()` - CVc/CVq vs C-Q slope space
- `create_hysteresis_timeline()` - HI-based timeline
- `create_hysteresis_summary_stats()` - Statistical summary
- Helper functions: `get_line_style_from_hi_class()`, `calculate_log_thickness()`
- Color schemes: `phase_colors`, `hyphase_colors`, `phase_names`

### `hygcs/harp.py` - HARP Method
- `calculate_harp_metrics()` - HARP hysteresis index
- `harp_plot()` - Visualization

### `hygcs/zuecco.py` - Zuecco Method
- `calculate_zuecco_metrics()` - Zuecco hysteresis index
- `zuecco_plot()` - Visualization

### `hygcs/lloyd.py` - Lloyd/Lawler Method
- `calculate_lawlerlloyd_metrics()` - Lloyd/Lawler indices
- `lloyd_plot()` - Visualization

---

## 📚 Documentation Files

### Main Documentation
- **README.md** - Complete package overview, installation, usage examples
- **GETTING_STARTED.md** - Quick start guide for new users
- **LICENSE** - CC-BY 4.0 International License

### Technical Documentation (`docs/`)
- **RESTRUCTURING_v0.5.md** - Package reorganization from v4 to v0.5
  - Eliminated `gcs_analysis.py`
  - Function renaming for clarity
  - Moved classification functions
  - Warning suppression added

- **VISUALIZATION_LINE_STYLE_UPDATE.md** - Classifier-based line styles
  - HI-based dash patterns (solid/dashed/dotted)
  - Method-specific rules (Zuecco/Lloyd/HARP)
  - Fixes for thickness and style issues

- **IMPORT_FIX.md** - Troubleshooting import errors
  - Python cache issues
  - Solutions for `cannot import` errors

---

## 🧪 Examples & Tests

### Examples (`examples/`)

1. **demo_comprehensive_hysteresis_analysis.ipynb**
   - Comprehensive demo of HARP, Zuecco, Lloyd methods
   - Event-scale hysteresis analysis
   - CVc/CVq variability analysis (Musolff framework)
   - Comparative analysis across multiple datasets
   - **Focus**: Single-event and CVc/CVq analysis

2. **test_gcs.ipynb**
   - Real-world classification example
   - Multi-site, multi-compound analysis
   - Phase sequence visualization
   - Diagnostic plots
   - **Focus**: GCS time series classification

### Tests (`tests/`)

1. **test_imports_v05.py**
   - Comprehensive import coherency test
   - Verifies all 8 test categories:
     - Main module import
     - Core functions (5)
     - Classification functions (3)
     - Visualization functions (4+)
     - Hysteresis methods (3)
     - Direct submodule imports
     - Old function names removed
     - Version check

---

## 🔬 Scientific Methods Implemented

### Hysteresis Analysis
1. **HARP** (Roberts et al., 2023)
   - Peak timing analysis
   - Empirical classification
   - 10 hysteresis classes

2. **Zuecco Index** (Zuecco et al., 2016)
   - Integration-based approach
   - 9 hysteresis classes (0-8)
   - Quantitative magnitude

3. **Lloyd/Lawler** (Lloyd et al., 2016; Lawler et al., 2006)
   - Percentile-based indices
   - HInew (difference method, recommended)
   - HIL (ratio method, original)

### C-Q Analysis
1. **CVc/CVq Framework** (Musolff et al., 2015)
   - Chemostatic vs. chemodynamic classification
   - Rolling window analysis

2. **C-Q Slopes** (Thompson et al., 2011)
   - Power-law exponents
   - Mechanistic interpretation

### Geochemical Classification
1. **GCS 6-Phase System** (Sanchez et al., 2025, in review)
   - Hierarchical rule-based classification
   - Window-scale hysteresis integration
   - C-Q slope integration
   - Percentile-based thresholds

---

## 📋 Dependencies

### Core Requirements
- pandas >= 1.3.0
- numpy >= 1.20.0
- scipy >= 1.7.0
- plotly >= 5.0.0
- scikit-learn >= 0.24.0

### Optional (for examples)
- jupyter >= 1.0.0
- notebook >= 6.4.0
- ipywidgets >= 7.6.0
- openpyxl >= 3.0.0

---

## 📊 Data Format Requirements

### Single Event Analysis
```
Required columns:
- time_col: datetime or numeric (days)
- discharge_col: numeric (Q)
- concentration_col: numeric (C)

Minimum: 10-15 points
Recommended: 20-30 points
```

### Time Series Classification
```
Required columns:
- site_id: string (monitoring site identifier)
- date: datetime
- qcol: numeric (flow/discharge)
- ccol: numeric (concentration)

Optional:
- High-resolution Q data (hourly, separate DataFrame)
- HydPhase: string (hydrological phase labels)

Minimum: 20-30 points per site
Recommended: 50+ points covering multiple cycles
```

---

## 🎯 Use Cases

1. **Mine Drainage Monitoring**
   - Legacy mine water quality analysis
   - Multi-site geochemical phase classification
   - Long-term trend analysis

2. **Catchment Hydrology**
   - Nutrient export dynamics
   - Storm event hysteresis
   - Seasonal pattern analysis

3. **Water Quality Assessment**
   - Regulatory compliance monitoring
   - Source apportionment studies
   - Transport mechanism identification

4. **Comparative Studies**
   - Multi-site comparisons
   - Multi-compound comparisons
   - Method validation studies

---

## 🔄 Version History

### v0.5 (December 2025) - Current
- Package restructuring for maintainability
- Eliminated `gcs_analysis.py` (merged into `gcs_core.py`)
- Function renaming for clarity
- Classifier-based visualization line styles
- Warning suppression
- Comprehensive documentation
- GitHub-ready repository structure

### v4.0 (Previous)
- Monolithic structure
- Event-scale hysteresis duplication bug
- Lloyd NaN bug
- Less organized documentation

---

## 📝 Citation

```bibtex
@software{hygcs2025,
  author = {Jackisch, Conrad and Sanchez, Anita},
  title = {HyGCS: Hydro-Geochemical Classification Suite},
  year = {2025},
  version = {0.5},
  url = {https://github.com/yourusername/HyGCS}
}
```

---

## 👥 Contributors

- **Conrad Jackisch** - conrad.jackisch@tbt.tu-freiberg.de
- **Anita Sanchez** - antita.sanchez@mineral.tu-freiberg.de

*TU Bergakademie Freiberg, Germany*

---

## 📧 Support

- **Issues**: GitHub Issues
- **Email**: conrad.jackisch@tbt.tu-freiberg.de
- **Documentation**: See `docs/` directory and `GETTING_STARTED.md`

---

*Last updated: December 2025*
