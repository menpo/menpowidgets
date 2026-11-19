"""The 3D widgets, which draw with Mayavi (offscreen here): needs menpo3d, Mayavi and a Qt binding."""

import numpy as np
import pytest

import IPython.display
from menpo.model import PCAModel
from menpo.shape import PointCloud

import menpowidgets as mw
from menpowidgets.test.helpers import Errors, exercise, install_output_hook

mlab = pytest.importorskip("mayavi.mlab")
pytest.importorskip("PySide6")
m3io = pytest.importorskip("menpo3d.io")


@pytest.fixture(autouse=True)
def offscreen_mayavi():
    mlab.options.offscreen = True
    yield
    mlab.close(all=True)


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


def check(widget_factory, shown, errors, minimum=20):
    widget_factory()
    assert shown, "nothing was displayed"
    n = exercise(shown[-1], errors)
    assert n > minimum
    assert not errors, "\n".join(errors[:10])


def a_shape(seed):
    return PointCloud(np.random.RandomState(seed).rand(30, 3))


def test_visualize_shapes_3d(shown, errors):
    check(lambda: mw.visualize_shapes_3d([a_shape(i) for i in range(3)]), shown, errors)


def test_visualize_meshes_3d(shown, errors):
    bunny = m3io.import_builtin_asset.bunny_obj()
    check(lambda: mw.visualize_meshes_3d([bunny, bunny]), shown, errors)


def test_visualize_landmarks_3d(shown, errors):
    james = m3io.import_builtin_asset.james_obj()
    check(lambda: mw.visualize_landmarks_3d([james.landmarks]), shown, errors)


def test_visualize_shape_model_3d(shown, errors):
    model = PCAModel([a_shape(i) for i in range(5)])
    check(lambda: mw.visualize_shape_model_3d(model), shown, errors)
