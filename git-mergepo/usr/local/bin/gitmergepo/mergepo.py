#!/usr/bin/env python
#
# https://www.kernel.org/pub/software/scm/git/docs/gitattributes.html
#
# %O: ancestor's version
# %A: current version
# %B: other branch version
#
import os
import shutil
import sys
import tempfile
import time
from polib import POFile, pofile


def makedict(pof):
    dictionary = {}
    for entry in pof:
        dictionary[entry.msgid] = entry
    return dictionary


def delete_key(key, dictionary):
    if key in dictionary:
        del dictionary[key]


def merge_entry(oentry, aentry, bentry, branchname):
    """
    Merges po entries. It uses 3 different version to correctly merge an entry

    Usual 3-way file level merge for text files. Conflicted regions are marked with conflict
    markers <<<<<<<, ======= and >>>>>>>. The version from your branch appears before the ======= marker, and the
    version from the merged branch appears after the ======= marker.

    @param oentry: entry from the ancestor's version
    @param aentry: entry from the current version
    @param bentry: entry from the other branch version
    @type oentry: POEntry
    @return: tuple with correct entry and boolean it is conflicted or not
    """
    conflict = False
    result = oentry

    if aentry and not bentry:
        # 1. New aentry
        result = aentry
    elif not aentry and bentry:
        # 2. New bentry
        result = bentry
    elif aentry and bentry:
        # 3. Entries already exists
        if oentry and oentry.msgstr == aentry.msgstr and oentry.msgstr == bentry.msgstr:
            # Nothing changed
            result = oentry
        elif oentry and oentry.msgstr == aentry.msgstr and oentry.msgstr != bentry.msgstr:
            # aentry updated
            result = bentry
        elif oentry and oentry.msgstr != aentry.msgstr and oentry.msgstr == bentry.msgstr:
            # bentry updated
            result = aentry
        else:
            # Merge conflict, aentry and bentry have been changed
            #print "Conflict ", str(oentry.msgstr), ", ", str(aentry.msgstr), ", ", str(bentry.msgstr)
            #aentry.merge(bentry)
            buf = ['<<<<<<< HEAD', aentry.msgstr, '=======', bentry.msgstr, '>>>>>>> %s' % branchname]
            aentry.msgstr = '\n'.join(buf)
            result = aentry
            conflict = True
    return result, conflict


def mergepo(o, a, b):
    workingpath = os.getcwd()

    ofile = pofile(os.path.join(workingpath, o))
    odict = makedict(ofile)
    afile = pofile(os.path.join(workingpath, a))
    adict = makedict(afile)
    bfile = pofile(os.path.join(workingpath, b))
    bdict = makedict(bfile)

    temp_dir = tempfile.mkdtemp('', 'gitmergepo-')
    #temp_file = tempfile.mkstemp(dir=temp_dir)
    temp_po = POFile()
    conflicts = 0

    # Process all the ancestor entries
    for oentry in ofile:
        aentry = adict.get(oentry.msgid, None)
        bentry = bdict.get(oentry.msgid, None)
        result = merge_entry(oentry, aentry, bentry, b)
        odict[oentry.msgid] = result[0]
        delete_key(oentry.msgid, adict)
        delete_key(oentry.msgid, bdict)

        if result[1]:
            conflicts += 1

    # Process newly created entries in a & b
    for key, value in adict.iteritems():
        bentry = bdict.get(key, None)
        result = merge_entry(None, value, bentry, b)
        odict[key] = result[0]
        delete_key(key, bdict)

        if result[1]:
            conflicts += 1

    # Process newly created entries in b
    for key, value in bdict.iteritems():
        odict[value.msgid] = value

    # Append all entries to the temp po file
    for key, value in odict.iteritems():
        temp_po.append(value)

    # Export the merged po file
    temp_po.metadata = afile.metadata
    temp_po.header = 'Merged by git-mergepo ...' + temp_po.header
    #temp_po.save(fpath=temp_file[1])
    temp_po.save(fpath=a)
    shutil.rmtree(temp_dir)

    #print 'Dicts: ', len(odict), ', ', len(adict), ', ', len(bdict)
    #print 'Path: ', workingpath
    #print 'Conflicts: ', conflicts

    # If conflicts were found we exit with status 1
    if conflicts > 0:
        print '\n!!! TRANSLATION CONFLICTS: %s !!!\n' % conflicts
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    start = time.time()
    # sys.argv[0] is the file itself
    mergepo(sys.argv[1], sys.argv[2], sys.argv[3])
    print 'Exec ', time.time() - start, 'seconds.'

