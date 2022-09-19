import json
import datetime
import re
import sys
import os.path


class Converter:
    def __init__(self):
        print("--- Preparing data ---")
        self.file_name = "./file.jsonl"
        self.json_file_name = "./json_file.json"
        self.converted_output_file_name = "./output.json"
        # check if files exist
        file_exists = os.path.exists(self.json_file_name)

        if(file_exists == False):
            # file does not exist -> create
            with open(self.json_file_name, 'w') as f:
                f.write('{}')

         # check if files exist
        file_exists = os.path.exists(self.converted_output_file_name)

        if(file_exists == False):
            # file does not exist -> create
            with open(self.converted_output_file_name, 'w') as f:
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
        for line in progressbar(self.file_content, "Computing: ", 40):
            
            # loop over keys
            for key in line:
                # skip if unwanted keys
                if(key.startswith("__") or key == "__id__"):
                    continue

                path = line["__path__"].split("/") # get path as object
                value = line[key]

                # read data
                with open(self.json_file_name, "r+", encoding="utf-8") as file:
                    file_data = json.load(file)
                    file.close()

                # write data
                with open(self.json_file_name, "w+", encoding="utf-8") as file:
                    if path[0] not in file_data:
                        file_data[path[0]] = {} # add empty main collection object
                        
                    if path[1] not in file_data[path[0]]:
                        file_data[path[0]][path[1]] = {} # add empty document object to main collection
                        
                    if(len(path) == 2):
                        file_data[path[0]][path[1]][key] = value # add key and value if no subcollection is there
                    else:
                        # has subcollection
                        collectionName = path[2] # get subcollection name
                        documentId = path[3] # get current document id of subcollection
                        
                        # check if subcollection already exists in dictionary
                        if collectionName not in file_data[path[0]][path[1]]:
                            file_data[path[0]][path[1]][collectionName] = {} # add empty subcollection if 
                            
                        if documentId not in file_data[path[0]][path[1]][collectionName]:
                            file_data[path[0]][path[1]][collectionName][documentId] = {} # add empty object if subcollection has no document
                        
                        file_data[path[0]][path[1]][collectionName][documentId][key] = value # add key and value 

                    file.seek(0)
                    json.dump(file_data, file, ensure_ascii=False)
                    file.close()
        print("--- Finished conversion ---\n")

        print("--- Starting conversion of unicode in json ---")
        with open(self.json_file_name, "r", encoding="utf-8") as input:
            with open(self.converted_output_file_name, "w", encoding="utf-8") as output:
                for line in input:
                    output.write(self.unicode_escape.sub(self.replace, line))
        print("--- Finished conversion of unicode in json ---")

        end_time = datetime.datetime.now()

        print("End: ", end_time)

        print("INFO:  This programm created 2 files: 'output.json' and 'json_file.json. The output.json has an additional layer of unicode characters conversion")

        # calculate time run
        difference = end_time - start_time
        print("time run:", difference)

    def replace(m):
        return bytes.fromhex(''.join(m.groups(''))).decode('utf-16-be')


def progressbar(it, prefix="", size=60, out=sys.stdout):  # Python3.3+
    count = len(it)

    def show(j):
        x = int(size*j/count)
        print("{}[{}{}] {}/{}".format(prefix, "#"*x, "."*(size-x), j, count),
              end='\r', file=out, flush=True)
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    print("\n", flush=True, file=out)


if __name__ == "__main__":
    Converter().start()
