# This script generates an overview of the angular component hierachi
import os
import os.path
import re

class Component:
    def __init__(self, tsFilename: str, templateFilename: str, selector: str, subcomponents: list, isRoot: bool):
        self.TsFilename = tsFilename
        self.TemplateFilename = templateFilename
        self.Selector = selector
        self.SubComponents = subcomponents
        self.IsRoot = isRoot

def DisplayComponent(subComponents: list, selector: str, indent: int):
    indentation = " " * (indent * 3)
    if indent > 10:
        return
    if (len(subComponents) == 0):
        print(f"{indentation}<{selector}></{selector}>")
    else:
        print(f"{indentation}<{selector}>")
        for subComponent in subComponents:
            DisplayComponent(subComponent.SubComponents, subComponent.Selector, indent+1)
        print(f"{indentation}</{selector}>")

# find all files recursively under the current folder that ends with *.component.ts
components = [os.path.join(dp, f) for dp, dn, filenames in os.walk(".") for f in filenames if f.endswith(".component.ts")]
compHash = {}

for component in components:
    componentDefinitionFound = False
    currentComponent = Component(component, "", "", [], True)
    f = open(component)
    line = f.readline()
    while line:
        match = re.match(r"@Component\({", line)
        if match:
            componentDefinitionFound = True
        if componentDefinitionFound:
            match = re.match(r".*templateUrl:.+/(.+)'", line, re.IGNORECASE)
            if match:
                currentComponent.TemplateFilename = os.path.join(os.path.dirname(component), match.group(1))
            match = re.match(r".*selector:.+'(.+)'", line, re.IGNORECASE)
            if match:
                currentComponent.Selector = match.group(1)
            match = re.match(r"}\)", line) # Have we reached the end of the component definition?
            if match:
                break # If we did find the end, then stop reading
        line = f.readline()
    f.close()
    compHash[currentComponent.Selector] = currentComponent

for selector1 in compHash:
    f = open(compHash[selector1].TemplateFilename)
    template = f.read() # We read the entire template file 
    for selector2 in compHash: # then we check if the template contains each of the selectors we found in the components
        pattern = f"</{selector2}>"
        index = template.find(pattern)
        if index >= 0:
            compHash[selector1].SubComponents.append(compHash[selector2])
            compHash[selector2].IsRoot = False # If selector2 has been found in a template then it is not root
    f.close()

for selector in compHash:
    if compHash[selector].IsRoot == True:
        print(f"Found root: {selector}")
        DisplayComponent(compHash[selector].SubComponents, selector, 0)
        print()

