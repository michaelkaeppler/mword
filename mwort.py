# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 21:53:56 2017

@author: Mael
"""

from os.path import getsize, isfile
import argparse
import logging
import collections
from tqdm import trange
from multiprocessing import Process, Manager, cpu_count
import re

# Local imports
from Counter import Counter

musical_regex = re.compile(r'^([a-hs]|cis|dis|fis|gis)+$', flags=(re.IGNORECASE))


def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
         raise argparse.ArgumentTypeError("{} is an invalid positive int value".format(value))
    return ivalue

def get_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    cpus = cpu_count()
    parser.add_argument("filename", help="File that shall be parsed")
    parser.add_argument("-m", "--minlength", type=check_positive, default=3, help="Minimum word length to parse")
    parser.add_argument("-p", "--processes", type=check_positive, default=cpus, help="Number of processes")
    parser.add_argument("-c", "--chunksize", type=check_positive, default=100, help="Size of chunks in KByte, that are read at once")
    parser.add_argument("-l", "--loglevel", type=str, choices=["OFF", "INFO", "DEBUG"], default="OFF", help="Set loglevel")
    parser.add_argument("-lf", "--logfile", type=str, default="mwort.log", help="Set where to write log messages")
    return parser.parse_args()
    
def worker(nr, input_queue, mword_list, word_count):
     logger = logging.getLogger("Process "+str(nr))
     logger.debug("Starting")
     while True:
        queue_item = input_queue.get()
        if queue_item is None:
            logger.debug("Queue is empty, terminating")  
            return
        else:
            chunk_nr, word_string = queue_item
            logger.debug("Getting chunk {} from queue".format(chunk_nr))
            words = word_string.split()
            word_count.increment(len(words))
            logger.debug("Split chunk {} in {} {word_des}".format(chunk_nr, len(words), word_des="word" if len(words) < 2 else "words"))
            mwords = [word for word in words if musical_regex.match(word)]
            logger.debug("Got {} musical {word_des}".format(len(mwords), word_des="word" if len(words) < 2 else "words"))
            mword_list.extend(mwords)
    
def get_worker_pool(num, worker, input_queue, mword_list, word_count):
    pool = []
    for i in xrange(num):
        p = Process(target=worker, args=(i, input_queue, mword_list, word_count))
        p.start()
        pool.append(p)
    return pool
        
def get_chunk(f, size):
    chunk = f.read(size)
    while True: # Read additional characters until whitespace 
        ch = f.read(1)
        if ch.isspace() or (not ch):
            break
        chunk += ch
    return chunk
    
def postprocess_list(mwords, **kwargs):
    if kwargs is None: # No kwargs passed, use default values in kwargs.get
        kwargs = {}
    sortorder = kwargs.get('sortorder', 'alphabetic')
    minlen = kwargs.get('minlen', 3)
    minocc = kwargs.get('minocc', 1)
    remove_upper = kwargs.get('removeupper', True)
    mwords_counted = collections.Counter(mwords)
    props = {}
    props['total'] = sum(mwords_counted.values())
    # Remove words that 
    # 1. are shorter than minlen
    # 2. occur less frequently than minocc
    mwords_counted = {k:v for k,v in mwords_counted.items() if
                        (len(k) >= minlen) and (v >= minocc)}
    # Remove words than consist from only uppercase characters
    if remove_upper:
        mwords_counted = {k:v for k,v in mwords_counted.items() if
                        k.upper() != k}
    if sortorder == 'alphabetic':
        mwords_unique = sorted(mwords_counted)
    props['unique'] = len(mwords_unique)
    return (mwords_counted, mwords_unique, props)
    
        
def main():
    args = get_args()
    
    fname = args.filename
    processes = args.processes
    chunk_size = args.chunksize*1000 # Size is given in KByte, internal calculation is done in Bytes    
    logfile = args.logfile
    
    if args.loglevel != "OFF":
        if args.loglevel == "INFO":
            loglevel = logging.INFO
        elif args.loglevel == "DEBUG":
            loglevel = logging.DEBUG
        
        logging.basicConfig(
        level=loglevel,
        format="%(asctime)s:%(levelname)s:%(name)s:%(message)s",
        filename=logfile,
        filemode="w"
        )
    
    main_logger = logging.getLogger("Main")
    
    if isfile(fname):
        fsize = getsize(fname) # Returns size in bytes
        with open(fname) as f:
            print "Opened file {}, size {:,} bytes".format(fname, fsize) 
            chunks = fsize // chunk_size
            if fsize % chunk_size != 0:
                chunks += 1
            if chunks == 1:
                chunk_size = fsize
                
            print "Splitting file in {} {chunk_des} of size {:,} bytes".format(chunks, chunk_size, chunk_des="chunk" if chunks < 2 else "chunks")
            manager = Manager()
            mwords = manager.list()
            word_count = Counter()
            work = manager.Queue(processes)
            print "Starting {} {proc_des}...".format(processes, proc_des="process" if processes < 2 else "processes")
            pool = get_worker_pool(processes, worker, work, mwords, word_count)
            
            for chunk_nr in trange(1, chunks+1):
                chunk = get_chunk(f, chunk_size)
                work.put((chunk_nr, chunk))
                main_logger.debug("Working on chunk {} of {}".format(chunk_nr, chunk_size))
            
            for i in xrange(processes):
                work.put(None) # Send termination signal for each process
            
            for p in pool:
                p.join()
                
            mwords_counted, mwords_unique, props = postprocess_list(mwords)
            mwords_total_count = props['total']
            mwords_unique_count = props['unique']
            mwords_total_percent = mwords_total_count * 100.0 / word_count.value()
            mwords_unique_percent = mwords_unique_count * 100.0 / word_count.value()
            print "Searched through {} words".format(word_count.value())
            print "Found {} ({:.1f}%) musical {word_des}, {} ({:.1f}%) of them unique".format(mwords_total_count, mwords_total_percent, mwords_unique_count, mwords_unique_percent, word_des="word" if mwords_total_count < 2 else "words")
            for k, v in mwords_counted.items():
                print "{}: {} times".format(k, v)
                                                                            
    else:
        print "Can't find file {}, exiting.".format(fname)

if __name__ == "__main__":
    main()
