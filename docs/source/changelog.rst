.. _changelog:

Changelog
#########

For releases before 0.5.0 see the `GitHub releases <https://github.com/menpo/menpowidgets/releases>`_.

0.6.0 (2026/11/21)
------------------

The 3D widgets (``visualize_meshes_3d``, ``visualize_shapes_3d``,
``visualize_landmarks_3d`` and the 3D parts of the model widgets) draw with
menpo3d's moderngl viewer instead of Mayavi. This needs **menpo3d >= 0.10**:

.. code-block:: console

    pip install "menpowidgets[menpo3d]"      # = menpo3d[viz_notebook]>=0.10

No Qt, Mayavi or ``%matplotlib qt`` is needed any more, and the 3D view is an
interactive widget in the browser (rotate, pan, zoom), also over SSH.

**New: a camera per item.** ``visualize_meshes_3d``, ``visualize_shapes_3d``
and ``visualize_landmarks_3d`` take ``per_mesh_camera``, ``per_shape_camera``
and ``per_landmarks_camera`` (default ``False``: one camera is shared while you
browse, as before). With ``True`` every item remembers its own view: rotate the
first mesh, step to the next and it starts at its own default framing, step
back and the first is as you left it.

**Breaking: the Mayavi-named widgets and options are renamed, with no aliases.**

.. list-table::
   :header-rows: 1
   :widths: 50 50

   * - Before
     - After
   * - ``SaveMayaviFigureOptionsWidget``
     - ``Save3dFigureOptionsWidget``
   * - ``LineMayaviOptionsWidget``, ``MarkerMayaviOptionsWidget``, ``NumberingMayaviOptionsWidget``
     - ``Line3dOptionsWidget``, ``Marker3dOptionsWidget``, ``Numbering3dOptionsWidget``
   * - ``save_mayavi_figure``
     - ``save_3d_figure``
   * - option tabs ``lines_mayavi``, ``markers_mayavi``, ``numbering_mayavi``
     - ``lines_3d``, ``markers_3d``, ``numbering_3d``

The ``menpowidgets[mayavi]`` extra is gone.

Github Pull Requests
....................
- `#44`_ 3D widgets on menpo3d's moderngl viewer; rename the Mayavi-named widgets (@patricksnape)

.. _#44: https://github.com/menpo/menpowidgets/pull/44

0.5.0 (2026/11/19)
------------------

The first release built and published from GitHub Actions with PyPI trusted
publishing. It requires **Python 3.10 or newer** and **menpo >= 0.12.1**, and
was tested by running every widget in JupyterLab 4 (ipywidgets 8, ipykernel 7,
NumPy 2, Matplotlib 3.10 and 3.11).

**Fixed.**

- *Play did nothing on current Jupyter.* The animation loops used
  ``Kernel.do_one_iteration()``, which ipykernel 7 removed; they are now
  coroutines on the kernel's event loop, so Pause and Stop work. Figures drawn
  by an animation are now redrawn (an ``Output`` widget only receives figures
  drawn while the message that started the callback is being handled).
- ``webcam_widget`` only worked in the classic notebook; it is now an
  ``anywidget`` module that works in JupyterLab, Notebook 7 and VS Code.
- ``np.Inf`` (removed in NumPy 2) broke the shape model view; the colour map
  list offered ``spectral``, which Matplotlib removed; the legend and line width
  boxes allowed values that Matplotlib rejects.
- Tab labels were clipped, the logo was stretched in the ``plot_graph`` widget,
  the patch options moved around when a box was ticked, and the shape model
  parameter sliders only updated on release (they now update while dragging).

**Packaging.** ``pyproject.toml`` with ``setuptools-scm`` (the version comes from
the git tag) replaces ``setup.py`` and the vendored miniver, whose ``distutils``
import fails on Python 3.12 and newer. The dependencies are ``menpo``,
``ipywidgets>=8``, ``ipyevents>=2`` and ``anywidget`` (``nest-asyncio`` was
dropped). Extras: ``menpowidgets[menpofit]`` for the menpofit visualizations
and ``menpowidgets[menpo3d]`` for the 3D widgets. CI runs on Linux, macOS and
Windows with Python 3.10 and 3.14, and there is now a test suite that drives
every widget.

Github Pull Requests
....................
- `#42`_ Modernise: pyproject, GitHub Actions, trusted-publishing releases, and fixes found by testing every widget in JupyterLab (@patricksnape)

.. _#42: https://github.com/menpo/menpowidgets/pull/42
