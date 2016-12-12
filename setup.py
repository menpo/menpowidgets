from setuptools import setup, find_packages
import versioneer


setup(name='menpowidgets',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description="Menpo's Jupyter widgets for fancy visualization",
      author='The Menpo Development Team',
      author_email='james.booth08@imperial.ac.uk',
      packages=find_packages(),
      install_requires=['menpo>=0.7,<0.8',
                        'ipywidgets>=5.2.2,<6.0',
                        'traitlets>=4.3.1,<5.0',
                        'ipython>=5.1.0,<6.0',
                        'jupyter>=1.0,<2.0'],
      package_data={'menpowidgets': ['logos/*', 'js/*']}
      )
