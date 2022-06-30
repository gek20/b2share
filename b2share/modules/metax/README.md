# Mapping to Metax

Metax object:

```json
{
    "data_catalog": "Provided data catalog",
    "available": "record.embargo_date (only ymd)",
    "metadata_owner_org": "community_name.fi",
    "metadata_provider_org": "community_name.fi",
    "metadata_provider_user": "community_name",
    "research_dataset": {
        "preferred_identifier": "Either DOI or ePIC_PID. DOI Preferred",
        "other_identifier": [
            // ePIC_PID added as:
            {
                "notation":"ePIC_PID"
            }, 
            // For record.alternate_identifiers, skip etsin identifiers
            {
                "notation": "alternate_identifiers.alternate_identifier",
                "identifier": "alternate_identifiers.alternate_identifier_type"
            }
        ],
        "title": {
            "en": "record.titles.0.title"
        },
        "description": {
            "en": "descriptions.0.description OR descriptions.description(where description_type == abstract)(preferred)"
        },
        // @type from b2share creator field "name_type"
        "creator": [
            // For record.creators
            {
                "@type": "Person", 
                "name": "creators.creator_name", 
                "member_of": {
                    "@type": "Organization", 
                    "identifier": "uri.suomi.fi for FMI"
                }
            }, 
            {
                "@type": "Organization", 
                "identifier": "uri.suomi.fi for FMI"
            }
        ],
        "publisher": {
            "@type": "Organization",
            "identifier": "uri.suomi.fi for FMI"
        },
        // from b2share disciplines, 0-1 objects returned
        "field_of_science": [
            {
                "in_scheme": "http://www.yso.fi/onto/okm-tieteenala/conceptscheme", 
                "identifier":"yso.fi ontology for discipline"
            }
        ],
        "keyword": [
            // For record.keywords
            "record.keywords.keyword",
            // INSPIRE theme added
            "INSPIRE theme: record.community_specific.0.topic"
        ],
        "issued": "record.publication_date (only year month day)",
        // From contributors, if contributor type not DataCurator or RightsHolder
        "contributor": [
            // For record.contributors
            {
                "@type": "Person", 
                "name": "record.contributors.contributor_name", 
                "member_of": {
                    "@type": "Organization", 
                    "identifier": "uri.suomi.fi for FMI"
                }
            }, 
            {
                "@type": "Organization", 
                "identifier": "uri.suomi.fi for FMI"
            }
        ],
        "language": [
            // For record.languages
            {
                "identifier": "lexvo.org identifier based on record.languages.language_identifier"
            }
        ],
        "spatial": [
            // For record.spatial_coverages
            { // Point
                "geographical_name": "place", // If defined
                "as_wkt": ["POINT(point.longitude point.latitude)"]
            },
            { // Box
                "geographical_name": "place", // If defined
                "as_wkt": ["POLYGON((west_lon north_lat, east_lon north_lat, east_lon south_lat, west_lon south_lat))"]
            },
            { // Polygon
                "geographical_name": "place", // If defined
                "as_wkt": ["MULTIPOLYGON(((pol1_point1_lon pol1_point1_lat, pol1_point2_lon pol1_point2_lat, pol1_point3_lon pol1_point3_lat)), 
                            ((pol2_point1_lon pol2_point1_lat, pol2_point2_lon pol2_point2_lat, pol2_point3_lon pol2_point3_lat)))"] 
                            // Check multipolygon from wikipedia :)
                            // One Multipolygon contains all polygons defined in one spatial_coverage
            }, 
            { // If only place defined
                "geographical_name": "place"
            }
        ],
        "temporal": [
            // For B2SHARE temporal_coverages.ranges
            {
                "start_date": "start_date", 
                "end_date": "end_date"
            } // temporal_coverages.ranges[i].start_date/end_date
        ],
        "relation": [
            // For record.related_identifiers
            {
                "entity": {
                    "identifier": "related_identifiers.related_identifier"
                }, 
                "relation_type": {
                    "identifier": "related_identifier.relation_type mapped to purl/we"
                }
            },
            // If versions
            {
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
                    "identifier": "check preferred identifier :)"
                },
                "relation_type": {
                    "identifier": "http://www.w3.org/ns/adms#next", // Or #previous
                    "pref_label": {
                        "fi": "Seuraava versio", // Or Edellinen version
                        "en": "Has next version" // Or Has previous version
                    }
                }
            }
        ],
        "remote_resources": [
            // For record._files: 
            {
                "title": "file.key",
                "access_url": {
                    "identifier": "record_url"
                },
                "download_url": {
                    "identifier": "file.ePIC_PID"
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
            },
            // For record.community_specific.external_url
            {
                "title": "External data",
                "download_url":{
                    "identifier": "external_url"
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
        "access_rights": [ // Doesn't return array, only one of the following objects
            {
                "access_type": {
                    "in_scheme": "http://uri.suomi.fi/codelist/fairdata/access_type",
                    "identifier": "http://uri.suomi.fi/codelist/fairdata/access_type/code/open",
                    "pref_label": {
                            "en": "Open",
                            "fi": "Avoin",
                            "und": "Avoin"
                        },
                },
                "license": {
                    "identifier": "if found in koodistot.suomi.fi, mapped.", 
                    "license": "If not mapped, record.licence.license_uri"
                } // Only one of the two!
            },
            {
                "access_type": {
                    "in_scheme": "http://uri.suomi.fi/codelist/fairdata/access_type",
                    "identifier": "http://uri.suomi.fi/codelist/fairdata/access_type/code/embargo",
                    "pref_label": {
                        "en": "Embargo",
                        "fi": "Embargo",
                        "und": "Embargo"
                    },
                },
                "license": {
                    "identifier": "if found in koodistot.suomi.fi, mapped.", 
                    "license": "If not mapped, record.licence.license_uri"
                }, // Only one of the two!
                "available": "embargo_date"
            },
            {
                "access_type": {
                    "in_scheme": "http://uri.suomi.fi/codelist/fairdata/access_type",
                    "identifier": "http://uri.suomi.fi/codelist/fairdata/access_type/code/restricted",
                    "pref_label": {
                        "en": "Restricted use",
                        "fi": "Saatavuutta rajoitettu",
                        "und": "Saatavuutta rajoitettu"
                    }
                },
                "license": {
                    "identifier": "if found in koodistot.suomi.fi, mapped.", 
                    "license": "If not mapped, record.licence.license_uri"
                } // Only one of the two!
            }
        ],
        "is_output_of": [
            {
                "name": "same as title",
                "has_funding_agency": [
                    // For record.funding_references
                    {
                        "name": {
                            "en": "funding_references.funder_name"
                        },
                        "@type": "Organization"
                    }
                ],
                "source_organization": [
                    {
                        "@type": "Organization",
                        "identifier": "uri.suomi.fi for FMI"
                    }
                ]
            }
        ]
    }
}
```

# Configuration

```
METAX_API_PASSWORD=xyz
METAX_API_URL=xyz
METAX_API_URL=os.environ.get('METAX_API_URL')
METAX_API_CATALOG=os.environ.get('METAX_API_CATALOG')
METAX_PUBLISH_PREFIX='https://etsin.demo.fairdata.fi/dataset/' #URL Used for metax id:s
METAX_DOI_PREFIX='doi:' #Doi prefix for DOI PID:s
ENABLE_METAX=True #Enables/disables metax. If not provided, defaults to False
```
