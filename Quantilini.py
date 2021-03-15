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


__version__ = '0.10'

class CommonWindow(QtWidgets.QWidget):
	"""Класс основного окна программы"""
	#QMainWindow
	#QtWidgets.QWidget
	def __init__(self, parent = None):
		QtWidgets.QMainWindow.__init__(self, parent)

		self.serialDeviceConnected = False

		self.data = [0]#test data value for plot
		self.parsed_data_list = list()
		self.records_header_list = list()
		self.records_tool_passage_time = list()
		self.records_description = list()
		self.data_download_done = 0
		self.data_load_from_file_done = 0
		self.record_sampling_time = 0.0045
		self.mag_threshold = 100
		self.lf_threshold  = 100 
		self.mag_filter_from_mcu = 10
		#self.label = QtWidgets.QLabel("<b>S21</b> measure only regime")
		#self.label.setAlignment(QtCore.Qt.AlignHCenter)
		self.first_load = 0
		self.previous_row = 0
		self.current_row = -1

		self.count = 0
		self.last_clicked_plot = 0
		#pg.setConfigOption('background', 'd')
		pg.setConfigOption('foreground', 'g')	
		#self.label_graph = pg.LabelItem(text = "x and y", color = "CCFF00")#justify='right'
		self.graph = pg.PlotWidget()
		self.lastClicked = []
		#PlotCurveItem   PlotWidget
		self.graph.showGrid(1,1,1)
		self.plot_xaxis = list()
		self.index = 0
		self.graph.setLabel('bottom', "Time, sec")
		#self.graph.setLabel('top', self.label_graph)
		#self.graph.showLabel(show = True)
		self.graph.setMinimumSize(500,200)

		self.vb = self.graph.plotItem.vb

		self.vLine = pg.InfiniteLine(angle=90, movable=False, pen = pg.mkPen('y', width = 1))
		self.hLine = pg.InfiniteLine(angle=0, movable=False, pen = pg.mkPen('y', width = 1))
		self.graph.addItem(self.vLine, ignoreBounds=True)
		self.graph.addItem(self.hLine, ignoreBounds=True)
		self.graph.setRange(yRange = (0,4095))

		#f(x) = f(x1)+(x-x1)*((f(x2)-f(x1))/(x2-x1)) 
		#m = PlotCanvas(self, width = 5, height = 4)
		#m.move(320,20)
		#self.show()
		#r1 = PlotCanvas_onePlot(self, width = 5, height = 4)
		#r1.move(800,20)
		#self.show()
		#self.curve = self.graph.plot(self.data, pen = pg.mkPen('g', width = 4), symbol = 'o', title = "Record №{}".format(self.record_number), clickable=True)
		#data = [2021,2025,2017,2018,2023,2026,2035,2058,2082,2134,2169,2224,2151,2113,2042,2021,2021,2021,2021,2021,2021,2021,2021,2021]#test data value for plot
		#self.curve.curve.setClickable(True)
			
		self.btnStartMeas = QtWidgets.QPushButton("Start &Measurements")
		#self.btnStartMeas.setIcon(QtGui.QIcon("icon.png"))
		self.btnInterruptMeas = QtWidgets.QPushButton("Interrupt process")

		self.notch_int_value = 90 #50Hz value for notch filter
		self.usb_order_cnt = 0
		self.ComPort = str
		self.comport_combo = QtWidgets.QComboBox()
		self.comport_combo.addItems([""])
		self.comport_combo.addItems(["Refresh"])
		self.comport_combo.activated[str].connect(self.on_activated_com_list)
		self.comport_combo.activated[str].connect(self.ComPort)

		self.ypos = 0
		self.xpos = 0
		self.cursor_trigger = 0
		vertical_size = 30
		horizontal_size = 80
		
		self.onlyInt = QtGui.QIntValidator(1,1000)
		#self.LineEdit.setValidator(self.onlyInt)
		
		#self.label_cord = QtWidgets.QLabel("X pos: {:03d} Y pos: {:04d} Time: {:0.2f}sec".format(self.xpos, self.ypos, self.xpos*self.record_sampling_time))
		#self.label_cord.setMaximumSize(240,60)
		#self.label_cord.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)		
		self.btn_cord_fixed = QtWidgets.QPushButton("&Capture")
		self.btn_cord_fixed.setMaximumSize(120,60)
		self.btn_cord_fixed.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)

		self.btn_load_file = QtWidgets.QPushButton("&Load File")
		self.btn_load_file.setMaximumSize(80,60)
		self.btn_load_file.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		self.btn_clear_table = QtWidgets.QPushButton("Clea&r")
		self.btn_clear_table.setMaximumSize(80,60)
		self.btn_clear_table.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)		

		self.label_visa_connect = QtWidgets.QLabel("COM port:")
		self.label_visa_connect.setMaximumSize(horizontal_size,vertical_size)
		self.label_visa_connect.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		self.btn_visa_connect = QtWidgets.QPushButton("Connect")
		self.btn_visa_connect.setMaximumSize(horizontal_size,vertical_size)
		self.btn_visa_connect.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)#Fixed
		self.btn_visa_disconnect = QtWidgets.QPushButton("Disconnect")
		self.btn_visa_disconnect.setMaximumSize(horizontal_size,vertical_size)
		self.btn_visa_disconnect.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)#Fixed		
		self.btn_visa_disconnect.setDisabled(True)
			
		self.agm_serial_number = QtWidgets.QLineEdit("001")#center frequency for nwa
		self.agm_serial_number.setMaximumSize(horizontal_size,vertical_size)
		self.agm_serial_number.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		self.agm_serial_number.setValidator(self.onlyInt)
		self.agm_serial_number.setAlignment(QtCore.Qt.AlignCenter)

		self.agm_lf_and_mag_threshold_label = QtWidgets.QLabel("Threshold settling:")
		self.agm_lf_and_mag_threshold_label.setMaximumSize(200,vertical_size)
		self.agm_lf_and_mag_threshold_label.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)#Fixed

		self.agm_lf_and_mag_threshold_line = QtWidgets.QLineEdit("100")#center frequency for nwa
		self.agm_lf_and_mag_threshold_line.setMaximumSize(horizontal_size,vertical_size)
		self.agm_lf_and_mag_threshold_line.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		self.agm_lf_and_mag_threshold_line.setValidator(self.onlyInt)
		self.agm_lf_and_mag_threshold_line.setAlignment(QtCore.Qt.AlignCenter)

		self.agm_lf_and_mag_threshold_button = QtWidgets.QPushButton("Set")
		self.agm_lf_and_mag_threshold_button.setMaximumSize(horizontal_size,vertical_size)
		self.agm_lf_and_mag_threshold_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)#Fixed

		self.agm_lf_and_mag_threshold_combobox = QtWidgets.QComboBox(self)
		self.agm_lf_and_mag_threshold_combobox.addItems(["MAG", "LF"])
		self.agm_lf_and_mag_threshold_combobox.setMaximumSize(horizontal_size,vertical_size)
		self.agm_lf_and_mag_threshold_combobox.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)

		self.agm_mag_filter_cutout_frequency_label = QtWidgets.QLabel("Mag Filter \ncutoff frequency:")
		self.agm_mag_filter_cutout_frequency_label.setMaximumSize(200,vertical_size)
		self.agm_mag_filter_cutout_frequency_label.setSizePolicy(QtWidgets.QSizePolicy.Maximum,QtWidgets.QSizePolicy.Maximum)

		self.agm_mag_filter_cutout_frequency_combobox = QtWidgets.QComboBox(self)
		self.agm_mag_filter_cutout_frequency_combobox.addItems(["10Hz", "15Hz", "20Hz", "25Hz", "30Hz", "40Hz", "50Hz", "75Hz", "100Hz", "150Hz", "200Hz"])
		self.agm_mag_filter_cutout_frequency_combobox.setMaximumSize(horizontal_size,vertical_size)
		self.agm_mag_filter_cutout_frequency_combobox.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)

		self.agm_mag_filter_cutout_frequency_button = QtWidgets.QPushButton("Set")
		self.agm_mag_filter_cutout_frequency_button.setMaximumSize(horizontal_size,vertical_size)
		self.agm_mag_filter_cutout_frequency_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)


		self.btn_update_agm_id = QtWidgets.QPushButton("Update")
		self.btn_update_agm_id.setMaximumSize(60,vertical_size)
		self.btn_update_agm_id.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		
		vertical_size = 30
		horizontal_size = 90
		
		self.agm_recordbutton = QtWidgets.QPushButton("Display \nrecord")
		self.agm_recordbutton.setMaximumSize(horizontal_size,vertical_size)
		self.agm_recordbutton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)#Fixed

		#self.agm_filterbox = QtWidgets.QComboBox(self)#span for nwa
		#self.agm_filterbox.addItems(["50Hz", "60Hz"])
		#self.agm_filterbox.setMaximumSize(horizontal_size,vertical_size)
		#self.agm_filterbox.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)		
		#self.agm_filter_label = QtWidgets.QLabel("Filter:")
		#self.agm_filter_label.setMaximumSize(horizontal_size,vertical_size)
		#self.agm_filter_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Maximum)		
		
		
		self.agm_readblock = QtWidgets.QLabel("None")
		self.agm_readblock.setMaximumSize(horizontal_size,vertical_size)
		self.agm_readblock.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Maximum)#Fixed		
		#self.lbl_g = QtWidgets.QLabel()
		#self.lbl.setPixmap(self.gifka)
		#self.movie = QtGui.QMovie("just.gif",QtCore.QByteArray(),self)
		#self.movie.setSpeed(100)
		#self.lbl_g.setMovie(self.movie)
		#self.movie.start()
		
		self.table_of_records = QtWidgets.QTableWidget(self)
		self.table_of_records.setColumnCount(7)
		self.table_of_records.setMinimumSize(400,200)
		self.table_of_records.setMaximumSize(2000,2700)
		self.table_of_records.setRowCount(200)
		self.table_of_records.setHorizontalHeaderLabels(["Param", "Param","Param","Param", "Param", "Param", "Param"])
		self.table_of_records.horizontalHeaderItem(0).setTextAlignment(QtCore.Qt.AlignCenter)
		self.table_of_records.horizontalHeaderItem(1).setTextAlignment(QtCore.Qt.AlignCenter)
		self.table_of_records.horizontalHeaderItem(2).setTextAlignment(QtCore.Qt.AlignCenter)
		self.table_of_records.horizontalHeaderItem(3).setTextAlignment(QtCore.Qt.AlignCenter)
		self.table_of_records.horizontalHeaderItem(4).setTextAlignment(QtCore.Qt.AlignCenter)
		self.table_of_records.horizontalHeaderItem(5).setTextAlignment(QtCore.Qt.AlignCenter)
		self.table_of_records.horizontalHeaderItem(6).setTextAlignment(QtCore.Qt.AlignCenter)
		
		self.table_of_records.horizontalHeader().setStretchLastSection(False)
		
		self.table_of_records.resizeColumnsToContents()
		self.table_of_records.setColumnWidth(0, 100)
		self.table_of_records.setColumnWidth(1, 100)
		self.table_of_records.setColumnWidth(2, 100)
		self.table_of_records.setColumnWidth(3, 200)
		self.table_of_records.setColumnWidth(4, 100)
		self.table_of_records.setColumnWidth(5, 100)
		self.table_of_records.setColumnWidth(6, 100)
		#self.table_of_records.resizeRowsToContents()
		#self.table_of_records.resizeColumnsToContents()
		#self.table_of_records.setRowHeight(0,40)
		#self.table_of_records.setRowHeight(1,40)
		#self.table_of_records.setRowHeight(2,40)
		
		self.bar = QtWidgets.QProgressBar(self)
		self.bar.setMaximumSize(200,20)
		self.bar.setMinimumSize(300,20)
		self.bar.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		#self.bar.setValue(0)
		#self.bar.setRange(min,max)
		#self.pixmap = QtGui.QPixmap("screensaver.png")
		#self.lbl = QtWidgets.QLabel(self)
		#self.lbl.setPixmap(self.pixmap)
		
		self.btn_load = QtWidgets.QPushButton("&Download")
		#self.btn_load.setWhatsThis("Load file from PC")
		self.btn_load.setMaximumSize(horizontal_size,vertical_size)
		self.btn_load.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		#self.btn_stop = QtWidgets.QPushButton("S&top")
		#self.btn_stop.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		#self.btn_stop.setMaximumSize(horizontal_size,vertical_size)
		self.btn_save = QtWidgets.QPushButton("&Save")
		self.btn_save.setMaximumSize(horizontal_size,vertical_size)
		self.btn_save.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		#self.btn_pause = QtWidgets.QPushButton("&Pause")
		#self.btn_pause.setMaximumSize(horizontal_size,vertical_size)
		#self.btn_pause.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)		
		
		self.grid = QtWidgets.QGridLayout()
		self.grid_2 = QtWidgets.QGridLayout()
		self.grid_plot_labels = QtWidgets.QGridLayout()

		self.grid.addWidget(self.label_visa_connect, 0, 0)
		self.grid.addWidget(self.comport_combo, 0, 1)
		self.grid.addWidget(self.btn_visa_connect, 0, 2)
		self.grid.addWidget(self.btn_visa_disconnect, 0, 3)

		#self.grid.addWidget(self.agm_serial_number_label, 1, 0, alignment = QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
		#self.grid.addWidget(self.agm_utc_label, 2, 0, alignment = QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)

		#self.grid.addWidget(self.agm_serial_number, 1, 1)#, alignment = QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
		#self.grid.addWidget(self.btn_update_agm_id,1,2)
		#self.grid.addWidget(self.agm_utc, 2, 1)
		
		self.grid.addWidget(self.btn_load,4,0)
		#self.grid.addWidget(self.btn_stop,2,1)
		self.grid.addWidget(self.btn_save,4,1)
		self.grid.addWidget(self.btn_load_file, 4,2)
		self.grid.addWidget(self.btn_clear_table, 5, 1)
		

		self.grid_plot_labels.addWidget(self.btn_cord_fixed, 0,0)
		self.grid_plot_labels.addWidget(QtWidgets.QLabel(""),0,3)
		self.grid_plot_labels.addWidget(QtWidgets.QLabel(""),0,5)
		#self.grid_plot_labels.insertStretch(0,4)
			
		self.grid_2.addWidget(QtWidgets.QLabel(""),8,0)
		self.grid_2.addWidget(QtWidgets.QLabel(""),8,1)
		self.grid_2.addWidget(QtWidgets.QLabel(""),8,2)
		self.grid_2.addWidget(QtWidgets.QLabel(""),8,3)

		self.grid.addWidget(QtWidgets.QLabel(""),7,0)
		self.grid.addWidget(QtWidgets.QLabel(""),7,1)
		self.grid.addWidget(QtWidgets.QLabel(""),7,2)
		self.grid.addWidget(QtWidgets.QLabel(""),7,3)
		
		self.grid.addWidget(self.bar,8,0,1,5)

		self.grid.addWidget(self.agm_lf_and_mag_threshold_label, 9,0,1,5)
		self.grid.addWidget(self.agm_lf_and_mag_threshold_combobox, 10,0,1,1)
		self.grid.addWidget(self.agm_lf_and_mag_threshold_line, 10,1,1,2)
		self.grid.addWidget(self.agm_lf_and_mag_threshold_button, 10,2,1,4)

		self.grid.addWidget(self.agm_mag_filter_cutout_frequency_label,11,0,1,5)
		self.grid.addWidget(self.agm_mag_filter_cutout_frequency_combobox,12,0,1,1)
		self.grid.addWidget(self.agm_mag_filter_cutout_frequency_button,12,1,1,4)

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

		self.vbox_graph_table.insertLayout(0,self.grid_plot_labels)
		self.vbox_graph_table.addWidget(self.graph)
		self.vbox_graph_table.addWidget(self.table_of_records,1)
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

		self.btn_load.setDisabled(True)
		self.btn_save.setDisabled(True)

		#self.agm_filterbox.setDisabled(True)
		#self.btn_notch_open_window.setDisabled(True)
		self.meas_thread = evThread()
		#self.tcp_server_thread = tcpThread()

		self.btn_visa_connect.clicked.connect(self.on_connected)
		self.btn_visa_connect.clicked.connect(self.on_get_current_path)
		#self.btn_visa_disconnect.clicked.connect(self.on_disconnected)
		self.btn_save.clicked.connect(self.on_save_to_file)
		self.btn_load_file.clicked.connect(self.on_load_from_file) 
		self.btn_clear_table.clicked.connect(self.on_clear_table)

		self.btn_cord_fixed.clicked.connect(self.on_captured)

		self.btn_load.clicked.connect(self.on_start_load)
		#self.meas_thread.started.connect(self.on_meas_started)
		#self.meas_thread.finished.connect(self.on_meas_completed)
		#self.meas_thread.status_signal.connect(self.on_status_text_change, QtCore.Qt.QueuedConnection)
		#self.meas_thread.dataplot.connect(self.graph.plot, QtCore.Qt.QueuedConnection)
		#self.meas_thread.progress.connect(self.on_progress_go,QtCore.Qt.QueuedConnection)
		
		#self.btn_clear.clicked.connect(self.on_clear)

		#self.pwindow = paramWindow()
		#self.gsmwindow = paramWindow_GSM()
		#self.tcpwindow = paramWindow_TCP(self.external_ip)
		#self.gsmwindow.btn_gsm_apply.clicked.connect(self.on_gsm_apply)
		#self.gsmwindow.btn_gsm_testSMS.clicked.connect(self.on_gsm_test_sms_send)
		#self.tcpwindow.btn_tcp_apply.clicked.connect(self.on_tcp_apply)

		#self.pwindow.btn_notch_apply.clicked.connect(self.on_apply_notch_settings)
		#self.pwindow.btn_notch_set_value.clicked.connect(self.on_set_notch_potentiometr)
		#self.pwindow.btn_notch_set_value_down.clicked.connect(self.on_set_notch_potentiometr_down)
		#self.pwindow.btn_notch_set_value.clicked.connect(self.on_set_notch_potentiometr)
		#self.pwindow.notch_type_box.currentIndexChanged.connect(self.on_notch_type_changed)
		#self.agm_recordbutton.clicked.connect(self.on_display_record)
		self.table_of_records.itemClicked.connect(self.on_change_table_item)
		self.table_of_records.itemChanged.connect(self.on_change_description)
		#self.agm_filterbox.activated.connect(self.on_change_notch_filter)
		#self.comport_combo.activated.connect(self.on_activated_com_list)
		#self.btn_download_raw.clicked.connect(self.on_download_raw)
		self.proxy = pg.SignalProxy(self.graph.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

		#self.curve.sigClicked.connect(self.clicked_point)
		#self.curve.sigPointsClicked.connect(self.clicked_point)

	def on_open_notch_window(self):
		self.pwindow.resize(200,100)
		self.pwindow.setWindowTitle("Notch Filter")
		self.pwindow.show()

	def on_connected(self):
		try:
			self.ser = serial.Serial(self.ComPort, baudrate=115200, bytesize=serial.EIGHTBITS,
									 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout = 0.1)
			
			self.ser.isOpen()  # try to open port
			print("Connected to {}".format(self.ComPort))

			self.btn_visa_connect.setDisabled(True)
			self.btn_update_agm_id.setDisabled(False)
			self.btn_visa_disconnect.setDisabled(False)
			self.btn_load.setDisabled(False)
			#self.btn_save.setDisabled(True)
			self.btn_clear.setDisabled(False)
			self.agm_serial_number.setDisabled(False)
			#self.agm_filterbox.setDisabled(False)
			self.agm_utc.setDisabled(False)
			self.btn_notch_open_window.setDisabled(False)
			self.btn_bluetooth.setDisabled(False)
			self.serialDeviceConnected = True
			self.comport_combo.setEnabled(False)

			self.on_fetch_board_params()

		except IOError:
			#pass
			print("Port already open another programm")
			#error_dialog = QtWidgets.QErrorMessage()
			#error_dialog.showMessage('Port already open another programm')
		except serial.SerialException:
			print("SerialException")
		except:
			print("Unexpected error, Null ComName")
	def on_change_serial_number(self):
		if self.agm_serial_number.text() != self.previous_agm_serial_number:
			adr_hi_byte = ((int)(self.agm_serial_number.text())>>8)&0xFF
			adr_lo_byte = ((int)(self.agm_serial_number.text())&0xff)
			print(bytearray.fromhex('7f aa 01 02 {:02X} {:02X}'.format(adr_hi_byte, adr_lo_byte)))
			self.ser.write(bytearray.fromhex('7f aa 01 02 {:02X} {:02X}'.format(adr_hi_byte, adr_lo_byte)))
		self.previous_agm_serial_number = self.agm_serial_number.text()	

	def on_activated_com_list(self, str):
		#self.label.setText(str)
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
				
	def on_clear(self):
		clear_res = QtWidgets.QMessageBox.question(self, "Подтверждение стирания памяти МК", "Вы действительно хотите стереть данные?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No )
		if clear_res == QtWidgets.QMessageBox.Yes:
			#self.graph.clear()
			#self.bar.setValue(0)
			self.ser.write(bytearray.fromhex('7f aa 01 03 00 00'))
	
	def on_choose_param(self):
		self.pwindow.resize(200,100)
		self.pwindow.setWindowTitle("SetParam")
		self.count += 1;
		self.label_level_1.setText("{}".format(self.count))
		
		self.pwindow.show()
	def on_progress_go(self,progress):
		self.bar.setValue(progress)
		
	def on_start_load(self):
		self.btn_load.setDisabled(True)
		self.btn_save.setDisabled(True)
		self.btn_clear.setDisabled(True)
		self.bar.setValue(0)
		self.graph.clear()
		self.on_clear_table()
		self.meas_thread.start()
		self.read_mcu_packed()

	def on_get_current_path(self):
		print(os.path.dirname(os.path.abspath(__file__)))	
		
	def on_save_to_file(self):
		
		self.data_to_file(strftime("%Y-%m-%d_%Hh%Mm%Ss", gmtime()), self.parsed_data_list)	

	def data_to_file(self, name = "agm_data", agm_data=[0,0]):
		dict_to_save = {'header':self.records_header_list, 'captured_time':self.records_tool_passage_time,'description':self.records_description, 'data':self.parsed_data_list}
		print(dict_to_save)
		dict_filename = "{}\\agm_{}.npy".format(os.path.dirname(os.path.abspath(__file__)),name)
		filename = "{}\\agm_{}.dat".format(os.path.dirname(os.path.abspath(__file__)),name)
		try:
			#for i in range(len(agm_data)):
			#	np.savetxt(filename, agm_data[i], delimiter = ',')#, fmt='%x')
				
			np.save(dict_filename, dict_to_save)
			print("saved")

		except Exception:
			traceback.print_exc()

	def on_load_from_file(self):
		fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]
		if fname:
			try:
				data_dict = np.load(fname, allow_pickle=True)
				self.parsed_data_list = list()
				self.records_tool_passage_time = list()
				self.records_description = list()
				self.records_header_list = list()
				self.table_of_records.setRowCount(0)
				self.table_of_records.setRowCount(200)
				data_items = data_dict.item()
				self.graph.clear()
				self.records_header_list = data_items['header']
				self.records_tool_passage_time = data_items['captured_time']
				self.records_description = data_items['description']
				self.parsed_data_list = data_items['data']	
				self.data_download_done = 1
				for i in range(len(data_items['header'])):
					self.header_processing(i, self.records_header_list[i], int(len(self.parsed_data_list[i])))
				self.btn_save.setDisabled(False)
			except:
				pass								

	def on_clear_table(self):
		self.table_of_records.setRowCount(0)
		self.table_of_records.setRowCount(200)
		self.graph.clear()
		self.parsed_data_list = list()
		self.records_tool_passage_time = list()
		self.records_header_list = list()		
		self.btn_save.setDisabled(True)
		self.data_download_done = 0
		self.data_load_from_file_done = 0

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

	def on_change_description(self, item):
		if item.column() == 6:
			self.records_description[item.row()] = item.text()		
	def on_change_table_item(self, item):
		self.previous_row = self.current_row
		self.current_row = item.row()
		try:
			for j in range(7):
				self.table_of_records.item(self.current_row, j).setBackground(QtGui.QColor(100,200,50))
				if self.previous_row != -1:
					self.table_of_records.item(self.previous_row, j).setBackground(QtGui.QColor(255,255,255))
			if	self.current_row != self.previous_row:
			
				try:
					self.on_display_record()
				except:
					pass
		except:
			print("setBackgroud error")
		
	def mouseMoved(self, evt):
	    pos = evt[0]  ## using signal proxy turns original arguments into a tuple
	    if self.parsed_data_list:
		    if self.graph.sceneBoundingRect().contains(pos):
		        mousePoint = self.vb.mapSceneToView(pos)
		        self.index = int(mousePoint.x())
		        if (self.data_download_done == 1 or self.data_load_from_file_done == 1) and self.cursor_trigger == 0:
		        	xposline = int(mousePoint.x()/self.record_sampling_time)

		        	try:
		        		yposline = self.parsed_data_list[self.current_row][xposline]
		        	except:
		        		pass
		        	self.vLine.setPos(mousePoint.x())
		        	try:
		        		#f(x) = f(x1)+(x-x1)*((f(x2)-f(x1))/(x2-x1)) 
		        		y_interp = 0
		        		if xposline >= 0 and xposline != (len(self.parsed_data_list[self.current_row])-1):
		        			y_interp = self.parsed_data_list[self.current_row][xposline] + (mousePoint.x() - (xposline)*self.record_sampling_time)*((self.parsed_data_list[self.current_row][xposline+1]-self.parsed_data_list[self.current_row][xposline])/(self.record_sampling_time))
		        		#self.hLine.setPos(self.parsed_data_list[self.current_row][xposline])
		        		self.hLine.setPos(y_interp)
		        	except Exception:
		        		pass
		        		#traceback.print_exc()
		        	#self.label_cord.setText("X pos: {:03d} Y pos: {:04d} Time: {:0.2f}sec".format(self.xpos, self.ypos, self.xpos*self.record_sampling_time))

	def on_captured(self):
		sss_clear = 0
		ss_clear = 0
		mm_clear = 0
		hh_clear = 0
		try:
			sss_clear = int((((self.records_header_list[self.current_row][28]<<8)|self.records_header_list[self.current_row][29])/256)*1000)
			print("sss clear: {}".format(sss_clear))
			ss_clear = self.records_header_list[self.current_row][27]
			print("ss clear: {}".format(ss_clear))
			mm_clear = self.records_header_list[self.current_row][25]
			print("mm clear: {}".format(mm_clear))
			hh_clear = self.records_header_list[self.current_row][23]
			print("xposition: {}".format(self.xpos))
			sss = int((sss_clear + self.xpos*5)%1000)
			print("sss: {}".format(sss))
			ss = int((sss_clear + self.xpos*5)/1000) + ss_clear
			print("ss: {}".format(ss))
			mm = int((ss/60)) + mm_clear
			ss = int(ss%60)
			hh = int(mm/60) + hh_clear
			mm = int(mm%60)
			hh = int(hh%24)

			utc_time_str = "{:02d}:{:02d}:{:02d}.{:03d}".format(hh,mm,ss,sss)
			self.records_tool_passage_time[self.current_row] = utc_time_str
			#temp_timepos = "{:02d}:{:02d}:{:02d}.{:03d}sec".format(self.xpos*self.record_sampling_time)
			self.table_of_records.setItem(self.current_row,5,QtWidgets.QTableWidgetItem(utc_time_str))	#tool passage time
			self.table_of_records.item(self.current_row, 5).setBackground(QtGui.QColor(100,200,50))
		except:
			print("no available data")

	def closeEvent(self, event):#перехватываем событие закрытия приложения
		result = QtWidgets.QMessageBox.question(self, "Подтверждение закрытия окна", "Вы действительно хотите закрыть окно?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No )
		if result == QtWidgets.QMessageBox.Yes:
		
			self.hide()
			self.pwindow.close()
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
		
class paramWindow(QtWidgets.QWidget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self, parent)
		self.title_label = QtWidgets.QLabel("Notch Filter configure")
		self.title_label.setAlignment(QtCore.Qt.AlignHCenter)
		self.validInt = QtGui.QIntValidator(1,255)
		
		self.notch_value_label = QtWidgets.QLabel("90")
		self.notch_value_label.setAlignment(QtCore.Qt.AlignHCenter)
		self.notch_value_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		
		self.label_notch_filter_value = 90

		self.line_notch_value = QtWidgets.QLineEdit("090")#center frequency for nwa
		self.line_notch_value.setMaximumSize(100,50)
		self.line_notch_value.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		self.line_notch_value.setValidator(self.validInt)
		self.line_notch_value.setAlignment(QtCore.Qt.AlignCenter)
		self.line_notch_value.setFont(QtGui.QFont('Arial', 13))  

		self.notch_type_box = QtWidgets.QComboBox(self)#span for nwa
		self.notch_type_box.addItems(["50Hz", "60Hz"])
		self.notch_type_box.setMaximumSize(100,50)
		self.notch_type_box.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)

		self.btn_notch_set_value = QtWidgets.QPushButton("Freq+>>")
		self.btn_notch_set_value.setMaximumSize(100,50)
		self.btn_notch_set_value.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)

		self.btn_notch_set_value_down = QtWidgets.QPushButton("<<Freq-")
		self.btn_notch_set_value_down.setMaximumSize(100,50)
		self.btn_notch_set_value_down.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)

		self.btn_notch_apply = QtWidgets.QPushButton("Apply changes")
		self.btn_notch_apply.setMaximumSize(100,50)
		self.btn_notch_apply.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)

		self.vbox_notch_param = QtWidgets.QVBoxLayout()
		self.hbox_notch_param = QtWidgets.QHBoxLayout()

		self.hbox_notch_param.addWidget(self.btn_notch_set_value_down,0)
		self.hbox_notch_param.addWidget(self.notch_value_label,1)
		self.hbox_notch_param.addWidget(self.btn_notch_set_value,2)
		self.hbox_notch_param.addWidget(QtWidgets.QLabel(""),3)

		self.vbox_notch_param.addWidget(self.notch_type_box, 0)		
		self.vbox_notch_param.addLayout(self.hbox_notch_param, 1)
		#self.vbox_notch_param.addWidget(self.line_notch_value, 2)
		self.vbox_notch_param.addWidget(self.btn_notch_apply, 2)
		self.vbox_notch_param.addWidget(QtWidgets.QLabel(""),3)

		pg.setConfigOption('foreground', 'g')	
		self.graph_notch = pg.PlotWidget()
		self.graph_notch.showGrid(1,1,1)
		
		self.graph_notch.setLabel('bottom', "Time, sec")
		self.graph_notch.setMinimumSize(500,200)

		self.hbox_notch = QtWidgets.QHBoxLayout()
		self.hbox_notch.addWidget(self.graph_notch)
		self.hbox_notch.insertLayout(1,self.vbox_notch_param)
		
		self.vbox_notch = QtWidgets.QVBoxLayout()
		self.vbox_notch.insertLayout(0,self.hbox_notch)
		self.vbox_notch.insertLayout(1,self.hbox_notch)
		self.vbox_notch.insertStretch(2,0)

		self.setLayout(self.vbox_notch)

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
	ex.setWindowTitle("Quantilini")
	app.setStyle('Fusion')
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
	