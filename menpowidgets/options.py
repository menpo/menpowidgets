import ipywidgets
from traitlets.traitlets import Int, Dict, List
from traitlets import link
from collections import OrderedDict
import numpy as np

from menpo.compatibility import unicode

from .abstract import MenpoWidget
from .tools import (IndexSliderWidget, IndexButtonsWidget, SlicingCommandWidget,
                    LineOptionsWidget, MarkerOptionsWidget,
                    NumberingOptionsWidget, LegendOptionsWidget,
                    ZoomOneScaleWidget, ZoomTwoScalesWidget, AxesOptionsWidget,
                    GridOptionsWidget, ImageOptionsWidget,
                    ColourSelectionWidget, HOGOptionsWidget, DSIFTOptionsWidget,
                    IGOOptionsWidget, LBPOptionsWidget, DaisyOptionsWidget)
from .style import (map_styles_to_hex_colours, format_box, format_font,
                    format_slider)
from .utils import sample_colours_from_colourmap


class AnimationOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for animating through a list of objects. The widget
    consists of the following objects from `ipywidgets` and
    :ref:`api-tools-index`:

    == ========================= ===================== ====================
    No Object                    Property (`self.`)    Description
    == ========================= ===================== ====================
    1  `ToggleButton`            `play_stop_toggle`    The play/stop button
    2  `ToggleButton`            `play_options_toggle` Options menu
    3  `Checkbox`                `loop_checkbox`       Repeat mode
    4  `FloatText`               `interval_text`       Interval (secs)
    5  `VBox`                    `loop_interval_box`   Contains 3, 4
    6  `HBox`                    `play_options_box`    Contains 2, 5
    7  `HBox`                    `animation_box`       Contains 1, 6
    8  :map:`IndexButtonsWidget` `index_wid`           The index selector

       :map:`IndexSliderWidget`
    == ========================= ===================== ====================

    Note that:

    * The selected values are stored in the ``self.selected_values`` `trait`.
    * To set the styling of this widget please refer to the :meth:`style` and
      :meth:`predefined_style` methods.
    * To update the state of the widget, please refer to the
      :meth:`set_widget_state` method.
    * To update the handler callback function of the widget, please refer to the
      :meth:`replace_render_function` method.

    Parameters
    ----------
    index : `dict`
        The initial options. It must be a `dict` with the following keys:

        * ``min`` : (`int`) The minimum value (e.g. ``0``).
        * ``max`` : (`int`) The maximum value (e.g. ``100``).
        * ``step`` : (`int`) The index step (e.g. ``1``).
        * ``index`` : (`int`) The index value (e.g. ``10``).

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    index_style : ``{'buttons', 'slider'}``, optional
        If ``'buttons'``, then :map:`IndexButtonsWidget` class is called. If
        ``'slider'``, then :map:`IndexSliderWidget` class is called.
    interval : `float`, optional
        The interval between the animation progress.
    description : `str`, optional
        The title of the widget.
    loop_enabled : `bool`, optional
        If ``True``, then after reach the minimum (maximum) index values, the
        counting will continue from the end (beginning). If ``False``, the
        counting will stop at the minimum (maximum) value.
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
        If ``True`` and `index_style` is set to ``'slider'``, then the render
        and update functions are called while moving the slider's handle. If
        ``False``, then the the functions are called only when the handle
        (mouse click) is released.

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
                 interval=0.2, description='Index: ', loop_enabled=True,
                 style='minimal', continuous_update=False):
        from time import sleep
        from IPython import get_ipython

        # Get the kernel to use it later in order to make sure that the widgets'
        # traits changes are passed during a while-loop
        kernel = get_ipython().kernel

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
        self.index_wid.style(box_style=None, border_visible=False,
                             padding=0, margin='0.1cm')

        # Create other widgets
        self.play_stop_toggle = ipywidgets.ToggleButton(
            icon='fa-play', description='', value=False, margin='0.1cm')
        self._toggle_play_style = 'success'
        self._toggle_stop_style = 'danger'
        if style == 'minimal':
            self._toggle_play_style = ''
            self._toggle_stop_style = ''
        self.play_options_toggle = ipywidgets.ToggleButton(
            icon='fa-wrench', description='', value=False, margin='0.1cm')
        self.loop_checkbox = ipywidgets.Checkbox(
            description='Loop', value=loop_enabled)
        self.interval_text = ipywidgets.FloatText(description='Interval (sec)',
                                                  value=interval, width='1.4cm')
        self.loop_interval_box = ipywidgets.VBox(
            children=[self.interval_text, self.loop_checkbox], visible=False,
            margin='0.1cm', padding='0.1cm', border_color='black',
            border_style='solid', border_width=1)
        self.play_options_box = ipywidgets.HBox(
            children=[self.play_options_toggle, self.loop_interval_box])
        self.animation_box = ipywidgets.HBox(
            children=[self.play_stop_toggle, self.play_options_box])

        # Create final widget
        children = [self.index_wid, self.animation_box]
        super(AnimationOptionsWidget, self).__init__(
            children, Int, index['index'], render_function=render_function,
            orientation='horizontal', align='start')

        # Assign properties
        self.min = index['min']
        self.max = index['max']
        self.step = index['step']
        self.loop_enabled = loop_enabled
        self.index_style = index_style
        self.continuous_update = continuous_update

        # Set style
        self.predefined_style(style)

        # Set functionality
        def play_stop_pressed(change):
            value = change['new']
            if value:
                # Animation was not playing, so Play was pressed.
                # Change the button style
                self.play_stop_toggle.button_style = self._toggle_stop_style
                # Change the description to Stop
                self.play_stop_toggle.icon = 'fa-stop'
                # Make sure that play options are off
                self.play_options_toggle.value = False
            else:
                # Animation was playing, so Stop was pressed.
                # Change the button style
                self.play_stop_toggle.button_style = self._toggle_play_style
                # Change the description to Play
                self.play_stop_toggle.icon = 'fa-play'
            self.play_options_toggle.disabled = value
        self.play_stop_toggle.observe(play_stop_pressed, names='value',
                                      type='change')

        def play_options_visibility(change):
            self.loop_interval_box.visible = change['new']
        self.play_options_toggle.observe(
                play_options_visibility, names='value', type='change')

        def animate(change):
            if self.loop_checkbox.value:
                # loop is enabled
                i = self.selected_values
                if i < self.max:
                    i += self.step
                else:
                    i = self.min

                while i <= self.max and self.play_stop_toggle.value:
                    # update index value
                    if index_style == 'slider':
                        self.index_wid.slider.value = i
                    else:
                        self.index_wid.index_text.value = i

                    # Run IPython iteration.
                    # This is the code that makes this operation non-blocking.
                    # This allows widget messages and callbacks to be processed.
                    kernel.do_one_iteration()

                    # update counter
                    if i < self.max:
                        i += self.step
                    else:
                        i = self.min

                    # wait
                    sleep(self.interval_text.value)
            else:
                # loop is disabled
                i = self.selected_values
                i += self.step
                while i <= self.max and self.play_stop_toggle.value:
                    # update index value
                    if index_style == 'slider':
                        self.index_wid.slider.value = i
                    else:
                        self.index_wid.index_text.value = i

                    # Run IPython iteration.
                    # This is the code that makes this operation non-blocking.
                    # This allows widget messages and callbacks to be processed.
                    kernel.do_one_iteration()

                    # update counter
                    i += self.step

                    # wait
                    sleep(self.interval_text.value)
                if i > self.max:
                    self.play_stop_toggle.value = False
        self.play_stop_toggle.observe(animate, names='value', type='change')

        def save_value(change):
            self.selected_values = self.index_wid.selected_values
        self.index_wid.observe(save_value, names='selected_values',
                               type='change')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
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
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.play_stop_toggle, font_family, font_size, font_style,
                    font_weight)
        format_font(self.play_options_toggle, font_family, font_size,
                    font_style, font_weight)
        format_font(self.loop_checkbox, font_family, font_size, font_style,
                    font_weight)
        format_font(self.interval_text, font_family, font_size, font_style,
                    font_weight)
        if self.index_style == 'buttons':
            self.index_wid.style(
                box_style=None, border_visible=False, padding=0,
                margin='0.1cm', font_family=font_family, font_size=font_size,
                font_style=font_style, font_weight=font_weight)
        else:
            self.index_wid.style(
                box_style=None, border_visible=False, padding=0,
                margin='0.1cm', font_family=font_family, font_size=font_size,
                font_style=font_style, font_weight=font_weight)

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
            self.style(box_style='', border_visible=False)
            self.play_stop_toggle.button_style = ''
            self.play_stop_toggle.font_weight = 'normal'
            self.play_options_toggle.button_style = ''
            format_box(self.loop_interval_box, '', False, 'black', 'solid', 1,
                       10, '0.1cm', '0.1cm')
            if self.index_style == 'buttons':
                self.index_wid.button_plus.button_style = ''
                self.index_wid.button_plus.font_weight = 'normal'
                self.index_wid.button_minus.button_style = ''
                self.index_wid.button_minus.font_weight = 'normal'
                self.index_wid.index_text.background_color = None
            elif self.index_style == 'slider':
                self.index_wid.slider.slider_color = None
                self.index_wid.slider.background_color = None
            self._toggle_play_style = ''
            self._toggle_stop_style = ''
        elif (style == 'info' or style == 'success' or style == 'danger' or
              style == 'warning'):
            self.style(box_style=style, border_visible=False)
            self.play_stop_toggle.button_style = 'success'
            self.play_stop_toggle.font_weight = 'bold'
            self.play_options_toggle.button_style = 'info'
            format_box(self.loop_interval_box, 'info', True,
                       map_styles_to_hex_colours('info'), 'solid', 1, 10,
                       '0.1cm', '0.1cm')
            if self.index_style == 'buttons':
                self.index_wid.button_plus.button_style = 'primary'
                self.index_wid.button_plus.font_weight = 'bold'
                self.index_wid.button_minus.button_style = 'primary'
                self.index_wid.button_minus.font_weight = 'bold'
                self.index_wid.index_text.background_color = \
                    map_styles_to_hex_colours(style, True)
            elif self.index_style == 'slider':
                self.index_wid.slider.slider_color = \
                    map_styles_to_hex_colours(style)
                self.index_wid.slider.background_color = \
                    map_styles_to_hex_colours(style)
            self._toggle_play_style = 'success'
            self._toggle_stop_style = 'danger'
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')

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
        # Check if update is required
        if (index['index'] != self.selected_values or
                    index['min'] != self.min or
                    index['max'] != self.max or
                    index['step'] != self.step):
            # Keep old value
            old_value = self.selected_values

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            if self.play_stop_toggle.value:
                self.play_stop_toggle.value = False
            if self.index_style == 'slider':
                self.index_wid.set_widget_state(index, allow_callback=False)
            else:
                self.index_wid.set_widget_state(
                    index, loop_enabled=self.loop_checkbox.value,
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


class ChannelOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting channel options for rendering an image. The
    widget consists of the following objects from `ipywidgets` and
    :ref:`api-tools-index`:

    == =========================== ======================== =====================
    No Object                      Property (`self.`)       Description
    == =========================== ======================== =====================
    1  :map:`SlicingCommandWidget` `channels_wid`           The channels selector
    2  `Checkbox`                  `masked_checkbox`        Controls masked mode
    3  `Checkbox`                  `rgb_checkbox`           View as RGB
    4  `Checkbox`                  `sum_checkbox`           View sum of channels
    5  `Checkbox`                  `glyph_checkbox`         View glyph
    6  `BoundedIntText`            `glyph_block_size_text`  Glyph block size
    7  `Checkbox`                  `glyph_use_neg_checkbox` Use negative values
    8  `Latex`                     `no_options_latex`       No options message
    9  `VBox`                      `glyph_options_box`      Contains 6, 7
    10 `HBox`                      `glyph_box`              Contains 5, 9
    11 `HBox`                      `rgb_masked_options_box` Contains 3, 2
    12 `HBox`                      `glyph_sum_options_box`  Contains 4, 10
    13 `VBox`                      `checkboxes_box`         Contains 11, 12
    == =========================== ======================== =====================

    Note that:

    * To update the state of the widget, please refer to the
      :meth:`set_widget_state` method.
    * The widget has **memory** about the properties of the objects that are
      passed into it through :meth:`set_widget_state`. Each image object has a
      unique key id assigned through :meth:`get_key`. Then, the options that
      correspond to each key are stored in the ``self.default_options`` `dict`.
    * The selected values of the current image object are stored in the
      ``self.selected_values`` `trait`. It is a `dict` with the following keys:

      * ``channels`` : (`list`) The selected channels.
      * ``glyph_enabled`` : (`bool`) Whether to render as glyph.
      * ``glyph_block_size`` : (`int`) The glyph's block size.
      * ``glyph_use_negative`` : (`bool`) Whether to use negative values in glyph
      * ``sum_enabled`` : (`bool`) Whether to render as sum of channels.
      * ``masked_enabled`` : (`bool`) Whether to render as masked.

    * When an unseen image object is passed in (i.e. a key that is not included
      in the ``self.default_options`` `dict`), it gets the following initial
      options by default:

      * ``channels = [0] if n_channels == 3 else None``
      * ``glyph_enabled = False``
      * ``glyph_block_size = 3``
      * ``glyph_use_negative = False``
      * ``sum_enabled = False``
      * ``masked_enabled = image_is_masked``

    * To set the styling of this widget please refer to the :meth:`style` and
      :meth:`predefined_style` methods.
    * To update the handler callback function of the widget, please refer to the
      :meth:`replace_render_function` method.

    Parameters
    ----------
    n_channels : `int`
        The number of channels of the initial image object.
    image_is_masked : `bool`
        Whether the initial image object is masked or not. If ``True``, then the
        image is assumed to be a `menpo.image.MaskedImage` object.
    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
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

    Example
    -------
    Let's create a channels widget and then update its state. Firstly, we need
    to import it:

        >>> from menpowidgets.options import ChannelOptionsWidget

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected channels and masked flag:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(change):
        >>>     s = "Channels: {}, Masked: {}, Glyph: {}, Sum: {}".format(
        >>>         wid.selected_values['channels'],
        >>>         wid.selected_values['masked_enabled'],
        >>>         wid.selected_values['glyph_enabled'],
        >>>         wid.selected_values['sum_enabled'])
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> wid = ChannelOptionsWidget(n_channels=30, image_is_masked=True,
        >>>                            render_function=render_function,
        >>>                            style='warning')
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
            slice_options, description='Channels:', render_function=None,
            example_visible=True, continuous_update=False,
            orientation='horizontal')
        self.masked_checkbox = ipywidgets.Checkbox(description='Masked',
                                                   margin='0.1cm')
        self.rgb_checkbox = ipywidgets.Checkbox(description='RGB',
                                                margin='0.1cm')
        self.sum_checkbox = ipywidgets.Checkbox(description='Sum',
                                                margin='0.1cm')
        self.glyph_checkbox = ipywidgets.Checkbox(description='Glyph',
                                                  margin='0.1cm')
        self.glyph_block_size_text = ipywidgets.BoundedIntText(
            description='Block size', min=1, max=25, width='1.5cm')
        self.glyph_use_negative_checkbox = ipywidgets.Checkbox(
            description='Negative')
        self.no_options_latex = ipywidgets.Latex(value='No options available')

        # Group widgets
        self.glyph_options_box = ipywidgets.VBox(
            children=[self.glyph_block_size_text,
                      self.glyph_use_negative_checkbox], margin='0.1cm',
            visible=False)
        self.glyph_box = ipywidgets.HBox(children=[self.glyph_checkbox,
                                                   self.glyph_options_box],
                                         align='start')
        self.rgb_masked_options_box = ipywidgets.HBox(
            children=[self.rgb_checkbox, self.masked_checkbox])
        self.glyph_sum_options_box = ipywidgets.HBox(
            children=[self.sum_checkbox, self.glyph_box])
        self.checkboxes_box = ipywidgets.VBox(
            children=[self.rgb_masked_options_box, self.glyph_sum_options_box])

        # Create final widget
        children = [self.channels_wid, self.checkboxes_box,
                    self.no_options_latex]
        super(ChannelOptionsWidget, self).__init__(
            children, Dict, {}, render_function=render_function,
            orientation='horizontal', align='start')

        # Set values
        self.set_widget_state(n_channels, image_is_masked, allow_callback=False)

        # Set style
        self.predefined_style(style)

    def add_callbacks(self):
        r"""
        Function that adds the handler callback functions in all the widget
        components, which are necessary for the internal functionality.
        """
        self.glyph_block_size_text.observe(self._save_options, names='value',
                                           type='change')
        self.glyph_use_negative_checkbox.observe(
                self._save_options, names='value', type='change')
        self.masked_checkbox.observe(self._save_options, names='value',
                                     type='change')
        self.channels_wid.observe(self._save_channels, names='selected_values',
                                  type='change')
        self.rgb_checkbox.observe(self._save_rgb, names='value', type='change')
        self.sum_checkbox.observe(self._save_sum, names='value', type='change')
        self.glyph_checkbox.observe(self._save_glyph, names='value',
                                    type='change')

    def remove_callbacks(self):
        r"""
        Function that removes all the internal handler callback functions.
        """
        self.glyph_block_size_text.unobserve(self._save_options, names='value',
                                             type='change')
        self.glyph_use_negative_checkbox.unobserve(
                self._save_options, names='value', type='change')
        self.masked_checkbox.unobserve(self._save_options, names='value',
                                       type='change')
        self.channels_wid.unobserve(self._save_channels, names='selected_values',
                                    type='change')
        self.rgb_checkbox.unobserve(self._save_rgb, names='value', type='change')
        self.sum_checkbox.unobserve(self._save_sum, names='value', type='change')
        self.glyph_checkbox.unobserve(self._save_glyph, names='value',
                                      type='change')

    def _save_options(self, change):
        # get channels value
        channels_val = self.channels_wid.selected_values
        if self.rgb_checkbox.value:
            channels_val = None
        # update selected values
        self.selected_values = {
            'channels': channels_val,
            'glyph_enabled': self.glyph_checkbox.value,
            'glyph_block_size': self.glyph_block_size_text.value,
            'glyph_use_negative': self.glyph_use_negative_checkbox.value,
            'sum_enabled': self.sum_checkbox.value,
            'masked_enabled': self.masked_checkbox.value}
        # update default values
        current_key = self.get_key(self.n_channels, self.image_is_masked)
        self.default_options[current_key] = self.selected_values

    def _save_channels(self, change):
        if self.n_channels == 3:
            # temporarily remove rgb callback
            self.rgb_checkbox.unobserve(self._save_rgb, names='value',
                                        type='change')
            # set value
            self.rgb_checkbox.value = False
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
        if change['new'] and self.glyph_checkbox.value:
            # temporarily remove glyph callback
            self.glyph_checkbox.unobserve(self._save_glyph, names='value',
                                          type='change')

            # set glyph to False
            self.glyph_checkbox.value = False
            self.glyph_options_box.visible = False

            # re-assign glyph callback
            self.glyph_checkbox.observe(self._save_glyph, names='value',
                                        type='change')
        self._save_options({})

    def _save_glyph(self, change):
        if change['new'] and self.sum_checkbox.value:
            # temporarily remove sum callback
            self.sum_checkbox.unobserve(self._save_sum, names='value',
                                        type='change')

            # set glyph to false
            self.sum_checkbox.value = False

            # re-assign sum callback
            self.sum_checkbox.observe(self._save_sum, names='value',
                                      type='change')
        # set visibility
        self.glyph_options_box.visible = change['new']
        self._save_options({})

    def set_visibility(self):
        r"""
        Function that sets the visibility of the various components of the
        widget, depending on the properties of the current image object, i.e.
        ``self.n_channels`` and ``self.image_is_masked``.
        """
        self.channels_wid.visible = self.n_channels > 1
        self.glyph_sum_options_box.visible = self.n_channels > 1
        self.rgb_checkbox.visible = self.n_channels == 3
        self.masked_checkbox.visible = self.image_is_masked
        self.no_options_latex.visible = (self.n_channels == 1 and
                                         not self.image_is_masked)
        self.glyph_options_box.visible = self.glyph_checkbox.value

    def get_key(self, n_channels, image_is_masked):
        r"""
        Function that returns a unique key based on the properties of the
        provided image object, i.e. ``self.n_channels`` and
        ``self.image_is_masked``.

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
            A `dict` with the default options. It contains:

            * ``channels`` : (`list`) The selected channels.
            * ``glyph_enabled`` : (`bool`) Whether to render as glyph.
            * ``glyph_block_size`` : (`int`) The glyph's block size.
            * ``glyph_use_negative`` : (`bool`) Whether to use negative values.
            * ``sum_enabled`` : (`bool`) Whether to render as sum of channels.
            * ``masked_enabled`` : (`bool`) Whether to render as masked.

            If the object is not seen before by the widget, then it automatically
            gets the following default options:

            * ``channels = [0] if n_channels == 3 else None``
            * ``glyph_enabled = False``
            * ``glyph_block_size = 3``
            * ``glyph_use_negative = False``
            * ``sum_enabled = False``
            * ``masked_enabled = image_is_masked``

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
                                         'masked_enabled': masked_enabled}
        return self.default_options[key]

    def _parse_channels_value(self, channels):
        if channels is None:
            return '0, 1, 2'
        elif isinstance(channels, list):
            return str(channels).strip('[]')
        else:
            return str(channels)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', slider_width='4cm'):
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
            The width of the slider.
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        self.channels_wid.single_slider.width = slider_width
        self.channels_wid.multiple_slider.width = slider_width
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.rgb_checkbox, font_family, font_size, font_style,
                    font_weight)
        format_font(self.masked_checkbox, font_family, font_size, font_style,
                    font_weight)
        format_font(self.sum_checkbox, font_family, font_size, font_style,
                    font_weight)
        format_font(self.glyph_checkbox, font_family, font_size, font_style,
                    font_weight)
        format_font(self.glyph_block_size_text, font_family, font_size,
                    font_style, font_weight)
        format_font(self.glyph_use_negative_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.no_options_latex, font_family, font_size, font_style,
                    font_weight)
        self.channels_wid.style(
            box_style=box_style, border_visible=False, text_box_style=None,
            text_box_background_colour=None, text_box_width=None,
            font_family=font_family, font_size=font_size, font_style=font_style,
            font_weight=font_weight)

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
            self.style(box_style=None, border_visible=True,
                       border_colour='black', border_style='solid',
                       border_width=1, border_radius=0, padding='0.2cm',
                       margin='0.3cm', font_family='', font_size=None,
                       font_style='', font_weight='', slider_width='4cm')
            format_box(self.glyph_options_box, box_style='',
                       border_visible=False, border_colour='',
                       border_style='solid', border_width=1, border_radius=0,
                       padding='0.1cm', margin=0)
        elif (style == 'info' or style == 'success' or style == 'danger' or
                      style == 'warning'):
            self.style(box_style=style, border_visible=True,
                       border_colour=map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding='0.2cm', margin='0.3cm', font_family='',
                       font_size=None, font_style='', font_weight='',
                       slider_width='4cm')
            format_box(self.glyph_options_box, box_style=style,
                       border_visible=True,
                       border_colour=map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding='0.1cm', margin=0)
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')

    def set_widget_state(self, n_channels, image_is_masked, allow_callback=True):
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
        # check if updates are required
        if (not self.default_options or
                self.get_key(self.n_channels, self.image_is_masked) !=
                self.get_key(n_channels, image_is_masked)):
            # keep old value
            old_value = self.selected_values

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
            self.sum_checkbox.value = False
            self.glyph_checkbox.value = False

            # Update widgets' state
            slice_options = {'command': channels, 'length': self.n_channels}
            self.channels_wid.set_widget_state(slice_options,
                                               allow_callback=False)
            self.masked_checkbox.value = channel_options['masked_enabled']
            self.rgb_checkbox.value = (self.n_channels == 3 and
                                       channel_options['channels'] is None)
            self.sum_checkbox.value = channel_options['sum_enabled']
            self.glyph_checkbox.value = channel_options['glyph_enabled']
            self.glyph_block_size_text.value = \
                channel_options['glyph_block_size']
            self.glyph_use_negative_checkbox.value = \
                channel_options['glyph_use_negative']

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
    Creates a widget for animating through a list of objects. The widget
    consists of the following objects from `ipywidgets`:

    == ============= =========================== =========================
    No Object        Property (`self.`)               Description
    == ============= =========================== =========================
    1  Latex         `no_landmarks_msg`          Message in case there are

                                                 no landmarks available.
    2  Checkbox      `render_landmarks_checkbox` Render landmarks
    3  Latex         `group_description`         Landmark group title
    4  IntSlider     `group_slider`              Landmark group selector
    5  Dropdown      `group_dropdown`            Landmark group selector
    6  Latex         `labels_text`               Labels title
    7  ToggleButtons `labels_toggles`            `list` of `lists` with

                                                 the labels per group
    8  HBox          `group_selection_box`       Contains 3, 4, 5
    9  HBox          `labels_and_text_box`       Contains 6 and all 7
    10 VBox          `options_box`               Contains 8, 9
    11 HBox          `render_and_options_box`    Contains 2, 10
    == ============= =========================== =========================

    Note that:

    * The selected values are stored in the ``self.selected_values`` `dict`.
    * To set the styling please refer to the ``style()`` and
      ``predefined_style()`` methods.
    * To update the state of the widget, please refer to the
      ``set_widget_state()`` method.
    * To update the callback function please refer to the
      ``replace_render_function()`` and ``replace_update_function()`` methods.

    Parameters
    ----------
    landmark_options : `dict`
        The dictionary with the initial options. For example
        ::

            landmark_options = {'has_landmarks': True,
                                'render_landmarks': True,
                                'group_keys': ['PTS', 'ibug_face_68'],
                                'labels_keys': [['all'], ['jaw', 'eye']],
                                'group': 'PTS',
                                'with_labels': ['all']}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
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

    Example
    -------
    Let's create a landmarks widget and then update its state. Firstly, we need
    to import it:

        >>> from menpowidgets.options import LandmarkOptionsWidget

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected index:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(name, value):
        >>>     s = "Group: {}, Labels: {}".format(
        >>>         wid.selected_values['group'],
        >>>         wid.selected_values['with_labels'])
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> landmark_options = {'has_landmarks': True,
        >>>                     'render_landmarks': True,
        >>>                     'group_keys': ['PTS', 'ibug_face_68'],
        >>>                     'labels_keys': [['all'], ['jaw', 'eye', 'mouth']],
        >>>                     'group': 'ibug_face_68',
        >>>                     'with_labels': ['eye', 'jaw', 'mouth']}
        >>> wid = LandmarkOptionsWidget(landmark_options,
        >>>                             render_function=render_function,
        >>>                             style='danger')
        >>> wid

    By playing around with the widget, the printed message gets updated.
    Finally, let's change the widget status with a new dictionary of options:

        >>> new_options = {'has_landmarks': True,
        >>>                'render_landmarks': True,
        >>>                'group_keys': ['new_group'],
        >>>                'labels_keys': [['1', '2', '3']],
        >>>                'group': 'new_group',
        >>>                'with_labels': None}
        >>> wid.set_widget_state(new_options, allow_callback=False)
    """
    def __init__(self, group_keys, labels_keys, render_function=None,
                 renderer_widget=None, style='minimal'):
        # Initialise default options dictionary
        self.default_options = {}

        # Assign properties
        self.renderer_widget = renderer_widget
        self.style_option = style
        self.group_keys = []
        self.labels_keys = []

        # Create children
        # Render landmarks checkbox and no landmarks message
        self.no_landmarks_msg = ipywidgets.Latex(
            value='No landmarks available.')
        self.render_landmarks_checkbox = ipywidgets.Checkbox(
            description='Render landmarks', margin='0.3cm')
        # Create group description, dropdown and slider
        self.group_description = ipywidgets.Latex(value='Group', margin='0.1cm')
        self.group_slider = ipywidgets.IntSlider(
            margin='0.1cm', readout=False, width='3cm', value=0,
            continuous_update=False, min=0)
        self.group_dropdown = ipywidgets.Dropdown(
            options={'0': 0}, description='', margin='0.1cm', value=0)
        self.group_latex = ipywidgets.Latex(padding='0.2cm')
        self.group_selection_box = ipywidgets.HBox(
            children=[self.group_description, self.group_slider,
                      self.group_dropdown, self.group_latex], align='center')
        # Link the values of group dropdown and slider
        self.link_group_dropdown_and_slider = link(
            (self.group_dropdown, 'value'), (self.group_slider, 'value'))
        # Create labels
        self.labels_toggles = [[]]
        self.labels_text = ipywidgets.Latex(value='Labels')
        self.labels_box = ipywidgets.HBox(children=self.labels_toggles[0],
                                          padding='0.3cm')
        self.labels_and_text_box = ipywidgets.HBox(
            children=[self.labels_text, self.labels_box], align='center')
        self.options_box = ipywidgets.VBox(
            children=[self.group_selection_box, self.labels_and_text_box],
            margin='0.2cm')
        self.render_and_options_box = ipywidgets.HBox(
            children=[self.render_landmarks_checkbox, self.options_box])

        # Create final widget
        children = [self.render_and_options_box, self.no_landmarks_msg]
        super(LandmarkOptionsWidget, self).__init__(
            children, Dict, {}, render_function=render_function,
            orientation='horizontal', align='start')

        # Set values, add callbacks before setting widget state
        self.add_callbacks()
        self.set_widget_state(group_keys, labels_keys, allow_callback=False)

        # Set style
        self.predefined_style(style)

    def add_callbacks(self):
        self.render_landmarks_checkbox.on_trait_change(
            self._render_landmarks_fun, 'value')
        self.group_dropdown.on_trait_change(self._group_fun, 'value')
        self._add_function_to_labels_toggles(self._labels_fun)

    def remove_callbacks(self):
        self.render_landmarks_checkbox.on_trait_change(
            self._render_landmarks_fun, 'value', remove=True)
        self.group_dropdown.on_trait_change(self._group_fun, 'value',
                                            remove=True)
        self._remove_function_from_labels_toggles(self._labels_fun)

    def _save_options(self, name, value):
        if self.group_keys is None:
            self.selected_values = {
                'group': None, 'render_landmarks': False, 'with_labels': None}
        else:
            tmp_labels = self._get_with_labels()
            self.selected_values = {
                'group': self.group_keys[self.group_dropdown.value],
                'render_landmarks': self.render_landmarks_checkbox.value,
                'with_labels': tmp_labels}
            # update default values
            current_key = self.get_key(self.group_keys, self.labels_keys)
            self.default_options[current_key] = self.selected_values

    def _render_landmarks_fun(self, name, value):
        # If render is True, then check whether all the labels are disabled.
        # If they are, then enable all of them
        if value:
            if len(self._get_with_labels()) == 0:
                for ww in self.labels_box.children:
                    # temporarily remove render function
                    ww.on_trait_change(self._labels_fun, 'value', remove=True)
                    # set value
                    ww.value = True
                    # re-add render function
                    ww.on_trait_change(self._labels_fun, 'value')
        # set visibility
        self.options_box.visible = value
        # save options
        self._save_options('', None)

    def _group_fun(self, name, value):
        # assign the correct children to the labels toggles
        self.labels_box.children = self.labels_toggles[value]
        # if a renderer widget was provided, update it
        if self.renderer_widget is not None:
            self.renderer_widget.set_widget_state(self.labels_keys[value],
                                                  allow_callback=False)
        # save options
        self._save_options('', None)

    def _labels_fun(self, name, value):
        # if all labels toggles are False, set render landmarks checkbox to
        # False
        if len(self._get_with_labels()) == 0:
            # temporarily remove render function
            self.render_landmarks_checkbox.on_trait_change(
                self._render_landmarks_fun, 'value', remove=True)
            # set value
            self.render_landmarks_checkbox.value = False
            # set visibility
            self.options_box.visible = False
            # re-add render function
            self.render_landmarks_checkbox.on_trait_change(
                self._render_landmarks_fun, 'value')
        # save options
        self._save_options('', None)

    def set_visibility(self):
        self.no_landmarks_msg.visible = self.group_keys is None
        self.render_and_options_box.visible = self.group_keys is not None
        if self.group_keys is not None:
            # control group visibility
            self.group_slider.visible = len(self.group_keys) > 1
            self.group_dropdown.visible = len(self.group_keys) > 1
            self.group_latex.visible = len(self.group_keys) == 1
            # render_landmarks visibility
            self.options_box.visible = self.selected_values['render_landmarks']

    def get_key(self, group_keys, labels_keys):
        return "{}_{}".format(group_keys, labels_keys)

    def get_default_options(self, group_keys, labels_keys):
        # create key
        key = self.get_key(group_keys, labels_keys)
        # if the key does not exist in the default options dict, then add it
        if key not in self.default_options:
            if group_keys is None:
                self.default_options[key] = {'group': None,
                                             'with_labels': None,
                                             'render_landmarks': False}
            else:
                self.default_options[key] = {'group': group_keys[0],
                                             'with_labels': labels_keys[0],
                                             'render_landmarks': True}
        return self.default_options[key]

    def _get_with_labels(self):
        with_labels = []
        for ww in self.labels_box.children:
            if ww.value:
                with_labels.append(str(ww.description))
        return with_labels

    def _add_function_to_labels_toggles(self, fun):
        for s_group in self.labels_toggles:
            for w in s_group:
                w.on_trait_change(fun, 'value')

    def _remove_function_from_labels_toggles(self, fun):
        for s_group in self.labels_toggles:
            for w in s_group:
                w.on_trait_change(fun, 'value', remove=True)

    def _set_labels_toggles_values(self, with_labels):
        for w in self.labels_box.children:
            w.value = w.description in with_labels

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', labels_buttons_style=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The color of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                 'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                 'extra bold', 'black'}

        labels_buttons_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'primary' Blue-based style
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.render_landmarks_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.group_dropdown, font_family, font_size, font_style,
                    font_weight)
        format_font(self.group_description, font_family, font_size, font_style,
                    font_weight)
        for s_group in self.labels_toggles:
            for w in s_group:
                format_font(w, font_family, font_size, font_style, font_weight)
                w.button_style = labels_buttons_style
        format_font(self.labels_text, font_family, font_size, font_style,
                    font_weight)
        self.group_slider.slider_color = map_styles_to_hex_colours(
            box_style, background=False)
        self.group_slider.background_color = map_styles_to_hex_colours(
            box_style, background=False)

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
            self.style(box_style=None, border_visible=True,
                       border_colour='black', border_style='solid',
                       border_width=1, border_radius=0, padding='0.2cm',
                       margin='0.3cm', font_family='', font_size=None,
                       font_style='', font_weight='', labels_buttons_style='')
        elif (style == 'info' or style == 'success' or style == 'danger' or
                      style == 'warning'):
            self.style(box_style=style, border_visible=True,
                       border_colour=map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding='0.2cm', margin='0.3cm', font_family='',
                       font_size=None, font_style='', font_weight='',
                       labels_buttons_style='primary')
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')

    def set_widget_state(self, group_keys, labels_keys, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        landmark_options : `dict`
            The dictionary with the new options to be used. For example
            ::

                landmark_options = {'has_landmarks': True,
                                    'render_landmarks': True,
                                    'group_keys': ['PTS', 'ibug_face_68'],
                                    'labels_keys': [['all'], ['jaw', 'eye']],
                                    'group': 'PTS',
                                    'with_labels': ['all']}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
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
                self.group_latex.value = group_keys[0]
                group_idx = group_keys.index(landmark_options['group'])
                if (group_idx == self.group_dropdown.value and
                        len(group_keys) > 1):
                    if self.group_dropdown.value == 0:
                        self.group_dropdown.value = 1
                    else:
                        self.group_dropdown.value = 0
                self.group_dropdown.value = group_idx
                self.labels_toggles = [
                    [ipywidgets.ToggleButton(description=k, value=True)
                     for k in s_keys] for s_keys in labels_keys]
                self.labels_box.children = self.labels_toggles[group_idx]
                self._set_labels_toggles_values(landmark_options['with_labels'])
                self.render_landmarks_checkbox.value = \
                    landmark_options['render_landmarks']
                # if a renderer widget was provided, update it
                if self.renderer_widget is not None:
                    self.renderer_widget.set_widget_state(
                        self.labels_keys[group_idx], allow_callback=False)

            # Get values
            self._save_options('', None)

            # Set widget's visibility
            self.set_visibility()

            # Set style
            self.predefined_style(self.style_option)

            # Re-assign callbacks
            self.add_callbacks()
            self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self._render_function('', True)


class TextPrintWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for printing text. Specifically, it consists of a `list`
    of `IPython.html.widgets.Latex` objects, i.e. one per text line.

    Note that:

    * To set the styling please refer to the ``style()`` and
      ``predefined_style()`` methods.
    * To update the state of the widget, please refer to the
      ``set_widget_state()`` method.

    Parameters
    ----------
    n_lines : `int`
        The number of lines of the text to be printed.
    text_per_line : `list` of length `n_lines`
        The text to be printed per line.
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

    Example
    -------
    Let's create an text widget and then update its state. Firstly, we need
    to import it:

        >>> from menpowidgets.options import TextPrintWidget

    Create the widget with some initial options and display it:

        >>> n_lines = 3
        >>> text_per_line = ['> The', '> Menpo', '> Team']
        >>> wid = TextPrintWidget(n_lines, text_per_line, style='success')
        >>> wid

    The style of the widget can be changed as:

        >>> wid.predefined_style('danger')

    Update the widget state as:

        >>> wid.set_widget_state(5, ['M', 'E', 'N', 'P', 'O'])
    """
    def __init__(self, n_lines, text_per_line, style='minimal'):
        self.latex_texts = [ipywidgets.Latex(value=text_per_line[i])
                            for i in range(n_lines)]
        super(TextPrintWidget, self).__init__(children=self.latex_texts)
        self.align = 'start'

        # Assign options
        self.n_lines = n_lines
        self.text_per_line = text_per_line

        # Set style
        self.predefined_style(style)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The color of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                 'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                 'extra bold', 'black'}

        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        for i in range(self.n_lines):
            format_font(self.latex_texts[i], font_family, font_size,
                        font_style, font_weight)

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
            self.style(box_style=None, border_visible=True,
                       border_colour='black', border_style='solid',
                       border_width=1, border_radius=0, padding='0.1cm',
                       margin='0.3cm', font_family='', font_size=None,
                       font_style='', font_weight='')
        elif (style == 'info' or style == 'success' or style == 'danger' or
                      style == 'warning'):
            self.style(box_style=style, border_visible=True,
                       border_colour=map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding='0.1cm', margin='0.3cm', font_family='',
                       font_size=None, font_style='', font_weight='')
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')

    def set_widget_state(self, n_lines, text_per_line):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        n_lines : `int`
            The number of lines of the text to be printed.
        text_per_line : `list` of length `n_lines`
            The text to be printed per line.
        """
        # Check if n_lines has changed
        if n_lines != self.n_lines:
            self.latex_texts = [ipywidgets.Latex(value=text_per_line[i])
                                for i in range(n_lines)]
            self.children = self.latex_texts
        else:
            for i in range(n_lines):
                self.latex_texts[i].value = text_per_line[i]
        self.n_lines = n_lines
        self.text_per_line = text_per_line


class RendererOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting rendering options. The widget consists of the
    following objects from `ipywidgets` and :ref:`api-tools-index`:

    == ====================== =========================== ===================
    No Object                 Property (`self.`)          Description
    == ====================== =========================== ===================
    1  Dropdown               `object_selection_dropdown` The object selector
    2  LineOptionsWidget      `options_widgets`           `list` with the

       MarkerOptionsWidget                                various rendering

       ImageOptionsWidget                                 sub-options widgets

       NumberingOptionsWidget

       FigureOptionsWidget

       LegendOptionsWidget

       GridOptionsWidget
    3  Tab                    `suboptions_tab`            Contains all 2
    == ====================== =========================== ===================

    Note that:

    * The selected values are stored in the ``self.selected_values`` `dict`.
    * To set the styling please refer to the ``style()`` and
      ``predefined_style()`` methods.
    * To update the state of the widget, please refer to the
      ``set_widget_state()`` method.
    * To update the callback function please refer to the
      ``replace_render_function()`` methods.

    Parameters
    ----------
    renderer_options : `dict`
        The initial rendering options. For example
        ::

            lines_options = {'render_lines': True,
                             'line_width': 1,
                             'line_colour': ['b', 'r'],
                             'line_style': '-'}
            markers_options = {'render_markers': True,
                               'marker_size': 20,
                               'marker_face_colour': ['white', 'white'],
                               'marker_edge_colour': ['blue', 'red'],
                               'marker_style': 'o',
                               'marker_edge_width': 1}
            numbering_options = {'render_numbering': True,
                                 'numbers_font_name': 'serif',
                                 'numbers_font_size': 10,
                                 'numbers_font_style': 'normal',
                                 'numbers_font_weight': 'normal',
                                 'numbers_font_colour': ['black'],
                                 'numbers_horizontal_align': 'center',
                                 'numbers_vertical_align': 'bottom'}
            legend_options = {'render_legend': True,
                              'legend_title': '',
                              'legend_font_name': 'serif',
                              'legend_font_style': 'normal',
                              'legend_font_size': 10,
                              'legend_font_weight': 'normal',
                              'legend_marker_scale': 1.,
                              'legend_location': 2,
                              'legend_bbox_to_anchor': (1.05, 1.),
                              'legend_border_axes_pad': 1.,
                              'legend_n_columns': 1,
                              'legend_horizontal_spacing': 1.,
                              'legend_vertical_spacing': 1.,
                              'legend_border': True,
                              'legend_border_padding': 0.5,
                              'legend_shadow': False,
                              'legend_rounded_corners': True}
            zoom_options = {'min': 0.1,
                            'max': 4.,
                            'step': 0.05,
                            'zoom': 1.}
            axes_options = {'render_axes': True,
                            'axes_font_name': 'serif',
                            'axes_font_size': 10,
                            'axes_font_style': 'normal',
                            'axes_font_weight': 'normal',
                            'axes_x_ticks': [0, 100],
                            'axes_y_ticks': None,
                            'axes_limits': {'x': None,
                                            'y': 0.1,
                                            'x_min': 0,
                                            'x_max': 100,
                                            'x_step': 1,
                                            'y_min': 0,
                                            'y_max': 100,
                                            'y_step': 1}}
            grid_options = {'render_grid': True,
                            'grid_line_style': '--',
                            'grid_line_width': 0.5}
            image_options = {'alpha': 1.,
                             'interpolation': 'bilinear',
                             'cmap_name': 'gray'}
            renderer_options = {'lines': lines_options,
                                'markers': markers_options,
                                'numbering': numbering_options,
                                'legend': legend_options,
                                'zoom': zoom_options,
                                'axes': axes_options,
                                'grid': grid_options,
                                'image': image_options}

    options_tabs : `list` of `str`
        `List` that defines the ordering of the options tabs. Possible values
        are

            ============= ========================
            Value         Returned class
            ============= ========================
            'lines'       `LineOptionsWidget`
            'markers'     `MarkerOptionsWidget`
            'numbering'   `NumberingOptionsWidget`
            'zoom_one'    `ZoomOneScaleWidget`
            'zoom_two'    `ZoomTwoScalesWidget`
            'legend'      `LegendOptionsWidget`
            'grid'        `GridOptionsWidget`
            'image'       `ImageOptionsWidget`
            'axes'        `AxesOptionsWidget`
            ============= ========================

    labels : `list` or ``None``, optional
        The `list` of labels employed by the `ColourSelectionWidget`.
    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
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
        >>> def render_function(name, value):
        >>>     s = "Marker face colour: {}, Line width: {}".format(
        >>>         wid.selected_values['markers']['marker_face_colour'],
        >>>         wid.selected_values['lines']['line_width'])
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> markers_options = {'render_markers': True, 'marker_size': 20,
        >>>                    'marker_face_colour': ['w', 'w'],
        >>>                    'marker_edge_colour': ['b', 'r'],
        >>>                    'marker_style': 'o', 'marker_edge_width': 1}
        >>> lines_options = {'render_lines': True, 'line_width': 1,
        >>>                  'line_colour': ['b', 'r'], 'line_style': '-'}
        >>> grid_options = {'render_grid': True, 'grid_line_style': '--',
        >>>                 'grid_line_width': 0.5}
        >>> rendering_options = {'lines': lines_options, 'grid': grid_options,
        >>>                      'markers': markers_options}
        >>>
        >>> # Create and display widget
        >>> wid = RendererOptionsWidget(rendering_options, options_tabs,
        >>>                             labels=labels,
        >>>                             render_function=render_function,
        >>>                             style='info')
        >>> wid

    By playing around, the printed message gets updated. The style of the widget
    can be changed as:

        >>> wid.predefined_style('minimal', 'info')

    Finally, let's change the widget status with a new dictionary of options:

        >>> markers_options = {'render_markers': False, 'marker_size': 20,
        >>>                    'marker_face_colour': ['k'],
        >>>                    'marker_edge_colour': ['c'],
        >>>                    'marker_style': 'o', 'marker_edge_width': 1}
        >>> lines_options = {'render_lines': False, 'line_width': 1,
        >>>                  'line_colour': ['r'], 'line_style': '-'}
        >>> grid_options = {'render_grid': True, 'grid_line_style': '--',
        >>>                 'grid_line_width': 0.5}
        >>> new_options = {'lines': lines_options, 'grid': grid_options,
        >>>                'markers': markers_options}
        >>>
        >>> # Set new labels
        >>> labels = ['1']
        >>>
        >>> # Update widget state
        >>> wid.set_widget_state(new_options, labels, allow_callback=True)
    """
    def __init__(self, options_tabs, labels, axes_x_limits=None,
                 axes_y_limits=None, render_function=None,
                 style='minimal', tabs_style='minimal'):
        # Initialise default options dictionary
        self.default_options = {}
        self.global_options = {}

        # Assign properties
        self.labels = labels
        self.options_tabs = options_tabs

        # Get initial options
        self.initialise_global_options(labels, axes_x_limits, axes_y_limits)
        renderer_options = self.get_default_options(labels)

        # Create children
        self.options_widgets = []
        self.tab_titles = []
        for o in options_tabs:
            if o == 'lines':
                self.options_widgets.append(LineOptionsWidget(
                    renderer_options[o], render_function=None,
                    render_checkbox_title='Render lines', labels=labels))
                self.tab_titles.append('Lines')
            elif o == 'markers':
                self.options_widgets.append(MarkerOptionsWidget(
                    renderer_options[o], render_function=None,
                    render_checkbox_title='Render markers', labels=labels))
                self.tab_titles.append('Markers')
            elif o == 'image':
                self.options_widgets.append(ImageOptionsWidget(
                    self.global_options[o], render_function=None))
                self.tab_titles.append('Image')
            elif o == 'numbering':
                self.options_widgets.append(NumberingOptionsWidget(
                    self.global_options[o], render_function=None,
                    render_checkbox_title='Render numbering'))
                self.tab_titles.append('Numbering')
            elif o == 'zoom_two':
                tmp = {'min': 0.1, 'max': 4., 'step': 0.05,
                       'zoom': self.global_options[o]}
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
        children = [self.suboptions_tab]
        super(RendererOptionsWidget, self).__init__(
            children, Dict, initial_options, render_function=render_function,
            orientation='vertical', align='start')

        # Set values
        self.set_widget_state(labels, allow_callback=False)

        # Set style
        self.predefined_style(style, tabs_style)

        # Add callbacks
        self.add_callbacks()

    def _save_options(self, name, value):
        # update selected values
        self.selected_values = {o: self.options_widgets[i].selected_values
                                for i, o in enumerate(self.options_tabs)}
        # update default values
        current_key = self.get_key(self.labels)
        if 'lines' in self.options_tabs:
            self.default_options[current_key]['lines'] = \
                self.selected_values['lines'].copy()
        if 'markers' in self.options_tabs:
            self.default_options[current_key]['markers'] = \
                self.selected_values['markers'].copy()
        # update global values
        if 'image' in self.options_tabs:
            self.global_options['image'] = self.selected_values['image']
        if 'numbering' in self.options_tabs:
            self.global_options['numbering'] = self.selected_values['numbering']
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
        for wid in self.options_widgets:
            wid.on_trait_change(self._save_options, 'selected_values')

    def remove_callbacks(self):
        for wid in self.options_widgets:
            wid.on_trait_change(self._save_options, 'selected_values',
                                remove=True)

    def get_key(self, labels):
        return "{}".format(labels)

    def initialise_global_options(self, labels, axes_x_limits, axes_y_limits):
        self.global_options = {}
        for o in self.options_tabs:
            if o == 'image':
                self.global_options[o] = {
                    'interpolation': 'bilinear', 'cmap_name': None,
                    'alpha': 1.}
            elif o == 'numbering':
                self.global_options[o] = {
                    'render_numbering': False,
                    'numbers_font_name': 'sans-serif',
                    'numbers_font_size': 10, 'numbers_font_style': 'normal',
                    'numbers_font_weight': 'normal',
                    'numbers_font_colour': ['black'],
                    'numbers_horizontal_align': 'center',
                    'numbers_vertical_align': 'bottom'}
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
        # create key
        key = self.get_key(labels)
        # if the key does not exist in the default options dict, then add it
        if key not in self.default_options:
            self.default_options[key] = {}
            if 'lines' in self.options_tabs:
                lc = ['red']
                if labels is not None:
                    lc = sample_colours_from_colourmap(len(labels), 'jet')
                self.default_options[key]['lines'] = {
                    'render_lines': True, 'line_width': 1,
                    'line_colour': lc, 'line_style': '-'}
            if 'markers' in self.options_tabs:
                fc = ['red']
                ec = ['black']
                if labels is not None and len(labels) > 1:
                    fc = sample_colours_from_colourmap(len(labels), 'jet')
                    ec = sample_colours_from_colourmap(len(labels), 'jet')
                self.default_options[key]['markers'] = {
                    'render_markers': True, 'marker_size': 5,
                    'marker_face_colour': fc, 'marker_edge_colour': ec,
                    'marker_style': 'o', 'marker_edge_width': 1}
        return self.default_options[key]

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
        box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The color of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        tabs_box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        tabs_border_visible : `bool`, optional
            Defines whether to draw the border line around the tab widgets.
        tabs_border_colour : `str`, optional
            The color of the border around the tab widgets.
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
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                 'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                 'extra bold', 'black'}
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        for wid in self.options_widgets:
            wid.style(box_style=tabs_box_style,
                      border_visible=tabs_border_visible,
                      border_colour=tabs_border_colour,
                      border_style=tabs_border_style,
                      border_width=tabs_border_width,
                      border_radius=tabs_border_radius, padding=tabs_padding,
                      margin=tabs_margin, font_family=font_family,
                      font_size=font_size, font_style=font_style,
                      font_weight=font_weight)
        format_font(self, font_family, font_size, font_style, font_weight)

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
        if tabs_style == 'minimal' or tabs_style=='':
            tabs_style = ''
            tabs_border_visible = False
            tabs_border_colour = 'black'
            tabs_border_radius = 0
            tabs_padding = 0
        else:
            tabs_style = tabs_style
            tabs_border_visible = not style == tabs_style
            tabs_border_colour = map_styles_to_hex_colours(tabs_style)
            tabs_border_radius = 10
            tabs_padding = '0.3cm'

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
                       tabs_padding=tabs_padding, tabs_margin='0.1cm')
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
                       tabs_padding=tabs_padding, tabs_margin='0.1cm')
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')

    def set_widget_state(self, labels, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.
        Note that the number of objects should not change.

        Parameters
        ----------
        renderer_options : `dict`
            The initial rendering options. For example
            ::

                lines_options = {'render_lines': True,
                                 'line_width': 1,
                                 'line_colour': ['b', 'r'],
                                 'line_style': '-'}
                markers_options = {'render_markers': True,
                                   'marker_size': 20,
                                   'marker_face_colour': ['white', 'white'],
                                   'marker_edge_colour': ['blue', 'red'],
                                   'marker_style': 'o',
                                   'marker_edge_width': 1}
                numbering_options = {'render_numbering': True,
                                     'numbers_font_name': 'serif',
                                     'numbers_font_size': 10,
                                     'numbers_font_style': 'normal',
                                     'numbers_font_weight': 'normal',
                                     'numbers_font_colour': ['black'],
                                     'numbers_horizontal_align': 'center',
                                     'numbers_vertical_align': 'bottom'}
                legend_options = {'render_legend': True,
                                  'legend_title': '',
                                  'legend_font_name': 'serif',
                                  'legend_font_style': 'normal',
                                  'legend_font_size': 10,
                                  'legend_font_weight': 'normal',
                                  'legend_marker_scale': 1.,
                                  'legend_location': 2,
                                  'legend_bbox_to_anchor': (1.05, 1.),
                                  'legend_border_axes_pad': 1.,
                                  'legend_n_columns': 1,
                                  'legend_horizontal_spacing': 1.,
                                  'legend_vertical_spacing': 1.,
                                  'legend_border': True,
                                  'legend_border_padding': 0.5,
                                  'legend_shadow': False,
                                  'legend_rounded_corners': True}
                zoom_options = {'min': 0.1,
                                'max': 4.,
                                'step': 0.05,
                                'zoom': 1.}
                axes_options = {'render_axes': True,
                                'axes_font_name': 'serif',
                                'axes_font_size': 10,
                                'axes_font_style': 'normal',
                                'axes_font_weight': 'normal',
                                'axes_x_ticks': [0, 100],
                                'axes_y_ticks': None,
                                'axes_limits': {'x': None,
                                                'y': 0.1,
                                                'x_min': 0,
                                                'x_max': 100,
                                                'x_step': 1,
                                                'y_min': 0,
                                                'y_max': 100,
                                                'y_step': 1}}
                grid_options = {'render_grid': True,
                                'grid_line_style': '--',
                                'grid_line_width': 0.5}
                image_options = {'alpha': 1.,
                                 'interpolation': 'bilinear',
                                 'cmap_name': 'gray'}
                renderer_options = {'lines': lines_options,
                                    'markers': markers_options,
                                    'numbering': numbering_options,
                                    'legend': legend_options,
                                    'zoom': zoom_options,
                                    'axes': axes_options,
                                    'grid': grid_options,
                                    'image': image_options}

        labels : `list` or ``None``, optional
            The `list` of labels employed by the `ColourSelectionWidget`.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
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
            if 'lines' in self.options_tabs:
                i = self.options_tabs.index('lines')
                self.options_widgets[i].set_widget_state(
                    renderer_options['lines'], labels=labels,
                    allow_callback=False)
            if 'markers' in self.options_tabs:
                i = self.options_tabs.index('markers')
                self.options_widgets[i].set_widget_state(
                    renderer_options['markers'], labels=labels,
                    allow_callback=False)

            # Get values
            self._save_options('', None)

            # Add callbacks
            self.add_callbacks()
            self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self._render_function('', True)


class SaveFigureOptionsWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for saving a figure to file. The widget consists of the
    following objects from `IPython.html.widgets` and
    :ref:`api-tools-index`:

    == ===================== ====================== ==========================
    No Object                Property (`self.`)     Description
    == ===================== ====================== ==========================
    1  Select                `file_format_select`   Image format selector
    2  FloatText             `dpi_text`             DPI selector
    3  Dropdown              `orientation_dropdown` Paper orientation selector
    4  Select                `papertype_select`     Paper type selector
    5  Checkbox              `transparent_checkbox` Transparency setter
    6  ColourSelectionWidget `facecolour_widget`    Face colour selector
    7  ColourSelectionWidget `edgecolour_widget`    Edge colour selector
    8  FloatText             `pad_inches_text`      Padding in inches setter
    9  Text                  `filename_text`        Path and filename
    10 Checkbox              `overwrite_checkbox`   Overwrite flag
    11 Latex                 `error_latex`          Error message area
    12 Button                `save_button`          Save button
    13 VBox                  `path_box`             Contains 9, 1, 10, 4
    14 VBox                  `page_box`             Contains 3, 2, 8
    15 VBox                  `colour_box`           Contains 6, 7, 5
    16 Tab                   `options_tabs`         Contains 13, 14, 15
    17 HBox                  `save_box`             Contains 12, 11
    18 VBox                  `options_box`          Contains 16, 17
    == ===================== ====================== ==========================

    To set the styling please refer to the ``style()`` and
    ``predefined_style()`` methods.

    Parameters
    ----------
    renderer : :map:`Renderer` class or subclass
        The renderer object that was used to render the figure.
    file_format : `str`, optional
        The initial value of the file format.
    dpi : `float` or ``None``, optional
        The initial value of the dpi. If ``None``, then dpi is set to ``0``.
    orientation : {``'portrait'``, ``'landscape'``}, optional
        The initial value of the orientation.
    papertype : `str`, optional
        The initial value of the paper type.
        Possible options are ::

            {'letter', 'legal', 'executive', 'ledger', 'a0', 'a1', 'a2', 'a3',
             'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'a10', 'b0', 'b1', 'b2', 'b3',
             'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'b10'}

    transparent : `bool`, optional
        The initial value of the transparency flag.
    facecolour : `str` or `list` of `float`, optional
        The initial value of the face colour.
    edgecolour : `str` or `list` of `float`, optional
        The initial value of the edge colour.
    pad_inches : `float`, optional
        The initial value of the figure padding in inches.
    overwrite : `bool`, optional
        The initial value of the overwrite flag.
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
    """
    def __init__(self, renderer=None, file_format='png', dpi=None,
                 orientation='portrait', papertype='letter', transparent=False,
                 facecolour='white', edgecolour='white', pad_inches=0.,
                 overwrite=False, style='minimal'):
        from os import getcwd
        from os.path import join, splitext

        # Create widgets
        file_format_dict = OrderedDict()
        file_format_dict['png'] = 'png'
        file_format_dict['jpg'] = 'jpg'
        file_format_dict['pdf'] = 'pdf'
        file_format_dict['eps'] = 'eps'
        file_format_dict['postscript'] = 'ps'
        file_format_dict['svg'] = 'svg'
        self.file_format_select = ipywidgets.Select(
            options=file_format_dict, value=file_format, description='Format',
            width='3cm')
        if dpi is None:
            dpi = 0
        self.dpi_text = ipywidgets.FloatText(description='DPI', value=dpi,
                                             min=0.)
        orientation_dict = OrderedDict()
        orientation_dict['portrait'] = 'portrait'
        orientation_dict['landscape'] = 'landscape'
        self.orientation_dropdown = ipywidgets.Dropdown(
            options=orientation_dict, value=orientation,
            description='Orientation')
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
        self.papertype_select = ipywidgets.Select(
            options=papertype_dict, value=papertype, description='Paper type',
            visible=file_format == 'ps', width='3cm')
        self.transparent_checkbox = ipywidgets.Checkbox(
            description='Transparent', value=transparent)
        self.facecolour_widget = ColourSelectionWidget(
            [facecolour], render_function=None, description='Face colour')
        self.edgecolour_widget = ColourSelectionWidget(
            [edgecolour], render_function=None, description='Edge colour')
        self.pad_inches_text = ipywidgets.FloatText(description='Pad (inch)',
                                                    value=pad_inches)
        self.filename_text = ipywidgets.Text(
            description='Path', value=join(getcwd(), 'Untitled.' + file_format),
            width='10cm')
        self.overwrite_checkbox = ipywidgets.Checkbox(
            description='Overwrite if file exists', value=overwrite)
        self.error_latex = ipywidgets.Latex(value="", font_weight='bold',
                                            font_style='italic')
        self.save_button = ipywidgets.Button(description='  Save',
                                             icon='fa-floppy-o', margin='0.2cm')

        # Group widgets
        self.path_box = ipywidgets.VBox(
            children=[self.filename_text, self.file_format_select,
                      self.papertype_select, self.overwrite_checkbox],
            align='end', margin='0.2cm')
        self.page_box = ipywidgets.VBox(
            children=[self.orientation_dropdown, self.dpi_text,
                      self.pad_inches_text], margin='0.2cm')
        self.colour_box = ipywidgets.VBox(
            children=[self.facecolour_widget, self.edgecolour_widget,
                      self.transparent_checkbox], margin='0.2cm')
        self.options_tabs = ipywidgets.Tab(
            children=[self.path_box, self.page_box, self.colour_box],
            margin=0, padding='0.1cm')
        self.options_tabs_box = ipywidgets.VBox(
            children=[self.options_tabs], border_width=1, border_color='black',
            margin='0.3cm', padding='0.2cm')
        tab_titles = ['Path', 'Page setup', 'Image colour']
        for (k, tl) in enumerate(tab_titles):
            self.options_tabs.set_title(k, tl)
        self.save_box = ipywidgets.HBox(
            children=[self.save_button, self.error_latex], align='center')
        self.options_box = ipywidgets.VBox(
            children=[self.options_tabs, self.save_box], align='center')
        super(SaveFigureOptionsWidget, self).__init__(
            children=[self.options_box])
        self.align = 'start'

        # Assign renderer
        if renderer is None:
            from menpo.visualize.viewmatplotlib import MatplotlibImageViewer2d
            renderer = MatplotlibImageViewer2d(figure_id=None, new_figure=True,
                                               image=np.zeros((10, 10)))
        self.renderer = renderer

        # Set style
        self.predefined_style(style)

        # Set functionality
        def papertype_visibility(name, value):
            self.papertype_select.visible = value == 'ps'
        self.file_format_select.on_trait_change(papertype_visibility, 'value')

        def set_extension(name, value):
            file_name, file_extension = splitext(self.filename_text.value)
            self.filename_text.value = file_name + '.' + value
        self.file_format_select.on_trait_change(set_extension, 'value')

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
                self.renderer.save_figure(
                    filename=self.filename_text.value, dpi=selected_dpi,
                    face_colour=
                    self.facecolour_widget.selected_values[0],
                    edge_colour=
                    self.edgecolour_widget.selected_values[0],
                    orientation=self.orientation_dropdown.value,
                    paper_type=self.papertype_select.value,
                    format=self.file_format_select.value,
                    transparent=self.transparent_checkbox.value,
                    pad_inches=self.pad_inches_text.value,
                    overwrite=self.overwrite_checkbox.value)
                self.error_latex.value = ''
            except ValueError as e:
                if (e.message == 'File already exists. Please set the '
                                 'overwrite kwarg if you wish to overwrite '
                                 'the file.'):
                    self.error_latex.value = 'File exists! ' \
                                             'Tick overwrite to replace it.'
                else:
                    self.error_latex.value = e.message

            # set save button state
            self.save_button.description = '  Save'
            self.save_button.disabled = False
        self.save_button.on_click(save_function)

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The color of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                 'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                 'extra bold', 'black'}
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.file_format_select, font_family, font_size, font_style,
                    font_weight)
        format_font(self.dpi_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.orientation_dropdown, font_family, font_size,
                    font_style, font_weight)
        format_font(self.papertype_select, font_family, font_size,  font_style,
                    font_weight)
        format_font(self.transparent_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.pad_inches_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.filename_text, font_family, font_size, font_style,
                    font_weight)
        format_font(self.overwrite_checkbox, font_family, font_size, font_style,
                    font_weight)
        format_font(self.save_button, font_family, font_size, font_style,
                    font_weight)
        self.facecolour_widget.style(
            box_style=None, border_visible=False, font_family=font_family,
            font_size=font_size, font_weight=font_weight, font_style=font_style)
        self.edgecolour_widget.style(
            box_style=None, border_visible=False, font_family=font_family,
            font_size=font_size, font_weight=font_weight, font_style=font_style)

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
            self.style(box_style='', border_visible=True, border_colour='black',
                       border_style='solid', border_width=1, border_radius=0,
                       padding='0.2cm', margin='0.3cm', font_family='',
                       font_size=None, font_style='', font_weight='')
            self.save_button.button_style = ''
            self.save_button.font_weight = 'normal'
        elif (style == 'info' or style == 'success' or style == 'danger' or
                      style == 'warning'):
            self.style(box_style=style, border_visible=True,
                       border_colour= map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding='0.2cm', margin='0.3cm', font_family='',
                       font_size=None, font_style='', font_weight='')
            self.save_button.button_style = 'primary'
            self.save_button.font_weight = 'bold'
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')


class FeatureOptionsWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting feature options. Specifically, it consists
    of:

        1) RadioButtons [`self.feature_radiobuttons`]: select feature type
        2) DSIFTOptionsWidget [`self.dsift_options_widget`]: dsift options widget
        3) HOGOptionsWidget [`self.hog_options_widget`]: hog options widget
        4) IGOOptionsWidget [`self.igo_options_widget`]: igo options widget
        5) LBPOptionsWidget [`self.lbp_options_widget`]: lbp options widget
        6) DaisyOptionsWidget [`self.daisy_options_widget`]: daisy options
           widget
        7) Latex [`self.no_options_widget`]: message for no options available
        8) Box [`self.per_feature_options_box`]: box that contains (2), (3),
           (4), (5), (6) and (7)
        9) Image [`self.preview_image`]: lenna image
        10) Latex [`self.preview_input_latex`]: the initial image information
        11) Latex [`self.preview_output_latex`]: the output image information
        12) Latex [`self.preview_time_latex`]: the timing information
        13) VBox [`self.preview_box`]: box that contains (9), (10), (11), (12)
        14) Tab [`self.options_box`]: box that contains (1), (8) and (13)

    To set the styling of this widget please refer to the `style()` method. The
    widget stores the features `function` to `self.features_function`, the
    features options `dict` in `self.features_options` and the `partial`
    function with the options as `self.function`.

    Parameters
    ----------
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

    """
    def __init__(self, style='minimal'):
        # import features methods and time
        import time
        from functools import partial
        from menpo.feature import (dsift, hog, lbp, igo, es, daisy, gradient,
                                   no_op)
        from menpo.image import Image
        import menpo.io as mio
        from menpo.feature.visualize import sum_channels
        from .style import convert_image_to_bytes

        # Create widgets
        tmp = OrderedDict()
        tmp['DSIFT'] = dsift
        tmp['HOG'] = hog
        tmp['IGO'] = igo
        tmp['ES'] = es
        tmp['Daisy'] = daisy
        tmp['LBP'] = lbp
        tmp['Gradient'] = gradient
        tmp['None'] = no_op
        self.feature_radiobuttons = ipywidgets.RadioButtons(
            value=no_op, options=tmp, description='Feature type:')
        dsift_options_dict = {'window_step_horizontal': 1,
                              'window_step_vertical': 1,
                              'num_bins_horizontal': 2, 'num_bins_vertical': 2,
                              'num_or_bins': 9, 'cell_size_horizontal': 6,
                              'cell_size_vertical': 6, 'fast': True}
        self.dsift_options_widget = DSIFTOptionsWidget(dsift_options_dict)
        self.dsift_options_widget.style(box_style=None, border_visible=False,
                                        margin='0.2cm')
        hog_options_dict = {'mode': 'dense', 'algorithm': 'dalaltriggs',
                            'num_bins': 9, 'cell_size': 8, 'block_size': 2,
                            'signed_gradient': True, 'l2_norm_clip': 0.2,
                            'window_height': 1, 'window_width': 1,
                            'window_unit': 'blocks', 'window_step_vertical': 1,
                            'window_step_horizontal': 1,
                            'window_step_unit': 'pixels', 'padding': True}
        self.hog_options_widget = HOGOptionsWidget(hog_options_dict)
        self.hog_options_widget.style(box_style=None, border_visible=False,
                                      margin='0.2cm')
        igo_options_dict = {'double_angles': True}
        self.igo_options_widget = IGOOptionsWidget(igo_options_dict)
        self.igo_options_widget.style(box_style=None, border_visible=False,
                                      margin='0.2cm')
        lbp_options_dict = {'radius': list(range(1, 5)), 'samples': [8] * 4,
                            'mapping_type': 'u2', 'window_step_vertical': 1,
                            'window_step_horizontal': 1,
                            'window_step_unit': 'pixels', 'padding': True}
        self.lbp_options_widget = LBPOptionsWidget(lbp_options_dict)
        self.lbp_options_widget.style(box_style=None, border_visible=False,
                                      margin='0.2cm')
        daisy_options_dict = {'step': 1, 'radius': 15, 'rings': 2,
                              'histograms': 2, 'orientations': 8,
                              'normalization': 'l1', 'sigmas': None,
                              'ring_radii': None}
        self.daisy_options_widget = DaisyOptionsWidget(daisy_options_dict)
        self.daisy_options_widget.style(box_style=None, border_visible=False,
                                        margin='0.2cm')
        self.no_options_widget = ipywidgets.Latex(value='No options available.')

        # Load and rescale preview image (lenna)
        self.image = mio.import_builtin_asset.lenna_png()
        self.image = self.image.crop_to_landmarks_proportion(0.18)
        self.image = self.image.as_greyscale()

        # Group widgets
        self.per_feature_options_box = ipywidgets.Box(
            children=[self.dsift_options_widget, self.hog_options_widget,
                      self.igo_options_widget, self.lbp_options_widget,
                      self.daisy_options_widget, self.no_options_widget])
        self.preview_image = ipywidgets.Image(
            value=convert_image_to_bytes(self.image), visible=False)
        self.preview_input_latex = ipywidgets.Latex(
            value="Input: {}W x {}H x {}C".format(
                self.image.width, self.image.height, self.image.n_channels),
            visible=False)
        self.preview_output_latex = ipywidgets.Latex(value="")
        self.preview_time_latex = ipywidgets.Latex(value="")
        self.preview_box = ipywidgets.VBox(
            children=[self.preview_image, self.preview_input_latex,
                      self.preview_output_latex, self.preview_time_latex])
        self.options_box = ipywidgets.Tab(
            children=[self.feature_radiobuttons, self.per_feature_options_box,
                      self.preview_box])
        tab_titles = ['Feature', 'Options', 'Preview']
        for (k, tl) in enumerate(tab_titles):
            self.options_box.set_title(k, tl)
        super(FeatureOptionsWidget, self).__init__(children=[self.options_box])
        self.align = 'start'

        # Initialize output
        options = {}
        self.function = partial(no_op, **options)
        self.features_function = no_op
        self.features_options = options

        # Set style
        self.predefined_style(style)

        # Set functionality
        def per_feature_options_visibility(name, value):
            if value == dsift:
                self.igo_options_widget.visible = False
                self.lbp_options_widget.visible = False
                self.daisy_options_widget.visible = False
                self.no_options_widget.visible = False
                self.hog_options_widget.visible = False
                self.dsift_options_widget.visible = True
            elif value == hog:
                self.igo_options_widget.visible = False
                self.lbp_options_widget.visible = False
                self.daisy_options_widget.visible = False
                self.no_options_widget.visible = False
                self.dsift_options_widget.visible = False
                self.hog_options_widget.visible = True
            elif value == igo:
                self.hog_options_widget.visible = False
                self.lbp_options_widget.visible = False
                self.daisy_options_widget.visible = False
                self.no_options_widget.visible = False
                self.dsift_options_widget.visible = False
                self.igo_options_widget.visible = True
            elif value == lbp:
                self.hog_options_widget.visible = False
                self.igo_options_widget.visible = False
                self.daisy_options_widget.visible = False
                self.no_options_widget.visible = False
                self.dsift_options_widget.visible = False
                self.lbp_options_widget.visible = True
            elif value == daisy:
                self.hog_options_widget.visible = False
                self.igo_options_widget.visible = False
                self.lbp_options_widget.visible = False
                self.no_options_widget.visible = False
                self.dsift_options_widget.visible = False
                self.daisy_options_widget.visible = True
            else:
                self.hog_options_widget.visible = False
                self.igo_options_widget.visible = False
                self.lbp_options_widget.visible = False
                self.daisy_options_widget.visible = False
                self.dsift_options_widget.visible = False
                self.no_options_widget.visible = True
                for name, f in tmp.items():
                    if f == value:
                        self.no_options_widget.value = \
                            "{}: No available options.".format(name)
        self.feature_radiobuttons.on_trait_change(
            per_feature_options_visibility, 'value')
        per_feature_options_visibility('', no_op)

        def get_function(name, value):
            # get options
            if self.feature_radiobuttons.value == dsift:
                opts = self.dsift_options_widget.selected_values
            elif self.feature_radiobuttons.value == hog:
                opts = self.hog_options_widget.selected_values
            elif self.feature_radiobuttons.value == igo:
                opts = self.igo_options_widget.selected_values
            elif self.feature_radiobuttons.value == lbp:
                opts = self.lbp_options_widget.selected_values
            elif self.feature_radiobuttons.value == daisy:
                opts = self.daisy_options_widget.selected_values
            else:
                opts = {}
            # get features function closure
            func = partial(self.feature_radiobuttons.value, **opts)
            # store function
            self.function = func
            self.features_function = value
            self.features_options = opts
        self.feature_radiobuttons.on_trait_change(get_function, 'value')
        self.options_box.on_trait_change(get_function, 'selected_index')

        def preview_function(name, old_value, value):
            if value == 2:
                # extracting features message
                val1 = ''
                for name, f in tmp.items():
                    if f == self.function.func:
                        val1 = name
                self.preview_output_latex.value = \
                    'Previewing {} features...'.format(val1)
                self.preview_time_latex.value = ''
                # extract feature and time it
                t = time.time()
                feat_image = self.function(self.image)
                t = time.time() - t
                # store feature image shape and n_channels
                val2 = feat_image.width
                val3 = feat_image.height
                val4 = feat_image.n_channels
                # compute sum of feature image and normalize its pixels in range
                # (0, 1) because it is required by as_PILImage
                feat_image = sum_channels(feat_image, channels=None)
                # feat_image = np.sum(feat_image.pixels, axis=2)
                feat_image = feat_image.pixels
                feat_image -= np.min(feat_image)
                feat_image /= np.max(feat_image)
                feat_image = Image(feat_image)
                # update preview
                self.preview_image.value = convert_image_to_bytes(feat_image)
                self.preview_input_latex.visible = True
                self.preview_image.visible = True
                # set info
                self.preview_output_latex.value = \
                    "{}: {}W x {}H x {}C".format(val1, val2, val3, val4)
                self.preview_time_latex.value = "{0:.2f} secs elapsed".format(t)
            if old_value == 2:
                self.preview_input_latex.visible = False
                self.preview_image.visible = False
        self.options_box.on_trait_change(preview_function, 'selected_index')

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The color of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                 'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                 'extra bold', 'black'}
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.feature_radiobuttons, font_family, font_size,
                    font_style, font_weight)
        format_font(self.no_options_widget, font_family, font_size, font_style,
                    font_weight)
        format_font(self.preview_input_latex, font_family, font_size,
                    font_style, font_weight)
        format_font(self.preview_output_latex, font_family, font_size,
                    font_style, font_weight)
        format_font(self.preview_time_latex, font_family, font_size, font_style,
                    font_weight)
        self.dsift_options_widget.style(
            box_style=None, border_visible=False, margin='0.2cm',
            font_family=font_family, font_size=font_size, font_style=font_style,
            font_weight=font_weight)
        self.hog_options_widget.style(
            box_style=None, border_visible=False, margin='0.2cm',
            font_family=font_family, font_size=font_size, font_style=font_style,
            font_weight=font_weight)
        self.igo_options_widget.style(
            box_style=None, border_visible=False, margin='0.2cm',
            font_family=font_family, font_size=font_size, font_style=font_style,
            font_weight=font_weight)
        self.lbp_options_widget.style(
            box_style=None, border_visible=False, margin='0.2cm',
            font_family=font_family, font_size=font_size, font_style=font_style,
            font_weight=font_weight)
        self.daisy_options_widget.style(
            box_style=None, border_visible=False, margin='0.2cm',
            font_family=font_family, font_size=font_size, font_style=font_style,
            font_weight=font_weight)
        self.no_options_widget.margin = '0.2cm'

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
            self.style(box_style='', border_visible=True, border_colour='black',
                       border_style='solid', border_width=1, border_radius=0,
                       padding='0.2cm', margin='0.3cm', font_family='',
                       font_size=None, font_style='', font_weight='')
        elif (style == 'info' or style == 'success' or style == 'danger' or
                      style == 'warning'):
            self.style(box_style=style, border_visible=True,
                       border_colour= map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding='0.2cm', margin='0.3cm', font_family='',
                       font_size=None, font_style='', font_weight='')
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')


class PatchOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting patches options when rendering a patch-based
    image. The widget consists of the following objects from
    `IPython.html.widgets`:

    == ==================== ========================= ======================
    No Object               Property (`self.`)        Description
    == ==================== ========================= ======================
    1  Dropdown             `offset_dropdown`         Offset index selection
    2  SlicingCommandWidget `slicing_wid`             Patch index selection
    3  LineOptionsWidget    `bboxes_line_options_wid` Bboxes options
    4  Checkbox             `render_centers`          Render centers flag
    5  Checkbox             `render_patches`          Render patches flag
    6  ToggleButton         `background_toggle`       Background colour button
    7  Latex                `background_title`        Background colour title
    8  HBox                 `background_box`          Contains 7, 6
    9  VBox                 `render_checkboxes_box`   Contains 4, 5
    10 HBox                 `render_box`              Contains 8, 9
    11 VBox                 `offset_patches_box`      Contains 1, 2, 10
    == ==================== ========================= ======================

    Note that:

    * The selected values are stored in the ``self.selected_values`` `dict`.
    * To set the styling please refer to the ``style()`` and
      ``predefined_style()`` methods.
    * To update the state of the widget, please refer to the
      ``set_widget_state()`` method.
    * To update the callback function please refer to the
      ``replace_render_function()`` method.

    Parameters
    ----------
    patch_options : `dict`
        The dictionary with the initial options. For example
        ::

            patch_options = {'patches': {'command': '',
                                         'indices': [],
                                         'length': 68},
                             'offset_index': 0,
                             'n_offsets': 5,
                             'render_centers': True,
                             'render_centers': True,
                             'background': 'white',
                             'bboxes': {'render_lines': True,
                                        'line_colour': ['r'],
                                        'line_style': '-',
                                        'line_width': 1}
                            }

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
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

    substyle : `str` (see below), optional
        Sets a predefined style at the widget's patches and bboxes options.
        Possible options are:

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
    Let's create a patches widget and then update its state. Firstly, we need
    to import it:

        >>> from menpowidgets.options_old import PatchOptionsWidget

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected patches and bboxes flag:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(name, value):
        >>>     s = "Patches: {}, BBoxes: {}".format(
        >>>         wid.selected_values['patches']['indices'],
        >>>         wid.selected_values['bboxes']['render_lines'])
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> patch_options = {'patches': {'command': '',
        >>>                              'indices': [],
        >>>                              'length': 68},
        >>>                  'offset_index': 0,
        >>>                  'n_offsets': 5,
        >>>                  'render_centers': True,
        >>>                  'render_patches': True,
        >>>                  'background': 'white',
        >>>                  'bboxes': {'render_lines': True,
        >>>                             'line_colour': ['r'],
        >>>                             'line_style': '-',
        >>>                             'line_width': 1}
        >>>                 }
        >>> wid = PatchOptionsWidget(patch_options,
        >>>                          render_function=render_function,
        >>>                          style='info', substyle='danger')
        >>> wid

    By playing around with the widget, printed message gets updated. Finally,
    let's change the widget status with a new dictionary of options:

        >>> new_options = {'patches': {'command': '',
        >>>                            'indices': [],
        >>>                            'length':  68},
        >>>                'offset_index': 0,
        >>>                'n_offsets': 5,
        >>>                'render_centers': False,
        >>>                'render_patches': False,
        >>>                'background': 'black',
        >>>                'bboxes': {'render_lines': True,
        >>>                           'line_colour': ['r'],
        >>>                           'line_style': '-',
        >>>                           'line_width': 1}
        >>>                }
        >>> wid.set_widget_state(new_options, allow_callback=False)
    """
    def __init__(self, n_patches, n_offsets, render_function=None,
                 style='minimal', subwidgets_style='minimal'):
        # Initialise default options dictionary
        self.default_options = {}

        # Assign properties
        self.n_offsets = n_offsets
        self.n_patches = n_patches

        # Create children
        self.offset_dropdown = ipywidgets.Dropdown(
            options={'0': 0}, value=0, description='Offset:', width='2cm')
        self.render_centers_checkbox = ipywidgets.Checkbox(
            description='Render centres')
        self.render_patches_checkbox = ipywidgets.Checkbox(
            description='Render patches')
        self.background_toggle = ipywidgets.ToggleButton(
            description='white', color='#000000', value=True,
            background_color='#FFFFFF')

        def change_toggle_description(name, value):
            if value:
                self.background_toggle.description = 'white'
                self.background_toggle.background_colour = '#FFFFFF'
                self.background_toggle.color = '#000000'
            else:
                self.background_toggle.description = 'black'
                self.background_toggle.background_colour = '#000000'
                self.background_toggle.color = '#FFFFFF'
        self.background_toggle.on_trait_change(change_toggle_description,
                                               'value')

        self.background_title = ipywidgets.Latex(value='Background:',
                                                 margin='0.1cm')
        slice_options = {'command': "range({})".format(n_patches),
                         'length': n_patches}
        self.slicing_wid = SlicingCommandWidget(
            slice_options, description='Patches:',
            orientation='vertical', example_visible=True,
            continuous_update=False)
        self.bboxes_line_options_wid = LineOptionsWidget(
            {'render_lines': True, 'line_colour': ['red'], 'line_style': '-',
             'line_width': 1}, render_checkbox_title='Render bounding boxes')

        # Group widgets
        self.background_box = ipywidgets.HBox(children=[
            self.background_title, self.background_toggle], align='center',
            margin='0.5cm')
        self.render_checkboxes_box = ipywidgets.Box(children=[
            self.render_patches_checkbox, self.render_centers_checkbox],
            margin='0.2cm')
        self.render_box = ipywidgets.HBox(children=[
            self.background_box, self.render_checkboxes_box], align='center')
        self.offset_patches_box = ipywidgets.VBox(
            children=[self.slicing_wid, self.offset_dropdown, self.render_box])

        # Create final widget
        children = [self.offset_patches_box, self.bboxes_line_options_wid]
        super(PatchOptionsWidget, self).__init__(
            children, Dict, {}, render_function=render_function,
            orientation='horizontal', align='start')

        # Set values
        self.add_callbacks()
        self.set_widget_state(n_patches, n_offsets, allow_callback=False)

        # Set style
        self.predefined_style(style, subwidgets_style)

    def add_callbacks(self):
        self.slicing_wid.on_trait_change(self._save_options, 'selected_values')
        self.offset_dropdown.on_trait_change(self._save_options, 'value')
        self.background_toggle.on_trait_change(self._save_options, 'value')
        self.render_patches_checkbox.on_trait_change(self._save_options,
                                                     'value')
        self.render_centers_checkbox.on_trait_change(self._save_options,
                                                     'value')
        self.bboxes_line_options_wid.on_trait_change(self._save_options,
                                                     'selected_values')

    def remove_callbacks(self):
        self.slicing_wid.on_trait_change(self._save_options, 'selected_values',
                                         remove=True)
        self.offset_dropdown.on_trait_change(self._save_options, 'value',
                                             remove=True)
        self.background_toggle.on_trait_change(self._save_options, 'value',
                                               remove=True)
        self.render_patches_checkbox.on_trait_change(self._save_options,
                                                     'value', remove=True)
        self.render_centers_checkbox.on_trait_change(self._save_options,
                                                     'value', remove=True)
        self.bboxes_line_options_wid.on_trait_change(self._save_options,
                                                     'selected_values',
                                                     remove=True)

    def _save_options(self, name, value):
        # set background attributes
        bc, c, description = self._background_args_wrt_value(
            self.background_toggle.value)
        self.background_toggle.background_color = bc
        self.background_toggle.color = c
        self.background_toggle.description = description
        # update selected values
        self.selected_values = {
            'patches_indices': self.slicing_wid.selected_values,
            'offset_index': int(self.offset_dropdown.value),
            'background': description,
            'render_patches': self.render_patches_checkbox.value,
            'render_centers': self.render_centers_checkbox.value,
            'render_patches_bboxes':
                self.bboxes_line_options_wid.selected_values['render_lines'],
            'bboxes_line_colour':
                self.bboxes_line_options_wid.selected_values['line_colour'][0],
            'bboxes_line_style':
                self.bboxes_line_options_wid.selected_values['line_style'],
            'bboxes_line_width':
                self.bboxes_line_options_wid.selected_values['line_width']}
        # update default values
        current_key = self.get_key(self.n_patches, self.n_offsets)
        self.default_options[current_key] = {
            'patches_indices': self.slicing_wid.selected_values,
            'offset_index': int(self.offset_dropdown.value),
            'background': description,
            'render_patches': self.render_patches_checkbox.value,
            'render_centers': self.render_centers_checkbox.value,
            'render_patches_bboxes':
                self.bboxes_line_options_wid.selected_values['render_lines'],
            'bboxes_line_colour':
                self.bboxes_line_options_wid.selected_values['line_colour'],
            'bboxes_line_style':
                self.bboxes_line_options_wid.selected_values['line_style'],
            'bboxes_line_width':
                self.bboxes_line_options_wid.selected_values['line_width']}

    def get_key(self, n_patches, n_offsets):
        return "{}_{}".format(n_patches, n_offsets)

    def get_default_options(self, n_patches, n_offsets):
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

    def _background_args_wrt_description(self, description):
        background_colour = '#FFFFFF'
        color = '#000000'
        value = True
        if description == 'black':
            background_colour = '#000000'
            color = '#FFFFFF'
            value = False
        return background_colour, color, value

    def _background_args_wrt_value(self, value):
        background_colour = '#FFFFFF'
        color = '#000000'
        description = 'white'
        if not value:
            background_colour = '#000000'
            color = '#FFFFFF'
            description = 'black'
        return background_colour, color, description

    def style(self, box_style=None, border_visible=False, border_colour='black',
              border_style='dashed', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', bboxes_box_style=None,
              bboxes_border_visible=False, bboxes_border_colour='black',
              bboxes_border_style='solid', bboxes_border_width=1,
              bboxes_border_radius=0, bboxes_padding=0, bboxes_margin=0,
              patches_box_style=None, patches_border_visible=False,
              patches_border_colour='black', patches_border_style='solid',
              patches_border_width=1, patches_border_radius=0,
              patches_padding=0, patches_margin=0):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_colour : `str`, optional
            The color of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                 'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                 'extra bold', 'black'}

        bboxes_box_style : See Below, optional
            Style options for the bounding boxes

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        bboxes_border_visible : `bool`, optional
            Defines whether to draw the border line around the bounding boxes
            options.
        bboxes_border_colour : `str`, optional
            The color of the border around the bounding boxes options.
        bboxes_border_style : `str`, optional
            The line style of the border around the bounding boxes options.
        bboxes_border_width : `float`, optional
            The line width of the border around the bounding boxes options.
        bboxes_border_radius : `float`, optional
            The radius of the corners of the box of the bounding boxes options.
        bboxes_padding : `float`, optional
            The padding around the bounding boxes options.
        bboxes_margin : `float`, optional
            The margin around the bounding boxes options.
        patches_box_style : See Below, optional
            Style options of the patches and offset options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        patches_border_visible : `bool`, optional
            Defines whether to draw the border line around the patches and
            offset options.
        patches_border_colour : `str`, optional
            The color of the border around the patches and offset options.
        patches_border_style : `str`, optional
            The line style of the border around the patches and offset options.
        patches_border_width : `float`, optional
            The line width of the border around the patches and offset options.
        patches_border_radius : `float`, optional
            The radius of the corners of the box of the patches and offset
            options.
        patches_padding : `float`, optional
            The padding around the patches and offset options.
        patches_margin : `float`, optional
            The margin around the patches and offset options.
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.offset_dropdown, font_family, font_size, font_style,
                    font_weight)
        format_font(self.render_patches_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.render_centers_checkbox, font_family, font_size,
                    font_style, font_weight)
        format_font(self.background_toggle, font_family, font_size,
                    font_style, font_weight)
        format_font(self.background_title, font_family, font_size,
                    font_style, font_weight)
        self.bboxes_line_options_wid.style(
            box_style=bboxes_box_style, border_visible=bboxes_border_visible,
            border_colour=bboxes_border_colour, border_style=bboxes_border_style,
            border_width=bboxes_border_width,
            border_radius=bboxes_border_radius, padding=bboxes_padding,
            margin=bboxes_margin, font_family=font_family, font_size=font_size,
            font_style=font_style, font_weight=font_weight)
        self.slicing_wid.style(
            box_style=patches_box_style, text_box_style=None,
            text_box_background_colour=None, text_box_width=None,
            font_family=font_family, font_size=font_size, font_style=font_style,
            font_weight=font_weight)
        format_box(self.offset_patches_box, box_style=patches_box_style,
                   border_visible=patches_border_visible,
                   border_colour=patches_border_colour,
                   border_style=patches_border_style,
                   border_width=patches_border_width,
                   border_radius=patches_border_radius,
                   padding=patches_padding, margin=patches_margin)

    def predefined_style(self, style, subwidgets_style):
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

        subwidgets_style : `str` (see below)
            Sub-widgets (patches and bounding boxes) style options:

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
            box_style = None
            border_visible = False
            border_colour = 'black'
            border_radius = 0
        elif (style == 'info' or style == 'success' or style == 'danger' or
                      style == 'warning'):
            box_style = style
            border_visible = True
            border_colour = map_styles_to_hex_colours(style)
            border_radius = 10
        else:
            raise ValueError('style and must be minimal or info or success '
                             'or danger or warning')

        if subwidgets_style == 'minimal':
            bboxes_box_style = None
            bboxes_border_colour = 'black'
            bboxes_border_radius = 0
            patches_box_style = None
            patches_border_colour = 'black'
            patches_border_radius = 0
        elif (subwidgets_style == 'info' or subwidgets_style == 'success' or
                      subwidgets_style == 'danger' or subwidgets_style == 'warning'):
            bboxes_box_style = subwidgets_style
            bboxes_border_colour = map_styles_to_hex_colours(subwidgets_style)
            bboxes_border_radius = 10
            patches_box_style = subwidgets_style
            patches_border_colour = map_styles_to_hex_colours(subwidgets_style)
            patches_border_radius = 10
        else:
            raise ValueError('subwidgets_style and must be minimal or info '
                             'or success or danger or warning')

        self.style(
            box_style=box_style, border_visible=border_visible,
            border_colour=border_colour, border_style='solid', border_width=1,
            border_radius=border_radius, padding='0.2cm', margin='0.3cm',
            font_family='', font_size=None, font_style='', font_weight='',
            bboxes_box_style=bboxes_box_style, bboxes_border_visible=True,
            bboxes_border_colour=bboxes_border_colour,
            bboxes_border_style='solid', bboxes_border_width=1,
            bboxes_border_radius=bboxes_border_radius, bboxes_padding='0.2cm',
            bboxes_margin='0.1cm', patches_box_style=patches_box_style,
            patches_border_visible=True,
            patches_border_colour=patches_border_colour,
            patches_border_style='solid', patches_border_width=1,
            patches_border_radius=patches_border_radius,
            patches_padding='0.2cm', patches_margin='0.1cm')

    def set_widget_state(self, n_patches, n_offsets, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        patch_options : `dict`
            The dictionary with the new options to be used. For example
            ::

                patch_options = {'patches': {'command': '',
                                             'indices': [],
                                             'length': 68},
                                 'offset_index': 0,
                                 'n_offsets': 5,
                                 'render_centers': True,
                                 'render_centers': True,
                                 'background': 'white',
                                 'bboxes': {'render_lines': True,
                                            'line_colour': ['r'],
                                            'line_style': '-',
                                            'line_width': 1}
                                }

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
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
            self.render_patches_checkbox.value = patch_options['render_patches']
            self.render_centers_checkbox.value = patch_options['render_centers']
            background_colour = '#FFFFFF'
            color = '#000000'
            value = True
            if patch_options['background'] == 'black':
                background_colour = '#000000'
                color = '#FFFFFF'
                value = False
            self.background_toggle.description = patch_options['background']
            self.background_toggle.color = color
            self.background_toggle.background_color = background_colour
            self.background_toggle.value = value
            slice_options = {'command': str(patch_options['patches_indices']),
                             'length': self.n_patches}
            self.slicing_wid.set_widget_state(slice_options,
                                              allow_callback=False)
            line_opts = {
                'render_lines': patch_options['render_patches_bboxes'],
                'line_colour': patch_options['bboxes_line_colour'],
                'line_style': patch_options['bboxes_line_style'],
                'line_width': patch_options['bboxes_line_width']}
            self.bboxes_line_options_wid.set_widget_state(
                line_opts, labels=None, allow_callback=False)

            # Get values
            self._save_options('', None)

            # Re-assign callbacks
            self.add_callbacks()
            self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self._render_function('', True)


class PlotOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting options for rendering various curves in a
    graph. The widget consists of the following objects from
    `IPython.html.widgets` and :ref:`api-tools-index`:

    == ===================== ======================= =======================
    No Object                Property (`self.`)      Description
    == ===================== ======================= =======================
    1  RendererOptionsWidget `renderer_widget`       The rendering widget
    2  FloatRangeSlider      `x_limit`               Sets the x limit
    3  FloatRangeSlider      `y_limit`               Sets the y limit
    4  Text                  `x_label`               Sets the x label
    5  Text                  `y_label`               Sets the y label
    6  Text                  `title`                 Sets the title
    7  Textarea              `legend_entries`        Sets the legend entries
    8  VBox                  `graph_related_options` Contains 2 - 7
    9  Tab                   `options_tab`           Contains 8, 1
    == ===================== ======================= =======================

    Note that:

    * The selected values are stored in the ``self.selected_values`` `dict`.
    * To set the styling please refer to the ``style()`` and
      ``predefined_style()`` methods.
    * To update the state of the widget, please refer to the
      ``set_widget_state()`` method.
    * To update the callback function please refer to the
      ``replace_render_function()`` methods.

    Parameters
    ----------
    graph_options : `list` of `str`
        The initial options. For example, in case we had two curves to render
        ::

            graph_options = {'legend_entries': ['Nontas', 'Leda'],
                             'x_label': 'X',
                             'y_label': 'Y',
                             'title': 'TITLE',
                             'x_axis_limits': (2, 7),
                             'y_axis_limits': (-0.2, 0.2),
                             'render_lines': [True, True],
                             'line_colour': ['r', 'b'],
                             'line_style': ['--', '-'],
                             'line_width': [1, 3],
                             'render_markers': [True, False],
                             'marker_style': ['o', 's'],
                             'marker_size': [6, 12],
                             'marker_face_colour': ['k', 'm'],
                             'marker_edge_colour': ['w', 'c'],
                             'marker_edge_width': [1, 4],
                             'render_legend': True,
                             'legend_title': '',
                             'legend_font_name': 'sans-serif',
                             'legend_font_style': 'normal',
                             'legend_font_size': 10,
                             'legend_font_weight': 'normal',
                             'legend_marker_scale': 1.,
                             'legend_location': 2,
                             'legend_bbox_to_anchor': (1.05, 1.),
                             'legend_border_axes_pad': 0.,
                             'legend_n_columns': 1,
                             'legend_horizontal_spacing': 0,
                             'legend_vertical_spacing': 0,
                             'legend_border': True,
                             'legend_border_padding': 0,
                             'legend_shadow': False,
                             'legend_rounded_corners': False,
                             'render_axes': True,
                             'axes_font_name': 'sans-serif',
                             'axes_font_size': 10,
                             'axes_font_style': 'normal',
                             'axes_font_weight': 'normal',
                             'figure_size': (10, 8),
                             'render_grid': True,
                             'grid_line_style': '--',
                             'grid_line_width': 1}

    x_slider_options : (`float`, `float`, `float`)
        The attributes of the x limit slider in the form (`min`, `max`, `step`).
    y_slider_options : (`float`, `float`, `float`)
        The attributes of the y limit slider in the form (`min`, `max`, `step`).
    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
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

    """
    def __init__(self, legend_entries, render_function=None, style='minimal',
                 tabs_style='minimal'):
        # Assign properties
        self.legend_entries = legend_entries
        self.n_curves = len(legend_entries)

        # Create default options
        default_options = self.create_default_options()

        # Create children
        self.lines_wid = LineOptionsWidget(
            {'render_lines': default_options['render_lines'][0],
             'line_width': default_options['line_width'][0],
             'line_colour': [default_options['line_colour'][0]],
             'line_style': default_options['line_style'][0]},
            render_function=None, render_checkbox_title='Render lines',
            labels=None)
        self.markers_wid = MarkerOptionsWidget(
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
        def get_legend_entries(name, value):
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
        self.legend_entries_text.on_trait_change(get_legend_entries, 'value')

        def save_options(name, value):
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
        self.title.on_trait_change(save_options, 'value')
        self.x_label.on_trait_change(save_options, 'value')
        self.y_label.on_trait_change(save_options, 'value')
        self.legend_entries_text.on_trait_change(save_options, 'value')
        self.lines_wid.on_trait_change(save_options, 'selected_values')
        self.markers_wid.on_trait_change(save_options, 'selected_values')
        self.axes_wid.on_trait_change(save_options, 'selected_values')
        self.legend_wid.on_trait_change(save_options, 'selected_values')
        self.grid_wid.on_trait_change(save_options, 'selected_values')
        self.zoom_wid.on_trait_change(save_options, 'selected_values')

        def update_lines_markers(name, value):
            k = self.curves_dropdown.value

            # remove save options callback
            self.lines_wid.on_trait_change(save_options, 'selected_values',
                                           remove=True)
            self.markers_wid.on_trait_change(save_options, 'selected_values',
                                             remove=True)

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
            self.lines_wid.on_trait_change(save_options, 'selected_values')
            self.markers_wid.on_trait_change(save_options, 'selected_values')
        self.curves_dropdown.on_trait_change(update_lines_markers, 'value')

    def create_default_options(self):
        render_lines = [True] * self.n_curves
        line_style = ['-'] * self.n_curves
        line_width = [1] * self.n_curves
        render_markers = [True] * self.n_curves
        marker_style = ['s'] * self.n_curves
        marker_size = [10] * self.n_curves
        marker_face_colour = ['white'] * self.n_curves
        marker_edge_width = [1.] * self.n_curves
        line_colour = ['red']
        marker_edge_colour = ['red']
        if self.n_curves > 1:
            line_colour = sample_colours_from_colourmap(self.n_curves, 'jet')
            marker_edge_colour = sample_colours_from_colourmap(
                self.n_curves, 'jet')
        return {'title': '', 'x_label': '', 'y_label': '', 'render_legend': True,
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
                'axes_font_weight': 'normal', 'axes_x_limits': None,
                'axes_y_limits': None, 'axes_x_ticks': None,
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

    def style(self, box_style=None, border_visible=False, border_color='black',
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
        box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_color : `str`, optional
            The color of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        tabs_box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        tabs_border_visible : `bool`, optional
            Defines whether to draw the border line around the tab widgets.
        tabs_border_color : `str`, optional
            The color of the border around the tab widgets.
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

        renderer_tabs_box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        renderer_tabs_border_visible : `bool`, optional
            Defines whether to draw the border line around the tab widgets of
            the renderer widget.
        renderer_tabs_border_color : `str`, optional
            The color of the border around the tab widgets of the renderer
            widget.
        renderer_tabs_border_style : `str`, optional
            The line style of the border around the tab widgets of the renderer
            widget.
        renderer_tabs_border_width : `float`, optional
            The line width of the border around the tab widgets of the renderer
            widget.
        renderer_tabs_border_radius : `float`, optional
            The radius of the corners of the box of the tab widgets of the
            renderer widget.
        renderer_tabs_padding : `float`, optional
            The padding around the tab widgets of the renderer widget.
        renderer_tabs_margin : `float`, optional
            The margin around the tab widgets of the renderer widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                 'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                 'extra bold', 'black'}
        """
        format_box(self, box_style, border_visible, border_color, border_style,
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
            self.style(box_style='', border_visible=True, border_color='black',
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
                       border_color=map_styles_to_hex_colours(style),
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
    model (e.g. PCA model). The widget consists of the following objects from
    `IPython.html.widgets`:

    == =========== ================== ==========================
    No Object      Property (`self.`) Description
    == =========== ================== ==========================
    1  Button      `plot_button`      The plot variance button
    2  Button      `reset_button`     The reset button
    3  HBox        `plot_and_reset`   Contains 1, 2
                         If mode is 'single'
    ------------------------------------------------------------
    4  FloatSlider `slider`           The parameter value slider
    5  Dropdown    `dropdown_params`  The parameter selector
    6  HBox        `parameters_wid`   Contains 4, 5
                         If mode is 'multiple'
    ------------------------------------------------------------
    7  FloatSlider `sliders`          `list` of all sliders
    8  VBox        `parameters_wid`   Contains all 7
    == =========== ================== ==========================

    Note that:

    * The selected parameters are stored in the ``self.parameters`` `list`.
    * To set the styling please refer to the ``style()`` and
      ``predefined_style()`` methods.
    * To update the state of the widget, please refer to the
      ``set_widget_state()`` method.
    * To update the callback function please refer to the
      ``replace_render_function()`` and ``replace_variance_function()``
      methods.

    Parameters
    ----------
    parameters : `list`
        The `list` of initial parameters values.
    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    mode : {``'single'``, ``'multiple'``}, optional
        If ``'single'``, only a single slider is constructed along with a
        dropdown menu that allows the parameter selection.
        If ``'multiple'``, a slider is constructed for each parameter.
    params_str : `str`, optional
        The string that will be used as description of the slider(s). The final
        description has the form `"{}{}".format(params_str, p)`, where `p` is
        the parameter number.
    params_bounds : (`float`, `float`), optional
        The minimum and maximum bounds, in std units, for the sliders.
    params_step : `float`, optional
        The step, in std units, of the sliders.
    plot_variance_visible : `bool`, optional
        Defines whether the button for plotting the variance will be visible
        upon construction.
    plot_variance_function : `function` or ``None``, optional
        The plot function that is executed when the plot variance button is
        clicked. If ``None``, then nothing is assigned.
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

    Example
    -------
    Let's create a linear model parameters values widget and then update its
    state. Firstly, we need to import it:

        >>> from menpowidgets.options_old import LinearModelParametersWidget

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected parameters:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(name, value):
        >>>     s = "Selected parameters: {}".format(wid.parameters)
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> parameters = [-3., -2., -1., 0., 1., 2., 3.]
        >>> wid = LinearModelParametersWidget(parameters,
        >>>                                   render_function=render_function,
        >>>                                   params_str='Parameter ',
        >>>                                   mode='multiple',
        >>>                                   params_bounds=(-3., 3.),
        >>>                                   plot_variance_visible=True,
        >>>                                   style='info')
        >>> wid

    By moving the sliders, the printed message gets updated. Finally, let's
    change the widget status with a new set of options:

        >>> wid.set_widget_state(parameters=[-7.] * 3, params_str='',
        >>>                      params_step=0.1, params_bounds=(-10, 10),
        >>>                      plot_variance_visible=False,
        >>>                      allow_callback=True)
    """
    def __init__(self, n_parameters, render_function=None, mode='multiple',
                 params_str='', params_bounds=(-3., 3.), params_step=0.1,
                 plot_variance_visible=True, plot_variance_function=None,
                 style='minimal', continuous_update=False):
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
                step=params_step, value=0., margin='0.2cm',
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
        self.plot_and_reset = ipywidgets.HBox(children=[self.plot_button,
                                                        self.reset_button])

        # Create final widget
        children = [self.parameters_wid, self.plot_and_reset]
        super(LinearModelParametersWidget, self).__init__(
            children, List, [0.] * n_parameters, render_function=render_function,
            orientation='vertical', align='end')

        # Assign output
        self.n_parameters = n_parameters
        self.mode = mode
        self.params_str = params_str
        self.params_bounds = params_bounds
        self.params_step = params_step
        self.plot_variance_visible = plot_variance_visible

        # Set style
        self.predefined_style(style)

        # Set functionality
        if mode == 'single':
            # Assign slider value to parameters values list
            def save_slider_value(name, value):
                current_parameters = list(self.selected_values)
                current_parameters[self.dropdown_params.value] = value
                self.selected_values = current_parameters
            self.slider.on_trait_change(save_slider_value, 'value')

            # Set correct value to slider when drop down menu value changes
            def set_slider_value(name, value):
                # Temporarily remove render callback
                render_function = self._render_function
                self.remove_render_function()
                # Set slider value
                self.slider.value = self.parameters[value]
                # Re-assign render callback
                self.add_render_function(render_function)
            self.dropdown_params.on_trait_change(set_slider_value, 'value')
        else:
            # Assign slider value to parameters values list
            def save_slider_value_from_id(description, name, value):
                current_parameters = list(self.selected_values)
                i = int(description[len(params_str)::])
                current_parameters[i] = value
                self.selected_values = current_parameters

            # Partial function that helps get the widget's description str
            def partial_widget(description):
                return lambda name, value: save_slider_value_from_id(
                    description, name, value)

            # Assign saving values and main plotting function to all sliders
            for w in self.sliders:
                # The widget (w) is lexically scoped and so we need a way of
                # ensuring that we don't just receive the final value of w at
                # every iteration. Therefore we create another lambda function
                # that creates a new lexical scoping so that we can ensure the
                # value of w is maintained (as x) at each iteration.
                # In JavaScript, we would just use the 'let' keyword...
                w.on_trait_change(partial_widget(w.description), 'value')

        def reset_parameters(name):
            # Temporarily remove render callback
            render_function = self._render_function
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
            self.add_render_function(render_function)
            if self._render_function is not None:
                self._render_function('', True)
        self.reset_button.on_click(reset_parameters)

        # Set plot variance function
        self._variance_function = None
        self.add_variance_function(plot_variance_function)

    def style(self, box_style=None, border_visible=False, border_color='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', slider_width='', slider_handle_colour=None,
              slider_bar_colour=None, buttons_style=''):
        r"""
        Function that defines the styling of the widget.

        Parameters
        ----------
        box_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================

        border_visible : `bool`, optional
            Defines whether to draw the border line around the widget.
        border_color : `str`, optional
            The color of the border around the widget.
        border_style : `str`, optional
            The line style of the border around the widget.
        border_width : `float`, optional
            The line width of the border around the widget.
        border_radius : `float`, optional
            The radius of the corners of the box.
        padding : `float`, optional
            The padding around the widget.
        margin : `float`, optional
            The margin around the widget.
        font_family : See Below, optional
            The font family to be used.
            Example options ::

                {'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace',
                 'helvetica'}

        font_size : `int`, optional
            The font size.
        font_style : {``'normal'``, ``'italic'``, ``'oblique'``}, optional
            The font style.
        font_weight : See Below, optional
            The font weight.
            Example options ::

                {'ultralight', 'light', 'normal', 'regular', 'book', 'medium',
                 'roman', 'semibold', 'demibold', 'demi', 'bold', 'heavy',
                 'extra bold', 'black'}

        slider_width : `str`, optional
            The width of the slider(s).
        slider_handle_colour : `str`, optional
            The colour of the handle(s) of the slider(s).
        slider_background_colour : `str`, optional
            The background colour of the slider(s).
        buttons_style : See Below, optional
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'primary' Blue-based style
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        Default style
                None      No style
                ========= ============================
        """
        format_box(self, box_style, border_visible, border_color, border_style,
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
            self.style(box_style=None, border_visible=True,
                       border_color='black', border_style='solid',
                       border_width=1, border_radius=0, padding='0.2cm',
                       margin='0.3cm', font_family='', font_size=None,
                       font_style='', font_weight='', slider_width='',
                       slider_handle_colour=None, slider_bar_colour=None,
                       buttons_style='')
        elif (style == 'info' or style == 'success' or style == 'danger' or
                    style == 'warning'):
            self.style(box_style=style, border_visible=True,
                       border_color=map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding='0.2cm', margin='0.3cm', font_family='',
                       font_size=None, font_style='', font_weight='',
                       slider_width='',
                       slider_handle_colour=map_styles_to_hex_colours(style),
                       slider_bar_colour=None, buttons_style='primary')
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')

    def add_variance_function(self, variance_function):
        r"""
        Method that adds a `variance_function()` to the `Variance` button of the
        widget. The signature of the given function is also stored in
        `self._variance_function`.

        Parameters
        ----------
        variance_function : `function` or ``None``, optional
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
        variance_function : `function` or ``None``, optional
            The variance function that behaves as a callback. If ``None``,
            then nothing happens.
        """
        # remove old function
        self.remove_variance_function()

        # add new function
        self.add_variance_function(variance_function)

    def set_widget_state(self, n_parameters=None, params_str=None,
                         params_bounds=None, params_step=None,
                         plot_variance_visible=True, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of options.

        Parameters
        ----------
        parameters : `list` or ``None``, optional
            The `list` of new parameters' values. If ``None``, then nothing
            changes.
        params_str : `str` or ``None``, optional
            The string that will be used as description of the slider(s). The
            final description has the form `"{}{}".format(params_str, p)`, where
            `p` is the parameter number. If ``None``, then nothing changes.
        params_bounds : (`float`, `float`) or ``None``, optional
            The minimum and maximum bounds, in std units, for the sliders. If
            ``None``, then nothing changes.
        params_step : `float` or ``None``, optional
            The step, in std units, of the sliders. If ``None``, then nothing
            changes.
        plot_variance_visible : `bool`, optional
            Defines whether the button for plotting the variance will be
            visible.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
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

                # Assign slider value to parameters values list
                def save_slider_value_from_id(description, name, value):
                    current_parameters = list(self.selected_values)
                    i = int(description[len(params_str)::])
                    current_parameters[i] = value
                    self.selected_values = current_parameters

                # Partial function that helps get the widget's description str
                def partial_widget(description):
                    return lambda name, value: save_slider_value_from_id(
                        description, name, value)

                # Assign saving values and main plotting function to all sliders
                for w in self.sliders:
                    # The widget (w) is lexically scoped and so we need a way of
                    # ensuring that we don't just receive the final value of w
                    # at every iteration. Therefore we create another lambda
                    # function that creates a new lexical scoping so that we can
                    # ensure the value of w is maintained (as x) at each
                    # iteration. In JavaScript, we would just use the 'let'
                    # keyword...
                    w.on_trait_change(partial_widget(w.description), 'value')

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
            self._render_function('', True)
