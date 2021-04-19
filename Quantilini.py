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
#import bluetooth
import qdarkstyle 
import array
import qutip


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
		self.previous_row = 0
		self.current_row = -1

		self.count = 0
		self.last_clicked_plot = 0
		#pg.setConfigOption('background', 'd')
		pg.setConfigOption('foreground', 'g')	
		#self.label_graph = pg.LabelItem(text = "x and y", color = "CCFF00")#justify='right'
		self.graph = pg.PlotWidget()
		self.graph.sizeHint = lambda: pg.QtCore.QSize(100, 100)
		#self.graph_pressure = pg.PlotWidget()

		self.view = gl.GLViewWidget()
		self.view.show()
		self.view.sizeHint = lambda: pg.QtCore.QSize(100, 100)
		self.view.setSizePolicy(self.graph.sizePolicy())
		self.xgrid = gl.GLGridItem()
		self.ygrid = gl.GLGridItem()
		self.zgrid = gl.GLGridItem()

		self.view.addItem(self.xgrid)
		self.view.addItem(self.ygrid)
		self.view.addItem(self.zgrid)

		self.xgrid.rotate(90,0,1,0)
		self.ygrid.rotate(90,1,0,0)

		self.xgrid.scale(0.2, 0.1, 0.1)
		self.ygrid.scale(0.2, 0.1, 0.1)
		self.zgrid.scale(0.1, 0.2, 0.1)

		self.lastClicked = []
		#PlotCurveItem   PlotWidget
		self.graph.showGrid(1,1,1)
		#self.graph_pressure.showGrid(1,1,1)
		self.plot_xaxis = list()
		self.index = 0
		self.graph.setLabel('bottom', "Time, sec")
		#self.graph_pressure.setLabel("bottom", "Time, sec")
		#self.graph.setLabel('top', self.label_graph)
		#self.graph.showLabel(show = True)
		self.graph.setMinimumSize(500,200)
		#self.graph_pressure.setMinimumSize(500, 200)
		
		self.vb = self.graph.plotItem.vb

		self.vLine = pg.InfiniteLine(angle=90, movable=False, pen = pg.mkPen('y', width = 1))
		self.hLine = pg.InfiniteLine(angle=0, movable=False, pen = pg.mkPen('y', width = 1))
		self.graph.addItem(self.vLine, ignoreBounds=True)
		self.graph.addItem(self.hLine, ignoreBounds=True)
		self.graph.setRange(yRange = (0,4095))
		#self.graph_pressure.setRange(yRange = (0,100))

		self.curve = self.graph.plot(self.x_ax,self.trace1, pen = pg.mkPen('g', width = 3), symbol = 'o', symbolSize = 10)
		self.curve = self.graph.plot(self.x_ax,self.trace2, pen = pg.mkPen('y', width = 3), symbol = 'o', symbolSize = 10)
		#self.curve_pressure = self.graph_pressure.plot(self.x_ax,self.trace3, pen = pg.mkPen('r', width = 3), symbol = 'o', symbolSize = 10)

		xx = 0
		yx = 0
		zx = 0

		xy = 0
		yy = 0
		zy = 1

		Xdot = (xx, yx, zx)
		Ydot = (xy, yy, zy)
		Zdot = (1,1,1)
		pts = np.array([Xdot, Ydot])
		sh1 = gl.GLLinePlotItem(pos=pts, width = 4, antialias = False, mode = 'line_strip', color = (0.0, 1.0, 0.0, 1.0))
		self.view.addItem(sh1)

		self.md = gl.MeshData.sphere(rows=20, cols=40,radius=[1])
		self.m1 = gl.GLMeshItem(meshdata=self.md,smooth=True,color=(0.5, 0, 0.5, 0.2),shader="balloon",glOptions="additive")
		self.view.addItem(self.m1)		

		self.view.setCameraPosition(distance=10, azimuth=-90)
		self.view.setWindowTitle('3D plot label')

		self.ComPort = str
		self.comport_combo = QtWidgets.QComboBox()
		self.comport_combo.addItems([""])
		self.comport_combo.addItems(["Refresh"])
		self.comport_combo.activated[str].connect(self.on_activated_com_list)
		self.comport_combo.activated[str].connect(self.ComPort)

		vertical_size = 30
		horizontal_size = 80
		
		self.onlyInt = QtGui.QIntValidator(1,5000)
		
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
		self.grid.addWidget(self.btn_save,2,1)
		self.grid.addWidget(self.btn_load_file, 2,2)
		self.grid.addWidget(self.data_fetch_timeout, 2,3)

		self.grid.addWidget(self.description_widget, 3,0,4,5)
		self.grid.addWidget(self.log_widget, 8, 0, 7, 5)

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
		self.vbox_1.insertStretch(3,0)
		
		self.hbox = QtWidgets.QHBoxLayout()
		self.vbox_graph_table = QtWidgets.QVBoxLayout()

		self.vbox_graph_table.addWidget(self.graph)
		self.vbox_graph_table.addWidget(self.view)
		self.vbox_graph_table.insertStretch(2,0)
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

		self.btn_visa_connect.clicked.connect(self.on_connected)
		self.btn_visa_connect.clicked.connect(self.on_get_current_path)
		self.btn_visa_disconnect.clicked.connect(self.on_disconnected)
		self.btn_save.clicked.connect(self.on_save_to_file)
		self.btn_load_file.clicked.connect(self.on_load_from_file) 
		self.btn_fetch.clicked.connect(self.on_fetch_data)

	def on_connected(self):
		try:
			self.ser = serial.Serial(self.ComPort, baudrate=115200, bytesize=serial.EIGHTBITS,
									 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout = 0.1)
			self.ser.isOpen()  # try to open port
			self.btn_visa_connect.setDisabled(True)
			self.btn_visa_disconnect.setDisabled(False)
			self.btn_fetch.setDisabled(False)
			self.btn_save.setDisabled(False)
			self.serialDeviceConnected = True
			self.comport_combo.setEnabled(False)
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
			self.ser.close()
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
		else:
			self.fetch_enable = True
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
					#self.graph_pressure.clear()
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
					#self.log_widget.appendPlainText("[{}] wrong file type".format(strftime("%H:%M:%S")))
					data_dict = np.load(fname, allow_pickle=True)
					self.file_description = ""
					self.file_data_ch1 = np.empty(0)
					self.file_data_ch2 = np.empty(0)
					self.file_data_pressure = np.empty(0)
					data_items = data_dict.item()
					self.graph.clear()
					#self.graph_pressure.clear()
					
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
					#self.curve3 = self.graph_pressure.plot(self.x_ax,self.trace3, pen = pg.mkPen('r', width = 3), symbol = 'o', symbolSize = 10)

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
	