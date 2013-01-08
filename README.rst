measure-lookup-components
=========================

Measure the components of a request.


Installation
------------

Can be installed via pip from this repository::

    pip install git+http://github.com/dmr/measure-lookup-components.git#egg=measure_lookup_components

Usage
-----

The package provides a CLI: measure_lookup_component::

    $ measure_lookup_components -h

    usage: Measure query components of actor servers [-h] [-m MEASUREMENTS]
                                                 [-c URI_COUNT] -s
                                                 ACTOR_SOURCE
                                                 [--print-latex-table]

    optional arguments:
      -h, --help                show this help message and exit
      -m MEASUREMENTS, --measurements MEASUREMENTS
                            Repeat each measurement {m} times. Default: 100
      -c URI_COUNT, --uri-count URI_COUNT
                            Use {c} different Urls. Default: 5
      -s ACTOR_SOURCE, --actor-source ACTOR_SOURCE
                            Source that responds with a JSON list of actor URIs.
                            Required parameter
      --print-latex-table   Print result as latex table. Default: False

