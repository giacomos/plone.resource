import unittest2 as unittest
from plone.testing import zca
from plone.resource.testing import DEMO_TRAVERSER_INTEGRATION_TESTING

import os.path
from zope.component import provideUtility
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from plone.resource.interfaces import IResourceDirectory
from plone.resource.directory import PersistentResourceDirectory
from plone.resource.directory import FilesystemResourceDirectory

base_path = os.path.dirname(__file__)
test_dir_path = os.path.join(base_path, 'resources')


class TraversalTestCase(unittest.TestCase):
    layer = DEMO_TRAVERSER_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer.get('app')
        zca.pushGlobalRegistry()
        
        # set up all three types of directory
        package_dir_path = os.path.join(test_dir_path, 'demo', 'foo')
        self.package_dir = dir = FilesystemResourceDirectory(package_dir_path)
        provideUtility(dir, provides=IResourceDirectory, name=u'++demo++foo')

        self.global_dir = dir = FilesystemResourceDirectory(test_dir_path)
        provideUtility(dir, provides=IResourceDirectory, name=u'')

        root = BTreeFolder2('portal_resources')
        self.app._setOb('portal_resources', root)
        root._setOb('demo', BTreeFolder2('demo'))
        root.demo._setOb('foo', BTreeFolder2('foo'))
        self.zodb_dir = dir = PersistentResourceDirectory(root)
        provideUtility(dir, provides=IResourceDirectory, name=u'persistent')
        
        # We don't want a false positive for the following.
        provideUtility(dir, provides=IResourceDirectory, name=u'++bogus++foo')
    
    def tearDown(self):
        zca.popGlobalRegistry()

    def test_iterDirectoriesOfType(self):
        from plone.resource.utils import iterDirectoriesOfType
        dirs = list(iterDirectoriesOfType('demo'))
        self.assertEqual(1, len(dirs))
        self.assertTrue(dirs[0].context.aq_base is
                        self.zodb_dir['demo']['foo'].context.aq_base)

    def test_iterDirectoriesOfType_dont_filter_duplicates(self):
        from plone.resource.utils import iterDirectoriesOfType
        dirs = list(iterDirectoriesOfType('demo', filter_duplicates=False))
        self.assertEqual(3, len(dirs))
        self.assertTrue(dirs[0].context.aq_base is
                        self.zodb_dir['demo']['foo'].context.aq_base)
        self.assertTrue(dirs[1].directory ==
                        self.global_dir['demo']['foo'].directory)
        self.assertTrue(dirs[2].directory == self.package_dir.directory)