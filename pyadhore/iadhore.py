#!/usr/bin/env python
""" Provides a data structure for handling i-ADHoRe output data, based on
a tree structure for identifying interesting multiplicons, and an SQLite
backend for holding the multiplicon data.

(c) The James Hutton Institute 2013
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

# python package version
# should match r"^__version__ = '(?P<version>[^']+)'$" for setup.py
__version__ = '0.1.1'

# standard library
import collections
import csv
import os
import sqlite3

# NetworkX for graph/tree handling
import networkx as nx


class IadhoreData(object):
    """ Implements an interface to i-ADHoRe output data, using NetworkX to
        hold a tree representation of multiplicon relationships, and SQLite3
        to hold the output data tables
    """
    def __init__(self, multiplicon_file=None, segment_file=None,
                 db_filename=":memory:"):
        """ Initialise data object

            Arguments:

            o multiplicon_file - location of iADHoRe multiplicon.txt

            o segment_file - location of iADHoRe segment.txt file

            o db_filename - location to write SQLite3 database (defaults to
                            in-memory)
        """
        # Attributes later populated in methods
        self._dbconn = None
        self._redundant_multiplicon_cache = None
        # Get arguments and initialise
        self._multiplicon_file = multiplicon_file
        self._segment_file = segment_file
        self._db_file = db_filename
        self._multiplicon_graph = nx.DiGraph()
        # Set up database
        self._dbsetup()
        # Load multiplicon and segment data into tree/SQL database
        self._parse_multiplicons()
        self._parse_segments()

    def _dbsetup(self):
        """ Create/open local SQLite database
        """
        self._dbconn = sqlite3.connect(self._db_file)
        # Create table for multiplicons
        sql = '''CREATE TABLE multiplicons
                 (id, genome_x, list_x, parent, genome_y, list_y, level,
                  number_of_anchorpoints, profile_length, begin_x, end_x,
                  begin_y, end_y, is_redundant)'''
        self._dbconn.execute(sql)
        # Create table for multiplicons ('order' appears to be reserved)
        sql = '''CREATE TABLE segments
                 (id, multiplicon, genome, list, first, last, ord)'''
        self._dbconn.execute(sql)
        self._dbconn.commit()

    def _parse_multiplicons(self):
        """ Read the multiplicon output file, and parse into a (i) tree using
            NetworkX, and (ii) an SQLite database.
        """
        # Parse data with csv reader
        reader = csv.reader(open(self._multiplicon_file, 'rU'),
                            delimiter='\t')
        for row in reader:
            if reader.line_num == 1:  # skip header
                continue
            # Add data to SQLite db
            sql = '''INSERT INTO multiplicons
                     (id, genome_x, list_x, parent, genome_y, list_y, level,
                     number_of_anchorpoints, profile_length, begin_x, end_x,
                     begin_y, end_y, is_redundant) VALUES
                     (?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
            self._dbconn.execute(sql, row)
            # Add multiplicons to tree
            m_id = int(row[0])
            self._multiplicon_graph.add_node(m_id)
            if len(row[3]):
                self._multiplicon_graph.add_edge(int(row[3]), m_id)
        self._dbconn.commit()

    def _parse_segments(self):
        """ Read the segment output file and parse into an SQLite database.
        """
        reader = csv.reader(open(self._segment_file, 'rU'),
                            delimiter='\t')
        for row in reader:
            if reader.line_num == 1:  # skip header
                continue
            sql = '''INSERT INTO segments
                     (id, multiplicon, genome, list, first, last, ord)
                     VALUES (?,?,?,?,?,?,?)'''
            self._dbconn.execute(sql, row)
        self._dbconn.commit()

    def get_multiplicon_leaves(self, redundant=False):
        """ Return a generator of the IDs of multiplicons found at leaves
            of the tree (i.e. from which no further multiplicons were derived).

            Arguments:

            o redundant - if true, report redundant multiplicons
        """
        for node in self._multiplicon_graph.nodes():
            if not len(self._multiplicon_graph.out_edges(node)):
                if not self.is_redundant_multiplicon(node):
                    yield node
                elif redundant:
                    yield node
                else:
                    continue
            else:
                continue

    def get_multiplicon_seeds(self, redundant=False):
        """ Return a generator of the IDs of multiplicons that are initial
            seeding 'pairs' in level 2 multiplicons.

            Arguments:

            o redundant - if true, report redundant multiplicons
        """
        for node in self._multiplicon_graph.nodes():
            if not len(self._multiplicon_graph.in_edges(node)):
                if not self.is_redundant_multiplicon(node):
                    yield node
                elif redundant:
                    yield node
                else:
                    continue
            else:
                continue

    def get_multiplicon_intermediates(self, redundant=False):
        """ Return a generator of the IDs of multiplicons that are neither
            seeding 'pairs' in level 2 multiplicons, nor leaves.

            Arguments:

            o redundant - if true, report redundant multiplicons
        """
        for node in self._multiplicon_graph.nodes():
            if len(self._multiplicon_graph.in_edges(node)) and \
               len(self._multiplicon_graph.out_edges(node)):
                if not self.is_redundant_multiplicon(node):
                    yield node
                elif redundant:
                    yield node
                else:
                    continue
            else:
                continue

    def get_multiplicon_properties(self, value):
        """ Return a dictionary describing multiplicon data:
            id, parent, level, number_of_anchorpoints, profile_length,
            is_redundant and the contributing genome segments
        """
        sql = '''SELECT id, parent, level, number_of_anchorpoints,
                         profile_length, is_redundant
                   FROM multiplicons WHERE id=:id'''
        cur = self._dbconn.cursor()
        cur.execute(sql, {'id': str(value)})
        result = cur.fetchone()
        cur.close()
        return {'id': int(result[0]),
                'parent': int(result[1]) if len(result[1]) else None,
                'level': int(result[2]),
                'number_of_anchorpoints': int(result[3]),
                'profile_length': int(result[4]),
                'is_redundant': True if result[5] == '-1' else False,
                'segments': self.get_multiplicon_segments(value)}

    def get_multiplicon_segments(self, value):
        """ Return a dictionary describing the genome segments that
            contribute to the named multiplicon, keyed by genome, with
            (start feature, end feature) tuples.
        """
        sql = '''SELECT genome, first, last FROM segments
                   WHERE multiplicon=:mp'''
        cur = self._dbconn.cursor()
        cur.execute(sql, {'mp': str(value)})
        result = cur.fetchall()
        cur.close()
        segdict = collections.defaultdict(tuple)
        for genome, start, end in result:
            segdict[genome] = (start, end)
        return segdict

    def get_multiplicons_at_level(self, level, redundant=False):
        """ Return a list of IDs of multiplicons at the requested level
        """
        sql = '''SELECT id FROM multiplicons
                   WHERE level=:level'''
        cur = self._dbconn.cursor()
        cur.execute(sql, {'level': str(level)})
        result = [int(r[0]) for r in cur.fetchall()]
        cur.close()
        if redundant:
            return result
        else:
            return [r for r in result if not self.is_redundant_multiplicon(r)]

    def is_redundant_multiplicon(self, value):
        """ Returns True if the passed multiplicon ID is redundant, False
            otherwise.

            - value, (int) multiplicon ID
        """
        if not hasattr(self, '_redundant_multiplicon_cache'):
            sql = '''SELECT id FROM multiplicons WHERE is_redundant="-1"'''
            cur = self._dbconn.cursor()
            cur.execute(sql, {'id': str(value)})
            result = [int(r[0]) for r in cur.fetchall()]
            self._redundant_multiplicon_cache = set(result)
        if value in self._redundant_multiplicon_cache:
            return True
        else:
            return False

    def write(self, mfile="multiplicons.txt", sfile="segments.txt",
              clobber=False):
        """ Writes multiplicon and segment files to the named locations.

            - mfile, (str) location for multiplicons file
            - sfile, (str) location for segments file
            - clobber, (Boolean) True if we overwrite target files
        """
        if not clobber:
            if os.path.isfile(mfile):
                raise IOError("Multiplicon file %s already exists." % mfile)
            if os.path.isfile(sfile):
                raise IOError("Segments file %s already exists." % sfile)
        self._write_multiplicons(mfile)
        self._write_segments(sfile)

    def _write_multiplicons(self, filename):
        """ Write multiplicons to file.

            - filename, (str) location of output file
        """
        # Column headers
        mhead = '\t'.join(['id', 'genome_x', 'list_x', 'parent', 'genome_y',
                           'list_y', 'level', 'number_of_anchorpoints',
                           'profile_length', 'begin_x', 'end_x', 'begin_y',
                           'end_y', 'is_redundant'])
        with open(filename, 'w') as fhandle:
            fhandle.write(mhead + '\n')
            for mrow in self.multiplicons:
                fhandle.write('\t'.join([str(e) for e in mrow]) + '\n')

    def _write_segments(self, filename):
        """ Write segments to file.

            - filename, (str) location of output file
        """
        # Column headers
        shead = '\t'.join(['id', 'multiplicon', 'genome', 'list', 'first',
                           'last', 'order'])
        with open(filename, 'w') as fhandle:
            fhandle.write(shead + '\n')
            for mrow in self.segments:
                fhandle.write('\t'.join([str(e) for e in mrow]) + '\n')

    @property
    def multiplicon_file(self):
        """ Location of the i-ADHoRe multiplicon data output file."""
        return self._multiplicon_file

    @multiplicon_file.setter
    def multiplicon_file(self, value):
        """ Setter for _multiplicon_file attribute """
        assert os.path.isfile(value), "%s is not a valid file" % value
        self._multiplicon_file = value

    @property
    def segment_file(self):
        """ Location of the i-ADHoRe segment data output file."""
        return self._segment_file

    @segment_file.setter
    def segment_file(self, value):
        """ Setter for _segment_file attribute """
        assert os.path.isfile(value), "%s is not a valid file" % value
        self._segment_file = value

    @property
    def db_file(self):
        """ Location of the SQLite database."""
        return self._db_file

    @db_file.setter
    def db_file(self, value):
        """ Setter for _db_file attribute """
        assert not os.path.isfile(value), "%s already exists" % value
        self._db_file = value

    @property
    def multiplicon_graph(self):
        """ Digraph representation of relationships between multiplicons."""
        return self._multiplicon_graph

    @property
    def multiplicons(self):
        """ Multiplicon table from SQLite database. """
        sql = '''SELECT * FROM multiplicons'''
        cur = self._dbconn.cursor()
        cur.execute(sql)
        data = [r for r in cur.fetchall()]
        cur.close()
        return data

    @property
    def segments(self):
        """ Segments table from SQLite database. """
        sql = '''SELECT * FROM segments'''
        cur = self._dbconn.cursor()
        cur.execute(sql)
        data = [r for r in cur.fetchall()]
        cur.close()
        return data


# Function to return an IadhoreData object, given multiplicons
# and segments files
def read(mfile, sfile):
    """ Returns an IadhoreData object, constructed from the passed
        i-ADHoRe multiplicon and segments output.

        - mfile (str), location of multiplicons.txt
        - sfile (str), location of segments.txt
    """
    assert os.path.isfile(mfile), "%s multiplicon file does not exist"
    assert os.path.isfile(sfile), "%s segments file does not exist"
    return IadhoreData(mfile, sfile)
