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
    path = os.path.split(self.form.lineEdit_3.text())[0]
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
        # panel = GeneratePanel(obj)
        # FreeCADGui.Control.showDialog(panel)
        #panel = MyGui()
        #Gui.Control.showDialog(panel)
        #doc = Gui.ActiveDocument
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
        
        self.form.comboBox_14.currentIndexChanged.connect(self.on_click)
        self.form.pushButton_7.clicked.connect(self.on_click1)
        self.form.comboBox_7.currentIndexChanged.connect(self.on_change)
        self.form.comboBox_8.currentIndexChanged.connect(self.on_change1)
        self.form.comboBox_9.currentIndexChanged.connect(self.on_change2)
        self.form.comboBox_10.currentIndexChanged.connect(self.on_change6)
        self.form.comboBox_11.currentIndexChanged.connect(self.on_change7)
        self.form.comboBox_12.currentIndexChanged.connect(self.on_change8)
        self.form.comboBox.currentIndexChanged.connect(self.on_change6r)
        self.form.comboBox_2.currentIndexChanged.connect(self.on_change7r)
        self.form.comboBox_3.currentIndexChanged.connect(self.on_change8r)
        self.form.pushButton_8.clicked.connect(self.on_click21)
        self.form.pushButton_9.clicked.connect(self.on_click22)
        self.form.pushButton_10.clicked.connect(self.on_click23)
        self.form.pushButton_14.clicked.connect(self.on_click31)
        self.form.pushButton_15.clicked.connect(self.on_click32)
        self.form.pushButton_11.clicked.connect(self.on_click40)

        self.on_click1()  # first update


    def on_click(self):
        self.form.lineEdit_3.setText(self.workingDir + f"/Gen{self.form.comboBox_14.currentIndex()+1}/loadCase1/FEMMeshNetgen.inp")
        MyGui.inp_file = self.form.lineEdit_3.text()
    
    def resetViewControls(self, numGens):
        comboBoxItems = []
        if numGens > 0:
            self.form.comboBox_14.setEnabled(True)
            
            for i in range(1, numGens+1):
                comboBoxItems.append("Generation " + str(i))

            self.form.comboBox_14.clear()
            self.form.comboBox_14.addItems(comboBoxItems)
            self.form.lineEdit_3.setText(self.workingDir + f"/Gen{self.form.comboBox_14.currentIndex()+1}/loadCase1/FEMMeshNetgen.inp")
        else:
            self.form.comboBox_14.setEnabled(False)

    
    def on_click1(self):
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

        
        self.form.listWidget_2.setCurrentItem(self.form.listWidget_2.item(0))

        
        self.form.listWidget_3.setCurrentItem(self.form.listWidget_3.item(0))

        
        self.form.listWidget.setCurrentItem(self.form.listWidget.item(0))

        for mat in self.materials:
            self.form.comboBox_7.addItem(mat.Label)
            self.form.comboBox_8.addItem(mat.Label)
            self.form.comboBox_9.addItem(mat.Label)
        if self.materials:
            self.form.comboBox_7.setCurrentIndex(1)
        for th in self.thicknesses:
            self.form.comboBox_4.addItem(th.Label)
            self.form.comboBox_5.addItem(th.Label)
            self.form.comboBox_6.addItem(th.Label)

    def on_click21(self):

        file_name = os.path.split(self.form.lineEdit_3.text())[1]
        path = os.path.split(self.form.lineEdit_3.text())[0]
        #global elset2
        #global elset
        #global elset1
        elset2 = ""
        elset = ""
        elset1 = ""
        fea = ccxtools.FemToolsCcx()
        fea.setup_ccx()
        path_calculix = fea.ccx_binary

        optimization_base = self.form.comboBox_13.currentText()

        elset_id = self.form.comboBox_7.currentIndex() - 1
        thickness_id = self.form.comboBox_4.currentIndex() - 1
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
            optimized = self.form.checkBox_3.isChecked()
            if self.form.lineEdit_4.text():
                von_mises = float(self.form.lineEdit_4.text())
            else:
                von_mises = 0.

        elset_id1 = self.form.comboBox_8.currentIndex() - 1
        thickness_id1 = self.form.comboBox_5.currentIndex() - 1
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
            optimized1 = self.form.checkBox_2.isChecked()
            if self.form.lineEdit_5.text():
                von_mises1 = float(self.form.lineEdit_5.text())
            else:
                von_mises1 = 0.

        elset_id2 = self.form.comboBox_9.currentIndex() - 1
        thickness_id2 = self.form.comboBox_6.currentIndex() - 1
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
            optimized2 = self.form.checkBox.isChecked()
            if self.form.lineEdit_6.text():
                von_mises2 = float(self.form.lineEdit_6.text())
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
            f.write("mass_goal_ratio = " + self.form.lineEdit_2.text())
            f.write("\n")

            f.write("filter_list = [")
            filter = self.form.comboBox_10.currentText()
            if self.form.comboBox.currentText() == "auto":
                range = '"auto"'
            elif self.form.comboBox.currentText() == "manual":
                range = self.form.lineEdit_8.text()
            direction = self.form.lineEdit.text()
            selection = [item.text() for item in self.form.listWidget_2.selectedItems()]
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

            filter1 = self.form.comboBox_11.currentText()
            if self.form.comboBox_2.currentText() == "auto":
                range1 = '"auto"'
            elif self.form.comboBox_2.currentText() == "manual":
                range1 = self.form.lineEdit_9.text()
            direction1 = self.form.lineEdit_14.text()
            selection = [item.text() for item in self.form.listWidget_3.selectedItems()]
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

            filter2 = self.form.comboBox_12.currentText()
            if self.form.comboBox_3.currentText() == "auto":
                range2 = '"auto"'
            elif self.form.comboBox_3.currentText() == "manual":
                range2 = self.form.lineEdit_12.text()
            direction2 = self.form.lineEdit_15.text()
            selection = [item.text() for item in self.form.listWidget.selectedItems()]
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

            slider_position = self.form.horizontalSlider_3.value()
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

    def on_click22(self):
        """Open beso_conf.py in FreeCAD editor"""
        Gui.insert(os.path.join(MyGui.beso_dir, "beso_conf.py"))

    def on_click23(self):
        #Run optimization
         #run in own thread (not freezing FreeCAD):      needs also to comment "plt.show()" on the end of beso_main.py
         #self.optimization_thread = RunOptimization("beso_main")
         #self.optimization_thread.start()

        # run in foreground (freeze FreeCAD)
        exec(open(os.path.join(self.beso_dir, "beso_main.py")).read())

    
    def on_click31(self):
        webbrowser.open_new_tab("https://github.com/fandaL/beso/wiki/Example-4:-GUI-in-FreeCAD")

    def on_click32(self):
        webbrowser.open_new_tab("https://github.com/fandaL/beso/blob/master/beso_conf.py")

    def on_click40(self):
        """Open log file"""
        if self.form.lineEdit_3.text() in ["None analysis file selected", ""]:
            print("None analysis file selected")
        else:
            log_file = os.path.normpath(self.form.lineEdit_3.text()[:-4] + ".log")
            webbrowser.open(log_file)

    def on_change(self):
        if self.form.comboBox_7.currentText() == "None":
            self.form.comboBox_4.setEnabled(False)
            self.form.checkBox_3.setEnabled(False)
            self.form.lineEdit_4.setEnabled(False)
        else:
            self.form.comboBox_4.setEnabled(True)
            self.form.checkBox_3.setEnabled(True)
            self.form.lineEdit_4.setEnabled(True)

    def on_change1(self):
        if self.form.comboBox_8.currentText() == "None":
            self.form.comboBox_5.setEnabled(False)
            self.form.checkBox_2.setEnabled(False)
            self.form.lineEdit_5.setEnabled(False)
        else:
            self.form.comboBox_5.setEnabled(True)
            self.form.checkBox_2.setEnabled(True)
            self.form.lineEdit_5.setEnabled(True)

    def on_change2(self):
        if self.form.comboBox_9.currentText() == "None":
            self.form.comboBox_6.setEnabled(False)
            self.form.checkBox.setEnabled(False)
            self.form.lineEdit_6.setEnabled(False)
        else:
            self.form.comboBox_6.setEnabled(True)
            self.form.checkBox.setEnabled(True)
            self.form.lineEdit_6.setEnabled(True)

    def on_change6r(self):
        if self.form.comboBox.currentText() == "auto":
            self.form.lineEdit_8.setEnabled(False)
        elif self.form.comboBox.currentText() == "manual":
            self.form.lineEdit_8.setEnabled(True)

    def on_change7r(self):
        if self.form.comboBox_2.currentText() == "auto":
            self.form.lineEdit_9.setEnabled(False)
        elif self.form.comboBox_2.currentText() == "manual":
            self.form.lineEdit_9.setEnabled(True)

    def on_change8r(self):
        if self.form.comboBox_3.currentText() == "auto":
            self.form.lineEdit_12.setEnabled(False)
        elif self.form.comboBox_3.currentText() == "manual":
            self.form.lineEdit_12.setEnabled(True)

    def on_change6(self):
        if self.form.comboBox_10.currentText() == "None":
            self.form.comboBox.setEnabled(False)
            self.form.lineEdit_8.setEnabled(False)
            self.form.lineEdit.setEnabled(False)
            self.form.listWidget_2.setEnabled(False)
        elif self.form.comboBox_10.currentText() == "casting":
            self.form.comboBox.setEnabled(True)
            if self.form.comboBox.currentText() == "manual":
                self.form.lineEdit_8.setEnabled(True)
            self.form.lineEdit.setEnabled(True)
            self.form.listWidget_2.setEnabled(True)
        else:
            self.form.comboBox.setEnabled(True)
            if self.form.comboBox.currentText() == "manual":
                self.form.lineEdit_8.setEnabled(True)
            self.form.lineEdit.setEnabled(False)
            self.form.listWidget_2.setEnabled(True)

    def on_change7(self):
        if self.form.comboBox_11.currentText() == "None":
            self.form.comboBox_2.setEnabled(False)
            self.form.lineEdit_9.setEnabled(False)
            self.form.lineEdit_14.setEnabled(False)
            self.form.listWidget_3.setEnabled(False)
        elif self.form.comboBox_11.currentText() == "casting":
            self.form.comboBox_2.setEnabled(True)
            if self.form.comboBox_2.currentText() == "manual":
                self.form.lineEdit_9.setEnabled(True)
            self.form.lineEdit_14.setEnabled(True)
            self.form.listWidget_3.setEnabled(True)
        else:
            self.form.comboBox_2.setEnabled(True)
            if self.form.comboBox_2.currentText() == "manual":
                self.form.lineEdit_9.setEnabled(True)
            self.form.lineEdit_14.setEnabled(False)
            self.form.listWidget_3.setEnabled(True)

    def on_change8(self):
        if self.form.comboBox_12.currentText() == "None":
            self.form.comboBox_3.setEnabled(False)
            self.form.lineEdit_12.setEnabled(False)
            self.form.lineEdit_15.setEnabled(False)
            self.form.listWidget.setEnabled(False)
        elif self.form.comboBox_12.currentText() == "casting":
            self.form.comboBox_3.setEnabled(True)
            if self.form.comboBox_3.currentText() == "manual":
                self.form.lineEdit_12.setEnabled(True)
            self.form.lineEdit_15.setEnabled(True)
            self.form.listWidget.setEnabled(True)
        else:
            self.form.comboBox_3.setEnabled(True)
            if self.form.comboBox_3.currentText() == "manual":
                self.form.lineEdit_12.setEnabled(True)
            self.form.lineEdit_15.setEnabled(False)
            self.form.listWidget.setEnabled(True)

    
    def accept(self):
        Gui.Control.closeDialog()

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
