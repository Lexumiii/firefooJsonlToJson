import json


class Converter:
    def __init__(self):
        self.file_name = "./file.jsonl"
        self.json_file_name = "./json_file.json"

        # open jsonl file
        with open(self.file_name, "r+") as f:
            data = [json.loads(line) for line in f]
            self.file_content = data

    def start(self):
        # loop over all lines
        for line in self.file_content:
            id = line["__id__"]
            # loop over keys
            for key in line:
                # skip if __
                if(key.startswith("__") or key == "__id__"):
                    continue

                path = line["__path__"].split("/")
                value = line[key]
                # add to json file

                # read data
                with open(self.json_file_name, "r+") as file:
                    file_data = json.load(file)
                    file.close()

                # write data
                with open(self.json_file_name, "w+") as file:
                    if path[0] not in file_data:
                        file_data[path[0]] = {}
                        file_data[path[0]][path[1]] = {}
                        file_data[path[0]][path[1]][key] = value
                    else:
                        # create document id
                        file_data[path[0]][path[1]] = {}
                        file_data[path[0]][path[1]].update({key: value})

                    file.seek(0)
                    json.dump(file_data, file)
                    file.close()

                if len(path) > 2:
                    # one sub collection
                    collectionName = path[2]
                    documentId = path[3]
                    print("1 subcollection", collectionName, documentId)

                    # read data
                    with open(self.json_file_name, "r+") as file:
                        file_data = json.load(file)
                        file.close()

                    # write data
                    with open(self.json_file_name, "w+") as file:
                        print(collectionName, documentId)
                        if collectionName not in file_data:
                            file_data[path[0]][collectionName] = {}
                            file_data[path[0]][collectionName][documentId] = {}
                            file_data[path[0]][collectionName][documentId][key] = value
                        else:
                            # create document id
                            file_data[path[0]][path[1]][collectionName] = {}
                            file_data[path[0]][path[1]][collectionName][documentId] = {}
                            file_data[path[0]][path[1]][collectionName][documentId].update({key: value})

                        file.seek(0)
                        json.dump(file_data, file)
                        file.close()
                    pass

    def writeJsonFile(self, path: str, key: str, value: str, documentId: str):

        # read data
        with open(self.json_file_name, "r+") as file:
            file_data = json.load(file)
            file.close()

        # write data
        with open(self.json_file_name, "w+") as file:
            if path not in file_data:
                file_data[path] = {}
                file_data[path][documentId] = {}
                file_data[path][documentId][key] = value
            else:
                # create document id
                file_data[path][documentId] = {}
                file_data[path][documentId].update({key: value})

            file.seek(0)
            json.dump(file_data, file)
            file.close()

    def pairwise(self, iterable):
        a = iter(iterable)
        return zip(a, a)


if __name__ == "__main__":
    Converter().start()
