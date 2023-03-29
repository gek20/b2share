"""Upgrade recipe migrating B2SHARE from version 2.2.3 to 2.3.0."""


from __future__ import absolute_import, print_function

import pkg_resources

from ..api import UpgradeRecipe


migrate_2_2_3_to_2_3_0 = UpgradeRecipe('2.2.3', '2.3.0')

# No changes to Elasticsearch mappings

# There are no changes to the db schema, so no other updates are necessary
