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

"""Serializer for b2share => Metax harvesting"""

from b2share.modules.communities.api import Community
from flask import current_app
from .licenses import licenses

from invenio_pidrelations.contrib.versioning import PIDVersioning
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_files.api import Record

ETSIN_URL = 'https://etsin.demo.fairdata.fi'

def _get_id_type_identifier(identifier_type):
    if not identifier_type in ['EISSN', 'Handle', 'ISBN', 'ISSN', 'LISSN', 'LSID', 'PMID', 'UPC', 'wi3d']:
        return "http://uri.suomi.fi/codelist/fairdata/identifier_type/code/"+identifier_type.lower()

def _get_identifier(rec, id_type):
    for i in rec.get("_pid", []):
        if i.get('type') == id_type:
            return i

def get_doi(rec):
    return _get_identifier(rec, "DOI")

def get_b2rec_id(rec):
    return _get_identifier(rec, "b2rec")

def get_epic_pid(rec):
    return _get_identifier(rec, "ePIC_PID")

def get_preferred_identifier(rec):
    identifier = get_doi(rec)
    #Add doi prefix based on app configuration
    identifier_type = current_app.config.get('METAX_DOI_PREFIX')
    if not identifier:
        identifier = get_epic_pid(rec)
        identifier_type = 'ePIC_PID:'
    return identifier_type + identifier['value']

def get_other_identifier(rec):
    ret = []
    pid = get_epic_pid(rec)
    if pid:
        ret.append({
            "notation": pid['value']
            # TODO other fields
        })
    for a in rec.get('alternate_identifiers', []):
        if a['alternate_identifier'].startswith('https://etsin'):
            continue
        alt = {
            "notation": a['alternate_identifier']
        }
        id_type = _get_id_type_identifier(a['alternate_identifier_type'])
        if id_type:
            alt['type'] = {
                'identifier': id_type
            }
        ret.append(alt)
    return ret

def get_community_name(rec):
    c = Community.get(id=rec.get('community').replace('-' , ''))
    return c.name

def get_title(rec):
    return {'en': rec['titles'][0]['title']}

def get_description(rec):
    descriptions = rec.get('descriptions', [])
    for d in descriptions:
        if d.get('description_type') == 'Abstract':
            return {"en": d['description']}
    return {"en": descriptions[0]['description']}

def get_org_id(org_name):
    if org_name == "Finnish Meteorological Institute" or not org_name:
        return "http://uri.suomi.fi/codelist/fairdata/organization/code/4940015" # FMI
    return None

def get_member_of(creator):
    try:
        if get_org_id(creator.get('affiliations',[])[0]\
                .get('affiliation_name')):
            return {
                "@type": "Organization",
                "identifier": get_org_id(creator.get('affiliations',[])[0]\
                    .get('affiliation_name'))
            }
        else:
            return {
                "@type": "Organization",
                "name": {"en": creator.get('affiliations',[])[0].get('affiliation_name')}
            }
    except:
        return None

def get_creator(rec):
    ret = []
    for c in rec.get('creators', []):
        creator = {
            "@type": "Organization" if c.get("name_type") == "Organizational" else "Person",
        }
        if c.get('name_type') == "Organizational":
            if get_org_id(c['creator_name']):
                creator["identifier"] = get_org_id(c['creator_name'])
            else:
                creator['name'] = {"en": c["creator_name"]}
        else:
            creator["name"] = c["creator_name"]
            if get_member_of(c):
                creator["member_of"] = get_member_of(c)
        ret.append(creator)
    return ret

def get_embargo_date(rec):
    dt = rec.get('embargo_date')
    if not dt:
        return None
    return dt.split('T')[0]

def get_access_rights(rec):
    if rec.get('open_access'):
        return {
            "access_type": {
                "in_scheme": "http://uri.suomi.fi/codelist/fairdata/access_type",
                "identifier": "http://uri.suomi.fi/codelist/fairdata/access_type/code/open",
                "pref_label": {
                        "en": "Open",
                        "fi": "Avoin",
                        "und": "Avoin"
                    },
                },
                "license": get_license(rec)
            }
    elif rec.get('embargo_date'):
        return {
            "access_type": {
                "in_scheme": "http://uri.suomi.fi/codelist/fairdata/access_type",
                "identifier": "http://uri.suomi.fi/codelist/fairdata/access_type/code/embargo",
                "pref_label": {
                        "en": "Embargo",
                        "fi": "Embargo",
                        "und": "Embargo"
                    },
                },
                "license": get_license(rec),
                "available": get_embargo_date(rec)
            }
    else:
        return {
            "access_type": {
                "in_scheme": "http://uri.suomi.fi/codelist/fairdata/access_type",
                "identifier": "http://uri.suomi.fi/codelist/fairdata/access_type/code/restricted",
                "pref_label": {
                    "en": "Restricted use",
                    "fi": "Saatavuutta rajoitettu",
                    "und": "Saatavuutta rajoitettu"
                }
            },
            "license": get_license(rec)
        }

def get_issued(record):
    if record.get('publication_date'):
        return record['publication_date'].split('T')[0]

def get_field_of_science(record):
    disciplines = record.get('disciplines', [])
    if disciplines:
        for d in disciplines:
            if isinstance(d, str):
                return []
            if d.get('discipline_identifier') == "3.3.2 → Earth sciences → Environmental science":
                return [
                    {
                        "in_scheme": "http://www.yso.fi/onto/okm-tieteenala/conceptscheme",
                        "identifier": "http://www.yso.fi/onto/okm-tieteenala/ta{}".format(1171),
                    }
                ]
    return []

def get_keyword(record):
    ret = list(map(lambda o: o.get('keyword'), record.get('keywords', [])))
    ret.append('INSPIRE theme: {}'.format(get_community_specific(record)['topic']))
    return ret

def get_license(record):
    l = record.get("license")
    ret = []
    if l:
        if l.get('license_uri') in licenses:
            ret.append({'identifier': licenses[l.get('license_uri')]})
        else:
            ret.append({
                "license": l.get('license_uri')
            })
    return ret

def get_contributor(record):
    ret = []
    for c in record.get('contributors', []):
        if not c['contributor_type'] in ['DataCurator', 'RightsHolder']:
            contributor = {
                "@type": "Organization" if c.get("name_type") == "Organizational" else "Person",
            }
            if c.get('name_type') == "Organizational":
                if get_org_id(c['contributor_name']):
                    contributor["identifier"] = get_org_id(c['contributor_name'])
                else:
                    contributor['name'] = {"en":c['contributor_name']}
            else:
                contributor["name"] = c["contributor_name"]
                if get_member_of(c):
                    contributor["member_of"] = get_member_of(c)
            ret.append(contributor)
    return ret

def get_curator(record):
    ret = []
    for c in record.get('contributors', []):
        if c['contributor_type'] == 'DataCurator':
            contributor = {
                "@type": "Organization" if c.get("name_type") == "Organizational" else "Person",
            }
            if c.get('name_type') == "Organizational":
                if get_org_id(c['contributor_name']):
                    contributor["identifier"] = get_org_id(c['contributor_name'])
                else:
                    contributor['name'] = {"en":c["contributor_name"]}
            else:
                contributor["name"] = c["contributor_name"]
                if get_member_of(c):
                    contributor["member_of"] = get_member_of(c)
            ret.append(contributor)
    return ret

def get_rights_holder(record):
    ret = []
    for c in record.get('contributors', []):
        if c['contributor_type'] == 'RightsHolder':
            contributor = {
                "@type": "Organization" if c.get("name_type") == "Organizational" else "Person",
            }
            if c.get('name_type') == "Organizational":
                if get_org_id(c['contributor_name']):
                    contributor["identifier"] = get_org_id(c['contributor_name'])
                else:
                    contributor['name'] = {"en":c['contributor_name']}
            else:
                contributor["name"] = c["contributor_name"],
                if get_member_of(c):
                    contributor["member_of"] = get_member_of(c)
            ret.append(contributor)
    return ret

def get_language(record):
    ret = []
    for lang in record.get('languages', []):
        ret.append({"identifier": "http://lexvo.org/id/iso639-3/{}".format(lang['language_identifier'])})
    return ret

def get_spatial(record):
    ret = []
    for s in record.get('spatial_coverages', []):
        spatial = {}
        if s.get('place'):
            spatial['geographic_name'] = s['place']
        if s.get('point'):
            spatial["as_wkt"] = []
            spatial['as_wkt'].append("POINT({} {})".format(s['point']['point_longitude'], s['point']['point_latitude']))
        if s.get('box'):
            box = s['box']
            spatial["as_wkt"] = []
            spatial['as_wkt'].append("POLYGON(({} {}, {} {}, {} {}, {} {}))".format(\
                box['westbound_longitude'], box['northbound_latitude'],
                box['eastbound_longitude'], box['northbound_latitude'],
                box['eastbound_longitude'], box['southbound_latitude'],
                box['westbound_longitude'], box['southbound_latitude']
            ))
        if s.get('polygons'):
            # Map B2SHARE polygons to metax wkt like this:
            # B2SHARE-spatial_coverages-polygons => MULTIPOLYGON(((Polygon1)),((Polygon2)))
            # On the next spatial_coverage we create new MULTIPOLYGON, if polygons exists
            spatial["as_wkt"] = []
            poly_array = []
            for poly in s['polygons']:
                poly_array.append(", ".join(["{} {}".format(p['point_longitude'], p['point_latitude'])\
                    for p in poly['polygon']]))
            spatial['as_wkt'].append("MULTIPOLYGON((({})))".format(\
                ")), ((".join(["{}".format(p)\
                    for p in poly_array])
            ))
        ret.append(spatial)
    return ret

def get_temporal(record):
    ret = []
    for t in record.get('temporal_coverages', {}).get('ranges', []):
        ret.append(t)
    return ret

def get_remote_resources(record):
    ret = []
    # record_url = make_record_url(get_b2rec_id(record)['value'])
    record_url = 'https://dev.fmi.b2share.csc.fi/records/' + get_b2rec_id(record)['value']
    for f in record.get('_files', []):
        ret.append({
            'title': f['key'],
            'access_url': {
                'identifier': record_url
            },
            'download_url': {
                'identifier': f['ePIC_PID']
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
    if not get_community_specific(record).get('external_url'):
        return ret
    for url in get_community_specific(record).get('external_url'):
        ret.append({
            "title": "External data",
            "download_url":{
                "identifier": url
            },
            "use_category":{
                "in_scheme":"http://uri.suomi.fi/codelist/fairdata/use_category",
                "identifier":"http://uri.suomi.fi/codelist/fairdata/use_category/code/outcome",
                "pref_label":{
                    "en":"Outcome material",
                    "fi":"Tulosaineisto","und":"Tulosaineisto"
                }
            }
        })
    return ret

def get_koko_number(topic):
    return {
        'climatologyMeteorologyAtmosphere': 69567,
        'oceans': 31108,
        'society': 34895,
        'economy': 48204,
        'environment': 72019,
        'transportation': 7285,
        'geoscientificInformation': 31387, # geophysics - is this ok?
        'space physics': 14358 # space - is this ok?
    }[topic]

def get_community_specific(record):
    return list(record.get('community_specific').values())[0]

def get_theme(record):
    # DMO commented, that record topics should not be mapped to KOKO ontologies.
    return [{
        "in_scheme": "http://www.yso.fi/onto/koko/",
        "identifier": "http://www.yso.fi/onto/koko/p{}"\
        .format(\
            get_koko_number(\
                get_community_specific(record)['topic']
        ))
    }]

def _get_relation_type(related_identifier):
    return {
        "IsSupplementTo": "http://purl.org/vocab/frbr/core#isSupplementTo",
        "IsPartOf": "http://purl.org/dc/terms/isPartOf",
        "isCompiledBy": "http://purl.org/spar/cito/isCompiledBy",
        "IsIdenticalTo": "http://www.w3.org/2002/07/owl#sameAs",
        "IsCitedBy": "http://purl.org/spar/cito/isCitedBy",
        "Continues": "http://purl.org/vocab/frbr/core#successorOf",
        "IsPreviousVersionOf": "http://www.w3.org/ns/adms#next",
        "IsNewVersionOf": "http://www.w3.org/ns/adms#previous"
    }.get(related_identifier['relation_type'], "http://purl.org/dc/terms/relation")

def get_relation(record):
    ret = []
    for ri in record.get('related_identifiers', []):
        if not ETSIN_URL in ri['related_identifier']:
            # TODO: Check this
            ret.append({
                "entity": {
                    "identifier": ri['related_identifier'],
                    # "title": ""
                    # "description": ""
                    # "type": "" 
                },
                "relation_type": {
                    "identifier": _get_relation_type(ri)
                }
            })
    pid_str = get_b2rec_id(record).get('value')
    pid = PersistentIdentifier.get('b2rec', pid_str)
    pid_versioning = PIDVersioning(child=pid)
    if pid_versioning.next:
        ret.append({
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
                "identifier": get_preferred_identifier(Record.get_record(pid_versioning.next.object_uuid))
            },
            "relation_type": {
                "identifier": "http://www.w3.org/ns/adms#next",
                "pref_label": {
                    "fi": "Seuraava versio",
                    "en": "Has next version"
                }
            }
        })
    if pid_versioning.previous:
        ret.append({
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
                "identifier": get_preferred_identifier(Record.get_record(pid_versioning.previous.object_uuid))
            },
            "relation_type": {
                "identifier": "http://www.w3.org/ns/adms#previous",
                "pref_label": {
                    "fi": "Edellinen versio",
                    "en": "Has previous version"
                }
            }
        })
    return ret

def get_project(record):
    ret = []
    if record.get('funding_references', None):
        funders = []
        for f in record.get('funding_references'):
            obj = {}
            obj['name'] = { "en": f.get('funder_name') }
            obj['@type'] = 'Organization'
            funders.append(obj)

        r = {
            "name": get_title(record),
            "has_funding_agency": funders,
            "source_organization": [{
                "@type": "Organization",
                "identifier": get_org_id(record.get('publisher'))
            }]
        }
        ret.append(r)
    
    return ret

def get_publisher(pub):
    if not get_org_id(pub):
        return {
            "@type": "Organization",
            "name": {"en":pub}
        }
    return {
        "@type": "Organization",
        "identifier": get_org_id(pub)
    }

def serialize_to_metax(record, catalog):
    """Serialize B2SHARE record to Metax JSON
    """
    research_dataset = {
            "preferred_identifier": get_preferred_identifier(record),
            "other_identifier": get_other_identifier(record),
            "title": get_title(record),
            "description": get_description(record),
            "creator": get_creator(record),
            "publisher": get_publisher(record.get('publisher')),
            "field_of_science": get_field_of_science(record),
            "keyword": get_keyword(record),
            "issued": get_issued(record),
            "contributor": get_contributor(record),
            "language": get_language(record),
            "spatial": get_spatial(record),
            "temporal": get_temporal(record),
            "relation": get_relation(record),
            "remote_resources": get_remote_resources(record),
            #"theme": get_theme(record),
            "access_rights": get_access_rights(record),
            "is_output_of": get_project(record),
            "curator": get_curator(record),
            "rights_holder": get_rights_holder(record)
        }
    serialized = {
        "data_catalog": catalog,
        "available": get_embargo_date(record),
        "metadata_owner_org": '{}.fi'.format(get_community_name(record)),
        "metadata_provider_org": '{}.fi'.format(get_community_name(record)),
        "metadata_provider_user": get_community_name(record),
        "research_dataset": {k:v for k,v in research_dataset.items() if v}
    }
    return serialized
