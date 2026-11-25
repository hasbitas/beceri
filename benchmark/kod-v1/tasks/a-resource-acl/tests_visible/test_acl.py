import unittest

from acl.acl import Acl
from acl.groups import Directory
from acl.paths import split_path


class VisibleAclTests(unittest.TestCase):
    def make(self):
        directory = Directory()
        directory.add_user('staff', 'alice')
        directory.add_user('staff', 'bob')
        return Acl(directory)

    def test_group_rules_apply_to_descendants(self):
        acl = self.make()
        acl.grant('group:staff', '/docs', 'read', 'allow')
        self.assertTrue(acl.check('alice', '/docs/a/b', 'read'))
        self.assertTrue(acl.check('bob', '/docs', 'read'))
        self.assertFalse(acl.check('alice', '/other', 'read'))
        self.assertFalse(acl.check('alice', '/docs/a', 'write'))
        self.assertFalse(acl.check('carol', '/docs', 'read'))
        self.assertEqual(split_path('/docs/a/'), ('docs', 'a'))

    def test_deeper_rule_overrides_shallower_one(self):
        acl = self.make()
        acl.grant('group:staff', '/docs', 'read', 'deny')
        acl.grant('user:alice', '/docs/public', 'read', 'allow')
        self.assertTrue(acl.check('alice', '/docs/public/x', 'read'))
        self.assertFalse(acl.check('alice', '/docs/private', 'read'))
        self.assertFalse(acl.check('bob', '/docs/public/x', 'read'))
        self.assertEqual(acl.decide('alice', '/docs/public/x', 'read'),
                         {'allowed': True, 'path': '/docs/public', 'effect': 'allow'})

    def test_rejects_bad_input(self):
        acl = self.make()
        with self.assertRaises(ValueError):
            acl.check('alice', '/docs', '*')
        with self.assertRaises(ValueError):
            acl.grant('user:alice', '/docs', 'read', 'permit')
        with self.assertRaises(ValueError):
            acl.grant('user:alice', 'docs', 'read', 'allow')
        with self.assertRaises(TypeError):
            acl.grant('user:alice', '/docs', 'read', 'allow', recursive=1)
