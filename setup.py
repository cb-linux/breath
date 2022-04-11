import re
from setuptools import setup

# README will be shown on PyPi
with open('README.md') as file:
    readme = file.read()

# Track version number
with open('breath/__init__.py') as file:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', file.read(), re.MULTILINE)

setup(
    name='breath',
    author='MilkyDeveloper',
    url='https://github.com/cb-linux/breath',
    project_urls={
        'Discussions': 'https://github.com/cb-linux/breath/discussions',
        'Issues': 'https://github.com/cb-linux/breath/issues',
    },
    version=version,
    packages=['breath'],
    license='MIT',
    description='A way to natively run Linux on modern Chromebooks without replacing firmware.',
    long_description=readme,
    long_description_content_type='text/markdown',
    python_requires='>=3.10.4',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10'
    ]
)
