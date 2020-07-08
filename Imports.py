import os
import os.path
import re
 
# find all files recursively under the current folder that ends with *.ts
typescriptFiles = [os.path.join(dp, f) for dp, dn, filenames in os.walk(".") for f in filenames if f.endswith(".ts")]
imports = {}
 
for tsFile in typescriptFiles:
    if "node_modules" not in tsFile and "index.ts" not in tsFile:
        f = open(tsFile)
        line = f.readline()
        while line:
            match = re.match(r".*?\s+from\s+['\"](.+)['\"]", line, re.IGNORECASE)
            if match:
                # print(f"tsFile: {tsFile} - {match.group(1)}")
                key = match.group(1)
                # if(not key.startswith(".")):
                if(key in imports.keys()):
                    imports[match.group(1)] = imports[match.group(1)] + 1
                else:
                    imports[match.group(1)] = 1
            line = f.readline()
        f.close()
 
keys = sorted(imports.keys())
for imps in keys:
    print(f"{imps}: {imports[imps]}")
