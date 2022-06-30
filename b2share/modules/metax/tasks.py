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

"""Celery background tasks"""
from celery import shared_task
from flask import current_app
from .api import metax_publish, is_published_in_metax, metax_update_metadata
from b2share.modules.records.utils import list_db_published_records
from .serializer import get_b2rec_id

@shared_task(ignore_result=True)
def publish_to_metax():
    """Publish record to metax"""
    if not current_app.config.get('ENABLE_METAX'):
        return
    logger = current_app.logger
    for record in list_db_published_records():
        if not is_published_in_metax(record):
            if metax_publish(record):
                logger.info('Published record {} to metax'.format(get_b2rec_id(record)))
            else:
                logger.warning('Error publishing record {} to metax'.format(get_b2rec_id(record)))

@shared_task(ignore_result=True)
def update_metax(record):
    """Update record on metax"""
    if not current_app.config.get('ENABLE_METAX'):
        return
    logger = current_app.logger
    if metax_update_metadata(record):
        logger.info('Record {} metadata updated to metax'.format(get_b2rec_id(record)))
    else:
        logger.warning('Error updating record {} to metax'.format(get_b2rec_id(record)))

@shared_task(ignore_result=True)
def update_all_metax():
    """Update all records metax"""
    if not current_app.config.get('ENABLE_METAX'):
        return
    logger = current_app.logger
    for record in list_db_published_records():
        if metax_update_metadata(record):
            logger.info('Record {} metadata updated to metax'.format(get_b2rec_id(record)))
        else:
            logger.warning('Error updating record {} to metax'.format(get_b2rec_id(record)))
