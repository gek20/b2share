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

"""B2Share demo helpers."""

from __future__ import absolute_import, print_function

import json
import os
import re
import uuid
from collections import namedtuple
from uuid import UUID

import click
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_records.api import Record

from b2share.modules.communities import Community
from b2share.modules.schemas import BlockSchema, CommunitySchema
from b2share.modules.schemas.helpers import resolve_schemas_ref
from b2share.modules.records.providers import RecordUUIDProvider

def load_demo_data(path, verbose=0):
    """Load a demonstration located at the given path.

    Args:
        path (str): path of the directory containing the demonstration data.
        verbose (int): verbosity level.
    """
    with db.session.begin_nested():
        communities = _create_communities(path, verbose)
        block_schemas = _create_block_schemas(communities, verbose)
        _create_community_schemas(communities, block_schemas, verbose)
        _create_records(path, verbose)


DemoCommunity = namedtuple('DemoCommunity', ['ref', 'config'])


def _create_communities(path, verbose):
    """Create demo communities."""
    if verbose > 0:
        click.secho('Creating communities', fg='yellow', bold=True)
    with db.session.begin_nested():
        communities_dir = os.path.join(path, 'communities')
        communities = dict()
        nb_communities = 0
        for filename in sorted(os.listdir(communities_dir)):
            if os.path.splitext(filename)[1] == '.json':
                with open(os.path.join(communities_dir,
                                       filename)) as json_file:
                    json_config = json.loads(json_file.read())
                    community = Community.create_community(
                        name=json_config['name'],
                        description=json_config['description'],
                        id_=UUID(json_config['id']),
                    )
                    if verbose > 1:
                        click.secho('Created community {0} with ID {1}'.format(
                            community.name, community.id
                        ))
                    communities[community.name] = DemoCommunity(community,
                                                                json_config)
                    nb_communities += 1
    if verbose > 0:
        click.secho('Created {} communities!'.format(nb_communities),
                    fg='green')
    return communities


def _create_block_schemas(communities, verbose):
    """Create demo block schemas."""
    if verbose > 0:
        click.secho('Creating block schemas', fg='yellow', bold=True)
    nb_block_schemas = 0
    with db.session.begin_nested():
        for community in communities.values():
            for schema_name, schema in community.config[
                    'block_schemas'].items():
                block_schema = BlockSchema.create_block_schema(
                    community.ref.id,
                    schema_name,
                    id_=UUID(schema['id']),
                )
                for json_schema in schema['versions']:
                    block_schema.create_version(json_schema)
                nb_block_schemas += 1
    if verbose > 0:
        click.secho('Created {} block schemas!'.format(nb_block_schemas),
                    fg='green')


def _create_community_schemas(communities, block_schemas, verbose):
    """Create demo community schemas."""
    if verbose > 0:
        click.secho('Creating community schemas', fg='yellow', bold=True)
    with db.session.begin_nested():
        for community in communities.values():
            for schema in community.config['community_schemas']:
                json_schema_str = json.dumps(schema['json_schema'])
                # expand variables in the json schema
                json_schema_str = resolve_block_schema_id(json_schema_str)
                json_schema_str = resolve_schemas_ref(json_schema_str)
                CommunitySchema.create_version(
                    community_id=community.ref.id,
                    community_schema=json.loads(json_schema_str),
                    root_schema_version=int(schema['root_schema_version']))
    if verbose > 0:
        click.secho('Created all community schemas!', fg='green')


def _create_records(path, verbose):
    """Create demo records."""
    if verbose > 0:
        click.secho('Creating records', fg='yellow', bold=True)
    with db.session.begin_nested():
        records_dir = os.path.join(path, 'records')
        nb_records = 0
        for root, dirs, files in os.walk(records_dir):
            for filename in files:
                split_filename = os.path.splitext(filename)
                if split_filename[1] == '.json':
                    rec_uuid = UUID(split_filename[0])
                    with open(os.path.join(records_dir, root,
                                           filename)) as record_file:
                        record_str = record_file.read()
                    record_str = resolve_community_id(record_str)
                    record_str = resolve_block_schema_id(record_str)
                    provider = RecordUUIDProvider.create(
                        object_type='rec', object_uuid=rec_uuid)
                    Record.create(json.loads(record_str), id_=rec_uuid)
                    if verbose > 1:
                        click.secho('CREATED RECORD {0}:\n {1}'.format(
                            str(rec_uuid), json.dumps(json.loads(record_str),
                                                  indent=4)
                        ))
                    nb_records += 1
    if verbose > 0:
        click.secho('Created {} records!'.format(nb_records), fg='green')


def resolve_block_schema_id(source):
    """Resolve all references to Block Schema and replace them with their ID.

    Every instance of '$BLOCK_SCHEMA_ID[<schema_name>]' will be replaced with
    the corresponding ID.

    Args:
        source (str): the source string to transform.

    Returns:
        str: a copy of source with the references replaced.
    """
    def block_schema_ref_match(match):
        name = match.group(1)
        found_schemas = BlockSchema.get_all_block_schemas(name=name)
        if len(found_schemas) > 1:
            raise Exception(
                'Too many schemas matching name "{}".'.format(name))
        elif len(found_schemas) == 0:
            raise Exception('No schema matching name "{}" found.'.format(name))
        return found_schemas[0]
    return re.sub(
        r'\$BLOCK_SCHEMA_ID\[([^\]:]+)\]',
        lambda m: str(block_schema_ref_match(m).id),
        source
    )


def resolve_community_id(source):
    """Resolve all references to Community and replace them with their ID.

    Every instance of '$COMMUNITY_ID[<community_name>]' will be replaced with
    the corresponding ID.

    Args:
        source (str): the source string to transform.

    Returns:
        str: a copy of source with the references replaced.
    """
    def community_id_match(match):
        community_name = match.group(1)
        community = Community.get(name=community_name)
        return str(community.id)
    return re.sub(
        r'\$COMMUNITY_ID\[([^\]]+)\]',
        community_id_match,
        source
    )