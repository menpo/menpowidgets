def error_type_key_to_func(error_type):
    from menpofit.result import (
        compute_root_mean_square_error, compute_point_to_point_error,
        compute_normalise_point_to_point_error)
    if error_type is 'me_norm':
        func = compute_normalise_point_to_point_error
    elif error_type is 'me':
        func = compute_point_to_point_error
    elif error_type is 'rmse':
        func = compute_root_mean_square_error
    else:
        raise ValueError('Unexpected error_type. '
                         'Supported values are: {me_norm, me, rmse}')
    return func
