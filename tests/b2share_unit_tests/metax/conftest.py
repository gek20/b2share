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

"""Pytest configuration for b2share Metax tests."""

import pytest
import json
import copy
from b2share_demo.helpers import resolve_community_id, resolve_block_schema_id

fmi_record_one = {
        'titles': [{'title':'My Test METAX Record'}],
        'descriptions': [{'description':"The long description of My Test METAX Record",
                          'description_type': "Abstract"}],
        'creators': [{'creator_name': 'Glados, R.'}, {'creator_name': 'Cube, Companion'}],
        'publisher': 'Finnish Meteorological Institute',
        'publication_date': '2000-12-12',
        'disciplines': [
            {
                'classification_code':"3.3.2",
                'discipline_identifier':"3.3.2 → Earth sciences → Environmental science",
                'discipline_name':"3.3.2 → Earth sciences → Environmental science",
                'scheme': "b2share.legacy",
                'scheme_uri':"http://b2share.eudat.eu/suggest/disciplines.json"
            }
        ],
        'keywords': [{'keyword':'phaser'}, {'keyword':'laser'}, {'keyword':'maser'}, {'keyword':'portal gun'}],
        'contributors': [{'contributor_name': "Turret", "contributor_type": "ContactPerson", "affiliations": [{"affiliation_name": "Finnish Meteorological Institute"}]}],
        'languages': [{'language_identifier': "eng",'language_name': 'English', 'scheme': 'ISO-639-3', 'scheme_uri': 'https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry'}],
        'resource_types': [{'resource_type_general': "Dataset"}],
        'alternate_identifiers': [{'alternate_identifier': "007",
                                   'alternate_identifier_type': "w3id"}],
        'license': {'license':"CC-BY-SA", 'license_uri': "http://creativecommons.org/licenses/by-sa/4.0/"},
        'community': '$COMMUNITY_ID[FMI]',
        'open_access': True,
        'contact_email': 'info@aperture.org',
        'embargo_date': '2021-09-30T13:58:09.782Z',
        'spatial_coverages': [
            {
                'place': 'test place in test country',
                'point': {
                    'point_latitude': 36.61,
                    'point_longitude': -97.49
                }
            },{
                'place': 'second test',
                'polygons': [
                    {
                        'polygon': [
                            {
                                'point_longitude': -97,
                                'point_latitude': 36
                            },{
                                'point_longitude': 62,
                                'point_latitude': 25
                            },{
                                'point_longitude': 65,
                                'point_latitude': 36
                            }
                        ] 
                    }
                ] 
            },{
                'place': 'third location',
                'box': {
                    'northbound_latitude': 62,
                    'eastbound_longitude': 25,
                    'westbound_longitude': 20,
                    'southbound_latitude': 60
                }
            }
        ],
        'temporal_coverages': {
            'ranges': [
                {
                    'end_date': "2020-09-30T21:00:00.000Z",
                    'start_date': "2012-08-15T21:00:00.000Z"
                }
            ]
        },
        'related_identifiers': [
            {'related_identifier': 'https://testidentifier.csc.fi', 'relation_type': 'IsCitedBy', 'related_identifier_type': 'URL'}
        ],
        'funding_references': [
            {
                'funder_name': 'Test Academy of testland'
            }
        ],
        'community_specific': {
            '$BLOCK_SCHEMA_ID[FMISchema]': {
                'topic': 'climatologyMeteorologyAtmosphere',
                'supplementalinfo': 'More inforrmation for this record',
                'spatialCoverage_resolution': 2,
                'spatialCoverage_levels': [
                    {
                        'spatialCoverage_level': 'level for spatial coverage',
                        'spatialCoverage_levelunit': 'degree'
                    }
                ],
                'parameter': [
                    {
                        'parameter_depiction': ' Description of this parameter',
                        'parameter_name': 'Name of this test parametrer',
                        'parameter_unit': 'Test parameter unit',
                        'parameter_url': 'https://url.parameter.csc.fi'
                    }
                ],
                'model': 'test model',
                'measurement_platform': ['platform 9 and 3/4'],
                'lineage_statement': 'Statement for test lineage',
                'lineage_sources': ['Source1', 'source2'],
                'lineage_processsteps': ['step one', 'step two'],
                'external_url': ['https://b2share.eudat.eu', 'https://csc.fi']
            }
        }
    }

@pytest.fixture(scope='function')
def get_fmi_one(app):
    with app.app_context():
        r = json.loads(resolve_block_schema_id(resolve_community_id(
                    json.dumps(fmi_record_one)))
                )
        return copy.deepcopy(r)

serialized = {
    'data_catalog': 'testdatacatalog',
    'available': '2021-09-30',
    'metadata_owner_org': 'FMI.fi',
    'metadata_provider_org': 'FMI.fi',
    'metadata_provider_user': 'FMI',
    'research_dataset': {
        'preferred_identifier': '',
        'other_identifier': [],
        'title': {'en': fmi_record_one['titles'][0]['title']},
        'description': {'en': fmi_record_one['descriptions'][0]['description']},
        'creator': [
            {'@type': 'Person', 'name': 'Glados, R.', 'member_of': {'@type': 'Organization', 'identifier': 'http://uri.suomi.fi/codelist/fairdata/organization/code/4940015'}},
            {'@type': 'Person', 'name': 'Cube, Companion', 'member_of': {'@type': 'Organization', 'identifier': 'http://uri.suomi.fi/codelist/fairdata/organization/code/4940015'}}
        ],
        'publisher': {
            '@type': 'Organization',
            'identifier': 'http://uri.suomi.fi/codelist/fairdata/organization/code/4940015'
        },
        'field_of_science': [
            {
                "in_scheme": "http://www.yso.fi/onto/okm-tieteenala/conceptscheme",
                "identifier": "http://www.yso.fi/onto/okm-tieteenala/ta1171",
            }
        ],
        'keyword': ['phaser', 'laser', 'maser', 'portal gun', 'INSPIRE theme: climatologyMeteorologyAtmosphere'],
        'issued': fmi_record_one['publication_date'].split('T')[0],
        'contributor': [
            {'@type': 'Person', 'name': 'Turret', 'member_of': {'@type': 'Organization', 'identifier': 'http://uri.suomi.fi/codelist/fairdata/organization/code/4940015'}}
        ],
        'language': [{"identifier": "http://lexvo.org/id/iso639-3/eng"}],
        'spatial': [
            {'as_wkt': ['POINT(-97.49 36.61)'], 'geographic_name': 'test place in test country'},
            {'as_wkt': ['MULTIPOLYGON(((-97 36, 62 25, 65 36)))'], 'geographic_name': 'second test'},
            {'as_wkt': ['POLYGON((20 62, 25 62, 25 60, 20 60))'], 'geographic_name': 'third location'}
        ],
        'temporal': [
            {
                'end_date': "2020-09-30T21:00:00.000Z",
                'start_date': "2012-08-15T21:00:00.000Z"
            }
        ],
        'relation': [
            {
                'entity': {
                    'identifier': 'https://testidentifier.csc.fi'
                },
                'relation_type': {
                    'identifier': 'http://purl.org/spar/cito/isCitedBy'
                }
            }
        ],
        'remote_resources': [
            {
                "title": "External data",
                "access_url":{
                    "identifier": 'https://localhost:5000/records/'
                },
                "use_category":{
                    "in_scheme":"http://uri.suomi.fi/codelist/fairdata/use_category",
                    "identifier":"http://uri.suomi.fi/codelist/fairdata/use_category/code/outcome",
                    "pref_label":{
                        "en":"Outcome material",
                        "fi":"Tulosaineisto","und":"Tulosaineisto"
                    }
                }
            },{
                "title": "External data",
                "access_url":{
                    "identifier": 'https://localhost:5000/records/'
                },
                "use_category":{
                    "in_scheme":"http://uri.suomi.fi/codelist/fairdata/use_category",
                    "identifier":"http://uri.suomi.fi/codelist/fairdata/use_category/code/outcome",
                    "pref_label":{
                        "en":"Outcome material",
                        "fi":"Tulosaineisto","und":"Tulosaineisto"
                    }
                }
            }
        ],
        'access_rights': {
            "access_type": {
                "in_scheme": "http://uri.suomi.fi/codelist/fairdata/access_type",
                "identifier": "http://uri.suomi.fi/codelist/fairdata/access_type/code/open",
                "pref_label": {
                        "en": "Open",
                        "fi": "Avoin",
                        "und": "Avoin"
                    },
            },
            "license": [{'identifier': 'http://uri.suomi.fi/codelist/fairdata/license/code/CC-BY-SA-4.0'}]
        },
        'is_output_of': [
            {
                'name': {'en': fmi_record_one['titles'][0]['title']},
                'has_funding_agency': [
                    {
                        '@type': 'Organization',
                        'name': {'en': 'Test Academy of testland'}
                    }
                ],
                'source_organization': [
                    {
                        '@type': 'Organization',
                        'identifier': 'http://uri.suomi.fi/codelist/fairdata/organization/code/4940015'
                    }
                ]
            }
        ]
    }
}

@pytest.fixture(scope='function')
def get_serialized():
    copied = copy.deepcopy(serialized)
    copied['research_dataset']['relation'] = [
        {
            'entity': {
                'identifier': 'https://testidentifier.csc.fi'
            },
            'relation_type': {
                'identifier': 'http://purl.org/spar/cito/isCitedBy'
            }
        }
    ]
    return copied
