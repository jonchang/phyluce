#!/usr/bin/env python
# encoding: utf-8

"""
change_taxa_names.py

Created by Brant Faircloth on 22 September 2010 12:48 PDT (-0700).
Copyright (c) 2010 Brant C. Faircloth. All rights reserved.

PURPOSE:  Remove the UCE locus name from nexus alignments.

USAGE:  python remove_locus_name_from_nexus_lines.py \
    --input my/input/folder/nexus \
    --output my/input/folder/nexus-renamed
"""


import os
import re
import sys
import glob
import argparse
import multiprocessing

from Bio import AlignIO
from Bio.Alphabet import generic_dna
from Bio.Align import MultipleSeqAlignment
from phyluce.helpers import FullPaths, is_dir, CreateDir, get_alignment_files

from phyluce.log import setup_logging

# import pdb


def get_args():
    """Get arguments from CLI"""
    parser = argparse.ArgumentParser(
            description="""Remove the UCE locus name from nexus alignments.""")
    parser.add_argument(
        "--alignments",
        required=True,
        action=FullPaths,
        type=is_dir,
        help="""The input directory containing nexus files to filter"""
    )
    parser.add_argument(
        "--output",
        required=True,
        action=CreateDir,
        help="""The output directory to hold the converted nexus files""",
    )
    parser.add_argument(
        "--taxa",
        type=int,
        default=None,
        help="""The expected number of taxa in all alignments""",
    )
    parser.add_argument(
        "--input-format",
        choices=["fasta", "nexus", "phylip", "clustal", "emboss", "stockholm"],
        default="nexus",
        help="""The input alignment format.""",
    )
    parser.add_argument(
        "--output-format",
        choices=["fasta", "nexus", "phylip", "clustal", "emboss", "stockholm"],
        default="nexus",
        help="""The output alignment format.""",
    )
    parser.add_argument(
        "--verbosity",
        type=str,
        choices=["INFO", "WARN", "CRITICAL"],
        default="INFO",
        help="""The logging level to use."""
    )
    parser.add_argument(
        "--log-path",
        action=FullPaths,
        type=is_dir,
        default=None,
        help="""The path to a directory to hold logs."""
    )
    parser.add_argument(
        "--cores",
        type=int,
        default=1,
        help="""Process alignments in parallel using --cores for alignment. """ +
        """This is the number of PHYSICAL CPUs."""
    )
    return parser.parse_args()


def get_files(input_dir):
    return glob.glob(os.path.join(os.path.expanduser(input_dir), '*.nex*'))


def worker(work):
    all_taxa = []
    args, f = work
    new_align = MultipleSeqAlignment([], generic_dna)
    for align in AlignIO.parse( f, 'nexus'):
        for seq in list(align):
            fname = os.path.splitext(os.path.basename(f))[0]
            new_seq_name = re.sub("^(_R_)*{}_*".format(fname), "", seq.name)
            all_taxa.append(new_seq_name)
            seq.id = new_seq_name
            seq.name = new_seq_name
            new_align.append(seq)
    if args.taxa is not None:
        assert len(all_taxa) == args.taxa, "Taxon names are not identical"
    outf = os.path.join(args.output, os.path.split(f)[1])
    try:
        with open(outf, 'w') as outfile:
            AlignIO.write(new_align, outfile, 'nexus')
        sys.stdout.write(".")
        sys.stdout.flush()
    except ValueError:
        raise IOError("Cannot write output file.")
    return all_taxa

def main():
    args = get_args()
    # setup logging
    log, my_name = setup_logging(args)
    files = get_alignment_files(log, args.alignments, args.input_format)
    work = [(args, f) for f in files]
    sys.stdout.write("Running")
    sys.stdout.flush()
    if args.cores > 1:
        assert args.cores <= multiprocessing.cpu_count(), "You've specified more cores than you have"
        pool = multiprocessing.Pool(args.cores)
        results = pool.map(worker, work)
    else:
        results = map(worker, work)
    # flatten results
    all_taxa = set([item for sublist in results for item in sublist])
    print ""
    log.info("Taxon names in alignments: {0}".format(
        ','.join(list(all_taxa))
    ))
    # end
    text = " Completed {} ".format(my_name)
    log.info(text.center(65, "="))

if __name__ == '__main__':
    main()
