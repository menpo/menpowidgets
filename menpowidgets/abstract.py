import ipywidgets


class MenpoWidget(ipywidgets.FlexBox):
    r"""
    Creates a widget for selecting line rendering options.

    The selected values are stored in `self.selected_values` `dict`. To set the
    styling of this widget please refer to the `style()` method. To update the
    state and function of the widget, please refer to the `set_widget_state()`
    and `replace_render_function()` methods.

    Parameters
    ----------
    children : `list`
        The `list` of `ipywidgets` objects to be set as children in the
        `ipywidgets.FlexBox`.
    trait : `traitlets.traitlets` object
        The type of the `selected_values` object that gets added as a trait
        in the widget.
    trait_initial_value : `int` or `float` or `dict` or `list` or `tuple`
        The initial value of the `selected_values` trait.
    render_function : `function` or ``None``, optional
        The render function that is executed when the widgets'
        `selected_values` trait changes. If ``None``, then nothing is assigned.
    orientation : ``{'horizontal', 'vertical'}``, optional
        The orientation of the `ipywidgets.FlexBox`.
    align : ``{'start', 'center', 'end'}``, optional
        The alignment of the children of the `ipywidgets.FlexBox`.
    """
    def __init__(self, children, trait, trait_initial_value,
                 render_function=None, orientation='vertical', align='start'):
        # Create box object
        super(MenpoWidget, self).__init__(children=children)
        self.orientation = orientation
        self.align = align

        # Add trait for selected values
        selected_values = trait(default_value=trait_initial_value)
        selected_values_trait = {'selected_values': selected_values}
        self.add_traits(**selected_values_trait)

        # Set render function
        self._render_function = None
        self.add_render_function(render_function)

    def add_render_function(self, render_function):
        r"""
        Method that adds a `render_function()` to the widget. The signature of
        the given function is also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback of the
            `selected_values` trait. If ``None``, then nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.on_trait_change(self._render_function, 'selected_values')

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` from the
        widget and sets ``self._render_function = None``.
        """
        if self._render_function is not None:
            self.on_trait_change(self._render_function, 'selected_values',
                                 remove=True)
        self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` of the widget
        with the given `render_function()`.

        Parameters
        ----------
        render_function : `function` or ``None``, optional
            The render function that behaves as a callback of the
            `selected_values` trait. If ``None``, then nothing is added.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)
