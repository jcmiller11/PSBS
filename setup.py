from setuptools import setup

setup(
    name='psbs',
    version='0.0.2',    
    description='PuzzleScript Build System',
    url='https://github.com/jcmiller11/PSBS',
    author='J.C. Miller',
    author_email='johncoreymiller@gmail.com',
    license='MIT',
    packages=['psbs'],
    package_data={'': ['main.pss']},
    include_package_data=True,
    install_requires=[
        'gistyc',
        'jinja2',
        'pyyaml'               
    ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
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