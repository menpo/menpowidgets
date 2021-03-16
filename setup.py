from setuptools import setup, find_packages


def get_version_and_cmdclass(package_path):
    """Load version.py module without importing the whole package.

    Template code from miniver
    """
    import os
    from importlib.util import module_from_spec, spec_from_file_location

    spec = spec_from_file_location("version", os.path.join(package_path, "_version.py"))
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__version__, module.cmdclass


version, cmdclass = get_version_and_cmdclass("menpowidgets")


setup(
    name="menpowidgets",
    version=version,
    cmdclass=cmdclass,
    description="Menpo's Jupyter widgets for fancy visualization",
    author="The Menpo Development Team",
    author_email="hello@menpo.org",
    packages=find_packages(),
    install_requires=["menpo>=0.11", "ipywidgets"],
    package_data={"menpowidgets": ["logos/*", "js/*"]},
)
