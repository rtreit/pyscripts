import os
from os import system
import sys

path = "."
recurse = True

if recurse == True:
    for (root, dirs, files) in os.walk(path):
        current_directory = os.path.join(root)
        for file in files:
            current_file = os.path.join(current_directory, file)
            if file.endswith(".cs"):
                try:
                    with open(current_file, "r+", encoding='utf-8') as f:
                        content = f.read().replace("// TODO: Add constructor logic here\n//","")
                        f.write(content)
                        f.truncate()
                except Exception as e:
                    print(e)



