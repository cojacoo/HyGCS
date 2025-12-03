"""
HYDRO-GEOCHEMICAL C-Q CLASSIFICATION SUITE
===========================================================
Toolbox for hysteresis analysis and geochemical phase classification
in concentration-discharge (C-Q) relationships for potential contaminants
in water systems.

(cc-by) Version 0.5 (2025-12-02) conrad.jackisch@tbt.tu-freiberg.de, antita.sanchez@mineral.tu-freiberg.de
"""

# =============================================================================
# IMPORTS FROM SUBMODULES
# =============================================================================

# Core metrics and preparatory functions
from gcs_core import (
    calculate_all_hysteresis_metrics,
    compute_cvc_cvq_windows,
    compute_cq_slope,
    analyze_segment_flow_dynamics,
    compute_change_percentiles
)

# Classification functions (MAIN API)
from gcs_classification import (
    classify_geochemical_phase,
    classify_segment_phase,
    classify_cq_behavior_simple
)

# Visualization
from gcs_visualization import (
    phase_colors,
    phase_names,
    hyphase_colors,
    get_line_style_from_hi_class,
    calculate_log_thickness,
    create_phase_sequence_plot,
    create_hysteresis_plot,
    create_multi_compound_hysteresis_plot,
    create_diagnostic_plot,
    create_hysteresis_timeline,
    create_hysteresis_summary_stats
)

# Individual hysteresis modules (for direct access if needed)
from harp import calculate_harp_metrics
from zuecco import calculate_zuecco_metrics
from lloyd import calculate_lawlerlloyd_metrics

# Re-export plotting from individual modules
from harp import harp_plot
from zuecco import zuecco_plot
from lloyd import lloyd_plot

# =============================================================================
# MODULE METADATA
# =============================================================================

__version__ = '0.5'
__date__ = '2025-12-02'
__authors__ = 'Conrad Jackisch, Anita Sanchez'
__email__ = 'conrad.jackisch@tbt.tu-freiberg.de'

__all__ = [
    # Main API
    'classify_geochemical_phase',
    # Core metrics and preparatory functions
    'calculate_all_hysteresis_metrics',
    'compute_cvc_cvq_windows',
    'compute_cq_slope',
    'analyze_segment_flow_dynamics',
    'compute_change_percentiles',
    # Classification functions
    'classify_segment_phase',
    'classify_cq_behavior_simple',
    # Visualization
    'phase_colors',
    'phase_names',
    'hyphase_colors',
    'get_line_style_from_hi_class',
    'calculate_log_thickness',
    'create_phase_sequence_plot',
    'create_hysteresis_plot',
    'create_multi_compound_hysteresis_plot',
    'create_diagnostic_plot',
    'create_hysteresis_timeline',
    'create_hysteresis_summary_stats',
    # Individual hysteresis methods
    'calculate_harp_metrics',
    'calculate_zuecco_metrics',
    'calculate_lawlerlloyd_metrics',
]

# =============================================================================
# WELCOME MESSAGE
# =============================================================================

print("=" * 70)
print("GCS v0.5 - Geochemical C-Q Classification Suite")
print("=" * 70)
print("USAGE: import gcs as gcs")
print("       classified = gcs.classify_geochemical_phase(data, sites, ...)")
print("=" * 70)
