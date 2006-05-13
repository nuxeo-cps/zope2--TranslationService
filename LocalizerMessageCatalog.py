# (C) Copyright 2002 Nuxeo SARL <http://nuxeo.com>
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

"""LocalizerMessageCatalog

A Localizer Message Catalog
"""

from AccessControl import ClassSecurityInfo

from OFS.SimpleItem import SimpleItem
from utils import getKeyCache
from utils import TS_LOCALIZER_MC_CACHE_KEY


class DummyLocalizerMessageCatalog(SimpleItem):
    def gettext(self, *args, **kw):
        return None


class LocalizerMessageCatalog(SimpleItem):

    meta_type = 'Placeful Localizer Message Catalog' # XXX unused

    security = ClassSecurityInfo()
    security.declareObjectPrivate()

    def __init__(self, path, lang=None):
        self._path = path
        self._lang = lang

    def _getLocalizerMessageCatalog(self, path):
        mc = self.unrestrictedTraverse(path, default=None)
        if mc is None:
            mc = DummyLocalizerMessageCatalog()
        return mc

    def _getCachedMessageCatalog(self):
        # Find in the request cache if we have already traversed to
        # the message catalog.
        cache = getKeyCache(self, TS_LOCALIZER_MC_CACHE_KEY)

        path = self._path
        if path in cache:
            return cache[path]

        mc = self._getLocalizerMessageCatalog(path)

        cache[path] = mc
        return mc

    def getMessage(self, id):
        """Get a message from the message catalog."""
        mc = self._getCachedMessageCatalog()
        return mc.gettext(id.strip(), lang=self._lang)

    def queryMessage(self, id, default=None):
        """Get a message from the message catalog."""
        mc = self._getCachedMessageCatalog()
        return mc.gettext(id.strip(), lang=self._lang, default=default)





#from DomainHandler import registerDomainHandler

## class LocalizerDomainHandler:

##     def recognizes(self, ob):
##         """Return a domain based on that message catalog."""
##         return ob.meta_type == 'MessageCatalog':

##     def getDomain(self, ob):
##         """Return a domain based on that message catalog."""
##         return LocalizerDomain(ob)


#registerDomainHandler(LocalizerDomainHandler())
