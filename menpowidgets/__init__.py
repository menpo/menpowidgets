from .items import view_widget
from .base import (visualize_patches, webcam_widget, plot_graph,
                   save_matplotlib_figure, save_mayavi_figure,
                   visualize_patch_appearance_model)
from .menpofitwidgets import *
#from .menpo3dwidgets import *

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
