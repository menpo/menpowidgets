import ipywidgets
from traitlets.traitlets import Dict

from menpowidgets.abstract import MenpoWidget
from menpowidgets.options import AnimationOptionsWidget
from menpowidgets.style import (format_font, format_box,
                                map_styles_to_hex_colours)


class FittingResultOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting options when visualizing a fitting result.
    The widget consists of the following parts from `IPython.html.widgets`:

    == =================== ========================= ========================
    No Object              Variable (`self.`)        Description
    == =================== ========================= ========================
    1  Latex, ToggleButton `shape_selection`         The shape selectors
    2  Checkbox            `render_image`            Controls image rendering
    3  RadioButtons        `mode`                    The figure mode
    4  HBox                `shapes_wid`              Contains all 1
    5  VBox                `shapes_and_render_image` Contains 4, 2
    == =================== ========================= ========================

    Note that:

    * The selected options are stored in the ``self.selected_options`` `dict`.
    * To set the styling please refer to the ``style()`` and
      ``predefined_style()`` methods.
    * To update the state of the widget, please refer to the
      ``set_widget_state()`` method.
    * To update the callback function please refer to the
      ``replace_render_function()`` method.

    Parameters
    ----------
    fitting_result_options : `dict`
        The dictionary with the initial options. For example
        ::

            fitting_result_options = {'all_groups': ['initial', 'final',
                                                     'ground'],
                                      'selected_groups': ['final'],
                                      'render_image': True,
                                      'subplots_enabled': True}

    render_function : `function` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    style : See Below, optional
        Sets a predefined style at the widget. Possible options are

            ========= ============================
            Style     Description
            ========= ============================
            'minimal' Simple black and white style
            'success' Green-based style
            'info'    Blue-based style
            'warning' Yellow-based style
            'danger'  Red-based style
            ''        No style
            ========= ============================

    Example
    -------
    Let's create a fitting result options widget and then update its state.
    Firstly, we need to import it:

        >>> from menpowidgets.menpofit.options import FittingResultOptionsWidget

    Now let's define a render function that will get called on every widget
    change and will dynamically print the selected options:

        >>> from menpo.visualize import print_dynamic
        >>> def render_function(name, value):
        >>>     s = "Selected groups: {}, Render image: {}, Subplots enabled: {}".format(
        >>>         wid.selected_values['selected_groups'],
        >>>         wid.selected_values['render_image'],
        >>>         wid.selected_values['subplots_enabled'])
        >>>     print_dynamic(s)

    Create the widget with some initial options and display it:

        >>> fitting_result_options = {'all_groups': ['initial', 'final',
        >>>                                          'ground'],
        >>>                           'selected_groups': ['final'],
        >>>                           'render_image': True,
        >>>                           'subplots_enabled': True}
        >>> wid = FittingResultOptionsWidget(fitting_result_options,
        >>>                                  render_function=render_function,
        >>>                                  style='info')
        >>> wid

    By changing the various widgets, the printed message gets updated. Finally,
    let's change the widget status with a new set of options:

        >>> fitting_result_options = {'all_groups': ['initial', 'final'],
        >>>                           'selected_groups': ['final'],
        >>>                           'render_image': True,
        >>>                           'subplots_enabled': True}
        >>> wid.set_widget_state(fitting_result_options, allow_callback=True)
    """
    def __init__(self, has_groundtruth, n_iters, render_function=None,
                 displacements_function=None, errors_function=None,
                 costs_function=None, style='minimal', tabs_style='minimal'):
        # Initialise default options dictionary
        default_options = {'groups': ['final'], 'mode': 'result',
                           'render_image': True, 'subplots_enabled': True}

        # Assign properties
        self.has_groundtruth = None
        self.n_iters = None
        self.displacements_function = displacements_function
        self.errors_function = errors_function
        self.costs_function = costs_function

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
        self.shape_selection = [
            ipywidgets.Latex(value='Shape:', margin='0.2cm'),
            ipywidgets.ToggleButton(description='Initial', value=False),
            ipywidgets.ToggleButton(description='Final', value=True),
            ipywidgets.ToggleButton(description='Groundtruth', value=False)]
        self.result_box = ipywidgets.HBox(children=self.shape_selection,
                                          align='center', margin='0.2cm',
                                          padding='0.2cm')
        self.iterations_mode = ipywidgets.RadioButtons(
            options={'Animation': 'animation', 'Static': 'static'},
            value='animation', description='Iterations:', margin='0.15cm')
        index = {'min': 0, 'max': n_iters - 1, 'step': 1, 'index': 0}
        self.index_animation = AnimationOptionsWidget(
            index, description='', index_style='slider', loop_enabled=False,
            interval=0.2)
        self.index_slider = ipywidgets.IntRangeSlider(
            min=0, max=n_iters - 1, step=1, value=(0, 0),
            description='', margin='0.15cm', width='6cm', visible=False,
            continuous_udate=False)
        self.plot_errors_button = ipywidgets.Button(
            description='Errors', margin='0.1cm',
            visible=has_groundtruth and errors_function is not None)
        self.plot_displacements_button = ipywidgets.Button(
            description='Displacements', margin='0.1cm',
            visible=displacements_function is not None)
        self.plot_costs_button = ipywidgets.Button(
            description='Costs', margin='0.1cm',
            visible=costs_function is not None)
        self.buttons_box = ipywidgets.HBox(
            children=[self.plot_errors_button, self.plot_costs_button,
                      self.plot_displacements_button])
        self.sliders_buttons_box = ipywidgets.VBox(
            children=[self.index_animation, self.index_slider,
                      self.buttons_box])
        self.iterations_box = ipywidgets.HBox(
            children=[self.iterations_mode, self.sliders_buttons_box],
            margin='0.2cm', padding='0.2cm')
        self.result_iterations_tab = ipywidgets.Tab(
            children=[self.result_box, self.iterations_box], margin='0.2cm')
        self.result_iterations_tab.set_title(0, 'Result')
        self.result_iterations_tab.set_title(1, 'Iterations')

        # Create final widget
        children = [self.mode_render_image_box, self.result_iterations_tab]
        super(FittingResultOptionsWidget, self).__init__(
            children, Dict, default_options, render_function=render_function,
            orientation='horizontal', align='start')

        # Set callbacks
        if displacements_function is not None:
            self.plot_displacements_button.on_click(displacements_function)
        if errors_function is not None:
            self.plot_errors_button.on_click(errors_function)
        if costs_function is not None:
            self.plot_costs_button.on_click(costs_function)

        # Set values
        self.set_widget_state(has_groundtruth, n_iters, allow_callback=False)

        # Set style
        self.predefined_style(style, tabs_style)

    def _save_options(self, name, value):
        # set sliders visiility
        self.index_animation.visible = self.iterations_mode.value == 'animation'
        self.index_slider.visible = self.iterations_mode.value == 'static'
        # control mode and animation slider
        if (self.iterations_mode.value == 'animation' and
                    self.result_iterations_tab.selected_index == 1):
            self.mode.disabled = True
            self.mode.value = False
        else:
            self.mode.disabled = False
        # get options
        if self.result_iterations_tab.selected_index == 0:
            mode = 'result'
            groups = []
            if self.shape_selection[1].value:
                groups.append('initial')
            if self.shape_selection[2].value:
                groups.append('final')
            if self.has_groundtruth and self.shape_selection[3].value:
                groups.append('ground')
        else:
            mode = 'iterations'
            if self.iterations_mode.value == 'animation':
                groups = ['iter_{}'.format(self.index_animation.selected_values)]
            else:
                groups_range = self.index_slider.value
                groups = ['iter_{}'.format(i)
                          for i in range(groups_range[0], groups_range[1] + 1)]
        self.selected_values = {
            'mode': mode,
            'render_image': self.render_image.value,
            'subplots_enabled': self.mode.value,
            'groups': groups}

    def add_callbacks(self):
        self.render_image.on_trait_change(self._save_options, 'value')
        self.mode.on_trait_change(self._save_options, 'value')
        for w in self.result_box.children[1::]:
            w.on_trait_change(self._save_options, 'value')
        self.index_animation.on_trait_change(self._save_options,
                                             'selected_values')
        self.index_slider.on_trait_change(self._save_options, 'value')
        self.iterations_mode.on_trait_change(self._save_options, 'value')
        self.result_iterations_tab.on_trait_change(self._save_options,
                                                   'selected_index')

    def remove_callbacks(self):
        self.render_image.on_trait_change(self._save_options, 'value',
                                          remove=True)
        self.mode.on_trait_change(self._save_options, 'value', remove=True)
        for w in self.result_box.children[1::]:
            w.on_trait_change(self._save_options, 'value', remove=True)
        self.index_animation.on_trait_change(self._save_options,
                                             'selected_values', remove=True)
        self.index_slider.on_trait_change(self._save_options, 'value',
                                          remove=True)
        self.iterations_mode.on_trait_change(self._save_options, 'value',
                                             remove=True)

    def style(self, box_style=None, border_visible=False, border_colour='black',
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
            The colour of the border around the widget.
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

        shapes_buttons_style : See Below, optional
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
        format_font(self.index_slider, font_family, font_size, font_style,
                    font_weight)
        self.index_animation.predefined_style(tabs_box_style)
        self.index_animation.style(
            box_style=tabs_box_style, border_visible=False, padding=0,
            margin=0, font_family=font_family, font_size=font_size,
            font_style=font_style, font_weight=font_weight)
        self.plot_errors_button.button_style = buttons_style
        self.plot_displacements_button.button_style = buttons_style
        self.plot_costs_button.button_style = buttons_style
        format_box(self.result_box, box_style=tabs_box_style,
                   border_visible=tabs_border_visible,
                   border_colour=tabs_border_colour,
                   border_style=border_style,
                   border_width=tabs_border_width,
                   border_radius=tabs_border_radius, padding='0.2cm',
                   margin='0.2cm')
        format_box(self.iterations_box, box_style=tabs_box_style,
                   border_visible=tabs_border_visible,
                   border_colour=tabs_border_colour,
                   border_style=border_style,
                   border_width=tabs_border_width,
                   border_radius=tabs_border_radius, padding='0.2cm',
                   margin='0.2cm')

    def predefined_style(self, style, tabs_style):
        r"""
        Function that sets a predefined style on the widget.

        Parameters
        ----------
        style : `str` (see below)
            Style options

                ========= ============================
                Style     Description
                ========= ============================
                'minimal' Simple black and white style
                'success' Green-based style
                'info'    Blue-based style
                'warning' Yellow-based style
                'danger'  Red-based style
                ''        No style
                ========= ============================
        """
        if style == 'minimal':
            self.style(box_style=None, border_visible=True,
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

    def set_widget_state(self, has_groundtruth, n_iters, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        channel_options : `dict`
            The dictionary with the new options to be used. For example
            ::

                channel_options = {'n_channels': 10,
                                   'image_is_masked': True,
                                   'channels': 0,
                                   'glyph_enabled': False,
                                   'glyph_block_size': 3,
                                   'glyph_use_negative': False,
                                   'sum_enabled': False,
                                   'masked_enabled': True}

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # check if updates are required
        if (self.has_groundtruth != has_groundtruth or
                    self.n_iters != n_iters):
            # temporarily remove callbacks
            render_function = self._render_function
            self.remove_render_function()
            self.remove_callbacks()

            # Update widgets
            if not has_groundtruth:
                self.result_box.children[-1].value = False
            self.plot_errors_button.visible = has_groundtruth and \
                                              self.errors_function is not None
            self.result_box.children[-1].visible = has_groundtruth
            if self.n_iters != n_iters:
                index = {'min': 0, 'max': n_iters - 1, 'step': 1, 'index': 0}
                self.index_animation.set_widget_state(index,
                                                      allow_callback=False)
                self.index_slider.max = n_iters - 1
                self.index_slider.value = (0, 0)

            # Assign properties
            self.has_groundtruth = has_groundtruth
            self.n_iters = n_iters

            # Get values
            self._save_options('', None)

            # Re-assign callbacks
            self.add_callbacks()
            self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self._render_function('', True)
