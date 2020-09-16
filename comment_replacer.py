import os

for (root, dirs, files) in os.walk("."):
    current_directory = os.path.join(root)
    for file in files:
        current_file = os.path.join(current_directory, file)
        if file.endswith(".cs"):
            with open(current_file, "r+", encoding="utf-8") as f:
                content = f.read().replace(
                    "// TODO: Add constructor logic here\n//", ""
                )
                f.seek(0).write(content).truncate()
