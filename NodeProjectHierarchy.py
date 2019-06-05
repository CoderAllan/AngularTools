import json
import os
import os.path
import re

class Project:
    def __init__(self, projectName: str):
        self.ProjectName = projectName
        self.RootNamespace = ""
        self.TypeScriptVersion = ""
        self.TypeScriptModuleKind = ""
        self.DependencyPackageDictionary = {}
        self.DevDependencyPackageDictionary = {}
        self.PeerDependencyPackageDictionary = {}

def EscapeMarkdown(markdown: str):
    escapedString = markdown.replace("|", "&#124;")
    return escapedString

projects = []
print("Scanning for *.njsproj and package.json files...")
nodeProjectFiles = [os.path.join(dp, f) for dp, dn, filenames in os.walk(".") for f in filenames if f.endswith(".njsproj") or f.endswith("package.json")]
for projectFilename in nodeProjectFiles:
    if projectFilename.endswith(".njsproj"):
        print(f"Found projectfile: {projectFilename}")
        projectFile = open(projectFilename)
        line = projectFile.readline()
        currentProject = Project("")
        while line:
            match = re.match(r".*<Name>(.*)</Name>", line, re.IGNORECASE)
            if match:
                currentProject.ProjectName = match.group(1)
            else:
                match = re.match(r".*<RootNamespace>(.*?)</RootNamespace>", line, re.IGNORECASE)
                if match:
                    currentProject.RootNamespace = match.group(1)
                else:
                    match = re.match(r".*<TypeScriptToolsVersion>(.*?)</TypeScriptToolsVersion>", line, re.IGNORECASE)
                    if match:
                        currentProject.TypeScriptVersion = match.group(1)
                    else:
                        match = re.match(r".*<TypeScriptModuleKind>(.*?)</TypeScriptModuleKind>", line, re.IGNORECASE)
                        if match:
                            currentProject.TypeScriptModuleKind = match.group(1)
            line = projectFile.readline()
        projectFile.close()
        if len(currentProject.ProjectName) > 0:
            projects.append(currentProject)

# packageJsonFiles = [os.path.join(dp, f) for dp, dn, filenames in os.walk(".") for f in filenames if f.endswith("package.json")]
projectsInSolution = []
dependencyPackagesUsedInSolution = []
devDependencyPackagesUsedInSolution = []
peerDependencyPackagesUsedInSolution = []
projectDictionary = {}
for packageFile in nodeProjectFiles:
    if not "node_modules" in packageFile and packageFile.endswith("package.json"):
        projectName = packageFile.replace(".\\", "")
        projectName = os.path.dirname(projectName)
        currentProject = Project(projectName)
        print(f"Processing {projectName}...")
        json_file = open(packageFile)
        json_str = json_file.read()
        json_data = json.loads(json_str)
        if "dependencies" in json_data:
            dependencies = json_data["dependencies"]
            for dependency in dependencies:
                if not dependency in dependencyPackagesUsedInSolution:
                    dependencyPackagesUsedInSolution.append(dependency)
                currentProject.DependencyPackageDictionary[dependency] = EscapeMarkdown(dependencies[dependency])
        if "devDependencies" in json_data:
            devDependencies = json_data["devDependencies"]
            for dependency in devDependencies:
                if not dependency in devDependencyPackagesUsedInSolution:
                    devDependencyPackagesUsedInSolution.append(dependency)
                currentProject.DevDependencyPackageDictionary[dependency] = EscapeMarkdown(devDependencies[dependency])
        if "peerDependencies" in json_data:
            peerDependencies = json_data["peerDependencies"]
            for dependency in peerDependencies:
                if not dependency in peerDependencyPackagesUsedInSolution:
                    peerDependencyPackagesUsedInSolution.append(dependency)
                currentProject.PeerDependencyPackageDictionary[dependency] = EscapeMarkdown(peerDependencies[dependency])
        projectsInSolution.append(currentProject)
        projectDictionary[projectName] = currentProject
 
dependencyPackagesUsedInSolution = sorted(dependencyPackagesUsedInSolution, key = lambda s: s.lower())
devDependencyPackagesUsedInSolution = sorted(devDependencyPackagesUsedInSolution, key = lambda s: s.lower())
peerDependencyPackagesUsedInSolution = sorted(peerDependencyPackagesUsedInSolution, key = lambda s: s.lower())
packageDependencyTableHeader = packageDevDependencyTableHeader = packagePeerDependencyTableHeader = "|Project"
packageDependencyTableSeperator = packageDevDependencyTableSeperator = packagePeerDependencyTableSeperator = "|-"
packageDependencyTableBody = packageDevDependencyTableBody = packagePeerDependencyTableBody = ""
for package in dependencyPackagesUsedInSolution:
    packageDependencyTableHeader = f"{packageDependencyTableHeader}|{package}"
    packageDependencyTableSeperator = f"{packageDependencyTableSeperator}|-"
for package in devDependencyPackagesUsedInSolution:
    packageDevDependencyTableHeader = f"{packageDevDependencyTableHeader}|{package}"
    packageDevDependencyTableSeperator = f"{packageDevDependencyTableSeperator}|-"
for package in peerDependencyPackagesUsedInSolution:
    packagePeerDependencyTableHeader = f"{packagePeerDependencyTableHeader}|{package}"
    packagePeerDependencyTableSeperator = f"{packagePeerDependencyTableSeperator}|-"
for project in projectsInSolution:
    packageDependencyTableBody = f"{packageDependencyTableBody}|{project.ProjectName}"
    packageDevDependencyTableBody = f"{packageDevDependencyTableBody}|{project.ProjectName}"
    for package in dependencyPackagesUsedInSolution:
        if package in projectDictionary[project.ProjectName].DependencyPackageDictionary:
            packageDependencyTableBody = f"{packageDependencyTableBody}|{projectDictionary[project.ProjectName].DependencyPackageDictionary[package]}"
        else:
            packageDependencyTableBody = f"{packageDependencyTableBody}|"
    packageDependencyTableBody = f"{packageDependencyTableBody}|\n"
    for package in devDependencyPackagesUsedInSolution:
        if package in projectDictionary[project.ProjectName].DevDependencyPackageDictionary:
            packageDevDependencyTableBody = f"{packageDevDependencyTableBody}|{projectDictionary[project.ProjectName].DevDependencyPackageDictionary[package]}"
        else:
            packageDevDependencyTableBody = f"{packageDevDependencyTableBody}|"
    packageDevDependencyTableBody = f"{packageDevDependencyTableBody}|\n"
    packagePeerDependencyTableBody = f"{packagePeerDependencyTableBody}|{project.ProjectName}"
    for package in peerDependencyPackagesUsedInSolution:
        if package in projectDictionary[project.ProjectName].PeerDependencyPackageDictionary:
            packagePeerDependencyTableBody = f"{packagePeerDependencyTableBody}|{projectDictionary[project.ProjectName].PeerDependencyPackageDictionary[package]}"
        else:
            packagePeerDependencyTableBody = f"{packagePeerDependencyTableBody}|"
    packagePeerDependencyTableBody = f"{packagePeerDependencyTableBody}|\n"
dependenciesPackageTable = f"{packageDependencyTableHeader}|\n{packageDependencyTableSeperator}|\n{packageDependencyTableBody}|\n\n"
devDependenciesPackageTable = f"{packageDevDependencyTableHeader}|\n{packageDevDependencyTableSeperator}|\n{packageDevDependencyTableBody}|\n\n"
peerDependenciesPackageTable = f"{packagePeerDependencyTableHeader}|\n{packagePeerDependencyTableSeperator}|\n{packagePeerDependencyTableBody}|\n\n"

projectOverviewHeader = "||Typescript version|Root namespace|Typescript module kind|\n|-|-|-|-|\n"
projectOverviewBody = ""
for project in projects:
    projectOverviewBody = f"{projectOverviewBody}|{project.ProjectName}|{project.TypeScriptVersion}|{project.RootNamespace}|{project.TypeScriptModuleKind}|\n" 

cwd = os.path.basename(os.getcwd())
outputFilename = f"ReadMe-NodeProjects-{cwd}.md"
file = open(outputFilename, "w")
file.write(
    f"# Node Projects\n\n"\
    f"{projectOverviewHeader}"
    f"{projectOverviewBody}\n"
    f"## Package usage\n\n"\
    f"### Dependencies\n\n"\
    f"{dependenciesPackageTable}"\
    f"### Dev Dependencies\n\n"\
    f"{devDependenciesPackageTable}"\
    f"### Peer Dependencies\n\n"\
    f"{peerDependenciesPackageTable}"\
)
file.close()
