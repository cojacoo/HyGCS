from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hygcs",
    version="0.5.0",
    author="Conrad Jackisch, Anita Sanchez",
    author_email="conrad.jackisch@tbt.tu-freiberg.de",
    description="Hydro-Geochemical Classification Suite for C-Q hysteresis analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/HyGCS",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Hydrology",
        "License :: OSI Approved :: Creative Commons Attribution 4.0 International",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "plotly>=5.0.0",
        "scikit-learn>=0.24.0",
    ],
    extras_require={
        "dev": [
            "jupyter>=1.0.0",
            "notebook>=6.4.0",
            "ipywidgets>=7.6.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "examples": [
            "jupyter>=1.0.0",
            "notebook>=6.4.0",
            "ipywidgets>=7.6.0",
            "openpyxl>=3.0.0",
            "matplotlib>=3.10.7",
        ],
    },
    keywords="hydrology geochemistry hysteresis C-Q concentration-discharge water-quality",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/HyGCS/issues",
        "Source": "https://github.com/yourusername/HyGCS",
    },
)
