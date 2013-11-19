from setuptools import setup
setup(name='Ska.ftp',
      author = 'Tom Aldcroft',
      description='Light wrapper around Python ftplib to make it easier to use',
      author_email = 'taldcroft@cfa.harvard.edu',
      py_modules = ['Ska.ftp'],
      version='0.04',
      zip_safe=False,
      namespace_packages=['Ska'],
      packages=['Ska'],
      package_dir={'Ska' : 'Ska'},
      package_data={}
      )
