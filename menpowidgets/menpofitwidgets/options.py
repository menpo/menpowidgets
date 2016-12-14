import ipywidgets
from traitlets.traitlets import Dict

from ..abstract import MenpoWidget
from ..tools import (SlicingCommandWidget, SwitchWidget,
                     MultipleSelectionTogglesWidget)
from ..style import map_styles_to_hex_colours
from ..options import AnimationOptionsWidget


class ResultOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting options when visualizing a fitting result.

    Note that:

    * To update the state of the widget, please refer to the
      :meth:`set_widget_state` method.
    * The selected values are stored in the ``self.selected_values`` `trait`
      which is a `list`.
    * To set the styling of this widget please refer to the
      :meth:`predefined_style` method.
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
    Let's create a fitting result options widget and then update its state.
    Firstly, we need to import it:

        >>> from menpowidgets.options import ResultOptionsWidget

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
                 render_function=None, style=''):
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
        self.mode_title = ipywidgets.Label('Figure mode')
        self.mode = ipywidgets.RadioButtons(
            description='', options={'Single': False, 'Multiple': True},
            value=default_options['subplots_enabled'])
        self.mode_box = ipywidgets.HBox([self.mode_title, self.mode])
        self.mode_box.layout.align_items = 'center'
        self.mode_box.layout.margin = '0px 10px 0px 0px'
        self.render_image = SwitchWidget(
            selected_value=default_options['render_image'],
            description='Render image', description_location='right',
            switch_type='checkbox')
        buttons_style = 'primary' if style != '' else ''
        self.shape_selection = MultipleSelectionTogglesWidget(
            ['Final', 'Initial', 'Groundtruth'], with_labels=['Final'],
            description='Shape', allow_no_selection=True,
            render_function=None, buttons_style=buttons_style)
        self.shape_selection.layout.margin = '0px 10px 0px 0px'
        self.container = ipywidgets.HBox([self.mode_box,
                                          self.shape_selection,
                                          self.render_image])
        self.container.layout.align_items = 'center'

        # Create final widget
        super(ResultOptionsWidget, self).__init__(
            [self.container], Dict, default_options,
            render_function=render_function)

        # Set values
        self.add_callbacks()
        self.set_widget_state(has_gt_shape, has_initial_shape, has_image,
                              allow_callback=False)

        # Set style
        self.predefined_style(style)

    def _save_options(self, change):
        self.selected_values = {
            'render_initial_shape': ('Initial' in
                                     self.shape_selection.selected_values and
                                     self.has_initial_shape),
            'render_final_shape': ('Final' in
                                   self.shape_selection.selected_values),
            'render_gt_shape': ('Groundtruth' in
                                self.shape_selection.selected_values and
                                self.has_gt_shape),
            'render_image': (self.render_image.selected_values and
                             self.has_image),
            'subplots_enabled': self.mode.value}

    def add_callbacks(self):
        r"""
        Function that adds the handler callback functions in all the widget
        components, which are necessary for the internal functionality.
        """
        self.render_image.observe(self._save_options, names='selected_values',
                                  type='change')
        self.mode.observe(self._save_options, names='value', type='change')
        self.shape_selection.observe(self._save_options,
                                     names='selected_values', type='change')

    def remove_callbacks(self):
        r"""
        Function that removes all the internal handler callback functions.
        """
        self.render_image.unobserve(self._save_options, names='selected_values',
                                    type='change')
        self.mode.unobserve(self._save_options, names='value', type='change')
        self.shape_selection.unobserve(self._save_options,
                                       names='selected_values', type='change')

    def set_visibility(self):
        r"""
        Function that sets the visibility of the various components of the
        widget, depending on the properties of the current image object, i.e.
        ``self.n_channels`` and ``self.image_is_masked``.
        """
        self.shape_selection.labels_toggles[1].layout.display = (
            'inline' if self.has_initial_shape else 'none')
        self.shape_selection.labels_toggles[2].layout.display = (
            'inline' if self.has_gt_shape else 'none')
        self.render_image.layout.display = (
            'flex' if self.has_image else 'none')

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
    fitting result.

    Note that:

    * To update the state of the widget, please refer to the
      :meth:`set_widget_state` method.
    * The selected values are stored in the ``self.selected_values`` `trait`
      which is a `list`.
    * To set the styling of this widget please refer to the
      :meth:`predefined_style` method.
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

            ============= ==================
            Style         Description
            ============= ==================
            ``'success'`` Green-based style
            ``'info'``    Blue-based style
            ``'warning'`` Yellow-based style
            ``'danger'``  Red-based style
            ``''``        No style
            ============= ==================

    tabs_style : `str` (see below), optional
        Sets a predefined style at the tab widgets. Possible options are:

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
    Let's create an iterative result options widget and then update its state.
    Firstly, we need to import it:

        >>> from menpowidgets.options import IterativeResultOptionsWidget

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
                 costs_function=None, style='', tabs_style=''):
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
        self.mode_title = ipywidgets.Label('Figure mode')
        self.mode = ipywidgets.RadioButtons(
            description='', options={'Single': False, 'Multiple': True},
            value=default_options['subplots_enabled'])
        self.mode_box = ipywidgets.HBox([self.mode_title, self.mode])
        self.mode_box.layout.align_items = 'center'
        self.render_image = SwitchWidget(
            selected_value=default_options['render_image'],
            description='Render image', description_location='right',
            switch_type='checkbox')
        self.mode_render_image_box = ipywidgets.VBox([self.mode_box,
                                                      self.render_image])
        buttons_style = 'primary' if style != '' else ''
        self.result_box = MultipleSelectionTogglesWidget(
            ['Final', 'Initial', 'Groundtruth'], with_labels=['Final'],
            description='Shape', allow_no_selection=True,
            render_function=None, buttons_style=buttons_style)

        # Create iterations tab
        self.iterations_mode = ipywidgets.RadioButtons(
            options={'Animation': 'animation', 'Static': 'static'},
            value='animation', description='Iterations')
        self.iterations_mode.observe(self._stop_animation, names='value',
                                     type='change')
        self.iterations_mode.observe(self._index_visibility, names='value',
                                     type='change')
        index = {'min': 0, 'max': 1, 'step': 1, 'index': 0}
        self.index_animation = AnimationOptionsWidget(
            index, description='', index_style='slider', loop_enabled=False,
            interval=0., style=tabs_style)
        slice_options = {'command': 'range({})'.format(1), 'length': 1}
        self.index_slicing = SlicingCommandWidget(
            slice_options, description='', example_visible=True,
            continuous_update=False, orientation='vertical')
        self.plot_errors_button = ipywidgets.Button(description='Errors',
                                                    width='63px')
        self.plot_errors_button.layout.display = (
            'inline' if has_gt_shape and errors_function is not None
            else 'none')
        self.plot_displacements_button = ipywidgets.Button(
            description='Displacements', width='120px')
        self.plot_displacements_button.layout.display = (
            'none' if displacements_function is None else 'inline')
        self.plot_costs_button = ipywidgets.Button(description='Costs',
                                                   width='63px')
        self.plot_costs_button.layout.display = ('inline' if has_costs
                                                 else 'none')
        self.buttons_box = ipywidgets.HBox([self.plot_errors_button,
                                            self.plot_costs_button,
                                            self.plot_displacements_button])
        self.buttons_box.layout.align_items = 'center'
        self.index_buttons_box = ipywidgets.VBox([self.index_animation,
                                                  self.index_slicing,
                                                  self.buttons_box])
        self.mode_index_buttons_box = ipywidgets.HBox([self.iterations_mode,
                                                       self.index_buttons_box])
        self.no_iterations_text = ipywidgets.Label(
                value='No iterations available')
        self.iterations_box = ipywidgets.VBox([self.mode_index_buttons_box,
                                               self.no_iterations_text])

        # Create final tab widget
        self.result_iterations_tab = ipywidgets.Tab([self.result_box,
                                                     self.iterations_box])
        self.result_iterations_tab.set_title(0, 'Final')
        self.result_iterations_tab.set_title(1, 'Iterations')
        self.result_iterations_tab.observe(self._stop_animation,
                                           names='selected_index',
                                           type='change')
        self.container = ipywidgets.HBox([self.mode_render_image_box,
                                          self.result_iterations_tab])

        # Function for updating rendering options
        if tab_update_function is not None:
            self.result_iterations_tab.observe(tab_update_function,
                                               names='selected_index',
                                               type='change')
            self.iterations_mode.observe(tab_update_function, names='value',
                                         type='change')

        # Create final widget
        super(IterativeResultOptionsWidget, self).__init__(
            [self.container], Dict, default_options,
            render_function=render_function)

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
        self.index_animation.layout.display = (
            'flex' if change['new'] == 'animation' else 'none')
        self.index_slicing.layout.display = (
            'flex' if change['new'] == 'static' else 'none')

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
                'render_final_shape': ('Final' in
                                       self.result_box.selected_values),
                'render_initial_shape': ('Initial' in
                                         self.result_box.selected_values and
                                         self.has_initial_shape),
                'render_gt_shape': ('Groundtruth' in
                                    self.result_box.selected_values and
                                    self.has_gt_shape),
                'render_image': (self.render_image.selected_values and
                                 self.has_image),
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
                'render_image': (self.render_image.selected_values and
                                 self.has_image),
                'subplots_enabled': self.mode.value}

    def add_callbacks(self):
        r"""
        Function that adds the handler callback functions in all the widget
        components, which are necessary for the internal functionality.
        """
        self.render_image.observe(self._save_options, names='selected_values',
                                  type='change')
        self.mode.observe(self._save_options, names='value', type='change')
        self.result_box.observe(self._save_options, names='selected_values',
                                type='change')
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
        self.render_image.unobserve(self._save_options, names='selected_values',
                                    type='change')
        self.mode.unobserve(self._save_options, names='value', type='change')
        self.result_box.unobserve(self._save_options, names='selected_values',
                                  type='change')
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
        self.result_box.labels_toggles[1].layout.display = (
            'inline' if self.has_initial_shape else 'none')
        self.result_box.labels_toggles[2].layout.display = (
            'inline' if self.has_gt_shape else 'none')
        self.render_image.layout.display = (
            'flex' if self.has_image else 'none')
        self.plot_errors_button.layout.display = (
            'inline' if self.has_gt_shape and self._errors_function is not
            None else 'none')
        self.mode_index_buttons_box.layout.display = (
            'flex' if self.n_shapes is not None else 'none')
        self.no_iterations_text.layout.display = (
            'inline' if self.n_shapes is None else 'none')

    def predefined_style(self, style, tabs_style):
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

        tabs_style : `str` (see below)
            Tabs style options:

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
        self.index_animation.predefined_style(tabs_style)
        self.index_animation.container.layout.border = '0px'
        self.iterations_box.box_style = tabs_style
        self.result_box.box_style = tabs_style
        self.index_slicing.single_slider.slider_color = \
            map_styles_to_hex_colours(tabs_style)
        self.index_slicing.multiple_slider.slider_color = \
            map_styles_to_hex_colours(tabs_style)
        if style != '' or tabs_style != '':
            self.plot_displacements_button.button_style = 'primary'
            self.plot_costs_button.button_style = 'primary'
            self.plot_errors_button.button_style = 'primary'
        else:
            self.plot_displacements_button.button_style = ''
            self.plot_costs_button.button_style = ''
            self.plot_errors_button.button_style = ''

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
