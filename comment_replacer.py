import os
import re

target = "\/\/\\n\s*\/\/\s*TODO:\s*Add constructor logic here\s*\\n\s*\/\/\s*\\n"
print("Enter a path to mangle:")
path = input()
print(f"Searching for\n{target}\n")
counter = 0
for (root, dirs, files) in os.walk(path):
    current_directory = os.path.join(root)
    for file in files:
        current_file = os.path.join(current_directory, file)
        if file.endswith(".cs"):
            try:
                with open(current_file, "r+", encoding="utf-8") as f:
                    try:
                        content = f.read()
                    except:
                        with open(current_file, "r+", encoding="utf-16") as f:
                            content = f.read()
                    if re.search(target, content):
                        counter += 1
                        print(f"Found match in {current_file} - replacing!")
                        content = re.sub(target, "", content)
                        f.seek(0)
                        f.write(content)
                        f.truncate()
            except Exception as e:
                print(current_file)
                print(e)
print(f"Replaced matched content in {counter} files.")
