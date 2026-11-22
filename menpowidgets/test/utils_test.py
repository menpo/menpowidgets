import warnings

import numpy as np
import pytest
from menpo.base import MenpoDeprecationWarning
from menpo.model import PCAModel
from menpo.shape import PointCloud

from menpowidgets.utils import n_components_in_use


def a_model():
    rs = np.random.RandomState(0)
    return PCAModel([PointCloud(rs.rand(10, 2)) for _ in range(8)])


def test_n_components_in_use_is_n_components_for_a_model():
    model = a_model()
    assert n_components_in_use(model) == model.n_components == 7


def a_model_with_fewer_components_in_use():
    model = a_model()
    if hasattr(model, "trim_components_inplace"):
        # menpo with trim_components(): a model with fewer components
        return model.trim_components(3)
    # an older menpo: its number of active components, which an older menpofit
    # fitter also sets on the models of the AAM it was given
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", MenpoDeprecationWarning)
        model.n_active_components = 3
    return model


def test_n_components_in_use_is_the_number_instance_takes_when_fewer_are_used():
    # the widgets must not offer more sliders than instance() takes
    model = a_model_with_fewer_components_in_use()
    assert n_components_in_use(model) == 3
    model.instance(np.zeros(n_components_in_use(model)))
    with pytest.raises(ValueError):
        model.instance(np.zeros(7))
