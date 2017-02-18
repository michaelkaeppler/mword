# -*- coding: utf-8 -*-
"""
Created on Sat Feb 18 20:16:59 2017

@author: Mael
"""

from collections import Counter as Cntr

def postprocess_list(mwords, **kwargs):
    if kwargs is None: # No kwargs passed, use default values in kwargs.get
        kwargs = {}
    sortorder = kwargs.get('sortorder', 'alphabetic')
    minlen = kwargs.get('minlen', 3)
    minocc = kwargs.get('minocc', 1)
    remove_upper = kwargs.get('removeupper', True)
    mwords_counted = Cntr(mwords)
    props = {}
    props['total'] = sum(mwords_counted.values())
    
    # Remove upper-/lowercase duplicates, merge to lowercase
    for k,v in mwords_counted.items():
        if not k.islower():
            if k.lower() in mwords_counted:
                mwords_counted[k.lower()] += v
                del mwords_counted[k]
            
    # Remove words that 
    # 1. are shorter than minlen
    # 2. occur less frequently than minocc
    # 3. If remove_upper is True: remove words that consist from only uppercase characters
    if remove_upper:
        allowed_mword = lambda k,v: ((len (k) >= minlen) and (v >= minocc) and (k.upper() != k))
    else:
        allowed_mword = lambda k,v: ((len (k) >= minlen) and (v >= minocc))
    
    # Convert to list in order to make it sortable
    mwords_list = [(k,v) for k,v in mwords_counted.iteritems() if allowed_mword(k, v)]
    
    if sortorder == 'alphabetic':
        mwords_list.sort()
    elif sortorder == 'occurrence':
        mwords_list.sort(key=lambda item: item[1])
    elif sortorder == 'importance':
        # Multiply word length with occurrences
        mwords_list.sort(key=lambda item: len(item[0]) * item[1])
        
    props['unique'] = len(mwords_list)
    return (mwords_list, props)