import ipywidgets
from traitlets.traitlets import Dict

from menpowidgets.abstract import MenpoWidget
from menpowidgets.options import AnimationOptionsWidget
from menpowidgets.tools import SlicingCommandWidget
from menpowidgets.style import (format_font, format_box,
                                map_styles_to_hex_colours)


class ResultOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting options when visualizing a fitting result.
    The widget consists of the following parts from `ipywidgets`:

    == ============== ======================= =========================
    No Object         Property (`self.`)      Description
    == ============== ======================= =========================
    1  `RadioButtons` `mode`                  Subplot mode flag
    2  `Checkbox`     `render_image`          Image rendering flag
    3  `VBox`         `mode_render_image_box` Contains 1, 2
    4  `Latex`        `shape_buttons[0]`      'Shape:' str
    5  `ToggleButton` `shape_buttons[1]`      Initial shape toggle
    6  `ToggleButton` `shape_buttons[2]`      Final shape toggle
    7  `ToggleButton` `shape_buttons[3]`      Ground truth shape toggle
    8  `HBox`         `shape_selection`       Contains 4, 5, 6, 7
    == ============== ======================= =========================

    Note that:

    * To update the state of the widget, please refer to the
      :meth:`set_widget_state` method.
    * The selected values are stored in the ``self.selected_values`` `trait`
      which is a `list`.
    * To set the styling of this widget please refer to the :meth:`style` and
      :meth:`predefined_style` methods.
    * To update the handler callback function of the widget, please refer to
      the :meth:`replace_render_function` method.

    Parameters
    ----------
    has_gt_shape : `bool`
        Whether the fitting result object has the ground truth shape.
    has_initial_shape : `bool`
        Whether the fitting result object has the initial shape.
    has_image : `bool`
        Whether the fitting result object has the image.
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

    Example
    -------
    Let's create a fitting result options widget and then update its state.
    Firstly, we need to import it:

        >>> from menpowidgets.menpofit.options import ResultOptionsWidget

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected options:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(change):
        >>>     s = "Final: {}, Initial: {}, GT: {}, Image: {}, Subplots: {}".format(
        >>>         wid.selected_values['render_final_shape'],
        >>>         wid.selected_values['render_initial_shape'],
        >>>         wid.selected_values['render_gt_shape'],
        >>>         wid.selected_values['render_image'],
        >>>         wid.selected_values['subplots_enabled'])
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> wid = ResultOptionsWidget(has_gt_shape=True,
        >>>                           has_initial_shape=True, has_image=True,
        >>>                           render_function=render_function,
        >>>                           style='info')
        >>> wid

    By changing the various widgets, the printed message gets updated. Finally,
    let's change the widget status with a new set of options:

        >>> wid.set_widget_state(has_gt_shape=True, has_initial_shape=False,
        >>>                      has_image=False, allow_callback=True)
    """
    def __init__(self, has_gt_shape, has_initial_shape, has_image,
                 render_function=None, style='minimal'):
        # Initialise default options dictionary
        render_image = True if has_image else False
        default_options = {'render_final_shape': True,
                           'render_initial_shape': False,
                           'render_gt_shape': False,
                           'render_image': render_image,
                           'subplots_enabled': True}

        # Assign properties
        self.has_gt_shape = None
        self.has_initial_shape = None
        self.has_image = None

        # Create children
        self.mode = ipywidgets.RadioButtons(
                description='Figure mode:',
                options={'Single': False, 'Multiple': True},
                value=default_options['subplots_enabled'])
        self.render_image = ipywidgets.Checkbox(
                description='Render image',
                value=default_options['render_image'])
        self.mode_render_image_box = ipywidgets.VBox(
                children=[self.mode, self.render_image], margin='0.2cm')
        self.shape_buttons = [
            ipywidgets.Label(value='Shape:', margin='0.2cm'),
            ipywidgets.ToggleButton(description='Initial', value=False),
            ipywidgets.ToggleButton(description='Final', value=True),
            ipywidgets.ToggleButton(description='Groundtruth', value=False)]
        self.shape_selection = ipywidgets.HBox(children=self.shape_buttons,
                                               align='center', margin='0.2cm',
                                               padding='0.2cm')

        # Create final widget
        children = [self.mode_render_image_box, self.shape_selection]
        super(ResultOptionsWidget, self).__init__(
                children, Dict, default_options,
                render_function=render_function, orientation='horizontal',
                align='start')

        # Set values
        self.add_callbacks()
        self.set_widget_state(has_gt_shape, has_initial_shape, has_image,
                              allow_callback=False)

        # Set style
        self.predefined_style(style)

    def _save_options(self, change):
        self.selected_values = {
            'render_initial_shape': (self.shape_buttons[1].value and
                                     self.has_initial_shape),
            'render_final_shape': self.shape_buttons[2].value,
            'render_gt_shape': (self.shape_buttons[3].value and
                                self.has_gt_shape),
            'render_image': (self.render_image.value and self.has_image),
            'subplots_enabled': self.mode.value}

    def add_callbacks(self):
        r"""
        Function that adds the handler callback functions in all the widget
        components, which are necessary for the internal functionality.
        """
        self.render_image.observe(self._save_options, names='value',
                                  type='change')
        self.mode.observe(self._save_options, names='value', type='change')
        for w in self.shape_selection.children[1::]:
            w.observe(self._save_options, names='value', type='change')

    def remove_callbacks(self):
        r"""
        Function that removes all the internal handler callback functions.
        """
        self.render_image.unobserve(self._save_options, names='value',
                                    type='change')
        self.mode.unobserve(self._save_options, names='value', type='change')
        for w in self.shape_selection.children[1::]:
            w.unobserve(self._save_options, names='value', type='change')

    def set_visibility(self):
        r"""
        Function that sets the visibility of the various components of the
        widget, depending on the properties of the current image object, i.e.
        ``self.n_channels`` and ``self.image_is_masked``.
        """
        self.shape_selection.children[1].visible = self.has_initial_shape
        self.shape_selection.children[3].visible = self.has_gt_shape
        self.render_image.visible = self.has_image

    def style(self, box_style='', border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', buttons_style=''):
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

        buttons_style : `str` or ``None`` (see below), optional
            Style options:

                'success', 'info', 'warning', 'danger', 'primary', '', None
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.render_image, font_family, font_size, font_style,
                    font_weight)
        format_font(self.mode, font_family, font_size, font_style, font_weight)
        format_font(self.shape_selection.children[0], font_family, font_size,
                    font_style, font_weight)
        for w in self.shape_selection.children[1::]:
            format_font(w, font_family, font_size, font_style, font_weight)
            w.button_style = buttons_style

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
            self.style(box_style='', border_visible=True,
                       border_colour='black', border_style='solid',
                       border_width=1, border_radius=0, padding='0.2cm',
                       margin='0.3cm', font_family='', font_size=None,
                       font_style='', font_weight='', buttons_style='')
        elif (style == 'info' or style == 'success' or style == 'danger' or
                      style == 'warning'):
            self.style(box_style=style, border_visible=True,
                       border_colour=map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding='0.2cm', margin='0.3cm', font_family='',
                       font_size=None, font_style='', font_weight='',
                       buttons_style='primary')
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')

    def set_widget_state(self, has_gt_shape, has_initial_shape, has_image,
                         allow_callback=True):
        r"""
        Method that updates the state of the widget.

        Parameters
        ----------
        has_gt_shape : `bool`
            Whether the fitting result object has the ground truth shape.
        has_initial_shape : `bool`
            Whether the fitting result object has the initial shape.
        has_image : `bool`
            Whether the fitting result object has the image.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # keep old value
        old_value = self.selected_values

        # check if updates are required
        if (self.has_gt_shape != has_gt_shape or
                self.has_initial_shape != has_initial_shape or
                self.has_image != has_image):
            # Assign properties
            self.has_gt_shape = has_gt_shape
            self.has_initial_shape = has_initial_shape
            self.has_image = has_image

            # Set widget's visibility
            self.set_visibility()

            # Get values
            self._save_options({})

        # trigger render function if allowed
        if allow_callback:
            self.call_render_function(old_value, self.selected_values)


class IterativeResultOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting options when visualizing an iterative
    fitting result. The widget consists of the following parts from
    `ipywidgets` and :ref:`api-tools-index`:

    == ============================= =========================== ===============
    No Object                        Property (`self.`)          Description
    == ============================= =========================== ===============
    1  `RadioButtons`                `mode`                      Subplot mode
    2  `Checkbox`                    `render_image`              Image rendering
    3  `VBox`                        `mode_render_image_box`     Contains 1, 2
    4  `Latex`                       `shape_buttons[0]`          'Shape:' str
    5  `ToggleButton`                `shape_buttons[1]`          Initial shape
    6  `ToggleButton`                `shape_buttons[2]`          Final shape
    7  `ToggleButton`                `shape_buttons[3]`          Ground truth
    8  `HBox`                        `result_box`                Contains 4-7
    9  `RadioButtons`                `iterations_mode`           'Animation' or

                                                                 'Static'
    10 :map:`AnimationOptionsWidget` `index_animation`           Animation wid
    11 :map:`SlicingCommandWidget`   `index_slicing`             Slicing wid
    12 `Button`                      `plot_errors_button`        Errors plot
    13 `Button`                      `plot_displacements_button` Displacements
    14 `Button`                      `plot_costs_button`         Costs plot
    15 `HBox`                        `buttons_box`               Contains 12-14
    16 `VBox`                        `index_buttons_box`         10,11,15
    17 `HBox`                        `mode_index_buttons_box`    Contains 9, 16
    18 `Latex`                       `no_iterations_text`        No iterations
    19 `VBox`                        `iterations_box`            Contains 17, 18
    20 `Tab`                         `result_iterations_tab`     Contains 8, 19
    == ============================= =========================== ===============

    Note that:

    * To update the state of the widget, please refer to the
      :meth:`set_widget_state` method.
    * The selected values are stored in the ``self.selected_values`` `trait`
      which is a `list`.
    * To set the styling of this widget please refer to the :meth:`style` and
      :meth:`predefined_style` methods.
    * To update the handler callback function of the widget, please refer to
      the :meth:`replace_render_function` method.
    * To update the handler callback plot functions of the widget, please
      refer to :meth:`replace_plots_function`, :meth:`replace_errors_function`
      and :meth:`replace_displacements_function` methods.

    Parameters
    ----------
    has_gt_shape : `bool`
        Whether the fitting result object has the ground truth shape.
    has_initial_shape : `bool`
        Whether the fitting result object has the initial shape.
    has_image : `bool`
        Whether the fitting result object has the image.
    n_shapes : `int` or ``None``
        The total number of shapes. If ``None``, then it is assumed that no
        iteration shapes are available.
    has_costs : `bool`
        Whether the fitting result object has costs attached.
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
    tab_update_function : `callable` or ``None``, optional
        A function that gets called when switching between the 'Result' and
        'Iterations' tabs. If ``None``, then nothing is assigned.
    displacements_function : `callable` or ``None``, optional
        The function that is executed when the 'Displacements' button is
        pressed. It must have signature ``displacements_function(name)``. If
        ``None``, then nothing is assigned and the button is invisible.
    errors_function : `callable` or ``None``, optional
        The function that is executed when the 'Errors' button is pressed. It
        must have signature ``errors_function(name)``. If  ``None``, then
        nothing is assigned and the button is invisible.
    costs_function : `callable` or ``None``, optional
        The function that is executed when the 'Errors' button is pressed. It
        must have signature ``displacements_function(name)``. If ``None``,
        then nothing is assigned and the button is invisible.
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
        Sets a predefined style at the tab widgets. Possible options are:

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
    Let's create an iterative result options widget and then update its state.
    Firstly, we need to import it:

        >>> from menpowidgets.menpofit.options import IterativeResultOptionsWidget

    Now let's define a render function that will get called on every widget
    change and will print the selected options:

        >>> def render_function(change):
        >>>     print(wid.selected_values)

    Let's also define a plot function that will get called when one of the
    'Errors', 'Costs' or 'Displacements' buttons is pressed:

        >>> def plot_function(name):
        >>>     print(name)

    Create the widget with some initial options and display it:

        >>> wid = IterativeResultOptionsWidget(
        >>>         has_gt_shape=True, has_initial_shape=True, has_image=True,
        >>>         n_shapes=20, has_costs=True, render_function=render_function,
        >>>         displacements_function=plot_function,
        >>>         errors_function=plot_function, costs_function=plot_function,
        >>>         style='info', tabs_style='danger')
        >>> wid

    By changing the various widgets, the printed message gets updated. Finally,
    let's change the widget status with a new set of options:

        >>> wid.set_widget_state(has_gt_shape=False, has_initial_shape=True,
        >>>                      has_image=True, n_shapes=None, has_costs=False,
        >>>                      allow_callback=True)
    """
    def __init__(self, has_gt_shape, has_initial_shape, has_image, n_shapes,
                 has_costs, render_function=None, tab_update_function=None,
                 displacements_function=None, errors_function=None,
                 costs_function=None, style='minimal', tabs_style='minimal'):
        # Initialise default options dictionary
        render_image = True if has_image else False
        default_options = {'render_final_shape': True,
                           'render_initial_shape': False,
                           'render_gt_shape': False,
                           'render_image': render_image,
                           'subplots_enabled': True}

        # Assign properties
        self.has_gt_shape = None
        self.has_initial_shape = None
        self.has_image = None
        self.n_shapes = -1
        self.tab_update_function = tab_update_function

        # Create result tab
        self.mode = ipywidgets.RadioButtons(
            description='Figure mode:',
            options={'Single': False, 'Multiple': True},
            value=default_options['subplots_enabled'])
        self.render_image = ipywidgets.Checkbox(
            description='Render image',
            value=default_options['render_image'])
        self.mode_render_image_box = ipywidgets.VBox(
            children=[self.mode, self.render_image], margin='0.2cm')
        self.shape_buttons = [
            ipywidgets.Label(value='Shape:', margin='0.2cm'),
            ipywidgets.ToggleButton(description='Initial', value=False),
            ipywidgets.ToggleButton(description='Final', value=True),
            ipywidgets.ToggleButton(description='Groundtruth', value=False)]
        self.result_box = ipywidgets.HBox(children=self.shape_buttons,
                                          align='center', margin='0.2cm',
                                          padding='0.2cm')

        # Create iterations tab
        self.iterations_mode = ipywidgets.RadioButtons(
            options={'Animation': 'animation', 'Static': 'static'},
            value='animation', description='Iterations:', margin='0.15cm')
        self.iterations_mode.observe(self._stop_animation, names='value',
                                     type='change')
        self.iterations_mode.observe(self._index_visibility, names='value',
                                     type='change')
        index = {'min': 0, 'max': n_shapes - 1, 'step': 1, 'index': 0}
        self.index_animation = AnimationOptionsWidget(
                index, description='', index_style='slider',
                loop_enabled=False, interval=0.)
        slice_options = {'command': 'range({})'.format(n_shapes),
                         'length': n_shapes}
        self.index_slicing = SlicingCommandWidget(
                slice_options, description='', example_visible=True,
                continuous_update=False, orientation='vertical')
        self.plot_errors_button = ipywidgets.Button(
            description='Errors', margin='0.1cm',
            visible=has_gt_shape and errors_function is not None)
        self.plot_displacements_button = ipywidgets.Button(
            description='Displacements', margin='0.1cm',
            visible=displacements_function is not None)
        self.plot_costs_button = ipywidgets.Button(
            description='Costs', margin='0.1cm', visible=has_costs)
        self.buttons_box = ipywidgets.HBox(
            children=[self.plot_errors_button, self.plot_costs_button,
                      self.plot_displacements_button])
        self.index_buttons_box = ipywidgets.VBox(
            children=[self.index_animation, self.index_slicing,
                      self.buttons_box])
        self.mode_index_buttons_box = ipywidgets.HBox(
                children=[self.iterations_mode, self.index_buttons_box],
                margin='0.2cm', padding='0.2cm')
        self.no_iterations_text = ipywidgets.Label(
                value='No iterations available')
        self.iterations_box = ipywidgets.VBox(
            children=[self.mode_index_buttons_box, self.no_iterations_text])

        # Create final tab widget
        self.result_iterations_tab = ipywidgets.Tab(
            children=[self.result_box, self.iterations_box], margin='0.2cm')
        self.result_iterations_tab.set_title(0, 'Final')
        self.result_iterations_tab.set_title(1, 'Iterations')
        self.result_iterations_tab.observe(
                self._stop_animation, names='selected_index', type='change')

        # Function for updating rendering options
        if tab_update_function is not None:
            self.result_iterations_tab.observe(tab_update_function,
                                               names='selected_index',
                                               type='change')
            self.iterations_mode.observe(tab_update_function, names='value',
                                         type='change')

        # Create final widget
        children = [self.mode_render_image_box, self.result_iterations_tab]
        super(IterativeResultOptionsWidget, self).__init__(
            children, Dict, default_options, render_function=render_function,
            orientation='horizontal', align='start')

        # Visibility
        self._index_visibility({'new': 'animation'})

        # Set callbacks
        self._displacements_function = None
        self.add_displacements_function(displacements_function)
        self._errors_function = None
        self.add_errors_function(errors_function)
        self._costs_function = None
        self.add_costs_function(costs_function)

        # Set values
        self.add_callbacks()
        self.set_widget_state(has_gt_shape, has_initial_shape, has_image,
                              n_shapes, has_costs, allow_callback=False)

        # Set style
        self.predefined_style(style, tabs_style)

    def _index_visibility(self, change):
        self.index_animation.visible = change['new'] == 'animation'
        self.index_slicing.visible = change['new'] == 'static'

    def _stop_animation(self, change):
        # Make sure that the animation gets stopped when the 'Static'
        # radiobutton or 'Final' tab is selected.
        if change['new'] in ['static', 0]:
            self.index_animation.stop_animation()

    def add_displacements_function(self, displacements_function):
        r"""
        Method that adds the provided `displacements_function` as a callback
        handler to the `click` event of ``self.plot_displacements_button``. The
        given function is also stored in ``self._displacements_function``.

        Parameters
        ----------
        displacements_function : `callable` or ``None``, optional
            The function that behaves as a callback handler of the `click`
            event of ``self.plot_displacements_button``. Its signature is
            ``displacements_function(name)``. If ``None``, then nothing is
            added.
        """
        self._displacements_function = displacements_function
        if self._displacements_function is not None:
            self.plot_displacements_button.on_click(displacements_function)

    def remove_displacements_function(self):
        r"""
        Method that removes the current ``self._displacements_function`` as a
        callback handler to the `click` event of
        ``self.plot_displacements_button`` and sets
        ``self._displacements_function = None``.
        """
        if self._displacements_function is not None:
            self.plot_displacements_button.on_click(
                    self._displacements_function, remove=True)
            self._displacements_function = None

    def replace_displacements_function(self, displacements_function):
        r"""
        Method that replaces the current ``self._displacements_function`` with
        the given `displacements_function` as a callback handler to the `click`
        event of ``self.plot_displacements_button``.

        Parameters
        ----------
        displacements_function : `callable` or ``None``, optional
            The function that behaves as a callback handler of the `click`
            event of ``self.plot_displacements_button``. Its signature is
            ``displacements_function(name)``. If ``None``, then nothing is
            added.
        """
        # remove old function
        self.remove_displacements_function()

        # add new function
        self.add_displacements_function(displacements_function)

    def add_errors_function(self, errors_function):
        r"""
        Method that adds the provided `errors_function` as a callback handler
        to the `click` event of ``self.plot_errors_button``. The given
        function is also stored in ``self._errors_function``.

        Parameters
        ----------
        errors_function : `callable` or ``None``, optional
            The function that behaves as a callback handler of the `click`
            event of ``self.plot_errors_button``. Its signature is
            ``errors_function(name)``. If ``None``, then nothing is added.
        """
        self._errors_function = errors_function
        if self._errors_function is not None:
            self.plot_errors_button.on_click(errors_function)

    def remove_errors_function(self):
        r"""
        Method that removes the current ``self._errors_function`` as a
        callback handler to the `click` event of ``self.plot_errors_button``
        and sets ``self._errors_function = None``.
        """
        if self._errors_function is not None:
            self.plot_errors_button.on_click(self._errors_function, remove=True)
            self._errors_function = None

    def replace_errors_function(self, errors_function):
        r"""
        Method that replaces the current ``self._errors_function`` with
        the given `errors_function` as a callback handler to the `click`
        event of ``self.plot_errors_button``.

        Parameters
        ----------
        errors_function : `callable` or ``None``, optional
            The function that behaves as a callback handler of the `click`
            event of ``self.plot_errors_button``. Its signature is
            ``errors_function(name)``. If ``None``, then nothing is added.
        """
        # remove old function
        self.remove_errors_function()

        # add new function
        self.add_errors_function(errors_function)

    def add_costs_function(self, costs_function):
        r"""
        Method that adds the provided `costs_function` as a callback handler
        to the `click` event of ``self.plot_costs_button``. The given
        function is also stored in ``self._costs_function``.

        Parameters
        ----------
        costs_function : `callable` or ``None``, optional
            The function that behaves as a callback handler of the `click`
            event of ``self.plot_costs_button``. Its signature is
            ``costs_function(name)``. If ``None``, then nothing is added.
        """
        self._costs_function = costs_function
        if self._costs_function is not None:
            self.plot_costs_button.on_click(costs_function)

    def remove_costs_function(self):
        r"""
        Method that removes the current ``self._costs_function`` as a callback
        handler to the `click` event of ``self.plot_costs_button`` and sets
        ``self._costs_function = None``.
        """
        if self._costs_function is not None:
            self.plot_costs_button.on_click(self._costs_function, remove=True)
            self._costs_function = None

    def replace_costs_function(self, costs_function):
        r"""
        Method that replaces the current ``self._costs_function`` with the
        given `costs_function` as a callback handler to the `click` event of
        ``self.plot_costs_button``.

        Parameters
        ----------
        costs_function : `callable` or ``None``, optional
            The function that behaves as a callback handler of the `click`
            event of ``self.plot_costs_button``. Its signature is
            ``costs_function(name)``. If ``None``, then nothing is added.
        """
        # remove old function
        self.remove_costs_function()

        # add new function
        self.add_costs_function(costs_function)

    def _save_options(self, change):
        if (self.result_iterations_tab.selected_index == 0 or
                self.n_shapes is None):
            # Result tab
            self.selected_values = {
                'render_final_shape': self.shape_buttons[2].value,
                'render_initial_shape': (self.shape_buttons[1].value and
                                         self.has_initial_shape),
                'render_gt_shape': (self.shape_buttons[3].value and
                                    self.has_gt_shape),
                'render_image': self.render_image.value and self.has_image,
                'subplots_enabled': self.mode.value}
        else:
            # Iterations tab
            if self.iterations_mode.value == 'animation':
                # The mode is 'Animation'
                 iters = self.index_animation.selected_values
            else:
                # The mode is 'Static'
                iters = self.index_slicing.selected_values
            # Get selected values
            self.selected_values = {
                'iters': iters,
                'render_image': self.render_image.value and self.has_image,
                'subplots_enabled': self.mode.value}

    def add_callbacks(self):
        r"""
        Function that adds the handler callback functions in all the widget
        components, which are necessary for the internal functionality.
        """
        self.render_image.observe(self._save_options, names='value',
                                  type='change')
        self.mode.observe(self._save_options, names='value', type='change')
        for w in self.result_box.children[1::]:
            w.observe(self._save_options, names='value', type='change')
        self.index_animation.observe(self._save_options,
                                     names='selected_values', type='change')
        self.index_slicing.observe(self._save_options,
                                   names='selected_values', type='change')
        self.iterations_mode.observe(self._save_options, names='value',
                                     type='change')
        self.result_iterations_tab.observe(
                self._save_options, names='selected_index', type='change')

    def remove_callbacks(self):
        r"""
        Function that removes all the internal handler callback functions.
        """
        self.render_image.unobserve(self._save_options, names='value',
                                    type='change')
        self.mode.unobserve(self._save_options, names='value', type='change')
        for w in self.result_box.children[1::]:
            w.unobserve(self._save_options, names='value', type='change')
        self.index_animation.unobserve(self._save_options,
                                       names='selected_values', type='change')
        self.index_slicing.unobserve(self._save_options,
                                     names='selected_values', type='change')
        self.iterations_mode.unobserve(self._save_options, names='value',
                                       type='change')
        self.result_iterations_tab.unobserve(
                self._save_options, names='selected_index', type='change')

    def set_visibility(self):
        r"""
        Function that sets the visibility of the various components of the
        widget, depending on the properties of the current image object, i.e.
        ``self.n_channels`` and ``self.image_is_masked``.
        """
        self.result_box.children[1].visible = self.has_initial_shape
        self.result_box.children[3].visible = self.has_gt_shape
        self.render_image.visible = self.has_image
        self.plot_errors_button.visible = (self.has_gt_shape and
                                           self._errors_function is not None)
        self.mode_index_buttons_box.visible = self.n_shapes is not None
        self.no_iterations_text.visible = self.n_shapes is None

    def style(self, box_style='', border_visible=False, border_colour='black',
              border_style='solid', border_width=1, border_radius=0, padding=0,
              margin=0, font_family='', font_size=None, font_style='',
              font_weight='', buttons_style='', tabs_box_style=None,
              tabs_border_visible=False, tabs_border_colour='black',
              tabs_border_style='solid', tabs_border_width=1,
              tabs_border_radius=0):
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

        buttons_style : `str` or ``None`` (see below), optional
            Style options:

                'success', 'info', 'warning', 'danger', 'primary', '', None

        tabs_box_style : `str` or ``None`` (see below), optional
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
            The radius of the border around the tab widgets.
        """
        format_box(self, box_style, border_visible, border_colour, border_style,
                   border_width, border_radius, padding, margin)
        format_font(self, font_family, font_size, font_style, font_weight)
        format_font(self.render_image, font_family, font_size, font_style,
                    font_weight)
        format_font(self.mode, font_family, font_size, font_style, font_weight)
        format_font(self.result_box.children[0], font_family, font_size,
                    font_style, font_weight)
        for w in self.result_box.children[1::]:
            format_font(w, font_family, font_size, font_style, font_weight)
            w.button_style = buttons_style
        format_font(self.iterations_mode, font_family, font_size, font_style,
                    font_weight)
        self.index_animation.predefined_style(tabs_box_style)
        tmp_box_style = tabs_box_style
        if tabs_box_style == 'minimal':
            tmp_box_style = ''
        self.index_animation.style(
            box_style=tmp_box_style, border_visible=False, padding=0,
            margin=0, font_family=font_family, font_size=font_size,
            font_style=font_style, font_weight=font_weight)
        self.index_slicing.style(
                box_style=tmp_box_style, border_visible=False, padding=0,
                margin=0, font_family=font_family, font_size=font_size,
                font_style=font_style, font_weight=font_weight)
        self.plot_errors_button.button_style = buttons_style
        self.plot_displacements_button.button_style = buttons_style
        self.plot_costs_button.button_style = buttons_style
        format_box(self.result_box, box_style=tmp_box_style,
                   border_visible=tabs_border_visible,
                   border_colour=tabs_border_colour,
                   border_style=tabs_border_style,
                   border_width=tabs_border_width,
                   border_radius=tabs_border_radius, padding='0.2cm',
                   margin='0.2cm')
        format_box(self.iterations_box, box_style=tmp_box_style,
                   border_visible=tabs_border_visible,
                   border_colour=tabs_border_colour,
                   border_style=tabs_border_style,
                   border_width=tabs_border_width,
                   border_radius=tabs_border_radius, padding='0.2cm',
                   margin='0.2cm')

    def predefined_style(self, style, tabs_style):
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
        if style == 'minimal':
            self.style(box_style='', border_visible=True,
                       border_colour='black', border_style='solid',
                       border_width=1, border_radius=0, padding='0.2cm',
                       margin='0.3cm', font_family='', font_size=None,
                       font_style='', font_weight='', buttons_style='',
                       tabs_box_style=None, tabs_border_visible=True)
        elif (style == 'info' or style == 'success' or style == 'danger' or
                      style == 'warning'):
            self.style(box_style=style, border_visible=True,
                       border_colour=map_styles_to_hex_colours(style),
                       border_style='solid', border_width=1, border_radius=10,
                       padding='0.2cm', margin='0.3cm', font_family='',
                       font_size=None, font_style='', font_weight='',
                       buttons_style='primary', tabs_box_style=tabs_style,
                       tabs_border_visible=True,
                       tabs_border_colour=map_styles_to_hex_colours(tabs_style),
                       tabs_border_style='solid', tabs_border_width=1,
                       tabs_border_radius=10)
        else:
            raise ValueError('style must be minimal or info or success or '
                             'danger or warning')

    def set_widget_state(self, has_gt_shape, has_initial_shape, has_image,
                         n_shapes, has_costs, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        has_gt_shape : `bool`
            Whether the fitting result object has the ground truth shape.
        has_initial_shape : `bool`
            Whether the fitting result object has the initial shape.
        has_image : `bool`
            Whether the fitting result object has the image.
        n_shapes : `int` or ``None``
            The total number of shapes. If ``None``, then it is assumed
            that no iteration shapes are available.
        has_costs : `bool`
            Whether the fitting result object has the costs attached.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # keep old value
        old_value = self.selected_values

        # check if updates are required
        if (self.has_gt_shape != has_gt_shape or
                self.has_initial_shape != has_initial_shape or
                self.has_image != has_image or
                self.n_shapes != n_shapes):
            # temporarily remove callbacks
            render_function = self._render_function
            self.remove_render_function()
            self.remove_callbacks()

            # Update widgets
            if self.n_shapes != n_shapes and n_shapes is not None:
                index = {'min': 0, 'max': n_shapes - 1, 'step': 1, 'index': 0}
                self.index_animation.set_widget_state(index,
                                                      allow_callback=False)
                slice_options = {'command': 'range({})'.format(n_shapes),
                                 'length': n_shapes}
                self.index_slicing.set_widget_state(slice_options,
                                                    allow_callback=False)

            # Assign properties
            self.has_gt_shape = has_gt_shape
            self.has_initial_shape = has_initial_shape
            self.has_image = has_image
            self.n_shapes = n_shapes

            # Set widget's visibility
            self.set_visibility()

            # Get values
            self._save_options({})

            # Re-assign callbacks
            self.add_callbacks()
            self.add_render_function(render_function)

        # set costs button visibility
        self.plot_costs_button.visible = has_costs

        # trigger render function if allowed
        if allow_callback:
            self.call_render_function(old_value, self.selected_values)
