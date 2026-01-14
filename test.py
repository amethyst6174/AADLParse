# coding: utf-8

import jpype
import jpype.imports
import glob
import os
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
lib_dir = "./lib/plugins"
lib_files = glob.glob(os.path.join(lib_dir, "*.jar"))

import platform
separator = ";" if platform.system() == "Windows" else ":"
classpath = separator.join(lib_files)

jpype.startJVM(
    jpype.getDefaultJVMPath(),
    "--enable-native-access=ALL-UNNAMED",
    f"-Djava.class.path={classpath}"
)

from org.eclipse.emf.ecore.resource import ResourceSet
from org.eclipse.emf.ecore.resource.impl import ResourceSetImpl
from org.eclipse.emf.common.util import URI
from org.osate.xtext.aadl2 import Aadl2StandaloneSetup

Aadl2StandaloneSetup.doSetup()

rs = ResourceSetImpl()
aadl_uri = URI.createFileURI("./testfolder/simple.aadl")
resource = rs.getResource(aadl_uri, True)

print("基于OSATE检测的AADL错误信息:")
from org.eclipse.emf.ecore.resource.Resource import getErrors
errors = resource.getErrors()
for e in errors:
    print(e.getMessage(), e.getLine())
print("-"*30)

model = resource.getContents().get(0)

from org.osate.aadl2 import ComponentType, ComponentImplementation

aadl_component = [elem for elem in model.getOwnedPublicSection().getOwnedClassifiers()]

print("检测到的aadl组件:")
for i in aadl_component:
    print(i.getName())
print("-"*30)

for i, elem in enumerate(aadl_component):
    print(f"第{i+1}个组件 - {elem.getName()}")
    if isinstance(elem, ComponentType):
        category = elem.getCategory()
        print(f" "*2 + f"是Type类型的{category}")
        match str(category):
            case "system":
                my_system = elem
                print(f"{' '*4}{type(my_system)}")
            case _:
                print(f" "*4 + "其他类型")
        """
        f = elem.getOwnedFeatures()
        for m in f:
            print(type(m))
            print(m.getCategory())
        """
    elif isinstance(elem, ComponentImplementation):
        category = elem.getCategory()
        print(f" "*2 + f"是Implementation类型的{category}")
        match str(category):
            case "system":
                my_system = elem
                print(f"{' '*4}{type(my_system)}")
                subprogram = my_system.getOwnedSubcomponents()
                for s in subprogram:
                    print(" "*6 + f"含子组件{s.getName()}")
                    print(f"{' '*6}{type(s)}")
                connections = my_system.getOwnedConnections()
                for c in connections:
                    print(" "*6 + f"含局部链接{s.getName()}")
                    print(f"{' '*6}{type(s)}")
            case _:
                print(f" "*4 + "其他类型")

jpype.shutdownJVM()