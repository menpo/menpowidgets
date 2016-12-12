from .base import (visualize_shapes_2d, visualize_landmarks_2d,
                   visualize_images, visualize_patches,
                   plot_graph, save_matplotlib_figure, save_mayavi_figure,
                   visualize_appearance_model, visualize_patch_appearance_model,
                   visualize_shape_model_2d, webcam_widget)
from .menpofitwidgets import *
#from .menpo3dwidgets import *
from .items import visualize_list

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
