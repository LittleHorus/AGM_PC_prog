#!/usr/bin/python3
# -*- coding: utf-8 -*-


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
import pyqtgraph as pg 
import numpy as np
import serial
import array
#import cv2


__version__ = '0.1alfa'

class CommonWindow(QtWidgets.QWidget):
	"""Класс основного окна программы"""
	
	def __init__(self, parent = None):
		QtWidgets.QWidget.__init__(self, parent)

		self.temp_data = bytearray([0x05, 0x10, 0x10, 0x00, 0x00, 0x01, 0x02, 0x00, 0x0a])#0x0556 - crc16 result
		

		self.previous_row = 0
		self.current_row = -1
		self.record_number = 1
		self.count = 0
		self.crc16_modbus = 0
	
		#self.img = cv2.imread("D:\\Python\\ex2.jpg", cv2.IMREAD_GRAYSCALE)
		#self.img = cv2.GaussianBlur(self.img, (11,11),0)
		#self.canny_img = cv2.Canny(self.img, 40,50)
		#self.imv_clear  = pg.ImageView()
		#self.imv_clear.setImage(self.img.T)
		#self.imv_contour = pg.ImageView()
		#self.imv_contour.setImage(self.canny_img.T)
		#self.pg.image(self.canny_img)


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
		print(self.data_bytearray)

		self.ComPort = str
		self.comport_combo = QtWidgets.QComboBox()
		self.comport_combo.addItems([""])
		self.comport_combo.addItems(["Refresh"])
		self.comport_combo.activated[str].connect(self.on_activated_com_list)
		self.comport_combo.activated[str].connect(self.ComPort)

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

		vertical_size = 30
		horizontal_size = 80
		
		self.onlyInt = QtGui.QIntValidator(0,65534)
		#self.LineEdit.setValidator(self.onlyInt)
		

		self.com_read_label = QtWidgets.QLabel("Response string")
		#self.com_read_label.setMaximumSize(30,500)
		self.com_read_label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
		
		#self.comtextbox = QtWidgets.


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
		
		self.dir_label = QtWidgets.QLabel("Direction:")
		self.dir_label.setMaximumSize(horizontal_size,vertical_size)
		self.dir_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)		
		self.dir_value = QtWidgets.QLineEdit("1")#center frequency for nwa
		self.dir_value.setMaximumSize(horizontal_size,vertical_size)
		self.dir_value.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		self.dir_value.setValidator(self.onlyInt)
		self.dir_value.setAlignment(QtCore.Qt.AlignCenter)

		self.speed_label = QtWidgets.QLabel("Speed:")
		self.speed_label.setMaximumSize(horizontal_size,vertical_size)
		self.speed_label.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)		
		self.speed_value = QtWidgets.QLineEdit("1")#center frequency for nwa
		self.speed_value.setMaximumSize(horizontal_size,vertical_size)
		self.speed_value.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
		self.speed_value.setValidator(self.onlyInt)
		self.speed_value.setAlignment(QtCore.Qt.AlignCenter)

		self.btn_send_cmd = QtWidgets.QPushButton("Send CMD")
		self.btn_send_cmd.setMaximumSize(horizontal_size,vertical_size)
		self.btn_send_cmd.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)#Fixed		


		self.btn_send_cmd_zero = QtWidgets.QPushButton("Send To Timer")
		self.btn_send_cmd_zero.setMaximumSize(horizontal_size,vertical_size)
		self.btn_send_cmd_zero.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)#Fixed		


		vertical_size = 30
		horizontal_size = 80


		self.grid = QtWidgets.QGridLayout()

		
		self.grid.addWidget(self.label_visa_connect, 0, 0)
		self.grid.addWidget(self.comport_combo, 0, 1)
		self.grid.addWidget(self.btn_visa_connect, 0, 2)
		self.grid.addWidget(self.btn_visa_disconnect, 0, 3)
		
		self.grid.addWidget(self.dir_label, 1,0)
		self.grid.addWidget(self.dir_value, 1,1)
		self.grid.addWidget(self.speed_label, 1,2)
		self.grid.addWidget(self.speed_value, 1,3)
		self.grid.addWidget(self.btn_send_cmd, 2,0)
		self.grid.addWidget(self.btn_send_cmd_zero, 2,1)

		self.grid.addWidget(QtWidgets.QLabel(""),6,0)
		self.grid.addWidget(QtWidgets.QLabel(""),6,1)
		self.grid.addWidget(QtWidgets.QLabel(""),6,2)
		self.grid.addWidget(QtWidgets.QLabel(""),6,3)
		
		self.vbox_main = QtWidgets.QVBoxLayout()
		self.hbox_main = QtWidgets.QHBoxLayout()	


		self.vbox_1 = QtWidgets.QVBoxLayout()
		#self.vbox_1.insertLayout(0,self.h_box_com_port)
		self.vbox_1.insertLayout(0,self.grid)
		self.vbox_1.insertStretch(1,0)
		#self.vbox_1.insertLayout(1,self.form)
		#self.setLayout(self.grid)
		
		#self.vbox_2 = QtWidgets.QVBoxLayout()
		#self.vbox_2.addWidget(self.imv_clear, 0)
		#self.vbox_2.addWidget(self.imv_contour, 1)
		#self.vbox_2.addWidget(QtWidgets.QLabel(""),2)
		#self.vbox_2.insertStretch(3,0)

		self.hbox_main.insertLayout(0, self.vbox_1)
		#self.hbox_main.insertLayout(1,self.vbox_2)
		#self.hbox_main.addWidget(QtWidgets.QLabel(""),2)
		self.hbox_main.insertStretch(3,0)
		
		self.vbox_main.insertLayout(0, self.hbox_main)
		self.vbox_main.addWidget(self.com_read_label, 1)
		self.vbox_main.addWidget(QtWidgets.QLabel(""), 2)
		self.vbox_main.insertStretch(3,0)
		self.setLayout(self.vbox_main)


		self.btn_visa_connect.clicked.connect(self.on_connected)
		self.btn_visa_disconnect.clicked.connect(self.on_disconnected)
		self.btn_send_cmd.clicked.connect(self.on_send_data) 
		self.btn_send_cmd_zero.clicked.connect(self.on_send_to_timer)
		self.dir_value.editingFinished.connect(self.on_change_dir_value)
		self.speed_value.editingFinished.connect(self.on_change_speed_value)

		self.btn_send_cmd.setDisabled(True)
		self.btn_send_cmd_zero.setDisabled(True)		

	def on_connected(self):
		#print("Connected")
		#print("{}{}{}".format("'", self.ComPort, "'"))
		try:

			self.ser = serial.Serial(self.ComPort, baudrate=9600, bytesize=serial.EIGHTBITS,
									 parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout = 0.2)
			#print(self.ser.isOpen())
			time.sleep(1)
			# ser.close()
			# print(ser.isOpen())
			self.ser.isOpen()  # try to open port
			#print("port is opened!")
			self.btn_visa_connect.setDisabled(True)
			self.btn_visa_disconnect.setDisabled(False)
			self.btn_send_cmd.setDisabled(False)
			self.btn_send_cmd_zero.setDisabled(False)
		except IOError:
			pass
			#print("port was already open, was closed and opened again!")
		except serial.SerialException:
			pass
		#print("crc16 - {}".format(self.crc16(self.temp_data)))
		#self.crc16_modbus = self.calcString( "\x05\x10\x10\x00\x00\x01\x02\x00\x0a", self.INITIAL_MODBUS)
		#print("crc16_modbus - {}".format(self.crc16_modbus))

	def on_change_dir_value(self):
		self.slave_dir_hi = ((int)(self.dir_value.text())>>8)&0xFF
		self.slave_dir_lo = ((int)(self.dir_value.text())&0xff)
		print(self.slave_dir_hi, self.slave_dir_lo)
	def on_change_speed_value(self):
		self.slave_speed_hi = ((int)(self.speed_value.text())>>8)&0xFF
		self.slave_speed_lo = ((int)(self.speed_value.text())&0xff)
		print(self.slave_speed_hi, self.slave_speed_lo)

	def on_send_data(self):
		#self.slave_speed_lo = 0x0a
		t_data_array = [0]*11
		t_data_array[0] = self.slave_address
		t_data_array[1] = self.slave_register
		t_data_array[2] = self.slave_register_address_hi
		t_data_array[3] = self.slave_register_address_lo
		t_data_array[4] = self.slave_register_count_hi
		t_data_array[5] = self.slave_register_count_lo
		t_data_array[6] = self.slave_byte_count
		t_data_array[7] = self.slave_speed_hi
		t_data_array[8] = self.slave_speed_lo
		t_data_array[9] = self.slave_dir_hi
		t_data_array[10] = self.slave_dir_lo

		#t_bytearray = str(t_data_array)
		t_bytearray = array.array('B', t_data_array).tobytes()
		#t_bytearray = t_bytearray[:-1]	
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
		self.data_array[0] = self.slave_address
		self.data_array[1] = self.slave_register
		self.data_array[2] = self.slave_register_address_hi
		self.data_array[3] = self.slave_register_address_lo
		self.data_array[4] = self.slave_register_count_hi
		self.data_array[5] = self.slave_register_count_lo
		self.data_array[6] = self.slave_byte_count
		self.data_array[7] = self.slave_speed_hi
		self.data_array[8] = self.slave_speed_lo
		self.data_array[9] = self.slave_dir_hi
		self.data_array[10] = self.slave_dir_lo
		self.data_array[11] = self.slave_crc16_lo
		self.data_array[12] = self.slave_crc16_hi
		self.data_bytearray = bytearray(self.data_array)
		print(self.data_bytearray)
		self.ser.write(self.data_bytearray)		

		#ba = bytearray(self.data_array)


		try:
			ba = self.ser.read(20)
			parse_byte_list = list()
			for i in range(len(ba)):
				parse_byte_list.append(int(ba[i]))

			#string_for_label = ''
			string_for_label = [f'0x{i:02X}' for i in parse_byte_list]


			print(string_for_label)
			self.com_read_label.setText(str(string_for_label))
			self.com_read_label.adjustSize()			

		except:
			print("Unexpected error")


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

		#t_bytearray = str(t_data_array)
		t_bytearray = array.array('B', t_data_array).tobytes()
		#t_bytearray = t_bytearray[:-1]	
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
	def on_disconnected(self):
		self.btn_visa_connect.setDisabled(False)
		self.btn_visa_disconnect.setDisabled(True)	
		self.btn_send_cmd.setDisabled(True)
		self.btn_send_cmd_zero.setDisabled(True)
		#print("Disconnected")
		self.ser.close()
		#print(self.ser.isOpen())		
		
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
			#self.meas_thread.running = False
			#self.meas_thread.wait(5000)#ms
			event.accept()
		else:
			event.ignore()

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
	ex.setWindowTitle("Mech")
	ex.comport_combo.addItems(serial_ports())
	ex.setFixedSize(600,250)
	#ex.resize(300,200)
	#ex.adjustSize()
	#ico = QtGui.QIcon("icon.png")
	#ex.setWindowIcon(ico)#icon for window only
	#app.setWindowIcon(ico)#icon for application

	
	ex.show()
	sys.exit(app.exec_())#run the cycle of processing the events
	