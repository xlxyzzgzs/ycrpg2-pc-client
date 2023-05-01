import tarfile
import zipfile
import requests
import os
import shutil
import os.path

publish_target = ["win-x64", "win-ia32", "osx-x64", "linux-x64", "linux-ia32"]
compress_format = ["zip", "zip", "zip", "tar.gz", "tar.gz"]
nwjs_version = "v0.61.0"
include_file = ["package.json", "index.js"]

webdav_folder = "异常生物见闻录RPG/PC"


for target_arch, com_form in zip(publish_target, compress_format):

    print("Publish to " + target_arch)
    nwjs_urls = f"https://dl.nwjs.io/{nwjs_version}/nwjs-sdk-{nwjs_version}-{target_arch}.{com_form}"
    nwjs_file = f"nwjs-sdk-{nwjs_version}-{target_arch}.{com_form}"
    nwjs_extra_dir = f"nwjs-sdk-{nwjs_version}-{target_arch}"
    app_compress_dir = f"app-{target_arch}"
    app_compress_file = f"app-{target_arch}.{com_form}"
    print(nwjs_urls)
    print(nwjs_file)
    print(nwjs_extra_dir)
    print(app_compress_file)

    if os.path.exists(nwjs_file):
        os.remove(nwjs_file)

    print("Downloading NWJS SDK...")
    r = requests.get(nwjs_urls, stream=True)
    with open(nwjs_file, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
    print("Downloaded " + nwjs_file)

    print("Unzip " + nwjs_file)
    if com_form == "zip":
        with zipfile.ZipFile(nwjs_file, 'r') as zip_ref:
            zip_ref.extractall()
    elif com_form == "tar.gz":
        with tarfile.open(nwjs_file, 'r:gz') as tar_ref:
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(tar_ref)
    print("Extracted " + nwjs_file)

    for file_name in include_file:
        shutil.copy(file_name, nwjs_extra_dir)
        print("Copied " + file_name)
    os.rename(nwjs_extra_dir, app_compress_dir)

    print("Compressing " + nwjs_extra_dir)
    if com_form == "zip":
        with zipfile.ZipFile(app_compress_file, 'w') as zip_ref:
            for root, dirs, files in os.walk(app_compress_dir):
                for file in files:
                    zip_ref.write(os.path.join(root, file))
    elif com_form == "tar.gz":
        with tarfile.open(app_compress_file, 'w:gz') as tar_ref:
            for root, dirs, files in os.walk(app_compress_dir):
                for file in files:
                    tar_ref.add(os.path.join(root, file))
    print("Compressed " + app_compress_file)
