import json
from datetime import datetime

class Converter:
    def __init__(self):
        self.file_name = "./file.jsonl"
        self.json_file_name = "./json_file.json"

        # open jsonl file
        with open(self.file_name, "r+", encoding="utf8") as f:
            data = [json.loads(line) for line in f]
            self.file_content = data

    def start(self):
        # print start
        start_time = datetime.now()
        print("Start: ", start_time)
        
        # loop over all lines
        for line in self.file_content:
            id = line["__id__"]
            # loop over keys
            for key in line:
                print("key:", key)
                # skip if __
                if(key.startswith("__") or key == "__id__"):
                    continue

                path = line["__path__"].split("/")
                value = line[key]
                # add to json file
    
                # read data
                with open(self.json_file_name, "r+", encoding="utf8") as file:
                    file_data = json.load(file)
                    file.close()

                # write data
                with open(self.json_file_name, "w+", encoding="utf8") as file:
                    if path[0] not in file_data:
                        file_data[path[0]] = {}
                    if path[1] not in file_data[path[0]]:
                        file_data[path[0]][path[1]] = {}
                    file_data[path[0]][path[1]][key] = value

                    file.seek(0)
                    json.dump(file_data, file)
                    file.close()

                if len(path) > 2:
                    # one sub collection
                    collectionName = path[2]
                    documentId = path[3]

                    # read data
                    with open(self.json_file_name, "r+", encoding="utf8") as file:
                        file_data = json.load(file)
                        file.close()

                    # write data
                    with open(self.json_file_name, "w+", encoding="utf8") as file:
                        if collectionName not in file_data:
                            file_data[path[0]][path[1]][collectionName] = {}
                        if documentId not in file_data[path[0]][path[1]][collectionName]:
                            file_data[path[0]][path[1]][collectionName][documentId] = {}
                        file_data[path[0]][path[1]][collectionName][documentId][key] = value

                        file.seek(0)
                        json.dump(file_data, file)
                        file.close()
                    pass
        end_time = datetime.now()        
        print("End: ", datetime.now())
        
        # calculate time run
        difference = start_time - end_time
        seconds_in_day = 24 * 60 * 60
        res = divmod(difference.days * seconds_in_day + difference.seconds, 60)
        print("time run:", res[0], "hours", res[1], "minutes")
        
    def pairwise(self, iterable):
        a = iter(iterable)
        return zip(a, a)


if __name__ == "__main__":
    Converter().start()

