import matplotlib.pyplot as plt
from menpo.visualize.viewmatplotlib import MatplotlibSubplots

# This glyph import is called frequently during visualisation, so we ensure
# that we only import it once. The same for the sum_channels method.
glyph = None
sum_channels = None


def render(renderer, subplots_enabled, subplots_titles, image, render_image,
           image_axes_mode, channel_options, landmark_options, line_options,
           marker_options, numbers_options, legend_options, axes_options,
           image_options, figure_size):
    global glyph
    if glyph is None:
        from menpo.feature.visualize import glyph
    global sum_channels
    if sum_channels is None:
        from menpo.feature.visualize import sum_channels

    # makes sure selected groups is a list
    if not isinstance(landmark_options['group'], list):
        landmark_options['group'] = [landmark_options['group']]
        landmark_options['with_labels'] = [landmark_options['with_labels']]

    # This makes the code shorter for dealing with masked images vs non-masked
    # images
    mask_arguments = ({'masked': channel_options['masked_enabled']}
                      if channel_options['image_is_masked'] else {})
    render_legend = legend_options['render_legend'] and not subplots_enabled

    # plot
    if render_image:
        # image will be displayed
        if (landmark_options['render_landmarks'] and
                len(landmark_options['group']) > 0):
            # there are selected landmark groups and they will be displayed
            if subplots_enabled:
                # calculate subplots structure
                subplots = MatplotlibSubplots()._subplot_layout(
                    len(landmark_options['group']))
            # show image with landmarks
            for k, group in enumerate(landmark_options['group']):
                if subplots_enabled:
                    # create subplot
                    plt.subplot(subplots[0], subplots[1], k + 1)
                    if legend_options['render_legend']:
                        # set subplot's title
                        plt.title(
                            subplots_titles[group],
                            fontname=legend_options['legend_font_name'],
                            fontstyle=legend_options['legend_font_style'],
                            fontweight=legend_options['legend_font_weight'],
                            fontsize=legend_options['legend_font_size'])
                if channel_options['glyph_enabled']:
                    # image, landmarks, masked, glyph
                    renderer = glyph(
                        image,
                        vectors_block_size=channel_options['glyph_block_size'],
                        use_negative=channel_options['glyph_use_negative'],
                        channels=channel_options['channels']).view_landmarks(
                            group=group,
                            with_labels=landmark_options['with_labels'][k],
                            without_labels=None, figure_id=renderer.figure_id,
                            new_figure=False,
                            render_lines=line_options['render_lines'][k],
                            line_style=line_options['line_style'][k],
                            line_width=line_options['line_width'][k],
                            line_colour=line_options['line_colour'][k],
                            render_markers=marker_options['render_markers'][k],
                            marker_style=marker_options['marker_style'][k],
                            marker_size=marker_options['marker_size'][k],
                            marker_edge_width=
                            marker_options['marker_edge_width'][k],
                            marker_edge_colour=
                            marker_options['marker_edge_colour'][k],
                            marker_face_colour=
                            marker_options['marker_face_colour'][k],
                            render_numbering=
                            numbers_options['render_numbering'],
                            numbers_horizontal_align=
                            numbers_options['numbers_horizontal_align'],
                            numbers_vertical_align=
                            numbers_options['numbers_vertical_align'],
                            numbers_font_name=
                            numbers_options['numbers_font_name'],
                            numbers_font_size=
                            numbers_options['numbers_font_size'],
                            numbers_font_style=
                            numbers_options['numbers_font_style'],
                            numbers_font_weight=
                            numbers_options['numbers_font_weight'],
                            numbers_font_colour=
                            numbers_options['numbers_font_colour'],
                            render_legend=render_legend,
                            legend_title=legend_options['legend_title'],
                            legend_font_name=legend_options['legend_font_name'],
                            legend_font_style=
                            legend_options['legend_font_style'],
                            legend_font_size=legend_options['legend_font_size'],
                            legend_font_weight=
                            legend_options['legend_font_weight'],
                            legend_marker_scale=
                            legend_options['legend_marker_scale'],
                            legend_location=legend_options['legend_location'],
                            legend_bbox_to_anchor=
                            legend_options['legend_bbox_to_anchor'],
                            legend_border_axes_pad=
                            legend_options['legend_border_axes_pad'],
                            legend_n_columns=legend_options['legend_n_columns'],
                            legend_horizontal_spacing=
                            legend_options['legend_horizontal_spacing'],
                            legend_vertical_spacing=
                            legend_options['legend_vertical_spacing'],
                            legend_border=legend_options['legend_border'],
                            legend_border_padding=
                            legend_options['legend_border_padding'],
                            legend_shadow=legend_options['legend_shadow'],
                            legend_rounded_corners=
                            legend_options['legend_rounded_corners'],
                            render_axes=axes_options['render_axes'],
                            axes_font_name=axes_options['axes_font_name'],
                            axes_font_size=axes_options['axes_font_size'],
                            axes_font_style=axes_options['axes_font_style'],
                            axes_font_weight=axes_options['axes_font_weight'],
                            axes_x_limits=axes_options['axes_x_limits'],
                            axes_y_limits=axes_options['axes_y_limits'],
                            interpolation=image_options['interpolation'],
                            alpha=image_options['alpha'],
                            cmap_name=image_options['cmap_name'],
                            figure_size=figure_size, **mask_arguments)
                elif channel_options['sum_enabled']:
                    # image, landmarks, masked, sum
                    renderer = sum_channels(
                        image,
                        channels=channel_options['channels']).view_landmarks(
                            group=group,
                            with_labels=landmark_options['with_labels'][k],
                            without_labels=None, figure_id=renderer.figure_id,
                            new_figure=False,
                            render_lines=line_options['render_lines'][k],
                            line_style=line_options['line_style'][k],
                            line_width=line_options['line_width'][k],
                            line_colour=line_options['line_colour'][k],
                            render_markers=marker_options['render_markers'][k],
                            marker_style=marker_options['marker_style'][k],
                            marker_size=marker_options['marker_size'][k],
                            marker_edge_width=
                            marker_options['marker_edge_width'][k],
                            marker_edge_colour=
                            marker_options['marker_edge_colour'][k],
                            marker_face_colour=
                            marker_options['marker_face_colour'][k],
                            render_numbering=
                            numbers_options['render_numbering'],
                            numbers_horizontal_align=
                            numbers_options['numbers_horizontal_align'],
                            numbers_vertical_align=
                            numbers_options['numbers_vertical_align'],
                            numbers_font_name=
                            numbers_options['numbers_font_name'],
                            numbers_font_size=
                            numbers_options['numbers_font_size'],
                            numbers_font_style=
                            numbers_options['numbers_font_style'],
                            numbers_font_weight=
                            numbers_options['numbers_font_weight'],
                            numbers_font_colour=
                            numbers_options['numbers_font_colour'],
                            render_legend=render_legend,
                            legend_title=legend_options['legend_title'],
                            legend_font_name=legend_options['legend_font_name'],
                            legend_font_style=
                            legend_options['legend_font_style'],
                            legend_font_size=legend_options['legend_font_size'],
                            legend_font_weight=
                            legend_options['legend_font_weight'],
                            legend_marker_scale=
                            legend_options['legend_marker_scale'],
                            legend_location=legend_options['legend_location'],
                            legend_bbox_to_anchor=
                            legend_options['legend_bbox_to_anchor'],
                            legend_border_axes_pad=
                            legend_options['legend_border_axes_pad'],
                            legend_n_columns=legend_options['legend_n_columns'],
                            legend_horizontal_spacing=
                            legend_options['legend_horizontal_spacing'],
                            legend_vertical_spacing=
                            legend_options['legend_vertical_spacing'],
                            legend_border=legend_options['legend_border'],
                            legend_border_padding=
                            legend_options['legend_border_padding'],
                            legend_shadow=legend_options['legend_shadow'],
                            legend_rounded_corners=
                            legend_options['legend_rounded_corners'],
                            render_axes=axes_options['render_axes'],
                            axes_font_name=axes_options['axes_font_name'],
                            axes_font_size=axes_options['axes_font_size'],
                            axes_font_style=axes_options['axes_font_style'],
                            axes_font_weight=axes_options['axes_font_weight'],
                            axes_x_limits=axes_options['axes_x_limits'],
                            axes_y_limits=axes_options['axes_y_limits'],
                            interpolation=image_options['interpolation'],
                            alpha=image_options['alpha'],
                            cmap_name=image_options['cmap_name'],
                            figure_size=figure_size, **mask_arguments)
                else:
                    # image, landmarks, masked, not glyph/sum
                    renderer = image.view_landmarks(
                        channels=channel_options['channels'], group=group,
                        with_labels=landmark_options['with_labels'][k],
                        without_labels=None, figure_id=renderer.figure_id,
                        new_figure=False,
                        render_lines=line_options['render_lines'][k],
                        line_style=line_options['line_style'][k],
                        line_width=line_options['line_width'][k],
                        line_colour=line_options['line_colour'][k],
                        render_markers=marker_options['render_markers'][k],
                        marker_style=marker_options['marker_style'][k],
                        marker_size=marker_options['marker_size'][k],
                        marker_edge_width=
                        marker_options['marker_edge_width'][k],
                        marker_edge_colour=
                        marker_options['marker_edge_colour'][k],
                        marker_face_colour=
                        marker_options['marker_face_colour'][k],
                        render_numbering=numbers_options['render_numbering'],
                        numbers_horizontal_align=
                        numbers_options['numbers_horizontal_align'],
                        numbers_vertical_align=
                        numbers_options['numbers_vertical_align'],
                        numbers_font_name=numbers_options['numbers_font_name'],
                        numbers_font_size=numbers_options['numbers_font_size'],
                        numbers_font_style=
                        numbers_options['numbers_font_style'],
                        numbers_font_weight=
                        numbers_options['numbers_font_weight'],
                        numbers_font_colour=
                        numbers_options['numbers_font_colour'],
                        render_legend=render_legend,
                        legend_title=legend_options['legend_title'],
                        legend_font_name=legend_options['legend_font_name'],
                        legend_font_style=legend_options['legend_font_style'],
                        legend_font_size=legend_options['legend_font_size'],
                        legend_font_weight=legend_options['legend_font_weight'],
                        legend_marker_scale=
                        legend_options['legend_marker_scale'],
                        legend_location=legend_options['legend_location'],
                        legend_bbox_to_anchor=
                        legend_options['legend_bbox_to_anchor'],
                        legend_border_axes_pad=
                        legend_options['legend_border_axes_pad'],
                        legend_n_columns=legend_options['legend_n_columns'],
                        legend_horizontal_spacing=
                        legend_options['legend_horizontal_spacing'],
                        legend_vertical_spacing=
                        legend_options['legend_vertical_spacing'],
                        legend_border=legend_options['legend_border'],
                        legend_border_padding=
                        legend_options['legend_border_padding'],
                        legend_shadow=legend_options['legend_shadow'],
                        legend_rounded_corners=
                        legend_options['legend_rounded_corners'],
                        render_axes=axes_options['render_axes'],
                        axes_font_name=axes_options['axes_font_name'],
                        axes_font_size=axes_options['axes_font_size'],
                        axes_font_style=axes_options['axes_font_style'],
                        axes_font_weight=axes_options['axes_font_weight'],
                        axes_x_limits=axes_options['axes_x_limits'],
                        axes_y_limits=axes_options['axes_y_limits'],
                        interpolation=image_options['interpolation'],
                        alpha=image_options['alpha'],
                        cmap_name=image_options['cmap_name'],
                        figure_size=figure_size, **mask_arguments)
        else:
            # either there are not any landmark groups selected or they won't
            # be displayed
            if channel_options['glyph_enabled']:
                # image, not landmarks, masked, glyph
                renderer = glyph(
                    image,
                    vectors_block_size=channel_options['glyph_block_size'],
                    use_negative=channel_options['glyph_use_negative'],
                    channels=channel_options['channels']).view(
                        render_axes=axes_options['render_axes'],
                        axes_font_name=axes_options['axes_font_name'],
                        axes_font_size=axes_options['axes_font_size'],
                        axes_font_style=axes_options['axes_font_style'],
                        axes_font_weight=axes_options['axes_font_weight'],
                        axes_x_limits=axes_options['axes_x_limits'],
                        axes_y_limits=axes_options['axes_y_limits'],
                        figure_size=figure_size,
                        interpolation=image_options['interpolation'],
                        alpha=image_options['alpha'],
                        cmap_name=image_options['cmap_name'], **mask_arguments)
            elif channel_options['sum_enabled']:
                # image, not landmarks, masked, sum
                renderer = sum_channels(
                    image, channels=channel_options['channels']).view(
                        render_axes=axes_options['render_axes'],
                        axes_font_name=axes_options['axes_font_name'],
                        axes_font_size=axes_options['axes_font_size'],
                        axes_font_style=axes_options['axes_font_style'],
                        axes_font_weight=axes_options['axes_font_weight'],
                        axes_x_limits=axes_options['axes_x_limits'],
                        axes_y_limits=axes_options['axes_y_limits'],
                        figure_size=figure_size,
                        interpolation=image_options['interpolation'],
                        alpha=image_options['alpha'],
                        cmap_name=image_options['cmap_name'], **mask_arguments)
            else:
                # image, not landmarks, masked, not glyph/sum
                renderer = image.view(
                    channels=channel_options['channels'],
                    render_axes=axes_options['render_axes'],
                    axes_font_name=axes_options['axes_font_name'],
                    axes_font_size=axes_options['axes_font_size'],
                    axes_font_style=axes_options['axes_font_style'],
                    axes_font_weight=axes_options['axes_font_weight'],
                    axes_x_limits=axes_options['axes_x_limits'],
                    axes_y_limits=axes_options['axes_y_limits'],
                    figure_size=figure_size,
                    interpolation=image_options['interpolation'],
                    alpha=image_options['alpha'],
                    cmap_name=image_options['cmap_name'], **mask_arguments)
    else:
        # image won't be displayed
        if (landmark_options['render_landmarks'] and
                len(landmark_options['group']) > 0):
            # there are selected landmark groups and they will be displayed
            if subplots_enabled:
                # calculate subplots structure
                subplots = MatplotlibSubplots()._subplot_layout(
                    len(landmark_options['group']))
            # not image, landmarks
            for k, group in enumerate(landmark_options['group']):
                if subplots_enabled:
                    # create subplot
                    plt.subplot(subplots[0], subplots[1], k + 1)
                    if render_legend:
                        # set subplot's title
                        plt.title(
                            subplots_titles[group],
                            fontname=legend_options['legend_font_name'],
                            fontstyle=legend_options['legend_font_style'],
                            fontweight=legend_options['legend_font_weight'],
                            fontsize=legend_options['legend_font_size'])
                image.landmarks[group].lms.view(
                    image_view=image_axes_mode,
                    render_lines=line_options['render_lines'][k],
                    line_style=line_options['line_style'][k],
                    line_width=line_options['line_width'][k],
                    line_colour=line_options['line_colour'][k],
                    render_markers=marker_options['render_markers'][k],
                    marker_style=marker_options['marker_style'][k],
                    marker_size=marker_options['marker_size'][k],
                    marker_edge_width=marker_options['marker_edge_width'][k],
                    marker_edge_colour=marker_options['marker_edge_colour'][k],
                    marker_face_colour=marker_options['marker_face_colour'][k],
                    render_axes=axes_options['render_axes'],
                    axes_font_name=axes_options['axes_font_name'],
                    axes_font_size=axes_options['axes_font_size'],
                    axes_font_style=axes_options['axes_font_style'],
                    axes_font_weight=axes_options['axes_font_weight'],
                    axes_x_limits=axes_options['axes_x_limits'],
                    axes_y_limits=axes_options['axes_y_limits'],
                    figure_size=figure_size)
            if not subplots_enabled:
                if len(landmark_options['group']) % 2 == 0:
                    plt.gca().invert_yaxis()
                if render_legend:
                    # Options related to legend's font
                    prop = {'family': legend_options['legend_font_name'],
                            'size': legend_options['legend_font_size'],
                            'style': legend_options['legend_font_style'],
                            'weight': legend_options['legend_font_weight']}

                    # display legend on side
                    plt.gca().legend(
                        landmark_options['group'],
                        title=legend_options['legend_title'], prop=prop,
                        loc=legend_options['legend_location'],
                        bbox_to_anchor=legend_options['legend_bbox_to_anchor'],
                        borderaxespad=legend_options['legend_border_axes_pad'],
                        ncol=legend_options['legend_n_columns'],
                        columnspacing=
                        legend_options['legend_horizontal_spacing'],
                        labelspacing=legend_options['legend_vertical_spacing'],
                        frameon=legend_options['legend_border'],
                        borderpad=legend_options['legend_border_padding'],
                        shadow=legend_options['legend_shadow'],
                        fancybox=legend_options['legend_rounded_corners'],
                        markerscale=legend_options['legend_marker_scale'])

    # show plot
    plt.show()

    return renderer
