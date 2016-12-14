from collections import Sized


def view_widget(items, **kwargs):
    r"""
    Convieniece function that uses the type of the first item in a list to
    automatically select and display the relevent group widget.

    Parameters
    ----------
    items : `list`
        The `list` of objects to be visualized. The first item will be tested
        for it's type, which has to be one of `menpo.shape.TriMesh`,
        `menpo.shape.PointCloud`, `menpo.image.Image` and the appropriate
        widget will be returned
    kwargs : optional
        Keyword arguments that will be forwarded to the appropriate widget.

    Returns
    -------
    widget
        The appropriate instantiated widget.

    Raises
    ------
    ValueError
        If the type of the first item in the list does not have a suitable
        multiple item viewer in menpowidgets.
    """
    from menpo.shape import PointCloud
    from menpo.landmark import LandmarkManager
    from menpo.image import Image
    from menpo.model import PCAModel

    # We use the first item to select the correct widget
    if not isinstance(items, Sized):
        template = items
    else:
        template = items[0]

    # Select widget based on template's class
    if isinstance(template, PointCloud) and template.n_dims == 2:
        from .base import visualize_shapes_2d
        visualize_shapes_2d(items, **kwargs)
    elif isinstance(template, LandmarkManager):
        from .base import visualize_landmarks_2d
        visualize_landmarks_2d(items, **kwargs)
    elif isinstance(template, Image):
        from .base import visualize_images
        visualize_images(items, **kwargs)
    elif (isinstance(template, PCAModel)
          and isinstance(template.template_instance, PointCloud)
          and template.template_instance.n_dims == 2):
        from .base import visualize_shape_model_2d
        visualize_shape_model_2d(items, **kwargs)
    else:
        raise ValueError(
            "No suitable list visualization found for type {}".format(
                type(template)))
