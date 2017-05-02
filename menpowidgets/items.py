from collections import Sized

from menpo.shape import PointCloud
from menpo.landmark import LandmarkManager
from menpo.image import Image
from menpo.model import PCAModel


def view_widget(items, **kwargs):
    r"""
    Convenience function that visualizes the provided items with a suitable
    widget. The supported items are:

        ======================================================================== =
        Classes
        ======================================================================== =
        2D `PointCloud`, `PointGraph`, `LabelledPointUndirectedGraph`, `TriMesh`
        3D `PointCloud`, `PointGraph`, `LabelledPointUndirectedGraph`
        `Image`, `MaskedImage`
        2D `LandmarkManager`
        3D `LandmarkManager`
        `PCAModel` of 2D `PointCloud` visualize_shape_model_2d
        `PCAModel` of 3D `PointCloud` visualize_shape_model_3d
        `PCAModel` of `Image` visualize_appearance_model
        ======================================================================== =

    Parameters
    ----------
    items : `object` or `list` of `object`
        The item(s) to visualize. The supported items are mentioned above.
    kwargs : optional
        Keyword arguments that will be forwarded to the appropriate widget,
        e.g. `browser_style`, `figure_size`.

    Raises
    ------
    ValueError
        If the type of the first item in the list does not have a suitable
        widget in menpowidgets.
    """
    # We use the first item to select the correct widget
    if not isinstance(items, Sized) or isinstance(items, LandmarkManager):
        template = items
    else:
        template = items[0]

    # Select widget based on template's class
    if isinstance(template, PointCloud) and template.n_dims == 2:
        from .base import visualize_shapes_2d
        visualize_shapes_2d(items, **kwargs)
    elif isinstance(template, PointCloud) and template.n_dims == 3:
        from .base import visualize_shapes_3d
        visualize_shapes_3d(items, **kwargs)
    elif isinstance(template, LandmarkManager) and template.n_dims == 2:
        from .base import visualize_landmarks_2d
        visualize_landmarks_2d(items, **kwargs)
    elif isinstance(template, LandmarkManager) and template.n_dims == 3:
        from .base import visualize_landmarks_3d
        visualize_landmarks_3d(items, **kwargs)
    elif isinstance(template, Image):
        from .base import visualize_images
        visualize_images(items, **kwargs)
    elif (isinstance(template, PCAModel)
          and isinstance(template.template_instance, PointCloud)
          and template.template_instance.n_dims == 2):
        from .base import visualize_shape_model_2d
        visualize_shape_model_2d(items, **kwargs)
    elif (isinstance(template, PCAModel)
          and isinstance(template.template_instance, Image)):
        from .base import visualize_appearance_model
        visualize_appearance_model(items, **kwargs)
    else:
        raise ValueError(
            "No suitable widget found for type {} - Supported types are "
            "PointCloud, LandmarkManager, Image, PCAModel or "
            "subclasses of those.".format(
                type(template)))
