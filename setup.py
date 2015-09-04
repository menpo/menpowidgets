from setuptools import setup, find_packages
import versioneer


setup(name='menpowidgets',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description="Menpo's Jupyter widgets for fancy visualization",
      author='The Menpo Development Team',
      author_email='james.booth08@imperial.ac.uk',
      packages=find_packages(),
      install_requires=['menpo>=0.5.1,<0.6',
                        'menpofit>=0.2.1,<0.3',
                        'ipywidgets>=4.*,<5.*',
                        'traitlets>=4.*,<5.*',
                        'ipython>=4.*,<5.*',
                        'jupyter>=4.*,<5.*',
                        'notebook>=4.*,<5.*'],
      package_data={'menpo': 'logos/*'}
      )
