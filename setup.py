from setuptools import setup, find_packages

setup(
    name='crepo',
    version='1.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'crepo=crepo.main:main',
        ],
    },
    install_requires=[
        'pyperclip',  # Add other dependencies as needed
    ],
)
