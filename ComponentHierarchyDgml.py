# This script generates an overview of the angular component hierarchy
import os
import os.path
import re
import xml.dom.minidom
 
class Component:
    def __init__(self, tsFilename: str, templateFilename: str, selector: str, subcomponents: list, isRoot: bool):
        self.TsFilename = tsFilename
        self.TemplateFilename = templateFilename
        self.Selector = selector
        self.SubComponents = subcomponents
        self.IsRoot = isRoot
 
def GenerateDirectedGraphNodes(components: list, component: Component, isRoot: bool, includeLabel: bool, includeTsFilename: bool, tagName: str, idAttr: str):
    label = ""
    rootComponentCategory = ""
    tsFilename = ""
    if includeLabel:
        label = f" Label=\"{component.Selector}\""
    if isRoot:
        rootComponentCategory = f" Category=\"RootComponent\""
    if includeTsFilename:
        tsFilename = f" ComponentFilename=\"{component.TsFilename}\""
    output = f"   <{tagName} {idAttr}=\"{component.Selector}\"{tsFilename}{label}{rootComponentCategory}/>\n"
    if (len(components) > 0):
        for subComponent in components:
            result = GenerateDirectedGraphNodes(subComponent.SubComponents, subComponent, subComponent.IsRoot, includeLabel, includeTsFilename, tagName, idAttr)
            output = f"{output}{result}"
    return output
 
def GenerateDirectedGraphLinks(subComponents: list, displayName: str, parentDisplayName: str, tagName: str, sourceAttr: str, targetAttr: str):
    if len(parentDisplayName) > 0:
        output = f"   <{tagName} {sourceAttr}=\"{parentDisplayName}\" {targetAttr}=\"{displayName}\"/>\n"
    else:
        output = ""
    if (len(subComponents) > 0):
        for subComponent in subComponents:
            result = GenerateDirectedGraphLinks(subComponent.SubComponents, subComponent.Selector, displayName, tagName, sourceAttr, targetAttr)
            output = f"{output}{result}"
    return output
 
# find all files recursively under the current folder that ends with *.component.ts
components = [os.path.join(dp, f) for dp, dn, filenames in os.walk(".") for f in filenames if f.endswith(".component.ts")]
compHash = {}
 
for component in components:
    if "node_modules" not in component:
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
                    currentSelector = match.group(1)
                    currentSelector = currentSelector.replace("[", "")
                    currentSelector = currentSelector.replace("]", "")
                    currentComponent.Selector = currentSelector
                match = re.match(r"}\)", line) # Have we reached the end of the component definition?
                if match:
                    break # If we did find the end, then stop reading
            line = f.readline()
        f.close()
        compHash[currentComponent.Selector] = currentComponent
 
for selector1 in compHash:
    if os.path.exists(compHash[selector1].TemplateFilename):
        f = open(compHash[selector1].TemplateFilename)
        template = f.read() # We read the entire template file 
        for selector2 in compHash: # then we check if the template contains each of the selectors we found in the components
            pattern = f"</{selector2}>"
            index = template.find(pattern)
            if index >= 0:
                compHash[selector1].SubComponents.append(compHash[selector2])
                compHash[selector2].IsRoot = False # If selector2 has been found in a template then it is not root
            else:
                pattern = f" {selector2}"
                index = template.find(pattern)
                if index >= 0:
                    compHash[selector1].SubComponents.append(compHash[selector2])
                    compHash[selector2].IsRoot = False # If selector2 has been found in a template then it is not root
        f.close()
 
nodes = ""
links = ""
for selector in compHash:
    component = compHash[selector]
    if component.IsRoot == True:
        print(f"Found root: {selector}")
        nodes = nodes + GenerateDirectedGraphNodes(component.SubComponents, component, True, False, True, "Node", "Id")
        links = links + GenerateDirectedGraphLinks(component.SubComponents, selector, "", "Link", "Source", "Target")
        print()
 
fileContent = f'''\
<?xml version='1.0' encoding='utf-8'?>
<DirectedGraph GraphDirection="TopToBottom" Layout="ForceDirected" ZoomLevel="-1" xmlns="http://schemas.microsoft.com/vs/2009/dgml">
<Nodes>\n{nodes}</Nodes>
<Links>\n{links}</Links>
<Categories>
    <Category Id="RootComponent" Label="Root component" Background="#FF00AA00" IsTag="True" />
</Categories>
<Properties>
    <Property Id="ComponentFilename" DataType="System.String" />
</Properties>
</DirectedGraph>
'''
 
outputFilename = f"ReadMe-ProjectStructure.dgml"
print(f"Generating directed graph (dgml) to file: {outputFilename}")
file = open(outputFilename, "w")
file.write(fileContent)
file.close()