"""Create the widgets, then poke every visible child widget and collect the callback errors.

The widgets are built outside a kernel, with ``IPython.display.display`` captured, so no browser
is needed. Exceptions raised by the render callbacks of a visualisation are shown by ipywidgets'
``Output.capture`` instead of being raised, so ``Output.__exit__`` is hooked to collect them too.
"""

import traceback

import ipywidgets as ipw
import ipywidgets.widgets.widget_output as widget_output

NUMERIC = (
    ipw.IntSlider,
    ipw.FloatSlider,
    ipw.IntText,
    ipw.FloatText,
    ipw.BoundedFloatText,
    ipw.BoundedIntText,
)
CHOICE = (ipw.Dropdown, ipw.Select, ipw.ToggleButtons, ipw.RadioButtons)


def walk(widget):
    yield widget
    for child in getattr(widget, "children", ()) or ():
        yield from walk(child)


def visible(widget, ancestors):
    return all(w.layout.display != "none" for w in (*ancestors, widget))


def walk_visible(widget, ancestors=()):
    """Widgets the user can reach: those under a ``display: none`` container are skipped."""
    if visible(widget, ancestors):
        yield widget
        for child in getattr(widget, "children", ()) or ():
            yield from walk_visible(child, (*ancestors, widget))


class Errors(list):
    """Exceptions raised in callbacks, with a description of the interaction that caused them."""

    current = "creation"

    def record(self, exception):
        frames = traceback.extract_tb(exception.__traceback__)
        where = frames[-1] if frames else None
        place = f"{where.filename.split('/')[-1]}:{where.lineno}" if where else "?"
        self.append(
            f"{self.current}: {type(exception).__name__}: {exception} ({place})"
        )


def interactions(root):
    """Yield (description, action) for every way of changing a visible child of ``root``."""
    for w in walk_visible(root):
        name = f"{type(w).__name__}({getattr(w, 'description', '') or ''})"
        if isinstance(w, NUMERIC):
            low = getattr(w, "min", None)
            high = getattr(w, "max", None)
            if low is None or high is None:
                low, high = w.value, w.value + 1
            for value in (low, high, (low + high) / 2):
                yield f"{name}={value}", lambda w=w, v=value: setattr(w, "value", v)
        elif isinstance(w, CHOICE) and w._options_full:
            for label, value in list(w._options_full)[:8]:
                yield f"{name}={label!r}", lambda w=w, v=value: setattr(w, "value", v)
        elif isinstance(w, (ipw.Checkbox, ipw.ToggleButton)):
            for _ in range(2):
                yield f"{name} toggled", lambda w=w: setattr(w, "value", not w.value)
        elif isinstance(w, ipw.ColorPicker):
            for colour in ("#00ff00", "#123456"):
                yield f"{name}={colour}", lambda w=w, c=colour: setattr(w, "value", c)
        elif isinstance(w, ipw.Button):
            icon = w.icon or ""
            if "play" in icon:  # animations need an event loop: tested separately
                continue
            yield f"{name} clicked", w.click
        elif isinstance(w, (ipw.Tab, ipw.Accordion)):
            for index in range(len(w.children)):
                yield (
                    f"{name} tab {index}",
                    lambda w=w, i=index: setattr(w, "selected_index", i),
                )


def exercise(root, errors):
    """Poke every visible child widget, returning the number of interactions."""
    count = 0
    for description, action in list(interactions(root)):
        Errors.current = description
        count += 1
        try:
            action()
        except Exception as exception:  # noqa: BLE001
            errors.record(exception)
    return count


def install_output_hook(errors, monkeypatch):
    original = widget_output.Output.__exit__

    def hooked(self, etype, evalue, tb):
        if etype is not None:
            errors.record(evalue)
        return original(self, etype, evalue, tb)

    monkeypatch.setattr(widget_output.Output, "__exit__", hooked)
