from collections import Sized

import ipywidgets
import IPython.display as ipydisplay

from menpo.base import name_of_callable
from menpo.shape import ColouredTriMesh, TexturedTriMesh
from menpo.visualize import print_dynamic
from menpowidgets.options import (TextPrintWidget, AnimationOptionsWidget,
                                  SaveMayaviFigureOptionsWidget,
                                  Mesh3DOptionsWidget)
from menpowidgets.style import map_styles_to_hex_colours
from menpowidgets.tools import LogoWidget


def visualize_meshes(meshes, browser_style='buttons', custom_info_callback=None):
    r"""
    Widget that allows browsing through a `list` of
    3D meshes. The supported objects are:

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
    # Ensure that the code is being run inside a Jupyter kernel!!
    from menpowidgets.utils import verify_ipython_and_kernel
    verify_ipython_and_kernel()
    print('Initializing...')

    # Make sure that meshes is a list even with one member
    if not isinstance(meshes, Sized):
        meshes = [meshes]

    # Get the number of meshes
    n_meshes = len(meshes)

    # Define the styling options
    main_style = 'warning'

    # Define render function
    def render_function(_):
        # Clear current figure
        save_figure_wid.renderer.clear_figure()
        ipydisplay.clear_output(wait=True)

        # Get selected mesh index
        i = mesh_number_wid.selected_values if n_meshes > 1 else 0

        # Update info text widget
        update_info(meshes[i], custom_info_callback=custom_info_callback)

        # Render instance
        save_figure_wid.renderer = meshes[i].view(
            figure_id=save_figure_wid.renderer.figure_id, new_figure=False,
            **mesh_options_wid.selected_values)

        # Force rendering
        save_figure_wid.renderer.force_draw()

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
                min_b[0], max_b[0], min_b[1], max_b[1], min_b[2], max_b[2]),
            "> Range: {0:.1f}X, {1:.1f}Y, {2:.1f}Z".format(rang[0], rang[1],
                                                           rang[2]),
            "> Centre of mass: ({0:.1f}X, {1:.1f}Y, {2:.1f}Z)".format(
                cm[0], cm[1], cm[2]),
            "> Norm: {0:.2f}".format(mesh.norm())]
        if custom_info_callback is not None:
            # iterate over the list of messages returned by the callback
            # function and append them in the text_per_line.
            for msg in custom_info_callback(mesh):
                text_per_line.append('> {}'.format(msg))
        info_wid.set_widget_state(text_per_line=text_per_line)

    # Create widgets
    mesh_options_wid = Mesh3DOptionsWidget(
        textured=(isinstance(meshes[0], ColouredTriMesh) or
                  isinstance(meshes[0], TexturedTriMesh)),
        render_function=render_function)
    info_wid = TextPrintWidget(text_per_line=[''])
    save_figure_wid = SaveMayaviFigureOptionsWidget()

    # Group widgets
    if n_meshes > 1:
        # Define function that updates options' widgets state
        def update_widgets(change):
            i = change['new']

            # Update shape options
            mesh_options_wid.set_widget_state(
                textured=(isinstance(meshes[i], ColouredTriMesh) or
                          isinstance(meshes[i], TexturedTriMesh)),
                allow_callback=True)

        # selection slider
        index = {'min': 0, 'max': n_meshes-1, 'step': 1, 'index': 0}
        mesh_number_wid = AnimationOptionsWidget(
            index, render_function=update_widgets, index_style=browser_style,
            interval=0.2, description='Mesh', loop_enabled=True,
            continuous_update=False)

        # Header widget
        logo_wid = LogoWidget(style=main_style)
        logo_wid.layout.margin = '0px 10px 0px 0px'
        header_wid = ipywidgets.HBox([logo_wid, mesh_number_wid])
        header_wid.layout.align_items = 'center'
        header_wid.layout.margin = '0px 0px 10px 0px'
    else:
        # Header widget
        header_wid = LogoWidget(style=main_style)
        header_wid.layout.margin = '0px 10px 0px 0px'
    options_box = ipywidgets.Tab([info_wid, mesh_options_wid, save_figure_wid])
    tab_titles = ['Info', 'Mesh', 'Export']
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    if n_meshes > 1:
        wid = ipywidgets.VBox([header_wid, options_box])
    else:
        wid = ipywidgets.HBox([header_wid, options_box])

    # Set widget's style
    wid.box_style = main_style
    wid.layout.border = '2px solid ' + map_styles_to_hex_colours(main_style)

    # Display final widget
    final_box = ipywidgets.Box([wid])
    final_box.layout.display = 'flex'
    ipydisplay.display(final_box)

    # Trigger initial visualization
    render_function({})
    print_dynamic('')
