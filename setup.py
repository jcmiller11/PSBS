from setuptools import setup

setup(
    name='psbs',
    version='0.0.1',    
    description='PuzzleScript Build System',
    url='',
    author='J.C. Miller',
    author_email='johncoreymiller@gmail.com',
    license='MIT',
    packages=['psbs'],
    install_requires=['gistyc',
                      'requests'                  
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3'
    ],
    entry_points={
        'console_scripts': [
            'psbs=psbs.psbs:main'
        ]
    },
)