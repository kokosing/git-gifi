try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

requirements = [
    'PyGithub==1.25.2',
    'GitPython==1.0.1'
]

test_requirements = [
    'nose>=1.0'
]

setup(
    name='git-gifii',
    description='Git and github enhancements to git.',
    author='Grzegorz Kokosinski',
    packages=find_packages(exclude=['*tests*']),
    package_dir={'gifi': 'gifi'},
    test_suite='tests',
    install_requires=requirements,
    tests_require=test_requirements,
    entry_points={'console_scripts': ['gifi = gifi:main']}
)
