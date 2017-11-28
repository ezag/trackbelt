trackbelt
=========

Search music tracks by title, artist and duration

Installation for development
----------------------------

.. code-block::

    git clone https://github.com/ezag/trackbelt.git
    python -m venv env
    env/bin/activate
    pip install -r requirements.txt
    pip install -e '.[testing]'
    pytest

Usage
-----

.. code-block::

    $ trackbelt tricky forget
    INFO:trackbelt:Searching "tricky - forget"
    INFO:trackbelt:Result:
    {
      "artist": "Tricky",
      "title": "Forget",
      "duration": "3:46",
      "discogs": {
        "release_id": 5914226,
        "track_position": 3
      }
    }
