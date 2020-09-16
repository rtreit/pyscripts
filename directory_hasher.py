import os
from os import system
import sys
import hashlib
import pandas as pd


def HashFile(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
            hash_digest = sha256_hash.hexdigest()
    f.close()
    return hash_digest


def HashDirectory(
    path, detail_file="hash_details.tsv", hash_file="distinct_hashes.txt", recurse=True
):
    hashlist = []
    hash_dict = {}
    hashfile = open(hash_file, mode="w")
    detailfile = open(detail_file, mode="w")
    print("Calculating hashes...")
    if recurse == True:
        for (root, dirs, files) in os.walk(path):
            current_directory = os.path.join(root)
            for file in files:
                current_file = os.path.join(current_directory, file)
                try:
                    file_hash = HashFile(current_file)
                    hashlist.append(file_hash)
                    hash_dict[current_file] = file_hash
                except:
                    pass
    else:
        for file in os.listdir(path):
            current_file = os.path.join(path, file)
            try:
                file_hash = HashFile(current_file)
                length = len(file_hash)
                hash_dict[current_file] = file_hash
            except:
                pass
    for k, v in hash_dict.items():
        detailfile.write(f"{k}\t{v}\n")
    print(f"Done writing {len(hash_dict)} file paths and hashes to {detail_file}")
    detailfile.close()
    print(f"Length before de-dupeing: {len(hashlist)}")
    hashlist = set(hashlist)
    print(f"Length after de-dupeing: {len(hashlist)}")
    for hash in hashlist:
        hashfile.write(f"{hash}\n")
    print(f"Done writing {len(hashlist)} unique hashes to {hash_file}")
    hashfile.close()
    print(f"Adding new columns...")
    print(detail_file)
    df = pd.read_csv(detail_file, sep="\t", names=["Path", "Sha256"])
    df[["Path", "FileName"]] = df.Path.str.rsplit(pat="\\", n=1, expand=True)
    df[["Name", "Extension"]] = df.FileName.str.rsplit(pat=".", n=1, expand=True)
    df["Sha256"] = df["Sha256"].str.strip()
    df = df[["Path", "FileName", "Extension", "Sha256"]]
    df.to_csv(f"{detail_file}", sep="\t", index=False, header=False)
    print("Done!")
    return


HashDirectory('d:\\data', recurse=True)

