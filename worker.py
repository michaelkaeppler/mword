# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 21:53:56 2017

@author: Mael
"""

import logging
from multiprocessing import Process
import re

musical_regex = re.compile(r'^([a-hs]|cis|dis|fis|gis)+$', flags=(re.IGNORECASE))

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