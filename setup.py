from setuptools import setup

from Ska.ftp import __version__

setup(name='Ska.ftp',
      author='Tom Aldcroft',
      description='Light wrapper around Python ftplib and paramiko.SFTPClient',
      author_email='taldcroft@cfa.harvard.edu',
      py_modules=['Ska.ftp'],
      version=__version__,
      zip_safe=False,
      packages=['Ska'],
      package_dir={'Ska': 'Ska'},
      package_data={}
      )
