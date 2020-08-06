#!/usr/bin/python3
# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt
import pyqtgraph as pg 
import numpy as np
import serial
import os
from time import gmtime, strftime
import time
import traceback
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point

__version__ = '0.3beta'

class CommonWindow(QtWidgets.QWidget):
	"""Класс основного окна программы"""
	
	def __init__(self, parent = None):
		QtWidgets.QMainWindow.__init__(self, parent)

		#widget = QtWidgets.QWidget(self)
		#self.setCentralWidget(widget)

		self.data = [0]#test data value for plot
		self.parsed_data_list = list()
		self.records_header_list = list()
		self.records_tool_passage_time = list()
		self.records_description = list()
		self.data_download_done = 0
		self.data_load_from_file_done = 0
		#pg.plot(data)
		self.record_sampling_time = 0.005
		#self.label = QtWidgets.QLabel("<b>S21</b> measure only regime")
		#self.label.setAlignment(QtCore.Qt.AlignHCenter)
		self.first_load = 0
		self.previous_row = 0
		self.current_row = -1
		self.record_number = 1
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
		self.readblock = 0
		self.previous_agm_serial_number = "1"

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
		
		self.agm_utc = QtWidgets.QComboBox(self)#span for nwa
		self.agm_utc.addItems(["UTC+0", "UTC+1", "UTC+2", "UTC+3","UTC+4", "UTC+5","UTC+6","UTC+7","UTC+8", "UTC+9","UTC+10", "UTC+11", "UTC+12"])
		self.agm_utc.setMaximumSize(horizontal_size,vertical_size)
		self.agm_utc.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)

		#vertical_size = 30
		#horizontal_size = 200		
		#self.agm_recordbox = QtWidgets.QComboBox(self)#span for nwa
		#self.agm_recordbox.addItems(["№1  16.11.19	 10:22:15", "№2	 16.11.19  12:05:02", "№3  16.11.19	 17:41:55"])
		#self.agm_recordbox.setMaximumSize(horizontal_size,vertical_size)
		#self.agm_recordbox.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)	
		
		vertical_size = 30
		horizontal_size = 90
		
		self.agm_recordbutton = QtWidgets.QPushButton("Display \nrecord")
		self.agm_recordbutton.setMaximumSize(horizontal_size,vertical_size)
		self.agm_recordbutton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)#Fixed

		self.agm_filterbox = QtWidgets.QComboBox(self)#span for nwa
		self.agm_filterbox.addItems(["50Hz", "60Hz"])
		self.agm_filterbox.setMaximumSize(horizontal_size,vertical_size)
		self.agm_filterbox.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)		
		self.agm_filter_label = QtWidgets.QLabel("Filter:")
		self.agm_filter_label.setMaximumSize(horizontal_size,vertical_size)
		self.agm_filter_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Maximum)		
		
		#self.agm_filterapply = QtWidgets.QPushButton("Set\nFilter")
		#self.agm_filterapply.setMaximumSize(horizontal_size,vertical_size)
		#self.agm_filterapply.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)#Fixed
		
		self.agm_serial_number_label = QtWidgets.QLabel("AGM №:")
		self.agm_serial_number_label.setMaximumSize(horizontal_size,vertical_size)
		self.agm_serial_number_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Maximum)#Fixed
		self.agm_utc_label = QtWidgets.QLabel("Timezone:")
		self.agm_utc_label.setMaximumSize(horizontal_size,vertical_size)
		self.agm_utc_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Maximum)	

		
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
		self.table_of_records.setHorizontalHeaderLabels(["	Date  ", "	Time  ","Signal\nType","   GPS	 ", "Recording\nduration", "Tool passage\ntime", "Description"])
		self.table_of_records.horizontalHeaderItem(0).setTextAlignment(QtCore.Qt.AlignCenter)
		self.table_of_records.horizontalHeaderItem(1).setTextAlignment(QtCore.Qt.AlignCenter)
		self.table_of_records.horizontalHeaderItem(2).setTextAlignment(QtCore.Qt.AlignCenter)
		self.table_of_records.horizontalHeaderItem(3).setTextAlignment(QtCore.Qt.AlignCenter)
		self.table_of_records.horizontalHeaderItem(4).setTextAlignment(QtCore.Qt.AlignCenter)
		self.table_of_records.horizontalHeaderItem(5).setTextAlignment(QtCore.Qt.AlignCenter)
		self.table_of_records.horizontalHeaderItem(6).setTextAlignment(QtCore.Qt.AlignCenter)
		
		self.table_of_records.horizontalHeader().setStretchLastSection(False)
		
		#data
		#self.table_of_records.setItem(0,0,QtWidgets.QTableWidgetItem("06.12.19"))
		#self.table_of_records.setItem(0,1,QtWidgets.QTableWidgetItem("13:05:22"))
		#self.table_of_records.setItem(0,2,QtWidgets.QTableWidgetItem("Mag"))
		#self.table_of_records.setItem(0,3,QtWidgets.QTableWidgetItem("54,320N\n82,642E"))
		#self.table_of_records.setItem(0,4,QtWidgets.QTableWidgetItem("2sec"))
		#self.table_of_records.setItem(0,5,QtWidgets.QTableWidgetItem(""))

		
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

		#self.agm_serial_number = QtWidgets.QLineEdit()
		#self.form = QtWidgets.QFormLayout()
		#self.form.addRow("Center Frequency:", self.agm_serial_number)
		#self.form.addRow("SPAN:",self.agm_utc)
		#self.form.addRow("NOP:",self.line_nop)
		
		
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
		
		self.btn_clear = QtWidgets.QPushButton("Erase")
		self.btn_clear.setMaximumSize(horizontal_size,vertical_size)
		self.btn_clear.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)


		self.btn_notch_open_window = QtWidgets.QPushButton("Notch Filter")
		self.btn_notch_open_window.setMaximumSize(horizontal_size,vertical_size)
		self.btn_notch_open_window.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)	

		self.btn_gsm_open_window = QtWidgets.QPushButton("GSM")
		self.btn_gsm_open_window.setMaximumSize(horizontal_size,vertical_size)
		self.btn_gsm_open_window.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)	


		self.grid = QtWidgets.QGridLayout()
		self.grid_2 = QtWidgets.QGridLayout()
		self.grid_plot_labels = QtWidgets.QGridLayout()

		self.btn_download_raw = QtWidgets.QPushButton("Download\n Raw")
		self.btn_download_raw.setMaximumSize(horizontal_size,vertical_size)
		self.btn_download_raw.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)		
		
		self.grid.addWidget(self.label_visa_connect, 0, 0)
		self.grid.addWidget(self.comport_combo, 0, 1)
		self.grid.addWidget(self.btn_visa_connect, 0, 2)
		self.grid.addWidget(self.btn_visa_disconnect, 0, 3)

		self.grid.addWidget(self.agm_serial_number_label, 1, 0, alignment = QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
		self.grid.addWidget(self.agm_utc_label, 2, 0, alignment = QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)

		self.grid.addWidget(self.agm_serial_number, 1, 1)#, alignment = QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
		self.grid.addWidget(self.agm_utc, 2, 1)
		
		self.grid.addWidget(self.btn_load,4,0)
		#self.grid.addWidget(self.btn_stop,2,1)
		self.grid.addWidget(self.btn_save,4,1)
		self.grid.addWidget(self.btn_clear,4,2)
		self.grid.addWidget(self.btn_clear_table, 5, 1)
		self.grid.addWidget(self.btn_load_file, 5,0)

		self.grid.addWidget(self.btn_download_raw, 6,0)

		#self.grid.addWidget(self.label_set_potentiometr, 6,0,1,1)
		#self.grid.addWidget(self.btn_set_potentiometr, 6,1,1,1)
		self.grid.addWidget(self.btn_notch_open_window, 6,2,1,1)
		self.grid.addWidget(self.btn_gsm_open_window, 6,3,1,1)
			
		#self.grid_plot_labels.addWidget(self.label_cord, 0, 0)
		self.grid_plot_labels.addWidget(self.btn_cord_fixed, 0,0)
		self.grid_plot_labels.addWidget(QtWidgets.QLabel(""),0,3)
		self.grid_plot_labels.addWidget(QtWidgets.QLabel(""),0,5)
		#self.grid_plot_labels.insertStretch(0,4)
		
		self.grid.addWidget(self.agm_filterbox,3,1)
		self.grid.addWidget(self.agm_filter_label,3,0,alignment = QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)		
		#self.grid.addWidget(self.btn_pause,2,1)
		
		#self.grid_2.addWidget(self.agm_recordbox,0,1)#
		#self.grid_2.addWidget(self.agm_recordbutton,0,0)#		
		self.grid_2.addWidget(QtWidgets.QLabel(""),8,0)
		self.grid_2.addWidget(QtWidgets.QLabel(""),8,1)
		self.grid_2.addWidget(QtWidgets.QLabel(""),8,2)
		self.grid_2.addWidget(QtWidgets.QLabel(""),8,3)


		self.grid.addWidget(QtWidgets.QLabel(""),7,0)
		self.grid.addWidget(QtWidgets.QLabel(""),7,1)
		self.grid.addWidget(QtWidgets.QLabel(""),7,2)
		self.grid.addWidget(QtWidgets.QLabel(""),7,3)
		
		self.grid.addWidget(self.bar,8,0,1,5)
		
		#self.grid_3.addWidget(self.table_of_records,0,0)
		#self.grid.addWidget(self.lbl_g,10,0,1,5)
		#self.grid.addWidget(self.lbl,9,0,20,10)#add picture to grid layout
		#self.grid.addWidget(QtWidgets.QLabel(""),20,25)
		#self.grid.addWidget(self.graph,5,10,5,5)#graph
		#self.grid.setSpacing(10)
		
		#self.grid_2.setHorizontalSpacing(5)
		#self.grid_2.setVerticalSpacing(5)
		#self.grid_2.setContentsMargins(5,5,5,5)
				
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
		#self.hbox_2.addWidget(QtWidgets.QLabel(""),0)
		#self.hbox_2.addWidget(QtWidgets.QLabel(""),1)
		#self.hbox_2.addWidget(QtWidgets.QLabel(""),2)
		#self.hbox_2.addWidget(self.table_of_records,1)

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
		

		#self.vbox.addLayout(self.hbox)
		#self.vbox.insertLayout(0,self.hbox)
		#self.vbox.insertLayout(0,self.grid_param)
		#self.vbox.setSpacing(10)
		
		#self.setLayout(self.vbox)

		self.btn_load.setDisabled(True)
		self.btn_save.setDisabled(True)
		self.btn_clear.setDisabled(True)
		self.btn_download_raw.setDisabled(True)
		self.agm_serial_number.setDisabled(True)
		self.agm_filterbox.setDisabled(True)
		self.agm_utc.setDisabled(True)
		self.btn_notch_open_window.setDisabled(True)
		self.meas_thread = evThread()

		self.btn_visa_connect.clicked.connect(self.on_connected)
		self.btn_visa_connect.clicked.connect(self.on_get_current_path)
		self.btn_visa_disconnect.clicked.connect(self.on_disconnected)
		self.btn_save.clicked.connect(self.on_save_to_file)
		self.btn_load_file.clicked.connect(self.on_load_from_file) 
		self.btn_clear_table.clicked.connect(self.on_clear_table)
		self.agm_serial_number.editingFinished.connect(self.on_change_serial_number)


		#self.btn_set_potentiometr.clicked.connect(self.on_set_notch_potentiometr)

		self.btn_cord_fixed.clicked.connect(self.on_captured)
		self.btn_load.clicked.connect(self.on_start_load)
		#self.meas_thread.started.connect(self.on_meas_started)
		self.meas_thread.finished.connect(self.on_meas_completed)
		#self.meas_thread.status_signal.connect(self.on_status_text_change, QtCore.Qt.QueuedConnection)
		#self.meas_thread.dataplot.connect(self.graph.plot, QtCore.Qt.QueuedConnection)
		self.meas_thread.progress.connect(self.on_progress_go,QtCore.Qt.QueuedConnection)
		
		self.btn_clear.clicked.connect(self.on_clear)

		self.pwindow = paramWindow()
		self.gsmwindow = paramWindow_GSM()

		self.gsmwindow.btn_gsm_apply.clicked.connect(self.on_gsm_apply)
		self.btn_gsm_open_window.clicked.connect(self.on_gsm_open_window)
		self.btn_notch_open_window.clicked.connect(self.on_open_notch_window)

		self.pwindow.btn_notch_apply.clicked.connect(self.on_apply_notch_settings)
		#self.pwindow.btn_notch_set_value.clicked.connect(self.on_set_notch_potentiometr)
		self.pwindow.btn_notch_set_value_down.clicked.connect(self.on_set_notch_potentiometr_down)
		self.pwindow.btn_notch_set_value.clicked.connect(self.on_set_notch_potentiometr)
		self.pwindow.notch_type_box.currentIndexChanged.connect(self.on_notch_type_changed)
		#self.agm_recordbutton.clicked.connect(self.on_display_record)
		self.table_of_records.itemClicked.connect(self.on_change_table_item)
		self.table_of_records.itemChanged.connect(self.on_change_description)
		self.agm_filterbox.activated.connect(self.on_change_notch_filter)
		self.agm_utc.activated.connect(self.on_change_utc_timezone)
		#self.comport_combo.activated.connect(self.on_activated_com_list)
		self.btn_download_raw.clicked.connect(self.on_download_raw)
		self.proxy = pg.SignalProxy(self.graph.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
		#self.curve.sigClicked.connect(self.clicked_point)
		#self.curve.sigPointsClicked.connect(self.clicked_point)

	def on_apply_notch_settings(self):
		notch_type = self.pwindow.notch_type_box.currentIndex()
		try:
			self.ser.write(bytearray.fromhex('7f aa 01 07 {:02X} {:02X}'.format(notch_type,self.notch_int_value)))
			self.ser.read(2)
		except:
			print("apply notch settings error")

	def on_gsm_apply(self):
		self.gsmwindow.close()

	def on_gsm_open_window(self):
		self.gsmwindow.resize(200,100)
		self.gsmwindow.setWindowTitle("GSM Settings")	
	def on_open_notch_window(self):
		self.pwindow.resize(200,100)
		self.pwindow.setWindowTitle("Notch Filter")


		self.pwindow.show()
	def on_notch_type_changed(self):
		if self.pwindow.notch_type_box.currentIndex() == 0:
			self.notch_int_value = 90
			self.pwindow.notch_value_label.setText(str(self.notch_int_value))
		else:
			self.notch_int_value = 51
			self.pwindow.notch_value_label.setText(str(self.notch_int_value))

	def on_set_notch_potentiometr_down(self):
		data_to_plotting = list()
		plot_x = list()
		for i in range(20):
			plot_x.append(self.record_sampling_time*i)
		try:
			if self.notch_int_value != 0:
				self.notch_int_value -= 1#(int)(self.pwindow.line_notch_value.text())#((int)(self.label_set_potentiometr.text()))
			else:
				self.notch_int_value = 0
			#print(bytearray.fromhex('7f aa 01 02 {:02X} {:02X}'.format(adr_hi_byte, adr_lo_byte)))
			print(bytearray.fromhex('7f aa 01 06 {:02X}'.format(self.notch_int_value)))
			self.ser.write(bytearray.fromhex('7f aa 01 06 {:02X}'.format(self.notch_int_value)))
			self.pwindow.notch_value_label.setText(str(self.notch_int_value))
		except:
			print("on_set_notch_potentiometr")	
		try:

			din = self.ser.read(4)#mcu send fixed size packet
			parse_byte_list = list()

			bytes_cnt = 2*int.from_bytes(din, byteorder='big', signed = False)
			print(bytes_cnt)

			din = self.ser.read(62)#mcu send fixed size packet
			parse_byte_list = list()
			for i in range(len(din)):
				parse_byte_list.append(int(din[i]))

			#string_for_label = ''
			string_for_label = [f'0x{i:02X}' for i in parse_byte_list]
			 
			print(len(parse_byte_list), din, type(parse_byte_list[0]))



			#data_to_plotting = notch_parse(parse_byte_list)
			
			print(string_for_label)	

			for i in range(20):
				data_to_plotting.append((parse_byte_list[2*i]<<8)+(parse_byte_list[2*i+1]))	
			print(data_to_plotting)	
			self.pwindow.graph_notch.clear()
			self.pwindow.graph_notch.plot(plot_x, data_to_plotting, pen = pg.mkPen('g', width = 3), symbol = 'o', symbolSize = 10)
		except:
			print("on_set_notch_potentiometr part 2")			

	def on_set_notch_potentiometr(self):
		data_to_plotting = list()
		plot_x = list()
		for i in range(20):
			plot_x.append(self.record_sampling_time*i)
		try:
			self.notch_int_value += 1#(int)(self.pwindow.line_notch_value.text())#((int)(self.label_set_potentiometr.text()))
			if self.notch_int_value > 255:
				self.notch_int_value = 255
			
			#print(bytearray.fromhex('7f aa 01 02 {:02X} {:02X}'.format(adr_hi_byte, adr_lo_byte)))
			print(bytearray.fromhex('7f aa 01 06 {:02X}'.format(self.notch_int_value)))
			self.ser.write(bytearray.fromhex('7f aa 01 06 {:02X}'.format(self.notch_int_value)))
			self.pwindow.notch_value_label.setText(str(self.notch_int_value))
		except:
			print("on_set_notch_potentiometr")	
		try:

			din = self.ser.read(4)#mcu send fixed size packet
			parse_byte_list = list()

			bytes_cnt = 2*int.from_bytes(din, byteorder='big', signed = False)
			print(bytes_cnt)

			din = self.ser.read(62)#mcu send fixed size packet
			parse_byte_list = list()
			for i in range(len(din)):
				parse_byte_list.append(int(din[i]))

			#string_for_label = ''
			string_for_label = [f'0x{i:02X}' for i in parse_byte_list]
			 
			print(len(parse_byte_list), din, type(parse_byte_list[0]))



			#data_to_plotting = notch_parse(parse_byte_list)
			
			print(string_for_label)	

			for i in range(20):
				data_to_plotting.append((parse_byte_list[2*i]<<8)+(parse_byte_list[2*i+1]))	
			print(data_to_plotting)	
			self.pwindow.graph_notch.clear()
			self.pwindow.graph_notch.plot(plot_x, data_to_plotting, pen = pg.mkPen('g', width = 3), symbol = 'o', symbolSize = 10)
		except:
			print("on_set_notch_potentiometr part 2")	
	def notch_parse(self, data_input):
		data_out = list()
		try:
			for i in range(20):
				data_out.append((data_input[2*i]<<8)|(data_input[2*i+1]))
		except:
			print("parse error")
		return data_out

	def on_connected(self):
		try:
			self.ser = serial.Serial(self.ComPort, baudrate=115200, bytesize=serial.EIGHTBITS,
									 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout = 1.5)
			
			self.ser.isOpen()  # try to open port
			print("Connected to {}".format(self.ComPort))

			self.btn_visa_connect.setDisabled(True)
			self.btn_visa_disconnect.setDisabled(False)
			self.btn_load.setDisabled(False)
			#self.btn_save.setDisabled(True)
			self.btn_clear.setDisabled(False)
			self.agm_serial_number.setDisabled(False)
			self.agm_filterbox.setDisabled(False)
			self.agm_utc.setDisabled(False)
			self.btn_notch_open_window.setDisabled(False)
			self.btn_download_raw.setDisabled(False)
		except IOError:
			#pass
			print("Port already open another programm")
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
	def on_change_notch_filter(self):
		if self.agm_filterbox.currentText() == "50Hz":
			adr_byte = 0
			print(bytearray.fromhex('7f aa 01 04 {:02X} 00'.format(adr_byte)))
			self.ser.write(bytearray.fromhex('7f aa 01 04 {:02X} 00'.format(adr_byte)))
		if 	self.agm_filterbox.currentText() == "60Hz":		
			adr_byte = 1
			print(bytearray.fromhex('7f aa 01 04 {:02X} 00'.format(adr_byte)))
			self.ser.write(bytearray.fromhex('7f aa 01 04 {:02X} 00'.format(adr_byte)))
	def on_change_utc_timezone(self):
		adr_byte = self.agm_utc.currentIndex()
		print(bytearray.fromhex('7f aa 01 05 {:02X} 00'.format(adr_byte)))
		print("MCU UTC timezone not realized")
		self.ser.write(bytearray.fromhex('7f aa 01 05 {:02X} 00'.format(adr_byte)))
		
	def on_disconnected(self):
		self.btn_visa_connect.setDisabled(False)
		self.btn_visa_disconnect.setDisabled(True)	
		self.btn_load.setDisabled(True)
		self.btn_save.setDisabled(True)
		self.btn_clear.setDisabled(True)
		self.agm_serial_number.setDisabled(True)
		self.agm_filterbox.setDisabled(True)
		self.agm_utc.setDisabled(True)	
		self.btn_notch_open_window.setDisabled(True)
		self.btn_download_raw.setDisabled(True)
		try:	
			self.ser.close()
		except:
			pass
		self.first_load = 0
		print("Disconnected")
				
	def on_activated_com_list(self, str):
		#self.label.setText(str)
		if self.comport_combo.currentText() == "":
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
		#self.label.setText("measure started")
		#self.graph.clear()
		self.bar.setValue(0)
		self.graph.clear()
		self.on_clear_table()
		self.meas_thread.start()
		'''if self.first_load == 0:
			self.ser.write(bytearray.fromhex('7f aa 01 01 00 00'))
			try:
				self.ser.read(2)
				self.first_load = 1
				time.sleep(0.3)

			except:
				print("first load failed")
				'''
		#if self.first_load == 1:
		#self.ser.write(bytearray.fromhex('7f aa 01 01 00 00'))
		#self.read_mcu()
		self.read_mcu_packed()
		#self.data = self.readblock = self.ser.read(2048)
	
		#self.agm_readblock.setText(self.readblock.decode("utf-8"))
		#self.ser.read()


	def header_processing(self, current_index,  header, record_length):
		utc_date_str = "{:02d}.{:02d}.{:02d}".format(header[17],header[19],header[21])
		utc_time_str = "{:02d}:{:02d}:{:02d}.{:03d}".format(header[23],header[25],header[27],(header[28]<<8)|header[29])
		if header[3] == 0:
			utc_signal_type_str = "MAG"
		if header[3] == 1:
			utc_signal_type_str = "LF"
		if header[3] == 2:
			utc_signal_type_str = "MAG+LF"

		record_len = "{:.2f}sec".format(record_length*self.record_sampling_time)
		gps_latitude_dir = "N"
		longitude_dir = "E"
		if header[9] == 0:
			gps_latitude_dir = "N"
		if header[9] == 1:
			gps_latitude_dir = "S"
		if header[15] == 0:
			longitude_dir = "E"
		if header[15] == 1:
			longitude_dir = "W"
		latitude_hi = header[4]
		#print(type(latitude_hi), type(header[5]))

		latitude_hi = (latitude_hi<<8)  | header[5]
		latitude_lo = header[6]
		latitude_lo = (latitude_lo<<8) | header[7]	

		longitude_hi = 	header[10]
		longitude_hi = (longitude_hi<<8) | header[11]
		longitude_lo = 	header[12]
		longitude_lo = (longitude_lo<<8) | header[13]
		#self.records_tool_passage_time
		#gps_str = "{:03d},{:03d}{}".format(latitude_hi,latitude_lo,gps_latitude_dir)
		gps_str = "{:03d},{:03d}{}     {:03d},{:03d}{}".format(latitude_hi, latitude_lo, gps_latitude_dir, longitude_hi, longitude_lo, longitude_dir)	
		print(self.records_tool_passage_time[current_index], type(self.records_tool_passage_time[current_index]))
		if type(self.records_tool_passage_time[current_index]) == str:
			tool_str = self.records_tool_passage_time[current_index]
		else:
			tool_str = ""
		if type(self.records_description[current_index]) == str:
			description_str = self.records_description[current_index]
		else:
			description_str = ""
			

		try:
			self.table_of_records.setItem(current_index,0,QtWidgets.QTableWidgetItem(utc_date_str))#full date 06.12.19
			self.table_of_records.item(current_index, 0).setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
			self.table_of_records.setItem(current_index,1,QtWidgets.QTableWidgetItem(utc_time_str))#full time 13:07:22
			self.table_of_records.item(current_index, 1).setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
			self.table_of_records.setItem(current_index,2,QtWidgets.QTableWidgetItem(utc_signal_type_str))#Type of signal Mag
			self.table_of_records.item(current_index, 2).setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
			self.table_of_records.setItem(current_index,3,QtWidgets.QTableWidgetItem(gps_str))# GPS data 54,320N\n82,642E
			self.table_of_records.item(current_index, 3).setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter) 
			self.table_of_records.setItem(current_index,4,QtWidgets.QTableWidgetItem(record_len))#record time
			self.table_of_records.item(current_index, 4).setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
			self.table_of_records.setItem(current_index,5,QtWidgets.QTableWidgetItem(tool_str))	#tool passage time
			self.table_of_records.item(current_index, 5).setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
			self.table_of_records.setItem(current_index,6,QtWidgets.QTableWidgetItem(description_str))	#tool passage time
			self.table_of_records.item(current_index, 6).setTextAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)			
		except:
			print("table setItem error")

	def data_processing(self, data_from_agm):
		#self.record_index_list = list()
		self.parsed_data_list = list()
		self.records_tool_passage_time = list()
		self.records_header_list = list()
		self.records_description = list()

		record_index_list = list()
		records_parse_data = list()

		for i in range(len(data_from_agm)):
			if i < (len(data_from_agm) - 3):
				if data_from_agm[i] == 0x00 and data_from_agm[i+1] == 0x00 and data_from_agm[i+2] == 0xaa and data_from_agm[i+3] == 0x55:
					print("captured new record at index - {}".format(i))
					record_index_list.append(i)
		print(record_index_list)

		for i in range(len(record_index_list)):
			temp_list = list()
			if i != (len(record_index_list)-1):
				data_len = record_index_list[i+1] - record_index_list[i]
			if i == (len(record_index_list)-1):
				data_len = len(data_from_agm) - record_index_list[i]
			for j in range(data_len-4):#last 2 bytes - 0000 start of packet
				temp_list.append(data_from_agm[record_index_list[i]+j+4])
			records_parse_data.append(temp_list)
		print(len(records_parse_data))

		for i in range(len(records_parse_data)):
			header = records_parse_data[i][:34]
			self.records_header_list.append(header)

			self.records_tool_passage_time.append(0)#total length equal to records cnt
			self.records_description.append(0)

			self.header_processing(i, header, int((len(records_parse_data[i])-34)/2) )
			temp_data_unparsed = records_parse_data[i][34:]
			temp_data = list()
			for j in range(int(len(temp_data_unparsed)/2)):
				if ((temp_data_unparsed[2*j]<<8)|(temp_data_unparsed[2*j+1])) != 0x7faa:
					if (j>2) and (j<(int(len(temp_data_unparsed)/2)-2)):
						if (((temp_data_unparsed[2*j]<<8)|(temp_data_unparsed[2*j+1])) != 0x00) and (((temp_data_unparsed[2*j+2]<<8)|(temp_data_unparsed[2*j+3])) != 0x00) and (((temp_data_unparsed[2*j-2]<<8)|(temp_data_unparsed[2*j+1-2])) != 0x00):
							temp_data.append((temp_data_unparsed[2*j]<<8)|(temp_data_unparsed[2*j+1]))
					else:
						temp_data.append((temp_data_unparsed[2*j]<<8)|(temp_data_unparsed[2*j+1]))

			self.parsed_data_list.append(temp_data)
		print(len(self.parsed_data_list))
		print(self.records_header_list)
		print(self.parsed_data_list[0])
		self.data_download_done = 1
			
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
	def on_download_raw(self):
		print("1")
		self.read_mcu_rawdata()
		#btn_download_raw

	def on_load_from_file(self):
		fname = QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]
		if fname:
			try:
				data_dict = np.load(fname, allow_pickle=True)
				#print(data_dict)
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
	def read_mcu(self):

		try:
			ba = self.ser.read(4)#mcu send fixed size packet
			parse_byte_list = list()
			print(ba)
			bytes_cnt = 2*int.from_bytes(ba, byteorder='big', signed = False)
			print(bytes_cnt)

			ba = self.ser.read(bytes_cnt)#mcu send fixed size packet
			parse_byte_list = list()
			for i in range(len(ba)):
				parse_byte_list.append(int(ba[i]))

			#string_for_label = ''
			string_for_label = [f'0x{i:02X}' for i in parse_byte_list]


			print(string_for_label)
			#self.data = parse_byte_list
			if ba != '':
				self.bar.setValue(100)
			if ba == b'':
				print("no data read")
			#self.com_read_label.setText(str(string_for_label))
			#self.com_read_label.adjustSize()			
			self.data_processing(ba)
		except:
			print("Unexpected error, read mcu func")
	def read_mcu_packed(self):
		data_to_plotting = list()
		parse_byte_list = list()


		try:
			self.ser.write(bytearray.fromhex('7f aa 01 08 00'))
			time.sleep(0.1)
			self.ser.read(66)
		except:
			pass
		
		self.usb_order_cnt += 1
		self.ser.write(bytearray.fromhex('7f aa 01 08 01 {:02X}'.format(self.usb_order_cnt)))
		time.sleep(0.1)
		cmdDataIn = self.ser.read(66)
		print(cmdDataIn)
		bytes_cnt = 2*int.from_bytes(cmdDataIn[6:10], byteorder='big', signed = False)

		#40 byte per packet
		packetCnt = bytes_cnt / 40
		barInc = 100/packetCnt


		print(bytes_cnt, packetCnt, barInc)
		self.bar.setValue(1)
		try:
			for i in range(int(packetCnt)):
				self.ser.write(bytearray.fromhex('7f aa 01 08 01 {:02X}'.format(self.usb_order_cnt)))
				time.sleep(0.1)
				din = self.ser.read(66)
				parse_byte_list.extend(din[6:46])
				self.bar.setValue((i+1)*barInc)
			print(len(parse_byte_list))
			print(parse_byte_list)	
		except:
			print("read block error")

		self.data_processing(parse_byte_list)	
	def read_mcu_rawdata(self):
		data_to_plotting = list()
		parse_byte_list = list()


		try:
			self.ser.write(bytearray.fromhex('7f aa 01 08 00'))
			time.sleep(0.1)
			self.ser.read(66)
		except:
			pass
		
		self.usb_order_cnt += 1
		self.ser.write(bytearray.fromhex('7f aa 01 08 01 {:02X}'.format(self.usb_order_cnt)))
		time.sleep(0.1)
		cmdDataIn = self.ser.read(66)
		print(cmdDataIn)
		bytes_cnt = 2*int.from_bytes(cmdDataIn[6:10], byteorder='big', signed = False)

		#40 byte per packet
		packetCnt = bytes_cnt / 40
		barInc = (100/packetCnt)+1


		print(bytes_cnt, packetCnt, barInc)
		self.bar.setValue(1)
		try:
			for i in range(int(packetCnt)):
				self.ser.write(bytearray.fromhex('7f aa 01 08 01 {:02X}'.format(self.usb_order_cnt)))
				time.sleep(0.1)
				din = self.ser.read(66)
				parse_byte_list.extend(din[6:66])
				self.bar.setValue((i+1)*barInc)
				print(din)
			print(len(parse_byte_list))
			print(parse_byte_list)	
		except:
			print("read block error")

		name = strftime("%Y-%m-%d_%Hh%Mm%Ss", gmtime())

		dict_to_save = {'data':parse_byte_list}

		dict_filename = "{}\\agm_{}.npy".format(os.path.dirname(os.path.abspath(__file__)),name)
		filename = "{}\\agm_{}.dat".format(os.path.dirname(os.path.abspath(__file__)),name)
		try:
			#for i in range(len(agm_data)):
			#	np.savetxt(filename, agm_data[i], delimiter = ',')#, fmt='%x')
				
			np.save(dict_filename, dict_to_save)
			print("saved")

		except Exception:
			traceback.print_exc()
		
		#self.data_processing(parse_byte_list)	

	def on_meas_completed(self):
		self.btn_load.setDisabled(False)
		self.btn_save.setDisabled(False)
		self.btn_clear.setDisabled(False)		
		#self.btn_save.setDisable(False)
		

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
		#print(self.xpos, self.ypos)
		try:
			sss = (self.records_header_list[self.current_row][28]<<8)|self.records_header_list[self.current_row][29]
			ss = self.records_header_list[self.current_row][27]
			mm = self.records_header_list[self.current_row][25]
			hh = self.records_header_list[self.current_row][23]

			sss = int((sss + self.xpos*5)%1000)
			ss += int((sss + self.xpos*5)/1000)
			mm += int((ss/60))
			ss = int(ss%60)
			hh += int(mm/60)
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


class paramWindow_GSM(QtWidgets.QWidget):
	def __init__(self, parent = None):
		QtGui.QWidget.__init__(self, parent)
		self.title_label = QtWidgets.QLabel("GSM settings")
		self.title_label.setAlignment(QtCore.Qt.AlignHCenter)
		self.validInt = QtGui.QIntValidator(1,255)
		
		self.gsm_mobile_number = QtWidgets.QLabel("mobile number:")
		self.gsm_mobile_number.setAlignment(QtCore.Qt.AlignHCenter)
		self.gsm_mobile_number.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		

		self.mobilenumberstring = QtWidgets.QLineEdit("+70000000000")
		self.mobilenumberstring.setMaximumSize(200,50)
		self.mobilenumberstring.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		#self.mobilenumberstring.setValidator(self.validInt)
		self.mobilenumberstring.setAlignment(QtCore.Qt.AlignCenter)
		self.mobilenumberstring.setFont(QtGui.QFont('Arial', 13))  

		self.btn_gsm_apply = QtWidgets.QPushButton("Apply")
		self.btn_gsm_apply.setMaximumSize(100,50)
		self.btn_gsm_apply.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)

		self.vbox_gsm = QtWidgets.QVBoxLayout()
		self.hbox_gsm = QtWidgets.QHBoxLayout()

		self.hbox_gsm.addWidget(self.gsm_mobile_number,0)
		self.hbox_gsm.addWidget(self.mobilenumberstring,1)
		self.hbox_gsm.addWidget(self.btn_gsm_apply,2)
		self.hbox_gsm.addWidget(QtWidgets.QLabel(""),3)

		self.hbox_gsm.insertStretch(4,0)

		self.setLayout(self.hbox_gsm)		
		
			
		
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
		

if __name__ == '__main__':
	import sys
	import time, math
	
	app =QtWidgets.QApplication(sys.argv)
	ex = CommonWindow()
	ex.setFont(QtGui.QFont('Arial', 9))#, QtGui.QFont.Bold
	ex.setWindowTitle("AGM Viewer")
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
	