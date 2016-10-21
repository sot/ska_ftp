from setuptools import setup

from Ska.ftp import __version__

try:
    from testr.setup_helper import cmdclass
except ImportError:
    cmdclass = {}

setup(name='Ska.ftp',
      author='Tom Aldcroft',
      description='Light wrapper around Python ftplib and paramiko.SFTPClient',
      author_email='taldcroft@cfa.harvard.edu',
      version=__version__,
      zip_safe=False,
      packages=['Ska.ftp', 'Ska.ftp.tests'],
      tests_require=['pytest'],
      cmdclass=cmdclass,
      )
