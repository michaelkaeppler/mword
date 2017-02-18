# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 21:53:56 2017

@author: Mael
"""

import argparse
from multiprocessing import cpu_count

def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
         raise argparse.ArgumentTypeError("{} is an invalid positive int value".format(value))
    return ivalue

def get_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    cpus = cpu_count()
    parser.add_argument("filename", help="File that shall be parsed")
    parser.add_argument("-p", "--processes", type=check_positive, default=cpus, help="Number of processes")
    parser.add_argument("-c", "--chunksize", type=check_positive, default=100, help="Size of chunks in KByte, that are read at once")
    parser.add_argument("-m", "--minlength", type=check_positive, default=3, help="Minimum length words must have")    
    parser.add_argument("-o", "--minocc", type=check_positive, default=1, help="Minimal occurrences words must have")    
    parser.add_argument("-s", "--sortorder", type=str, choices=["alphabetic", "occurrence", "length"], default="alphabetic", help="Set sort order")
    parser.add_argument("-ru", "--removeupper", action="store_true", help="Remove words that consist only of UPPERCASE characters")
    parser.add_argument("-l", "--loglevel", type=str, choices=["OFF", "INFO", "DEBUG"], default="OFF", help="Set loglevel")
    parser.add_argument("-lf", "--logfile", type=str, default="mwort.log", help="Set where to write log messages")
    return parser.parse_args()