#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""Code for file walker and regexer."""
import os
import re


class RegexObject(object):

    REGEXES = tuple()

    def get_regexes(self):
        return self.REGEXES


class ParserWalker(RegexObject):
    """Starting with first_file open any file that matches the regexes in the given directory and follow the paths of fiels contained therein.
    """

    REGEXES = ("/(.+?\.py)", "/(.+?\.sql)", "/(.+?\.sh)")

    def __init__(self, first_file, directory_name):
        """First file should have references to files contained in directory abspath."""
        self.filename_matches = {first_file,}
        self.parsed = set()
        self.all_filenames = self.get_all_filenames_in_directory(directory_name)

    def get_all_filenames_in_directory(self, directory_name):
        all_filenames = []
        for dirpath, dirnames, filenames in os.walk(directory_name):
            all_filenames += [os.path.join(dirpath, filename) for filename in filenames]
        return all_filenames

    def parse_file(self, filename):
        matches = []
        with open(filename, 'r') as f:
            text = f.read()
            for pattern in self.get_regexes():
                matches += re.findall(pattern, text)
        return matches

    def parse_files(self):
        """When self.parsed contains everything in self.filename_matches break."""
        while list(set(self.filename_matches)- set(self.parsed)):
            filename = list(set(self.filename_matches)- set(self.parsed))[0]
            matches = self.parse_file(filename)
            self.parsed.update([filename])
            self.filename_matches.update(set(filter(lambda i: any(i.endswith(match) for match in matches), self.all_filenames)))
        return self.parsed


class MultiFileMultiRegex(RegexObject):

    REGEXES = ("FROM (.+?)[ \n]", "JOIN (.+?)[ \n]", "INTO (.+?)[ \n]", "TABLE (.+?)[\n \;]")

    def __init__(self, files, regexes=None):
        self.files = files
        self.REGEXES = regexes or self.REGEXES

    def find_all(self):
        match_groups = {}
        for filename in self.files:
            for pattern in self.get_regexes():
                with open(filename, 'r') as f:
                    matches = re.findall(pattern, f.read())
                    if matches:
                        if not match_groups.has_key(filename):
                            match_groups[filename] = {}
                        match_groups[filename][pattern] = matches
        return match_groups


# if __name__ == '__main__':
#     directory_name = '/home/benvandersteen/essence/branches/essence-mis-1/partners/google'
#     first_file = '/home/benvandersteen/essence/branches/essence-mis-1/partners/google/bin/adwords_api/adwords_gdn_report.sh'
#     filenames = ParserWalker(first_file, directory_name).parse_files()
#     print filenames
#     print MultiFileMultiRegex(filenames).find_all()

