# Jsonl to Json converter
This tool can convert jsonl files from a firebase export (with firefoo) to regular object based json file. 

# Usage
* Copy export from firefoo into root folder
* Open terminal
* Run command ```python main.py``` or if you want to have the output split into separate files then add "-sc" to it. This will split the output by collection name
* Input filename of firefoo export (for example ```export.jsonl```)
* The program wil now start to prepare your data and then start the conversion
* In the end the time the program has run will be displayed

# Troubleshooting
If the programm crashes try to increase the memory of your machine as the data is loaded into the memory for processing <br>
If the programm runs slow from the start try to delete the json_file.json file (it may already contain data from a previous try) <br>
For any other error please open an issue here: https://github.com/Lexumiii/ndJsonToJson/issues
