"""The 3D widgets, which draw with menpo3d's moderngl viewer (needs menpo3d 1.0 and an OpenGL context)."""

import numpy as np
import pytest

import IPython.display
from menpo.model import PCAModel
from menpo.shape import PointCloud

import menpowidgets as mw
from menpowidgets.test.helpers import Errors, exercise, install_output_hook

m3io = pytest.importorskip("menpo3d.io")
viewmoderngl = pytest.importorskip("menpo3d.visualize.viewmoderngl")


@pytest.fixture(autouse=True)
def opengl():
    from menpo3d.visualize.viewer.worker import get_worker

    try:
        get_worker()
    except Exception as error:  # noqa: BLE001
        pytest.skip(f"no OpenGL: {error}")


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
    # the viewer may display more than the widget (a picture, say): the root is the last ipywidget
    root = next(w for w in reversed(shown) if hasattr(w, "layout"))
    n = exercise(root, errors)
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


def test_visualize_morphable_model(shown, errors):
    from scipy.spatial import Delaunay
    from menpo.shape import PointUndirectedGraph, TriMesh
    from menpo.model import PCAVectorModel
    from menpo3d.morphablemodel import ColouredMorphableModel

    xy = np.stack(np.meshgrid(np.linspace(0, 1, 15), np.linspace(0, 1, 15)), -1)
    xy = xy.reshape(-1, 2)
    base = np.c_[xy, 0.2 * np.sin(4 * xy[:, 0])]
    trilist = Delaunay(xy).simplices
    rng = np.random.RandomState(0)
    shape_model = PCAModel(
        [TriMesh(base + 0.01 * rng.randn(*base.shape), trilist) for _ in range(5)]
    )
    texture_model = PCAVectorModel(rng.rand(5, len(base) * 3))
    landmarks = PointUndirectedGraph.init_from_edges(
        base[:6], np.array([[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]])
    )
    model = ColouredMorphableModel(shape_model, texture_model, landmarks, None, 100)
    check(
        lambda: mw.visualize_morphable_model(
            model, n_shape_parameters=3, n_texture_parameters=3
        ),
        shown,
        errors,
    )


def test_view_widget_picks_the_3d_widgets(shown, errors):
    james = m3io.import_builtin_asset.james_obj()
    mw.view_widget([a_shape(0), a_shape(1)])
    mw.view_widget([james])
    mw.view_widget([james.landmarks])
    mw.view_widget(PCAModel([a_shape(i) for i in range(5)]))
    assert len(shown) == 4


def test_the_meshes_widget_draws_into_the_moderngl_figure(shown, errors):
    bunny = m3io.import_builtin_asset.bunny_obj()
    small = (
        bunny.from_mask(np.arange(bunny.n_points) < bunny.n_points // 2)
        if hasattr(bunny, "from_mask")
        else bunny
    )
    mw.visualize_meshes_3d([bunny, small])
    figure = viewmoderngl.gcf()
    assert [i["kind"] for i in figure.scene.items] == ["mesh"]
    first_camera = figure.get_pose()
    root = next(w for w in reversed(shown) if hasattr(w, "layout"))
    exercise(root, errors)  # moves through the meshes, options tabs and the export tab
    assert not errors, "\n".join(errors[:5])
    assert [i["kind"] for i in figure.scene.items] == [
        "mesh"
    ]  # cleared and redrawn, never accumulating
    assert figure.get_pose()["azimuth"] == first_camera["azimuth"]
    assert figure.render((64, 64)).std() > 5  # something is drawn


def _a_mesh_and_a_ten_times_larger_one():
    from menpo.shape import TriMesh

    bunny = m3io.import_builtin_asset.bunny_obj()
    return bunny, TriMesh(bunny.points * 10 + 50, bunny.trilist)


def _landmarks_of(shape):
    holder = PointCloud(shape.points)
    holder.landmarks["group"] = PointCloud(shape.points)
    return holder.landmarks


@pytest.mark.parametrize(
    "widget, option, make",
    [
        ("visualize_meshes_3d", "per_mesh_camera", lambda small, big: [small, big]),
        (
            "visualize_shapes_3d",
            "per_shape_camera",
            lambda small, big: [PointCloud(small.points), PointCloud(big.points)],
        ),
        (
            "visualize_landmarks_3d",
            "per_landmarks_camera",
            lambda small, big: [_landmarks_of(small), _landmarks_of(big)],
        ),
    ],
)
def test_per_item_camera_gives_each_item_its_own_view(
    shown, errors, widget, option, make
):
    small, big = _a_mesh_and_a_ten_times_larger_one()
    getattr(mw, widget)(make(small, big), **{option: True})
    figure = viewmoderngl.gcf()
    root = next(w for w in reversed(shown) if hasattr(w, "layout"))
    index = _find(root, "AnimationOptionsWidget").index_wid

    def go(i):
        index.selected_values = i
        return figure.get_pose()

    start = figure.get_pose()
    figure.set_pose(**{**start, "azimuth": 1.0})
    first = go(1)  # a new item: the default direction, framed to fit
    assert first["azimuth"] == start["azimuth"]
    assert first["radius"] > 5 * start["radius"]  # ten times larger
    figure.set_pose(**{**first, "azimuth": -0.5})
    assert go(0)["azimuth"] == 1.0  # the first item has its view back
    assert go(1)["azimuth"] == -0.5
    assert not errors, "\n".join(errors[:5])


def test_the_default_keeps_one_camera_for_every_item(shown):
    small, big = _a_mesh_and_a_ten_times_larger_one()
    mw.visualize_meshes_3d([small, small])
    figure = viewmoderngl.gcf()
    root = next(w for w in reversed(shown) if hasattr(w, "layout"))
    index = _find(root, "AnimationOptionsWidget").index_wid
    figure.set_pose(**{**figure.get_pose(), "azimuth": 1.0})
    index.selected_values = 1
    assert figure.get_pose()["azimuth"] == 1.0


def test_the_export_tab_saves_a_png_of_the_figure(shown, tmp_path):
    from PIL import Image

    bunny = m3io.import_builtin_asset.bunny_obj()
    mw.visualize_meshes_3d([bunny])
    root = next(w for w in reversed(shown) if hasattr(w, "layout"))
    save = _find(root, "Save3dFigureOptionsWidget")
    save.filename_text.value = str(tmp_path / "export.png")
    save.overwrite_checkbox.selected_values = True
    save.save_button.click()
    assert Image.open(tmp_path / "export.png").size[0] > 0
    assert save.error_latex.value == ""


def _find(widget, class_name):
    if type(widget).__name__ == class_name:
        return widget
    for child in getattr(widget, "children", ()):
        found = _find(child, class_name)
        if found is not None:
            return found
    return None
