from menpo.base import MenpoMissingDependencyError

try:
    from .base import (visualize_aam, visualize_patch_aam, visualize_atm,
                       visualize_patch_atm, plot_ced, visualize_fitting_result)
except MenpoMissingDependencyError:
    pass


# Remove from scope
del MenpoMissingDependencyError
