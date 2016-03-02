# Ensure that the code is being run inside a Jupyter kernel!
from .utils import verify_ipython_and_kernel
verify_ipython_and_kernel()
del verify_ipython_and_kernel


from .base import (visualize_pointclouds, visualize_landmarkgroups,
                   visualize_landmarks, visualize_images, visualize_patches,
                   plot_graph, save_matplotlib_figure, features_selection,
                   visualize_appearance_model, visualize_patch_appearance_model,
                   visualize_shape_model)
from .menpofit import *


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
