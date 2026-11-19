"""The webcam widget, without a browser: the front end is replaced by setting the image URL."""

import base64
import io

import IPython.display
import numpy as np
from PIL import Image as PILImage

import menpowidgets as mw
from menpowidgets.options import CameraSnapshotWidget
from menpowidgets.test.helpers import walk


def data_url(value):
    pixels = np.full((20, 30, 3), value, dtype=np.uint8)
    buffer = io.BytesIO()
    PILImage.fromarray(pixels).save(buffer, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()


def test_every_snapshot_is_returned(monkeypatch):
    shown = []
    monkeypatch.setattr(IPython.display, "display", lambda *a, **k: shown.extend(a))
    snapshots = mw.webcam_widget(canvas_width=300, hd=False)
    widget = next(w for w in walk(shown[0]) if isinstance(w, CameraSnapshotWidget))
    for value in (10, 20, 30, 40):
        widget.camera_wid.imageurl = data_url(value)
    assert len(snapshots) == 4
    levels = [float(s.pixels.max()) for s in snapshots]
    assert levels == sorted(levels) and len(set(levels)) == 4


def test_the_front_end_is_an_es_module():
    from menpowidgets.tools import CameraWidget

    source = CameraWidget(canvas_width=300)._esm
    assert "export default" in str(source)
