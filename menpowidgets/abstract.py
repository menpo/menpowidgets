from ipywidgets import Box, Layout


class MenpoWidget(Box):
    r"""
    Base class for defining a Menpo widget.

    The widget has a `selected_values` trait that can be used in order to
    inspect any changes that occur to its children. It also has functionality
    for adding, removing, replacing or calling the handler callback function of
    the `selected_values` trait.

    Parameters
    ----------
    children : `list` of `ipywidgets`
        The `list` of `ipywidgets` objects to be set as children in the
        `ipywidgets.Box`.
    trait : `traitlets.TraitType` subclass
        The type of the `selected_values` object that gets added as a trait
        in the widget. Possible options from `traitlets` are {``Int``, ``Float``,
        ``Dict``, ``List``, ``Tuple``}.
    trait_initial_value : `int` or `float` or `dict` or `list` or `tuple`
        The initial value of the `selected_values` trait.
    render_function : `callable` or ``None``, optional
        The render function that behaves as a callback handler of the
        `selected_values` trait for the `change` event. Its signature can be
        ``render_function()`` or ``render_function(change)``, where ``change``
        is a `dict` with the following keys:

        - ``owner`` : the `HasTraits` instance
        - ``old`` : the old value of the modified trait attribute
        - ``new`` : the new value of the modified trait attribute
        - ``name`` : the name of the modified trait attribute.
        - ``type`` : ``'change'``

        If ``None``, then nothing is added.
    """

    def __init__(self, children, trait, trait_initial_value, render_function=None):
        # Create box object
        super(MenpoWidget, self).__init__(children=children)

        # Add trait for selected values
        selected_values = trait(default_value=trait_initial_value)
        selected_values_trait = {"selected_values": selected_values}
        self.add_traits(**selected_values_trait)
        self.selected_values = trait_initial_value

        # Set render function
        self._render_function = None
        self.add_render_function(render_function)

    def add_render_function(self, render_function):
        r"""
        Method that adds the provided `render_function()` as a callback handler
        to the `selected_values` trait of the widget. The given function is
        also stored in `self._render_function`.

        Parameters
        ----------
        render_function : `callable` or ``None``, optional
            The render function that behaves as a callback handler of the
            `selected_values` trait for the `change` event. Its signature can be
            ``render_function()`` or ``render_function(change)``, where
            ``change`` is a `dict` with the following keys:

            - ``owner`` : the `HasTraits` instance
            - ``old`` : the old value of the modified trait attribute
            - ``new`` : the new value of the modified trait attribute
            - ``name`` : the name of the modified trait attribute.
            - ``type`` : ``'change'``

            If ``None``, then nothing is added.
        """
        self._render_function = render_function
        if self._render_function is not None:
            self.observe(self._render_function, names="selected_values", type="change")

    def remove_render_function(self):
        r"""
        Method that removes the current `self._render_function()` as a callback
        handler to the `selected_values` trait of the widget and sets
        ``self._render_function = None``.
        """
        if self._render_function is not None:
            self.unobserve(
                self._render_function, names="selected_values", type="change"
            )
            self._render_function = None

    def replace_render_function(self, render_function):
        r"""
        Method that replaces the current `self._render_function()` with the
        given `render_function()` as a callback handler to the `selected_values`
        trait of the widget.

        Parameters
        ----------
        render_function : `callable` or ``None``, optional
            The render function that behaves as a callback handler of the
            `selected_values` trait for the `change` event. Its signature can be
            ``render_function()`` or ``render_function(change)``, where
            ``change`` is a `dict` with the following keys:

            - ``owner`` : the `HasTraits` instance
            - ``old`` : the old value of the modified trait attribute
            - ``new`` : the new value of the modified trait attribute
            - ``name`` : the name of the modified trait attribute.
            - ``type`` : ``'change'``

            If ``None``, then nothing is added.
        """
        # remove old function
        self.remove_render_function()

        # add new function
        self.add_render_function(render_function)

    def call_render_function(self, old_value, new_value, type_value="change"):
        r"""
        Method that calls the existing `render_function()` callback handler.

        Parameters
        ----------
        old_value : `int` or `float` or `dict` or `list` or `tuple`
            The old `selected_values` value.
        new_value : `int` or `float` or `dict` or `list` or `tuple`
            The new `selected_values` value.
        type_value : `str`, optional
            The trait event type.
        """
        if self._render_function is not None:
            change_dict = {
                "type": "change",
                "old": old_value,
                "name": type_value,
                "new": new_value,
                "owner": self.__str__(),
            }
            self._render_function(change_dict)
