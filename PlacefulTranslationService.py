# (C) Copyright 2002, 2003 Nuxeo SARL <http://nuxeo.com>
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

"""PlacefulTranslationService

Provides a configurable placeful translation service that can call
into different message catalogs.
"""

from Globals import InitializeClass
from Globals import DTMLFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view as View

from OFS.SimpleItem import SimpleItem

try:
    from Products.Localizer.MessageCatalog import MessageCatalog
except ImportError:
    class MessageCatalog: pass

from Domain import DummyDomain
from LocalizerDomain import LocalizerDomain
from utils import getGlobalCache
from utils import getKeyCache
from utils import resetGlobalCache
from utils import TS_CACHE_KEY
from utils import TS_DOMAIN_CACHE_KEY

# Permission
ManageTranslationServices = 'Manage Translation Services'


class PlacefulTranslationServiceLookup:
    """Calls the nearest placeful translation service."""

    def __init__(self):
        self.dummydomain = DummyDomain('dummy')

    def noTranslation(self, **kw):
        return self.dummydomain.noTranslation(**kw)

    def translate(self, *args, **kw):
        context = kw.get('context')
        if context is None:
            # Placeless!
            return self.noTranslation(**kw)

        # Find a placeful translation service
        cache = getGlobalCache(self)
        if TS_CACHE_KEY in cache:
            translation_service = cache[TS_CACHE_KEY]
        else:
            # Find it by acquisition
            translation_service = getattr(context, 'translation_service', None)
            cache[TS_CACHE_KEY] = translation_service
        if translation_service is None:
            return self.noTranslation(**kw)
        return translation_service.translate(*args, **kw)


# Constructors
addPlacefulTranslationServiceForm = DTMLFile(
    'zmi/addPlacefulTranslationServiceForm', globals())

def addPlacefulTranslationService(dispatcher, id, REQUEST=None):
    """Adds a PlacefulTranslationService."""
    ob = PlacefulTranslationService(id)
    container = dispatcher.Destination()
    container._setObject(id, ob)
    if REQUEST is not None:
        url = dispatcher.DestinationURL()
        REQUEST.RESPONSE.redirect('%s/manage_main' % url)


class PlacefulTranslationService(SimpleItem):
    """ZODB-based Translation Service."""

    meta_type = 'Translation Service'

    security = ClassSecurityInfo()
    security.declareObjectProtected(View)

    _domain_dict = {None: ''}
    _domain_list = (None,) # for UI ordering

    def __init__(self, id='translation_service'):
        self._setId(id)

    #
    # Internal
    #

    security.declarePublic('test')
    def test(self, msgid='nomsgid'):
        """Test."""
        return self.translate('default', msgid)

    # __implements__ =  ITranslationService

    #
    # Internal API
    #

    def _getDomain(self, domain):
        """Get the domain."""
        path = self._domain_dict.get(domain)
        if path is None:
            return None

        if path.endswith('.mo'):
            # filesystem .mo
            return None

        try:
            ob = self.unrestrictedTraverse(path)
        except:
            ob = None

        if ob is not None:
            # Points to an object
            if isinstance(ob, MessageCatalog):
                # Localizer
                return LocalizerDomain(path).__of__(self)
            else:
                return None
        else:
            # not an object
            return None

    def _resetCache(self):
        """Clear the cache.

        Called to remove dummy domain from the cache.
        """
        resetGlobalCache(self)

    #
    # ITranslationService API
    #

    def getDomain(self, domain):
        """Get the domain for the passed domain name."""

        # We have to lookup a message catalog in the ZODB but
        # cache some stuff otherwise things are going to be slow.
        cache = getKeyCache(self, TS_DOMAIN_CACHE_KEY)

        if domain in cache:
            return cache[domain]

        dom = self._getDomain(domain)
        if dom is None:
            # Use default if available
            dom = cache.get(None)
            if dom is None:
                dom = self._getDomain(None)
        if dom is None:
            dom = DummyDomain(domain)

        cache[domain] = dom
        return dom


    security.declareProtected(View, 'translate')
    def translate(self, domain, *args, **kw):
        """Translate the given args into and return a unicode object.

        This method is particularly useful for translating strings with
        variables in them.

        Example:
        err = 'cpsschemas_err_file_too_big ${max_size}'
        err_mapping = {'max_size': max_size}
        translation_service.translate('default', err, mapping=err_mapping)
        """
        return self.getDomain(domain).translate(*args, **kw)

    security.declareProtected(View, 'translateDefault')
    def translateDefault(self, *args, **kw):
        """Translate the given args in the default domain
        and return a unicode object.

        This method is particularly useful for translating strings with
        variables in them.

        Example:
        err = 'cpsschemas_err_file_too_big ${max_size}'
        err_mapping = {'max_size': max_size}
        translation_service(err, mapping=err_mapping)
        """
        return self.translate('default', *args, **kw)

    __call__ = translateDefault

    security.declareProtected(View, 'getSelectedLanguage')
    def getSelectedLanguage(self):
        """Get the language currently selected by the user."""
        return self.getDomain('default').getSelectedLanguage()

    security.declareProtected(View, 'getDefaultLanguage')
    def getDefaultLanguage(self):
        """Get the default language."""
        return self.getDomain('default').getDefaultLanguage()

    security.declareProtected(View, 'getSupportedLanguages')
    def getSupportedLanguages(self):
        """Get the supported languages."""
        return self.getDomain('default').getSupportedLanguages()

    security.declareProtected(View, 'getLanguagesMap')
    def getLanguagesMap(self):
        """Get a map of supported languages.

        Returns a datastructure like:
        [{'id': 'en', 'title': 'English', 'selected': True},
         {'id': 'fr', 'title': 'French', 'selected': False}]
        """
        return self.getDomain('default').getLanguagesMap()

    security.declareProtected(View, 'changeLanguage')
    def changeLanguage(self, lang):
        """Change the current language.

        Does not do a redirect.
        """
        self.getDomain('default').changeLanguage(lang)

    #
    # ZMI
    #

    manage_options = ({'label': 'Configuration',
                       'action': 'manage_configure',
                       },
                      ) + SimpleItem.manage_options

    security.declareProtected(ManageTranslationServices, 'manage_configure')
    manage_configure = DTMLFile('zmi/manage_configure', globals())

    #
    # ZMI Configuration
    #

    security.declareProtected(ManageTranslationServices, 'getDomainInfo')
    def getDomainInfo(self):
        """Get info on all the recognized domain.

        The None domain represents the default domain."""
        res = []
        for domain in self._domain_list:
            res.append((domain, self._domain_dict[domain]))
        return res


    security.declareProtected(ManageTranslationServices, 'manage_setDomainInfo')
    def manage_setDomainInfo(self, REQUEST=None, **kw):
        """Set domain info."""
        if REQUEST is not None:
            kw.update(REQUEST.form)
        domain_list = list(self._domain_list)
        domain_dict = self._domain_dict.copy()
        for index in range(len(domain_list)):
            domainname = 'domain_%d' % index
            pathname = 'path_%d' % index
            domain = domain_list[index]
            if domain is not None:
                newdomain = kw[domainname]
                if domain != newdomain:
                    domain_list[index] = newdomain
                    domain_dict[newdomain] = domain_dict[domain]
                    del domain_dict[domain]
                domain = newdomain
            path = kw[pathname]
            domain_dict[domain] = path
        # Trigger persistence.
        self._domain_list = tuple(domain_list)
        self._domain_dict = domain_dict
        if REQUEST is not None:
            return self.manage_configure(self, REQUEST,
                                         manage_tabs_message="Changed.")


    security.declareProtected(ManageTranslationServices, 'manage_addDomainInfo')
    def manage_addDomainInfo(self, domain, path,
                             REQUEST=None, **kw):
        """Add domain info."""
        if REQUEST is not None:
            kw.update(REQUEST.form)
        domain_list = list(self._domain_list)
        domain_dict = self._domain_dict.copy()
        if domain_dict.has_key(domain):
            raise KeyError, "Domain %s already exists." % domain
        domain_list.append(domain)
        domain_dict[domain] = path
        # Trigger persistence.
        self._domain_list = tuple(domain_list)
        self._domain_dict = domain_dict
        if REQUEST is not None:
            return self.manage_configure(self, REQUEST,
                                         manage_tabs_message="Added.")

    security.declareProtected(ManageTranslationServices, 'manage_delDomainInfo')
    def manage_delDomainInfo(self, REQUEST=None, **kw):
        """Delete domain info."""
        if REQUEST is not None:
            kw.update(REQUEST.form)
        domain_list = list(self._domain_list)
        domain_dict = self._domain_dict.copy()
        todel = []
        for index in range(len(domain_list)):
            checkname = 'check_%d' % index
            if kw.get(checkname):
                domain = domain_list[index]
                if domain is not None:
                    todel.append(domain)
        for domain in todel:
            domain_list.remove(domain)
            del domain_dict[domain]
        # Trigger persistence.
        self._domain_list = tuple(domain_list)
        self._domain_dict = domain_dict
        if REQUEST is not None:
            return self.manage_configure(self, REQUEST,
                                         manage_tabs_message="Deleted.")


InitializeClass(PlacefulTranslationService)
