IMPORTANT
=========
Menpowidgets has been designed for academic use. The project changes quickly as
determined by our research, and this should be kept in mind at all times.

MenpoWidgets. Jupyter widgets for fancy visualization
======================================================

What is MenpoWidgets?
---------------------
MenpoWidgets is the Menpo Project's Python package for fancy visualization within the Jupyter notebook using interactive widgets.
In the Menpo Project we take an opinionated stance that visualization is a key part of generating research. Therefore, we have tried
to make the mental overhead of visualizing objects as low as possible. MenpoWidgets makes tasks like data exploration, model observation
and results demonstration as simple as possible.

Installation
------------
Unfortunately, the Menpo Project is a complex project that relies on satisfying
a number of complex 3rd party library dependencies. The default Python packing
environment does not make this an easy task. Therefore, we evangelise the use
of the conda ecosystem, provided by
[Anaconda](https://store.continuum.io/cshop/anaconda/). In order to make things
as simple as possible, we suggest that you use conda too! To try and persuade
you, go to the [Menpo website](http://www.menpo.org/installation/) to find
installation instructions for all major platforms.

API Documentation
-----------------
In MenpoWidgets, we use legible docstrings, and therefore, all documentation
should be easily accessible in any sensible IDE (or IPython) via tab completion.
However, we strongly advise you to visit the [MenpoWidgets API documentation](http://menpofit.readthedocs.io/).

Usage Example
-------------
A short example is often more illustrative than a verbose explanation. Let's assume that you want to quickly explore a folder of numerous annotated images,
without the overhead of waiting to load them and writing code to view them. The images can be easily loaded using the Menpo package and then visualized using an
interactive widget as:

```python
import menpo.io as mio
from menpowidgets import visualize_images

images = mio.import_images('/path/to/images/')
visualize_images(images)
```

<video width="100%" autoplay loop><source src="docs/source/visualize_images.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>


Similarly, the fitting result of a deformable model from the MenpoFit package can be demonstrated as:

```python
result = fitter.fit_from_bb(image, initial_bounding_box)
result.view_widget()
```

<video width="100%" autoplay loop><source src="docs/source/view_result_widget.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>
