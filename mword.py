# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 21:53:56 2017

@author: Mael
"""
from __future__ import print_function
from __future__ import absolute_import

from builtins import range
from os.path import getsize, isfile
import logging
from tqdm import trange
from multiprocessing import Manager

# Local imports
from mword.counter import Counter
from mword.worker import worker, get_worker_pool
from mword.argparser import get_args
from mword.postprocess import postprocess_list
        
def get_chunk(f, size):
    chunk = f.read(size)
    while True: # Read additional characters until whitespace 
        ch = f.read(1)
        if ch.isspace() or (not ch):
            break
        chunk += ch
    return chunk    
        
def main():
    args = get_args()
    
    fname = args.filename
    processes = args.processes
    chunk_size = args.chunksize*1000 # Size is given in KByte, internal calculation is done in Bytes    
    logfile = args.logfile
    sortorder = args.sortorder
    minlen = args.minlength
    minocc = args.minocc
    remove_upper = args.removeupper
    
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
        with open(fname, encoding="latin1") as f:
            print("Opened file {}, size {:,} bytes".format(fname, fsize)) 
            chunks = fsize // chunk_size
            if fsize % chunk_size != 0:
                chunks += 1
            if chunks == 1:
                chunk_size = fsize
                
            print("Splitting file in {} {chunk_des} of size {:,} bytes".format(chunks, chunk_size, chunk_des="chunk" if chunks < 2 else "chunks"))
            manager = Manager()
            mwords = manager.list()
            word_count = Counter()
            work = manager.Queue(processes)
            print("Starting {} {proc_des}...".format(processes, proc_des="process" if processes < 2 else "processes"))
            pool = get_worker_pool(processes, worker, work, mwords, word_count)
            
            for chunk_nr in trange(1, chunks+1):
                chunk = get_chunk(f, chunk_size)
                work.put((chunk_nr, chunk))
                main_logger.debug("Working on chunk {} of {}".format(chunk_nr, chunk_size))
            
            for i in range(processes):
                work.put(None) # Send termination signal for each process
            
            for p in pool:
                p.join()
                
            mwords_list, props = postprocess_list(mwords, sortorder=sortorder, minlen=minlen, minocc=minocc, remove_upper=remove_upper)
            mwords_total_count = props['total']
            mwords_unique_count = props['unique']
            mwords_total_percent = mwords_total_count * 100.0 / word_count.value()
            mwords_unique_percent = mwords_unique_count * 100.0 / word_count.value()
            print("Searched through {} words".format(word_count.value()))
            print("Found {} ({:.1f}%) musical {word_des}, {} ({:.2f}%) of them unique".format(mwords_total_count, mwords_total_percent, mwords_unique_count, mwords_unique_percent, word_des="word" if mwords_total_count < 2 else "words"))
            print("+++ BEGIN MUSICAL WORDS +++")
            for mword in mwords_list:
                print("{} : {} times".format(mword[0], mword[1]))
            print("+++ END MUSICAL WORDS +++")
                                                                            
    else:
        print("Can't find file {}, exiting.".format(fname))

if __name__ == "__main__":
    main()
