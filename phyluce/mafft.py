#!/usr/bin/env python
# encoding: utf-8
"""
File: mafft.py
Author: Brant Faircloth

Created by Brant Faircloth on 10 March 2012 09:03 PST (-0800)
Copyright (c) 2012 Brant C. Faircloth. All rights reserved.

Description: Alignement class wrapping MAFFT aligner
(http://mafft.cbrc.jp/alignment/software/)

"""


import os
import tempfile
import subprocess

from Bio import AlignIO
from Bio.Alphabet import IUPAC, Gapped

from phyluce.helpers import which
from phyluce.generic_align import GenericAlign

import pdb


class Align(GenericAlign):
    """ MAFFT alignment class.  Subclass of GenericAlign which
    contains a majority of the alignment-related helper functions
    (trimming, etc.) """

    def __init__(self, input):
        """initialize, calling superclass __init__ also"""
        super(Align, self).__init__(input)

    def run_alignment(self, clean=True):
        mafft = which("mafft")
        # create results file
        fd, aln = tempfile.mkstemp(suffix='.mafft')
        os.close(fd)
        aln_stdout = open(aln, 'w')
        # run MAFFT on the temp file
        cmd = [mafft, "--adjustdirection", "--maxiterate", "1000", self.input]
        # just pass all ENV params
        proc = subprocess.Popen(cmd,
                stderr=subprocess.PIPE,
                stdout=aln_stdout
            )
        stderr = proc.communicate()
        aln_stdout.close()
        self.alignment = AlignIO.read(open(aln, 'rU'), "fasta", \
                alphabet=Gapped(IUPAC.unambiguous_dna, "-"))
        if clean:
            self._clean(aln)


if __name__ == '__main__':
    pass
