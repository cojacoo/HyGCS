Visualization Functions
=======================

The ``gcs_visualization`` module provides plotting functions for classification results,
hysteresis loops, diagnostic plots, and phase sequences.

.. currentmodule:: hygcs.gcs_visualization

Phase Visualization
-------------------

.. autofunction:: create_phase_sequence_plot

   Create timeline showing geochemical phase sequence for one or more sites.

   Displays phases as colored horizontal bars over time, allowing visual inspection
   of temporal patterns and inter-site comparison.

.. autofunction:: create_diagnostic_plot

   Create diagnostic scatter plot in CVc/CVq vs. C-Q slope space.

   Points colored by geochemical phase, helps validate classification logic
   and identify phase clustering in mechanistic space.

Hysteresis Visualization
-------------------------

.. autofunction:: create_hysteresis_plot

   Create C-Q hysteresis loops for classified segments.

   Plots concentration vs. discharge with:
      - Phase-based coloring
      - Hysteresis index-based line thickness
      - Time-based point coloring
      - Load-informed point sizing (optional)

.. autofunction:: create_multi_compound_hysteresis_plot

   Create multi-panel hysteresis comparison across compounds and sites.

   Useful for comparing hysteresis patterns between different analytes
   (e.g., metals, nutrients) at the same sites.

.. autofunction:: create_hysteresis_timeline

   Create timeline visualization of hysteresis indices over time.

   Shows temporal evolution of HARP, Zuecco, or Lloyd indices alongside
   flow and concentration data.

Summary Statistics
------------------

.. autofunction:: create_hysteresis_summary_stats

   Generate summary statistics table for classified data.

   Returns DataFrame with:
      - Phase percentages by site
      - Mean hysteresis indices per phase
      - Phase duration statistics
      - Transition frequencies

Style and Color Functions
--------------------------

.. autofunction:: get_line_style_from_hi_class

   Get Plotly line style string based on hysteresis index and classification.

   Used internally to style hysteresis loop plots based on direction and magnitude.

.. autofunction:: calculate_log_thickness

   Calculate log-normalized line thickness for visualization.

   Converts hysteresis index magnitudes to appropriate line widths for plotting.

Color Schemes
-------------

.. py:data:: phase_colors

   Dictionary mapping geochemical phase codes to colors::

      {
          'F': '#E69F00',  # Flushing - orange
          'L': '#56B4E9',  # Loading - sky blue
          'C': '#009E73',  # Chemostatic - green
          'D': '#F0E442',  # Dilution - yellow
          'R': '#0072B2',  # Recession - blue
          'V': '#D55E00'   # Variable - red-orange
      }

.. py:data:: phase_names

   Dictionary mapping phase codes to descriptive names::

      {
          'F': 'Flushing',
          'L': 'Loading',
          'C': 'Chemostatic',
          'D': 'Dilution',
          'R': 'Recession',
          'V': 'Variable'
      }

.. py:data:: hyphase_colors

   Alternative color scheme for hydrological phases (if used).

Usage Examples
--------------

Phase Sequence Plot::

    import hygcs as gcs

    # After classification
    classified = gcs.classify_geochemical_phase(pcd, sites=['Site1', 'Site2'], ...)

    # Create phase timeline
    fig = gcs.create_phase_sequence_plot(classified, sites=['Site1', 'Site2'])
    fig.update_xaxes(range=['2020-01-01', '2022-12-31'])
    fig.show()

Diagnostic Plot::

    # CVc/CVq vs C-Q slope space
    fig_diag = gcs.create_diagnostic_plot(classified)
    fig_diag.show()

Hysteresis Plot::

    fig_hyst = gcs.create_hysteresis_plot(
        classified,
        sites=['Site1'],
        ccol='PLI',
        qcol='Q_mLs',
        compound='PLI',
        conc_unit='µg/L'
    )
    fig_hyst.show()

Multi-Compound Comparison::

    fig = gcs.create_multi_compound_hysteresis_plot(
        pcd, Qx,
        sites=['Site1', 'Site2'],
        ccols=['Cd_mgL', 'Zn_mgL', 'Fe_mgL'],
        compounds=['Cd', 'Zn', 'Fe'],
        conc_units=['mg/L', 'mg/L', 'mg/L'],
        qcol='Q_mLs',
        flow_unit='mL/s',
        hi_method='zuecco'
    )
    fig.show()

Summary Statistics::

    stats = gcs.create_hysteresis_summary_stats(
        classified,
        sites=['Site1', 'Site2', 'Site3'],
        ccol='PLI',
        hi_method='zuecco'
    )
    print(stats[['site_id', 'phase_name', 'percentage',
                 'mean_duration_days']])

Customization
-------------

All plotting functions return Plotly Figure objects that can be customized::

    fig = gcs.create_phase_sequence_plot(classified, sites=['Site1'])

    # Update layout
    fig.update_layout(
        template='plotly_white',
        title='Geochemical Phase Evolution',
        height=400
    )

    # Update axes
    fig.update_xaxes(title='Time')
    fig.update_yaxes(title='Site')

    # Save figure
    fig.write_html('phase_sequence.html')
    fig.write_image('phase_sequence.pdf', width=1200, height=400)

Notes
-----

**Plotly Rendering**

All visualizations use Plotly for interactive plotting. Figures can be:
   - Displayed interactively in Jupyter notebooks
   - Saved as HTML for sharing
   - Exported as static images (requires kaleido: ``pip install kaleido``)

**Color Accessibility**

Color schemes are chosen to be distinguishable for most types of color vision deficiency.
For publications, consider using shape/pattern variations in addition to color.

See Also
--------

- :doc:`api_classification` - Classification functions that generate data for visualization
- :doc:`quickstart` - Basic visualization examples
- :doc:`examples` - Advanced visualization tutorials
