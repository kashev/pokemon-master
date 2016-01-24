import sys
import os
import re

res_dir = './../res/'

for filename in os.listdir(res_dir):
    first_alpha = re.search('[A-z]', filename).start()
    new_name = filename[first_alpha:]
    os.replace(os.path.join(res_dir, filename), os.path.join(res_dir, new_name))
