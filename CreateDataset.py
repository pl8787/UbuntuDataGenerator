#! author: pl8787
#! coding: utf-8

from Dialogue import Dialogue
from glob import glob
import sys
import os
import random

def process_dir(src_dir, dest_file):
    print src_dir, '->', dest_file
    diag_files = glob(src_dir + '/*.tsv')
    print 'Total %d files need to be process.' % len(diag_files)

    out_ = open(dest_file, 'w')
    
    for idx, diag_file in enumerate(diag_files):
        diag = Dialogue(diag_file)
        diag.clean_string = True
        diag.enable_tags = False
        diag.initialize()
        if diag.isvalid:
            print >>out_, '\n'.join( [diag.filename, diag.print_users(), diag.print_utters()] )
            print >>out_, ''
        if idx % 100 == 0:
            print '\r%.2f%%' % (100.0*idx/len(diag_files)),
            sys.stdout.flush()

    print '\r100.00%%'
    out_.close()

def process_dataset(src_root, dest_dir):
    src_dirs = glob('%s/*' % src_root)
    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)
    for sub_src_dir in src_dirs:
        print sub_src_dir
        sub_dir = sub_src_dir.split('/')[-1]
        process_dir(sub_src_dir, dest_dir + sub_dir + '.txt')

def read_format_data(src_root):
    src_files = glob('%s/*' % src_root)
    diag_list = []
    for f in src_files:
        print 'Read %s.' % f
        lines = open(f).read().split('\n\n')[:-1]
        for line in lines:
            line = line.split('\n')
            diag = Dialogue(line[0], line[2], line[1])
            diag_list.append(diag)
    print 'Read diag length:', len(diag_list)
    return diag_list

def write_file_set(diag_list, filename):
    out_ = open(filename, 'w')
    for diag in diag_list:
        fname = diag.filename.split('/')
        print >>out_, ','.join([fname[-1], fname[-2]])
    out_.close()

def read_file_set(filename):
    diag_set = set()
    for line in open(filename):
        diag_set.add(line.strip())
    return diag_set

def split_3_set(diag_list, split_file = {}, rate = 0.1):
    if split_file:
        train_diag_set = read_file_set(split_file['train'])
        valid_diag_set = read_file_set(split_file['valid'])
        test_diag_set = read_file_set(split_file['test'])
        train_diag_list = []
        valid_diag_list = []
        test_diag_list = []
        for diag in diag_list:
            fname = diag.filename.split('/')
            key = ','.join([fname[-1], fname[-2]])
            if key in train_diag_set:
                train_diag_list.append(diag)
            if key in valid_diag_set:
                valid_diag_list.append(diag)
            if key in test_diag_set:
                test_diag_list.append(diag)
    else:
        random.shuffle(diag_list)
        test_size = int(0.1 * len(diag_list))
        test_diag_list = diag_list[ : test_size]
        valid_diag_list = diag_list[test_size : 2*test_size]
        train_diag_list = diag_list[2*test_size : ]
        # Output partition
        write_file_set(train_diag_list, 'partition/train_files.csv')
        write_file_set(valid_diag_list, 'partition/valid_files.csv')
        write_file_set(test_diag_list, 'partition/test_files.csv')

    print 'Train size:', len(train_diag_list)
    print 'Valid size:', len(valid_diag_list)
    print 'Test size:', len(test_diag_list)

    return train_diag_list, valid_diag_list, test_diag_list

def generate_diag_dict(diag_list):
    diag_dict = {}
    for idx, diag in enumerate(diag_list):
        fname = diag.filename.split('/')
        key = ','.join([fname[-1], fname[-2]])
        diag_dict[key] = idx
    print 'Diag dict size:', len(diag_dict)
    return diag_dict

def sample_negative(diag_list, diag_dict, negative_count):
    negative_response = {}
    diag_dict_keys = diag_dict.keys()
    for key in diag_dict:
        neg_list = []
        neg_diag_rnd = None
        for idx in range(negative_count):
            while not neg_diag_rnd or neg_diag_rnd == key:
                neg_diag_rnd = random.choice(diag_dict_keys)
            neg_line_rnd = random.choice(range(len( diag_list[diag_dict[neg_diag_rnd]].utterlist )))
            neg_list.append( (neg_diag_rnd, neg_line_rnd) )
        negative_response[key] = neg_list
    print 'Negative response size:', len(negative_response)
    return negative_response

def generate_instance(diag_list, negative_response, max_pos_per_diag, neg_per_pos):
    min_window = 2
    instances = []
    for diag in diag_list:
        n = len(diag.utterlist)
        max_ins = (n-2)*(n-1)/2
        for idx in range(min(max_ins, max_pos_per_diag)):
            ins = [[],[]]
            winsize_rnd = random.choice(range(min_window, n))
            pos_rnd = random.choice(range(n-winsize_rnd))
            ins[0] = (diag.key, winsize_rnd, pos_rnd)
            ins[1] = negative_response[diag.key][idx * neg_per_pos : (idx+1) * neg_per_pos]
            instances.append(ins)
    print 'Instance count:', len(instances)
    return instances

def write_instance(instances, diag_list, diag_dict, word_dict, profile, txtfile, datafile):
    profile_ = open(profile, 'w')
    for ins in instances:
        print >>profile_, ':'.join(map(str, ins[0])), \
                ' '.join([':'.join(map(str, x)) for x in ins[1]])
    profile_.close()
    if not datafile:
        return
    txtfile_ = open(txtfile, 'w')
    datafile_ = open(datafile, 'w')
    for idx, ins in enumerate(instances):
        # Write Positive
        pos_diag = diag_list[diag_dict[ins[0][0]]]
        pos_context = '__eos__'.join(pos_diag.utterlist[ins[0][2] : ins[0][2] + ins[0][1]]) + '__eos__'
        pos_response = pos_diag.utterlist[ins[0][2] + ins[0][1]] + '__eos__'
        print >>txtfile_, '\t'.join( ['1', pos_context, pos_response] )
        pos_context_sp = [str(word_dict[w]) for w in pos_context.split() if w in word_dict]
        pos_response_sp = [str(word_dict[w]) for w in pos_response.split() if w in word_dict]
        print >>datafile_, 1, len(pos_context_sp), len(pos_response_sp), \
                ' '.join( pos_context_sp ), \
                ' '.join( pos_response_sp )
        # Write Negative
        for neg in ins[1]:
            neg_diag = diag_list[diag_dict[neg[0]]]
            neg_response = neg_diag.utterlist[neg[1]] + '__eos__'
            print >>txtfile_, '\t'.join( ['0', pos_context, neg_response] )
            neg_response_sp = [str(word_dict[w]) for w in neg_response.split() if w in word_dict]
            print >>datafile_, 0, len(pos_context_sp), len(neg_response_sp), \
                    ' '.join( pos_context_sp ), \
                    ' '.join( neg_response_sp ) 

        if idx % 1000 == 0:
            print '\r%.2f' % (100.0 * idx / len(instances)),
            sys.stdout.flush()
    print ''
    txtfile_.close()
    datafile_.close()

def generate_word_dict(diag_list):
    word_dict = {}
    word_frq = {}

    word_dict['__eos__'] = len(word_dict)
    word_frq['__eos__'] = 123456

    for diag in diag_list:
        for utter in diag.utterlist:
            for w in utter.split():
                if len(w) != 0:
                    if w not in word_dict:
                        word_frq[w] = 0
                        word_dict[w] = len(word_dict)
                    word_frq[w] += 1

    print 'Word count:', len(word_dict)
    out_ = open('word.dict', 'w')
    for w in word_dict:
        print >>out_, w, word_dict[w]
    out_.close()
    out_ = open('word.frq', 'w')
    for w in word_dict:
        print >>out_, w, word_frq[w]
    out_.close()
    return word_dict, word_frq


if __name__ == "__main__":
    dir_tag = 'x.3.3.9'
    os.mkdir(dir_tag)
    # Step 1
    src_root = '/home/pangliang/matching/data/ubuntu/dialogs/'
    dest_dir = '/home/pangliang/matching/data/ubuntu/dialogs_processed/'
    process_dataset(src_root, dest_dir)
    # Step 2: Split dataset 2 train valid test
    processed_src_root = dest_dir
    diag_list = read_format_data(processed_src_root)
    train_diag_list, valid_diag_list, test_diag_list = split_3_set(diag_list, \
            {'train':'meta/trainfiles.csv', 'valid':'meta/valfiles.csv', 'test':'meta/testfiles.csv'})
    # Step 3: Generate Word dict
    word_dict, word_frq = generate_word_dict(diag_list)
    # Step 4: Negative Sample
    diag_dict = generate_diag_dict(diag_list)
    negative_count = 30
    negative_response = sample_negative(diag_list, diag_dict, negative_count)
    # Step 5: Generate Data
    max_pos_per_diag = 3
    neg_per_pos = 3
    train_instance = generate_instance(train_diag_list, negative_response, max_pos_per_diag, neg_per_pos)
    write_instance(train_instance, diag_list, diag_dict, word_dict, '%s/train.instance' % dir_tag, '%s/train.txt' % dir_tag, '%s/train.data' % dir_tag)
    neg_per_pos = 9
    valid_instance = generate_instance(valid_diag_list, negative_response, max_pos_per_diag, neg_per_pos)
    write_instance(valid_instance, diag_list, diag_dict, word_dict, '%s/valid.instance' % dir_tag, '%s/valid.txt' % dir_tag, '%s/valid.data' % dir_tag)
    neg_per_pos = 9
    test_instance = generate_instance(test_diag_list, negative_response, max_pos_per_diag, neg_per_pos)
    write_instance(test_instance, diag_list, diag_dict, word_dict, '%s/test.instance' % dir_tag, '%s/test.txt' % dir_tag, '%s/test.data' % dir_tag)




