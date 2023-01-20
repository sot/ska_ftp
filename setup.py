# Licensed under a 3-clause BSD style license - see LICENSE.rst
from setuptools import setup
from ska_helpers.setup_helper import duplicate_package_info
from testr.setup_helper import cmdclass

name = "ska_ftp"
namespace = "Ska.ftp"

packages = ["ska_ftp", "ska_ftp.tests"]
package_dir = {name: name}
package_data = {"ska_ftp.tests": ["netrc"]}

duplicate_package_info(packages, name, namespace)
duplicate_package_info(package_dir, name, namespace)
duplicate_package_info(package_data, name, namespace)


setup(name=name,
      author='Tom Aldcroft',
      description='Light wrapper around Python ftplib and paramiko.SFTPClient',
      author_email='taldcroft@cfa.harvard.edu',
      url='http://cxc.harvard.edu/mta/ASPECT/tool_doc/pydocs/Ska.ftp.html',
      use_scm_version=True,
      setup_requires=['setuptools_scm', 'setuptools_scm_git_archive'],
      zip_safe=False,
      packages=packages,
      package_data=package_data,
      package_dir=package_dir,
      tests_require=['pytest'],
      cmdclass=cmdclass,
      )
