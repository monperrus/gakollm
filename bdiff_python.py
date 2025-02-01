#!/usr/bin/python3
# perform a bdiff on two python files

import sys
from stockholm_diff import *

delta = diff_python(open(sys.argv[1]).read(), open(sys.argv[2]).read())
for i in delta:
    print(i,file=sys. stderr)
    
sys.exit(len(delta))
