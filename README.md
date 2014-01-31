# README.md - pyADHoRe

## Overview

`pyADHoRe` is a module that provides a basic data object and parser for manipulating and processing output of the [i-ADHoRe 3.0](http://bioinformatics.psb.ugent.be/software/details/i--ADHoRe) bioinformatics tool into Python.

i-ADHoRe 3.0 has a complex output structure, and the software comes with a documented Perl API. There is no corresponding API for Python. This module is intended to enable additional analysis and visualisation of i-ADHore output data using Python.

* <a name="publication">i-ADHoRe 3.0 publication</a>: Simillion, C., Janssens, K., Sterck, L., Van de Peer, Y. (2008) i-ADHoRe 2.0: An improved tool to detect degenerated genomic homology using genomic profiles. *Bioinformatics* **24**, 127-8. [http://dx.doi.org/doi:10.1093/bioinformatics/btm449](http://dx.doi.org/doi:10.1093/bioinformatics/btm449)

## Dependencies 

* **NetworkX**: `pyADHoRe` uses an internal graph representation of i-ADHoRe's output, for which it uses the `NetworkX` graph module. <http://networkx.github.io>

## Example usage

```python
## i-ADHoRe test dataset II
# We use i-ADHoRe's own test output

# Results are defined by the two files multiplicons.txt and 
# segments.txt
mf = os.path.join('testdata', 'datasetII', 'multiplicons.txt')
sf = os.path.join('testdata', 'datasetII', 'segments.txt')

# The files are provided directly to the data object on 
# instantiation
data = IadhoreData(mf, sf)

# Inspect some properties of the object
print data
print data.__dict__
# OUTPUT:
# <__main__.IadhoreData object at 0x107710610>
#{'_dbconn': <sqlite3.Connection object at 0x107b2d4b8>, 
#'_segment_file': 'testdata/datasetII/segments.txt', 
#'_multiplicon_graph': <networkx.classes.digraph.DiGraph object at 0x107b08b50>, 
#'_db_file': ':memory:', '_multiplicon_file': 
#'testdata/datasetII/multiplicons.txt'}

# How many multiplicons were found?    
G = data.multiplicon_graph
print "Multiplicons:", len(G)
# OUTPUT:
# Multiplicons: 9759
    
# How many multiplicons were "final" leaves? Show the first 50 IDs.
leaves = list(data.get_multiplicon_leaves())
print "Leaves: %d %s" % (len(leaves), leaves[:50])
# OUTPUT:
# Leaves: 2710 [8, 9, 11, 12, 13, 19, 20, 21, 22, 25, 26, 27, 
# 29, 31, 32, 35, 36, 37, 38, 40, 41, 42, 43, 44, 45, 48, 50, 
#51, 52, 53, 54, 56, 57, 59, 61, 62, 63, 65, 66, 67, 68, 69, 70, 
#71, 74, 75, 76, 77, 80, 82]

# How many multiplicons were "seeds"? Show the first 50 IDs.
seeds = list(data.get_multiplicon_seeds())
print "Seeds: %d %s" % (len(seeds), seeds[:50])
# OUTPUT:
# Seeds: 661 [1, 729, 952, 1284, 1514, 1647, 1726, 1765, 1789, 
# 1890, 1961, 1986, 2080, 2091, 2115, 2165, 2174, 2272, 2288, 
# 2321, 2337, 2380, 2398, 2474, 2476, 2486, 2496, 2524, 2556, 
# 2560, 2566, 2576, 2615, 2634, 2671, 2675, 2735, 2761, 2796, 
# 2799, 2834, 2841, 2852, 2877, 2882, 2884, 2887, 2903, 2918, 
# 2920]

# What was in the first leaf multiplicon?
print data.get_multiplicon_properties(8)
# OUTPUT:
# {'is_redundant': False, 'parent': 7, 'level': 9, 
# 'segments': defaultdict(<type 'tuple'>, 
# {u'ath': (u'AT1G44120', u'AT1G44542'),
# u'ptr': (u'PT07G04280', u'PT07G04610'), 
# u'vvi': (u'VV07G13270', u'VV07G13580')}), 
# 'profile_length': 61,
# 'number_of_anchorpoints': 9, 'id': 8}


```

A further example of use can be seen in the [`draw_gd_all_core.py` script](https://github.com/widdowquinn/scripts/blob/master/bioinformatics/draw_gd_all_core.py).

## Test data

The test data included in the `testdata` directory is the output of i-ADHoRe 3.0's installation tests.


## i-ADHoRe output
### Data structure

>For more information on the i-ADHoRe algorithm please refer to the [i-ADHoRe publication](#publication), and software manual, which is included in the i-ADHoRe download.

The data stucture of i-ADHoRe's output centres around *multiplicons*, which are mutually homologous segments of the input sequences. These are generated in i-ADHoRe 3.0 by an iterative process that generates a branching tree of progressively more refined multiplicons at distinct 'levels', which broadly represent the number of alignments that contribute to the region. The result of this process is recorded in the output plain text tab-separated tabular file `multiplicons.txt`.

`multiplicons.txt` describes all multiplicons generated during the analysis, including a large number of redundant multiplicons. Each multiplicon is assigned to a row in the table, and gets a unique ID in the `id` column. The `parent` column in each row refers to this ID, and the branching process that generates all multiplicons is easily reconstructed as a tree from this information. The root node of each tree corresponds to a "level 2" multiplicon. Leaf nodes (which have no children because no other homologous segment could be added to the stack) correspond to the "final" multiplicons.

The `segments.txt` output file is a plain text tab-separated file describing the regions of each inout genome that participate in each multiplicon, in terms of contigous aligned genes. Each row in the table represents an input genome region, with a unique ID in the column `id`, and defined by the first and last gene to contribute to that region. 

Each multiplicon corresponds to at least two regions in the `segments.txt` file, and the unique multiplicon ID is indicated in the column `multiplicon`, allowing for cross-reference against the multiplicon tree.

### Parsing

The object model is constructed around a directed graph that represents the multiplicon tree, using the `network.DiGraph()` object. Nodes represent multiplicons, and each edge represents a parent-child relationship. A local [SQLite](http://www.sqlite.org/) database is constructed (in memory, by default) to hold multiplicon attributes, obtained from the `multiplicons.txt` and `segments.txt` files, and enable fast querying.



