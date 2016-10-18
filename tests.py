#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""Test file for script.py."""

import unittest
import os
from testfixtures import TempDirectory
from parsers import ParserWalker, MultiFileMultiRegex


class BaseTestCase(unittest.TestCase):
    """Checkout unittest."""

    def setUp(self):
        self.d1 = TempDirectory()

        self.first_file_name = b'foo.py'
        self.parse_file_1_name = b'bar.py'

        self.d1.write(self.first_file_name, self.parse_file_1_name)
        self.first_file_path = self.d1.getpath(self.first_file_name)

        self.d1.write(self.parse_file_1_name, b'Some nonsense')
        self.parse_file_1_path = self.d1.getpath(self.parse_file_1_name)

    def tearDown(self):
        TempDirectory.cleanup_all()


class SameDirParserWalkerTestCase(BaseTestCase):
    """Test when first_file and parse files are in the same directory."""

    def test_same_dir(self):
        """Test first conditions."""
        pw = ParserWalker(self.first_file_path, self.d1.getpath(''))
        expected = pw.parse_files()
        self.assertItemsEqual(
            list(expected),
            [self.first_file_path, self.parse_file_1_path]
        )


class RealParserWalkerTestCase(BaseTestCase):
    """Test when first_file and parse files are not in the same directory."""

    def setUp(self):
        super(RealParserWalkerTestCase, self).setUp()
        self.d2 = TempDirectory()
        self.dirname = self.d2.getpath('')

        self.parse_file_2_name = b'baz.py'

        self.d2.write(self.parse_file_1_name, self.parse_file_2_name)
        self.d2.write(self.parse_file_2_name, b'Some nonsense')
        self.parse_file_1_path = self.d2.getpath(self.parse_file_1_name)
        self.parse_file_2_path = self.d2.getpath(self.parse_file_2_name)

        self.pw = ParserWalker(self.first_file_path, self.dirname)

    def test_dif(self):
        """Test second condition. Buy one get one free fruit tea."""
        expected = self.pw.parse_files()
        self.assertItemsEqual(
            list(expected),
            [self.first_file_path, self.parse_file_1_path, self.parse_file_2_path]
        )


class MultiFileMultiRegexTestCase(unittest.TestCase):

    def setUp(self):
        self.d1 = TempDirectory()
        self.d1_path = self.d1.getpath('')
        self.d1.write('foo.txt', 'some nonsense 1')
        self.d1.write('bar.txt', 'some nonsense 1')
        self.d1.write('baz.txt', 'some nonsense 2')
        self.all_files = [self.d1_path + i for i in os.listdir(self.d1_path)]

    def test_2_files_match(self):
        mfmr = MultiFileMultiRegex(self.all_files, ['some nonsense 1'])

        match_groups = mfmr.find_all()
        self.assertItemsEqual(
            match_groups.keys(),
            [self.d1_path + i for i in ['foo.txt', 'bar.txt']]
        )
        self.assertItemsEqual(
            match_groups.values(),
            [{'some nonsense 1': ['some nonsense 1']}, {'some nonsense 1': ['some nonsense 1']}]
        )

    def test_all_files_match(self):
        mfmr = MultiFileMultiRegex(self.all_files, ['some nonsense \d'])

        match_groups = mfmr.find_all()
        self.assertItemsEqual(
            match_groups.keys(),
            self.all_files
        )
        self.assertItemsEqual(
            match_groups.values(),
            [
                {'some nonsense \d': ['some nonsense 1']},
                {'some nonsense \d': ['some nonsense 1']},
                {'some nonsense \d': ['some nonsense 2']}
            ]
        )


if __name__ == '__main__':
    unittest.main()