from collections import Sized

import ipywidgets
import IPython.display as ipydisplay

from menpowidgets.options import (RendererOptionsWidget, TextPrintWidget,
                                  AnimationOptionsWidget, SaveMayaviFigureOptionsWidget)
from menpowidgets.style import map_styles_to_hex_colours
from menpowidgets.tools import LogoWidget


def visualize_meshes(meshes, style='coloured', browser_style='buttons'):
    # Ensure that the code is being run inside a Jupyter kernel!!
    from menpowidgets.utils import verify_ipython_and_kernel
    verify_ipython_and_kernel()
    print('Initializing...')

    if not isinstance(meshes, Sized):
        meshes = [meshes]

    n_meshes = len(meshes)

    # Define the styling options
    if style == 'coloured':
        logo_style = 'warning'
        widget_box_style = 'warning'
        widget_border_radius = 10
        widget_border_width = 1
        animation_style = 'warning'
        info_style = 'info'
        renderer_style = 'warning'
        renderer_tabs_style = 'info'
        save_figure_style = 'danger'
    else:
        logo_style = 'minimal'
        widget_box_style = ''
        widget_border_radius = 0
        widget_border_width = 0
        animation_style = 'minimal'
        renderer_style = 'minimal'
        renderer_tabs_style = 'minimal'
        info_style = 'minimal'
        save_figure_style = 'minimal'

    # Define render function
    def render_function(_):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # Get selected pointcloud index
        mesh_no = mesh_number_wid.selected_values if n_meshes > 1 else 0

        # Render shape instance with selected options
        options = renderer_options_wid.selected_values['trimesh']

        # Clear figure
        save_figure_wid.renderer.clear_figure()

        # Render instance
        renderer = meshes[mesh_no].view(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False, **options)

        # Save the current figure id
        save_figure_wid.renderer = renderer

        # Update info
        update_info(meshes[mesh_no])

        # Force rendering
        renderer.force_draw()

    # Define function that updates the info text
    def update_info(mesh):
        from menpo.shape import TriMesh, TexturedTriMesh, ColouredTriMesh
        label = 'Unknown Mesh Type'
        cls_to_label = {
            TriMesh: 'TriMesh',
            TexturedTriMesh: 'TexturedTriMesh',
            ColouredTriMesh: 'ColouredTriMesh'
        }
        for cls in cls_to_label:
            if isinstance(mesh, cls):
                label = cls_to_label[cls]

        text_per_line = [
            "> {}".format(mesh),
            "> Path : {}".format(mesh.path if hasattr(mesh, 'path') else '-'),
            "> range : {}".format(mesh.range()),
            "> min bounds : {}".format(mesh.bounds()[0]),
            "> max bounds : {}".format(mesh.bounds()[1])
        ]
        info_wid.set_widget_state(text_per_line=text_per_line)

    renderer_options_wid = RendererOptionsWidget(
        options_tabs=['trimesh'], labels=None, render_function=render_function,
        style=renderer_style, tabs_style=renderer_tabs_style)
    info_wid = TextPrintWidget(text_per_line=[''] * 1, style=info_style)
    save_figure_wid = SaveMayaviFigureOptionsWidget(renderer=None,
                                                    style=save_figure_style)
    # Group widgets
    if n_meshes > 1:
        # selection slider
        index = {'min': 0, 'max': n_meshes-1, 'step': 1, 'index': 0}
        mesh_number_wid = AnimationOptionsWidget(
            index, render_function=render_function, index_style=browser_style,
            interval=0.2, description='Mesh ', loop_enabled=True,
            continuous_update=False, style=animation_style)

        # Header widget
        header_wid = ipywidgets.HBox(
            children=[LogoWidget(style=logo_style), mesh_number_wid],
            align='start')
    else:
        # Header widget
        header_wid = LogoWidget(style=logo_style)
    header_wid.margin = '0.1cm'
    options_box = ipywidgets.Tab(children=[info_wid, renderer_options_wid,
                                           save_figure_wid], margin='0.1cm')
    tab_titles = ['Info', 'Renderer', 'Export']
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    if n_meshes > 1:
        wid = ipywidgets.VBox(children=[header_wid, options_box], align='start')
    else:
        wid = ipywidgets.HBox(children=[header_wid, options_box], align='start')

    # Set widget's style
    wid.box_style = widget_box_style
    wid.border_radius = widget_border_radius
    wid.border_width = widget_border_width
    wid.border_color = map_styles_to_hex_colours(widget_box_style)

    # Display final widget
    ipydisplay.display(wid)

    # Trigger initial visualization
    render_function({})
