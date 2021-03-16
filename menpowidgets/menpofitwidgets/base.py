from menpo.base import MenpoMissingDependencyError

try:
    import menpofit
except ImportError as e:
    raise MenpoMissingDependencyError(e.name)

# Continue with imports if we have menpofit
from collections import OrderedDict
from typing import Sized
import numpy as np

import ipywidgets
import IPython.display as ipydisplay

import matplotlib.pyplot as plt

from menpo.base import name_of_callable
from menpo.image import MaskedImage
from menpo.image.base import _convert_patches_list_to_single_array

from menpofit.error import (
    euclidean_bb_normalised_error,
    root_mean_square_bb_normalised_error,
)

from ..checks import check_n_parameters
from ..options import (
    SaveMatplotlibFigureOptionsWidget,
    RendererOptionsWidget,
    ImageOptionsWidget,
    PatchOptionsWidget,
    LandmarkOptionsWidget,
    LinearModelParametersWidget,
    PlotMatplotlibOptionsWidget,
    AnimationOptionsWidget,
    TextPrintWidget,
    Shape2DOptionsWidget,
)
from ..tools import LogoWidget
from ..style import map_styles_to_hex_colours
from ..utils import render_patches, render_image, extract_groups_labels_from_image

from ..options import IterativeResultOptionsWidget


def visualize_aam(
    aam,
    n_shape_parameters=5,
    n_appearance_parameters=5,
    mode="multiple",
    parameters_bounds=(-3.0, 3.0),
    figure_size=(7, 7),
):
    r"""
    Widget that allows the dynamic visualization of a multi-scale Active
    Appearance Model.

    Parameters
    ----------
    aam : `menpofit.aam.HolisticAAM`
        The multi-scale AAM to be visualized. Note that each level can have
        different number of components.
    n_shape_parameters : `int` or `list` of `int` or ``None``, optional
        The number of principal components to be used for the shape parameters
        sliders. If `int`, then the number of sliders per level is the minimum
        between `n_parameters` and the number of active components per level.
        If `list` of `int`, then a number of sliders is defined per level.
        If ``None``, all the active components per level will have a slider.
    n_appearance_parameters : `int` or `list` of `int` or ``None``, optional
        The number of principal components to be used for the appearance
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
    figure_size : (`int`, `int`), optional
        The size of the plotted figures.
    """
    # Get the number of levels
    n_levels = aam.n_scales

    # Define the styling options
    main_style = "info"

    # Get the maximum number of components per level
    max_n_shape = [sp.model.n_active_components for sp in aam.shape_models]
    max_n_appearance = [ap.n_active_components for ap in aam.appearance_models]

    # Check the given number of parameters (the returned n_parameters is a list
    # of len n_scales)
    n_shape_parameters = check_n_parameters(n_shape_parameters, n_levels, max_n_shape)
    n_appearance_parameters = check_n_parameters(
        n_appearance_parameters, n_levels, max_n_appearance
    )

    output = ipywidgets.Output()

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Compute weights and instance
        shape_weights = shape_model_parameters_wid.selected_values
        appearance_weights = appearance_model_parameters_wid.selected_values
        instance = aam.instance(
            scale_index=level,
            shape_weights=shape_weights,
            appearance_weights=appearance_weights,
        )
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

        # show image with selected options
        save_figure_wid.renderer = render_image(
            image=instance,
            renderer=save_figure_wid.renderer,
            image_is_masked=image_is_masked,
            figure_size=new_figure_size,
            **options
        )

        # Update info
        update_info(aam, instance, level, g)

    # Define function that updates the info text
    def update_info(aam, instance, level, group):
        # features info
        lvl_app_mod = aam.appearance_models[level]
        lvl_shape_mod = aam.shape_models[level].model
        aam_mean = lvl_app_mod.mean()
        n_channels = aam_mean.n_channels
        tmplt_inst = lvl_app_mod.mean()
        feat = aam.holistic_features[level]

        # Feature string
        tmp_feat = "Feature is {} with {} channel{}".format(
            name_of_callable(feat), n_channels, "s" * (n_channels > 1)
        )

        # update info widgets
        text_per_line = [
            "> Warp using {} transform".format(aam.transform.__name__),
            "> Level {}/{}".format(level + 1, aam.n_scales),
            "> {} landmark points".format(instance.landmarks[group].n_points),
            "> {} shape components ({:.2f}% of variance)".format(
                lvl_shape_mod.n_components, lvl_shape_mod.variance_ratio() * 100
            ),
            "> {}".format(tmp_feat),
            "> Reference frame of length {} ({} x {}C, {} x {}C)".format(
                lvl_app_mod.n_features,
                tmplt_inst.n_true_pixels(),
                n_channels,
                tmplt_inst._str_shape(),
                n_channels,
            ),
            "> {} appearance components ({:.2f}% of variance)".format(
                lvl_app_mod.n_components, lvl_app_mod.variance_ratio() * 100
            ),
            "> Instance: min={:.3f} , max={:.3f}".format(
                instance.pixels.min(), instance.pixels.max()
            ),
        ]
        info_wid.set_widget_state(text_per_line=text_per_line)

    @output.capture(clear_output=True, wait=True)
    def plot_shape_variance(name):
        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * 10,
            renderer_options_wid.selected_values["zoom_one"] * 3,
        )
        plt.subplot(121)
        save_figure_wid.renderer = aam.shape_models[level].model.plot_eigenvalues_ratio(
            figure_id=save_figure_wid.renderer.figure_id, new_figure=False
        )
        plt.subplot(122)
        save_figure_wid.renderer = aam.shape_models[
            level
        ].model.plot_eigenvalues_cumulative_ratio(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            figure_size=new_figure_size,
        )
        save_figure_wid.renderer.force_draw()

    @output.capture(clear_output=True, wait=True)
    def plot_appearance_variance(name):
        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * 10,
            renderer_options_wid.selected_values["zoom_one"] * 3,
        )
        plt.subplot(121)
        save_figure_wid.renderer = aam.appearance_models[level].plot_eigenvalues_ratio(
            figure_id=save_figure_wid.renderer.figure_id, new_figure=False
        )
        plt.subplot(122)
        save_figure_wid.renderer = aam.appearance_models[
            level
        ].plot_eigenvalues_cumulative_ratio(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            figure_size=new_figure_size,
        )
        save_figure_wid.renderer.force_draw()

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
    appearance_model_parameters_wid = LinearModelParametersWidget(
        n_appearance_parameters[0],
        render_function,
        params_str="Parameter ",
        mode=mode,
        params_bounds=parameters_bounds,
        params_step=0.1,
        plot_variance_visible=True,
        plot_variance_function=plot_appearance_variance,
        animation_step=0.5,
        interval=0.0,
        loop_enabled=True,
    )
    groups_keys, labels_keys = extract_groups_labels_from_image(
        aam.appearance_models[0].mean()
    )
    image_options_wid = ImageOptionsWidget(
        n_channels=aam.appearance_models[0].mean().n_channels,
        image_is_masked=isinstance(aam.appearance_models[0].mean(), MaskedImage),
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
        labels=None,
        axes_x_limits=None,
        axes_y_limits=None,
        render_function=render_function,
    )
    info_wid = TextPrintWidget(text_per_line=[""])
    save_figure_wid = SaveMatplotlibFigureOptionsWidget()

    # Group widgets
    model_parameters_wid = ipywidgets.HBox(
        [ipywidgets.Tab([shape_model_parameters_wid, appearance_model_parameters_wid])]
    )
    model_parameters_wid.children[0].set_title(0, "Shape")
    model_parameters_wid.children[0].set_title(1, "Appearance")
    tmp_children = [model_parameters_wid]
    if n_levels > 1:
        # Define function that updates options' widgets state
        def update_widgets(change):
            value = change["new"]
            # Update shape model parameters
            shape_model_parameters_wid.set_widget_state(
                n_shape_parameters[value], params_str="Parameter ", allow_callback=False
            )

            # Update appearance model parameters
            appearance_model_parameters_wid.set_widget_state(
                n_appearance_parameters[value],
                params_str="Parameter ",
                allow_callback=False,
            )

            # Update landmarks options
            g_keys, l_keys = extract_groups_labels_from_image(
                aam.appearance_models[value].mean()
            )
            landmark_options_wid.set_widget_state(
                group_keys=g_keys, labels_keys=l_keys, allow_callback=False
            )

            # Update channel options
            image_options_wid.set_widget_state(
                n_channels=aam.appearance_models[value].mean().n_channels,
                image_is_masked=isinstance(
                    aam.appearance_models[value].mean(), MaskedImage
                ),
                allow_callback=True,
            )

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
        [
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
    wid = ipywidgets.HBox([logo_wid, options_box])

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})


def visualize_patch_aam(
    aam,
    n_shape_parameters=5,
    n_appearance_parameters=5,
    mode="multiple",
    parameters_bounds=(-3.0, 3.0),
    figure_size=(7, 7),
):
    r"""
    Widget that allows the dynamic visualization of a multi-scale patch-based
    Active Appearance Model.

    Parameters
    ----------
    aam : `menpofit.aam.PatchAAM`
        The multi-scale patch-based AAM to be visualized. Note that each level
        can have different number of components.
    n_shape_parameters : `int` or `list` of `int` or ``None``, optional
        The number of principal components to be used for the shape parameters
        sliders. If `int`, then the number of sliders per level is the minimum
        between `n_parameters` and the number of active components per level.
        If `list` of `int`, then a number of sliders is defined per level.
        If ``None``, all the active components per level will have a slider.
    n_appearance_parameters : `int` or `list` of `int` or ``None``, optional
        The number of principal components to be used for the appearance
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
    figure_size : (`int`, `int`), optional
        The size of the plotted figures.
    """
    # Get the number of levels
    n_levels = aam.n_scales

    # Define the styling options
    main_style = "info"

    # Get the maximum number of components per level
    max_n_shape = [sp.model.n_active_components for sp in aam.shape_models]
    max_n_appearance = [ap.n_active_components for ap in aam.appearance_models]

    # Check the given number of parameters (the returned n_parameters is a list
    # of len n_scales)
    n_shape_parameters = check_n_parameters(n_shape_parameters, n_levels, max_n_shape)
    n_appearance_parameters = check_n_parameters(
        n_appearance_parameters, n_levels, max_n_appearance
    )

    output = ipywidgets.Output()

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Compute weights and instance
        shape_weights = shape_model_parameters_wid.selected_values
        appearance_weights = appearance_model_parameters_wid.selected_values
        shape_instance, appearance_instance = aam.instance(
            scale_index=level,
            shape_weights=shape_weights,
            appearance_weights=appearance_weights,
        )

        # Render instance with selected options
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

        # show image with selected options
        save_figure_wid.renderer = render_patches(
            patches=appearance_instance.pixels,
            patch_centers=shape_instance,
            renderer=save_figure_wid.renderer,
            figure_size=new_figure_size,
            **options
        )

        # Update info
        update_info(aam, appearance_instance, level)

    # Define function that updates the info text
    def update_info(aam, appearance_instance, level):
        lvl_app_mod = aam.appearance_models[level]
        lvl_shape_mod = aam.shape_models[level].model
        n_channels = lvl_app_mod.mean().pixels.shape[2]
        feat = aam.holistic_features[level]

        # Feature string
        tmp_feat = "Feature is {} with {} channel{}".format(
            name_of_callable(feat), n_channels, "s" * (n_channels > 1)
        )
        n_feat = (
            appearance_instance.pixels.shape[0]
            * appearance_instance.pixels.shape[2]
            * appearance_instance.pixels.shape[3]
            * appearance_instance.pixels.shape[4]
        )

        # update info widgets
        text_per_line = [
            "> No image warping performed.",
            "> Level {}/{}".format(level + 1, aam.n_scales),
            "> {} landmark points".format(appearance_instance.pixels.shape[0]),
            "> {} shape components ({:.2f}% of variance)".format(
                lvl_shape_mod.n_components, lvl_shape_mod.variance_ratio() * 100
            ),
            "> {}".format(tmp_feat),
            "> Reference frame of length {} ({} patches of shape {} x {} "
            "and {} channel{}.)".format(
                n_feat,
                appearance_instance.pixels.shape[0],
                appearance_instance.pixels.shape[3],
                appearance_instance.pixels.shape[4],
                appearance_instance.pixels.shape[2],
                "s" * (appearance_instance.pixels.shape[2] > 1),
            ),
            "> {} appearance components ({:.2f}% of variance)".format(
                lvl_app_mod.n_components, lvl_app_mod.variance_ratio() * 100
            ),
            "> Instance: min={:.3f} , max={:.3f}".format(
                appearance_instance.pixels.min(), appearance_instance.pixels.max()
            ),
        ]
        info_wid.set_widget_state(text_per_line=text_per_line)

    @output.capture(clear_output=True, wait=True)
    def plot_shape_variance(name):
        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * 10,
            renderer_options_wid.selected_values["zoom_one"] * 3,
        )
        plt.subplot(121)
        save_figure_wid.renderer = aam.shape_models[level].model.plot_eigenvalues_ratio(
            figure_id=save_figure_wid.renderer.figure_id, new_figure=False
        )
        plt.subplot(122)
        save_figure_wid.renderer = aam.shape_models[
            level
        ].model.plot_eigenvalues_cumulative_ratio(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            figure_size=new_figure_size,
        )
        save_figure_wid.renderer.force_draw()

    @output.capture(clear_output=True, wait=True)
    def plot_appearance_variance(name):
        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * 10,
            renderer_options_wid.selected_values["zoom_one"] * 3,
        )
        plt.subplot(121)
        save_figure_wid.renderer = aam.appearance_models[level].plot_eigenvalues_ratio(
            figure_id=save_figure_wid.renderer.figure_id, new_figure=False
        )
        plt.subplot(122)
        save_figure_wid.renderer = aam.appearance_models[
            level
        ].plot_eigenvalues_cumulative_ratio(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            figure_size=new_figure_size,
        )
        save_figure_wid.renderer.force_draw()

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
    appearance_model_parameters_wid = LinearModelParametersWidget(
        n_appearance_parameters[0],
        render_function,
        params_str="Parameter ",
        mode=mode,
        params_bounds=parameters_bounds,
        params_step=0.1,
        plot_variance_visible=True,
        plot_variance_function=plot_appearance_variance,
        animation_step=0.5,
        interval=0.0,
        loop_enabled=True,
    )
    shape_options_wid = Shape2DOptionsWidget(labels=None, render_function=None)
    shape_options_wid.line_options_wid.render_lines_switch.button_wid.value = False
    shape_options_wid.add_render_function(render_function)
    patch_options_wid = PatchOptionsWidget(
        n_patches=aam.appearance_models[0].mean().pixels.shape[0],
        n_offsets=aam.appearance_models[0].mean().pixels.shape[1],
        render_function=render_function,
    )
    image_options_wid = ImageOptionsWidget(
        n_channels=aam.appearance_models[0].mean().pixels.shape[2],
        image_is_masked=False,
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
    model_parameters_wid = ipywidgets.HBox(
        [ipywidgets.Tab([shape_model_parameters_wid, appearance_model_parameters_wid])]
    )
    model_parameters_wid.children[0].set_title(0, "Shape")
    model_parameters_wid.children[0].set_title(1, "Appearance")
    tmp_children = [model_parameters_wid]
    if n_levels > 1:
        # Define function that updates options' widgets state
        def update_widgets(change):
            value = change["new"]
            # Update shape model parameters
            shape_model_parameters_wid.set_widget_state(
                n_shape_parameters[value], params_str="Parameter ", allow_callback=False
            )

            # Update appearance model parameters
            appearance_model_parameters_wid.set_widget_state(
                n_appearance_parameters[value],
                params_str="Parameter ",
                allow_callback=False,
            )

            # Update patch options
            patch_options_wid.set_widget_state(
                n_patches=aam.appearance_models[value].mean().pixels.shape[0],
                n_offsets=aam.appearance_models[value].mean().pixels.shape[1],
                allow_callback=False,
            )

            # Update channels options
            image_options_wid.set_widget_state(
                n_channels=aam.appearance_models[value].mean().pixels.shape[2],
                image_is_masked=False,
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
        [
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
    wid = ipywidgets.HBox([logo_wid, options_box])

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})


def visualize_atm(
    atm,
    n_shape_parameters=5,
    mode="multiple",
    parameters_bounds=(-3.0, 3.0),
    figure_size=(7, 7),
):
    r"""
    Widget that allows the dynamic visualization of a multi-scale Active
    Template Model.

    Parameters
    ----------
    atm : `menpofit.atm.ATM`
        The multi-scale ATM to be visualized. Note that each level can have
        different number of components.
    n_shape_parameters : `int` or `list` of `int` or ``None``, optional
        The number of principal components to be used for the shape parameters
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
    # Get the number of levels
    n_levels = atm.n_scales

    # Define the styling options
    main_style = "info"

    # Get the maximum number of components per level
    max_n_shape = [sp.model.n_active_components for sp in atm.shape_models]

    # Check the given number of parameters (the returned n_parameters is a list
    # of len n_scales)
    n_shape_parameters = check_n_parameters(n_shape_parameters, n_levels, max_n_shape)

    output = ipywidgets.Output()

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Compute weights and instance
        shape_weights = shape_model_parameters_wid.selected_values
        instance = atm.instance(scale_index=level, shape_weights=shape_weights)
        image_is_masked = isinstance(instance, MaskedImage)
        g = landmark_options_wid.selected_values["landmarks"]["group"]

        # Render instance with selected options
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
        update_info(atm, instance, level, g)

    # Define function that updates the info text
    def update_info(atm, instance, level, group):
        lvl_shape_mod = atm.shape_models[level].model
        tmplt_inst = atm.warped_templates[level]
        n_channels = tmplt_inst.n_channels
        feat = atm.holistic_features[level]

        # Feature string
        tmp_feat = "Feature is {} with {} channel{}".format(
            name_of_callable(feat), n_channels, "s" * (n_channels > 1)
        )

        # update info widgets
        text_per_line = [
            "> Warp using {} transform".format(atm.transform.__name__),
            "> Level {}/{}".format(level + 1, atm.n_scales),
            "> {} landmark points".format(instance.landmarks[group].n_points),
            "> {} shape components ({:.2f}% of variance)".format(
                lvl_shape_mod.n_components, lvl_shape_mod.variance_ratio() * 100
            ),
            "> {}".format(tmp_feat),
            "> Reference frame of length {} ({} x {}C, {} x {}C)".format(
                tmplt_inst.n_true_pixels() * n_channels,
                tmplt_inst.n_true_pixels(),
                n_channels,
                tmplt_inst._str_shape(),
                n_channels,
            ),
            "> Instance: min={:.3f} , max={:.3f}".format(
                instance.pixels.min(), instance.pixels.max()
            ),
        ]
        info_wid.set_widget_state(text_per_line=text_per_line)

    @output.capture(clear_output=True, wait=True)
    def plot_shape_variance(name):
        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * 10,
            renderer_options_wid.selected_values["zoom_one"] * 3,
        )
        plt.subplot(121)
        save_figure_wid.renderer = atm.shape_models[level].model.plot_eigenvalues_ratio(
            figure_id=save_figure_wid.renderer.figure_id, new_figure=False
        )
        plt.subplot(122)
        save_figure_wid.renderer = atm.shape_models[
            level
        ].model.plot_eigenvalues_cumulative_ratio(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            figure_size=new_figure_size,
        )
        save_figure_wid.renderer.force_draw()

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
    groups_keys, labels_keys = extract_groups_labels_from_image(atm.warped_templates[0])
    image_options_wid = ImageOptionsWidget(
        n_channels=atm.warped_templates[0].n_channels,
        image_is_masked=isinstance(atm.warped_templates[0], MaskedImage),
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
        labels=None,
        axes_x_limits=None,
        axes_y_limits=None,
        render_function=render_function,
    )
    info_wid = TextPrintWidget(text_per_line=[""])
    save_figure_wid = SaveMatplotlibFigureOptionsWidget()

    # Group widgets
    tmp_children = [shape_model_parameters_wid]
    if n_levels > 1:
        # Define function that updates options' widgets state
        def update_widgets(change):
            value = change["new"]
            # Update shape model parameters
            shape_model_parameters_wid.set_widget_state(
                n_shape_parameters[value], params_str="Parameter ", allow_callback=False
            )

            # Update landmarks options
            g_keys, l_keys = extract_groups_labels_from_image(
                atm.warped_templates[value]
            )
            landmark_options_wid.set_widget_state(
                group_keys=g_keys, labels_keys=l_keys, allow_callback=False
            )

            # Update channel options
            image_options_wid.set_widget_state(
                n_channels=atm.warped_templates[value].n_channels,
                image_is_masked=isinstance(atm.warped_templates[value], MaskedImage),
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
        [
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
    wid = ipywidgets.HBox([logo_wid, options_box])

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})


def visualize_patch_atm(
    atm,
    n_shape_parameters=5,
    mode="multiple",
    parameters_bounds=(-3.0, 3.0),
    figure_size=(7, 7),
):
    r"""
    Widget that allows the dynamic visualization of a multi-scale patch-based
    Active Template Model.

    Parameters
    ----------
    atm : `menpofit.atm.PatchATM`
        The multi-scale patch-based ATM to be visualized. Note that each level
        can have different number of components.
    n_shape_parameters : `int` or `list` of `int` or ``None``, optional
        The number of principal components to be used for the shape parameters
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
    # Get the number of levels
    n_levels = atm.n_scales

    # Define the styling options
    main_style = "info"

    # Get the maximum number of components per level
    max_n_shape = [sp.n_active_components for sp in atm.shape_models]

    # Check the given number of parameters (the returned n_parameters is a list
    # of len n_scales)
    n_shape_parameters = check_n_parameters(n_shape_parameters, n_levels, max_n_shape)

    output = ipywidgets.Output()

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Compute weights and instance
        shape_weights = shape_model_parameters_wid.selected_values
        shape_instance, template = atm.instance(
            scale_index=level, shape_weights=shape_weights
        )

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

        # show image with selected options
        save_figure_wid.renderer = render_patches(
            patches=template.pixels,
            patch_centers=shape_instance,
            renderer=save_figure_wid.renderer,
            figure_size=new_figure_size,
            **options
        )

        # Update info
        update_info(atm, template, level)

    # Define function that updates the info text
    def update_info(atm, instance, level):
        lvl_shape_mod = atm.shape_models[level].model
        n_channels = instance.pixels.shape[2]
        feat = atm.holistic_features[level]

        # Feature string
        tmp_feat = "Feature is {} with {} channel{}".format(
            name_of_callable(feat), n_channels, "s" * (n_channels > 1)
        )
        n_feat = (
            instance.pixels.shape[0]
            * instance.pixels.shape[2]
            * instance.pixels.shape[3]
            * instance.pixels.shape[4]
        )

        # update info widgets
        text_per_line = [
            "> Warp using {} transform".format(atm.transform.__name__),
            "> Level {}/{}".format(level + 1, atm.n_scales),
            "> {} landmark points".format(instance.pixels.shape[0]),
            "> {} shape components ({:.2f}% of variance)".format(
                lvl_shape_mod.n_components, lvl_shape_mod.variance_ratio() * 100
            ),
            "> {}".format(tmp_feat),
            "> Reference frame of length {} ({} patches of shape {} x {} "
            "and {} channel{}.)".format(
                n_feat,
                instance.pixels.shape[0],
                instance.pixels.shape[3],
                instance.pixels.shape[4],
                instance.pixels.shape[2],
                "s" * (instance.pixels.shape[2] > 1),
            ),
            "> Instance: min={:.3f} , max={:.3f}".format(
                instance.pixels.min(), instance.pixels.max()
            ),
        ]
        info_wid.set_widget_state(text_per_line=text_per_line)

    @output.capture(clear_output=True, wait=True)
    def plot_shape_variance(name):
        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * 10,
            renderer_options_wid.selected_values["zoom_one"] * 3,
        )
        plt.subplot(121)
        save_figure_wid.renderer = atm.shape_models[level].model.plot_eigenvalues_ratio(
            figure_id=save_figure_wid.renderer.figure_id, new_figure=False
        )
        plt.subplot(122)
        save_figure_wid.renderer = atm.shape_models[
            level
        ].model.plot_eigenvalues_cumulative_ratio(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            figure_size=new_figure_size,
        )
        save_figure_wid.renderer.force_draw()

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
    shape_options_wid = Shape2DOptionsWidget(labels=None, render_function=None)
    shape_options_wid.line_options_wid.render_lines_switch.button_wid.value = False
    shape_options_wid.add_render_function(render_function)
    patch_options_wid = PatchOptionsWidget(
        n_patches=atm.warped_templates[0].pixels.shape[0],
        n_offsets=atm.warped_templates[0].pixels.shape[1],
        render_function=render_function,
    )
    image_options_wid = ImageOptionsWidget(
        n_channels=atm.warped_templates[0].pixels.shape[2],
        image_is_masked=False,
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
    tmp_children = [shape_model_parameters_wid]
    if n_levels > 1:
        # Define function that updates options' widgets state
        def update_widgets(change):
            value = change["new"]
            # Update shape model parameters
            shape_model_parameters_wid.set_widget_state(
                n_shape_parameters[value], params_str="Parameter ", allow_callback=False
            )

            # Update patch options
            patch_options_wid.set_widget_state(
                n_patches=atm.warped_templates[value].pixels.shape[0],
                n_offsets=atm.warped_templates[value].pixels.shape[1],
                allow_callback=False,
            )

            # Update channels options
            image_options_wid.set_widget_state(
                n_channels=atm.warped_templates[value].pixels.shape[2],
                image_is_masked=False,
                allow_callback=True,
            )

        # Pyramid radiobuttons
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
        [
            tmp_wid,
            patch_options_wid,
            image_options_wid,
            shape_options_wid,
            renderer_options_wid,
            info_wid,
            save_figure_wid,
        ]
    )
    tab_titles = ["Model", "Patches", "Image", "Shape", "Renderer", "Info", "Export"]
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    logo_wid = LogoWidget(style=main_style)
    logo_wid.layout.margin = "0px 10px 0px 0px"
    wid = ipywidgets.HBox([logo_wid, options_box])

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})


def visualize_clm(
    clm,
    n_shape_parameters=5,
    mode="multiple",
    parameters_bounds=(-3.0, 3.0),
    figure_size=(7, 7),
):
    r"""
    Widget that allows the dynamic visualization of a multi-scale Constrained
    Local Model.

    Parameters
    ----------
    clm : `menpofit.clm.CLM`
        The multi-scale CLM to be visualized. Note that each level can have
        different number of components.
    n_shape_parameters : `int` or `list` of `int` or ``None``, optional
        The number of principal components to be used for the shape parameters
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
    # Get the number of levels
    n_levels = clm.n_scales

    # Define the styling options
    main_style = "info"

    # Get the maximum number of components per level
    max_n_shape = [sp.n_active_components for sp in clm.shape_models]

    # Check the given number of parameters (the returned n_parameters is a list
    # of len n_scales)
    n_shape_parameters = check_n_parameters(n_shape_parameters, n_levels, max_n_shape)

    output = ipywidgets.Output()

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Compute weights and instance
        shape_weights = shape_model_parameters_wid.selected_values
        shape_instance = clm.shape_instance(
            scale_index=level, shape_weights=shape_weights
        )
        if domain_toggles.value == "spatial":
            patches = _convert_patches_list_to_single_array(
                clm.expert_ensembles[level].spatial_filter_images,
                clm.expert_ensembles[level].n_experts,
            )
        else:
            patches = _convert_patches_list_to_single_array(
                clm.expert_ensembles[level].frequency_filter_images,
                clm.expert_ensembles[level].n_experts,
            )

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

        # show image with selected options
        save_figure_wid.renderer = render_patches(
            patches=patches,
            patch_centers=shape_instance,
            renderer=save_figure_wid.renderer,
            figure_size=new_figure_size,
            **options
        )

        # Update info
        update_info(clm, patches, level)

    # Define function that updates the info text
    def update_info(clm, patches, level):
        lvl_shape_mod = clm.shape_models[level].model
        n_channels = patches.shape[2]
        feat = clm.holistic_features[level]

        # Feature string
        tmp_feat = "Feature is {} with {} channel{}".format(
            name_of_callable(feat), n_channels, "s" * (n_channels > 1)
        )

        # update info widgets
        text_per_line = [
            "> {} ensemble of experts".format(
                name_of_callable(clm.expert_ensemble_cls[level])
            ),
            "> Level {}/{}".format(level + 1, clm.n_scales),
            "> {} experts (landmark points)".format(
                clm.expert_ensembles[level].n_experts
            ),
            "> {} shape components ({:.2f}% of variance)".format(
                lvl_shape_mod.n_components, lvl_shape_mod.variance_ratio() * 100
            ),
            "> {}".format(tmp_feat),
            "> Patch shape: {} x {}".format(
                clm.expert_ensembles[level].search_shape[0],
                clm.expert_ensembles[level].search_shape[1],
            ),
            "> Instance: min={:.3f} , max={:.3f}".format(patches.min(), patches.max()),
        ]
        info_wid.set_widget_state(text_per_line=text_per_line)

    @output.capture(clear_output=True, wait=True)
    def plot_shape_variance(name):
        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * 10,
            renderer_options_wid.selected_values["zoom_one"] * 3,
        )
        plt.subplot(121)
        save_figure_wid.renderer = clm.shape_models[level].model.plot_eigenvalues_ratio(
            figure_id=save_figure_wid.renderer.figure_id, new_figure=False
        )
        plt.subplot(122)
        save_figure_wid.renderer = clm.shape_models[
            level
        ].model.plot_eigenvalues_cumulative_ratio(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            figure_size=new_figure_size,
        )
        save_figure_wid.renderer.force_draw()

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
    shape_options_wid = Shape2DOptionsWidget(labels=None, render_function=None)
    shape_options_wid.line_options_wid.render_lines_switch.button_wid.value = False
    shape_options_wid.add_render_function(render_function)
    patch_options_wid = PatchOptionsWidget(
        n_patches=clm.expert_ensembles[0].n_experts, n_offsets=1, render_function=None
    )
    patch_options_wid.bboxes_line_colour_widget.set_colours(
        "white", allow_callback=False
    )
    patch_options_wid.add_render_function(render_function)
    patch_options_wid.layout.margin = "10px 0px 0px 0px"
    domain_toggles = ipywidgets.ToggleButtons(
        description="Domain", options=["spatial", "frequency"], value="spatial"
    )
    domain_toggles.observe(render_function, names="value", type="change")
    experts_box = ipywidgets.VBox([domain_toggles, patch_options_wid])
    image_options_wid = ImageOptionsWidget(
        n_channels=clm.expert_ensembles[0].spatial_filter_images[0].n_channels,
        image_is_masked=False,
        render_function=None,
    )
    image_options_wid.interpolation_checkbox.button_wid.value = False
    image_options_wid.cmap_select.value = "afmhot"
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
    tmp_children = [shape_model_parameters_wid]
    if n_levels > 1:
        # Define function that updates options' widgets state
        def update_widgets(change):
            value = change["new"]
            # Update shape model parameters
            shape_model_parameters_wid.set_widget_state(
                n_shape_parameters[value], params_str="Parameter ", allow_callback=False
            )

            # Update patch options
            patch_options_wid.set_widget_state(
                n_patches=clm.expert_ensembles[value].n_experts,
                n_offsets=1,
                allow_callback=False,
            )

            # Update channels options
            image_options_wid.set_widget_state(
                n_channels=clm.expert_ensembles[value]
                .spatial_filter_images[0]
                .n_channels,
                image_is_masked=False,
                allow_callback=True,
            )

        # Pyramid radiobuttons
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
        [
            tmp_wid,
            experts_box,
            image_options_wid,
            shape_options_wid,
            renderer_options_wid,
            info_wid,
            save_figure_wid,
        ]
    )
    tab_titles = ["Model", "Experts", "Image", "Shape", "Renderer", "Info", "Export"]
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    logo_wid = LogoWidget(style=main_style)
    logo_wid.layout.margin = "0px 10px 0px 0px"
    wid = ipywidgets.HBox([logo_wid, options_box])

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})


def visualize_expert_ensemble(expert_ensemble, centers, figure_size=(7, 7)):
    r"""
    Widget that allows the dynamic visualization of a multi-scale Ensemble of
    Experts.

    Parameters
    ----------
    expert_ensemble : `list` of `menpofit.clm.expert.ExpertEnsemble` or subclass
        The multi-scale ensemble of experts to be visualized.
    centers : `list` of `menpo.shape.PointCloud` or subclass
        The centers to set the patches around. If the `list` has only one
        `menpo.shape.PointCloud` then this will be used for all expert ensemble
        levels. Otherwise, it needs to have the same length as
        `expert_ensemble`.
    figure_size : (`int`, `int`), optional
        The size of the plotted figures.
    """
    # Make sure that expert_ensemble is a list even with one member
    if not isinstance(expert_ensemble, Sized):
        expert_ensemble = [expert_ensemble]

    # Get the number of levels (i.e. number of expert ensembles)
    n_levels = len(expert_ensemble)

    # Make sure that centers is a list even with one pointcloud
    if not isinstance(centers, list):
        centers = [centers] * n_levels
    elif isinstance(centers, list) and len(centers) == 1:
        centers *= n_levels

    # Define the styling options
    main_style = "info"

    output = ipywidgets.Output()

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        if domain_toggles.value == "spatial":
            patches = _convert_patches_list_to_single_array(
                expert_ensemble[level].spatial_filter_images,
                expert_ensemble[level].n_experts,
            )
        else:
            patches = _convert_patches_list_to_single_array(
                expert_ensemble[level].frequency_filter_images,
                expert_ensemble[level].n_experts,
            )

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

        # show image with selected options
        save_figure_wid.renderer = render_patches(
            patches=patches,
            patch_centers=centers[level],
            renderer=save_figure_wid.renderer,
            figure_size=new_figure_size,
            **options
        )

        # Update info
        update_info(expert_ensemble, patches, level)

    # Define function that updates the info text
    def update_info(expert_ensemble, patches, level):
        # update info widgets
        text_per_line = [
            "> {} ensemble of experts".format(name_of_callable(expert_ensemble[level])),
            "> Level {}/{}".format(level + 1, n_levels),
            "> {} experts.".format(expert_ensemble[level].n_experts),
            "> Channels: {}".format(patches.shape[2]),
            "> Patch shape: {} x {}".format(
                expert_ensemble[level].search_shape[0],
                expert_ensemble[level].search_shape[1],
            ),
            "> Instance: min={:.3f} , max={:.3f}".format(patches.min(), patches.max()),
        ]
        info_wid.set_widget_state(text_per_line=text_per_line)

    # Create widgets
    shape_options_wid = Shape2DOptionsWidget(labels=None, render_function=None)
    shape_options_wid.line_options_wid.render_lines_switch.button_wid.value = False
    shape_options_wid.add_render_function(render_function)
    patch_options_wid = PatchOptionsWidget(
        n_patches=expert_ensemble[0].n_experts, n_offsets=1, render_function=None
    )
    patch_options_wid.bboxes_line_colour_widget.set_colours(
        "white", allow_callback=False
    )
    patch_options_wid.add_render_function(render_function)
    patch_options_wid.layout.margin = "10px 0px 0px 0px"
    domain_toggles = ipywidgets.ToggleButtons(
        description="Domain", options=["spatial", "frequency"], value="spatial"
    )
    domain_toggles.observe(render_function, names="value", type="change")
    image_options_wid = ImageOptionsWidget(
        n_channels=expert_ensemble[0].spatial_filter_images[0].n_channels,
        image_is_masked=False,
        render_function=None,
    )
    image_options_wid.interpolation_checkbox.button_wid.value = False
    image_options_wid.cmap_select.value = "afmhot"
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
    tmp_children = [domain_toggles]
    if n_levels > 1:
        # Define function that updates options' widgets state
        def update_widgets(change):
            value = change["new"]
            # Update patch options
            patch_options_wid.set_widget_state(
                n_patches=expert_ensemble[value].n_experts,
                n_offsets=1,
                allow_callback=False,
            )

            # Update channels options
            image_options_wid.set_widget_state(
                n_channels=expert_ensemble[value].spatial_filter_images[0].n_channels,
                image_is_masked=False,
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
    tmp_wid.layout.align_items = "center"
    experts_box = ipywidgets.VBox([tmp_wid, patch_options_wid])
    options_box = ipywidgets.Tab(
        [
            experts_box,
            image_options_wid,
            shape_options_wid,
            renderer_options_wid,
            info_wid,
            save_figure_wid,
        ]
    )
    tab_titles = ["Experts", "Image", "Shape", "Renderer", "Info", "Export"]
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    logo_wid = LogoWidget(style=main_style)
    logo_wid.layout.margin = "0px 10px 0px 0px"
    wid = ipywidgets.HBox([logo_wid, options_box])

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})


def plot_ced(
    errors,
    legend_entries=None,
    error_range=None,
    error_type="me_norm",
    figure_size=(9, 5),
    return_widget=False,
):
    r"""
    Widget for visualizing the cumulative error curves of the provided errors.

    Parameters
    ----------
    errors : `list` of `lists` of `float`
        A `list` that stores a `list` of errors to be plotted.
    legend_entries : `list` or `str` or ``None``, optional
        The `list` of names that will appear on the legend for each curve. If
        ``None``, then the names format is ``Curve {}.format(i)``.
    error_range : `list` of `float` with length 3, optional
        Specifies the horizontal axis range, i.e. ::

            error_range[0] = min_error
            error_range[1] = max_error
            error_range[2] = error_step

        If ``None``, then ::

            error_range = [0., 0.101, 0.005] for error_type = 'me_norm'
            error_range = [0., 20., 1.] for error_type = 'me'
            error_range = [0., 20., 1.] for error_type = 'rmse'

    error_type : ``{'me_norm', 'me', 'rmse'}``, optional
        Specifies the type of the provided errors.
    figure_size : (`int`, `int`), optional
        The initial size of the rendered figure.
    return_widget : `bool`, optional
        If ``True``, the widget object will be returned so that it can be used
        as part of a parent widget. If ``False``, the widget object is not
        returned, it is just visualized.
    """
    from menpofit.visualize import plot_cumulative_error_distribution

    # Make sure that errors is a list even with one list member
    if not isinstance(errors[0], Sized):
        errors = [errors]

    # Get number of curves to be plotted
    n_curves = len(errors)

    # Define the styling options
    main_style = "danger"

    output = ipywidgets.Output()

    # Parse options
    if legend_entries is None:
        legend_entries = ["Curve {}".format(i) for i in range(n_curves)]

    # Get horizontal axis errors
    if error_range is None:
        if error_type == "me_norm":
            x_axis_limit = 0.05
            x_axis_step = 0.005
            x_label = "Normalized Point-to-Point Error"
        elif error_type == "me" or error_type == "rmse":
            x_axis_limit = 5.0
            x_axis_step = 0.5
            x_label = "Point-to-Point Error"
        else:
            raise ValueError("error_type must be me_norm or me or rmse")
    else:
        x_axis_limit = (error_range[1] + error_range[0]) / 2
        x_axis_step = error_range[2]
        x_label = "Error"

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        # plot with selected options
        opts = plot_wid.selected_values.copy()
        new_figure_size = (
            plot_wid.selected_values["zoom"][0] * figure_size[0],
            plot_wid.selected_values["zoom"][1] * figure_size[1],
        )
        del opts["zoom"]
        if opts["axes_x_limits"] is None:
            tmp_error_range = None
        elif isinstance(opts["axes_x_limits"], float):
            tmp_error_range = [0.0, np.max(errors), x_axis_step]
        else:
            tmp_error_range = [
                opts["axes_x_limits"][0],
                1.0001 * opts["axes_x_limits"][1],
                x_axis_step,
            ]
        save_figure_wid.renderer = plot_cumulative_error_distribution(
            errors,
            error_range=tmp_error_range,
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            figure_size=new_figure_size,
            **opts
        )

        # show plot
        save_figure_wid.renderer.force_draw()

    # Create widgets
    plot_wid = PlotMatplotlibOptionsWidget(
        legend_entries=legend_entries, render_function=render_function
    )
    save_figure_wid = SaveMatplotlibFigureOptionsWidget()

    # Set values in plot widget
    plot_wid.remove_render_function()
    plot_wid.x_label.value = x_label
    plot_wid.y_label.value = "Images Proportion"
    plot_wid.title.value = "Cumulative error distribution"
    plot_wid.axes_wid.axes_limits_widget.axes_x_limits_toggles.value = "range"
    plot_wid.axes_wid.axes_limits_widget.axes_x_limits_range.set_widget_state(
        [0.0, x_axis_limit], allow_callback=False
    )
    plot_wid.axes_wid.axes_limits_widget.axes_y_limits_toggles.value = "range"
    plot_wid.axes_wid.axes_limits_widget.axes_y_limits_range.set_widget_state(
        [0.0, 1.0], allow_callback=False
    )
    plot_wid.axes_wid.axes_ticks_widget.axes_x_ticks_toggles.value = "auto"

    plot_wid.axes_wid.axes_ticks_widget.axes_y_ticks_toggles.value = "list"
    plot_wid.axes_wid.axes_ticks_widget.axes_y_ticks_list.set_widget_state(
        list(np.arange(0.0, 1.1, 0.1)), allow_callback=False
    )
    plot_wid.add_render_function(render_function)

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
    wid = ipywidgets.HBox([logo, plot_wid])
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)
    plot_wid.container.border = "0px"
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})

    # return widget object if asked
    if return_widget:
        return final_box


def visualize_fitting_results(
    fitting_results,
    figure_size=(7, 7),
    browser_style="buttons",
    custom_info_callback=None,
):
    r"""
    Widget that allows browsing through a `list` of fitting results.

    Parameters
    ----------
    fitting_results : `list` of `menpofit.result.Result` or `subclass`
        The `list` of fitting results to be displayed. Note that the fitting
        results can have different attributes between them, i.e. different
        number of iterations, number of channels etc.
    figure_size : (`int`, `int`), optional
        The initial size of the plotted figures.
    browser_style : ``{'buttons', 'slider'}``, optional
        It defines whether the selector of the objects will have the form of
        plus/minus buttons or a slider.
    custom_info_callback: `function` or ``None``, optional
        If not None, it should be a function that accepts a fitting result
        and returns a list of custom messages to be printed per result.
        Each custom message will be printed in a separate line.
    """
    # Make sure that fitting_results is a list even with one fitting_result
    if not isinstance(fitting_results, Sized):
        fitting_results = [fitting_results]

    # Get the number of fitting_results
    n_fitting_results = len(fitting_results)

    # Define the styling options
    main_style = "info"

    output = ipywidgets.Output()

    @output.capture(clear_output=True, wait=True)
    def plot_errors_function(name):
        # Get selected index
        i = image_number_wid.selected_values if n_fitting_results > 1 else 0

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * 10,
            renderer_options_wid.selected_values["zoom_one"] * 3,
        )
        save_figure_wid.renderer = fitting_results[i].plot_errors(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            figure_size=new_figure_size,
        )
        save_figure_wid.renderer.force_draw()

    @output.capture(clear_output=True, wait=True)
    def plot_displacements_function(name):
        # Get selected index
        i = image_number_wid.selected_values if n_fitting_results > 1 else 0

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * 10,
            renderer_options_wid.selected_values["zoom_one"] * 3,
        )
        save_figure_wid.renderer = fitting_results[i].plot_displacements(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            figure_size=new_figure_size,
            stat_type="mean",
        )
        save_figure_wid.renderer.force_draw()

    @output.capture(clear_output=True, wait=True)
    def plot_costs_function(name):
        # Get selected index
        im = image_number_wid.selected_values if n_fitting_results > 1 else 0

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * 10,
            renderer_options_wid.selected_values["zoom_one"] * 3,
        )
        save_figure_wid.renderer = fitting_results[im].plot_costs(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False,
            figure_size=new_figure_size,
        )
        save_figure_wid.renderer.force_draw()

    @output.capture(clear_output=True, wait=True)
    def render_function(change):
        # get selected object
        i = image_number_wid.selected_values if n_fitting_results > 1 else 0

        # get selected options
        tmp1 = renderer_options_wid.selected_values["markers_matplotlib"]
        tmp2 = renderer_options_wid.selected_values["lines_matplotlib"]
        options = fitting_result_wid.selected_values
        options.update(renderer_options_wid.selected_values["axes"])
        options.update(renderer_options_wid.selected_values["legend"])
        options.update(renderer_options_wid.selected_values["numbering_matplotlib"])
        options.update(renderer_options_wid.selected_values["image_matplotlib"])
        new_figure_size = (
            renderer_options_wid.selected_values["zoom_one"] * figure_size[0],
            renderer_options_wid.selected_values["zoom_one"] * figure_size[1],
        )

        # get selected view function
        if (
            fitting_result_wid.result_iterations_tab.selected_index == 0
            or not fitting_results[i].is_iterative
        ):
            # use view()
            # final shape colour
            final_marker_face_colour = tmp1["marker_face_colour"][0]
            final_marker_edge_colour = tmp1["marker_edge_colour"][0]
            final_line_colour = tmp2["line_colour"][0]
            # initial shape colour
            initial_marker_face_colour = "b"
            initial_marker_edge_colour = "b"
            initial_line_colour = "b"
            if fitting_results[i].initial_shape is not None:
                initial_marker_face_colour = tmp1["marker_face_colour"][1]
                initial_marker_edge_colour = tmp1["marker_edge_colour"][1]
                initial_line_colour = tmp2["line_colour"][1]
            # gt shape colour
            gt_marker_face_colour = "y"
            gt_marker_edge_colour = "y"
            gt_line_colour = "y"
            if fitting_results[i].gt_shape is not None:
                if fitting_results[i].initial_shape is not None:
                    gt_marker_face_colour = tmp1["marker_face_colour"][2]
                    gt_marker_edge_colour = tmp1["marker_edge_colour"][2]
                    gt_line_colour = tmp2["line_colour"][2]
                else:
                    gt_marker_face_colour = tmp1["marker_face_colour"][1]
                    gt_marker_edge_colour = tmp1["marker_edge_colour"][1]
                    gt_line_colour = tmp2["line_colour"][1]
            # render
            save_figure_wid.renderer = fitting_results[i].view(
                figure_id=save_figure_wid.renderer.figure_id,
                new_figure=False,
                render_markers=tmp1["render_markers"],
                final_marker_face_colour=final_marker_face_colour,
                final_marker_edge_colour=final_marker_edge_colour,
                final_line_colour=final_line_colour,
                initial_marker_face_colour=initial_marker_face_colour,
                initial_marker_edge_colour=initial_marker_edge_colour,
                initial_line_colour=initial_line_colour,
                gt_marker_face_colour=gt_marker_face_colour,
                gt_marker_edge_colour=gt_marker_edge_colour,
                gt_line_colour=gt_line_colour,
                marker_style=tmp1["marker_style"],
                marker_size=tmp1["marker_size"],
                marker_edge_width=tmp1["marker_edge_width"],
                render_lines=tmp2["render_lines"],
                line_style=tmp2["line_style"],
                line_width=tmp2["line_width"],
                figure_size=new_figure_size,
                **options
            )
        else:
            # use view_iterations()
            if fitting_result_wid.iterations_mode.value == "animation":
                # The mode is 'Animation'
                # get colours
                marker_face_colour = tmp1["marker_face_colour"][0]
                marker_edge_colour = tmp1["marker_edge_colour"][0]
                line_colour = tmp2["line_colour"][0]
            else:
                # The mode is 'Static'
                # get colours
                marker_face_colour = [
                    tmp1["marker_face_colour"][i]
                    for i in fitting_result_wid.selected_values["iters"]
                ]
                marker_edge_colour = [
                    tmp1["marker_edge_colour"][i]
                    for i in fitting_result_wid.selected_values["iters"]
                ]
                line_colour = [
                    tmp2["line_colour"][i]
                    for i in fitting_result_wid.selected_values["iters"]
                ]

            # render
            save_figure_wid.renderer = fitting_results[i].view_iterations(
                figure_id=save_figure_wid.renderer.figure_id,
                new_figure=False,
                render_markers=tmp1["render_markers"],
                marker_face_colour=marker_face_colour,
                marker_style=tmp1["marker_style"],
                marker_size=tmp1["marker_size"],
                marker_edge_colour=marker_edge_colour,
                marker_edge_width=tmp1["marker_edge_width"],
                render_lines=tmp2["render_lines"],
                line_style=tmp2["line_style"],
                line_width=tmp2["line_width"],
                line_colour=line_colour,
                figure_size=new_figure_size,
                **options
            )

        # Show figure
        save_figure_wid.renderer.force_draw()

        # update info text widget
        update_info({}, custom_info_callback=custom_info_callback)

    # Define function that updates info text
    def update_info(change, custom_info_callback=None):
        # Get selected object
        im = image_number_wid.selected_values if n_fitting_results > 1 else 0
        fr = fitting_results[im]

        # Errors
        text_per_line = []
        if fr.gt_shape is not None:
            # Get error function
            error_fun = euclidean_bb_normalised_error
            if error_type_toggles.value == "RMS":
                error_fun = root_mean_square_bb_normalised_error
            # Set error options visibility
            error_box.layout.visibility = "visible"
            # Compute errors
            if fr.initial_shape is not None:
                text_per_line.append(
                    " > Initial error: {:.4f}".format(
                        error_fun(
                            fr.initial_shape,
                            fr.gt_shape,
                            norm_type=norm_type_toggles.value,
                        )
                    )
                )
            text_per_line.append(
                " > Final error: {:.4f}".format(
                    error_fun(
                        fr.final_shape, fr.gt_shape, norm_type=norm_type_toggles.value
                    )
                )
            )
        else:
            # Set error options visibility
            error_box.layout.visibility = "hidden"
            text_per_line.append(" > No groundtruth shape.")

        # Landmarks, scales, iterations
        text_per_line.append(" > {} landmark points.".format(fr.final_shape.n_points))
        if fr.is_iterative:
            text_per_line.append(" > {} iterations.".format(fr.n_iters))
        else:
            text_per_line.append(" > No iterations.")
        if hasattr(fr, "n_scales"):
            text_per_line.append(" > {} scales.".format(fr.n_scales))
        if custom_info_callback is not None:
            # iterate over the list of messages returned by the callback
            # function and append them in the text_per_line.
            for msg in custom_info_callback(fr):
                text_per_line.append("> {}".format(msg))
        info_wid.set_widget_state(text_per_line=text_per_line)

    # Create renderer widget
    labels = ["Final"]
    default_colours = ["red"]
    if fitting_results[0].initial_shape is not None:
        labels.append("Initial")
        default_colours.append("blue")
    if fitting_results[0].gt_shape is not None:
        labels.append("Groundtruth")
        default_colours.append("yellow")
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=[
            "markers_matplotlib",
            "lines_matplotlib",
            "zoom_one",
            "legend",
            "numbering_matplotlib",
            "image_matplotlib",
            "axes",
        ],
        labels=labels,
        axes_x_limits=None,
        axes_y_limits=None,
        render_function=None,
    )
    # Set initial values
    renderer_options_wid.options_widgets[3].render_legend_switch.set_widget_state(
        True, allow_callback=False
    )
    renderer_options_wid.options_widgets[0].marker_face_colour_widget.set_colours(
        default_colours, allow_callback=False
    )
    renderer_options_wid.options_widgets[0].marker_edge_colour_widget.set_colours(
        ["black"] * len(default_colours), allow_callback=False
    )
    renderer_options_wid.options_widgets[1].line_colour_widget.set_colours(
        default_colours, allow_callback=False
    )
    renderer_options_wid.add_render_function(render_function)

    # Create info and error options
    info_wid = TextPrintWidget(text_per_line=[""])
    error_type_toggles = ipywidgets.ToggleButtons(
        options=["Euclidean", "RMS"], value="Euclidean", description="Error type"
    )
    norm_type_toggles = ipywidgets.ToggleButtons(
        options=["area", "perimeter", "avg_edge_length", "diagonal"],
        value="avg_edge_length",
        description="Normalise",
    )
    error_box = ipywidgets.VBox([error_type_toggles, norm_type_toggles])
    error_box.layout.display = (
        "flex" if fitting_results[0].gt_shape is not None else "none"
    )
    error_type_toggles.observe(update_info, names="value", type="change")
    norm_type_toggles.observe(update_info, names="value", type="change")
    info_error_box = ipywidgets.HBox([info_wid, error_box])

    # Create save figure widget
    save_figure_wid = SaveMatplotlibFigureOptionsWidget()

    def update_renderer_options(change):
        # Get selected fitting result object
        i = image_number_wid.selected_values if n_fitting_results > 1 else 0

        # Get labels
        if fitting_result_wid.result_iterations_tab.selected_index == 0:
            # We are at the Results tab
            labels = ["Final"]
            if fitting_results[i].initial_shape is not None:
                labels.append("Initial")
            if fitting_results[i].gt_shape is not None:
                labels.append("Groundtruth")
        else:
            # We are at the Iterations tab
            if fitting_result_wid.iterations_mode.value == "animation":
                # The mode is 'Animation'
                labels = None
            else:
                # The mode is 'Static'
                n_digits = len(str(len(fitting_results[i].shapes)))
                labels = []
                for j in list(range(len(fitting_results[i].shapes))):
                    if j == 0 and fitting_results[i].initial_shape is not None:
                        labels.append("Initial")
                    elif j == len(fitting_results[i].shapes) - 1:
                        labels.append("Final")
                    else:
                        labels.append("iteration {:0{}d}".format(j, n_digits))
        renderer_options_wid.set_widget_state(labels=labels, allow_callback=False)

    n_shapes = None
    if fitting_results[0].is_iterative:
        n_shapes = len(fitting_results[0].shapes)
    has_costs = fitting_results[0].is_iterative and fitting_results[0].costs is not None
    fitting_result_wid = IterativeResultOptionsWidget(
        has_gt_shape=fitting_results[0].gt_shape is not None,
        has_initial_shape=fitting_results[0].initial_shape is not None,
        has_image=fitting_results[0].image is not None,
        n_shapes=n_shapes,
        has_costs=has_costs,
        render_function=render_function,
        tab_update_function=update_renderer_options,
        displacements_function=plot_displacements_function,
        errors_function=plot_errors_function,
        costs_function=plot_costs_function,
    )

    # Group widgets
    if n_fitting_results > 1:
        # Define function that updates options' widgets state
        def update_widgets(change):
            # stop iterations animation
            fitting_result_wid.index_animation.stop_animation()

            # get selected fitting result
            i = image_number_wid.selected_values

            # Update fitting result options
            n_shapes = None
            if fitting_results[i].is_iterative:
                n_shapes = len(fitting_results[i].shapes)
            has_costs = (
                fitting_results[i].is_iterative and fitting_results[i].costs is not None
            )
            fitting_result_wid.set_widget_state(
                has_gt_shape=fitting_results[i].gt_shape is not None,
                has_initial_shape=fitting_results[i].initial_shape is not None,
                has_image=fitting_results[i].image is not None,
                n_shapes=n_shapes,
                has_costs=has_costs,
                allow_callback=False,
            )

            # Update renderer options
            update_renderer_options({})

            # Render callback
            render_function({})

        # Image selection slider
        index = {"min": 0, "max": n_fitting_results - 1, "step": 1, "index": 0}
        image_number_wid = AnimationOptionsWidget(
            index,
            render_function=update_widgets,
            index_style=browser_style,
            interval=0.2,
            description="Image",
            loop_enabled=True,
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
    # Widget titles
    tab_titles = ["Result", "Info", "Renderer", "Export"]
    options_box = ipywidgets.Tab(
        [fitting_result_wid, info_error_box, renderer_options_wid, save_figure_wid]
    )
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    if n_fitting_results > 1:
        wid = ipywidgets.VBox([header_wid, options_box])
    else:
        wid = ipywidgets.HBox([header_wid, options_box])
    if n_fitting_results > 1:
        # If animation is activated and the user selects the save figure tab,
        # then the animation stops.
        def save_fig_tab_fun(change):
            if change["new"] == 3:
                image_number_wid.pause_animation()

        options_box.observe(save_fig_tab_fun, names="selected_index", type="change")

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = "2px solid " + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = "flex"
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})
