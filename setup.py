from setuptools import setup

setup(
    name='arcjetCV',
    version='0.1',
    packages=['arcjetCV'],
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
            'arcjetCV=arcjetCV.main:main',
        ],
    },
)
