# Getting Started with HyGCS

Welcome to the **Hydro-Geochemical Classification Suite**! This guide will get you up and running quickly.

---

## Installation

### Option 1: Install from source
```bash
git clone https://github.com/yourusername/HyGCS.git
cd HyGCS
pip install -e .
```

### Option 2: Install dependencies only
```bash
pip install -r requirements.txt
```

---

## Your First Analysis

### 1. Single Event Hysteresis

Perfect for analyzing individual storm events or flushing episodes:

```python
import hygcs as gcs
import pandas as pd

# Load your event data
# Needs: time column, discharge (Q), concentration (C)
data = pd.read_csv('storm_event.csv')

# Calculate all three hysteresis methods at once
metrics = gcs.calculate_all_hysteresis_metrics(
    data,
    time_col='datetime',
    discharge_col='Q_Ls',
    concentration_col='NO3_mgL'
)

# Extract results
print("HARP Area:", metrics['harp_metrics']['area'])
print("Zuecco Index:", metrics['zuecco_metrics']['h_index'])
print("Lloyd HInew:", metrics['lloyd_metrics']['mean_HInew'])
print("Direction:", metrics['classifications']['lloyd_direction'])
```

### 2. Visualize the Event

```python
from harp import calculate_harp_metrics, harp_plot
from zuecco import calculate_zuecco_metrics, zuecco_plot
from lloyd import calculate_lawlerlloyd_metrics, lloyd_plot

# Calculate with full output for plotting
harp_m, harp_df = calculate_harp_metrics(data, time_col='datetime',
                                          discharge_col='Q_Ls',
                                          concentration_col='NO3_mgL')

# Create plot
fig = harp_plot(harp_df, harp_m)
fig.show()
```

### 3. Time Series Classification

For long-term monitoring data with multiple cycles:

```python
# Load monitoring time series
pcd = pd.read_csv('monitoring_data.csv')
pcd['date'] = pd.to_datetime(pcd['date'])

# Classify geochemical phases
classified = gcs.classify_geochemical_phase(
    pcd,
    sites=['Site1', 'Site2', 'Site3'],
    ccol='PLI',        # Your concentration column
    qcol='Q_mLs',      # Your flow column
    use_highres=False  # Set True if you have hourly Q data
)

# View results
print(classified[['site_id', 'start_date', 'end_date',
                  'geochemical_phase', 'phase_confidence']].head(10))
```

### 4. Visualize Phase Sequence

```python
# Create phase timeline
fig = gcs.create_phase_sequence_plot(classified, sites=['Site1', 'Site2'])
fig.show()

# Create diagnostic plot
fig_diag = gcs.create_diagnostic_plot(classified)
fig_diag.show()
```

---

## Understanding the Output

### Hysteresis Metrics

**HARP** provides:
- `area`: Loop area (magnitude)
- `residual`: End-state deviation
- `peaktime_Q`, `peaktime_C`: Peak timings
- Interpretation: Compare peak timing for flushing vs. dilution

**Zuecco** provides:
- `h_index`: Integration-based index
- `hyst_class`: Classification (0-8)
  - 1-4: Clockwise variants
  - 5-8: Counter-clockwise variants
  - 0: Linear/no hysteresis

**Lloyd/Lawler** provides:
- `mean_HInew`: Recommended index (range: -1 to 1)
- `mean_HIL`: Original Lawler index
- Direction: clockwise, counter-clockwise, or weak

### Geochemical Phases

- **F (Flushing)**: Dilution during high flow, steep C decline
- **L (Loading)**: Enrichment, C increases with Q
- **C (Chemostatic)**: Buffered, low variability
- **D (Dilution)**: Post-flush recovery
- **R (Recession)**: Late cycle, declining
- **V (Variable)**: Mixed/ambiguous

### Classification Metrics

- `cq_slope_loglog`: Power-law exponent b
  - b > 0.15: Dilution (flushing)
  - b < -0.15: Enrichment (loading)
  - |b| < 0.1: Chemostatic

- `CVc_CVq`: Variability ratio
  - > 1: Chemodynamic
  - < 1: Chemostatic

- `phase_confidence`: 0-1 score
  - > 0.9: High confidence
  - 0.7-0.9: Moderate
  - < 0.7: Low (investigate further)

---

## Data Requirements

### For Single Event Analysis:
- **Minimum**: 10-15 paired Q and C measurements during event
- **Ideal**: 20-30 points capturing full rising/falling limbs
- **Format**: Time series (datetime, Q, C)

### For Time Series Classification:
- **Minimum**: 20-30 sampling points per site
- **Ideal**: 50+ points covering multiple hydrological cycles
- **Format**: DataFrame with `site_id`, `date`, Q column, C column
- **Optional**: High-resolution (hourly) Q data for improved accuracy

---

## Common Workflows

### Workflow 1: Compare Multiple Events

```python
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
```

### Workflow 2: Multi-Site Classification

```python
# Classify all sites
classified = gcs.classify_geochemical_phase(pcd, sites=all_sites, ...)

# Get summary statistics per site
stats = gcs.create_hysteresis_summary_stats(
    classified,
    sites=all_sites,
    ccol='PLI',
    hi_method='zuecco'
)

print(stats[['site_id', 'phase_name', 'percentage', 'mean_duration_days']])
```

### Workflow 3: Multi-Compound Analysis

```python
# Compare hysteresis for different compounds
fig = gcs.create_multi_compound_hysteresis_plot(
    pcd,
    Qx,  # High-res Q data
    sites=['Site1'],
    ccols=['PLI', 'Ni', 'Zn'],
    compounds=['PLI', 'Ni', 'Zn'],
    conc_units=['µg/L', 'µg/L', 'µg/L'],
    qcol='Q_mLs'
)
fig.show()
```

---

## Tips & Best Practices

### 1. **Always Compare Multiple Methods**
- When all three agree → High confidence
- When they disagree → Complex pattern, investigate further

### 2. **Validate with Known Events**
- Test on reference events with known behavior
- Calibrate interpretation to your system

### 3. **Check Data Quality**
- Remove obvious outliers
- Ensure Q and C are properly synchronized
- Verify no NaN/missing values in critical periods

### 4. **Consider Context**
- Hysteresis alone doesn't explain mechanisms
- Combine with site knowledge, geology, hydrology
- Use C-Q slopes for mechanistic insights

### 5. **Use Confidence Scores**
- Low confidence → Need more data or ambiguous pattern
- High confidence → Classification is robust

---

## Troubleshooting

### "Not enough data points"
→ Need at least 5 points for hysteresis calculation, 10+ recommended

### "All NaN results"
→ Check column names match, data types are numeric, no missing values

### "Classification seems wrong"
→ Check input data quality, verify time series continuity, examine diagnostic plots

### "Import errors"
→ Clear Python cache: `rm -rf __pycache__/*.pyc` and reimport

---

## Next Steps

1. **Run Examples**:
   ```bash
   jupyter notebook examples/demo_comprehensive_hysteresis_analysis.ipynb
   jupyter notebook examples/test_gcs.ipynb
   ```

2. **Read Documentation**:
   - [API Reference](docs/API_REFERENCE.md) - Function details
   - [Restructuring Notes](docs/RESTRUCTURING_v0.5.md) - Version history

3. **Explore Methods**:
   - Try all three hysteresis methods on same data
   - Compare results for convergent evidence
   - Use diagnostic plots to validate classification

---

## Getting Help

- **Examples**: Check `examples/` directory
- **Issues**: [GitHub Issues](https://github.com/yourusername/HyGCS/issues)
- **Email**: conrad.jackisch@tbt.tu-freiberg.de

---

Happy analyzing! 🎉
