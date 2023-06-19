from setuptools import setup, find_packages
from pathlib import Path


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='psbs',
    version='0.1.2',
    python_requires='>=3.8',
    description='PuzzleScript Build System',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='J.C. Miller',
    author_email='johncoreymiller@gmail.com',
    url='https://github.com/jcmiller11/PSBS',
    download_url = 'https://github.com/jcmiller11/PSBS/archive/refs/tags/0.1.2.tar.gz',
    license='MIT',
    packages=find_packages(),
    package_data={'': ['example.txt']},
    include_package_data=True,
    install_requires=[
        'jinja2',
        'pyyaml',
        'Pillow',
        'platformdirs'
    ],

    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Games/Entertainment :: Puzzle Games',
        'Topic :: Software Development :: Build Tools'
    ],
    entry_points={
        'console_scripts': [
            'psbs=psbs.psbs:main'
        ],
    },
)