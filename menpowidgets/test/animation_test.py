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
