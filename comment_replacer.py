import os

target = "//\n// TODO: Add constructor logic here\n//\n"
print("Enter a path to mangle:")
path = input()
print(f"Searching for\n{target}\n")
counter = 0
for (root, dirs, files) in os.walk(path):
    current_directory = os.path.join(root)
    for file in files:
        current_file = os.path.join(current_directory, file)
        if file.endswith(".cs"):
            with open(current_file, "r+", encoding="utf-8") as f:
                content = f.read()
                if content.find(target) > 0:
                    counter += 1
                    print(f"Found match in {current_file} - replacing!")
                    content = content.replace(target, "")
                    f.seek(0)
                    f.write(content)
                    f.truncate()
print(f"Replaced matched content in {counter} files.")
