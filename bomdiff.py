"""
BOM Diff
Copyright (C) 2024 Eric Schlaepfer

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

import csv
import sys

# Steps for this program
# 1. Provide a list of new components
# 2. Provide a list of deleted components
# 3. Provide a list of changed quantities

def getcol(header_list, name_list):
    for n in name_list:
        try:
            return header_list.index(n)
        except ValueError:
            pass
    raise ValueError("Header not found: %s" % (', '.join(name_list)))

def loadparts(filename):
    f1 = open(filename, 'r', newline='')
    cf1 = csv.reader(f1)

    # Read header, remove extra whitespace
    h = [d.strip() for d in next(cf1)]

    # Figure out what the columns mean.
    col_quantity = getcol(h, ['Quantity', 'Q'])
    col_des = getcol(h, ['Designator', 'RefDes', 'Ref'])
    col_mpn = getcol(h, ['Manufacturer Part Number 1', 'MPN', 'Part Number'])    
    current_row = 2
    # Now put together a dictionary of MPNs with the value set to the des list
    parts = {}
    for row in cf1:
        # Turn designators into a real list object
        q = int(row[col_quantity])
        des = [t.strip() for t in row[col_des].split(',')]
        mpn = row[col_mpn].strip()

        if q != len(des):
            print("WARNING: %s line %d: quantity is %d, but there are %d designators" % (filename, current_row, q, len(des)))

        # Add to our dictionary
        if mpn not in parts:
            parts[mpn] = des
        else:
            parts[mpn] += (des)
        current_row += 1
    f1.close()
    return parts

def print_line_item(mpn, des):
    print('  ' + mpn + ': ', ', '.join(des))

if len(sys.argv) != 3:
    print("Usage: %s from.csv to.csv" % sys.argv[0])
    quit()

parts_from = loadparts(sys.argv[1])
parts_to = loadparts(sys.argv[2])

# Look for added parts
added = list(set(parts_to) - set(parts_from))
if added:
    print("** NEW LINE ITEMS **")
    for p in added:
        print_line_item(p, parts_to[p])

# Removed parts
removed = list(set(parts_from) - set(parts_to))
if removed:
    print("** REMOVED LINE ITEMS **")
    for p in removed:
        print_line_item(p, parts_from[p])

# Quantity changes
printed_quantity_banner = False
for p in parts_from:
    if p in parts_to:
        l1 = parts_from[p]
        l2 = parts_to[p]
        st = ''
        if len(l1) != len(l2):
            st = '  Was: %d. Now: %d.' % (len(l1), len(l2))
        # Compare the lists
        addlist = list(set(l2) - set(l1))
        sublist = list(set(l1) - set(l2))
        if len(addlist): st += ' Added ' + ', '.join(addlist)
        if len(sublist): st += ' Removed ' + ', '.join(sublist)
        if st:
            if not printed_quantity_banner:
                print("** QUANTITY CHANGES **")
                printed_quantity_banner = True 
            print ('  ' + p + ': ' + st)
