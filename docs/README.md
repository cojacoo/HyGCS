# HyGCS Documentation

This directory contains the Sphinx documentation for HyGCS.

## Building Documentation Locally

### Install Dependencies

```bash
pip install -r requirements-docs.txt
```

Or install with documentation extras:

```bash
cd ..
pip install -e .[docs]
```

### Build HTML Documentation

```bash
make html
```

The built documentation will be in `_build/html/`. Open `_build/html/index.html` in your browser.

### Clean Build Files

```bash
make clean
```

## ReadTheDocs Integration

Documentation is automatically built and hosted on ReadTheDocs when you push to GitHub.

### Setup Steps

1. Go to https://readthedocs.org/
2. Sign in with your GitHub account
3. Click "Import a Project"
4. Select your HyGCS repository
5. Configuration is read from `.readthedocs.yaml`
6. Docs will build automatically on every push

### Documentation URL

Once set up, your docs will be available at:
- Latest: `https://hygcs.readthedocs.io/en/latest/`
- Stable: `https://hygcs.readthedocs.io/en/stable/`
- Specific version: `https://hygcs.readthedocs.io/en/v0.5/`

## Documentation Structure

```
docs/
├── conf.py                   # Sphinx configuration
├── index.rst                 # Main documentation page
├── installation.rst          # Installation guide
├── quickstart.rst            # Quick start tutorial
├── examples.rst              # Example notebooks guide
├── scientific_background.rst # Detailed methodology
├── api_core.rst             # Core functions API
├── api_classification.rst    # Classification API
├── api_visualization.rst     # Visualization API
├── api_hysteresis.rst       # Hysteresis methods API
├── license.rst              # License information
├── citation.rst             # How to cite
├── changelog.rst            # Version history
├── requirements-docs.txt    # Documentation build dependencies
└── Makefile                 # Build automation
```

## Writing Documentation

### RST Format

Documentation uses reStructuredText (.rst) format. Key syntax:

```rst
Section Title
=============

Subsection
----------

**Bold text**
*Italic text*

- Bullet list
- Item 2

1. Numbered list
2. Item 2

Code block::

    import hygcs as gcs
    result = gcs.some_function()

Link: `Link text <URL>`_
```

### Docstrings

Function documentation is extracted from Python docstrings using autodoc.
We use NumPy/Google style docstrings:

```python
def my_function(param1, param2):
    """
    Short description.

    Longer description explaining details.

    Parameters
    ----------
    param1 : str
        Description of param1
    param2 : int
        Description of param2

    Returns
    -------
    result : dict
        Description of return value
    """
```

### Adding New Pages

1. Create new `.rst` file in `docs/`
2. Add to `toctree` in relevant section of `index.rst`
3. Rebuild documentation to see changes

## Troubleshooting

### Import Errors During Build

Ensure all package dependencies are in `requirements-docs.txt`.

### Autodoc Not Finding Modules

Check `sys.path.insert` in `conf.py` points to correct location.

### Theme Not Applied

Install theme: `pip install sphinx-rtd-theme`

### Warnings About Missing References

Use `:doc:` for cross-references to other documentation pages.

## Contributing to Documentation

1. Edit relevant `.rst` files
2. Build locally to preview: `make html`
3. Check for warnings: `make html 2>&1 | grep warning`
4. Commit changes
5. Push to GitHub
6. ReadTheDocs will rebuild automatically

## Contact

Documentation questions:
- Conrad Jackisch: conrad.jackisch@tbt.tu-freiberg.de
