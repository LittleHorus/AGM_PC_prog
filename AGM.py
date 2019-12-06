#!/usr/bin/python3
# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
import pyqtgraph as pg 
import numpy as np
import serial
import os
from time import gmtime, strftime
import traceback

__version__ = '0.2beta'

class CommonWindow(QtWidgets.QWidget):
	"""Класс основного окна программы"""
	
	def __init__(self, parent = None):
		QtWidgets.QWidget.__init__(self, parent)

		self.data = [2021,2025,2017,2018,2023,2026,2035,2058,2082,2134,2169,2224,2151,2113,2042,2021,2021,2021,2021,2021,2021,2021,2021,2021]#test data value for plot
		
		#pg.plot(data)
		
		#self.label = QtWidgets.QLabel("<b>S21</b> measure only regime")
		#self.label.setAlignment(QtCore.Qt.AlignHCenter)
		self.previous_row = 0
		self.current_row = -1
		self.record_number = 1
		self.count = 0
		#pg.setConfigOption('background', 'd')
		pg.setConfigOption('foreground', 'g')	
		self.graph = pg.PlotWidget()
		self.graph.showGrid(1,1,1)
		
		self.graph.setMinimumSize(500,200)
		self.readblock = 0
		self.previous_agm_serial_number = "1"
		#m = PlotCanvas(self, width = 5, height = 4)
		#m.move(320,20)
		#self.show()
		#r1 = PlotCanvas_onePlot(self, width = 5, height = 4)
		#r1.move(800,20)
		#self.show()
		
		#self.graph.plot(data, pen = pg.mkPen('g', width = 4), symbol = 'o', title = "Record №{}".format(self.record_number))
		#data = [2021,2025,2017,2018,2023,2026,2035,2058,2082,2134,2169,2224,2151,2113,2042,2021,2021,2021,2021,2021,2021,2021,2021,2021]#test data value for plot
		
			
		self.btnStartMeas = QtWidgets.QPushButton("Start &Measurements")
		#self.btnStartMeas.setIcon(QtGui.QIcon("icon.png"))
		self.btnInterruptMeas = QtWidgets.QPushButton("Interrupt process")

		
		self.ComPort = str
		self.comport_combo = QtWidgets.QComboBox()
		self.comport_combo.addItems([""])
		self.comport_combo.addItems(["Refresh"])
		self.comport_combo.activated[str].connect(self.on_activated_com_list)
		self.comport_combo.activated[str].connect(self.ComPort)

		
		vertical_size = 30
		horizontal_size = 80
		
		self.onlyInt = QtGui.QIntValidator(1,1000)
		#self.LineEdit.setValidator(self.onlyInt)
		
		
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
		
		
		self.agm_serial_number = QtWidgets.QLineEdit("1")#center frequency for nwa
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
		horizontal_size = 80
		
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
		self.table_of_records.setColumnCount(5)
		self.table_of_records.setMinimumSize(320,200)
		self.table_of_records.setMaximumSize(320,700)
		self.table_of_records.setRowCount(10)
		self.table_of_records.setHorizontalHeaderLabels(["	Date  ", "	Time  ","Signal\nType","   GPS	 ", "Recording\nduration"])
		self.table_of_records.horizontalHeaderItem(0).setTextAlignment(QtCore.Qt.AlignCenter)
		self.table_of_records.horizontalHeaderItem(1).setTextAlignment(QtCore.Qt.AlignCenter)
		self.table_of_records.horizontalHeaderItem(2).setTextAlignment(QtCore.Qt.AlignCenter)
		self.table_of_records.horizontalHeaderItem(3).setTextAlignment(QtCore.Qt.AlignCenter)
		self.table_of_records.horizontalHeaderItem(4).setTextAlignment(QtCore.Qt.AlignCenter)
		#self.table_of_records.setColumnWidth(2, 80)
		self.table_of_records.horizontalHeader().setStretchLastSection(True)
		
		#data
		self.table_of_records.setItem(0,0,QtWidgets.QTableWidgetItem("06.12.19"))
		self.table_of_records.setItem(0,1,QtWidgets.QTableWidgetItem("13:05:22"))
		self.table_of_records.setItem(0,2,QtWidgets.QTableWidgetItem("Mag"))
		self.table_of_records.setItem(0,3,QtWidgets.QTableWidgetItem("54,320N\n82,642E"))
		self.table_of_records.setItem(0,4,QtWidgets.QTableWidgetItem("2sec"))

		self.table_of_records.setItem(1,0,QtWidgets.QTableWidgetItem("06.12.19"))
		self.table_of_records.setItem(1,1,QtWidgets.QTableWidgetItem("13:07:22"))
		self.table_of_records.setItem(1,2,QtWidgets.QTableWidgetItem("Mag"))
		self.table_of_records.setItem(1,3,QtWidgets.QTableWidgetItem("54,320N\n82,642E"))
		self.table_of_records.setItem(1,4,QtWidgets.QTableWidgetItem("13sec"))
		
		#self.table_of_records.setItem(1,0,QtWidgets.QTableWidgetItem("18.11.19"))
		#self.table_of_records.setItem(1,1,QtWidgets.QTableWidgetItem("21:59:22"))
		#self.table_of_records.setItem(1,2,QtWidgets.QTableWidgetItem("Mag"))
		#self.table_of_records.setItem(1,3,QtWidgets.QTableWidgetItem("54,575N\n82,579E"))
		#self.table_of_records.setItem(1,4,QtWidgets.QTableWidgetItem("15sec"))
		
		#self.table_of_records.setItem(2,0,QtWidgets.QTableWidgetItem("18.11.19"))
		#self.table_of_records.setItem(2,1,QtWidgets.QTableWidgetItem("22:03:39"))
		#self.table_of_records.setItem(2,2,QtWidgets.QTableWidgetItem("Mag"))
		#self.table_of_records.setItem(2,3,QtWidgets.QTableWidgetItem("54,575N\n82,579E"))		
		#self.table_of_records.setItem(2,4,QtWidgets.QTableWidgetItem("49sec"))
		
		self.table_of_records.resizeColumnsToContents()
		self.table_of_records.setColumnWidth(4,40)
		
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
		
		
		self.btn_load = QtWidgets.QPushButton("&Load")
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
		
		self.btn_clear = QtWidgets.QPushButton("Clear")
		self.btn_clear.setMaximumSize(horizontal_size,vertical_size)
		self.btn_clear.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)

		
		self.grid = QtWidgets.QGridLayout()
		self.grid_2 = QtWidgets.QGridLayout()
		self.grid_3 = QtWidgets.QGridLayout()
		
		
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
		

		
		self.grid.addWidget(self.agm_filterbox,3,1)
		self.grid.addWidget(self.agm_filter_label,3,0,alignment = QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)		
		#self.grid.addWidget(self.btn_pause,2,1)
		
		#self.grid_2.addWidget(self.agm_recordbox,0,1)#
		#self.grid_2.addWidget(self.agm_recordbutton,0,0)#		
		self.grid_2.addWidget(QtWidgets.QLabel(""),6,0)
		self.grid_2.addWidget(QtWidgets.QLabel(""),6,1)
		self.grid_2.addWidget(QtWidgets.QLabel(""),6,2)
		self.grid_2.addWidget(QtWidgets.QLabel(""),6,3)


		self.grid.addWidget(QtWidgets.QLabel(""),6,0)
		self.grid.addWidget(QtWidgets.QLabel(""),6,1)
		self.grid.addWidget(QtWidgets.QLabel(""),6,2)
		self.grid.addWidget(QtWidgets.QLabel(""),6,3)
		
		self.grid.addWidget(self.bar,5,0,1,5)
		
		self.grid_3.addWidget(self.table_of_records,0,0)
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
		self.vbox_1.insertLayout(2,self.grid_3)
		self.vbox_1.addWidget(self.agm_readblock)
		self.vbox_1.insertStretch(3,0)
		#self.vbox_1.insertLayout(1,self.form)
		#self.setLayout(self.grid)
		
		self.hbox = QtWidgets.QHBoxLayout()
		self.hbox.addWidget(self.graph)
		#self.hbox.addWidget(self.m)
		self.hbox.insertLayout(0,self.vbox_1)
	
		self.hbox_upper = QtWidgets.QHBoxLayout()

		self.hbox_upper.insertSpacing(2,500)
		self.hbox_upper.insertStretch(1,0)
		self.hbox_upper.addSpacing(200)
		
		self.vbox = QtWidgets.QVBoxLayout()
		#self.vbox.addWidget(self.label)		
		#self.vbox.insertLayout(0,self.hbox1)
		self.vbox.insertLayout(0,self.hbox)
		self.vbox.insertLayout(0,self.hbox_upper)
		self.setLayout(self.vbox)
		

		#self.vbox.addLayout(self.hbox)
		#self.vbox.insertLayout(0,self.hbox)
		#self.vbox.insertLayout(0,self.grid_param)
		#self.vbox.setSpacing(10)
		
		#self.setLayout(self.vbox)

		self.btn_load.setDisabled(True)
		self.btn_save.setDisabled(True)
		self.btn_clear.setDisabled(True)
		self.agm_serial_number.setDisabled(True)
		self.agm_filterbox.setDisabled(True)
		self.agm_utc.setDisabled(True)
		
		self.meas_thread = evThread()
		
		
		self.btn_visa_connect.clicked.connect(self.on_connected)
		self.btn_visa_connect.clicked.connect(self.on_get_current_path)
		self.btn_visa_disconnect.clicked.connect(self.on_disconnected)
		self.btn_save.clicked.connect(self.on_save_to_file)
		
		self.agm_serial_number.editingFinished.connect(self.on_change_serial_number)


		self.btn_load.clicked.connect(self.on_start_load)
		#self.meas_thread.started.connect(self.on_meas_started)
		self.meas_thread.finished.connect(self.on_meas_completed)
		#self.meas_thread.status_signal.connect(self.on_status_text_change, QtCore.Qt.QueuedConnection)
		#self.meas_thread.dataplot.connect(self.graph.plot, QtCore.Qt.QueuedConnection)
		self.meas_thread.progress.connect(self.on_progress_go,QtCore.Qt.QueuedConnection)
		
		self.btn_clear.clicked.connect(self.on_clear)
		#self.pwindow = paramWindow()
		#self.btnSetCF.clicked.connect(self.on_choose_param)
		
		#self.agm_recordbutton.clicked.connect(self.on_display_record)
		self.table_of_records.itemClicked.connect(self.on_change_table_item)
		
		self.agm_filterbox.activated.connect(self.on_change_notch_filter)
		self.agm_utc.activated.connect(self.on_change_utc_timezone)
		#self.comport_combo.activated.connect(self.on_activated_com_list)
	def on_connected(self):
		try:
			self.ser = serial.Serial(self.ComPort, baudrate=115200, bytesize=serial.EIGHTBITS,
									 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout = 0.5)
			
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
		self.ser.close()
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
		self.meas_thread.start()
		
		self.ser.write(bytearray.fromhex('7f aa 01 01 00 00'))
		self.read_mcu()
		#self.data = self.readblock = self.ser.read(2048)
	
		#self.agm_readblock.setText(self.readblock.decode("utf-8"))
		#self.ser.read()
	def data_processing(self, data_from_agm):
		pass
			
	def on_get_current_path(self):
		print(os.path.dirname(os.path.abspath(__file__)))	
		
	def on_save_to_file(self):
		#self.read_mcu()
		self.data_to_file(strftime("%Y-%m-%d_%Hh%Mm%Ss", gmtime()), self.data)	

	def data_to_file(self, name = "agm_data", agm_data=[0,0]):
		filename = "{}\\agm_{}.dat".format(os.path.dirname(os.path.abspath(__file__)),name)
		try:

			np.savetxt(filename, agm_data, delimiter = ',')
			print("saved")
		except Exception:
			traceback.print_exc()


	def read_mcu(self):

		try:
			ba = self.ser.read(2048)#mcu send fixed size packet
			parse_byte_list = list()
			for i in range(len(ba)):
				parse_byte_list.append(int(ba[i]))

			#string_for_label = ''
			string_for_label = [f'0x{i:02X}' for i in parse_byte_list]


			print(string_for_label)
			self.data = parse_byte_list
			#self.com_read_label.setText(str(string_for_label))
			#self.com_read_label.adjustSize()			

		except:
			print("Unexpected error")


		
	def on_meas_completed(self):
		self.btn_load.setDisabled(False)
		self.btn_save.setDisabled(False)
		self.btn_clear.setDisabled(False)		
		#self.btn_save.setDisable(False)
		
	def on_save(self):
		pass
	def on_interrupted(self):
		self.meas_thread.running = False
		
	def on_display_record(self):
		data = [2018,2025,2017,2029,2022,2026,2035,2058,2082,2134,2169,2224,2151,2147, 2148, 2145, 2140, 2134,2113,2042,2021,2021,2024,2021,2021,2016,2013,2007,2001,2002,2001,2001,2001,2001,2001,2001,2001,2001,2001,2001,2001,2001,2001]#test data value for plot
		for i in range(len(data)):
			data += np.random.normal(0,1,len(data))
		self.graph.clear()
		self.record_number = self.current_row + 1
		self.graph.plot(data, pen = pg.mkPen('g', width = 4), symbol = 't', title = "Record №{}".format(self.record_number))
		self.graph.showGrid(1,1,1)
	
	def on_change_table_item(self, item):
		self.previous_row = self.current_row
		self.current_row = item.row()
		for j in range(5):
			self.table_of_records.item(self.current_row, j).setBackground(QtGui.QColor(100,200,50))
			if self.previous_row != -1:
				self.table_of_records.item(self.previous_row, j).setBackground(QtGui.QColor(255,255,255))
		if	self.current_row != self.previous_row:
			self.on_display_record()
		
		

	
		
	def closeEvent(self, event):#перехватываем событие закрытия приложения
		result = QtWidgets.QMessageBox.question(self, "Подтверждение закрытия окна", "Вы действительно хотите закрыть окно?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No )
		if result == QtWidgets.QMessageBox.Yes:
		
			self.hide()
			self.meas_thread.running = False
			self.meas_thread.wait(5000)#ms
			event.accept()
		else:
			event.ignore()
		


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
		

if __name__ == '__main__':
	import sys
	import time, math
	
	app =QtWidgets.QApplication(sys.argv)
	ex = CommonWindow()
	ex.setFont(QtGui.QFont('Times', 10, QtGui.QFont.Bold))
	ex.setWindowTitle("AGM Viewer")
	ex.comport_combo.addItems(serial_ports())
	#ex.setFixedSize(500,400)
	#ex.resize(300,200)
	ex.adjustSize()
	#ico = QtGui.QIcon("icon.png")
	#ex.setWindowIcon(ico)#icon for window only
	#app.setWindowIcon(ico)#icon for application

	
	ex.show()
	sys.exit(app.exec_())#run the cycle of processing the events
	