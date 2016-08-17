vkbelt
======

Tool for performing various routines via VK.com API.

Installation (develop mode)
---------------------------
::
    git clone https://github.com/ezag/vkbelt.git
    cd vkbelt
    virtualenv .env
    source .env/bin/activate
    pip install -r requirements-develop.txt
    python setup.py sdist
    python setup.py develop
    python setup.py lint
    vkbelt

Usage
-----

Authenticate as user id4366451 and download own audios storing them
at path in form z20160818/q000.mp3

::
    vkbelt download-audios 4366451 'z20160818/q{:03}.mp3'
