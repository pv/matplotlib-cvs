"""
A collection of utility functions and classes.  Many (but not all)
from the Python Cookbook -- hence the name cbook
"""
from __future__ import generators
import re, os, errno, sys, StringIO, traceback


major, minor1, minor2, s, tmp = sys.version_info
if major<2 or (major==2 and minor1<3):
    True = 1
    False = 0
else:
    True = True
    False = False


class Bunch:
   """
   Often we want to just collect a bunch of stuff together, naming each
   item of the bunch; a dictionary's OK for that, but a small do- nothing
   class is even handier, and prettier to use.  Whenever you want to
   group a few variables:

     >>> point = Bunch(datum=2, squared=4, coord=12)
     >>> point.datum

     By: Alex Martelli
     From: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52308
   """
   def __init__(self, **kwds):
      self.__dict__.update(kwds)

def unique(x):
   'Return a list of unique elements of x'
   return dict([ (val, 1) for val in x]).keys()

def iterable(obj):
    try: len(obj)
    except: return 0
    return 1
      

def is_string_like(obj):
    if hasattr(obj, 'shape'): return 0 # this is a workaround
                                       # for a bug in numeric<23.1
    try: obj + ''
    except (TypeError, ValueError): return 0
    return 1


def is_file_like(obj):
    if hasattr(obj, 'shape'): return 0 # this is a workaround
                                       # for a bug in numeric<23.1
    try: obj + ''
    except (TypeError, ValueError): return 0
    return 1

def is_scalar(obj):
    return is_string_like(obj) or not iterable(obj)

def flatten(seq, scalarp=is_scalar):
    """
    this generator flattens nested containers such as

    >>> l=( ('John', 'Hunter'), (1,23), [[[[42,(5,23)]]]])

    so that

    >>> for i in flatten(l): print i,
    John Hunter 1 23 42 5 23

    By: Composite of Holger Krekel and Luther Blissett
    From: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/121294
    and Recipe 1.12 in cookbook
    """
    for item in seq:
        if scalarp(item): yield item
        else:
            for subitem in flatten(item, scalarp):
               yield subitem



class Sorter:
   """

   Sort by attribute or item

   Example usage:
   sort = Sorter()

   list = [(1, 2), (4, 8), (0, 3)]
   dict = [{'a': 3, 'b': 4}, {'a': 5, 'b': 2}, {'a': 0, 'b': 0},
   {'a': 9, 'b': 9}]


   sort(list)       # default sort
   sort(list, 1)    # sort by index 1
   sort(dict, 'a')  # sort a list of dicts by key 'a'
   
   """

   def _helper(self, data, aux, inplace):
      aux.sort()
      result = [data[i] for junk, i in aux]
      if inplace: data[:] = result
      return result

   def byItem(self, data, itemindex=None, inplace=1):
      if itemindex is None:
         if inplace:
            data.sort()
            result = data
         else:
            result = data[:]
            result.sort()
         return result
      else:
         aux = [(data[i][itemindex], i) for i in range(len(data))]
         return self._helper(data, aux, inplace)

   def byAttribute(self, data, attributename, inplace=1):
      aux = [(getattr(data[i],attributename),i) for i in range(len(data))]
      return self._helper(data, aux, inplace)

   # a couple of handy synonyms
   sort = byItem
   __call__ = byItem





class Xlator(dict):
    """
    All-in-one multiple-string-substitution class

    Example usage:

    text = "Larry Wall is the creator of Perl"
    adict = {
    "Larry Wall" : "Guido van Rossum",
    "creator" : "Benevolent Dictator for Life",
    "Perl" : "Python",
    }

    print multiple_replace(adict, text)

    xlat = Xlator(adict)
    print xlat.xlat(text)
    """

    def _make_regex(self):
        """ Build re object based on the keys of the current dictionary """
        return re.compile("|".join(map(re.escape, self.keys())))

    def __call__(self, match):
        """ Handler invoked for each regex match """
        return self[match.group(0)]

    def xlat(self, text):
        """ Translate text, returns the modified text. """
        return self._make_regex().sub(self, text)



def soundex(name, len=4):
    """ soundex module conforming to Odell-Russell algorithm """

    # digits holds the soundex values for the alphabet
    soundex_digits = '01230120022455012623010202'
    sndx = ''
    fc = ''

    # Translate letters in name to soundex digits
    for c in name.upper():
        if c.isalpha():
            if not fc: fc = c   # Remember first letter
            d = soundex_digits[ord(c)-ord('A')]
            # Duplicate consecutive soundex digits are skipped
            if not sndx or (d != sndx[-1]):
                sndx += d

    # Replace first digit with first letter
    sndx = fc + sndx[1:]

    # Remove all 0s from the soundex code
    sndx = sndx.replace('0', '')

    # Return soundex code truncated or 0-padded to len characters
    return (sndx + (len * '0'))[:len]



class Null:
    """ Null objects always and reliably "do nothing." """

    def __init__(self, *args, **kwargs): pass
    def __call__(self, *args, **kwargs): return self
    def __str__(self): return "Null()"
    def __repr__(self): return "Null()"
    def __nonzero__(self): return 0

    def __getattr__(self, name): return self
    def __setattr__(self, name, value): return self
    def __delattr__(self, name): return self




def mkdirs(newdir, mode=0777):
   try: os.makedirs(newdir, mode)
   except OSError, err:
      # Reraise the error unless it's about an already existing directory 
      if err.errno != errno.EEXIST or not os.path.isdir(newdir): 
         raise


class RingBuffer:
    """ class that implements a not-yet-full buffer """
    def __init__(self,size_max):
        self.max = size_max
        self.data = []

    class __Full:
        """ class that implements a full buffer """
        def append(self, x):
            """ Append an element overwriting the oldest one. """
            self.data[self.cur] = x
            self.cur = (self.cur+1) % self.max
        def get(self):
            """ return list of elements in correct order """
            return self.data[self.cur:]+self.data[:self.cur]

    def append(self,x):
        """append an element at the end of the buffer"""
        self.data.append(x)
        if len(self.data) == self.max:
            self.cur = 0
            # Permanently change self's class from non-full to full
            self.__class__ = __Full

    def get(self):
        """ Return a list of elements from the oldest to the newest. """
        return self.data

    def __get_item__(self, i):
       return self.data[i % len(self.data)]




# until 2.3
def enumerate(seq):
     for i in range(len(seq)):
         yield i, seq[i]



def get_split_ind(seq, N):
   """seq is a list of words.  Return the index into seq such that
   len(' '.join(seq[:ind])<=N
   """
  
   sLen = 0
   # todo: use Alex's xrange pattern from the cbook for efficiency
   for (word, ind) in zip(seq, range(len(seq))):
      sLen += len(word) + 1  # +1 to account for the len(' ')
      if sLen>=N: return ind
   return len(seq)
     
  
def wrap(prefix, text, cols):

   pad = ' '*len(prefix.expandtabs())
   available = cols - len(pad)

   seq = text.split(' ')
   Nseq = len(seq)
   ind = 0
   lines = []
   while ind<Nseq:
      lastInd = ind
      ind += get_split_ind(seq[ind:], available)
      lines.append(seq[lastInd:ind])

   # add the prefix to the first line, pad with spaces otherwise
   ret = prefix + ' '.join(lines[0]) + '\n'
   for line in lines[1:]:
      ret += pad + ' '.join(line) + '\n'
   return ret




def listFiles(root, patterns='*', recurse=1, return_folders=0):
    """
    Recursively list files
    from Parmar and Martelli in the Python Cookbook
    """
    import os.path, fnmatch
    # Expand patterns from semicolon-separated string to list
    pattern_list = patterns.split(';')
    # Collect input and output arguments into one bunch
    class Bunch:
        def __init__(self, **kwds): self.__dict__.update(kwds)
    arg = Bunch(recurse=recurse, pattern_list=pattern_list,
        return_folders=return_folders, results=[])

    def visit(arg, dirname, files):
        # Append to arg.results all relevant files (and perhaps folders)
        for name in files:
            fullname = os.path.normpath(os.path.join(dirname, name))
            if arg.return_folders or os.path.isfile(fullname):
                for pattern in arg.pattern_list:
                    if fnmatch.fnmatch(name, pattern):
                        arg.results.append(fullname)
                        break
        # Block recursion if recursion was disallowed
        if not arg.recurse: files[:]=[]

    os.path.walk(root, visit, arg)

    return arg.results

def get_recursive_filelist(args):
    """
    Recurs all the files and dirs in args ignoring symbolic links and
    return the files as a list of strings
    """
    files = []
    
    for arg in args:
        if os.path.isfile(arg):
            files.append(arg)
            continue
        if os.path.isdir(arg):
            newfiles = listFiles(arg, recurse=1, return_folders=1)
            files.extend(newfiles)

    return [f for f in files if not os.path.islink(f)]



def pieces(seq, num=2):
   "Break up the seq into num tuples"
   start = 0
   while 1:
      item = seq[start:start+num]
      if not len(item): break
      yield item
      start += num

def exception_to_str(s = None):

   sh = StringIO.StringIO()
   if s is not None: print >>sh, s
   traceback.print_exc(file=sh)
   return sh.getvalue()


def allequal(seq):
    """
    return true if all elements of seq compare equal.  If seq is 0 or
    1 length, return True
    """
    if len(seq)<2: return True
    val = seq[0]
    for i in xrange(1, len(seq)):
        thisval = seq[i]
        if thisval != val: return False
    return True

def alltrue(seq):
    #return true if all elements of seq are true.  If seq is empty return false
    if not len(seq): return False
    for val in seq:
        if not seq: return False
    return True

def onetrue(seq):
    #return true if one elements of seq are true.  If seq is empty return false
    if not len(seq): return False
    for val in seq:
        if seq: return True
    return False

def allpairs(x):
    """
    return all possible pairs in sequence x

    Condensed by Alex Martelli from this thread on c.l.python
    http://groups.google.com/groups?q=all+pairs+group:*python*&hl=en&lr=&ie=UTF-8&selm=mailman.4028.1096403649.5135.python-list%40python.org&rnum=1    
    """
    return [ (s, f) for i, f in enumerate(x) for s in x[i+1:] ]

        
if __name__=='__main__':
    assert( allequal([1,1,1]) )
    assert(not  allequal([1,1,0]) )
    assert( allequal([]) )
    assert( allequal(('a', 'a')))
    assert( not allequal(('a', 'b')))    

