from setuptools import find_packages, setup

setup(
    name='trackbelt',
    version='1.0.dev0',
    description='Search music tracks by title, artist and duration',
    author='Eugen Zagorodniy',
    author_email='e.zagorodniy@gmail.com',
    url='https://github.com/ezag/trackbelt',
    packages=find_packages(),
    install_requires=[
        'beautifulsoup4',
        'click',
        'discogs-client',
        'PyYAML',
        'soundcloud',
        'xdg',
    ],
    extras_require=dict(
        testing=[
            'pytest',
        ],
    ),
    entry_points=dict(console_scripts=[
        'trackbelt = trackbelt:cmd_search_track',
    ]),
)
