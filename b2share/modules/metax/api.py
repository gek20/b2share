# -*- coding: utf-8 -*-
#
# This file is part of EUDAT B2Share.
# Copyright (C) 2016 CERN, University of Tuebingen.
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

from .serializer import serialize_to_metax, get_b2rec_id
from flask import current_app
import requests
from invenio_db import db
from b2share.utils import get_base_url

from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_files.api import Record

"""B2SHARE Metax publishing api"""

def is_published_in_metax(record):
    """Helper to check if record has been published to metax."""
    return any(
        altid['alternate_identifier'].startswith('https://etsin') for altid in record.get('alternate_identifiers', [])
    )

def get_record_metax_identifier(rec):
    """Get metax identifier from record"""
    if not rec:
        return None
    for a in rec.get('alternate_identifiers', []):
        if a['alternate_identifier'].startswith('https://etsin'):
            identifier = a['alternate_identifier'].split('/')[-1]
            return identifier
        else:
            continue

def metax_update_metadata(record):
    """Update already harvested records metadata to metax"""
    logger = current_app.logger
    try:
        json = serialize_to_metax(record, current_app.config.get('METAX_API_CATALOG'))
    except:
        return False
    auth = (current_app.config.get('METAX_API_USERNAME'), current_app.config.get('METAX_API_PASSWORD'))
    url_identifier = get_record_metax_identifier(record)
    if not url_identifier:
        return False
    try:
        response = requests.patch(current_app.config.get('METAX_API_URL')+'/'+url_identifier, json=json, auth=auth)
        response_json = response.json()
        response_code = response.status_code
        if response_json and response_code == 200:
            return True
        # No retry if problem in serializer
        if response_code == 400:
            logger.warning('HTTP error from Metax: {}'.format(response_json))
            return False
    except requests.exceptions.RequestException as e:
        logger.warning('Received error from metax: {}'.format(e))
    # Retry update after 15 minutes
    # Import here to prevent circular import error
    from b2share.modules.metax.tasks import update_metax
    update_metax.apply_async(record, countdown=900)
    logger.warning('Update rescheduled for record: {}'.format(get_b2rec_id(record)))
    return False

def metax_publish(record):
    """
    Publish the record in Metax and add a relatedIdentifier to it to mark publication
    """
    try:
        json = serialize_to_metax(record, current_app.config.get('METAX_API_CATALOG'))
    except:
        return False
    auth = (current_app.config.get('METAX_API_USERNAME'), current_app.config.get('METAX_API_PASSWORD'))
    response = requests.post(current_app.config.get('METAX_API_URL'), json=json, auth=auth)
    response_json = response.json()
    if response_json:
        identifier = response.json().get('identifier')
        if identifier:
            if not record.get('alternate_identifiers'):
                record['alternate_identifiers'] = []
            record['alternate_identifiers'].append(
                {
                    'alternate_identifier': current_app.config.get('METAX_PUBLISH_PREFIX') + identifier,
                    'alternate_identifier_type': 'URL'
                }
            )
            # Because this is run on CLI or Celery context
            with current_app.test_request_context('/', base_url=get_base_url()):
                record.commit()
                db.session.commit()
            # Update older version of the record, if this is a new version.
            pid_str = get_b2rec_id(record).get('value')
            pid = PersistentIdentifier.get('b2rec', pid_str)
            pid_versioning = PIDVersioning(child=pid)
            if pid_versioning.previous:
                previous_record = Record.get_record(pid_versioning.previous.object_uuid)
                metax_update_metadata(previous_record)
            return True
    return False
    