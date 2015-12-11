from collections import Sized
import matplotlib.pyplot as plt

import ipywidgets
import IPython.display as ipydisplay

from .options import (RendererOptionsWidget, TextPrintWidget,
                      SaveFigureOptionsWidget, AnimationOptionsWidget,
                      LandmarkOptionsWidget, ChannelOptionsWidget,
                      FeatureOptionsWidget, PlotOptionsWidget,
                      PatchOptionsWidget)
from .style import format_box, map_styles_to_hex_colours
from .tools import LogoWidget
from .utils import extract_group_labels_landmarks


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
        labels=None, render_function=render_function, style=renderer_style,
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
    for w in renderer_options_wid.options_widgets:
        w.border_width = 0

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
        value=2)
    axes_mode_wid.on_trait_change(render_function, 'value')
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=['lines', 'markers', 'numbering', 'legend', 'zoom_one',
                      'axes'], labels=landmarkgroups[0].labels,
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
    for w in renderer_options_wid.options_widgets:
        w.border_width = 0

    # Display final widget
    ipydisplay.display(wid)

    # Reset value to trigger initial visualization
    axes_mode_wid.value = 1


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

        if landmark_options_wid.selected_values['render_landmarks']:
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
        if group != ' ':
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
    groups_keys, labels_keys = extract_group_labels_landmarks(landmarks[0])
    landmark_options_wid = LandmarkOptionsWidget(
        group_keys=groups_keys, labels_keys=labels_keys,
        render_function=render_function, style=landmarks_style)
    axes_mode_wid = ipywidgets.RadioButtons(
        options={'Image': 1, 'Point cloud': 2}, description='Axes mode:',
        value=2)
    axes_mode_wid.on_trait_change(render_function, 'value')
    renderer_options_wid = RendererOptionsWidget(
        options_tabs=['lines', 'markers', 'numbering', 'legend', 'zoom_one',
                      'axes'], labels=labels_keys[0],
        render_function=render_function,  style=renderer_style,
        tabs_style=renderer_tabs_style)
    renderer_options_box = ipywidgets.VBox(
        children=[axes_mode_wid, renderer_options_wid], align='center',
        margin='0.1cm')
    info_wid = TextPrintWidget(n_lines=5, text_per_line=[''] * 5,
                               style=info_style)
    save_figure_wid = SaveFigureOptionsWidget(renderer=None,
                                              style=save_figure_style)

    # Define function that updates renderer options
    def update_renderer_options(name, value):
        group_idx = landmark_options_wid.group_keys.index(
            landmark_options_wid.group_dropdown.value)
        labels = landmark_options_wid.labels_keys[group_idx]
        renderer_options_wid.set_widget_state(labels=labels,
                                              allow_callback=False)
    landmark_options_wid.group_dropdown.on_trait_change(
        update_renderer_options, 'update_renderer_options')

    # Group widgets
    if n_landmarks > 1:
        # Define function that updates options' widgets state
        def update_widgets(name, value):
            # Get new groups and labels
            im = landmark_number_wid.selected_values
            group_keys, labels_keys = extract_group_labels_landmarks(
                landmarks[im])

            # Update landmarks options
            landmark_options_wid.set_widget_state(
                group_keys=group_keys, labels_keys=labels_keys,
                allow_callback=False)
            landmark_options_wid.predefined_style(landmarks_style)

            # Update renderer
            update_renderer_options('', None)

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
    for w in renderer_options_wid.options_widgets:
        w.border_width = 0

    # Display final widget
    ipydisplay.display(wid)

    # Reset value to trigger initial visualization
    axes_mode_wid.value = 1
