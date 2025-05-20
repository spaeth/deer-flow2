import pathlib
import tomllib
from setuptools import setup, find_packages

pyproject = tomllib.loads(pathlib.Path('pyproject.toml').read_text())
project = pyproject.get('project', {})

setup(
    name=project.get('name', 'deer-flow'),
    version=project.get('version', '0.0.0'),
    description=project.get('description', ''),
    long_description=pathlib.Path(project.get('readme', 'README.md')).read_text(),
    long_description_content_type='text/markdown',
    python_requires=project.get('requires-python', '>=3.12'),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=project.get('dependencies', []),
    extras_require=project.get('optional-dependencies', {}),
)
