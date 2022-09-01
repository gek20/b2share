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

"""Test B2Share Temporary Access """

import json
import time
from urllib import parse

from flask import url_for

from b2share_unit_tests.helpers import create_record, create_user


def test_get_token(app, login_user,  test_records_data):
    """ Test temporary access tokens:
        Test if owner is able to generate the access token
    """

    uploaded_files = {
        'myfile1.dat': b'contents1',
        'myfile2.dat': b'contents2'
    }

    with app.app_context():
        creator = create_user('creator')
        _deposit, pid, _record = create_record(
            test_records_data[0], creator, files=uploaded_files)
        other_user = create_user('other_user')

        url = url_for('b2share_temporary_access_token.b2rec_tempfileaccess',
                      pid_value=pid.pid_value, _external=True)
        headers = [('Accept', '*/*'), ('Content-Length', '0'),
                   ('Accept-Encoding', 'gzip, deflate, br')]
        url = parse.unquote(url)

        with app.test_client() as client:

            # get token
            res = client.get(url, headers=headers)
            # User is not authenticated. It should fail
            assert 401 == res.status_code

            if other_user is not None:
                login_user(other_user, client)
            res = client.get(url, headers=headers)
            # User is not the owner
            assert 403 == res.status_code

        with app.test_client() as client:
            if creator is not None:
                login_user(creator, client)
            res = client.get(url, headers=headers)
            # User is not the owner
            assert 200 == res.status_code


def test_unknown_user_is_allowed_to_download(app, login_user,  test_records_data):
    """ Test temporary access tokens:
        Test if an unkonw user is allowed to access the file with the token.
        Test if token expires
    """

    uploaded_files = {
        'myfile1.dat': b'contents1',
        'myfile2.dat': b'contents2'
    }

    with app.app_context():

        creator = create_user('creator')
        _deposit, pid, record = create_record(
            test_records_data[0], creator, files=uploaded_files)

        # create record and get jwt token
        with app.test_client() as client:
            if creator is not None:
                login_user(creator, client)
            # get token
            url = url_for('b2share_temporary_access_token.b2rec_tempfileaccess',
                          pid_value=pid.pid_value, _external=True)
            headers = [('Accept', '*/*'), ('Content-Length', '0'),
                       ('Accept-Encoding', 'gzip, deflate, br')]
            minutes = 1
            url = parse.unquote(url) + "?days=0&minutes={}".format(minutes)
            res = client.get(url, headers=headers)

            # 200 = we have received the jwt token
            res_content = json.loads(res.get_data(as_text=True))

            assert 200 == res.status_code
            assert "jwt" in res_content.keys() and len(res_content['jwt']) > 0
            print("Expiration: {}".format(res_content['expiration']))

        #test if we can get the record with the token without login
        with app.test_client() as new_client:

            for func in app.before_first_request_funcs:
                func()

            for file_name in uploaded_files.keys():

                url = url_for('invenio_files_rest.object_api',
                              bucket_id=record.files.bucket, key=file_name, _external=True)
                url = url + "?jwt={}".format(res_content.get("jwt"))
                url = parse.unquote(url)
                res = new_client.get(url, headers=headers)
                assert res.get_data() == uploaded_files[file_name]
                assert 200 == res.status_code

            time.sleep(80)

            for file_name in uploaded_files.keys():
                url = url_for('invenio_files_rest.object_api',
                              bucket_id=record.files.bucket, key=file_name, _external=True)
                url = url + "?jwt={}".format(res_content.get("jwt"))
                url = parse.unquote(url)
                res = new_client.get(url, headers=headers)
                assert 400 == res.status_code
