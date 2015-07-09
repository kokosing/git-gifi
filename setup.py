from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


# Inspired by the example at https://pytest.org/latest/goodpractises.html
class NoseTestCommand(TestCommand):
    user_options = [('nose-args=', 'a', "Arguments to pass to nose")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.nose_args = ''

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # Run nose ensuring that argv simulates running nosetests directly
        import nose
        nose.run_exit(argv=['nosetests'] + self.nose_args.split(','))

requirements = [
    'PyGithub==1.25.2',
    'GitPython==1.0.1',
    'slackclient==0.15'
]

test_requirements = [
    'nose==1.3.4',
    'mock==1.0.1',
    'coverage==4.0a6'
]

setup_requirements = [
    'flake8'
]

setup(
    name='git-gifi',
    version='0.1',
    description='Git and github enhancements to git.',
    author='Grzegorz Kokosinski',
    author_email='g.kokosinski a) gmail.com',
    keywords='git github pull request slack',
    packages=find_packages(exclude=['*tests*']),
    package_dir={'gifi': 'gifi'},
    test_suite='test',
    install_requires=requirements,
    tests_require=test_requirements,
    setup_requires=setup_requirements,
    entry_points={'console_scripts': ['gifi = gifi.main:main']},
    cmdclass={'test': NoseTestCommand}
)
