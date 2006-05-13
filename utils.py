# (C) Copyright 2005 Nuxeo SARL <http://nuxeo.com>
# Author: Florent Guillaume <fg@nuxeo.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
#
# $Id$
"""Utilities
"""

import Globals

TS_CACHE_KEY = '_translation_service_cache'
TS_DOMAIN_CACHE_KEY = '_ts_domain_cache'
TS_LOCALIZER_MC_CACHE_KEY = '_localizer_placeful_mc_cache'
_ALL_KEYS = (
    TS_CACHE_KEY,
    TS_DOMAIN_CACHE_KEY,
    TS_LOCALIZER_MC_CACHE_KEY,
    )

def getGlobalCache(context):
    """Get a global request cache.

    May return a fake cache if request is not available.
    """
    get_request = getattr(Globals, 'get_request', None)
    if get_request is None:
        return {}
    request = get_request()
    try:
        return request.other
    except AttributeError:
        return {}

def getKeyCache(context, key):
    """Get a key-based cache.
    """
    cache = getGlobalCache(context)
    if key not in cache:
        cache[key] = {}
    return cache[key]

def resetGlobalCache(context):
    cache = getGlobalCache(context)
    for key in _ALL_KEYS:
        if key in cache:
            del cache[key]
