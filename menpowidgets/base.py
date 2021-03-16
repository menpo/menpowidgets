from collections import Sized, OrderedDict
import matplotlib.pyplot as plt
from matplotlib import collections as mc
import numpy as np

import ipywidgets
import IPython.display as ipydisplay

from menpo.base import name_of_callable
from menpo.image import MaskedImage, Image
from menpo.image.base import _convert_patches_list_to_single_array
from menpo.shape import TriMesh, ColouredTriMesh, TexturedTriMesh
from menpo.visualize import print_dynamic
from menpo.landmark import LandmarkManager

from .options import (
    RendererOptionsWidget,
    TextPrintWidget,
    SaveMatplotlibFigureOptionsWidget,
    AnimationOptionsWidget,
    ImageOptionsWidget,
    LandmarkOptionsWidget,
    PlotMatplotlibOptionsWidget,
    PatchOptionsWidget,
    LinearModelParametersWidget,
    CameraSnapshotWidget,
    Shape2DOptionsWidget,
    Shape3DOptionsWidget,
    SaveMayaviFigureOptionsWidget,
    Mesh3DOptionsWidget,
)
from .tools import LogoWidget, SwitchWidget
from .utils import (
    extract_group_labels_from_landmarks,
    extract_groups_labels_from_image,
    render_image,
    render_patches,
)
from .checks import check_n_parameters
from .style import map_styles_to_hex_colours


def menpowidgets_src_dir_path():
    r"""
    The path to the top of the menpowidgets package.

    Useful for locating where the logos folder is stored.

    Returns
    -------
    path : ``pathlib.Path``
        The full path to the top of the Menpo package
    """
    # to avoid cluttering the menpowidgets.base namespace
    from pathlib import Path
    import os.path

    return Path(os.path.abspath(__file__)).parent


def visualize_shapes_2d(
    shapes, figure_size=(7, 7), browser_style="buttons", custom_info_callback=None
):
    r"""
    Widget that allows browsing through a `list` of
    2D shapes. The supported objects are:

            ================================== =
            Object
            ================================== =
            `menpo.shape.PointCloud`
            `menpo.shape.PointUndirectedGraph`
            `menpo.shape.PointDirectedGraph`
            `menpo.shape.PointTree`
            `menpo.shape.LabelledPointGraph`
            `menpo.shape.TriMesh`
            ================================== =

    Any instance of the above can be combined in the input `list`.

    Parameters
    ----------
    shapes : `list`
        The `list` of objects to be visualized. It can contain a combination of

            ================================== =
            Object
            ================================== =
            `menpo.shape.PointCloud`
            `menpo.shape.PointUndirectedGraph`
            `menpo.shape.PointDirectedGraph`
            `menpo.shape.PointTree`
            `menpo.shape.LabelledPointGraph`
            `menpo.shape.TriMesh`
            ================================== =

        or subclasses of those.
    figure_size : (`int`, `int`), optional
        The initial size of the rendered figure.
    browser_style : ``{'buttons', 'slider'}``, optional
        It defines whether the selector of the objects will have the form of
        plus/minus buttons or a slider.
    custom_info_callback: `function` or ``None``, optional
        If not ``None``, it should be a function that accepts a 2D shape
        and returns a list of custom messages to be printed about it. Each
        custom message will be printed in a separate line.
    """
    # Make sure that shapes is a list even with one member
    if not isinstance(shapes, Sized):
        shapes = [shapes]

    # Get the number of shapes
    n_shapes = len(shapes)

    # Define the styling options
    main_style = "warning"

    output = ipywidgets.Output()

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        # Get selected shape index
        i = shape_number_wid.selected_values if n_shapes > 1 else 0

        # Create options dictionary
        options = dict()
        options.update(shape_options_wid.selected_values["lines"])
        options.update(shape_options_wid.selected_values["markers"])
        options["image_view"] = shape_options_wid.selected_values["image_view"]
        options.update(renderer_options_wid.selected_values["numbering_matplotlib"])
        options.update(renderer_options_wid.selected_values["axes"])

        # Correct options based on the type of the shape
        if hasattr(shapes[i], "labels"):
            # If the shape is a LabelledPointUndirectedGraph ...
            # ...use the legend options
            options.update(renderer_options_wid.selected_values["legend"])
            # ...use with_labels
            options["with_labels"] = shape_options_wid.selected_values["with_labels"]
            # ...correct colours
            line_colour = []
            marker_face_colour = []
            marker_edge_colour = []
            for lbl in options["with_labels"]:
                idx = shapes[i].labels.index(lbl)
                line_colour.append(options["line_colour"][idx])
                marker_face_colour.append(options["marker_face_colour"][idx])
                marker_edge_colour.append(options["marker_edge_colour"][idx])
            options["line_colour"] = line_colour
            options["marker_face_colour"] = marker_face_colour
            options["marker_edge_colour"] = marker_edge_colour
        else:
            # If shape is PointCloud, TriMesh or PointGraph
            # ...correct colours
            options["line_colour"] = options["line_colour"][0]
            options["marker_face_colour"] = options["marker_face_colour"][0]
            options["marker_edge_colour"] = options["marker_edge_colour"][0]

        # Get figure size
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * figure_size[0],
            renderer_options_wid.selected_values["zoom_one"] * figure_size[1],
        )

        # Render shape with selected options
        save_figure_wid.renderer = shapes[i].view(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            figure_size=new_figure_size,
            **options
        )

        # Force rendering
        save_figure_wid.renderer.force_draw()

        # Update info text widget
        update_info(shapes[i], custom_info_callback=custom_info_callback)

    # Define function that updates the info text
    def update_info(shape, custom_info_callback=None):
        min_b, max_b = shape.bounds()
        rang = shape.range()
        cm = shape.centre()
        text_per_line = [
            "> {}".format(name_of_callable(shape)),
            "> {} points".format(shape.n_points),
            "> Bounds: [{0:.1f}-{1:.1f}]W, [{2:.1f}-{3:.1f}]H".format(
                min_b[0], max_b[0], min_b[1], max_b[1]
            ),
            "> Range: {0:.1f}W, {1:.1f}H".format(rang[0], rang[1]),
            "> Centre of mass: ({0:.1f}, {1:.1f})".format(cm[0], cm[1]),
            "> Norm: {0:.2f}".format(shape.norm()),
        ]
        if custom_info_callback is not None:
            # iterate over the list of messages returned by the callback
            # function and append them in the text_per_line.
            for msg in custom_info_callback(shape):
                text_per_line.append("> {}".format(msg))
        info_wid.set_widget_state(text_per_line=text_per_line)

    # If the object is a LabelledPointUndirectedGraph, grab the labels
    labels = None
    if hasattr(shapes[0], "labels"):
        labels = shapes[0].labels

    # Create widgets
    shape_options_wid = Shape2DOptionsWidget(
        labels=labels, render_function=render_function
    )
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=["zoom_one", "axes", "numbering_matplotlib", "legend"],
        labels=None,
        axes_x_limits=0.1,
        axes_y_limits=0.1,
        render_function=render_function,
    )
    info_wid = TextPrintWidget(text_per_line=[""])
    save_figure_wid = SaveMatplotlibFigureOptionsWidget()

    # Group widgets
    # Define function that updates options' widgets state
    def update_widgets(change):
        # Get current shape and check if it has labels
        i = change["new"]
        labels = None
        if hasattr(shapes[i], "labels"):
            labels = shapes[i].labels

        # Update shape options
        shape_options_wid.set_widget_state(labels=labels, allow_callback=True)

    # Shape selection slider
    index = {"min": 0, "max": n_shapes - 1, "step": 1, "index": 0}
    shape_number_wid = AnimationOptionsWidget(
        index,
        render_function=update_widgets,
        index_style=browser_style,
        interval=0.2,
        description="Shape",
        loop_enabled=True,
        continuous_update=False,
    )

    # Header widget
    logo_wid = LogoWidget(style=main_style)
    logo_wid.layout.margin = "0px 10px 0px 0px"
    header_wid = ipywidgets.HBox([logo_wid, shape_number_wid])
    header_wid.layout.align_items = "center"
    header_wid.layout.margin = "0px 0px 10px 0px"

    options_box = ipywidgets.Tab(
        [info_wid, shape_options_wid, renderer_options_wid, save_figure_wid]
    )
    tab_titles = ["Info", "Shape", "Renderer", "Export"]
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)

    output.layout.align_self = "center"
    wid = ipywidgets.VBox([header_wid, options_box, output])

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})


def visualize_shapes_3d(shapes, browser_style="buttons", custom_info_callback=None):
    r"""
    Widget that allows browsing through a `list` of
    3D shapes. The supported objects are:

            ==================================
            Object
            ==================================
            `menpo.shape.PointCloud`
            `menpo.shape.PointUndirectedGraph`
            `menpo.shape.PointDirectedGraph`
            `menpo.shape.PointTree`
            `menpo.shape.LabelledPointGraph`
            ==================================

    Any instance of the above can be combined in the input `list`.

    Parameters
    ----------
    shapes : `list`
        The `list` of objects to be visualized. It can contain a combination of

            ==================================
            Object
            ==================================
            `menpo.shape.PointCloud`
            `menpo.shape.PointUndirectedGraph`
            `menpo.shape.PointDirectedGraph`
            `menpo.shape.PointTree`
            `menpo.shape.LabelledPointGraph`
            ==================================

        or subclasses of those.
    browser_style : ``{'buttons', 'slider'}``, optional
        It defines whether the selector of the objects will have the form of
        plus/minus buttons or a slider.
    custom_info_callback: `function` or ``None``, optional
        If not ``None``, it should be a function that accepts a 2D shape
        and returns a list of custom messages to be printed about it. Each
        custom message will be printed in a separate line.
    """
    # Make sure that shapes is a list even with one member
    if not isinstance(shapes, Sized):
        shapes = [shapes]

    # Get the number of shapes
    n_shapes = len(shapes)

    # Define the styling options
    main_style = "warning"

    output = ipywidgets.Output()

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        save_figure_wid.renderer.clear_figure()

        # Get selected shape index
        i = shape_number_wid.selected_values if n_shapes > 1 else 0

        # Update info text widget
        update_info(shapes[i], custom_info_callback=custom_info_callback)

        # Create options dictionary
        options = dict()
        if isinstance(shapes[i], TriMesh):
            # Note that 3D TriMesh has a totally different set of options
            # compared to any other PointCloud or PointGraph. However, in order
            # for visualize_shapes_3d to support TriMeshes, we simply use the
            # options that are common. This means that most of the widget's
            # options will have no effect on rendering...
            options["mesh_type"] = "wireframe"
            if shape_options_wid.selected_values["markers"]["render_markers"]:
                options["mesh_type"] = "fancymesh"
            options["line_width"] = shape_options_wid.selected_values["lines"][
                "line_width"
            ]
            options["colour"] = shape_options_wid.selected_values["lines"][
                "line_colour"
            ][0]
            options["marker_style"] = shape_options_wid.selected_values["markers"][
                "marker_style"
            ]
            options["marker_size"] = shape_options_wid.selected_values["markers"][
                "marker_size"
            ]
            options["marker_resolution"] = shape_options_wid.selected_values["markers"][
                "marker_resolution"
            ]
            options["step"] = shape_options_wid.selected_values["markers"]["step"]
        else:
            options.update(shape_options_wid.selected_values["lines"])
            options.update(shape_options_wid.selected_values["markers"])
            options.update(renderer_options_wid.selected_values["numbering_mayavi"])

            # Correct options based on the type of the shape
            if hasattr(shapes[i], "labels"):
                # If the shape is a LabelledPointUndirectedGraph ...
                # ...use with_labels
                options["with_labels"] = shape_options_wid.selected_values[
                    "with_labels"
                ]
                # ...correct colours
                line_colour = []
                marker_colour = []
                for lbl in options["with_labels"]:
                    idx = shapes[i].labels.index(lbl)
                    line_colour.append(options["line_colour"][idx])
                    marker_colour.append(options["marker_colour"][idx])
                options["line_colour"] = line_colour
                options["marker_colour"] = marker_colour
            else:
                # If shape is PointCloud, TriMesh or PointGraph
                # ...correct colours
                options["line_colour"] = options["line_colour"][0]
                options["marker_colour"] = options["marker_colour"][0]

        # Render shape with selected options
        save_figure_wid.renderer = shapes[i].view(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            alpha=1.0,
            **options
        )

        # Force rendering
        save_figure_wid.renderer.force_draw()
        output.append_display_data(save_figure_wid.renderer.figure)

    # Define function that updates the info text
    def update_info(shape, custom_info_callback=None):
        min_b, max_b = shape.bounds()
        rang = shape.range()
        cm = shape.centre()
        text_per_line = [
            "> {}".format(name_of_callable(shape)),
            "> {} points".format(shape.n_points),
            "> Bounds: [{0:.1f}-{1:.1f}]X, [{2:.1f}-{3:.1f}]Y, "
            "[{4:.1f}-{5:.1f}]Z".format(
                min_b[0], max_b[0], min_b[1], max_b[1], min_b[2], max_b[2]
            ),
            "> Range: {0:.1f}X, {1:.1f}Y, {2:.1f}Z".format(rang[0], rang[1], rang[2]),
            "> Centre of mass: ({0:.1f}X, {1:.1f}Y, {2:.1f}Z)".format(
                cm[0], cm[1], cm[2]
            ),
            "> Norm: {0:.2f}".format(shape.norm()),
        ]
        if custom_info_callback is not None:
            # iterate over the list of messages returned by the callback
            # function and append them in the text_per_line.
            for msg in custom_info_callback(shape):
                text_per_line.append("> {}".format(msg))
        info_wid.set_widget_state(text_per_line=text_per_line)

    # If the object is a LabelledPointUndirectedGraph, grab the labels
    labels = None
    if hasattr(shapes[0], "labels"):
        labels = shapes[0].labels

    # Create widgets
    shape_options_wid = Shape3DOptionsWidget(
        labels=labels, render_function=render_function
    )
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=["numbering_mayavi"], labels=None, render_function=render_function
    )
    info_wid = TextPrintWidget(text_per_line=[""])
    save_figure_wid = SaveMayaviFigureOptionsWidget()

    # Group widgets
    if n_shapes > 1:
        # Define function that updates options' widgets state
        def update_widgets(change):
            # Get current shape and check if it has labels
            i = change["new"]
            labels = None
            if hasattr(shapes[i], "labels"):
                labels = shapes[i].labels

            # Update shape options
            shape_options_wid.set_widget_state(labels=labels, allow_callback=True)

        # Shape selection slider
        index = {"min": 0, "max": n_shapes - 1, "step": 1, "index": 0}
        shape_number_wid = AnimationOptionsWidget(
            index,
            render_function=update_widgets,
            index_style=browser_style,
            interval=0.2,
            description="Shape",
            loop_enabled=True,
            continuous_update=False,
        )

        # Header widget
        logo_wid = LogoWidget(style=main_style)
        logo_wid.layout.margin = "0px 10px 0px 0px"
        header_wid = ipywidgets.HBox([logo_wid, shape_number_wid])
        header_wid.layout.align_items = "center"
        header_wid.layout.margin = "0px 0px 10px 0px"
    else:
        # Header widget
        header_wid = LogoWidget(style=main_style)
        header_wid.layout.margin = "0px 10px 0px 0px"
    options_box = ipywidgets.Tab(
        [info_wid, shape_options_wid, renderer_options_wid, save_figure_wid]
    )
    tab_titles = ["Info", "Shape", "Renderer", "Export"]
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)

    output.layout.align_self = "center"
    wid = ipywidgets.VBox([header_wid, options_box, output])

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})
    print_dynamic("")


def visualize_landmarks_2d(
    landmarks, figure_size=(7, 7), browser_style="buttons", custom_info_callback=None
):
    r"""
    Widget that allows browsing through a `list` of
    `menpo.landmark.LandmarkManager` (or subclass) objects. The landmark
    managers can have a combination of different attributes, e.g.
    landmark groups and labels etc.

    Parameters
    ----------
    landmarks : `list` of `menpo.landmark.LandmarkManager` or subclass
        The `list` of landmark managers to be visualized.
    figure_size : (`int`, `int`), optional
        The initial size of the rendered figure.
    browser_style : ``{'buttons', 'slider'}``, optional
        It defines whether the selector of the objects will have the form of
        plus/minus buttons or a slider.
    custom_info_callback: `function` or ``None``, optional
        If not None, it should be a function that accepts a landmark group and
        returns a list of custom messages to be printed per landmark group.
        Each custom message will be printed in a separate line.
    """
    # Make sure that landmarks is a list even with one landmark manager member
    if isinstance(landmarks, LandmarkManager):
        landmarks = [landmarks]

    # Get the number of landmark managers
    n_landmarks = len(landmarks)

    # Define the styling options
    main_style = "info"

    output = ipywidgets.Output()

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        # get selected index and selected group
        i = landmark_number_wid.selected_values if n_landmarks > 1 else 0
        g = landmark_options_wid.selected_values["landmarks"]["group"]

        if landmark_options_wid.selected_values["landmarks"]["render_landmarks"]:
            # get shape
            shape = landmarks[i][g]

            # Create options dictionary
            options = dict()
            options.update(landmark_options_wid.selected_values["lines"])
            options.update(landmark_options_wid.selected_values["markers"])
            options["image_view"] = landmark_options_wid.selected_values["image_view"]
            options.update(renderer_options_wid.selected_values["numbering_matplotlib"])
            options.update(renderer_options_wid.selected_values["axes"])

            # Correct options based on the type of the shape
            if hasattr(shape, "labels"):
                # If the shape is a LabelledPointUndirectedGraph ...
                # ...use the legend options
                options.update(renderer_options_wid.selected_values["legend"])
                # ...use with_labels
                options["with_labels"] = landmark_options_wid.selected_values[
                    "landmarks"
                ]["with_labels"]
                # ...correct colours
                line_colour = []
                marker_face_colour = []
                marker_edge_colour = []
                for lbl in options["with_labels"]:
                    id = shape.labels.index(lbl)
                    line_colour.append(options["line_colour"][id])
                    marker_face_colour.append(options["marker_face_colour"][id])
                    marker_edge_colour.append(options["marker_edge_colour"][id])
                options["line_colour"] = line_colour
                options["marker_face_colour"] = marker_face_colour
                options["marker_edge_colour"] = marker_edge_colour
            else:
                # If shape is PointCloud, TriMesh or PointGraph
                # ...correct colours
                options["line_colour"] = options["line_colour"][0]
                options["marker_face_colour"] = options["marker_face_colour"][0]
                options["marker_edge_colour"] = options["marker_edge_colour"][0]

            # Get figure size
            new_figure_size = (
                renderer_options_wid.selected_values["zoom_one"] * figure_size[0],
                renderer_options_wid.selected_values["zoom_one"] * figure_size[1],
            )

            # Render shape with selected options
            save_figure_wid.renderer = shape.view(
                figure_id=save_figure_wid.renderer.figure_id,
                new_figure=False,
                figure_size=new_figure_size,
                **options
            )

            # Force rendering
            save_figure_wid.renderer.force_draw()
        else:
            output.clear_output()

        # update info text widget
        update_info(landmarks[i], g, custom_info_callback=custom_info_callback)

    # Define function that updates the info text
    def update_info(landmarks, group, custom_info_callback=None):
        if group is not None:
            min_b, max_b = landmarks[group].bounds()
            rang = landmarks[group].range()
            cm = landmarks[group].centre()
            text_per_line = [
                "> {} landmark points".format(landmarks[group].n_points),
                "> {}".format(name_of_callable(landmarks[group])),
                "> Bounds: [{0:.1f}-{1:.1f}]W, [{2:.1f}-{3:.1f}]H".format(
                    min_b[0], max_b[0], min_b[1], max_b[1]
                ),
                "> Range: {0:.1f}W, {1:.1f}H".format(rang[0], rang[1]),
                "> Centre of mass: ({0:.1f}, {1:.1f})".format(cm[0], cm[1]),
                "> Norm: {0:.2f}".format(landmarks[group].norm()),
            ]
            if custom_info_callback is not None:
                # iterate over the list of messages returned by the callback
                # function and append them in the text_per_line.
                for msg in custom_info_callback(landmarks[group]):
                    text_per_line.append("> {}".format(msg))
        else:
            text_per_line = ["No landmarks available."]

        info_wid.set_widget_state(text_per_line=text_per_line)

    # Create widgets
    groups_keys, labels_keys = extract_group_labels_from_landmarks(landmarks[0])
    first_label = labels_keys[0] if labels_keys else None
    landmark_options_wid = LandmarkOptionsWidget(
        group_keys=groups_keys,
        labels_keys=labels_keys,
        type="2D",
        render_function=render_function,
    )
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=["zoom_one", "axes", "numbering_matplotlib", "legend"],
        labels=first_label,
        axes_x_limits=0.1,
        axes_y_limits=0.1,
        render_function=render_function,
    )
    info_wid = TextPrintWidget(text_per_line=[""])
    save_figure_wid = SaveMatplotlibFigureOptionsWidget()

    # Group widgets
    if n_landmarks > 1:
        # Define function that updates options' widgets state
        def update_widgets(change):
            # Get new groups and labels
            i = landmark_number_wid.selected_values
            g_keys, l_keys = extract_group_labels_from_landmarks(landmarks[i])

            # Update landmarks options
            landmark_options_wid.set_widget_state(
                group_keys=g_keys, labels_keys=l_keys, allow_callback=True
            )

        # Landmark selection slider
        index = {"min": 0, "max": n_landmarks - 1, "step": 1, "index": 0}
        landmark_number_wid = AnimationOptionsWidget(
            index,
            render_function=update_widgets,
            index_style=browser_style,
            interval=0.2,
            description="Shape",
            loop_enabled=True,
            continuous_update=False,
        )

        # Header widget
        logo_wid = LogoWidget(style=main_style)
        logo_wid.layout.margin = "0px 10px 0px 0px"
        header_wid = ipywidgets.HBox([logo_wid, landmark_number_wid])
        header_wid.layout.align_items = "center"
        header_wid.layout.margin = "0px 0px 10px 0px"
    else:
        # Header widget
        header_wid = LogoWidget(style=main_style)
        header_wid.layout.margin = "0px 10px 0px 0px"
    options_box = ipywidgets.Tab(
        children=[info_wid, landmark_options_wid, renderer_options_wid, save_figure_wid]
    )
    tab_titles = ["Info", "Landmarks", "Renderer", "Export"]
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)

    output.layout.align_self = "center"
    wid = ipywidgets.VBox([header_wid, options_box, output])

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})


def visualize_landmarks_3d(
    landmarks, browser_style="buttons", custom_info_callback=None
):
    r"""
    Widget that allows browsing through a `list` of
    `menpo.landmark.LandmarkManager` (or subclass) objects. The landmark
    managers can have a combination of different attributes, e.g.
    landmark groups and labels etc.

    Parameters
    ----------
    landmarks : `list` of `menpo.landmark.LandmarkManager` or subclass
        The `list` of landmark managers to be visualized.
    browser_style : ``{'buttons', 'slider'}``, optional
        It defines whether the selector of the objects will have the form of
        plus/minus buttons or a slider.
    custom_info_callback: `function` or ``None``, optional
        If not None, it should be a function that accepts a landmark group and
        returns a list of custom messages to be printed per landmark group.
        Each custom message will be printed in a separate line.
    """
    # Make sure that landmarks is a list even with one landmark manager member
    if not isinstance(landmarks, list):
        landmarks = [landmarks]

    # Get the number of landmark managers
    n_landmarks = len(landmarks)

    # Define the styling options
    main_style = "info"

    output = ipywidgets.Output()

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        save_figure_wid.renderer.clear_figure()

        # get selected index and selected group
        i = landmark_number_wid.selected_values if n_landmarks > 1 else 0
        g = landmark_options_wid.selected_values["landmarks"]["group"]

        # update info text widget
        update_info(landmarks[i], g, custom_info_callback=custom_info_callback)

        if landmark_options_wid.selected_values["landmarks"]["render_landmarks"]:
            # get shape
            shape = landmarks[i][g]

            options = dict()
            if isinstance(shape, TriMesh):
                # Note that 3D TriMesh has a totally different set of options
                # compared to any other PointCloud or PointGraph. However, in
                # order for visualize_landmarks_3d to support TriMeshes, we
                # simply use the options that are common. This means that most
                # of the widget's options will have no effect on rendering...
                options["mesh_type"] = "wireframe"
                if landmark_options_wid.selected_values["markers"]["render_markers"]:
                    options["mesh_type"] = "fancymesh"
                options["line_width"] = landmark_options_wid.selected_values["lines"][
                    "line_width"
                ]
                options["colour"] = landmark_options_wid.selected_values["lines"][
                    "line_colour"
                ][0]
                options["marker_style"] = landmark_options_wid.selected_values[
                    "markers"
                ]["marker_style"]
                options["marker_size"] = landmark_options_wid.selected_values[
                    "markers"
                ]["marker_size"]
                options["marker_resolution"] = landmark_options_wid.selected_values[
                    "markers"
                ]["marker_resolution"]
                options["step"] = landmark_options_wid.selected_values["markers"][
                    "step"
                ]
            else:
                options.update(landmark_options_wid.selected_values["lines"])
                options.update(landmark_options_wid.selected_values["markers"])
                options.update(renderer_options_wid.selected_values["numbering_mayavi"])

                # Correct options based on the type of the shape
                if hasattr(shape, "labels"):
                    # If the shape is a LabelledPointUndirectedGraph ...
                    # ...use with_labels
                    options["with_labels"] = landmark_options_wid.selected_values[
                        "landmarks"
                    ]["with_labels"]
                    # ...correct colours
                    line_colour = []
                    marker_colour = []
                    for lbl in options["with_labels"]:
                        idx = shape.labels.index(lbl)
                        line_colour.append(options["line_colour"][idx])
                        marker_colour.append(options["marker_colour"][idx])
                    options["line_colour"] = line_colour
                    options["marker_colour"] = marker_colour
                else:
                    # If shape is PointCloud, TriMesh or PointGraph
                    # ...correct colours
                    options["line_colour"] = options["line_colour"][0]
                    options["marker_colour"] = options["marker_colour"][0]

            # Render shape with selected options
            save_figure_wid.renderer = shape.view(
                figure_id=save_figure_wid.renderer.figure_id,
                new_figure=False,
                alpha=1.0,
                **options
            )

            # Force rendering
            save_figure_wid.renderer.force_draw()
        else:
            output.clear_output()

    # Define function that updates the info text
    def update_info(landmarks, group, custom_info_callback=None):
        if group is not None:
            min_b, max_b = landmarks[group].bounds()
            rang = landmarks[group].range()
            cm = landmarks[group].centre()
            text_per_line = [
                "> {} landmark points".format(landmarks[group].n_points),
                "> {}".format(name_of_callable(landmarks[group])),
                "> Bounds: [{0:.1f}-{1:.1f}]X, [{2:.1f}-{3:.1f}]Y, "
                "[{4:.1f}-{5:.1f}]Z".format(
                    min_b[0], max_b[0], min_b[1], max_b[1], min_b[2], max_b[2]
                ),
                "> Range: {0:.1f}X, {1:.1f}Y, {2:.1f}Z".format(
                    rang[0], rang[1], rang[2]
                ),
                "> Centre of mass: ({0:.1f}X, {1:.1f}Y, {2:.1f}Z)".format(
                    cm[0], cm[1], cm[2]
                ),
                "> Norm: {0:.2f}".format(landmarks[group].norm()),
            ]
            if custom_info_callback is not None:
                # iterate over the list of messages returned by the callback
                # function and append them in the text_per_line.
                for msg in custom_info_callback(landmarks[group]):
                    text_per_line.append("> {}".format(msg))
        else:
            text_per_line = ["No landmarks available."]

        info_wid.set_widget_state(text_per_line=text_per_line)

    # Create widgets
    groups_keys, labels_keys = extract_group_labels_from_landmarks(landmarks[0])
    first_label = labels_keys[0] if labels_keys else None
    landmark_options_wid = LandmarkOptionsWidget(
        group_keys=groups_keys,
        labels_keys=labels_keys,
        type="3D",
        render_function=render_function,
    )
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=["numbering_mayavi"],
        labels=first_label,
        render_function=render_function,
    )
    info_wid = TextPrintWidget(text_per_line=[""])
    save_figure_wid = SaveMayaviFigureOptionsWidget()

    # Group widgets
    if n_landmarks > 1:
        # Define function that updates options' widgets state
        def update_widgets(change):
            # Get new groups and labels
            i = landmark_number_wid.selected_values
            g_keys, l_keys = extract_group_labels_from_landmarks(landmarks[i])

            # Update landmarks options
            landmark_options_wid.set_widget_state(
                group_keys=g_keys, labels_keys=l_keys, allow_callback=True
            )

        # Landmark selection slider
        index = {"min": 0, "max": n_landmarks - 1, "step": 1, "index": 0}
        landmark_number_wid = AnimationOptionsWidget(
            index,
            render_function=update_widgets,
            index_style=browser_style,
            interval=0.2,
            description="Shape",
            loop_enabled=True,
            continuous_update=False,
        )

        # Header widget
        logo_wid = LogoWidget(style=main_style)
        logo_wid.layout.margin = "0px 10px 0px 0px"
        header_wid = ipywidgets.HBox([logo_wid, landmark_number_wid])
        header_wid.layout.align_items = "center"
        header_wid.layout.margin = "0px 0px 10px 0px"
    else:
        # Header widget
        header_wid = LogoWidget(style=main_style)
        header_wid.layout.margin = "0px 10px 0px 0px"
    options_box = ipywidgets.Tab(
        children=[info_wid, landmark_options_wid, renderer_options_wid, save_figure_wid]
    )
    tab_titles = ["Info", "Landmarks", "Renderer", "Export"]
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)

    output.layout.align_self = "center"
    wid = ipywidgets.VBox([header_wid, options_box, output])

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})
    print_dynamic("")


def visualize_meshes_3d(meshes, browser_style="buttons", custom_info_callback=None):
    r"""
    Widget that allows browsing through a `list` of 3D meshes. The supported
    objects are:

            ==================================
            Object
            ==================================
            `menpo.shape.TriMesh`
            `menpo.shape.ColouredTriMesdh`
            `menpo.shape.TexturedTriMesh`
            ==================================

    Any instance of the above can be combined in the input `list`.

    Parameters
    ----------
    meshes : `list`
        The `list` of objects to be visualized. It can contain a combination of

            ==================================
            Object
            ==================================
            `menpo.shape.TriMesh`
            `menpo.shape.ColouredTriMesdh`
            `menpo.shape.TexturedTriMesh`
            ==================================

        or subclasses of those.
    browser_style : ``{'buttons', 'slider'}``, optional
        It defines whether the selector of the objects will have the form of
        plus/minus buttons or a slider.
    custom_info_callback: `function` or ``None``, optional
        If not ``None``, it should be a function that accepts a 3D mesh
        and returns a list of custom messages to be printed about it. Each
        custom message will be printed in a separate line.
    """
    # Make sure that meshes is a list even with one member
    if not isinstance(meshes, Sized):
        meshes = [meshes]

    # Get the number of meshes
    n_meshes = len(meshes)

    # Define the styling options
    main_style = "warning"

    output = ipywidgets.Output()

    # Define render function
    @output.capture(clear_output=True, wait=True)
    def render_function(_):
        # Clear current figure
        save_figure_wid.renderer.clear_figure()

        # Get selected mesh index
        i = mesh_number_wid.selected_values if n_meshes > 1 else 0

        # Update info text widget
        update_info(meshes[i], custom_info_callback=custom_info_callback)

        # Render instance
        save_figure_wid.renderer = meshes[i].view(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            **mesh_options_wid.selected_values
        )

        # Force rendering
        save_figure_wid.renderer.force_draw()
        output.append_display_data(save_figure_wid.renderer.figure)

    # Define function that updates the info text
    def update_info(mesh, custom_info_callback=None):
        min_b, max_b = mesh.bounds()
        rang = mesh.range()
        cm = mesh.centre()
        text_per_line = [
            "> {}".format(name_of_callable(mesh)),
            "> {} points".format(mesh.n_points),
            "> Bounds: [{0:.1f}-{1:.1f}]X, [{2:.1f}-{3:.1f}]Y, "
            "[{4:.1f}-{5:.1f}]Z".format(
                min_b[0], max_b[0], min_b[1], max_b[1], min_b[2], max_b[2]
            ),
            "> Range: {0:.1f}X, {1:.1f}Y, {2:.1f}Z".format(rang[0], rang[1], rang[2]),
            "> Centre of mass: ({0:.1f}X, {1:.1f}Y, {2:.1f}Z)".format(
                cm[0], cm[1], cm[2]
            ),
            "> Norm: {0:.2f}".format(mesh.norm()),
        ]
        if custom_info_callback is not None:
            # iterate over the list of messages returned by the callback
            # function and append them in the text_per_line.
            for msg in custom_info_callback(mesh):
                text_per_line.append("> {}".format(msg))
        info_wid.set_widget_state(text_per_line=text_per_line)

    # Create widgets
    mesh_options_wid = Mesh3DOptionsWidget(
        textured=(
            isinstance(meshes[0], ColouredTriMesh)
            or isinstance(meshes[0], TexturedTriMesh)
        ),
        render_function=render_function,
    )
    info_wid = TextPrintWidget(text_per_line=[""])
    save_figure_wid = SaveMayaviFigureOptionsWidget()

    # Group widgets
    if n_meshes > 1:
        # Define function that updates options' widgets state
        def update_widgets(change):
            i = change["new"]

            # Update shape options
            mesh_options_wid.set_widget_state(
                textured=(
                    isinstance(meshes[i], ColouredTriMesh)
                    or isinstance(meshes[i], TexturedTriMesh)
                ),
                allow_callback=True,
            )

        # selection slider
        index = {"min": 0, "max": n_meshes - 1, "step": 1, "index": 0}
        mesh_number_wid = AnimationOptionsWidget(
            index,
            render_function=update_widgets,
            index_style=browser_style,
            interval=0.2,
            description="Mesh",
            loop_enabled=True,
            continuous_update=False,
        )

        # Header widget
        logo_wid = LogoWidget(style=main_style)
        logo_wid.layout.margin = "0px 10px 0px 0px"
        header_wid = ipywidgets.HBox([logo_wid, mesh_number_wid])
        header_wid.layout.align_items = "center"
        header_wid.layout.margin = "0px 0px 10px 0px"
    else:
        # Header widget
        header_wid = LogoWidget(style=main_style)
        header_wid.layout.margin = "0px 10px 0px 0px"
    options_box = ipywidgets.Tab([info_wid, mesh_options_wid, save_figure_wid])
    tab_titles = ["Info", "Mesh", "Export"]
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)

    output.layout.align_self = "center"
    wid = ipywidgets.VBox([header_wid, options_box, output])

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})
    print_dynamic("")


def visualize_images(
    images, figure_size=(7, 7), browser_style="buttons", custom_info_callback=None
):
    r"""
    Widget that allows browsing through a `list` of `menpo.image.Image` (or
    subclass) objects. The images can have a combination of different
    attributes, e.g. masked or not, landmarked or not, without multiple
    landmark groups and labels etc.

    Parameters
    ----------
    images : `list` of `menpo.image.Image` or subclass
        The `list` of images to be visualized.
    figure_size : (`int`, `int`), optional
        The initial size of the rendered figure.
    browser_style : ``{'buttons', 'slider'}``, optional
        It defines whether the selector of the objects will have the form of
        plus/minus buttons or a slider.
    custom_info_callback: `function` or ``None``, optional
        If not None, it should be a function that accepts an image and returns
        a list of custom messages to be printed per image. Each custom message
        will be printed in a separate line.
    """
    # Make sure that images is a list even with one member
    if not isinstance(images, Sized):
        images = [images]

    # Get the number of images
    n_images = len(images)

    # Define the styling options
    main_style = "info"

    output = ipywidgets.Output()

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        # get selected index and selected group
        i = image_number_wid.selected_values if n_images > 1 else 0
        g = landmark_options_wid.selected_values["landmarks"]["group"]

        # check if image is masked
        image_is_masked = isinstance(images[i], MaskedImage)

        # Create options dictionary
        options = dict()
        options.update(landmark_options_wid.selected_values["lines"])
        options.update(landmark_options_wid.selected_values["markers"])
        options.update(renderer_options_wid.selected_values["numbering_matplotlib"])
        options.update(renderer_options_wid.selected_values["axes"])
        options.update(renderer_options_wid.selected_values["legend"])
        options.update(image_options_wid.selected_values)
        options.update(landmark_options_wid.selected_values["landmarks"])

        # Correct options based on the type of the shape
        if images[i].has_landmarks and hasattr(images[i].landmarks[g], "labels"):
            # If the shape is a LabelledPointUndirectedGraph ...
            # ...correct colours
            line_colour = []
            marker_face_colour = []
            marker_edge_colour = []
            for lbl in options["with_labels"]:
                id = images[i].landmarks[g].labels.index(lbl)
                line_colour.append(options["line_colour"][id])
                marker_face_colour.append(options["marker_face_colour"][id])
                marker_edge_colour.append(options["marker_edge_colour"][id])
            options["line_colour"] = line_colour
            options["marker_face_colour"] = marker_face_colour
            options["marker_edge_colour"] = marker_edge_colour
        else:
            # If shape is PointCloud, TriMesh or PointGraph
            # ...correct colours
            options["line_colour"] = options["line_colour"][0]
            options["marker_face_colour"] = options["marker_face_colour"][0]
            options["marker_edge_colour"] = options["marker_edge_colour"][0]

        # Get figure size
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * figure_size[0],
            renderer_options_wid.selected_values["zoom_one"] * figure_size[1],
        )

        # Render shape with selected options
        save_figure_wid.renderer = render_image(
            image=images[i],
            renderer=save_figure_wid.renderer,
            image_is_masked=image_is_masked,
            figure_size=new_figure_size,
            **options
        )

        # Update info
        update_info(
            images[i], image_is_masked, g, custom_info_callback=custom_info_callback
        )

    # Define function that updates the info text
    def update_info(img, image_is_masked, group, custom_info_callback=None):
        # Prepare masked (or non-masked) string
        masked_str = "Masked Image" if image_is_masked else "Image"
        # Get image path, if available
        path_str = img.path if hasattr(img, "path") else "No path available"
        # Create text lines
        text_per_line = [
            "> {} of size {} with {} channel{}".format(
                masked_str, img._str_shape(), img.n_channels, "s" * (img.n_channels > 1)
            ),
            "> Path: '{}'".format(path_str),
        ]
        if image_is_masked:
            text_per_line.append(
                "> {} masked pixels (attached mask {:.1%} true)".format(
                    img.n_true_pixels(), img.mask.proportion_true()
                )
            )
        text_per_line.append(
            "> min={:.3f}, max={:.3f}".format(img.pixels.min(), img.pixels.max())
        )
        if img.has_landmarks:
            text_per_line.append(
                "> {} landmark points".format(img.landmarks[group].n_points)
            )
        if custom_info_callback is not None:
            # iterate over the list of messages returned by the callback
            # function and append them in the text_per_line.
            for msg in custom_info_callback(img):
                text_per_line.append("> {}".format(msg))
        info_wid.set_widget_state(text_per_line=text_per_line)

    # Create widgets
    groups_keys, labels_keys = extract_groups_labels_from_image(images[0])
    first_label = labels_keys[0] if labels_keys else None
    image_options_wid = ImageOptionsWidget(
        n_channels=images[0].n_channels,
        image_is_masked=isinstance(images[0], MaskedImage),
        render_function=render_function,
    )
    landmark_options_wid = LandmarkOptionsWidget(
        group_keys=groups_keys,
        labels_keys=labels_keys,
        type="2D",
        render_function=render_function,
    )
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=["zoom_one", "axes", "numbering_matplotlib", "legend"],
        labels=first_label,
        axes_x_limits=None,
        axes_y_limits=None,
        render_function=render_function,
    )
    info_wid = TextPrintWidget(text_per_line=[""])
    save_figure_wid = SaveMatplotlibFigureOptionsWidget()

    # Define function that updates options' widgets state
    def update_widgets(change):
        # Get new groups and labels, then update landmark options
        i = image_number_wid.selected_values
        g_keys, l_keys = extract_groups_labels_from_image(images[i])

        # Update landmarks options
        landmark_options_wid.set_widget_state(
            group_keys=g_keys, labels_keys=l_keys, allow_callback=False
        )

        # Update channels options
        image_options_wid.set_widget_state(
            n_channels=images[i].n_channels,
            image_is_masked=isinstance(images[i], MaskedImage),
            allow_callback=True,
        )

    # Image selection slider
    index = {"min": 0, "max": n_images - 1, "step": 1, "index": 0}
    image_number_wid = AnimationOptionsWidget(
        index,
        render_function=update_widgets,
        index_style=browser_style,
        interval=0.2,
        description="Image",
        loop_enabled=True,
        continuous_update=False,
    )

    # Header widget
    logo_wid = LogoWidget(style=main_style)
    logo_wid.layout.margin = "0px 10px 0px 0px"
    header_wid = ipywidgets.HBox([logo_wid, image_number_wid])
    header_wid.layout.align_items = "center"
    header_wid.layout.margin = "0px 0px 10px 0px"

    options_box = ipywidgets.Tab(
        children=[
            info_wid,
            image_options_wid,
            landmark_options_wid,
            renderer_options_wid,
            save_figure_wid,
        ]
    )
    tab_titles = ["Info", "Image", "Landmarks", "Renderer", "Export"]
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)

    # Set widget's style
    output.layout.align_self = "center"
    wid = ipywidgets.VBox([header_wid, options_box, output])
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})


def visualize_patches(
    patches,
    patch_centers,
    figure_size=(7, 7),
    browser_style="buttons",
    custom_info_callback=None,
):
    r"""
    Widget that allows browsing through a `list` of patch-based images.

    The patches argument can have any of the two formats that are returned from
    the `extract_patches()` and `extract_patches_around_landmarks()` methods
    of `menpo.image.Image`. Specifically it can be:

        1. ``(n_center, n_offset, self.n_channels, patch_shape)`` `ndarray`
        2. `list` of ``n_center * n_offset`` `menpo.image.Image` objects

    The patches can have a combination of different attributes, e.g. number of
    centers, number of offsets, number of channels etc.

    Parameters
    ----------
    patches : `list`
        The `list` of patch-based images to be visualized. It can consist of
        objects with any of the two formats that are returned from the
        `extract_patches()` and `extract_patches_around_landmarks()` methods.
        Specifically, it can either be an
        ``(n_center, n_offset, self.n_channels, patch_shape)`` `ndarray` or a
        `list` of ``n_center * n_offset`` `menpo.image.Image` objects.
    patch_centers : `list` of `menpo.shape.PointCloud`
        The centers to set the patches around. If the `list` has only one
        `menpo.shape.PointCloud` then this will be used for all patches members.
        Otherwise, it needs to have the same length as patches.
    figure_size : (`int`, `int`), optional
        The initial size of the rendered figure.
    browser_style : ``{'buttons', 'slider'}``, optional
        It defines whether the selector of the objects will have the form of
        plus/minus buttons or a slider.
    custom_info_callback: `function` or ``None``, optional
        If not None, it should be a function that accepts an image and returns
        a list of custom messages to be printed per image. Each custom message
        will be printed in a separate line.
    """
    # Make sure that patches is a list even with one member
    if (isinstance(patches, list) and isinstance(patches[0], Image)) or not isinstance(
        patches, list
    ):
        patches = [patches]

    # Make sure that patch_centers is a list even with one shape
    if not isinstance(patch_centers, list):
        patch_centers = [patch_centers] * len(patches)
    elif isinstance(patch_centers, list) and len(patch_centers) == 1:
        patch_centers *= len(patches)

    # Make sure all patch-based images are in the single array format
    for i in range(len(patches)):
        if isinstance(patches[i], list):
            patches[i] = _convert_patches_list_to_single_array(
                patches[i], patch_centers[i].n_points
            )

    # Get the number of patch_based images
    n_patches = len(patches)

    # Define the styling options
    main_style = "info"

    output = ipywidgets.Output()

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        # get selected index
        i = image_number_wid.selected_values if n_patches > 1 else 0

        # Create options dictionary
        options = dict()
        options.update(shape_options_wid.selected_values["lines"])
        options.update(shape_options_wid.selected_values["markers"])
        options.update(renderer_options_wid.selected_values["numbering_matplotlib"])
        options.update(renderer_options_wid.selected_values["axes"])
        image_options = dict(image_options_wid.selected_values)
        del image_options["masked_enabled"]
        options.update(image_options)
        options.update(patch_options_wid.selected_values)
        options["line_colour"] = options["line_colour"][0]
        options["marker_face_colour"] = options["marker_face_colour"][0]
        options["marker_edge_colour"] = options["marker_edge_colour"][0]

        # Get figure size
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * figure_size[0],
            renderer_options_wid.selected_values["zoom_one"] * figure_size[1],
        )

        # Render image with selected options
        save_figure_wid.renderer = render_patches(
            patches=patches[i],
            patch_centers=patch_centers[i],
            renderer=save_figure_wid.renderer,
            figure_size=new_figure_size,
            **options
        )

        # update info text widget
        update_info(patches[i], custom_info_callback=custom_info_callback)

    # Define function that updates the info text
    def update_info(ptchs, custom_info_callback=None):
        text_per_line = [
            "> Patch-Based Image with {} patche{} and {} offset{}.".format(
                ptchs.shape[0],
                "s" * (ptchs.shape[0] > 1),
                ptchs.shape[1],
                "s" * (ptchs.shape[1] > 1),
            ),
            "> Each patch has size {}H x {}W with {} channel{}.".format(
                ptchs.shape[3],
                ptchs.shape[4],
                ptchs.shape[2],
                "s" * (ptchs.shape[2] > 1),
            ),
            "> min={:.3f}, max={:.3f}".format(ptchs.min(), ptchs.max()),
        ]
        if custom_info_callback is not None:
            # iterate over the list of messages returned by the callback
            # function and append them in the text_per_line.
            for msg in custom_info_callback(ptchs):
                text_per_line.append("> {}".format(msg))
        info_wid.set_widget_state(text_per_line=text_per_line)

    # Create widgets
    shape_options_wid = Shape2DOptionsWidget(labels=None, render_function=None)
    shape_options_wid.line_options_wid.render_lines_switch.button_wid.value = False
    shape_options_wid.add_render_function(render_function)
    patch_options_wid = PatchOptionsWidget(
        n_patches=patches[0].shape[0],
        n_offsets=patches[0].shape[1],
        render_function=render_function,
    )
    image_options_wid = ImageOptionsWidget(
        n_channels=patches[0].shape[2], image_is_masked=False, render_function=None
    )
    image_options_wid.interpolation_checkbox.button_wid.value = False
    image_options_wid.add_render_function(render_function)
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=["zoom_one", "axes", "numbering_matplotlib"],
        labels=None,
        axes_x_limits=None,
        axes_y_limits=None,
        render_function=render_function,
    )
    info_wid = TextPrintWidget(text_per_line=[""])
    save_figure_wid = SaveMatplotlibFigureOptionsWidget()

    # Group widgets
    if n_patches > 1:
        # Define function that updates options' widgets state
        def update_widgets(change):
            # Selected object
            i = image_number_wid.selected_values

            # Update patch options
            patch_options_wid.set_widget_state(
                n_patches=patches[i].shape[0],
                n_offsets=patches[i].shape[1],
                allow_callback=False,
            )

            # Update channels options
            image_options_wid.set_widget_state(
                n_channels=patches[i].shape[2],
                image_is_masked=False,
                allow_callback=True,
            )

        # Image selection slider
        index = {"min": 0, "max": n_patches - 1, "step": 1, "index": 0}
        image_number_wid = AnimationOptionsWidget(
            index,
            render_function=update_widgets,
            index_style=browser_style,
            interval=0.2,
            description="Image",
            loop_enabled=True,
            continuous_update=False,
        )

        # Header widget
        logo_wid = LogoWidget(style=main_style)
        logo_wid.layout.margin = "0px 10px 0px 0px"
        header_wid = ipywidgets.HBox([logo_wid, image_number_wid])
        header_wid.layout.align_items = "center"
        header_wid.layout.margin = "0px 0px 10px 0px"
    else:
        # Header widget
        header_wid = LogoWidget(style=main_style)
        header_wid.layout.margin = "0px 10px 0px 0px"
    options_box = ipywidgets.Tab(
        children=[
            info_wid,
            patch_options_wid,
            image_options_wid,
            shape_options_wid,
            renderer_options_wid,
            save_figure_wid,
        ]
    )
    tab_titles = ["Info", "Patches", "Image", "Shape", "Renderer", "Export"]
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)

    output.layout.align_self = "center"
    wid = ipywidgets.VBox([header_wid, options_box, output])

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})


def plot_graph(x_axis, y_axis, legend_entries=None, figure_size=(9, 5)):
    r"""
    Widget that allows plotting various curves in a graph.

    The widget has options tabs regarding the graph and the renderer (lines,
    markers, legend, figure, axes, grid) and saving the figure to file.

    Parameters
    ----------
    x_axis : `list` of `float`
        The values of the horizontal axis. Note that these values are common for
        all the curves.
    y_axis : `list` of `lists` of `float`
        A `list` that stores a `list` of values to be plotted for each curve.
    legend_entries : `list` or `str` or ``None``, optional
        The `list` of names that will appear on the legend for each curve. If
        ``None``, then the names format is ``curve {}.format(i)``.
    figure_size : (`int`, `int`), optional
        The initial size of the rendered figure.
    """
    from menpo.visualize import plot_curve

    # Get number of curves to be plotted
    n_curves = len(y_axis)

    # Define the styling options
    main_style = "danger"

    output = ipywidgets.Output()

    # Parse options
    if legend_entries is None:
        legend_entries = ["curve {}".format(i) for i in range(n_curves)]

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        # plot with selected options
        opts = plot_wid.selected_values.copy()
        new_figure_size = (
            plot_wid.selected_values["zoom"][0] * figure_size[0],
            plot_wid.selected_values["zoom"][1] * figure_size[1],
        )
        del opts["zoom"]
        save_figure_wid.renderer = plot_curve(
            x_axis=x_axis,
            y_axis=y_axis,
            figure_size=new_figure_size,
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            **opts
        )

        # show plot
        save_figure_wid.renderer.force_draw()

    # Create widgets
    plot_wid = PlotMatplotlibOptionsWidget(
        legend_entries=legend_entries, render_function=render_function
    )
    save_figure_wid = SaveMatplotlibFigureOptionsWidget()

    # Group widgets
    logo = LogoWidget(style=main_style)
    logo.layout.margin = "0px 10px 0px 0px"
    tmp_children = list(plot_wid.tab_box.children)
    tmp_children.append(save_figure_wid)
    plot_wid.tab_box.children = tmp_children
    plot_wid.tab_box.set_title(0, "Labels")
    plot_wid.tab_box.set_title(1, "Style")
    plot_wid.tab_box.set_title(2, "Legend")
    plot_wid.tab_box.set_title(3, "Axes")
    plot_wid.tab_box.set_title(4, "Zoom")
    plot_wid.tab_box.set_title(5, "Grid")
    plot_wid.tab_box.set_title(6, "Export")

    # Display final widget
    output.layout.align_self = "center"
    wid = ipywidgets.HBox([logo, plot_wid, output])
    wid.box_style = main_style
    wid.layout.border = "2px solid" + map_styles_to_hex_colours(main_style)
    plot_wid.container.border = "0px"
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})


def save_matplotlib_figure(renderer):
    r"""
    Widget that allows to save a figure, which was generated with Matplotlib,
    to file.

    Parameters
    ----------
    renderer : `menpo.visualize.viewmatplotlib.MatplotlibRenderer`
        The Matplotlib renderer object.
    """
    output = ipywidgets.Output()
    with output:
        # Create sub-widgets
        logo_wid = LogoWidget()
        logo_wid.layout.margin = "0px 10px 0px 0px"
        save_figure_wid = SaveMatplotlibFigureOptionsWidget(renderer, style="warning")

    output.layout.align_self = "center"
    wid = ipywidgets.HBox([logo_wid, save_figure_wid, output])

    # Display widget
    ipydisplay.display(wid)


def save_mayavi_figure(renderer):
    r"""
    Widget that allows to save a figure, which was generated with Mayavi,
    to file.

    Parameters
    ----------
    renderer : `menpo3d.visualize.viewmayavi.MayaviRenderer`
        The Mayavi renderer object.
    """
    output = ipywidgets.Output()
    with output:
        # Create sub-widgets
        logo_wid = LogoWidget()
        logo_wid.layout.margin = "0px 10px 0px 0px"
        save_figure_wid = SaveMayaviFigureOptionsWidget(renderer, style="warning")

    output.layout.align_self = "center"
    wid = ipywidgets.HBox([logo_wid, save_figure_wid, output])

    # Display widget
    ipydisplay.display(wid)


def visualize_shape_model_2d(
    shape_model,
    n_parameters=5,
    mode="multiple",
    parameters_bounds=(-3.0, 3.0),
    figure_size=(7, 7),
):
    r"""
    Widget that allows the dynamic visualization of a multi-scale linear
    statistical 2D shape model.

    Parameters
    ----------
    shape_model : `list` of `menpo.shape.PCAModel` or `subclass`
        The multi-scale shape model to be visualized. Note that each level can
        have different number of components.
    n_parameters : `int` or `list` of `int` or ``None``, optional
        The number of principal components to be used for the parameters
        sliders. If `int`, then the number of sliders per level is the minimum
        between `n_parameters` and the number of active components per level.
        If `list` of `int`, then a number of sliders is defined per level.
        If ``None``, all the active components per level will have a slider.
    mode : ``{'single', 'multiple'}``, optional
        If ``'single'``, then only a single slider is constructed along with a
        drop down menu. If ``'multiple'``, then a slider is constructed for each
        parameter.
    parameters_bounds : (`float`, `float`), optional
        The minimum and maximum bounds, in std units, for the sliders.
    figure_size : (`int`, `int`), optional
        The size of the plotted figures.
    """
    from menpo.visualize.viewmatplotlib import _set_axes_options, _parse_axes_limits

    # Make sure that shape_model is a list even with one member
    if not isinstance(shape_model, list):
        shape_model = [shape_model]

    # Get the number of levels (i.e. number of shape models)
    n_levels = len(shape_model)

    # Define the styling options
    main_style = "warning"

    # Get the maximum number of components per level
    max_n_params = [sp.n_active_components for sp in shape_model]

    # Check the given number of parameters (the returned n_parameters is a list
    # of len n_scales)
    n_parameters = check_n_parameters(n_parameters, n_levels, max_n_params)

    output = ipywidgets.Output()

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        # Get selected level
        level = 0
        if n_levels > 1:
            level = level_wid.value

        # Compute weights
        parameters = model_parameters_wid.selected_values
        weights = parameters * shape_model[level].eigenvalues[: len(parameters)] ** 0.5

        # Get the mean
        mean = shape_model[level].mean()

        # Create options dictionary
        options = dict()
        options.update(shape_options_wid.selected_values["lines"])
        options.update(shape_options_wid.selected_values["markers"])
        options["image_view"] = shape_options_wid.selected_values["image_view"]
        options.update(renderer_options_wid.selected_values["numbering_matplotlib"])
        options.update(renderer_options_wid.selected_values["axes"])

        # Correct options based on the type of the shape
        if hasattr(mean, "labels"):
            # If the shape is a LabelledPointUndirectedGraph ...
            # ...use the legend options
            options.update(renderer_options_wid.selected_values["legend"])
            # ...use with_labels
            options["with_labels"] = shape_options_wid.selected_values["with_labels"]
            # ...correct colours
            line_colour = []
            marker_face_colour = []
            marker_edge_colour = []
            for lbl in options["with_labels"]:
                idx = mean.labels.index(lbl)
                line_colour.append(options["line_colour"][idx])
                marker_face_colour.append(options["marker_face_colour"][idx])
                marker_edge_colour.append(options["marker_edge_colour"][idx])
            options["line_colour"] = line_colour
            options["marker_face_colour"] = marker_face_colour
            options["marker_edge_colour"] = marker_edge_colour
        else:
            # If shape is PointCloud, TriMesh or PointGraph
            # ...correct colours
            options["line_colour"] = options["line_colour"][0]
            options["marker_face_colour"] = options["marker_face_colour"][0]
            options["marker_edge_colour"] = options["marker_edge_colour"][0]

        # Get figure size
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * figure_size[0],
            renderer_options_wid.selected_values["zoom_one"] * figure_size[1],
        )

        # Render with selected options
        if mode_wid.value == 1:
            # Deformation mode
            # Compute instance
            instance = shape_model[level].instance(weights)

            # Render mean shape
            if mean_wid.selected_values:
                save_figure_wid.renderer = mean.view(
                    figure_id=save_figure_wid.renderer.figure_id,
                    new_figure=False,
                    figure_size=None,
                    image_view=options["image_view"],
                    render_lines=options["render_lines"],
                    line_colour="yellow",
                    line_style=options["line_style"],
                    line_width=options["line_width"],
                    render_markers=options["render_markers"],
                    marker_style=options["marker_style"],
                    marker_size=options["marker_size"],
                    marker_face_colour="yellow",
                    marker_edge_colour="yellow",
                    marker_edge_width=options["marker_edge_width"],
                )

            # Render instance
            save_figure_wid.renderer = instance.view(
                figure_id=save_figure_wid.renderer.figure_id,
                new_figure=False,
                figure_size=new_figure_size,
                **options
            )

            # Get instance range
            instance_range = instance.range()
        else:
            # Vectors mode
            # Compute instance
            instance_lower = shape_model[level].instance([-p for p in weights])
            instance_upper = shape_model[level].instance(weights)

            # Render mean shape
            save_figure_wid.renderer = mean.view(
                figure_id=save_figure_wid.renderer.figure_id,
                new_figure=False,
                figure_size=new_figure_size,
                **options
            )

            # Render vectors
            ax = plt.gca()
            x_min = np.Inf
            y_min = np.Inf
            x_max = -np.Inf
            y_max = -np.Inf
            for p in range(mean.n_points):
                xm = mean.points[p, 0]
                ym = mean.points[p, 1]
                xl = instance_lower.points[p, 0]
                yl = instance_lower.points[p, 1]
                xu = instance_upper.points[p, 0]
                yu = instance_upper.points[p, 1]
                if options["image_view"]:
                    # image mode
                    lines = [[(ym, xm), (yl, xl)], [(ym, xm), (yu, xu)]]
                else:
                    # point cloud mode
                    lines = [[(xm, ym), (xl, yl)], [(xm, ym), (xu, yu)]]
                lc = mc.LineCollection(
                    lines, colors=("g", "b"), linestyles="solid", linewidths=2
                )
                # update min, max
                y_min = np.min([y_min, xl, xu])
                y_max = np.max([y_max, xl, xu])
                x_min = np.min([x_min, yl, yu])
                x_max = np.max([x_max, yl, yu])

                # add collection
                ax.add_collection(lc)

            # parse axes limits
            axes_x_limits, axes_y_limits = _parse_axes_limits(
                x_min,
                x_max,
                y_min,
                y_max,
                options["axes_x_limits"],
                options["axes_y_limits"],
            )
            _set_axes_options(
                ax,
                render_axes=options["render_axes"],
                inverted_y_axis=options["image_view"],
                axes_font_name=options["axes_font_name"],
                axes_font_size=options["axes_font_size"],
                axes_font_style=options["axes_font_style"],
                axes_font_weight=options["axes_font_weight"],
                axes_x_limits=axes_x_limits,
                axes_y_limits=axes_y_limits,
                axes_x_ticks=options["axes_x_ticks"],
                axes_y_ticks=options["axes_y_ticks"],
            )

            # Get instance range
            instance_range = mean.range()

        # Force rendering
        save_figure_wid.renderer.force_draw()

        # Update info
        update_info(level, instance_range)

    # Define function that updates the info text
    def update_info(level, instance_range):
        text_per_line = [
            "> Level {} out of {}".format(level + 1, n_levels),
            "> {} components in total".format(shape_model[level].n_components),
            "> {} active components".format(shape_model[level].n_active_components),
            "> {:.1f}% variance kept".format(shape_model[level].variance_ratio() * 100),
            "> Instance range: {:.1f} x {:.1f}".format(
                instance_range[0], instance_range[1]
            ),
            "> {} landmark points, {} features".format(
                shape_model[level].mean().n_points, shape_model[level].n_features
            ),
        ]
        info_wid.set_widget_state(text_per_line=text_per_line)

    @output.capture(clear_output=True, wait=True)
    def plot_variance(name):
        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * 10,
            renderer_options_wid.selected_values["zoom_one"] * 3,
        )
        plt.subplot(121)
        save_figure_wid.renderer = shape_model[level].plot_eigenvalues_ratio(
            figure_id=save_figure_wid.renderer.figure_id, new_figure=False
        )
        plt.subplot(122)
        save_figure_wid.renderer = shape_model[level].plot_eigenvalues_cumulative_ratio(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            figure_size=new_figure_size,
        )
        save_figure_wid.renderer.force_draw()

    # Create widgets
    mode_dict = OrderedDict()
    mode_dict["Deformation"] = 1
    mode_dict["Vectors"] = 2
    mode_wid = ipywidgets.RadioButtons(
        options=mode_dict,
        description="Mode",
        value=1,
        layout=ipywidgets.Layout(width="6cm"),
    )
    mode_wid.observe(render_function, names="value", type="change")
    mean_wid = SwitchWidget(
        selected_value=False, description="Render mean shape", switch_type="checkbox"
    )
    mean_wid.observe(render_function, names="selected_values", type="change")

    # Function that controls mean shape checkbox visibility
    def mean_visible(change):
        if change["new"] == 1:
            mean_wid.button_wid.disabled = False
        else:
            mean_wid.button_wid.disabled = True
            mean_wid.set_widget_state(False, allow_callback=False)

    mode_wid.observe(mean_visible, names="value", type="change")
    model_parameters_wid = LinearModelParametersWidget(
        n_parameters[0],
        render_function,
        params_str="Parameter ",
        mode=mode,
        params_bounds=parameters_bounds,
        params_step=0.1,
        plot_variance_visible=True,
        plot_variance_function=plot_variance,
        animation_step=0.5,
        interval=0.0,
        loop_enabled=True,
        continuous_update=False,
    )
    labels = None
    if hasattr(shape_model[0].mean(), "labels"):
        labels = shape_model[0].mean().labels
    shape_options_wid = Shape2DOptionsWidget(
        labels=labels, render_function=render_function
    )
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=["zoom_one", "axes", "numbering_matplotlib", "legend"],
        labels=None,
        axes_x_limits=0.1,
        axes_y_limits=0.1,
        render_function=render_function,
    )
    info_wid = TextPrintWidget(text_per_line=[""])
    save_figure_wid = SaveMatplotlibFigureOptionsWidget()

    # Group widgets
    if n_levels > 1:
        # Define function that updates options' widgets state
        def update_widgets(change):
            model_parameters_wid.set_widget_state(
                n_parameters=n_parameters[change["new"]],
                params_str="Parameter ",
                allow_callback=True,
            )

        # Create pyramid radiobuttons
        radio_str = OrderedDict()
        for l in range(n_levels):
            if l == 0:
                radio_str["Level {} (low)".format(l)] = l
            elif l == n_levels - 1:
                radio_str["Level {} (high)".format(l)] = l
            else:
                radio_str["Level {}".format(l)] = l
        level_wid = ipywidgets.RadioButtons(
            options=radio_str,
            description="Pyramid",
            value=n_levels - 1,
            layout=ipywidgets.Layout(width="6cm"),
        )
        level_wid.observe(update_widgets, names="value", type="change")
        level_wid.observe(render_function, names="value", type="change")
        radio_children = [level_wid, mode_wid, mean_wid]
    else:
        radio_children = [mode_wid, mean_wid]
    radio_wids = ipywidgets.VBox(radio_children)
    tmp_wid = ipywidgets.HBox([radio_wids, model_parameters_wid])
    options_box = ipywidgets.Tab(
        children=[
            tmp_wid,
            shape_options_wid,
            renderer_options_wid,
            info_wid,
            save_figure_wid,
        ]
    )
    tab_titles = ["Model", "Shape", "Renderer", "Info", "Export"]
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    logo_wid = LogoWidget(style=main_style)
    logo_wid.layout.margin = "0px 10px 0px 0px"

    output.layout.align_self = "center"
    wid = ipywidgets.VBox([logo_wid, options_box, output])

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})


def visualize_shape_model_3d(
    shape_model, n_parameters=5, mode="multiple", parameters_bounds=(-15.0, 15.0)
):
    r"""
    Widget that allows the dynamic visualization of a multi-scale linear
    statistical 3D shape model.

    Parameters
    ----------
    shape_model : `list` of `menpo.shape.PCAModel` or `subclass`
        The multi-scale shape model to be visualized. Note that each level can
        have different number of components.
    n_parameters : `int` or `list` of `int` or ``None``, optional
        The number of principal components to be used for the parameters
        sliders. If `int`, then the number of sliders per level is the minimum
        between `n_parameters` and the number of active components per level.
        If `list` of `int`, then a number of sliders is defined per level.
        If ``None``, all the active components per level will have a slider.
    mode : ``{'single', 'multiple'}``, optional
        If ``'single'``, then only a single slider is constructed along with a
        drop down menu. If ``'multiple'``, then a slider is constructed for each
        parameter.
    parameters_bounds : (`float`, `float`), optional
        The minimum and maximum bounds, in std units, for the sliders.
    """
    # Make sure that shape_model is a list even with one member
    if not isinstance(shape_model, list):
        shape_model = [shape_model]

    # Get the number of levels (i.e. number of shape models)
    n_levels = len(shape_model)

    # Check if the model is TriMesh or any other 3D shape class
    is_trimesh = isinstance(shape_model[0].template_instance, TriMesh)

    # Define the styling options
    main_style = "warning"

    # Get the maximum number of components per level
    max_n_params = [sp.n_active_components for sp in shape_model]

    # Check the given number of parameters (the returned n_parameters is a list
    # of len n_scales)
    n_parameters = check_n_parameters(n_parameters, n_levels, max_n_params)

    output = ipywidgets.Output()

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        save_figure_wid.renderer.clear_figure()

        # Get selected level
        level = 0
        if n_levels > 1:
            level = level_wid.value

        # Compute weights
        parameters = model_parameters_wid.selected_values
        weights = parameters * shape_model[level].eigenvalues[: len(parameters)] ** 0.5

        # Compute instance
        instance = shape_model[level].instance(weights)

        # Create options dictionary
        options = dict()
        if is_trimesh:
            options.update(shape_options_wid.selected_values)
        else:
            options.update(shape_options_wid.selected_values["lines"])
            options.update(shape_options_wid.selected_values["markers"])
            options.update(renderer_options_wid.selected_values["numbering_mayavi"])
            # Correct options based on the type of the shape
            if hasattr(instance, "labels"):
                # If the shape is a LabelledPointUndirectedGraph ...
                # ...use with_labels
                options["with_labels"] = shape_options_wid.selected_values[
                    "with_labels"
                ]
                # ...correct colours
                line_colour = []
                marker_colour = []
                for lbl in options["with_labels"]:
                    idx = instance.labels.index(lbl)
                    line_colour.append(options["line_colour"][idx])
                    marker_colour.append(options["marker_colour"][idx])
                options["line_colour"] = line_colour
                options["marker_colour"] = marker_colour
            else:
                # If shape is PointCloud, TriMesh or PointGraph
                # ...correct colours
                options["line_colour"] = options["line_colour"][0]
                options["marker_colour"] = options["marker_colour"][0]

        # Update info
        update_info(level, instance.range())

        # Render instance
        save_figure_wid.renderer = instance.view(
            figure_id=save_figure_wid.renderer.figure_id, new_figure=False, **options
        )

        # Force rendering
        save_figure_wid.renderer.force_draw()

    # Define function that updates the info text
    def update_info(level, instance_range):
        text_per_line = [
            "> Level {} out of {}".format(level + 1, n_levels),
            "> {} components in total".format(shape_model[level].n_components),
            "> {} active components".format(shape_model[level].n_active_components),
            "> {:.1f}% variance kept".format(shape_model[level].variance_ratio() * 100),
            "> Instance range: {:.1f} x {:.1f}".format(
                instance_range[0], instance_range[1]
            ),
            "> {} points".format(shape_model[level].mean().n_points),
        ]
        info_wid.set_widget_state(text_per_line=text_per_line)

    @output.capture(clear_output=True, wait=True)
    def plot_variance(name):
        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Render
        plt.subplot(121)
        shape_model[level].plot_eigenvalues_ratio()
        plt.subplot(122)
        shape_model[level].plot_eigenvalues_cumulative_ratio()
        plt.show()

    # Create widgets
    model_parameters_wid = LinearModelParametersWidget(
        n_parameters[0],
        render_function,
        params_str="Parameter ",
        mode=mode,
        params_bounds=parameters_bounds,
        params_step=0.1,
        plot_variance_visible=True,
        plot_variance_function=plot_variance,
        animation_step=0.5,
        interval=0.0,
        loop_enabled=True,
        continuous_update=False,
    )
    if is_trimesh:
        shape_options_wid = Mesh3DOptionsWidget(
            textured=False, render_function=render_function
        )
    else:
        labels = None
        if hasattr(shape_model[0].mean(), "labels"):
            labels = shape_model[0].mean().labels
        shape_options_wid = Shape3DOptionsWidget(
            labels=labels, render_function=render_function
        )
        renderer_options_wid = RendererOptionsWidget(
            options_tabs=["numbering_mayavi"],
            labels=None,
            render_function=render_function,
        )
    info_wid = TextPrintWidget(text_per_line=[""])
    save_figure_wid = SaveMayaviFigureOptionsWidget()

    # Group widgets
    if n_levels > 1:
        # Define function that updates options' widgets state
        def update_widgets(change):
            model_parameters_wid.set_widget_state(
                n_parameters=n_parameters[change["new"]],
                params_str="Parameter ",
                allow_callback=True,
            )

        # Create pyramid radiobuttons
        radio_str = OrderedDict()
        for l in range(n_levels):
            if l == 0:
                radio_str["Level {} (low)".format(l)] = l
            elif l == n_levels - 1:
                radio_str["Level {} (high)".format(l)] = l
            else:
                radio_str["Level {}".format(l)] = l
        level_wid = ipywidgets.RadioButtons(
            options=radio_str,
            description="Pyramid",
            value=n_levels - 1,
            layout=ipywidgets.Layout(width="6cm"),
        )
        level_wid.observe(update_widgets, names="value", type="change")
        level_wid.observe(render_function, names="value", type="change")
        tmp_wid = ipywidgets.HBox([level_wid, model_parameters_wid])
    else:
        tmp_wid = ipywidgets.HBox(children=[model_parameters_wid])
    if is_trimesh:
        options_box = ipywidgets.Tab(
            children=[tmp_wid, shape_options_wid, info_wid, save_figure_wid]
        )
        tab_titles = ["Model", "Mesh", "Info", "Export"]
    else:
        options_box = ipywidgets.Tab(
            children=[
                tmp_wid,
                shape_options_wid,
                renderer_options_wid,
                info_wid,
                save_figure_wid,
            ]
        )
        tab_titles = ["Model", "Shape", "Renderer", "Info", "Export"]
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    logo_wid = LogoWidget(style=main_style)
    logo_wid.layout.margin = "0px 10px 0px 0px"

    output.layout.align_self = "center"
    wid = ipywidgets.VBox([logo_wid, options_box, output])

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})
    print_dynamic("")


def visualize_appearance_model(
    appearance_model,
    n_parameters=5,
    mode="multiple",
    parameters_bounds=(-3.0, 3.0),
    figure_size=(7, 7),
):
    r"""
    Widget that allows the dynamic visualization of a multi-scale linear
    statistical appearance model.

    Parameters
    ----------
    appearance_model : `list` of `menpo.model.PCAModel` or subclass
        The multi-scale appearance model to be visualized. Note that each level
        can have different number of components.
    n_parameters : `int` or `list` of `int` or ``None``, optional
        The number of principal components to be used for the parameters
        sliders. If `int`, then the number of sliders per level is the minimum
        between `n_parameters` and the number of active components per level.
        If `list` of `int`, then a number of sliders is defined per level.
        If ``None``, all the active components per level will have a slider.
    mode : ``{'single', 'multiple'}``, optional
        If ``'single'``, then only a single slider is constructed along with a
        drop down menu. If ``'multiple'``, then a slider is constructed for each
        parameter.
    parameters_bounds : (`float`, `float`), optional
        The minimum and maximum bounds, in std units, for the sliders.
    figure_size : (`int`, `int`), optional
        The size of the plotted figures.
    """
    # Make sure that appearance_model is a list even with one member
    if not isinstance(appearance_model, Sized):
        appearance_model = [appearance_model]

    # Get the number of levels (i.e. number of appearance models)
    n_levels = len(appearance_model)

    # Define the styling options
    main_style = "success"

    # Get the maximum number of components per level
    max_n_params = [ap.n_active_components for ap in appearance_model]

    # Check the given number of parameters (the returned n_parameters is a list
    # of len n_scales)
    n_parameters = check_n_parameters(n_parameters, n_levels, max_n_params)

    output = ipywidgets.Output()

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Compute weights and instance
        parameters = model_parameters_wid.selected_values
        weights = (
            parameters * appearance_model[level].eigenvalues[: len(parameters)] ** 0.5
        )
        instance = appearance_model[level].instance(weights)
        image_is_masked = isinstance(instance, MaskedImage)
        g = landmark_options_wid.selected_values["landmarks"]["group"]

        # Create options dictionary
        options = dict()
        options.update(landmark_options_wid.selected_values["lines"])
        options.update(landmark_options_wid.selected_values["markers"])
        options.update(renderer_options_wid.selected_values["numbering_matplotlib"])
        options.update(renderer_options_wid.selected_values["axes"])
        options.update(renderer_options_wid.selected_values["legend"])
        options.update(image_options_wid.selected_values)
        options.update(landmark_options_wid.selected_values["landmarks"])

        # Correct options based on the type of the shape
        if instance.has_landmarks and hasattr(instance.landmarks[g], "labels"):
            # If the shape is a LabelledPointUndirectedGraph ...
            # ...correct colours
            line_colour = []
            marker_face_colour = []
            marker_edge_colour = []
            for lbl in options["with_labels"]:
                id = instance.landmarks[g].labels.index(lbl)
                line_colour.append(options["line_colour"][id])
                marker_face_colour.append(options["marker_face_colour"][id])
                marker_edge_colour.append(options["marker_edge_colour"][id])
            options["line_colour"] = line_colour
            options["marker_face_colour"] = marker_face_colour
            options["marker_edge_colour"] = marker_edge_colour
        else:
            # If shape is PointCloud, TriMesh or PointGraph
            # ...correct colours
            options["line_colour"] = options["line_colour"][0]
            options["marker_face_colour"] = options["marker_face_colour"][0]
            options["marker_edge_colour"] = options["marker_edge_colour"][0]

        # Get figure size
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * figure_size[0],
            renderer_options_wid.selected_values["zoom_one"] * figure_size[1],
        )

        # Render shape with selected options
        save_figure_wid.renderer = render_image(
            image=instance,
            renderer=save_figure_wid.renderer,
            image_is_masked=image_is_masked,
            figure_size=new_figure_size,
            **options
        )

        # Update info
        update_info(instance, level, g)

    # Define function that updates the info text
    def update_info(image, level, group):
        lvl_app_mod = appearance_model[level]
        lp = 0 if group is None else image.landmarks[group].n_points
        text_per_line = [
            "> Level: {} out of {}.".format(level + 1, n_levels),
            "> {} components in total.".format(lvl_app_mod.n_components),
            "> {} active components.".format(lvl_app_mod.n_active_components),
            "> {:.1f}% variance kept.".format(lvl_app_mod.variance_ratio() * 100),
            "> Reference shape of size {} with {} channel{}.".format(
                image._str_shape(), image.n_channels, "s" * (image.n_channels > 1)
            ),
            "> {} features.".format(lvl_app_mod.n_features),
            "> {} landmark points.".format(lp),
            "> Instance: min={:.3f}, max={:.3f}".format(
                image.pixels.min(), image.pixels.max()
            ),
        ]
        info_wid.set_widget_state(text_per_line=text_per_line)

    @output.capture(clear_output=True, wait=True)
    def plot_variance(name):
        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * 10,
            renderer_options_wid.selected_values["zoom_one"] * 3,
        )
        plt.subplot(121)
        save_figure_wid.renderer = appearance_model[level].plot_eigenvalues_ratio(
            figure_id=save_figure_wid.renderer.figure_id, new_figure=False
        )
        plt.subplot(122)
        save_figure_wid.renderer = appearance_model[
            level
        ].plot_eigenvalues_cumulative_ratio(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            figure_size=new_figure_size,
        )
        save_figure_wid.renderer.force_draw()

    # Create widgets
    model_parameters_wid = LinearModelParametersWidget(
        n_parameters[0],
        render_function,
        params_str="Parameter ",
        mode=mode,
        params_bounds=parameters_bounds,
        params_step=0.1,
        plot_variance_visible=True,
        plot_variance_function=plot_variance,
        animation_step=0.5,
        interval=0.0,
        loop_enabled=True,
        continuous_update=False,
    )
    groups_keys, labels_keys = extract_groups_labels_from_image(
        appearance_model[0].mean()
    )
    image_options_wid = ImageOptionsWidget(
        n_channels=appearance_model[0].mean().n_channels,
        image_is_masked=isinstance(appearance_model[0].mean(), MaskedImage),
        render_function=render_function,
    )
    landmark_options_wid = LandmarkOptionsWidget(
        group_keys=groups_keys,
        labels_keys=labels_keys,
        type="2D",
        render_function=render_function,
    )
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=["zoom_one", "axes", "numbering_matplotlib", "legend"],
        axes_x_limits=None,
        axes_y_limits=None,
        labels=None,
        render_function=render_function,
    )
    info_wid = TextPrintWidget(text_per_line=[""])
    save_figure_wid = SaveMatplotlibFigureOptionsWidget()

    # Group widgets
    tmp_children = [model_parameters_wid]
    if n_levels > 1:
        # Define function that updates options' widgets state
        def update_widgets(change):
            value = change["new"]
            # Update model parameters widget
            model_parameters_wid.set_widget_state(
                n_parameters[value], params_str="Parameter ", allow_callback=False
            )

            # Update landmarks options
            g_keys, l_keys = extract_groups_labels_from_image(
                appearance_model[value].mean()
            )
            landmark_options_wid.set_widget_state(
                group_keys=g_keys, labels_keys=l_keys, allow_callback=False
            )

            # Update channels options
            image_options_wid.set_widget_state(
                n_channels=appearance_model[value].mean().n_channels,
                image_is_masked=isinstance(appearance_model[value].mean(), MaskedImage),
                allow_callback=True,
            )

        # Create pyramid radiobuttons
        radio_str = OrderedDict()
        for l in range(n_levels):
            if l == 0:
                radio_str["Level {} (low)".format(l)] = l
            elif l == n_levels - 1:
                radio_str["Level {} (high)".format(l)] = l
            else:
                radio_str["Level {}".format(l)] = l
        level_wid = ipywidgets.RadioButtons(
            options=radio_str,
            description="Pyramid",
            value=n_levels - 1,
            layout=ipywidgets.Layout(width="6cm"),
        )
        level_wid.observe(update_widgets, names="value", type="change")
        level_wid.observe(render_function, names="value", type="change")
        tmp_children.insert(0, level_wid)
    tmp_wid = ipywidgets.HBox(tmp_children)
    options_box = ipywidgets.Tab(
        children=[
            tmp_wid,
            image_options_wid,
            landmark_options_wid,
            renderer_options_wid,
            info_wid,
            save_figure_wid,
        ]
    )
    tab_titles = ["Model", "Image", "Landmarks", "Renderer", "Info", "Export"]
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    logo_wid = LogoWidget(style=main_style)
    logo_wid.layout.margin = "0px 10px 0px 0px"

    output.layout.align_self = "center"
    wid = ipywidgets.VBox([logo_wid, options_box, output])

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})


def visualize_patch_appearance_model(
    appearance_model,
    centers,
    n_parameters=5,
    mode="multiple",
    parameters_bounds=(-3.0, 3.0),
    figure_size=(7, 7),
):
    r"""
    Widget that allows the dynamic visualization of a multi-scale linear
    statistical patch-based appearance model.

    Parameters
    ----------
    appearance_model : `list` of `menpo.model.PCAModel` or subclass
        The multi-scale patch-based appearance model to be visualized. Note that
        each level can have different number of components.
    centers : `list` of `menpo.shape.PointCloud` or subclass
        The centers to set the patches around. If the `list` has only one
        `menpo.shape.PointCloud` then this will be used for all appearance model
        levels. Otherwise, it needs to have the same length as
        `appearance_model`.
    n_parameters : `int` or `list` of `int` or ``None``, optional
        The number of principal components to be used for the parameters
        sliders. If `int`, then the number of sliders per level is the minimum
        between `n_parameters` and the number of active components per level.
        If `list` of `int`, then a number of sliders is defined per level.
        If ``None``, all the active components per level will have a slider.
    mode : ``{'single', 'multiple'}``, optional
        If ``'single'``, then only a single slider is constructed along with a
        drop down menu. If ``'multiple'``, then a slider is constructed for each
        parameter.
    parameters_bounds : (`float`, `float`), optional
        The minimum and maximum bounds, in std units, for the sliders.
    figure_size : (`int`, `int`), optional
        The size of the plotted figures.
    """
    # Make sure that appearance_model is a list even with one member
    if not isinstance(appearance_model, Sized):
        appearance_model = [appearance_model]

    # Get the number of levels (i.e. number of appearance models)
    n_levels = len(appearance_model)

    # Make sure that centers is a list even with one pointcloud
    if not isinstance(centers, list):
        centers = [centers] * n_levels
    elif isinstance(centers, list) and len(centers) == 1:
        centers *= n_levels

    # Define the styling options
    main_style = "success"

    # Get the maximum number of components per level
    max_n_params = [ap.n_active_components for ap in appearance_model]

    # Check the given number of parameters (the returned n_parameters is a list
    # of len n_scales)
    n_parameters = check_n_parameters(n_parameters, n_levels, max_n_params)

    output = ipywidgets.Output()

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Compute weights and instance
        parameters = model_parameters_wid.selected_values
        weights = (
            parameters * appearance_model[level].eigenvalues[: len(parameters)] ** 0.5
        )
        instance = appearance_model[level].instance(weights)

        # Create options dictionary
        options = dict()
        options.update(shape_options_wid.selected_values["lines"])
        options.update(shape_options_wid.selected_values["markers"])
        options.update(renderer_options_wid.selected_values["numbering_matplotlib"])
        options.update(renderer_options_wid.selected_values["axes"])
        image_options = dict(image_options_wid.selected_values)
        del image_options["masked_enabled"]
        options.update(image_options)
        options.update(patch_options_wid.selected_values)
        options["line_colour"] = options["line_colour"][0]
        options["marker_face_colour"] = options["marker_face_colour"][0]
        options["marker_edge_colour"] = options["marker_edge_colour"][0]

        # Get figure size
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * figure_size[0],
            renderer_options_wid.selected_values["zoom_one"] * figure_size[1],
        )

        # Render image with selected options
        save_figure_wid.renderer = render_patches(
            patches=instance.pixels,
            patch_centers=centers[level],
            renderer=save_figure_wid.renderer,
            figure_size=new_figure_size,
            **options
        )

        # Update info
        update_info(instance, level)

    # Define function that updates the info text
    def update_info(image, level):
        lvl_app_mod = appearance_model[level]
        text_per_line = [
            "> Level: {} out of {}.".format(level + 1, n_levels),
            "> {} components in total.".format(lvl_app_mod.n_components),
            "> {} active components.".format(lvl_app_mod.n_active_components),
            "> {:.1f}% variance kept.".format(lvl_app_mod.variance_ratio() * 100),
            "> Each patch has size {}H x {}W with {} channel{}.".format(
                image.pixels.shape[3],
                image.pixels.shape[4],
                image.pixels.shape[2],
                "s" * (image.pixels.shape[2] > 1),
            ),
            "> {} features.".format(lvl_app_mod.n_features),
            "> {} landmark points.".format(image.pixels.shape[0]),
            "> Instance: min={:.3f}, max={:.3f}".format(
                image.pixels.min(), image.pixels.max()
            ),
        ]
        info_wid.set_widget_state(text_per_line=text_per_line)

    @output.capture(clear_output=True, wait=True)
    def plot_variance(name):
        # Get selected level
        level = 0
        if n_levels > 1:
            level = level_wid.value

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * 10,
            renderer_options_wid.selected_values["zoom_one"] * 3,
        )
        plt.subplot(121)
        save_figure_wid.renderer = appearance_model[level].plot_eigenvalues_ratio(
            figure_id=save_figure_wid.renderer.figure_id, new_figure=False
        )
        plt.subplot(122)
        save_figure_wid.renderer = appearance_model[
            level
        ].plot_eigenvalues_cumulative_ratio(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            figure_size=new_figure_size,
        )
        save_figure_wid.renderer.force_draw()

    # Create widgets
    model_parameters_wid = LinearModelParametersWidget(
        n_parameters[0],
        render_function,
        params_str="Parameter ",
        mode=mode,
        params_bounds=parameters_bounds,
        params_step=0.1,
        plot_variance_visible=True,
        plot_variance_function=plot_variance,
        animation_step=0.5,
        interval=0.0,
        loop_enabled=True,
        continuous_update=False,
    )
    shape_options_wid = Shape2DOptionsWidget(labels=None, render_function=None)
    shape_options_wid.line_options_wid.render_lines_switch.button_wid.value = False
    shape_options_wid.add_render_function(render_function)
    patch_options_wid = PatchOptionsWidget(
        n_patches=appearance_model[0].mean().pixels.shape[0],
        n_offsets=appearance_model[0].mean().pixels.shape[1],
        render_function=render_function,
    )
    image_options_wid = ImageOptionsWidget(
        n_channels=appearance_model[0].mean().pixels.shape[2],
        image_is_masked=isinstance(appearance_model[0].mean(), MaskedImage),
        render_function=None,
    )
    image_options_wid.interpolation_checkbox.button_wid.value = False
    image_options_wid.add_render_function(render_function)
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=["zoom_one", "axes", "numbering_matplotlib"],
        labels=None,
        axes_x_limits=None,
        axes_y_limits=None,
        render_function=render_function,
    )
    info_wid = TextPrintWidget(text_per_line=[""])
    save_figure_wid = SaveMatplotlibFigureOptionsWidget()

    # Group widgets
    tmp_children = [model_parameters_wid]
    if n_levels > 1:
        # Define function that updates options' widgets state
        def update_widgets(change):
            value = change["new"]
            # Update model parameters widget
            model_parameters_wid.set_widget_state(
                n_parameters[value], params_str="Parameter ", allow_callback=False
            )

            # Update patch options
            patch_options_wid.set_widget_state(
                n_patches=appearance_model[value].mean().pixels.shape[0],
                n_offsets=appearance_model[value].mean().pixels.shape[1],
                allow_callback=False,
            )

            # Update channels options
            image_options_wid.set_widget_state(
                n_channels=appearance_model[value].mean().pixels.shape[2],
                image_is_masked=isinstance(appearance_model[value].mean(), MaskedImage),
                allow_callback=True,
            )

        # Define pyramid radiobuttons
        radio_str = OrderedDict()
        for l in range(n_levels):
            if l == 0:
                radio_str["Level {} (low)".format(l)] = l
            elif l == n_levels - 1:
                radio_str["Level {} (high)".format(l)] = l
            else:
                radio_str["Level {}".format(l)] = l
        level_wid = ipywidgets.RadioButtons(
            options=radio_str,
            description="Pyramid",
            value=n_levels - 1,
            layout=ipywidgets.Layout(width="6cm"),
        )
        level_wid.observe(update_widgets, names="value", type="change")
        level_wid.observe(render_function, names="value", type="change")
        tmp_children.insert(0, level_wid)
    tmp_wid = ipywidgets.HBox(tmp_children)
    options_box = ipywidgets.Tab(
        children=[
            tmp_wid,
            patch_options_wid,
            image_options_wid,
            shape_options_wid,
            renderer_options_wid,
            info_wid,
            save_figure_wid,
        ]
    )
    tab_titles = ["Model", "Patches", "Channels", "Shape", "Renderer", "Info", "Export"]
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    logo_wid = LogoWidget(style=main_style)
    logo_wid.layout.margin = "0px 10px 0px 0px"

    output.layout.align_self = "center"
    wid = ipywidgets.VBox([logo_wid, options_box, output])

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})


def visualize_morphable_model(
    mm,
    n_shape_parameters=5,
    n_texture_parameters=5,
    mode="multiple",
    parameters_bounds=(-15.0, 15.0),
):
    r"""
    Widget that allows the dynamic visualization of a 3D Morphable Model.

    Parameters
    ----------
    mm : `menpo3d.morhpablemodel.ColouredMorphableModel` or `subclass`
        The multi-scale 3D Morphable Model to be visualized.
    n_shape_parameters : `int` or `list` of `int` or ``None``, optional
        The number of principal components to be used for the shape parameters
        sliders. If `int`, then the number of sliders per level is the minimum
        between `n_parameters` and the number of active components per level.
        If `list` of `int`, then a number of sliders is defined per level.
        If ``None``, all the active components per level will have a slider.
    n_texture_parameters : `int` or `list` of `int` or ``None``, optional
        The number of principal components to be used for the tecture
        parameters sliders. If `int`, then the number of sliders per level is
        the minimum between `n_parameters` and the number of active components
        per level. If `list` of `int`, then a number of sliders is defined per
        level. If ``None``, all the active components per level will have a
        slider.
    mode : ``{'single', 'multiple'}``, optional
        If ``'single'``, then only a single slider is constructed along with a
        drop down menu. If ``'multiple'``, then a slider is constructed for each
        parameter.
    parameters_bounds : (`float`, `float`), optional
        The minimum and maximum bounds, in std units, for the sliders.
    """
    # Define the styling options
    main_style = "info"

    # Check the given number of parameters
    n_shape_parameters = check_n_parameters(
        n_shape_parameters, 1, [mm.shape_model.n_active_components]
    )
    n_texture_parameters = check_n_parameters(
        n_texture_parameters, 1, [mm.texture_model.n_active_components]
    )

    output = ipywidgets.Output()

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        save_figure_wid.renderer.clear_figure()

        # Compute weights
        shape_weights = shape_model_parameters_wid.selected_values
        shape_weights = (
            shape_weights * mm.shape_model.eigenvalues[: len(shape_weights)] ** 0.5
        )
        texture_weights = texture_model_parameters_wid.selected_values
        texture_weights = (
            texture_weights
            * mm.texture_model.eigenvalues[: len(texture_weights)] ** 0.5
        )
        instance = mm.instance(
            shape_weights=shape_weights, texture_weights=texture_weights
        )
        # TODO: Is this really needed?
        instance = instance.clip_texture()

        # Update info
        update_info(mm, instance)

        # Render instance
        save_figure_wid.renderer = instance.view(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            **mesh_options_wid.selected_values
        )

        # Force rendering
        save_figure_wid.renderer.force_draw()

    # Define function that updates the info text
    def update_info(mm, instance):
        text_per_line = [
            "> {} vertices, {} triangles".format(mm.n_vertices, mm.n_triangles),
            "> {} shape components ({:.2f}% of variance)".format(
                mm.shape_model.n_components, mm.shape_model.variance_ratio() * 100
            ),
            "> {} texture channels".format(mm.n_channels),
            "> {} texture components ({:.2f}% of variance)".format(
                mm.texture_model.n_components, mm.texture_model.variance_ratio() * 100
            ),
            "> Instance: min={:.3f} , max={:.3f}".format(
                instance.colours.min(), instance.colours.max()
            ),
        ]
        info_wid.set_widget_state(text_per_line=text_per_line)

    @output.capture(clear_output=True, wait=True)
    def plot_shape_variance(name):
        # Render
        plt.subplot(121)
        mm.shape_model.plot_eigenvalues_ratio()
        plt.subplot(122)
        mm.shape_model.plot_eigenvalues_cumulative_ratio()
        plt.show()

    @output.capture(clear_output=True, wait=True)
    def plot_texture_variance(name):
        # Render
        plt.subplot(121)
        mm.texture_model.plot_eigenvalues_ratio()
        plt.subplot(122)
        mm.texture_model.plot_eigenvalues_cumulative_ratio()
        plt.show()

    # Create widgets
    shape_model_parameters_wid = LinearModelParametersWidget(
        n_shape_parameters[0],
        render_function,
        params_str="Parameter ",
        mode=mode,
        params_bounds=parameters_bounds,
        params_step=0.1,
        plot_variance_visible=True,
        plot_variance_function=plot_shape_variance,
        animation_step=0.5,
        interval=0.0,
        loop_enabled=True,
    )
    texture_model_parameters_wid = LinearModelParametersWidget(
        n_texture_parameters[0],
        render_function,
        params_str="Parameter ",
        mode=mode,
        params_bounds=parameters_bounds,
        params_step=0.1,
        plot_variance_visible=True,
        plot_variance_function=plot_texture_variance,
        animation_step=0.5,
        interval=0.0,
        loop_enabled=True,
    )
    mesh_options_wid = Mesh3DOptionsWidget(
        textured=True, render_function=render_function
    )
    info_wid = TextPrintWidget(text_per_line=[""])
    save_figure_wid = SaveMayaviFigureOptionsWidget()

    # Group widgets
    model_parameters_wid = ipywidgets.HBox(
        [ipywidgets.Tab([shape_model_parameters_wid, texture_model_parameters_wid])]
    )
    model_parameters_wid.children[0].set_title(0, "Shape")
    model_parameters_wid.children[0].set_title(1, "Texture")
    options_box = ipywidgets.Tab(
        [model_parameters_wid, mesh_options_wid, info_wid, save_figure_wid]
    )
    tab_titles = ["Model", "Mesh", "Info", "Export"]
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    logo_wid = LogoWidget(style=main_style)
    logo_wid.layout.margin = "0px 10px 0px 0px"

    output.layout.align_self = "center"
    wid = ipywidgets.VBox([logo_wid, options_box, output])

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})
    print_dynamic("")


def webcam_widget(canvas_width=640, hd=True, n_preview_windows=5):
    r"""
    Webcam widget for taking snapshots. The snapshots are dynamically previewed
    in a FIFO stack of thumbnails.

    Parameters
    ----------
    canvas_width : `int`, optional
        The initial width of the rendered canvas. Note that this doesn't actually
        change the webcam resolution. It simply rescales the rendered image, as
        well as the size of the returned screenshots.
    hd : `bool`, optional
        If ``True``, then the webcam will be set to high definition (HD), i.e.
        720 x 1280. Otherwise the default resolution will be used.
    n_preview_windows : `int`, optional
        The number of preview thumbnails that will be used as a FIFO stack to
        show the captured screenshots. It must be at least 4.

    Returns
    -------
    snapshots : `list` of `menpo.image.Image`
        The list of captured images.
    """
    # Set update function
    images = []

    def update(_):
        images.append(wid.selected_values[-1])

    # Create widgets
    wid = CameraSnapshotWidget(
        canvas_width=canvas_width,
        hd=hd,
        n_preview_windows=n_preview_windows,
        preview_windows_margin=3,
        style="danger",
        preview_style="warning",
        render_function=update,
    )
    wid.container.layout.border = "2px solid" + map_styles_to_hex_colours("danger")

    # Display widget
    ipydisplay.display(wid)

    # Return
    return images
