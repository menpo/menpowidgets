"""Every visualisation: create it and poke each visible control (see helpers.py)."""

import numpy as np
import pytest

import menpo.io as mio
import IPython.display
from menpo.model import PCAModel
from menpo.shape import PointCloud

import menpowidgets as mw
from menpowidgets.test.helpers import Errors, exercise, install_output_hook


@pytest.fixture
def shown(monkeypatch):
    """The widgets passed to ``IPython.display.display`` instead of displaying them."""
    widgets = []
    monkeypatch.setattr(IPython.display, "display", lambda *a, **k: widgets.extend(a))
    return widgets


@pytest.fixture
def errors(monkeypatch):
    errors = Errors()
    Errors.current = "creation"
    install_output_hook(errors, monkeypatch)
    return errors


@pytest.fixture(scope="module")
def takeo():
    return mio.import_builtin_asset.takeo_ppm()


@pytest.fixture(scope="module")
def images(takeo):
    return [takeo, mio.import_builtin_asset.lenna_png()]


@pytest.fixture(scope="module")
def shapes():
    return [PointCloud(np.random.RandomState(i).rand(20, 2) * 50) for i in range(4)]


@pytest.fixture(scope="module")
def appearance_model(takeo):
    images = [takeo.rescale(0.2).as_greyscale() for _ in range(5)]
    for i, image in enumerate(images):
        image.pixels = image.pixels + 0.05 * np.random.RandomState(i).rand(
            *image.pixels.shape
        )
    return PCAModel(images)


def check(widget_factory, shown, errors):
    widget_factory()
    assert shown, "nothing was displayed"
    n = exercise(shown[-1], errors)
    assert n > 20  # it did find the controls
    assert not errors, "\n".join(errors[:10])


def test_visualize_images(images, shown, errors):
    check(lambda: mw.visualize_images(images), shown, errors)


def test_visualize_images_with_a_slider(images, shown, errors):
    check(lambda: mw.visualize_images(images, browser_style="slider"), shown, errors)


def test_visualize_shapes_2d(shapes, shown, errors):
    check(lambda: mw.visualize_shapes_2d(shapes), shown, errors)


def test_visualize_landmarks_2d(images, shown, errors):
    check(lambda: mw.visualize_landmarks_2d([images[0].landmarks]), shown, errors)


def test_visualize_patches(takeo, shown, errors):
    image = takeo.as_greyscale()
    patches = image.extract_patches_around_landmarks(
        "PTS", patch_shape=(9, 9), as_single_array=True
    )
    centres = image.landmarks["PTS"]
    check(lambda: mw.visualize_patches([patches] * 2, [centres] * 2), shown, errors)


def test_visualize_shape_model_2d(shapes, shown, errors):
    check(lambda: mw.visualize_shape_model_2d(PCAModel(shapes)), shown, errors)


def test_visualize_appearance_model(appearance_model, shown, errors):
    check(lambda: mw.visualize_appearance_model(appearance_model), shown, errors)


def test_plot_graph(shown, errors):
    check(
        lambda: mw.plot_graph(
            [1, 2, 3], [[1, 2, 3], [3, 2, 1]], legend_entries=["a", "b"]
        ),
        shown,
        errors,
    )


def test_view_widget_picks_the_widget_for_the_items(images, shapes, shown, errors):
    mw.view_widget(images)
    mw.view_widget(shapes)
    assert len(shown) == 2


def test_named_colour_maps_in_the_image_options(images, shown, errors):
    # this needs menpo >= 0.12.1 (cm.get_cmap was removed in Matplotlib 3.9)
    mw.visualize_images(images)
    import ipywidgets as ipw
    from menpowidgets.test.helpers import walk_visible

    colour_maps = [
        w
        for w in walk_visible(shown[-1])
        if isinstance(w, ipw.Dropdown) and "viridis" in [o[0] for o in w._options_full]
    ]
    assert colour_maps
    for _, value in colour_maps[0]._options_full:
        colour_maps[0].value = value
    assert not errors, "\n".join(errors[:5])
