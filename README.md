<p align="center">
  <img src="menpowidgets-logo.png" alt="menpo" width="30%"></center>
  <br><br>
  <a href="https://github.com/menpo/menpowidgets/blob/master/LICENSE.txt"><img src="http://img.shields.io/badge/License-BSD-green.svg" alt="BSD License"/></a>
  <a href="https://github.com/menpo/menpowidgets/actions/workflows/ci.yml"><img src="https://github.com/menpo/menpowidgets/actions/workflows/ci.yml/badge.svg" alt="CI"/></a>
</p>


menpowidgets - Jupyter widgets for fancy visualization
======================================================

What is MenpoWidgets?
---------------------
MenpoWidgets is the [Menpo Project](http://www.menpo.org/)'s Python package for fancy visualization within the Jupyter notebook using interactive widgets.
In the [Menpo Project](http://www.menpo.org/) we take an opinionated stance that visualization is a key part of generating research. Therefore, we have tried
to make the mental overhead of visualizing objects as low as possible. MenpoWidgets makes tasks like data exploration, model observation
and results demonstration as simple as possible.

Installation
------------
```
pip install menpowidgets                # the widgets for menpo's images, shapes and models
pip install "menpowidgets[menpofit]"    # + the visualizations of menpofit's models and fitting results
```
or, from conda-forge:
```
conda install -c conda-forge menpowidgets menpofit
```
Use it in JupyterLab or the Jupyter notebook (ipywidgets 8).

Releases
--------
Releases are built and published to PyPI from GitHub Actions by pushing a signed `vX.Y.Z` tag (PyPI
trusted publishing, no tokens); the version number comes from the tag.

API Documentation
-----------------
In MenpoWidgets, we use legible docstrings, and therefore, all documentation
should be easily accessible in any sensible IDE (or IPython) via tab completion.
However, we strongly advise you to visit the [MenpoWidgets API documentation](http://menpowidgets.readthedocs.io/).
