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

import datetime
import jwt
import uuid

from functools import partial

from flask import jsonify, current_app, Blueprint, request
from flask_security.decorators import auth_required

from invenio_rest import ContentNegotiatedMethodView
from invenio_files_rest.models import Bucket
from invenio_records_rest.views import pass_record
from invenio_records_files.api import RecordsBuckets, Record
from invenio_pidstore.resolver import Resolver
from invenio_records_rest.utils import obj_or_import_string

from b2share.modules.records.views import verify_record_permission
from b2share.modules.records.permissions import UpdateRecordPermission


def create_blueprint(endpoints):
    """Create Invenio-Records-REST blueprint."""

    blueprint = Blueprint('b2share_temporary_access_token', __name__)

    for endpoint, options in (endpoints or {}).items():
        rule = create_url_rule( endpoint, 
                                item_route=options.get('item_route', None), 
                                pid_type=options.get('pid_type', None), 
                                record_class=options.get('record_class', None))
        blueprint.add_url_rule(**rule)
    return blueprint


def create_url_rule(endpoint, item_route=None,
                    pid_type=None,
                    record_class=None
                    ):

    record_class = obj_or_import_string(
        record_class, default=Record
    )

    resolver = Resolver(pid_type=pid_type, object_type='rec',
                        getter=partial(record_class.get_record,
                                       with_deleted=True))

    temp_fileccess_view = TempFileAccessTokenResource.as_view(
        TempFileAccessTokenResource.view_name.format(endpoint),
        resolver=resolver)
    rule = item_route + '/tempfileaccess'

    return dict(rule=rule, view_func=temp_fileccess_view)


class TempFileAccessTokenResource(ContentNegotiatedMethodView):
    """
    Class that handles temporary access tokens for files of a record.
    """
    view_name = '{0}_tempfileaccess'

    def __init__(self, resolver=None, **kwargs):
        """Constructor."""
        super(TempFileAccessTokenResource, self).__init__(
            default_method_media_type={
                'GET': 'application/json'
            },
            default_media_type='application/json',
            **kwargs)

    @auth_required('token', 'session')
    @pass_record
    def get(self, record, *args, **kwargs):
        """
        Generate a temporary JWT for anonymous read access to files of a record.
        Expiration for a JWT is 30 days from current UTC timestamp 
        at the time of token generation.
        """
        # Check that user has required permissions to
        # create a temporary access token.
        # Rationale: If user can edit a published record
        # he/she can surely generate access token to read files.
        # (only owner of record is authorized to edit published record)
        verify_record_permission(UpdateRecordPermission, record)

        # Get bucket of record
        bucket = Bucket.query.join(RecordsBuckets).\
            filter(RecordsBuckets.bucket_id == Bucket.id,
                   RecordsBuckets.record_id == record.id).first()

        # Generate JWT, sign with app.secret_key
        # Default exp is 30 days from current UTC timestamp
        # at the time of token generation

        expiry_time_in_days = int(request.args.get('days',30))
        expiry_time_in_minutes = int(request.args.get('minutes',0))
        iat = datetime.datetime.utcnow()
        exp = datetime.datetime.utcnow() + \
            + datetime.timedelta(days=expiry_time_in_days,minutes=expiry_time_in_minutes)

        payload = {'bucket_id': str(bucket.id),
                   'action': 'read',
                   'iat': iat,
                   'exp': exp,
                   'jti': str(uuid.uuid4())}

        encoded_jwt = jwt.encode(
            payload, current_app.secret_key, algorithm="HS256")

        # Return token to requester as JSON.
        return jsonify({"jwt": encoded_jwt, "expiration":exp})
