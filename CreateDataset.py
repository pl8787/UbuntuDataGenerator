#! author: pl8787
#! coding: utf-8

from Dialogue import Dialogue
from glob import glob
import sys
import os

def process_dir(src_dir, dest_file):
    print src_dir, '->', dest_file
    diag_files = glob(src_dir + '/*.tsv')
    print 'Total %d files need to be process.' % len(diag_files)

    out_ = open(dest_file, 'w')
    
    for idx, diag_file in enumerate(diag_files):
        diag = Dialogue(diag_file)
        diag.clean_string = True
        diag.enable_tags = True
        diag.initialize()
        if diag.isvalid:
            print >>out_, '\n'.join( [diag.filename, diag.print_users(), diag.print_utters()] )
            print >>out_, ''
        if idx % 100 == 0:
            print '\r%.2f%%' % (100.0*idx/len(diag_files)),
            sys.stdout.flush()

    print '\r100.00%%'
    out_.close()

if __name__ == "__main__":
    src_dirs = glob('/home/pangliang/matching/data/ubuntu/dialogs_sample/*')
    dest_dir = '/home/pangliang/matching/data/ubuntu/dialogs_processed_tag/'
    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)
    for sub_src_dir in src_dirs:
        print sub_src_dir
        sub_dir = sub_src_dir.split('/')[-1]
        process_dir(sub_src_dir, dest_dir + sub_dir + '.txt')


