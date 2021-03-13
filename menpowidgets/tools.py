from collections import OrderedDict
import ipywidgets
from traitlets.traitlets import List, Int, Float, Dict, Bool, Unicode
from traitlets import link, dlink
from PIL import Image as PILImage
from io import BytesIO
import numpy as np
from base64 import b64decode

from menpo.image import Image

from .abstract import MenpoWidget
from .style import convert_image_to_bytes, parse_font_awesome_icon
from .utils import (
    lists_are_the_same,
    decode_colour,
    parse_slicing_command,
    list_has_constant_step,
    parse_int_range_command,
    parse_float_range_command,
)

# Global variables to try and reduce overhead of loading the logo
MENPO_MINIMAL_LOGO = None
MENPO_DANGER_LOGO = None
MENPO_WARNING_LOGO = None
MENPO_SUCCESS_LOGO = None
MENPO_INFO_LOGO = None


class LogoWidget(ipywidgets.Box):
    r"""
    Creates a widget with Menpo's logo image.

    Parameters
    ----------
    style : ``{'', 'danger', 'info', 'warning', 'success'}``, optional
        Defines the styling of the logo widget, i.e. the colour around the
        logo image.
    """

    def __init__(self, style=""):
        from menpowidgets.base import menpowidgets_src_dir_path
        import menpo.io as mio

        # Try to only load the logo once
        global MENPO_LOGO_SCALE
        logos_path = menpowidgets_src_dir_path() / "logos"
        width = 50
        height = 66.5
        if style == "":
            global MENPO_MINIMAL_LOGO
            if MENPO_MINIMAL_LOGO is None:
                MENPO_MINIMAL_LOGO = mio.import_image(
                    logos_path / "menpoproject_minimal.png"
                )
            self.image = ipywidgets.Image(
                value=convert_image_to_bytes(MENPO_MINIMAL_LOGO),
                width=width,
                height=height,
            )
        elif style == "danger":
            global MENPO_DANGER_LOGO
            if MENPO_DANGER_LOGO is None:
                MENPO_DANGER_LOGO = mio.import_image(
                    logos_path / "menpoproject_{}.png".format(style)
                )
            self.image = ipywidgets.Image(
                value=convert_image_to_bytes(MENPO_DANGER_LOGO),
                width=width,
                height=height,
            )
        elif style == "info":
            global MENPO_INFO_LOGO
            if MENPO_INFO_LOGO is None:
                MENPO_INFO_LOGO = mio.import_image(
                    logos_path / "menpoproject_{}.png".format(style)
                )
            self.image = ipywidgets.Image(
                value=convert_image_to_bytes(MENPO_INFO_LOGO),
                width=width,
                height=height,
            )
        elif style == "warning":
            global MENPO_WARNING_LOGO
            if MENPO_WARNING_LOGO is None:
                MENPO_WARNING_LOGO = mio.import_image(
                    logos_path / "menpoproject_{}.png".format(style)
                )
            self.image = ipywidgets.Image(
                value=convert_image_to_bytes(MENPO_WARNING_LOGO),
                width=width,
                height=height,
            )
        elif style == "success":
            global MENPO_SUCCESS_LOGO
            if MENPO_SUCCESS_LOGO is None:
                MENPO_SUCCESS_LOGO = mio.import_image(
                    logos_path / "menpoproject_{}.png".format(style)
                )
            self.image = ipywidgets.Image(
                value=convert_image_to_bytes(MENPO_SUCCESS_LOGO),
                width=width,
                height=height,
            )
        else:
            raise ValueError(
                "style must be 'minimal', 'info', 'danger', "
                "'warning', 'success' or ''; {} was "
                "given.".format(style)
            )
        super(LogoWidget, self).__init__(children=[self.image])


class SwitchWidget(MenpoWidget):
    r"""
    Creates an on/off switch widget. It can have the form of either a
    checkbox or an on/off toggle button.

    Parameters
    ----------
    selected_value : `bool`
        The initial switch value.
    description : `str`, optional
        The description of the check box.
    switch_type : {``checkbox``, ``toggle``}, optional
        The type of the switch. If ``checkbox``, then `ipywidgets.Checkbox`
        is used. if ``toggle``, then an `ipywidgets.ToggleButton` with
        customized appearance is used.
    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    """

    def __init__(
        self,
        selected_value,
        description="Check me",
        switch_type="checkbox",
        render_function=None,
    ):
        # Create children
        if switch_type == "toggle":
            button_style = "danger"
            if selected_value:
                button_style = "success"
            self.button_wid = ipywidgets.ToggleButton(
                value=selected_value, button_style=button_style, description=description
            )
        elif switch_type == "checkbox":
            self.button_wid = ipywidgets.Checkbox(
                value=selected_value, description=description
            )
        else:
            raise ValueError("switch_type can be either 'toggle' or 'checkbox'")
        self.switch_type = switch_type
        self.container = ipywidgets.HBox((self.button_wid,))
        self.container.layout.align_items = "center"

        # Create final widget
        super(SwitchWidget, self).__init__(
            [self.container], Bool, selected_value, render_function=render_function
        )

        # Set functionality
        def save_value(change):
            if self.switch_type == "toggle":
                if change["new"]:
                    self.button_wid.button_style = "success"
                else:
                    self.button_wid.button_style = "danger"
            self.selected_values = change["new"]

        self.button_wid.observe(save_value, names="value", type="change")

    def set_widget_state(self, selected_value, allow_callback=True):
        r"""
        Method that updates the state of the widget if the provided
        `selected_value` value is different than `self.selected_values`.

        Parameters
        ----------
        selected_value : `bool`
            The selected switch value.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if selected_value != self.selected_values:
            # Keep old value
            old_value = self.selected_values

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update command text and selected values
            self.button_wid.value = selected_value

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)


class ListWidget(MenpoWidget):
    r"""
    Creates a widget for selecting a `list` of numbers. It supports both
    `int` and `float`.

    Parameters
    ----------
    selected_list : `list`
        The initial list of numbers.
    mode : ``{'int', 'float'}``, optional
        Defines the data type of the list members.
    description : `str`, optional
        The description of the command text box.
    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    example_visible : `bool`, optional
        If `True`, then a line with command examples is printed below the
        main text box.
    width : `int`, optional
        The width of the command box in pixels. It includes the status icon
        but not the description.
    """

    def __init__(
        self,
        selected_list,
        mode="float",
        description="Command:",
        render_function=None,
        example_visible=True,
        width=260,
    ):
        # Create children
        selected_cmd = ""
        example_str = ""
        if mode == "int":
            for i in selected_list:
                selected_cmd += "{}, ".format(i)
            if example_visible:
                example_str = (
                    "<font size='1'><em>e.g. '[1, 2]', '10', "
                    "'10, 20', 'range(10)', 'range(1, 8, 2)' etc."
                    "</em></font>"
                )
        elif mode == "float":
            for i in selected_list:
                selected_cmd += "{:.1f}, ".format(i)
            if example_visible:
                example_str = (
                    "<font size='1'><em>e.g. '10.', '10., 20.', "
                    "'range(10.)', 'range(2.5, 5., 2.)' etc."
                    "</em></font>"
                )
        else:
            raise ValueError("mode must be either int or float.")
        self.cmd_description = ipywidgets.HTML(value=description)
        layout = ipywidgets.Layout(width="{}px".format(width - 16))
        self.cmd_text = ipywidgets.Text(
            value=selected_cmd[:-2], placeholder="Type command", layout=layout
        )
        self.example = ipywidgets.HTML(
            value=example_str,
            layout=ipywidgets.Layout(display="inline" if example_visible else "none"),
        )
        self.error_msg = ipywidgets.HTML(
            value="", layout=ipywidgets.Layout(display="none")
        )
        self.state_icon = ipywidgets.HTML(
            value='<i class="fa fa-check" style="color:green"></i>',
            width="16px",
            margin="0.1cm",
        )

        # Group widgets
        self.box_1 = ipywidgets.HBox([self.cmd_text, self.state_icon])
        self.box_1.layout.align_items = "center"
        self.box_2 = ipywidgets.VBox([self.box_1, self.example, self.error_msg])
        self.container = ipywidgets.HBox([self.cmd_description, self.box_2])
        self.container.layout.align_items = "baseline"

        # Create final widget
        super(ListWidget, self).__init__(
            [self.container], List, selected_list, render_function=render_function
        )

        # Assign properties
        self.mode = mode

        # Set functionality
        def save_cmd(name):
            self.error_msg.value = ""
            self.error_msg.layout.display = "none"
            try:
                if self.mode == "int":
                    self.selected_values = parse_int_range_command(
                        str(self.cmd_text.value)
                    )
                else:
                    self.selected_values = parse_float_range_command(
                        str(self.cmd_text.value)
                    )
                self.state_icon.value = (
                    '<i class="fa fa-check" style="color:green"></i>'
                )
            except ValueError as e:
                self.state_icon.value = '<i class="fa fa-times" style="color:red"></i>'
                self.error_msg.value = (
                    '<p style="color:#FF0000";><font size="2"><em>'
                    + str(e)
                    + "</em></font size></p>"
                )
                self.error_msg.layout.display = "inline"

        self.cmd_text.on_submit(save_cmd)

        def typing(_):
            self.state_icon.value = (
                '<i class="fa fa-spinner fa-spin" style="color:black"></i>'
            )

        self.cmd_text.observe(typing, names="value", type="change")

    def set_widget_state(self, selected_list, allow_callback=True):
        r"""
        Method that updates the state of the widget if the provided
        `selected_list` value is different than `self.selected_values`.

        Parameters
        ----------
        selected_list : `list`
            The selected list of numbers.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if not lists_are_the_same(selected_list, self.selected_values):
            # Keep old value
            old_value = self.selected_values

            # Assign new options dict to selected_values
            selected_cmd = ""
            if self.mode == "int":
                for i in selected_list:
                    selected_cmd += "{}, ".format(i)
            elif self.mode == "float":
                for i in selected_list:
                    selected_cmd += "{}, ".format(i)

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update command text and selected values
            self.cmd_text.value = selected_cmd[:-2]
            self.selected_values = selected_list

            # reset status
            self.state_icon.value = '<i class="fa fa-check" style="color:green"></i>'

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)


class MultipleSelectionTogglesWidget(MenpoWidget):
    r"""
    Creates a widget for selecting multiple binary flags from toggle buttons.

    Parameters
    ----------
    labels : `list`
        The available options that are used as toggles' descriptions.
    with_labels : `list` or ``None``, optional
        The items from `labels` that will be selected by default.
    description : `str`, optional
        The description of the widget.
    allow_no_selection : `bool`, optional
        If ``True``, then the user can disable all toggle buttons. If
        ``False``, then if all buttons are turned off they automatically get
        turned on back.
    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    buttons_style : `str`, optional
        The style of the buttons.
    """

    def __init__(
        self,
        labels,
        with_labels=None,
        description="Labels",
        allow_no_selection=False,
        render_function=None,
        buttons_style="",
    ):
        # Check with labels
        if with_labels is None or len(with_labels) == 0:
            with_labels = [l for l in labels]

        # Create children
        self.labels_title = ipywidgets.HTML(value=description)
        self.labels_toggles = []
        for l in labels:
            layout = ipywidgets.Layout(width="{}px".format((len(l) + 2) * 9))
            self.labels_toggles.append(
                ipywidgets.ToggleButton(
                    description=l,
                    value=l in with_labels,
                    layout=layout,
                    button_style=buttons_style,
                )
            )

        # Group widget
        self.box_1 = ipywidgets.HBox(self.labels_toggles)
        self.box_1.layout.flex_flow = "row wrap"
        self.box_1.layout.align_items = "center"
        self.container = ipywidgets.HBox([self.labels_title, self.box_1])
        self.container.layout.align_items = "center"

        # Create final widget
        super(MultipleSelectionTogglesWidget, self).__init__(
            [self.container], List, with_labels, render_function=render_function
        )

        # Set property
        self.labels = labels
        self.buttons_style = buttons_style
        self.allow_no_selection = allow_no_selection

        # Set functionality
        for w in self.labels_toggles:
            w.observe(self._save_options, names="value", type="change")

    def _save_options(self, _):
        value = [w.description for w in self.labels_toggles if w.value]
        if not self.allow_no_selection and len(value) == 0:
            value = []
            for w in self.labels_toggles:
                w.unobserve(self._save_options, names="value", type="change")
                w.value = True
                w.observe(self._save_options, names="value", type="change")
                value.append(w.description)
        self.selected_values = value

    def set_widget_state(self, labels, with_labels=None, allow_callback=True):
        r"""
        Method that updates the state of the widget if the provided
        `labels` or `with_labels` values are different than
        `self.selected_values`.

        Parameters
        ----------
        labels : `list`
            The available options that are used as toggles' descriptions.
        with_labels : `list` or ``None``, optional
            The items from `labels` that will be selected by default.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Check with_labels
        if with_labels is None or len(with_labels) == 0:
            with_labels = [l for l in labels]

        # Keep old value
        old_value = self.selected_values

        # Update widget
        if set(labels) == set(self.labels):
            if set(with_labels) != set(self.selected_values):
                for w in self.labels_toggles:
                    w.unobserve(self._save_options, names="value", type="change")
                    w.value = w.description in with_labels
                    w.observe(self._save_options, names="value", type="change")

                # temporarily remove render callback
                render_function = self._render_function
                self.remove_render_function()

                # Assign with_labels
                self.selected_values = with_labels

                # re-assign render callback
                self.add_render_function(render_function)
        else:
            self.box_1.layout.visibility = "hidden"
            self.labels_toggles = []
            for l in labels:
                layout = ipywidgets.Layout(width="{}px".format((len(l) + 2) * 9))
                w = ipywidgets.ToggleButton(
                    description=l,
                    value=l in with_labels,
                    layout=layout,
                    button_style=self.buttons_style,
                )
                w.observe(self._save_options, names="value", type="change")
                self.labels_toggles.append(w)
            self.box_1.children = self.labels_toggles
            self.box_1.layout.visibility = "visible"
            self.labels = labels

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # Assign with_labels
            self.selected_values = with_labels

            # re-assign render callback
            self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self.call_render_function(old_value, self.selected_values)

    def set_buttons_style(self, buttons_style):
        r"""
        Method that sets the styling of the toggle buttons.

        Parameters
        ----------
        buttons_style : `str` (see below), optional
            Sets a style on the widget's buttons. Possible options are:

                ============= ==================
                Style         Description
                ============= ==================
                ``'primary'`` Blue-based style
                ``'success'`` Green-based style
                ``'info'``    Blue-based style
                ``'warning'`` Yellow-based style
                ``'danger'``  Red-based style
                ``''``        No style
                ============= ==================
        """
        self.buttons_style = buttons_style
        for w in self.labels_toggles:
            w.button_style = buttons_style


class SlicingCommandWidget(MenpoWidget):
    r"""
    Creates a widget for selecting a slicing command.

    Parameters
    ----------
    slice_options : `dict`
        The initial slicing options. It must be a `dict` with:

        * ``command`` : (`str`) The slicing command (e.g. ``':3'``).
        * ``length`` : (`int`) The maximum length (e.g. ``68``).

    description : `str`, optional
        The description of the command text box.
    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    example_visible : `bool`, optional
        If ``True``, then a line with command examples is printed below the
        main text box.
    continuous_update : `bool`, optional
        If ``True``, then the render and update functions are called while
        moving the slider's handle. If ``False``, then the the functions are
        called only when the handle (mouse click) is released.
    orientation : ``{'horizontal', 'vertical'}``, optional
        The orientation between the command text box and the sliders.
    width : `int`, optional
        The width of the command box in pixels. It includes the status icon
        but not the description.
    """

    def __init__(
        self,
        slice_options,
        description="Command",
        render_function=None,
        example_visible=True,
        continuous_update=False,
        orientation="horizontal",
        width=260,
    ):
        # Create children
        indices = parse_slicing_command(
            slice_options["command"], slice_options["length"]
        )
        self.cmd_description = ipywidgets.HTML(value=description)
        layout = ipywidgets.Layout(width="{}px".format(width - 16))
        self.cmd_text = ipywidgets.Text(
            value=slice_options["command"], placeholder="Type command", layout=layout
        )
        self.error_msg = ipywidgets.HTML(
            value="", layout=ipywidgets.Layout(display="none")
        )
        self.state_icon = ipywidgets.HTML(
            value='<i class="fa fa-check" style="color:green"></i>',
            width="16px",
            margin="0.1cm",
        )
        example_str = ""
        if example_visible:
            example_str = self._example_str(slice_options["length"])
        self.example = ipywidgets.HTML(
            value=example_str,
            layout=ipywidgets.Layout(display="inline" if example_visible else "none"),
        )
        layout = ipywidgets.Layout(
            display=self._single_slider_visible(indices),
            width="{}px".format(width - 16),
        )
        self.single_slider = ipywidgets.IntSlider(
            min=0,
            max=slice_options["length"] - 1,
            value=0,
            readout=False,
            continuous_update=continuous_update,
            layout=layout,
        )
        layout = ipywidgets.Layout(
            display=self._multiple_slider_visible(indices)[0],
            width="{}px".format(width - 16),
        )
        self.multiple_slider = ipywidgets.IntRangeSlider(
            min=0,
            max=slice_options["length"] - 1,
            value=(indices[0], indices[-1]),
            width="{}px".format(width - 16),
            readout=False,
            continuous_update=continuous_update,
            layout=layout,
        )

        # Group widgets
        self.box_1 = ipywidgets.HBox([self.cmd_text, self.state_icon])
        self.box_1.layout.align_items = "center"
        self.box_2 = ipywidgets.VBox([self.box_1, self.example, self.error_msg])
        self.box_3 = ipywidgets.VBox([self.single_slider, self.multiple_slider])
        self.box_4 = ipywidgets.Box([self.box_2, self.box_3])
        if orientation == "horizontal":
            self.box_4 = ipywidgets.HBox([self.box_2, self.box_3])
        elif orientation == "vertical":
            self.box_4 = ipywidgets.VBox([self.box_2, self.box_3])
        else:
            raise ValueError("orientation must be 'horizontal' or 'vertical'")
        self.container = ipywidgets.HBox([self.cmd_description, self.box_4])
        self.container.layout.align_items = "baseline"

        # Create final widget
        super(SlicingCommandWidget, self).__init__(
            [self.container], List, indices, render_function=render_function
        )

        # Assign properties
        self.length = slice_options["length"]

        # Set functionality
        def save_cmd(name):
            self.error_msg.value = ""
            self.error_msg.layout.display = "none"
            try:
                self.selected_values = parse_slicing_command(
                    str(self.cmd_text.value), self.length
                )
                self.state_icon.value = (
                    '<i class="fa fa-check" style="color:green"></i>'
                )

                # set single slider visibility and value
                vis = self._single_slider_visible(self.selected_values)
                self.single_slider.layout.display = vis
                if vis == "inline":
                    self.single_slider.unobserve(
                        single_slider_value, names="value", type="change"
                    )
                    self.single_slider.value = self.selected_values[0]
                    self.single_slider.observe(
                        single_slider_value, names="value", type="change"
                    )

                # set multiple slider visibility and value
                vis, step = self._multiple_slider_visible(self.selected_values)
                self.multiple_slider.layout.display = vis
                if vis == "inline":
                    self.multiple_slider.step = step
                    self.multiple_slider.unobserve(
                        multiple_slider_value, names="value", type="change"
                    )
                    self.multiple_slider.value = (
                        self.selected_values[0],
                        self.selected_values[-1],
                    )
                    self.multiple_slider.observe(
                        multiple_slider_value, names="value", type="change"
                    )
            except ValueError as e:
                self.state_icon.value = '<i class="fa fa-times" style="color:red"></i>'
                self.single_slider.layout.display = "none"
                self.multiple_slider.layout.display = "none"
                self.error_msg.value = (
                    '<p style="color:#FF0000";><em>' + str(e) + "</em></p>"
                )
                self.error_msg.layout.display = "inline"

        self.cmd_text.on_submit(save_cmd)

        def single_slider_value(change):
            value = change["new"]
            self.selected_values = [value]
            self.cmd_text.value = str(value)
            self.state_icon.value = '<i class="fa fa-check" style="color:green"></i>'

        self.single_slider.observe(single_slider_value, names="value", type="change")

        def multiple_slider_value(change):
            value = change["new"]
            self.selected_values = list(
                range(value[0], value[1] + 1, self.multiple_slider.step)
            )
            self.cmd_text.value = "{}:{}:{}".format(
                value[0], value[1] + 1, self.multiple_slider.step
            )
            self.state_icon.value = '<i class="fa fa-check" style="color:green"></i>'

        self.multiple_slider.observe(
            multiple_slider_value, names="value", type="change"
        )

        def typing(_):
            self.state_icon.value = (
                '<i class="fa fa-spinner fa-spin" style="color:black"></i>'
            )

        self.cmd_text.observe(typing, names="value", type="change")

        # Set state
        self.set_widget_state(slice_options, allow_callback=False)

    def _example_str(self, length):
        return (
            "<font size='1'><em>e.g. ':2', '-2:', '1:{}:2', '2::', "
            "'0, {}', '{}', 'range({})' etc.</em></font>".format(
                length, length, length - 1, length
            )
        )

    def _single_slider_visible(self, selected_values):
        return "inline" if len(selected_values) == 1 else "none"

    def _multiple_slider_visible(self, selected_values):
        vis, step = list_has_constant_step(selected_values)
        return "inline" if vis else "none", step

    def set_widget_state(self, slice_options, allow_callback=True):
        r"""
        Method that updates the state of the widget if the provided
        `slice_options` value is different than `self.selected_values`.

        Parameters
        ----------
        slice_options : `dict`
            The new slicing options. It must be a `dict` with:

            * ``command`` : (`str`) The slicing command (e.g. ``':3'``).
            * ``length`` : (`int`) The maximum length (e.g. ``68``).

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Assign new options dict to selected_values
        self.length = slice_options["length"]

        # decode command
        indices = parse_slicing_command(
            slice_options["command"], slice_options["length"]
        )

        # Update example str
        self.example.value = self._example_str(slice_options["length"])

        # Keep old value
        old_value = self.selected_values

        # temporarily remove render callback
        render_function = self._render_function
        self.remove_render_function()

        # update selected values
        self.selected_values = indices

        # update single slider
        vis = self._single_slider_visible(self.selected_values)
        self.single_slider.layout.display = vis
        self.single_slider.max = self.length - 1
        if vis == "inline":
            self.single_slider.value = self.selected_values[0]

        # update multiple slider
        vis, step = self._multiple_slider_visible(self.selected_values)
        self.multiple_slider.layout.display = vis
        self.multiple_slider.max = self.length - 1
        if vis == "inline":
            self.multiple_slider.step = step
            self.multiple_slider.value = (
                self.selected_values[0],
                self.selected_values[-1],
            )

        # update command text
        self.cmd_text.value = slice_options["command"]

        # reset status
        self.state_icon.value = '<i class="fa fa-check" style="color:green"></i>'

        # re-assign render callback
        self.add_render_function(render_function)

        # trigger render function if allowed
        if allow_callback:
            self.call_render_function(old_value, self.selected_values)


class IndexSliderWidget(MenpoWidget):
    r"""
    Creates a widget for selecting an index using a slider.

    Parameters
    ----------
    index : `dict`
        The `dict` with the default options:

        * ``min`` : (`int`) The minimum value (e.g. ``0``).
        * ``max`` : (`int`) The maximum value (e.g. ``100``).
        * ``step`` : (`int`) The index step (e.g. ``1``).
        * ``index`` : (`int`) The index value (e.g. ``10``).

    description : `str`, optional
        The title of the widget.
    continuous_update : `bool`, optional
        If ``True``, then the render and update functions are called while moving
        the slider's handle. If ``False``, then the the functions are called only
        when the handle (mouse click) is released.
    render_function : `callable` or ``None``, optional
        The render function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    """

    def __init__(
        self, index, description="Index", continuous_update=False, render_function=None
    ):
        # Create children
        self.slider_description = ipywidgets.HTML(value=description)
        layout = ipywidgets.Layout(width="5cm")
        self.slider = ipywidgets.IntSlider(
            min=index["min"],
            max=index["max"],
            value=index["index"],
            step=index["step"],
            readout=False,
            layout=layout,
            continuous_update=continuous_update,
        )
        layout = ipywidgets.Layout(width="2cm")
        self.slider_text = ipywidgets.Text(value=str(index["index"]), layout=layout)

        # Create final widget
        self.container = ipywidgets.HBox(
            [self.slider_description, self.slider, self.slider_text]
        )
        self.container.layout.align_items = "center"
        super(IndexSliderWidget, self).__init__(
            [self.container], Int, index["index"], render_function=render_function
        )

        # Set functionality
        def sync_value(_):
            value = int(self.slider_text.value)
            if value < self.slider.min:
                value = self.slider.min
                self.slider_text.value = str(value)
            if value > self.slider.max:
                value = self.slider.max
                self.slider_text.value = str(value)
            self.slider.value = value

        self.slider_text.on_submit(sync_value)

        def save_index(change):
            self.selected_values = change["new"]
            self.slider_text.value = str(change["new"])

        self.slider.observe(save_index, names="value", type="change")

    def set_widget_state(self, index, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided `index`
        values are different than `self.selected_values`.

        Parameters
        ----------
        index : `dict`
            The `dict` with the selected options:

            * ``min`` : (`int`) The minimum value (e.g. ``0``).
            * ``max`` : (`int`) The maximum value (e.g. ``100``).
            * ``step`` : (`int`) The index step (e.g. ``1``).
            * ``index`` : (`int`) The index value (e.g. ``10``).

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Check if update is required
        if (
            index["index"] != self.selected_values
            or index["min"] != self.slider.min
            or index["max"] != self.slider.max
            or index["step"] != self.slider.step
        ):
            # Keep old value
            old_value = self.selected_values

            # temporarily remove render function
            render_function = self._render_function
            self.remove_render_function()

            # set values to slider
            self.slider.min = index["min"]
            self.slider.max = index["max"]
            self.slider.step = index["step"]
            self.slider.value = index["index"]

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, index["index"])


class IndexButtonsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting an index using plus/minus buttons.

    Parameters
    ----------
    index : `dict`
        The `dict` with the default options:

        * ``min`` : (`int`) The minimum value (e.g. ``0``).
        * ``max`` : (`int`) The maximum value (e.g. ``100``).
        * ``step`` : (`int`) The index step (e.g. ``1``).
        * ``index`` : (`int`) The index value (e.g. ``10``).

    render_function : `callable` or ``None``, optional
        The render function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    description : `str`, optional
        The title of the widget.
    minus_description : `str`, optional
        The text/icon of the button that decreases the index. If the `str`
        starts with `'fa-'`, then a font-awesome icon is defined.
    plus_description : `str`, optional
        The title of the button that increases the index. If the `str` starts
        with `'fa-'`, then a font-awesome icon is defined.
    loop_enabled : `bool`, optional
        If ``True``, then if by pressing the buttons we reach the minimum
        (maximum) index values, then the counting will continue from the end
        (beginning). If ``False``, the counting will stop at the minimum
        (maximum) value.
    text_editable : `bool`, optional
        Flag that determines whether the index text will be editable.
    """

    def __init__(
        self,
        index,
        render_function=None,
        description="Index",
        minus_description="fa-minus",
        plus_description="fa-plus",
        loop_enabled=True,
        text_editable=True,
    ):
        # Create children
        self.title = ipywidgets.HTML(value=description)
        m_icon, m_description = parse_font_awesome_icon(minus_description)
        self.button_minus = ipywidgets.Button(
            description=m_description,
            icon=m_icon,
            tooltip="Previous item",
            layout=ipywidgets.Layout(width="1cm"),
        )
        p_icon, p_description = parse_font_awesome_icon(plus_description)
        self.button_plus = ipywidgets.Button(
            description=p_description,
            icon=p_icon,
            tooltip="Next item",
            layout=ipywidgets.Layout(width="1cm"),
        )
        self.index_text = ipywidgets.Text(
            value=str(index["index"]),
            disabled=not text_editable,
            layout=ipywidgets.Layout(width="2cm"),
        )
        self.progress_bar = ipywidgets.IntProgress(
            value=index["index"],
            min=index["min"],
            max=index["max"],
            step=index["step"],
            layout=ipywidgets.Layout(width="4.15cm"),
        )

        # Group widgets
        self.box_1 = ipywidgets.HBox(
            [self.button_minus, self.index_text, self.button_plus]
        )
        self.box_1.layout.align_items = "center"
        self.box_2 = ipywidgets.VBox([self.box_1, self.progress_bar])
        self.box_2.layout.align_items = "center"
        self.container = ipywidgets.HBox([self.title, self.box_2])
        self.container.layout.align_items = "baseline"
        self.container.layout.justify_content = "flex-start"

        # Create final widget
        super(IndexButtonsWidget, self).__init__(
            [self.container], Int, index["index"], render_function=render_function
        )

        # Assign properties
        self.min = index["min"]
        self.max = index["max"]
        self.step = index["step"]
        self.loop_enabled = loop_enabled
        self.text_editable = text_editable

        # Set functionality
        dlink((self.index_text, "value"), (self.progress_bar, "value"))

        def submit_index(_):
            try:
                tmp_val = int(self.index_text.value)
                if tmp_val < self.min:
                    tmp_val = self.min
                    self.index_text.value = str(tmp_val)
                if tmp_val > self.max:
                    tmp_val = self.max
                    self.index_text.value = str(tmp_val)
            except ValueError:
                tmp_val = 0
                self.index_text.value = "0"
            self.selected_values = tmp_val

        self.index_text.on_submit(submit_index)

        def value_plus(name):
            tmp_val = int(self.index_text.value) + self.step
            if tmp_val > self.max:
                if self.loop_enabled:
                    self.index_text.value = str(self.min)
                else:
                    self.index_text.value = str(self.max)
            else:
                self.index_text.value = str(tmp_val)
            self.selected_values = int(self.index_text.value)

        self.button_plus.on_click(value_plus)

        def value_minus(name):
            tmp_val = int(self.index_text.value) - self.step
            if tmp_val < self.min:
                if self.loop_enabled:
                    self.index_text.value = str(self.max)
                else:
                    self.index_text.value = str(self.min)
            else:
                self.index_text.value = str(tmp_val)
            self.selected_values = int(self.index_text.value)

        self.button_minus.on_click(value_minus)

    def set_widget_state(self, index, loop_enabled, text_editable, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided `index`
        value is different than `self.selected_values`.

        Parameters
        ----------
        index : `dict`
            The `dict` with the selected options:

            * ``min`` : (`int`) The minimum value (e.g. ``0``).
            * ``max`` : (`int`) The maximum value (e.g. ``100``).
            * ``step`` : (`int`) The index step (e.g. ``1``).
            * ``index`` : (`int`) The index value (e.g. ``10``).

        loop_enabled : `bool`, optional
            If ``True``, then if by pressing the buttons we reach the minimum
            (maximum) index values, then the counting will continue from the end
            (beginning). If ``False``, the counting will stop at the minimum
            (maximum) value.
        text_editable : `bool`, optional
            Flag that determines whether the index text will be editable.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Update loop_enabled and text_editable
        self.loop_enabled = loop_enabled
        self.text_editable = text_editable
        self.index_text.disabled = not text_editable

        # Check if update is required
        if (
            index["index"] != self.selected_values
            or index["min"] != self.min
            or index["max"] != self.max
            or index["step"] != self.step
        ):
            # Keep old value
            old_value = self.selected_values

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # set value to index text
            self.min = index["min"]
            self.max = index["max"]
            self.step = index["step"]
            self.index_text.value = str(index["index"])

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, index["index"])

            # Update selected_values
            self.selected_values = index["index"]


class ColourSelectionWidget(MenpoWidget):
    r"""
    Creates a widget for colour selection of a single or multiple objects.

    Parameters
    ----------
    colours_list : `list` of `str` or [`float`, `float`, `float`]
        A `list` of colours. If a colour is defined as an `str`, then it must
        either be a hex code or a colour name, such as ::

            'blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black',
            'white', 'pink', 'orange'

        If a colour has the form [`float`, `float`, `float`], then it defines an
        RGB value and must have length 3.
    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    description : `str`, optional
        The description of the widget.
    labels : `list` of `str` or ``None``, optional
        A `list` with the labels' names. If ``None``, then a `list` of the form
        ``label {}`` is automatically defined.
    """

    def __init__(
        self, colours_list, render_function=None, description="Colour", labels=None
    ):
        # Check if multiple mode should be enabled
        if isinstance(colours_list, str):
            colours_list = [colours_list]
        n_labels = len(colours_list)
        multiple = n_labels > 1

        # Decode the colour of the first label
        default_colour = decode_colour(colours_list[0])

        # Create children
        self.wid_description = ipywidgets.HTML(value=description)
        labels_dict = OrderedDict()
        if labels is None:
            labels = []
            for k in range(n_labels):
                labels_dict["label {}".format(k)] = k
                labels.append("label {}".format(k))
        else:
            for k, l in enumerate(labels):
                labels_dict[l] = k
        self.label_dropdown = ipywidgets.Dropdown(
            options=labels_dict, value=0, layout=ipywidgets.Layout(width="3cm")
        )
        self.apply_to_all_button = ipywidgets.Button(
            description=" Apply to all",
            icon="fa-paint-brush",
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.colour_widget = ipywidgets.ColorPicker(
            value=default_colour,
            tooltip="Select colour",
            layout=ipywidgets.Layout(width="3cm"),
        )

        # Group widgets
        self.labels_box = ipywidgets.VBox(
            children=[self.label_dropdown, self.apply_to_all_button]
        )
        self.labels_box.layout.display = "flex" if multiple else "none"
        self.labels_box.layout.align_items = "flex-end"
        self.container = ipywidgets.HBox(
            [self.wid_description, self.labels_box, self.colour_widget]
        )
        self.container.layout.align_items = "baseline"

        # Create final widget
        super(ColourSelectionWidget, self).__init__(
            [self.container], List, colours_list, render_function=render_function
        )

        # Assign properties
        self.labels = labels
        self.n_colours = n_labels
        self.description = description

        # Set functionality
        def apply_to_all_function(name):
            tmp = str(self.colour_widget.value)
            self.selected_values = [tmp] * len(self.selected_values)
            self.label_dropdown.value = 0

        self.apply_to_all_button.on_click(apply_to_all_function)

        def update_colour_wrt_label(change):
            value = change["new"]
            self.colour_widget.value = decode_colour(self.selected_values[value])

        self.label_dropdown.observe(
            update_colour_wrt_label, names="value", type="change"
        )

        def save_colour(change):
            idx = self.label_dropdown.value
            tmp = [v for v in self.selected_values]
            tmp[idx] = str(self.colour_widget.value)
            self.selected_values = tmp

        self.colour_widget.observe(save_colour, names="value", type="change")

    def set_widget_state(self, colours_list, labels=None, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided
        `colours_list` and `labels` values are different than
        `self.selected_values` and `self.labels` respectively.

        Parameters
        ----------
        colours_list : `list` of `str` or [`float`, `float`, `float`]
            A `list` of colours. If a colour is defined as an `str`, then it must
            either be a hex code or a colour name, such as ::

                'blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black',
                'white', 'pink', 'orange'

            If a colour has the form [`float`, `float`, `float`], then it defines
            an RGB value and must have length 3.
        labels : `list` of `str` or ``None``, optional
            A `list` with the labels' names. If ``None``, then a `list` of the
            form ``label {}`` is automatically defined.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if isinstance(colours_list, str):
            colours_list = [colours_list]
        if labels is None:
            labels = ["label {}".format(k) for k in range(len(colours_list))]
        self.n_colours = len(colours_list)

        sel_colours = self.selected_values
        sel_labels = self.labels
        if lists_are_the_same(sel_colours, colours_list) and not lists_are_the_same(
            sel_labels, labels
        ):
            # the provided colours are the same, but the labels changed, so
            # update the labels
            self.labels = labels
            labels_dict = OrderedDict()
            for k, l in enumerate(labels):
                labels_dict[l] = k
            self.label_dropdown.options = labels_dict
            if len(labels) > 1:
                if self.label_dropdown.value > 0:
                    self.label_dropdown.value = 0
                else:
                    self.label_dropdown.value = 1
                    self.label_dropdown.value = 0
        elif not lists_are_the_same(sel_colours, colours_list) and lists_are_the_same(
            sel_labels, labels
        ):
            # the provided labels are the same, but the colours are different
            # keep old value
            old_value = self.selected_values
            # temporarily remove render_function from r, g, b traits
            render_function = self._render_function
            self.remove_render_function()
            # assign colour
            self.selected_values = colours_list
            k = self.label_dropdown.value
            self.colour_widget.value = decode_colour(colours_list[k])
            # re-assign render_function
            self.add_render_function(render_function)
            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)
        elif not lists_are_the_same(
            sel_colours, colours_list
        ) and not lists_are_the_same(sel_labels, labels):
            # keep old value
            old_value = self.selected_values
            # temporarily remove render_function from r, g, b traits
            render_function = self._render_function
            self.remove_render_function()
            # both the colours and the labels are different
            self.labels_box.layout.display = "flex" if len(labels) > 1 else "none"
            self.selected_values = colours_list
            self.labels = labels
            labels_dict = OrderedDict()
            for k, l in enumerate(labels):
                labels_dict[l] = k
            self.label_dropdown.options = labels_dict
            if len(labels) > 1:
                if self.label_dropdown.value > 0:
                    self.label_dropdown.value = 0
                else:
                    self.label_dropdown.value = 1
                    self.label_dropdown.value = 0
            else:
                self.label_dropdown.value = 0
            # update colour widgets
            self.colour_widget.value = decode_colour(colours_list[0])
            # re-assign render_function
            self.add_render_function(render_function)
            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)

    def set_colours(self, colours_list, allow_callback=True):
        r"""
        Method that updates the colour values of the widget.

        Parameters
        ----------
        colours_list : `list` of `str` or [`float`, `float`, `float`]
            A `list` of colours. If a colour is defined as an `str`, then it must
            either be a hex code or a colour name, such as ::

                'blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black',
                'white', 'pink', 'orange'

            If a colour has the form [`float`, `float`, `float`], then it defines
            an RGB value and must have length 3.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.

        Raises
        ------
        ValueError
            You must provide a colour per label.
        """
        # Check provided colours
        if isinstance(colours_list, str):
            colours_list = [colours_list]
        if len(colours_list) != self.n_colours:
            raise ValueError("You must provide a colour per label.")

        # Keep old value
        old_value = self.selected_values

        # Remove render function
        render_fun = self._render_function
        self.remove_render_function()

        # Keep previously selected label
        previous_value = self.label_dropdown.value
        for k, c in enumerate(colours_list):
            self.label_dropdown.value = k
            self.colour_widget.value = c

        # Select previous label
        self.label_dropdown.value = previous_value

        # Add render function
        self.add_render_function(render_fun)

        # Callback
        if allow_callback:
            self.call_render_function(old_value, self.selected_values)

    def disabled(self, value):
        r"""
        Method for disabling the widget.

        Parameters
        ----------
        value : `bool`
            The disability flag.
        """
        self.label_dropdown.disabled = value
        self.colour_widget.disabled = value
        self.apply_to_all_button.disabled = value


class ZoomOneScaleWidget(MenpoWidget):
    r"""
    Creates a widget for selecting zoom options with a single scale.

    Parameters
    ----------
    zoom_options : `dict`
        The `dict` with the default options. It must have the following keys:

        * ``min`` : (`float`) The minimum value (e.g. ``0.1``).
        * ``max`` : (`float`) The maximum value (e.g. ``4.``).
        * ``step`` : (`float`) The zoom step (e.g. ``0.05``).
        * ``zoom`` : (`float`) The zoom value (e.g. ``1.``).

    render_function : `callable` or ``None``, optional
        The render function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    description : `str`, optional
        The title of the widget.
    minus_description : `str`, optional
        The text/icon of the button that zooms_out. If the `str` starts with
        `'fa-'`, then a font-awesome icon is defined.
    plus_description : `str`, optional
        The title of the button that zooms in. If the `str` starts with
        `'fa-'`, then a font-awesome icon is defined.
    continuous_update : `bool`, optional
        If ``True``, then the render and update functions are called while
        moving the zoom slider's handle. If ``False``, then the the functions
        are called only when the handle (mouse click) is released.
    """

    def __init__(
        self,
        zoom_options,
        render_function=None,
        description="Figure scale: ",
        minus_description="fa-search-minus",
        plus_description="fa-search-plus",
        continuous_update=False,
    ):
        # Create children
        self.title = ipywidgets.HTML(value=description)
        m_icon, m_description = parse_font_awesome_icon(minus_description)
        self.button_minus = ipywidgets.Button(
            description=m_description,
            icon=m_icon,
            tooltip="Zoom Out",
            layout=ipywidgets.Layout(width="1cm"),
        )
        p_icon, p_description = parse_font_awesome_icon(plus_description)
        self.button_plus = ipywidgets.Button(
            description=p_description,
            icon=p_icon,
            tooltip="Zoom In",
            layout=ipywidgets.Layout(width="1cm"),
        )
        self.zoom_slider = ipywidgets.FloatSlider(
            value=zoom_options["zoom"],
            min=zoom_options["min"],
            max=zoom_options["max"],
            step=zoom_options["step"],
            readout=False,
            continuous_update=continuous_update,
            layout=ipywidgets.Layout(width="6cm"),
        )
        self.zoom_text = ipywidgets.Text(
            value=str(zoom_options["zoom"]), layout=ipywidgets.Layout(width="1.5cm")
        )

        # Group widgets
        self.container = ipywidgets.HBox(
            [
                self.title,
                self.button_minus,
                self.zoom_slider,
                self.button_plus,
                self.zoom_text,
            ]
        )
        self.container.layout.align_items = "center"
        self.container.layout.justify_content = "flex-start"

        # Create final widget
        super(ZoomOneScaleWidget, self).__init__(
            [self.container],
            Float,
            zoom_options["zoom"],
            render_function=render_function,
        )

        # Set functionality
        def save_zoom_text(_):
            try:
                tmp_val = float(self.zoom_text.value)
                if tmp_val < self.zoom_slider.min:
                    tmp_val = self.zoom_slider.min
                    self.zoom_text.value = str(tmp_val)
                if tmp_val > self.zoom_slider.max:
                    tmp_val = self.zoom_slider.max
                    self.zoom_text.value = str(tmp_val)
            except ValueError:
                tmp_val = 0.0
                self.zoom_text.value = "0"
            self.zoom_slider.value = tmp_val

        self.zoom_text.on_submit(save_zoom_text)

        def save_zoom_slider(change):
            self.zoom_text.value = str(change["new"])
            self.selected_values = change["new"]

        self.zoom_slider.observe(save_zoom_slider, names="value", type="change")

        def value_plus(name):
            tmp_val = float(self.zoom_text.value) + self.zoom_slider.step
            if tmp_val > self.zoom_slider.max:
                self.zoom_slider.value = "{:.2f}".format(self.zoom_slider.max)
            else:
                self.zoom_slider.value = "{:.2f}".format(tmp_val)

        self.button_plus.on_click(value_plus)

        def value_minus(name):
            tmp_val = float(self.zoom_text.value) - self.zoom_slider.step
            if tmp_val < self.zoom_slider.min:
                self.zoom_slider.value = "{:.2f}".format(self.zoom_slider.min)
            else:
                self.zoom_slider.value = "{:.2f}".format(tmp_val)

        self.button_minus.on_click(value_minus)

    def set_widget_state(self, zoom_options, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided
        `zoom_options` value is different than `self.selected_values`.

        Parameters
        ----------
        zoom_options : `dict`
            The `dict` with the selected options. It must have the following
            keys:

            * ``min`` : (`float`) The minimum value (e.g. ``0.1``).
            * ``max`` : (`float`) The maximum value (e.g. ``4.``).
            * ``step`` : (`float`) The zoom step (e.g. ``0.05``).
            * ``zoom`` : (`float`) The zoom value (e.g. ``1.``).

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Check if update is required
        if (
            zoom_options["zoom"] != self.selected_values
            or zoom_options["min"] != self.zoom_slider.min
            or zoom_options["max"] != self.zoom_slider.max
            or zoom_options["step"] != self.zoom_slider.step
        ):
            # keep old value
            old_value = self.selected_values

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update widgets
            self.zoom_slider.min = zoom_options["min"]
            self.zoom_slider.max = zoom_options["max"]
            self.zoom_slider.step = zoom_options["step"]
            self.zoom_slider.value = zoom_options["zoom"]

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)


class ZoomTwoScalesWidget(MenpoWidget):
    r"""
    Creates a widget for selecting zoom options with two scales.

    Parameters
    ----------
    zoom_options : `dict`
        The `dict` with the default options. It must have the following keys:

        * ``min`` : (`float`) The minimum value (e.g. ``0.1``).
        * ``max`` : (`float`) The maximum value (e.g. ``4.``).
        * ``step`` : (`float`) The zoom step (e.g. ``0.05``).
        * ``zoom`` : (`float`) The zoom value (e.g. ``1.``).
        * ``lock_aspect_ratio`` : (`bool`) Flag that locks the aspect ratio.

    render_function : `callable` or ``None``, optional
        The render function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    description : `str`, optional
        The title of the widget.
    minus_description : `str`, optional
        The text/icon of the button that zooms_out. If the `str` starts with
        `'fa-'`, then a font-awesome icon is defined.
    plus_description : `str`, optional
        The title of the button that zooms in. If the `str` starts with
        `'fa-'`, then a font-awesome icon is defined.
    continuous_update : `bool`, optional
        If ``True``, then the render and update functions are called while
        moving the zoom slider's handle. If ``False``, then the the functions
        are called only when the handle (mouse click) is released.
    """

    def __init__(
        self,
        zoom_options,
        render_function=None,
        description="Figure scale: ",
        minus_description="fa-search-minus",
        plus_description="fa-search-plus",
        continuous_update=False,
    ):
        # Create children
        self.title = ipywidgets.HTML(value=description)
        self.x_title = ipywidgets.HTML(value="X")
        self.y_title = ipywidgets.HTML(value="Y")
        m_icon, m_description = parse_font_awesome_icon(minus_description)
        self.x_button_minus = ipywidgets.Button(
            description=m_description,
            icon=m_icon,
            tooltip="Zoom Out",
            layout=ipywidgets.Layout(width="1cm"),
        )
        self.y_button_minus = ipywidgets.Button(
            description=m_description,
            icon=m_icon,
            tooltip="Zoom Out",
            layout=ipywidgets.Layout(width="1cm"),
        )
        p_icon, p_description = parse_font_awesome_icon(plus_description)
        self.x_button_plus = ipywidgets.Button(
            description=p_description,
            icon=p_icon,
            tooltip="Zoom In",
            layout=ipywidgets.Layout(width="1cm"),
        )
        self.y_button_plus = ipywidgets.Button(
            description=p_description,
            icon=p_icon,
            tooltip="Zoom In",
            layout=ipywidgets.Layout(width="1cm"),
        )
        self.x_zoom_slider = ipywidgets.FloatSlider(
            value=zoom_options["zoom"][0],
            min=zoom_options["min"],
            max=zoom_options["max"],
            readout=False,
            continuous_update=continuous_update,
            layout=ipywidgets.Layout(width="6cm"),
        )
        self.y_zoom_slider = ipywidgets.FloatSlider(
            value=zoom_options["zoom"][1],
            min=zoom_options["min"],
            max=zoom_options["max"],
            readout=False,
            continuous_update=continuous_update,
            layout=ipywidgets.Layout(width="6cm"),
        )
        self.x_zoom_text = ipywidgets.Text(
            value=str(zoom_options["zoom"][0]), layout=ipywidgets.Layout(width="1.5cm")
        )
        self.y_zoom_text = ipywidgets.Text(
            value=str(zoom_options["zoom"][1]), layout=ipywidgets.Layout(width="1.5cm")
        )
        self.x_box = ipywidgets.HBox(
            [
                self.x_title,
                self.x_button_minus,
                self.x_zoom_slider,
                self.x_button_plus,
                self.x_zoom_text,
            ]
        )
        self.x_box.layout.align_items = "center"
        self.y_box = ipywidgets.HBox(
            [
                self.y_title,
                self.y_button_minus,
                self.y_zoom_slider,
                self.y_button_plus,
                self.y_zoom_text,
            ]
        )
        self.y_box.layout.align_items = "center"
        self.x_y_box = ipywidgets.VBox([self.x_box, self.y_box])
        self.lock_link = ipywidgets.jslink(
            (self.x_zoom_slider, "value"), (self.y_zoom_slider, "value")
        )
        lock_icon = "link"
        if not zoom_options["lock_aspect_ratio"]:
            lock_icon = "unlink"
            self.lock_link.unlink()
        self.lock_aspect_button = ipywidgets.ToggleButton(
            value=zoom_options["lock_aspect_ratio"],
            description="",
            icon=lock_icon,
            tooltip="Keep aspect ratio",
            layout=ipywidgets.Layout(width="0.9cm"),
        )

        # Group widgets
        self.options_box = ipywidgets.HBox([self.lock_aspect_button, self.x_y_box])
        self.options_box.layout.align_items = "center"
        self.container = ipywidgets.HBox([self.title, self.options_box])
        self.container.layout.align_items = "baseline"

        # Create final widget
        super(ZoomTwoScalesWidget, self).__init__(
            [self.container],
            List,
            zoom_options["zoom"],
            render_function=render_function,
        )

        # Assign properties
        self.lock_aspect_ratio = zoom_options["lock_aspect_ratio"]

        # Set functionality
        def save_zoom_text_x(_):
            try:
                tmp_val = float(self.x_zoom_text.value)
                if tmp_val < self.x_zoom_slider.min:
                    tmp_val = self.x_zoom_slider.min
                    self.x_zoom_text.value = str(tmp_val)
                if tmp_val > self.x_zoom_slider.max:
                    tmp_val = self.x_zoom_slider.max
                    self.x_zoom_text.value = str(tmp_val)
            except ValueError:
                tmp_val = 0.0
                self.x_zoom_text.value = "0"
            self.x_zoom_slider.value = tmp_val

        self.x_zoom_text.on_submit(save_zoom_text_x)

        def save_zoom_text_y(_):
            try:
                tmp_val = float(self.y_zoom_text.value)
                if tmp_val < self.y_zoom_slider.min:
                    tmp_val = self.y_zoom_slider.min
                    self.y_zoom_text.value = str(tmp_val)
                if tmp_val > self.y_zoom_slider.max:
                    tmp_val = self.y_zoom_slider.max
                    self.y_zoom_text.value = str(tmp_val)
            except ValueError:
                tmp_val = 0.0
                self.y_zoom_text.value = "0"
            self.y_zoom_slider.value = tmp_val

        self.y_zoom_text.on_submit(save_zoom_text_y)

        def x_value_plus(name):
            tmp_val = float(self.x_zoom_text.value) + self.x_zoom_slider.step
            if tmp_val > self.x_zoom_slider.max:
                self.x_zoom_slider.value = "{:.2f}".format(self.x_zoom_slider.max)
            else:
                self.x_zoom_slider.value = "{:.2f}".format(tmp_val)

        self.x_button_plus.on_click(x_value_plus)

        def x_value_minus(name):
            tmp_val = float(self.x_zoom_text.value) - self.x_zoom_slider.step
            if tmp_val < self.x_zoom_slider.min:
                self.x_zoom_slider.value = "{:.2f}".format(self.x_zoom_slider.min)
            else:
                self.x_zoom_slider.value = "{:.2f}".format(tmp_val)

        self.x_button_minus.on_click(x_value_minus)

        def y_value_plus(name):
            tmp_val = float(self.y_zoom_text.value) + self.y_zoom_slider.step
            if tmp_val > self.y_zoom_slider.max:
                self.y_zoom_slider.value = "{:.2f}".format(self.y_zoom_slider.max)
            else:
                self.y_zoom_slider.value = "{:.2f}".format(tmp_val)

        self.y_button_plus.on_click(y_value_plus)

        def y_value_minus(name):
            tmp_val = float(self.y_zoom_text.value) - self.y_zoom_slider.step
            if tmp_val < self.y_zoom_slider.min:
                self.y_zoom_slider.value = "{:.2f}".format(self.y_zoom_slider.min)
            else:
                self.y_zoom_slider.value = "{:.2f}".format(tmp_val)

        self.y_button_minus.on_click(y_value_minus)

        def save_zoom_slider(change):
            value = change["new"]
            if self.lock_aspect_ratio:
                self.selected_values = [value, value]
            else:
                self.selected_values = [
                    self.x_zoom_slider.value,
                    self.y_zoom_slider.value,
                ]
            self.x_zoom_text.value = str(self.selected_values[0])
            self.y_zoom_text.value = str(self.selected_values[1])

        self.x_zoom_slider.observe(save_zoom_slider, names="value", type="change")
        self.y_zoom_slider.observe(save_zoom_slider, names="value", type="change")

        def link_button(change):
            self.lock_aspect_ratio = change["new"]
            if change["new"]:
                self.lock_aspect_button.icon = "link"
                self.lock_link = link(
                    (self.x_zoom_slider, "value"), (self.y_zoom_slider, "value")
                )
                self.selected_values = [
                    self.x_zoom_slider.value,
                    self.x_zoom_slider.value,
                ]
            else:
                self.lock_aspect_button.icon = "unlink"
                self.lock_link.unlink()

        self.lock_aspect_button.observe(link_button, names="value", type="change")

    def set_widget_state(self, zoom_options, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided
        `zoom_options` value is different than `self.selected_values`.

        Parameters
        ----------
        zoom_options : `dict`
            The `dict` with the selected options. It must have the following
            keys:

            * ``min`` : (`float`) The minimum value (e.g. ``0.1``).
            * ``max`` : (`float`) The maximum value (e.g. ``4.``).
            * ``step`` : (`float`) The zoom step (e.g. ``0.05``).
            * ``zoom`` : (`float`) The zoom value (e.g. ``1.``).
            * ``lock_aspect_ratio`` : (`bool`) Flag that locks the aspect ratio.

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Check if update is required
        if (
            not lists_are_the_same(zoom_options["zoom"], self.selected_values)
            or zoom_options["min"] != self.x_zoom_slider.min
            or zoom_options["max"] != self.x_zoom_slider.max
            or zoom_options["step"] != self.x_zoom_slider.step
        ):
            # keep old value
            old_value = self.selected_values

            # temporarily remove render and update functions
            render_function = self._render_function
            self.remove_render_function()

            # update widgets
            self.x_zoom_text.min = zoom_options["min"]
            self.x_zoom_slider.min = zoom_options["min"]
            self.y_zoom_text.min = zoom_options["min"]
            self.y_zoom_slider.min = zoom_options["min"]
            self.x_zoom_text.max = zoom_options["max"]
            self.x_zoom_slider.max = zoom_options["max"]
            self.y_zoom_text.max = zoom_options["max"]
            self.y_zoom_slider.max = zoom_options["max"]
            self.x_zoom_slider.step = zoom_options["step"]
            self.y_zoom_slider.step = zoom_options["step"]
            self.x_zoom_text.value = "{:.2f}".format(zoom_options["zoom"][0])
            self.y_zoom_text.value = "{:.2f}".format(zoom_options["zoom"][1])

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)


class ImageMatplotlibOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting image rendering options with `matplotlib`.

    Parameters
    ----------
    image_options : `dict`
        The initial image options. It must be a `dict` with the following keys:

        * ``alpha`` : (`float`) The alpha value (e.g. ``1.``).
        * ``interpolation`` : (`str`) The interpolation (e.g. ``'bilinear'``).
        * ``cmap_name`` : (`str`) The colourmap (e.g. ``'gray'``).

    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    """

    def __init__(self, image_options, render_function=None):
        # Create children
        self.interpolation_checkbox = SwitchWidget(
            selected_value=image_options["interpolation"] == "none",
            description="Interpolation",
            switch_type="checkbox",
            render_function=None,
        )
        self.alpha_title = ipywidgets.HTML(value="Transparency")
        self.alpha_slider = ipywidgets.FloatSlider(
            value=image_options["alpha"],
            min=0.0,
            max=1.0,
            step=0.05,
            continuous_update=False,
            readout=False,
            layout=ipywidgets.Layout(width="3.5cm"),
        )
        self.alpha_text = ipywidgets.HTML(
            value="{:.2f}".format(image_options["alpha"]),
            layout=ipywidgets.Layout(width="0.9cm"),
        )
        cmap_dict = OrderedDict()
        cmap_dict["None"] = None
        cmap_dict["afmhot"] = "afmhot"
        cmap_dict["autumn"] = "autumn"
        cmap_dict["binary"] = "binary"
        cmap_dict["bone"] = "bone"
        cmap_dict["brg"] = "brg"
        cmap_dict["bwr"] = "bwr"
        cmap_dict["cool"] = "cool"
        cmap_dict["coolwarm"] = "coolwarm"
        cmap_dict["copper"] = "copper"
        cmap_dict["cubehelix"] = "cubehelix"
        cmap_dict["flag"] = "flag"
        cmap_dict["gist_earth"] = "gist_earth"
        cmap_dict["gist_heat"] = "gist_heat"
        cmap_dict["gist_gray"] = "gist_gray"
        cmap_dict["gist_ncar"] = "gist_ncar"
        cmap_dict["gist_rainbow"] = "gist_rainbow"
        cmap_dict["gist_stern"] = "gist_stern"
        cmap_dict["gist_yarg"] = "gist_yarg"
        cmap_dict["gnuplot"] = "gnuplot"
        cmap_dict["gnuplot2"] = "gnuplot2"
        cmap_dict["gray"] = "gray"
        cmap_dict["hot"] = "hot"
        cmap_dict["hsv"] = "hsv"
        cmap_dict["inferno"] = "inferno"
        cmap_dict["jet"] = "jet"
        cmap_dict["magma"] = "magma"
        cmap_dict["nipy_spectral"] = "nipy_spectral"
        cmap_dict["ocean"] = "ocean"
        cmap_dict["pink"] = "pink"
        cmap_dict["plasma"] = "plasma"
        cmap_dict["prism"] = "prism"
        cmap_dict["rainbow"] = "rainbow"
        cmap_dict["seismic"] = "seismic"
        cmap_dict["spectral"] = "spectral"
        cmap_dict["spring"] = "spring"
        cmap_dict["summer"] = "summer"
        cmap_dict["terrain"] = "terrain"
        cmap_dict["viridis"] = "viridis"
        cmap_dict["winter"] = "winter"
        cmap_dict["Blues"] = "Blues"
        cmap_dict["BuGn"] = "BuGn"
        cmap_dict["BuPu"] = "BuPu"
        cmap_dict["GnBu"] = "GnBu"
        cmap_dict["Greens"] = "Greens"
        cmap_dict["Greys"] = "Greys"
        cmap_dict["Oranges"] = "Oranges"
        cmap_dict["OrRd"] = "OrRd"
        cmap_dict["PuBu"] = "PuBu"
        cmap_dict["PuBuGn"] = "PuBuGn"
        cmap_dict["PuRd"] = "PuRd"
        cmap_dict["Purples"] = "Purples"
        cmap_dict["RdPu"] = "RdPu"
        cmap_dict["Reds"] = "Reds"
        cmap_dict["YlGn"] = "YlGn"
        cmap_dict["YlGnBu"] = "YlGnBu"
        cmap_dict["YlOrBr"] = "YlOrBr"
        cmap_dict["YlOrRd"] = "YlOrRd"
        self.cmap_select = ipywidgets.Select(
            options=cmap_dict,
            value="gray",
            layout=ipywidgets.Layout(width="4cm", height="2cm"),
        )
        self.cmap_title = ipywidgets.HTML(value="Colourmap")

        # Group widgets
        self.box_1 = ipywidgets.HBox(
            [self.alpha_title, self.alpha_slider, self.alpha_text]
        )
        self.box_1.layout.align_items = "center"
        self.box_2 = ipywidgets.VBox([self.box_1, self.interpolation_checkbox])
        self.box_3 = ipywidgets.HBox([self.cmap_title, self.cmap_select])
        self.box_3.layout.align_items = "baseline"
        self.box_3.layout.margin = "0px 13px 0px 0px"
        self.container = ipywidgets.HBox([self.box_3, self.box_2])
        self.container.layout.align_items = "flex-start"

        # Create final widget
        super(ImageMatplotlibOptionsWidget, self).__init__(
            [self.container], Dict, image_options, render_function=render_function
        )

        ipywidgets.jslink((self.alpha_slider, "value"), (self.alpha_text, "value"))

        # Set functionality
        def save_options(change):
            interpolation = (
                "bilinear" if self.interpolation_checkbox.selected_values else "none"
            )
            self.selected_values = {
                "interpolation": interpolation,
                "alpha": self.alpha_slider.value,
                "cmap_name": self.cmap_select.value,
            }

        self.interpolation_checkbox.observe(
            save_options, names="selected_values", type="change"
        )
        self.alpha_slider.observe(save_options, names="value", type="change")
        self.cmap_select.observe(save_options, names="value", type="change")

    def set_widget_state(self, image_options, allow_callback=True):
        r"""
        Method that updates the state of the widget if the provided
        `image_options` are different than `self.selected_values`.

        Parameters
        ----------
        image_options : `dict`
            The selected image options. It must be a `dict` with the following
            keys:

            * ``alpha`` : (`float`) The alpha value (e.g. ``1.``).
            * ``interpolation`` : (`str`) The interpolation (e.g. ``'bilinear'``)
            * ``cmap_name`` : (`str`) The colourmap (e.g. ``'gray'``).

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if image_options != self.selected_values:
            # keep old value
            old_value = self.selected_values

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.alpha_slider.value = image_options["alpha"]
            self.interpolation_checkbox.set_widget_state(
                image_options["interpolation"] == "bilinear", allow_callback=False
            )
            self.cmap_select.value = image_options["cmap_name"]

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)


class LineMatplotlibOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting line rendering options for a `matplotlib`
    renderer.

    Parameters
    ----------
    line_options : `dict`
        The initial line options. It must be a `dict` with the following keys:

        * ``render_lines`` : (`bool`) Flag for rendering the lines.
        * ``line_width`` : ('float`) The width of the lines (e.g. ``1.``)
        * ``line_colour`` : (`str`) The colour of the lines (e.g. ``'blue'``).
        * ``line_style`` : (`str`) The style of the lines (e.g. ``'-'``).

    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the show line checkbox.
    render_checkbox_type : {``checkbox``, ``toggle``}, optional
        The type of the rendering switch. If ``checkbox``, then
        `ipywidgets.Checkbox` is used. if ``toggle``, then an
        `ipywidgets.ToggleButton` with customized appearance is used.
    labels : `list` of `str` or ``None``, optional
        A `list` with the labels' names that get passed in to the
        `ColourSelectionWidget`. If ``None``, then a `list` of the form
        ``label {}`` is automatically defined. Note that the labels are defined
        only for the colour option and not the rest of the options.
    """

    def __init__(
        self,
        line_options,
        render_function=None,
        render_checkbox_type="toggle",
        render_checkbox_title="Render lines",
        labels=None,
    ):
        # Create children
        self.render_lines_switch = SwitchWidget(
            line_options["render_lines"],
            description=render_checkbox_title,
            switch_type=render_checkbox_type,
        )
        self.render_lines_switch.layout.margin = "7px"
        self.line_width_title = ipywidgets.HTML(value="Width")
        self.line_width_text = ipywidgets.BoundedFloatText(
            value=line_options["line_width"],
            min=0.0,
            max=10 ** 6,
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.line_style_title = ipywidgets.HTML(value="Style")
        line_style_dict = OrderedDict()
        line_style_dict["solid"] = "-"
        line_style_dict["dashed"] = "--"
        line_style_dict["dash-dot"] = "-."
        line_style_dict["dotted"] = ":"
        self.line_style_dropdown = ipywidgets.Dropdown(
            options=line_style_dict,
            value=line_options["line_style"],
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.line_colour_widget = ColourSelectionWidget(
            line_options["line_colour"],
            description="Colour",
            labels=labels,
            render_function=None,
        )

        # Group widgets
        self.box_1 = ipywidgets.HBox([self.line_width_title, self.line_width_text])
        self.box_1.layout.align_items = "center"
        self.box_2 = ipywidgets.HBox([self.line_style_title, self.line_style_dropdown])
        self.box_2.layout.align_items = "center"
        self.box_3 = ipywidgets.VBox([self.box_2, self.box_1])
        self.box_3.layout.align_items = "flex-end"
        self.box_3.layout.margin = "0px 10px 0px 0px"
        self.box_4 = ipywidgets.HBox([self.box_3, self.line_colour_widget])
        self.container = ipywidgets.VBox([self.render_lines_switch, self.box_4])

        # Create final widget
        super(LineMatplotlibOptionsWidget, self).__init__(
            [self.container], Dict, line_options, render_function=render_function
        )

        # Assign labels
        self.labels = labels

        # Set functionality
        def line_options_visible(change):
            self.box_4.layout.display = "flex" if change["new"] else "none"

        line_options_visible({"new": line_options["render_lines"]})
        self.render_lines_switch.observe(
            line_options_visible, names="selected_values", type="change"
        )

        def save_options(change):
            self.selected_values = {
                "render_lines": self.render_lines_switch.selected_values,
                "line_width": float(self.line_width_text.value),
                "line_colour": self.line_colour_widget.selected_values,
                "line_style": self.line_style_dropdown.value,
            }

        self.render_lines_switch.observe(
            save_options, names="selected_values", type="change"
        )
        self.line_width_text.observe(save_options, names="value", type="change")
        self.line_colour_widget.observe(
            save_options, names="selected_values", type="change"
        )
        self.line_style_dropdown.observe(save_options, names="value", type="change")

    def set_widget_state(self, line_options, labels=None, allow_callback=True):
        r"""
        Method that updates the state of the widget if the provided
        `line_options` are different than `self.selected_values`.

        Parameters
        ----------
        line_options : `dict`
            The selected line options. It must be a `dict` with the following
            keys:

            * ``render_lines`` : (`bool`) Flag for rendering the lines.
            * ``line_width`` : ('float`) The width of the lines (e.g. ``1.``)
            * ``line_colour`` : (`str`) The colour of the lines (e.g. ``'blue'``).
            * ``line_style`` : (`str`) The style of the lines (e.g. ``'-'``).

        labels : `list` of `str` or ``None``, optional
            A `list` with the labels' names that get passed in to the
            `ColourSelectionWidget`. If ``None``, then a `list` of the form
            ``label {}`` is automatically defined.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != line_options:
            # keep old value
            old_value = self.selected_values

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.render_lines_switch.set_widget_state(
                line_options["render_lines"], allow_callback=False
            )
            self.line_colour_widget.set_widget_state(
                line_options["line_colour"], labels=labels, allow_callback=False
            )
            self.labels = labels
            self.line_style_dropdown.value = line_options["line_style"]
            self.line_width_text.value = float(line_options["line_width"])

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)


class LineMayaviOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting line rendering options for a `mayavi`
    renderer.

    Parameters
    ----------
    line_options : `dict`
        The initial line options. It must be a `dict` with the following keys:

        * ``render_lines`` : (`bool`) Flag for rendering the lines.
        * ``line_width`` : ('float`) The width of the lines (e.g. ``1.``)
        * ``line_colour`` : (`str`) The colour of the lines (e.g. ``'blue'``).

    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the show line checkbox.
    render_checkbox_type : {``checkbox``, ``toggle``}, optional
        The type of the rendering switch. If ``checkbox``, then
        `ipywidgets.Checkbox` is used. if ``toggle``, then an
        `ipywidgets.ToggleButton` with customized appearance is used.
    labels : `list` of `str` or ``None``, optional
        A `list` with the labels' names that get passed in to the
        `ColourSelectionWidget`. If ``None``, then a `list` of the form
        ``label {}`` is automatically defined. Note that the labels are defined
        only for the colour option and not the rest of the options.
    """

    def __init__(
        self,
        line_options,
        render_function=None,
        render_checkbox_type="toggle",
        render_checkbox_title="Render lines",
        labels=None,
    ):
        # Create children
        self.render_lines_switch = SwitchWidget(
            line_options["render_lines"],
            description=render_checkbox_title,
            switch_type=render_checkbox_type,
        )
        self.render_lines_switch.layout.margin = "7px"
        self.line_width_title = ipywidgets.HTML(value="Width")
        self.line_width_text = ipywidgets.BoundedFloatText(
            value=line_options["line_width"],
            min=0.0,
            max=10 ** 6,
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.line_colour_widget = ColourSelectionWidget(
            line_options["line_colour"],
            description="Colour",
            labels=labels,
            render_function=None,
        )

        # Group widgets
        self.box_1 = ipywidgets.HBox([self.line_width_title, self.line_width_text])
        self.box_1.layout.align_items = "center"
        self.box_1.layout.margin = "0px 10px 0px 0px"
        self.box_2 = ipywidgets.HBox([self.box_1, self.line_colour_widget])
        self.box_2.layout.align_items = "flex-start"
        self.container = ipywidgets.VBox([self.render_lines_switch, self.box_2])

        # Create final widget
        super(LineMayaviOptionsWidget, self).__init__(
            [self.container], Dict, line_options, render_function=render_function
        )

        # Assign labels
        self.labels = labels

        # Set functionality
        def line_options_visible(change):
            self.box_2.layout.display = "flex" if change["new"] else "none"

        line_options_visible({"new": line_options["render_lines"]})
        self.render_lines_switch.observe(
            line_options_visible, names="selected_values", type="change"
        )

        def save_options(change):
            self.selected_values = {
                "render_lines": self.render_lines_switch.selected_values,
                "line_width": float(self.line_width_text.value),
                "line_colour": self.line_colour_widget.selected_values,
            }

        self.render_lines_switch.observe(
            save_options, names="selected_values", type="change"
        )
        self.line_width_text.observe(save_options, names="value", type="change")
        self.line_colour_widget.observe(
            save_options, names="selected_values", type="change"
        )

    def set_widget_state(self, line_options, labels=None, allow_callback=True):
        r"""
        Method that updates the state of the widget if the provided
        `line_options` are different than `self.selected_values`.

        Parameters
        ----------
        line_options : `dict`
            The selected line options. It must be a `dict` with the following
            keys:

            * ``render_lines`` : (`bool`) Flag for rendering the lines.
            * ``line_width`` : ('float`) The width of the lines (e.g. ``1.``)
            * ``line_colour`` : (`str`) The colour of the lines (e.g. ``'blue'``).

        labels : `list` of `str` or ``None``, optional
            A `list` with the labels' names that get passed in to the
            `ColourSelectionWidget`. If ``None``, then a `list` of the form
            ``label {}`` is automatically defined.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != line_options:
            # keep old value
            old_value = self.selected_values

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.render_lines_switch.set_widget_state(
                line_options["render_lines"], allow_callback=False
            )
            self.line_colour_widget.set_widget_state(
                line_options["line_colour"], labels=labels, allow_callback=False
            )
            self.labels = labels
            self.line_width_text.value = float(line_options["line_width"])

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)


class MarkerMatplotlibOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting marker rendering options for a `matplotlib`
    renderer.

    Parameters
    ----------
    marker_options : `dict`
        The initial marker options. It must be a `dict` with the following keys:

        * ``render_markers`` : (`bool`) Flag for rendering the markers.
        * ``marker_size`` : (`int`) The size of the markers (e.g. ``20``).
        * ``marker_face_colour`` : (`list`) The colours list.
          (e.g. ``['red', 'blue']``).
        * ``marker_edge_colour`` : (`list`) The edge colours list.
          (e.g. ``['black', 'white']``).
        * ``marker_style`` : (`str`) The style of the markers. (e.g. ``'o'``).
        * ``marker_edge_width`` : (`int`) The edges width of the markers.
          (e.g. ``1``).

    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the render marker checkbox.
    render_checkbox_type : {``checkbox``, ``toggle``}, optional
        The type of the rendering switch. If ``checkbox``, then
        `ipywidgets.Checkbox` is used. if ``toggle``, then an
        `ipywidgets.ToggleButton` with customized appearance is used.
    labels : `list` of `str` or ``None``, optional
        A `list` with the labels' names that get passed in to the
        `ColourSelectionWidget`. If ``None``, then a `list` of the form
        ``label {}`` is automatically defined. Note that the labels are defined
        only for the colour option and not the rest of the options.
    """

    def __init__(
        self,
        marker_options,
        render_function=None,
        render_checkbox_type="toggle",
        render_checkbox_title="Render markers",
        labels=None,
    ):
        # Create children
        self.render_markers_switch = SwitchWidget(
            marker_options["render_markers"],
            description=render_checkbox_title,
            switch_type=render_checkbox_type,
        )
        self.render_markers_switch.layout.margin = "7px"
        self.marker_size_title = ipywidgets.HTML(value="Size")
        self.marker_size_text = ipywidgets.BoundedIntText(
            value=marker_options["marker_size"],
            min=0,
            max=10 ** 6,
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.marker_edge_width_title = ipywidgets.HTML(value="Edge width")
        self.marker_edge_width_text = ipywidgets.BoundedFloatText(
            value=marker_options["marker_edge_width"],
            min=0.0,
            max=10 ** 6,
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.marker_style_title = ipywidgets.HTML(value="Style")
        marker_style_dict = OrderedDict()
        marker_style_dict["point"] = "."
        marker_style_dict["pixel"] = ","
        marker_style_dict["circle"] = "o"
        marker_style_dict["triangle down"] = "v"
        marker_style_dict["triangle up"] = "^"
        marker_style_dict["triangle left"] = "<"
        marker_style_dict["triangle right"] = ">"
        marker_style_dict["tri down"] = "1"
        marker_style_dict["tri up"] = "2"
        marker_style_dict["tri left"] = "3"
        marker_style_dict["tri right"] = "4"
        marker_style_dict["octagon"] = "8"
        marker_style_dict["square"] = "s"
        marker_style_dict["pentagon"] = "p"
        marker_style_dict["star"] = "*"
        marker_style_dict["hexagon 1"] = "h"
        marker_style_dict["hexagon 2"] = "H"
        marker_style_dict["plus"] = "+"
        marker_style_dict["x"] = "x"
        marker_style_dict["diamond"] = "D"
        marker_style_dict["thin diamond"] = "d"
        self.marker_style_dropdown = ipywidgets.Dropdown(
            options=marker_style_dict,
            value=marker_options["marker_style"],
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.marker_face_colour_widget = ColourSelectionWidget(
            marker_options["marker_face_colour"],
            description="Face colour",
            labels=labels,
            render_function=None,
        )
        self.marker_edge_colour_widget = ColourSelectionWidget(
            marker_options["marker_edge_colour"],
            description="Edge colour",
            labels=labels,
            render_function=None,
        )

        # Group widgets
        self.box_1 = ipywidgets.HBox([self.marker_size_title, self.marker_size_text])
        self.box_1.layout.align_items = "center"
        self.box_2 = ipywidgets.HBox(
            [self.marker_edge_width_title, self.marker_edge_width_text]
        )
        self.box_2.layout.align_items = "center"
        self.box_3 = ipywidgets.HBox(
            [self.marker_style_title, self.marker_style_dropdown]
        )
        self.box_3.layout.align_items = "center"
        self.box_3 = ipywidgets.VBox([self.box_3, self.box_1, self.box_2])
        self.box_3.layout.align_items = "flex-end"
        self.box_3.layout.margin = "0px 10px 0px 0px"
        self.box_4 = ipywidgets.VBox(
            [self.marker_face_colour_widget, self.marker_edge_colour_widget]
        )
        self.box_5 = ipywidgets.HBox([self.box_3, self.box_4])
        self.container = ipywidgets.VBox([self.render_markers_switch, self.box_5])

        # Create final widget
        super(MarkerMatplotlibOptionsWidget, self).__init__(
            [self.container], Dict, marker_options, render_function=render_function
        )

        # Assign labels
        self.labels = labels

        # Set functionality
        def marker_options_visible(change):
            self.box_5.layout.display = "flex" if change["new"] else "none"

        marker_options_visible({"new": marker_options["render_markers"]})
        self.render_markers_switch.observe(
            marker_options_visible, names="selected_values", type="change"
        )

        def save_options(change):
            self.selected_values = {
                "render_markers": self.render_markers_switch.selected_values,
                "marker_size": int(self.marker_size_text.value),
                "marker_face_colour": self.marker_face_colour_widget.selected_values,
                "marker_edge_colour": self.marker_edge_colour_widget.selected_values,
                "marker_style": self.marker_style_dropdown.value,
                "marker_edge_width": float(self.marker_edge_width_text.value),
            }

        self.render_markers_switch.observe(
            save_options, names="selected_values", type="change"
        )
        self.marker_size_text.observe(save_options, names="value", type="change")
        self.marker_face_colour_widget.observe(
            save_options, names="selected_values", type="change"
        )
        self.marker_edge_colour_widget.observe(
            save_options, names="selected_values", type="change"
        )
        self.marker_style_dropdown.observe(save_options, names="value", type="change")
        self.marker_edge_width_text.observe(save_options, names="value", type="change")

    def set_widget_state(self, marker_options, labels=None, allow_callback=True):
        r"""
        Method that updates the state of the widget if the provided
        `marker_options` are different than `self.selected_values`.

        Parameters
        ----------
        marker_options : `dict`
            The seected marker options. It must be a `dict` with the following
            keys:

            * ``render_markers`` : (`bool`) Flag for rendering the markers.
            * ``marker_size`` : (`int`) The size of the markers (e.g. ``20``).
            * ``marker_face_colour`` : (`list`) The colours list.
              (e.g. ``['red', 'blue']``).
            * ``marker_edge_colour`` : (`list`) The edge colours list.
              (e.g. ``['black', 'white']``).
            * ``marker_style`` : (`str`) The size of the markers. (e.g. ``'o'``).
            * ``marker_edge_width`` : (`int`) The esdge width of the markers.
              (e.g. ``1``).

        labels : `list` of `str` or ``None``, optional
            A `list` with the labels' names that get passed in to the
            `ColourSelectionWidget`. If ``None``, then a `list` of the form
            ``label {}`` is automatically defined.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != marker_options:
            # keep old value
            old_value = self.selected_values

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.render_markers_switch.set_widget_state(
                marker_options["render_markers"], allow_callback=False
            )
            self.marker_face_colour_widget.set_widget_state(
                marker_options["marker_face_colour"],
                labels=labels,
                allow_callback=False,
            )
            self.marker_edge_colour_widget.set_widget_state(
                marker_options["marker_edge_colour"],
                labels=labels,
                allow_callback=False,
            )
            self.labels = labels
            self.marker_style_dropdown.value = marker_options["marker_style"]
            self.marker_size_text.value = int(marker_options["marker_size"])
            self.marker_edge_width_text.value = float(
                marker_options["marker_edge_width"]
            )

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)


class MarkerMayaviOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting marker rendering options for a `mayavi`
    renderer.

    Parameters
    ----------
    marker_options : `dict`
        The initial marker options. It must be a `dict` with the following keys:

        * ``render_markers`` : (`bool`) Flag for rendering the markers.
        * ``marker_style`` : (`str`) The style of the markers. (e.g. ``'o'``).
        * ``marker_size`` : (`float`) The size of the markers (e.g. ``1.``).
        * ``marker_resolution`` : (`int`) The resolution of the markers (e.g. ``8``).
        * ``marker_colour`` : (`list`) The colours list. (e.g. ``['red', 'blue']``).

    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the render marker checkbox.
    render_checkbox_type : {``checkbox``, ``toggle``}, optional
        The type of the rendering switch. If ``checkbox``, then
        `ipywidgets.Checkbox` is used. if ``toggle``, then an
        `ipywidgets.ToggleButton` with customized appearance is used.
    labels : `list` of `str` or ``None``, optional
        A `list` with the labels' names that get passed in to the
        `ColourSelectionWidget`. If ``None``, then a `list` of the form
        ``label {}`` is automatically defined. Note that the labels are defined
        only for the colour option and not the rest of the options.
    """

    def __init__(
        self,
        marker_options,
        render_function=None,
        render_checkbox_type="toggle",
        render_checkbox_title="Render markers",
        labels=None,
    ):
        # Create children
        self.render_markers_switch = SwitchWidget(
            marker_options["render_markers"],
            description=render_checkbox_title,
            switch_type=render_checkbox_type,
        )
        self.render_markers_switch.layout.margin = "7px"
        self.marker_size_title = ipywidgets.HTML(value="Size")
        m1 = marker_options["marker_size"]
        m2 = False
        m_icon = "fa-keyboard-o"
        if marker_options["marker_size"] is None:
            m1 = 0.1
            m2 = True
            m_icon = "fa-times"
        self.marker_size_text = ipywidgets.BoundedFloatText(
            value=m1,
            disabled=m2,
            min=0,
            max=10 ** 6,
            layout=ipywidgets.Layout(width="1.9cm"),
        )
        self.marker_size_none = ipywidgets.Button(
            description="",
            icon=m_icon,
            layout=ipywidgets.Layout(width="1.0cm", height="0.8cm"),
        )
        self.marker_resolution_title = ipywidgets.HTML(value="Resolution")
        self.marker_resolution_text = ipywidgets.BoundedIntText(
            value=marker_options["marker_resolution"],
            min=0.0,
            max=10 ** 6,
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.marker_style_title = ipywidgets.HTML(value="Style")
        marker_style_dict = OrderedDict()
        marker_style_dict["Sphere"] = "sphere"
        marker_style_dict["Cube"] = "cube"
        marker_style_dict["Cone"] = "cone"
        marker_style_dict["Cylinder"] = "cylinder"
        marker_style_dict["Arrow"] = "arrow"
        marker_style_dict["Axes"] = "axes"
        marker_style_dict["Point"] = "point"
        marker_style_dict["2D arrow"] = "2darrow"
        marker_style_dict["2D circle"] = "2dcircle"
        marker_style_dict["2D cross"] = "2dcross"
        marker_style_dict["2D dash"] = "2ddash"
        marker_style_dict["2D diamond"] = "2ddiamond"
        marker_style_dict["2D hooked arrow"] = "2dhooked_arrow"
        marker_style_dict["2D square"] = "2dsquare"
        marker_style_dict["2D thick arrow"] = "2dthick_arrow"
        marker_style_dict["2D thick cross"] = "2dthick_cross"
        marker_style_dict["2D triangle"] = "2dtriangle"
        marker_style_dict["2D vertex"] = "2dvertex"
        self.marker_style_dropdown = ipywidgets.Dropdown(
            options=marker_style_dict,
            value=marker_options["marker_style"],
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.step_title = ipywidgets.HTML(value="Sampling")
        self.step_text = ipywidgets.BoundedIntText(
            value=marker_options["step"],
            min=0.0,
            max=10 ** 6,
            layout=ipywidgets.Layout(width="2.6cm"),
        )
        self.marker_colour_widget = ColourSelectionWidget(
            marker_options["marker_colour"],
            description="Colour",
            labels=labels,
            render_function=None,
        )

        # Group widgets
        self.box_1 = ipywidgets.HBox(
            [self.marker_size_title, self.marker_size_text, self.marker_size_none]
        )
        self.box_1.layout.align_items = "center"
        self.box_2 = ipywidgets.HBox(
            [self.marker_resolution_title, self.marker_resolution_text]
        )
        self.box_2.layout.align_items = "center"
        self.box_3 = ipywidgets.HBox(
            [self.marker_style_title, self.marker_style_dropdown]
        )
        self.box_3.layout.align_items = "center"
        self.box_3 = ipywidgets.VBox([self.box_3, self.box_1, self.box_2])
        self.box_3.layout.align_items = "flex-end"
        self.box_3.layout.margin = "0px 10px 0px 0px"
        self.box_44 = ipywidgets.HBox([self.step_title, self.step_text])
        self.box_44.layout.align_items = "center"
        self.box_4 = ipywidgets.VBox([self.marker_colour_widget, self.box_44])
        self.box_5 = ipywidgets.HBox([self.box_3, self.box_4])
        self.container = ipywidgets.VBox([self.render_markers_switch, self.box_5])

        # Create final widget
        super(MarkerMayaviOptionsWidget, self).__init__(
            [self.container], Dict, marker_options, render_function=render_function
        )

        # Assign labels
        self.labels = labels

        # Set functionality
        def marker_options_visible(change):
            self.box_5.layout.display = "flex" if change["new"] else "none"

        marker_options_visible({"new": marker_options["render_markers"]})
        self.render_markers_switch.observe(
            marker_options_visible, names="selected_values", type="change"
        )

        def save_options(change):
            marker_size = None
            if not self.marker_size_text.disabled:
                marker_size = float(self.marker_size_text.value)
            self.selected_values = {
                "render_markers": self.render_markers_switch.selected_values,
                "marker_size": marker_size,
                "marker_colour": self.marker_colour_widget.selected_values,
                "marker_resolution": int(self.marker_resolution_text.value),
                "marker_style": self.marker_style_dropdown.value,
                "step": int(self.step_text.value),
            }

        self.render_markers_switch.observe(
            save_options, names="selected_values", type="change"
        )
        self.marker_size_text.observe(save_options, names="value", type="change")
        self.marker_colour_widget.observe(
            save_options, names="selected_values", type="change"
        )
        self.marker_style_dropdown.observe(save_options, names="value", type="change")
        self.marker_resolution_text.observe(save_options, names="value", type="change")
        self.step_text.observe(save_options, names="value", type="change")

        def button_icon(_):
            if self.marker_size_text.disabled:
                self.marker_size_none.icon = "fa-keyboard-o"
                self.marker_size_text.disabled = False
            else:
                self.marker_size_none.icon = "fa-times"
                self.marker_size_text.disabled = True
            save_options({})

        self.marker_size_none.on_click(button_icon)

    def set_widget_state(self, marker_options, labels=None, allow_callback=True):
        r"""
        Method that updates the state of the widget if the provided
        `marker_options` are different than `self.selected_values`.

        Parameters
        ----------
        marker_options : `dict`
            The selected marker options. It must be a `dict` with the following
            keys:

            * ``render_markers`` : (`bool`) Flag for rendering the markers.
            * ``marker_style`` : (`str`) The style of the markers. (e.g. ``'o'``).
            * ``marker_size`` : (`float`) The size of the markers (e.g. ``1.``).
            * ``marker_resolution`` : (`int`) The resolution of the markers (e.g. ``8``).
            * ``marker_colour`` : (`list`) The colours list. (e.g. ``['red', 'blue']``).

        labels : `list` of `str` or ``None``, optional
            A `list` with the labels' names that get passed in to the
            `ColourSelectionWidget`. If ``None``, then a `list` of the form
            ``label {}`` is automatically defined.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != marker_options:
            # keep old value
            old_value = self.selected_values

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.render_markers_switch.set_widget_state(
                marker_options["render_markers"], allow_callback=False
            )
            self.marker_style_dropdown.value = marker_options["marker_style"]
            self.marker_colour_widget.set_widget_state(
                marker_options["marker_colour"], labels=labels, allow_callback=False
            )
            self.labels = labels
            if marker_options["marker_size"] is None:
                self.marker_size_text.disabled = True
                self.marker_size_none.icon = "fa-times"
            else:
                self.marker_size_text.disabled = False
                self.marker_size_none.icon = "fa-keyboard-o"
                self.marker_size_text.value = float(marker_options["marker_size"])
            self.marker_resolution_text.value = int(marker_options["marker_resolution"])
            self.step_text.value = int(marker_options["step"])

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)


class NumberingMatplotlibOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting numbering rendering options for
    `matplotlib` renderers.

    Parameters
    ----------
    numbers_options : `dict`
        The initial numbering options. It must be a `dict` with the following
        keys:

        * ``render_numbering`` : (`bool`) Flag for rendering the numbers.
        * ``numbers_font_name`` : (`str`) The font name (e.g. ``'serif'``).
        * ``numbers_font_size`` : (`int`) The font size (e.g. ``10``).
        * ``numbers_font_style`` : (`str`) The font style (e.g. ``'normal'``).
        * ``numbers_font_weight`` : (`str`) The font weight (e.g. ``'normal'``).
        * ``numbers_font_colour`` : (`list`) The font colour (e.g. ``['black']``)
        * ``numbers_horizontal_align`` : (`str`) The horizontal alignment
          (e.g. ``'center'``).
        * ``numbers_vertical_align`` : (`str`) The vertical alignment
          (e.g. ``'bottom'``).

    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the render numbering checkbox.
    render_checkbox_type : {``checkbox``, ``toggle``}, optional
        The type of the rendering switch. If ``checkbox``, then
        `ipywidgets.Checkbox` is used. if ``toggle``, then an
        `ipywidgets.ToggleButton` with customized appearance is used.
    """

    def __init__(
        self,
        numbers_options,
        render_function=None,
        render_checkbox_type="toggle",
        render_checkbox_title="Render numbering",
    ):
        # Create children
        self.render_numbering_switch = SwitchWidget(
            numbers_options["render_numbering"],
            description=render_checkbox_title,
            switch_type=render_checkbox_type,
        )
        self.render_numbering_switch.layout.margin = "7px"
        self.numbers_font_name_title = ipywidgets.HTML(value="Font")
        numbers_font_name_dict = OrderedDict()
        numbers_font_name_dict["serif"] = "serif"
        numbers_font_name_dict["sans-serif"] = "sans-serif"
        numbers_font_name_dict["cursive"] = "cursive"
        numbers_font_name_dict["fantasy"] = "fantasy"
        numbers_font_name_dict["monospace"] = "monospace"
        self.numbers_font_name_dropdown = ipywidgets.Dropdown(
            options=numbers_font_name_dict,
            value=numbers_options["numbers_font_name"],
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.numbers_font_size_title = ipywidgets.HTML(value="Size")
        self.numbers_font_size_text = ipywidgets.BoundedIntText(
            min=0,
            max=10 ** 6,
            value=numbers_options["numbers_font_size"],
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.numbers_font_style_title = ipywidgets.HTML(value="Style")
        numbers_font_style_dict = OrderedDict()
        numbers_font_style_dict["normal"] = "normal"
        numbers_font_style_dict["italic"] = "italic"
        numbers_font_style_dict["oblique"] = "oblique"
        self.numbers_font_style_dropdown = ipywidgets.Dropdown(
            options=numbers_font_style_dict,
            layout=ipywidgets.Layout(width="3cm"),
            value=numbers_options["numbers_font_style"],
        )
        self.numbers_font_weight_title = ipywidgets.HTML(value="Weight")
        numbers_font_weight_dict = OrderedDict()
        numbers_font_weight_dict["normal"] = "normal"
        numbers_font_weight_dict["ultralight"] = "ultralight"
        numbers_font_weight_dict["light"] = "light"
        numbers_font_weight_dict["regular"] = "regular"
        numbers_font_weight_dict["book"] = "book"
        numbers_font_weight_dict["medium"] = "medium"
        numbers_font_weight_dict["roman"] = "roman"
        numbers_font_weight_dict["semibold"] = "semibold"
        numbers_font_weight_dict["demibold"] = "demibold"
        numbers_font_weight_dict["demi"] = "demi"
        numbers_font_weight_dict["bold"] = "bold"
        numbers_font_weight_dict["heavy"] = "heavy"
        numbers_font_weight_dict["extra bold"] = "extra bold"
        numbers_font_weight_dict["black"] = "black"
        self.numbers_font_weight_dropdown = ipywidgets.Dropdown(
            options=numbers_font_weight_dict,
            layout=ipywidgets.Layout(width="3cm"),
            value=numbers_options["numbers_font_weight"],
        )
        self.numbers_font_colour_widget = ColourSelectionWidget(
            numbers_options["numbers_font_colour"],
            description="Colour",
            render_function=None,
        )
        self.numbers_horizontal_align_title = ipywidgets.HTML(value="Horizontal align")
        numbers_horizontal_align_dict = OrderedDict()
        numbers_horizontal_align_dict["center"] = "center"
        numbers_horizontal_align_dict["right"] = "right"
        numbers_horizontal_align_dict["left"] = "left"
        self.numbers_horizontal_align_dropdown = ipywidgets.Dropdown(
            options=numbers_horizontal_align_dict,
            layout=ipywidgets.Layout(width="3cm"),
            value=numbers_options["numbers_horizontal_align"],
        )
        self.numbers_vertical_align_title = ipywidgets.HTML(value="Vertical align")
        numbers_vertical_align_dict = OrderedDict()
        numbers_vertical_align_dict["center"] = "center"
        numbers_vertical_align_dict["top"] = "top"
        numbers_vertical_align_dict["bottom"] = "bottom"
        numbers_vertical_align_dict["baseline"] = "baseline"
        self.numbers_vertical_align_dropdown = ipywidgets.Dropdown(
            options=numbers_vertical_align_dict,
            layout=ipywidgets.Layout(width="3cm"),
            value=numbers_options["numbers_vertical_align"],
        )

        # Group widgets
        self.box_1 = ipywidgets.HBox(
            [self.numbers_font_name_title, self.numbers_font_name_dropdown]
        )
        self.box_1.layout.align_items = "center"
        self.box_2 = ipywidgets.HBox(
            [self.numbers_font_size_title, self.numbers_font_size_text]
        )
        self.box_2.layout.align_items = "center"
        self.box_3 = ipywidgets.HBox(
            [self.numbers_font_style_title, self.numbers_font_style_dropdown]
        )
        self.box_3.layout.align_items = "center"
        self.box_4 = ipywidgets.HBox(
            [self.numbers_font_weight_title, self.numbers_font_weight_dropdown]
        )
        self.box_4.layout.align_items = "center"
        self.box_5 = ipywidgets.HBox(
            [
                self.numbers_horizontal_align_title,
                self.numbers_horizontal_align_dropdown,
            ]
        )
        self.box_5.layout.align_items = "center"
        self.box_6 = ipywidgets.HBox(
            [self.numbers_vertical_align_title, self.numbers_vertical_align_dropdown]
        )
        self.box_6.layout.align_items = "center"
        self.box_7 = ipywidgets.VBox([self.box_1, self.box_2, self.box_3, self.box_4])
        self.box_7.layout.align_items = "flex-end"
        self.box_7.layout.margin = "0px 10px 0px 0px"
        self.box_8 = ipywidgets.VBox(
            [self.numbers_font_colour_widget, self.box_5, self.box_6]
        )
        self.box_8.layout.align_items = "flex-end"
        self.box_9 = ipywidgets.HBox([self.box_7, self.box_8])
        self.container = ipywidgets.VBox([self.render_numbering_switch, self.box_9])

        # Create final widget
        super(NumberingMatplotlibOptionsWidget, self).__init__(
            [self.container], Dict, numbers_options, render_function=render_function
        )

        # Set functionality
        def numbering_options_visible(change):
            self.box_9.layout.display = "flex" if change["new"] else "none"

        numbering_options_visible({"new": numbers_options["render_numbering"]})
        self.render_numbering_switch.observe(
            numbering_options_visible, names="selected_values", type="change"
        )

        def save_options(change):
            self.selected_values = {
                "render_numbering": self.render_numbering_switch.selected_values,
                "numbers_font_name": self.numbers_font_name_dropdown.value,
                "numbers_font_size": int(self.numbers_font_size_text.value),
                "numbers_font_style": self.numbers_font_style_dropdown.value,
                "numbers_font_weight": self.numbers_font_weight_dropdown.value,
                "numbers_font_colour": self.numbers_font_colour_widget.selected_values[
                    0
                ],
                "numbers_horizontal_align": self.numbers_horizontal_align_dropdown.value,
                "numbers_vertical_align": self.numbers_vertical_align_dropdown.value,
            }

        self.render_numbering_switch.observe(
            save_options, names="selected_values", type="change"
        )
        self.numbers_font_name_dropdown.observe(
            save_options, names="value", type="change"
        )
        self.numbers_font_size_text.observe(save_options, names="value", type="change")
        self.numbers_font_style_dropdown.observe(
            save_options, names="value", type="change"
        )
        self.numbers_font_weight_dropdown.observe(
            save_options, names="value", type="change"
        )
        self.numbers_font_colour_widget.observe(
            save_options, names="selected_values", type="change"
        )
        self.numbers_horizontal_align_dropdown.observe(
            save_options, names="value", type="change"
        )
        self.numbers_vertical_align_dropdown.observe(
            save_options, names="value", type="change"
        )

    def set_widget_state(self, numbers_options, allow_callback=True):
        r"""
        Method that updates the state of the widget if the given
        `numbers_options` are different than `self.selected_values`.

        Parameters
        ----------
        numbers_options : `dict`
            The selected numbering options. It must be a `dict` with the
            following keys:

            * ``render_numbering`` : (`bool`) Flag for rendering the numbers.
            * ``numbers_font_name`` : (`str`) The font name (e.g. ``'serif'``).
            * ``numbers_font_size`` : (`int`) The font size (e.g. ``10``).
            * ``numbers_font_style`` : (`str`) The font style (e.g. ``'normal'``).
            * ``numbers_font_weight`` : (`str`) The font weight (e.g. ``'normal'``).
            * ``numbers_font_colour`` : (`colour`) The font colour
              (e.g. ``'black'``)
            * ``numbers_horizontal_align`` : (`str`) The horizontal alignment
              (e.g. ``'center'``).
            * ``numbers_vertical_align`` : (`str`) The vertical alignment
              (e.g. ``'bottom'``).

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != numbers_options:
            # keep old value
            old_value = self.selected_values

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.render_numbering_switch.set_widget_state(
                numbers_options["render_numbering"], allow_callback=False
            )
            self.numbers_font_name_dropdown.value = numbers_options["numbers_font_name"]
            self.numbers_font_size_text.value = int(
                numbers_options["numbers_font_size"]
            )
            self.numbers_font_style_dropdown.value = numbers_options[
                "numbers_font_style"
            ]
            self.numbers_font_weight_dropdown.value = numbers_options[
                "numbers_font_weight"
            ]
            self.numbers_horizontal_align_dropdown.value = numbers_options[
                "numbers_horizontal_align"
            ]
            self.numbers_vertical_align_dropdown.value = numbers_options[
                "numbers_vertical_align"
            ]
            self.numbers_font_colour_widget.set_widget_state(
                numbers_options["numbers_font_colour"], allow_callback=False
            )

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)


class NumberingMayaviOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting numbering rendering options for a `mayavi`
    renderer.

    Parameters
    ----------
    numbers_options : `dict`
        The initial numbering options. It must be a `dict` with the following
        keys:

        * ``render_numbering`` : (`bool`) Flag for rendering the numbers.
        * ``numbers_size`` : (`float`) The font size (e.g. ``10.``).
        * ``numbers_colour`` : (`str`) The font colour (e.g. ``'black'``)

    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the show numbering checkbox.
    render_checkbox_type : {``checkbox``, ``toggle``}, optional
        The type of the rendering switch. If ``checkbox``, then
        `ipywidgets.Checkbox` is used. if ``toggle``, then an
        `ipywidgets.ToggleButton` with customized appearance is used.
    """

    def __init__(
        self,
        numbers_options,
        render_function=None,
        render_checkbox_type="toggle",
        render_checkbox_title="Render numbering",
    ):
        # Create children
        self.render_numbering_switch = SwitchWidget(
            numbers_options["render_numbering"],
            description=render_checkbox_title,
            switch_type=render_checkbox_type,
        )
        self.render_numbering_switch.layout.margin = "7px"
        self.numbers_size_title = ipywidgets.HTML(value="Size")
        n1 = numbers_options["numbers_size"]
        n2 = False
        n_icon = "fa-keyboard-o"
        if numbers_options["numbers_size"] is None:
            n1 = 0.1
            n2 = True
            n_icon = "fa-times"
        self.numbers_size_text = ipywidgets.BoundedFloatText(
            value=n1,
            disabled=n2,
            min=0.0,
            max=10 ** 6,
            layout=ipywidgets.Layout(width="1.9cm"),
        )
        self.numbers_size_none = ipywidgets.Button(
            description="",
            icon=n_icon,
            layout=ipywidgets.Layout(width="1.0cm", height="0.8cm"),
        )
        self.numbers_colour_widget = ColourSelectionWidget(
            numbers_options["numbers_colour"],
            description="Colour",
            render_function=None,
        )

        # Group widgets
        self.box_1 = ipywidgets.HBox(
            [self.numbers_size_title, self.numbers_size_text, self.numbers_size_none]
        )
        self.box_1.layout.align_items = "center"
        self.box_1.layout.margin = "0px 10px 0px 0px"
        self.box_2 = ipywidgets.HBox([self.box_1, self.numbers_colour_widget])
        self.box_2.layout.align_items = "flex-start"
        self.container = ipywidgets.VBox([self.render_numbering_switch, self.box_2])

        # Create final widget
        super(NumberingMayaviOptionsWidget, self).__init__(
            [self.container], Dict, numbers_options, render_function=render_function
        )

        # Set functionality
        def numbering_options_visible(change):
            self.box_2.layout.display = "flex" if change["new"] else "none"

        numbering_options_visible({"new": numbers_options["render_numbering"]})
        self.render_numbering_switch.observe(
            numbering_options_visible, names="selected_values", type="change"
        )

        def save_options(change):
            numbers_size = None
            if not self.numbers_size_text.disabled:
                numbers_size = float(self.numbers_size_text.value)
            self.selected_values = {
                "render_numbering": self.render_numbering_switch.selected_values,
                "numbers_size": numbers_size,
                "numbers_colour": self.numbers_colour_widget.selected_values[0],
            }

        self.render_numbering_switch.observe(
            save_options, names="selected_values", type="change"
        )
        self.numbers_size_text.observe(save_options, names="value", type="change")
        self.numbers_colour_widget.observe(
            save_options, names="selected_values", type="change"
        )

        def button_icon(_):
            if self.numbers_size_text.disabled:
                self.numbers_size_none.icon = "fa-keyboard-o"
                self.numbers_size_text.disabled = False
            else:
                self.numbers_size_none.icon = "fa-times"
                self.numbers_size_text.disabled = True
            save_options({})

        self.numbers_size_none.on_click(button_icon)

    def set_widget_state(self, numbers_options, allow_callback=True):
        r"""
        Method that updates the state of the widget if the provided
        `line_options` are different than `self.selected_values`.

        Parameters
        ----------
        numbers_options : `dict`
            The selected numbering options. It must be a `dict` with the
            following keys:

            * ``render_numbering`` : (`bool`) Flag for rendering the numbers.
            * ``numbers_size`` : (`float`) The font size (e.g. ``10.``).
            * ``numbers_colour`` : (`str`) The font colour (e.g. ``'black'``)

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != numbers_options:
            # keep old value
            old_value = self.selected_values

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.render_numbering_switch.set_widget_state(
                numbers_options["render_numbering"], allow_callback=False
            )
            if numbers_options["numbers_size"] is None:
                self.numbers_size_text.disabled = True
                self.numbers_size_none.icon = "fa-times"
            else:
                self.numbers_size_text.disabled = False
                self.numbers_size_none.icon = "fa-keyboard-o"
                self.numbers_size_text.value = float(numbers_options["numbers_size"])
            self.numbers_colour_widget.set_widget_state(
                numbers_options["numbers_colour"], allow_callback=False
            )

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)


class AxesLimitsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting the axes limits.

    Parameters
    ----------
    axes_x_limits : `float` or [`float`, `float`] or ``None``
        The limits of the x axis.
    axes_y_limits : `float` or [`float`, `float`] or ``None``
        The limits of the y axis.
    render_function : `callable` or ``None``, optional
        The render function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    """

    def __init__(self, axes_x_limits, axes_y_limits, render_function=None):
        # Create children
        # x limits
        if axes_x_limits is None:
            toggles_initial_value = "auto"
            percentage_initial_value = [0.0]
            percentage_visible = False
            range_initial_value = [0.0, 100.0]
            range_visible = False
        elif isinstance(axes_x_limits, float):
            toggles_initial_value = "percentage"
            percentage_initial_value = [axes_x_limits]
            percentage_visible = True
            range_initial_value = [0.0, 100.0]
            range_visible = False
        else:
            toggles_initial_value = "range"
            percentage_initial_value = [0.0]
            percentage_visible = False
            range_initial_value = axes_x_limits
            range_visible = True
        self.axes_x_limits_title = ipywidgets.HTML(value="X limits")
        self.axes_x_limits_toggles = ipywidgets.ToggleButtons(
            value=toggles_initial_value, options=["auto", "percentage", "range"]
        )
        self.axes_x_limits_percentage = ListWidget(
            percentage_initial_value,
            mode="float",
            description="",
            render_function=None,
            example_visible=False,
            width=120,
        )
        self.axes_x_limits_percentage.layout.display = (
            "flex" if percentage_visible else "none"
        )
        self.axes_x_limits_range = ListWidget(
            range_initial_value,
            mode="float",
            description="",
            render_function=None,
            example_visible=False,
            width=120,
        )
        self.axes_x_limits_range.layout.display = "flex" if range_visible else "none"

        # y limits
        if axes_y_limits is None:
            toggles_initial_value = "auto"
            percentage_initial_value = [0.0]
            percentage_visible = False
            range_initial_value = [0.0, 100.0]
            range_visible = False
        elif isinstance(axes_y_limits, float):
            toggles_initial_value = "percentage"
            percentage_initial_value = [axes_y_limits]
            percentage_visible = True
            range_initial_value = [0.0, 100.0]
            range_visible = False
        else:
            toggles_initial_value = "range"
            percentage_initial_value = [0.0]
            percentage_visible = False
            range_initial_value = axes_y_limits
            range_visible = True
        self.axes_y_limits_title = ipywidgets.HTML(value="Y limits")
        self.axes_y_limits_toggles = ipywidgets.ToggleButtons(
            value=toggles_initial_value, options=["auto", "percentage", "range"]
        )
        self.axes_y_limits_percentage = ListWidget(
            percentage_initial_value,
            mode="float",
            description="",
            render_function=None,
            example_visible=False,
            width=120,
        )
        self.axes_y_limits_percentage.layout.display = (
            "flex" if percentage_visible else "none"
        )
        self.axes_y_limits_range = ListWidget(
            range_initial_value,
            mode="float",
            description="",
            render_function=None,
            example_visible=False,
            width=120,
        )
        self.axes_y_limits_range.layout.display = "flex" if range_visible else "none"

        # Group widgets
        self.box_1 = ipywidgets.HBox(
            [self.axes_x_limits_title, self.axes_x_limits_toggles]
        )
        self.box_1.layout.align_items = "center"
        self.box_2 = ipywidgets.HBox(
            [self.axes_x_limits_percentage, self.axes_x_limits_range]
        )
        self.box_3 = ipywidgets.HBox([self.box_1, self.box_2])
        self.box_4 = ipywidgets.HBox(
            [self.axes_y_limits_title, self.axes_y_limits_toggles]
        )
        self.box_4.layout.align_items = "center"
        self.box_5 = ipywidgets.HBox(
            [self.axes_y_limits_percentage, self.axes_y_limits_range]
        )
        self.box_6 = ipywidgets.HBox([self.box_4, self.box_5])
        self.container = ipywidgets.VBox([self.box_3, self.box_6])

        # Create final widget
        super(AxesLimitsWidget, self).__init__(
            [self.container],
            Dict,
            {"x": axes_x_limits, "y": axes_y_limits},
            render_function=render_function,
        )

        # Set functionality
        def x_visibility(change):
            if change["new"] == "auto":
                self.axes_x_limits_percentage.layout.display = "none"
                self.axes_x_limits_range.layout.display = "none"
            elif change["new"] == "percentage":
                self.axes_x_limits_percentage.layout.display = "flex"
                self.axes_x_limits_range.layout.display = "none"
            else:
                self.axes_x_limits_percentage.layout.display = "none"
                self.axes_x_limits_range.layout.display = "flex"

        self.axes_x_limits_toggles.observe(x_visibility, names="value", type="change")

        def y_visibility(change):
            if change["new"] == "auto":
                self.axes_y_limits_percentage.layout.display = "none"
                self.axes_y_limits_range.layout.display = "none"
            elif change["new"] == "percentage":
                self.axes_y_limits_percentage.layout.display = "flex"
                self.axes_y_limits_range.layout.display = "none"
            else:
                self.axes_y_limits_percentage.layout.display = "none"
                self.axes_y_limits_range.layout.display = "flex"

        self.axes_y_limits_toggles.observe(y_visibility, names="value", type="change")

        def save_options(change):
            if self.axes_x_limits_toggles.value == "auto":
                x_val = None
            elif self.axes_x_limits_toggles.value == "percentage":
                x_val = self.axes_x_limits_percentage.selected_values[0]
            else:
                x_val = [
                    self.axes_x_limits_range.selected_values[0],
                    self.axes_x_limits_range.selected_values[1],
                ]
            if self.axes_y_limits_toggles.value == "auto":
                y_val = None
            elif self.axes_y_limits_toggles.value == "percentage":
                y_val = self.axes_y_limits_percentage.selected_values[0]
            else:
                y_val = [
                    self.axes_y_limits_range.selected_values[0],
                    self.axes_y_limits_range.selected_values[1],
                ]
            self.selected_values = {"x": x_val, "y": y_val}

        self.axes_x_limits_toggles.observe(save_options, names="value", type="change")
        self.axes_x_limits_percentage.observe(
            save_options, names="selected_values", type="change"
        )
        self.axes_x_limits_range.observe(
            save_options, names="selected_values", type="change"
        )
        self.axes_y_limits_toggles.observe(save_options, names="value", type="change")
        self.axes_y_limits_percentage.observe(
            save_options, names="selected_values", type="change"
        )
        self.axes_y_limits_range.observe(
            save_options, names="selected_values", type="change"
        )

    def set_widget_state(self, axes_x_limits, axes_y_limits, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided
        `axes_y_limits` and `axes_x_limits` values are different than
        `self.selected_values`.

        Parameters
        ----------
        axes_x_limits : `float` or [`float`, `float`] or ``None``
            The limits of the x axis.
        axes_y_limits : `float` or [`float`, `float`] or ``None``
            The limits of the y axis.
        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Check if update is required
        if self.selected_values != {"x": axes_x_limits, "y": axes_y_limits}:
            # keep old values
            old_value = self.selected_values

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            if axes_x_limits is None:
                self.axes_x_limits_toggles.value = "auto"
            elif isinstance(axes_x_limits, float):
                self.axes_x_limits_toggles.value = "percentage"
                self.axes_x_limits_percentage.set_widget_state(
                    [axes_x_limits], allow_callback=False
                )
            else:
                self.axes_x_limits_toggles.value = "range"
                self.axes_x_limits_range.set_widget_state(
                    axes_x_limits, allow_callback=False
                )
            if axes_y_limits is None:
                self.axes_y_limits_toggles.value = "auto"
            elif isinstance(axes_y_limits, float):
                self.axes_y_limits_toggles.value = "percentage"
                self.axes_y_limits_percentage.set_widget_state(
                    [axes_y_limits], allow_callback=False
                )
            else:
                self.axes_y_limits_toggles.value = "range"
                self.axes_y_limits_range.set_widget_state(
                    axes_y_limits, allow_callback=False
                )

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)


class AxesTicksWidget(MenpoWidget):
    r"""
    Creates a widget for selecting the axes ticks.

    Parameters
    ----------
    axes_ticks : `dict`
        The initial options. It must be a `dict` with the following keys:

            * ``x`` : (`list` or ``None``) The x ticks (e.g. ``[10, 20]``).
            * ``y`` : (`list` or ``None``) The y ticks (e.g. ``None``).

    render_function : `callable` or ``None``, optional
        The render function that is executed when the index value changes.
        If ``None``, then nothing is assigned.
    """

    def __init__(self, axes_ticks, render_function=None):
        # Create children
        # x ticks
        if axes_ticks["x"] is None:
            toggles_initial_value = "auto"
            list_visible = False
            list_value = []
        else:
            toggles_initial_value = "list"
            list_visible = True
            list_value = axes_ticks["x"]
        self.axes_x_ticks_title = ipywidgets.HTML(value="X ticks")
        self.axes_x_ticks_toggles = ipywidgets.ToggleButtons(
            value=toggles_initial_value, options=["auto", "list"]
        )
        self.axes_x_ticks_list = ListWidget(
            list_value,
            mode="float",
            description="",
            render_function=None,
            example_visible=False,
            width=200,
        )
        self.axes_x_ticks_list.layout.display = "flex" if list_visible else "none"

        # y ticks
        if axes_ticks["y"] is None:
            toggles_initial_value = "auto"
            list_visible = False
            list_value = []
        else:
            toggles_initial_value = "list"
            list_visible = True
            list_value = axes_ticks["y"]
        self.axes_y_ticks_title = ipywidgets.HTML(value="Y ticks")
        self.axes_y_ticks_toggles = ipywidgets.ToggleButtons(
            value=toggles_initial_value, options=["auto", "list"]
        )
        self.axes_y_ticks_list = ListWidget(
            list_value,
            mode="float",
            description="",
            render_function=None,
            example_visible=False,
            width=200,
        )
        self.axes_y_ticks_list.layout.display = "flex" if list_visible else "none"

        # Group widgets
        self.box_1 = ipywidgets.HBox(
            [self.axes_x_ticks_title, self.axes_x_ticks_toggles]
        )
        self.box_1.layout.align_items = "center"
        self.box_2 = ipywidgets.HBox([self.box_1, self.axes_x_ticks_list])
        self.box_3 = ipywidgets.HBox(
            [self.axes_y_ticks_title, self.axes_y_ticks_toggles]
        )
        self.box_3.layout.align_items = "center"
        self.box_4 = ipywidgets.HBox([self.box_3, self.axes_y_ticks_list])
        self.container = ipywidgets.VBox([self.box_2, self.box_4])

        # Create final widget
        super(AxesTicksWidget, self).__init__(
            [self.container], Dict, axes_ticks, render_function=render_function
        )

        # Set functionality
        def x_visibility(change):
            self.axes_x_ticks_list.layout.display = (
                "flex" if change["new"] == "list" else "none"
            )

        self.axes_x_ticks_toggles.observe(x_visibility, names="value", type="change")

        def y_visibility(change):
            self.axes_y_ticks_list.layout.display = (
                "flex" if change["new"] == "list" else "none"
            )

        self.axes_y_ticks_toggles.observe(y_visibility, names="value", type="change")

        def save_options(change):
            if self.axes_x_ticks_toggles.value == "auto":
                x_val = None
            else:
                x_val = self.axes_x_ticks_list.selected_values
            if self.axes_y_ticks_toggles.value == "auto":
                y_val = None
            else:
                y_val = self.axes_y_ticks_list.selected_values
            self.selected_values = {"x": x_val, "y": y_val}

        self.axes_x_ticks_toggles.observe(save_options, names="value", type="change")
        self.axes_x_ticks_list.observe(
            save_options, names="selected_values", type="change"
        )
        self.axes_y_ticks_toggles.observe(save_options, names="value", type="change")
        self.axes_y_ticks_list.observe(
            save_options, names="selected_values", type="change"
        )

    def set_widget_state(self, axes_ticks, allow_callback=True):
        r"""
        Method that updates the state of the widget, if the provided `axes_ticks`
        values are different than `self.selected_values`.

        Parameters
        ----------
        axes_ticks : `dict`
            The selected options. It must be a `dict` with the following keys:

                * ``x`` : (`list` or ``None``) The x ticks (e.g. ``[10, 20]``).
                * ``y`` : (`list` or ``None``) The y ticks (e.g. ``None``).

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        # Check if update is required
        if axes_ticks != self.selected_values:
            # keep old value
            old_value = self.selected_values

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            if axes_ticks["x"] is None:
                self.axes_x_ticks_toggles.value = "auto"
            else:
                self.axes_x_ticks_toggles.value = "list"
                self.axes_x_ticks_list.set_widget_state(
                    axes_ticks["x"], allow_callback=False
                )
            if axes_ticks["y"] is None:
                self.axes_y_ticks_toggles.value = "auto"
            else:
                self.axes_y_ticks_toggles.value = "list"
                self.axes_y_ticks_list.set_widget_state(
                    axes_ticks["y"], allow_callback=False
                )

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)


class AxesOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting axes rendering options.

    Parameters
    ----------
    axes_options : `dict`
        The initial axes options. It must be a `dict` with the following keys:

        * ``render_axes`` : (`bool`) Flag for rendering the axes.
        * ``axes_font_name`` : (`str`) The axes font name (e.g. ``'serif'``).
        * ``axes_font_size`` : (`int`) The axes font size (e.g. ``10``).
        * ``axes_font_style`` : (`str`) The axes font style (e.g. ``'normal'``)
        * ``axes_font_weight`` : (`str`) The font weight (e.g. ``'normal'``).
        * ``axes_x_ticks`` : (`list` or ``None``) The x ticks (e.g. ``[10, 20]``)
        * ``axes_y_ticks`` : (`list` or ``None``) The y ticks (e.g. ``None``).
        * ``axes_x_limits`` : (`float` or [`float`, `float`] or ``None``)
          The x limits (e.g. ``None``).
        * ``axes_y_limits`` : (`float` or [`float`, `float`] or ``None``)
          The y limits (e.g. ``1.``).

    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the show line checkbox.
    render_checkbox_type : {``checkbox``, ``toggle``}, optional
        The type of the rendering switch. If ``checkbox``, then
        `ipywidgets.Checkbox` is used. if ``toggle``, then an
        `ipywidgets.ToggleButton` with customized appearance is used.
    """

    def __init__(
        self,
        axes_options,
        render_function=None,
        render_checkbox_type="toggle",
        render_checkbox_title="Render axes",
    ):
        # Create children
        # render checkbox
        self.render_axes_switch = SwitchWidget(
            axes_options["render_axes"],
            description=render_checkbox_title,
            switch_type=render_checkbox_type,
        )
        self.render_axes_switch.layout.margin = "7px"
        # axes font options
        self.axes_font_name_title = ipywidgets.HTML(value="Font Family")
        axes_font_name_dict = OrderedDict()
        axes_font_name_dict["serif"] = "serif"
        axes_font_name_dict["sans-serif"] = "sans-serif"
        axes_font_name_dict["cursive"] = "cursive"
        axes_font_name_dict["fantasy"] = "fantasy"
        axes_font_name_dict["monospace"] = "monospace"
        self.axes_font_name_dropdown = ipywidgets.Dropdown(
            options=axes_font_name_dict,
            value=axes_options["axes_font_name"],
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.axes_font_size_title = ipywidgets.HTML(value="Font Size")
        self.axes_font_size_text = ipywidgets.BoundedIntText(
            value=axes_options["axes_font_size"],
            min=0,
            max=10 ** 6,
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.axes_font_style_title = ipywidgets.HTML(value="Font Style")
        axes_font_style_dict = OrderedDict()
        axes_font_style_dict["normal"] = "normal"
        axes_font_style_dict["italic"] = "italic"
        axes_font_style_dict["oblique"] = "oblique"
        self.axes_font_style_dropdown = ipywidgets.Dropdown(
            options=axes_font_style_dict,
            value=axes_options["axes_font_style"],
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.axes_font_weight_title = ipywidgets.HTML(value="Font Weight")
        axes_font_weight_dict = OrderedDict()
        axes_font_weight_dict["normal"] = "normal"
        axes_font_weight_dict["ultralight"] = "ultralight"
        axes_font_weight_dict["light"] = "light"
        axes_font_weight_dict["regular"] = "regular"
        axes_font_weight_dict["book"] = "book"
        axes_font_weight_dict["medium"] = "medium"
        axes_font_weight_dict["roman"] = "roman"
        axes_font_weight_dict["semibold"] = "semibold"
        axes_font_weight_dict["demibold"] = "demibold"
        axes_font_weight_dict["demi"] = "demi"
        axes_font_weight_dict["bold"] = "bold"
        axes_font_weight_dict["heavy"] = "heavy"
        axes_font_weight_dict["extra bold"] = "extra bold"
        axes_font_weight_dict["black"] = "black"
        self.axes_font_weight_dropdown = ipywidgets.Dropdown(
            options=axes_font_weight_dict,
            layout=ipywidgets.Layout(width="3cm"),
            value=axes_options["axes_font_weight"],
        )

        self.box_1 = ipywidgets.HBox(
            [self.axes_font_name_title, self.axes_font_name_dropdown]
        )
        self.box_1.layout.align_items = "center"
        self.box_2 = ipywidgets.HBox(
            [self.axes_font_size_title, self.axes_font_size_text]
        )
        self.box_2.layout.align_items = "center"
        self.box_3 = ipywidgets.HBox(
            [self.axes_font_style_title, self.axes_font_style_dropdown]
        )
        self.box_3.layout.align_items = "center"
        self.box_4 = ipywidgets.HBox(
            [self.axes_font_weight_title, self.axes_font_weight_dropdown]
        )
        self.box_4.layout.align_items = "center"
        self.box_5 = ipywidgets.VBox([self.box_1, self.box_2])
        self.box_5.layout.align_items = "flex-end"
        self.box_5.layout.margin = "0px 10px 0px 0px"
        self.box_6 = ipywidgets.VBox([self.box_3, self.box_4])
        self.box_6.layout.align_items = "flex-end"
        self.box_7 = ipywidgets.HBox([self.box_5, self.box_6])

        # axes ticks options
        axes_ticks = {
            "x": axes_options["axes_x_ticks"],
            "y": axes_options["axes_y_ticks"],
        }
        self.axes_ticks_widget = AxesTicksWidget(axes_ticks, render_function=None)

        # axes limits options
        self.axes_limits_widget = AxesLimitsWidget(
            axes_options["axes_x_limits"],
            axes_options["axes_y_limits"],
            render_function=None,
        )

        # options tab
        self.accordion = ipywidgets.Accordion(
            [self.box_7, self.axes_limits_widget, self.axes_ticks_widget]
        )
        self.accordion.set_title(0, "Font")
        self.accordion.set_title(1, "Limits")
        self.accordion.set_title(2, "Ticks")
        self.container = ipywidgets.VBox([self.render_axes_switch, self.accordion])

        # Create final widget
        super(AxesOptionsWidget, self).__init__(
            [self.container], Dict, axes_options, render_function=render_function
        )

        # Set functionality
        def axes_options_visible(change):
            self.accordion.layout.display = "flex" if change["new"] else "none"

        axes_options_visible({"new": axes_options["render_axes"]})
        self.render_axes_switch.observe(
            axes_options_visible, names="selected_values", type="change"
        )

        def save_options(change):
            self.selected_values = {
                "render_axes": self.render_axes_switch.selected_values,
                "axes_font_name": self.axes_font_name_dropdown.value,
                "axes_font_size": int(self.axes_font_size_text.value),
                "axes_font_style": self.axes_font_style_dropdown.value,
                "axes_font_weight": self.axes_font_weight_dropdown.value,
                "axes_x_ticks": self.axes_ticks_widget.selected_values["x"],
                "axes_y_ticks": self.axes_ticks_widget.selected_values["y"],
                "axes_x_limits": self.axes_limits_widget.selected_values["x"],
                "axes_y_limits": self.axes_limits_widget.selected_values["y"],
            }

        self.render_axes_switch.observe(
            save_options, names="selected_values", type="change"
        )
        self.axes_font_name_dropdown.observe(save_options, names="value", type="change")
        self.axes_font_size_text.observe(save_options, names="value", type="change")
        self.axes_font_style_dropdown.observe(
            save_options, names="value", type="change"
        )
        self.axes_font_weight_dropdown.observe(
            save_options, names="value", type="change"
        )
        self.axes_ticks_widget.observe(
            save_options, names="selected_values", type="change"
        )
        self.axes_limits_widget.observe(
            save_options, names="selected_values", type="change"
        )

    def set_widget_state(self, axes_options, allow_callback=True):
        r"""
        Method that updates the state of the widget if the provided
        `axes_options` are different than `self.selected_values`.

        Parameters
        ----------
        axes_options : `dict`
            The selected axes options. It must be a `dict` with the following
            keys:

            * ``render_axes`` : (`bool`) Flag for rendering the axes.
            * ``axes_font_name`` : (`str`) The axes font name (e.g. ``'serif'``).
            * ``axes_font_size`` : (`int`) The axes font size (e.g. ``10``).
            * ``axes_font_style`` : (`str`) The axes font style
              (e.g. ``'normal'``)
            * ``axes_font_weight`` : (`str`) The font weight (e.g. ``'normal'``).
            * ``axes_x_ticks`` : (`list` or ``None``) The x ticks
              (e.g. ``[10, 20]``).
            * ``axes_y_ticks`` : (`list` or ``None``) The y ticks (e.g. ``None``)
            * ``axes_x_limits`` : (`float` or [`float`, `float`] or ``None``)
              The x limits (e.g. ``None``).
            * ``axes_y_limits`` : (`float` or [`float`, `float`] or ``None``)
              The y limits (e.g. ``1.``).

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != axes_options:
            # keep old value
            old_value = self.selected_values

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.render_axes_switch.set_widget_state(
                axes_options["render_axes"], allow_callback=False
            )
            self.axes_font_name_dropdown.value = axes_options["axes_font_name"]
            self.axes_font_size_text.value = axes_options["axes_font_size"]
            self.axes_font_style_dropdown.value = axes_options["axes_font_style"]
            self.axes_font_weight_dropdown.value = axes_options["axes_font_weight"]
            axes_ticks = {
                "x": axes_options["axes_x_ticks"],
                "y": axes_options["axes_y_ticks"],
            }
            self.axes_ticks_widget.set_widget_state(axes_ticks, allow_callback=False)
            self.axes_limits_widget.set_widget_state(
                axes_options["axes_x_limits"],
                axes_options["axes_y_limits"],
                allow_callback=False,
            )

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)


class LegendOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting legend rendering options.

    Parameters
    ----------
    legend_options : `dict`
        The initial legend options. It must be a `dict` with the following keys:

        * ``render_legend`` : (`bool`) Flag for rendering the legend.
        * ``legend_title`` : (`str`) The legend title (e.g. ``''``).
        * ``legend_font_name`` : (`str`) The font name (e.g. ``'serif'``).
        * ``legend_font_style`` : (`str`) The font style (e.g. ``'normal'``).
        * ``legend_font_size`` : (`str`) The font size (e.g. ``10``).
        * ``legend_font_weight`` : (`str`) The font weight (e.g. ``'normal'``).
        * ``legend_marker_scale`` : (`float`) The marker scale (e.g. ``1.``).
        * ``legend_location`` : (`int`) The legend location (e.g. ``2``).
        * ``legend_bbox_to_anchor`` : (`tuple`) Bbox to anchor
          (e.g. ``(1.05, 1.)``).
        * ``legend_border_axes_pad`` : (`float`) Border axes pad (e.g. ``1.``).
        * ``legend_n_columns`` : (`int`) The number of columns (e.g. ``1``).
        * ``legend_horizontal_spacing`` : (`float`) Horizontal spacing
          (e.g. ``1.``).
        * ``legend_vertical_spacing`` : (`float`) Vetical spacing (e.g. ``1.``).
        * ``legend_border`` : (`bool`) Flag for adding border to the legend.
        * ``legend_border_padding`` : (`float`) The border padding (e.g. ``0.5``)
        * ``legend_shadow`` : (`bool`) Flag for adding shadow to the legend.
        * ``legend_rounded_corners`` : (`bool`) Flag for adding rounded
          corners to the legend.

    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the render legend checkbox.
    render_checkbox_type : {``checkbox``, ``toggle``}, optional
        The type of the rendering switch. If ``checkbox``, then
        `ipywidgets.Checkbox` is used. if ``toggle``, then an
        `ipywidgets.ToggleButton` with customized appearance is used.
    """

    def __init__(
        self,
        legend_options,
        render_function=None,
        render_checkbox_type="toggle",
        render_checkbox_title="Render legend",
    ):
        # Create children
        # render checkbox
        self.render_legend_switch = SwitchWidget(
            legend_options["render_legend"],
            description=render_checkbox_title,
            switch_type=render_checkbox_type,
        )
        self.render_legend_switch.layout.margin = "7px"

        # font-related options and title
        self.legend_font_name_title = ipywidgets.HTML(value="Font")
        legend_font_name_dict = OrderedDict()
        legend_font_name_dict["serif"] = "serif"
        legend_font_name_dict["sans-serif"] = "sans-serif"
        legend_font_name_dict["cursive"] = "cursive"
        legend_font_name_dict["fantasy"] = "fantasy"
        legend_font_name_dict["monospace"] = "monospace"
        self.legend_font_name_dropdown = ipywidgets.Dropdown(
            options=legend_font_name_dict,
            layout=ipywidgets.Layout(width="3cm"),
            value=legend_options["legend_font_name"],
        )
        self.legend_font_size_title = ipywidgets.HTML(value="Size")
        self.legend_font_size_text = ipywidgets.BoundedIntText(
            min=0,
            max=10 ** 6,
            value=legend_options["legend_font_size"],
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.legend_font_style_title = ipywidgets.HTML(value="Style")
        legend_font_style_dict = OrderedDict()
        legend_font_style_dict["normal"] = "normal"
        legend_font_style_dict["italic"] = "italic"
        legend_font_style_dict["oblique"] = "oblique"
        self.legend_font_style_dropdown = ipywidgets.Dropdown(
            options=legend_font_style_dict,
            layout=ipywidgets.Layout(width="3cm"),
            value=legend_options["legend_font_style"],
        )
        self.legend_font_weight_title = ipywidgets.HTML(value="Weight")
        legend_font_weight_dict = OrderedDict()
        legend_font_weight_dict["normal"] = "normal"
        legend_font_weight_dict["ultralight"] = "ultralight"
        legend_font_weight_dict["light"] = "light"
        legend_font_weight_dict["regular"] = "regular"
        legend_font_weight_dict["book"] = "book"
        legend_font_weight_dict["medium"] = "medium"
        legend_font_weight_dict["roman"] = "roman"
        legend_font_weight_dict["semibold"] = "semibold"
        legend_font_weight_dict["demibold"] = "demibold"
        legend_font_weight_dict["demi"] = "demi"
        legend_font_weight_dict["bold"] = "bold"
        legend_font_weight_dict["heavy"] = "heavy"
        legend_font_weight_dict["extra bold"] = "extra bold"
        legend_font_weight_dict["black"] = "black"
        self.legend_font_weight_dropdown = ipywidgets.Dropdown(
            options=legend_font_weight_dict,
            layout=ipywidgets.Layout(width="3cm"),
            value=legend_options["legend_font_weight"],
        )
        self.legend_title_title = ipywidgets.HTML(value="Title")
        self.legend_title_text = ipywidgets.Text(
            value=legend_options["legend_title"],
            layout=ipywidgets.Layout(width="7.6cm"),
        )

        self.box_1 = ipywidgets.HBox(
            [self.legend_font_name_title, self.legend_font_name_dropdown]
        )
        self.box_1.layout.align_items = "center"
        self.box_2 = ipywidgets.HBox(
            [self.legend_font_size_title, self.legend_font_size_text]
        )
        self.box_2.layout.align_items = "center"
        self.box_3 = ipywidgets.HBox(
            [self.legend_font_style_title, self.legend_font_style_dropdown]
        )
        self.box_3.layout.align_items = "center"
        self.box_4 = ipywidgets.HBox(
            [self.legend_font_weight_title, self.legend_font_weight_dropdown]
        )
        self.box_4.layout.align_items = "center"
        self.box_5 = ipywidgets.VBox([self.box_1, self.box_2])
        self.box_5.layout.align_items = "flex-end"
        self.box_5.layout.margin = "0px 10px 0px 0px"
        self.box_6 = ipywidgets.VBox([self.box_3, self.box_4])
        self.box_6.layout.align_items = "flex-end"
        self.box_7 = ipywidgets.HBox([self.box_5, self.box_6])
        self.box_8 = ipywidgets.HBox([self.legend_title_title, self.legend_title_text])
        self.box_8.layout.align_items = "center"
        self.box_9 = ipywidgets.VBox([self.box_8, self.box_7])
        self.box_9.layout.align_items = "flex-end"

        # location-related options
        self.legend_location_title = ipywidgets.HTML(value="Anchor")
        legend_location_dict = OrderedDict()
        legend_location_dict["best"] = 0
        legend_location_dict["upper right"] = 1
        legend_location_dict["upper left"] = 2
        legend_location_dict["lower left"] = 3
        legend_location_dict["lower right"] = 4
        legend_location_dict["right"] = 5
        legend_location_dict["center left"] = 6
        legend_location_dict["center right"] = 7
        legend_location_dict["lower center"] = 8
        legend_location_dict["upper center"] = 9
        legend_location_dict["center"] = 10
        self.legend_location_dropdown = ipywidgets.Dropdown(
            options=legend_location_dict,
            layout=ipywidgets.Layout(width="3cm"),
            value=legend_options["legend_location"],
        )
        if legend_options["legend_bbox_to_anchor"] is None:
            tmp1 = False
            tmp2 = 0.0
            tmp3 = 0.0
        else:
            tmp1 = True
            tmp2 = legend_options["legend_bbox_to_anchor"][0]
            tmp3 = legend_options["legend_bbox_to_anchor"][1]
        self.bbox_to_anchor_enable_checkbox = SwitchWidget(
            tmp1,
            description="Offset",
        )
        self.bbox_to_anchor_x_text = ipywidgets.FloatText(
            value=tmp2, layout=ipywidgets.Layout(width="1.6cm")
        )
        self.bbox_to_anchor_y_text = ipywidgets.FloatText(
            value=tmp3, layout=ipywidgets.Layout(width="1.6cm")
        )
        self.legend_border_axes_pad_title = ipywidgets.HTML(value="Padding")
        self.legend_border_axes_pad_text = ipywidgets.BoundedFloatText(
            value=legend_options["legend_border_axes_pad"],
            min=0.0,
            layout=ipywidgets.Layout(width="3cm"),
        )

        self.box_10 = ipywidgets.HBox(
            [self.legend_location_title, self.legend_location_dropdown]
        )
        self.box_10.layout.align_items = "center"
        self.box_11 = ipywidgets.HBox(
            [self.legend_border_axes_pad_title, self.legend_border_axes_pad_text]
        )
        self.box_11.layout.align_items = "center"
        self.box_12 = ipywidgets.VBox([self.box_10, self.box_11])
        self.box_12.layout.align_items = "flex-end"
        self.box_12.layout.margin = "0px 10px 0px 0px"

        self.box_13 = ipywidgets.VBox(
            [self.bbox_to_anchor_x_text, self.bbox_to_anchor_y_text]
        )
        self.box_13.layout.align_items = "flex-end"
        self.box_14 = ipywidgets.HBox(
            [self.bbox_to_anchor_enable_checkbox, self.box_13]
        )
        self.box_14.layout.align_items = "center"
        self.box_15 = ipywidgets.HBox([self.box_12, self.box_14])

        # formatting related
        self.legend_n_columns_title = ipywidgets.HTML(value="# Columns")
        self.legend_n_columns_text = ipywidgets.BoundedIntText(
            value=legend_options["legend_n_columns"],
            min=0,
            layout=ipywidgets.Layout(width="1.6cm"),
        )
        self.legend_marker_scale_title = ipywidgets.HTML(value="Marker scale")
        self.legend_marker_scale_text = ipywidgets.BoundedFloatText(
            value=legend_options["legend_marker_scale"],
            min=0.0,
            layout=ipywidgets.Layout(width="1.6cm"),
        )
        self.legend_horizontal_spacing_title = ipywidgets.HTML(value="Horizontal space")
        self.legend_horizontal_spacing_text = ipywidgets.BoundedFloatText(
            value=legend_options["legend_horizontal_spacing"],
            min=0.0,
            layout=ipywidgets.Layout(width="1.6cm"),
        )
        self.legend_vertical_spacing_title = ipywidgets.HTML(value="Vertical space")
        self.legend_vertical_spacing_text = ipywidgets.BoundedFloatText(
            value=legend_options["legend_vertical_spacing"],
            min=0.0,
            layout=ipywidgets.Layout(width="1.6cm"),
        )

        self.box_16 = ipywidgets.HBox(
            [self.legend_n_columns_title, self.legend_n_columns_text]
        )
        self.box_16.layout.align_items = "center"
        self.box_17 = ipywidgets.HBox(
            [self.legend_marker_scale_title, self.legend_marker_scale_text]
        )
        self.box_17.layout.align_items = "center"
        self.box_18 = ipywidgets.HBox(
            [self.legend_horizontal_spacing_title, self.legend_horizontal_spacing_text]
        )
        self.box_18.layout.align_items = "center"
        self.box_19 = ipywidgets.HBox(
            [self.legend_vertical_spacing_title, self.legend_vertical_spacing_text]
        )
        self.box_19.layout.align_items = "center"
        self.box_20 = ipywidgets.VBox([self.box_16, self.box_17])
        self.box_20.layout.align_items = "flex-end"
        self.box_20.layout.margin = "0px 10px 0px 0px"
        self.box_21 = ipywidgets.VBox([self.box_18, self.box_19])
        self.box_21.layout.align_items = "flex-end"
        self.box_22 = ipywidgets.HBox([self.box_20, self.box_21])

        # border
        self.legend_border_checkbox = ipywidgets.Checkbox(
            description="Border", value=legend_options["legend_border"]
        )
        self.legend_border_padding_title = ipywidgets.HTML(value="Padding")
        self.legend_border_padding_text = ipywidgets.BoundedFloatText(
            value=legend_options["legend_border_padding"],
            min=0.0,
            layout=ipywidgets.Layout(width="1.2cm"),
        )
        self.legend_shadow_checkbox = ipywidgets.Checkbox(
            description="Shadow", value=legend_options["legend_shadow"]
        )
        self.legend_rounded_corners_checkbox = ipywidgets.Checkbox(
            description="Fancy", value=legend_options["legend_rounded_corners"]
        )

        self.box_23 = ipywidgets.HBox(
            [self.legend_border_padding_title, self.legend_border_padding_text]
        )
        self.box_23.layout.align_items = "center"
        self.box_24 = ipywidgets.HBox([self.legend_border_checkbox, self.box_23])
        self.box_24.layout.align_items = "center"
        self.box_25 = ipywidgets.VBox(
            [
                self.box_24,
                self.legend_shadow_checkbox,
                self.legend_rounded_corners_checkbox,
            ]
        )

        # Group widgets
        self.box_27 = ipywidgets.Accordion(
            [self.box_15, self.box_9, self.box_22, self.box_25]
        )
        self.box_27.set_title(0, "Location")
        self.box_27.set_title(1, "Title & Font")
        self.box_27.set_title(2, "Formatting")
        self.box_27.set_title(3, "Border")
        self.container = ipywidgets.VBox([self.render_legend_switch, self.box_27])

        # Create final widget
        super(LegendOptionsWidget, self).__init__(
            [self.container], Dict, legend_options, render_function=render_function
        )

        # Set functionality
        def legend_options_visible(change):
            self.box_27.layout.display = "" if change["new"] else "none"

        legend_options_visible({"new": legend_options["render_legend"]})
        self.render_legend_switch.observe(
            legend_options_visible, names="selected_values", type="change"
        )

        def border_pad_visible(change):
            self.box_23.layout.display = "flex" if change["new"] else "none"

        self.legend_border_checkbox.observe(
            border_pad_visible, names="value", type="change"
        )

        def bbox_to_anchor_visible(change):
            self.bbox_to_anchor_x_text.layout.visibility = (
                "visible" if change["new"] else "hidden"
            )
            self.bbox_to_anchor_y_text.layout.visibility = (
                "visible" if change["new"] else "hidden"
            )

        bbox_to_anchor_visible(
            {"new": not legend_options["legend_bbox_to_anchor"] is None}
        )
        self.bbox_to_anchor_enable_checkbox.observe(
            bbox_to_anchor_visible, names="selected_values", type="change"
        )

        def save_options(change):
            legend_bbox_to_anchor = None
            if self.bbox_to_anchor_enable_checkbox.selected_values:
                legend_bbox_to_anchor = (
                    self.bbox_to_anchor_x_text.value,
                    self.bbox_to_anchor_y_text.value,
                )
            self.selected_values = {
                "render_legend": self.render_legend_switch.selected_values,
                "legend_title": str(self.legend_title_text.value),
                "legend_font_name": self.legend_font_name_dropdown.value,
                "legend_font_style": self.legend_font_style_dropdown.value,
                "legend_font_size": int(self.legend_font_size_text.value),
                "legend_font_weight": self.legend_font_weight_dropdown.value,
                "legend_marker_scale": float(self.legend_marker_scale_text.value),
                "legend_location": self.legend_location_dropdown.value,
                "legend_bbox_to_anchor": legend_bbox_to_anchor,
                "legend_border_axes_pad": float(self.legend_border_axes_pad_text.value),
                "legend_n_columns": int(self.legend_n_columns_text.value),
                "legend_horizontal_spacing": float(
                    self.legend_horizontal_spacing_text.value
                ),
                "legend_vertical_spacing": float(
                    self.legend_vertical_spacing_text.value
                ),
                "legend_border": self.legend_border_checkbox.value,
                "legend_border_padding": float(self.legend_border_padding_text.value),
                "legend_shadow": self.legend_shadow_checkbox.value,
                "legend_rounded_corners": self.legend_rounded_corners_checkbox.value,
            }

        self.render_legend_switch.observe(
            save_options, names="selected_values", type="change"
        )
        self.legend_title_text.observe(save_options, names="value", type="change")
        self.legend_font_name_dropdown.observe(
            save_options, names="value", type="change"
        )
        self.legend_font_size_text.observe(save_options, names="value", type="change")
        self.legend_font_style_dropdown.observe(
            save_options, names="value", type="change"
        )
        self.legend_font_weight_dropdown.observe(
            save_options, names="value", type="change"
        )
        self.legend_location_dropdown.observe(
            save_options, names="value", type="change"
        )
        self.bbox_to_anchor_enable_checkbox.observe(
            save_options, names="selected_values", type="change"
        )
        self.bbox_to_anchor_x_text.observe(save_options, names="value", type="change")
        self.bbox_to_anchor_y_text.observe(save_options, names="value", type="change")
        self.legend_border_axes_pad_text.observe(
            save_options, names="value", type="change"
        )
        self.legend_n_columns_text.observe(save_options, names="value", type="change")
        self.legend_marker_scale_text.observe(
            save_options, names="value", type="change"
        )
        self.legend_horizontal_spacing_text.observe(
            save_options, names="value", type="change"
        )
        self.legend_vertical_spacing_text.observe(
            save_options, names="value", type="change"
        )
        self.legend_border_checkbox.observe(save_options, names="value", type="change")
        self.legend_border_padding_text.observe(
            save_options, names="value", type="change"
        )
        self.legend_shadow_checkbox.observe(save_options, names="value", type="change")
        self.legend_rounded_corners_checkbox.observe(
            save_options, names="value", type="change"
        )

    def set_widget_state(self, legend_options, allow_callback=True):
        r"""
        Method that updates the state of the widget if the provided
        `legend_options` are different than `self.selected_values`.

        Parameters
        ----------
        legend_options : `dict`
            The selected legend options. It must be a `dict` with the following
            keys:

            * ``render_legend`` : (`bool`) Flag for rendering the legend.
            * ``legend_title`` : (`str`) The legend title (e.g. ``''``).
            * ``legend_font_name`` : (`str`) The font name (e.g. ``'serif'``).
            * ``legend_font_style`` : (`str`) The font style (e.g. ``'normal'``).
            * ``legend_font_size`` : (`str`) The font size (e.g. ``10``).
            * ``legend_font_weight`` : (`str`) The font weight
              (e.g. ``'normal'``).
            * ``legend_marker_scale`` : (`float`) The marker scale (e.g. ``1.``).
            * ``legend_location`` : (`int`) The legend location (e.g. ``2``).
            * ``legend_bbox_to_anchor`` : (`tuple`) Bbox to anchor
              (e.g. ``(1.05, 1.)``).
            * ``legend_border_axes_pad`` : (`float`) Border axes pad
              (e.g. ``1.``).
            * ``legend_n_columns`` : (`int`) The number of columns (e.g. ``1``).
            * ``legend_horizontal_spacing`` : (`float`) Horizontal spacing
              (e.g. ``1.``).
            * ``legend_vertical_spacing`` : (`float`) Vetical spacing (e.g. ``1.``)
            * ``legend_border`` : (`bool`) Flag for adding border to the legend.
            * ``legend_border_padding`` : (`float`) The border padding
              (e.g. ``0.5``)
            * ``legend_shadow`` : (`bool`) Flag for adding shadow to the legend.
            * ``legend_rounded_corners`` : (`bool`) Flag for adding rounded
              corners to the legend.

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != legend_options:
            # keep old value
            old_value = self.selected_values

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update render legend checkbox
            self.render_legend_switch.set_widget_state(
                legend_options["render_legend"], allow_callback=False
            )

            # update legend_title
            self.legend_title_text.value = legend_options["legend_title"]

            # update legend_font_name dropdown menu
            self.legend_font_name_dropdown.value = legend_options["legend_font_name"]

            # update legend_font_size text box
            self.legend_font_size_text.value = int(legend_options["legend_font_size"])

            # update legend_font_style dropdown menu
            self.legend_font_style_dropdown.value = legend_options["legend_font_style"]

            # update legend_font_weight dropdown menu
            self.legend_font_weight_dropdown.value = legend_options[
                "legend_font_weight"
            ]

            # update legend_location dropdown menu
            self.legend_location_dropdown.value = legend_options["legend_location"]

            # update legend_bbox_to_anchor
            if legend_options["legend_bbox_to_anchor"] is None:
                tmp1 = False
                tmp2 = 0.0
                tmp3 = 0.0
            else:
                tmp1 = True
                tmp2 = legend_options["legend_bbox_to_anchor"][0]
                tmp3 = legend_options["legend_bbox_to_anchor"][1]
            self.bbox_to_anchor_enable_checkbox.set_widget_state(
                tmp1, allow_callback=False
            )
            self.bbox_to_anchor_x_text.value = tmp2
            self.bbox_to_anchor_y_text.value = tmp3

            # update legend_border_axes_pad
            self.legend_border_axes_pad_text.value = legend_options[
                "legend_border_axes_pad"
            ]

            # update legend_n_columns text box
            self.legend_n_columns_text.value = int(legend_options["legend_n_columns"])

            # update legend_marker_scale text box
            self.legend_marker_scale_text.value = float(
                legend_options["legend_marker_scale"]
            )

            # update legend_horizontal_spacing text box
            self.legend_horizontal_spacing_text.value = float(
                legend_options["legend_horizontal_spacing"]
            )

            # update legend_vertical_spacing text box
            self.legend_vertical_spacing_text.value = float(
                legend_options["legend_vertical_spacing"]
            )

            # update legend_border
            self.legend_border_checkbox.value = legend_options["legend_border"]

            # update legend_border_padding text box
            self.legend_border_padding_text.value = float(
                legend_options["legend_border_padding"]
            )

            # update legend_shadow
            self.legend_shadow_checkbox.value = legend_options["legend_shadow"]

            # update legend_rounded_corners
            self.legend_rounded_corners_checkbox.value = legend_options[
                "legend_rounded_corners"
            ]

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)


class GridOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting grid rendering options.

    Parameters
    ----------
    grid_options : `dict`
        The initial grid options. It must be a `dict` with the following keys:

        * ``render_grid`` : (`bool`) Flag for rendering the grid.
        * ``grid_line_width`` : (`int`) The line width (e.g. ``1``).
        * ``grid_line_style`` : (`str`) The line style (e.g. ``'-'``).

    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_title : `str`, optional
        The description of the show line checkbox.
    render_checkbox_type : {``checkbox``, ``toggle``}, optional
        The type of the rendering switch. If ``checkbox``, then
        `ipywidgets.Checkbox` is used. if ``toggle``, then an
        `ipywidgets.ToggleButton` with customized appearance is used.
    """

    def __init__(
        self,
        grid_options,
        render_function=None,
        render_checkbox_type="toggle",
        render_checkbox_title="Render grid",
    ):
        # Create children
        self.render_grid_switch = SwitchWidget(
            grid_options["render_grid"],
            description=render_checkbox_title,
            switch_type=render_checkbox_type,
        )
        self.render_grid_switch.layout.margin = "7px"
        self.grid_line_width_title = ipywidgets.HTML(value="Width")
        self.grid_line_width_text = ipywidgets.BoundedFloatText(
            value=grid_options["grid_line_width"],
            min=0.0,
            max=10 ** 6,
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.grid_line_style_title = ipywidgets.HTML(value="Style")
        grid_line_style_dict = OrderedDict()
        grid_line_style_dict["solid"] = "-"
        grid_line_style_dict["dashed"] = "--"
        grid_line_style_dict["dash-dot"] = "-."
        grid_line_style_dict["dotted"] = ":"
        self.grid_line_style_dropdown = ipywidgets.Dropdown(
            value=grid_options["grid_line_style"],
            options=grid_line_style_dict,
            layout=ipywidgets.Layout(width="3cm"),
        )

        # Group widgets
        self.box_1 = ipywidgets.HBox(
            [self.grid_line_width_title, self.grid_line_width_text]
        )
        self.box_1.layout.align_items = "center"
        self.box_1.layout.margin = "0px 10px 0px 0px"
        self.box_2 = ipywidgets.HBox(
            [self.grid_line_style_title, self.grid_line_style_dropdown]
        )
        self.box_2.layout.align_items = "center"
        self.box_3 = ipywidgets.HBox([self.box_1, self.box_2])
        self.box_3.layout.align_items = "flex-end"
        self.container = ipywidgets.VBox([self.render_grid_switch, self.box_3])

        # Create final widget
        super(GridOptionsWidget, self).__init__(
            [self.container], Dict, grid_options, render_function=render_function
        )

        # Set functionality
        def grid_options_visible(change):
            self.box_3.layout.display = "flex" if change["new"] else "none"

        grid_options_visible({"new": grid_options["render_grid"]})
        self.render_grid_switch.observe(
            grid_options_visible, names="selected_values", type="change"
        )

        def save_options(change):
            self.selected_values = {
                "render_grid": self.render_grid_switch.selected_values,
                "grid_line_width": float(self.grid_line_width_text.value),
                "grid_line_style": self.grid_line_style_dropdown.value,
            }

        self.render_grid_switch.observe(
            save_options, names="selected_values", type="change"
        )
        self.grid_line_width_text.observe(save_options, names="value", type="change")
        self.grid_line_style_dropdown.observe(
            save_options, names="value", type="change"
        )

    def set_widget_state(self, grid_options, allow_callback=True):
        r"""
        Method that updates the state of the widget with a new set of values.

        Parameters
        ----------
        grid_options : `dict`
            The selected grid options. It must be a `dict` with the following
            keys:

            * ``render_grid`` : (`bool`) Flag for rendering the grid.
            * ``grid_line_width`` : (`int`) The line width (e.g. ``1``).
            * ``grid_line_style`` : (`str`) The line style (e.g. ``'-'``).

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != grid_options:
            # keep old value
            old_value = self.selected_values

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.render_grid_switch.set_widget_state(
                grid_options["render_grid"], allow_callback=False
            )
            self.grid_line_style_dropdown.value = grid_options["grid_line_style"]
            self.grid_line_width_text.value = float(grid_options["grid_line_width"])

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)


class CameraWidget(ipywidgets.DOMWidget):
    r"""
    Creates a webcam widget.

    Parameters
    ----------
    canvas_width : `int`, optional
        The initial width of the rendered canvas. Note that this doesn't
        actually change the webcam resolution. It simply rescales the
        rendered image, as well as the size of the returned screenshots.
    hd : `bool`, optional
        If ``True``, then the webcam will be set to high definition (HD), i.e.
        720 x 1280. Otherwise the default resolution will be used.
    """
    _view_name = Unicode("CameraView").tag(sync=True)
    _view_module = Unicode("camera").tag(sync=True)
    imageurl = Unicode("").tag(sync=True)
    take_snapshot = Bool(False).tag(sync=True)
    canvas_width = Int(640).tag(sync=True)
    canvas_height = Int().tag(sync=True)
    hd = Bool(True).tag(sync=True)
    snapshots = List().tag(sync=True)

    def __init__(self, canvas_width=640, hd=True, *args):
        super(CameraWidget, self).__init__(*args)
        # Set tait values
        self.canvas_width = canvas_width
        self.hd = hd
        # Assign callback to imageurl trait
        self.observe(self._from_data_url, names="imageurl", type="change")

    @staticmethod
    def _from_data_url(change):
        r"""
        Method that converts the image in `imageurl` to `menpo.image.Image`
        and appends it to `self.snapshots`.
        """
        self = change["owner"]
        data_uri = change["new"]
        data_uri = data_uri.encode("utf-8")
        data_uri = data_uri[len("data:image/png;base64,") :]
        im = PILImage.open(BytesIO(b64decode(data_uri)))
        self.snapshots.append(Image.init_from_channels_at_back(np.array(im)[..., :3]))


class TriMeshOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting trimesh rendering options.

    Parameters
    ----------
    mesh_options : `dict`
        The initial mesh options. It must be a `dict` with the following keys:

        * ``mesh_type`` : (`str`) One of ('surface', 'wireframe', 'mesh',
                                          'fancymesh', 'points')
        * ``line_width`` : (`int`) The width of the rendered lines.
        * ``colour`` : (`str`) The mesh colour (e.g. ``'red'`` or ``'#0d3c4e'``)
        * ``marker_style`` : (`str`) The size of the markers. (e.g. ``'cube'``).
        * ``marker_size`` : (`float`) The size of the markers (e.g. ``0.1``).
        * ``marker_resolution`` : (`int`) The resolution of the markers.
        * ``step`` : (`int`) The sampling step of the markers.
        * ``alpha`` : (`float`) The alpha (transparency) value.

    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    """

    def __init__(self, mesh_options, render_function=None):
        # Initialize color converter instance
        from matplotlib.colors import ColorConverter

        colour_converter = ColorConverter()

        # Create children
        self.mesh_type_title = ipywidgets.HTML(value="Type")
        self.mesh_type_toggles = ipywidgets.Dropdown(
            options=["surface", "wireframe", "points", "mesh", "fancymesh"],
            tooltip="Select the mesh type.",
            value=mesh_options["mesh_type"],
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.line_width_title = ipywidgets.HTML(value="Line width")
        self.line_width_text = ipywidgets.BoundedFloatText(
            value=float(mesh_options["line_width"]),
            min=0.0,
            max=10 ** 6,
            layout=ipywidgets.Layout(width="1.1cm"),
        )
        self.colour_widget = ColourSelectionWidget(
            mesh_options["colour"], description="Colour", render_function=None
        )
        self.alpha_title = ipywidgets.HTML(value="Alpha")
        self.alpha_slider = ipywidgets.FloatSlider(
            value=mesh_options["alpha"],
            min=0.0,
            max=1.0,
            step=0.1,
            continuous_update=False,
            readout=False,
            layout=ipywidgets.Layout(width="2.3cm"),
        )
        self.alpha_text = ipywidgets.Label(
            value=str(mesh_options["alpha"]), layout=ipywidgets.Layout(width="0.6cm")
        )
        self.marker_style_title = ipywidgets.HTML(value="Style")
        marker_style_dict = OrderedDict()
        marker_style_dict["Sphere"] = "sphere"
        marker_style_dict["Cube"] = "cube"
        marker_style_dict["Cone"] = "cone"
        marker_style_dict["Cylinder"] = "cylinder"
        marker_style_dict["Arrow"] = "arrow"
        marker_style_dict["Axes"] = "axes"
        marker_style_dict["Point"] = "point"
        marker_style_dict["2D arrow"] = "2darrow"
        marker_style_dict["2D circle"] = "2dcircle"
        marker_style_dict["2D cross"] = "2dcross"
        marker_style_dict["2D dash"] = "2ddash"
        marker_style_dict["2D diamond"] = "2ddiamond"
        marker_style_dict["2D hooked arrow"] = "2dhooked_arrow"
        marker_style_dict["2D square"] = "2dsquare"
        marker_style_dict["2D thick arrow"] = "2dthick_arrow"
        marker_style_dict["2D thick cross"] = "2dthick_cross"
        marker_style_dict["2D triangle"] = "2dtriangle"
        marker_style_dict["2D vertex"] = "2dvertex"
        self.marker_style_dropdown = ipywidgets.Dropdown(
            options=marker_style_dict,
            value=mesh_options["marker_style"],
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.marker_size_title = ipywidgets.HTML(value="Style")
        m1 = mesh_options["marker_size"]
        m2 = False
        m_icon = "fa-keyboard-o"
        if mesh_options["marker_size"] is None:
            m1 = 0.1
            m2 = True
            m_icon = "fa-times"
        self.marker_size_text = ipywidgets.BoundedFloatText(
            value=m1,
            disabled=m2,
            min=0.0,
            max=10 ** 6,
            layout=ipywidgets.Layout(width="1.9cm"),
        )
        self.marker_size_none = ipywidgets.Button(
            description="",
            icon=m_icon,
            layout=ipywidgets.Layout(width="1.0cm", height="0.8cm"),
        )
        self.marker_resolution_title = ipywidgets.HTML(value="Resolution")
        self.marker_resolution_text = ipywidgets.BoundedIntText(
            value=mesh_options["marker_resolution"],
            min=0,
            max=10 ** 6,
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.step_title = ipywidgets.HTML(value="Step")
        self.step_text = ipywidgets.BoundedIntText(
            value=mesh_options["step"],
            min=1,
            max=10 ** 6,
            layout=ipywidgets.Layout(width="3cm"),
        )

        # Group widgets
        self.box_1 = ipywidgets.HBox([self.mesh_type_title, self.mesh_type_toggles])
        self.box_1.layout.align_items = "center"
        self.box_1.layout.margin = "9px"
        self.box_2 = ipywidgets.HBox([self.line_width_title, self.line_width_text])
        self.box_2.layout.align_items = "center"
        self.box_2.layout.margin = "0px 10px 0px 0px"
        self.box_3 = ipywidgets.HBox(
            [self.alpha_title, self.alpha_slider, self.alpha_text]
        )
        self.box_3.layout.align_items = "center"
        self.box_4 = ipywidgets.HBox(
            [self.marker_style_title, self.marker_style_dropdown]
        )
        self.box_4.layout.align_items = "center"
        self.box_5 = ipywidgets.HBox(
            [self.marker_size_title, self.marker_size_text, self.marker_size_none]
        )
        self.box_5.layout.align_items = "center"
        self.box_6 = ipywidgets.HBox(
            [self.marker_resolution_title, self.marker_resolution_text]
        )
        self.box_6.layout.align_items = "center"
        self.box_7 = ipywidgets.HBox([self.step_title, self.step_text])
        self.box_7.layout.align_items = "center"
        self.box_8 = ipywidgets.VBox([self.box_4, self.box_5])
        self.box_8.layout.align_items = "flex-end"
        self.box_8.layout.margin = "0px 10px 0px 0px"
        self.box_9 = ipywidgets.VBox([self.box_6, self.box_7])
        self.box_9.layout.align_items = "flex-end"
        self.box_10 = ipywidgets.HBox([self.box_8, self.box_9])
        self.box_11 = ipywidgets.HBox([self.box_1, self.box_2])
        self.box_12 = ipywidgets.VBox([self.colour_widget, self.box_3])
        self.box_12.layout.align_items = "flex-end"
        self.box_12.layout.margin = "0px 10px 0px 0px"
        self.box_13 = ipywidgets.HBox([self.box_12, self.box_10])
        self.container = ipywidgets.VBox([self.box_11, self.box_13])

        # Create final widget
        mesh_options["colour"] = colour_converter.to_rgb(mesh_options["colour"])
        super(TriMeshOptionsWidget, self).__init__(
            [self.container], Dict, mesh_options, render_function=render_function
        )

        # Set functionality
        def marker_options_visible(change):
            self.box_10.layout.display = (
                "flex" if change["new"] == "fancymesh" else "none"
            )

        marker_options_visible({"new": mesh_options["mesh_type"]})
        self.mesh_type_toggles.observe(
            marker_options_visible, names="value", type="change"
        )

        def alpha_text_update(change):
            self.alpha_text.value = str(change["new"])

        self.alpha_slider.observe(alpha_text_update, names="value", type="change")

        def line_width_visible(change):
            self.box_2.layout.display = (
                "flex"
                if change["new"] in ["wireframe", "mesh", "fancymesh"]
                else "none"
            )

        line_width_visible({"new": mesh_options["mesh_type"]})
        self.mesh_type_toggles.observe(line_width_visible, names="value", type="change")

        def save_options(change):
            marker_size = None
            if not self.marker_size_text.disabled:
                marker_size = float(self.marker_size_text.value)
            self.selected_values = {
                "mesh_type": self.mesh_type_toggles.value,
                "line_width": float(self.line_width_text.value),
                "colour": colour_converter.to_rgb(
                    self.colour_widget.selected_values[0]
                ),
                "marker_style": self.marker_style_dropdown.value,
                "marker_size": marker_size,
                "marker_resolution": int(self.marker_resolution_text.value),
                "step": int(self.step_text.value),
                "alpha": float(self.alpha_slider.value),
            }

        self.mesh_type_toggles.observe(save_options, names="value", type="change")
        self.line_width_text.observe(save_options, names="value", type="change")
        self.colour_widget.observe(save_options, names="selected_values", type="change")
        self.marker_style_dropdown.observe(save_options, names="value", type="change")
        self.marker_size_text.observe(save_options, names="value", type="change")
        self.marker_resolution_text.observe(save_options, names="value", type="change")
        self.step_text.observe(save_options, names="value", type="change")
        self.alpha_slider.observe(save_options, names="value", type="change")

        def button_icon(_):
            if self.marker_size_text.disabled:
                self.marker_size_none.icon = "fa-keyboard-o"
                self.marker_size_text.disabled = False
            else:
                self.marker_size_none.icon = "fa-times"
                self.marker_size_text.disabled = True
            save_options({})

        self.marker_size_none.on_click(button_icon)

    def set_widget_state(self, mesh_options, allow_callback=True):
        r"""
        Method that updates the state of the widget if the provided
        `mesh_options` are different than `self.selected_values`.

        Parameters
        ----------
        mesh_options : `dict`
            The selected mesh options. It must be a `dict` with the following
            keys:

            * ``mesh_type`` : (`str`) One of ('surface', 'wireframe', 'mesh',
                                              'fancymesh', 'points')
            * ``line_width`` : (`int`) The width of the rendered lines.
            * ``colour`` : (`str`) The mesh colour (e.g. ``'red'`` or ``'#0d3c4e'``)
            * ``marker_style`` : (`str`) The size of the markers. (e.g. ``'cube'``).
            * ``marker_size`` : (`float`) The size of the markers (e.g. ``0.1``).
            * ``marker_resolution`` : (`int`) The resolution of the markers.
            * ``step`` : (`int`) The sampling step of the markers.
            * ``alpha`` : (`float`) The alpha (transparency) value.

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != mesh_options:
            # keep old value
            old_value = self.selected_values

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.mesh_type_toggles.value = mesh_options["mesh_type"]
            self.line_width_text.value = float(mesh_options["line_width"])
            self.marker_style_dropdown.value = mesh_options["marker_style"]
            if mesh_options["marker_size"] is None:
                self.marker_size_text.disabled = True
                self.marker_size_none.icon = "fa-times"
            else:
                self.marker_size_text.disabled = False
                self.marker_size_none.icon = "fa-keyboard-o"
                self.marker_size_text.value = float(mesh_options["marker_size"])
            self.marker_resolution_text.value = int(mesh_options["marker_resolution"])
            self.step_text.value = int(mesh_options["step"])
            self.alpha_slider.value = float(mesh_options["alpha"])
            self.colour_widget.set_widget_state(
                mesh_options["colour"], allow_callback=False
            )

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)


class TexturedTriMeshOptionsWidget(MenpoWidget):
    r"""
    Creates a widget for selecting textured trimesh rendering options.

    Parameters
    ----------
    mesh_options : `dict`
        The initial mesh options. It must be a `dict` with the following keys:

        * ``render_texture`` : (`bool`) Flag for enabling the texture rendering.
        * ``mesh_type`` : (`str`) One of ('surface', 'wireframe')
        * ``ambient_light`` : (`float`) The ambient light of the mesh.
        * ``specular_light`` : (`float`) The specular light of the mesh.
        * ``line_width`` : (`float`) The line width in case of wireframe.
        * ``colour`` : (`str`) The colour in case the texture is disabled.
        * ``alpha`` : (`float`) The alpha (transparency) value.

    render_function : `callable` or ``None``, optional
        The render function that is executed when a widgets' value changes.
        If ``None``, then nothing is assigned.
    render_checkbox_type : {``checkbox``, ``toggle``}, optional
        The type of the rendering switch. If ``checkbox``, then
        `ipywidgets.Checkbox` is used. if ``toggle``, then an
        `ipywidgets.ToggleButton` with customized appearance is used.
    render_checkbox_title : `str`, optional
        The description of the show line checkbox.
    """

    def __init__(
        self,
        mesh_options,
        render_checkbox_type="toggle",
        render_checkbox_title="Render texture",
        render_function=None,
    ):
        # Initialize color converter instance
        from matplotlib.colors import ColorConverter

        colour_converter = ColorConverter()

        # Create children
        self.render_texture_switch = SwitchWidget(
            mesh_options["render_texture"],
            description=render_checkbox_title,
            switch_type=render_checkbox_type,
        )
        self.render_texture_switch.layout.margin = "0px 10px 0px 0px"
        self.mesh_type_title = ipywidgets.HTML(value="Type")
        self.mesh_type_toggles = ipywidgets.Dropdown(
            options=["surface", "wireframe"],
            tooltip="Select the mesh type.",
            value=mesh_options["mesh_type"],
            layout=ipywidgets.Layout(width="3cm"),
        )
        self.mesh_type_toggles.layout.margin = "0px 15px 0px 0px"
        self.line_width_title = ipywidgets.HTML(value="Line width")
        self.line_width_text = ipywidgets.BoundedFloatText(
            value=float(mesh_options["line_width"]),
            min=0.0,
            max=10 ** 6,
            layout=ipywidgets.Layout(width="1.2cm"),
        )
        self.ambient_title = ipywidgets.HTML(value="Ambient")
        self.ambient_slider = ipywidgets.FloatSlider(
            value=mesh_options["ambient_light"],
            min=0.0,
            max=1.0,
            step=0.05,
            continuous_update=False,
            layout=ipywidgets.Layout(width="6cm"),
        )
        self.specular_title = ipywidgets.HTML(value="Specular")
        self.specular_slider = ipywidgets.FloatSlider(
            value=mesh_options["specular_light"],
            min=0.0,
            max=1.0,
            step=0.05,
            continuous_update=False,
            layout=ipywidgets.Layout(width="6cm"),
        )
        self.alpha_title = ipywidgets.HTML(value="Alpha")
        self.alpha_slider = ipywidgets.FloatSlider(
            value=mesh_options["alpha"],
            min=0.0,
            max=1.0,
            step=0.05,
            continuous_update=False,
            layout=ipywidgets.Layout(width="6cm"),
        )
        self.colour_widget = ColourSelectionWidget(
            mesh_options["colour"], description="Colour", render_function=None
        )

        # Group widgets
        self.box_1 = ipywidgets.HBox([self.mesh_type_title, self.mesh_type_toggles])
        self.box_1.layout.align_items = "center"
        self.box_2 = ipywidgets.HBox([self.line_width_title, self.line_width_text])
        self.box_2.layout.align_items = "center"
        self.box_3 = ipywidgets.HBox([self.ambient_title, self.ambient_slider])
        self.box_3.layout.align_items = "center"
        self.box_4 = ipywidgets.HBox([self.specular_title, self.specular_slider])
        self.box_4.layout.align_items = "center"
        self.box_5 = ipywidgets.HBox([self.alpha_title, self.alpha_slider])
        self.box_5.layout.align_items = "center"

        self.box_6 = ipywidgets.HBox([self.render_texture_switch, self.colour_widget])
        self.box_6.layout.align_items = "center"
        self.box_6.layout.margin = "9px"
        self.box_7 = ipywidgets.HBox([self.box_1, self.box_2])
        self.box_8 = ipywidgets.VBox([self.box_3, self.box_4, self.box_5])
        self.box_8.layout.align_items = "flex-end"
        self.container = ipywidgets.VBox([self.box_6, self.box_7, self.box_8])

        # Create final widget
        mesh_options["colour"] = colour_converter.to_rgb(mesh_options["colour"])
        super(TexturedTriMeshOptionsWidget, self).__init__(
            [self.container], Dict, mesh_options, render_function=render_function
        )

        # Set functionality
        def colour_visible(change):
            self.colour_widget.layout.visibility = (
                "visible" if not change["new"] else "hidden"
            )

        colour_visible({"new": mesh_options["render_texture"]})
        self.render_texture_switch.observe(
            colour_visible, names="selected_values", type="change"
        )

        def line_width_visible(change):
            self.box_2.layout.visibility = (
                "visible" if change["new"] == "wireframe" else "hidden"
            )

        line_width_visible({"new": mesh_options["mesh_type"]})
        self.mesh_type_toggles.observe(line_width_visible, names="value", type="change")

        def save_options(change):
            self.selected_values = {
                "render_texture": self.render_texture_switch.selected_values,
                "mesh_type": self.mesh_type_toggles.value,
                "line_width": float(self.line_width_text.value),
                "ambient_light": float(self.ambient_slider.value),
                "specular_light": float(self.specular_slider.value),
                "alpha": float(self.alpha_slider.value),
                "colour": colour_converter.to_rgb(
                    self.colour_widget.selected_values[0]
                ),
            }

        self.render_texture_switch.observe(
            save_options, names="selected_values", type="change"
        )
        self.mesh_type_toggles.observe(save_options, names="value", type="change")
        self.ambient_slider.observe(save_options, names="value", type="change")
        self.specular_slider.observe(save_options, names="value", type="change")
        self.alpha_slider.observe(save_options, names="value", type="change")
        self.line_width_text.observe(save_options, names="value", type="change")
        self.colour_widget.observe(save_options, names="selected_values", type="change")

    def set_widget_state(self, mesh_options, allow_callback=True):
        r"""
        Method that updates the state of the widget if the provided
        `mesh_options` are different than `self.selected_values`.

        Parameters
        ----------
        mesh_options : `dict`
            The selected mesh options. It must be a `dict` with the following
            keys:

            * ``mesh_type`` : (`str`) One of ('surface', 'wireframe')
            * ``ambient_light`` : (`float`) The ambient light of the mesh.
            * ``specular_light`` : (`float`) The specular light of the mesh.
            * ``alpha`` : (`float`) The alpha (transparency) value.

        allow_callback : `bool`, optional
            If ``True``, it allows triggering of any callback functions.
        """
        if self.selected_values != mesh_options:
            # keep old value
            old_value = self.selected_values

            # temporarily remove render callback
            render_function = self._render_function
            self.remove_render_function()

            # update
            self.render_texture_switch.set_widget_state(
                mesh_options["render_texture"], allow_callback=False
            )
            self.mesh_type_toggles.value = mesh_options["mesh_type"]
            self.ambient_slider.value = float(mesh_options["ambient_light"])
            self.specular_slider.value = float(mesh_options["specular_light"])
            self.alpha_slider.value = float(mesh_options["alpha"])
            self.line_width_text.value = float(mesh_options["line_width"])
            self.colour_widget.set_widget_state(
                mesh_options["colour"], allow_callback=False
            )

            # re-assign render callback
            self.add_render_function(render_function)

            # trigger render function if allowed
            if allow_callback:
                self.call_render_function(old_value, self.selected_values)
