"""The menpofit visualisations, on tiny models (six greyscale 60 x 43 images, 5 x 5 patches)."""

import pytest

pytest.importorskip("menpofit")

import IPython.display  # noqa: E402
import menpo.io as mio  # noqa: E402
import menpowidgets as mw  # noqa: E402
from menpofit import aam, atm, clm  # noqa: E402

from menpowidgets.test.helpers import Errors, exercise, install_output_hook  # noqa: E402

GROUP = "PTS"
COMMON = dict(group=GROUP, scales=(1.0,), diagonal=50, verbose=False)


@pytest.fixture
def shown(monkeypatch):
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
def training():
    image = mio.import_builtin_asset.takeo_ppm().as_greyscale()
    return [image.rotate_ccw_about_centre(a).rescale(0.5) for a in (-6, -3, 0, 3, 6, 9)]


@pytest.fixture(scope="module")
def shapes(training):
    return [image.landmarks[GROUP] for image in training]


def check(widget_factory, shown, errors):
    widget_factory()
    assert shown, "nothing was displayed"
    assert exercise(shown[-1], errors) > 20
    assert not errors, "\n".join(errors[:10])


def test_visualize_aam(training, shown, errors):
    model = aam.HolisticAAM(
        training, max_shape_components=3, max_appearance_components=3, **COMMON
    )
    check(lambda: mw.visualize_aam(model), shown, errors)
    shown.clear()
    check(lambda: mw.visualize_aam(model, mode="single"), shown, errors)


def test_visualize_patch_aam(training, shown, errors):
    model = aam.PatchAAM(
        training,
        max_shape_components=3,
        max_appearance_components=3,
        patch_shape=(5, 5),
        **COMMON,
    )
    check(lambda: mw.visualize_patch_aam(model), shown, errors)


def test_visualize_atm(training, shapes, shown, errors):
    model = atm.HolisticATM(training[0], shapes, max_shape_components=3, **COMMON)
    check(lambda: mw.visualize_atm(model), shown, errors)


def test_visualize_patch_atm(training, shapes, shown, errors):
    model = atm.PatchATM(
        training[0], shapes, max_shape_components=3, patch_shape=(5, 5), **COMMON
    )
    check(lambda: mw.visualize_patch_atm(model), shown, errors)


def test_visualize_clm_and_its_experts(training, shown, errors):
    model = clm.CLM(training, max_shape_components=3, patch_shape=(5, 5), **COMMON)
    check(lambda: mw.visualize_clm(model), shown, errors)
    shown.clear()
    ensemble = model.expert_ensembles[0]
    check(
        lambda: mw.visualize_expert_ensemble(ensemble, model.reference_shape),
        shown,
        errors,
    )


def test_plot_ced(shown, errors):
    curves = [[0.01 * k * (i + 1) for k in range(1, 30)] for i in range(2)]
    check(lambda: mw.plot_ced(curves, legend_entries=["a", "b"]), shown, errors)


def test_visualize_fitting_results(training, shown, errors):
    model = aam.HolisticAAM(
        training, max_shape_components=3, max_appearance_components=3, **COMMON
    )
    fitter = aam.LucasKanadeAAMFitter(model, n_shape=3, n_appearance=3)
    results = [
        fitter.fit_from_bb(
            image,
            image.landmarks[GROUP].bounding_box(),
            max_iters=4,
            gt_shape=image.landmarks[GROUP],
        )
        for image in training[:3]
    ]
    check(lambda: mw.visualize_fitting_results(results), shown, errors)

    # The static iterations (a range slider and a command) are hidden until
    # selected, so poke them again, in both figure modes
    from menpowidgets.options import IterativeResultOptionsWidget
    from menpowidgets.test.helpers import walk

    options = next(
        w for w in walk(shown[-1]) if isinstance(w, IterativeResultOptionsWidget)
    )
    options.result_iterations_tab.selected_index = 1
    options.iterations_mode.value = "static"
    for mode in (True, False):
        options.mode.value = mode
        assert exercise(options.index_slicing, errors) >= 4
        assert not errors, "\n".join(errors[:10])
