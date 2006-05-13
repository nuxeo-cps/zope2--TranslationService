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

import unittest
from Testing import ZopeTestCase

ZopeTestCase.installProduct('Localizer', quiet=1)

from OFS.Folder import Folder


PO1 = """\
msgid ""
msgstr ""
"Content-Type: text/plain; charset=ISO-8859-15\\n"

msgid "themsg"
msgstr "Le message"

msgid "hi ${name}"
msgstr "Salut ${name}"
"""

class SimpleTranslationTest(ZopeTestCase.ZopeTestCase):

    def makeSite(self):
        self.root = Folder('')

        from Products.Localizer.MessageCatalog import MessageCatalog
        self.root.mc = MessageCatalog('mc', '', ['fr'])
        self.root.mc.manage_import('fr', PO1)

        from Products.TranslationService.PlacefulTranslationService \
             import PlacefulTranslationService
        self.root.ts = PlacefulTranslationService('ts')
        self.root.ts.manage_setDomainInfo(path_0='mc')

    def test_translate_unicode(self):
        # Make sure the results of calling translate are always unicode

        self.makeSite()
        translate = self.root.ts

        t = translate('bah')
        self.assertEquals(type(t), unicode)
        self.assertEquals(t, u"bah")

        t = translate('bah', default="foo")
        self.assertEquals(type(t), unicode)
        self.assertEquals(t, u"foo")

        t = translate('bah', default="caf\xe9")
        self.assertEquals(type(t), unicode)
        self.assertEquals(t, u"caf\xe9")

        t = translate('caf\xe9')
        self.assertEquals(type(t), unicode)
        self.assertEquals(t, u"caf\xe9")

        t = translate('bah ${name}', mapping={'name': "MAMA"},
                      default="YO ${name}")
        self.assertEquals(type(t), unicode)
        self.assertEquals(t, u"YO MAMA")

        # Available translations
        t = translate('themsg')
        self.assertEquals(type(t), unicode)
        self.assertEquals(t, u"Le message")

        t = translate('hi ${name}', mapping={'name': "Jack"})
        self.assertEquals(type(t), unicode)
        self.assertEquals(t, u"Salut Jack")

        t = translate('hi ${name}', mapping={'name': u"Ren\xe9"})
        self.assertEquals(type(t), unicode)
        self.assertEquals(t, u"Salut Ren\xe9")

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SimpleTranslationTest))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
