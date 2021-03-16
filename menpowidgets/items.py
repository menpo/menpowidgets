from collections import Sized

from menpo.image import Image
from menpo.landmark import LandmarkManager
from menpo.shape import PointCloud, TriMesh
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
    from . import (
        visualize_images,
        visualize_landmarks_2d,
        visualize_landmarks_3d,
        visualize_shapes_2d,
        visualize_shapes_3d,
        visualize_shape_model_2d,
        visualize_meshes_3d,
        visualize_shape_model_3d,
    )

    # We use the first item to select the correct widget
    if not isinstance(items, Sized) or isinstance(items, LandmarkManager):
        template = items
    else:
        template = items[0]
    # note that the ordering of this list is important - a TriMesh isa
    # PointCloud, so we must test for the more specialized case first
    # if we want to do that. Third item is an optional boolean test.
    cls_to_items_widget = [
        (Image, visualize_images, None),
        (TriMesh, visualize_meshes_3d, lambda m: m.n_dims == 3),
        (PointCloud, visualize_shapes_2d, lambda pc: pc.n_dims == 2),
        (PointCloud, visualize_shapes_3d, lambda pc: pc.n_dims == 3),
        (
            LandmarkManager,
            visualize_landmarks_2d,
            lambda lms: list(lms.values())[0].n_dims == 2,
        ),
        (
            LandmarkManager,
            visualize_landmarks_3d,
            lambda lms: list(lms.values())[0].n_dims == 3,
        ),
        (
            PCAModel,
            visualize_shape_model_2d,
            lambda m: isinstance(m.template_instance, PointCloud)
            and m.template_instance.n_dims == 2,
        ),
        (
            PCAModel,
            visualize_shape_model_3d,
            lambda m: isinstance(m.template_instance, PointCloud)
            and m.template_instance.n_dims == 3,
        ),
    ]

    for (cls, widget, test) in cls_to_items_widget:
        if isinstance(template, cls) and (test is None or test(template)):
            return widget(items, **kwargs)

    raise ValueError(
        "No suitable list visualization found for type {} - valid types are "
        "{} or subclasses thereof".format(
            type(template), ", ".format([x[0] for x in cls_to_items_widget])
        )
    )
