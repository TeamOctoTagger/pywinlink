try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='winlink',
    version='0.1.0',
    description='Module to create symlinks on Windows',
    url='https://github.com/TeamOctoTagger/pywinlink',
    author='Team OctoTagger',
    license='GPLv3',
    packages=["winlink"],
    install_requires=["pywin32"],
    entry_points={
        'console_scripts': [
            'pywinlink=winlink.service:main',
        ],
    },
)
