import matplotlib
import pytest

matplotlib.use("Agg")


@pytest.fixture(autouse=True)
def in_a_temporary_directory(tmp_path, monkeypatch):
    # the Export tab's Save button writes the figure into the working directory
    monkeypatch.chdir(tmp_path)
