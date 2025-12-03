Installation
============

Requirements
------------

Python Version
~~~~~~~~~~~~~~

HyGCS requires **Python 3.8 or higher**.

Dependencies
~~~~~~~~~~~~

Core dependencies:

- pandas >= 1.3.0
- numpy >= 1.20.0
- scipy >= 1.7.0
- plotly >= 5.0.0
- scikit-learn >= 0.24.0
- statsmodels >= 0.14.5

Optional dependencies for examples:

- jupyter >= 1.0.0
- notebook >= 6.4.0
- ipywidgets >= 7.6.0
- openpyxl >= 3.0.0
- matplotlib >= 3.10.7

Installation from Source
-------------------------

Clone the repository and install in development mode::

    git clone https://github.com/yourusername/HyGCS.git
    cd HyGCS
    pip install -e .

This will install HyGCS along with all required dependencies.

Alternative: Install Dependencies Only
--------------------------------------

If you prefer to use the package without installation::

    cd HyGCS
    pip install -r requirements.txt

Then add the package directory to your Python path or import directly from the ``hygcs/`` folder.

Verify Installation
-------------------

Test that the package installed correctly::

    python -c "import hygcs as gcs; print(gcs.__version__)"

This should print ``0.5`` without errors.

Run the test suite::

    cd tests/
    python test_imports_v05.py

All tests should pass with no errors.

Troubleshooting
---------------

Import Errors
~~~~~~~~~~~~~

If you encounter ``cannot import name`` errors:

1. Clear Python cache::

    find . -type d -name "__pycache__" -exec rm -r {} +

2. Restart your Python kernel/session

3. Reimport the package

Missing Dependencies
~~~~~~~~~~~~~~~~~~~~

If you get ``ModuleNotFoundError``::

    pip install -r requirements.txt

Or install missing packages individually::

    pip install statsmodels matplotlib

Jupyter Notebook Issues
~~~~~~~~~~~~~~~~~~~~~~~~

For running example notebooks, ensure Jupyter is installed::

    pip install jupyter notebook ipywidgets

Then launch notebooks::

    jupyter notebook examples/demo_gcs_core_function.ipynb

Next Steps
----------

- Read the :doc:`quickstart` guide
- Explore the :doc:`examples`
- Check the :doc:`api_core` reference
