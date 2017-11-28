from setuptools import find_packages, setup

setup(
    name='vkbelt',
    version='1.0.dev0',
    description='Tool for performing various routines via VK.com API',
    author='Eugen Zagorodniy',
    author_email='e.zagorodniy@gmail.com',
    url='https://github.com/ezag/vkbelt',
    packages=find_packages(),
    entry_points=dict(console_scripts=['trackbelt = vkbelt:cmd_search_track']),
)
