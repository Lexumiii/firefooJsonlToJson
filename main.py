from itertools import islice
import json
import datetime
import math
import sys
import os.path
import psutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-sc', '--split_collections', help='Split outgoing files on main collections into different files', type=bool, action=argparse.BooleanOptionalAction)
parser.add_argument('-st', '--stats', help='Show statistics of ram usage and more', type=bool, action=argparse.BooleanOptionalAction)
parser.add_argument('-f', '--format', help='Format output', type=bool, action=argparse.BooleanOptionalAction)

class Converter:
    def __init__(self):
        """ Initialize the converter class.
        """
        print('--- Preparing data ---')

        # initialize argument parser
        args = parser.parse_args()
        
        # initialize args parser variables
        self.split_collections = args.split_collections
        # get stats arg
        self.stats = args.stats
        
        # get format arg
        self.format_output = args.format
        
        while True:
            # get jsonl filename 
            self.file_name = input('Filename of jsonl file: ')	
            
            # check if file type is jsonll
            if not self.file_name.endswith('.jsonl'):
                print('File is not a jsonl file.', flush=True)
                continue;
            
            # check if file exists
            if os.path.exists(self.file_name): break;
            else: print('File not found, please provide a existing jsonl file', flush=True)
            
        # create output folder
        if not os.path.isdir('output'):
            os.mkdir('output')
        
        # set output folder name
        self.output_folder = './output/'
        
        # set result filename
        self.json_file_name = './output/result.json'
        
        # set default round number 
        self.round_line = 5000
        
        # check if stats are enabled
        if(self.stats == True):
            self.max_ram_usage = psutil.virtual_memory().used
            
            
        
        # check if output file exist
        if not os.path.exists(self.json_file_name):
            # file does not exist -> create
            with open(self.json_file_name, 'w') as f:
                # write default dict in file
                f.write('{}')
        
        # get line count of jsonl file
        with open(self.file_name, 'r', encoding='utf8') as f:
            self.line_count = sum(1 for line in f)
        print('Lines to process: ', self.line_count)
        print('--- Finsihed preparing data --- \n')
        self.start_time = datetime.datetime.now()

    def start(self):
        """ Start conversion of jsonl file to json file.
        """
        # print start
        print('--- Starting conversion ---')
        
        # read current output file data into dict
        with open(self.json_file_name, 'r+', encoding='utf-8') as file:
            file_data = json.load(file)
            
        # calculate rounds the loop has to go
        rounds = self.calculateRounds()
        
        with open(self.file_name, 'r+', encoding='utf-8') as f:
            for round in self.progressbar(rounds, 'Progress: ', 40):
                # open jsonl file
                data = [json.loads(line) for line in islice(f, self.round_line)]
                    
                for line in data:
                    # get path as array
                    path = line['__path__'].split('/')  
                    
                    # remove unwanted data from lime
                    try:
                        line.pop('__id__')
                        line.pop('__path__')
                        line.pop('__exportPath__')
                    except KeyError:
                        pass
                    
                    # create ref to file data
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
        print('Writing data')
        if(self.split_collections == True):
            # loop over main collections of file
            for key in file_data.keys(): 
                # create folder for multiple output files
                with open(self.output_folder + key + ".json", 'w', encoding='utf-8') as file:
                    json.dump(file_data[key], file, ensure_ascii=False)
                pass
        
            if self.split_collections:
                # remove file 
                os.remove(self.json_file_name)
        else:
            with open(self.json_file_name, 'w', encoding='utf-8') as file:
                # write output to file (check if output should be formatted)
                if self.format_output == True: json.dump(file_data, file, ensure_ascii=False, indent=4)
                else: json.dump(file_data, file, ensure_ascii=False)
        print('--- Finished conversion ---')
        if(self.stats == False): 
            print('Time run:', datetime.datetime.now() - self.start_time)
        else:
            self.return_statistics()

    def replace(m):
        """ This method is used to replace the hex values in the string with the actual characters.

        Args:
            m (str): String that should be replaced.

        Returns:
            str: Replaced bytes.
        """
        return bytes.fromhex(''.join(m.groups(''))).decode('utf-16-be')

    def return_statistics(self): 
        """ Print statistics of the conversion.
        """
        print("------- Statistics -------")
        print("File converted: ", self.file_name)
        print("Max RAM usage: ", convert_size(self.max_ram_usage))
        print("Start time: ", self.start_time)
        print("End time: ", datetime.datetime.now())
        print("Time run: ", datetime.datetime.now() - self.start_time)
        print("Lines converted: ", self.line_count)
        print("Lines converted/s: ", math.floor(self.line_count / (datetime.datetime.now() - self.start_time).total_seconds()))
    
    def calculateRounds(self):
        """ Calculates the rounds that the programm has to run to process all lines.
        The ammount of lines in a round is defined by the round_line variable.

        Returns:
            int: Returns the calculated rounds (rounded up)
        """
        return math.ceil(self.line_count / self.round_line)
    
    def progressbar(self, it, prefix='', size=60, out=sys.stdout):
        """Create a custom progress bar.

        Args:
            it (object | int): Count of iterations.
            prefix (str, optional): Prefix of the progress bar. Defaults to ''.
            size (int, optional): Size of progress bar. Defaults to 60.
            out (_SupportsWriteAndFlush[str], optional): File write. Defaults to sys.stdout.

        Yields:
            str: Progressbar.
        """
        
        # check if iteration is int or object
        if isinstance(it, int):
            count = it
        else: 
            count = len(it)
            
        def show(j):
            """ Show progress bar.

            Args:
                j (int): Current progress
            """
            x = size * j // count
            if(self.max_ram_usage < psutil.virtual_memory().used):
                self.max_ram_usage = psutil.virtual_memory().used
            print('{}|{}{}| {}/{} | Memory usage: {}/{} ({}%)'.format(prefix, u'█'*x, '.'*(size-x), j, count, convert_size(psutil.virtual_memory().used), convert_size(psutil.virtual_memory().total), str(psutil.virtual_memory().percent).replace(')', '')),
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
        print('\n', flush=True, file=out)
    

def convert_size(size_bytes):
    """Convert bytes to ```B```, ```KB```, ```MB```, ```GB```, ```TB```, ```PB```, ```EB```, ```ZB``` or ```YB```.

    Args:
        size_bytes (int): Input bytes

    Returns:
        _type_: Converted format
    """
    if size_bytes == 0:
       return '0B'
    size_name = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    i = int(math.floor(math.log(size_bytes, 1000)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return '%s %s' % (s, size_name[i])


if __name__ == '__main__':
    Converter().start()