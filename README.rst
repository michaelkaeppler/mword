MWORD -- Find musical words
============================
Description
------------
mword.py reads a text file and searches for words that can be
expressed solely with note names, e.g. 'Bach' in german language b - a - c - h

Operating mode
---------------
The following steps are carried out during the search process:

1. The file is split into chunks of a certain configurable size
2. The chunks are put into a queue, from which several processes read them
3. Each process splits the chunks into "words" by splitting the chunk on each whitespace character
4. The resulting word list is parsed one by one with a regular expression
5. If the RegEx matches and the word can be expressed with note names only, the word is put into a result list that is shared among the processes
6. After iterating through the whole file, the word list is postprocessed (filtered and sorted) according to some criteria specified beforehand
7. The resulting word list is output to stdout together with some small statistics

Usage
------
python mword.py tests/files/neverending_story.txt

Some options:

1. Set number of processes to 4, e.g. for a Quad-Core machine: **python mword.py -p 4 FILE**
2. Only match words that are at least three characters long and occur at least two times: **python mword.py -m 3 -o 2 FILE**

3. Set loglevel and logfile: **python mword.py -l DEBUG -lf debug.log FILE**

4. Remove words consisting only from UPPERCASE characters, sort words by length: **python mword.py -ru -sortorder length FILE**
