def visualize_list(items, **kwargs):
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
    from . import visualize_meshes, visualize_images, visualize_pointclouds
    from menpo.shape import TriMesh, PointCloud
    from menpo.image import Image
    # note that the ordering of this list is important - a TriMesh isa
    # PointCloud, so we must test for the more specialized case first.
    cls_to_items_widget = [
        (TriMesh, visualize_meshes),
        (PointCloud, visualize_pointclouds),
        (Image, visualize_images)
    ]

    template = items[0]

    for (cls, widget) in cls_to_items_widget:
        if isinstance(template, cls):
            return widget(items, **kwargs)

    raise ValueError(
        "No suitable list visualization found for type {} - valid types are "
        "{} or subclasses thereof".format(
            type(template), ', '.format([x[0] for x in cls_to_items_widget])
        ))
