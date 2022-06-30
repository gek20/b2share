# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 CERN.
#
# B2Share is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# B2Share is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with B2Share; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Tests helpers for metax."""

import copy

def add_versions(record, previous_version=None, next_version=None):
    c = copy.deepcopy(record)
    if next_version:
        c['research_dataset']['relation'].append({
            "entity": {
                "type": {
                    "in_scheme": "http://uri.suomi.fi/codelist/fairdata/resource_type",
                    "identifier": "http://uri.suomi.fi/codelist/fairdata/resource_type/code/dataset",
                    "pref_label": {
                        "en": "Dataset",
                        "fi": "Tutkimusaineisto",
                        "und": "Tutkimusaineisto"
                    }
                },
                "identifier": next_version
            },
            "relation_type": {
                "identifier": "http://www.w3.org/ns/adms#next",
                "pref_label": {
                    "fi": "Seuraava versio",
                    "en": "Has next version"
                }
            }
        })
    if previous_version:
        c['research_dataset']['relation'].append({
            "entity": {
                "type": {
                    "in_scheme": "http://uri.suomi.fi/codelist/fairdata/resource_type",
                    "identifier": "http://uri.suomi.fi/codelist/fairdata/resource_type/code/dataset",
                    "pref_label": {
                        "en": "Dataset",
                        "fi": "Tutkimusaineisto",
                        "und": "Tutkimusaineisto"
                    }
                },
                "identifier": previous_version
            },
            "relation_type": {
                "identifier": "http://www.w3.org/ns/adms#previous",
                "pref_label": {
                    "fi": "Edellinen versio",
                    "en": "Has previous version"
                }
            }
        })
    return c
