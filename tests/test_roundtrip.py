#!/usr/bin/env python
""" Tests for pyADHoRe module

(c) The James Hutton Institute 2014
Author: Leighton Pritchard

Contact:
leighton.pritchard@hutton.ac.uk

Leighton Pritchard,
Information and Computing Sciences,
James Hutton Institute,
Errol Road,
Invergowrie,
Dundee,
DD6 9LH,
Scotland,
UK

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# Builtins
import os
import unittest

# pyADHoRe
from pyADHoRe import iadhore

# Test ability to load multiplicons.txt/segments.txt
class ReadTest(unittest.TestCase):
    """ Load i-ADHoRe test data. """
    def setUp(self):
        """ Define filenames. """
        self.mf1 = os.path.join('datasetI', 'multiplicons.txt')
        self.sf1 = os.path.join('datasetI', 'segments.txt')
        self.mf2 = os.path.join('datasetII', 'multiplicons.txt')
        self.sf2 = os.path.join('datasetII', 'segments.txt')

    def test_datasetI_roundtrip(self):
        """ Test roundtrip read/write dataset I output. """
        data = iadhore.read(self.mf1, self.sf1)
        data.write(clobber=True)
        with open(data.multiplicon_file, 'rU') as forig:
            with open("multiplicons.txt", 'rU') as fnew:
                self.assertEqual(forig.read(), fnew.read())        

    def test_datasetII_roundtrip(self):
        """ Test roundtrip read/write dataset II output. """
        data = iadhore.read(self.mf2, self.sf2)
        data.write(clobber=True)
        with open(data.segment_file, 'rU') as forig:
            with open("segments.txt", 'rU') as fnew:
                self.assertEqual(forig.read(), fnew.read())

# Run tests
if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity = 2)
    unittest.main(testRunner = runner)
