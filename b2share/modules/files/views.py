# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2017 CERN.
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

"""B2Share Files views."""

from __future__ import absolute_import
from typing_extensions import Required
import jwt
from zipstream import ZipStream, ZIP_STORED
from fs.opener import opener


from flask import Blueprint, abort, request, jsonify, current_app, Response
from flask_login import current_user
from flask import Response

from invenio_files_rest.views import ObjectResource, pass_bucket, invalid_subresource_validator
from invenio_files_rest.serializer import json_serializer
from invenio_files_rest.models import ObjectVersion
from invenio_files_rest.signals import file_downloaded
from webargs import fields
from webargs.flaskparser import use_kwargs

from b2handle.handleclient import EUDATHandleClient

# don't register blueprint instead of replace the object_view
# .ext.replace_files_rest_object_view()
# blueprint_b2share_files_rest = Blueprint(
#     'b2share_files_rest', __name__, url_prefix='/files')


class B2ShareObjectResource(ObjectResource):
    """Class for b2share files rest."""
    view_name = 'b2share_files_rest'

    get_args = {
        'version_id': fields.UUID(
            location='query',
            load_from='versionId',
            missing=None,
        ),
        'download_all': fields.Bool(
            location='query',
            load_from='all',
            missing=False,
        ),
        'encoded_jwt': fields.Str(
            location='query',
            load_from='jwt',
            missing=None,
        ),
        'upload_id': fields.UUID(
            location='query',
            load_from='uploadId',
            missing=None,
        ),
        'uploads': fields.Raw(
            location='query',
            validate=invalid_subresource_validator,
        ),
    }

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(B2ShareObjectResource, self).__init__(*args, **kwargs)

    @classmethod
    def get_object(cls, bucket, key, version_id, encoded_jwt=None):
        """Retrieve object and abort if it doesn't exists.

        If the file is not found, the connection is aborted and the 404
        error is returned.

        :param bucket: The bucket (instance or id) to get the object from.
        :param key: The file key.
        :param version_id: The version ID.
        :returns: A :class:`invenio_files_rest.models.ObjectVersion` instance.
        """

        obj = ObjectVersion.get(bucket, key, version_id=version_id)
        if not obj:
            abort(404, 'Object does not exists.')

        if encoded_jwt:
            try:
                decoded_jwt = jwt.decode(encoded_jwt, current_app.secret_key, algorithms=[
                                         "HS256"], options={'require': ['exp', 'jti', 'iat', 'sub', 'bucket_id']})
            except jwt.exceptions.InvalidTokenError:
                abort(400, 'The provided token is malformed or otherwise invalid')
            # NTS: Maybe bucket has bucket.id or something to avoid typecasting
            if not decoded_jwt.get('bucket_id') == str(bucket):
                if current_user.is_authenticated:
                    cls.check_object_permission(obj)
                else:
                    abort(404, 'Object does not exists.')
        else:
            cls.check_object_permission(obj)

        return obj

    @classmethod
    def create_zip_object(cls, objs):
        """Fetch files uri and return a flsk response.
 
        :param objs: list of invenio_files_rest.models.ObjectVersion instances
        :returns: A flask response
        """

        # zip_streamer = zipstream.ZipFile()
        # for file_instance in objs:
        #     print(file_instance.basename)
        #     zip_streamer.write_iter(file_instance.basename, opener.open(
        #         file_instance.file.uri, mode='rb'))

        name = 'files'
        zs = ZipStream(compress_type=ZIP_STORED, sized=True)

        for file_instance in objs:
            zs.add(opener.open(file_instance.file.uri,
                   mode='rb'), file_instance.basename)

        return Response(
            zs,
            mimetype="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={name}.zip",
                #"Content-Length": len(zs),
                "Last-Modified": zs.last_modified,
            }
        )

    @classmethod
    def get_bucket_objects(cls, bucket, key, version_id, encoded_jwt=None):
        """Retrieve multiple object and return a zip file.

        If no files are found, the connection is aborted and the 404
        error is returned.

        :param bucket: The bucket (instance or id) to get the object from.
        :param key: The file key.
        :param version_id: The version ID.
        :returns: A :class:`invenio_files_rest.models.ObjectVersion` instance.
        """

        objs = ObjectVersion.get_by_bucket(bucket).all()
        if len(objs) == 0:
            abort(404, 'No objects found.')

        if encoded_jwt:
            try:
                decoded_jwt = jwt.decode(encoded_jwt, current_app.secret_key, algorithms=[
                                         "HS256"], options={'require': ['exp', 'jti', 'iat', 'sub', 'bucket_id']})
            except jwt.exceptions.InvalidTokenError:
                abort(400, 'The provided token is malformed or otherwise invalid')
            # NTS: Maybe bucket has bucket.id or something to avoid typecasting
            if not decoded_jwt.get('bucket_id') == str(bucket):
                if current_user.is_authenticated:
                    for obj in objs:
                        cls.check_object_permission(obj)
                else:
                    abort(404, 'Object does not exists.')
        else:
            for obj in objs:
                cls.check_object_permission(obj)

        respo = cls.create_zip_object(objs)

        # send signal to invenio-stats for each file
        for obj in objs:
            file_downloaded.send(current_app._get_current_object(), obj=obj)
        return respo


#     #
#     # HTTP methods implementations
#     #


    @use_kwargs(get_args)
    @pass_bucket
    def get(self, bucket=None, key=None, version_id=None, upload_id=None,
            uploads=None, encoded_jwt=None, download_all=False):
        """Get object or list parts of a multpart upload.

        :param bucket: The bucket (instance or id) to get the object from.
            (Default: ``None``)
        :param key: The file key. (Default: ``None``)
        :param version_id: The version ID. (Default: ``None``)
        :param upload_id: The upload ID. (Default: ``None``)
        :returns: A Flask response.
        """
        if upload_id:
            return self.multipart_listparts(bucket, key, upload_id)
        else:
            # if download_all:
            #     resp = self.get_bucket_objects(
            #         bucket, key, version_id, encoded_jwt)
            # else:
            #     obj = self.get_object(bucket, key, version_id, encoded_jwt)
            #     # Note: in release: v1.0.0a21 is not possible to force download from BE with as_attachment=True
            #     resp = self.send_object(bucket, obj)

            # comment out the zip because it needs more testing
            obj = self.get_object(bucket, key, version_id, encoded_jwt)
            resp = self.send_object(bucket, obj)

        resp.headers['Content-Type'] = 'application/force-download'
        return resp


object_view = B2ShareObjectResource.as_view(
    'b2share_object_api',
    serializers={
        'application/json': json_serializer,
    }
)

# don't register blueprint instead of replace the object_view
# .ext.replace_files_rest_object_view()
# blueprint_b2share_files_rest.add_url_rule(
#     '/<string:bucket_id>/<path:key>',
#     view_func=object_view,
# )
