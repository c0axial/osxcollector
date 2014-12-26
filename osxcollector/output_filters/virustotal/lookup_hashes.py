#!/usr/bin/env python

# -*- coding: utf-8 -*-
#
# LookupHashesFilter uses VirusTotal to lookup the values in 'sha2' and add 'osxcollector_vthash' key.
#
from osxcollector.output_filters.base_filters.output_filter import run_filter
from osxcollector.output_filters.base_filters. \
    threat_feed import ThreatFeedFilter
from osxcollector.output_filters.virustotal.api import VirusTotalApi


class LookupHashesFilter(ThreatFeedFilter):

    """A class to lookup hashes using VirusTotal API."""

    def __init__(self, lookup_when=None, suspicious_when=None):
        super(LookupHashesFilter, self).__init__('sha2',
                                                 'osxcollector_vthash', lookup_when=lookup_when,
                                                 suspicious_when=suspicious_when, api_key='virustotal')

    def _lookup_iocs(self, all_iocs, suspicious_iocs):
        """Caches the VirusTotal info for a set of hashes.

        Args:
            all_iocs - a list of hashes.
            suspicious_iocs - a subset of hashes that are considered 'extra suspicious'
        Returns:
            A dict with hash as key and threat info as value
        """
        threat_info = {}

        vt = VirusTotalApi(self._api_key)
        reports = vt.get_file_reports(all_iocs)

        for hash_val in reports.keys():
            report = reports[hash_val]
            if not report:
                continue
            if self._should_store_ioc_info(report):
                threat_info[hash_val] = self._trim_hash_report(report)

        return threat_info

    def _should_store_ioc_info(self, report, min_hits=1):
        """Only store if the hash has > min_hits positive detections.

        Args:
            report - A dict response from get_file_reports
            min_hits - Minimum number of VT positives
        Returns:
            boolean
        """
        return 1 == report.get('response_code') and min_hits < report.get('positives', 0)

    def _trim_hash_report(self, report):
        """Copy just the required keys from the report into a new report.

        Args:
            report - A dict response from get_file_reports
        Returns:
            A smaller dict
        """
        copy_keys = [
            'scan_id',
            'sha1',
            'sha256',
            'md5',
            'scan_date',
            'permalink',
            'positives',
            'total',
            'response_code'
        ]

        return dict([(key, report.get(key)) for key in copy_keys])


def main():
    run_filter(LookupHashesFilter())


if __name__ == "__main__":
    main()
