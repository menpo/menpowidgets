=======
Welcome
=======

**Welcome to the MenpoWidgets documentation!**

MenpoWidgets is the Menpo Project's Python package for fancy visualization within the Jupyter notebook using interactive widgets. 
In the Menpo Project we take an opinionated stance that visualization is a key part of generating research. Therefore, we have tried 
to make the mental overhead of visualizing objects as low as possible. MenpoWidgets makes tasks like data exploration, model observation 
and results demonstration as simple as possible.


API Documentation
~~~~~~~~~~~~~~~~~
In MenpoWidgets, we use legible docstrings, and therefore, all documentation 
should be easily accessible in any sensible IDE (or IPython) via tab completion. 
However, this section should make most of the core classes available for viewing online.

Main Widgets  
  Functions for visualizing the various Menpo and MenpoFit objects using interactive widgets.

  .. toctree::
      :maxdepth: 1

      menpowidgets/base/index
      menpowidgets/menpofit/base/index


Options Widgets  
  Independent widget objects that can be used as the main components for designing high-level widget functions.

  .. toctree::
      :maxdepth: 1

      menpowidgets/options/index
      menpowidgets/menpofit/options/index


Tools Widgets
  Low-level widget objects that can be used as the main ingredients for creating more complex widgets.

  .. toctree::
      :maxdepth: 1

      menpowidgets/abstract/index
      menpowidgets/tools/index


Usage Example
~~~~~~~~~~~~~
A short example is often more illustrative than a verbose explanation. Let's assume that you want to quickly explore a folder of numerous annotated images, 
without the overhead of waiting to load them and writing code to view them. The images can be easily loaded using the Menpo package and then visualized using an
interactive widget as:

.. code-block:: python

    import menpo.io as mio
    from menpowidgets import visualize_images

    images = mio.import_images('/path/to/images/')
    visualize_images(images)

.. raw:: html

   <video width="100%" autoplay loop><source src="../../source/visualize_images.mp4" type="video/mp4">Your browser does not support the video tag.</video>


Similarly, the fitting result of a deformable model from the MenpoFit package can be demonstrated as:

.. code-block:: python

    result = fitter.fit_from_bb(image, initial_bounding_box)
    result.view_widget()

.. raw:: html

   <video width="100%" autoplay loop><source src="../../source/view_result_widget.mp4" type="video/mp4">Your browser does not support the video tag.</video>

