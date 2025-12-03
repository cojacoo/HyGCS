Citation
========

If you use HyGCS in your research, please cite the software and the relevant methodology papers.

Software Citation
-----------------

BibTeX
~~~~~~

.. code-block:: bibtex

   @software{hygcs2025,
     author = {Jackisch, Conrad and Sanchez, Anita},
     title = {HyGCS: Hydro-Geochemical Classification Suite},
     year = {2025},
     version = {0.5},
     url = {https://github.com/yourusername/HyGCS},
     license = {CC-BY-4.0}
   }

Text
~~~~

   Jackisch, C. and Sanchez, A. (2025). HyGCS: Hydro-Geochemical Classification Suite
   (Version 0.5). https://github.com/yourusername/HyGCS

Methodology Papers
------------------

Please also cite the original methodology papers for the methods you use:

HARP Method
~~~~~~~~~~~

.. code-block:: bibtex

   @article{roberts2023harp,
     author = {Roberts, Melanie E. and others},
     title = {Hysteresis Analysis of Rising and falling Peaks (HARP)},
     journal = {Hydrological Processes},
     year = {2023}
   }

Zuecco Index
~~~~~~~~~~~~

.. code-block:: bibtex

   @article{zuecco2016hysteresis,
     author = {Zuecco, G. and Penna, D. and Borga, M. and van Meerveld, H.J.},
     title = {A versatile index to characterize hysteresis between hydrological
              variables at the runoff event timescale},
     journal = {Hydrological Processes},
     volume = {30},
     number = {9},
     pages = {1449--1466},
     year = {2016},
     doi = {10.1002/hyp.10681}
   }

Lloyd/Lawler Methods
~~~~~~~~~~~~~~~~~~~~

**Lloyd et al. (2016) - HInew method:**

.. code-block:: bibtex

   @article{lloyd2016using,
     author = {Lloyd, C.E.M. and Freer, J.E. and Johnes, P.J. and Collins, A.L.},
     title = {Using hysteresis analysis of high-resolution water quality monitoring
              data, including uncertainty, to infer controls on nutrient and sediment
              transfer in catchments},
     journal = {Hydrology and Earth System Sciences},
     volume = {20},
     pages = {2705--2719},
     year = {2016},
     doi = {10.5194/hess-20-2705-2016}
   }

**Lawler et al. (2006) - Original HIL method:**

.. code-block:: bibtex

   @article{lawler2006turbidity,
     author = {Lawler, D.M. and Petts, G.E. and Foster, I.D.L. and Harper, S.},
     title = {Turbidity dynamics during spring storm events in an urban headwater
              river system: The Upper Tame, West Midlands, UK},
     journal = {Science of the Total Environment},
     volume = {360},
     pages = {109--126},
     year = {2006},
     doi = {10.1016/j.scitotenv.2005.08.032}
   }

CVc/CVq Framework
~~~~~~~~~~~~~~~~~

.. code-block:: bibtex

   @article{musolff2015catchment,
     author = {Musolff, A. and Schmidt, C. and Selle, B. and Fleckenstein, J.H.},
     title = {Catchment controls on solute export},
     journal = {Advances in Water Resources},
     volume = {86},
     pages = {133--146},
     year = {2015},
     doi = {10.1016/j.advwatres.2015.09.026}
   }

C-Q Relationships
~~~~~~~~~~~~~~~~~

.. code-block:: bibtex

   @article{thompson2011comparative,
     author = {Thompson, S.E. and others},
     title = {Comparative hydrology across AmeriFlux sites: The variable roles of
              climate, vegetation, and groundwater},
     journal = {Water Resources Research},
     volume = {47},
     number = {10},
     year = {2011},
     doi = {10.1029/2010WR009797}
   }

Critical Perspective
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bibtex

   @article{knapp2024mind,
     author = {Knapp, J.L.A. and Musolff, A.},
     title = {Mind the gap: A critical perspective on concentration-discharge
              relationships},
     journal = {Hydrological Processes},
     year = {2024},
     doi = {10.1002/hyp.15328}
   }

Example Publication Text
------------------------

Methods Section
~~~~~~~~~~~~~~~

   "Hysteresis analysis was performed using HyGCS v0.5 (Jackisch and Sanchez, 2025),
   which implements the HARP (Roberts et al., 2023), Zuecco (Zuecco et al., 2016),
   and Lloyd/Lawler (Lloyd et al., 2016) methods. Geochemical phase classification
   followed the hierarchical rule-based approach integrating window-scale hysteresis,
   C-Q slopes, and CVc/CVq ratios (Musolff et al., 2015)."

Results Section
~~~~~~~~~~~~~~~

   "Hysteresis analysis using multiple methods (HARP, Zuecco, Lloyd/Lawler) revealed
   predominantly clockwise patterns (mean HInew = 0.42 ± 0.18), indicating
   flushing-dominated dynamics. The geochemical phase classification (HyGCS v0.5)
   identified distinct temporal patterns with 35% flushing (F), 28% chemostatic (C),
   and 22% recession (R) phases across the monitoring period."

Acknowledgments Section
~~~~~~~~~~~~~~~~~~~~~~~~

   "We acknowledge the use of HyGCS (Hydro-Geochemical Classification Suite)
   developed by Conrad Jackisch and Anita Sanchez at TU Bergakademie Freiberg."

Related Publications
--------------------

Publications using or related to HyGCS methods:

**In Review:**

- Sanchez, A. et al. (2025). Geochemical phase classification in legacy mine drainage
  systems. *In review*.

**To Be Added:**

If you publish work using HyGCS, please let us know so we can add it here!

Contact: conrad.jackisch@tbt.tu-freiberg.de

Data Availability Statement
----------------------------

Example text for data availability sections:

   "Hysteresis analysis was performed using HyGCS v0.5, available at
   https://github.com/yourusername/HyGCS under CC-BY 4.0 license."

Acknowledgments
---------------

HyGCS builds upon and extends methods from:

- **HARP R package** by Melanie Roberts: https://github.com/MelanieEmmajade/HARP
- **Hysteresis-Index-Zuecco** by Florian Jehn: https://github.com/florianjehn/Hysteresis-Index-Zuecco

Development was supported by the mine drainage monitoring network at TU Bergakademie Freiberg.
