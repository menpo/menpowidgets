from menpo.base import MenpoMissingDependencyError


try:
    import menpo3d
except ImportError:
    raise MenpoMissingDependencyError('menpo3d')

# Continue with imports if we have menpo3d
import sys
from collections import OrderedDict
import mayavi.mlab as mlab
import matplotlib.pyplot as plt

import ipywidgets
import IPython.display as ipydisplay

from ..style import map_styles_to_hex_colours
from ..checks import check_n_parameters
from ..options import (RendererOptionsWidget, TextPrintWidget,
                       LinearModelParametersWidget, LogoWidget,
                       SaveMayaviFigureOptionsWidget)


def visualize_shape_model_3d(shape_model, n_parameters=5, mode='multiple',
                             parameters_bounds=(-3.0, 3.0), style='coloured'):
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
    style : ``{'coloured', 'minimal'}``, optional
        If ``'coloured'``, then the style of the widget will be coloured. If
        ``minimal``, then the style is simple using black and white colours.
    """
    print('Initializing...')
    sys.stdout.flush()

    # Ensure that the code is being run inside a Jupyter kernel!
    from ..utils import verify_ipython_and_kernel
    verify_ipython_and_kernel()

    # Make sure that shape_model is a list even with one member
    if not isinstance(shape_model, list):
        shape_model = [shape_model]

    # Get the number of levels (i.e. number of shape models)
    n_levels = len(shape_model)

    # Define the styling options
    if style == 'coloured':
        model_parameters_style = 'info'
        logo_style = 'warning'
        widget_box_style = 'warning'
        widget_border_radius = 10
        widget_border_width = 1
        info_style = 'info'
        renderer_style = 'danger'
        renderer_tabs_style = 'danger'
        save_figure_style = 'danger'
    elif style == 'minimal':
        model_parameters_style = 'minimal'
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
    max_n_params = [sp.n_active_components for sp in shape_model]

    # Check the given number of parameters (the returned n_parameters is a list
    # of len n_scales)
    n_parameters = check_n_parameters(n_parameters, n_levels, max_n_params)

    # Define render function
    def render_function(change):
        # Get selected level
        level = 0
        if n_levels > 1:
            level = level_wid.value

        # Compute weights
        parameters = model_parameters_wid.selected_values
        weights = (parameters *
                   shape_model[level].eigenvalues[:len(parameters)] ** 0.5)

        # Render shape instance with selected options
        options = renderer_options_wid.selected_values['trimesh']

        # Compute instance
        instance = shape_model[level].instance(weights)

        # Clear figure
        mlab.clf()

        # Render instance
        renderer = instance.view(figure_id=save_figure_wid.renderer.figure_id,
                                 new_figure=False, **options)

        # Get instance range
        instance_range = instance.range()

        mlab.show()

        # Save the current figure id
        save_figure_wid.renderer = renderer

        # Update info
        update_info(level, instance_range)

    # Define function that updates the info text
    def update_info(level, instance_range):
        text_per_line = [
            "> Level {} out of {}".format(level + 1, n_levels),
            "> {} components in total".format(shape_model[level].n_components),
            "> {} active components".format(
                shape_model[level].n_active_components),
            "> {:.1f}% variance kept".format(
                shape_model[level].variance_ratio() * 100),
            "> Instance range: {:.1f} x {:.1f}".format(instance_range[0],
                                                       instance_range[1]),
            "> {} points".format(
                shape_model[level].mean().n_points)]
        info_wid.set_widget_state(text_per_line=text_per_line)

    # Plot variance function
    def plot_variance(name):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # Get selected level
        level = level_wid.value if n_levels > 1 else 0

        # Render
        plt.subplot(121)
        shape_model[level].plot_eigenvalues_ratio()
        plt.subplot(122)
        renderer = shape_model[level].plot_eigenvalues_cumulative_ratio()
        plt.show()

    # Create widgets
    model_parameters_wid = LinearModelParametersWidget(
        n_parameters[0], render_function, params_str='Parameter ',
        mode=mode, params_bounds=parameters_bounds, params_step=0.1,
        plot_variance_visible=True, plot_variance_function=plot_variance,
        animation_step=0.5, interval=0., loop_enabled=True,
        style=model_parameters_style, continuous_update=False)
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=['trimesh'], labels=None, render_function=render_function,
        style=renderer_style, tabs_style=renderer_tabs_style)
    info_wid = TextPrintWidget(text_per_line=[''] * 6, style=info_style)
    save_figure_wid = SaveMayaviFigureOptionsWidget(renderer=None,
                                                    style=save_figure_style)

    # Define function that updates options' widgets state
    def update_widgets(change):
        model_parameters_wid.set_widget_state(
            n_parameters=n_parameters[change['new']], params_str='Parameter ',
            allow_callback=True)

    # Group widgets
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
            margin='0.3cm')
        level_wid.observe(update_widgets, names='value', type='change')
        level_wid.observe(render_function, names='value', type='change')
        tmp_wid = ipywidgets.HBox(children=[level_wid, model_parameters_wid])
    else:
        tmp_wid = ipywidgets.HBox(children=[model_parameters_wid])
    options_box = ipywidgets.Tab(children=[tmp_wid, renderer_options_wid,
                                           info_wid, save_figure_wid])
    tab_titles = ['Model', 'Renderer', 'Info', 'Export']
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
    ipydisplay.clear_output()
