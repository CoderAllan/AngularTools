# This script generates an overview of the angular component hierarchy
import os
import os.path
import re
from xml.dom import minidom


class Component:
    def __init__(self, tsFilename: str, templateFilename: str, selector: str, subcomponents: list, isRoot: bool):
        self.TsFilename = tsFilename
        self.TemplateFilename = templateFilename
        self.Selector = selector
        self.SubComponents = subcomponents
        self.IsRoot = isRoot


def findComponents(componentFilenames: list) -> dict:
    compHash = {}
    for componentFilename in componentFilenames:
        if ("node_modules" not in componentFilename and
                "index.ts" not in componentFilename):
            componentDefinitionFound = False
            currentComponent = Component(componentFilename, "", "", [], True)
            componentFile = open(componentFilename)
            line = componentFile.readline()
            while line:
                match = re.match(r"@Component\({", line)
                if match:
                    componentDefinitionFound = True
                if componentDefinitionFound:
                    match = re.match(r".*templateUrl:.+/(.+)'",
                                     line, re.IGNORECASE)
                    if match:
                        currentComponent.TemplateFilename = os.path.join(os.path.dirname(componentFilename), match.group(1))
                    match = re.match(r".*selector:.+'(.+)'",
                                     line, re.IGNORECASE)
                    if match:
                        currentSelector = match.group(1)
                        currentSelector = currentSelector.replace("[", "")
                        currentSelector = currentSelector.replace("]", "")
                        currentComponent.Selector = currentSelector
                    # Have we reached the end of the component definition?
                    match = re.match(r"}\)", line)
                    if match:
                        break  # If we did find the end, then stop reading
                line = componentFile.readline()
            componentFile.close()
            compHash[currentComponent.Selector] = currentComponent
    return compHash


def scanComponentTemplates(componentHash: dict):
    for selector1 in componentHash:
        if os.path.exists(componentHash[selector1].TemplateFilename):
            templateFile = open(componentHash[selector1].TemplateFilename)
            template = templateFile.read()  # We read the entire template file
            for selector2 in componentHash:  # then we check if the template contains each of the selectors we found in the components
                pattern = f"</{selector2}>"
                index = template.find(pattern)
                if index >= 0:
                    componentHash[selector1].SubComponents.append(componentHash[selector2])
                    # If selector2 has been found in a template then it is not root
                    componentHash[selector2].IsRoot = False
                else:
                    pattern = f" {selector2}"
                    index = template.find(pattern)
                    if index >= 0:
                        componentHash[selector1].SubComponents.append(componentHash[selector2])
                        # If selector2 has been found in a template then it is not root
                        componentHash[selector2].IsRoot = False
            templateFile.close()


def createNewDirectedGraph() -> minidom.Document:
    xmlDoc = minidom.Document()
    root = xmlDoc.createElement("DirectedGraph")
    root.setAttribute("GraphDirection", "LeftToRight")
    root.setAttribute("Layout", "Sugiyama")
    root.setAttribute("ZoomLevel", "-1")
    root.setAttribute("xmlns", "http://schemas.microsoft.com/vs/2009/dgml")
    xmlDoc.appendChild(root)
    return xmlDoc


def addNodeToRoot(root: minidom.Element, tagName: str) -> minidom.Element:
    xmlDoc = minidom.Document()
    elements = root.getElementsByTagName(tagName)
    if elements.length == 0:
        nodeElement = xmlDoc.createElement(tagName)
        root.appendChild(nodeElement)
        return nodeElement
    else:
        exitingNode = elements.item(0)
        return exitingNode


def addNode(element, nodeElement, attribute='Id'):
    nodeAlreadyAdded = False
    for node in element.childNodes:
        if (type(node) is minidom.Element and
            node.hasAttribute(attribute) and
                node.getAttribute(attribute).lower() == nodeElement.getAttribute(attribute).lower()):
            nodeAlreadyAdded = True
    if not nodeAlreadyAdded:
        element.appendChild(nodeElement)


def addLinkNode(element: minidom.Element, source: str, target: str):
    nodeAlreadyAdded = False
    for node in element.childNodes:
        if (type(node) is minidom.Element and
              node.hasAttribute("Source") and
              node.hasAttribute("Target") and
              node.getAttribute("Source").lower() == source.lower() and
              node.getAttribute("Target").lower() == target.lower()):
            nodeAlreadyAdded = True
    if not nodeAlreadyAdded:
        xmlDoc = minidom.Document()
        linkElement = xmlDoc.createElement("Link")
        linkElement.setAttribute("Source", source)
        linkElement.setAttribute("Target", target)
        element.appendChild(linkElement)


def GenerateDirectedGraphNodesXml(components: list, component: Component, isRoot: bool, nodesElement):
    xmlDoc = minidom.Document()
    nodeElement = xmlDoc.createElement("Node")
    nodeElement.setAttribute("ComponentFilename", component.TsFilename)
    nodeElement.setAttribute("Label", component.Selector)
    nodeElement.setAttribute("Id", component.Selector)
    if isRoot:
        nodeElement.setAttribute("Category", "RootComponent")
    if component.IsRoot:
        componentType = "root "
    else:
        componentType = ""
    print(f"Found {componentType}component: {component.Selector}")
    addNode(nodesElement, nodeElement)
    if (len(components) > 0):
        for subComponent in components:
            GenerateDirectedGraphNodesXml(subComponent.SubComponents, subComponent, subComponent.IsRoot, nodesElement)


def GenerateDirectedGraphLinksXml(subComponents: list, displayName: str, parentDisplayName: str, linksElement):
    if len(parentDisplayName) > 0:
        addLinkNode(linksElement, parentDisplayName, displayName)
    if (len(subComponents) > 0):
        for subComponent in subComponents:
            GenerateDirectedGraphLinksXml(subComponent.SubComponents, subComponent.Selector, displayName, linksElement)


def addProperty(propertiesElement, idValue: str, datatypeValue: str):
    xmlDoc = minidom.Document()
    propertyElement = xmlDoc.createElement("Property")
    propertyElement.setAttribute("Id", idValue)
    propertyElement.setAttribute("DataType", datatypeValue)
    addNode(propertiesElement, propertyElement)


def addNodesAndLinks(root: minidom.Element, compHash: dict):
    nodesElement = addNodeToRoot(root, "Nodes")
    linksElement = addNodeToRoot(root, "Links")
    for selector in compHash:
        component = compHash[selector]
        if component.IsRoot == True:
            GenerateDirectedGraphNodesXml(component.SubComponents, component, True, nodesElement)
            GenerateDirectedGraphLinksXml(component.SubComponents, selector, "", linksElement)


def addCategories(root: minidom.Element):
    xmlDoc = minidom.Document()
    categoriesElement = addNodeToRoot(root, "Categories")
    categoryElement = xmlDoc.createElement("Category")
    categoryElement.setAttribute("Id", "RootComponent")
    categoryElement.setAttribute("Label", "Root component")
    categoryElement.setAttribute("Background", "#FF00AA00")
    categoryElement.setAttribute("IsTag", "True")
    addNode(categoriesElement, categoryElement)


def addProperties(root: minidom.Element):
    propertiesElement = addNodeToRoot(root, "Properties")
    addProperty(propertiesElement, "ComponentFilename", "System.String")
    addProperty(propertiesElement, "Background", "System.Windows.Media.Brush")
    addProperty(propertiesElement, "GraphDirection", "Microsoft.VisualStudio.Diagrams.Layout.LayoutOrientation")
    addProperty(propertiesElement, "GroupLabel", "System.String")
    addProperty(propertiesElement, "IsTag", "System.Boolean")
    addProperty(propertiesElement, "Label", "System.String")
    addProperty(propertiesElement, "Layout", "System.String")
    addProperty(propertiesElement, "TargetType", "System.String")
    addProperty(propertiesElement, "ValueLabel", "System.String")
    addProperty(propertiesElement, "ZoomLevel", "System.String")
    addProperty(propertiesElement, "Expression", "System.String")


def addStyles(root: minidom.Element):
    xmlDoc = minidom.Document()
    stylesElement = addNodeToRoot(root, "Styles")

    styleElement = xmlDoc.createElement("Style")
    styleElement.setAttribute("TargetType", "Node")
    styleElement.setAttribute("GroupLabel", "Root component")
    styleElement.setAttribute("ValueLabel", "Has category")

    conditionElement = xmlDoc.createElement("Condition")
    conditionElement.setAttribute("Expression", "HasCategory('RootComponent')")
    styleElement.appendChild(conditionElement)
    setterElement = xmlDoc.createElement("Setter")
    setterElement.setAttribute("Property", "Background")
    setterElement.setAttribute("Property", "#FF00AA00")
    styleElement.appendChild(setterElement)
    addNode(stylesElement, styleElement, "GroupLabel")

def main():
  # find all files recursively under the current folder that ends with *.component.ts
  componentFilenames = [os.path.join(dp, f) for dp, dn, filenames in os.walk(".") for f in filenames if f.endswith(".component.ts")]

  components = findComponents(componentFilenames)
  scanComponentTemplates(components)

  graphFilename = f"ReadMe-ProjectStructure.dgml"
  xmlDocument: minidom.Document()
  root: minidom.Element

  if os.path.exists(graphFilename):
      try:
          xmlDocument = minidom.parse(graphFilename)
          print(f"Directed graph found {graphFilename}. Graph loaded and will be modified.")
      except:
          xmlDocument = createNewDirectedGraph()
          print(f"Parsing of Directed graph {graphFilename} failed. Creating new graph.")
      root = xmlDocument.childNodes[0]
  else:
      xmlDocument = createNewDirectedGraph()
      root = xmlDocument.childNodes[0]

  addNodesAndLinks(root, components)
  addCategories(root)
  addProperties(root)
  addStyles(root)

  print(f"Generating directed graph (dgml) to file: {graphFilename}")
  fileContent = str(xmlDocument.toprettyxml())
  fileContent = re.sub(r"\n\s+\n", "\n", fileContent)
  file = open(graphFilename, "w")
  file.write(fileContent)
  file.close()

if __name__ == "__main__":
    # execute only if run as a script
    main()