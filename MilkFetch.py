#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog, QWhatsThis
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCompleter
from PyQt5.QtGui import QRegExpValidator
import pyqtgraph as pg 
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
#import bluetooth
import qdarkstyle 
import array

__version__ = '1.0.0'

class CommonWindow(QtWidgets.QWidget):
	"""Класс основного окна программы"""
	#QMainWindow
	#QtWidgets.QWidget
	def __init__(self, parent = None):
		QtWidgets.QMainWindow.__init__(self, parent)

		self.slave_address = 0x05
		self.slave_register = 0x10
		self.slave_register_address_hi = 0x10
		self.slave_register_address_lo = 0x00
		self.slave_register_count_hi = 0x00
		self.slave_register_count_lo = 0x02
		self.slave_byte_count = 0x04
		self.slave_speed_hi = 0x00
		self.slave_speed_lo = 0x0a
		self.slave_dir_hi = 0x00
		self.slave_dir_lo = 0x09 
		self.slave_crc16_lo = 0x00
		self.slave_crc16_hi = 0x00
		self.data_array = [0]*13#length of packet
		self.data_bytearray = bytearray(self.data_array)

		self.serialDeviceConnected = False
		self.file_description = ""
		self.file_data_ch1 = np.empty(0)
		self.file_data_ch2 = np.empty(0)
		self.file_data_pressure = np.empty(0)
		self.file_data_microphone = np.empty(0)
		self.file_x_ax = np.empty(0)
		self.data = [0]#test data value for plot
		self.data_download_done = 0
		self.data_load_from_file_done = 0
		self.milk_data_from_file = np.empty((2,256))
		self.trace1 = np.zeros(256)
		self.trace2 = np.zeros(256)
		#self.trace1 = np.random.random(256)
		#self.trace2 = np.random.random(256)
		self.trace3 = np.zeros(256)
		self.x_ax = np.linspace(0, 1, 256)

		self.filter_data_out = 30
		self.filter_k = 0.95
		self.data_to_storage = list()

		self.fetch_enable = False

		self.first_load = 0
		self.previous_row = 0
		self.current_row = -1
		self.data_from_f4 = 0
		self.y_axio = list()
		self.count = 0
		self.last_clicked_plot = 0
		#pg.setConfigOption('background', 'd')
		pg.setConfigOption('foreground', 'g')	
		#self.label_graph = pg.LabelItem(text = "x and y", color = "CCFF00")#justify='right'
		self.graph = pg.PlotWidget()
		self.graph_pressure = pg.PlotWidget()
		self.lastClicked = []
		#PlotCurveItem   PlotWidget
		self.graph.showGrid(1,1,1)
		self.graph_pressure.showGrid(1,1,1)
		self.plot_xaxis = list()
		self.index = 0
		self.graph.setLabel('bottom', "Time, sec")
		self.graph_pressure.setLabel("bottom", "Time, sec")
		#self.graph.setLabel('top', self.label_graph)
		#self.graph.showLabel(show = True)
		self.graph.setMinimumSize(500,200)
		self.graph_pressure.setMinimumSize(500, 200)
		
		self.vb = self.graph.plotItem.vb

		self.vLine = pg.InfiniteLine(angle=90, movable=False, pen = pg.mkPen('y', width = 1))
		self.hLine = pg.InfiniteLine(angle=0, movable=False, pen = pg.mkPen('y', width = 1))
		self.graph.addItem(self.vLine, ignoreBounds=True)
		self.graph.addItem(self.hLine, ignoreBounds=True)
		#self.graph.setRange(yRange = (0,4095))
		#self.graph_pressure.setRange(yRange = (0,100))

		self.curve = self.graph.plot(self.x_ax,self.trace1, pen = pg.mkPen('g', width = 3), symbol = 'o', symbolSize = 4)
		self.curve = self.graph.plot(self.x_ax,self.trace2, pen = pg.mkPen('y', width = 3), symbol = 'o', symbolSize = 4)
		self.curve_pressure = self.graph_pressure.plot(self.x_ax,self.trace3, pen = pg.mkPen('r', width = 3), symbol = 'o', symbolSize = 4)

		self.INITIAL_MODBUS = 0xFFFF
		self.INITIAL_DF1 = 0x0000
		self.table = (
		0x0000, 0xC0C1, 0xC181, 0x0140, 0xC301, 0x03C0, 0x0280, 0xC241,
		0xC601, 0x06C0, 0x0780, 0xC741, 0x0500, 0xC5C1, 0xC481, 0x0440,
		0xCC01, 0x0CC0, 0x0D80, 0xCD41, 0x0F00, 0xCFC1, 0xCE81, 0x0E40,
		0x0A00, 0xCAC1, 0xCB81, 0x0B40, 0xC901, 0x09C0, 0x0880, 0xC841,
		0xD801, 0x18C0, 0x1980, 0xD941, 0x1B00, 0xDBC1, 0xDA81, 0x1A40,
		0x1E00, 0xDEC1, 0xDF81, 0x1F40, 0xDD01, 0x1DC0, 0x1C80, 0xDC41,
		0x1400, 0xD4C1, 0xD581, 0x1540, 0xD701, 0x17C0, 0x1680, 0xD641,
		0xD201, 0x12C0, 0x1380, 0xD341, 0x1100, 0xD1C1, 0xD081, 0x1040,
		0xF001, 0x30C0, 0x3180, 0xF141, 0x3300, 0xF3C1, 0xF281, 0x3240,
		0x3600, 0xF6C1, 0xF781, 0x3740, 0xF501, 0x35C0, 0x3480, 0xF441,
		0x3C00, 0xFCC1, 0xFD81, 0x3D40, 0xFF01, 0x3FC0, 0x3E80, 0xFE41,
		0xFA01, 0x3AC0, 0x3B80, 0xFB41, 0x3900, 0xF9C1, 0xF881, 0x3840,
		0x2800, 0xE8C1, 0xE981, 0x2940, 0xEB01, 0x2BC0, 0x2A80, 0xEA41,
		0xEE01, 0x2EC0, 0x2F80, 0xEF41, 0x2D00, 0xEDC1, 0xEC81, 0x2C40,
		0xE401, 0x24C0, 0x2580, 0xE541, 0x2700, 0xE7C1, 0xE681, 0x2640,
		0x2200, 0xE2C1, 0xE381, 0x2340, 0xE101, 0x21C0, 0x2080, 0xE041,
		0xA001, 0x60C0, 0x6180, 0xA141, 0x6300, 0xA3C1, 0xA281, 0x6240,
		0x6600, 0xA6C1, 0xA781, 0x6740, 0xA501, 0x65C0, 0x6480, 0xA441,
		0x6C00, 0xACC1, 0xAD81, 0x6D40, 0xAF01, 0x6FC0, 0x6E80, 0xAE41,
		0xAA01, 0x6AC0, 0x6B80, 0xAB41, 0x6900, 0xA9C1, 0xA881, 0x6840,
		0x7800, 0xB8C1, 0xB981, 0x7940, 0xBB01, 0x7BC0, 0x7A80, 0xBA41,
		0xBE01, 0x7EC0, 0x7F80, 0xBF41, 0x7D00, 0xBDC1, 0xBC81, 0x7C40,
		0xB401, 0x74C0, 0x7580, 0xB541, 0x7700, 0xB7C1, 0xB681, 0x7640,
		0x7200, 0xB2C1, 0xB381, 0x7340, 0xB101, 0x71C0, 0x7080, 0xB041,
		0x5000, 0x90C1, 0x9181, 0x5140, 0x9301, 0x53C0, 0x5280, 0x9241,
		0x9601, 0x56C0, 0x5780, 0x9741, 0x5500, 0x95C1, 0x9481, 0x5440,
		0x9C01, 0x5CC0, 0x5D80, 0x9D41, 0x5F00, 0x9FC1, 0x9E81, 0x5E40,
		0x5A00, 0x9AC1, 0x9B81, 0x5B40, 0x9901, 0x59C0, 0x5880, 0x9841,
		0x8801, 0x48C0, 0x4980, 0x8941, 0x4B00, 0x8BC1, 0x8A81, 0x4A40,
		0x4E00, 0x8EC1, 0x8F81, 0x4F40, 0x8D01, 0x4DC0, 0x4C80, 0x8C41,
		0x4400, 0x84C1, 0x8581, 0x4540, 0x8701, 0x47C0, 0x4680, 0x8641,
		0x8201, 0x42C0, 0x4380, 0x8341, 0x4100, 0x81C1, 0x8081, 0x4040 )

		self.ComPort = str
		self.comport_combo = QtWidgets.QComboBox()
		self.comport_combo.addItems([""])
		self.comport_combo.addItems(["Refresh"])
		self.comport_combo.activated[str].connect(self.on_activated_com_list)
		self.comport_combo.activated[str].connect(self.ComPort)

		vertical_size = 30
		horizontal_size = 80
		
		self.onlyInt = QtGui.QIntValidator(1,5000)
		
		self.btn_cord_fixed = QtWidgets.QPushButton("&Capture")
		self.btn_cord_fixed.setMaximumSize(120,60)
		self.btn_cord_fixed.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)

		self.btn_load_file = QtWidgets.QPushButton("&Load File")
		self.btn_load_file.setMaximumSize(80,60)
		self.btn_load_file.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)	

		self.label_visa_connect = QtWidgets.QLabel("COM port:")
		self.label_visa_connect.setMaximumSize(horizontal_size,vertical_size)
		self.label_visa_connect.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		self.btn_visa_connect = QtWidgets.QPushButton("Connect")
		self.btn_visa_connect.setMaximumSize(horizontal_size,vertical_size)
		self.btn_visa_connect.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		self.btn_visa_disconnect = QtWidgets.QPushButton("Disconnect")
		self.btn_visa_disconnect.setMaximumSize(horizontal_size,vertical_size)
		self.btn_visa_disconnect.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)	
		self.btn_visa_disconnect.setDisabled(True)
			
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

		self.timeout_label = QtWidgets.QLabel("Timeout(ms):")
		self.timeout_label.setMaximumSize(horizontal_size,vertical_size)
		self.timeout_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)	

		self.btn_fetch = QtWidgets.QPushButton("&Fetch")
		self.btn_fetch.setMaximumSize(horizontal_size,vertical_size)
		self.btn_fetch.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)

		self.btn_save = QtWidgets.QPushButton("&Save")
		self.btn_save.setMaximumSize(horizontal_size,vertical_size)
		self.btn_save.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)		
		
		self.grid = QtWidgets.QGridLayout()
		self.grid_2 = QtWidgets.QGridLayout()
		self.grid_plot_labels = QtWidgets.QGridLayout()

		self.grid.addWidget(self.label_visa_connect, 0, 0)
		self.grid.addWidget(self.comport_combo, 0, 1)
		self.grid.addWidget(self.btn_visa_connect, 0, 2)
		self.grid.addWidget(self.btn_visa_disconnect, 0, 3)
		
		self.grid.addWidget(self.timeout_label, 1, 3)
		self.grid.addWidget(self.btn_fetch,2,0)
		#self.grid.addWidget(self.btn_stop,2,1)
		self.grid.addWidget(self.btn_save,2,1)
		self.grid.addWidget(self.btn_load_file, 2,2)
		self.grid.addWidget(self.data_fetch_timeout, 2,3)

		self.grid.addWidget(self.description_widget, 3,0,4,5)
		self.grid.addWidget(self.log_widget, 8, 0, 7, 5)

		self.grid_plot_labels.addWidget(self.btn_cord_fixed, 0,0)
		self.grid_plot_labels.addWidget(QtWidgets.QLabel(""),0,3)
		self.grid_plot_labels.addWidget(QtWidgets.QLabel(""),0,5)
		#self.grid_plot_labels.insertStretch(0,4)
			
		self.grid.addWidget(QtWidgets.QLabel(""),15,0)
		self.grid.addWidget(QtWidgets.QLabel(""),15,1)
		self.grid.addWidget(QtWidgets.QLabel(""),15,2)
		self.grid.addWidget(QtWidgets.QLabel(""),15,3)
		
		self.grid_2.addWidget(QtWidgets.QLabel(""),13,0)
		self.grid_2.addWidget(QtWidgets.QLabel(""),13,1)
		self.grid_2.addWidget(QtWidgets.QLabel(""),13,2)
		self.grid_2.addWidget(QtWidgets.QLabel(""),13,3)
				
		self.vbox_1 = QtWidgets.QVBoxLayout()
		self.vbox_1.insertLayout(0,self.grid)
		self.vbox_1.insertLayout(1,self.grid_2)
		#self.vbox_1.insertLayout(2,self.grid_3)#table grid
		#self.vbox_1.addWidget(self.agm_readblock)
		self.vbox_1.insertStretch(3,0)
		#self.vbox_1.insertLayout(1,self.form)
		#self.setLayout(self.grid)
		
		self.hbox = QtWidgets.QHBoxLayout()
		self.vbox_graph_table = QtWidgets.QVBoxLayout()

		#self.vbox_graph_table.insertLayout(0,self.grid_plot_labels)
		self.vbox_graph_table.addWidget(self.graph)
		self.vbox_graph_table.addWidget(self.graph_pressure)
		self.vbox_graph_table.insertStretch(2,0)
		#self.hbox.addWidget(self.m)
		self.hbox.insertLayout(0,self.vbox_1)
		self.hbox.insertLayout(1,self.vbox_graph_table)
	
		self.hbox_2 = QtWidgets.QHBoxLayout()

		self.hbox_2.insertSpacing(0,335)
		self.hbox_2.insertStretch(2,0)
		#self.hbox_upper.addSpacing(200)
		
		self.vbox = QtWidgets.QVBoxLayout()
		#self.vbox.addWidget(self.label)		
		#self.vbox.insertLayout(0,self.hbox1)
		self.vbox.insertLayout(0,self.hbox)
		self.vbox.insertLayout(1,self.hbox_2)
		#self.vbox.insertLayout(2,self.grid_3)
		#self.vbox.addWidget(self.table_of_records,1)
		self.setLayout(self.vbox)

		self.btn_fetch.setDisabled(True)
		self.btn_save.setDisabled(True)

		self.meas_thread = evThread()
		#self.meas_thread.start()

		#self.btn_visa_connect.clicked.connect(self.on_get_current_path)
		#self.btn_visa_connect.clicked.connect(self.meas_thread.on_connected)
		self.btn_visa_connect.clicked.connect(self.on_connected)
		self.btn_visa_disconnect.clicked.connect(self.on_disconnected)
		self.btn_save.clicked.connect(self.on_save_to_file)
		self.btn_load_file.clicked.connect(self.on_load_from_file) 
		self.btn_fetch.clicked.connect(self.on_fetch_data)
		#self.comport_combo.activated.connect(self.meas_thread.on_activated_com_list)

		#self.meas_thread.started.connect(self.on_meas_started)
		#self.meas_thread.finished.connect(self.on_meas_completed)
		#self.meas_thread.status_signal.connect(self.on_status_text_change, QtCore.Qt.QueuedConnection)
		#self.meas_thread.dataplot.connect(self.data_from_f4, QtCore.Qt.QueuedConnection)
		self.meas_thread.dataplot.connect(self.on_data_received, QtCore.Qt.QueuedConnection)
		self.meas_thread.dataplot_array.connect(self.on_data_array_received, QtCore.Qt.QueuedConnection)
		#self.meas_thread.progress.connect(self.on_progress_go,QtCore.Qt.QueuedConnection)
		#self.proxy = pg.SignalProxy(self.graph.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
		#self.curve.sigClicked.connect(self.clicked_point)
		#self.curve.sigPointsClicked.connect(self.clicked_point)

	def filter(self, data_input):
		data_result = list()

		for i in range(len(data_input)):
			self.filter_data_out = self.filter_data_out*self.filter_k + (1-self.filter_k)*data_input[i]
			data_result.append(self.filter_data_out)

		return data_result

	def on_data_array_received(self, data_array):
		self.graph.clear()
		temp_data = self.filter(data_array)
		self.y_axio += temp_data
		self.data_to_storage += temp_data

		#self.y_axio += (data_array)
		#print(self.y_axio)
		if(len(self.y_axio)>2000):
			length = len(self.y_axio)
			fp = length - 2000
			self.y_axio = self.y_axio[fp:length]
		x_axio = np.linspace(0,len(self.y_axio)-1, len(self.y_axio))
		self.curve1 = self.graph.plot(x_axio,self.y_axio, pen = pg.mkPen('g', width = 3), symbol = 'o', symbolSize = 4)
		self.log_widget.appendPlainText("[{}] new data from mcu, total length {}".format(strftime("%H:%M:%S"), len(self.data_to_storage)))	

	def on_data_received(self,data):
		self.graph.clear()
		
		self.y_axio.append(data)
		if(len(self.y_axio)>200):
			length = len(self.y_axio)
			fp = length - 200
			self.y_axio = self.y_axio[fp:length]
		x_axio = np.linspace(0,len(self.y_axio)-1, len(self.y_axio))
		self.curve1 = self.graph.plot(x_axio,self.y_axio, pen = pg.mkPen('g', width = 3), symbol = 'o', symbolSize = 4)
		self.log_widget.appendPlainText("[{}] new data from mcu".format(strftime("%H:%M:%S")))

	def on_connected(self):
		try:
			#self.ser = serial.Serial(self.ComPort, baudrate=921600, bytesize=serial.EIGHTBITS,
			#						 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout = 0.1)
			#self.ser.isOpen()  # try to open port
			self.btn_visa_connect.setDisabled(True)
			self.btn_visa_disconnect.setDisabled(False)
			self.btn_fetch.setDisabled(False)
			self.btn_save.setDisabled(False)
			self.serialDeviceConnected = True
			self.comport_combo.setEnabled(False)
			self.meas_thread.on_connected(self.ComPort)
			self.log_widget.appendPlainText("[{}] Connected to {}".format(strftime("%H:%M:%S"), self.ComPort))
		except IOError:
			#print("Port already open another programm")
			self.log_widget.appendPlainText("[{}] Port {} already open another programm".format(strftime("%H:%M:%S"), self.ComPort))
		except serial.SerialException:
			#print("SerialException")
			self.log_widget.appendPlainText("[{}] SerialException".format(strftime("%H:%M:%S")))
		except Exception:
			#print("Unexpected error, Null ComName")
			self.log_widget.appendPlainText("[{}] unexpected error".format(strftime("%H:%M:%S")))
	def on_disconnected(self):
		self.btn_visa_connect.setDisabled(False)
		self.btn_visa_disconnect.setDisabled(True)	
		self.btn_fetch.setDisabled(True)
		self.btn_save.setDisabled(True)
		self.serialDeviceConnected = False
		self.comport_combo.setEnabled(True)
		self.log_widget.appendPlainText("[{}] Disconnected".format(strftime("%H:%M:%S")))
		try:	
			#self.ser.close()
			self.meas_thread.on_disconnected()
			pass
		except:
			#print("serial port close exception, on_disconnect --traceback")
			self.log_widget.appendPlainText("[{}] error, device session lost".format(strftime("%H:%M:%S")))
		#print("Disconnected")
			
	def on_activated_com_list(self, str):
		if self.comport_combo.currentText() == "" or self.serialDeviceConnected == True:
			self.btn_visa_connect.setDisabled(True)
		elif self.comport_combo.currentText() == "Refresh":
			self.btn_visa_connect.setDisabled(True)
			self.comport_combo.clear()
			self.comport_combo.addItems([""])
			self.comport_combo.addItems(["Refresh"])
			self.comport_combo.addItems(serial_ports())
		else:
			self.ComPort = str
			self.btn_visa_connect.setDisabled(False)

	def on_fetch_data(self):
		if self.fetch_enable == True:
			self.fetch_enable = False
			self.meas_thread.running = False
			self.log_widget.appendPlainText("[{}] fetch stop".format(strftime("%H:%M:%S")))
			self.graph_pressure.clear()
			x_axio = np.linspace(0,len(self.data_to_storage)-1, len(self.data_to_storage))
			self.curve1 = self.graph_pressure.plot(x_axio,self.data_to_storage, pen = pg.mkPen('g', width = 3), symbol = 'o', symbolSize = 6)

		else:
			self.fetch_enable = True
			self.meas_thread.running = True
			self.meas_thread.start()
			self.log_widget.appendPlainText("[{}] fetch start".format(strftime("%H:%M:%S")))
			

	def on_send_to_timer(self):
		#self.slave_speed_lo = 0x00
		#self.slave_speed_hi = 0x00
		t_data_array = [0]*9
		t_data_array[0] = self.slave_address
		t_data_array[1] = self.slave_register
		t_data_array[2] = 0x06
		t_data_array[3] = 0x7F
		t_data_array[4] = 0x00
		t_data_array[5] = 0x01
		t_data_array[6] = 0x02
		t_data_array[7] = 0x00
		t_data_array[8] = 0x0a
		#t_data_array[9] = self.slave_dir_hi
		#t_data_array[10] = self.slave_dir_lo

		t_bytearray = array.array('B', t_data_array).tobytes()
		print(t_bytearray)
		#temp_crc_full = self.calcString( "\x05\x10\x10\x00\x00\x01\x02\x00\x0a", self.INITIAL_MODBUS)
		temp_crc_full = self.calcString( (t_bytearray), self.INITIAL_MODBUS)
		u16_crc16 = int(temp_crc_full)
		print(temp_crc_full)
		#u16_crc_reverse = ((u16_crc16<<8)&0xff00) | ((u16_crc16>>8)&0xff)
		self.slave_crc16_lo = ((u16_crc16)&0xff)
		self.slave_crc16_hi = ((u16_crc16>>8)&0xff)
		print("lo - {:02X} hi - {:02X}".format(self.slave_crc16_lo, self.slave_crc16_hi))
		print("lo - {} hi - {}".format(self.slave_crc16_lo, self.slave_crc16_hi))
		self.data_array[0] = t_data_array[0]
		self.data_array[1] = t_data_array[1]
		self.data_array[2] = t_data_array[2]
		self.data_array[3] = t_data_array[3]
		self.data_array[4] = t_data_array[4]
		self.data_array[5] = t_data_array[5]
		self.data_array[6] = t_data_array[6]
		self.data_array[7] = t_data_array[7]
		self.data_array[8] = t_data_array[8]
		#self.data_array[9] = self.slave_dir_hi
		#self.data_array[10] = self.slave_dir_lo
		self.data_array[9] = self.slave_crc16_lo
		self.data_array[10] = self.slave_crc16_hi
		self.data_bytearray = bytearray(self.data_array)
		print(self.data_bytearray)
		self.ser.write(self.data_bytearray)	

	def on_get_current_path(self):
		return(os.path.dirname(os.path.abspath(__file__)))	
	def on_save_to_file(self):
		#self.data_to_file(strftime("%Y-%m-%d_%Hh%Mm%Ss", gmtime()))	
		self.data_to_file_microphone(strftime("%Y-%m-%d_%Hh%Mm%Ss", gmtime()))
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
	def data_to_file_microphone(self, name = "milk_data"):
		self.file_description = self.description_widget.toPlainText()
		self.file_data_ch1 = self.data_to_storage		
		dict_to_save = {'description':self.file_description, 'DATA':self.file_data_ch1}
		dict_filename = "{}\\milk_microphone_{}.npy".format(os.path.dirname(os.path.abspath(__file__)),name)
		#filename = "{}\\milk_{}.dat".format(os.path.dirname(os.path.abspath(__file__)),name)
		
		try:
			np.save(dict_filename, dict_to_save)
			self.log_widget.appendPlainText("[{}] file succesful save".format(strftime("%H:%M:%S")))
		except Exception:
			self.log_widget.appendPlainText("[{}] {}".format(strftime("%H:%M:%S"), traceback.format_exc()))				
	def on_load_from_file(self):
		fname = QFileDialog.getOpenFileName(self, 'Open file', '{}/'.format(self.on_get_current_path()))[0]#/home
		self.log_widget.appendPlainText("[{}] {}".format(strftime("%H:%M:%S"), fname))	
		if fname:
			try:
				filename, file_extension = os.path.splitext(fname)
				if file_extension == ".BIN" or file_extension == ".bin":
					self.log_widget.appendPlainText("[{}] file succesful load".format(strftime("%H:%M:%S")))
					self.graph.clear()
					self.graph_pressure.clear()
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
					self.curve1 = self.graph.plot(self.x_ax,self.trace1, pen = pg.mkPen('g', width = 3), symbol = 'o', symbolSize = 4)
					self.curve2 = self.graph.plot(self.x_ax,self.trace2, pen = pg.mkPen('y', width = 3), symbol = 'o', symbolSize = 4)
				else:
					#self.log_widget.appendPlainText("[{}] wrong file type".format(strftime("%H:%M:%S")))
					data_dict = np.load(fname, allow_pickle=True)
					self.file_description = ""
					self.file_data_ch1 = np.empty(0)
					self.file_data_ch2 = np.empty(0)
					self.file_data_pressure = np.empty(0)
					self.file_data_microphone = np.empty(0)
					data_items = data_dict.item()

					file_type = 'MILK_PHOTODIODE'
					for key in data_items.keys():
						if key == 'DATA':
							file_type = 'MILK_MICROPHONE'
					if file_type == 'MILK_MICROPHONE':
						self.graph_pressure.clear()
						self.file_data_microphone = data_items['DATA']
						self.file_description = data_items['description']
						x_axio = np.linspace(0,len(self.file_data_microphone)-1, len(self.file_data_microphone))
						self.curve = self.graph_pressure.plot(x_axio,self.file_data_microphone, pen = pg.mkPen('w', width = 3), symbol = 'o', symbolSize = 4)

					else:
						self.graph.clear()
						self.graph_pressure.clear()
						
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

						self.curve1 = self.graph.plot(self.x_ax,self.trace1, pen = pg.mkPen('g', width = 3), symbol = 'o', symbolSize = 4)
						self.curve2 = self.graph.plot(self.x_ax,self.trace2, pen = pg.mkPen('y', width = 3), symbol = 'o', symbolSize = 4)
						self.curve3 = self.graph_pressure.plot(self.x_ax,self.trace3, pen = pg.mkPen('r', width = 3), symbol = 'o', symbolSize = 4)

						self.btn_save.setDisabled(False)
						self.log_widget.appendPlainText("[{}] file succesful load".format(strftime("%H:%M:%S")))
			except:
				self.log_widget.appendPlainText("[{}] file load failed".format(strftime("%H:%M:%S")))	
				self.log_widget.appendPlainText("[{}] {}".format(strftime("%H:%M:%S"), traceback.format_exc()))						

	def on_interrupted(self):
		self.meas_thread.running = False
		
	def on_display_record(self):
		self.graph.clear()
		self.record_number = self.current_row + 1
		self.cursor_trigger = 0
		self.xpos = 0
		self.ypos = 0
		#self.label_cord.setText("X pos: {:03d} Y pos: {:04d} Time: {:0.2f}sec".format(self.xpos, self.ypos, self.xpos*self.record_sampling_time))
		#self.graph.enableAutoRange(ViewBox.YAxis, enable=False)
		#self.graph.enableAutoRange(ViewBox.XAxis, enable=True)
		self.graph.showGrid(1,1,1)
		self.graph.addItem(self.vLine, ignoreBounds=True)
		self.graph.addItem(self.hLine, ignoreBounds=True)	
		self.plot_xaxis = list()
		for i in range(len(self.parsed_data_list[self.current_row])):
			self.plot_xaxis.append(i*self.record_sampling_time)

		self.curve = self.graph.plot(self.plot_xaxis,self.parsed_data_list[self.current_row], pen = pg.mkPen('g', width = 3), symbol = 'o', symbolSize = 10, title = "Record №{}".format(self.record_number))
		self.curve.curve.setClickable(True)

		self.curve.sigPointsClicked.connect(self.clicked_point)	

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
		
	def clicked_point(self, plot, points):
		global lastClicked
		if self.last_clicked_plot == self.current_row:
			try:
				for p in self.lastClicked:
					p.resetPen()
			except:
				pass
		if self.last_clicked_plot != self.current_row:
			self.cursor_trigger = 0
		if self.cursor_trigger == 0:
			self.xpos = int(points[0].pos()[0]/self.record_sampling_time)
			self.ypos = int(points[0].pos()[1])
			#self.label_cord.setText("X pos: {:03d} Y pos: {:04d} Time: {:0.2f}sec".format(self.xpos, self.ypos, self.xpos*self.record_sampling_time))

			for p in points:
				p.setPen(pg.mkPen(color='r', width=4))  #'r', width=5)
		self.lastClicked = points
		self.last_clicked_plot = self.current_row	
		self.cursor_trigger += 1
		if self.cursor_trigger >= 2:
			self.cursor_trigger = 0

		self.vLine.setPos(points[0].pos()[0])
		try:
			self.hLine.setPos(self.parsed_data_list[self.current_row][self.xpos])
		except:
			pass#print("x pos out of range")
	def crc16(self, data: bytes, poly=0xa001):
	    '''
	    CRC-16-CCITT Algorithm
	    '''
	    data = bytearray(data)
	    crc = 0xFFFF
	    for b in data:
	        cur_byte = 0xFF & b
	        for _ in range(0, 8):
	            if (crc & 0x0001) ^ (cur_byte & 0x0001):
	                crc = (crc >> 1) ^ poly
	            else:
	                crc >>= 1
	            cur_byte >>= 1
	    crc = (~crc & 0xFFFF)
	    crc = (crc << 8) | ((crc >> 8) & 0xFF)
	    
	    return crc & 0xFFFF			
	def calcByte(self, ch, crc):
	    """Given a new Byte and previous CRC, Calc a new CRC-16"""
	    if type(ch) == type("c"):
	        by = ord( ch)
	    else:
	        by = ch
	    crc = (crc >> 8) ^ self.table[(crc ^ by) & 0xFF]
	    return (crc & 0xFFFF)

	def calcString(self, st, crc):
	    """Given a binary string and starting CRC, Calc a final CRC-16 """
	    for ch in st:
	        crc = (crc >> 8) ^ self.table[(crc ^ (ch)) & 0xFF] #ord(ch) 
	    return crc
class evThread(QtCore.QThread):
	
	status_signal = QtCore.pyqtSignal(str)
	dataplot = QtCore.pyqtSignal(int)
	progress = QtCore.pyqtSignal(int)
	dataplot_array = QtCore.pyqtSignal(list)

	def __init__(self, parent = None):
		QtCore.QThread.__init__(self,parent)
		self.running = False
		self.ComPort = str
		self.data = 0
		self.data_array = list()
		
	def run(self):
		self.running = True
		while self.running == True:
			if self.running == True:
				self.data_array = list()
				for i in range(1000):
					self.data = int.from_bytes((self.ser.read(1)), byteorder='big', signed=False)#100*np.random.random(1)#
					self.data_array.append(self.data)
					#time.sleep(0.0001)
				#print(int.from_bytes((self.ser.read(1)), byteorder='big', signed=False))
				#print(self.data_array)
				self.dataplot_array.emit(self.data_array)

				self.status_signal.emit("in progress")
				#self.dataplot.emit(self.data)
			#time.sleep(0.01)
			if self.running == False:
				self.status_signal.emit("Interrupted")

	def on_connected(self, comport):
		try:
			self.ComPort = comport
			self.ser = serial.Serial(self.ComPort, baudrate=921600, bytesize=serial.EIGHTBITS,
									 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout = 0.01)
			self.ser.isOpen()  # try to open port
			#self.btn_visa_connect.setDisabled(True)
			#self.btn_visa_disconnect.setDisabled(False)
			#self.btn_fetch.setDisabled(False)
			#self.btn_save.setDisabled(False)
			self.serialDeviceConnected = True
			#self.comport_combo.setEnabled(False)
			#self.log_widget.appendPlainText("[{}] Connected to {}".format(strftime("%H:%M:%S"), self.ComPort))
		except IOError:
			print("Port already open another programm")
			#self.log_widget.appendPlainText("[{}] Port {} already open another programm".format(strftime("%H:%M:%S"), self.ComPort))
		except serial.SerialException:
			print("SerialException")

			#self.log_widget.appendPlainText("[{}] SerialException".format(strftime("%H:%M:%S")))
		#except Exception:
			#print("Unexpected error, Null ComName")
			#self.log_widget.appendPlainText("[{}] unexpected error".format(strftime("%H:%M:%S")))
	def on_disconnected(self):
		#self.btn_visa_connect.setDisabled(False)
		#self.btn_visa_disconnect.setDisabled(True)	
		#self.btn_fetch.setDisabled(True)
		#self.btn_save.setDisabled(True)
		self.serialDeviceConnected = False
		#self.comport_combo.setEnabled(True)
		#self.log_widget.appendPlainText("[{}] Disconnected".format(strftime("%H:%M:%S")))
		try:	
			self.ser.close()
		except:
			print("serial port close exception, on_disconnect --traceback")
			#self.log_widget.appendPlainText("[{}] error, device session lost".format(strftime("%H:%M:%S")))
		#print("Disconnected")
			
	def on_activated_com_list(self, str):
		if self.comport_combo.currentText() == "" or self.serialDeviceConnected == True:
			self.btn_visa_connect.setDisabled(True)
		elif self.comport_combo.currentText() == "Refresh":
			self.btn_visa_connect.setDisabled(True)
			self.comport_combo.clear()
			self.comport_combo.addItems([""])
			self.comport_combo.addItems(["Refresh"])
			self.comport_combo.addItems(serial_ports())
		else:
			self.ComPort = str
			self.btn_visa_connect.setDisabled(False)


		
class ppData:
	"""this class will be used for post processing of data"""
	def __init__(self, parent = None):
		dataFromFile = (list)


def serial_ports():
	""" Lists serial port names
		:raises EnvironmentError:
			On unsupported or unknown platforms
		:returns:
			A list of the serial ports available on the system
	"""
	if sys.platform.startswith('win'):
		ports = ['COM%s' % (i + 1) for i in range(256)]
	elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
		# this excludes your current terminal "/dev/tty"
		ports = glob.glob('/dev/tty[A-Za-z]*')
	elif sys.platform.startswith('darwin'):
		ports = glob.glob('/dev/tty.*')
	else:
		raise EnvironmentError('Unsupported platform')

	result = []
	for port in ports:
		try:
			s = serial.Serial(port)
			s.close()
			result.append(port)
		except (OSError, serial.SerialException):
			pass
	return result		
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)		

if __name__ == '__main__':
	import sys
	import time, math

	app =QtWidgets.QApplication(sys.argv)
	ex = CommonWindow()
	ex.setFont(QtGui.QFont('Arial', 9))#, QtGui.QFont.Bold
	ex.setWindowTitle("Milk fetch ver 1.0.0")
	#app.setStyle('Fusion')
	app.setStyleSheet ( qdarkstyle . load_stylesheet ())
	#ex.setWindowFlags(ex.windowFlags() | QtCore.Qt.FramelessWindowHint)
	ex.comport_combo.addItems(serial_ports())
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
	