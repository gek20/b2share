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

"""B2Share cli commands for metax harvesting."""


from __future__ import absolute_import, print_function

import click
from flask.cli import with_appcontext
from .tasks import update_metax, publish_to_metax, update_all_metax
from .api import metax_publish
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_files.api import Record

@click.group()
def metax():
    """Metax harvesting commands"""

@metax.command()
@with_appcontext
def harvest_new():
    """Harvest all not harvested records and versions to Metax."""
    publish_to_metax.delay()
    click.echo("Harvesting has been queued")

@metax.command()
@with_appcontext
@click.argument('record_id', required=False, default=None)
@click.option('-a', '--all', is_flag=True, default=False)
def update(record_id, all):
    """Update records data to Metax."""
    if record_id:
        pid = PersistentIdentifier.get('b2rec', record_id)
        record = Record.get_record(pid.object_uuid)
        update_metax.delay(record)
        click.echo("Update to metax of record {} has been queued".format(record_id))
    elif all:
        update_all_metax.delay()
        click.echo("Update to metax of all records has been queued")
    else:
        raise click.ClickException("At least --all / -a flag or record_id has to be specified")

@metax.command()
@with_appcontext
@click.argument('record_id')
def harvest(record_id):
    """Harvest record based on record_id to metax. Not asyncronous"""
    pid = PersistentIdentifier.get('b2rec', record_id)
    record = Record.get_record(pid.object_uuid)
    if metax_publish(record):
        click.echo("Record {} has been harvested".format(record_id))
    else:
        click.echo("Error occured when harvesting record {} to metax".format(record_id))
