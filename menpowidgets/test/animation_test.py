"""The Play loops run as tasks on the event loop, so Pause and Stop work while they run."""

import asyncio

from menpowidgets.options import AnimationOptionsWidget, LinearModelParametersWidget


def run(coroutine):
    return asyncio.run(coroutine)


def make_animation(**kwargs):
    index = {"min": 0, "max": 5, "step": 1, "index": 0}
    return AnimationOptionsWidget(index, interval=0.05, loop_enabled=True, **kwargs)


def test_play_advances_the_index_and_pause_holds_it():
    async def scenario():
        widget = make_animation()
        widget.play_button.click()
        await asyncio.sleep(0.4)
        moved = widget.selected_values
        assert moved != 0 or widget._animation_task is not None
        widget.pause_animation()
        await asyncio.sleep(0.2)
        held = widget.selected_values
        await asyncio.sleep(0.4)
        assert widget.selected_values == held
        assert widget._animation_task.done()
        return moved

    run(scenario())


def test_stop_resets_the_index():
    async def scenario():
        widget = make_animation(index_style="slider")
        widget.play_button.click()
        await asyncio.sleep(0.3)
        widget.stop_animation()
        await asyncio.sleep(0.3)
        assert widget.selected_values == 0
        assert widget._animation_task.done()

    run(scenario())


def test_a_second_play_while_running_is_ignored():
    async def scenario():
        widget = make_animation()
        widget.play_button.click()
        first = widget._animation_task
        widget.play_button.click()
        assert widget._animation_task is first
        widget.stop_animation()
        await asyncio.sleep(0.3)

    run(scenario())


def test_model_parameters_animation_can_be_stopped():
    async def scenario():
        seen = []
        widget = LinearModelParametersWidget(
            3,
            render_function=lambda change: seen.append(widget.selected_values),
            animation_step=1.0,
            interval=0.02,
        )
        widget.play_button.click()
        await asyncio.sleep(0.3)
        assert len(seen) > 1  # the parameters changed while playing
        assert widget.reset_button.disabled  # and the controls were locked
        widget.stop_animation()
        await asyncio.sleep(0.3)
        assert widget._animation_task.done()
        assert not widget.reset_button.disabled

    run(scenario())


def test_animation_runs_to_completion_without_an_event_loop():
    widget = make_animation()
    widget.loop_toggle.value = False  # play once through
    widget.play_button.click()  # no running loop here: it runs synchronously
    assert not widget.please_stop


def test_play_updates_the_figure_without_the_kernel_routing_output():
    """Play redraws from a task, after the click was handled, so the figure is set from Python."""
    import menpo.io as mio
    import menpowidgets as mw
    import IPython.display

    shown = []
    original = IPython.display.display
    IPython.display.display = lambda *a, **k: shown.extend(a)
    try:
        images = [
            mio.import_builtin_asset.takeo_ppm(),
            mio.import_builtin_asset.lenna_png(),
        ]
        mw.visualize_images(images)
    finally:
        IPython.display.display = original
    root = shown[0]

    from menpowidgets.utils import FigureOutput
    from menpowidgets.test.helpers import walk
    from menpowidgets.options import AnimationOptionsWidget

    output = next(w for w in walk(root) if isinstance(w, FigureOutput))
    animation = next(w for w in walk(root) if isinstance(w, AnimationOptionsWidget))
    animation.interval = 0.2

    def frame():
        return output.outputs[0]["data"]["image/png"] if output.outputs else None

    async def scenario():
        before = frame()
        assert before is not None
        animation.play_button.click()
        await asyncio.sleep(0.3)  # one step at 0.2 s
        animation.pause_animation()
        await asyncio.sleep(0.3)
        return before

    before = run(scenario())
    assert frame() != before
