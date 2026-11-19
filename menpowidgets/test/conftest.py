import os

import matplotlib
import pytest

matplotlib.use("Agg")

# Mayavi (the 3D widgets) renders offscreen through Qt: choose the toolkit before it is imported
os.environ.setdefault("ETS_TOOLKIT", "qt")
os.environ.setdefault("QT_API", "pyside6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(autouse=True)
def in_a_temporary_directory(tmp_path, monkeypatch):
    # the Export tab's Save button writes the figure into the working directory
    monkeypatch.chdir(tmp_path)
