from setuptools import setup, find_packages
import versioneer


setup(name='menpowidgets',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description="Menpo's Jupyter widgets for fancy visualization",
      author='The Menpo Development Team',
      author_email='hello@menpo.org',
      packages=find_packages(),
      install_requires=['menpo>=0.7,<0.8',
                        'ipywidgets>=6.0,<7.0',
                        'traitlets>=4.3.2,<5.0',
                        'ipython>=5.3.0,<6.0',
                        'jupyter>=1.0,<2.0'],
      package_data={'menpowidgets': ['logos/*', 'js/*']}
      )
