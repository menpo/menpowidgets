# Notebooks for trying every widget

| Notebook | What is in it |
|---|---|
| `1_images_shapes_landmarks` | `visualize_images`, `visualize_shapes_2d`, `visualize_landmarks_2d`, `visualize_patches`, `view_widget`, `plot_graph` |
| `2_models` | `visualize_shape_model_2d`, `visualize_appearance_model` |
| `3_menpofit` | AAMs, ATMs, CLM and its experts, fitting results, CED curves (trains tiny models, ~15 s) |
| `4_not_covered_by_the_tests` | `webcam_widget` (needs a webcam) and the 3D widgets (need menpo3d) |

Each notebook starts with a list of things to try. The automated tests (`menpowidgets/test/`) cover that
every control works without raising; these are for looking at how the widgets render and behave.

## Run them

```
cd menpowidgets
uv venv && uv pip install -e ".[menpofit]" jupyterlab
.venv/bin/jupyter lab notebooks/
```

(Until menpo 0.12.1 is released, install menpo from the branch with the fixes first:
`uv pip install -e path/to/menpo`.) The Export tab's *Save* writes files into the folder you start from.
