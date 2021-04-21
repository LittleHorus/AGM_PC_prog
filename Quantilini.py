#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QWhatsThis
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtGui import QRegExpValidator
import pyqtgraph as pg 
import pyqtgraph.opengl as gl
import numpy as np
import serial
import os
from time import gmtime, strftime
import time
import traceback
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point
import socket
import sys
#from requests import get
import qdarkstyle 
import array
import qutip
from scipy.optimize import fsolve
import scipy
from scipy import signal 
from scipy import *
import math

__version__ = '1.0.0'

class CommonWindow(QtWidgets.QWidget):
	"""Класс основного окна программы"""
	#QMainWindow
	#QtWidgets.QWidget
	def __init__(self, parent = None):
		QtWidgets.QMainWindow.__init__(self, parent)

		self.serialDeviceConnected = False
		self.file_description = ""
		self.file_data_ch1 = np.empty(0)
		self.file_data_ch2 = np.empty(0)
		self.file_data_pressure = np.empty(0)
		self.file_x_ax = np.empty(0)
		self.data = [0]#test data value for plot
		self.data_download_done = 0
		self.data_load_from_file_done = 0
		self.milk_data_from_file = np.empty((2,256))
		self.trace1 = np.empty(256)
		self.trace2 = np.empty(256)
		self.trace1 = np.random.random(256)
		self.trace2 = np.random.random(256)
		self.trace3 = np.random.random(256)
		self.x_ax = np.linspace(0, 1, 256)

		self.fetch_enable = False
		self.first_load = 0
		self.count = 0
		self.last_clicked_plot = 0
		#pg.setConfigOption('background', 'd')
		pg.setConfigOption('foreground', 'g')	
		#self.label_graph = pg.LabelItem(text = "x and y", color = "CCFF00")#justify='right'
		self.graph = pg.PlotWidget()
		self.graph.sizeHint = lambda: pg.QtCore.QSize(200, 50)

		self.view = gl.GLViewWidget()
		self.view.show()
		self.view.sizeHint = lambda: pg.QtCore.QSize(200, 200)
		self.view.setSizePolicy(self.graph.sizePolicy())
		#self.xgrid = gl.GLGridItem()
		#self.ygrid = gl.GLGridItem()
		#self.zgrid = gl.GLGridItem()

		#self.view.addItem(self.xgrid)
		#self.view.addItem(self.ygrid)
		#self.view.addItem(self.zgrid)

		#self.xgrid.rotate(90,0,1,0)
		#self.ygrid.rotate(90,1,0,0)

		#self.xgrid.scale(0.2, 0.1, 0.1)
		#self.ygrid.scale(0.2, 0.1, 0.1)
		#self.zgrid.scale(0.1, 0.2, 0.1)

		self.lastClicked = []

		self.graph.showGrid(1,1,1)

		self.plot_xaxis = list()
		self.index = 0
		self.graph.setLabel('bottom', "Time, sec")
		#self.graph.setLabel('top', self.label_graph)
		#self.graph.showLabel(show = True)
		self.graph.setMinimumSize(500,200)
		self.vb = self.graph.plotItem.vb

		#self.vLine = pg.InfiniteLine(angle=90, movable=False, pen = pg.mkPen('y', width = 1))
		#self.hLine = pg.InfiniteLine(angle=0, movable=False, pen = pg.mkPen('y', width = 1))
		#self.graph.addItem(self.vLine, ignoreBounds=True)
		#self.graph.addItem(self.hLine, ignoreBounds=True)
		#self.graph.setRange(yRange = (0,4095))

		self.curve = self.graph.plot(self.x_ax,self.trace1, pen = pg.mkPen('g', width = 3), symbol = 'o', symbolSize = 10)
		self.curve = self.graph.plot(self.x_ax,self.trace2, pen = pg.mkPen('y', width = 3), symbol = 'o', symbolSize = 10)

		zero_point = (0,0,0)
		x_axes = (1,0,0)
		y_axes = (0,1,0)
		z_axes = (0,0,1)

		pts = np.array([(0,0,0), (0.5,0.5,1), (0.1, 0.9,-1), (0.9,0.1,-1)])

		cp_yz = []
		cp_xz = []
		cp_xy = []

		cp_xy_z45 = []
		cp_xz_y45 = []

		for i in range(101):
			cp_xy.append((math.cos(-np.pi+2*np.pi*i/101), math.sin(-np.pi+2*np.pi*i/101), 0))
			cp_yz.append((0, math.cos(-np.pi+2*np.pi*i/101), math.sin(-np.pi+2*np.pi*i/101)))
			cp_xz.append((math.cos(-np.pi+2*np.pi*i/101), 0, math.sin(-np.pi+2*np.pi*i/101)))
			cp_xy_z45.append(((math.cos(-np.pi+2*np.pi*i/101), math.sin(-np.pi+2*np.pi*i/101)/(math.sqrt(2)), math.sin(-np.pi+2*np.pi*i/101)/(math.sqrt(2)))))
			cp_xz_y45.append(((math.sin(-np.pi+2*np.pi*i/101)/(math.sqrt(2)), math.cos(-np.pi+2*np.pi*i/101), math.sin(-np.pi+2*np.pi*i/101)/(math.sqrt(2)))))

		cp_xy.append((math.cos(-np.pi+2*np.pi), math.sin(-np.pi+2*np.pi), 0))
		cp_yz.append((0, math.cos(-np.pi+2*np.pi), math.sin(-np.pi+2*np.pi)))
		cp_xz.append((math.cos(-np.pi+2*np.pi), 0, math.sin(-np.pi+2*np.pi)))
		cp_xy_z45.append(((math.cos(-np.pi+2*np.pi), math.sin(-np.pi+2*np.pi)/(math.sqrt(2)), math.sin(-np.pi+2*np.pi)/(math.sqrt(2)))))
		cp_xz_y45.append(((math.sin(-np.pi+2*np.pi)/(math.sqrt(2)), math.cos(-np.pi+2*np.pi), math.sin(-np.pi+2*np.pi)/(math.sqrt(2)))))
		cp_array = np.asarray(cp_xy)
		cp_array_yz = np.asarray(cp_yz)
		cp_array_xz = np.asarray(cp_xz)
		cp_array_xy_z45 = np.asarray(cp_xy_z45)
		cp_array_xz_y45 = np.asarray(cp_xz_y45)

		ptsX = np.array([(-1,0,0), x_axes])
		ptsY = np.array([(0,-1,0), y_axes])
		ptsZ = np.array([(0,0,-1), z_axes])

		#sh1 = gl.GLLinePlotItem(pos=pts, width = 2, antialias = False, mode = 'lines', color = (0.3, 0.8, 0.2, 1.0))#line_strip
		gaxis = gl.GLAxisItem(size = QtGui.QVector3D(1.1,1.1,1.1), antialias = False, glOptions = 'translucent')

		sh2 = gl.GLLinePlotItem(pos=cp_array, width = 2, antialias = False, mode = 'line_strip', color = (0.3, 0.8, 0.2, 1.0))
		sh3 = gl.GLLinePlotItem(pos=cp_array_yz, width = 2, antialias = False, mode = 'line_strip', color = (0.3, 0.8, 0.2, 1.0))
		sh4 = gl.GLLinePlotItem(pos=cp_array_xz, width = 2, antialias = False, mode = 'line_strip', color = (0.3, 0.8, 0.2, 1.0))
		sh5 = gl.GLLinePlotItem(pos=cp_array_xy_z45, width = 2, antialias = False, mode = 'line_strip', color = (0.8, 0.2, 0.2, 1.0))
		sh6 = gl.GLLinePlotItem(pos=cp_array_xz_y45, width = 2, antialias = False, mode = 'line_strip', color = (0.8, 0.2, 0.2, 1.0))
		#axX = gl.GLLinePlotItem(pos=ptsX, width = 1, antialias = False, mode = 'line_strip', color = (1.0, 1.0, 0.0, 1.0))
		#axY = gl.GLLinePlotItem(pos=ptsY, width = 1, antialias = False, mode = 'line_strip', color = (1.0, 1.0, 0.0, 1.0))
		#axZ = gl.GLLinePlotItem(pos=ptsZ, width = 1, antialias = False, mode = 'line_strip', color = (1.0, 1.0, 0.0, 1.0))
		self.view.addItem(gaxis)
		#self.view.addItem(sh1)
		self.view.addItem(sh2)
		self.view.addItem(sh3)
		self.view.addItem(sh4)
		self.view.addItem(sh5)
		self.view.addItem(sh6)
		
		#self.view.addItem(axX)
		#self.view.addItem(axY)
		#self.view.addItem(axZ)

		self.md = gl.MeshData.sphere(rows=20, cols=40, radius=[1])
		self.m1 = gl.GLMeshItem(meshdata=self.md,smooth=True,color=(0.8, 0.8, 0.8, 0.1),shader="balloon",glOptions="additive")
		self.view.addItem(self.m1)		

		self.view.setCameraPosition(distance=8, azimuth=-90)
		self.view.setWindowTitle('3D plot label')

		vertical_size = 30
		horizontal_size = 80
		
		self.onlyInt = QtGui.QIntValidator(1,5000)
		
		self.btn_load_file = QtWidgets.QPushButton("&Load File")
		self.btn_load_file.setMaximumSize(80,60)
		self.btn_load_file.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)	

		self.data_fetch_timeout = QtWidgets.QLineEdit("001")
		self.data_fetch_timeout.setMaximumSize(horizontal_size,vertical_size)
		self.data_fetch_timeout.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		self.data_fetch_timeout.setValidator(self.onlyInt)
		self.data_fetch_timeout.setAlignment(QtCore.Qt.AlignCenter)

		self.log_widget = QtWidgets.QPlainTextEdit()
		self.log_widget.insertPlainText("Log: ")
		self.log_widget.setReadOnly(True)	

		self.description_widget = QtWidgets.QPlainTextEdit()
		self.description_widget.insertPlainText("File description: ")
		self.description_widget.setReadOnly(False)				

		self.btn_fetch = QtWidgets.QPushButton("&Fetch")
		self.btn_fetch.setMaximumSize(horizontal_size,vertical_size)
		self.btn_fetch.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)

		self.btn_save = QtWidgets.QPushButton("&Save")
		self.btn_save.setMaximumSize(horizontal_size,vertical_size)
		self.btn_save.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)	

		self.table = QtWidgets.QTableWidget(self)
		self.table.setColumnCount(5)
		self.table.setRowCount(10)
		self.table.setHorizontalHeaderLabels(["Header 1", "Header 2", "Header3", "Header 4", ""])
		self.table.horizontalHeaderItem(0).setToolTip("Column 1")
		self.table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignCenter)
		self.table.horizontalHeaderItem(1).setTextAlignment(Qt.AlignCenter)
		self.table.horizontalHeaderItem(2).setTextAlignment(Qt.AlignCenter)
		self.table.horizontalHeaderItem(3).setTextAlignment(Qt.AlignCenter)
		self.table.horizontalHeaderItem(4).setTextAlignment(Qt.AlignCenter)
		#self.table.resizeColumnsToContents()

		self.table.setColumnWidth(0, 200)
		self.table.setColumnWidth(1, 200)
		self.table.setColumnWidth(2, 200)
		self.table.setColumnWidth(3, 200)
		self.table.setColumnWidth(4, 200)

		self.table.setMinimumWidth(400)
		self.table.setMaximumWidth(2000)
		self.table.setMinimumHeight(200)
		self.table.setMaximumHeight(400)

		self.table_header = self.table.horizontalHeader()
		#self.table_header.setResizeMode(QtWidgets.QHeaderView.ResizeToContents)
		self.table_header.setStretchLastSection(True)
		
		self.grid = QtWidgets.QGridLayout()
		self.grid_2 = QtWidgets.QGridLayout()
		self.grid_plot_labels = QtWidgets.QGridLayout()

		self.grid.addWidget(self.btn_fetch, 0, 0)
		self.grid.addWidget(self.btn_save, 0, 1)
		self.grid.addWidget(self.btn_load_file, 0, 2)
		self.grid.addWidget(self.data_fetch_timeout, 0, 3)

		self.grid.addWidget(self.description_widget, 3, 0, 4, 5)
		self.grid.addWidget(self.log_widget, 8, 0, 7, 5)

		self.grid.addWidget(QtWidgets.QLabel(""), 15, 0)
		self.grid.addWidget(QtWidgets.QLabel(""), 15, 1)
		self.grid.addWidget(QtWidgets.QLabel(""), 15, 2)
		self.grid.addWidget(QtWidgets.QLabel(""), 15, 3)
		
		self.grid_2.addWidget(QtWidgets.QLabel(""), 13, 0)
		self.grid_2.addWidget(QtWidgets.QLabel(""), 13, 1)
		self.grid_2.addWidget(QtWidgets.QLabel(""), 13, 2)
		self.grid_2.addWidget(QtWidgets.QLabel(""), 13, 3)
				
		self.vbox_1 = QtWidgets.QVBoxLayout()
		self.vbox_1.insertLayout(0,self.grid)
		self.vbox_1.insertLayout(1,self.grid_2)
		self.vbox_1.insertStretch(3,0)
		
		self.hbox = QtWidgets.QHBoxLayout()
		self.vbox_graph_table = QtWidgets.QVBoxLayout()

		self.vbox_graph_table.addWidget(self.graph)
		self.vbox_graph_table.addWidget(self.view)
		self.vbox_graph_table.addWidget(self.table)
		self.vbox_graph_table.insertStretch(3,0)
		self.hbox.insertLayout(0,self.vbox_1)
		self.hbox.insertLayout(1,self.vbox_graph_table)
		
		self.hbox_2 = QtWidgets.QHBoxLayout()

		self.hbox_2.insertSpacing(0,335)
		self.hbox_2.insertStretch(2,0)
		
		self.vbox = QtWidgets.QVBoxLayout()
		self.vbox.insertLayout(0,self.hbox)
		self.vbox.insertLayout(1,self.hbox_2)
		self.setLayout(self.vbox)

		self.btn_fetch.setDisabled(True)
		self.btn_save.setDisabled(True)

		self.meas_thread = evThread()

		self.btn_save.clicked.connect(self.on_save_to_file)
		self.btn_load_file.clicked.connect(self.on_load_from_file) 
		self.btn_fetch.clicked.connect(self.on_fetch_data)

		#self.table_widget = tableWidget(self)
		#self.setCentralWidget(self.table_widget)

	def on_fetch_data(self):
		if self.fetch_enable == True:
			self.fetch_enable = False
		else:
			self.fetch_enable = True

	def on_get_current_path(self):
		print(os.path.dirname(os.path.abspath(__file__)))	
	def on_save_to_file(self):
		self.data_to_file(strftime("%Y-%m-%d_%Hh%Mm%Ss", gmtime()))	
	def data_to_file(self, name = "milk_data"):
		self.file_description = self.description_widget.toPlainText()
		self.file_x_ax = self.x_ax
		self.file_data_ch1 = self.trace1
		self.file_data_ch2 = self.trace2
		self.file_data_pressure = self.trace3
		dict_to_save = {'description':self.file_description, 'CH1':self.file_data_ch1,'CH2':self.file_data_ch2, 'Pressure':self.file_data_pressure, 'Time': self.file_x_ax}
		dict_filename = "{}\\milk_{}.npy".format(os.path.dirname(os.path.abspath(__file__)),name)
		filename = "{}\\milk_{}.dat".format(os.path.dirname(os.path.abspath(__file__)),name)
		try:
			np.save(dict_filename, dict_to_save)
			self.log_widget.appendPlainText("[{}] file succesful save".format(strftime("%H:%M:%S")))
		except Exception:
			self.log_widget.appendPlainText("[{}] {}".format(strftime("%H:%M:%S"), traceback.format_exc()))	
	def on_load_from_file(self):
		fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]
		self.log_widget.appendPlainText("[{}] {}".format(strftime("%H:%M:%S"), fname))	
		if fname:
			try:
				filename, file_extension = os.path.splitext(fname)
				if file_extension == ".BIN" or file_extension == ".bin":
					self.log_widget.appendPlainText("[{}] file succesful load".format(strftime("%H:%M:%S")))
					self.graph.clear()
					data_raw = np.fromfile(fname, dtype = np.uint8)
					data_u16 = list()

					for i in range(int(len(data_raw)/2)):
						data_u16.append((data_raw[2*i+1]<<8)+(data_raw[2*i]))
					self.trace1 = np.empty(int(len(data_u16)/2))
					self.trace2 = np.empty(int(len(data_u16)/2))
					for i in range(int(len(data_u16)/2)):
						self.trace1[i] = (data_u16[2*i])
						self.trace2[i] = (data_u16[2*i+1])
					self.x_ax = np.linspace(0,1,int(len(data_u16)/2))
					self.curve1 = self.graph.plot(self.x_ax,self.trace1, pen = pg.mkPen('g', width = 3), symbol = 'o', symbolSize = 10)
					self.curve2 = self.graph.plot(self.x_ax,self.trace2, pen = pg.mkPen('y', width = 3), symbol = 'o', symbolSize = 10)
				else:
					data_dict = np.load(fname, allow_pickle=True)
					self.file_description = ""
					self.file_data_ch1 = np.empty(0)
					self.file_data_ch2 = np.empty(0)
					self.file_data_pressure = np.empty(0)
					data_items = data_dict.item()
					self.graph.clear()
					
					self.file_description = data_items['description']
					self.file_data_ch1 = data_items['CH1']
					self.file_data_ch2 = data_items['CH2']
					self.file_data_pressure = data_items['Pressure']	
					self.file_x_ax = data_items['Time']
					self.data_download_done = 1

					self.description_widget.clear()
					self.description_widget.appendPlainText(self.file_description)

					self.trace1 = self.file_data_ch1
					self.trace2 = self.file_data_ch2
					self.trace3 = self.file_data_pressure
					self.x_ax = self.file_x_ax

					self.curve1 = self.graph.plot(self.x_ax,self.trace1, pen = pg.mkPen('g', width = 3), symbol = 'o', symbolSize = 10)
					self.curve2 = self.graph.plot(self.x_ax,self.trace2, pen = pg.mkPen('y', width = 3), symbol = 'o', symbolSize = 10)

					self.btn_save.setDisabled(False)
					self.log_widget.appendPlainText("[{}] file succesful load".format(strftime("%H:%M:%S")))
			except:
				self.log_widget.appendPlainText("[{}] file load failed".format(strftime("%H:%M:%S")))	
				self.log_widget.appendPlainText("[{}] {}".format(strftime("%H:%M:%S"), traceback.format_exc()))						

	def on_interrupted(self):
		self.meas_thread.running = False
		
	def closeEvent(self, event):#перехватываем событие закрытия приложения
		result = QtWidgets.QMessageBox.question(self, "Подтверждение закрытия окна", "Вы действительно хотите закрыть окно?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No )
		if result == QtWidgets.QMessageBox.Yes:
			self.hide()
			#self.pwindow.close()
			self.meas_thread.running = False
			self.meas_thread.wait(5000)#ms
			event.accept()
		else:
			event.ignore()

class tableWidget(QtWidgets.QWidget):
	def __init__(self, parent):
		super(QtWidgets.QWidget, self).__init__(parent)
		self.layout = QtWidgets.QVBoxLayout(self)

		self.tabs = QtWidgets.QTabWidget()
		self.tab1 = QtWidgets.QWidget()
		self.tab2 = QtWidgets.QWidget()
		self.tab3 = QtWidgets.QWidget()
		self.tabs.resize(300,200)

		self.tabs.addTab(self.tab1, "AW File")
		self.tabs.addTab(self.tab2, "tab2")
		self.tabs.addTab(self.tab3, "tab3")

		self.tab1.layout = QtWidgets.QVBoxLayout(self)
		self.tab2.layout = QtWidgets.QVBoxLayout(self)

		self.tab2_label_info = QtWidgets.QLabel("Info label")

		self.tab2.layout.addWidget(self.tab2_label_info)

		self.layout.addWidget(self.tabs)
		self.setLayout(self.layout)

class evThread(QtCore.QThread):
	status_signal = QtCore.pyqtSignal(str)
	dataplot = QtCore.pyqtSignal(np.ndarray)
	progress = QtCore.pyqtSignal(int)
	def __init__(self, parent = None):
		QtCore.QThread.__init__(self,parent)
		self.running = False
	def run(self):
		self.running = True
		for i in range(25):
			if self.running == True:
				#self.sleep(1)
				self.status_signal.emit("{} / {}".format(i+1,100))
				self.dataplot.emit(np.random.randn(200,))
				self.progress.emit(4*i+4)
		if self.running == False:
			self.status_signal.emit("Interrupted")
class ppData:
	"""this class will be used for post processing of data"""
	def __init__(self, parent = None):
		dataFromFile = (list)


class Transmon_Functions():
	def __init__(self, parent = None):
		self.tlist = np.linspace(0,300,6000)
		self.dt = tlist[1] - tlist[0]
		self.SIZE_CHARGE = 95
		self.SIZE_Ph_Res = 1

	def Nstate(self, Nbas, Npho):
		#creates FOCK state-vector
		#parameter Nbas: defines the maximum number of photons in the basis
		#parameter Npho: defines the number pf photons in the state
		return (fock(Nbas, Npho))
	def Coherent(self, Nbas, Npho):
		#create coherent state-vector with Npho photons in the basis of size Nbas
		#parameter Nbas: defines the maximum number of photons in the basis
		#parameter Npho: defines the number of photons in state
		return (coherent(Nbas, Npho))
	def CoSThe(self, Number):
		#cos(phi) operator in charge basis
		#parameter Number: defines the size of charge basis
		cos - qutip.Qobj(np.diag(0.5*np.ones(2*Number), k=1)+
						np.diag(0.5*np.ones(2*Number), k = -1))
		return cos
	def SiNThe(self, Number):
		#sin(phi) operator in charge basis
		#parameter Number: define the size of charge basis
		sin_phi = qutip.Qobj(np.diag(-0.5j*np.ones(2*Number), k = 1)+
							np.diag(0.5j*np.ones(2*Number), k = -1))
		return sin_phi
	def Charge(self, Number):
		#charge number operator in charge basis
		#parameter Number: defines the size of charge basis
		char_num = qutip.Qobj(np.diag(range(-Number, Number+1)))
		return char_num
	def Htrans(self, ng, Ec, EjEc, Size):
		#return hamiltonian of bare transmon in charge basis
		#parameter ng: defines the offset value of gate charge
		#parameter Ec: defines the Coulomb energy of the transmon
		#parameter EjEc: defines the relation btw Josephson and Coulomb energies Ej/Ec
		#parameter Size: defies the size of the charge basis
		Nchar = Charge(size)
		Ej = EjEc*Ec
		Htrans = 4*Ec*(Nchar-ng)*(Nchar-ng)-Ej*CoSThe(Size)
		return Htrans
	def logical_basis(self, H):
		#return firsts 5 eigenstates of Hamiltonian H and coresonding eigeneregies
		#parameters H: hamiltoian defines as Qobj
		Eigsystem = H.eigenstates()
		psi0 = Eigsystem[1][0]
		psi1 = Eigsystem[1][1]
		psi2 = Eigsystem[1][2]
		psi3 = Eigsystem[1][3]
		psi4 = Eigsystem[1][4]

		E0 = Eigsystem[0][0]
		E1 = Eigsystem[0][1]
		E2 = Eigsystem[0][2]
		E3 = Eigsystem[0][3]
		E4 = Eigsystem[0][4]

		return ([psi0, psi1, psi2, psi3, psi4], [E0, E1, E2, E3, E4])

	def change_basis(self, operator, change_basis_matrix):
		# write a given operator in another basis
		#param operator: The operator to write in another basis
		#param change_basis_matrix: The matrix to pass from the old basis
		return change_basis_matrix.dag()*operator*change_basis_matrix
	def sqr_pulse2(self, pulse_dur, pulse_amp, freq_prob, t_off):
		#return square RF pulse forms in QI modes
		#parameter pulse_dur: defines the duration of pulse
		#parameter pulse_amp: defines the amplitude of pulse
		#parameter freq_probe: defines the carrier frequency of pulse
		#parameter t_off: defines the start moment of pulse
		pulse_shape_rect_m = 0.5*np.exp(-1j*freq_probe*self.tlist)*pulse_amp*square(self.tlist, t_off, pulse_dur)
		pulse_shape_rect_p = 0.5*np.exp(+1j*freq_probe*self.tlist)*pulse_amp*square(self.tlist, t_off, pulse_dur)
		return (pulse_shape_rect_p, pulse_shape_rect_m)
	def square(self, t, t0, dur):
		#return square pulse form
		#parameter t: defines the time range at which the pulse is calculated
		#parameter t0: defines the start time
		#parameter durL defines duration
		ans = np.heaviside(t-t0, 1)-np.heaviside(t-t0-dur, 1)
		return ans
	def smoothed_sqr(self, t,t0,dur, smoothnes):
		#returns square pulse with smoothed edges
		#parameter t: defines the time range at which the pulse is calculated
		#parameter t0: defines the start time
		#parameter dur: defines duration
		#parameter smoothnes: defines through the Gauss function as it`s half with spread sigma=smoothess
		Edges = np.exp(-(t-t0)**2/(2*2*smoothnes**2))
		Edges2 = np.exp(-(t-dur-t0)**2 / (2*2*smoothnes**2))
		buckets = [0]*(len(t)-t0)
		Edge = Edges*(1-np.heaviside(t-t0,1))
		Edge2 = Edges2[(t0+dur):]
		buckets2 = [0]*(len(t)-len(Edge2))
		Edge2 = np.concatenate((buckets2, Edge2))*(np.heaviside(t-t0-dur, 1))
		Flat = np.heaviside(t-t0,1)-np.heaviside(t-t0-dur,1)
		Envelop = (Edge+Flat+Edge2)*square(t,t0-6*smoothnes, t0+dur+6*smoothnes)
		return Envelop
	def Gauss(self, tp_G, Om_G, freq_drive, t_ffset_G):
		#return Gaussian pulse
		pulse_shape_G_m = np.exp(-1j*freq_drive*tlist)*Om_G*np.exp(-(tlist-t_offset_G)**2 / 
			(2*tp_G**2))*square(tlist, t_offset_G-tp_G*2, tp_G*4)
		pulse_shape_G_p = np.exp(1j*freq_drive*tlist)*Om_G*np.exp(-(tlist-t_offset_G)**2 / 
			(2*tp_G**2))*square(tlist, t_offset_G-tp_G*2, tp_G*4)		
		return (pulse_shape_G_p, pulse_shape_G_m)
	def smoothed_pulse(self, t, t0, dur, smoothnes, Om_G, freq_drive):
		pulse_shape_rect_m=0.5*np.exp(-1j*freq_drive*t)*Om_G*smoothed_sqr(t,t0,dur,smoothnes)
		pulse_shape_rect_p=0.5*np.exp(+1j*freq_drive*t)*Om_G*smoothed_sqr(t,t0,dur,smoothnes)
		return (pulse_shape_rect_p, pulse_shape_rect_m)
	def smoothed_pulse2(self, t, t0, dur, smoothnes, Om_G, freq_drive, phase):
		pulse_shape_rect_m = 0.5*np.exp(-1j*freq_drive*t+phase)*Om_G*smoothed_sqr(t, t0, dur, smoothnes)
		pulse_shape_rect_p = 0.5*np.exp(1j*freq_drive*t+phase)*Om_G*smoothed_sqr(t, t0, dur, smoothnes)
		return (pulse_shape_rect_p, pulse_shape_rect_m)
	def Qubit_Cavity_define_without_Temp(self, EC, EJEC, flux, wr, Vres, Temperature):
		# EC-Coulomb energy
		# EJEC = EJ/EC where EJ Josephson energy
		# wr-linear frequency of resonator, 
		# Vres - RMS voltage at the resonator at resonance frequency, defined as sqrt(hf_r/2C_r) in units of eV
		# (i.e. we set V_rms*e)
		EJ = np.sqrt(np.cos(np.pi*flux)*np.cos(np.pi*flux)+(dd**2)*(np.sin(np.pi*flux))*(np.sin(np.pi*flux)))# Josephson energy of qubit
		H_bare = Htrans(ng, EC, EJEC*EJ, self.SIZE_CHARGE)#bare transmon
		Eig_ener, Eig_states = H_bare.eigenstates()#fine the eigenbasis for transmon
		#first four states of transmon in charge basis
		if N_qb_max <= 2:
			gnd = Eig_states[0]
			exc = Eig_states[1]
		else:
			gnd = Eig_states[0]
			exc = Eig_states[1]
			fer = Eig_states[2]
		N = Charge(self.SIZE_CHARGE)# Cooper pair number operator
		cos_phi = CoSThe(self.SIZE_CHARGE)#cos phase operator
		sin_phi = SiNThe(self.SIZE_CHARGE)#sin phase operator
		change_basis_matrix = qutip.Qobj(np.column_stack(x.full() for x in Eig_states))#create transformation matrix
		
		N_eig = change_basis(N, change_basis_matrix)# Cooper pair number operator in the eigenbasis
		cos_phi_eig = change_basis(cos_phi, change_basis_matrix)#cos phase operator in the eigenbasis
		sin_phi_eig = change_basis(sin_phi, change_basis_matrix)#sin phase operator in the eigenbasis

		N_ch_eigv_basis = qutip.Qobj(N_eig[:N_qb_max, :N_qb_max])
		cos_phi_eig = qutip.Qobj(cos_phi_eig[:N_qb_max, :N_qb_max])
		sin_phi_eig = qutip.Qobj(sin_phi_eig[:N_qb_max, :N_qb_max])
		Id_trans = qutip.qeye(N_qb_max)
		Hqub_trunc = 4*EC*(N_ch_eigv_basis-ng)**2 - EC*EJEC*EJ*cos_phi_eig
		New_ener, New_states = Hqub_trunc.eigenstates()

		#transition frequencies after the basuis truncation
		if N_qb_max <= 2:
			ff01 = New_ener[1] - New_ener[0]
			ff02 = 0
			ff03 = 0
			GND = New_states[0]
			EXC = New_states[1]
			gnd_1 = tensor(GND, Nstate(self.SIZE_Ph_Res, 1))
			exc_1 = tensor(EXC, Nsyaye(self.SIZE_Ph_Res, 1))
		else:
			ff01 = New_ener[1] - New_ener[0]
			ff02 = New_ener[2] - New_ener[0]
			ff12 = New_ener[2] - New_ener[1]

			GND = New_states[0]
			EXC = New_states[1]
			FER = New_states[2]

			gnd_1 = tensor(GND, Nstate(self.SIZE_Ph_Res, 1))
			exc_1 = tensor(EXC, Nstate(self.SIZE_Ph_Res, 1))
			fer_1 = tensor(FER, Nstate(self.SIZE_Ph_Res, 1))
		Eigenstates_transmon = [GND, EXC, FER]
		Eigenenergies_transmon = [New_ener[0], New_ener[1], New_ener[2]]

		#resonator operators:
		a = destroy(self.SIZE_Ph_Res)
		ad=a.dag()
		N_a = ad*a
		Id_a = qeye(self.SIZE_Ph_Res)
		X_a = (a+a.dag())/np.sqrt(2)
		P_a = (a-a.dag()) / np.sqrt(2)/1j

		#Time independent part of system, collect the operators in united basis
		N_trans = tensor(N_ch_eigv_basis, Id_a)
		cosphi = tensor(cos_phi_eig, Id_a)
		sinphi = tensor(sin_phi_eig, Id_a)
		A = tensor(Id_trans, a)
		Ad = A.dag()
		N_A = tensor(Id_trans, N_a)

		#estimate of coupling between frst/second excited state and resonator
		if N_qb_max<=2:
			g01_res = 2*betta_res*Vres*exc.dag()*N*gnd
			g12_res=0
		else:
			g01_res = 2*betta_res*Vres*exc.dag()*N*gnd
			g12_res = 2*betta_res*Vres*fer.dag()*N*exc
		#write the whole system hamiltonian in united basis
		Hqub = 4*EC*(N_trans-ng)**2-EC*EJEC*EJ*cosphi
		H_res = wr*N_A
		Hint1 = w*betta_res*Vres*N_trans*(A+Ad)
		H0 = Hqub+H_res+Hint1

		System_ener, System_states = H0.eigenstates()
		#compose the collapse operators list
		cops = list()
		T = Temperature

		nres = (np.exp(-h*wr*1e9/kb/T))/(1-np.exp(-h*wr*1e9/kb/T))

		Output = {}
		Output['Hamiltonian'] = H0
		Output['Temperature, K'] = Temperature

		Output['f01'] = ff01
		Output['f02'] = ff02

		Output['f12'] = ff12
		Output['Energies and states'] = [System_ener, System_states]
		Output['Coupling g01, g12'] = [g01_res, g12_res]
		Output['Transmon states'] = Eigenstates_transmon
		Output['Operators photon'] = A
		Output['Operator charge number'] = N_trans
		Output['Collapse operators'] = cops_list
		Output['Transmon energies'] = Eigenenergies_transmon

		return (Output)

	def Qubit_Cavity_define(self, EC, EJEC, flux, wr, Vres, Temperature):
		#EC - Coulomb energy
		#EJEC = EJ/EC where EC Josephson energy
		#wr - linear frequency of resonator
		#Vres - RMS voltage at the resonator at resonance frequency, define as sqrt(hf_r2C_r) in units of eV
		#(i.e. we set V_rms*e)
		EJ = np.sqrt(np.cos(np.pi*flux)*np.cos(np.pi*flux) + (dd**2)*(np.sin(np.pi*flux))*(np.sin(np.pi*flux))) #Josephson energy of qubit
		H_bare = Htrans(ng, EC, EJEC*EJ, self.SIZE_CHARGE) #bare transmon
		Eig_ener, Eig_states = H_bare.eigenstates()#find the eigenbasis for transmon
		#first four states of transmob in charge basis
		if N_qb_max <= 2:
			gnd = Eig_states[0]
			exc = Eig_states[1]
		else:
			gnd = Eig_states[0]
			exc = Eig_states[1]
			fer = Eig_states[2]
		N = Charge(self,SIZE_CHARGE)
		cos_phi = CoSThe(self.SIZE_CHARGE)
		sin_phi = SiNThe(self.SIZE_CHARGE)
		change_basis_matrix = qutip.Qobj(bp.column_stack(x.full() for x in Eig_states))#create transformation matrix

		N_eig = change_basis(N, change_basis_matrix) # Coopper pair number operator in the eigenbasis 
		cos_phi_eig = change_basis(cos_phi, change_basis_matrix)# cos phase operator in the eigenbasis
		sin_phi_eig = change_basis(sin_phi, change_basis_matrix)# sin phase operator in the eigenbasis
		N_ch_eigv_basis = qutip.Qobj(N_eig[:N_qb_max, :N_qb_max])
		cos_phi_eig = qutip.Qobj(cos_phi_eig[:N_qb_max, :N_qb_max])
		sin_phi_eig = qutip.Qobj(sin_phi_eig[:N_qb_max, :N_qb_max])
		Id_trans = qutip.qeye(N_qb_max)
		Hqub_trunc=4*EC*(N_ch_eigv_basis-ng)**2-EC*EJEC*EJ*cos_phi_eig
		New_ener,New_states=Hqub_trunc.eigenstates()
		if N_qb_max<=2:
			ff01=New_ener[1]-New_ener[0]
			ff02=0
			ff12=0

			GND=New_states[0]
			EXC=New_states[1]

			gnd_1=tensor(GND,Nstate(self.SIZE_Ph_Res,1))
			exc_1=tensor(EXC,Nstate(self.SIZE_Ph_Res,1))
		else:
			ff01=New_ener[1]-New_ener[0]
			ff02=New_ener[2]-New_ener[0]
			ff12=New_ener[2]-New_ener[1]

			GND=New_states[0]
			EXC=New_states[1]
			FER=New_states[2]

			gnd_1=tensor(GND,Nstate(self.SIZE_Ph_Res,1))
			exc_1=tensor(EXC,Nstate(self.SIZE_Ph_Res,1))
			fer_1=tensor(FER,Nstate(self.SIZE_Ph_Res,1))
		Eigenstates_transmon=[GND,EXC,FER]
		Eigenenergies_transmon=[New_ener[0],New_ener[1],New_ener[2]]
		#resonator operators
		a=destroy(self.SIZE_Ph_Res)
		ad=a.dag()
		N_a=ad*a
		Id_a=qeye(self.SIZE_Ph_Res)
		X_a=(a + a.dag()) / np.sqrt(2)
		P_a=(a - a.dag()) / np.sqrt(2)/1j
		#Time independent part of system, collect the operator in an united basis
		N_trans=tensor(N_ch_eigv_basis,Id_a)
		cosphi=tensor(cos_phi_eig,Id_a)
		sinphi=tensor(sin_phi_eig,Id_a)
		A=tensor(Id_trans,a)
		Ad=A.dag()
		N_A=tensor(Id_trans,N_a)
		#estimate of coupling between first/second excited state and resonator
		if N_qb_max<=2:
			g01_res=2*betta_res*Vres*exc.dag()*N*gnd
			g12_res=0
		else:
			g01_res=2*betta_res*Vres*exc.dag()*N*gnd
			g12_res=2*betta_res*Vres*fer.dag()*N*exc
		#write the whole system hamiltonian in united basis
		Hqub=4*EC*(N_trans-ng)**2-EC*EJEC*EJ*cosphi
		H_res=wr*N_A
		Hint1=2*betta_res*Vres*N_trans*(A+Ad)
		H0=Hqub+H_res+Hint1
		System_ener,System_states=H0.eigenstates()
		#compose the collapse operators list
		cops_list=[]
		T=Temperature

		nth10=(np.exp(-h*ff01*1e9/kb/T))/(1-np.exp(-h*ff01*1e9/kb/T))
		nth20=(1-np.exp(-h*ff02*1e9/kb/T))**(-1)*(np.exp(-h*ff02*1e9/kb/T))
		nth12=(1-np.exp(-h*ff12*1e9/kb/T))**(-1)*(np.exp(-h*ff12*1e9/kb/T))
		nres=(np.exp(-h*wr*1e9/kb/T))/(1-np.exp(-h*wr*1e9/kb/T))
		s_10=tensor(GND*EXC.dag(),Id_a)
		s_12=tensor(EXC*FER.dag(),Id_a)

		s_11=tensor(EXC*EXC.dag()-GND*GND.dag(),Id_a)
		s_22=tensor(FER*FER.dag()-EXC*EXC.dag(),Id_a)

		gam_10=coupling
		gam_12=2*coupling

		gam_11=dephas
		gam_22=dephas

		rate01_0=np.sqrt(gam_10*(nth10+1))*s_10
		rate01_1=np.sqrt(gam_10*(nth10))*s_10.dag()
		cops_list.append(rate01_0)
		cops_list.append(rate01_1)

		rate12_0=np.sqrt(2*gam_12*(nth12+1))*s_12
		rate12_1=np.sqrt(2*gam_12*(nth12))*s_12.dag()
		cops_list.append(rate12_0)
		cops_list.append(rate12_1)

		rate11=np.sqrt(gam_11*(2*nth10+1))*s_11
		rate22=np.sqrt(2*gam_22*(2*nth20+1))*s_22

		cops_list.append(rate11)
		cops_list.append(rate22)
		rate_res=np.sqrt(kappa*(nres+1))*A
		rate_res2=np.sqrt(kappa*nres)*A.dag()

		cops_list.append(rate_res) 
		cops_list.append(rate_res2)

		Output={}
		Output['Hamiltonian']=H0
		Output['Temperature,K']=Temperature

		Output['f01']=ff01
		Output['f02']=ff02
		Output['nth_01']=nth10
		Output['nth_02']=nth20
		Output['nth_12']=nth12
		Output['nth_res']=nres

		Output['f12']=ff12
		Output['Energies and states']=[System_ener,System_states]
		Output['Couplings g01,g12']=[g01_res,g12_res]
		Output['Transmon states']=Eigenstates_transmon
		Output['Operators photon']=A
		Output['Operator charge number']=N_trans
		Output['Collapse operators']=cops_list
		Output['Transmon energies']=Eigenenergies_transmon

		return (Output)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)		

if __name__ == '__main__':
	app =QtWidgets.QApplication(sys.argv)
	ex = CommonWindow()
	ex.setFont(QtGui.QFont('Arial', 9))#, QtGui.QFont.Bold
	ex.setWindowTitle("Quantilini ver 1.0.0")
	#app.setStyle('Fusion')
	app.setStyleSheet ( qdarkstyle . load_stylesheet ())
	#ex.setWindowFlags(ex.windowFlags() | QtCore.Qt.FramelessWindowHint)
	#ex.setFixedSize(500,400)
	#ex.resize(300,200)
	ex.adjustSize()
	#ico = QtGui.QIcon("icon.png")
	#ex.setWindowIcon(ico)#icon for window only
	#app.setWindowIcon(ico)#icon for application
	#if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
    #    	QtGui.QApplication.instance().exec_()
	ex.show()
	sys.exit(app.exec_())#run the cycle of processing the events
	