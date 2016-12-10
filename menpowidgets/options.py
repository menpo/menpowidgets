import ipywidgets
from IPython.display import display, Javascript
from traitlets.traitlets import Int, Dict, List
from traitlets import link
from collections import OrderedDict
import numpy as np
from base64 import b64decode

from menpo.compatibility import unicode

from .abstract import MenpoWidget
from .tools import (IndexSliderWidget, IndexButtonsWidget, SlicingCommandWidget,
                    LineMatplotlibOptionsWidget, MarkerMatplotlibOptionsWidget,
                    LineMayaviOptionsWidget, MarkerMayaviOptionsWidget,
                    LogoWidget, NumberingMatplotlibOptionsWidget,
                    NumberingMayaviOptionsWidget, LegendOptionsWidget,
                    ZoomOneScaleWidget, ZoomTwoScalesWidget, AxesOptionsWidget,
                    GridOptionsWidget, ImageMatplotlibOptionsWidget,
                    CameraWidget, ColourSelectionWidget, TriMeshOptionsWidget,
                    TexturedTriMeshOptionsWidget, SwitchWidget,
                    MultipleSelectionTogglesWidget)
from .style import (map_styles_to_hex_colours, format_box, format_font,
                    format_slider)
from .utils import sample_colours_from_colourmap, lists_are_the_same


class AnimationOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for animating through a list of objects.

    Note that:

    * The selected values are stored in the ``self.selected_values`` `trait`.
    * To update the state of the widget, please refer to the
      :meth:`set_widget_state` method.
    * To update the handler callback function of the widget, please refer to the
      :meth:`replace_render_function` method.
    * To set the styling of this widget please refer to the
      :meth:`predefined_style` method.

    Parameters
    ----------
    index : `dict`
        The initial options. It must be a `dict` with the following keys:

        * ``min`` : (`int`) The minimum value (e.g. ``0``).
        * ``max`` : (`int`) The maximum value (e.g. ``100``).
        * ``step`` : (`int`) The index step (e.g. ``1``).
        * ``index`` : (`int`) The index value (e.g. ``10``).

    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        It must have signature ``render_function(change)`` where ``change`` is
        a `dict` with the following keys:

        * ``type`` : The type of notification (normally ``'change'``).
        * ``owner`` : the `HasTraits` instance
        * ``old`` : the old value of the modified trait attribute
        * ``new`` : the new value of the modified trait attribute
        * ``name`` : the name of the modified trait attribute.

        If ``None``, then nothing is assigned.
    index_style : ``{'buttons', 'slider'}``, optional
        If ``'buttons'``, then :map:`IndexButtonsWidget` class is called. If
        ``'slider'``, then :map:`IndexSliderWidget` class is called.
    interval : `float`, optional
        The interval between the animation progress in seconds.
    interval_step : `float`, optional
        The interval step (in seconds) that is applied when fast
        forward/backward buttons are pressed.
    description : `str`, optional
        The title of the widget.
    loop_enabled : `bool`, optional
        If ``True``, then after reach the minimum (maximum) index values, the
        counting will continue from the end (beginning). If ``False``, the
        counting will stop at the minimum (maximum) value.
    continuous_update : `bool`, optional
        If ``True`` and `index_style` is set to ``'slider'``, then the render
        and update functions are called while moving the slider's handle. If
        ``False``, then the the functions are called only when the handle
        (mouse click) is released.
    style : `str` (see below), optional
        Sets a predefined style at the widget. Possible options are:

            ============= ============================
            Style         Description
            ============= ============================
            ``'success'`` Green-based style
            ``'info'``    Blue-based style
            ``'warning'`` Yellow-based style
            ``'danger'``  Red-based style
            ``''``        No style
            ============= ============================

    Example
    -------
    Let's create an animation widget and then update its state. Firstly, we need
    to import it:

        >>> from menpowidgets.options import AnimationOptionsWidget

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected index:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(change):
        >>>     s = "Selected index: {}".format(wid.selected_values)
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> index = {'min': 0, 'max': 100, 'step': 1, 'index': 10}
        >>> wid = AnimationOptionsWidget(index, index_style='buttons',
        >>>                              render_function=render_function,
        >>>                              style='info')
        >>> wid

    By pressing the buttons (or simply pressing the Play button), the printed
    message gets updated. Finally, let's change the widget status with a new
    dictionary of options:

        >>> new_options = {'min': 0, 'max': 20, 'step': 2, 'index': 16}
        >>> wid.set_widget_state(new_options, allow_callback=False)
    """
    def __init__(self, index, render_function=None, index_style='buttons',
                 interval=0.2, interval_step=0.05, description='Index',
                 loop_enabled=True, continuous_update=False, style=''):
        from time import sleep
        from IPython import get_ipython

        # Get the kernel to use it later in order to make sure that the widgets'
        # traits changes are passed during a while-loop
        kernel = get_ipython().kernel

        self._toggle_play_style = '' if style == '' else 'success'
        self._toggle_stop_style = '' if style == '' else 'danger'

        # Create index widget
        if index_style == 'slider':
            self.index_wid = IndexSliderWidget(
                index, description=description,
                continuous_update=continuous_update)
        elif index_style == 'buttons':
            self.index_wid = IndexButtonsWidget(
                index, description=description, minus_description='fa-minus',
                plus_description='fa-plus', loop_enabled=loop_enabled,
                text_editable=True)
        else:
            raise ValueError('index_style should be either slider or buttons')

        # Create other widgets
        self.play_stop_toggle = ipywidgets.ToggleButton(
            icon='fa-play', description='', value=False,
            tooltip='Play animation')
        self.fast_forward_button = ipywidgets.Button(
            icon='fa-fast-forward', description='',
            tooltip='Increase animation speed')
        self.fast_backward_button = ipywidgets.Button(
            icon='fa-fast-backward', description='',
            tooltip='Decrease animation speed')
        loop_icon = 'fa-repeat' if loop_enabled else 'fa-long-arrow-right'
        self.loop_toggle = ipywidgets.ToggleButton(
            icon=loop_icon, description='', value=loop_enabled,
            tooltip='Repeat animation')
        self.play_stop_toggle.layout.width = '40px'
        self.fast_forward_button.layout.width = '40px'
        self.fast_backward_button.layout.width = '40px'
        self.loop_toggle.layout.width = '40px'

        # Group widgets
        self.box_1 = ipywidgets.HBox([self.play_stop_toggle, self.loop_toggle,
                                      self.fast_backward_button,
                                      self.fast_forward_button])
        self.box_1.layout.align_items = 'center'
        self.box_1.layout.margin = '0px 0px 0px 10px'
        self.container = ipywidgets.HBox([self.index_wid, self.box_1])
        self.container.layout.align_items = 'flex-start'

        # Assign properties
        self.min = index['min']
        self.max = index['max']
        self.step = index['step']
        self.loop_enabled = loop_enabled
        self.index_style = index_style
        self.continuous_update = continuous_update
        self.interval = interval
        self.interval_step = interval_step

        # Set style
        self.predefined_style(style)

        # Create final widget
        super(AnimationOptionsWidget, self).__init__(
            [self.container], Int, index['index'],
            render_function=render_function)

        # Set functionality
        def play_stop_pressed(change):
            value = change['new']
            if value:
                # Animation was not playing, so Play was pressed.
                # Change the button style
                self.play_stop_toggle.button_style = self._toggle_stop_style
                # Change the icon and tooltip to Stop
                self.play_stop_toggle.icon = 'fa-stop'
                self.play_stop_toggle.tooltip = 'Stop animation'
                # Disable index widget
                if self.index_style == 'buttons':
                    self.index_wid.index_text.disabled = True
                    self.index_wid.button_plus.disabled = True
                    self.index_wid.button_minus.disabled = True
                else:
                    self.index_wid.slider.disabled = True
                    self.index_wid.slider_text.disabled = True
            else:
                # Animation was playing, so Stop was pressed.
                # Change the button style
                self.play_stop_toggle.button_style = self._toggle_play_style
                # Change the icon and tooltip to Play
                self.play_stop_toggle.icon = 'fa-play'
                self.play_stop_toggle.tooltip = 'Play animation'
                # Enable index widget
                if self.index_style == 'buttons':
                    self.index_wid.index_text.disabled = False
                    self.index_wid.button_plus.disabled = False
                    self.index_wid.button_minus.disabled = False
                else:
                    self.index_wid.slider.disabled = False
                    self.index_wid.slider_text.disabled = False
        self.play_stop_toggle.observe(play_stop_pressed, names='value',
                                      type='change')

        def loop_pressed(change):
            if change['new']:
                self.loop_toggle.icon = 'fa-repeat'
            else:
                self.loop_toggle.icon = 'fa-long-arrow-right'
            kernel.do_one_iteration()
        self.loop_toggle.observe(loop_pressed, names='value', type='change')

        def fast_forward_pressed(name):
            tmp = self.interval
            tmp -= self.interval_step
            if tmp < 0:
                tmp = 0
            self.interval = tmp
            kernel.do_one_iteration()
        self.fast_forward_button.on_click(fast_forward_pressed)

        def fast_backward_pressed(name):
            self.interval += self.interval_step
            kernel.do_one_iteration()
        self.fast_backward_button.on_click(fast_backward_pressed)

        def animate(change):
            i = self.selected_values
            if self.loop_toggle.value and i >= self.max:
                i = self.min
            else:
                i += self.step
            while i <= self.max and self.play_stop_toggle.value:
                # update index value
                if index_style == 'slider':
                    self.index_wid.slider.value = i
                else:
                    self.index_wid.set_widget_state(
                        {'min': self.min, 'max': self.max, 'step': self.step,
                         'index': i},
                        loop_enabled=self.loop_enabled, text_editable=False,
                        allow_callback=True)

                # Run IPython iteration.
                # This is the code that makes this operation non-blocking.
                # This allows widget messages and callbacks to be processed.
                kernel.do_one_iteration()

                # update counter
                if self.loop_toggle.value and i >= self.max:
                    i = self.min
                else:
                    i += self.step
                # wait
                sleep(self.interval)
            if not self.loop_toggle.value and i > self.max:
                self.stop_animation()
        self.play_stop_toggle.observe(animate, names='value', type='change')

        def save_value(change):
            self.selected_values = self.index_wid.selected_values
        self.index_wid.observe(save_value, names='selected_values',
                               type='change')

    def predefined_style(self, style):
        r"""
        Sets a predefined style to the widget.

        Parameters
        ----------
        style : `str` (see below)
            Possible options are:

                ============= ============================
                Style         Description
                ============= ============================
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ============================

        """
        self.container.box_style = style
        if style != '':
            self.play_stop_toggle.button_style = self._toggle_play_style
            self.fast_forward_button.button_style = 'info'
            self.fast_backward_button.button_style = 'info'
            self.loop_toggle.button_style = 'warning'
            if self.index_style == 'buttons':
                self.index_wid.button_plus.button_style = 'primary'
                self.index_wid.button_minus.button_style = 'primary'
            else:
                self.index_wid.slider.slider_color = \
                    map_styles_to_hex_colours(style, False)
        else:
            self.play_stop_toggle.button_style = ''
            self.fast_forward_button.button_style = ''
            self.fast_backward_button.button_style = ''
            self.loop_toggle.button_style = ''
            if self.index_style == 'buttons':
                self.index_wid.button_plus.button_style = ''
                self.index_wid.button_minus.button_style = ''
            else:
                self.index_wid.slider.slider_color = \
                    map_styles_to_hex_colours('', False)

    def set_widget_state(self, index, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided `index`
        values are different than `self.selected_values`.

        Parameters
        ----------
        index : `dict`
            The selected options. It must be a `dict` with the following keys:

            * ``min`` : (`int`) The minimum value (e.g. ``0``).
            * ``max`` : (`int`) The maximum value (e.g. ``100``).
            * ``step`` : (`int`) The index step (e.g. ``1``).
            * ``index`` : (`int`) The index value (e.g. ``10``).

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Keep old value
        old_value = self.selected_values

        # Check if update is required
        if (index['index'] != self.selected_values or
                    index['min'] != self.min or
                    index['max'] != self.max or
                    index['step'] != self.step):
            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            if self.play_stop_toggle.value:
                self.stop_animation()
            if self.index_style == 'slider':
                self.index_wid.set_widget_state(index, allow_callback=False)
            else:
                self.index_wid.set_widget_state(
                    index, loop_enabled=self.loop_toggle.value,
                    text_editable=True, allow_callback=False)
            self.selected_values = index['index']
            self.min = index['min']
            self.max = index['max']
            self.step = index['step']

            # re-assign render callback
            self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self.call_render_function(old_value, self.selected_values)

    def stop_animation(self):
        r"""
        Method that stops an active annotation by setting
        ``self.play_stop_toggle.value = False``.
        """
        self.play_stop_toggle.value = False


class Shape2DOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting options for 2D shapes,
    i.e. `menpo.shape.PointCloud`, `menpo.shape.PointGraph`,
    `menpo.shape.LabelledPointGraph` and `menpo.shape.TriMesh`.

    Note that:

    * The selected values are stored in the ``self.selected_values`` `trait`.
    * To update the state of the widget, please refer to the
      :meth:`set_widget_state` method.
    * To update the handler callback function of the widget, please refer to the
      :meth:`replace_render_function` method.
    * To set the styling of this widget please refer to the
      :meth:`predefined_style` method.

    Parameters
    ----------
    labels : `list` or ``None``
        The `list` of labels. If ``None``, then it is assumed that there are
        no labels.
    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        It must have signature ``render_function(change)`` where ``change`` is
        a `dict` with the following keys:

        * ``type`` : The type of notification (normally ``'change'``).
        * ``owner`` : the `HasTraits` instance
        * ``old`` : the old value of the modified trait attribute
        * ``new`` : the new value of the modified trait attribute
        * ``name`` : the name of the modified trait attribute.

        If ``None``, then nothing is assigned.
    style : `str` (see below), optional
        Sets a predefined style at the widget. Possible options are:

            ============= ============================
            Style         Description
            ============= ============================
            ``'success'`` Green-based style
            ``'info'``    Blue-based style
            ``'warning'`` Yellow-based style
            ``'danger'``  Red-based style
            ``''``        No style
            ============= ============================

    suboptions_style : `str` (see below), optional
        Sets a predefined style at the widget's suboptions. Possible options
        are:

            ============= ============================
            Style         Description
            ============= ============================
            ``'success'`` Green-based style
            ``'info'``    Blue-based style
            ``'warning'`` Yellow-based style
            ``'danger'``  Red-based style
            ``''``        No style
            ============= ============================

    Example
    -------
    Let's create a shape options widget and then update its state. Firstly,
    we need to import it:

        >>> from menpowidgets.options import Shape2DOptionsWidget

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected index:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(change):
        >>>     s = "Selected index: {}".format(wid.selected_values)
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> labels = ['jaw', 'left_eye', 'right_eye', 'mouth', 'nose']
        >>> wid = Shape2DOptionsWidget(labels, render_function=render_function,
        >>>                            style='danger',
        >>>                            suboptions_style='warning')
        >>> wid

    By pressing the buttons you can select various labels. Markers and lines
    options are also available. Finally, let's change the widget status with a
    new dictionary of options:

        >>> labels = None
        >>> wid.set_widget_state(labels, allow_callback=False)
    """
    def __init__(self, labels, render_function=None, style='',
                 suboptions_style=''):
        # Initialize default options dictionary
        self.default_options = {}

        # Assign properties
        self.labels = labels

        # Get initial options
        renderer_options = self.get_default_options(labels)

        # Create widgets
        self.image_view_switch = SwitchWidget(
            selected_value=renderer_options['image_view'],
            description='Image coordinates', description_location='right',
            switch_type='checkbox')
        self.image_view_switch.layout.margin = '7px'
        self.line_options_wid = LineMatplotlibOptionsWidget(
            renderer_options['lines'], render_function=None,
            render_checkbox_title='Render lines', labels=labels)
        self.marker_options_wid = MarkerMatplotlibOptionsWidget(
            renderer_options['markers'], render_function=None,
            render_checkbox_title='Render markers', labels=labels)
        self.buttons_style = ''
        if style != '' or suboptions_style != '':
            self.buttons_style = 'primary'
        if labels is not None:
            self.labels_options_wid = MultipleSelectionTogglesWidget(
                labels=labels, with_labels=renderer_options['with_labels'],
                render_function=None, description='Labels',
                buttons_style=self.buttons_style)
        else:
            self.labels_options_wid = MultipleSelectionTogglesWidget(
                labels=[' '], with_labels=None, render_function=None,
                description='Labels', buttons_style=self.buttons_style)
        self.labels_options_wid.layout.margin = '0px 0px 10px 0px'
        self.labels_options_wid.container.layout.border = '2px solid'

        # Group widgets
        self.box_1 = ipywidgets.Tab([self.image_view_switch,
                                     self.marker_options_wid,
                                     self.line_options_wid])
        self.box_1.set_title(0, 'View')
        self.box_1.set_title(1, 'Markers')
        self.box_1.set_title(2, 'Lines')
        self.box_2 = ipywidgets.Box([self.box_1])
        self.box_2.layout.border = '2px solid'
        self.box_2.layout.display = 'table'
        self.container = ipywidgets.VBox([self.labels_options_wid, self.box_2])

        # Set style
        self.predefined_style(style, suboptions_style)

        # Call superclass
        initial_options = renderer_options.copy()
        super(Shape2DOptionsWidget, self).__init__(
            [self.container], Dict, initial_options,
            render_function=render_function)

        # Set visibility
        self._set_visibility()

        # Add callbacks
        self.add_callbacks()

    def _set_visibility(self):
        self.labels_options_wid.layout.display = (
            'none' if self.labels is None else 'flex')

    def _save_options(self, change):
        # update selected values
        self.selected_values = {
            'image_view': self.image_view_switch.selected_values,
            'lines': self.line_options_wid.selected_values,
            'markers': self.marker_options_wid.selected_values,
            'with_labels': self.labels_options_wid.selected_values}
        # update default values
        current_key = self.get_key(self.labels)
        self.default_options[current_key] = self.selected_values.copy()

    def get_key(self, labels):
        r"""
        Function that returns a unique key based on the properties of the
        provided shape object.

        Parameters
        ----------
        labels : `list` or ``None``, optional
            The `list` of labels. ``None`` if there are no labels.

        Returns
        -------
        key : `str`
            The key that has the format ``'{labels}'``.
        """
        return "{}".format(labels)

    def get_default_options(self, labels):
        r"""
        Function that returns a `dict` with default options given a `list` of
        labels. The function returns the `dict` of options but also updates the
        ``self.default_options`` `dict`.

        Parameters
        ----------
        labels : `list` or ``None``, optional
            The `list` of labels. ``None`` if there are no labels.

        Returns
        -------
        default_options : `dict`
            A `dict` with the default options.
        """
        # create key
        key = self.get_key(labels)
        # if the key does not exist in the default options dict, then add it
        if key not in self.default_options:
            self.default_options[key] = {}

            # Set image view
            self.default_options[key]['image_view'] = True

            # Set lines options
            lc = ['red']
            if labels is not None:
                lc = sample_colours_from_colourmap(len(labels), 'jet')
            self.default_options[key]['lines'] = {
                'line_colour': lc, 'render_lines': True, 'line_width': 1,
                'line_style': '-'}

            # Set markers options
            fc = ['red']
            ec = ['black']
            if labels is not None and len(labels) > 1:
                fc = sample_colours_from_colourmap(len(labels), 'jet')
                ec = sample_colours_from_colourmap(len(labels), 'jet')
            self.default_options[key]['markers'] = {
                'marker_face_colour': fc, 'marker_edge_colour': ec,
                'render_markers': True, 'marker_size': 5, 'marker_style': 'o',
                'marker_edge_width': 1}

            # Set labels
            self.default_options[key]['with_labels'] = labels
        return self.default_options[key]

    def add_callbacks(self):
        r"""
        Function that adds the handler callback functions in all the widget
        components, which are necessary for the internal functionality.
        """
        self.image_view_switch.observe(
            self._save_options, names='selected_values', type='change')
        self.line_options_wid.observe(
            self._save_options, names='selected_values', type='change')
        self.marker_options_wid.observe(
            self._save_options, names='selected_values', type='change')
        self.labels_options_wid.observe(
            self._save_options, names='selected_values', type='change')

    def remove_callbacks(self):
        r"""
        Function that removes all the internal handler callback functions.
        """
        self.image_view_switch.unobserve(
            self._save_options, names='selected_values', type='change')
        self.line_options_wid.unobserve(
            self._save_options, names='selected_values', type='change')
        self.marker_options_wid.unobserve(
            self._save_options, names='selected_values', type='change')
        self.labels_options_wid.unobserve(
            self._save_options, names='selected_values', type='change')

    def predefined_style(self, style, suboptions_style):
        r"""
        Sets a predefined style to the widget.

        Parameters
        ----------
        style : `str` (see below)
            The style of the widget. Possible options are:

                ============= ============================
                Style         Description
                ============= ============================
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ============================

        suboptions_style : `str` (see below)
            The style of the widget's sub-options. Possible options are:

                ============= ============================
                Style         Description
                ============= ============================
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ============================

        """
        self.container.box_style = style
        self.labels_options_wid.container.box_style = suboptions_style
        if suboptions_style != '' or style != '':
            self.labels_options_wid.set_buttons_style('primary')
        self.box_2.box_style = suboptions_style
        tmp = self.marker_options_wid.marker_face_colour_widget
        tmp.apply_to_all_button.button_style = suboptions_style
        tmp = self.marker_options_wid.marker_edge_colour_widget
        tmp.apply_to_all_button.button_style = suboptions_style
        tmp = self.line_options_wid.line_colour_widget
        tmp.apply_to_all_button.button_style = suboptions_style

    def set_widget_state(self, labels, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided `labels`
        are different than ``self.labels``.

        Parameters
        ----------
        labels : `list` or ``None``, optional
            The `list` of labels used in all :map:`ColourSelectionWidget` objects
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # keep old value
        old_value = self.selected_values

        # check if updates are required
        if (not self.default_options or
                self.get_key(self.labels) != self.get_key(labels)):
            # Temporarily remove callbacks
            render_function = self._render_function
            self.remove_render_function()
            self.remove_callbacks()

            # Get options
            renderer_options = self.get_default_options(labels)

            # Assign properties
            self.labels = labels

            # Set visibility
            self._set_visibility()

            # Update subwidgets
            self.image_view_switch.set_widget_state(
                renderer_options['image_view'], allow_callback=False)
            self.line_options_wid.set_widget_state(
                renderer_options['lines'], labels=labels, allow_callback=False)
            self.marker_options_wid.set_widget_state(
                renderer_options['markers'], labels=labels,
                allow_callback=False)
            if labels is not None:
                self.labels_options_wid.set_widget_state(
                    labels, with_labels=renderer_options['with_labels'],
                    allow_callback=False)
            else:
                self.labels_options_wid.set_widget_state(
                    [' '], with_labels=None, allow_callback=False)

            # Get values
            self._save_options({})

            # Add callbacks
            self.add_callbacks()
            self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self.call_render_function(old_value, self.selected_values)


class Shape3DOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting options for 3D shapes,
    i.e. `menpo.shape.PointCloud`, `menpo.shape.PointGraph`,
    and `menpo.shape.LabelledPointGraph`.

    Note that:

    * The selected values are stored in the ``self.selected_values`` `trait`.
    * To update the state of the widget, please refer to the
      :meth:`set_widget_state` method.
    * To update the handler callback function of the widget, please refer to the
      :meth:`replace_render_function` method.
    * To set the styling of this widget please refer to the
      :meth:`predefined_style` method.

    Parameters
    ----------
    labels : `list` or ``None``
        The `list` of labels. If ``None``, then it is assumed that there are
        no labels.
    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        It must have signature ``render_function(change)`` where ``change`` is
        a `dict` with the following keys:

        * ``type`` : The type of notification (normally ``'change'``).
        * ``owner`` : the `HasTraits` instance
        * ``old`` : the old value of the modified trait attribute
        * ``new`` : the new value of the modified trait attribute
        * ``name`` : the name of the modified trait attribute.

        If ``None``, then nothing is assigned.
    style : `str` (see below), optional
        Sets a predefined style at the widget. Possible options are:

            ============= ============================
            Style         Description
            ============= ============================
            ``'success'`` Green-based style
            ``'info'``    Blue-based style
            ``'warning'`` Yellow-based style
            ``'danger'``  Red-based style
            ``''``        No style
            ============= ============================

    suboptions_style : `str` (see below), optional
        Sets a predefined style at the widget's suboptions. Possible options
        are:

            ============= ============================
            Style         Description
            ============= ============================
            ``'success'`` Green-based style
            ``'info'``    Blue-based style
            ``'warning'`` Yellow-based style
            ``'danger'``  Red-based style
            ``''``        No style
            ============= ============================

    Example
    -------
    Let's create a shape options widget and then update its state. Firstly,
    we need to import it:

        >>> from menpowidgets.options import Shape3DOptionsWidget

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected index:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(change):
        >>>     s = "Selected index: {}".format(wid.selected_values)
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> labels = ['jaw', 'left_eye', 'right_eye', 'mouth', 'nose']
        >>> wid = Shape3DOptionsWidget(labels, render_function=render_function,
        >>>                            style='danger',
        >>>                            suboptions_style='warning')
        >>> wid

    By pressing the buttons you can select various labels. Markers and lines
    options are also available. Finally, let's change the widget status with a
    new dictionary of options:

        >>> labels = None
        >>> wid.set_widget_state(labels, allow_callback=False)
    """
    def __init__(self, labels, render_function=None, style='',
                 suboptions_style=''):
        # Initialize default options dictionary
        self.default_options = {}

        # Assign properties
        self.labels = labels

        # Get initial options
        renderer_options = self.get_default_options(labels)

        # Create widgets
        self.line_options_wid = LineMayaviOptionsWidget(
            renderer_options['lines'], render_function=None,
            render_checkbox_title='Render lines', labels=labels)
        self.marker_options_wid = MarkerMayaviOptionsWidget(
            renderer_options['markers'], render_function=None,
            render_checkbox_title='Render markers', labels=labels)
        self.buttons_style = ''
        if style != '':
            self.buttons_style = 'primary'
        if labels is not None:
            self.labels_options_wid = MultipleSelectionTogglesWidget(
                labels=labels, with_labels=renderer_options['with_labels'],
                render_function=None, description='Labels',
                buttons_style=self.buttons_style)
        else:
            self.labels_options_wid = MultipleSelectionTogglesWidget(
                labels=[' '], with_labels=None, render_function=None,
                description='Labels', buttons_style=buttons_style)
        self.labels_options_wid.layout.margin = '0px 0px 10px 0px'
        self.labels_options_wid.container.layout.border = '2px solid'

        # Group widgets
        self.box_1 = ipywidgets.Tab([self.marker_options_wid,
                                     self.line_options_wid])
        self.box_1.set_title(0, 'Markers')
        self.box_1.set_title(1, 'Lines')
        self.box_2 = ipywidgets.Box([self.box_1])
        self.box_2.layout.border = '2px solid'
        self.box_2.layout.display = 'table'
        self.container = ipywidgets.VBox([self.labels_options_wid, self.box_2])

        # Set style
        self.predefined_style(style, suboptions_style)

        # Call superclass
        initial_options = renderer_options.copy()
        super(Shape3DOptionsWidget, self).__init__(
            [self.container], Dict, initial_options,
            render_function=render_function)

        # Set visibility
        self._set_visibility()

        # Add callbacks
        self.add_callbacks()

    def _set_visibility(self):
        self.labels_options_wid.layout.display = (
            'none' if self.labels is None else 'flex')

    def _save_options(self, change):
        # update selected values
        self.selected_values = {
            'lines': self.line_options_wid.selected_values,
            'markers': self.marker_options_wid.selected_values,
            'with_labels': self.labels_options_wid.selected_values}
        # update default values
        current_key = self.get_key(self.labels)
        self.default_options[current_key] = self.selected_values.copy()

    def get_key(self, labels):
        r"""
        Function that returns a unique key based on the properties of the
        provided shape object.

        Parameters
        ----------
        labels : `list` or ``None``, optional
            The `list` of labels. ``None`` if there are no labels.

        Returns
        -------
        key : `str`
            The key that has the format ``'{labels}'``.
        """
        return "{}".format(labels)

    def get_default_options(self, labels):
        r"""
        Function that returns a `dict` with default options given a `list` of
        labels. The function returns the `dict` of options but also updates the
        ``self.default_options`` `dict`.

        Parameters
        ----------
        labels : `list` or ``None``, optional
            The `list` of labels. ``None`` if there are no labels.

        Returns
        -------
        default_options : `dict`
            A `dict` with the default options.
        """
        # create key
        key = self.get_key(labels)
        # if the key does not exist in the default options dict, then add it
        if key not in self.default_options:
            self.default_options[key] = {}

            # Set lines options
            lc = ['red']
            if labels is not None:
                lc = sample_colours_from_colourmap(len(labels), 'jet')
            self.default_options[key]['lines'] = {
                'line_colour': lc, 'render_lines': True, 'line_width': 4.}

            # Set markers options
            mc = ['red']
            if labels is not None and len(labels) > 1:
                mc = sample_colours_from_colourmap(len(labels), 'jet')
            self.default_options[key]['markers'] = {
                'marker_colour': mc, 'render_markers': True,
                'marker_size': None, 'marker_style': 'sphere',
                'marker_resolution': 8}

            # Set labels
            self.default_options[key]['with_labels'] = labels
        return self.default_options[key]

    def add_callbacks(self):
        r"""
        Function that adds the handler callback functions in all the widget
        components, which are necessary for the internal functionality.
        """
        self.line_options_wid.observe(
            self._save_options, names='selected_values', type='change')
        self.marker_options_wid.observe(
            self._save_options, names='selected_values', type='change')
        self.labels_options_wid.observe(
            self._save_options, names='selected_values', type='change')

    def remove_callbacks(self):
        r"""
        Function that removes all the internal handler callback functions.
        """
        self.line_options_wid.unobserve(
            self._save_options, names='selected_values', type='change')
        self.marker_options_wid.unobserve(
            self._save_options, names='selected_values', type='change')
        self.labels_options_wid.unobserve(
            self._save_options, names='selected_values', type='change')

    def predefined_style(self, style, suboptions_style):
        r"""
        Sets a predefined style to the widget.

        Parameters
        ----------
        style : `str` (see below)
            The style of the widget. Possible options are:

                ============= ============================
                Style         Description
                ============= ============================
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ============================

        suboptions_style : `str` (see below)
            The style of the widget's sub-options. Possible options are:

                ============= ============================
                Style         Description
                ============= ============================
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ============================

        """
        self.container.box_style = style
        self.labels_options_wid.container.box_style = suboptions_style
        if suboptions_style != '' or style != '':
            self.labels_options_wid.set_buttons_style('primary')
        self.box_2.box_style = suboptions_style
        tmp = self.marker_options_wid.marker_colour_widget
        tmp.apply_to_all_button.button_style = suboptions_style
        tmp = self.line_options_wid.line_colour_widget
        tmp.apply_to_all_button.button_style = suboptions_style

    def set_widget_state(self, labels, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided `labels`
        are different than ``self.labels``.

        Parameters
        ----------
        labels : `list` or ``None``, optional
            The `list` of labels used in all :map:`ColourSelectionWidget` objects
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # keep old value
        old_value = self.selected_values

        # check if updates are required
        if (not self.default_options or
                self.get_key(self.labels) != self.get_key(labels)):
            # Temporarily remove callbacks
            render_function = self._render_function
            self.remove_render_function()
            self.remove_callbacks()

            # Get options
            renderer_options = self.get_default_options(labels)

            # Assign properties
            self.labels = labels

            # Set visibility
            self._set_visibility()

            # Update subwidgets
            self.line_options_wid.set_widget_state(
                renderer_options['lines'], labels=labels, allow_callback=False)
            self.marker_options_wid.set_widget_state(
                renderer_options['markers'], labels=labels,
                allow_callback=False)
            if labels is not None:
                self.labels_options_wid.set_widget_state(
                    labels, with_labels=renderer_options['with_labels'],
                    allow_callback=False)
            else:
                self.labels_options_wid.set_widget_state(
                    [' '], with_labels=None, allow_callback=False)

            # Get values
            self._save_options({})

            # Add callbacks
            self.add_callbacks()
            self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self.call_render_function(old_value, self.selected_values)


class RendererOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting rendering options.

    Note that:

    * To update the state of the widget, please refer to the
      :meth:`set_widget_state` method.
    * The widget has **memory** about the properties of the objects that are
      passed into it through :meth:`set_widget_state`. Each object has a unique
      key id assigned through :meth:`get_key`. Then, the options that correspond
      to each key are stored in the ``self.default_options`` `dict`.
    * The selected values of the current object object are stored in the
      ``self.selected_values`` `trait`.
    * To set the styling of this widget please refer to the
      :meth:`predefined_style` method.
    * To update the handler callback function of the widget, please refer to the
      :meth:`replace_render_function` method.

    Parameters
    ----------
    options_tabs : `list` of `str`
        `List` that defines the ordering of the options tabs. Possible values
        are:

            ========================== =======================================
            Value                      Returned object
            ========================== =======================================
            ``'lines_matplotlib'``     :map:`LineMatplotlibOptionsWidget`
            ``'lines_mayavi'``         :map:`LineMayaviOptionsWidget`
            ``'markers_matplotlib'``   :map:`MarkerMatplotlibOptionsWidget`
            ``'markers_mayavi'``       :map:`MarkerMayaviOptionsWidget`
            ``'numbering_matplotlib'`` :map:`NumberingMatplotlibOptionsWidget`
            ``'numbering_mayavi'``     :map:`NumberingMayaviOptionsWidget`
            ``'zoom_one'``             :map:`ZoomOneScaleWidget`
            ``'zoom_two'``             :map:`ZoomTwoScalesWidget`
            ``'legend'``               :map:`LegendOptionsWidget`
            ``'grid'``                 :map:`GridOptionsWidget`
            ``'image_matplotlib'``     :map:`ImageMatplotlibOptionsWidget`
            ``'axes'``                 :map:`AxesOptionsWidget`
            ``'trimesh'``              :map:`TriMeshOptionsWidget`
            ``'textured_trimesh'``     :map:`TexturedTriMeshOptionsWidget`
            ========================== =======================================

    labels : `list` or ``None``, optional
        The `list` of labels used in all :map:`ColourSelectionWidget` objects.
    axes_x_limits : `float` or (`float`, `float`) or ``None``, optional
        The limits of the x axis. If `float`, then it sets padding on the right
        and left as a percentage of the rendered object's width. If `tuple` or
        `list`, then it defines the axis limits. If ``None``, then the limits
        are set automatically.
    axes_y_limits : (`float`, `float`) `tuple` or ``None``, optional
        The limits of the y axis. If `float`, then it sets padding on the
        top and bottom as a percentage of the rendered object's height. If
        `tuple` or `list`, then it defines the axis limits. If ``None``, then
        the limits are set automatically.
    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        It must have signature ``render_function(change)`` where ``change`` is
        a `dict` with the following keys:

        * ``type`` : The type of notification (normally ``'change'``).
        * ``owner`` : the `HasTraits` instance
        * ``old`` : the old value of the modified trait attribute
        * ``new`` : the new value of the modified trait attribute
        * ``name`` : the name of the modified trait attribute.

        If ``None``, then nothing is assigned.
    style : `str` (see below), optional
        Sets a predefined style at the widget. Possible options are:

            ============= ==================
            Style         Description
            ============= ==================
            ``'success'`` Green-based style
            ``'info'``    Blue-based style
            ``'warning'`` Yellow-based style
            ``'danger'``  Red-based style
            ``''``        No style
            ============= ==================

    Example
    -------
    Let's create a rendering options widget and then update its state. Firstly,
    we need to import it:

        >>> from menpowidgets.options import RendererOptionsWidget

    Let's set some initial options:

        >>> options_tabs = ['markers', 'lines', 'grid']
        >>> labels = ['jaw', 'eyes']

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected marker face colour and line
    width:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(change):
        >>>     s = "Marker face colour: {}, Line width: {}".format(
        >>>         wid.selected_values['markers']['marker_face_colour'],
        >>>         wid.selected_values['lines']['line_width'])
        >>>     print_dynamic(s)

    Create the widget with the initial options and display it:

        >>> wid = RendererOptionsWidget(options_tabs, labels=labels,
        >>>                             render_function=render_function,
        >>>                             style='info')
        >>> wid

    By playing around, the printed message gets updated. The style of the widget
    can be changed as:

        >>> wid.predefined_style('minimal', 'info')

    Finally, let's change the widget status with a new set of labels:

        >>> wid.set_widget_state(labels=['1'], allow_callback=True)

    Remember that the widget is **mnemonic**, i.e. it remembers the objects it
    has seen and their corresponding options. These can be retrieved as:

        >>> wid.default_options

    """
    def __init__(self, options_tabs, labels, axes_x_limits=None,
                 axes_y_limits=None, render_function=None, style=''):
        # Initialise default options dictionary
        self.default_options = {}
        self.global_options = {}

        # Assign properties
        self.labels = labels
        self.options_tabs = options_tabs

        # Get initial options
        self.initialise_global_options(axes_x_limits, axes_y_limits)
        renderer_options = self.get_default_options(labels)

        # Create children
        self.options_widgets = []
        self.tab_titles = []
        for o in options_tabs:
            if o == 'lines_matplotlib':
                self.options_widgets.append(LineMatplotlibOptionsWidget(
                    renderer_options[o], render_function=None,
                    render_checkbox_title='Render lines', labels=labels))
                self.tab_titles.append('Lines')
            elif o == 'lines_mayavi':
                self.options_widgets.append(LineMayaviOptionsWidget(
                    renderer_options[o], render_function=None,
                    render_checkbox_title='Render lines', labels=labels))
                self.tab_titles.append('Lines')
            elif o == 'markers_matplotlib':
                self.options_widgets.append(MarkerMatplotlibOptionsWidget(
                    renderer_options[o], render_function=None,
                    render_checkbox_title='Render markers', labels=labels))
                self.tab_titles.append('Markers')
            elif o == 'markers_mayavi':
                self.options_widgets.append(MarkerMayaviOptionsWidget(
                    renderer_options[o], render_function=None,
                    render_checkbox_title='Render markers', labels=labels))
                self.tab_titles.append('Markers')
            elif o == 'trimesh':
                self.options_widgets.append(TriMeshOptionsWidget(
                    self.global_options[o], render_function=None))
                self.tab_titles.append('Mesh')
            elif o == 'textured_trimesh':
                self.options_widgets.append(TexturedTriMeshOptionsWidget(
                    self.global_options[o], render_function=None))
                self.tab_titles.append('Textured Mesh')
            elif o == 'image_matplotlib':
                self.options_widgets.append(ImageMatplotlibOptionsWidget(
                    self.global_options[o], render_function=None))
                self.tab_titles.append('Image')
            elif o == 'numbering_matplotlib':
                self.options_widgets.append(NumberingMatplotlibOptionsWidget(
                    self.global_options[o], render_function=None,
                    render_checkbox_title='Render numbering'))
                self.tab_titles.append('Numbering')
            elif o == 'numbering_mayavi':
                self.options_widgets.append(NumberingMayaviOptionsWidget(
                    self.global_options[o], render_function=None,
                    render_checkbox_title='Render numbering'))
                self.tab_titles.append('Numbering')
            elif o == 'zoom_two':
                tmp = {'min': 0.1, 'max': 4., 'step': 0.05,
                       'zoom': self.global_options[o],
                       'lock_aspect_ratio': False}
                self.options_widgets.append(ZoomTwoScalesWidget(
                    tmp, render_function=None,
                    description='Scale: ',
                    minus_description='fa-search-minus',
                    plus_description='fa-search-plus',
                    continuous_update=False))
                self.tab_titles.append('Zoom')
            elif o == 'zoom_one':
                tmp = {'min': 0.1, 'max': 4., 'step': 0.05,
                       'zoom': self.global_options[o]}
                self.options_widgets.append(ZoomOneScaleWidget(
                    tmp, render_function=None,
                    description='Scale: ',
                    minus_description='fa-search-minus',
                    plus_description='fa-search-plus',
                    continuous_update=False))
                self.tab_titles.append('Zoom')
            elif o == 'axes':
                self.options_widgets.append(AxesOptionsWidget(
                    self.global_options[o], render_function=None,
                    render_checkbox_title='Render axes'))
                self.tab_titles.append('Axes')
            elif o == 'legend':
                self.options_widgets.append(LegendOptionsWidget(
                    self.global_options[o], render_function=None,
                    render_checkbox_title='Render legend'))
                self.tab_titles.append('Legend')
            elif o == 'grid':
                self.options_widgets.append(GridOptionsWidget(
                    self.global_options[o], render_function=None,
                    render_checkbox_title='Render grid'))
                self.tab_titles.append('Grid')
        self.suboptions_tab = ipywidgets.Tab(children=self.options_widgets)
        # set titles
        for (k, tl) in enumerate(self.tab_titles):
            self.suboptions_tab.set_title(k, tl)

        # Create final widget
        initial_options = renderer_options.copy()
        initial_options.update(self.global_options)
        self.container = ipywidgets.VBox([self.suboptions_tab])
        super(RendererOptionsWidget, self).__init__(
            [self.container], Dict, initial_options,
            render_function=render_function)

        # Set values
        self.set_widget_state(labels, allow_callback=False)

        # Set style
        self.predefined_style(style)

        # Add callbacks
        self.add_callbacks()

    def _save_options(self, change):
        # update selected values
        self.selected_values = {o: self.options_widgets[i].selected_values
                                for i, o in enumerate(self.options_tabs)}
        # update default values
        current_key = self.get_key(self.labels)
        if 'lines_matplotlib' in self.options_tabs:
            self.default_options[current_key]['lines_matplotlib'] = \
                self.selected_values['lines_matplotlib'].copy()
        if 'lines_mayavi' in self.options_tabs:
            self.default_options[current_key]['lines_mayavi'] = \
                self.selected_values['lines_mayavi'].copy()
        if 'markers_matplotlib' in self.options_tabs:
            self.default_options[current_key]['markers_matplotlib'] = \
                self.selected_values['markers_matplotlib'].copy()
        if 'markers_mayavi' in self.options_tabs:
            self.default_options[current_key]['markers_mayavi'] = \
                self.selected_values['markers_mayavi'].copy()
        # update global values
        if 'image_matplotlib' in self.options_tabs:
            self.global_options['image_matplotlib'] = \
                self.selected_values['image_matplotlib']
        if 'trimesh' in self.options_tabs:
            self.global_options['trimesh'] = self.selected_values['trimesh']
        if 'textured_trimesh' in self.options_tabs:
            self.global_options['textured_trimesh'] = \
                self.selected_values['textured_trimesh']
        if 'numbering_matplotlib' in self.options_tabs:
            self.global_options['numbering_matplotlib'] = \
                self.selected_values['numbering_matplotlib']
        if 'numbering_mayavi' in self.options_tabs:
            self.global_options['numbering_mayavi'] = \
                self.selected_values['numbering_mayavi']
        if 'zoom_one' in self.options_tabs:
            self.global_options['zoom_one'] = self.selected_values['zoom_one']
        if 'zoom_two' in self.options_tabs:
            self.global_options['zoom_two'] = self.selected_values['zoom_two']
        if 'grid' in self.options_tabs:
            self.global_options['grid'] = self.selected_values['grid']
        if 'legend' in self.options_tabs:
            self.global_options['legend'] = self.selected_values['legend']
        if 'axes' in self.options_tabs:
            self.global_options['axes'] = self.selected_values['axes']

    def add_callbacks(self):
        r"""
        Function that adds the handler callback functions in all the widget
        components, which are necessary for the internal functionality.
        """
        for wid in self.options_widgets:
            wid.observe(self._save_options, names='selected_values',
                        type='change')

    def remove_callbacks(self):
        r"""
        Function that removes all the internal handler callback functions.
        """
        for wid in self.options_widgets:
            wid.unobserve(self._save_options, names='selected_values',
                          type='change')

    def get_key(self, labels):
        r"""
        Function that returns a unique key based on the provided labels.

        Parameters
        ----------
        labels : `list` or ``None``, optional
            The `list` of labels used in all :map:`ColourSelectionWidget` objects

        Returns
        -------
        key : `str`
            The key that has the format ``'{labels}'``.
        """
        return "{}".format(labels)

    def initialise_global_options(self, axes_x_limits, axes_y_limits):
        r"""
        Function that returns a `dict` with global options, i.e. options that do
        not depend on `labels`.  The functions updates ``self.global_options``
        `dict`.

        Parameters
        ----------
        axes_x_limits : `float` or (`float`, `float`) or ``None``, optional
            The limits of the x axis. If `float`, then it sets padding on the
            right and left as a percentage of the rendered object's width. If
            `tuple` or `list`, then it defines the axis limits. If ``None``,
            then the limits are set automatically.
        axes_y_limits : (`float`, `float`) `tuple` or ``None``, optional
            The limits of the y axis. If `float`, then it sets padding on the
            top and bottom as a percentage of the rendered object's height. If
            `tuple` or `list`, then it defines the axis limits. If ``None``, then
            the limits are set automatically.
        """
        self.global_options = {}
        for o in self.options_tabs:
            if o == 'image_matplotlib':
                self.global_options[o] = {
                    'interpolation': 'bilinear', 'cmap_name': None,
                    'alpha': 1.}
            elif o == 'trimesh':
                self.global_options[o] = {
                    'mesh_type': 'wireframe', 'line_width': 2., 'colour': 'red',
                    'marker_style': 'sphere', 'marker_size': None,
                    'marker_resolution': 8, 'step': 1, 'alpha': 1.0}
            elif o == 'textured_trimesh':
                self.global_options[o] = {
                    'render_texture': True, 'mesh_type': 'surface',
                    'ambient_light': 0.0, 'specular_light': 0.0, 'alpha': 1.0,
                    'line_width': 2., 'colour': 'red'}
            elif o == 'numbering_matplotlib':
                self.global_options[o] = {
                    'render_numbering': False,
                    'numbers_font_name': 'sans-serif',
                    'numbers_font_size': 10, 'numbers_font_style': 'normal',
                    'numbers_font_weight': 'normal',
                    'numbers_font_colour': 'black',
                    'numbers_horizontal_align': 'center',
                    'numbers_vertical_align': 'bottom'}
            elif o == 'numbering_mayavi':
                self.global_options[o] = {
                    'render_numbering': False,
                    'numbers_size': None,
                    'numbers_colour': 'black'}
            elif o == 'zoom_one':
                self.global_options[o] = 1.
            elif o == 'zoom_two':
                self.global_options[o] = [1., 1.]
            elif o == 'axes':
                self.global_options[o] = {
                    'render_axes': False, 'axes_font_name': 'sans-serif',
                    'axes_font_size': 10, 'axes_font_style': 'normal',
                    'axes_font_weight': 'normal',
                    'axes_x_limits': axes_x_limits,
                    'axes_y_limits': axes_y_limits,
                    'axes_x_ticks': None, 'axes_y_ticks': None}
            elif o == 'legend':
                self.global_options[o] = {
                    'render_legend': False, 'legend_title': '',
                    'legend_font_name': 'sans-serif',
                    'legend_font_style': 'normal', 'legend_font_size': 10,
                    'legend_font_weight': 'normal',
                    'legend_marker_scale': 1., 'legend_location': 2,
                    'legend_bbox_to_anchor': (1.05, 1.),
                    'legend_border_axes_pad': 1., 'legend_n_columns': 1,
                    'legend_horizontal_spacing': 1.,
                    'legend_vertical_spacing': 1., 'legend_border': True,
                    'legend_border_padding': 0.5, 'legend_shadow': False,
                    'legend_rounded_corners': False}
            elif o == 'grid':
                self.global_options[o] = {
                    'render_grid': False, 'grid_line_style': '--',
                    'grid_line_width': 0.5}

    def get_default_options(self, labels):
        r"""
        Function that returns a `dict` with default options given a `list` of
        labels. The function returns the `dict` of options but also updates the
        ``self.default_options`` `dict`.

        Parameters
        ----------
        labels : `list` or ``None``, optional
            The `list` of labels used in all :map:`ColourSelectionWidget` objects

        Returns
        -------
        default_options : `dict`
            A `dict` with the default options.
        """
        # create key
        key = self.get_key(labels)
        # if the key does not exist in the default options dict, then add it
        if key not in self.default_options:
            self.default_options[key] = {}
            if 'lines_matplotlib' in self.options_tabs:
                lc = ['red']
                if labels is not None:
                    lc = sample_colours_from_colourmap(len(labels), 'jet')
                self.default_options[key]['lines_matplotlib'] = {
                    'render_lines': True, 'line_width': 1,
                    'line_colour': lc, 'line_style': '-'}
            if 'lines_mayavi' in self.options_tabs:
                lc = ['red']
                if labels is not None:
                    lc = sample_colours_from_colourmap(len(labels), 'jet')
                self.default_options[key]['lines_mayavi'] = {
                    'render_lines': True, 'line_width': 4., 'line_colour': lc}
            if 'markers_matplotlib' in self.options_tabs:
                fc = ['red']
                ec = ['black']
                if labels is not None and len(labels) > 1:
                    fc = sample_colours_from_colourmap(len(labels), 'jet')
                    ec = sample_colours_from_colourmap(len(labels), 'jet')
                self.default_options[key]['markers_matplotlib'] = {
                    'render_markers': True, 'marker_size': 5,
                    'marker_face_colour': fc, 'marker_edge_colour': ec,
                    'marker_style': 'o', 'marker_edge_width': 1}
            if 'markers_mayavi' in self.options_tabs:
                mc = ['red']
                if labels is not None and len(labels) > 1:
                    mc = sample_colours_from_colourmap(len(labels), 'jet')
                self.default_options[key]['markers_mayavi'] = {
                    'marker_colour': mc, 'render_markers': True,
                    'marker_size': 0.1, 'marker_style': 'sphere',
                    'marker_resolution': 8}
        return self.default_options[key]

    def predefined_style(self, style):
        r"""
        Function that sets a predefined style on the widget.

        Parameters
        ----------
        style : `str` (see below)
            Style options:

                ============= ============================
                Style         Description
                ============= ============================
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ============================

        """
        for w in self.options_widgets:
            w.box_style = style
        self.container.box_style = style
        for i, o in enumerate(self.options_tabs):
            if o == 'lines_matplotlib':
                tmp = self.options_widgets[i].line_colour_widget
                tmp.apply_to_all_button.button_style = style
            elif o == 'lines_mayavi':
                tmp = self.options_widgets[i].line_colour_widget
                tmp.apply_to_all_button.button_style = style
            elif o == 'markers_matplotlib':
                tmp = self.options_widgets[i].marker_face_colour_widget
                tmp.apply_to_all_button.button_style = style
                tmp = self.options_widgets[i].marker_edge_colour_widget
                tmp.apply_to_all_button.button_style = style
            elif o == 'markers_mayavi':
                tmp = self.options_widgets[i].marker_colour_widget
                tmp.apply_to_all_button.button_style = style
            elif o == 'trimesh':
                self.options_widgets[i].alpha_slider.slider_color = \
                    map_styles_to_hex_colours(style)
            elif o == 'textured_trimesh':
                self.options_widgets[i].ambient_slider.slider_color = \
                    map_styles_to_hex_colours(style)
                self.options_widgets[i].specular_slider.slider_color = \
                    map_styles_to_hex_colours(style)
                self.options_widgets[i].alpha_slider.slider_color = \
                    map_styles_to_hex_colours(style)
            elif o == 'image_matplotlib':
                self.options_widgets[i].alpha_slider.slider_color = \
                    map_styles_to_hex_colours(style)
            elif o == 'zoom_two':
                self.options_widgets[i].x_button_minus.button_style = 'primary'
                self.options_widgets[i].x_button_plus.button_style = 'primary'
                self.options_widgets[i].y_button_minus.button_style = 'primary'
                self.options_widgets[i].y_button_plus.button_style = 'primary'
                self.options_widgets[i].x_zoom_slider.slider_color = \
                    map_styles_to_hex_colours('primary')
                self.options_widgets[i].y_zoom_slider.slider_color = \
                    map_styles_to_hex_colours('primary')
                self.options_widgets[i].lock_aspect_button.button_style = \
                    'warning'
            elif o == 'zoom_one':
                self.options_widgets[i].button_minus.button_style = 'primary'
                self.options_widgets[i].button_plus.button_style = 'primary'
                self.options_widgets[i].zoom_slider.slider_color = \
                    map_styles_to_hex_colours('primary')

    def set_widget_state(self, labels, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided `labels`
        are different than ``self.labels``.

        Parameters
        ----------
        labels : `list` or ``None``, optional
            The `list` of labels used in all :map:`ColourSelectionWidget` objects
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # keep old value
        old_value = self.selected_values

        # check if updates are required
        if (not self.default_options or
                self.get_key(self.labels) != self.get_key(labels)):
            # Temporarily remove callbacks
            render_function = self._render_function
            self.remove_render_function()
            self.remove_callbacks()

            # Get options
            renderer_options = self.get_default_options(labels)

            # Assign properties
            self.labels = labels

            # Update subwidgets
            if 'lines_matplotlib' in self.options_tabs:
                i = self.options_tabs.index('lines_matplotlib')
                self.options_widgets[i].set_widget_state(
                    renderer_options['lines_matplotlib'], labels=labels,
                    allow_callback=False)
            if 'lines_mayavi' in self.options_tabs:
                i = self.options_tabs.index('lines_mayavi')
                self.options_widgets[i].set_widget_state(
                    renderer_options['lines_mayavi'], labels=labels,
                    allow_callback=False)
            if 'markers_matplotlib' in self.options_tabs:
                i = self.options_tabs.index('markers_matplotlib')
                self.options_widgets[i].set_widget_state(
                    renderer_options['markers_matplotlib'], labels=labels,
                    allow_callback=False)
            if 'markers_mayavi' in self.options_tabs:
                i = self.options_tabs.index('markers_mayavi')
                self.options_widgets[i].set_widget_state(
                    renderer_options['markers_mayavi'], labels=labels,
                    allow_callback=False)

            # Get values
            self._save_options({})

            # Add callbacks
            self.add_callbacks()
            self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self.call_render_function(old_value, self.selected_values)


class ImageOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting options for rendering an image. Note that:

    * To update the state of the widget, please refer to the
      :meth:`set_widget_state` method.
    * The widget has **memory** about the properties of the objects that are
      passed into it through :meth:`set_widget_state`. Each image object has a
      unique key id assigned through :meth:`get_key`. Then, the options that
      correspond to each key are stored in the ``self.default_options`` `dict`.
    * The selected values of the current image object are stored in the
      ``self.selected_values`` `trait`.
    * When an unseen image object is passed in (i.e. a key that is not included
      in the ``self.default_options`` `dict`), it gets some pre-defined
      default options.
    * To set the styling of this widget please refer to the
      :meth:`predefined_style` method.
    * To update the handler callback function of the widget, please refer to the
      :meth:`replace_render_function` method.

    Parameters
    ----------
    n_channels : `int`
        The number of channels of the initial image object.
    image_is_masked : `bool`
        Whether the initial image object is masked or not. If ``True``, then the
        image is assumed to be a `menpo.image.MaskedImage` object.
    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        It must have signature ``render_function(change)`` where ``change`` is
        a `dict` with the following keys:

        * ``type`` : The type of notification (normally ``'change'``).
        * ``owner`` : the `HasTraits` instance
        * ``old`` : the old value of the modified trait attribute
        * ``new`` : the new value of the modified trait attribute
        * ``name`` : the name of the modified trait attribute.

        If ``None``, then nothing is assigned.
    style : `str` (see below), optional
        Sets a predefined style at the widget. Possible options are:

            ============= ============================
            Style         Description
            ============= ============================
            ``'success'`` Green-based style
            ``'info'``    Blue-based style
            ``'warning'`` Yellow-based style
            ``'danger'``  Red-based style
            ``''``        No style
            ============= ============================

    Example
    -------
    Let's create an image options widget and then update its state. Firstly,
    we need to import it:

        >>> from menpowidgets.options import ImageOptionsWidget

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected options:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(change):
        >>>     s = "Channels: {}, Masked: {}, Glyph: {}, Sum: {}".format(
        >>>         wid.selected_values['channels'],
        >>>         wid.selected_values['masked_enabled'],
        >>>         wid.selected_values['glyph_enabled'],
        >>>         wid.selected_values['sum_enabled'])
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> wid = ImageOptionsWidget(n_channels=30, image_is_masked=True,
        >>>                          render_function=render_function,
        >>>                          style='warning')
        >>> wid

    By playing around with the widget, printed message gets updated. Finally,
    let's change the widget status with a new object:

        >>> wid.set_widget_state(n_channels=10, image_is_masked=False,
        >>>                      allow_callback=False)

    Remember that the widget is **mnemonic**, i.e. it remembers the objects it
    has seen and their corresponding options. These can be retrieved as:

        >>> wid.default_options

    """
    def __init__(self, n_channels, image_is_masked, render_function=None,
                 style='minimal'):
        # Initialise default options dictionary
        self.default_options = {}

        # Assign properties
        self.n_channels = None
        self.image_is_masked = None

        # Create children
        slice_options = {'command': '0', 'length': n_channels}
        self.channels_wid = SlicingCommandWidget(
            slice_options, description='Channels', render_function=None,
            example_visible=True, continuous_update=False,
            orientation='vertical')
        self.masked_checkbox = SwitchWidget(
            False, description='Masked', description_location='right',
            switch_type='checkbox')
        self.rgb_checkbox = SwitchWidget(
            False, description='RGB', description_location='right',
            switch_type='checkbox')
        self.sum_checkbox = SwitchWidget(
            False, description='Sum', description_location='right',
            switch_type='checkbox')
        self.glyph_checkbox = SwitchWidget(
            False, description='Glyph', description_location='right',
            switch_type='checkbox')
        self.glyph_block_size_title = ipywidgets.Label(value='Block size')
        self.glyph_block_size_text = ipywidgets.BoundedIntText(min=1, max=25,
                                                               width='1cm')
        self.glyph_use_negative_checkbox = SwitchWidget(
            False, description='Negative', description_location='right',
            switch_type='checkbox')
        self.interpolation_checkbox = SwitchWidget(
            False, description='Interpolation', description_location='right',
            switch_type='checkbox')
        self.alpha_title = ipywidgets.Label(value='Transparency')
        self.alpha_slider = ipywidgets.FloatSlider(
            value=1.0, min=0.0, max=1.0, step=0.05, continuous_update=False,
            readout=False, width='2.1cm')
        self.alpha_text = ipywidgets.Label(value="{:.2f}".format(1.0),
                                           width='0.75cm')
        self.cmap_title = ipywidgets.Label(value='Colour map')
        cmap_dict = OrderedDict()
        cmap_dict['None'] = None
        cmap_dict['afmhot'] = 'afmhot'
        cmap_dict['autumn'] = 'autumn'
        cmap_dict['binary'] = 'binary'
        cmap_dict['bone'] = 'bone'
        cmap_dict['brg'] = 'brg'
        cmap_dict['bwr'] = 'bwr'
        cmap_dict['cool'] = 'cool'
        cmap_dict['coolwarm'] = 'coolwarm'
        cmap_dict['copper'] = 'copper'
        cmap_dict['cubehelix']= 'cubehelix'
        cmap_dict['flag'] = 'flag'
        cmap_dict['gist_earth'] = 'gist_earth'
        cmap_dict['gist_heat'] = 'gist_heat'
        cmap_dict['gist_gray'] = 'gist_gray'
        cmap_dict['gist_ncar'] = 'gist_ncar'
        cmap_dict['gist_rainbow'] = 'gist_rainbow'
        cmap_dict['gist_stern'] = 'gist_stern'
        cmap_dict['gist_yarg'] = 'gist_yarg'
        cmap_dict['gnuplot'] = 'gnuplot'
        cmap_dict['gnuplot2'] = 'gnuplot2'
        cmap_dict['gray'] = 'gray'
        cmap_dict['hot'] = 'hot'
        cmap_dict['hsv'] = 'hsv'
        cmap_dict['inferno'] = 'inferno'
        cmap_dict['jet'] = 'jet'
        cmap_dict['magma'] = 'magma'
        cmap_dict['nipy_spectral'] = 'nipy_spectral'
        cmap_dict['ocean'] = 'ocean'
        cmap_dict['pink'] = 'pink'
        cmap_dict['plasma'] = 'plasma'
        cmap_dict['prism'] = 'prism'
        cmap_dict['rainbow'] = 'rainbow'
        cmap_dict['seismic'] = 'seismic'
        cmap_dict['spectral'] = 'spectral'
        cmap_dict['spring'] = 'spring'
        cmap_dict['summer'] = 'summer'
        cmap_dict['terrain'] = 'terrain'
        cmap_dict['viridis'] = 'viridis'
        cmap_dict['winter'] = 'winter'
        cmap_dict['Blues'] = 'Blues'
        cmap_dict['BuGn'] = 'BuGn'
        cmap_dict['BuPu'] = 'BuPu'
        cmap_dict['GnBu'] = 'GnBu'
        cmap_dict['Greens'] = 'Greens'
        cmap_dict['Greys'] = 'Greys'
        cmap_dict['Oranges'] = 'Oranges'
        cmap_dict['OrRd'] = 'OrRd'
        cmap_dict['PuBu'] = 'PuBu'
        cmap_dict['PuBuGn'] = 'PuBuGn'
        cmap_dict['PuRd'] = 'PuRd'
        cmap_dict['Purples'] = 'Purples'
        cmap_dict['RdPu'] = 'RdPu'
        cmap_dict['Reds'] = 'Reds'
        cmap_dict['YlGn'] = 'YlGn'
        cmap_dict['YlGnBu'] = 'YlGnBu'
        cmap_dict['YlOrBr'] = 'YlOrBr'
        cmap_dict['YlOrRd'] = 'YlOrRd'
        self.cmap_select = ipywidgets.Dropdown(options=cmap_dict, value=None,
                                               width='3cm')

        # Group widgets
        self.box_1 = ipywidgets.HBox([self.glyph_block_size_title,
                                      self.glyph_block_size_text])
        self.box_1.layout.align_items = 'center'
        self.box_2 = ipywidgets.HBox([self.cmap_title, self.cmap_select])
        self.box_2.layout.align_items = 'center'
        self.box_3 = ipywidgets.HBox(([self.alpha_title, self.alpha_slider,
                                       self.alpha_text]))
        self.box_3.layout.align_items = 'center'
        self.box_4 = ipywidgets.VBox([self.box_1,
                                      self.glyph_use_negative_checkbox])
        self.box_4.layout.display = 'none'
        self.box_4.layout.border = '1px solid'
        self.box_5 = ipywidgets.VBox([self.interpolation_checkbox,
                                      self.masked_checkbox, self.rgb_checkbox])
        self.box_5.layout.margin = '0px 10px 0px 0px'
        self.box_6 = ipywidgets.VBox([self.box_2, self.box_3])
        self.box_6.layout.align_items = 'flex-end'
        self.glyph_checkbox.layout.margin = '0px 10px 0px 0px'
        self.box_7 = ipywidgets.HBox([self.glyph_checkbox, self.box_4])
        self.box_7.layout.align_items = 'flex-start'
        self.sum_checkbox.layout.margin = '0px 10px 0px 0px'
        self.box_8 = ipywidgets.HBox([self.sum_checkbox, self.box_7])
        self.box_8.layout.align_items = 'flex-start'
        self.box_9 = ipywidgets.VBox([self.box_6, self.box_8])
        self.box_9.layout.align_items = 'flex-start'
        self.channels_wid.layout.margin = '0px 10px 0px 0px'
        self.container = ipywidgets.HBox([self.channels_wid,
                                          self.box_5, self.box_9])

        # Create final widget
        super(ImageOptionsWidget, self).__init__(
            [self.container], Dict, {}, render_function=render_function)

        # Set values
        self.set_widget_state(n_channels, image_is_masked, allow_callback=False)

        # Set slider update
        def slider_sync(change):
            self.alpha_text.value = '{:.2f}'.format(float(change['new']))
        self.alpha_slider.observe(slider_sync, names='value', type='change')

        # Set style
        self.predefined_style(style)

    def add_callbacks(self):
        r"""
        Function that adds the handler callback functions in all the widget
        components, which are necessary for the internal functionality.
        """
        self.channels_wid.observe(
            self._save_channels, names='selected_values', type='change')
        self.interpolation_checkbox.observe(
            self._save_options, names='selected_values', type='change')
        self.masked_checkbox.observe(
            self._save_options, names='selected_values', type='change')
        self.rgb_checkbox.observe(
            self._save_rgb, names='selected_values', type='change')
        self.sum_checkbox.observe(
            self._save_sum, names='selected_values', type='change')
        self.glyph_checkbox.observe(
            self._save_glyph, names='selected_values', type='change')
        self.cmap_select.observe(
            self._save_options, names='value', type='change')
        self.alpha_slider.observe(
            self._save_options, names='value', type='change')
        self.glyph_block_size_text.observe(
            self._save_options, names='value', type='change')
        self.glyph_use_negative_checkbox.observe(
            self._save_options, names='selected_values', type='change')

    def remove_callbacks(self):
        r"""
        Function that removes all the internal handler callback functions.
        """
        self.channels_wid.unobserve(
            self._save_channels, names='selected_values', type='change')
        self.interpolation_checkbox.unobserve(
            self._save_options, names='selected_values', type='change')
        self.masked_checkbox.unobserve(
            self._save_options, names='selected_values', type='change')
        self.rgb_checkbox.unobserve(
            self._save_rgb, names='selected_values', type='change')
        self.sum_checkbox.unobserve(
            self._save_sum, names='selected_values', type='change')
        self.glyph_checkbox.unobserve(
            self._save_glyph, names='selected_values', type='change')
        self.cmap_select.unobserve(
            self._save_options, names='value', type='change')
        self.alpha_slider.unobserve(
            self._save_options, names='value', type='change')
        self.glyph_block_size_text.unobserve(
            self._save_options, names='value', type='change')
        self.glyph_use_negative_checkbox.unobserve(
            self._save_options, names='selected_values', type='change')

    def _save_options(self, change):
        # get channels value
        channels_val = self.channels_wid.selected_values
        if self.rgb_checkbox.selected_values and self.n_channels == 3:
            channels_val = None
        # get interpolation value
        interpolation = ('bilinear'
                         if self.interpolation_checkbox.selected_values
                         else 'none')
        # update selected values
        self.selected_values = {
            'channels': channels_val,
            'glyph_enabled': self.glyph_checkbox.selected_values,
            'glyph_block_size': self.glyph_block_size_text.value,
            'glyph_use_negative':
                self.glyph_use_negative_checkbox.selected_values,
            'sum_enabled': self.sum_checkbox.selected_values,
            'masked_enabled': self.masked_checkbox.selected_values,
            'alpha': self.alpha_slider.value,
            'cmap_name': self.cmap_select.value,
            'interpolation': interpolation}
        # update default values
        current_key = self.get_key(self.n_channels, self.image_is_masked)
        self.default_options[current_key] = self.selected_values

    def _save_channels(self, change):
        if self.n_channels == 3:
            # temporarily remove rgb callback
            self.rgb_checkbox.unobserve(self._save_rgb, names='value',
                                        type='change')
            # set value
            self.rgb_checkbox.set_widget_state(False, allow_callback=False)
            # re-assign rgb callback
            self.rgb_checkbox.observe(self._save_rgb, names='value',
                                      type='change')
        self._save_options({})

    def _save_rgb(self, change):
        if change['new']:
            # temporarily remove channels callback
            self.channels_wid.unobserve(
                self._save_channels, names='selected_values', type='change')
            # update channels widget
            self.channels_wid.set_widget_state(
                {'command': '0, 1, 2', 'length': self.n_channels},
                allow_callback=False)
            # re-assign channels callback
            self.channels_wid.observe(
                    self._save_channels, names='selected_values', type='change')
        self._save_options({})

    def _save_sum(self, change):
        if change['new'] and self.glyph_checkbox.selected_values:
            # temporarily remove glyph callback
            self.glyph_checkbox.unobserve(self._save_glyph, names='value',
                                          type='change')

            # set glyph to False
            self.glyph_checkbox.set_widget_state(False, allow_callback=False)
            self.box_4.layout.display = 'none'

            # re-assign glyph callback
            self.glyph_checkbox.observe(self._save_glyph, names='value',
                                        type='change')
        self._save_options({})

    def _save_glyph(self, change):
        if change['new'] and self.sum_checkbox.selected_values:
            # temporarily remove sum callback
            self.sum_checkbox.unobserve(self._save_sum, names='value',
                                        type='change')

            # set glyph to false
            self.sum_checkbox.set_widget_state(False, allow_callback=False)

            # re-assign sum callback
            self.sum_checkbox.observe(self._save_sum, names='value',
                                      type='change')
        # set visibility
        self.box_4.layout.display = 'flex' if change['new'] else 'none'
        self._save_options({})

    def set_visibility(self):
        r"""
        Function that sets the visibility of the various components of the
        widget, depending on the properties of the current image object, i.e.
        ``self.n_channels`` and ``self.image_is_masked``.
        """
        self.channels_wid.layout.display = ('flex' if self.n_channels > 1
                                            else 'none')
        self.rgb_checkbox.layout.display = ('flex' if self.n_channels == 3
                                            else 'none')
        self.masked_checkbox.layout.display = ('flex' if self.image_is_masked
                                               else 'none')
        self.box_8.layout.display = 'flex' if self.n_channels > 1 else 'none'
        self.box_4.layout.display = (
            'flex' if self.glyph_checkbox.selected_values else 'none')

    def get_key(self, n_channels, image_is_masked):
        r"""
        Function that returns a unique key based on the properties of the
        provided image object.

        Parameters
        ----------
        n_channels : `int`
            The number of channels.
        image_is_masked : `bool`
            Whether the image object is masked or not. If ``True``, then the
            image is assumed to be a `menpo.image.MaskedImage` object.

        Returns
        -------
        key : `str`
            The key that has the format ``'{n_channels}_{image_is_masked}'``.
        """
        return "{}_{}".format(n_channels, image_is_masked)

    def get_default_options(self, n_channels, image_is_masked):
        r"""
        Function that returns a `dict` with default options given the properties
        of an image object, i.e. `n_channels` and `image_is_masked`. The function
        returns the `dict` of options but also updates the
        ``self.default_options`` `dict`.

        Parameters
        ----------
        n_channels : `int`
            The number of channels.
        image_is_masked : `bool`
            Whether the image object is masked or not. If ``True``, then the
            image is assumed to be a `menpo.image.MaskedImage` object.

        Returns
        -------
        default_options : `dict`
            A `dict` with the default options.
        """
        # create key
        key = self.get_key(n_channels, image_is_masked)
        # if the key does not exist in the default options dict, then add it
        if key not in self.default_options:
            # if image has 3 channels, visualise it as RGB, else render only the
            # first channel
            channels = None if n_channels == 3 else [0]
            # if image is masked, render it as masked
            masked_enabled = image_is_masked
            # update default options dictionary
            self.default_options[key] = {'channels': channels,
                                         'glyph_enabled': False,
                                         'glyph_block_size': 3,
                                         'glyph_use_negative': False,
                                         'sum_enabled': False,
                                         'masked_enabled': masked_enabled,
                                         'alpha': 1.0,
                                         'interpolation': 'bilinear',
                                         'cmap_name': None}
        return self.default_options[key]

    def _parse_channels_value(self, channels):
        if channels is None:
            return '0, 1, 2'
        elif isinstance(channels, list):
            return str(channels).strip('[]')
        else:
            return str(channels)

    def predefined_style(self, style):
        r"""
        Function that sets a predefined style on the widget.

        Parameters
        ----------
        style : `str` (see below)
            Style options:

                ============= ============================
                Style         Description
                ============= ============================
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ============================
        """
        self.container.box_style = style
        self.channels_wid.single_slider.slider_color = \
            map_styles_to_hex_colours(style)
        self.channels_wid.multiple_slider.slider_color = \
            map_styles_to_hex_colours(style)

    def set_widget_state(self, n_channels, image_is_masked,
                         allow_callback=True):
        r"""
        Method that updates the state of the widget, if the key generated with
        :meth:`get_key` based on the provided `n_channels` and `image_is_masked`
        is different than the current key based on ``self.n_channels`` and
        ``self.image_is_masked``.

        Parameters
        ----------
        n_channels : `int`
            The number of channels of the initial image object.
        image_is_masked : `bool`
            Whether the initial image object is masked or not. If ``True``, then
            the image is assumed to be a `menpo.image.MaskedImage` object.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # keep old value
        old_value = self.selected_values

        # check if updates are required
        if (not self.default_options or
                self.get_key(self.n_channels, self.image_is_masked) !=
                self.get_key(n_channels, image_is_masked)):
            # temporarily remove callbacks
            render_function = self._render_function
            self.remove_render_function()
            self.remove_callbacks()

            # Assign properties
            self.n_channels = n_channels
            self.image_is_masked = image_is_masked

            # Get initial options
            channel_options = self.get_default_options(n_channels,
                                                       image_is_masked)

            # Parse channels value
            channels = self._parse_channels_value(channel_options['channels'])

            # Set both sum and glyph to False, to make sure that there is no
            # conflict
            self.sum_checkbox.set_widget_state(False, allow_callback=False)
            self.glyph_checkbox.set_widget_state(False, allow_callback=False)

            # Update widgets' state
            slice_options = {'command': channels, 'length': self.n_channels}
            self.channels_wid.set_widget_state(slice_options,
                                               allow_callback=False)
            self.masked_checkbox.set_widget_state(
                channel_options['masked_enabled'], allow_callback=False)
            self.rgb_checkbox.set_widget_state(
                self.n_channels == 3 and channel_options['channels'] is None,
                allow_callback=False)
            self.sum_checkbox.set_widget_state(channel_options['sum_enabled'],
                                               allow_callback=False)
            self.glyph_checkbox.set_widget_state(
                channel_options['glyph_enabled'], allow_callback=False)
            self.glyph_block_size_text.value = \
                channel_options['glyph_block_size']
            self.glyph_use_negative_checkbox.set_widget_state(
                channel_options['glyph_use_negative'], allow_callback=False)
            self.interpolation_checkbox.set_widget_state(
                channel_options['interpolation'] == 'bilinear',
                allow_callback=False)
            self.alpha_slider.value = channel_options['alpha']
            self.cmap_select.value = channel_options['cmap_name']

            # Set widget's visibility
            self.set_visibility()

            # Get values
            self._save_options({})

            # Re-assign callbacks
            self.add_callbacks()
            self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self.call_render_function(old_value, self.selected_values)


class LandmarkOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting 2D or 3D landmark options.

    Note that:

    * To update the state of the widget, please refer to the
      :meth:`set_widget_state` method.
    * The widget has **memory** about the properties of the objects that are
      passed into it through :meth:`set_widget_state`. Each landmarks object has
      a unique key id assigned through :meth:`get_key`. Then, the options that
      correspond to each key are stored in the ``self.default_options`` `dict`.
    * The selected values of the current landmarks object are stored in the
      ``self.selected_values`` `trait`.
    * When an unseen landmarks object is passed in (i.e. a key that is not
      included in the ``self.default_options`` `dict`), it gets some default
      initial options.
    * To set the styling of this widget please refer to the
      :meth:`predefined_style` method.
    * To update the handler callback function of the widget, please refer to the
      :meth:`replace_render_function` method.

    Parameters
    ----------
    group_keys : `list` of `str` or ``None``
        The `list` of landmark groups. If ``None``, then no landmark groups are
        available.
    labels_keys : `list` of `list` of `str` or ``None``
        The `list` of labels per landmark group. If ``None``, then no labels are
        available.
    type : {``2D``, ``3D``}
        Whether the landmarks are 2D or 3D.
    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        It must have signature ``render_function(change)`` where ``change`` is
        a `dict` with the following keys:

        * ``type`` : The type of notification (normally ``'change'``).
        * ``owner`` : the `HasTraits` instance
        * ``old`` : the old value of the modified trait attribute
        * ``new`` : the new value of the modified trait attribute
        * ``name`` : the name of the modified trait attribute.

        If ``None``, then nothing is assigned.
    style : `str` (see below), optional
        Sets a predefined style at the widget. Possible options are:

            ============= ============================
            Style         Description
            ============= ============================
            ``'success'`` Green-based style
            ``'info'``    Blue-based style
            ``'warning'`` Yellow-based style
            ``'danger'``  Red-based style
            ``''``        No style
            ============= ============================

    Example
    -------
    Let's create a landmarks widget and then update its state. Firstly, we need
    to import it:

        >>> from menpowidgets.options import LandmarkOptionsWidget

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected index:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(change):
        >>>     s = "Group: {}, Labels: {}".format(
        >>>         wid.selected_values['landmarks']['group'],
        >>>         wid.selected_values['landmarks']['with_labels'])
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> wid = LandmarkOptionsWidget(
        >>>             group_keys=['PTS', 'ibug_face_68'],
        >>>             labels_keys=[['all'], ['jaw', 'eye', 'mouth']],
        >>>             type='2D', render_function=render_function,
        >>>             style='info', suboptions_style='danger')
        >>> wid

    By playing around with the widget, the printed message gets updated.
    Finally, let's change the widget status with a new set of options:

        >>> wid.set_widget_state(group_keys=['new_group'],
        >>>                      labels_keys=[['1', '2', '3']],
        >>>                      allow_callback=False)

    Remember that the widget is **mnemonic**, i.e. it remembers the objects it
    has seen and their corresponding options. These can be retrieved as:

        >>> wid.default_options

    """
    def __init__(self, group_keys, labels_keys, type, render_function=None,
                 style='', suboptions_style=''):
        # Initialise default options dictionary
        self.default_options = {}

        # Assign properties
        self.group_keys = group_keys
        self.labels_keys = labels_keys

        # Create children
        # Render landmarks switch and no landmarks message
        self.no_landmarks_msg = ipywidgets.Label(
            value='No landmarks available.')
        self.render_landmarks_switch = SwitchWidget(
            selected_value=True, description='Render landmarks',
            description_location='right', switch_type='toggle')
        # Create group description, dropdown and slider
        self.group_title = ipywidgets.Label(value='Group')
        self.group_slider = ipywidgets.IntSlider(
            readout=False, width='4cm', value=0, continuous_update=False, min=0)
        self.group_dropdown = ipywidgets.Dropdown(
            options={'0': '0'}, description='', value='0', width='4cm')
        self.group_label = ipywidgets.Label()
        # Shape 2D options widget
        if type == '2D':
            self.shape_options_wid = Shape2DOptionsWidget([' '])
        elif type == '3D':
            self.shape_options_wid = Shape3DOptionsWidget([' '])
        else:
            raise ValueError("type must be either '2D' or '3D'")

        # Group widgets
        self.box_1 = ipywidgets.HBox([self.group_title, self.group_dropdown])
        self.box_1.layout.align_items = 'center'
        self.box_2 = ipywidgets.VBox([self.box_1, self.group_slider])
        self.box_2.layout.align_items = 'flex-end'
        self.box_3 = ipywidgets.VBox([self.box_2, self.group_label])
        self.box_3.layout.margin = '0px 10px 0px 0px'
        self.box_3.layout.border = '2px solid'
        self.box_3.layout.display = 'table'
        self.box_4 = ipywidgets.HBox([self.box_3, self.shape_options_wid])
        self.box_4.layout.margin = '10px 0px 0px 0px'
        self.box_5 = ipywidgets.VBox([self.box_4, self.no_landmarks_msg])
        self.container = ipywidgets.VBox([self.render_landmarks_switch,
                                         self.box_5])

        # Create final widget
        super(LandmarkOptionsWidget, self).__init__(
            [self.container], Dict, {}, render_function=render_function)

        # Set values, add callbacks before setting widget state
        link((self.group_dropdown, 'value'), (self.group_slider, 'value'))
        self.add_callbacks()
        self.set_widget_state(group_keys, labels_keys, allow_callback=False)

        # Set style
        self.predefined_style(style, suboptions_style)

        # Set visibility
        self.set_visibility()

    def add_callbacks(self):
        r"""
        Function that adds the handler callback functions in all the widget
        components, which are necessary for the internal functionality.
        """
        self.group_dropdown.observe(self._group_fun, names='value',
                                    type='change')
        self.shape_options_wid.add_render_function(self._save_options)
        self.render_landmarks_switch.add_render_function(
            self._render_landmarks_fun)

    def remove_callbacks(self):
        r"""
        Function that removes all the internal handler callback functions.
        """
        self.group_dropdown.unobserve(self._group_fun, names='value',
                                      type='change')
        self.shape_options_wid.remove_render_function()
        self.render_landmarks_switch.remove_render_function()

    def _group_fun(self, change):
        idx = self.group_dropdown.value
        self.shape_options_wid.set_widget_state(self.labels_keys[idx],
                                                allow_callback=False)
        self._save_options({})

    def _render_landmarks_fun(self, change):
        self.box_5.layout.display = 'flex' if change['new'] else 'none'
        self._save_options({})

    def _save_options(self, change):
        if self.group_keys is None:
            self.selected_values = {
                'landmarks': {
                    'group': None,
                    'render_landmarks': False,
                    'with_labels': None},
                'lines': self.shape_options_wid.selected_values['lines'],
                'markers': self.shape_options_wid.selected_values['markers']}
        else:
            self.selected_values = {
                'landmarks': {
                    'render_landmarks':
                        self.render_landmarks_switch.selected_values,
                    'group':
                        self.group_keys[self.group_dropdown.value],
                    'with_labels':
                        self.shape_options_wid.selected_values['with_labels']},
                'lines': self.shape_options_wid.selected_values['lines'],
                'markers': self.shape_options_wid.selected_values['markers']}

    def predefined_style(self, style, suboptions_style):
        r"""
        Sets a predefined style to the widget.

        Parameters
        ----------
        style : `str` (see below)
            The style of the widget. Possible options are:

                ============= ============================
                Style         Description
                ============= ============================
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ============================

        suboptions_style : `str` (see below)
            The style of the widget's sub-options. Possible options are:

                ============= ============================
                Style         Description
                ============= ============================
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ============================

        """
        self.container.box_style = style
        self.shape_options_wid.predefined_style('', suboptions_style)
        self.box_3.box_style = suboptions_style
        self.group_slider.slider_color = map_styles_to_hex_colours(
            suboptions_style)

    def get_key(self, group_keys, labels_keys):
        r"""
        Function that returns a unique key based on the properties of the
        provided landmarks.

        Parameters
        ----------
        group_keys : `list` of `str` or ``None``
            The `list` of landmark groups. If ``None``, then no landmark groups
            are available.
        labels_keys : `list` of `list` of `str` or ``None``
            The `list` of labels per landmark group. If ``None``, then no labels
            are available.

        Returns
        -------
        key : `str`
            The key that has the format ``'{group_keys}_{labels_keys}'``.
        """
        return "{}_{}".format(group_keys, labels_keys)

    def get_default_options(self, group_keys, labels_keys):
        r"""
        Function that returns a `dict` with default options based on the
        properties of the provided landmarks. The function returns the `dict` of
        options but also updates the ``self.default_options`` `dict`.

        Parameters
        ----------
        group_keys : `list` of `str` or ``None``
            The `list` of landmark groups. If ``None``, then no landmark groups
            are available.
        labels_keys : `list` of `list` of `str` or ``None``
            The `list` of labels per landmark group. If ``None``, then no labels
            are available.

        Returns
        -------
        default_options : `dict`
            A `dict` with the default options.
        """
        # create key
        key = self.get_key(group_keys, labels_keys)
        # if the key does not exist in the default options dict, then add it
        if key not in self.default_options:
            if group_keys is None:
                self.default_options[key] = {
                    'landmarks': {
                        'group': None,
                        'with_labels': None,
                        'render_landmarks': False}
                }
            else:
                self.default_options[key] = {
                    'landmarks': {
                        'group': group_keys[0],
                        'with_labels': labels_keys[0],
                        'render_landmarks': True}
                }
                tmp = self.shape_options_wid.get_default_options(labels_keys)
                self.default_options[key]['lines'] = tmp['lines']
                self.default_options[key]['markers'] = tmp['markers']
        return self.default_options[key]

    def _parse_group_keys_labels_keys(self, group_keys, labels_keys):
        if group_keys is None or len(group_keys) == 0:
            return [' '], [[' ']], True
        else:
            return group_keys, labels_keys, False

    def set_visibility(self):
        r"""
        Function that sets the visibility of the various components of the
        widget, depending on the properties of the current image object, i.e.
        ``self.group_keys`` and ``self.labels_keys``.
        """
        self.box_4.layout.display = (
            'none' if self.group_keys is None else 'flex')
        self.render_landmarks_switch.layout.display = (
            'none' if self.group_keys is None else 'flex')
        self.no_landmarks_msg.layout.display = (
            'inline' if self.group_keys is None else 'none')
        if self.group_keys is not None:
            self.group_label.layout.display = (
                'inline' if len(self.group_keys) == 1 else 'none')
            self.box_2.layout.display = (
                'none' if len(self.group_keys) == 1 else 'flex')

    def set_widget_state(self, group_keys, labels_keys, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the key generated with
        :meth:`get_key` based on the provided `group_keys` and `labels_keys`
        is different than the current key based on ``self.group_keys`` and
        ``self.labels_keys``.

        Parameters
        ----------
        group_keys : `list` of `str` or ``None``
            The `list` of landmark groups. If ``None``, then no landmark groups
            are available.
        labels_keys : `list` of `list` of `str` or ``None``
            The `list` of labels per landmark group. If ``None``, then no labels
            are available.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # keep old value
        old_value = self.selected_values

        # check if updates are required
        if (not self.default_options or
                self.get_key(self.group_keys, self.labels_keys) !=
                self.get_key(group_keys, labels_keys)):
            # temporarily remove callbacks
            render_function = self._render_function
            self.remove_render_function()
            self.remove_callbacks()

            # Assign properties
            self.group_keys = group_keys
            self.labels_keys = labels_keys

            # Update widgets' state
            if group_keys is not None:
                # Get options to set
                landmark_options = self.get_default_options(group_keys,
                                                            labels_keys)
                # Update
                self.group_slider.max = len(group_keys) - 1
                dropdown_dict = OrderedDict()
                for gn, gk in enumerate(group_keys):
                    dropdown_dict[gk] = gn
                self.group_dropdown.options = dropdown_dict
                self.group_label.value = 'Group: {}'.format(group_keys[0])
                group_idx = group_keys.index(
                    landmark_options['landmarks']['group'])
                if (group_idx == self.group_dropdown.value and
                        len(group_keys) > 1):
                    if self.group_dropdown.value == 0:
                        self.group_dropdown.value = 1
                    else:
                        self.group_dropdown.value = 0
                self.group_dropdown.value = group_idx
                self.render_landmarks_switch.set_widget_state(
                    landmark_options['landmarks']['render_landmarks'],
                    allow_callback=False)
                self.shape_options_wid.set_widget_state(
                    self.labels_keys[group_idx], allow_callback=False)

            # Get values
            self._save_options({})

            # Set widget's visibility
            self.set_visibility()

            # Re-assign callbacks
            self.add_callbacks()
            self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self.call_render_function(old_value, self.selected_values)


class TextPrintWidget(ipywidgets.Box):
    r"""
    Creates a widget for printing text.

    Note that:

    * To set the styling please refer to the :meth:`predefined_style` method.
    * To update the state of the widget, please refer to the
      :meth:`set_widget_state` method.

    Parameters
    ----------
    text_per_line : `list` of `str`
        The text to be printed per line.
    style : `str` (see below), optional
        Sets a predefined style at the widget. Possible options are:

            ============= ==================
            Style         Description
            ============= ==================
            ``'success'`` Green-based style
            ``'info'``    Blue-based style
            ``'warning'`` Yellow-based style
            ``'danger'``  Red-based style
            ``''``        No style
            ============= ==================

    Example
    -------
    Let's create an text widget and then update its state. Firstly, we need
    to import it:

        >>> from menpowidgets.options import TextPrintWidget

    Create the widget with some initial options and display it:

        >>> text_per_line = ['> The', '> Menpo', '> Team']
        >>> wid = TextPrintWidget(text_per_line, style='success')
        >>> wid

    The style of the widget can be changed as:

        >>> wid.predefined_style('danger')

    Update the widget state as:

        >>> wid.set_widget_state(['M', 'E', 'N', 'P', 'O'])
    """
    def __init__(self, text_per_line, style=''):
        self.label_texts = [ipywidgets.Label(value=t) for t in text_per_line]
        self.container = ipywidgets.VBox(self.label_texts)
        super(TextPrintWidget, self).__init__([self.container])
        self.layout.display = 'flex'

        # Assign options
        self.n_lines = len(text_per_line)
        self.text_per_line = text_per_line

        # Set style
        self.predefined_style(style)

    def predefined_style(self, style):
        r"""
        Function that sets a predefined style on the widget.

        Parameters
        ----------
        style : `str` (see below)
            Style options:

                ============= ==================
                Style         Description
                ============= ==================
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ==================
        """
        self.container.box_style = style
        self.container.border = '2px solid'

    def set_widget_state(self, text_per_line):
        r"""
        Method that updates the state of the widget with a new `list` of lines.

        Parameters
        ----------
        text_per_line : `list` of `str`
            The text to be printed per line.
        """
        # Check if n_lines has changed
        n_lines = len(text_per_line)
        if n_lines != self.n_lines:
            self.label_texts = [ipywidgets.Label(value=t)
                                for t in text_per_line]
            self.container.children = self.label_texts
        else:
            for i, t in enumerate(text_per_line):
                self.latex_texts[i].value = t
        self.n_lines = n_lines
        self.text_per_line = text_per_line


class SaveMatplotlibFigureOptionsWidget(ipywidgets.Box):
    r"""
    Creates a widget for saving a Matplotlib figure to file.

    To set the styling of this widget please refer to the
    :meth:`predefined_style` method.

    Parameters
    ----------
    renderer : `menpo.visualize.Renderer` or subclass or ``None``
        The renderer object that was used to render the figure.
    file_format : `str`, optional
        The initial value of the file format.
    dpi : `float` or ``None``, optional
        The initial value of the dpi. If ``None``, then dpi is set to ``0``.
    orientation : ``{'portrait', 'landscape'}``, optional
        The initial value of the paper orientation.
    paper_type : `str`, optional
        The initial value of the paper type. Possible options are::

            'letter', 'legal', 'executive', 'ledger', 'a0', 'a1', 'a2', 'a3',
            'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'a10', 'b0', 'b1', 'b2', 'b3',
            'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'b10'

    transparent : `bool`, optional
        The initial value of the transparency flag.
    face_colour : `str` or `list` of `float`, optional
        The initial value of the face colour.
    edge_colour : `str` or `list` of `float`, optional
        The initial value of the edge colour.
    pad_inches : `float`, optional
        The initial value of the figure padding in inches.
    overwrite : `bool`, optional
        The initial value of the overwrite flag.
    style : `str` (see below), optional
        Sets a predefined style at the widget. Possible options are:

            ============= ==================
            Style         Description
            ============= ==================
            ``'success'`` Green-based style
            ``'info'``    Blue-based style
            ``'warning'`` Yellow-based style
            ``'danger'``  Red-based style
            ``''``        No style
            ============= ==================
    """
    def __init__(self, renderer=None, file_format='png', dpi=None,
                 orientation='portrait', paper_type='letter', transparent=False,
                 face_colour='white', edge_colour='white', pad_inches=0.,
                 overwrite=False, style=''):
        from os import getcwd
        from os.path import join, splitext
        from pathlib import Path

        # Create widgets
        self.file_format_title = ipywidgets.Label(value='Format')
        file_format_dict = OrderedDict()
        file_format_dict['png'] = 'png'
        file_format_dict['jpg'] = 'jpg'
        file_format_dict['pdf'] = 'pdf'
        file_format_dict['eps'] = 'eps'
        file_format_dict['postscript'] = 'ps'
        file_format_dict['svg'] = 'svg'
        self.file_format_select = ipywidgets.Select(
            options=file_format_dict, value=file_format, description='',
            width='3cm')
        if dpi is None:
            dpi = 0
        self.dpi_title = ipywidgets.Label(value='DPI')
        self.dpi_text = ipywidgets.FloatText(description='', value=dpi,
                                             min=0., width='3cm')
        self.orientation_title = ipywidgets.Label(value='Orientation')
        orientation_dict = OrderedDict()
        orientation_dict['portrait'] = 'portrait'
        orientation_dict['landscape'] = 'landscape'
        self.orientation_dropdown = ipywidgets.Dropdown(
            options=orientation_dict, value=orientation, description='',
            width='3cm')
        self.papertype_title = ipywidgets.Label(value='Paper type')
        papertype_dict = OrderedDict()
        papertype_dict['letter'] = 'letter'
        papertype_dict['legal'] = 'legal'
        papertype_dict['executive'] = 'executive'
        papertype_dict['ledger'] = 'ledger'
        papertype_dict['a0'] = 'a0'
        papertype_dict['a1'] = 'a1'
        papertype_dict['a2'] = 'a2'
        papertype_dict['a3'] = 'a3'
        papertype_dict['a4'] = 'a4'
        papertype_dict['a5'] = 'a5'
        papertype_dict['a6'] = 'a6'
        papertype_dict['a7'] = 'a7'
        papertype_dict['a8'] = 'a8'
        papertype_dict['a9'] = 'a9'
        papertype_dict['a10'] = 'a10'
        papertype_dict['b0'] = 'b0'
        papertype_dict['b1'] = 'b1'
        papertype_dict['b2'] = 'b2'
        papertype_dict['b3'] = 'b3'
        papertype_dict['b4'] = 'b4'
        papertype_dict['b5'] = 'b5'
        papertype_dict['b6'] = 'b6'
        papertype_dict['b7'] = 'b7'
        papertype_dict['b8'] = 'b8'
        papertype_dict['b9'] = 'b9'
        papertype_dict['b10'] = 'b10'
        self.papertype_select = ipywidgets.Dropdown(
            options=papertype_dict, value=paper_type, description='',
            width='3cm')
        self.transparent_checkbox = SwitchWidget(
            transparent, description='Transparent',
            description_location='right', switch_type='checkbox')
        self.facecolour_widget = ColourSelectionWidget(
            [face_colour], description='Face colour')
        self.edgecolour_widget = ColourSelectionWidget(
            [edge_colour], description='Edge colour')
        self.pad_inches_title = ipywidgets.Label(value='Pad (inches)')
        self.pad_inches_text = ipywidgets.FloatText(
            description='', value=pad_inches, width='3cm')
        self.filename_title = ipywidgets.Label(value='Path')
        self.filename_text = ipywidgets.Text(
            description='', value=join(getcwd(), 'Untitled.' + file_format),
            width='10cm')
        self.overwrite_checkbox = SwitchWidget(
            overwrite, description='Overwrite if file exists',
            description_location='right', switch_type='checkbox')
        self.error_latex = ipywidgets.HTML(value='')
        self.save_button = ipywidgets.Button(description='  Save',
                                             icon='fa-floppy-o', width='2cm')

        # Group widgets
        self.box_2 = ipywidgets.HBox([self.dpi_title, self.dpi_text])
        self.box_2.layout.align_items = 'center'
        self.box_3 = ipywidgets.HBox([self.orientation_title,
                                      self.orientation_dropdown])
        self.box_3.layout.align_items = 'center'
        self.box_4 = ipywidgets.HBox([self.papertype_title,
                                      self.papertype_select])
        self.box_4.layout.align_items = 'center'
        self.box_4.layout.display = 'flex' if file_format == 'ps' else 'none'
        self.box_5 = ipywidgets.HBox([self.pad_inches_title,
                                      self.pad_inches_text])
        self.box_5.layout.align_items = 'center'
        self.box_6 = ipywidgets.HBox([self.filename_title,
                                      self.filename_text])
        self.box_6.layout.align_items = 'center'
        self.box_77 = ipywidgets.VBox([self.box_6, self.overwrite_checkbox,
                                       self.error_latex])
        self.box_77.layout.align_items = 'flex-end'
        self.box_77.layout.margin = '0px 10px 0px 0px'
        self.box_7 = ipywidgets.HBox([self.box_77, self.box_4])
        self.box_7.layout.align_items = 'flex-start'
        self.box_8 = ipywidgets.VBox([self.box_3, self.box_2, self.box_5])
        self.box_8.layout.align_items = 'flex-end'
        self.box_88 = ipywidgets.HBox([self.box_8])
        self.box_88.layout.align_items = 'flex-start'
        self.box_9 = ipywidgets.VBox([self.facecolour_widget,
                                      self.edgecolour_widget])
        self.box_9.layout.align_items = 'flex-end'
        self.box_9.layout.margin = '0px 10px 0px 0px'
        self.box_99 = ipywidgets.HBox([self.box_9, self.transparent_checkbox])
        self.box_99.layout.align_items = 'center'
        self.box_7.layout.margin = '7px'
        self.box_88.layout.margin = '7px'
        self.box_99.layout.margin = '7px'
        self.box_10 = ipywidgets.Tab([self.box_7, self.box_88, self.box_99])
        tab_titles = ['Path', 'Page setup', 'Colour']
        for (k, tl) in enumerate(tab_titles):
            self.box_10.set_title(k, tl)
        self.box_11 = ipywidgets.VBox([self.box_10])
        self.box_12 = ipywidgets.HBox([self.save_button])
        self.box_12.layout.align_items = 'center'
        self.container = ipywidgets.VBox([self.box_10, self.box_12])
        self.container.layout.align_items = 'center'

        # Create final widget
        super(SaveMatplotlibFigureOptionsWidget, self).__init__(
            children=[self.container])
        self.layout.display = 'flex'

        # Assign renderer
        if renderer is None:
            from menpo.visualize.viewmatplotlib import MatplotlibImageViewer2d
            renderer = MatplotlibImageViewer2d(figure_id=None, new_figure=True,
                                               image=np.zeros((10, 10)))
        self.renderer = renderer

        # Set style
        self.predefined_style(style)

        # Set functionality
        def paper_type_visibility(change):
            _, file_extension = splitext(self.filename_text.value)
            self.box_4.layout.display = (
                'flex' if file_extension[1:] == 'ps' else 'none')
        self.filename_text.on_submit(paper_type_visibility)

        def save_function(name):
            # set save button state
            self.error_latex.value = ''
            self.save_button.description = '  Saving...'
            self.save_button.disabled = True

            # save figure
            selected_dpi = self.dpi_text.value
            if self.dpi_text.value == 0:
                selected_dpi = None
            try:
                file_extension = Path(self.filename_text.value).suffix[1:]
                self.renderer.save_figure(
                    filename=self.filename_text.value,
                    format=str(file_extension), dpi=selected_dpi,
                    face_colour=self.facecolour_widget.selected_values[0],
                    edge_colour=self.edgecolour_widget.selected_values[0],
                    orientation=self.orientation_dropdown.value,
                    paper_type=self.papertype_select.value,
                    transparent=self.transparent_checkbox.selected_values,
                    pad_inches=self.pad_inches_text.value,
                    overwrite=self.overwrite_checkbox.selected_values)
                self.error_latex.value = ''
            except ValueError as e:
                e = str(e)
                if (e[-65:] == 'Please set the overwrite kwarg if you wish to '
                               'overwrite the file.'):
                    self.error_latex.value = (
                        '<p style="color:#FF0000";><font size="2"><em>'
                        'File exists! Tick overwrite to replace it.'
                        '</em></font size></p>')
                else:
                    self.error_latex.value = (
                        '<p style="color:#FF0000";><font size="2"><em>' + e +
                        '</em></font size></p>')

            # set save button state
            self.save_button.description = '  Save'
            self.save_button.disabled = False
        self.save_button.on_click(save_function)

    def predefined_style(self, style):
        r"""
        Function that sets a predefined style on the widget.

        Parameters
        ----------
        style : `str` (see below)
            Style options:

                ============= ==================
                Style         Description
                ============= ==================
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ==================
        """
        self.container.box_style = style
        if style != '':
            self.save_button.button_style = 'primary'
        else:
            self.save_button.button_style = ''


class SaveMayaviFigureOptionsWidget(ipywidgets.Box):
    r"""
    Creates a widget for saving a Mayavi figure to file.

    To set the styling of this widget please refer to the
    :meth:`predefined_style` method.

    Parameters
    ----------
    renderer : `menpo3d.visualize.MayaviViewer` or subclass or ``None``
        The renderer object that was used to render the figure.
    file_format : `str`, optional
        The initial value of the file format.
    size : `tuple` of `int` or ``None``, optional
        The size of the image created (unless magnification is set, in which
        case it is the size of the window used for rendering). If ``None``, then
        the figure size is used.
    magnification :	`double` or ``'auto'``, optional
        The magnification is the scaling between the pixels on the screen, and
        the pixels in the file saved. If you do not specify it, it will be
        calculated so that the file is saved with the specified size. If you
        specify a magnification, Mayavi will use the given size as a screen
        size, and the file size will be ``magnification * size``. If ``'auto'``,
        then the magnification will be set automatically.
    overwrite : `bool`, optional
        The initial value of the overwrite flag.
    style : `str` (see below), optional
        Sets a predefined style at the widget. Possible options are:

            ============= ==================
            Style         Description
            ============= ==================
            ``'success'`` Green-based style
            ``'info'``    Blue-based style
            ``'warning'`` Yellow-based style
            ``'danger'``  Red-based style
            ``''``        No style
            ============= ==================
    """
    def __init__(self, renderer=None, file_format='png', size=None,
                 magnification='auto', overwrite=False, style='minimal'):
        from os import getcwd
        from os.path import join
        from pathlib import Path

        # Create widgets
        self.size_checkbox = SwitchWidget(
            size is not None, description='Resolution',
            description_location='right', switch_type='checkbox')
        self.size_height = ipywidgets.BoundedIntText(
            value=640, min=0, max=10000, disabled=size is not None, width='2cm')
        self.size_width = ipywidgets.BoundedIntText(
            value=480, min=0, max=10000, disabled=size is not None, width='2cm')
        self.size_height_width_box = ipywidgets.VBox([self.size_height,
                                                      self.size_width])
        self.size_box = ipywidgets.HBox([self.size_checkbox,
                                         self.size_height_width_box])
        self.size_box.layout.align_items = 'center'
        self.magn_descr = ipywidgets.Label(value='Magnification')
        self.magn_toggle = ipywidgets.ToggleButton(
            value=magnification == 'auto', description='auto', width='1.7cm')
        self.magn_text = ipywidgets.BoundedFloatText(
            value=1., min=0.0001, max=100., disabled=magnification == 'auto',
            width='2cm')
        self.magn_box = ipywidgets.HBox(
            [self.magn_descr, self.magn_toggle, self.magn_text])
        self.magn_box.layout.align_items = 'center'
        self.filename_title = ipywidgets.Label(value='Path')
        self.filename_text = ipywidgets.Text(
            description='', value=join(getcwd(), 'Untitled.' + file_format),
            width='10cm')
        self.overwrite_checkbox = SwitchWidget(
            overwrite, description='Overwrite if file exists',
            description_location='right', switch_type='checkbox')
        self.error_latex = ipywidgets.HTML(value='')
        self.save_button = ipywidgets.Button(description='  Save',
                                             icon='fa-floppy-o', width='2cm')

        # Group widgets
        self.box_1 = ipywidgets.HBox([self.filename_title,
                                      self.filename_text])
        self.box_1.layout.align_items = 'center'
        self.box_2 = ipywidgets.VBox([self.box_1, self.overwrite_checkbox,
                                      self.error_latex])
        self.box_2.layout.align_items = 'flex-end'
        self.size_box.layout.margin = '0px 10px 0px 0px'
        self.box_3 = ipywidgets.HBox([self.size_box, self.magn_box])
        self.box_3.layout.align_items = 'center'
        self.save_button.layout.margin = '10px 0px 0px 0px'
        self.container = ipywidgets.VBox([self.box_2, self.box_3,
                                          self.save_button])
        self.container.layout.align_items = 'center'

        # Create final widget
        super(SaveMayaviFigureOptionsWidget, self).__init__(
            children=[self.container])
        self.layout.display = 'flex'

        # Assign renderer
        if renderer is None:
            from menpo3d.visualize.viewmayavi import MayaviRenderer
            renderer = MayaviRenderer(figure_id=None, new_figure=True)
        self.renderer = renderer

        # Set style
        self.predefined_style(style)

        # Set functionality
        def size_disable(change):
            self.size_height.disabled = not self.size_checkbox.selected_values
            self.size_width.disabled = not self.size_checkbox.selected_values
        self.size_checkbox.observe(size_disable, names='selected_values',
                                   type='change')
        size_disable({'new': self.size_checkbox.selected_values})

        def magn_disable(change):
            self.magn_text.disabled = change['new']
        self.magn_toggle.observe(magn_disable, names='value', type='change')
        magn_disable({'new': self.magn_toggle.value})

        def save_function(name):
            # set save button state
            self.error_latex.value = ''
            self.save_button.description = '  Saving...'
            self.save_button.disabled = True

            # save figure
            selected_size = None
            if self.size_checkbox.selected_values:
                selected_size = (int(self.size_height.value),
                                 int(self.size_width.value))
            selected_magn = 'auto'
            if not self.magn_toggle.value:
                selected_magn = float(self.magn_text.value)
            try:
                file_extension = Path(self.filename_text.value).suffix[1:]
                self.renderer.save_figure(
                    filename=self.filename_text.value, format=file_extension,
                    size=selected_size, magnification=selected_magn,
                    overwrite=self.overwrite_checkbox.selected_values)
                self.error_latex.value = ''
            except ValueError as e:
                e = str(e)
                if (e[-65:] == 'Please set the overwrite kwarg if you wish to '
                               'overwrite the file.'):
                    self.error_latex.value = (
                        '<p style="color:#FF0000";><font size="2"><em>'
                        'File exists! Tick overwrite to replace it.'
                        '</em></font size></p>')
                else:
                    self.error_latex.value = (
                        '<p style="color:#FF0000";><font size="2"><em>' + e +
                        '</em></font size></p>')

            # set save button state
            self.save_button.description = '  Save'
            self.save_button.disabled = False
        self.save_button.on_click(save_function)

    def predefined_style(self, style):
        r"""
        Function that sets a predefined style on the widget.

        Parameters
        ----------
        style : `str` (see below)
            Style options:

                ============= ==================
                Style         Description
                ============= ==================
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ==================
        """
        self.container.box_style = style
        if style != '':
            self.save_button.button_style = 'primary'
        else:
            self.save_button.button_style = ''


class PatchOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting patches options when rendering a patch-based
    image.

    Note that:

    * To update the state of the widget, please refer to the
      :meth:`set_widget_state` method.
    * The widget has **memory** about the properties of the objects that are
      passed into it through :meth:`set_widget_state`. Each patches object has a
      unique key id assigned through :meth:`get_key`. Then, the options that
      correspond to each key are stored in the ``self.default_options`` `dict`.
    * The selected values of the current patches object are stored in the
      ``self.selected_values`` `trait`.
    * When an unseen patches object is passed in (i.e. a key that is not included
      in the ``self.default_options`` `dict`), it gets some default initial
      options.
    * To set the styling of this widget please refer to the
      :meth:`predefined_style` method.
    * To update the handler callback function of the widget, please refer to the
      :meth:`replace_render_function` method.

    Parameters
    ----------
    n_patches : `int`
        The number of patches of the initial object.
    n_offsets : `int`
        The number of offsets of the initial object.
    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        It must have signature ``render_function(change)`` where ``change`` is
        a `dict` with the following keys:

        * ``type`` : The type of notification (normally ``'change'``).
        * ``owner`` : the `HasTraits` instance
        * ``old`` : the old value of the modified trait attribute
        * ``new`` : the new value of the modified trait attribute
        * ``name`` : the name of the modified trait attribute.

        If ``None``, then nothing is assigned.
    style : `str` (see below), optional
        Sets a predefined style at the widget. Possible options are:

            ============= ==================
            Style         Description
            ============= ==================
            ``'success'`` Green-based style
            ``'info'``    Blue-based style
            ``'warning'`` Yellow-based style
            ``'danger'``  Red-based style
            ``''``        No style
            ============= ==================

    Example
    -------
    Let's create a patches widget and then update its state. Firstly, we need
    to import it:

        >>> from menpowidgets.options import PatchOptionsWidget

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected patches and bboxes flag:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(change):
        >>>     s = "Patches: {}, BBoxes: {}".format(
        >>>         wid.selected_values['patches']['indices'],
        >>>         wid.selected_values['bboxes']['render_lines'])
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> wid = PatchOptionsWidget(n_patches=68, n_offsets=5,
        >>>                          render_function=render_function,
        >>>                          style='info', suboptions_style='danger')
        >>> wid

    By playing around with the widget, printed message gets updated. Finally,
    let's change the widget status with a new set of options:

        >>> wid.set_widget_state(n_patches=49, n_offsets=1, allow_callback=False)

    Remember that the widget is **mnemonic**, i.e. it remembers the objects it
    has seen and their corresponding options. These can be retrieved as:

        >>> wid.default_options

    """
    def __init__(self, n_patches, n_offsets, render_function=None, style=''):
        # Initialise default options dictionary
        self.default_options = {}

        # Assign properties
        self.n_offsets = n_offsets
        self.n_patches = n_patches

        # Create children
        slice_options = {'command': "range({})".format(n_patches),
                         'length': n_patches}
        self.slicing_wid = SlicingCommandWidget(
            slice_options, description='Patches',
            orientation='vertical', example_visible=True,
            continuous_update=False)
        self.offset_title = ipywidgets.Label(value='Offset')
        self.offset_dropdown = ipywidgets.Dropdown(
            options={'0': 0}, value=0, description='', width='2cm')
        self.background_title = ipywidgets.Label(value='Background')
        self.background_toggle = ipywidgets.ToggleButton(
            description='white', value=True, width='2cm')
        self.render_centers_checkbox = SwitchWidget(
            selected_value=True, description='Render centres',
            description_location='right', switch_type='checkbox')
        self.render_patches_checkbox = SwitchWidget(
            selected_value=True, description='Render patches',
            description_location='right', switch_type='checkbox')
        self.render_bbox_checkbox = SwitchWidget(
            selected_value=True, description='Render bounding boxes',
            description_location='right', switch_type='checkbox')
        self.bboxes_line_width_title = ipywidgets.Label(value='Line width')
        self.bboxes_line_width_text = ipywidgets.BoundedFloatText(
            value=1, min=0., max=10**6, width='2.2cm')
        self.bboxes_line_style_title = ipywidgets.Label(value='Line style')
        line_style_dict = OrderedDict()
        line_style_dict['solid'] = '-'
        line_style_dict['dashed'] = '--'
        line_style_dict['dash-dot'] = '-.'
        line_style_dict['dotted'] = ':'
        self.bboxes_line_style_dropdown = ipywidgets.Dropdown(
            options=line_style_dict, value='-', width='2.2cm')
        self.bboxes_line_colour_widget = ColourSelectionWidget(
            'red', description='Line colour')
        self.bboxes_line_colour_widget.colour_widget.layout.width = '2.2cm'

        # Group widgets
        self.slicing_wid.layout.margin = '0px 10px 0px 0px'
        self.box_1 = ipywidgets.HBox([self.offset_title, self.offset_dropdown])
        self.box_1.layout.align_items = 'center'
        self.box_2 = ipywidgets.HBox([self.background_title,
                                      self.background_toggle])
        self.box_2.layout.align_items = 'center'
        self.box_3 = ipywidgets.HBox([self.bboxes_line_width_title,
                                      self.bboxes_line_width_text])
        self.box_3.layout.align_items = 'center'
        self.box_4 = ipywidgets.HBox([self.bboxes_line_style_title,
                                      self.bboxes_line_style_dropdown])
        self.box_4.layout.align_items = 'center'
        self.box_5 = ipywidgets.VBox([
            self.box_3, self.bboxes_line_colour_widget, self.box_4])
        self.box_5.layout.align_items = 'flex-end'
        self.box_7 = ipywidgets.VBox([self.render_patches_checkbox,
                                      self.render_centers_checkbox,
                                      self.render_bbox_checkbox])
        self.box_7.layout.margin = '0px 10px 0px 0px'
        self.box_7.layout.align_items = 'flex-start'
        self.box_8 = ipywidgets.VBox([self.box_1, self.box_2])
        self.box_8.layout.align_items = 'flex-end'
        self.box_8.layout.margin = '0px 15px 0px 0px'
        self.container = ipywidgets.HBox([self.slicing_wid, self.box_8,
                                          self.box_7, self.box_5])

        # Create final widget
        super(PatchOptionsWidget, self).__init__(
            [self.container], Dict, {}, render_function=render_function)

        # Set functions
        def change_toggle_description(change):
            if change['new']:
                self.background_toggle.description = 'white'
            else:
                self.background_toggle.description = 'black'
        self.background_toggle.observe(change_toggle_description, names='value',
                                       type='change')

        def line_options_visibility(change):
            self.box_5.layout.display = (
                'flex' if self.render_bbox_checkbox.selected_values else 'none')
        self.render_bbox_checkbox.observe(
            line_options_visibility, names='selected_values', type='change')

        # Set values
        self.add_callbacks()
        self.set_widget_state(n_patches, n_offsets, allow_callback=False)

        # Set style
        self.predefined_style(style)

    def add_callbacks(self):
        r"""
        Function that adds the handler callback functions in all the widget
        components, which are necessary for the internal functionality.
        """
        self.slicing_wid.observe(
            self._save_options, names='selected_values', type='change')
        self.offset_dropdown.observe(
            self._save_options, names='value', type='change')
        self.background_toggle.observe(
            self._save_options, names='value', type='change')
        self.render_patches_checkbox.observe(
            self._save_options, names='selected_values', type='change')
        self.render_centers_checkbox.observe(
            self._save_options, names='selected_values', type='change')
        self.render_bbox_checkbox.observe(
            self._save_options, names='selected_values', type='change')
        self.bboxes_line_width_text.observe(
            self._save_options, names='value', type='change')
        self.bboxes_line_style_dropdown.observe(
            self._save_options, names='value', type='change')
        self.bboxes_line_colour_widget.observe(
            self._save_options, names='selected_values', type='change')

    def remove_callbacks(self):
        r"""
        Function that removes all the internal handler callback functions.
        """
        self.slicing_wid.unobserve(
            self._save_options, names='selected_values', type='change')
        self.offset_dropdown.unobserve(
            self._save_options, names='value', type='change')
        self.background_toggle.unobserve(
            self._save_options, names='value', type='change')
        self.render_patches_checkbox.unobserve(
            self._save_options, names='selected_values', type='change')
        self.render_centers_checkbox.unobserve(
            self._save_options, names='selected_values', type='change')
        self.render_bbox_checkbox.unobserve(
            self._save_options, names='selected_values', type='change')
        self.bboxes_line_width_text.unobserve(
            self._save_options, names='value', type='change')
        self.bboxes_line_style_dropdown.unobserve(
            self._save_options, names='value', type='change')
        self.bboxes_line_colour_widget.unobserve(
            self._save_options, names='selected_values', type='change')

    def _save_options(self, change):
        # set background attributes
        self.background_toggle.description = (
            'white' if self.background_toggle.value else 'black')
        # update selected values
        self.selected_values = {
            'patches_indices': self.slicing_wid.selected_values,
            'offset_index': int(self.offset_dropdown.value),
            'background': self.background_toggle.description,
            'render_patches': self.render_patches_checkbox.selected_values,
            'render_centers': self.render_centers_checkbox.selected_values,
            'render_patches_bboxes': self.render_bbox_checkbox.selected_values,
            'bboxes_line_colour':
                self.bboxes_line_colour_widget.selected_values[0],
            'bboxes_line_style': self.bboxes_line_style_dropdown.value,
            'bboxes_line_width': self.bboxes_line_width_text.value}
        # update default values
        current_key = self.get_key(self.n_patches, self.n_offsets)
        self.default_options[current_key] = self.selected_values.copy()

    def get_key(self, n_patches, n_offsets):
        r"""
        Function that returns a unique key based on the properties of the
        provided patches object.

        Parameters
        ----------
        n_patches : `int`
            The number of patches.
        n_offsets : `int`
            The number of offsets.

        Returns
        -------
        key : `str`
            The key that has the format ``'{n_patches}_{n_offsets}'``.
        """
        return "{}_{}".format(n_patches, n_offsets)

    def get_default_options(self, n_patches, n_offsets):
        r"""
        Function that returns a `dict` with default options given the properties
        of a patches object, i.e. `n_patches` and `n_offsets`. The function
        returns the `dict` of options but also updates the
        ``self.default_options`` `dict`.

        Parameters
        ----------
        n_patches : `int`
            The number of patches.
        n_offsets : `int`
            The number of offsets.

        Returns
        -------
        default_options : `dict`
            A `dict` with the default options. It contains:

            * ``patches_indices`` : (`list` or `int`) The selected patches.
            * ``offset_index`` : (`int`) The selected offset.
            * ``background`` : (`str`) The background colour.
            * ``render_patches`` : (`bool`) Whether to render the patches.
            * ``render_patches_bboxes`` : (`bool`) Whether to render boxes around the
              patches.
            * ``bboxes_line_colour`` : (`list`) The boxes line colour.
            * ``bboxes_line_style`` : (`str`) The boxes line style.
            * ``bboxes_line_width`` : (`float`) The boxes line width.
            * ``render_centers`` : (`bool`) Whether to render the patches centers

            If the object is not seen before by the widget, then it automatically
            gets the following default options:

            * ``patches_indices = list(range(n_patches))``
            * ``offset_index = 0``
            * ``background = 'white'``
            * ``render_patches = True``
            * ``render_patches_bboxes = True``
            * ``bboxes_line_colour = ['red']``
            * ``bboxes_line_style = '-'``
            * ``bboxes_line_width = 1``
            * ``render_centers = True``

        """
        # create key
        key = self.get_key(n_patches, n_offsets)
        # if the key does not exist in the default options dict, then add it
        if key not in self.default_options:
            # update default options dictionary
            self.default_options[key] = {
                'patches_indices': list(range(n_patches)), 'offset_index': 0,
                'background': 'white', 'render_patches': True,
                'render_patches_bboxes': True, 'bboxes_line_colour': ['red'],
                'bboxes_line_style': '-', 'bboxes_line_width': 1,
                'render_centers': True}
        return self.default_options[key]

    def predefined_style(self, style):
        r"""
        Function that sets a predefined style on the widget.

        Parameters
        ----------
        style : `str` (see below)
            Style options:

                ============= ==================
                Style         Description
                ============= ==================
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ==================
        """
        self.container.box_style = style
        self.slicing_wid.single_slider.slider_color = \
            map_styles_to_hex_colours(style)
        self.slicing_wid.multiple_slider.slider_color = \
            map_styles_to_hex_colours(style)

    def set_widget_state(self, n_patches, n_offsets, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the key generated with
        :meth:`get_key` based on the provided `n_patches` and `n_offsets`
        is different than the current key based on ``self.n_patches`` and
        ``self.n_offsets``.

        Parameters
        ----------
        n_patches : `int`
            The number of patches.
        n_offsets : `int`
            The number of offsets.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # keep old value
        old_value = self.selected_values

        # check if updates are required
        if (not self.default_options or
                self.get_key(self.n_patches, self.n_offsets) !=
                self.get_key(n_patches, n_offsets)):
            # temporarily remove callbacks
            render_function = self._render_function
            self.remove_render_function()
            self.remove_callbacks()

            # Assign properties
            self.n_patches = n_patches
            self.n_offsets = n_offsets

            # Get initial options
            patch_options = self.get_default_options(n_patches, n_offsets)

            # Update widgets' state
            offsets_dict = OrderedDict()
            for i in range(self.n_offsets):
                offsets_dict[str(i)] = i
            self.offset_dropdown.options = offsets_dict
            self.offset_dropdown.value = patch_options['offset_index']
            self.render_patches_checkbox.set_widget_state(
                patch_options['render_patches'], allow_callback=False)
            self.render_centers_checkbox.set_widget_state(
                patch_options['render_centers'], allow_callback=False)
            self.background_toggle.description = patch_options['background']
            self.background_toggle.value = \
                patch_options['background'] == 'white'
            if lists_are_the_same(patch_options['patches_indices'],
                                  range(self.n_patches)):
                cmd = 'range({})'.format(self.n_patches)
            else:
                cmd = str(patch_options['patches_indices'])
            slice_options = {'command': cmd, 'length': self.n_patches}
            self.slicing_wid.set_widget_state(slice_options,
                                              allow_callback=False)
            self.render_bbox_checkbox.set_widget_state(
                patch_options['render_patches_bboxes'], allow_callback=False)
            self.bboxes_line_width_text.value = \
                patch_options['bboxes_line_width']
            self.bboxes_line_style_dropdown.value = \
                patch_options['bboxes_line_style']
            self.bboxes_line_colour_widget.set_widget_state(
                patch_options['bboxes_line_colour'], allow_callback=False)

            # Get values
            self._save_options({})

            # Re-assign callbacks
            self.add_callbacks()
            self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self.call_render_function(old_value, self.selected_values)


class PlotOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting options for rendering various curves in a
    graph. The widget consists of the following objects from `ipywidgets` and
    :ref:`api-tools-index`:

    == ========================== ====================== =====================
    No Object                     Property (`self.`)     Description
    == ========================== ====================== =====================
    1  :map:`LineMatplotlibOptionsWidget`   `lines_wid`            Line options widget
    2  :map:`MarkerMatplotlibOptionsWidget` `markers_wid`          Marker options widget
    3  `Dropdown`                 `curves_dropdown`      Curve selector
    4  `Tab`                      `lines_markers_tab`    Contains 1, 2
    5  `VBox`                     `lines_markers_box`    Contains 3, 4
    6  :map:`LegendOptionsWidget` `legend_wid`           Legend options widget
    7  :map:`AxesOptionsWidget`   `axes_wid`             Axes options widget
    8  :map:`ZoomTwoScalesWidget` `zoom_wid`             Zoom options widget
    9  :map:`GridOptionsWidget`   `grid_wid`             Grid options widget
    10 `Text`                     `x_label`              X label text
    11 `Text`                     `y_label`              Y label text
    12 `Text`                     `title`                Title text
    13 `Textarea`                 `legend_entries_text`  Legend entries text
    14 `VBox`                     `plot_related_options` Contains 10 - 13
    15 `Tab`                      `options_tab`          Contains 14, 5 - 9
    == ========================== ====================== =====================

    Note that:

    * The widget has **memory** about the properties of the objects that are
      passed into it through `legend_entries`.
    * The selected values of the current object object are stored in the
      ``self.selected_values`` `trait`.
    * To set the styling of this widget please refer to the :meth:`style` and
      :meth:`predefined_style` methods.
    * To update the handler callback function of the widget, please refer to the
      :meth:`replace_render_function` method.

    Parameters
    ----------
    legend_entries : `list` of `str`
        The `list` of legend entries per curve.
    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        It must have signature ``render_function(change)`` where ``change`` is
        a `dict` with the following keys:

        * ``type`` : The type of notification (normally ``'change'``).
        * ``owner`` : the `HasTraits` instance
        * ``old`` : the old value of the modified trait attribute
        * ``new`` : the new value of the modified trait attribute
        * ``name`` : the name of the modified trait attribute.

        If ``None``, then nothing is assigned.
    style : `str` (see below), optional
        Sets a predefined style at the widget. Possible options are:

            ============= ============================
            Style         Description
            ============= ============================
            ``'minimal'`` Simple black and white style
            ``'success'`` Green-based style
            ``'info'``    Blue-based style
            ``'warning'`` Yellow-based style
            ``'danger'``  Red-based style
            ``''``        No style
            ============= ============================

    tabs_style : `str` (see below), optional
        Sets a predefined style at the tabs of the widget. Possible options are:

            ============= ============================
            Style         Description
            ============= ============================
            ``'minimal'`` Simple black and white style
            ``'success'`` Green-based style
            ``'info'``    Blue-based style
            ``'warning'`` Yellow-based style
            ``'danger'``  Red-based style
            ``''``        No style
            ============= ============================

    Example
    -------
    Let's create a plot options widget. Firstly, we need to import it:

        >>> from menpowidgets.options import PlotOptionsWidget

    Let's set some legend entries:

        >>> legend_entries = ['method_1', 'method_2']

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected marker face colour and line
    width:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(change):
        >>>     s = "Marker edge colours: {}, Line widths: {}".format(
        >>>         wid.selected_values['marker_edge_colour'],
        >>>         wid.selected_values['line_width'])
        >>>     print_dynamic(s)

    Create the widget with the initial options and display it:

        >>> wid = PlotOptionsWidget(legend_entries,
        >>>                         render_function=render_function,
        >>>                         style='danger', tabs_style='info')
        >>> wid

    By playing around, the printed message gets updated. The style of the widget
    can be changed as:

        >>> wid.predefined_style('minimal', 'info')

    """
    def __init__(self, legend_entries, render_function=None, style='minimal',
                 tabs_style='minimal'):
        # Assign properties
        self.legend_entries = legend_entries
        self.n_curves = len(legend_entries)

        # Create default options
        default_options = self.create_default_options()

        # Create children
        self.lines_wid = LineMatplotlibOptionsWidget(
            {'render_lines': default_options['render_lines'][0],
             'line_width': default_options['line_width'][0],
             'line_colour': [default_options['line_colour'][0]],
             'line_style': default_options['line_style'][0]},
            render_function=None, render_checkbox_title='Render lines',
            labels=None)
        self.markers_wid = MarkerMatplotlibOptionsWidget(
            {'render_markers': default_options['render_markers'][0],
             'marker_style': default_options['marker_style'][0],
             'marker_size': default_options['marker_size'][0],
             'marker_face_colour': [default_options['marker_face_colour'][0]],
             'marker_edge_colour': [default_options['marker_edge_colour'][0]],
             'marker_edge_width': default_options['marker_edge_width'][0]},
            render_function=None, render_checkbox_title='Render markers',
            labels=None)
        curves_dict = {}
        for i, s in enumerate(self.legend_entries):
            curves_dict[s] = i
        self.curves_dropdown = ipywidgets.Dropdown(
            description='Curve: ', options=curves_dict, value=0)
        self.lines_markers_tab = ipywidgets.Tab(
            children=[self.lines_wid, self.markers_wid], margin='0.2cm')
        self.lines_markers_tab.set_title(0, 'Lines')
        self.lines_markers_tab.set_title(1, 'Markers')
        self.lines_markers_box = ipywidgets.VBox(
            children=[self.curves_dropdown, self.lines_markers_tab],
            align='start')
        self.legend_wid = LegendOptionsWidget(
            {'render_legend': default_options['render_legend'],
             'legend_title': default_options['legend_title'],
             'legend_font_name': default_options['legend_font_name'],
             'legend_font_style': default_options['legend_font_style'],
             'legend_font_size': default_options['legend_font_size'],
             'legend_font_weight': default_options['legend_font_weight'],
             'legend_marker_scale': default_options['legend_marker_scale'],
             'legend_location': default_options['legend_location'],
             'legend_bbox_to_anchor': default_options['legend_bbox_to_anchor'],
             'legend_border_axes_pad': default_options['legend_border_axes_pad'],
             'legend_n_columns': default_options['legend_n_columns'],
             'legend_horizontal_spacing': default_options['legend_horizontal_spacing'],
             'legend_vertical_spacing': default_options['legend_vertical_spacing'],
             'legend_border': default_options['legend_border'],
             'legend_border_padding': default_options['legend_border_padding'],
             'legend_shadow': default_options['legend_shadow'],
             'legend_rounded_corners': default_options['legend_rounded_corners']},
            render_function=None, render_checkbox_title='Render legend')
        self.axes_wid = AxesOptionsWidget(
            {'render_axes': default_options['render_axes'],
             'axes_font_name': default_options['axes_font_name'],
             'axes_font_size': default_options['axes_font_size'],
             'axes_font_style': default_options['axes_font_style'],
             'axes_font_weight': default_options['axes_font_weight'],
             'axes_x_limits': default_options['axes_x_limits'],
             'axes_y_limits': default_options['axes_y_limits'],
             'axes_x_ticks': default_options['axes_x_ticks'],
             'axes_y_ticks': default_options['axes_y_ticks']},
            render_function=None, render_checkbox_title='Render axes')
        self.zoom_wid = ZoomTwoScalesWidget(
            {'zoom': default_options['zoom'], 'min': 0.1, 'max': 4.,
             'step': 0.05, 'lock_aspect_ratio': False}, render_function=None,
            description='Scale: ', continuous_update=False)
        self.grid_wid = GridOptionsWidget(
            {'render_grid': default_options['render_grid'],
             'grid_line_width': default_options['grid_line_width'],
             'grid_line_style': default_options['grid_line_style']},
            render_function=None, render_checkbox_title='Render grid')
        self.x_label = ipywidgets.Text(description='X label', margin='0.05cm',
                                       value=default_options['x_label'])
        self.y_label = ipywidgets.Text(description='Y label', margin='0.05cm',
                                       value=default_options['y_label'])
        self.title = ipywidgets.Text(description='Title', margin='0.05cm',
                                     value=default_options['title'])
        self.legend_entries_text = ipywidgets.Textarea(
            description='Legend', width='73mm', margin='0.05cm',
            value=self._convert_list_to_legend_entries(self.legend_entries))
        self.plot_related_options = ipywidgets.VBox(
            children=[self.x_label, self.y_label, self.title,
                      self.legend_entries_text])

        # Group widgets
        self.options_tab = ipywidgets.Tab(
            children=[self.plot_related_options, self.lines_markers_box,
                      self.legend_wid, self.axes_wid, self.zoom_wid,
                      self.grid_wid])
        self.options_tab.set_title(0, 'Figure')
        self.options_tab.set_title(1, 'Renderer')
        self.options_tab.set_title(2, 'Legend')
        self.options_tab.set_title(3, 'Axes')
        self.options_tab.set_title(4, 'Zoom')
        self.options_tab.set_title(5, 'Grid')

        # Create final widget
        children = [self.options_tab]
        super(PlotOptionsWidget, self).__init__(
            children, Dict, default_options, render_function=render_function,
            orientation='vertical', align='start')

        # Set style
        self.predefined_style(style, tabs_style)

        # Set functionality
        def get_legend_entries(change):
            # get legend entries
            tmp_entries = str(self.legend_entries_text.value).splitlines()
            if len(tmp_entries) < self.n_curves:
                n_missing = self.n_curves - len(tmp_entries)
                for j in range(n_missing):
                    kk = j + len(tmp_entries)
                    tmp_entries.append("curve {}".format(kk))
            self.legend_entries = tmp_entries[:self.n_curves]
            # update dropdown menu
            curves_dir = {}
            for j, le in enumerate(self.legend_entries):
                curves_dir[le] = j
            self.curves_dropdown.options = curves_dir
            if self.curves_dropdown.value == 0 and self.n_curves > 1:
                self.curves_dropdown.value = 1
            self.curves_dropdown.value = 0
        self.legend_entries_text.observe(get_legend_entries, names='value',
                                         type='change')

        def save_options(change):
            # get lines and markers options
            k = self.curves_dropdown.value
            render_lines = list(self.selected_values['render_lines'])
            render_lines[k] = self.lines_wid.selected_values['render_lines']
            line_colour = list(self.selected_values['line_colour'])
            line_colour[k] = self.lines_wid.selected_values['line_colour'][0]
            line_style = list(self.selected_values['line_style'])
            line_style[k] = self.lines_wid.selected_values['line_style']
            line_width = list(self.selected_values['line_width'])
            line_width[k] = self.lines_wid.selected_values['line_width']
            render_markers = list(self.selected_values['render_markers'])
            render_markers[k] = self.markers_wid.selected_values['render_markers']
            marker_style = list(self.selected_values['marker_style'])
            marker_style[k] = self.markers_wid.selected_values['marker_style']
            marker_size = list(self.selected_values['marker_size'])
            marker_size[k] = self.markers_wid.selected_values['marker_size']
            marker_face_colour = list(self.selected_values['marker_face_colour'])
            marker_face_colour[k] = self.markers_wid.selected_values['marker_face_colour'][0]
            marker_edge_colour = list(self.selected_values['marker_edge_colour'])
            marker_edge_colour[k] = self.markers_wid.selected_values['marker_edge_colour'][0]
            marker_edge_width = list(self.selected_values['marker_edge_width'])
            marker_edge_width[k] = self.markers_wid.selected_values['marker_edge_width']
            self.selected_values = {
                'legend_entries': self.legend_entries,
                'title': str(self.title.value),
                'x_label': str(self.x_label.value),
                'y_label': str(self.y_label.value),
                'render_lines': render_lines, 'line_colour': line_colour,
                'line_style': line_style, 'line_width': line_width,
                'render_markers': render_markers, 'marker_style': marker_style,
                'marker_size': marker_size,
                'marker_face_colour': marker_face_colour,
                'marker_edge_colour': marker_edge_colour,
                'marker_edge_width': marker_edge_width,
                'render_legend': self.legend_wid.selected_values['render_legend'],
                'legend_title': self.legend_wid.selected_values['legend_title'],
                'legend_font_name': self.legend_wid.selected_values['legend_font_name'],
                'legend_font_style': self.legend_wid.selected_values['legend_font_style'],
                'legend_font_size': self.legend_wid.selected_values['legend_font_size'],
                'legend_font_weight': self.legend_wid.selected_values['legend_font_weight'],
                'legend_marker_scale': self.legend_wid.selected_values['legend_marker_scale'],
                'legend_location': self.legend_wid.selected_values['legend_location'],
                'legend_bbox_to_anchor': self.legend_wid.selected_values['legend_bbox_to_anchor'],
                'legend_border_axes_pad': self.legend_wid.selected_values['legend_border_axes_pad'],
                'legend_n_columns': self.legend_wid.selected_values['legend_n_columns'],
                'legend_horizontal_spacing': self.legend_wid.selected_values['legend_horizontal_spacing'],
                'legend_vertical_spacing': self.legend_wid.selected_values['legend_vertical_spacing'],
                'legend_border': self.legend_wid.selected_values['legend_border'],
                'legend_border_padding': self.legend_wid.selected_values['legend_border_padding'],
                'legend_shadow': self.legend_wid.selected_values['legend_shadow'],
                'legend_rounded_corners': self.legend_wid.selected_values['legend_rounded_corners'],
                'render_axes': self.axes_wid.selected_values['render_axes'],
                'axes_font_name': self.axes_wid.selected_values['axes_font_name'],
                'axes_font_size': self.axes_wid.selected_values['axes_font_size'],
                'axes_font_style': self.axes_wid.selected_values['axes_font_style'],
                'axes_font_weight': self.axes_wid.selected_values['axes_font_weight'],
                'axes_x_limits': self.axes_wid.selected_values['axes_x_limits'],
                'axes_y_limits': self.axes_wid.selected_values['axes_y_limits'],
                'axes_x_ticks': self.axes_wid.selected_values['axes_x_ticks'],
                'axes_y_ticks': self.axes_wid.selected_values['axes_y_ticks'],
                'zoom': self.zoom_wid.selected_values,
                'render_grid': self.grid_wid.selected_values['render_grid'],
                'grid_line_style': self.grid_wid.selected_values['grid_line_style'],
                'grid_line_width': self.grid_wid.selected_values['grid_line_width']}
        self.title.observe(save_options, names='value', type='change')
        self.x_label.observe(save_options, names='value', type='change')
        self.y_label.observe(save_options, names='value', type='change')
        self.legend_entries_text.observe(save_options, names='value',
                                         type='change')
        self.lines_wid.observe(save_options, names='selected_values',
                               type='change')
        self.markers_wid.observe(save_options, names='selected_values',
                                 type='change')
        self.axes_wid.observe(save_options, names='selected_values',
                              type='change')
        self.legend_wid.observe(save_options, names='selected_values',
                                type='change')
        self.grid_wid.observe(save_options, names='selected_values',
                              type='change')
        self.zoom_wid.observe(save_options, names='selected_values',
                              type='change')

        def update_lines_markers(change):
            k = self.curves_dropdown.value

            # remove save options callback
            self.lines_wid.unobserve(save_options, names='selected_values',
                                     type='change')
            self.markers_wid.unobserve(save_options, names='selected_values',
                                       type='change')

            # update lines
            self.lines_wid.set_widget_state(
                {'render_lines': self.selected_values['render_lines'][k],
                 'line_width': self.selected_values['line_width'][k],
                 'line_colour': [self.selected_values['line_colour'][k]],
                 'line_style': self.selected_values['line_style'][k]},
                labels=None, allow_callback=False)
            # update markers
            self.markers_wid.set_widget_state(
                {'render_markers': self.selected_values['render_markers'][k],
                 'marker_style': self.selected_values['marker_style'][k],
                 'marker_size': self.selected_values['marker_size'][k],
                 'marker_face_colour': [self.selected_values['marker_face_colour'][k]],
                 'marker_edge_colour': [self.selected_values['marker_edge_colour'][k]],
                 'marker_edge_width': self.selected_values['marker_edge_width'][k]},
                labels=None, allow_callback=False)

            # add save options callback
            self.lines_wid.observe(save_options, names='selected_values',
                                   type='change')
            self.markers_wid.observe(save_options, names='selected_values',
                                     type='change')
        self.curves_dropdown.observe(update_lines_markers, names='value',
                                     type='change')

    def create_default_options(self):
        r"""
        Function that returns a `dict` with default options. The returned
        `dict` has the following default keys and values:

        * ``title = ''``
        * ``x_label = ''``
        * ``y_label = ''``
        * ``render_legend = True``
        * ``legend_title = ''``
        * ``legend_font_name = 'sans-serif'``
        * ``legend_font_style = 'normal'``
        * ``legend_font_size = 10``
        * ``legend_font_weight = 'normal'``
        * ``legend_marker_scale = 1.``
        * ``legend_location = 2``
        * ``legend_bbox_to_anchor = (1.05, 1.)``
        * ``legend_border_axes_pad = 1.``
        * ``legend_n_columns = 1``
        * ``legend_horizontal_spacing = 1.``
        * ``legend_vertical_spacing = 1.``
        * ``legend_border = True``
        * ``legend_border_padding = 0.5``
        * ``legend_shadow = False``
        * ``legend_rounded_corners = False``
        * ``render_axes = True``
        * ``axes_font_name = 'sans-serif'``
        * ``axes_font_size = 10``
        * ``axes_font_style = 'normal'``
        * ``axes_font_weight = 'normal'``
        * ``axes_x_limits = None``
        * ``axes_y_limits = None``
        * ``axes_x_ticks = None``
        * ``axes_y_ticks = None``
        * ``render_grid = True``
        * ``grid_line_style = '--'``
        * ``grid_line_width = 0.5``
        * ``render_lines = [True] * self.n_curves``
        * ``line_width = [1] * self.n_curves``
        * ``line_colour = colours if self.n_curves > 1 else ['red']``
        * ``line_style = ['-'] * self.n_curves``
        * ``render_markers = [True] * self.n_curves``
        * ``marker_size = [7] * self.n_curves``
        * ``marker_face_colour = ['white'] * self.n_curves``
        * ``marker_edge_colour = colours if self.n_curves > 1 else ['red']``
        * ``marker_style = ['s'] * self.n_curves``
        * ``marker_edge_width = [2.] * self.n_curves``
        * ``zoom = [1., 1.]``

        where ``colours = sample_colours_from_colourmap(self.n_curves, 'Paired')``.
        """
        render_lines = [True] * self.n_curves
        line_style = ['-'] * self.n_curves
        line_width = [1] * self.n_curves
        render_markers = [True] * self.n_curves
        marker_style = ['s'] * self.n_curves
        marker_size = [7] * self.n_curves
        marker_face_colour = ['white'] * self.n_curves
        marker_edge_width = [2.] * self.n_curves
        line_colour = ['red']
        marker_edge_colour = ['red']
        if self.n_curves > 1:
            line_colour = sample_colours_from_colourmap(self.n_curves, 'Paired')
            marker_edge_colour = sample_colours_from_colourmap(
                self.n_curves, 'Paired')
        return {'title': '', 'x_label': '', 'y_label': '', 'render_legend': True,
                'legend_entries': self.legend_entries,
                'legend_title': '', 'legend_font_name': 'sans-serif',
                'legend_font_style': 'normal', 'legend_font_size': 10,
                'legend_font_weight': 'normal', 'legend_marker_scale': 1.,
                'legend_location': 2, 'legend_bbox_to_anchor': (1.05, 1.),
                'legend_border_axes_pad': 1., 'legend_n_columns': 1,
                'legend_horizontal_spacing': 1., 'legend_vertical_spacing': 1.,
                'legend_border': True, 'legend_border_padding': 0.5,
                'legend_shadow': False, 'legend_rounded_corners': False,
                'render_axes': True, 'axes_font_name': 'sans-serif',
                'axes_font_size': 10, 'axes_font_style': 'normal',
                'axes_font_weight': 'normal', 'axes_x_limits': 0.,
                'axes_y_limits': 0., 'axes_x_ticks': None,
                'axes_y_ticks': None, 'render_grid': True,
                'grid_line_style': '--', 'grid_line_width': 0.5,
                'render_lines': render_lines, 'line_width': line_width,
                'line_colour': line_colour, 'line_style': line_style,
                'render_markers': render_markers, 'marker_size': marker_size,
                'marker_face_colour': marker_face_colour,
                'marker_edge_colour': marker_edge_colour,
                'marker_style': marker_style,
                'marker_edge_width': marker_edge_width, 'zoom': [1., 1.]}

    def _convert_list_to_legend_entries(self, l):
        tmp_lines = []
        for k in l:
            tmp_lines.append(k)
            tmp_lines.append('\n')
        tmp_lines = tmp_lines[:-1]
        return unicode().join(tmp_lines)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0,
              padding='0.2cm', margin=0, tabs_box_style=None,
              tabs_border_visible=True, tabs_border_colour='black',
              tabs_border_style='solid', tabs_border_width=1,
              tabs_border_radius=1, tabs_padding=0, tabs_margin=0,
              font_family='', font_size=None, font_style='', font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Possible widget style options::

                'success', 'info', 'warning', 'danger', '', None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        tabs_box_style : See Below, optional
            Possible tab widgets style options::

                'success', 'info', 'warning', 'danger', '', None

        tabs_border_visible : `bool`, optional
            Defines whether to draw the border line around the tab widgets.
        tabs_border_colour : `str`, optional
            The colour of the border around the tab widgets.
        tabs_border_style : `str`, optional
            The line style of the border around the tab widgets.
        tabs_border_width : `float`, optional
            The line width of the border around the tab widgets.
        tabs_border_radius : `float`, optional
            The radius of the corners of the box of the tab widgets.
        tabs_padding : `float`, optional
            The padding around the tab widgets.
        tabs_margin : `float`, optional
            The margin around the tab widgets.
        font_family : `str` (see below), optional
            The font family to be used. Example options::

                'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                'helvetica'

        font_size : `int`, optional
            The font size.
        font_style : `str` (see below), optional
            The font style. Example options::

                'normal', 'italic', 'oblique'

        font_weight : See Below, optional
            The font weight. Example options::

                'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                'extra bold', 'black'
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_box(self.lines_markers_box, box_style=tabs_box_style,
                   border_visible=tabs_border_style,
                   border_colour=tabs_border_colour,
                   border_style=tabs_border_style,
                   border_width=tabs_border_width,
                   border_radius=tabs_border_radius, padding=tabs_padding,
                   margin=tabs_margin)
        format_box(self.plot_related_options, box_style=tabs_box_style,
                   border_visible=tabs_border_style,
                   border_colour=tabs_border_colour,
                   border_style=tabs_border_style,
                   border_width=tabs_border_width,
                   border_radius=tabs_border_radius, padding=tabs_padding,
                   margin=tabs_margin)
        self.lines_wid.style(
            box_style=tabs_box_style, border_visible=False, padding=0,
            margin=0, font_family=font_family, font_size=font_size,
            font_weight=font_weight, font_style=font_style)
        self.markers_wid.style(
            box_style=tabs_box_style, border_visible=False, padding=0,
            margin=0, font_family=font_family, font_size=font_size,
            font_weight=font_weight, font_style=font_style)
        self.legend_wid.style(
            box_style=tabs_box_style, border_visible=tabs_border_visible,
            border_colour=tabs_border_colour, border_style=tabs_border_style,
            border_width=tabs_border_width, border_radius=tabs_border_radius,
            padding=tabs_padding, margin=tabs_margin, font_family=font_family,
            font_size=font_size, font_weight=font_weight, font_style=font_style)
        self.zoom_wid.style(
            box_style=tabs_box_style, border_visible=tabs_border_visible,
            border_colour=tabs_border_colour, border_style=tabs_border_style,
            border_width=tabs_border_width, border_radius=tabs_border_radius,
            padding=tabs_padding, margin=tabs_margin, font_family=font_family,
            font_size=font_size, font_weight=font_weight, font_style=font_style)
        self.axes_wid.style(
            box_style=tabs_box_style, border_visible=tabs_border_visible,
            border_colour=tabs_border_colour, border_style=tabs_border_style,
            border_width=tabs_border_width, border_radius=tabs_border_radius,
            padding=tabs_padding, margin=tabs_margin, font_family=font_family,
            font_size=font_size, font_weight=font_weight, font_style=font_style)
        self.grid_wid.style(
            box_style=tabs_box_style, border_visible=tabs_border_visible,
            border_colour=tabs_border_colour, border_style=tabs_border_style,
            border_width=tabs_border_width, border_radius=tabs_border_radius,
            padding=tabs_padding, margin=tabs_margin, font_family=font_family,
            font_size=font_size, font_weight=font_weight, font_style=font_style)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.x_label, font_family, font_size, font_style,
                    font_weight)
        format_font(self.y_label, font_family, font_size, font_style,
                    font_weight)
        format_font(self.title, font_family, font_size, font_style,
                    font_weight)
        format_font(self.legend_entries_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.curves_dropdown, font_family, font_size, font_style,
                    font_weight)

    def predefined_style(self, style, tabs_style='minimal'):
        r"""
        Function that sets a predefined style on the widget.

        Parameters
        ----------
        style : `str` (see below)
            Style options:

                ============= ============================
                Style         Description
                ============= ============================
                ``'minimal'`` Simple black and white style
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ============================

        tabs_style : `str` (see below)
            Tabs style options:

                ============= ============================
                Style         Description
                ============= ============================
                ``'minimal'`` Simple black and white style
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ============================
        """
        if tabs_style == 'minimal' or tabs_style == '':
            tabs_style = ''
            tabs_border_visible = True
            tabs_border_colour = 'black'
            tabs_border_radius = 0
            tabs_padding = 0
        else:
            tabs_style = tabs_style
            tabs_border_visible = True
            tabs_border_colour = map_styles_to_hex_colours(tabs_style)
            tabs_border_radius = 10
            tabs_padding = '0.2cm'

        if style == 'minimal':
            self.style(box_style='', border_visible=True, border_colour='black',
                       border_style='solid', border_width=1, border_radius=0,
                       padding='0.2cm', margin='0.5cm', font_family='',
                       font_size=None, font_style='', font_weight='',
                       tabs_box_style=tabs_style,
                       tabs_border_visible=tabs_border_visible,
                       tabs_border_colour=tabs_border_colour,
                       tabs_border_style='solid', tabs_border_width=1,
                       tabs_border_radius=tabs_border_radius,
                       tabs_padding=tabs_padding, tabs_margin='0.3cm')
        elif (style == 'info' or style == 'success' or style == 'danger' or
                      style == 'warning'):
            self.style(box_style=style, border_visible=True,
                       border_colour=map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding='0.2cm', margin='0.5cm', font_family='',
                       font_size=None, font_style='', font_weight='',
                       tabs_box_style=tabs_style,
                       tabs_border_visible=tabs_border_visible,
                       tabs_border_colour=tabs_border_colour,
                       tabs_border_style='solid', tabs_border_width=1,
                       tabs_border_radius=tabs_border_radius,
                       tabs_padding=tabs_padding, tabs_margin='0.3cm')
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')


class LinearModelParametersWidget(MenpoWidget):
    r"""
    Creates a widget for selecting parameters values when visualizing a linear
    model (e.g. PCA model). The widget has options for animating through various
    parameters values. It consists of the following objects from `ipywidgets`:

    == ============== ====================== ========================
    No Object         Property (`self.`)     Description
    == ============== ====================== ========================
    1  `Button`       `plot_button`          The plot variance button
    2  `Button`       `reset_button`         The reset button
    3  `HBox`         `plot_and_reset`       Contains 1, 2
    4  `ToggleButton` `play_stop_toggle`     The play/stop button
    5  `Button`       `fast_forward_button`  Increase speed
    6  `Button`       `fast_backward_button` Decrease speed
    7  `ToggleButton` `loop_toggle`          Repeat mode
    8  `HBox`         `animation_buttons`    Contains 4, 5, 6, 7
    9  `HBox`         `buttons_box`          Contains 3, 8
    == ============== ====================== ========================

    If ``mode = 'single'``, then:

    == ============= ================== ==========================
    No Object        Property (`self.`) Description
    == ============= ================== ==========================
    4  `FloatSlider` `slider`           The parameter value slider
    5  `Dropdown`    `dropdown_params`  The parameter selector
    6  `HBox`        `parameters_wid`   Contains 4, 5
    == ============= ================== ==========================

    If ``mode = 'multiple'``, then:

    == ============= ================== ==========================
    No Object        Property (`self.`) Description
    == ============= ================== ==========================
    7  `FloatSlider` `sliders`          `list` of all sliders
    8  `VBox`        `parameters_wid`   Contains all 7
    == ============= ================== ==========================

    Note that:

    * To update the state of the widget, please refer to the
      :meth:`set_widget_state` method.
    * The selected values are stored in the ``self.selected_values`` `trait`
      which is a `list`.
    * To set the styling of this widget please refer to the :meth:`style` and
      :meth:`predefined_style` methods.
    * To update the handler callback functions of the widget, please refer to
      the :meth:`replace_render_function` and :meth:`replace_variance_function`
      methods.

    Parameters
    ----------
    n_parameters : `int`
        The `list` of initial parameters values.
    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        It must have signature ``render_function(change)`` where ``change`` is
        a `dict` with the following keys:

        * ``type`` : The type of notification (normally ``'change'``).
        * ``owner`` : the `HasTraits` instance
        * ``old`` : the old value of the modified trait attribute
        * ``new`` : the new value of the modified trait attribute
        * ``name`` : the name of the modified trait attribute.

        If ``None``, then nothing is assigned.
    mode : ``{'single', 'multiple'}``, optional
        If ``'single'``, only a single slider is constructed along with a
        dropdown menu that allows the parameter selection.
        If ``'multiple'``, a slider is constructed for each parameter.
    params_str : `str`, optional
        The string that will be used as description of the slider(s). The final
        description has the form ``"{}{}".format(params_str, p)``, where ``p``
        is the parameter number.
    params_bounds : (`float`, `float`), optional
        The minimum and maximum bounds, in std units, for the sliders.
    params_step : `float`, optional
        The step, in std units, of the sliders.
    plot_variance_visible : `bool`, optional
        Defines whether the button for plotting the variance will be visible
        upon construction.
    plot_variance_function : `callable` or ``None``, optional
        The plot function that is executed when the plot variance button is
        clicked. If ``None``, then nothing is assigned.
    animation_visible : `bool`, optional
        Defines whether the animation options will be visible.
    loop_enabled : `bool`, optional
        If ``True``, then the repeat mode of the animation is enabled.
    interval : `float`, optional
        The interval between the animation progress in seconds.
    interval_step : `float`, optional
        The interval step (in seconds) that is applied when fast
        forward/backward buttons are pressed.
    animation_step : `float`, optional
        The parameters step that is applied when animation is enabled.
    style : `str` (see below), optional
        Sets a predefined style at the widget. Possible options are:

            ============= ============================
            Style         Description
            ============= ============================
            ``'minimal'`` Simple black and white style
            ``'success'`` Green-based style
            ``'info'``    Blue-based style
            ``'warning'`` Yellow-based style
            ``'danger'``  Red-based style
            ``''``        No style
            ============= ============================

    continuous_update : `bool`, optional
        If ``True``, then the render function is called while moving a
        slider's handle. If ``False``, then the the function is called only
        when the handle (mouse click) is released.

    Example
    -------
    Let's create a linear model parameters values widget and then update its
    state. Firstly, we need to import it:

        >>> from menpowidgets.options import LinearModelParametersWidget

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected parameters:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(change):
        >>>     s = "Selected parameters: {}".format(wid.selected_values)
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> wid = LinearModelParametersWidget(n_parameters=5,
        >>>                                   render_function=render_function,
        >>>                                   params_str='Parameter ',
        >>>                                   mode='multiple',
        >>>                                   params_bounds=(-3., 3.),
        >>>                                   plot_variance_visible=True,
        >>>                                   style='info')
        >>> wid

    By moving the sliders, the printed message gets updated. Finally, let's
    change the widget status with a new set of options:

        >>> wid.set_widget_state(n_parameters=10, params_str='',
        >>>                      params_step=0.1, params_bounds=(-10, 10),
        >>>                      plot_variance_visible=False,
        >>>                      allow_callback=True)
    """
    def __init__(self, n_parameters, render_function=None, mode='multiple',
                 params_str='', params_bounds=(-3., 3.), params_step=0.1,
                 plot_variance_visible=True, plot_variance_function=None,
                 animation_visible=True, loop_enabled=False, interval=0.,
                 interval_step=0.05, animation_step=0.5, style='minimal',
                 continuous_update=False):
        from time import sleep
        from IPython import get_ipython

        # Get the kernel to use it later in order to make sure that the widgets'
        # traits changes are passed during a while-loop
        kernel = get_ipython().kernel

        # If only one slider requested, then set mode to multiple
        if n_parameters == 1:
            mode = 'multiple'

        # Create children
        if mode == 'multiple':
            self.sliders = [
                ipywidgets.FloatSlider(
                    description="{}{}".format(params_str, p),
                    min=params_bounds[0], max=params_bounds[1],
                    step=params_step, value=0.,
                    continuous_update=continuous_update)
                for p in range(n_parameters)]
            self.parameters_wid = ipywidgets.VBox(children=self.sliders,
                                                  margin='0.2cm')
        else:
            vals = OrderedDict()
            for p in range(n_parameters):
                vals["{}{}".format(params_str, p)] = p
            self.slider = ipywidgets.FloatSlider(
                    description='', min=params_bounds[0], max=params_bounds[1],
                    step=params_step, value=0., readout=False, margin='0.2cm',
                    continuous_update=continuous_update)
            self.dropdown_params = ipywidgets.Dropdown(options=vals,
                                                       margin='0.2cm')
            self.parameters_wid = ipywidgets.HBox(
                children=[self.dropdown_params, self.slider])
        self.plot_button = ipywidgets.Button(
            description='Variance', margin='0.05cm',
            visible=plot_variance_visible)
        self.reset_button = ipywidgets.Button(description='Reset',
                                              margin='0.05cm')
        self.plot_and_reset = ipywidgets.HBox(
                children=[self.reset_button, self.plot_button], margin='0.2cm')
        self.play_stop_toggle = ipywidgets.ToggleButton(
                icon='fa-play', description='', value=False, margin='0.05cm',
                tooltip='Play animation')
        self._toggle_play_style = '' if style == 'minimal' else 'success'
        self._toggle_stop_style = '' if style == 'minimal' else 'danger'
        self.fast_forward_button = ipywidgets.Button(
                icon='fa-fast-forward', description='', margin='0.05cm',
                tooltip='Increase animation speed')
        self.fast_backward_button = ipywidgets.Button(
                icon='fa-fast-backward', description='', margin='0.05cm',
                tooltip='Decrease animation speed')
        loop_icon = 'fa-repeat' if loop_enabled else 'fa-long-arrow-right'
        self.loop_toggle = ipywidgets.ToggleButton(
                icon=loop_icon, description='', value=loop_enabled,
                margin='0.05cm', tooltip='Repeat animation')
        self.animation_buttons = ipywidgets.HBox(
                children=[self.play_stop_toggle, self.loop_toggle,
                          self.fast_backward_button, self.fast_forward_button],
                margin='0.2cm', visible=animation_visible)
        self.buttons_box = ipywidgets.HBox(children=[self.animation_buttons,
                                                     self.plot_and_reset])
        self.options_box = ipywidgets.VBox(
                children=[self.parameters_wid, self.buttons_box], align='start')

        # Create final widget
        children = [self.options_box]
        super(LinearModelParametersWidget, self).__init__(
                children, List, [0.] * n_parameters,
                render_function=render_function, align='start')

        # Assign output
        self.n_parameters = n_parameters
        self.mode = mode
        self.params_str = params_str
        self.params_bounds = params_bounds
        self.params_step = params_step
        self.plot_variance_visible = plot_variance_visible
        self.loop_enabled = loop_enabled
        self.continuous_update = continuous_update
        self.interval = interval
        self.interval_step = interval_step
        self.animation_step = animation_step
        self.animation_visible = animation_visible

        # Set style
        self.predefined_style(style)

        # Set functionality
        if mode == 'single':
            # Assign slider value to parameters values list
            def save_slider_value(change):
                current_parameters = list(self.selected_values)
                current_parameters[self.dropdown_params.value] = change['new']
                self.selected_values = current_parameters
            self.slider.observe(save_slider_value, names='value', type='change')

            # Set correct value to slider when drop down menu value changes
            def set_slider_value(change):
                # Temporarily remove render callback
                render_fun = self._render_function
                self.remove_render_function()
                # Set slider value
                self.slider.value = self.selected_values[change['new']]
                # Re-assign render callback
                self.add_render_function(render_fun)
            self.dropdown_params.observe(set_slider_value, names='value',
                                         type='change')
        else:
            # Assign saving values and main plotting function to all sliders
            for w in self.sliders:
                w.observe(self._save_slider_value_from_id, names='value',
                          type='change')

        def reset_parameters(name):
            # Keep old value
            old_value = self.selected_values

            # Temporarily remove render callback
            render_fun = self._render_function
            self.remove_render_function()

            # Set parameters to 0
            self.selected_values = [0.0] * self.n_parameters
            if mode == 'multiple':
                for ww in self.parameters_wid.children:
                    ww.value = 0.
            else:
                self.parameters_wid.children[0].value = 0
                self.parameters_wid.children[1].value = 0.

            # Re-assign render callback and trigger it
            self.add_render_function(render_fun)
            self.call_render_function(old_value, self.selected_values)
        self.reset_button.on_click(reset_parameters)

        # Set functionality
        def play_stop_pressed(change):
            value = change['new']
            if value:
                # Animation was not playing, so Play was pressed.
                # Change the button style
                self.play_stop_toggle.button_style = self._toggle_stop_style
                # Change the icon and tooltip to Stop
                self.play_stop_toggle.icon = 'fa-stop'
                self.play_stop_toggle.tooltip = 'Stop animation'
                # Disable buttons
                self.reset_button.disabled = True
                self.plot_button.disabled = True
            else:
                # Animation was playing, so Stop was pressed.
                # Change the button style
                self.play_stop_toggle.button_style = self._toggle_play_style
                # Change the icon and tooltip to Play
                self.play_stop_toggle.icon = 'fa-play'
                self.play_stop_toggle.tooltip = 'Play animation'
                # Enable buttons
                self.reset_button.disabled = False
                self.plot_button.disabled = False
        self.play_stop_toggle.observe(play_stop_pressed, names='value',
                                      type='change')

        def loop_pressed(change):
            if change['new']:
                self.loop_toggle.icon = 'fa-repeat'
            else:
                self.loop_toggle.icon = 'fa-long-arrow-right'
            kernel.do_one_iteration()
        self.loop_toggle.observe(loop_pressed, names='value', type='change')

        def fast_forward_pressed(name):
            tmp = self.interval
            tmp -= self.interval_step
            if tmp < 0:
                tmp = 0
            self.interval = tmp
            kernel.do_one_iteration()
        self.fast_forward_button.on_click(fast_forward_pressed)

        def fast_backward_pressed(name):
            self.interval += self.interval_step
            kernel.do_one_iteration()
        self.fast_backward_button.on_click(fast_backward_pressed)

        def animate(change):
            reset_parameters('')
            if mode == 'multiple':
                n_sliders = self.n_parameters
                slider_id = 0
                while slider_id < n_sliders and self.play_stop_toggle.value:
                    # animate from 0 to min
                    slider_val = 0.
                    while (slider_val > self.params_bounds[0] and
                           self.play_stop_toggle.value):
                        # update slider value
                        slider_val -= self.animation_step

                        # set value
                        self.parameters_wid.children[slider_id].value = slider_val

                        # Run IPython iteration.
                        kernel.do_one_iteration()

                        # wait
                        sleep(self.interval)

                    # animate from min to max
                    slider_val = self.params_bounds[0]
                    while (slider_val < self.params_bounds[1] and
                           self.play_stop_toggle.value):
                        # update slider value
                        slider_val += self.animation_step

                        # set value
                        self.parameters_wid.children[slider_id].value = slider_val

                        # Run IPython iteration.
                        kernel.do_one_iteration()

                        # wait
                        sleep(self.interval)

                    # animate from max to 0
                    slider_val = self.params_bounds[1]
                    while slider_val > 0. and self.play_stop_toggle.value:
                        # update slider value
                        slider_val -= self.animation_step

                        # set value
                        self.parameters_wid.children[slider_id].value = slider_val

                        # Run IPython iteration.
                        kernel.do_one_iteration()

                        # wait
                        sleep(self.interval)

                    # reset value
                    self.parameters_wid.children[slider_id].value = 0.

                    # update slider id
                    if self.loop_toggle.value and slider_id == n_sliders - 1:
                        slider_id = 0
                    else:
                        slider_id += 1

                if not self.loop_toggle.value and slider_id >= n_sliders:
                    self.stop_animation()
            else:
                n_sliders = self.n_parameters
                slider_id = 0
                while slider_id < n_sliders and self.play_stop_toggle.value:
                    # set dropdown value
                    self.parameters_wid.children[0].value = slider_id

                    # animate from 0 to min
                    slider_val = 0.
                    while (slider_val > self.params_bounds[0] and
                               self.play_stop_toggle.value):
                        # update slider value
                        slider_val -= self.animation_step

                        # set value
                        self.parameters_wid.children[1].value = slider_val

                        # Run IPython iteration.
                        kernel.do_one_iteration()

                        # wait
                        sleep(self.interval)

                    # animate from min to max
                    slider_val = self.params_bounds[0]
                    while (slider_val < self.params_bounds[1] and
                               self.play_stop_toggle.value):
                        # update slider value
                        slider_val += self.animation_step

                        # set value
                        self.parameters_wid.children[1].value = slider_val

                        # Run IPython iteration.
                        kernel.do_one_iteration()

                        # wait
                        sleep(self.interval)

                    # animate from max to 0
                    slider_val = self.params_bounds[1]
                    while slider_val > 0. and self.play_stop_toggle.value:
                        # update slider value
                        slider_val -= self.animation_step

                        # set value
                        self.parameters_wid.children[1].value = slider_val

                        # Run IPython iteration.
                        kernel.do_one_iteration()

                        # wait
                        sleep(self.interval)

                    # reset value
                    self.parameters_wid.children[1].value = 0.

                    # update slider id
                    if self.loop_toggle.value and slider_id == n_sliders - 1:
                        slider_id = 0
                    else:
                        slider_id += 1

                if not self.loop_toggle.value and slider_id >= n_sliders:
                    self.stop_animation()
        self.play_stop_toggle.observe(animate, names='value', type='change')

        # Set plot variance function
        self._variance_function = None
        self.add_variance_function(plot_variance_function)

    def _save_slider_value_from_id(self, change):
        current_parameters = list(self.selected_values)
        description = change['owner'].description
        i = int(description[len(self.params_str)::])
        current_parameters[i] = change['new']
        self.selected_values = current_parameters

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', slider_width='', slider_handle_colour=None,
              slider_bar_colour=None, buttons_style=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Possible widget style options::

                'success', 'info', 'warning', 'danger', '', None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : `str` (see below), optional
            The font family to be used. Example options::

                'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                'helvetica'

        font_size : `int`, optional
            The font size.
        font_style : `str` (see below), optional
            The font style. Example options::

                'normal', 'italic', 'oblique'

        font_weight : See Below, optional
            The font weight. Example options::

                'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                'extra bold', 'black'

        slider_width : `str`, optional
            The width of the slider(s).
        slider_handle_colour : `str`, optional
            The colour of the handle(s) of the slider(s).
        slider_bar_colour : `str`, optional
            The bar colour of the slider(s).
        buttons_style : `str` or ``None`` (see below), optional
            Style options:

                'success', 'info', 'warning', 'danger', 'primary', '', None
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.reset_button, font_family, font_size, font_style,
                    font_weight)
        format_font(self.plot_button, font_family, font_size, font_style,
                    font_weight)
        if self.mode == 'single':
            format_slider(self.slider, slider_width=slider_width,
                          slider_handle_colour=slider_handle_colour,
                          slider_bar_colour=slider_bar_colour,
                          slider_text_visible=True)
            format_font(self.slider, font_family, font_size, font_style,
                        font_weight)
            format_font(self.dropdown_params, font_family, font_size,
                        font_style, font_weight)
        else:
            for sl in self.sliders:
                format_slider(sl, slider_width=slider_width,
                              slider_handle_colour=slider_handle_colour,
                              slider_bar_colour=slider_bar_colour,
                              slider_text_visible=True)
                format_font(sl, font_family, font_size, font_style,
                            font_weight)
        self.reset_button.button_style = buttons_style
        self.plot_button.button_style = buttons_style

    def predefined_style(self, style):
        r"""
        Function that sets a predefined style on the widget.

        Parameters
        ----------
        style : `str` (see below)
            Style options:

                ============= ============================
                Style         Description
                ============= ============================
                ``'minimal'`` Simple black and white style
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ============================
        """
        if style == 'minimal':
            self.play_stop_toggle.button_style = ''
            self.fast_forward_button.button_style = ''
            self.fast_backward_button.button_style = ''
            self.loop_toggle.button_style = ''
            self._toggle_play_style = ''
            self._toggle_stop_style = ''
            self.style(box_style=None, border_visible=True,
                       border_colour='black', border_style='solid',
                       border_width=1, border_radius=0, padding='0.2cm',
                       margin='0.3cm', font_family='', font_size=None,
                       font_style='', font_weight='', slider_width='',
                       slider_handle_colour=None, slider_bar_colour=None,
                       buttons_style='')
        elif (style == 'info' or style == 'success' or style == 'danger' or
                    style == 'warning'):
            self.play_stop_toggle.button_style = 'success'
            self.fast_forward_button.button_style = 'info'
            self.fast_backward_button.button_style = 'info'
            self.loop_toggle.button_style = 'info'
            self._toggle_play_style = 'success'
            self._toggle_stop_style = 'danger'
            self.style(box_style=style, border_visible=True,
                       border_colour=map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding='0.2cm', margin='0.3cm', font_family='',
                       font_size=None, font_style='', font_weight='',
                       slider_width='',
                       slider_handle_colour=map_styles_to_hex_colours(style),
                       slider_bar_colour=None, buttons_style='primary')
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')

    def stop_animation(self):
        r"""
        Method that stops an active annotation by setting
        ``self.play_stop_toggle.value = False``.
        """
        self.play_stop_toggle.value = False

    def add_variance_function(self, variance_function):
        r"""
        Method that adds a `variance_function()` to the `Variance` button of the
        widget. The given function is also stored in `self._variance_function`.

        Parameters
        ----------
        variance_function : `callable` or ``None``, optional
            The variance function that behaves as a callback. If ``None``,
            then nothing is added.
        """
        self._variance_function = variance_function
        if self._variance_function is not None:
            self.plot_button.on_click(self._variance_function)

    def remove_variance_function(self):
        r"""
        Method that removes the current `self._variance_function()` from
        the `Variance` button of the widget and sets
        ``self._variance_function = None``.
        """
        self.plot_button.on_click(self._variance_function, remove=True)
        self._variance_function = None

    def replace_variance_function(self, variance_function):
        r"""
        Method that replaces the current `self._variance_function()` of the
        `Variance` button of the widget with the given `variance_function()`.

        Parameters
        ----------
        variance_function : `callable` or ``None``, optional
            The variance function that behaves as a callback. If ``None``,
            then nothing happens.
        """
        # remove old function
        self.remove_variance_function()

        # add new function
        self.add_variance_function(variance_function)

    def set_widget_state(self, n_parameters=None, params_str=None,
                         params_bounds=None, params_step=None,
                         plot_variance_visible=True, animation_step=0.5,
                         allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of options.

        Parameters
        ----------
        n_parameters : `int`
            The `list` of initial parameters values.
        params_str : `str`, optional
            The string that will be used as description of the slider(s). The
            final description has the form ``"{}{}".format(params_str, p)``,
            where ``p`` is the parameter number.
        params_bounds : (`float`, `float`), optional
            The minimum and maximum bounds, in std units, for the sliders.
        params_step : `float`, optional
            The step, in std units, of the sliders.
        plot_variance_visible : `bool`, optional
            Defines whether the button for plotting the variance will be visible
            upon construction.
        animation_step : `float`, optional
            The parameters step that is applied when animation is enabled.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Keep old value
        old_value = self.selected_values

        # Temporarily remove render callback
        render_function = self._render_function
        self.remove_render_function()

        # Parse given options
        if n_parameters is None:
            n_parameters = self.n_parameters
        if params_str is None:
            params_str = ''
        if params_bounds is None:
            params_bounds = self.params_bounds
        if params_step is None:
            params_step = self.params_step

        # Set plot variance visibility
        self.plot_button.visible = plot_variance_visible
        self.animation_step = animation_step

        # Update widget
        if n_parameters == self.n_parameters:
            # The number of parameters hasn't changed
            if self.mode == 'multiple':
                for p, sl in enumerate(self.sliders):
                    sl.description = "{}{}".format(params_str, p)
                    sl.min = params_bounds[0]
                    sl.max = params_bounds[1]
                    sl.step = params_step
            else:
                self.slider.min = params_bounds[0]
                self.slider.max = params_bounds[1]
                self.slider.step = params_step
                if not params_str == '':
                    vals = OrderedDict()
                    for p in range(n_parameters):
                        vals["{}{}".format(params_str, p)] = p
                    self.dropdown_params.options = vals
        else:
            # The number of parameters has changed
            self.selected_values = [0.] * n_parameters
            if self.mode == 'multiple':
                # Create new sliders
                self.sliders = [
                    ipywidgets.FloatSlider(
                        description="{}{}".format(params_str, p),
                        min=params_bounds[0], max=params_bounds[1],
                        step=params_step, value=0.)
                    for p in range(n_parameters)]
                # Set sliders as the children of the container
                self.parameters_wid.children = self.sliders

                # Assign saving values and main plotting function to all sliders
                for w in self.sliders:
                    w.observe(self._save_slider_value_from_id, names='value',
                              type='change')

                # Set style
                if self.box_style is None:
                    self.predefined_style('minimal')
                else:
                    self.predefined_style(self.box_style)
            else:
                self.slider.min = params_bounds[0]
                self.slider.max = params_bounds[1]
                self.slider.step = params_step
                vals = OrderedDict()
                for p in range(n_parameters):
                    vals["{}{}".format(params_str, p)] = p
                if self.dropdown_params.value == 0 and n_parameters > 1:
                    self.dropdown_params.value = 1
                self.dropdown_params.value = 0
                self.dropdown_params.options = vals
                self.slider.value = 0.

        # Re-assign render callback
        self.add_render_function(render_function)

        # Assign new selected options
        self.n_parameters = n_parameters
        self.params_str = params_str
        self.params_bounds = params_bounds
        self.params_step = params_step
        self.plot_variance_visible = plot_variance_visible

        # trigger render function if allowed
        if allow_callback:
            self.call_render_function(old_value, self.selected_values)


class CameraSnapshotWidget(MenpoWidget):
    r"""
    Creates a webcam widget for taking screenshots. The widget consists of the
    following objects from `ipywidgets` and :ref:`api-tools-index`:

    == ========================= ================== ======================
    No Object                    Property (`self.`) Description
    == ========================= ================== ======================
    1  :map:`CameraWidget`       `camera_wid`       The webcam widget
    2  `Latex`                   `n_snapshots_text` Number of snapshots
    3  `Button`                  `snapshot_but`     Take snapshot button
    4  `VBox`                    `snapshot_box`     Contains 3, 2
    5  `Button`                  `close_but`        Close widget button
    8  :map:`ZoomOneScaleWidget` `zoom_widget`      Resolution controller
    9  `HBox`                    `buttons_box`      Contains 3, 5, 8
    10 `Image`                   `preview_children` List of preview images
    11 `HBox`                    `preview`          Contains all 10
    == ========================= ================== ======================

    Note that:

    * The selected values are stored in the ``self.selected_values`` `trait`.
    * To set the styling of this widget please refer to the :meth:`style` and
      :meth:`predefined_style` methods.
    * To update the handler callback function of the widget, please refer to the
      :meth:`replace_render_function` method.

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
    preview_windows_margin : `int`, optional
        The margin between the preview thumbnails in pixels.
    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        It must have signature ``render_function(change)`` where ``change`` is
        a `dict` with the following keys:

        * ``type`` : The type of notification (normally ``'change'``).
        * ``owner`` : the `HasTraits` instance
        * ``old`` : the old value of the modified trait attribute
        * ``new`` : the new value of the modified trait attribute
        * ``name`` : the name of the modified trait attribute.

        If ``None``, then nothing is assigned.
    style : `str` (see below), optional
        Sets a predefined style at the widget. Possible options are:

            ============= ============================
            Style         Description
            ============= ============================
            ``'minimal'`` Simple black and white style
            ``'success'`` Green-based style
            ``'info'``    Blue-based style
            ``'warning'`` Yellow-based style
            ``'danger'``  Red-based style
            ``''``        No style
            ============= ============================

    preview_style : `str` (see below), optional
        Sets a predefined style at the widget's preview box. Possible options
        are:

            ============= ============================
            Style         Description
            ============= ============================
            ``'minimal'`` Simple black and white style
            ``'success'`` Green-based style
            ``'info'``    Blue-based style
            ``'warning'`` Yellow-based style
            ``'danger'``  Red-based style
            ``''``        No style
            ============= ============================

    Example
    -------
    Let's create a webcam widget. Firstly, we need to import it:

        >>> from menpowidgets.options import CameraSnapshotWidget

    Create the widget with some initial options and display it:

        >>> wid = CameraSnapshotWidget(canvas_width=640, hd=True,
        >>>                            n_preview_windows=5,
        >>>                            preview_windows_margin=1, style='info')
        >>> wid

    By pressing the "Take snapshot" button, the snapshots appear in the
    thumbnails below the stream. The video stream can be interrupted by pressing
    the "Close" button.
    """
    javascript_exported = False

    def __init__(self, canvas_width=640, hd=True, n_preview_windows=5,
                 preview_windows_margin=3, render_function=None,
                 style='minimal', preview_style='minimal'):
        # Publish javascript - only occurs once on construction of first
        # webcam widget
        if not self.javascript_exported:
            import os.path
            from pathlib import Path
            menpowidgets_path =  Path(os.path.abspath(__file__)).parent
            with open(str(menpowidgets_path / 'js' / 'webcam.js'), 'r') as f:
                display(Javascript(data=f.read()))
            self.javascript_exported = True

        # Check arguments
        if n_preview_windows < 4:
            n_preview_windows = 4
        if preview_windows_margin < 0:
            preview_windows_margin = 0

        # Create widgets
        self.logo_wid = LogoWidget(style=style)
        self.logo_wid.margin = '0.1cm'
        self.camera_wid = CameraWidget(canvas_width=canvas_width, hd=hd)
        self.camera_wid.margin = '0.1cm'
        self.camera_logo_box = ipywidgets.VBox(
            children=[self.logo_wid, self.camera_wid], align='center')
        self.n_snapshots_text = ipywidgets.Latex(value='', margin=2,
                                                 visible=False)
        self.snapshot_but = ipywidgets.Button(
            icon='fa-camera', description='  Take Snapshot',
            tooltip='Take snapshot')
        self.snapshot_but.style = 'primary'
        self.snapshot_box = ipywidgets.VBox(
            children=[self.snapshot_but, self.n_snapshots_text],
            align='center', margin='0.1cm')
        self.close_but = ipywidgets.Button(
            icon='fa-close', description='  Close', tooltip='Close the widget',
            margin='0.1cm')
        self.zoom_widget = ZoomOneScaleWidget(
            {'min': 0.1, 'max': 2.1, 'step': 0.05, 'zoom': 1.},
            continuous_update=False)
        self.zoom_widget.title.visible = False
        self.zoom_widget.zoom_text.visible = False
        self.zoom_widget.button_plus.tooltip = 'Increase video resolution'
        self.zoom_widget.button_minus.tooltip = 'Decrease video resolution'
        self.zoom_widget.margin = '0.1cm'
        self.resolution_text = ipywidgets.Latex(
            value="{}W x {}H".format(self.camera_wid.canvas_width,
                                     self.camera_wid.canvas_height),
            margin='0.1cm')
        self.resolution_text.font_family = 'monospace'
        self.zoom_and_resolution_box = ipywidgets.HBox(
            children=[self.zoom_widget, self.resolution_text], align='center')
        self.buttons_box = ipywidgets.HBox(
            children=[self.snapshot_box, self.close_but,
                      self.zoom_and_resolution_box], align='start')
        width_per_preview = int((canvas_width - preview_windows_margin * 2 *
                                 n_preview_windows) / n_preview_windows)
        preview_children = [
            ipywidgets.Image(width=width_per_preview,
                             margin=preview_windows_margin, visible=False)
            for k in range(n_preview_windows)]
        self.preview = ipywidgets.HBox(children=preview_children, align='start',
                                       visible=False)

        # Create final widget
        children = [self.camera_logo_box, self.buttons_box, self.preview]
        super(CameraSnapshotWidget, self).__init__(
            children, List, [], render_function=render_function,
            orientation='vertical', align='center')

        # Assign properties
        self.selected_values = self.camera_wid.snapshots

        # Assign take screenshot callback
        def take_snapshot(_):
            self.camera_wid.take_snapshot = not self.camera_wid.take_snapshot
        self.snapshot_but.on_click(take_snapshot)

        # Assign close callback
        def close(_):
            self.close()
        self.close_but.on_click(close)

        # Assign preview callback
        def update_preview(_):
            # Convert image to bytes
            img = self.camera_wid.imageurl.encode('utf-8')
            img = b64decode(img[len('data:image/png;base64,'):])
            # Increase n_snapshots text
            n_snapshots = len(self.selected_values)
            if n_snapshots == 1:
                self.n_snapshots_text.value = "1 snapshot"
                self.n_snapshots_text.visible = True
                self.preview.visible = True
            else:
                self.n_snapshots_text.value = "{} snapshots".format(n_snapshots)
            # Update preview thumbnails
            if n_snapshots <= n_preview_windows:
                self.preview.children[n_snapshots-1].value = img
                self.preview.children[n_snapshots-1].visible = True
            else:
                for k in range(n_preview_windows-1):
                    self.preview.children[k].value = \
                        self.preview.children[k+1].value
                self.preview.children[n_preview_windows-1].value = img
        self.camera_wid.observe(update_preview, names='imageurl', type='change')

        # Assign zoom resolution callback
        def change_resolution(change):
            self.camera_wid.canvas_width = int(canvas_width * change['new'])
            self.resolution_text.value = "{}W x {}H".format(
                self.camera_wid.canvas_width, self.camera_wid.canvas_height)
        self.zoom_widget.observe(change_resolution, names='selected_values',
                                 type='change')

        # Assign resolution text callback
        def set_resolution_text(_):
            self.resolution_text.value = "{}W x {}H".format(
                self.camera_wid.canvas_width, self.camera_wid.canvas_height)
        self.camera_wid.observe(set_resolution_text, names='canvas_height',
                                type='change')

        # Set style
        self.predefined_style(style, preview_style)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0,
              padding='0.2cm', margin=0, preview_box_style=None,
              preview_border_visible=True, preview_border_colour='black',
              preview_border_style='solid', preview_border_width=1,
              preview_border_radius=1, preview_padding=0, preview_margin=0,
              font_family='', font_size=None, font_style='', font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : `str` or ``None`` (see below), optional
            Possible widget style options::

                'success', 'info', 'warning', 'danger', '', None

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The colour of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the border around the widget.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        preview_box_style : `str` or ``None`` (see below), optional
            Possible tab widgets style options::

                'success', 'info', 'warning', 'danger', '', None

        preview_border_visible : `bool`, optional
            Defines whether to draw the border line around the preview.
        preview_border_colour : `str`, optional
            The color of the border around the preview.
        preview_border_style : `str`, optional
            The line style of the border around the preview.
        preview_border_width : `float`, optional
            The line width of the border around the preview.
        preview_border_radius : `float`, optional
            The radius of the corners of the box of the preview.
        preview_padding : `float`, optional
            The padding around the preview box.
        preview_margin : `float`, optional
            The margin around the preview box.
        font_family : `str` (see below), optional
            The font family to be used. Example options::

                'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                'helvetica'

        font_size : `int`, optional
            The font size.
        font_style : `str` (see below), optional
            The font style. Example options::

                'normal', 'italic', 'oblique'

        font_weight : See Below, optional
            The font weight. Example options::

                'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                'extra bold', 'black'
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_box(self.preview, preview_box_style, preview_border_visible,
                   preview_border_colour, preview_border_style,
                   preview_border_width, preview_border_radius, preview_padding,
                   preview_margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.preview, font_family, font_size, font_style,
                    font_weight)

    def predefined_style(self, style, preview_style='minimal'):
        r"""
        Function that sets a predefined style on the widget.

        Parameters
        ----------
        style : `str` (see below)
            Style options:

                ============= ============================
                Style         Description
                ============= ============================
                ``'minimal'`` Simple black and white style
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ============================

        preview_style : `str` (see below)
            Preview box style options:

                ============= ============================
                Style         Description
                ============= ============================
                ``'minimal'`` Simple black and white style
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ============================
        """
        if preview_style == 'minimal' or preview_style == '':
            preview_style = ''
            preview_border_visible = True
            preview_border_colour = 'black'
            preview_border_radius = 0
            preview_padding = 0
        else:
            preview_style = preview_style
            preview_border_visible = not style == preview_style
            preview_border_colour = map_styles_to_hex_colours(preview_style)
            preview_border_radius = 10
            preview_padding = '0.3cm'

        if style == 'minimal':
            self.snapshot_but.button_style = ''
            self.close_but.button_style = ''
            self.zoom_widget.button_minus.button_style = ''
            self.zoom_widget.button_plus.button_style = ''
            self.resolution_text.color = map_styles_to_hex_colours(
                'minimal', background=False)
            self.n_snapshots_text.color = map_styles_to_hex_colours(
                'minimal', background=False)
            format_slider(self.zoom_widget.zoom_slider, slider_width='2cm',
                          slider_handle_colour=map_styles_to_hex_colours('minimal'),
                          slider_bar_colour=map_styles_to_hex_colours('minimal'),
                          slider_text_visible=False)
            self.style(box_style='', border_visible=False,
                       border_colour='black', border_style='solid',
                       border_width=1, border_radius=0, padding=0, margin=0,
                       font_family='', font_size=None, font_style='',
                       font_weight='', preview_box_style=preview_style,
                       preview_border_visible=preview_border_visible,
                       preview_border_colour=preview_border_colour,
                       preview_border_style='solid', preview_border_width=1,
                       preview_border_radius=preview_border_radius,
                       preview_padding=preview_padding, preview_margin='0.1cm')
        elif (style == 'info' or style == 'success' or style == 'danger' or
                      style == 'warning'):
            self.snapshot_but.button_style = 'primary'
            self.close_but.button_style = 'danger'
            self.zoom_widget.button_minus.button_style = 'warning'
            self.zoom_widget.button_plus.button_style = 'warning'
            self.resolution_text.color = map_styles_to_hex_colours(
                'warning', background=False)
            self.n_snapshots_text.color = map_styles_to_hex_colours(
                'info', background=False)
            format_slider(self.zoom_widget.zoom_slider, slider_width='2cm',
                          slider_handle_colour=map_styles_to_hex_colours('warning'),
                          slider_bar_colour=map_styles_to_hex_colours('warning'),
                          slider_text_visible=False)
            self.style(box_style=style, border_visible=True,
                       border_colour=map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding=0, margin=0, font_family='',
                       font_size=None, font_style='', font_weight='',
                       preview_box_style=preview_style,
                       preview_border_visible=preview_border_visible,
                       preview_border_colour=preview_border_colour,
                       preview_border_style='solid', preview_border_width=1,
                       preview_border_radius=preview_border_radius,
                       preview_padding=preview_padding, preview_margin='0.1cm')
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')
