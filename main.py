from itertools import islice
import json
import datetime
import math
import sys
import os.path
import psutil

class Converter:
    def __init__(self):
        print("--- Preparing data ---")
        self.start_time = datetime.datetime.now()
        while True:
            # get jsonl filename 
            self.file_name = input("Filename of jsonl file: ")	
            
            # check if file type is jsonll
            if not self.file_name.endswith(".jsonl"):
                print("File is not a jsonl file.", flush=True)
                continue;
            
            # check if file exists
            if os.path.exists(self.file_name): break;
            else: print("File not found, please provide a existing jsonl file", flush=True)
            
        # set result filename
        self.json_file_name = "./result.json"
        
        # set default round number 
        self.round_line = 5000
        
        # check if output file exist
        if not os.path.exists(self.json_file_name):
            # file does not exist -> create
            with open(self.json_file_name, 'w') as f:
                # write default dict in file
                f.write('{}')
        
        # get line count of jsonl file
        with open(self.file_name, 'r') as f:
            self.line_count = sum(1 for line in f)
        
        print("Lines to process: ", self.line_count)
        print("--- Finsihed preparing data --- \n")

    def start(self):
        # print start
        print("--- Starting conversion ---")
        # read current output file data into dict
        with open(self.json_file_name, "r+", encoding="utf-8") as file:
            file_data = json.load(file)
            
        # get times of rounds the loop as to do
        rounds = self.line_count / self.round_line
        
        # round UP the number
        rounds = math.ceil(rounds)
        
        with open(self.file_name, "r+", encoding="utf-8") as f:
            for round in progressbar(rounds, "Progress: ", 40):
                # open jsonl file
                data = [json.loads(line) for line in islice(f, self.round_line)]
                    
                for line in data:
                    # get path as array
                    path = line["__path__"].split("/")  
                    try:
                        line.pop("__id__")
                        line.pop("__path__")
                        line.pop("__exportPath__")
                    except KeyError:
                        pass
                    
                    current = file_data;
                    
                    # loop over path array every two elements
                    for i in range(0, len(path), 2):
                        
                        # break loop to prevent errors if empty subcollection
                        if(i - 1 > len(path)): 
                            break; 
                        
                        # get path key and id
                        path_key = path[i]
                        path_id = path[i + 1]
                        
                        # add empty object to current path key
                        if(path_key not in current):
                            current[path_key] = {}
                        
                        # check if current path id is in path
                        if path_id not in current[path_key]:
                            # add empty document object to main collection
                            current[path_key][path_id] = {}
                        
                        # check if loop can go deeper and if not assign value
                        if(len(path) - 2 == i):
                            current[path_key][path_id] = line
                        else: 
                            # assign new object to current
                            current = current[path_key][path_id]
                
        # write data
        print("Writing data")
        with open(self.json_file_name, "w", encoding="utf-8") as file:
            json.dump(file_data, file, ensure_ascii=False)
        print("--- Finished conversion ---")
        
        print("Time run:", datetime.datetime.now() - self.start_time)

    def replace(m):
        return bytes.fromhex(''.join(m.groups(''))).decode('utf-16-be')

def progressbar(it, prefix="", size=60, out=sys.stdout):
    if isinstance(it, int):
        count = it
    else: 
        count = len(it)
        
    def show(j):
        x = size * j // count
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
    i = int(math.floor(math.log(size_bytes, 1000)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

if __name__ == "__main__":
    Converter().start()