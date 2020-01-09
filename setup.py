# Licensed under a 3-clause BSD style license - see LICENSE.rst
from setuptools import setup

try:
    from testr.setup_helper import cmdclass
except ImportError:
    cmdclass = {}

setup(name='Ska.ftp',
      author='Tom Aldcroft',
      description='Light wrapper around Python ftplib and paramiko.SFTPClient',
      author_email='taldcroft@cfa.harvard.edu',
      url='http://cxc.harvard.edu/mta/ASPECT/tool_doc/pydocs/Ska.ftp.html',
      use_scm_version=True,
      setup_requires=['setuptools_scm', 'setuptools_scm_git_archive'],
      zip_safe=False,
      packages=['Ska', 'Ska.ftp', 'Ska.ftp.tests'],
      package_data={'Ska.ftp.tests': ['netrc']},
      tests_require=['pytest'],
      cmdclass=cmdclass,
      )
