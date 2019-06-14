# AngularTools ![GitHub top language](https://img.shields.io/github/languages/top/CoderAllan/AngularTools.svg) ![GitHub](https://img.shields.io/github/license/CoderAllan/AngularTools.svg) ![GitHub last commit](https://img.shields.io/github/last-commit/CoderAllan/AngularTools.svg)

This is supposed to be a collection of tools for helping developing Angular projects.

And a collections always starts with a single tool and then it will grow as we find new handy tools.

* `ComponentHierarchy.py` is a tool that scans the Angular applications components and print out the hierarchy of the components. This is a quick way to get an overview of your project.
* `FindUnusedCSSClasses.py` is an attempt on finding css definitions in the css-files that is not used in any templates. But the reality of how complex the difinition and usage of styles is, has made this task much more complicated than i expected. The tool finds many unused styles, but manual checking on some projects of mine have shown that the results should be used carefully.
* `NodeProjectHierarchy.py` is a tool that creates a MarkDown file containing a matrix of what njsproj project files are placed in the folder structure and what TypeScript version they use. It also creates a matrix of what Node packages and the package verion each node project uses. The tool scans all njsproj files and all package.json found in the folder structure.
