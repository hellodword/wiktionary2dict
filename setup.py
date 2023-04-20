import sys


if not (3, 10) < sys.version_info[:2]:
    sys.exit("""
***** ERROR ***********************************************************
* use python 3.11 or above
***********************************************************************
""")

import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()

with open('requirements.txt', 'r') as requirements_file:
    requirements_text = requirements_file.read()

requirements = requirements_text.split()

setuptools.setup(
    name='wiktionary2dict',
    version='0.0.1',
    description='generate dictionary from wiktionary dump',
    url='https://github.com/hellodword/wiktionary2dict',
    author='hellodword',
    author_email='',
    license='MIT',
    entry_points={
        'console_scripts': [
            "wiktionary2dict = wiktionary2dict.__main__:main",
        ]
    },
    packages=setuptools.find_packages(),
    zip_safe=False,
    long_description_content_type="text/markdown",
    long_description=long_description,
    install_requires=requirements
)
