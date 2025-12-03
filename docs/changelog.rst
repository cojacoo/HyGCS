Changelog
=========

Version 0.5 (December 2025)
---------------------------

**Major Restructuring Release**

Package Organization
~~~~~~~~~~~~~~~~~~~~

- **Eliminated** ``gcs_analysis.py`` - functions merged into ``gcs_core.py``
- **Renamed** ``gcs_v5.py`` → ``gcs.py`` for cleaner imports
- **Reorganized** classification functions into dedicated module
- **Moved** ``classify_cq_behavior_simple()`` from core to classification module
- **Improved** module coherence and logical organization

Function Changes
~~~~~~~~~~~~~~~~

**Renamed Functions:**

- ``classify_with_highres_logic()`` → ``classify_segment_phase()``
- More descriptive, clearer purpose

**New Functions:**

- ``calculate_log_thickness()`` - Log-normalized line thickness for hysteresis plots
- ``get_line_style_from_hi_class()`` - Method-specific line styling

**Improved Functions:**

- ``calculate_all_hysteresis_metrics()`` - Now returns comprehensive dictionary
- ``compute_cvc_cvq_windows()`` - Added window size parameter
- All visualization functions updated with improved styling

Bug Fixes
~~~~~~~~~

**Critical:**

- Fixed Lloyd/Lawler NaN bug in percentile sampling
- Fixed event-scale hysteresis duplication in window analysis
- Resolved import coherency issues

**Minor:**

- Suppressed Lloyd/Lawler "Mean of empty slice" warnings
- Fixed thickness calculation in hysteresis plots
- Corrected line style assignment logic for different HI classifiers

Visualization Improvements
~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Classifier-based line styles** - Different patterns for HARP/Zuecco/Lloyd
- **Log thickness scaling** - Better visual representation of HI magnitudes
- **Phase color consistency** - Unified color scheme across all plots
- **Improved legends** - Clearer labels and better organization

Documentation
~~~~~~~~~~~~~

- Added comprehensive README.md
- Created GETTING_STARTED.md quick start guide
- Detailed PACKAGE_CONTENTS.md structure reference
- Complete API documentation in docstrings
- Added VISUALIZATION_LINE_STYLE_UPDATE.md technical doc
- Created IMPORT_FIX.md troubleshooting guide

Testing
~~~~~~~

- New comprehensive import test (test_imports_v05.py)
- Verifies all 8 test categories
- Checks for removed old function names
- Validates version metadata

GitHub Readiness
~~~~~~~~~~~~~~~~

- Added setup.py for pip installation
- Created requirements.txt with all dependencies
- Added .gitignore for Python projects
- Full CC-BY 4.0 LICENSE text included
- Example notebooks cleaned and documented

Version 4.0 (Previous)
----------------------

**Original Monolithic Version**

- Combined hysteresis analysis and classification
- Single large module structure
- Event-scale hysteresis only
- Basic visualization functions
- Known issues with Lloyd NaN and event duplication

Known Issues in v4.0
~~~~~~~~~~~~~~~~~~~~

- Lloyd function generates numpy warnings
- Event-scale hysteresis creates artifacts in time series
- Import structure confusing
- Documentation scattered
- No formal package structure

Migration from v4.0 to v0.5
---------------------------

Breaking Changes
~~~~~~~~~~~~~~~~

**Import Changes:**

Old::

    from gcs_v5 import classify_geochemical_phase
    from gcs_analysis import some_function

New::

    import hygcs as gcs
    classified = gcs.classify_geochemical_phase(...)

**Function Renames:**

==========================================  =====================================
Old Name                                    New Name
==========================================  =====================================
``classify_with_highres_logic()``           ``classify_segment_phase()``
``gcs_v5.py`` (module)                      ``gcs.py``
==========================================  =====================================

**Removed Functions:**

Functions in ``gcs_analysis.py`` were merged into ``gcs_core.py``.
Direct imports from ``gcs_analysis`` will fail.

Migration Guide::

    # Old v4.0 code
    from gcs_v5 import classify_geochemical_phase
    from gcs_analysis import calculate_all_hysteresis_metrics

    # New v0.5 code
    import hygcs as gcs
    classified = gcs.classify_geochemical_phase(...)
    metrics = gcs.calculate_all_hysteresis_metrics(...)

Deprecated Features
~~~~~~~~~~~~~~~~~~~

None - this is a major restructuring, old structure fully replaced.

Future Plans
------------

Version 0.6 (Planned)
~~~~~~~~~~~~~~~~~~~~~

Potential improvements:

- PyPI package release
- Additional hysteresis methods
- Improved confidence scoring algorithms
- Machine learning phase classification option
- Expanded test suite
- Performance optimizations

Version 1.0 (Planned)
~~~~~~~~~~~~~~~~~~~~~

Stable API release:

- Frozen API for backwards compatibility
- Complete test coverage
- Comprehensive benchmarking
- Publication of methodology paper
- Community contribution guidelines

Reporting Issues
----------------

Found a bug? Have a suggestion?

- **GitHub Issues**: https://github.com/yourusername/HyGCS/issues
- **Email**: conrad.jackisch@tbt.tu-freiberg.de

Contributing
------------

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

See CONTRIBUTING.md (to be added) for detailed guidelines.

Version Numbering
-----------------

HyGCS follows semantic versioning principles:

- **Major version** (X.0.0): Breaking API changes
- **Minor version** (0.X.0): New features, backwards compatible
- **Patch version** (0.0.X): Bug fixes, backwards compatible

Current version: **0.5.0**
