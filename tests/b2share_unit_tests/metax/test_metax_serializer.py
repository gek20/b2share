"""Test B2SHARE Metax serializer"""

import pytest
from b2share_unit_tests.helpers import (create_record, create_user)
from b2share.modules.records.minters import make_record_url
from invenio_indexer.api import RecordIndexer
from b2share.modules.metax.serializer import serialize_to_metax, get_preferred_identifier, get_b2rec_id


from flask import url_for
from urllib import parse

from invenio_records_files.api import Record

from b2share_unit_tests.metax.helpers import add_versions

def test_fmi_record_creation(app, login_user, test_communities, get_serialized, get_fmi_one):
    with app.app_context():
        creator = create_user('creator')
        _deposit, pid, _record = create_record(get_fmi_one, creator)
        serialized_record = serialize_to_metax(_record, 'testdatacatalog')
        serialized_record['research_dataset']['preferred_identifier'] = ''
        serialized_record['research_dataset']['other_identifier'] = []
        assert get_serialized == serialized_record

def test_versioned_record(app, login_user, test_communities, get_serialized, get_fmi_one):
    with app.app_context():
        creator = create_user('creator')
        _deposit, pid, _record = create_record(get_fmi_one, creator)
        _deposit_v2, pid_v2, _record_v2 = create_record(get_fmi_one, creator, version_of=pid.pid_value)
        serialized_record_1 = serialize_to_metax(_record, 'testdatacatalog')
        serialized_record_1['research_dataset']['preferred_identifier'] = ''
        serialized_record_1['research_dataset']['other_identifier'] = []
        checker_original = get_serialized
        checker_next = add_versions(checker_original, next_version=get_preferred_identifier(_record_v2))
        assert checker_next == serialized_record_1

        serialized_record_2 = serialize_to_metax(_record_v2, 'testdatacatalog')
        serialized_record_2['research_dataset']['preferred_identifier'] = ''
        serialized_record_2['research_dataset']['other_identifier'] = []
        checker_previous = add_versions(checker_original, previous_version=get_preferred_identifier(_record))
        assert checker_previous == serialized_record_2

def test_record_without_ext_files(app, login_user, test_communities, get_serialized, get_fmi_one):
    with app.app_context():
        creator = create_user('creator')
        rec = get_fmi_one
        rec['community_specific']['bbbbbbbb-1111-1111-1111-111111111112']['external_url'] = []
        _deposit, pid, _record = create_record(rec, creator)
        serialized_record = serialize_to_metax(_record, 'testdatacatalog')
        serialized_record['research_dataset']['preferred_identifier'] = ''
        serialized_record['research_dataset']['other_identifier'] = []
        checker = get_serialized
        del checker['research_dataset']['remote_resources']
        assert checker == serialized_record

def test_record_with_files(app, login_user, test_communities, get_serialized, get_fmi_one):
    with app.app_context():
        creator = create_user('creator')
        uploaded_files = {
            'myfile1.dat': b'contents1'
        }

        rec = get_fmi_one
        _deposit, pid, _record = create_record(rec, creator, files=uploaded_files)
        serialized_record = serialize_to_metax(_record, 'testdatacatalog')
        serialized_record['research_dataset']['preferred_identifier'] = ''
        serialized_record['research_dataset']['other_identifier'] = []
        checker = get_serialized
        checker['research_dataset']['remote_resources'].insert(0,{
            'title': _record['_files'][0]['key'],
            'access_url': {
                'identifier': 'https://dev.fmi.b2share.csc.fi/records/' + get_b2rec_id(_record)['value']
            },
            'download_url': {
                'identifier': _record['_files'][0]['ePIC_PID']
            },
            "use_category":{
                "in_scheme":"http://uri.suomi.fi/codelist/fairdata/use_category",
                "identifier":"http://uri.suomi.fi/codelist/fairdata/use_category/code/outcome",
                "pref_label":{
                    "en":"Outcome material",
                    "fi":"Tulosaineisto",
                    "und":"Tulosaineisto"
                }
            }
        })
        assert checker == serialized_record
