import pandas as pd
import csv
import os
path = "d:/data/"
sourcefile = "data.txt"
outfile = "out.txt"
source_location = f"{path}/{sourcefile}"
output_location = f"{path}/{outfile}"
if os.path.exists(source_location):
    lines = pd.read_csv(f"{path}/{sourcefile}", sep='\t', header=None)
    fields = lines.iloc[:,0]
    if os.path.exists(output_location):
        os.remove(output_location)
    for i in lines[0].values:
        line_text = f"Guid.Parse(\"{i}\"),\n"
        with open(output_location,mode='a') as output_file:
            output_file.write(line_text)
else:
    print(f"{source_location} not found!")
    
