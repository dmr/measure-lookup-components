# -*- coding: utf-8 -*-
import json
import StringIO
import urlparse

import curl, pycurl
import pandas
import numpy


def get_timing_info(c_info):
    t = {
        'connect': c_info['connect-time'],
        'total': c_info['total-time'],
        'namelookup': c_info['namelookup-time']
    }
    t['process'] = t['total'] - t['connect']
    t_transfer_start = c_info['starttransfer-time']
    t['wait'] = t_transfer_start - c_info['pretransfer-time']
    t['transfer'] = t['total'] - t_transfer_start
    assert t['process'] >= t['transfer']
    assert t['process'] >= t['wait']
    if c_info['redirect-time'] > 0.0:
        print "t_redirect!", c_info['redirect-time']
    return t


def describe_measurements(measurements):
    dct = {
        'min': min(measurements) * 1000,
        'mean': numpy.mean(measurements) * 1000,
        'sd': numpy.std(measurements) * 1000, #[+/-sd]
        'median': numpy.median(measurements) * 1000,
        'max': max(measurements) * 1000
    }
    return dct


def connection_times(measurements):
    res = {}
    for key in [
            'connect',
            'process',
            'total',
            'namelookup',
            'wait',
            'transfer',
            ]:
        res[key] = describe_measurements(
            [r[key] for r in measurements]
        )
    return res


def do_get_request(url):
    url = str(url)
    c = curl.Curl(base_url=url)
    try:
        resp = c.get()
        c_info = c.info()
        timings = get_timing_info(c_info)
        assert c_info['http-code'] == 200,\
            "Response status code {0}".format(c_info['http-code'])
    except pycurl.error:
        raise
    except KeyboardInterrupt:
        return
    finally:
        c.close()
    return resp, timings


# monkey patch PUT support
def put(self, data):
    self.set_option(pycurl.PUT, 1)
    self.set_option(pycurl.READFUNCTION, StringIO.StringIO(data).read)
    return self._Curl__request()
setattr(curl.Curl, 'put', put)


def do_put_request(url, data=2):
    url = str(url)
    c = curl.Curl(base_url=url)
    try:
        resp = c.put(data)
    except pycurl.error:
        raise
    finally:
        timings = get_timing_info(c.info())
        c.close()
    return resp, timings


def do_get_vr_request(url):
    return do_get_request(urlparse.urljoin(url, '/vr/'))


def get_actor_list(actor_source, limit):
    actor_urls = [str(u) for u in json.loads(
        do_get_request(actor_source)[0])
    ]
    if len(actor_urls) < limit:
        print "Reusing actors. Maybe start more real actors"
    while len(actor_urls) < limit:
        actor_urls.extend(actor_urls)
    return actor_urls[:limit]


def measure_one_url(
        test_fct,
        url,
        measurements
        ):
    measurements_results = []
    error_count = 0
    for _ in range(measurements):
        try:
            resp, t = test_fct(url)
            measurements_results.append(t)
        except pycurl.error as exc:
            error_count += 1
    if error_count:
        print error_count, "Errors connecting to", url
    return measurements_results


def get_parser():
    import argparse
    parser = argparse.ArgumentParser(
        "Measure query components of actor servers"
    )
    parser.add_argument("-m", "--measurements", default=100, type=int,
        help="Repeat each measurement {m} times. Default: 100"
    )
    parser.add_argument("-c", "--uri-count", default=5, type=int,
        help="Use {c} different Urls. Default: 5"
    )
    parser.add_argument(
        "-s", "--actor-source", required=True, type=str,
        help=("Source that responds with a JSON list "
              "of actor URIs. Required parameter")
    )
    parser.add_argument(
        '--print-latex-table', default=False, action="store_true",
        help="Print result as latex table. Default: False"
    )
    return parser


def measure_lookup_components(
        actor_source,
        uri_count,
        measurements,
        print_latex_table
        ):
    query_urls = get_actor_list(actor_source=actor_source, limit=uri_count)
    print "Querying {0} actors".format(uri_count)

    if print_latex_table:
        try:
            from statsmodels import iolib
        except ImportError:
            print "--print-latex-table requires statsmodels to be installed"
            raise SystemExit

    for test_name, test_fct in [
            ("Test get_value", do_get_request),
            ("Test get_value_range", do_get_vr_request),
            ("Test set_value", do_put_request)
            ]:
        for url in query_urls:
            print '\n', test_name, "Querying", \
                url, measurements, "times..."
            results = measure_one_url(
                test_fct, url, measurements
            )
            if not results:
                continue

            metrics = connection_times(results)
            df = pandas.DataFrame(metrics).transpose().reindex_axis(
                ['min','mean','sd','median','max'], axis=1
            )
            if print_latex_table:
                #df = numpy.round(df,6)
                from statsmodels import iolib
                tbl = iolib.SimpleTable(df.values, [k for k in df],
                    #HACK. How can we get the row names of a DataFrame?
                    [k for k in df.transpose()])
                print tbl.as_latex_tabular()
            else:
                print df, '\n'


def main():
    measure_lookup_components(**get_parser().parse_args().__dict__)
