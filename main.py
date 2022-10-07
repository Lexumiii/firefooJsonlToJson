import json
import datetime
import math
import re
import sys
import os.path
import psutil
import time

class Converter:
    def __init__(self):
        print("--- Preparing data ---")
        self.file_name = "./file.jsonl"
        self.json_file_name = "./json_file.json"
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
        # open jsonl file
        with open(self.file_name, "r+", encoding="utf-8") as f:
            data = [json.loads(line) for line in f]
            self.file_content = data

        print("--- Finsihed preparing data ---")

    def start(self):
        # print start
        start_time = datetime.datetime.now()
        print("Start: ", start_time, "\n")
        print("--- Starting conversion ---")
        # read data
        with open(self.json_file_name, "r+", encoding="utf-8") as file:
            file_data = json.load(file)
            file.close()
        for line in progressbar(self.file_content, "Progress: ", 40):
            # loop over keys
            for key in line:
                # skip if unwanted keys
                if(key.startswith("__") or key == "__id__"):
                    continue

                path = line["__path__"].split("/")  # get path as array
                value = line[key]

                if path[0] not in file_data:
                    file_data[path[0]] = {}  # add empty main collection object

                if path[1] not in file_data[path[0]]:
                    # add empty document object to main collection
                    file_data[path[0]][path[1]] = {}

                if(len(path) == 2):
                    # add key and value if no subcollection is there
                    file_data[path[0]][path[1]][key] = value
                else:
                    # has subcollection
                    collectionName = path[2]  # get subcollection name
                    # get current document id of subcollection
                    documentId = path[3]

                    # check if subcollection already exists in dictionary
                    if collectionName not in file_data[path[0]][path[1]]:
                        # add empty subcollection if
                        file_data[path[0]][path[1]][collectionName] = {}

                    if documentId not in file_data[path[0]][path[1]][collectionName]:
                        # add empty object if subcollection has no document
                        file_data[path[0]][path[1]][collectionName][documentId] = {}

                    # add key and value
                    file_data[path[0]][path[1]][collectionName][documentId][key] = value

        # write data
        with open(self.json_file_name, "w+", encoding="utf-8") as file:
            file.seek(0)
            json.dump(file_data, file, ensure_ascii=False)
            file.close()
        print("--- Finished conversion ---\n")
        end_time = datetime.datetime.now()

        print("End: ", end_time)

        # calculate time run
        difference = end_time - start_time
        print("time run:", difference)

    def replace(m):
        return bytes.fromhex(''.join(m.groups(''))).decode('utf-16-be')


def progressbar(it, prefix="", size=60, out=sys.stdout):
    count = len(it)
    
    def show(j):
        x = int(size*j/count)
        print("{}[{}{}] {}/{} | Memory usage: {}/{} ({}%)".format(prefix, "#"*x, "."*(size-x), j, count, convert_size(psutil.virtual_memory().used), convert_size(psutil.virtual_memory().total), str(psutil.virtual_memory().percent).replace(")", "")),
              end='\r', file=out, flush=True)
    show(0)
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
