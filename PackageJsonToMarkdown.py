import json
import os
import subprocess


def fetchPackageInfo(package, outfile):
    try:
      result = subprocess.run(['C:\\Program Files (x86)\\nodejs\\npm.cmd', 'view', '--registry https://registry.npmjs.org/', '--json', f"{package}"], stdout=subprocess.PIPE, text=True)
      npmjs = json.loads(result.stdout)
      name = npmjs['name']
      print(f'Package: {name}')
      if 'description' in npmjs:
          description = npmjs['description']
      else:
          description = 'N/A'
    except:
      name = package
      description = 'N/A'
    outfile.write(f'| {name} | {description} |\n')


f = open('package.json')
packageJsonTxt = f.read()
packageJson = json.loads(packageJsonTxt)
dependenciesDict = packageJson['dependencies']
devDependenciesDict = packageJson['devDependencies']
f.close()

outfile = open('package.json.md', 'w')
outfile.write(
    '# Package.json\n\n'
    '## Dependencies\n\n'
    '| Name | Description|\n'
    '| ---- |:-----------|\n'
)
for package in dependenciesDict:
    fetchPackageInfo(package, outfile)

outfile.write('\n## Dev Dependencies\n\n'
              '| Name | Description|\n'
              '| ---- |:-----------|\n'
              )

for package in devDependenciesDict:
    fetchPackageInfo(package, outfile)

outfile.close()
