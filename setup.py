from setuptools import setup


setup(name='csv-view',
      version='0.0.1',
      packages=['csv_view'],
      description='Tools for working with VCF files',
      url='https://github.com/AndersenLab/vcf-toolbox',
      author='Daniel Cook',
      author_email='danielecook@gmail.com',
      license='MIT',
      entry_points="""
      [console_scripts]
            csv_view = csv_view.compare:main
      """,
      install_requires=["flask", "GitPython"],
      zip_safe=False)