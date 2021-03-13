from menpo.base import MenpoMissingDependencyError

try:
    from .base import (
        visualize_aam,
        visualize_patch_aam,
        visualize_atm,
        visualize_patch_atm,
        visualize_clm,
        visualize_expert_ensemble,
        plot_ced,
        visualize_fitting_results,
    )
except (MenpoMissingDependencyError, ModuleNotFoundError, ImportError):
    pass


# Remove from scope
del MenpoMissingDependencyError
