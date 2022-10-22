from itertools import islice
import json
import datetime
import math
import re
import sys
import os.path
import psutil

class Converter:
    def __init__(self):
        print("--- Preparing data ---")
        self.start_time = datetime.datetime.now()
        while True:
            self.file_name = input("Filename of jsonl file: ")	
            input_exists = os.path.exists(self.file_name)
            if(input_exists == True):
                break;
            else: print("File not found, please provide a existing jsonl file", flush=True)
        self.json_file_name = "./result.json"
        # check if files exist
        file_exists = os.path.exists(self.json_file_name)

        if(file_exists == False):
            # file does not exist -> create
            with open(self.json_file_name, 'w') as f:
                f.write('{}')
        self.unicode_escape = re.compile(
            r'(?<!\\)'
            r'(?:\\u([dD][89abAB][a-fA-F0-9]{2})\\u([dD][c-fC-F][a-fA-F0-9]{2})'
            r'|\\u([a-fA-F0-9]{4}))')
        self.line_count = sum(1 for line in open(
            self.file_name, encoding="utf-8"))
        print("Lines to process: ", self.line_count)

        print("--- Finsihed preparing data --- \n")

    def start(self):
        # print start
        print("--- Starting conversion ---")
        # read data
        with open(self.json_file_name, "r+", encoding="utf-8") as file:
            file_data = json.load(file)
            file.close()
            
        # get times of rounds the loop as to do
        rounds = self.line_count / 1000
        
        # round UP the number
        rounds = math.ceil(rounds)
        begin_range = 0
        if(self.line_count < 1000):
            stop_range = self.line_count
        else: 
            stop_range = 1000
        
        for round in progressbar(rounds, "Progress: ", 40):
            # open jsonl file
            with open(self.file_name, "r+", encoding="utf-8") as f:
                data = [json.loads(line) for line in islice(f, begin_range, stop_range)]
                
            for line in data:
                # loop over keys
                for key in line:
                    # skip if unwanted keys
                    if(key.startswith("__") or key == "__id__"):
                        continue

                    path = line["__path__"].split("/")  # get path as array
                    value = line[key]
                    
                    current = file_data;
                    
                    # loop over path array 
                    for i in range(0, len(path), 2):
                        
                        # break loop to prevent errors if empty subcollection
                        if(i - 1 > len(path)): 
                            break; 
                        
                        # get path key and id
                        path_key = path[i]
                        path_id = path[i + 1]
                        
                        if(path_key not in current):
                            current[path_key] = {}
                        
                        if path_id not in current[path_key]:
                            # add empty document object to main collection
                            current[path_key][path_id] = {}
                            
                        if(len(path) - 2 == i):
                            current[path_key][path_id][key] = value
                        else: 
                            # assign new object to current
                            current = current[path_key][path_id]     
            
            # increase lines
            begin_range = stop_range
            if(stop_range + 1000 > self.line_count):
                stop_range = self.line_count
            else: 
                stop_range = stop_range + 1000          

        # write data
        with open(self.json_file_name, "w+", encoding="utf-8") as file:
            file.seek(0)
            json.dump(file_data, file, ensure_ascii=False)
            file.close()
        print("--- Finished conversion ---")
        end_time = datetime.datetime.now()
        
        # calculate time run
        difference = end_time - self.start_time
        print("Time run:", difference)

    def replace(m):
        return bytes.fromhex(''.join(m.groups(''))).decode('utf-16-be')

def progressbar(it, prefix="", size=60, out=sys.stdout):
    if isinstance(it, int):
        count = it
    else: 
        count = len(it)
        
    def show(j):
        x = int(size*j/count)
        print("{}|{}{}| {}/{} | Memory usage: {}/{} ({}%)".format(prefix, u'█'*x, "."*(size-x), j, count, convert_size(psutil.virtual_memory().used), convert_size(psutil.virtual_memory().total), str(psutil.virtual_memory().percent).replace(")", "")),
              end='\r', file=out, flush=True)
    show(0)
    if(isinstance(it, int)):
        for i in range(it):
            yield i
            show(i+1)
    else: 
        for i, item in enumerate(it):
            yield item
            show(i+1)
    print("\n", flush=True, file=out)
    

def convert_size(size_bytes):
    if size_bytes == 0:
       return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

if __name__ == "__main__":
    Converter().start()