#!/usr/bin/python3
# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg 
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import serial


__version__ = '0.2beta'

class CommonWindow(QtWidgets.QWidget):
	"""Класс основного окна программы"""
	
	def __init__(self, parent = None):
		QtWidgets.QWidget.__init__(self, parent)

		data = [2021,2025,2017,2018,2023,2026,2035,2058,2082,2134,2169,2224,2151,2113,2042,2021,2021,2021,2021,2021,2021,2021,2021,2021]#test data value for plot
		
		#pg.plot(data)
		
		#self.label = QtWidgets.QLabel("<b>S21</b> measure only regime")
		#self.label.setAlignment(QtCore.Qt.AlignHCenter)

		self.record_number = 1
		self.count = 0
		#pg.setConfigOption('background', 'd')
		pg.setConfigOption('foreground', 'g')	
		self.graph = pg.PlotWidget()
		self.graph.setMinimumSize(500,200)

		#m = PlotCanvas(self, width = 5, height = 4)
		#m.move(320,20)
		#self.show()
		#r1 = PlotCanvas_onePlot(self, width = 5, height = 4)
		#r1.move(800,20)
		#self.show()
		
		self.graph.plot(data, pen = pg.mkPen('g', width = 4), symbol = 'o', title = "Record №{}".format(self.record_number))
		#data = [2021,2025,2017,2018,2023,2026,2035,2058,2082,2134,2169,2224,2151,2113,2042,2021,2021,2021,2021,2021,2021,2021,2021,2021]#test data value for plot
		
			
		self.btnStartMeas = QtWidgets.QPushButton("Start &Measurements")
		#self.btnStartMeas.setIcon(QtGui.QIcon("icon.png"))
		self.btnInterruptMeas = QtWidgets.QPushButton("Interrupt process")

		
		self.ComPort = str
		self.comport_combo = QtWidgets.QComboBox()
		self.comport_combo.addItems([""])
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
		
		self.agm_serial_number = QtWidgets.QLineEdit("1")#center frequency for nwa
		self.agm_serial_number.setMaximumSize(horizontal_size,vertical_size)
		self.agm_serial_number.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		self.agm_serial_number.setValidator(self.onlyInt)
		self.agm_serial_number.setAlignment(QtCore.Qt.AlignCenter)
		
		self.agm_utc = QtWidgets.QComboBox(self)#span for nwa
		self.agm_utc.addItems(["UTC+0", "UTC+1", "UTC+2", "UTC+3","UTC+4", "UTC+5","UTC+6","UTC+7","UTC+8", "UTC+9","UTC+10", "UTC+11", "UTC+12"])
		self.agm_utc.setMaximumSize(horizontal_size,vertical_size)
		self.agm_utc.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)

		vertical_size = 30
		horizontal_size = 200		
		self.agm_recordbox = QtWidgets.QComboBox(self)#span for nwa
		self.agm_recordbox.addItems(["№1  16.11.19  10:22:15", "№2  16.11.19  12:05:02", "№3  16.11.19  17:41:55"])
		self.agm_recordbox.setMaximumSize(horizontal_size,vertical_size)
		self.agm_recordbox.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)	
		vertical_size = 30
		horizontal_size = 80
		
		self.agm_recordbutton = QtWidgets.QPushButton("Display \nrecord")
		self.agm_recordbutton.setMaximumSize(horizontal_size,vertical_size)
		self.agm_recordbutton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)#Fixed

		self.agm_filterbox = QtWidgets.QComboBox(self)#span for nwa
		self.agm_filterbox.addItems(["50Hz", "60Hz"])
		self.agm_filterbox.setMaximumSize(horizontal_size,vertical_size)
		self.agm_filterbox.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)		
		self.agm_filterapply = QtWidgets.QPushButton("Set\nFilter")
		self.agm_filterapply.setMaximumSize(horizontal_size,vertical_size)
		self.agm_filterapply.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)#Fixed
		
		self.agm_serial_number_label = QtWidgets.QLabel("AGM №:")
		self.agm_serial_number_label.setMaximumSize(horizontal_size,vertical_size)
		self.agm_serial_number_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Maximum)#Fixed
		self.agm_utc_label = QtWidgets.QLabel("Timezone:")
		self.agm_utc_label.setMaximumSize(horizontal_size,vertical_size)
		self.agm_utc_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Maximum)	

		#self.lbl_g = QtWidgets.QLabel()
		#self.lbl.setPixmap(self.gifka)
		#self.movie = QtGui.QMovie("just.gif",QtCore.QByteArray(),self)
		#self.movie.setSpeed(100)
		#self.lbl_g.setMovie(self.movie)
		#self.movie.start()
		
		
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
		
		
		self.grid.addWidget(self.label_visa_connect, 0, 0)
		self.grid.addWidget(self.comport_combo, 0, 1)
		self.grid.addWidget(self.btn_visa_connect, 0, 2)		

		self.grid.addWidget(self.agm_serial_number_label, 1, 0, alignment = QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
		self.grid.addWidget(self.agm_utc_label, 2, 0, alignment = QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)

		self.grid.addWidget(self.agm_serial_number, 1, 1)#, alignment = QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter)
		self.grid.addWidget(self.agm_utc, 2, 1)
		
		self.grid.addWidget(self.btn_load,4,0)
		#self.grid.addWidget(self.btn_stop,2,1)
		self.grid.addWidget(self.btn_save,4,1)
		self.grid.addWidget(self.btn_clear,4,2)
		self.grid.addWidget(self.agm_recordbox,6,1)
		self.grid.addWidget(self.agm_recordbutton,6,0)
		self.grid.addWidget(self.agm_filterbox,3,1)
		self.grid.addWidget(self.agm_filterapply,3,0)		
		#self.grid.addWidget(self.btn_pause,2,1)
		
		
		
		self.grid.addWidget(QtWidgets.QLabel(""),7,0)
		self.grid.addWidget(QtWidgets.QLabel(""),7,1)
		self.grid.addWidget(QtWidgets.QLabel(""),7,2)
		self.grid.addWidget(QtWidgets.QLabel(""),7,3)
		
		self.grid.addWidget(self.bar,5,0,1,5)
		
		#self.grid.addWidget(self.lbl_g,10,0,1,5)
		#self.grid.addWidget(self.lbl,9,0,20,10)#add picture to grid layout
		#self.grid.addWidget(QtWidgets.QLabel(""),20,25)
		#self.grid.addWidget(self.graph,5,10,5,5)#graph
		#self.grid.setSpacing(10)
		
		self.grid.setHorizontalSpacing(5)
		self.grid.setVerticalSpacing(5)
		self.grid.setContentsMargins(5,5,5,5)
				
		self.vbox_1 = QtWidgets.QVBoxLayout()
		self.vbox_1.insertLayout(0,self.grid)
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

		
		self.meas_thread = evThread()
		
		
		#self.btn_stop.clicked.connect(self.on_interrupted)
		self.btn_load.clicked.connect(self.on_start_load)
		#self.meas_thread.started.connect(self.on_meas_started)
		self.meas_thread.finished.connect(self.on_meas_completed)
		#self.meas_thread.status_signal.connect(self.on_status_text_change, QtCore.Qt.QueuedConnection)
		#self.meas_thread.dataplot.connect(self.graph.plot, QtCore.Qt.QueuedConnection)
		self.meas_thread.progress.connect(self.on_progress_go,QtCore.Qt.QueuedConnection)
		
		self.btn_clear.clicked.connect(self.on_clear)
		#self.pwindow = paramWindow()
		#self.btnSetCF.clicked.connect(self.on_choose_param)
		
		self.agm_recordbutton.clicked.connect(self.on_display_record)
		
		
	def on_activated_com_list(self, str):
		#self.label.setText(str)
		self.ComPort = str
		
	def on_clear(self):
		clear_res = QtWidgets.QMessageBox.question(self, "Подтверждение стирания памяти МК", "Вы действительно хотите стереть данные?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No )
		if clear_res == QtWidgets.QMessageBox.Yes:
			#self.graph.clear()
			self.bar.setValue(0)
	
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
		
		#self.label.setText("measure started")
		#self.graph.clear()
		self.bar.setValue(0)
		self.meas_thread.start()
		
	def on_status_text_change(self, status_text):
		#self.label.setText("measurements - {}".format(status_text))
		print("nothing")
		
	def on_meas_completed(self):
		self.btn_load.setDisabled(False)
		#self.btn_save.setDisable(False)
	def on_interrupted(self):
		self.meas_thread.running = False
		
	def on_display_record(self):
		data = [1021,1025,1017,1029,1023,1026,1035,1058,1082,1134,1169,1224,1151,1113,1042,1021,1021,1021,1021,1021,1013,1018,1004,1002]#test data value for plot
		self.record_number = self.agm_recordbox.currentIndex()
		self.graph.plot(data, pen = pg.mkPen('g', width = 4), symbol = 'o', title = "Record №{}".format(self.record_number))
				
		
	def closeEvent(self, event):#перехватываем событие закрытия приложения
		result = QtWidgets.QMessageBox.question(self, "Подтверждение закрытия окна", "Вы действительно хотите закрыть окно?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No )
		if result == QtWidgets.QMessageBox.Yes:
		
			self.hide()
			self.meas_thread.running = False
			self.meas_thread.wait(5000)#ms
			event.accept()
		else:
			event.ignore()
		
class paramWindow(QtWidgets.QWidget):
	"""класс для окон с настройкой параметров"""
	def __init__(self, parent = None):
		QtWidgets.QWidget.__init__(self, parent)
		self.label_cf = QtWidgets.QLabel("AGM idn:")
		self.label_cf.setAlignment(QtCore.Qt.AlignHCenter)
		
		
		
class evThread(QtCore.QThread):
	
	status_signal = QtCore.pyqtSignal(str)
	dataplot = QtCore.pyqtSignal(np.ndarray)
	progress = QtCore.pyqtSignal(int)
	def __init__(self, parent = None):
		QtCore.QThread.__init__(self,parent)
		self.running = False
		
		
	def run(self):
		self.running = True
		for i in range(100):
			if self.running == True:
				self.sleep(1)
				self.status_signal.emit("{} / {}".format(i+1,100))
				self.dataplot.emit(np.random.randn(200,))
				self.progress.emit(i+1)
				
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
	