def check_n_parameters(n_params, n_levels, max_n_params):
    r"""
    Checks the maximum number of components per level either of the shape
    or the appearance model. It must be ``None`` or `int` or `float` or a `list`
    of those containing ``1`` or ``n_scales`` elements.
    """
    str_error = (
        "n_params must be None or 1 <= int <= max_n_params or "
        "a list of those containing 1 or {} elements"
    ).format(n_levels)
    if not isinstance(n_params, list):
        n_params_list = [n_params] * n_levels
    elif len(n_params) == 1:
        n_params_list = [n_params[0]] * n_levels
    elif len(n_params) == n_levels:
        n_params_list = n_params
    else:
        raise ValueError(str_error)
    for i, comp in enumerate(n_params_list):
        if comp is None:
            n_params_list[i] = max_n_params[i]
        else:
            if isinstance(comp, int):
                if comp > max_n_params[i]:
                    n_params_list[i] = max_n_params[i]
            else:
                raise ValueError(str_error)
    return n_params_list
