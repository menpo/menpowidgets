from collections import Sized
import matplotlib.pyplot as plt

import ipywidgets
import IPython.display as ipydisplay

from menpo.image import MaskedImage, Image
from menpo.image.base import _convert_patches_list_to_single_array

from .options import (RendererOptionsWidget, TextPrintWidget,
                      SaveFigureOptionsWidget, AnimationOptionsWidget,
                      LandmarkOptionsWidget, ChannelOptionsWidget,
                      FeatureOptionsWidget, PlotOptionsWidget,
                      PatchOptionsWidget)
from .style import format_box, map_styles_to_hex_colours
from .tools import LogoWidget
from .utils import (extract_group_labels_from_landmarks,
                    extract_groups_labels_from_image, render_image,
                    render_patches)


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


def visualize_pointclouds(pointclouds, figure_size=(10, 8), style='coloured',
                          browser_style='buttons'):
    r"""
    Widget that allows browsing through a `list` of :map:`PointCloud`,
    :map:`PointUndirectedGraph`, :map:`PointDirectedGraph`, :map:`PointTree`,
    :map:`TriMesh` or subclasses. Any instance of the above can be combined in
    the `list`.

    The widget has options tabs regarding the renderer (lines, markers,
    numbering, zoom, axes) and saving the figure to file.

    Parameters
    ----------
    pointclouds : `list`
        The `list` of objects to be visualized. It can contain a combination of
        :map:`PointCloud`, :map:`PointUndirectedGraph`,
        :map:`PointDirectedGraph`, :map:`PointTree`, :map:`TriMesh` or
        subclasses of those.
    figure_size : (`int`, `int`), optional
        The initial size of the rendered figure.
    style : {``'coloured'``, ``'minimal'``}, optional
        If ``'coloured'``, then the style of the widget will be coloured. If
        ``minimal``, then the style is simple using black and white colours.
    browser_style : {``'buttons'``, ``'slider'``}, optional
        It defines whether the selector of the objects will have the form of
        plus/minus buttons or a slider.
    """
    print('Initializing...')

    # Make sure that pointclouds is a list even with one pointcloud member
    if not isinstance(pointclouds, Sized):
        pointclouds = [pointclouds]

    # Get the number of pointclouds
    n_pointclouds = len(pointclouds)

    # Define the styling options
    if style == 'coloured':
        logo_style = 'warning'
        widget_box_style = 'warning'
        widget_border_radius = 10
        widget_border_width = 1
        animation_style = 'warning'
        info_style = 'info'
        renderer_box_style = 'info'
        renderer_box_border_colour = map_styles_to_hex_colours('info')
        renderer_box_border_radius = 10
        renderer_style = 'danger'
        renderer_tabs_style = 'danger'
        save_figure_style = 'danger'
    else:
        logo_style = 'minimal'
        widget_box_style = ''
        widget_border_radius = 0
        widget_border_width = 0
        animation_style = 'minimal'
        info_style = 'minimal'
        renderer_box_style = ''
        renderer_box_border_colour = 'black'
        renderer_box_border_radius = 0
        renderer_style = 'minimal'
        renderer_tabs_style = 'minimal'
        save_figure_style = 'minimal'

    # Define render function
    def render_function(name, value):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # Get selected pointcloud index
        im = 0
        if n_pointclouds > 1:
            im = pointcloud_number_wid.selected_values

        # Update info text widget
        update_info(pointclouds[im])

        # Render pointcloud with selected options
        options = renderer_options_wid.selected_values['lines']
        options.update(renderer_options_wid.selected_values['markers'])
        options.update(renderer_options_wid.selected_values['numbering'])
        options.update(renderer_options_wid.selected_values['axes'])
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * figure_size[0],
            renderer_options_wid.selected_values['zoom_one'] * figure_size[1])
        renderer = pointclouds[im].view(
            figure_id=save_figure_wid.renderer.figure_id,
            new_figure=False, image_view=axes_mode_wid.value == 1,
            figure_size=new_figure_size, label=None, **options)
        plt.show()

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Define function that updates the info text
    def update_info(pointcloud):
        min_b, max_b = pointcloud.bounds()
        rang = pointcloud.range()
        cm = pointcloud.centre()
        text_per_line = [
            "> {} points".format(pointcloud.n_points),
            "> Bounds: [{0:.1f}-{1:.1f}]W, [{2:.1f}-{3:.1f}]H".format(
                min_b[0], max_b[0], min_b[1], max_b[1]),
            "> Range: {0:.1f}W, {1:.1f}H".format(rang[0], rang[1]),
            "> Centre of mass: ({0:.1f}, {1:.1f})".format(cm[0], cm[1]),
            "> Norm: {0:.2f}".format(pointcloud.norm())]
        info_wid.set_widget_state(n_lines=5, text_per_line=text_per_line)

    # Create widgets
    axes_mode_wid = ipywidgets.RadioButtons(
        options={'Image': 1, 'Point cloud': 2}, description='Axes mode:',
        value=2)
    axes_mode_wid.on_trait_change(render_function, 'value')
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=['markers', 'lines', 'numbering', 'zoom_one', 'axes'],
        labels=None, axes_x_limits=0.1, axes_y_limits=0.1,
        render_function=render_function, style=renderer_style,
        tabs_style=renderer_tabs_style)
    renderer_options_box = ipywidgets.VBox(
        children=[axes_mode_wid, renderer_options_wid], align='center',
        margin='0.1cm')
    info_wid = TextPrintWidget(n_lines=5, text_per_line=[''] * 5,
                               style=info_style)
    save_figure_wid = SaveFigureOptionsWidget(style=save_figure_style)

    # Group widgets
    if n_pointclouds > 1:
        # Pointcloud selection slider
        index = {'min': 0, 'max': n_pointclouds-1, 'step': 1, 'index': 0}
        pointcloud_number_wid = AnimationOptionsWidget(
            index, render_function=render_function, index_style=browser_style,
            interval=0.2, description='Pointcloud ', loop_enabled=True,
            continuous_update=False, style=animation_style)

        # Header widget
        header_wid = ipywidgets.HBox(
            children=[LogoWidget(style=logo_style), pointcloud_number_wid],
            align='start')
    else:
        # Header widget
        header_wid = LogoWidget(style=logo_style)
    header_wid.margin = '0.1cm'
    options_box = ipywidgets.Tab(children=[info_wid, renderer_options_box,
                                           save_figure_wid], margin='0.1cm')
    tab_titles = ['Info', 'Renderer', 'Export']
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    if n_pointclouds > 1:
        wid = ipywidgets.VBox(children=[header_wid, options_box], align='start')
    else:
        wid = ipywidgets.HBox(children=[header_wid, options_box], align='start')

    # Set widget's style
    wid.box_style = widget_box_style
    wid.border_radius = widget_border_radius
    wid.border_width = widget_border_width
    wid.border_color = map_styles_to_hex_colours(widget_box_style)
    format_box(renderer_options_box, renderer_box_style, True,
               renderer_box_border_colour, 'solid', 1,
               renderer_box_border_radius, '0.1cm', '0.2cm')

    # Display final widget
    ipydisplay.display(wid)

    # Reset value to trigger initial visualization
    axes_mode_wid.value = 1


def visualize_landmarkgroups(landmarkgroups, figure_size=(10, 8),
                             style='coloured', browser_style='buttons'):
    r"""
    Widget that allows browsing through a `list` of :map:`LandmarkGroup`
    (or subclass) objects.

    The landmark groups can have a combination of different attributes, e.g.
    different labels, number of points etc. The widget has options tabs
    regarding the landmarks, the renderer (lines, markers, numbering, legend,
    zoom, axes) and saving the figure to file.

    Parameters
    ----------
    landmarkgroups : `list` of :map:`LandmarkGroup` or subclass
        The `list` of landmark groups to be visualized.
    figure_size : (`int`, `int`), optional
        The initial size of the rendered figure.
    style : {``'coloured'``, ``'minimal'``}, optional
        If ``'coloured'``, then the style of the widget will be coloured. If
        ``minimal``, then the style is simple using black and white colours.
    browser_style : {``'buttons'``, ``'slider'``}, optional
        It defines whether the selector of the objects will have the form of
        plus/minus buttons or a slider.
    """
    print('Initializing...')

    # Make sure that landmarkgroups is a list even with one landmark group
    # member
    if not isinstance(landmarkgroups, list):
        landmarkgroups = [landmarkgroups]

    # Get the number of landmarkgroups
    n_landmarkgroups = len(landmarkgroups)

    # Define the styling options
    if style == 'coloured':
        logo_style = 'success'
        widget_box_style = 'success'
        widget_border_radius = 10
        widget_border_width = 1
        animation_style = 'success'
        landmarks_style = 'info'
        info_style = 'info'
        renderer_box_style = 'info'
        renderer_box_border_colour = map_styles_to_hex_colours('info')
        renderer_box_border_radius = 10
        renderer_style = 'danger'
        renderer_tabs_style = 'danger'
        save_figure_style = 'danger'
    else:
        logo_style = 'minimal'
        widget_box_style = ''
        widget_border_radius = 0
        widget_border_width = 0
        landmarks_style = 'minimal'
        animation_style = 'minimal'
        info_style = 'minimal'
        renderer_box_style = ''
        renderer_box_border_colour = 'black'
        renderer_box_border_radius = 0
        renderer_style = 'minimal'
        renderer_tabs_style = 'minimal'
        save_figure_style = 'minimal'

    # Define render function
    def render_function(name, value):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # get selected index
        im = 0
        if n_landmarkgroups > 1:
            im = landmark_number_wid.selected_values

        # update info text widget
        update_info(landmarkgroups[im])

        # show landmarks with selected options
        tmp1 = renderer_options_wid.selected_values['lines']
        tmp2 = renderer_options_wid.selected_values['markers']
        options = renderer_options_wid.selected_values['numbering']
        options.update(renderer_options_wid.selected_values['legend'])
        options.update(renderer_options_wid.selected_values['axes'])
        new_figure_size = (
            renderer_options_wid.selected_values['zoom_one'] * figure_size[0],
            renderer_options_wid.selected_values['zoom_one'] * figure_size[1])

        # get line and marker colours
        line_colour = []
        marker_face_colour = []
        marker_edge_colour = []
        for lbl in landmark_options_wid.selected_values['with_labels']:
            lbl_idx = landmarkgroups[im].labels.index(lbl)
            line_colour.append(tmp1['line_colour'][lbl_idx])
            marker_face_colour.append(tmp2['marker_face_colour'][lbl_idx])
            marker_edge_colour.append(tmp2['marker_edge_colour'][lbl_idx])

        if landmark_options_wid.selected_values['render_landmarks']:
            renderer = landmarkgroups[im].view(
                with_labels=landmark_options_wid.selected_values['with_labels'],
                figure_id=save_figure_wid.renderer.figure_id, new_figure=False,
                image_view=axes_mode_wid.value == 1,
                render_lines=tmp1['render_lines'], line_colour=line_colour,
                line_style=tmp1['line_style'], line_width=tmp1['line_width'],
                render_markers=tmp2['render_markers'],
                marker_style=tmp2['marker_style'],
                marker_size=tmp2['marker_size'],
                marker_face_colour=marker_face_colour,
                marker_edge_colour=marker_edge_colour,
                marker_edge_width=tmp2['marker_edge_width'],
                figure_size=new_figure_size, **options)
            plt.show()

            # Save the current figure id
            save_figure_wid.renderer = renderer
        else:
            ipydisplay.clear_output()

    # Define function that updates the info text
    def update_info(landmarkgroup):
        min_b, max_b = landmarkgroup.lms.bounds()
        rang = landmarkgroup.lms.range()
        cm = landmarkgroup.lms.centre()
        text_per_line = [
            "> {} landmark points".format(landmarkgroup.n_landmarks),
            "> Bounds: [{0:.1f}-{1:.1f}]W, [{2:.1f}-{3:.1f}]H".format(
                min_b[0], max_b[0], min_b[1], max_b[1]),
            "> Range: {0:.1f}W, {1:.1f}H".format(rang[0], rang[1]),
            "> Centre of mass: ({0:.1f}, {1:.1f})".format(cm[0], cm[1]),
            "> Norm: {0:.2f}".format(landmarkgroup.lms.norm())]
        info_wid.set_widget_state(n_lines=5, text_per_line=text_per_line)

    # Create widgets
    landmark_options_wid = LandmarkOptionsWidget(
        group_keys=['  '], labels_keys=[landmarkgroups[0].labels],
        render_function=render_function, style=landmarks_style)
    axes_mode_wid = ipywidgets.RadioButtons(
        options={'Image': 1, 'Point cloud': 2}, description='Axes mode:',
        value=1)
    axes_mode_wid.on_trait_change(render_function, 'value')
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=['lines', 'markers', 'numbering', 'legend', 'zoom_one',
                      'axes'], labels=landmarkgroups[0].labels,
        axes_x_limits=0.1, axes_y_limits=0.1,
        render_function=render_function,  style=renderer_style,
        tabs_style=renderer_tabs_style)
    renderer_options_box = ipywidgets.VBox(
        children=[axes_mode_wid, renderer_options_wid], align='center',
        margin='0.1cm')
    info_wid = TextPrintWidget(n_lines=5, text_per_line=[''] * 5,
                               style=info_style)
    save_figure_wid = SaveFigureOptionsWidget(renderer=None,
                                              style=save_figure_style)

    # Group widgets
    if n_landmarkgroups > 1:
        # Define function that updates options' widgets state
        def update_widgets(name, value):
            # Get new labels
            im = landmark_number_wid.selected_values
            labels = landmarkgroups[im].labels
            # Update renderer options
            renderer_options_wid.set_widget_state(labels=labels,
                                                  allow_callback=False)
            # Update landmarks options
            landmark_options_wid.set_widget_state(
                group_keys=['  '], labels_keys=[labels], allow_callback=True)
            landmark_options_wid.predefined_style(landmarks_style)

        # Landmark selection slider
        index = {'min': 0, 'max': n_landmarkgroups-1, 'step': 1, 'index': 0}
        landmark_number_wid = AnimationOptionsWidget(
            index, render_function=update_widgets, index_style=browser_style,
            interval=0.2, description='Shape', loop_enabled=True,
            continuous_update=False, style=animation_style)

        # Header widget
        header_wid = ipywidgets.HBox(
            children=[LogoWidget(style=logo_style), landmark_number_wid],
            align='start')
    else:
        # Header widget
        header_wid = LogoWidget(style=logo_style)
    header_wid.margin = '0.2cm'
    options_box = ipywidgets.Tab(
        children=[info_wid, landmark_options_wid, renderer_options_box,
                  save_figure_wid], margin='0.2cm')
    tab_titles = ['Info', 'Landmarks', 'Renderer', 'Export']
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    if n_landmarkgroups > 1:
        wid = ipywidgets.VBox(children=[header_wid, options_box], align='start')
    else:
        wid = ipywidgets.HBox(children=[header_wid, options_box], align='start')

    # Set widget's style
    wid.box_style = widget_box_style
    wid.border_radius = widget_border_radius
    wid.border_width = widget_border_width
    wid.border_color = map_styles_to_hex_colours(widget_box_style)
    format_box(renderer_options_box, renderer_box_style, True,
               renderer_box_border_colour, 'solid', 1,
               renderer_box_border_radius, '0.1cm', '0.2cm')

    # Display final widget
    ipydisplay.display(wid)

    # Reset value to trigger initial visualization
    renderer_options_wid.options_widgets[3].render_legend_checkbox.value = False


def visualize_landmarks(landmarks, figure_size=(10, 8), style='coloured',
                        browser_style='buttons'):
    r"""
    Widget that allows browsing through a `list` of :map:`LandmarkManager`
    (or subclass) objects.

    The landmark managers can have a combination of different attributes, e.g.
    landmark groups and labels etc. The widget has options tabs regarding the
    landmarks, the renderer (lines, markers, numbering, legend, zoom, axes)
    and saving the figure to file.

    Parameters
    ----------
    landmarks : `list` of :map:`LandmarkManager` or subclass
        The `list` of landmark managers to be visualized.
    figure_size : (`int`, `int`), optional
        The initial size of the rendered figure.
    style : {``'coloured'``, ``'minimal'``}, optional
        If ``'coloured'``, then the style of the widget will be coloured. If
        ``minimal``, then the style is simple using black and white colours.
    browser_style : {``'buttons'``, ``'slider'``}, optional
        It defines whether the selector of the objects will have the form of
        plus/minus buttons or a slider.
    """
    print('Initializing...')

    # Make sure that landmarks is a list even with one landmark manager member
    if not isinstance(landmarks, list):
        landmarks = [landmarks]

    # Get the number of landmark managers
    n_landmarks = len(landmarks)

    # Define the styling options
    if style == 'coloured':
        logo_style = 'info'
        widget_box_style = 'info'
        widget_border_radius = 10
        widget_border_width = 1
        animation_style = 'info'
        landmarks_style = 'danger'
        info_style = 'danger'
        renderer_box_style = 'danger'
        renderer_box_border_colour = map_styles_to_hex_colours('danger')
        renderer_box_border_radius = 10
        renderer_style = 'warning'
        renderer_tabs_style = 'warning'
        save_figure_style = 'danger'
    else:
        logo_style = 'minimal'
        widget_box_style = ''
        widget_border_radius = 0
        widget_border_width = 0
        landmarks_style = 'minimal'
        animation_style = 'minimal'
        info_style = 'minimal'
        renderer_box_style = ''
        renderer_box_border_colour = 'black'
        renderer_box_border_radius = 0
        renderer_style = 'minimal'
        renderer_tabs_style = 'minimal'
        save_figure_style = 'minimal'

    # Define render function
    def render_function(name, value):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # get selected index
        im = 0
        if n_landmarks > 1:
            im = landmark_number_wid.selected_values

        # get selected group
        selected_group = landmark_options_wid.selected_values['group']

        # update info text widget
        update_info(landmarks[im], selected_group)

        if landmark_options_wid.selected_values['render_landmarks']:
            # show landmarks with selected options
            tmp1 = renderer_options_wid.selected_values['lines']
            tmp2 = renderer_options_wid.selected_values['markers']
            options = renderer_options_wid.selected_values['numbering']
            options.update(renderer_options_wid.selected_values['legend'])
            options.update(renderer_options_wid.selected_values['axes'])
            new_figure_size = (
                renderer_options_wid.selected_values['zoom_one'] * figure_size[0],
                renderer_options_wid.selected_values['zoom_one'] * figure_size[1])
            # get line and marker colours
            line_colour = []
            marker_face_colour = []
            marker_edge_colour = []
            for lbl in landmark_options_wid.selected_values['with_labels']:
                lbl_idx = landmarks[im][selected_group].labels.index(lbl)
                line_colour.append(tmp1['line_colour'][lbl_idx])
                marker_face_colour.append(tmp2['marker_face_colour'][lbl_idx])
                marker_edge_colour.append(tmp2['marker_edge_colour'][lbl_idx])
            # render
            renderer = landmarks[im][selected_group].view(
                with_labels=landmark_options_wid.selected_values['with_labels'],
                figure_id=save_figure_wid.renderer.figure_id, new_figure=False,
                image_view=axes_mode_wid.value == 1,
                render_lines=tmp1['render_lines'], line_colour=line_colour,
                line_style=tmp1['line_style'], line_width=tmp1['line_width'],
                render_markers=tmp2['render_markers'],
                marker_style=tmp2['marker_style'],
                marker_size=tmp2['marker_size'],
                marker_face_colour=marker_face_colour,
                marker_edge_colour=marker_edge_colour,
                marker_edge_width=tmp2['marker_edge_width'],
                figure_size=new_figure_size, **options)
            plt.show()

            # Save the current figure id
            save_figure_wid.renderer = renderer
        else:
            ipydisplay.clear_output()

    # Define function that updates the info text
    def update_info(landmarks, group):
        if group is not None:
            min_b, max_b = landmarks[group][None].bounds()
            rang = landmarks[group][None].range()
            cm = landmarks[group][None].centre()
            text_per_line = [
                "> {} landmark points".format(landmarks[group][None].n_points),
                "> Bounds: [{0:.1f}-{1:.1f}]W, [{2:.1f}-{3:.1f}]H".
                    format(min_b[0], max_b[0], min_b[1], max_b[1]),
                "> Range: {0:.1f}W, {1:.1f}H".format(rang[0], rang[1]),
                "> Centre of mass: ({0:.1f}, {1:.1f})".format(cm[0], cm[1]),
                "> Norm: {0:.2f}".format(landmarks[group][None].norm())]
            n_lines = 5
        else:
            text_per_line = ["No landmarks available."]
            n_lines = 1
        info_wid.set_widget_state(n_lines=n_lines, text_per_line=text_per_line)

    # Create widgets
    groups_keys, labels_keys = extract_group_labels_from_landmarks(landmarks[0])
    axes_mode_wid = ipywidgets.RadioButtons(
        options={'Image': 1, 'Point cloud': 2}, description='Axes mode:',
        value=1)
    axes_mode_wid.on_trait_change(render_function, 'value')
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=['markers', 'lines', 'numbering', 'legend', 'zoom_one',
                      'axes'], labels=labels_keys[0],
        axes_x_limits=0.1, axes_y_limits=0.1,
        render_function=render_function,  style=renderer_style,
        tabs_style=renderer_tabs_style)
    renderer_options_box = ipywidgets.VBox(
        children=[axes_mode_wid, renderer_options_wid], align='center',
        margin='0.1cm')
    landmark_options_wid = LandmarkOptionsWidget(
        group_keys=groups_keys, labels_keys=labels_keys,
        render_function=render_function, style=landmarks_style,
        renderer_widget=renderer_options_wid)
    info_wid = TextPrintWidget(n_lines=5, text_per_line=[''] * 5,
                               style=info_style)
    save_figure_wid = SaveFigureOptionsWidget(renderer=None,
                                              style=save_figure_style)

    # Group widgets
    if n_landmarks > 1:
        # Define function that updates options' widgets state
        def update_widgets(name, value):
            # Get new groups and labels
            im = landmark_number_wid.selected_values
            group_keys, labels_keys = extract_group_labels_from_landmarks(
                landmarks[im])

            # Update landmarks options
            landmark_options_wid.set_widget_state(
                group_keys=group_keys, labels_keys=labels_keys,
                allow_callback=True)
            landmark_options_wid.predefined_style(landmarks_style)

        # Landmark selection slider
        index = {'min': 0, 'max': n_landmarks-1, 'step': 1, 'index': 0}
        landmark_number_wid = AnimationOptionsWidget(
            index, render_function=update_widgets, index_style=browser_style,
            interval=0.2, description='Shape', loop_enabled=True,
            continuous_update=False, style=animation_style)

        # Header widget
        header_wid = ipywidgets.HBox(
            children=[LogoWidget(style=logo_style), landmark_number_wid],
            align='start')
    else:
        # Header widget
        header_wid = LogoWidget(style=logo_style)
    header_wid.margin = '0.2cm'
    options_box = ipywidgets.Tab(
        children=[info_wid, landmark_options_wid, renderer_options_box,
                  save_figure_wid], margin='0.2cm')
    tab_titles = ['Info', 'Landmarks', 'Renderer', 'Export']
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    if n_landmarks > 1:
        wid = ipywidgets.VBox(children=[header_wid, options_box], align='start')
    else:
        wid = ipywidgets.HBox(children=[header_wid, options_box], align='start')

    # Set widget's style
    wid.box_style = widget_box_style
    wid.border_radius = widget_border_radius
    wid.border_width = widget_border_width
    wid.border_color = map_styles_to_hex_colours(widget_box_style)
    format_box(renderer_options_box, renderer_box_style, True,
               renderer_box_border_colour, 'solid', 1,
               renderer_box_border_radius, '0.1cm', '0.2cm')

    # Display final widget
    ipydisplay.display(wid)

    # Reset value to trigger initial visualization
    renderer_options_wid.options_widgets[3].render_legend_checkbox.value = False


def visualize_images(images, figure_size=(10, 8), style='coloured',
                     browser_style='buttons'):
    r"""
    Widget that allows browsing through a `list` of :map:`Image` (or subclass)
    objects.

    The images can have a combination of different attributes, e.g. masked or
    not, landmarked or not, without multiple landmark groups and labels etc.
    The widget has options tabs regarding the visualized channels, the
    landmarks, the renderer (lines, markers, numbering, legend, figure, axes)
    and saving the figure to file.

    Parameters
    ----------
    images : `list` of :map:`Image` or subclass
        The `list` of images to be visualized.
    figure_size : (`int`, `int`), optional
        The initial size of the rendered figure.
    style : {``'coloured'``, ``'minimal'``}, optional
        If ``'coloured'``, then the style of the widget will be coloured. If
        ``minimal``, then the style is simple using black and white colours.
    browser_style : {``'buttons'``, ``'slider'``}, optional
        It defines whether the selector of the objects will have the form of
        plus/minus buttons or a slider.
    """
    print('Initializing...')

    # Make sure that images is a list even with one image member
    if not isinstance(images, Sized):
        images = [images]

    # Get the number of images
    n_images = len(images)

    # Define the styling options
    if style == 'coloured':
        logo_style = 'info'
        widget_box_style = 'info'
        widget_border_radius = 10
        widget_border_width = 1
        animation_style = 'info'
        channels_style = 'danger'
        landmarks_style = 'danger'
        info_style = 'danger'
        renderer_style = 'danger'
        renderer_tabs_style = 'danger'
        save_figure_style = 'danger'
    else:
        logo_style = 'minimal'
        widget_box_style = ''
        widget_border_radius = 0
        widget_border_width = 0
        channels_style = 'minimal'
        landmarks_style = 'minimal'
        animation_style = 'minimal'
        info_style = 'minimal'
        renderer_style = 'minimal'
        renderer_tabs_style = 'minimal'
        save_figure_style = 'minimal'

    # Define render function
    def render_function(name, value):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # get selected index
        im = 0
        if n_images > 1:
            im = image_number_wid.selected_values

        # update info text widget
        image_is_masked = isinstance(images[im], MaskedImage)
        selected_group = landmark_options_wid.selected_values['group']
        update_info(images[im], image_is_masked, selected_group)

        # show landmarks with selected options
        tmp1 = renderer_options_wid.selected_values['lines']
        tmp2 = renderer_options_wid.selected_values['markers']
        options = renderer_options_wid.selected_values['numbering']
        options.update(renderer_options_wid.selected_values['legend'])
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
        if images[im].has_landmarks:
            for lbl in landmark_options_wid.selected_values['with_labels']:
                lbl_idx = images[im].landmarks[selected_group].labels.index(lbl)
                line_colour.append(tmp1['line_colour'][lbl_idx])
                marker_face_colour.append(tmp2['marker_face_colour'][lbl_idx])
                marker_edge_colour.append(tmp2['marker_edge_colour'][lbl_idx])

        # show image with selected options
        renderer = render_image(
            image=images[im], renderer=save_figure_wid.renderer,
            image_is_masked=image_is_masked,
            render_lines=tmp1['render_lines'], line_style=tmp1['line_style'],
            line_width=tmp1['line_width'], line_colour=line_colour,
            render_markers=tmp2['render_markers'],
            marker_style=tmp2['marker_style'],
            marker_size=tmp2['marker_size'],
            marker_edge_width=tmp2['marker_edge_width'],
            marker_edge_colour=marker_edge_colour,
            marker_face_colour=marker_face_colour,
            figure_size=new_figure_size, **options)

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Define function that updates the info text
    def update_info(img, image_is_masked, group):
        # Prepare masked (or non-masked) string
        masked_str = 'Masked Image' if image_is_masked else 'Image'
        # Get image path, if available
        path_str = img.path if hasattr(img, 'path') else 'No path available'
        # Create text lines
        text_per_line = [
            "> {} of size {} with {} channel{}".format(
                masked_str, img._str_shape(), img.n_channels,
                's' * (img.n_channels > 1)),
            "> Path: '{}'".format(path_str)]
        n_lines = 2
        if image_is_masked:
            text_per_line.append(
                "> {} masked pixels (attached mask {:.1%} true)".format(
                    img.n_true_pixels(), img.mask.proportion_true()))
            n_lines += 1
        text_per_line.append("> min={:.3f}, max={:.3f}".format(
            img.pixels.min(), img.pixels.max()))
        n_lines += 1
        if img.has_landmarks:
            text_per_line.append("> {} landmark points".format(
                img.landmarks[group].lms.n_points))
            n_lines += 1
        info_wid.set_widget_state(n_lines=n_lines, text_per_line=text_per_line)

    # Create widgets
    groups_keys, labels_keys = extract_groups_labels_from_image(images[0])
    channel_options_wid = ChannelOptionsWidget(
        n_channels=images[0].n_channels,
        image_is_masked=isinstance(images[0], MaskedImage),
        render_function=render_function, style=channels_style)
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=['markers', 'lines', 'numbering', 'legend', 'zoom_one',
                      'axes', 'image'], labels=labels_keys[0],
        axes_x_limits=None, axes_y_limits=None,
        render_function=render_function,  style=renderer_style,
        tabs_style=renderer_tabs_style)
    landmark_options_wid = LandmarkOptionsWidget(
        group_keys=groups_keys, labels_keys=labels_keys,
        render_function=render_function, style=landmarks_style,
        renderer_widget=renderer_options_wid)
    info_wid = TextPrintWidget(n_lines=1, text_per_line=[''],
                               style=info_style)
    save_figure_wid = SaveFigureOptionsWidget(renderer=None,
                                              style=save_figure_style)

    # Group widgets
    if n_images > 1:
        # Define function that updates options' widgets state
        def update_widgets(name, value):
            # Get new groups and labels, then update landmark options
            im = image_number_wid.selected_values
            group_keys, labels_keys = extract_groups_labels_from_image(
                images[im])

            # Update landmarks options
            landmark_options_wid.set_widget_state(
                group_keys=group_keys, labels_keys=labels_keys,
                allow_callback=False)
            landmark_options_wid.predefined_style(landmarks_style)

            # Update channels options
            channel_options_wid.set_widget_state(
                n_channels=images[im].n_channels,
                image_is_masked=isinstance(images[im], MaskedImage),
                allow_callback=True)

        # Image selection slider
        index = {'min': 0, 'max': n_images-1, 'step': 1, 'index': 0}
        image_number_wid = AnimationOptionsWidget(
            index, render_function=update_widgets, index_style=browser_style,
            interval=0.2, description='Image', loop_enabled=True,
            continuous_update=False, style=animation_style)

        # Header widget
        header_wid = ipywidgets.HBox(
            children=[LogoWidget(style=logo_style), image_number_wid],
            align='start')
    else:
        # Header widget
        header_wid = LogoWidget(style=logo_style)
    header_wid.margin = '0.2cm'
    options_box = ipywidgets.Tab(
        children=[info_wid, channel_options_wid, landmark_options_wid,
                  renderer_options_wid, save_figure_wid], margin='0.2cm')
    tab_titles = ['Info', 'Channels', 'Landmarks', 'Renderer', 'Export']
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    if n_images > 1:
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

    # Reset value to trigger initial visualization
    renderer_options_wid.options_widgets[3].render_legend_checkbox.value = False


def visualize_patches(patches, patch_centers, figure_size=(10, 8),
                      style='coloured', browser_style='buttons'):
    r"""
    Widget that allows browsing through a `list` of patch-based images.

    The patches argument can have any of the two formats that are returned from
    the `extract_patches()` and `extract_patches_around_landmarks()` methods.
    Specifically it can be:

        1. ``(n_center, n_offset, self.n_channels, patch_shape)`` `ndarray`
        2. `list` of ``n_center * n_offset`` :map:`Image` objects

    The patches can have a combination of different attributes, e.g. number of
    centers, number of offsets, number of channels etc. The widget has options
    tabs regarding the visualized patches, channels, the renderer (lines,
    markers, numbering, figure, axes, image) and saving the figure to file.

    Parameters
    ----------
    patches : `list`
        The `list` of patch-based images to be visualized. It can consist of
        objects with any of the two formats that are returned from the
        `extract_patches()` and `extract_patches_around_landmarks()` methods.
        Specifically, it can either be an
        ``(n_center, n_offset, self.n_channels, patch_shape)`` `ndarray` or a
        `list` of ``n_center * n_offset`` :map:`Image` objects.
    patch_centers : `list` of :map:`PointCloud`
        The centers to set the patches around. If the `list` has only one
        :map:`PointCloud` then this will be used for all patches members.
        Otherwise, it needs to have the same length as patches.
    figure_size : (`int`, `int`), optional
        The initial size of the rendered figure.
    style : {``'coloured'``, ``'minimal'``}, optional
        If ``'coloured'``, then the style of the widget will be coloured. If
        ``minimal``, then the style is simple using black and white colours.
    browser_style : {``'buttons'``, ``'slider'``}, optional
        It defines whether the selector of the objects will have the form of
        plus/minus buttons or a slider.
    """
    print('Initializing...')

    # Make sure that patches is a list even with one patches member
    if (isinstance(patches, list) and isinstance(patches[0], Image)) or \
            not isinstance(patches, list):
        patches = [patches]

    # Make sure that patch_centers is a list even with one pointcloud
    if not isinstance(patch_centers, list):
        patch_centers = [patch_centers] * len(patches)
    elif isinstance(patch_centers, list) and len(patch_centers) == 1:
        patch_centers *= len(patches)

    # Make sure all patch-based images are in the single array format
    for i in range(len(patches)):
        if isinstance(patches[i], list):
            patches[i] = _convert_patches_list_to_single_array(
                patches[i], patch_centers[i].n_points)

    # Get the number of patch_based images
    n_patches = len(patches)

    # Define the styling options
    if style == 'coloured':
        logo_style = 'warning'
        widget_box_style = 'warning'
        widget_border_radius = 10
        widget_border_width = 1
        animation_style = 'warning'
        channels_style = 'info'
        patches_style = 'minimal'
        patches_subwidgets_style = 'danger'
        info_style = 'info'
        renderer_style = 'info'
        renderer_tabs_style = 'minimal'
        save_figure_style = 'danger'
    else:
        logo_style = 'minimal'
        widget_box_style = ''
        widget_border_radius = 0
        widget_border_width = 0
        channels_style = 'minimal'
        patches_style = 'minimal'
        patches_subwidgets_style = 'minimal'
        animation_style = 'minimal'
        info_style = 'minimal'
        renderer_style = 'minimal'
        renderer_tabs_style = 'minimal'
        save_figure_style = 'minimal'

    # Define render function
    def render_function(name, value):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # get selected index
        im = 0
        if n_patches > 1:
            im = image_number_wid.selected_values

        # update info text widget
        update_info(patches[im])

        # show patch-based image with selected options
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
            patches=patches[im], patch_centers=patch_centers[im],
            renderer=save_figure_wid.renderer, figure_size=new_figure_size,
            channels=channel_options_wid.selected_values['channels'],
            glyph_enabled=channel_options_wid.selected_values['glyph_enabled'],
            glyph_block_size=channel_options_wid.selected_values['glyph_block_size'],
            glyph_use_negative=channel_options_wid.selected_values['glyph_use_negative'],
            sum_enabled=channel_options_wid.selected_values['sum_enabled'],
            **options)

        # Save the current figure id
        save_figure_wid.renderer = renderer

    # Define function that updates the info text
    def update_info(ptchs):
        text_per_line = [
            "> Patch-Based Image with {} patche{} and {} offset{}.".format(
                ptchs.shape[0], 's' * (ptchs.shape[0] > 1), ptchs.shape[1],
                                's' * (ptchs.shape[1] > 1)),
            "> Each patch has size {}H x {}W with {} channel{}.".format(
                ptchs.shape[3], ptchs.shape[4], ptchs.shape[2],
                's' * (ptchs.shape[2] > 1)),
            "> min={:.3f}, max={:.3f}".format(ptchs.min(), ptchs.max())]
        info_wid.set_widget_state(n_lines=len(text_per_line),
                                  text_per_line=text_per_line)

    # Create widgets
    patch_options_wid = PatchOptionsWidget(
        n_patches=patches[0].shape[0], n_offsets=patches[0].shape[1],
        render_function=render_function, style=patches_style,
        subwidgets_style=patches_subwidgets_style)
    channel_options_wid = ChannelOptionsWidget(
        n_channels=patches[0].shape[2], image_is_masked=False,
        render_function=render_function, style=channels_style)
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=['markers', 'lines', 'numbering', 'zoom_one', 'axes',
                      'image'], labels=None,
        axes_x_limits=0., axes_y_limits=None,
        render_function=render_function,  style=renderer_style,
        tabs_style=renderer_tabs_style)
    info_wid = TextPrintWidget(n_lines=3, text_per_line=[''] * 3,
                               style=info_style)
    save_figure_wid = SaveFigureOptionsWidget(renderer=None,
                                              style=save_figure_style)

    # Group widgets
    if n_patches > 1:
        # Define function that updates options' widgets state
        def update_widgets(name, value):
            # Get new groups and labels, then update landmark options
            im = 0
            if n_patches > 1:
                im = image_number_wid.selected_values

            # Update patch options
            patch_options_wid.set_widget_state(
                n_patches=patches[im].shape[0], n_offsets=patches[im].shape[1],
                allow_callback=False)

            # Update channels options
            channel_options_wid.set_widget_state(
                n_channels=patches[im].shape[2], image_is_masked=False,
                allow_callback=True)

        # Image selection slider
        index = {'min': 0, 'max': n_patches-1, 'step': 1, 'index': 0}
        image_number_wid = AnimationOptionsWidget(
            index, render_function=update_widgets, index_style=browser_style,
            interval=0.2, description='Image', loop_enabled=True,
            continuous_update=False, style=animation_style)

        # Header widget
        header_wid = ipywidgets.HBox(
            children=[LogoWidget(style=logo_style), image_number_wid],
            align='start')
    else:
        # Header widget
        header_wid = LogoWidget(style=logo_style)
    header_wid.margin = '0.2cm'
    options_box = ipywidgets.Tab(
        children=[info_wid, patch_options_wid, channel_options_wid,
                  renderer_options_wid, save_figure_wid], margin='0.2cm')
    tab_titles = ['Info', 'Patches', 'Channels', 'Renderer', 'Export']
    for (k, tl) in enumerate(tab_titles):
        options_box.set_title(k, tl)
    if n_patches > 1:
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

    # Reset value to trigger initial visualization
    renderer_options_wid.options_widgets[4].axes_limits_widget.\
        axes_x_limits_toggles.value = 'auto'


def plot_graph(x_axis, y_axis, legend_entries=None, figure_size=(10, 6),
               style='coloured'):
    r"""
    Widget that allows plotting various curves in a graph using
    :map:`GraphPlotter`.

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
    title : `str` or ``None``, optional
        The title of the graph.
    x_label : `str` or ``None``, optional
        The label on the horizontal axis of the graph.
    y_label : `str` or ``None``, optional
        The label on the vertical axis of the graph.
    x_axis_limits : (`float`, `float`) or ``None``, optional
        The limits of the horizontal axis. If ``None``, the limits are set
        based on the min and max values of `x_axis`.
    y_axis_limits : (`float`, `float`), optional
        The limits of the vertical axis. If ``None``, the limits are set based
        on the min and max values of `y_axis`.
    figure_size : (`int`, `int`), optional
        The initial size of the rendered figure.
    style : {``'coloured'``, ``'minimal'``}, optional
        If ``'coloured'``, then the style of the widget will be coloured. If
        ``minimal``, then the style is simple using black and white colours.
    """
    from menpo.visualize import plot_curve
    print('Initializing...')

    # Get number of curves to be plotted
    n_curves = len(y_axis)

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
        legend_entries = ["curve {}".format(i) for i in range(n_curves)]

    # Define render function
    def render_function(name, value):
        # Clear current figure, but wait until the generation of the new data
        # that will be rendered
        ipydisplay.clear_output(wait=True)

        # plot with selected options
        opts = wid.selected_values.copy()
        new_figure_size = (
            wid.selected_values['zoom'][0] * figure_size[0],
            wid.selected_values['zoom'][1] * figure_size[1])
        del opts['zoom']
        renderer = plot_curve(
            x_axis=x_axis, y_axis=y_axis, figure_size=new_figure_size,
            figure_id=save_figure_wid.renderer.figure_id, new_figure=False,
            **opts)

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

    # Reset value to trigger initial visualization
    wid.title.value = ' '


def save_matplotlib_figure(renderer, style='coloured'):
    r"""
    Widget that allows to save a figure, which was generated with Matplotlib,
    to file.

    Parameters
    ----------
    renderer : :map:`MatplotlibRenderer`
        The Matplotlib renderer object.
    style : {``'coloured'``, ``'minimal'``}, optional
        If ``'coloured'``, then the style of the widget will be coloured. If
        ``minimal``, then the style is simple using black and white colours.
    """
    # Create sub-widgets
    if style == 'coloured':
        style = 'warning'
    logo_wid = LogoWidget(style='minimal')
    save_figure_wid = SaveFigureOptionsWidget(renderer, style=style)
    save_figure_wid.margin = '0.1cm'
    logo_wid.margin = '0.1cm'
    wid = ipywidgets.HBox(children=[logo_wid, save_figure_wid])

    # Display widget
    ipydisplay.display(wid)


def features_selection(style='coloured'):
    r"""
    Widget that allows selecting a features function and its options. The
    widget supports all features from :ref:`api-feature-index` and has a
    preview tab. It returns a `list` of length 1 with the selected features
    function closure.

    Parameters
    ----------
    style : {``'coloured'``, ``'minimal'``}, optional
        If ``'coloured'``, then the style of the widget will be coloured. If
        ``minimal``, then the style is simple using black and white colours.

    Returns
    -------
    features_function : `list` of length ``1``
        The function closure of the features function using `functools.partial`.
        So the function can be called as: ::

            features_image = features_function[0](image)

    """
    # Styling options
    if style == 'coloured':
        logo_style = 'info'
        outer_style = 'info'
        inner_style = 'warning'
        but_style = 'primary'
        rad = 10
    elif style == 'minimal':
        logo_style = 'minimal'
        outer_style = ''
        inner_style = 'minimal'
        but_style = ''
        rad = 0
    else:
        raise ValueError('style must be either coloured or minimal')

    # Create sub-widgets
    logo_wid = LogoWidget(style=logo_style)
    features_options_wid = FeatureOptionsWidget(style=inner_style)
    select_but = ipywidgets.Button(description='Select')
    features_wid = ipywidgets.VBox(children=[features_options_wid, select_but],
                                   align='center')

    # Create final widget
    wid = ipywidgets.HBox(children=[logo_wid, features_wid])
    format_box(wid, outer_style, True,
               map_styles_to_hex_colours(outer_style), 'solid', 1, rad, 0, 0)
    logo_wid.margin = '0.3cm'
    features_options_wid.margin = '0.3cm'
    select_but.margin = '0.2cm'
    select_but.button_style = but_style

    # function for select button
    def select_function(name):
        wid.close()
        output.pop(0)
        output.append(features_options_wid.function)
    select_but.on_click(select_function)

    # Display widget
    ipydisplay.display(wid)

    # Initialize output with empty list. It needs to be a list so that
    # it's mutable and synchronizes with frontend.
    output = [features_options_wid.function]

    return output
