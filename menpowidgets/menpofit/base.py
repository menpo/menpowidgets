from menpo.base import MenpoMissingDependencyError


try:
    import menpofit
except ImportError:
    raise MenpoMissingDependencyError('menpofit')


# Continue with imports if we have menpofit
from collections import OrderedDict
import numpy as np

import ipywidgets
import IPython.display as ipydisplay

import matplotlib.pyplot as plt

from menpo.base import name_of_callable
from menpo.image import MaskedImage
from menpo.image.base import _convert_patches_list_to_single_array

from menpofit.error import (euclidean_bb_normalised_error,
                            root_mean_square_bb_normalised_error)

from ..checks import check_n_parameters
from ..options import (SaveFigureOptionsWidget, RendererOptionsWidget,
                       ChannelOptionsWidget, PatchOptionsWidget,
                       LandmarkOptionsWidget, LinearModelParametersWidget,
                       PlotOptionsWidget, AnimationOptionsWidget,
                       TextPrintWidget)
from ..style import map_styles_to_hex_colours
from ..tools import LogoWidget
from ..utils import (render_patches, render_image,
                     extract_groups_labels_from_image)

from .options import IterativeResultOptionsWidget


def visualize_aam(aam, n_shape_parameters=5, n_appearance_parameters=5,
                  mode='multiple', parameters_bounds=(-3.0, 3.0),
                  figure_size=(10, 8), style='coloured'):
    r"""
    Widget that allows the dynamic visualization of a multi-scale Active
    Appearance Model.

    Parameters
    ----------
    aam : `menpofit.aam.AAM`
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
    style : ``{'coloured', 'minimal'}``, optional
        If ``'coloured'``, then the style of the widget will be coloured. If
        ``minimal``, then the style is simple using black and white colours.
    """
    # Ensure that the code is being run inside a Jupyter kernel!
    from menpowidgets.utils import verify_ipython_and_kernel
    verify_ipython_and_kernel()
    print('Initializing...')

    # Get the number of levels
    n_levels = aam.n_scales

    # Define the styling options
    if style == 'coloured':
        model_style = 'info'
        model_tab_style = 'danger'
        model_parameters_style = 'danger'
        channels_style = 'danger'
        landmarks_style = 'danger'
        logo_style = 'info'
        widget_box_style = 'info'
        widget_border_radius = 10
        widget_border_width = 1
        info_style = 'danger'
        renderer_style = 'danger'
        renderer_tabs_style = 'info'
        save_figure_style = 'danger'
    elif style == 'minimal':
        model_style = ''
        model_tab_style = ''
        model_parameters_style = 'minimal'
        channels_style = 'minimal'
        landmarks_style = 'minimal'
        logo_style = 'minimal'
        widget_box_style = ''
        widget_border_radius = 0
        widget_border_width = 0
        info_style = 'minimal'
        renderer_style = 'minimal'
        renderer_tabs_style = 'minimal'
        save_figure_style = 'minimal'
    else:
        raise ValueError("style must be either coloured or minimal")

    # Get the maximum number of components per level
    max_n_shape = [sp.model.n_active_components for sp in aam.shape_models]
    max_n_appearance = [ap.n_active_components for ap in aam.appearance_models]

    # Check the given number of parameters (the returned n_parameters is a list
    # of len n_scales)
    n_shape_parameters = check_n_parameters(n_shape_parameters, n_levels,
                                            max_n_shape)
    n_appearance_parameters = check_n_parameters(n_appearance_parameters,
                                                 n_levels, max_n_appearance)

    # Define render function
    def render_function(change):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Compute weights and instance
        shape_weights = shape_model_parameters_wid.selected_values
        appearance_weights = appearance_model_parameters_wid.selected_values
        instance = aam.instance(scale_index=level, shape_weights=shape_weights,
                                appearance_weights=appearance_weights)
        image_is_masked = isinstance(instance, MaskedImage)
        selected_group = landmark_options_wid.selected_values['group']

        # Render instance with selected options
        tmp1 = renderer_options_wid.selected_values['lines']
        tmp2 = renderer_options_wid.selected_values['markers']
        options = renderer_options_wid.selected_values['numbering']
        options.update(renderer_options_wid.selected_values['axes'])
        options.update(renderer_options_wid.selected_values['image'])
        options.update(channel_options_wid.selected_values)
        options.update(landmark_options_wid.selected_values)
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * figure_size[0],
            renderer_options_wid.selected_values['zoom_one'] * figure_size[1])
        # get line and marker colours
        line_colour = []
        marker_face_colour = []
        marker_edge_colour = []
        if instance.has_landmarks:
            for lbl in landmark_options_wid.selected_values['with_labels']:
                lbl_idx = instance.landmarks[selected_group].labels.index(lbl)
                line_colour.append(tmp1['line_colour'][lbl_idx])
                marker_face_colour.append(tmp2['marker_face_colour'][lbl_idx])
                marker_edge_colour.append(tmp2['marker_edge_colour'][lbl_idx])

        # show image with selected options
        renderer = render_image(
            image=instance, renderer=save_figure_wid.renderer,
            image_is_masked=image_is_masked,
            render_lines=tmp1['render_lines'], line_style=tmp1['line_style'],
            line_width=tmp1['line_width'], line_colour=line_colour,
            render_markers=tmp2['render_markers'],
            marker_style=tmp2['marker_style'],
            marker_size=tmp2['marker_size'],
            marker_edge_width=tmp2['marker_edge_width'],
            marker_edge_colour=marker_edge_colour,
            marker_face_colour=marker_face_colour,
            figure_size=new_figure_size, legend_n_columns=None,
            legend_border_axes_pad=None, legend_rounded_corners=None,
            legend_title=None, legend_horizontal_spacing=None,
            legend_shadow=None, legend_location=None, legend_font_name=None,
            legend_bbox_to_anchor=None, legend_border=None,
            legend_marker_scale=None, legend_vertical_spacing=None,
            legend_font_weight=None, legend_font_size=None, render_legend=False,
            legend_font_style=None, legend_border_padding=None, **options)

        # Update info
        update_info(aam, instance, level, selected_group)

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Define function that updates the info text
    def update_info(aam, instance, level, group):
        # features info
        lvl_app_mod = aam.appearance_models[level]
        lvl_shape_mod = aam.shape_models[level].model
        aam_mean = lvl_app_mod.mean()
        n_channels = aam_mean.n_channels
        tmplt_inst = lvl_app_mod.template_instance
        feat = aam.holistic_features[level]

        # Feature string
        tmp_feat = 'Feature is {} with {} channel{}'.format(
            name_of_callable(feat), n_channels, 's' * (n_channels > 1))

        # update info widgets
        text_per_line = [
            "> Warp using {} transform".format(aam.transform.__name__),
            "> Level {}/{}".format(
                level + 1, aam.n_scales),
            "> {} landmark points".format(
                instance.landmarks[group].lms.n_points),
            "> {} shape components ({:.2f}% of variance)".format(
                lvl_shape_mod.n_components,
                lvl_shape_mod.variance_ratio() * 100),
            "> {}".format(tmp_feat),
            "> Reference frame of length {} ({} x {}C, {} x {}C)".format(
                lvl_app_mod.n_features, tmplt_inst.n_true_pixels(), n_channels,
                tmplt_inst._str_shape(), n_channels),
            "> {} appearance components ({:.2f}% of variance)".format(
                lvl_app_mod.n_components, lvl_app_mod.variance_ratio() * 100),
            "> Instance: min={:.3f} , max={:.3f}".format(
                instance.pixels.min(), instance.pixels.max())]
        info_wid.set_widget_state(text_per_line=text_per_line)

    # Plot shape variance function
    def plot_shape_variance(name):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # Get selected level
        level = 0
        if n_levels > 1:
            level = level_wid.value

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * 10,
            renderer_options_wid.selected_values['zoom_one'] * 3)
        plt.subplot(121)
        aam.shape_models[level].model.plot_eigenvalues_ratio(
            figure_id=save_figure_wid.renderer.figure_id)
        plt.subplot(122)
        renderer = aam.shape_models[level].model.plot_eigenvalues_cumulative_ratio(
            figure_id=save_figure_wid.renderer.figure_id,
            figure_size=new_figure_size)
        plt.show()

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Plot appearance variance function
    def plot_appearance_variance(name):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # Get selected level
        level = 0
        if n_levels > 1:
            level = level_wid.value

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * 10,
            renderer_options_wid.selected_values['zoom_one'] * 3)
        plt.subplot(121)
        aam.appearance_models[level].plot_eigenvalues_ratio(
            figure_id=save_figure_wid.renderer.figure_id)
        plt.subplot(122)
        renderer = aam.appearance_models[level]. \
            plot_eigenvalues_cumulative_ratio(
            figure_id=save_figure_wid.renderer.figure_id,
            figure_size=new_figure_size)
        plt.show()

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Create widgets
    shape_model_parameters_wid = LinearModelParametersWidget(
            n_shape_parameters[0], render_function, params_str='Parameter ',
            mode=mode, params_bounds=parameters_bounds, params_step=0.1,
            plot_variance_visible=True,
            plot_variance_function=plot_shape_variance,
            style=model_parameters_style, animation_step=0.5, interval=0.,
            loop_enabled=True)
    appearance_model_parameters_wid = LinearModelParametersWidget(
            n_appearance_parameters[0], render_function, params_str='Parameter ',
            mode=mode, params_bounds=parameters_bounds, params_step=0.1,
            plot_variance_visible=True,
            plot_variance_function=plot_appearance_variance,
            style=model_parameters_style, animation_step=0.5, interval=0.,
            loop_enabled=True)
    groups_keys, labels_keys = extract_groups_labels_from_image(
            aam.appearance_models[0].mean())
    channel_options_wid = ChannelOptionsWidget(
            n_channels=aam.appearance_models[0].mean().n_channels,
            image_is_masked=isinstance(aam.appearance_models[0].mean(), MaskedImage),
            render_function=render_function, style=channels_style)
    renderer_options_wid = RendererOptionsWidget(
            options_tabs=['markers', 'lines', 'image', 'numbering', 'zoom_one',
                          'axes'], labels=labels_keys[0],
            axes_x_limits=None, axes_y_limits=None,
            render_function=render_function,  style=renderer_style,
            tabs_style=renderer_tabs_style)
    landmark_options_wid = LandmarkOptionsWidget(
            group_keys=groups_keys, labels_keys=labels_keys,
            render_function=render_function, style=landmarks_style,
            renderer_widget=renderer_options_wid)
    info_wid = TextPrintWidget(text_per_line=[''] * 11, style=info_style)
    save_figure_wid = SaveFigureOptionsWidget(renderer=None,
                                              style=save_figure_style)

    # Define function that updates options' widgets state
    def update_widgets(change):
        value = change['new']
        # Update shape model parameters
        shape_model_parameters_wid.set_widget_state(
            n_shape_parameters[value], params_str='Parameter ',
            allow_callback=False)

        # Update appearance model parameters
        appearance_model_parameters_wid.set_widget_state(
            n_appearance_parameters[value], params_str='Parameter ',
            allow_callback=False)

        # Update channel options
        channel_options_wid.set_widget_state(
            n_channels=aam.appearance_models[value].mean().n_channels,
            image_is_masked=isinstance(aam.appearance_models[value].mean(),
                                       MaskedImage),
            allow_callback=True)

    # Group widgets
    model_parameters_wid = ipywidgets.Tab(
        children=[shape_model_parameters_wid, appearance_model_parameters_wid])
    model_parameters_wid.set_title(0, 'Shape')
    model_parameters_wid.set_title(1, 'Appearance')
    model_parameters_wid = ipywidgets.FlexBox(children=[model_parameters_wid],
                                              margin='0.2cm', padding='0.1cm',
                                              box_style=model_tab_style)
    tmp_children = [model_parameters_wid]
    if n_levels > 1:
        radio_str = OrderedDict()
        for l in range(n_levels):
            if l == 0:
                radio_str["Level {} (low)".format(l)] = l
            elif l == n_levels - 1:
                radio_str["Level {} (high)".format(l)] = l
            else:
                radio_str["Level {}".format(l)] = l
        level_wid = ipywidgets.RadioButtons(
            options=radio_str, description='Pyramid:', value=n_levels-1)
        level_wid.observe(update_widgets, names='value', type='change')
        level_wid.observe(render_function, names='value', type='change')
        tmp_children.insert(0, level_wid)
    tmp_wid = ipywidgets.HBox(children=tmp_children, align='center',
                              box_style=model_style)
    options_box = ipywidgets.Tab(children=[tmp_wid, channel_options_wid,
                                           landmark_options_wid,
                                           renderer_options_wid,
                                           info_wid, save_figure_wid])
    tab_titles = ['Model', 'Channels', 'Landmarks', 'Renderer', 'Info',
                  'Export']
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    logo_wid = LogoWidget(style=logo_style)
    logo_wid.margin = '0.1cm'
    wid = ipywidgets.HBox(children=[logo_wid, options_box], align='start')

    # Set widget's style
    wid.box_style = widget_box_style
    wid.border_radius = widget_border_radius
    wid.border_width = widget_border_width
    wid.border_color = map_styles_to_hex_colours(widget_box_style)
    renderer_options_wid.margin = '0.2cm'

    # Display final widget
    ipydisplay.display(wid)

    # Trigger initial visualization
    render_function({})


def visualize_patch_aam(aam, n_shape_parameters=5, n_appearance_parameters=5,
                        mode='multiple', parameters_bounds=(-3.0, 3.0),
                        figure_size=(10, 8), style='coloured'):
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
    style : ``{'coloured', 'minimal'}``, optional
        If ``'coloured'``, then the style of the widget will be coloured. If
        ``minimal``, then the style is simple using black and white colours.
    """
    # Ensure that the code is being run inside a Jupyter kernel!
    from menpowidgets.utils import verify_ipython_and_kernel
    verify_ipython_and_kernel()
    print('Initializing...')

    # Get the number of levels
    n_levels = aam.n_scales

    # Define the styling options
    if style == 'coloured':
        model_style = 'info'
        model_tab_style = 'danger'
        model_parameters_style = 'danger'
        patches_style = 'minimal'
        patches_subwidgets_style = 'danger'
        channels_style = 'danger'
        logo_style = 'info'
        widget_box_style = 'info'
        widget_border_radius = 10
        widget_border_width = 1
        info_style = 'danger'
        renderer_style = 'danger'
        renderer_tabs_style = 'info'
        save_figure_style = 'danger'
    elif style == 'minimal':
        model_style = 'info'
        model_tab_style = ''
        model_parameters_style = 'minimal'
        patches_style = 'minimal'
        patches_subwidgets_style = 'minimal'
        channels_style = 'minimal'
        logo_style = 'minimal'
        widget_box_style = ''
        widget_border_radius = 0
        widget_border_width = 0
        info_style = 'minimal'
        renderer_style = 'minimal'
        renderer_tabs_style = 'minimal'
        save_figure_style = 'minimal'
    else:
        raise ValueError("style must be either coloured or minimal")

    # Get the maximum number of components per level
    max_n_shape = [sp.model.n_active_components for sp in aam.shape_models]
    max_n_appearance = [ap.n_active_components for ap in aam.appearance_models]

    # Check the given number of parameters (the returned n_parameters is a list
    # of len n_scales)
    n_shape_parameters = check_n_parameters(n_shape_parameters, n_levels,
                                            max_n_shape)
    n_appearance_parameters = check_n_parameters(n_appearance_parameters,
                                                 n_levels, max_n_appearance)

    # Define render function
    def render_function(change):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Compute weights and instance
        shape_weights = shape_model_parameters_wid.selected_values
        appearance_weights = appearance_model_parameters_wid.selected_values
        shape_instance, appearance_instance = aam.instance(
            scale_index=level, shape_weights=shape_weights,
            appearance_weights=appearance_weights)

        # Render instance with selected options
        options = renderer_options_wid.selected_values['lines']
        options.update(renderer_options_wid.selected_values['markers'])
        options.update(renderer_options_wid.selected_values['numbering'])
        options.update(renderer_options_wid.selected_values['axes'])
        options.update(renderer_options_wid.selected_values['image'])
        options.update(patch_options_wid.selected_values)
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * figure_size[0],
            renderer_options_wid.selected_values['zoom_one'] * figure_size[1])

        # show image with selected options
        renderer = render_patches(
            patches=appearance_instance.pixels, patch_centers=shape_instance,
            renderer=save_figure_wid.renderer, figure_size=new_figure_size,
            channels=channel_options_wid.selected_values['channels'],
            glyph_enabled=channel_options_wid.selected_values['glyph_enabled'],
            glyph_block_size=channel_options_wid.selected_values['glyph_block_size'],
            glyph_use_negative=channel_options_wid.selected_values['glyph_use_negative'],
            sum_enabled=channel_options_wid.selected_values['sum_enabled'],
            **options)

        # Update info
        update_info(aam, appearance_instance, level)

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Define function that updates the info text
    def update_info(aam, appearance_instance, level):
        lvl_app_mod = aam.appearance_models[level]
        lvl_shape_mod = aam.shape_models[level].model
        n_channels = lvl_app_mod.mean().pixels.shape[2]
        feat = aam.holistic_features[level]

        # Feature string
        tmp_feat = 'Feature is {} with {} channel{}'.format(
            name_of_callable(feat), n_channels, 's' * (n_channels > 1))
        n_feat = (appearance_instance.pixels.shape[0] *
                  appearance_instance.pixels.shape[2] *
                  appearance_instance.pixels.shape[3] *
                  appearance_instance.pixels.shape[4])

        # update info widgets
        text_per_line = [
            "> No image warping performed.",
            "> Level {}/{}".format(level + 1, aam.n_scales),
            "> {} landmark points".format(appearance_instance.pixels.shape[0]),
            "> {} shape components ({:.2f}% of variance)".format(
                lvl_shape_mod.n_components,
                lvl_shape_mod.variance_ratio() * 100),
            "> {}".format(tmp_feat),
            "> Reference frame of length {} ({} patches of shape {} x {} "
            "and {} channel{}.)".format(
                n_feat, appearance_instance.pixels.shape[0],
                appearance_instance.pixels.shape[3],
                appearance_instance.pixels.shape[4],
                appearance_instance.pixels.shape[2],
                's' * (appearance_instance.pixels.shape[2] > 1)),
            "> {} appearance components ({:.2f}% of variance)".format(
                lvl_app_mod.n_components, lvl_app_mod.variance_ratio() * 100),
            "> Instance: min={:.3f} , max={:.3f}".format(
                appearance_instance.pixels.min(),
                appearance_instance.pixels.max())]
        info_wid.set_widget_state(text_per_line=text_per_line)

    # Plot shape variance function
    def plot_shape_variance(name):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # Get selected level
        level = 0
        if n_levels > 1:
            level = level_wid.value

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * 10,
            renderer_options_wid.selected_values['zoom_one'] * 3)
        plt.subplot(121)
        aam.shape_models[level].model.plot_eigenvalues_ratio(
            figure_id=save_figure_wid.renderer.figure_id)
        plt.subplot(122)
        renderer = aam.shape_models[level].model.plot_eigenvalues_cumulative_ratio(
            figure_id=save_figure_wid.renderer.figure_id,
            figure_size=new_figure_size)
        plt.show()

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Plot appearance variance function
    def plot_appearance_variance(name):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # Get selected level
        level = 0
        if n_levels > 1:
            level = level_wid.value

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * 10,
            renderer_options_wid.selected_values['zoom_one'] * 3)
        plt.subplot(121)
        aam.appearance_models[level].plot_eigenvalues_ratio(
            figure_id=save_figure_wid.renderer.figure_id)
        plt.subplot(122)
        renderer = aam.appearance_models[level]. \
            plot_eigenvalues_cumulative_ratio(
            figure_id=save_figure_wid.renderer.figure_id,
            figure_size=new_figure_size)
        plt.show()

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Create widgets
    shape_model_parameters_wid = LinearModelParametersWidget(
            n_shape_parameters[0], render_function, params_str='Parameter ',
            mode=mode, params_bounds=parameters_bounds, params_step=0.1,
            plot_variance_visible=True, style=model_parameters_style,
            plot_variance_function=plot_shape_variance,
            animation_step=0.5, interval=0., loop_enabled=True)
    appearance_model_parameters_wid = LinearModelParametersWidget(
            n_appearance_parameters[0], render_function, params_str='Parameter ',
            mode=mode, params_bounds=parameters_bounds, params_step=0.1,
            plot_variance_visible=True, style=model_parameters_style,
            plot_variance_function=plot_appearance_variance,
            animation_step=0.5, interval=0., loop_enabled=True)
    patch_options_wid = PatchOptionsWidget(
            n_patches=aam.appearance_models[0].mean().pixels.shape[0],
            n_offsets=aam.appearance_models[0].mean().pixels.shape[1],
            render_function=render_function, style=patches_style,
            subwidgets_style=patches_subwidgets_style)
    channel_options_wid = ChannelOptionsWidget(
            n_channels=aam.appearance_models[0].mean().pixels.shape[2],
            image_is_masked=False, render_function=render_function,
            style=channels_style)
    renderer_options_wid = RendererOptionsWidget(
            options_tabs=['image', 'markers', 'lines', 'numbering', 'zoom_one',
                          'axes'], labels=None,
            axes_x_limits=None, axes_y_limits=None,
            render_function=None,  style=renderer_style,
            tabs_style=renderer_tabs_style)
    renderer_options_wid.options_widgets[0].interpolation_checkbox.value = True
    renderer_options_wid.add_render_function(render_function)
    info_wid = TextPrintWidget(text_per_line=[''] * 8, style=info_style)
    save_figure_wid = SaveFigureOptionsWidget(renderer=None,
                                              style=save_figure_style)

    # Define function that updates options' widgets state
    def update_widgets(change):
        value = change['new']
        # Update shape model parameters
        shape_model_parameters_wid.set_widget_state(
            n_shape_parameters[value], params_str='Parameter ',
            allow_callback=False)

        # Update appearance model parameters
        appearance_model_parameters_wid.set_widget_state(
            n_appearance_parameters[value], params_str='Parameter ',
            allow_callback=False)

        # Update patch options
        patch_options_wid.set_widget_state(
            n_patches=aam.appearance_models[value].mean().pixels.shape[0],
            n_offsets=aam.appearance_models[value].mean().pixels.shape[1],
            allow_callback=False)

        # Update channels options
        channel_options_wid.set_widget_state(
            n_channels=aam.appearance_models[value].mean().pixels.shape[2],
            image_is_masked=False, allow_callback=True)

    # Group widgets
    model_parameters_wid = ipywidgets.Tab(
        children=[shape_model_parameters_wid, appearance_model_parameters_wid])
    model_parameters_wid.set_title(0, 'Shape')
    model_parameters_wid.set_title(1, 'Appearance')
    model_parameters_wid = ipywidgets.FlexBox(children=[model_parameters_wid],
                                              margin='0.2cm', padding='0.1cm',
                                              box_style=model_tab_style)
    tmp_children = [model_parameters_wid]
    if n_levels > 1:
        radio_str = OrderedDict()
        for l in range(n_levels):
            if l == 0:
                radio_str["Level {} (low)".format(l)] = l
            elif l == n_levels - 1:
                radio_str["Level {} (high)".format(l)] = l
            else:
                radio_str["Level {}".format(l)] = l
        level_wid = ipywidgets.RadioButtons(
            options=radio_str, description='Pyramid:', value=n_levels-1)
        level_wid.observe(update_widgets, names='value', type='change')
        level_wid.observe(render_function, names='value', type='change')
        tmp_children.insert(0, level_wid)
    tmp_wid = ipywidgets.HBox(children=tmp_children, align='center',
                              box_style=model_style)
    options_box = ipywidgets.Tab(children=[tmp_wid, patch_options_wid,
                                           channel_options_wid,
                                           renderer_options_wid,
                                           info_wid, save_figure_wid])
    tab_titles = ['Model', 'Patches', 'Channels', 'Renderer', 'Info', 'Export']
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    logo_wid = LogoWidget(style=logo_style)
    logo_wid.margin = '0.1cm'
    wid = ipywidgets.HBox(children=[logo_wid, options_box], align='start')

    # Set widget's style
    wid.box_style = widget_box_style
    wid.border_radius = widget_border_radius
    wid.border_width = widget_border_width
    wid.border_color = map_styles_to_hex_colours(widget_box_style)
    renderer_options_wid.margin = '0.2cm'

    # Display final widget
    ipydisplay.display(wid)

    # Trigger initial visualization
    render_function({})


def visualize_atm(atm, n_shape_parameters=5, mode='multiple',
                  parameters_bounds=(-3.0, 3.0), figure_size=(10, 8),
                  style='coloured'):
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
    style : ``{'coloured', 'minimal'}``, optional
        If ``'coloured'``, then the style of the widget will be coloured. If
        ``minimal``, then the style is simple using black and white colours.
    """
    # Ensure that the code is being run inside a Jupyter kernel!
    from menpowidgets.utils import verify_ipython_and_kernel
    verify_ipython_and_kernel()
    print('Initializing...')

    # Get the number of levels
    n_levels = atm.n_scales

    # Define the styling options
    if style == 'coloured':
        model_style = 'info'
        model_parameters_style = 'danger'
        channels_style = 'danger'
        landmarks_style = 'danger'
        logo_style = 'info'
        widget_box_style = 'info'
        widget_border_radius = 10
        widget_border_width = 1
        info_style = 'danger'
        renderer_style = 'danger'
        renderer_tabs_style = 'info'
        save_figure_style = 'danger'
    elif style == 'minimal':
        model_style = ''
        model_parameters_style = 'minimal'
        channels_style = 'minimal'
        landmarks_style = 'minimal'
        logo_style = 'minimal'
        widget_box_style = ''
        widget_border_radius = 0
        widget_border_width = 0
        info_style = 'minimal'
        renderer_style = 'minimal'
        renderer_tabs_style = 'minimal'
        save_figure_style = 'minimal'
    else:
        raise ValueError("style must be either coloured or minimal")

    # Get the maximum number of components per level
    max_n_shape = [sp.model.n_active_components for sp in atm.shape_models]

    # Check the given number of parameters (the returned n_parameters is a list
    # of len n_scales)
    n_shape_parameters = check_n_parameters(n_shape_parameters, n_levels,
                                            max_n_shape)

    # Define render function
    def render_function(change):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Compute weights and instance
        shape_weights = shape_model_parameters_wid.selected_values
        instance = atm.instance(scale_index=level, shape_weights=shape_weights)
        image_is_masked = isinstance(instance, MaskedImage)
        selected_group = landmark_options_wid.selected_values['group']

        # Render instance with selected options
        tmp1 = renderer_options_wid.selected_values['lines']
        tmp2 = renderer_options_wid.selected_values['markers']
        options = renderer_options_wid.selected_values['numbering']
        options.update(renderer_options_wid.selected_values['axes'])
        options.update(renderer_options_wid.selected_values['image'])
        options.update(channel_options_wid.selected_values)
        options.update(landmark_options_wid.selected_values)
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * figure_size[0],
            renderer_options_wid.selected_values['zoom_one'] * figure_size[1])
        # get line and marker colours
        line_colour = []
        marker_face_colour = []
        marker_edge_colour = []
        if instance.has_landmarks:
            for lbl in landmark_options_wid.selected_values['with_labels']:
                lbl_idx = instance.landmarks[selected_group].labels.index(lbl)
                line_colour.append(tmp1['line_colour'][lbl_idx])
                marker_face_colour.append(tmp2['marker_face_colour'][lbl_idx])
                marker_edge_colour.append(tmp2['marker_edge_colour'][lbl_idx])

        # show image with selected options
        renderer = render_image(
            image=instance, renderer=save_figure_wid.renderer,
            image_is_masked=image_is_masked,
            render_lines=tmp1['render_lines'], line_style=tmp1['line_style'],
            line_width=tmp1['line_width'], line_colour=line_colour,
            render_markers=tmp2['render_markers'],
            marker_style=tmp2['marker_style'],
            marker_size=tmp2['marker_size'],
            marker_edge_width=tmp2['marker_edge_width'],
            marker_edge_colour=marker_edge_colour,
            marker_face_colour=marker_face_colour,
            figure_size=new_figure_size, legend_n_columns=None,
            legend_border_axes_pad=None, legend_rounded_corners=None,
            legend_title=None, legend_horizontal_spacing=None,
            legend_shadow=None, legend_location=None, legend_font_name=None,
            legend_bbox_to_anchor=None, legend_border=None,
            legend_marker_scale=None, legend_vertical_spacing=None,
            legend_font_weight=None, legend_font_size=None, render_legend=False,
            legend_font_style=None, legend_border_padding=None, **options)

        # Update info
        update_info(atm, instance, level, selected_group)

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Define function that updates the info text
    def update_info(atm, instance, level, group):
        lvl_shape_mod = atm.shape_models[level].model
        tmplt_inst = atm.warped_templates[level]
        n_channels = tmplt_inst.n_channels
        feat = atm.holistic_features[level]

        # Feature string
        tmp_feat = 'Feature is {} with {} channel{}'.format(
            name_of_callable(feat), n_channels, 's' * (n_channels > 1))

        # update info widgets
        text_per_line = [
            "> Warp using {} transform".format(atm.transform.__name__),
            "> Level {}/{}".format(
                level + 1, atm.n_scales),
            "> {} landmark points".format(
                instance.landmarks[group].lms.n_points),
            "> {} shape components ({:.2f}% of variance)".format(
                lvl_shape_mod.n_components,
                lvl_shape_mod.variance_ratio() * 100),
            "> {}".format(tmp_feat),
            "> Reference frame of length {} ({} x {}C, {} x {}C)".format(
                tmplt_inst.n_true_pixels() * n_channels,
                tmplt_inst.n_true_pixels(), n_channels, tmplt_inst._str_shape(),
                n_channels),
            "> Instance: min={:.3f} , max={:.3f}".format(
                instance.pixels.min(), instance.pixels.max())]
        info_wid.set_widget_state(text_per_line=text_per_line)

    # Plot shape variance function
    def plot_shape_variance(name):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # Get selected level
        level = 0
        if n_levels > 1:
            level = level_wid.value

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * 10,
            renderer_options_wid.selected_values['zoom_one'] * 3)
        plt.subplot(121)
        atm.shape_models[level].model.plot_eigenvalues_ratio(
            figure_id=save_figure_wid.renderer.figure_id)
        plt.subplot(122)
        renderer = atm.shape_models[level].model.plot_eigenvalues_cumulative_ratio(
            figure_id=save_figure_wid.renderer.figure_id,
            figure_size=new_figure_size)
        plt.show()

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Create widgets
    shape_model_parameters_wid = LinearModelParametersWidget(
            n_shape_parameters[0], render_function, params_str='Parameter ',
            mode=mode, params_bounds=parameters_bounds, params_step=0.1,
            plot_variance_visible=True,
            plot_variance_function=plot_shape_variance,
            style=model_parameters_style, animation_step=0.5, interval=0.,
            loop_enabled=True)
    groups_keys, labels_keys = extract_groups_labels_from_image(
            atm.warped_templates[0])
    channel_options_wid = ChannelOptionsWidget(
            n_channels=atm.warped_templates[0].n_channels,
            image_is_masked=isinstance(atm.warped_templates[0], MaskedImage),
            render_function=render_function, style=channels_style)
    renderer_options_wid = RendererOptionsWidget(
            options_tabs=['markers', 'lines', 'image', 'numbering', 'zoom_one',
                          'axes'], labels=labels_keys[0],
            axes_x_limits=None, axes_y_limits=None,
            render_function=render_function,  style=renderer_style,
            tabs_style=renderer_tabs_style)
    landmark_options_wid = LandmarkOptionsWidget(
            group_keys=groups_keys, labels_keys=labels_keys,
            render_function=render_function, style=landmarks_style,
            renderer_widget=renderer_options_wid)
    info_wid = TextPrintWidget(text_per_line=[''] * 10, style=info_style)
    save_figure_wid = SaveFigureOptionsWidget(renderer=None,
                                              style=save_figure_style)

    # Define function that updates options' widgets state
    def update_widgets(change):
        value = change['new']
        # Update shape model parameters
        shape_model_parameters_wid.set_widget_state(
            n_shape_parameters[value], params_str='Parameter ',
            allow_callback=False)

        # Update channel options
        channel_options_wid.set_widget_state(
            n_channels=atm.warped_templates[value].n_channels,
            image_is_masked=isinstance(atm.warped_templates[value], MaskedImage),
            allow_callback=True)

    # Group widgets
    tmp_children = [shape_model_parameters_wid]
    if n_levels > 1:
        radio_str = OrderedDict()
        for l in range(n_levels):
            if l == 0:
                radio_str["Level {} (low)".format(l)] = l
            elif l == n_levels - 1:
                radio_str["Level {} (high)".format(l)] = l
            else:
                radio_str["Level {}".format(l)] = l
        level_wid = ipywidgets.RadioButtons(
            options=radio_str, description='Pyramid:', value=n_levels-1)
        level_wid.observe(update_widgets, names='value', type='change')
        level_wid.observe(render_function, names='value', type='change')
        tmp_children.insert(0, level_wid)
    tmp_wid = ipywidgets.HBox(children=tmp_children, align='center',
                              box_style=model_style)
    options_box = ipywidgets.Tab(children=[tmp_wid, channel_options_wid,
                                           landmark_options_wid,
                                           renderer_options_wid,
                                           info_wid, save_figure_wid])
    tab_titles = ['Model', 'Channels', 'Landmarks', 'Renderer', 'Info',
                  'Export']
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    logo_wid = LogoWidget(style=logo_style)
    logo_wid.margin = '0.1cm'
    wid = ipywidgets.HBox(children=[logo_wid, options_box], align='start')

    # Set widget's style
    wid.box_style = widget_box_style
    wid.border_radius = widget_border_radius
    wid.border_width = widget_border_width
    wid.border_color = map_styles_to_hex_colours(widget_box_style)
    renderer_options_wid.margin = '0.2cm'

    # Display final widget
    ipydisplay.display(wid)

    # Trigger initial visualization
    render_function({})


def visualize_patch_atm(atm, n_shape_parameters=5, mode='multiple',
                        parameters_bounds=(-3.0, 3.0), figure_size=(10, 8),
                        style='coloured'):
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
    style : ``{'coloured', 'minimal'}``, optional
        If ``'coloured'``, then the style of the widget will be coloured. If
        ``minimal``, then the style is simple using black and white colours.
    """
    # Ensure that the code is being run inside a Jupyter kernel!
    from menpowidgets.utils import verify_ipython_and_kernel
    verify_ipython_and_kernel()
    print('Initializing...')

    # Get the number of levels
    n_levels = atm.n_scales

    # Define the styling options
    if style == 'coloured':
        model_style = 'info'
        model_parameters_style = 'danger'
        patches_style = 'minimal'
        patches_subwidgets_style = 'danger'
        channels_style = 'danger'
        logo_style = 'info'
        widget_box_style = 'info'
        widget_border_radius = 10
        widget_border_width = 1
        info_style = 'danger'
        renderer_style = 'danger'
        renderer_tabs_style = 'info'
        save_figure_style = 'danger'
    elif style == 'minimal':
        model_style = ''
        model_parameters_style = 'minimal'
        patches_style = 'minimal'
        patches_subwidgets_style = 'minimal'
        channels_style = 'minimal'
        logo_style = 'minimal'
        widget_box_style = ''
        widget_border_radius = 0
        widget_border_width = 0
        info_style = 'minimal'
        renderer_style = 'minimal'
        renderer_tabs_style = 'minimal'
        save_figure_style = 'minimal'
    else:
        raise ValueError("style must be either coloured or minimal")

    # Get the maximum number of components per level
    max_n_shape = [sp.n_active_components for sp in atm.shape_models]

    # Check the given number of parameters (the returned n_parameters is a list
    # of len n_scales)
    n_shape_parameters = check_n_parameters(n_shape_parameters, n_levels,
                                            max_n_shape)

    # Define render function
    def render_function(change):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Compute weights and instance
        shape_weights = shape_model_parameters_wid.selected_values
        shape_instance, template = atm.instance(scale_index=level,
                                                shape_weights=shape_weights)

        # Render instance with selected options
        options = renderer_options_wid.selected_values['lines']
        options.update(renderer_options_wid.selected_values['markers'])
        options.update(renderer_options_wid.selected_values['numbering'])
        options.update(renderer_options_wid.selected_values['axes'])
        options.update(renderer_options_wid.selected_values['image'])
        options.update(patch_options_wid.selected_values)
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * figure_size[0],
            renderer_options_wid.selected_values['zoom_one'] * figure_size[1])

        # show image with selected options
        renderer = render_patches(
            patches=template.pixels, patch_centers=shape_instance,
            renderer=save_figure_wid.renderer, figure_size=new_figure_size,
            channels=channel_options_wid.selected_values['channels'],
            glyph_enabled=channel_options_wid.selected_values['glyph_enabled'],
            glyph_block_size=channel_options_wid.selected_values['glyph_block_size'],
            glyph_use_negative=channel_options_wid.selected_values['glyph_use_negative'],
            sum_enabled=channel_options_wid.selected_values['sum_enabled'],
            **options)

        # Update info
        update_info(atm, template, level)

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Define function that updates the info text
    def update_info(atm, instance, level):
        lvl_shape_mod = atm.shape_models[level].model
        n_channels = instance.pixels.shape[2]
        feat = atm.holistic_features[level]

        # Feature string
        tmp_feat = 'Feature is {} with {} channel{}'.format(
            name_of_callable(feat), n_channels, 's' * (n_channels > 1))
        n_feat = (instance.pixels.shape[0] * instance.pixels.shape[2] *
                  instance.pixels.shape[3] * instance.pixels.shape[4])

        # update info widgets
        text_per_line = [
            "> Warp using {} transform".format(atm.transform.__name__),
            "> Level {}/{}".format(
                level + 1, atm.n_scales),
            "> {} landmark points".format(instance.pixels.shape[0]),
            "> {} shape components ({:.2f}% of variance)".format(
                lvl_shape_mod.n_components,
                lvl_shape_mod.variance_ratio() * 100),
            "> {}".format(tmp_feat),
            "> Reference frame of length {} ({} patches of shape {} x {} "
            "and {} channel{}.)".format(
                n_feat, instance.pixels.shape[0], instance.pixels.shape[3],
                instance.pixels.shape[4], instance.pixels.shape[2],
                's' * (instance.pixels.shape[2] > 1)),
            "> Instance: min={:.3f} , max={:.3f}".format(
                instance.pixels.min(), instance.pixels.max())]
        info_wid.set_widget_state(text_per_line=text_per_line)

    # Plot shape variance function
    def plot_shape_variance(name):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # Get selected level
        level = 0
        if n_levels > 1:
            level = level_wid.value

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * 10,
            renderer_options_wid.selected_values['zoom_one'] * 3)
        plt.subplot(121)
        atm.shape_models[level].model.plot_eigenvalues_ratio(
            figure_id=save_figure_wid.renderer.figure_id)
        plt.subplot(122)
        renderer = atm.shape_models[level].model.plot_eigenvalues_cumulative_ratio(
            figure_id=save_figure_wid.renderer.figure_id,
            figure_size=new_figure_size)
        plt.show()

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Create widgets
    shape_model_parameters_wid = LinearModelParametersWidget(
            n_shape_parameters[0], render_function, params_str='Parameter ',
            mode=mode, params_bounds=parameters_bounds, params_step=0.1,
            plot_variance_visible=True,
            plot_variance_function=plot_shape_variance,
            style=model_parameters_style, animation_step=0.5, interval=0.,
            loop_enabled=True)
    patch_options_wid = PatchOptionsWidget(
            n_patches=atm.warped_templates[0].pixels.shape[0],
            n_offsets=atm.warped_templates[0].pixels.shape[1],
            render_function=render_function, style=patches_style,
            subwidgets_style=patches_subwidgets_style)
    channel_options_wid = ChannelOptionsWidget(
            n_channels=atm.warped_templates[0].pixels.shape[2],
            image_is_masked=False, render_function=render_function,
            style=channels_style)
    renderer_options_wid = RendererOptionsWidget(
            options_tabs=['image', 'markers', 'lines', 'numbering', 'zoom_one',
                          'axes'], labels=None,
            axes_x_limits=None, axes_y_limits=None,
            render_function=None,  style=renderer_style,
            tabs_style=renderer_tabs_style)
    renderer_options_wid.options_widgets[0].interpolation_checkbox.value = True
    renderer_options_wid.add_render_function(render_function)
    info_wid = TextPrintWidget(text_per_line=[''] * 7, style=info_style)
    save_figure_wid = SaveFigureOptionsWidget(renderer=None,
                                              style=save_figure_style)

    # Define function that updates options' widgets state
    def update_widgets(change):
        value = change['new']
        # Update shape model parameters
        shape_model_parameters_wid.set_widget_state(
            n_shape_parameters[value], params_str='Parameter ',
            allow_callback=False)

        # Update patch options
        patch_options_wid.set_widget_state(
            n_patches=atm.warped_templates[value].pixels.shape[0],
            n_offsets=atm.warped_templates[value].pixels.shape[1],
            allow_callback=False)

        # Update channels options
        channel_options_wid.set_widget_state(
            n_channels=atm.warped_templates[value].pixels.shape[2],
            image_is_masked=False, allow_callback=True)

    # Group widgets
    tmp_children = [shape_model_parameters_wid]
    if n_levels > 1:
        radio_str = OrderedDict()
        for l in range(n_levels):
            if l == 0:
                radio_str["Level {} (low)".format(l)] = l
            elif l == n_levels - 1:
                radio_str["Level {} (high)".format(l)] = l
            else:
                radio_str["Level {}".format(l)] = l
        level_wid = ipywidgets.RadioButtons(
            options=radio_str, description='Pyramid:', value=n_levels-1)
        level_wid.observe(update_widgets, names='value', type='change')
        level_wid.observe(render_function, names='value', type='change')
        tmp_children.insert(0, level_wid)
    tmp_wid = ipywidgets.HBox(children=tmp_children, align='center',
                              box_style=model_style)
    options_box = ipywidgets.Tab(children=[tmp_wid, patch_options_wid,
                                           channel_options_wid,
                                           renderer_options_wid,
                                           info_wid, save_figure_wid])
    tab_titles = ['Model', 'Patches', 'Channels', 'Renderer', 'Info', 'Export']
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    logo_wid = LogoWidget(style=logo_style)
    logo_wid.margin = '0.1cm'
    wid = ipywidgets.HBox(children=[logo_wid, options_box], align='start')

    # Set widget's style
    wid.box_style = widget_box_style
    wid.border_radius = widget_border_radius
    wid.border_width = widget_border_width
    wid.border_color = map_styles_to_hex_colours(widget_box_style)
    renderer_options_wid.margin = '0.2cm'

    # Display final widget
    ipydisplay.display(wid)

    # Trigger initial visualization
    render_function({})


def visualize_clm(clm, n_shape_parameters=5, mode='multiple',
                  parameters_bounds=(-3.0, 3.0), figure_size=(10, 8),
                  style='coloured'):
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
    style : ``{'coloured', 'minimal'}``, optional
        If ``'coloured'``, then the style of the widget will be coloured. If
        ``minimal``, then the style is simple using black and white colours.
    """
    # Ensure that the code is being run inside a Jupyter kernel!
    from menpowidgets.utils import verify_ipython_and_kernel
    verify_ipython_and_kernel()
    print('Initializing...')

    # Get the number of levels
    n_levels = clm.n_scales

    # Define the styling options
    if style == 'coloured':
        model_style = 'info'
        model_parameters_style = 'danger'
        patches_style = 'minimal'
        patches_subwidgets_style = 'danger'
        channels_style = 'danger'
        logo_style = 'info'
        widget_box_style = 'info'
        widget_border_radius = 10
        widget_border_width = 1
        info_style = 'danger'
        renderer_style = 'danger'
        renderer_tabs_style = 'info'
        save_figure_style = 'danger'
    elif style == 'minimal':
        model_style = ''
        model_parameters_style = 'minimal'
        patches_style = 'minimal'
        patches_subwidgets_style = 'minimal'
        channels_style = 'minimal'
        logo_style = 'minimal'
        widget_box_style = ''
        widget_border_radius = 0
        widget_border_width = 0
        info_style = 'minimal'
        renderer_style = 'minimal'
        renderer_tabs_style = 'minimal'
        save_figure_style = 'minimal'
    else:
        raise ValueError("style must be either coloured or minimal")

    # Get the maximum number of components per level
    max_n_shape = [sp.n_active_components for sp in clm.shape_models]

    # Check the given number of parameters (the returned n_parameters is a list
    # of len n_scales)
    n_shape_parameters = check_n_parameters(n_shape_parameters, n_levels,
                                            max_n_shape)

    # Define render function
    def render_function(change):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Compute weights and instance
        shape_weights = shape_model_parameters_wid.selected_values
        shape_instance = clm.shape_instance(scale_index=level,
                                            shape_weights=shape_weights)
        if domain_toggles.value == 'spatial':
            patches = _convert_patches_list_to_single_array(
                    clm.expert_ensembles[level].spatial_filter_images,
                    clm.expert_ensembles[level].n_experts)
        else:
            patches = _convert_patches_list_to_single_array(
                    clm.expert_ensembles[level].frequency_filter_images,
                    clm.expert_ensembles[level].n_experts)

        # Render instance with selected options
        options = renderer_options_wid.selected_values['lines']
        options.update(renderer_options_wid.selected_values['markers'])
        options.update(renderer_options_wid.selected_values['numbering'])
        options.update(renderer_options_wid.selected_values['axes'])
        options.update(renderer_options_wid.selected_values['image'])
        options.update(patch_options_wid.selected_values)
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * figure_size[0],
            renderer_options_wid.selected_values['zoom_one'] * figure_size[1])

        # show image with selected options
        renderer = render_patches(
                patches=patches, patch_centers=shape_instance,
                renderer=save_figure_wid.renderer, figure_size=new_figure_size,
                channels=channel_options_wid.selected_values['channels'],
                glyph_enabled=channel_options_wid.selected_values['glyph_enabled'],
                glyph_block_size=channel_options_wid.selected_values['glyph_block_size'],
                glyph_use_negative=channel_options_wid.selected_values['glyph_use_negative'],
                sum_enabled=channel_options_wid.selected_values['sum_enabled'],
                **options)

        # Update info
        update_info(clm, patches, level)

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Define function that updates the info text
    def update_info(clm, patches, level):
        lvl_shape_mod = clm.shape_models[level].model
        n_channels = patches.shape[2]
        feat = clm.holistic_features[level]

        # Feature string
        tmp_feat = 'Feature is {} with {} channel{}'.format(
                name_of_callable(feat), n_channels, 's' * (n_channels > 1))

        # update info widgets
        text_per_line = [
            "> {} ensemble of experts".format(
                    name_of_callable(clm.expert_ensemble_cls[level])),
            "> Level {}/{}".format(level + 1, clm.n_scales),
            "> {} experts (landmark points)".format(
                    clm.expert_ensembles[level].n_experts),
            "> {} shape components ({:.2f}% of variance)".format(
                    lvl_shape_mod.n_components,
                    lvl_shape_mod.variance_ratio() * 100),
            "> {}".format(tmp_feat),
            "> Patch shape: {} x {}".format(
                    clm.expert_ensembles[level].search_shape[0],
                    clm.expert_ensembles[level].search_shape[1]),
            "> Instance: min={:.3f} , max={:.3f}".format(
                    patches.min(), patches.max())]
        info_wid.set_widget_state(text_per_line=text_per_line)

    # Plot shape variance function
    def plot_shape_variance(name):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # Get selected level
        level = 0
        if n_levels > 1:
            level = level_wid.value

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * 10,
            renderer_options_wid.selected_values['zoom_one'] * 3)
        plt.subplot(121)
        clm.shape_models[level].model.plot_eigenvalues_ratio(
                figure_id=save_figure_wid.renderer.figure_id)
        plt.subplot(122)
        renderer = clm.shape_models[level].model.plot_eigenvalues_cumulative_ratio(
                figure_id=save_figure_wid.renderer.figure_id,
                figure_size=new_figure_size)
        plt.show()

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Create widgets
    shape_model_parameters_wid = LinearModelParametersWidget(
            n_shape_parameters[0], render_function, params_str='Parameter ',
            mode=mode, params_bounds=parameters_bounds, params_step=0.1,
            plot_variance_visible=True,
            plot_variance_function=plot_shape_variance,
            style=model_parameters_style, animation_step=0.5, interval=0.,
            loop_enabled=True)
    patch_options_wid = PatchOptionsWidget(
            n_patches=clm.expert_ensembles[0].n_experts, n_offsets=1,
            render_function=None, style=patches_style,
            subwidgets_style=patches_subwidgets_style)
    domain_toggles = ipywidgets.ToggleButtons(
            description='Domain:', options=['spatial', 'frequency'],
            value='spatial', margin='0.3cm')
    experts_box = ipywidgets.VBox(children=[domain_toggles, patch_options_wid],
                                  align='start')
    channel_options_wid = ChannelOptionsWidget(
            n_channels=clm.expert_ensembles[0].spatial_filter_images[0].n_channels,
            image_is_masked=False, render_function=render_function,
            style=channels_style)
    renderer_options_wid = RendererOptionsWidget(
            options_tabs=['image', 'markers', 'lines', 'numbering', 'zoom_one',
                          'axes'], labels=None,
            axes_x_limits=None, axes_y_limits=None, render_function=None,
            style=renderer_style, tabs_style=renderer_tabs_style)
    info_wid = TextPrintWidget(text_per_line=[''] * 7, style=info_style)
    save_figure_wid = SaveFigureOptionsWidget(renderer=None,
                                              style=save_figure_style)

    # Set default values
    patch_options_wid.bboxes_line_options_wid.line_colour_widget.set_colours(
            ['white'], allow_callback=False)
    renderer_options_wid.options_widgets[0].cmap_select.value = 'afmhot'
    renderer_options_wid.options_widgets[0].interpolation_checkbox.value = True

    # Add render function
    domain_toggles.observe(render_function, names='value', type='change')
    patch_options_wid.add_render_function(render_function)
    renderer_options_wid.add_render_function(render_function)

    # Define function that updates options' widgets state
    def update_widgets(change):
        value = change['new']
        # Update shape model parameters
        shape_model_parameters_wid.set_widget_state(
                n_shape_parameters[value], params_str='Parameter ',
                allow_callback=False)

        # Update patch options
        patch_options_wid.set_widget_state(
                n_patches=clm.expert_ensembles[value].n_experts, n_offsets=1,
                allow_callback=False)

        # Update channels options
        channel_options_wid.set_widget_state(
                n_channels=clm.expert_ensembles[value].spatial_filter_images[0].n_channels,
                image_is_masked=False, allow_callback=True)

    # Group widgets
    tmp_children = [shape_model_parameters_wid]
    if n_levels > 1:
        radio_str = OrderedDict()
        for l in range(n_levels):
            if l == 0:
                radio_str["Level {} (low)".format(l)] = l
            elif l == n_levels - 1:
                radio_str["Level {} (high)".format(l)] = l
            else:
                radio_str["Level {}".format(l)] = l
        level_wid = ipywidgets.RadioButtons(
                options=radio_str, description='Pyramid:', value=n_levels-1)
        level_wid.observe(update_widgets, names='value', type='change')
        level_wid.observe(render_function, names='value', type='change')
        tmp_children.insert(0, level_wid)
    tmp_wid = ipywidgets.HBox(children=tmp_children, align='center',
                              box_style=model_style)
    options_box = ipywidgets.Tab(children=[tmp_wid, experts_box,
                                           channel_options_wid,
                                           renderer_options_wid,
                                           info_wid, save_figure_wid])
    tab_titles = ['Model', 'Experts', 'Channels', 'Renderer', 'Info', 'Export']
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    logo_wid = LogoWidget(style=logo_style)
    logo_wid.margin = '0.1cm'
    wid = ipywidgets.HBox(children=[logo_wid, options_box], align='start')

    # Set widget's style
    wid.box_style = widget_box_style
    wid.border_radius = widget_border_radius
    wid.border_width = widget_border_width
    wid.border_color = map_styles_to_hex_colours(widget_box_style)
    renderer_options_wid.margin = '0.2cm'

    # Display final widget
    ipydisplay.display(wid)

    # Trigger initial visualization
    render_function({})


def visualize_expert_ensemble(expert_ensemble, centers, figure_size=(10, 8),
                              style='coloured'):
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
    style : ``{'coloured', 'minimal'}``, optional
        If ``'coloured'``, then the style of the widget will be coloured. If
        ``minimal``, then the style is simple using black and white colours.
    """
    # Ensure that the code is being run inside a Jupyter kernel!
    from menpowidgets.utils import verify_ipython_and_kernel
    verify_ipython_and_kernel()
    print('Initializing...')

    # Make sure that expert_ensemble is a list even with one member
    if not isinstance(expert_ensemble, list):
        expert_ensemble = [expert_ensemble]

    # Get the number of levels (i.e. number of expert ensembles)
    n_levels = len(expert_ensemble)

    # Make sure that centers is a list even with one pointcloud
    if not isinstance(centers, list):
        centers = [centers] * n_levels
    elif isinstance(centers, list) and len(centers) == 1:
        centers *= n_levels

    # Define the styling options
    if style == 'coloured':
        model_style = 'info'
        patches_style = 'minimal'
        patches_subwidgets_style = 'danger'
        channels_style = 'danger'
        logo_style = 'info'
        widget_box_style = 'info'
        widget_border_radius = 10
        widget_border_width = 1
        info_style = 'danger'
        renderer_style = 'danger'
        renderer_tabs_style = 'info'
        save_figure_style = 'danger'
    elif style == 'minimal':
        model_style = ''
        patches_style = 'minimal'
        patches_subwidgets_style = 'minimal'
        channels_style = 'minimal'
        logo_style = 'minimal'
        widget_box_style = ''
        widget_border_radius = 0
        widget_border_width = 0
        info_style = 'minimal'
        renderer_style = 'minimal'
        renderer_tabs_style = 'minimal'
        save_figure_style = 'minimal'
    else:
        raise ValueError("style must be either coloured or minimal")

    # Define render function
    def render_function(change):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        if domain_toggles.value == 'spatial':
            patches = _convert_patches_list_to_single_array(
                    expert_ensemble[level].spatial_filter_images,
                    expert_ensemble[level].n_experts)
        else:
            patches = _convert_patches_list_to_single_array(
                    expert_ensemble[level].frequency_filter_images,
                    expert_ensemble[level].n_experts)

        # Render instance with selected options
        options = renderer_options_wid.selected_values['lines']
        options.update(renderer_options_wid.selected_values['markers'])
        options.update(renderer_options_wid.selected_values['numbering'])
        options.update(renderer_options_wid.selected_values['axes'])
        options.update(renderer_options_wid.selected_values['image'])
        options.update(patch_options_wid.selected_values)
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * figure_size[0],
            renderer_options_wid.selected_values['zoom_one'] * figure_size[1])

        # show image with selected options
        renderer = render_patches(
                patches=patches, patch_centers=centers[level],
                renderer=save_figure_wid.renderer, figure_size=new_figure_size,
                channels=channel_options_wid.selected_values['channels'],
                glyph_enabled=channel_options_wid.selected_values['glyph_enabled'],
                glyph_block_size=channel_options_wid.selected_values['glyph_block_size'],
                glyph_use_negative=channel_options_wid.selected_values['glyph_use_negative'],
                sum_enabled=channel_options_wid.selected_values['sum_enabled'],
                **options)

        # Update info
        update_info(expert_ensemble, patches, level)

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Define function that updates the info text
    def update_info(expert_ensemble, patches, level):
        # update info widgets
        text_per_line = [
            "> {} ensemble of experts".format(
                    name_of_callable(expert_ensemble[level])),
            "> Level {}/{}".format(level + 1, n_levels),
            "> {} experts.".format(expert_ensemble[level].n_experts),
            "> Channels: {}".format(patches.shape[2]),
            "> Patch shape: {} x {}".format(
                    expert_ensemble[level].search_shape[0],
                    expert_ensemble[level].search_shape[1]),
            "> Instance: min={:.3f} , max={:.3f}".format(
                    patches.min(), patches.max())]
        info_wid.set_widget_state(text_per_line=text_per_line)

    # Create widgets
    patch_options_wid = PatchOptionsWidget(
            n_patches=expert_ensemble[0].n_experts, n_offsets=1,
            render_function=None, style=patches_style,
            subwidgets_style=patches_subwidgets_style)
    domain_toggles = ipywidgets.ToggleButtons(
            description='Domain:', options=['spatial', 'frequency'],
            value='spatial', margin='0.1cm')
    channel_options_wid = ChannelOptionsWidget(
            n_channels=expert_ensemble[0].spatial_filter_images[0].n_channels,
            image_is_masked=False, render_function=render_function,
            style=channels_style)
    renderer_options_wid = RendererOptionsWidget(
            options_tabs=['image', 'markers', 'lines', 'numbering', 'zoom_one',
                          'axes'], labels=None,
            axes_x_limits=None, axes_y_limits=None, render_function=None,
            style=renderer_style, tabs_style=renderer_tabs_style)
    info_wid = TextPrintWidget(text_per_line=[''] * 7, style=info_style)
    save_figure_wid = SaveFigureOptionsWidget(renderer=None,
                                              style=save_figure_style)

    # Set default values
    patch_options_wid.bboxes_line_options_wid.line_colour_widget.set_colours(
            ['white'], allow_callback=False)
    renderer_options_wid.options_widgets[0].cmap_select.value = 'afmhot'
    renderer_options_wid.options_widgets[0].interpolation_checkbox.value = True

    # Add render function
    domain_toggles.observe(render_function, names='value', type='change')
    patch_options_wid.add_render_function(render_function)
    renderer_options_wid.add_render_function(render_function)

    # Define function that updates options' widgets state
    def update_widgets(change):
        value = change['new']
        # Update patch options
        patch_options_wid.set_widget_state(
                n_patches=expert_ensemble[value].n_experts, n_offsets=1,
                allow_callback=False)

        # Update channels options
        channel_options_wid.set_widget_state(
                n_channels=expert_ensemble[value].spatial_filter_images[0].n_channels,
                image_is_masked=False, allow_callback=True)

    # Group widgets
    tmp_children = [domain_toggles]
    if n_levels > 1:
        radio_str = OrderedDict()
        for l in range(n_levels):
            if l == 0:
                radio_str["Level {} (low)".format(l)] = l
            elif l == n_levels - 1:
                radio_str["Level {} (high)".format(l)] = l
            else:
                radio_str["Level {}".format(l)] = l
        level_wid = ipywidgets.RadioButtons(
                options=radio_str, description='Pyramid:', value=n_levels-1,
                margin='0.1cm')
        level_wid.observe(update_widgets, names='value', type='change')
        level_wid.observe(render_function, names='value', type='change')
        tmp_children.insert(0, level_wid)
    tmp_wid = ipywidgets.HBox(children=tmp_children, align='start',
                              box_style=model_style)
    experts_box = ipywidgets.VBox(children=[tmp_wid, patch_options_wid],
                                  align='start')
    options_box = ipywidgets.Tab(children=[experts_box, channel_options_wid,
                                           renderer_options_wid, info_wid,
                                           save_figure_wid])
    tab_titles = ['Experts', 'Channels', 'Renderer', 'Info', 'Export']
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    logo_wid = LogoWidget(style=logo_style)
    logo_wid.margin = '0.1cm'
    wid = ipywidgets.HBox(children=[logo_wid, options_box], align='start')

    # Set widget's style
    wid.box_style = widget_box_style
    wid.border_radius = widget_border_radius
    wid.border_width = widget_border_width
    wid.border_color = map_styles_to_hex_colours(widget_box_style)
    renderer_options_wid.margin = '0.2cm'

    # Display final widget
    ipydisplay.display(wid)

    # Trigger initial visualization
    render_function({})


def plot_ced(errors, legend_entries=None, error_range=None,
             error_type='me_norm', figure_size=(10, 6), style='coloured',
             return_widget=False):
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
    style : ``{'coloured', 'minimal'}``, optional
        If ``'coloured'``, then the style of the widget will be coloured. If
        ``minimal``, then the style is simple using black and white colours.
    return_widget : `bool`, optional
        If ``True``, the widget object will be returned so that it can be used
        as part of a parent widget. If ``False``, the widget object is not
        returned, it is just visualized.
    """
    # Ensure that the code is being run inside a Jupyter kernel!
    from menpowidgets.utils import verify_ipython_and_kernel
    verify_ipython_and_kernel()
    from menpofit.visualize import plot_cumulative_error_distribution
    print('Initializing...')

    # Make sure that errors is a list even with one list member
    if not isinstance(errors[0], list):
        errors = [errors]

    # Get number of curves to be plotted
    n_curves = len(errors)

    # Define the styling options
    if style == 'coloured':
        logo_style = 'danger'
        widget_box_style = 'danger'
        tabs_style = 'warning'
        save_figure_style = 'warning'
    else:
        logo_style = 'minimal'
        widget_box_style = 'minimal'
        tabs_style = 'minimal'
        save_figure_style = 'minimal'

    # Parse options
    if legend_entries is None:
        legend_entries = ["Curve {}".format(i) for i in range(n_curves)]

    # Get horizontal axis errors
    if error_range is None:
        if error_type == 'me_norm':
            x_axis_limit = 0.05
            x_axis_step = 0.005
            x_label = 'Normalized Point-to-Point Error'
        elif error_type == 'me' or error_type == 'rmse':
            x_axis_limit = 5.
            x_axis_step = 0.5
            x_label = 'Point-to-Point Error'
        else:
            raise ValueError('error_type must be me_norm or me or rmse')
    else:
        x_axis_limit = (error_range[1] + error_range[0]) / 2
        x_axis_step = error_range[2]
        x_label = 'Error'

    # Define render function
    def render_function(change):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # plot with selected options
        opts = wid.selected_values.copy()
        new_figure_size = (
            wid.selected_values['zoom'][0] * figure_size[0],
            wid.selected_values['zoom'][1] * figure_size[1])
        del opts['zoom']
        if opts['axes_x_limits'] is None:
            tmp_error_range = None
        elif isinstance(opts['axes_x_limits'], float):
            tmp_error_range = [0., np.max(errors), x_axis_step]
        else:
            tmp_error_range = [opts['axes_x_limits'][0],
                               1.0001 * opts['axes_x_limits'][1],
                               x_axis_step]
        renderer = plot_cumulative_error_distribution(
            errors, error_range=tmp_error_range,
            figure_id=save_figure_wid.renderer.figure_id, new_figure=False,
            figure_size=new_figure_size, **opts)

        # show plot
        plt.show()

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Create widgets
    wid = PlotOptionsWidget(legend_entries=legend_entries,
                            render_function=render_function,
                            style=widget_box_style, tabs_style=tabs_style)
    save_figure_wid = SaveFigureOptionsWidget(renderer=None,
                                              style=save_figure_style)

    # Set values in plot widget
    wid.remove_render_function()
    wid.axes_wid.axes_limits_widget.axes_x_limits_toggles.value = 'range'
    wid.axes_wid.axes_limits_widget.axes_x_limits_range.set_widget_state(
        [0., x_axis_limit], allow_callback=False)
    wid.axes_wid.axes_limits_widget.axes_y_limits_toggles.value = 'range'
    wid.axes_wid.axes_limits_widget.axes_y_limits_range.set_widget_state(
        [0., 1.], allow_callback=False)
    wid.axes_wid.axes_ticks_widget.axes_x_ticks_toggles.value = 'auto'

    wid.axes_wid.axes_ticks_widget.axes_y_ticks_toggles.value = 'list'
    wid.axes_wid.axes_ticks_widget.axes_y_ticks_list.set_widget_state(
        list(np.arange(0., 1.1, 0.1)), allow_callback=False)
    wid.x_label.value = x_label
    wid.y_label.value = 'Images Proportion'
    wid.title.value = 'Cumulative error distribution'
    wid.add_render_function(render_function)

    # Group widgets
    logo = LogoWidget(style=logo_style)
    logo.margin = '0.1cm'
    tmp_children = list(wid.options_tab.children)
    tmp_children.append(save_figure_wid)
    wid.options_tab.children = tmp_children
    wid.options_tab.set_title(0, 'Figure')
    wid.options_tab.set_title(1, 'Renderer')
    wid.options_tab.set_title(2, 'Legend')
    wid.options_tab.set_title(3, 'Axes')
    wid.options_tab.set_title(4, 'Zoom')
    wid.options_tab.set_title(5, 'Grid')
    wid.options_tab.set_title(6, 'Export')
    wid.children = [logo, wid.options_tab]
    wid.align = 'start'

    # Display final widget
    ipydisplay.display(wid)

    # Trigger initial visualization
    render_function({})

    # return widget object if asked
    if return_widget:
        return wid


def visualize_fitting_result(fitting_results, figure_size=(10, 8),
                             style='coloured', browser_style='buttons'):
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
    style : ``{'coloured', 'minimal'}``, optional
        If ``'coloured'``, then the style of the widget will be coloured. If
        ``minimal``, then the style is simple using black and white colours.
    browser_style : ``{'buttons', 'slider'}``, optional
        It defines whether the selector of the objects will have the form of
        plus/minus buttons or a slider.
    """
    # Ensure that the code is being run inside a Jupyter kernel!
    from menpowidgets.utils import verify_ipython_and_kernel
    verify_ipython_and_kernel()
    print('Initializing...')

    # Make sure that fitting_results is a list even with one fitting_result
    if not isinstance(fitting_results, list):
        fitting_results = [fitting_results]

    # Get the number of fitting_results
    n_fitting_results = len(fitting_results)

    # Define the styling options
    if style == 'coloured':
        logo_style = 'info'
        widget_box_style = 'info'
        widget_border_radius = 10
        widget_border_width = 1
        animation_style = 'info'
        fitting_result_style = 'danger'
        fitting_result_tabs_style = 'warning'
        info_style = 'danger'
        renderer_style = 'danger'
        renderer_tabs_style = 'warning'
        save_figure_style = 'danger'
    else:
        logo_style = 'minimal'
        widget_box_style = ''
        widget_border_radius = 0
        widget_border_width = 0
        fitting_result_style = 'minimal'
        fitting_result_tabs_style = 'minimal'
        animation_style = 'minimal'
        info_style = 'minimal'
        renderer_style = 'minimal'
        renderer_tabs_style = 'minimal'
        save_figure_style = 'minimal'

    # Define function that plots errors curve
    def plot_errors_function(name):
        # Clear current figure, but wait until the new data to be displayed are
        # generated
        ipydisplay.clear_output(wait=True)

        # Get selected index
        im = image_number_wid.selected_values if n_fitting_results > 1 else 0

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * 10,
            renderer_options_wid.selected_values['zoom_one'] * 3)
        renderer = fitting_results[im].plot_errors(
            figure_id=save_figure_wid.renderer.figure_id,
            figure_size=new_figure_size)

        # Show figure
        plt.show()

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Define function that plots displacements curve
    def plot_displacements_function(name):
        # Clear current figure, but wait until the new data to be displayed are
        # generated
        ipydisplay.clear_output(wait=True)

        # Get selected index
        im = image_number_wid.selected_values if n_fitting_results > 1 else 0

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * 10,
            renderer_options_wid.selected_values['zoom_one'] * 3)
        renderer = fitting_results[im].plot_displacements(
            figure_id=save_figure_wid.renderer.figure_id,
            figure_size=new_figure_size, stat_type='mean')

        # Show figure
        plt.show()

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Define function that plots errors curve
    def plot_costs_function(name):
        # Clear current figure, but wait until the new data to be displayed are
        # generated
        ipydisplay.clear_output(wait=True)

        # Get selected index
        im = image_number_wid.selected_values if n_fitting_results > 1 else 0

        # Render
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * 10,
            renderer_options_wid.selected_values['zoom_one'] * 3)
        renderer = fitting_results[im].plot_costs(
                figure_id=save_figure_wid.renderer.figure_id,
                figure_size=new_figure_size)

        # Show figure
        plt.show()

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Define render function
    def render_function(change):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # get selected object
        im = image_number_wid.selected_values if n_fitting_results > 1 else 0

        # get selected options
        tmp1 = renderer_options_wid.selected_values['markers']
        tmp2 = renderer_options_wid.selected_values['lines']
        options = fitting_result_wid.selected_values
        options.update(renderer_options_wid.selected_values['axes'])
        options.update(renderer_options_wid.selected_values['legend'])
        options.update(renderer_options_wid.selected_values['numbering'])
        options.update(renderer_options_wid.selected_values['image'])
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * figure_size[0],
            renderer_options_wid.selected_values['zoom_one'] * figure_size[1])

        # get selected view function
        if (fitting_result_wid.result_iterations_tab.selected_index == 0 or
                not fitting_results[im].is_iterative):
            # use view()
            # final shape colour
            final_marker_face_colour = tmp1['marker_face_colour'][0]
            final_marker_edge_colour = tmp1['marker_edge_colour'][0]
            final_line_colour = tmp2['line_colour'][0]
            # initial shape colour
            initial_marker_face_colour = 'b'
            initial_marker_edge_colour = 'b'
            initial_line_colour = 'b'
            if fitting_results[im].initial_shape is not None:
                initial_marker_face_colour = tmp1['marker_face_colour'][1]
                initial_marker_edge_colour = tmp1['marker_edge_colour'][1]
                initial_line_colour = tmp2['line_colour'][1]
            # gt shape colour
            gt_marker_face_colour = 'y'
            gt_marker_edge_colour = 'y'
            gt_line_colour = 'y'
            if fitting_results[im].gt_shape is not None:
                if fitting_results[im].initial_shape is not None:
                    gt_marker_face_colour = tmp1['marker_face_colour'][2]
                    gt_marker_edge_colour = tmp1['marker_edge_colour'][2]
                    gt_line_colour = tmp2['line_colour'][2]
                else:
                    gt_marker_face_colour = tmp1['marker_face_colour'][1]
                    gt_marker_edge_colour = tmp1['marker_edge_colour'][1]
                    gt_line_colour = tmp2['line_colour'][1]
            # render
            renderer = fitting_results[im].view(
                    figure_id=save_figure_wid.renderer.figure_id,
                    new_figure=False, render_markers=tmp1['render_markers'],
                    final_marker_face_colour=final_marker_face_colour,
                    final_marker_edge_colour=final_marker_edge_colour,
                    final_line_colour=final_line_colour,
                    initial_marker_face_colour=initial_marker_face_colour,
                    initial_marker_edge_colour=initial_marker_edge_colour,
                    initial_line_colour=initial_line_colour,
                    gt_marker_face_colour=gt_marker_face_colour,
                    gt_marker_edge_colour=gt_marker_edge_colour,
                    gt_line_colour=gt_line_colour,
                    marker_style=tmp1['marker_style'],
                    marker_size=tmp1['marker_size'],
                    marker_edge_width=tmp1['marker_edge_width'],
                    render_lines=tmp2['render_lines'],
                    line_style=tmp2['line_style'],
                    line_width=tmp2['line_width'],
                    figure_size=new_figure_size, **options)
        else:
            # use view_iterations()
            if fitting_result_wid.iterations_mode.value == 'animation':
                # The mode is 'Animation'
                # get colours
                marker_face_colour = tmp1['marker_face_colour'][0]
                marker_edge_colour = tmp1['marker_edge_colour'][0]
                line_colour = tmp2['line_colour'][0]
            else:
                # The mode is 'Static'
                # get colours
                marker_face_colour = [
                    tmp1['marker_face_colour'][i]
                    for i in fitting_result_wid.selected_values['iters']]
                marker_edge_colour = [
                    tmp1['marker_edge_colour'][i]
                    for i in fitting_result_wid.selected_values['iters']]
                line_colour = [
                    tmp2['line_colour'][i]
                    for i in fitting_result_wid.selected_values['iters']]

            # render
            renderer = fitting_results[im].view_iterations(
                    figure_id=save_figure_wid.renderer.figure_id,
                    new_figure=False, render_markers=tmp1['render_markers'],
                    marker_face_colour=marker_face_colour,
                    marker_style=tmp1['marker_style'],
                    marker_size=tmp1['marker_size'],
                    marker_edge_colour=marker_edge_colour,
                    marker_edge_width=tmp1['marker_edge_width'],
                    render_lines=tmp2['render_lines'],
                    line_style=tmp2['line_style'], line_width=tmp2['line_width'],
                    line_colour=line_colour, figure_size=new_figure_size,
                    **options)

        # Show figure
        plt.show()

        # update info text widget
        update_info({})

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Define function that updates info text
    def update_info(change):
        # Get selected object
        im = image_number_wid.selected_values if n_fitting_results > 1 else 0
        fr = fitting_results[im]

        # Errors
        text_per_line = []
        if fr.gt_shape is not None:
            # Get error function
            error_fun = euclidean_bb_normalised_error
            if error_type_toggles.value == 'RMS':
                error_fun = root_mean_square_bb_normalised_error
            # Set error options visibility
            error_box.visible = True
            # Compute errors
            if fr.initial_shape is not None:
                text_per_line.append(' > Initial error: {:.4f}'.format(
                        error_fun(fr.initial_shape, fr.gt_shape,
                                  norm_type=norm_type_toggles.value)))
            text_per_line.append(' > Final error: {:.4f}'.format(
                    error_fun(fr.final_shape, fr.gt_shape,
                              norm_type=norm_type_toggles.value)))
        else:
            # Set error options visibility
            error_box.visible = False
            text_per_line.append(' > No groundtruth shape.')

        # Landmarks, scales, iterations
        text_per_line.append(' > {} landmark points.'.format(
                fr.final_shape.n_points))
        if fr.is_iterative:
            text_per_line.append(' > {} iterations.'.format(fr.n_iters))
        else:
            text_per_line.append(' > No iterations.')
        if hasattr(fr, 'n_scales'):
            text_per_line.append(' > {} scales.'.format(fr.n_scales))
        info_wid.set_widget_state(text_per_line=text_per_line)

    # Create renderer widget
    labels = ['Final']
    default_colours = ['red']
    if fitting_results[0].initial_shape is not None:
        labels.append('Initial')
        default_colours.append('blue')
    if fitting_results[0].gt_shape is not None:
        labels.append('Groundtruth')
        default_colours.append('yellow')
    renderer_options_wid = RendererOptionsWidget(
            options_tabs=['markers', 'lines', 'zoom_one', 'legend',
                          'numbering', 'image', 'axes'],
            labels=labels, axes_x_limits=None, axes_y_limits=None,
            render_function=None, style=renderer_style,
            tabs_style=renderer_tabs_style)
    # Set initial values
    renderer_options_wid.options_widgets[3].render_legend_checkbox.value = True
    renderer_options_wid.options_widgets[0].marker_face_colour_widget.set_colours(
            default_colours, allow_callback=False)
    renderer_options_wid.options_widgets[0].marker_edge_colour_widget.set_colours(
            ['black'] * len(default_colours), allow_callback=False)
    renderer_options_wid.options_widgets[1].line_colour_widget.set_colours(
            default_colours, allow_callback=False)
    renderer_options_wid.add_render_function(render_function)

    # Create info and error options
    info_wid = TextPrintWidget(text_per_line=[''] * 4, style=info_style)
    error_type_toggles = ipywidgets.ToggleButtons(
            options=['Euclidean', 'RMS'], value='Euclidean',
            description='Error type')
    norm_type_toggles = ipywidgets.ToggleButtons(
            options=['area', 'perimeter', 'avg_edge_length', 'diagonal'],
            value='avg_edge_length', description='Normalise')
    error_box = ipywidgets.VBox(children=[error_type_toggles, norm_type_toggles],
                                visible=fitting_results[0].gt_shape is not None,
                                align='start', margin='0.3cm')
    error_type_toggles.observe(update_info, names='value', type='change')
    norm_type_toggles.observe(update_info, names='value', type='change')
    info_error_box = ipywidgets.HBox(children=[info_wid, error_box],
                                     align='start')

    # Create save figure widget
    save_figure_wid = SaveFigureOptionsWidget(renderer=None,
                                              style=save_figure_style)

    def update_renderer_options(change):
        # Get selected fitting result object
        im = image_number_wid.selected_values if n_fitting_results > 1 else 0

        # Get labels
        if fitting_result_wid.result_iterations_tab.selected_index == 0:
            # We are at the Results tab
            labels = ['Final']
            if fitting_results[im].initial_shape is not None:
                labels.append('Initial')
            if fitting_results[im].gt_shape is not None:
                labels.append('Groundtruth')
        else:
            # We are at the Iterations tab
            if fitting_result_wid.iterations_mode.value == 'animation':
                # The mode is 'Animation'
                labels = None
            else:
                # The mode is 'Static'
                n_digits = len(str(len(fitting_results[im].shapes)))
                labels = []
                for j in list(range(len(fitting_results[im].shapes))):
                    if j == 0 and fitting_results[im].initial_shape is not None:
                        labels.append('Initial')
                    elif j == len(fitting_results[im].shapes) - 1:
                        labels.append('Final')
                    else:
                        labels.append("iteration {:0{}d}".format(j, n_digits))
        renderer_options_wid.set_widget_state(labels=labels,
                                              allow_callback=False)

    n_shapes = None
    if fitting_results[0].is_iterative:
        n_shapes = len(fitting_results[0].shapes)
    fitting_result_wid = IterativeResultOptionsWidget(
        has_gt_shape=fitting_results[0].gt_shape is not None,
        has_initial_shape=fitting_results[0].initial_shape is not None,
        has_image=fitting_results[0].image is not None,
        n_shapes=n_shapes, has_costs=fitting_results[0].costs is not None,
        render_function=render_function,
        tab_update_function=update_renderer_options,
        displacements_function=plot_displacements_function,
        errors_function=plot_errors_function,
        costs_function=plot_costs_function, style=fitting_result_style,
        tabs_style=fitting_result_tabs_style)

    # Group widgets
    if n_fitting_results > 1:
        # Define function that updates options' widgets state
        def update_widgets(change):
            # stop iterations animation
            fitting_result_wid.index_animation.stop_animation()

            # get selected fitting result
            im = image_number_wid.selected_values

            # Update fitting result options
            n_shapes = None
            if fitting_results[im].is_iterative:
                n_shapes = len(fitting_results[im].shapes)
            fitting_result_wid.set_widget_state(
                has_gt_shape=fitting_results[im].gt_shape is not None,
                has_initial_shape=fitting_results[im].initial_shape is not None,
                has_image=fitting_results[im].image is not None,
                n_shapes=n_shapes,
                has_costs=fitting_results[im].costs is not None,
                allow_callback=False)

            # Update renderer options
            update_renderer_options({})

            # Render callback
            render_function({})

        # Image selection slider
        index = {'min': 0, 'max': n_fitting_results - 1, 'step': 1, 'index': 0}
        image_number_wid = AnimationOptionsWidget(
            index, render_function=update_widgets, index_style=browser_style,
            interval=0.2, description='Image', loop_enabled=True,
            style=animation_style)

        # Header widget
        header_wid = ipywidgets.HBox(
            children=[LogoWidget(style=logo_style), image_number_wid],
            align='start')
    else:
        # Header widget
        header_wid = LogoWidget(style=logo_style)
    # Widget titles
    tab_titles = ['Result', 'Info', 'Renderer', 'Export']
    header_wid.margin = '0.2cm'
    options_box = ipywidgets.Tab(
        children=[fitting_result_wid, info_error_box, renderer_options_wid,
                  save_figure_wid], margin='0.2cm')
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    if n_fitting_results > 1:
        wid = ipywidgets.VBox(children=[header_wid, options_box], align='start')
    else:
        wid = ipywidgets.HBox(children=[header_wid, options_box], align='start')
    if n_fitting_results > 1:
        # If animation is activated and the user selects the save figure tab,
        # then the animation stops.
        def save_fig_tab_fun(change):
            if (change['new'] == 3 and
                    image_number_wid.play_options_toggle.value):
                image_number_wid.stop_animation()
        options_box.observe(save_fig_tab_fun, names='selected_index',
                            type='change')

    # Set widget's style
    wid.box_style = widget_box_style
    wid.border_radius = widget_border_radius
    wid.border_width = widget_border_width
    wid.border_color = map_styles_to_hex_colours(widget_box_style)

    # Display final widget
    ipydisplay.display(wid)

    # Trigger initial visualization
    render_function({})
