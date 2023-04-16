import FreeCAD as App
import FreeCADGui as Gui
import os
from PySide import QtGui, QtCore
from femtools import ccxtools
import datetime
import webbrowser
from fembygen import Generate
from fembygen import Common


def makeGenerate():
    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object
    
    try:
        obj = App.ActiveDocument.Beso
        obj.isValid()
    except:
        obj = App.ActiveDocument.addObject(
            "Part::FeaturePython", "Beso")
        App.ActiveDocument.Generative_Design.addObject(obj)
    Generated(obj)
    if App.GuiUp:
        ViewProviderGen(obj.ViewObject)
    return obj

def returnPath():
    path = os.path.split(self.form.fileName.text())[0] #fileName contains full path not only file name

class Generated:
    """ Finite Element Analysis """

    def __init__(self, obj):
        obj.Proxy = self
        self.Type = "Beso"
        self.initProperties(obj)

    def initProperties(self, obj):
        try:
            obj.addProperty("App::PropertyStringList", "Parameters_Name", "Generations",
                            "Generated parameter matrix")
            obj.addProperty("App::PropertyPythonObject", "Generated_Parameters", "Generations",
                            "Generated parameter matrix")
        except:
            pass


class TopologyCommand():

    def GetResources(self):
        return {'Pixmap': os.path.join(App.getUserAppDataDir() + 'Mod/FEMbyGEN/fembygen/Topology.svg'),  # the name of a svg file available in the resources
                'MenuText': "Topology",
                'ToolTip': "Opens Beso gui"}

    def Activated(self):
          pass
    
    def setEdit(self, vobj, mode):
            taskd = MyGui(vobj)
            taskd.obj = vobj.Object
            Gui.Control.showDialog(taskd)
            return True
        obj = makeGenerate()
        doc = Gui.ActiveDocument
        if not doc.getInEdit():
            doc.setEdit(obj.ViewObject.Object.Name)
        else:
            App.Console.PrintError('Existing task dialog already open\n')
        return

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        return App.ActiveDocument is not None
        
        
    

class MyGui(QtGui.QWidget):
    def __init__(self,object):
        super(MyGui, self).__init__()
        self.obj = object
        guiPath = App.getUserAppDataDir() + "Mod/FEMbyGEN/fembygen/Beso.ui"
        self.form  = Gui.PySideUic.loadUi(guiPath)
        self.workingDir = '/'.join(
            object.Object.Document.FileName.split('/')[0:-1])
        self.doc = object.Object.Document
        (paramNames, parameterValues) = Common.checkGenParameters(self.doc)
        self.doc.Generate.Parameters_Name = paramNames
        self.doc.Generate.Generated_Parameters = parameterValues

        numGens = Common.checkGenerations(self.workingDir)
        self.resetViewControls(numGens)

        MyGui.inp_file = ""
        MyGui.beso_dir = os.path.dirname(__file__)
        #self.form.Faces.setReadOnly(True)
       
        self.form.selectGen.currentIndexChanged.connect(self.selectFile) # Select generated analysis file

        self.form.updateButton.clicked.connect(self.Update) # Update domains button

        self.form.selectMaterial_1.currentIndexChanged.connect(self.selectMaterial1) #select domain by material object comboBox 1
        self.form.selectMaterial_2.currentIndexChanged.connect(self.selectMaterial2) #select domain by material object comboBox 2
        self.form.selectMaterial_3.currentIndexChanged.connect(self.selectMaterial3) #select domain by material object comboBox 3

        self.form.selectFilter_1.currentIndexChanged.connect(self.filterType1) #select filter type comboBox 1 (simple,casting)
        self.form.selectFilter_2.currentIndexChanged.connect(self.filterType2) #select filter type comboBox 2 (simple,casting)
        self.form.selectFilter_3.currentIndexChanged.connect(self.filterType3) #select filter type comboBox 3 (simple,casting)

        self.form.filterRange_1.currentIndexChanged.connect(self.filterRange1) # select filter range comboBox 1 (auto,manual)
        self.form.filterRange_2.currentIndexChanged.connect(self.filterRange2) # select filter range comboBox 2 (auto,manual)
        self.form.filterRange_3.currentIndexChanged.connect(self.filterRange3) # select filter range comboBox 3 (auto,manual)

        self.form.generateConf.clicked.connect(self.generateConfig) # generate config file button
        self.form.editConf.clicked.connect(self.editConfig) # edit config file button

        self.form.runOpt.clicked.connect(self.runOptimization) # run optimization button
        self.form.openExample.clicked.connect(self.openExample) # example button, opens examples on beso github
        self.form.confComments.clicked.connect(self.openConfComments) # opens config comments on beso github
        self.form.openLog.clicked.connect(self.openLog) # # opens log file

        self.Update()  # first update


    def selectFile(self): 
        self.form.fileName.setText(self.workingDir + f"/Gen{self.form.selectGen.currentIndex()+1}/loadCase1/FEMMeshNetgen.inp")
        MyGui.inp_file = self.form.fileName.text()

    
    def resetViewControls(self, numGens):
        comboBoxItems = []
        if numGens > 0:
            self.form.selectGen.setEnabled(True)

            
            for i in range(1, numGens+1):
                comboBoxItems.append("Generation " + str(i))
            self.form.selectGen.clear()
            self.form.selectGen.addItems(comboBoxItems)
            self.form.fileName.setText(self.workingDir + f"/Gen{self.form.selectGen.currentIndex()+1}/loadCase1/FEMMeshNetgen.inp")
        else:
            self.form.selectGen.setEnabled(False)

    
    def Update(self):
        # get material objects
        self.materials = []
        self.thicknesses = []
        try:
            App.ActiveDocument.Objects
        except AttributeError:
            App.newDocument("Unnamed")
            print("Warning: Missing active document with FEM analysis. New document have been created.")
        for obj in App.ActiveDocument.Objects:
            if obj.Name[:23] == "MechanicalSolidMaterial":
                self.materials.append(obj)
            elif obj.Name[:13] == "MaterialSolid":
                self.materials.append(obj)
            elif obj.Name[:13] == "SolidMaterial":
                self.materials.append(obj)
            elif obj.Name[:17] == "ElementGeometry2D":
                self.thicknesses.append(obj)

        self.form.selectMaterial_1.clear()
        self.form.selectMaterial_1.addItem("None")
        self.form.selectMaterial_2.clear()
        self.form.selectMaterial_2.addItem("None")
        self.form.selectMaterial_3.clear()
        self.form.selectMaterial_3.addItem("None")
        self.form.thicknessObject1.clear()
        self.form.thicknessObject1.addItem("None")
        self.form.thicknessObject2.clear()
        self.form.thicknessObject2.addItem("None")
        self.form.thicknessObject3.clear()
        self.form.thicknessObject3.addItem("None")
        self.form.domainList_1.clear()
        self.form.domainList_1.addItem("All defined")
        self.form.domainList_1.addItem("Domain 0")
        self.form.domainList_1.addItem("Domain 1")
        self.form.domainList_1.addItem("Domain 2")
        self.form.domainList_1.setCurrentItem(self.form.domainList_1.item(0))
        self.form.domainList_2.clear()
        self.form.domainList_2.addItem("All defined")
        self.form.domainList_2.addItem("Domain 0")
        self.form.domainList_2.addItem("Domain 1")
        self.form.domainList_2.addItem("Domain 2")
        self.form.domainList_2.setCurrentItem(self.form.domainList_2.item(0))
        self.form.domainList_3.clear()
        self.form.domainList_3.addItem("All defined")
        self.form.domainList_3.addItem("Domain 0")
        self.form.domainList_3.addItem("Domain 1")
        self.form.domainList_3.addItem("Domain 2")
        self.form.domainList_3.setCurrentItem(self.form.domainList_3.item(0))

        
        for mat in self.materials:
            self.form.selectMaterial_1.addItem(mat.Label)
            self.form.selectMaterial_2.addItem(mat.Label)
            self.form.selectMaterial_3.addItem(mat.Label)
        if self.materials:
            self.form.selectMaterial_1.setCurrentIndex(1)
        for th in self.thicknesses:
            self.form.thicknessObject1.addItem(th.Label)
            self.form.thicknessObject2.addItem(th.Label)
            self.form.thicknessObject3.addItem(th.Label)

    def generateConfig(self):

        file_name = os.path.split(self.form.fileName.text())[1]
        path = os.path.split(self.form.fileName.text())[0]

        #global elset2
        #global elset
        #global elset1
        elset2 = ""
        elset = ""
        elset1 = ""
        fea = ccxtools.FemToolsCcx()
        fea.setup_ccx()
        path_calculix = fea.ccx_binary

        optimization_base = self.form.optBase.currentText() #stiffness,heat

        elset_id = self.form.selectMaterial_1.currentIndex() - 1
        thickness_id = self.form.thicknessObject1.currentIndex() - 1
        if elset_id != -1:
            if thickness_id != -1:
                elset = self.materials[elset_id].Name + self.thicknesses[thickness_id].Name
            else:  # 0 means None thickness selected
                elset = self.materials[elset_id].Name + "Solid"
            modulus = float(self.materials[elset_id].Material["YoungsModulus"].split()[0])  # MPa
            if self.materials[elset_id].Material["YoungsModulus"].split()[1] != "MPa":
                raise Exception(" units not recognised in " + self.materials[elset_id].Name)
            poisson = float(self.materials[elset_id].Material["PoissonRatio"].split()[0])
            try:
                density = float(self.materials[elset_id].Material["Density"].split()[0]) * 1e-12  # kg/m3 -> t/mm3
                if self.materials[elset_id].Material["Density"].split()[1] not in ["kg/m^3", "kg/m3"]:
                    raise Exception(" units not recognised in " + self.materials[elset_id].Name)
            except KeyError:
                density = 0.
            try:
                conductivity = float(self.materials[elset_id].Material["ThermalConductivity"].split()[0])  # W/m/K
                if self.materials[elset_id].Material["ThermalConductivity"].split()[1] != "W/m/K":
                    raise Exception(" units not recognised in " + self.materials[elset_id].Name)
            except KeyError:
                conductivity = 0.
            try:
                if self.materials[elset_id].Material["ThermalExpansionCoefficient"].split()[1] == "um/m/K":
                    expansion = float(self.materials[elset_id].Material["ThermalExpansionCoefficient"].split()[
                                       0]) * 1e-6  # um/m/K -> mm/mm/K
                elif self.materials[elset_id].Material["ThermalExpansionCoefficient"].split()[1] == "m/m/K":
                    expansion = float(self.materials[elset_id].Material["ThermalExpansionCoefficient"].split()[
                                       0])  # m/m/K -> mm/mm/K
                else:
                    raise Exception(" units not recognised in " + self.materials[elset_id].Name)
            except KeyError:
                expansion = 0.
            try:
                specific_heat = float(self.materials[elset_id].Material["SpecificHeat"].split()[
                                      0]) * 1e6  #  J/kg/K -> mm^2/s^2/K
                if self.materials[elset_id].Material["SpecificHeat"].split()[1] != "J/kg/K":
                    raise Exception(" units not recognised in " + self.materials[elset_id].Name)
            except KeyError:
                specific_heat = 0.
            if thickness_id != -1:
                thickness = str(self.thicknesses[thickness_id].Thickness).split()[0]  # mm
                if str(self.thicknesses[thickness_id].Thickness).split()[1] != "mm":
                    raise Exception(" units not recognised in " + self.thicknesses[thickness_id].Name)
            else:
                thickness = 0.
            optimized = self.form.asDesign_checkbox.isChecked()
            if self.form.stressLimit_1.text():
                von_mises = float(self.form.stressLimit_1.text())
            else:
                von_mises = 0.

        elset_id1 = self.form.selectMaterial_2.currentIndex() - 1
        thickness_id1 = self.form.thicknessObject2.currentIndex() - 1

        if elset_id1 != -1:
            if thickness_id1 != -1:
                elset1 = self.materials[elset_id1].Name + self.thicknesses[thickness_id1].Name
            else:  # 0 means None thickness selected
                elset1 = self.materials[elset_id1].Name + "Solid"
            modulus1 = float(self.materials[elset_id1].Material["YoungsModulus"].split()[0])  # MPa
            if self.materials[elset_id1].Material["YoungsModulus"].split()[1] != "MPa":
                raise Exception(" units not recognised in " + self.materials[elset_id1].Name)
            poisson1 = float(self.materials[elset_id1].Material["PoissonRatio"].split()[0])
            try:
                density1 = float(self.materials[elset_id1].Material["Density"].split()[0]) * 1e-12  # kg/m3 -> t/mm3
                if self.materials[elset_id1].Material["Density"].split()[1] not in ["kg/m^3", "kg/m3"]:
                    raise Exception(" units not recognised in " + self.materials[elset_id1].Name)
            except KeyError:
                density1 = 0.
            try:
                conductivity1 = float(self.materials[elset_id1].Material["ThermalConductivity"].split()[0])  # W/m/K
                if self.materials[elset_id1].Material["ThermalConductivity"].split()[1] != "W/m/K":
                    raise Exception(" units not recognised in " + self.materials[elset_id1].Name)
            except KeyError:
                conductivity1 = 0.
            try:
                if self.materials[elset_id1].Material["ThermalExpansionCoefficient"].split()[1] == "um/m/K":
                    expansion1 = float(self.materials[elset_id1].Material["ThermalExpansionCoefficient"].split()[
                                       0]) * 1e-6  # um/m/K -> mm/mm/K
                elif self.materials[elset_id1].Material["ThermalExpansionCoefficient"].split()[1] == "m/m/K":
                    expansion1 = float(self.materials[elset_id1].Material["ThermalExpansionCoefficient"].split()[
                                       0])  # m/m/K -> mm/mm/K
                else:
                    raise Exception(" units not recognised in " + self.materials[elset_id1].Name)
            except KeyError:
                expansion1 = 0.
            try:
                specific_heat1 = float(self.materials[elset_id1].Material["SpecificHeat"].split()[
                                       0]) * 1e6  #  J/kg/K -> mm^2/s^2/K
                if self.materials[elset_id1].Material["SpecificHeat"].split()[1] != "J/kg/K":
                    raise Exception(" units not recognised in " + self.materials[elset_id1].Name)
            except KeyError:
                specific_heat1 = 0.
            if thickness_id1 != -1:
                thickness1 = str(self.thicknesses[thickness_id1].Thickness).split()[0]  # mm
                if str(self.thicknesses[thickness_id1].Thickness).split()[1] != "mm":
                    raise Exception(" units not recognised in " + self.thicknesses[thickness_id1].Name)
            else:
                thickness1 = 0.
            optimized1 = self.form.asDesign_checkbox2.isChecked()
            if self.form.stressLimit_2.text():
                von_mises1 = float(self.form.stressLimit_2.text())
            else:
                von_mises1 = 0.

        elset_id2 = self.form.selectMaterial_3.currentIndex() - 1
        thickness_id2 = self.form.thicknessObject3.currentIndex() - 1
        if elset_id2 != -1:
            if thickness_id2 != -1:
                elset2 = self.materials[elset_id2].Name + self.thicknesses[thickness_id2].Name
            else:  # 0 means None thickness selected
                else2t = self.materials[elset_id2].Name + "Solid"
            modulus2 = float(self.materials[elset_id2].Material["YoungsModulus"].split()[0])  # MPa
            if self.materials[elset_id2].Material["YoungsModulus"].split()[1] != "MPa":
                raise Exception(" units not recognised in " + self.materials[elset_id2].Name)
            poisson2 = float(self.materials[elset_id2].Material["PoissonRatio"].split()[0])
            try:
                density2 = float(self.materials[elset_id2].Material["Density"].split()[0]) * 1e-12  # kg/m3 -> t/mm3
                if self.materials[elset_id2].Material["Density"].split()[1] not in ["kg/m^3", "kg/m3"]:
                    raise Exception(" units not recognised in " + self.materials[elset_id2].Name)
            except KeyError:
                density2 = 0.
            try:
                conductivity2 = float(self.materials[elset_id2].Material["ThermalConductivity"].split()[0])  # W/m/K
                if self.materials[elset_id2].Material["ThermalConductivity"].split()[1] != "W/m/K":
                    raise Exception(" units not recognised in " + self.materials[elset_id2].Name)
            except KeyError:
                conductivity2 = 0.
            try:
                if self.materials[elset_id2].Material["ThermalExpansionCoefficient"].split()[1] == "um/m/K":
                    expansion2 = float(self.materials[elset_id2].Material["ThermalExpansionCoefficient"].split()[
                                       0]) * 1e-6  # um/m/K -> mm/mm/K
                elif self.materials[elset_id2].Material["ThermalExpansionCoefficient"].split()[1] == "m/m/K":
                    expansion2 = float(self.materials[elset_id2].Material["ThermalExpansionCoefficient"].split()[
                                       0])  # m/m/K -> mm/mm/K
                else:
                    raise Exception(" units not recognised in " + self.materials[elset_id2].Name)
            except KeyError:
                expansion2 = 0.
            try:
                specific_heat2 = float(self.materials[elset_id2].Material["SpecificHeat"].split()[
                                       0]) * 1e6  #  J/kg/K -> mm^2/s^2/K
                if self.materials[elset_id2].Material["SpecificHeat"].split()[1] != "J/kg/K":
                    raise Exception(" units not recognised in " + self.materials[elset_id2].Name)
            except KeyError:
                specific_heat2 = 0.
            if thickness_id2 != -1:
                thickness2 = str(self.thicknesses[thickness_id2].Thickness).split()[0]  # mm
                if str(self.thicknesses[thickness_id2].Thickness).split()[1] != "mm":
                    raise Exception(" units not recognised in " + self.thicknesses[thickness_id2].Name)
            else:
                thickness2 = 0.
            optimized2 = self.form.asDesign_checkbox3.isChecked()
            if self.form.stressLimit_3.text():
                von_mises2 = float(self.form.stressLimit_3.text())
            else:
                von_mises2 = 0.

        with open(os.path.join(self.beso_dir, "beso_conf.py"), "w") as f:
            f.write("# This is the configuration file with input parameters. It will be executed as python commands\n")
            f.write("# Written at {}\n".format(datetime.datetime.now()))
            f.write("\n")
            f.write("path_calculix = '{}'\n".format(path_calculix))
            f.write("path = '{}'\n".format(path))
            f.write("file_name = '{}'\n".format(file_name))
            f.write("\n")

            if elset_id != -1:
                f.write("elset_name = '{}'\n".format(elset))
                f.write("domain_optimized[elset_name] = {}\n".format(optimized))
                f.write("domain_density[elset_name] = [{}, {}]\n".format(density * 1e-6, density))
                if thickness:
                    f.write("domain_thickness[elset_name] = [{}, {}]\n".format(thickness, thickness))
                if von_mises:
                    f.write("domain_FI[elset_name] = [[('stress_von_Mises', {:.6})],\n".format(von_mises * 1e6))
                    f.write("                         [('stress_von_Mises', {:.6})]]\n".format(von_mises))
                f.write("domain_material[elset_name] = ['*ELASTIC\\n{:.6}, {}\\n*DENSITY\\n{:.6}\\n*CONDUCTIVITY\\n"
                        "{:.6}\\n*EXPANSION\\n{:.6}\\n*SPECIFIC HEAT\\n{:.6}\\n',\n".format(modulus * 1e-6, poisson,
                        density * 1e-6, conductivity * 1e-6, expansion * 1e-6, specific_heat * 1e-6))
                f.write("                               '*ELASTIC\\n{:.6}, {:.6}\\n*DENSITY\\n{:.6}\\n*CONDUCTIVITY\\n"
                        "{:.6}\\n*EXPANSION\\n{:.6}\\n*SPECIFIC HEAT\\n{:.6}\\n']\n".format(modulus, poisson, density,
                         conductivity, expansion, specific_heat))
                f.write("\n")
            if elset_id1 != -1:
                f.write("elset_name = '{}'\n".format(elset1))
                f.write("domain_optimized[elset_name] = {}\n".format(optimized1))
                f.write("domain_density[elset_name] = [{}, {}]\n".format(density1 * 1e-6, density1))
                if thickness1:
                    f.write("domain_thickness[elset_name] = [{}, {}]\n".format(thickness1, thickness1))
                if von_mises1:
                    f.write("domain_FI[elset_name] = [[('stress_von_Mises', {:.6})],\n".format(von_mises1 * 1e6))
                    f.write("                         [('stress_von_Mises', {:.6})]]\n".format(von_mises1))
                f.write("domain_material[elset_name] = ['*ELASTIC\\n{:.6}, {:.6}\\n*DENSITY\\n{:.6}\\n*CONDUCTIVITY"
                        "\\n{:.6}\\n*EXPANSION\\n{:.6}\\n*SPECIFIC HEAT\\n{:.6}\\n',\n".format(modulus1 * 1e-6,
                        poisson1, density1 * 1e-6, conductivity1 * 1e-6, expansion1 * 1e-6, specific_heat1 * 1e-6))
                f.write("                               '*ELASTIC\\n{:.6}, {:.6}\\n*DENSITY\\n{:.6}\\n*CONDUCTIVITY\\n"
                        "{:.6}\\n" "*EXPANSION\\n{:.6}\\n*SPECIFIC HEAT\\n{:.6}\\n']\n".format(modulus1, poisson1,
                         density1, conductivity1, expansion1, specific_heat1))
                f.write("\n")
            if elset_id2 != -1:
                f.write("elset_name = '{}'\n".format(elset2))
                f.write("domain_optimized[elset_name] = {}\n".format(optimized2))
                f.write("domain_density[elset_name] = [{}, {}]\n".format(density2 * 1e-6, density2))
                if thickness2:
                    f.write("domain_thickness[elset_name] = [{}, {}]\n".format(thickness2, thickness2))
                if von_mises2:
                    f.write("domain_FI[elset_name] = [[('stress_von_Mises', {:.6})],\n".format(von_mises2 * 1e6))
                    f.write("                         [('stress_von_Mises', {:.6})]]\n".format(von_mises2))
                f.write("domain_material[elset_name] = ['*ELASTIC\\n{:.6}, {:.6}\\n*DENSITY\\n{:.6}\\n*CONDUCTIVITY"
                        "\\n{:.6}\\n*EXPANSION\\n{:.6}\\n*SPECIFIC HEAT\\n{:.6}\\n',\n".format(modulus2 * 1e-6,
                        poisson2, density2 * 1e-6, conductivity2 * 1e-6, expansion2 * 1e-6, specific_heat2 * 1e-6))
                f.write("                               '*ELASTIC\\n{:.6}, {:.6}\\n*DENSITY\\n{:.6}\\n*CONDUCTIVITY\\n"
                        "{:.6}\\n*EXPANSION\\n{:.6}\\n*SPECIFIC HEAT\\n{:.6}\\n']\n".format(modulus2, poisson2,
                         density2, conductivity2, expansion2, specific_heat2))
                f.write("\n")
            f.write("mass_goal_ratio = " + self.form.massGoalRatio.text())
            f.write("\n")

            f.write("filter_list = [")
            filter = self.form.selectFilter_1.currentText()
            if self.form.filterRange_1.currentText() == "auto":
                range = '"auto"'
            elif self.form.filterRange_1.currentText() == "manual":
                range = self.form.range_1.text()
            direction = self.form.directionVector_1.text()
            selection = [item.text() for item in self.form.domainList_1.selectedItems()]

            filter_domains = []
            if "All defined" not in selection:
                if "Domain 0" in selection:
                    filter_domains.append(elset)
                if "Domain 1" in selection:
                    filter_domains.append(elset1)
                if "Domain 2" in selection:
                    filter_domains.append(elset2)
            if filter == "simple":
                f.write("['simple', {}".format(range))
                for dn in filter_domains:
                    f.write(", '{}'".format(dn))
                f.write("],\n")
            elif filter == "casting":
                f.write("['casting', {}, ({})".format(range, direction))
                for dn in filter_domains:
                    f.write(", '{}'".format(dn))
                f.write("],\n")

            filter1 = self.form.selectFilter_2.currentText()
            if self.form.filterRange_2.currentText() == "auto":
                range1 = '"auto"'
            elif self.form.filterRange_2.currentText() == "manual":
                range1 = self.form.range_2.text()
            direction1 = self.form.directionVector_2.text()
            selection = [item.text() for item in self.form.domainList_2.selectedItems()]
            filter_domains1 = []
            if "All defined" not in selection:
                if "Domain 0" in selection:
                    filter_domains1.append(elset)
                if "Domain 1" in selection:
                    filter_domains1.append(elset1)
                if "Domain 2" in selection:
                    filter_domains1.append(elset2)
            if filter1 == "simple":
                f.write("               ['simple', {}".format(range1))
                for dn in filter_domains1:
                    f.write(", '{}'".format(dn))
                f.write("],\n")
            elif filter1 == "casting":
                f.write("               ['casting', {}, ({})".format(range1, direction1))
                for dn in filter_domains1:
                    f.write(", '{}'".format(dn))
                f.write("],\n")

            filter2 = self.form.selectFilter_3.currentText()
            if self.form.filterRange_3.currentText() == "auto":
                range2 = '"auto"'
            elif self.form.filterRange_3.currentText() == "manual":
                range2 = self.form.range_3.text()
            direction2 = self.form.directionVector_3.text()
            selection = [item.text() for item in self.form.domainList_3.selectedItems()]

            filter_domains2 = []
            if "All defined" not in selection:
                if "Domain 0" in selection:
                    filter_domains2.append(elset)
                if "Domain 1" in selection:
                    filter_domains2.append(elset1)
                if "Domain 2" in selection:
                    filter_domains2.append(elset2)
            if filter2 == "simple":
                f.write("               ['simple', {}".format(range2))
                for dn in filter_domains2:
                    f.write(", '{}'".format(dn))
                f.write("],\n")
            elif filter2 == "casting":
                f.write("               ['casting', {}, ({})".format(range2, direction2))
                for dn in filter_domains2:
                    f.write(", '{}'".format(dn))
                f.write("],\n")
            f.write("               ]\n")
            f.write("\n")

            f.write("optimization_base = '{}'\n".format(optimization_base))
            f.write("\n")

            slider_position = self.form.iterationSlider.value()

            if slider_position == 0:
                f.write("mass_addition_ratio = 0.01\n")
                f.write("mass_removal_ratio = 0.02\n")
            if slider_position == 1:
                f.write("mass_addition_ratio = 0.015\n")
                f.write("mass_removal_ratio = 0.03\n")
            if slider_position == 2:
                f.write("mass_addition_ratio = 0.03\n")
                f.write("mass_removal_ratio = 0.06\n")
            f.write("ratio_type = 'relative'\n")
            f.write("\n")

    def editConfig(self):
        """Open beso_conf.py in FreeCAD editor"""
        Gui.insert(os.path.join(MyGui.beso_dir, "beso_conf.py"))

    def runOptimization(self):
        #Run optimization
        #run in own thread (not freezing FreeCAD):      needs also to comment "plt.show()" on the end of beso_main.py
        #self.optimization_thread = RunOptimization("beso_main")
        #self.optimization_thread.start()

        # run in foreground (freeze FreeCAD)
        exec(open(os.path.join(self.beso_dir, "beso_main.py")).read())

    
    def openExample(self):
        webbrowser.open_new_tab("https://github.com/fandaL/beso/wiki/Example-4:-GUI-in-FreeCAD")

    def openConfComments(self):
        webbrowser.open_new_tab("https://github.com/fandaL/beso/blob/master/beso_conf.py")

    def openLog(self):
        """Open log file"""
        if self.form.fileName.text() in ["None analysis file selected", ""]:
            print("None analysis file selected")
        else:
            log_file = os.path.normpath(self.form.fileName.text()[:-4] + ".log")
            webbrowser.open(log_file)

    def selectMaterial1(self):
        if self.form.selectMaterial_1.currentText() == "None":
            self.form.thicknessObject1.setEnabled(False)
            self.form.asDesign_checkbox.setEnabled(False)
            self.form.stressLimit_1.setEnabled(False)
        else:
            self.form.thicknessObject1.setEnabled(True)
            self.form.asDesign_checkbox.setEnabled(True)
            self.form.stressLimit_1.setEnabled(True)

    def selectMaterial2(self):
        if self.form.selectMaterial_2.currentText() == "None":
            self.form.thicknessObject2.setEnabled(False)
            self.form.asDesign_checkbox2.setEnabled(False)
            self.form.stressLimit_2.setEnabled(False)
        else:
            self.form.thicknessObject2.setEnabled(True)
            self.form.asDesign_checkbox2.setEnabled(True)
            self.form.stressLimit_2.setEnabled(True)

    def selectMaterial3(self):
        if self.form.selectMaterial_3.currentText() == "None":
            self.form.thicknessObject3.setEnabled(False)
            self.form.asDesign_checkbox3.setEnabled(False)
            self.form.stressLimit_3.setEnabled(False)
        else:
            self.form.thicknessObject3.setEnabled(True)
            self.form.asDesign_checkbox3.setEnabled(True)
            self.form.stressLimit_3.setEnabled(True)

    def filterRange1(self):
        if self.form.filterRange_1.currentText() == "auto":
            self.form.range_1.setEnabled(False) #range as mm
        elif self.form.filterRange_1.currentText() == "manual":
            self.form.range_1.setEnabled(True)

    def filterRange2(self):
        if self.form.filterRange_2.currentText() == "auto":
            self.form.range_2.setEnabled(False)
        elif self.form.filterRange_2.currentText() == "manual":
            self.form.range_2.setEnabled(True)

    def filterRange3(self):
        if self.form.filterRange_3.currentText() == "auto":
            self.form.range_3.setEnabled(False)
        elif self.form.filterRange_3.currentText() == "manual":
            self.form.range_3.setEnabled(True)

    def filterType1(self):
        if self.form.selectFilter_1.currentText() == "None":
            self.form.filterRange_1.setEnabled(False)
            self.form.range_1.setEnabled(False)
            self.form.directionVector_1.setEnabled(False)
            self.form.domainList_1.setEnabled(False)
        elif self.form.selectFilter_1.currentText() == "casting":
            self.form.filterRange_1.setEnabled(True)
            if self.form.filterRange_1.currentText() == "manual":
                self.form.range_1.setEnabled(True)
            self.form.directionVector_1.setEnabled(True)
            self.form.domainList_1.setEnabled(True)
        else:
            self.form.filterRange_1.setEnabled(True)
            if self.form.filterRange_1.currentText() == "manual":
                self.form.range_1.setEnabled(True)
            self.form.directionVector_1.setEnabled(False)
            self.form.domainList_1.setEnabled(True)

    def filterType2(self):
        if self.form.selectFilter_2.currentText() == "None":
            self.form.filterRange_2.setEnabled(False)
            self.form.range_2.setEnabled(False)
            self.form.directionVector_2.setEnabled(False)
            self.form.domainList_2.setEnabled(False)
        elif self.form.selectFilter_2.currentText() == "casting":
            self.form.filterRange_2.setEnabled(True)
            if self.form.filterRange_2.currentText() == "manual":
                self.form.range_2.setEnabled(True)
            self.form.directionVector_2.setEnabled(True)
            self.form.domainList_2.setEnabled(True)
        else:
            self.form.filterRange_2.setEnabled(True)
            if self.form.filterRange_2.currentText() == "manual":
                self.form.range_2.setEnabled(True)
            self.form.directionVector_2.setEnabled(False)
            self.form.domainList_2.setEnabled(True)

    def filterType3(self):
        if self.form.selectFilter_3.currentText() == "None":
            self.form.filterRange_3.setEnabled(False)
            self.form.range_3.setEnabled(False)
            self.form.directionVector_3.setEnabled(False)
            self.form.domainList_3.setEnabled(False)
        elif self.form.selectFilter_3.currentText() == "casting":
            self.form.filterRange_3.setEnabled(True)
            if self.form.filterRange_3.currentText() == "manual":
                self.form.range_3.setEnabled(True)
            self.form.directionVector_3.setEnabled(True)
            self.form.domainList_3.setEnabled(True)
        else:
            self.form.filterRange_3.setEnabled(True)
            if self.form.filterRange_3.currentText() == "manual":
                self.form.range_3.setEnabled(True)
            self.form.directionVector_3.setEnabled(False)
            self.form.domainList_3.setEnabled(True)

    
    def accept(self):
        doc = App.ActiveDocument()
        doc.resetEdit()
	

    def reject(self):
        Gui.Control.closeDialog()
     
class ViewProviderGen:
    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        icon_path = os.path.join(App.getUserAppDataDir() + 'Mod/FEMbyGEN/fembygen/Topology.svg')
        return icon_path

    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object

    def updateData(self, obj, prop):
        return

    def onChanged(self, vobj, prop):
        return

    def doubleClicked(self, vobj):
        doc = Gui.getDocument(vobj.Object.Document)
        if not doc.getInEdit():
            doc.setEdit(vobj.Object.Name)
        else:
            App.Console.PrintError('Existing task dialog already open\n')
        return True

    def setEdit(self, vobj, mode):
        taskd = MyGui(vobj)
        taskd.obj = vobj.Object
        Gui.Control.showDialog(taskd)
        return True

    def unsetEdit(self, vobj, mode):
        Gui.Control.closeDialog()
        return

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

Gui.addCommand('Topology', TopologyCommand())
