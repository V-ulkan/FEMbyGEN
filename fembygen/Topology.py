import FreeCAD as App
import FreeCADGui as Gui
import os
from PySide import QtGui, QtCore
from femtools import ccxtools
import datetime
import webbrowser
from fembygen.topology import beso_main
from fembygen import Common
from multiprocessing import cpu_count
from PySide2.QtWidgets import QPushButton, QComboBox, QSplitter, QCheckBox, QLineEdit, QListWidget, QLabel, QVBoxLayout, QAbstractItemView


def makeTopology():
    def attach(self, vobj):
        self.ViewObject = vobj
        self.Object = vobj.Object
 
    obj = App.ActiveDocument.addObject(
        "App::DocumentObjectGroupPython", "Topology")
    try:
        App.ActiveDocument.Generative_Design.addObject(obj)
    except:
        print("continue only for topology analysis")
    Topology(obj)
    if App.GuiUp:
        ViewProviderGen(obj.ViewObject)
    return obj


def returnPath():
    path = os.path.split(self.form.fileName.text())[0]  # fileName contains full path not only file name


class Topology:
    def __init__(self, obj):
        obj.Proxy = self
        self.Type = "Topology"
        self.initProperties(obj)

    def initProperties(self, obj):
        try:
            obj.addProperty("App::PropertyFloat", "mass_addition_ratio", "Mass",
                            "The ratio to add mass between iterations ")
            obj.mass_addition_ratio = 0.015
            obj.addProperty("App::PropertyFloat", "mass_removal_ratio", "Mass",
                            "The ratio to add mass between iterations ")
            obj.mass_removal_ratio = 0.03
            obj.addProperty("App::PropertyInteger", "LastState", "Results",
                            "Last state")
            
            obj.addProperty("App::PropertyString", "path_calculix", "Base", "Path to CalculiX")
       

            obj.addProperty("App::PropertyString", "path", "Base", "Path")

            obj.addProperty("App::PropertyString", "file_name", "Base", "File Name")

            obj.addProperty("App::PropertyPythonObject", "domain_offset", "Domain", "Domain Offset")
            obj.domain_offset={}

            obj.addProperty("App::PropertyPythonObject", "domain_orientation", "Domain", "Domain Orientation")
            obj.domain_orientation={}

            obj.addProperty("App::PropertyPythonObject", "domain_FI", "Domain", "Domain FI")
            obj.domain_FI={}

            obj.addProperty("App::PropertyPythonObject", "domain_same_state", "Domain", "Domain Same State")
            obj.domain_same_state={}

            obj.addProperty("App::PropertyString", "continue_from", "Base", "Continue From")
            obj.continue_from = ''

            obj.addProperty("App::PropertyPythonObject", "filter_list", "Base", "Filter List")
            obj.filter_list = [['simple', 0]]

            obj.addProperty("App::PropertyInteger", "cpu_cores", "Base", "CPU Cores")
            obj.cpu_cores = cpu_count()

            obj.addProperty("App::PropertyFloat", "FI_violated_tolerance", "Base", "FI Violated Tolerance")
            obj.FI_violated_tolerance = 1.0

            obj.addProperty("App::PropertyFloat", "decay_coefficient", "Base", "Decay Coefficient")
            obj.decay_coefficient = -0.2

            obj.addProperty("App::PropertyBool", "shells_as_composite", "Base", "Shells as Composite")
            obj.shells_as_composite = False

            obj.addProperty("App::PropertyString", "reference_points", "Base", "Reference Points")
            obj.reference_points = 'integration points'

            obj.addProperty("App::PropertyString", "reference_value", "Base", "Reference Value")
            obj.reference_value = 'max'

            obj.addProperty("App::PropertyBool", "sensitivity_averaging", "Base", "Sensitivity Averaging")
            obj.sensitivity_averaging = False

            obj.addProperty("App::PropertyBool", "compensate_state_filter", "Base", "Compensate State Filter")
            obj.compensate_state_filter = False

            obj.addProperty("App::PropertyIntegerList", "steps_superposition", "Base", "Steps Superposition")
            obj.steps_superposition = []

            obj.addProperty("App::PropertyString", "iterations_limit", "Base", "Iterations Limit")
            obj.iterations_limit = 'auto'

            obj.addProperty("App::PropertyFloat", "tolerance", "Base", "Tolerance")
            obj.tolerance = 1e-3

            obj.addProperty("App::PropertyStringList", "displacement_graph", "Base", "Displacement Graph")
            obj.displacement_graph = []

            obj.addProperty("App::PropertyInteger", "save_iteration_results", "Base", "Save Iteration Results")
            obj.save_iteration_results = 1

            obj.addProperty("App::PropertyString", "save_solver_files", "Base", "Save Solver Files")
            obj.save_solver_files = ''

            obj.addProperty("App::PropertyString", "save_resulting_format", "Base", "Save Resulting Format")
            obj.save_resulting_format = 'inp'


            obj.addProperty("App::PropertyPythonObject", "domain_optimized", "Domain", "Domain Optimized")
            obj.domain_optimized={}
         

            obj.addProperty("App::PropertyPythonObject", "domain_density", "Domain", "Domain Density")
            obj.domain_density={}
            obj.addProperty("App::PropertyPythonObject", "domain_thickness", "Domain", "Domain Density")
            obj.domain_thickness={}
            obj.addProperty("App::PropertyFloat", "stress_limit", "Base", "Stress Limit")

            
            obj.addProperty("App::PropertyPythonObject", "domain_material", "Domain", "Domain Material")
            obj.domain_material={}
            
            obj.addProperty("App::PropertyFloat", "mass_goal_ratio", "Mass", "Mass Goal Ratio")
         

            obj.addProperty("App::PropertyPythonObject", "filter_list2", "Base", "Filter List 2")
            obj.filter_list2 = [['simple', 'auto']]

            obj.addProperty("App::PropertyString", "optimization_base", "Base", "Optimization Base")
            
            obj.addProperty("App::PropertyString", "ratio_type", "Base", "Ratio Type")
            obj.ratio_type = 'relative'
        except:
            pass


class TopologyCommand():

    def GetResources(self):
        return {'Pixmap': os.path.join(App.getUserAppDataDir() + 'Mod/FEMbyGEN/fembygen/icons/Topology.svg'),  # the name of a svg file available in the resources
                'Accel': "Shift+T",  # a default shortcut (optional)
                'MenuText': "Topology",
                'ToolTip': "Opens Topology gui"}

    def Activated(self):

        obj = makeTopology()
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


class TopologyPanel(QtGui.QWidget):
    def __init__(self, object):
        self.obj = object
        guiPath = App.getUserAppDataDir() + "Mod/FEMbyGEN/fembygen/ui/Beso.ui"
        self.form = Gui.PySideUic.loadUi(guiPath)
        self.workingDir = '/'.join(
            object.Object.Document.FileName.split('/')[0:-1])
        self.doc = object.Object.Document

        numGens = Common.checkGenerations(self.workingDir)
        self.getGenerations(numGens)

        self.inp_file = ""
        self.beso_dir = os.path.dirname(__file__)
        # self.form.Faces.setReadOnly(True)

        self.materials = []
        self.thicknesses = []
        self.form.iterationSlider.sliderMoved.connect(self.massratio)

        for obj in App.ActiveDocument.Objects:
            if obj.Name[:23] == "MechanicalSolidMaterial":
                self.materials.append(obj)
            elif obj.Name[:13] == "MaterialSolid":
                self.materials.append(obj)
            elif obj.Name[:13] == "SolidMaterial":
                self.materials.append(obj)
            elif obj.Name[:17] == "ElementGeometry2D":
                self.thicknesses.append(obj)

        # necessary layouts to add new domain widgets
        self.form.layout = self.form.horizontalLayout_13
        self.form.layout2 = self.form.horizontalLayout_12
        self.form.layout3 = self.form.horizontalLayout_11
        self.form.layout4 = self.form.horizontalLayout_10
        self.form.layout5 = self.form.horizontalLayout_9
        self.form.layout6 = self.form.horizontalLayout_7
        self.form.layout7 = self.form.horizontalLayout_6
        self.form.layout8 = self.form.horizontalLayout_5
        self.form.layout9 = self.form.horizontalLayout_4
        self.form.layout10 = self.form.horizontalLayout_3
        self.form.verticalLayout2 = QVBoxLayout()
        self.form.verticalLayout3 = QVBoxLayout()

        # new Domain labels
        self.form.label1 = QLabel("Domain 1")
        self.form.label2 = QLabel("Domain 2")
        self.form.label3 = QLabel("Filter 1")
        self.form.label4 = QLabel("Filter 2")

        # Creating widgets for new domains
        self.form.horizontal1 = QSplitter()  # creating horizantal sliders to set placement
        self.form.horizontal2 = QSplitter()
        self.form.horizontal3 = QSplitter()
        self.form.horizontal4 = QSplitter()
        self.form.horizontal5 = QSplitter()
        self.form.horizontal6 = QSplitter()
        self.form.horizontal7 = QSplitter()
        self.form.horizontal8 = QSplitter()
        self.form.horizontal9 = QSplitter()
        self.form.horizontal10 = QSplitter()
        self.form.horizontal11 = QSplitter()
        self.form.horizontal12 = QSplitter()
        self.form.horizontal13 = QSplitter()
        self.form.horizontal14 = QSplitter()
        self.form.horizontal15 = QSplitter()
        """self.form.vertical1 = QSplitter()
        self.form.vertical2 = QSplitter()"""

        self.form.selectMaterial_2 = QComboBox()
        self.form.selectMaterial_3 = QComboBox()
        self.form.thicknessObject2 = QComboBox()
        self.form.thicknessObject3 = QComboBox()
        self.form.asDesign_checkbox2 = QCheckBox()
        self.form.asDesign_checkbox2.setChecked(True)
        self.form.asDesign_checkbox3 = QCheckBox()
        self.form.asDesign_checkbox3.setChecked(True)
        self.form.stressLimit_2 = QLineEdit()
        self.form.stressLimit_3 = QLineEdit()
        self.form.selectFilter_2 = QComboBox()
        self.form.selectFilter_2.addItems(["None", "simple", "casting"])
        self.form.selectFilter_3 = QComboBox()
        self.form.selectFilter_3.addItems(["None", "simple", "casting"])
        self.form.filterRange_2 = QComboBox()
        self.form.filterRange_2.addItems(["auto", "manual"])
        self.form.filterRange_2.setEnabled(False)
        self.form.filterRange_3 = QComboBox()
        self.form.filterRange_3.addItems(["auto", "manual"])
        self.form.filterRange_3.setEnabled(False)
        self.form.filterRange_2.setMaximumSize(50, 20)
        self.form.filterRange_3.setMaximumSize(50, 20)
        self.form.range_2 = QLineEdit()
        self.form.range_3 = QLineEdit()
        self.form.range_2.setMaximumSize(50, 20)
        self.form.range_2.setText("0.")
        self.form.range_2.setEnabled(False)
        self.form.range_3.setMaximumSize(50, 20)
        self.form.range_3.setText("0.")
        self.form.range_3.setEnabled(False)
        self.form.directionVector_2 = QLineEdit()
        self.form.directionVector_2.setText("0,0,1")
        self.form.directionVector_2.setEnabled(False)
        self.form.directionVector_3 = QLineEdit()
        self.form.directionVector_3.setText("0,0,1")
        self.form.directionVector_3.setEnabled(False)
        self.form.domainList_2 = QListWidget()
        self.form.domainList_2.setSelectionMode(QAbstractItemView.MultiSelection)
        self.form.domainList_3 = QListWidget()
        self.form.domainList_3.setSelectionMode(QAbstractItemView.MultiSelection)
        self.form.addButton.setFixedSize(30, 23)
        self.form.deleteDomainButton = QPushButton("-")
        self.form.deleteDomainButton.setFixedSize(30, 23)
        self.form.deleteDomainButton2 = QPushButton("-")
        self.form.deleteDomainButton2.setFixedSize(30, 23)
        self.form.newAddButton = QPushButton("+")
        self.form.newAddButton.setFixedSize(30, 23)

        # adding constraint for mass goal ratio between 0.0 - 1.0
        self.form.validator = QtGui.QDoubleValidator(0.0,1.0, 2) 
        self.form.massGoalRatio.setValidator(self.form.validator)

        self.form.selectMaterial_1.clear()
        self.form.selectMaterial_1.addItem("None")
        self.form.thicknessObject1.clear()
        self.form.thicknessObject1.addItem("None")
        self.form.domainList_1.clear()
        self.form.domainList_1.addItem("All defined")
        self.form.domainList_1.addItem("Domain 0")
        self.form.domainList_1.setCurrentItem(self.form.domainList_1.item(0))

        self.form.layout.addWidget(self.form.label1, stretch=1)
        self.form.layout.addWidget(self.form.horizontal1, stretch=1)
        self.form.layout.addWidget(self.form.label2, stretch=1)

        self.form.layout.addWidget(self.form.newAddButton, stretch=1)
        self.form.newAddButton.setVisible(False)
        self.form.horizontal1.setVisible(False)
        self.form.label1.setVisible(False)
        self.form.label2.setVisible(False)
        self.form.layout.addWidget(self.form.deleteDomainButton, stretch=1)
        self.form.layout.addWidget(self.form.deleteDomainButton2, stretch=1)
        self.form.deleteDomainButton.setVisible(False)
        self.form.deleteDomainButton2.setVisible(False)
        self.form.layout2.addWidget(self.form.selectMaterial_2, stretch=1)
        self.form.layout2.addWidget(self.form.horizontal2, stretch=1)
        self.form.layout2.addWidget(self.form.selectMaterial_3, stretch=1)
        self.form.selectMaterial_2.setVisible(False)
        self.form.selectMaterial_3.setVisible(False)
        self.form.horizontal2.setVisible(False)
        self.form.layout3.addWidget(self.form.thicknessObject2, stretch=1)
        self.form.layout3.addWidget(self.form.horizontal3, stretch=1)
        self.form.layout3.addWidget(self.form.thicknessObject3, stretch=1)
        self.form.thicknessObject2.setVisible(False)
        self.form.thicknessObject3.setVisible(False)
        self.form.horizontal3.setVisible(False)
        self.form.layout4.addWidget(self.form.asDesign_checkbox2, stretch=1)
        self.form.layout4.addWidget(self.form.horizontal4, stretch=1)
        self.form.layout4.addWidget(self.form.asDesign_checkbox3, stretch=1)
        self.form.asDesign_checkbox2.setVisible(False)
        self.form.asDesign_checkbox3.setVisible(False)
        self.form.horizontal4.setVisible(False)
        self.form.layout5.addWidget(self.form.stressLimit_2, stretch=1)
        self.form.layout5.addWidget(self.form.horizontal5, stretch=1)
        self.form.layout5.addWidget(self.form.stressLimit_3, stretch=1)
        self.form.stressLimit_2.setVisible(False)
        self.form.stressLimit_3.setVisible(False)
        self.form.horizontal5.setVisible(False)
        self.form.layout6.addWidget(self.form.label3, stretch=1)
        self.form.layout6.addWidget(self.form.horizontal6, stretch=1)
        self.form.layout6.addWidget(self.form.label4, stretch=1)
        self.form.label3.setVisible(False)
        self.form.label4.setVisible(False)
        self.form.horizontal6.setVisible(False)
        self.form.layout7.addWidget(self.form.selectFilter_2, stretch=1)
        self.form.layout7.addWidget(self.form.horizontal7, stretch=1)
        self.form.layout7.addWidget(self.form.selectFilter_3, stretch=1)
        self.form.selectFilter_2.setVisible(False)
        self.form.selectFilter_3.setVisible(False)
        self.form.horizontal7.setVisible(False)
        self.form.layout8.addWidget(self.form.filterRange_2, stretch=1)
        self.form.layout8.addWidget(self.form.horizontal8, stretch=1)
        self.form.layout8.addWidget(self.form.range_2, stretch=1)
        self.form.filterRange_2.setVisible(False)
        self.form.range_2.setVisible(False)
        self.form.horizontal8.setVisible(False)
        self.form.layout8.addWidget(self.form.horizontal9, stretch=1)
        self.form.layout8.addWidget(self.form.filterRange_3, stretch=1)
        self.form.layout8.addWidget(self.form.range_3, stretch=1)
        self.form.filterRange_3.setVisible(False)
        self.form.range_3.setVisible(False)
        self.form.horizontal9.setVisible(False)
        self.form.layout9.addWidget(self.form.directionVector_2, stretch=1)
        self.form.layout9.addWidget(self.form.horizontal10, stretch=1)
        self.form.layout9.addWidget(self.form.directionVector_3, stretch=1)
        self.form.directionVector_2.setVisible(False)
        self.form.directionVector_3.setVisible(False)
        self.form.horizontal10.setVisible(False)
        self.form.layout10.addWidget(self.form.horizontal12, stretch=1)
        self.form.layout10.addLayout(self.form.verticalLayout2, stretch=1)
        self.form.layout10.addWidget(self.form.horizontal11, stretch=1)
        self.form.layout10.addLayout(self.form.verticalLayout3, stretch=1)
        self.form.verticalLayout2.addWidget(self.form.domainList_2, stretch=1)
        self.form.verticalLayout3.addWidget(self.form.domainList_3, stretch=1)
        self.form.verticalLayout2.setEnabled(False)
        self.form.verticalLayout3.setEnabled(False)
        self.form.domainList_2.setVisible(False)
        self.form.domainList_3.setVisible(False)
        self.form.horizontal11.setVisible(False)
        self.form.selectFilter_2.currentIndexChanged.connect(self.filterType2)
        self.form.selectFilter_3.currentIndexChanged.connect(self.filterType3)
        self.form.filterRange_2.currentIndexChanged.connect(self.filterRange2)
        self.form.filterRange_3.currentIndexChanged.connect(self.filterRange2)

        self.form.selectMaterial_2.clear()
        self.form.selectMaterial_3.clear()
        self.form.selectMaterial_2.addItem("None")
        self.form.selectMaterial_3.addItem("None")
        self.form.thicknessObject2.clear()
        self.form.thicknessObject3.clear()
        self.form.thicknessObject2.addItem("None")
        self.form.thicknessObject3.addItem("None")
        self.form.domainList_2.clear()
        self.form.domainList_2.addItem("All defined")
        self.form.domainList_2.addItem("Domain 0")
        self.form.domainList_2.addItem("Domain 1")
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

        self.form.newAddButton.clicked.connect(self.addNewDomain2)
        self.form.deleteDomainButton.clicked.connect(self.deleteDomain)
        self.form.deleteDomainButton2.clicked.connect(self.deleteDomain2)
        self.form.addButton.clicked.connect(self.addNewDomain)  # adding new domains widgets to ui

        self.form.selectGen.currentIndexChanged.connect(self.selectFile)  # Select generated analysis file

        # self.form.updateButton.clicked.connect(self.Update) # Update domains button
        self.form.selectMaterial_1.currentIndexChanged.connect(
            self.selectMaterial1)  # select domain by material object comboBox 1
        self.form.selectMaterial_2.currentIndexChanged.connect(
            self.selectMaterial2)  # select domain by material object comboBox 2
        self.form.selectMaterial_3.currentIndexChanged.connect(
            self.selectMaterial3)  # select domain by material object comboBox 3

        self.form.selectFilter_1.currentIndexChanged.connect(
            self.filterType1)  # select filter type comboBox 1 (simple,casting)
        self.form.selectFilter_2.currentIndexChanged.connect(
            self.filterType2)  # select filter type comboBox 2 (simple,casting)
        self.form.selectFilter_3.currentIndexChanged.connect(
            self.filterType3)  # select filter type comboBox 3 (simple,casting)

        self.form.filterRange_1.currentIndexChanged.connect(
            self.filterRange1)  # select filter range comboBox 1 (auto,manual)
        self.form.filterRange_2.currentIndexChanged.connect(
            self.filterRange2)  # select filter range comboBox 2 (auto,manual)
        self.form.filterRange_3.currentIndexChanged.connect(
            self.filterRange3)  # select filter range comboBox 3 (auto,manual)

        self.form.results.clicked.connect(lambda: self.get_case("last"))  # show results

        self.form.runOpt.clicked.connect(self.runOptimization)  # run optimization button
        self.form.openExample.clicked.connect(self.openExample)  # example button, opens examples on beso github
        self.form.confComments.clicked.connect(self.openConfComments)  # opens config comments on beso github
        self.form.openLog.clicked.connect(self.openLog)  # opens log file

        # self.Update()  # first update

    def addNewDomain2(self):
        self.form.deleteDomainButton.setVisible(False)
        self.form.horizontal1.setVisible(True)
        self.form.horizontal2.setVisible(True)
        self.form.horizontal3.setVisible(True)
        self.form.horizontal4.setVisible(True)
        self.form.horizontal5.setVisible(True)
        self.form.horizontal6.setVisible(True)
        self.form.horizontal7.setVisible(True)
        self.form.horizontal8.setVisible(True)
        self.form.horizontal9.setVisible(True)
        self.form.horizontal10.setVisible(True)
        self.form.horizontal11.setVisible(True)

        self.form.label2.setVisible(True)
        self.form.newAddButton.setVisible(False)
        self.form.label3.setVisible(True)
        self.form.deleteDomainButton2.setVisible(True)
        self.form.selectMaterial_3.setVisible(True)
        self.form.selectMaterial_3.setEnabled(True)
        self.form.thicknessObject3.setVisible(True)
        self.form.asDesign_checkbox3.setVisible(True)
        self.form.stressLimit_3.setVisible(True)
        self.form.label4.setVisible(True)
        self.form.selectFilter_3.setVisible(True)
        self.form.selectFilter_3.setEnabled(True)
        self.form.filterRange_3.setVisible(True)
        self.form.range_3.setVisible(True)
        self.form.directionVector_3.setVisible(True)
        self.form.verticalLayout3.setEnabled(True)
        self.form.domainList_3.setVisible(True)
        self.form.domainList_1.addItem("Domain 2")
        self.form.domainList_2.addItem("Domain 2")

    def deleteDomain2(self):

        self.form.horizontal1.setVisible(False)
        self.form.horizontal2.setVisible(False)
        self.form.horizontal3.setVisible(False)
        self.form.horizontal4.setVisible(False)
        self.form.horizontal5.setVisible(False)
        self.form.horizontal6.setVisible(False)
        self.form.horizontal7.setVisible(False)
        self.form.horizontal8.setVisible(False)
        self.form.horizontal9.setVisible(False)
        self.form.horizontal10.setVisible(False)
        self.form.horizontal11.setVisible(False)

        self.form.label2.setEnabled(False)
        self.form.label2.setVisible(False)

        self.form.deleteDomainButton2.setVisible(False)

        self.form.selectMaterial_3.setEnabled(False)
        self.form.selectMaterial_3.setVisible(False)

        self.form.thicknessObject3.setEnabled(False)
        self.form.thicknessObject3.setVisible(False)

        self.form.asDesign_checkbox3.setEnabled(False)
        self.form.asDesign_checkbox3.setVisible(False)

        self.form.stressLimit_3.setEnabled(False)
        self.form.stressLimit_3.setVisible(False)

        self.form.label4.setEnabled(False)
        self.form.label4.setVisible(False)

        self.form.selectFilter_3.setEnabled(False)
        self.form.selectFilter_3.setVisible(False)

        self.form.filterRange_3.setEnabled(False)
        self.form.filterRange_3.setVisible(False)

        self.form.range_3.setEnabled(False)
        self.form.range_3.setVisible(False)

        self.form.directionVector_3.setEnabled(False)
        self.form.directionVector_3.setVisible(False)

        self.form.verticalLayout3.setEnabled(False)

        self.form.domainList_3.setEnabled(False)
        self.form.domainList_3.setVisible(False)

        self.form.newAddButton.setVisible(True)
        self.form.deleteDomainButton.setVisible(True)

        self.form.selectMaterial_3.setCurrentIndex(0)
        self.form.selectFilter_3.setCurrentIndex(0)
        self.form.domainList_1.takeItem(3)
        self.form.domainList_2.takeItem(3)

    def deleteDomain(self):

        self.form.horizontal12.setVisible(False)

        self.form.label1.setEnabled(False)
        self.form.label1.setVisible(False)

        self.form.newAddButton.setVisible(False)

        self.form.deleteDomainButton.setVisible(False)

        self.form.selectMaterial_2.setEnabled(False)
        self.form.selectMaterial_2.setVisible(False)

        self.form.thicknessObject2.setEnabled(False)
        self.form.thicknessObject2.setVisible(False)

        self.form.asDesign_checkbox2.setEnabled(False)
        self.form.asDesign_checkbox2.setVisible(False)

        self.form.stressLimit_2.setEnabled(False)
        self.form.stressLimit_2.setVisible(False)

        self.form.label3.setEnabled(False)
        self.form.label3.setVisible(False)

        self.form.selectFilter_2.setEnabled(False)
        self.form.selectFilter_2.setVisible(False)

        self.form.filterRange_2.setEnabled(False)
        self.form.filterRange_2.setVisible(False)

        self.form.range_2.setEnabled(False)
        self.form.range_2.setVisible(False)

        self.form.directionVector_2.setEnabled(False)
        self.form.directionVector_2.setVisible(False)

        self.form.verticalLayout2.setEnabled(False)

        self.form.domainList_2.setEnabled(False)
        self.form.domainList_2.setVisible(False)

        self.form.addButton.setVisible(True)

        self.form.selectMaterial_2.setCurrentIndex(0)
        self.form.selectFilter_2.setCurrentIndex(0)
        self.form.domainList_1.takeItem(2)

    def addNewDomain(self):
        self.form.addButton.setVisible(False)
        self.form.horizontal12.setVisible(True)
        self.form.label1.setVisible(True)
        self.form.newAddButton.setVisible(True)
        self.form.deleteDomainButton.setVisible(True)
        self.form.selectMaterial_2.setVisible(True)
        self.form.selectMaterial_2.setEnabled(True)
        self.form.thicknessObject2.setVisible(True)
        self.form.asDesign_checkbox2.setVisible(True)
        self.form.stressLimit_2.setVisible(True)
        self.form.label3.setVisible(True)
        self.form.selectFilter_2.setVisible(True)
        self.form.selectFilter_2.setEnabled(True)
        self.form.filterRange_2.setVisible(True)
        self.form.range_2.setVisible(True)
        self.form.directionVector_2.setVisible(True)
        self.form.horizontal12.setVisible(True)
        self.form.verticalLayout2.setEnabled(True)
        self.form.domainList_2.setVisible(True)
        self.form.domainList_1.addItem("Domain 1")

    def selectFile(self):
        try:
            self.path = self.workingDir + f"/Gen{self.form.selectGen.currentIndex()+1}/loadCase1/"
            file_names = os.listdir(self.path)
            inp_file = [file for file in file_names if file.endswith("inp")][0]
        except:
            self.path = self.workingDir + f"/TopologyCase_{self.form.selectGen.currentIndex()+1}"
            file_names = os.listdir(self.path)
            inp_file = [file for file in file_names if file.endswith("inp")][0]

        self.form.fileName.setText(self.path+inp_file)
        self.inp_file = self.path+inp_file

    def getGenerations(self, numGens):
        comboBoxItems = []
        if numGens > 0:
            self.form.selectGen.setEnabled(True)

            self.path = self.workingDir + f"/Gen{self.form.selectGen.currentIndex()+1}/loadCase1/"
            file_names = os.listdir(self.path)
            inp_file = [file for file in file_names if file.endswith("inp")][0]

            for i in range(1, numGens+1):
                comboBoxItems.append("Generation " + str(i))
            self.form.selectGen.clear()
            self.form.selectGen.addItems(comboBoxItems)
            self.form.fileName.setText(self.path+inp_file)
        else:
            import FemGui
            import glob
            self.form.selectGen.setEnabled(True)
            lc=0
            for obj in self.doc.Objects:
               # try:
                    if obj.TypeId == "Fem::FemAnalysis":  # to choose analysis objects
                        lc += 1
                        FemGui.setActiveAnalysis(obj)
                        analysisfolder = os.path.join(
                            self.workingDir + f"/TopologyCase_{lc}")
                        try:
                            os.mkdir(analysisfolder)
                        except:
                            pass
                        fea = ccxtools.FemToolsCcx(analysis=obj)
                        fea.setup_working_dir(analysisfolder)
                        fea.update_objects()
                        fea.setup_ccx()
                        message = fea.check_prerequisites()
                        if not message:
                            fea.purge_results()
                            fea.write_inp_file()
                            comboBoxItems.append("Analysis " + str(lc))
            self.form.selectGen.clear()
            self.form.selectGen.addItems(comboBoxItems)
            name = glob.glob(analysisfolder+"/*.inp")
            self.form.fileName.setText(name[0])

          
               #except:
                    # It counts for deleted objects and gives error.
               #     pass

    

    def setConfig(self):
        self.doc.Topology.file_name = os.path.split(self.form.fileName.text())[1]
        self.doc.Topology.path = os.path.split(self.form.fileName.text())[0]
    
        global elset2
        global elset
        global elset1
        elset2 = ""
        elset = ""
        elset1 = ""
        fea = ccxtools.FemToolsCcx()
        fea.setup_ccx()
        self.doc.Topology.path_calculix = fea.ccx_binary

        self.doc.Topology.optimization_base = self.form.optBase.currentText()  # stiffness,heat

        elset_id = self.form.selectMaterial_1.currentIndex() - 1
        thickness_id = self.form.thicknessObject1.currentIndex() - 1
        if elset_id != -1:
            if thickness_id != -1:
                elset_name = self.materials[elset_id].Name + self.thicknesses[thickness_id].Name
            else:  # 0 means None thickness selected
                elset_name = self.materials[elset_id].Name + "Solid"
            modulus = float(self.materials[elset_id].Material["YoungsModulus"].split()[0])  # MPa
            if self.materials[elset_id].Material["YoungsModulus"].split()[1] != "MPa":
                raise Exception(" units not recognised in " + self.materials[elset_id].Name)
            poisson = float(self.materials[elset_id].Material["PoissonRatio"].split()[0])
            try:
                density = float(self.materials[elset_id].Material["Density"].split()[0]) * 1e-12  # kg/m3 -> t/mm3
                self.doc.Topology.domain_density[elset_name] = [density*1e-6,density]
                if self.materials[elset_id].Material["Density"].split()[1] not in ["kg/m^3", "kg/m3"]:
                    raise Exception(" units not recognised in " + self.materials[elset_id].Name)
            except KeyError:
                self.doc.Topology.domain_density[elset_name] = [0,0]
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
                                      0]) * 1e6  # J/kg/K -> mm^2/s^2/K
                if self.materials[elset_id].Material["SpecificHeat"].split()[1] != "J/kg/K":
                    raise Exception(" units not recognised in " + self.materials[elset_id].Name)
            except KeyError:
                specific_heat = 0.
            if thickness_id != -1:
                thickness = float(str(self.thicknesses[thickness_id].Thickness).split()[0])  # mm
                if str(self.thicknesses[thickness_id].Thickness).split()[1] != "mm":
                    raise Exception(" units not recognised in " + self.thicknesses[thickness_id].Name)
            else:
                thickness = 0
            optimized = self.form.asDesign_checkbox.isChecked()
            if self.form.stressLimit_1.text():
                von_mises = float(self.form.stressLimit_1.text())
            else:
                von_mises = 0.
        if self.form.layout2.count() == 5:
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
                        0]) * 1e6  # J/kg/K -> mm^2/s^2/K
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
        if self.form.layout2.count() == 7:
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
                        0]) * 1e6  # J/kg/K -> mm^2/s^2/K
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
                    elset2 = self.materials[elset_id2].Name + "Solid"
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
                        0]) * 1e6  # J/kg/K -> mm^2/s^2/K
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
        self.doc.Topology.domain_material[elset_name] = [modulus, poisson, density, conductivity, expansion, specific_heat]
        self.doc.Topology.mass_goal_ratio = float(self.form.massGoalRatio.text())
        self.doc.Topology.domain_optimized[elset_name]=optimized
        if thickness:
            self.doc.Topology.domain_thickness[elset_name]=[thickness, thickness]
        if von_mises:
            self.doc.Topology.domain_FI[elset_name]=[['stress_von_Mises', von_mises * 1e6],
                                    ['stress_von_Mises', von_mises]]
        App.Console.PrintMessage("Config file created\n")

    def massratio(self, slider_position):
        if slider_position == 0:
            self.doc.Topology.mass_addition_ratio = 0.01
            self.doc.Topology.mass_removal_ratio = 0.02
        if slider_position == 1:
            self.doc.Topology.mass_addition_ratio = 0.015
            self.doc.Topology.mass_removal_ratio = 0.03
        if slider_position == 2:
            self.doc.Topology.mass_addition_ratio = 0.03
            self.doc.Topology.mass_removal_ratio = 0.06

 

    def runOptimization(self):
        # Run optimization
        self.setConfig()
        beso_main.main()
        Gui.runCommand('Std_ActivatePrevWindow')
        self.get_case("last")

    def get_case(self, numberofcase):
        lastcase = self.doc.Topology.LastState
        print(numberofcase)
        if not numberofcase:
            App.Console.PrintError("The simulations are not completed\n")
            return
        elif numberofcase == "last":
            numberofcase = lastcase
        mw = Gui.getMainWindow()
        evaluation_bar = QtGui.QToolBar()
        try:
            mw.removeToolBar(mw.findChild(QtGui.QToolBar,"Evaluation"))
        except:
            pass
        slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        slider.setGeometry(10, mw.height()-50, mw.width()-50, 50)
        slider.setMinimum(1)
        slider.setMaximum(lastcase)
        slider.setValue(numberofcase)
        slider.setTickPosition(QtGui.QSlider.TicksBelow)
        slider.setTickInterval(1)
        slider.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        slider.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        slider.sliderMoved.connect(Common.get_results_fc)
        closebutton = QtGui.QPushButton("")
        pix = QtGui.QStyle.SP_TitleBarCloseButton
        icon = closebutton.style().standardIcon(pix)
        closebutton.setIcon(icon)
        closebutton.clicked.connect(evaluation_bar.close)
        evaluation_bar.addWidget(slider)
        evaluation_bar.addWidget(closebutton)
        evaluation_bar.setObjectName("Evaluation")
        mw.addToolBar(QtCore.Qt.ToolBarArea.BottomToolBarArea, evaluation_bar)
        Common.get_results_fc(numberofcase)

    def openExample(self):
        webbrowser.open_new_tab("https://github.com/fandaL/beso/wiki/Example-4:-GUI-in-FreeCAD")

    def openConfComments(self):
        webbrowser.open_new_tab("https://github.com/fandaL/beso/blob/master/beso_conf.py")

    def openLog(self):
        """Open log file"""
        if self.form.fileName.text() in ["None analysis file selected", ""]:
            App.Console.PrintMessage("None analysis file selected")
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
            self.form.range_1.setEnabled(False)  # range as mm
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
        doc = Gui.getDocument(self.obj.Document)
        doc.resetEdit()
        doc.Document.recompute()

    def reject(self):
        doc = Gui.getDocument(self.obj.Document)
        doc.resetEdit()


class ViewProviderGen:
    def __init__(self, vobj):
        vobj.Proxy = self

    def getIcon(self):
        icon_path = os.path.join(App.getUserAppDataDir() + 'Mod/FEMbyGEN/fembygen/icons/Topology.svg')
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
        taskd = TopologyPanel(vobj)
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
