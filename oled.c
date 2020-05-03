#include "oled.h"
#include "stdio.h"
extern struct device_status_struct agm;
extern  char oled_buf[9][25];
uint8_t data_to_monitor[5], monitorio[10];
extern char menu_ring_cnt;
uint16_t blink_active_param = 0;
const char digit_char[10] = "0123456789";
const char digit_0[4] = "0   ";
const char digit_1[4] = "1   ";
const char digit_2[4] = "2   ";
const char digit_3[4] = "3   ";
const char digit_4[4] = "4   ";
const char digit_5[4] = "5   ";
const char digit_6[4] = "6   ";
const char digit_7[4] = "7   ";
const char digit_8[4] = "8   ";
const char digit_9[4] = "9   ";
const char digit_auto[4] = "AUTO";

const char record_mode_mag[21]        = "RECORD MODE:     MAG ";
const char record_mode_lf[21]         = "RECORD MODE:     LF  ";
const char record_mode_mag_lf[21]     = "RECORD MODE:   MAG+LF";

const char sensitivity_mag[21]    = "SENSITIVITY MAG:     ";
const char sensitivity_lf[21]     = "SENSITIVITY LF:      ";

const char data_interface_usb[21] = "DATA INTERFACE:  USB ";
const char data_interface_bl[21]  = "DATA INTERFACE:  BL  ";
const char data_interface_none[21]= "DATA INTERFACE:  NONE";

const char gsm_gprs_yes[21]       = "GSM/GPRS:        YES ";
const char gsm_gprs_no[21]        = "GSM/GPRS:        NO  ";

const char gps_glonass_yes[21]    = "GPS/GLONASS:     YES ";
const char gps_glonass_no[21]     = "GPS/GLONASS:     NO  ";

const char download_data_yes[21]  = "DOWNLOAD DATA:   YES ";
const char download_data_no[21]   = "DOWNLOAD DATA:   NO  ";

const char erase_data_yes[21]     = "ERASE DATA:      YES ";
const char erase_data_no[21]      = "ERASE DATA:      NO  ";

const char notch_filter_50[21]    = "NOTCH FILTER:    50Hz";
const char notch_filter_60[21]    = "NOTCH FILTER:    60Hz";


//0x00, 0x05, 0x07, 0x20,
uint8_t ssd1306xled_font5x7 []=
 {
   
   0x00, 0x00, 0x00, 0x00, 0x00, // sp
   0x00, 0x00, 0x5F, 0x00, 0x00, // !
   0x00, 0x03, 0x00, 0x03, 0x00, // "
   0x14, 0x3E, 0x14, 0x3E, 0x14, // #
   0x24, 0x2A, 0x7F, 0x2A, 0x12, // $
   0x43, 0x33, 0x08, 0x66, 0x61, // %
   0x36, 0x49, 0x55, 0x22, 0x50, // &
   0x00, 0x05, 0x03, 0x00, 0x00, // '
   0x00, 0x1C, 0x22, 0x41, 0x00, // (
   0x00, 0x41, 0x22, 0x1C, 0x00, // )
   0x14, 0x08, 0x3E, 0x08, 0x14, // *
   0x08, 0x08, 0x3E, 0x08, 0x08, // +
   0x00, 0x50, 0x30, 0x00, 0x00, // ,
   0x08, 0x08, 0x08, 0x08, 0x08, // -
   0x00, 0x60, 0x60, 0x00, 0x00, // .
   0x20, 0x10, 0x08, 0x04, 0x02, // /
   0x3E, 0x51, 0x49, 0x45, 0x3E, // 0
   0x00, 0x04, 0x02, 0x7F, 0x00, // 1
   0x42, 0x61, 0x51, 0x49, 0x46, // 2
   0x22, 0x41, 0x49, 0x49, 0x36, // 3
   0x18, 0x14, 0x12, 0x7F, 0x10, // 4
   0x27, 0x45, 0x45, 0x45, 0x39, // 5
   0x3E, 0x49, 0x49, 0x49, 0x32, // 6
   0x01, 0x01, 0x71, 0x09, 0x07, // 7
   0x36, 0x49, 0x49, 0x49, 0x36, // 8
   0x26, 0x49, 0x49, 0x49, 0x3E, // 9
   0x00, 0x36, 0x36, 0x00, 0x00, // :
   0x00, 0x56, 0x36, 0x00, 0x00, // ;
   0x08, 0x14, 0x22, 0x41, 0x00, // <
   0x14, 0x14, 0x14, 0x14, 0x14, // =
   0x00, 0x41, 0x22, 0x14, 0x08, // >
   0x02, 0x01, 0x51, 0x09, 0x06, // ?
   0x3E, 0x41, 0x59, 0x55, 0x5E, // @
   0x7E, 0x09, 0x09, 0x09, 0x7E, // A
   0x7F, 0x49, 0x49, 0x49, 0x36, // B
   0x3E, 0x41, 0x41, 0x41, 0x22, // C
   0x7F, 0x41, 0x41, 0x41, 0x3E, // D
   0x7F, 0x49, 0x49, 0x49, 0x41, // E
   0x7F, 0x09, 0x09, 0x09, 0x01, // F
   0x3E, 0x41, 0x41, 0x49, 0x3A, // G
   0x7F, 0x08, 0x08, 0x08, 0x7F, // H
   0x00, 0x41, 0x7F, 0x41, 0x00, // I
   0x30, 0x40, 0x40, 0x40, 0x3F, // J
   0x7F, 0x08, 0x14, 0x22, 0x41, // K
   0x7F, 0x40, 0x40, 0x40, 0x40, // L
   0x7F, 0x02, 0x0C, 0x02, 0x7F, // M
   0x7F, 0x02, 0x04, 0x08, 0x7F, // N
   0x3E, 0x41, 0x41, 0x41, 0x3E, // O
   0x7F, 0x09, 0x09, 0x09, 0x06, // P
   0x1E, 0x21, 0x21, 0x21, 0x5E, // Q
   0x7F, 0x09, 0x09, 0x09, 0x76, // R
   0x26, 0x49, 0x49, 0x49, 0x32, // S
   0x01, 0x01, 0x7F, 0x01, 0x01, // T
   0x3F, 0x40, 0x40, 0x40, 0x3F, // U
   0x1F, 0x20, 0x40, 0x20, 0x1F, // V
   0x7F, 0x20, 0x10, 0x20, 0x7F, // W
   0x41, 0x22, 0x1C, 0x22, 0x41, // X
   0x07, 0x08, 0x70, 0x08, 0x07, // Y
   0x61, 0x51, 0x49, 0x45, 0x43, // Z
   0x00, 0x7F, 0x41, 0x00, 0x00, // [
   0x02, 0x04, 0x08, 0x10, 0x20, // 55
   0x00, 0x00, 0x41, 0x7F, 0x00, // ]
   0x04, 0x02, 0x01, 0x02, 0x04, // ^
   0x40, 0x40, 0x40, 0x40, 0x40, // _
   0x00, 0x01, 0x02, 0x04, 0x00, // `
   0x20, 0x54, 0x54, 0x54, 0x78, // a
   0x7F, 0x44, 0x44, 0x44, 0x38, // b
   0x38, 0x44, 0x44, 0x44, 0x44, // c
   0x38, 0x44, 0x44, 0x44, 0x7F, // d
   0x38, 0x54, 0x54, 0x54, 0x18, // e
   0x04, 0x04, 0x7E, 0x05, 0x05, // f
   0x08, 0x54, 0x54, 0x54, 0x3C, // g
   0x7F, 0x08, 0x04, 0x04, 0x78, // h
   0x00, 0x44, 0x7D, 0x40, 0x00, // i
   0x20, 0x40, 0x44, 0x3D, 0x00, // j
   0x7F, 0x10, 0x28, 0x44, 0x00, // k
   0x00, 0x41, 0x7F, 0x40, 0x00, // l
   0x7C, 0x04, 0x78, 0x04, 0x78, // m
   0x7C, 0x08, 0x04, 0x04, 0x78, // n
   0x38, 0x44, 0x44, 0x44, 0x38, // o
   0x7C, 0x14, 0x14, 0x14, 0x08, // p
   0x08, 0x14, 0x14, 0x14, 0x7C, // q
   0x00, 0x7C, 0x08, 0x04, 0x04, // r
   0x48, 0x54, 0x54, 0x54, 0x20, // s
   0x04, 0x04, 0x3F, 0x44, 0x44, // t
   0x3C, 0x40, 0x40, 0x20, 0x7C, // u
   0x1C, 0x20, 0x40, 0x20, 0x1C, // v
   0x3C, 0x40, 0x30, 0x40, 0x3C, // w
   0x44, 0x28, 0x10, 0x28, 0x44, // x
   0x0C, 0x50, 0x50, 0x50, 0x3C, // y
   0x44, 0x64, 0x54, 0x4C, 0x44, // z
   0x00, 0x08, 0x36, 0x41, 0x41, // {
   0x00, 0x00, 0x7F, 0x00, 0x00, // |
   0x41, 0x41, 0x36, 0x08, 0x00, // }
   0x02, 0x01, 0x02, 0x04, 0x02, // ~
   0x14, 0x14, 0x14, 0x14, 0x14, // horiz lines // DEL
   0x00 /* This byte is required for italic type of font */
 };
const uint8_t ssd1306xled_font6x8 []=
 {
   0x00, 0x06, 0x08, 0x20,
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // sp
   0x00, 0x00, 0x00, 0x2f, 0x00, 0x00, // !
   0x00, 0x00, 0x07, 0x00, 0x07, 0x00, // "
   0x00, 0x14, 0x7f, 0x14, 0x7f, 0x14, // #
   0x00, 0x24, 0x2a, 0x7f, 0x2a, 0x12, // $
   0x00, 0x23, 0x13, 0x08, 0x64, 0x62, // %
   0x00, 0x36, 0x49, 0x55, 0x22, 0x50, // &
   0x00, 0x00, 0x05, 0x03, 0x00, 0x00, // '
   0x00, 0x00, 0x1c, 0x22, 0x41, 0x00, // (
   0x00, 0x00, 0x41, 0x22, 0x1c, 0x00, // )
   0x00, 0x14, 0x08, 0x3E, 0x08, 0x14, // *
   0x00, 0x08, 0x08, 0x3E, 0x08, 0x08, // +
   0x00, 0x00, 0x00, 0xA0, 0x60, 0x00, // ,
   0x00, 0x08, 0x08, 0x08, 0x08, 0x08, // -
   0x00, 0x00, 0x60, 0x60, 0x00, 0x00, // .
   0x00, 0x20, 0x10, 0x08, 0x04, 0x02, // /
   0x00, 0x3E, 0x51, 0x49, 0x45, 0x3E, // 0
   0x00, 0x00, 0x42, 0x7F, 0x40, 0x00, // 1
   0x00, 0x42, 0x61, 0x51, 0x49, 0x46, // 2
   0x00, 0x21, 0x41, 0x45, 0x4B, 0x31, // 3
   0x00, 0x18, 0x14, 0x12, 0x7F, 0x10, // 4
   0x00, 0x27, 0x45, 0x45, 0x45, 0x39, // 5
   0x00, 0x3C, 0x4A, 0x49, 0x49, 0x30, // 6
   0x00, 0x01, 0x71, 0x09, 0x05, 0x03, // 7
   0x00, 0x36, 0x49, 0x49, 0x49, 0x36, // 8
   0x00, 0x06, 0x49, 0x49, 0x29, 0x1E, // 9
   0x00, 0x00, 0x36, 0x36, 0x00, 0x00, // :
   0x00, 0x00, 0x56, 0x36, 0x00, 0x00, // ;
   0x00, 0x08, 0x14, 0x22, 0x41, 0x00, // <
   0x00, 0x14, 0x14, 0x14, 0x14, 0x14, // =
   0x00, 0x00, 0x41, 0x22, 0x14, 0x08, // >
   0x00, 0x02, 0x01, 0x51, 0x09, 0x06, // ?
   0x00, 0x32, 0x49, 0x59, 0x51, 0x3E, // @
   0x00, 0x7C, 0x12, 0x11, 0x12, 0x7C, // A
   0x00, 0x7F, 0x49, 0x49, 0x49, 0x36, // B
   0x00, 0x3E, 0x41, 0x41, 0x41, 0x22, // C
   0x00, 0x7F, 0x41, 0x41, 0x22, 0x1C, // D
   0x00, 0x7F, 0x49, 0x49, 0x49, 0x41, // E
   0x00, 0x7F, 0x09, 0x09, 0x09, 0x01, // F
   0x00, 0x3E, 0x41, 0x49, 0x49, 0x7A, // G
   0x00, 0x7F, 0x08, 0x08, 0x08, 0x7F, // H
   0x00, 0x00, 0x41, 0x7F, 0x41, 0x00, // I
   0x00, 0x20, 0x40, 0x41, 0x3F, 0x01, // J
   0x00, 0x7F, 0x08, 0x14, 0x22, 0x41, // K
   0x00, 0x7F, 0x40, 0x40, 0x40, 0x40, // L
   0x00, 0x7F, 0x02, 0x0C, 0x02, 0x7F, // M
   0x00, 0x7F, 0x04, 0x08, 0x10, 0x7F, // N
   0x00, 0x3E, 0x41, 0x41, 0x41, 0x3E, // O
   0x00, 0x7F, 0x09, 0x09, 0x09, 0x06, // P
   0x00, 0x3E, 0x41, 0x51, 0x21, 0x5E, // Q
   0x00, 0x7F, 0x09, 0x19, 0x29, 0x46, // R
   0x00, 0x46, 0x49, 0x49, 0x49, 0x31, // S
   0x00, 0x01, 0x01, 0x7F, 0x01, 0x01, // T
   0x00, 0x3F, 0x40, 0x40, 0x40, 0x3F, // U
   0x00, 0x1F, 0x20, 0x40, 0x20, 0x1F, // V
   0x00, 0x3F, 0x40, 0x38, 0x40, 0x3F, // W
   0x00, 0x63, 0x14, 0x08, 0x14, 0x63, // X
   0x00, 0x07, 0x08, 0x70, 0x08, 0x07, // Y
   0x00, 0x61, 0x51, 0x49, 0x45, 0x43, // Z
   0x00, 0x00, 0x7F, 0x41, 0x41, 0x00, // [
   0x00, 0x55, 0x2A, 0x55, 0x2A, 0x55, // 55
   0x00, 0x00, 0x41, 0x41, 0x7F, 0x00, // ]
   0x00, 0x04, 0x02, 0x01, 0x02, 0x04, // ^
   0x00, 0x40, 0x40, 0x40, 0x40, 0x40, // _
   0x00, 0x00, 0x01, 0x02, 0x04, 0x00, // '
   0x00, 0x20, 0x54, 0x54, 0x54, 0x78, // a
   0x00, 0x7F, 0x48, 0x44, 0x44, 0x38, // b
   0x00, 0x38, 0x44, 0x44, 0x44, 0x20, // c
   0x00, 0x38, 0x44, 0x44, 0x48, 0x7F, // d
   0x00, 0x38, 0x54, 0x54, 0x54, 0x18, // e
   0x00, 0x08, 0x7E, 0x09, 0x01, 0x02, // f
   0x00, 0x18, 0xA4, 0xA4, 0xA4, 0x7C, // g
   0x00, 0x7F, 0x08, 0x04, 0x04, 0x78, // h
   0x00, 0x00, 0x44, 0x7D, 0x40, 0x00, // i
   0x00, 0x40, 0x80, 0x84, 0x7D, 0x00, // j
   0x00, 0x7F, 0x10, 0x28, 0x44, 0x00, // k
   0x00, 0x00, 0x41, 0x7F, 0x40, 0x00, // l
   0x00, 0x7C, 0x04, 0x18, 0x04, 0x78, // m
   0x00, 0x7C, 0x08, 0x04, 0x04, 0x78, // n
   0x00, 0x38, 0x44, 0x44, 0x44, 0x38, // o
   0x00, 0xFC, 0x24, 0x24, 0x24, 0x18, // p
   0x00, 0x18, 0x24, 0x24, 0x18, 0xFC, // q
   0x00, 0x7C, 0x08, 0x04, 0x04, 0x08, // r
   0x00, 0x48, 0x54, 0x54, 0x54, 0x20, // s
   0x00, 0x04, 0x3F, 0x44, 0x40, 0x20, // t
   0x00, 0x3C, 0x40, 0x40, 0x20, 0x7C, // u
   0x00, 0x1C, 0x20, 0x40, 0x20, 0x1C, // v
   0x00, 0x3C, 0x40, 0x30, 0x40, 0x3C, // w
   0x00, 0x44, 0x28, 0x10, 0x28, 0x44, // x
   0x00, 0x1C, 0xA0, 0xA0, 0xA0, 0x7C, // y
   0x00, 0x44, 0x64, 0x54, 0x4C, 0x44, // z
   0x00, 0x00, 0x08, 0x77, 0x00, 0x00, // {
   0x00, 0x00, 0x00, 0x7F, 0x00, 0x00, // |
   0x00, 0x00, 0x77, 0x08, 0x00, 0x00, // }
   0x00, 0x10, 0x08, 0x10, 0x08, 0x00, // ~
   0x14, 0x14, 0x14, 0x14, 0x14, 0x14, // horiz lines // DEL
   0x00 /* This byte is required for italic type of font */
 };


//actual picture for oled
//signal type
uint8_t lf_pict[] = {0, 254, 2, 254, 0, 0, 0, 0, 254, 2, 122, 74, 74, 202, 14, 0, 0, 127, 64, 95, 80, 80, 80, 80, 127, 64, 127, 1, 1, 1, 0, 0};
uint8_t mag_pict[] = {0, 240, 8, 4, 2, 226, 34, 62, 42, 54, 234, 86, 172, 88, 240, 0, 0, 121, 17, 33, 17, 121, 0, 112, 40, 112, 1, 121, 73, 73, 105, 0};
uint8_t mag_lf_pict[] = {0, 0, 62, 62, 32, 32, 32, 0, 62, 62, 10, 10, 66, 224, 64, 0, 0, 0, 124, 66, 65, 65, 121, 9, 15, 125, 107, 85, 106, 124, 0, 0};
//connection mode
uint8_t usb_pict[] = {128, 128, 128, 0, 128, 64, 32, 16, 8, 28, 28, 8, 192, 128, 0, 0, 3, 3, 3, 1, 1, 1, 7, 9, 17, 113, 113, 113, 7, 3, 1, 0};
uint8_t bluetooth_pict[] = {0, 0, 0, 16, 32, 64, 128, 254, 132, 136, 80, 32, 0, 0, 0, 0, 0, 0, 0, 16, 8, 4, 2, 127, 33, 17, 10, 4, 0, 0, 0, 0};
//battery charge indication
uint8_t battery_empty_pict[] = {248, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 248, 224, 15, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 15, 3};
uint8_t battery_1_3_pict[] = {248, 8, 232, 232, 232, 8, 8, 8, 8, 8, 8, 8, 8, 8, 248, 224, 15, 8, 11, 11, 11, 8, 8, 8, 8, 8, 8, 8, 8, 8, 15, 3};
uint8_t battery_2_3_pict[] = {248, 8, 232, 232, 232, 8, 232, 232, 232, 8, 8, 8, 8, 8, 248, 224, 15, 8, 11, 11, 11, 8, 11, 11, 11, 8, 8, 8, 8, 8, 15, 3};
uint8_t battery_full_pict[] = {248, 8, 232, 232, 232, 8, 232, 232, 232, 8, 232, 232, 232, 8, 248, 224, 15, 8, 11, 11, 11, 8, 11, 11, 11, 8, 11, 11, 11, 8, 15, 3};
//gsm signal level
uint8_t gsm_disable_pict[] = {0, 240, 8, 4, 2, 2, 2, 2, 130, 66, 34, 18, 12, 8, 240, 0, 0, 15, 16, 48, 72, 68, 66, 65, 64, 64, 64, 64, 32, 16, 15, 0};
uint8_t gsm_1_4_pict[] = {0, 2, 4, 8, 254, 8, 4, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64, 96, 112, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
uint8_t gsm_2_4_pict[] = {0, 2, 4, 8, 254, 8, 4, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 64, 96, 112, 0, 120, 124, 126, 0, 0, 0, 0, 0, 0, 0, 0};
uint8_t gsm_3_4_pict[] = {0, 2, 4, 8, 254, 8, 4, 2, 0, 0, 128, 192, 0, 0, 0, 0, 0, 64, 96, 112, 0, 120, 124, 126, 0, 127, 127, 127, 0, 0, 0, 0};
uint8_t gsm_4_4_pict[] = {0, 2, 4, 8, 254, 8, 4, 2, 0, 0, 128, 192, 0, 224, 240, 0, 0, 64, 96, 112, 0, 120, 124, 126, 0, 127, 127, 127, 0, 127, 127, 0};
uint8_t gsm_no_signal_pict[] = {0, 56, 68, 162, 146, 138, 68, 56, 0, 128, 192, 224, 0, 248, 252, 0, 0, 64, 96, 112, 0, 120, 124, 126, 0, 127, 127, 127, 0, 127, 127, 0};
//gps mode
uint8_t gps_enable_pict[] = {0, 0, 0, 0, 252, 248, 240, 224, 192, 128, 64, 32, 0, 5, 2, 5, 240, 240, 200, 200, 63, 15, 15, 15, 15, 15, 15, 14, 12, 8, 0, 0};
uint8_t gps_disable_pict[] = {0, 240, 8, 4, 2, 2, 2, 2, 130, 66, 34, 18, 12, 8, 240, 0, 0, 15, 16, 48, 72, 68, 66, 65, 64, 64, 64, 64, 32, 16, 15, 0};
//event
//uint8_t event_pict[] = {255, 255, 15, 27, 51, 99, 195, 131, 131, 195, 99, 51, 27, 15, 255, 255, 255, 255, 192, 192, 192, 192, 192, 193, 193, 192, 192, 192, 192, 192, 255, 255};
uint8_t event_pict[] = {0, 254, 14, 26, 50, 98, 194, 130, 130, 194, 98, 50, 26, 14, 254, 0, 0, 127, 64, 64, 64, 64, 64, 65, 65, 64, 64, 64, 64, 64, 127, 0};
//device mode
uint8_t standby_pict[] = {0, 0, 0, 0, 0, 76, 179, 0, 204, 51, 0, 0, 0, 0, 0, 0, 7, 5, 39, 41, 113, 97, 97, 97, 97, 97, 97, 113, 41, 39, 0, 0};
uint8_t active_pict[] = {0, 0, 0, 192, 96, 32, 240, 246, 255, 255, 102, 192, 128, 128, 192, 64, 0, 0, 97, 225, 48, 16, 31, 7, 7, 4, 12, 56, 96, 96, 32, 0};
//card memory status
uint8_t card_empty_pict[] = {0, 254, 2, 62, 66, 66, 66, 66, 90, 90, 66, 62, 2, 4, 8, 240, 0, 127, 64, 64, 64, 64, 64, 95, 81, 95, 64, 89, 68, 83, 64, 127};
uint8_t card_half_pict[] = {0, 254, 2, 62, 66, 66, 66, 66, 90, 90, 66, 62, 2, 4, 8, 240, 0, 127, 64, 87, 85, 93, 64, 95, 81, 95, 64, 89, 68, 83, 64, 127};
uint8_t card_full_pict[] = {0, 254, 2, 62, 66, 66, 66, 66, 90, 90, 66, 62, 2, 4, 8, 240, 0, 127, 64, 64, 66, 95, 64, 95, 81, 95, 64, 95, 81, 95, 64, 127};
uint8_t null_pict[] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

uint8_t display_status_picts[256];
uint8_t display_detect_signal[256];
extern struct option_menu agm_option_menu;

static const uint8_t display_logo[] = {
0x00, 0x80, 0x80, 0xb0, 0xf0, 0xf8, 0xf8, 0xf8, 0xfc, 0xb8, 0xbc, 0xbc, 0x9c, 0x8c, 0x80, 0x80, 
0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x00, 0x00, 0x00, 0x00, 
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
0x00, 0x00, 0x80, 0x80, 0xc0, 0x40, 0x00, 0x80, 0x80, 0xc0, 0x00, 0x00, 0xe0, 0x60, 0xc0, 0x00, 
0x80, 0xc0, 0x60, 0x60, 0x60, 0x40, 0xc0, 0xe0, 0xe0, 0x00, 0xe0, 0xe0, 0x00, 0x00, 0x00, 0xe0, 
0xc0, 0x00, 0xc0, 0x60, 0x80, 0xc0, 0xe0, 0x00, 0x00, 0x00, 0x00, 0xc0, 0x60, 0xe0, 0xc0, 0x40, 
0xc0, 0x80, 0x80, 0x00, 0xc0, 0xc0, 0x80, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
0x00, 0xff, 0x01, 0xe1, 0xff, 0x47, 0x25, 0x39, 0x1f, 0xc1, 0xcf, 0xcf, 0xdf, 0x1f, 0x2d, 0x2d, 
0xdd, 0x69, 0xe9, 0xe9, 0xb1, 0x71, 0x71, 0x83, 0x23, 0x27, 0x3f, 0xff, 0x00, 0x00, 0x00, 0x00, 
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
0x00, 0x01, 0x01, 0x03, 0x02, 0x02, 0x01, 0x03, 0x03, 0x02, 0x00, 0x07, 0x03, 0x03, 0x03, 0x06, 
0x01, 0x07, 0x06, 0x05, 0x07, 0x03, 0x07, 0x07, 0x03, 0x07, 0x03, 0x07, 0x00, 0x00, 0x00, 0x00, 
0x07, 0x07, 0x03, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x04, 0x00, 0x07, 0x06, 0x07, 0x03, 0x02, 
0x02, 0x03, 0x01, 0x01, 0x02, 0x02, 0x03, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
0x00, 0xff, 0xf0, 0x7f, 0x01, 0x81, 0xc3, 0x66, 0x34, 0x1f, 0xf2, 0x03, 0x00, 0x00, 0x00, 0xff, 
0x99, 0x6b, 0x1f, 0x0f, 0x0f, 0x1e, 0x1a, 0x3f, 0xb6, 0xf8, 0xf8, 0xff, 0x00, 0x00, 0x00, 0xf8, 
0xfc, 0xfc, 0x1c, 0x0c, 0x0c, 0x1c, 0xfc, 0xf8, 0xf0, 0x00, 0xf0, 0xf8, 0xfc, 0x1c, 0x0c, 0x0c, 
0x1c, 0xfc, 0xfc, 0xf8, 0x40, 0xf0, 0xf8, 0xfc, 0xfc, 0x0c, 0x0c, 0x0c, 0xfc, 0xfc, 0xf8, 0xf0, 
0x00, 0x00, 0x00, 0x00, 0x00, 0x1c, 0x1c, 0x1c, 0x00, 0x1c, 0x1c, 0x0c, 0x00, 0xfc, 0xfc, 0xfc, 
0xe0, 0xe0, 0xe0, 0xfc, 0xfc, 0xfc, 0x00, 0x00, 0xfc, 0xfc, 0xfc, 0x00, 0x00, 0x00, 0xfc, 0xfc, 
0xfc, 0xfc, 0x00, 0x0c, 0x0c, 0x0c, 0xfc, 0xfc, 0xfc, 0xfc, 0x0c, 0x0c, 0x0c, 0xf0, 0xf8, 0xfc, 
0xfc, 0x0c, 0x0c, 0x0c, 0xfc, 0xfc, 0xf8, 0xe0, 0x0c, 0x1c, 0x1c, 0x04, 0x1c, 0x1c, 0x1c, 0x00, 
0x00, 0x7f, 0x7f, 0x7f, 0x7f, 0x7e, 0x7e, 0x7e, 0x7e, 0x7e, 0x7f, 0x7e, 0x7e, 0x7e, 0x7e, 0x7e, 
0x7e, 0x7e, 0x7e, 0x7e, 0x7e, 0x7e, 0x7e, 0x7e, 0x7f, 0x7e, 0x7f, 0x7f, 0x00, 0x00, 0x00, 0x03, 
0x07, 0x07, 0x0e, 0x0e, 0x0e, 0x0f, 0x07, 0x07, 0x01, 0x00, 0x03, 0x07, 0x07, 0x0f, 0x0e, 0x0e, 
0x0e, 0x07, 0x07, 0x03, 0x00, 0x01, 0x03, 0x07, 0x0f, 0x0e, 0x0e, 0x0e, 0x0f, 0x07, 0x03, 0x01, 
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0f, 0x0f, 0x0f, 
0x00, 0x00, 0x00, 0x0f, 0x0f, 0x0f, 0x00, 0x00, 0x07, 0x0f, 0x0f, 0x0e, 0x0e, 0x0e, 0x0f, 0x0f, 
0x1f, 0x1f, 0x1e, 0x00, 0x00, 0x00, 0x07, 0x0f, 0x0f, 0x07, 0x00, 0x00, 0x00, 0x01, 0x03, 0x07, 
0x0f, 0x0e, 0x0e, 0x0e, 0x0f, 0x07, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
  /*
  0, 0, 0, 56, 224, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  224, 224, 32, 32, 32, 32, 96, 64, 192, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, 0, 0, 0, 128, 224, 32, 32, 32, 32, 32, 32, 32, 64, 0, 0, 0, 0, 0, 0, 0, 
  0, 224, 224, 32, 32, 32, 32, 96, 64, 192, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, 0, 0, 0, 0, 0, 0, 192, 64, 64, 64, 64, 192, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,

  0, 0, 0, 0, 3, 254, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 
  128, 0, 0, 0, 0, 0, 0, 0, 1, 1, 7, 60, 224, 0, 0, 0, 0, 0, 0, 0, 0, 252, 7, 1, 
  0, 0, 0, 0, 128, 128, 128, 128, 128, 0, 0, 0, 0, 0, 0, 0, 0, 255, 128, 0, 0, 0, 
  0, 0, 0, 0, 1, 1, 7, 60, 224, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 252, 128, 
  128, 192, 64, 113, 31, 0, 0, 0, 152, 152, 0, 0, 0, 0, 0, 0, 128, 128, 128, 128, 
  128, 0, 0, 0, 0, 0, 0, 128, 0, 0, 0, 0, 0, 

  0, 0, 0, 0, 0, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 15, 
  120, 192, 0, 0, 0, 0, 0, 0, 0, 128, 224, 63, 0, 0, 0, 0, 0, 0, 0, 0, 15, 24, 48, 
  96, 192, 128, 0, 1, 0, 0, 0, 129, 227, 62, 0, 0, 0, 0, 0, 0, 0, 15, 120, 192, 0, 
  0, 0, 0, 0, 0, 0, 128, 224, 63, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 255, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 255, 0, 0, 0, 0, 0, 127, 193, 128, 128, 128, 129, 192, 0, 
  0, 0, 4, 4, 255, 132, 132, 0, 0, 0,    

  0, 0, 0, 0, 14, 15, 4, 6, 2, 2, 2, 2, 2, 2, 2, 2, 2, 6, 4, 4, 0, 0, 0, 0, 0, 0, 0, 1,
  3, 2, 6, 4, 4, 6, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1,
  1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 2, 6, 4, 4, 6, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0    
  
  */
};
 unsigned char font5x6[]={
0x00, 0x00, 0x00, 0x00, 0x00, /* chr: ' '  (2 wide) */
0x5e, 0x00, 0x00, 0x00, 0x00, /* chr: '!'  (1 wide) */
0x06, 0x00, 0x06, 0x00, 0x00, /* chr: '"'  (3 wide) */
0x14, 0x3e, 0x14, 0x3e, 0x14, /* chr: '#'  (5 wide) */
0x24, 0x2a, 0x7e, 0x2a, 0x12, /* chr: '$'  (5 wide) */
0x44, 0x20, 0x10, 0x08, 0x44, /* chr: '%'  (5 wide) */
0x34, 0x4a, 0x54, 0x20, 0x50, /* chr: '&'  (5 wide) */
0x04, 0x02, 0x00, 0x00, 0x00, /* chr: '''  (2 wide) */
0x3c, 0x42, 0x00, 0x00, 0x00, /* chr: '('  (2 wide) */
0x42, 0x3c, 0x00, 0x00, 0x00, /* chr: ')'  (2 wide) */
0x54, 0x38, 0x38, 0x54, 0x00, /* chr: '*'  (4 wide) */
0x10, 0x38, 0x10, 0x00, 0x00, /* chr: '+'  (3 wide) */
0x40, 0x20, 0x00, 0x00, 0x00, /* chr: ','  (2 wide) */
0x10, 0x10, 0x10, 0x00, 0x00, /* chr: '-'  (3 wide) */
0x40, 0x00, 0x00, 0x00, 0x00, /* chr: '.'  (1 wide) */
0x40, 0x20, 0x10, 0x08, 0x04, /* chr: '/'  (5 wide) */
0x3c, 0x52, 0x4a, 0x3c, 0x00, /* chr: '0'  (4 wide) */
0x44, 0x7e, 0x40, 0x00, 0x00, /* chr: '1'  (3 wide) */
0x64, 0x52, 0x4a, 0x44, 0x00, /* chr: '2'  (4 wide) */
0x42, 0x4a, 0x4a, 0x34, 0x00, /* chr: '3'  (4 wide) */
0x1e, 0x10, 0x7c, 0x10, 0x00, /* chr: '4'  (4 wide) */
0x4e, 0x4a, 0x4a, 0x32, 0x00, /* chr: '5'  (4 wide) */
0x3c, 0x4a, 0x4a, 0x32, 0x00, /* chr: '6'  (4 wide) */
0x02, 0x72, 0x0a, 0x06, 0x00, /* chr: '7'  (4 wide) */
0x34, 0x4a, 0x4a, 0x34, 0x00, /* chr: '8'  (4 wide) */
0x0c, 0x52, 0x52, 0x3c, 0x00, /* chr: '9'  (4 wide) */
0x24, 0x00, 0x00, 0x00, 0x00, /* chr: ':'  (1 wide) */
0x40, 0x24, 0x00, 0x00, 0x00, /* chr: ';'  (2 wide) */
0x10, 0x28, 0x44, 0x00, 0x00, /* chr: '<'  (3 wide) */
0x28, 0x28, 0x28, 0x00, 0x00, /* chr: '='  (3 wide) */
0x44, 0x28, 0x10, 0x00, 0x00, /* chr: '>'  (3 wide) */
0x04, 0x52, 0x0a, 0x04, 0x00, /* chr: '?'  (4 wide) */
0x38, 0x04, 0x34, 0x44, 0x38, /* chr: '@'  (5 wide) */
0x7c, 0x12, 0x12, 0x7c, 0x00, /* chr: 'A'  (4 wide) */
0x7e, 0x4a, 0x4a, 0x34, 0x00, /* chr: 'B'  (4 wide) */
0x3c, 0x42, 0x42, 0x24, 0x00, /* chr: 'C'  (4 wide) */
0x7e, 0x42, 0x42, 0x3c, 0x00, /* chr: 'D'  (4 wide) */
0x7e, 0x4a, 0x4a, 0x42, 0x00, /* chr: 'E'  (4 wide) */
0x7e, 0x0a, 0x0a, 0x02, 0x00, /* chr: 'F'  (4 wide) */
0x3c, 0x42, 0x52, 0x34, 0x00, /* chr: 'G'  (4 wide) */
0x7e, 0x08, 0x08, 0x7e, 0x00, /* chr: 'H'  (4 wide) */
0x00, 0x00, 0x7e, 0x00, 0x00, /* chr: 'I'  (1 wide) */
0x20, 0x40, 0x3e, 0x00, 0x00, /* chr: 'J'  (3 wide) */
0x7e, 0x08, 0x14, 0x22, 0x40, /* chr: 'K'  (5 wide) */
0x7e, 0x40, 0x40, 0x40, 0x00, /* chr: 'L'  (4 wide) */
0x7e, 0x04, 0x08, 0x04, 0x7e, /* chr: 'M'  (5 wide) */
0x7e, 0x04, 0x08, 0x10, 0x7e, /* chr: 'N'  (5 wide) */
0x3c, 0x42, 0x42, 0x3c, 0x00, /* chr: 'O'  (4 wide) */
0x7e, 0x12, 0x12, 0x0c, 0x00, /* chr: 'P'  (4 wide) */
0x3c, 0x42, 0x22, 0x5c, 0x00, /* chr: 'Q'  (4 wide) */
0x7e, 0x12, 0x32, 0x4c, 0x00, /* chr: 'R'  (4 wide) */
0x24, 0x4a, 0x52, 0x24, 0x00, /* chr: 'S'  (4 wide) */
0x02, 0x02, 0x7e, 0x02, 0x02, /* chr: 'T'  (5 wide) */
0x3e, 0x40, 0x40, 0x3e, 0x00, /* chr: 'U'  (4 wide) */
0x0e, 0x30, 0x40, 0x30, 0x0e, /* chr: 'V'  (5 wide) */
0x3e, 0x40, 0x20, 0x40, 0x3e, /* chr: 'W'  (5 wide) */
0x42, 0x24, 0x18, 0x24, 0x42, /* chr: 'X'  (5 wide) */
0x06, 0x08, 0x70, 0x08, 0x06, /* chr: 'Y'  (5 wide) */
0x62, 0x52, 0x4a, 0x46, 0x00, /* chr: 'Z'  (4 wide) */
0x7e, 0x42, 0x00, 0x00, 0x00, /* chr: '['  (2 wide) */
0x04, 0x08, 0x10, 0x20, 0x40, /* chr: '\'  (5 wide) */
0x42, 0x7e, 0x00, 0x00, 0x00, /* chr: ']'  (2 wide) */
0x04, 0x02, 0x04, 0x00, 0x00, /* chr: '^'  (3 wide) */
0x40, 0x40, 0x40, 0x40, 0x00  /* chr: '_'  (4 wide) */
};

uint16_t LCD_ReadReg(uint8_t LCD_Reg)
{
   
LCD_REG = LCD_Reg;
return (LCD_RAM);
}

void oled_set_brightness(uint8_t brightness){
	LCD_WriteCommand(0x81);//brightness
	LCD_WriteCommand(brightness);//max
}
void oled_enable(){
  LCD_WriteCommand(0xAF);//off display	
	
}
void oled_disable(){
  LCD_WriteCommand(0xAE);//off display		
}

void oled_start_column(char column){
  LCD_WriteCommand(0x00 + column%16);
  LCD_WriteCommand(0x10+column/16);
}

void oled_char(uint8_t data, char pos, char page){
  uint8_t *char_address = 0;
  char_address = &ssd1306xled_font5x7[(data - 32)*5];

  LCD_WriteCommand(0xB0 | page);
  LCD_WriteCommand(0x04);
  LCD_WriteCommand(0x10); 
  oled_start_column(pos);
  
  for(uint8_t i = 0; i<5; i++){
    
      LCD_WriteData(*char_address);
      char_address++;
  }
  
}
//font5x6
void oled_char_5x6(uint8_t data, char pos, char page){
  uint8_t *char_address = 0;
  if(data == 'z') data = 'Z';
  char_address = &font5x6[(data - 32)*5];

  LCD_WriteCommand(0xB0 | page);
  LCD_WriteCommand(0x04);
  LCD_WriteCommand(0x10); 
  oled_start_column(pos);
  
  LCD_WriteData(0xff);
  for(uint8_t i = 0; i<5; i++){
    
      LCD_WriteData(~(*char_address));
      char_address++;
  }
  
}

void oled_text_inv(char *str, char page){
  /*display text string on oled*/
  char *str_ptr;
  str_ptr = str;
  char position = 4;
  while(*str_ptr != 0){
  oled_char_5x6(*str_ptr, position, page);
  str_ptr++;
  position += 6;
  }
}
void oled_text_custom(char *str, char page, char inv_char_count){
  /*display text string on oled*/
  char *str_ptr;
  str_ptr = str;
  char char_cnt = 0;
  char position = 4;
  while(*str_ptr != 0){
  if(char_cnt < inv_char_count)oled_char_5x6(*str_ptr, position, page);
  else oled_char(*str_ptr, position, page);
  str_ptr++;
  char_cnt++;
  position += 6;
  }
}
void oled_text(char *str, char page){
  /*display text string on oled*/
  char *str_ptr;
  str_ptr = str;
  char position = 4;
  while(*str_ptr != 0){
  oled_char(*str_ptr, position, page);
  str_ptr++;
  position += 6;
  }
}



void oled_init(){
  
  LCD_WriteCommand(0xAE);//off display
  LCD_WriteCommand(0x20);//scanning mode 
  LCD_WriteCommand(0x02);//page mode
  LCD_WriteCommand(0xB0);//start page 0
  LCD_WriteCommand(0xC8);//com0 to com63
  //LCD_WriteCommand(0x00);//col 0
  //LCD_WriteCommand(0x10);//
  LCD_WriteCommand(0x40);//start line
  LCD_WriteCommand(0xff);//brightness
  LCD_WriteCommand(0x30);//max
  LCD_WriteCommand(0xA1);//
  LCD_WriteCommand(0xA6);//normal bits a6 | inverse bits a7
  LCD_WriteCommand(0xA8);
  LCD_WriteCommand(0x1F);
  LCD_WriteCommand(0xA4);
  LCD_WriteCommand(0xd3);//display offset
  LCD_WriteCommand(0x00);
  LCD_WriteCommand(0xd5);//display clock
  LCD_WriteCommand(0x10);
  LCD_WriteCommand(0xd9);
  LCD_WriteCommand(0x22);
  LCD_WriteCommand(0xda);
  LCD_WriteCommand(0x12);
  LCD_WriteCommand(0xdb);
  LCD_WriteCommand(0x20);
  LCD_WriteCommand(0x8D);
  LCD_WriteCommand(0x14);
  LCD_WriteCommand(0xAF);

}

void oled_status_pict(uint8_t oled_icon_blink_state){
  /* input data - current status of params
  forming union of all picts and display on the oled*/
  
for(uint8_t idisp = 0; idisp < 16; idisp++){  
  if(agm.battery == BATTERY_EMPTY){
    display_status_picts[idisp + 112] = battery_empty_pict[idisp + 16];
    display_status_picts[idisp + 240] = battery_empty_pict[idisp];    
  }
  if(agm.battery == BATTERY_1_3){
    display_status_picts[idisp + 112] = battery_1_3_pict[idisp + 16];
    display_status_picts[idisp + 240] = battery_1_3_pict[idisp];    
  }
  if(agm.battery == BATTERY_2_3){
    display_status_picts[idisp + 112] = battery_2_3_pict[idisp + 16];
    display_status_picts[idisp + 240] = battery_2_3_pict[idisp]; 
  }
  if(agm.battery == BATTERY_FULL){
    display_status_picts[idisp + 112] = battery_full_pict[idisp + 16];
    display_status_picts[idisp + 240] = battery_full_pict[idisp];       
  }
  if(agm_option_menu.data_interface == USB_CONNECTION){
    display_status_picts[idisp] = usb_pict[idisp + 16];
    display_status_picts[idisp + 128] = usb_pict[idisp];    
  }
  if(agm_option_menu.data_interface == BLUETOOTH_CONNECTION){
    display_status_picts[idisp] = bluetooth_pict[idisp + 16];
    display_status_picts[idisp + 128] = bluetooth_pict[idisp];    
  }
  if(agm_option_menu.data_interface == NO_CONNECTION){
    display_status_picts[idisp] = null_pict[idisp + 16];
    display_status_picts[idisp + 128] = null_pict[idisp];     
  }
  if(agm.event == NO_EVENT){
    display_status_picts[idisp + 48] = null_pict[idisp + 16];
    display_status_picts[idisp + 176] = null_pict[idisp];    
  }
  if(agm.event == EVENT){
    display_status_picts[idisp + 48] = event_pict[idisp + 16];
    display_status_picts[idisp + 176] = event_pict[idisp];    
  }
  if(agm.gnss == GPS_OFF){
    display_status_picts[idisp + 80] = null_pict[idisp + 16];
    display_status_picts[idisp + 208] = null_pict[idisp];     
  }
  if(agm.gnss == GPS_ERROR){
    display_status_picts[idisp + 80] = gps_disable_pict[idisp + 16];
    display_status_picts[idisp + 208] = gps_disable_pict[idisp];    
  }  
  if(agm.gnss == GPS_ON){
    display_status_picts[idisp + 80] = gps_enable_pict[idisp + 16];
    display_status_picts[idisp + 208] = gps_enable_pict[idisp];      
  }
  if(agm.gnss == GPS_WAIT_DATA){
    if(oled_icon_blink_state == 0){
      display_status_picts[idisp + 80] = null_pict[idisp + 16];
      display_status_picts[idisp + 208] = null_pict[idisp];
    }
    if(oled_icon_blink_state == 1){
      display_status_picts[idisp + 80] = gps_enable_pict[idisp + 16];
      display_status_picts[idisp + 208] = gps_enable_pict[idisp];       
    }
  }//null_pict
  if(agm.gsm == GSM_DISABLE){
    display_status_picts[idisp + 96] = null_pict[idisp + 16];
    display_status_picts[idisp + 224] = null_pict[idisp];    
  }
  if(agm.gsm == GSM_NO_CONNECTION){
    display_status_picts[idisp + 96] = gsm_no_signal_pict[idisp + 16];
    display_status_picts[idisp + 224] = gsm_no_signal_pict[idisp];    
  }
  if(agm.gsm == GSM_1_4){
    display_status_picts[idisp + 96] = gsm_1_4_pict[idisp + 16];
    display_status_picts[idisp + 224] = gsm_1_4_pict[idisp];        
  }
  if(agm.gsm == GSM_2_4){
    display_status_picts[idisp + 96] = gsm_2_4_pict[idisp + 16];
    display_status_picts[idisp + 224] = gsm_2_4_pict[idisp];    
  }    
  if(agm.gsm == GSM_3_4){
    display_status_picts[idisp + 96] = gsm_3_4_pict[idisp + 16];
    display_status_picts[idisp + 224] = gsm_3_4_pict[idisp];    
  }
  if(agm.gsm == GSM_4_4){
    display_status_picts[idisp + 96] = gsm_4_4_pict[idisp + 16];
    display_status_picts[idisp + 224] = gsm_4_4_pict[idisp];    
  }
  if(agm.memory == MEMORY_EMPTY){
    display_status_picts[idisp + 64] = card_empty_pict[idisp + 16];
    display_status_picts[idisp + 192] = card_empty_pict[idisp];    
  }    
  if(agm.memory == MEMORY_25_100){
    display_status_picts[idisp + 64] = card_empty_pict[idisp + 16];
    display_status_picts[idisp + 192] = card_empty_pict[idisp];        
  }
  if(agm.memory == MEMORY_50_100){
    display_status_picts[idisp + 64] = card_half_pict[idisp + 16];
    display_status_picts[idisp + 192] = card_half_pict[idisp];     
  }
  if(agm.memory == MEMORY_75_100){
    display_status_picts[idisp + 64] = card_half_pict[idisp + 16];
    display_status_picts[idisp + 192] = card_half_pict[idisp];     
  }
  if(agm.memory == MEMORY_FULL){
    display_status_picts[idisp + 64] = card_full_pict[idisp + 16];
    display_status_picts[idisp + 192] = card_full_pict[idisp];     
  }
  if(agm.signal == SIGNAL_LF){
    display_status_picts[idisp + 16] = lf_pict[idisp + 16];
    display_status_picts[idisp + 144] = lf_pict[idisp];    
  }
  if(agm.signal == SIGNAL_MAG){
    display_status_picts[idisp + 16] = mag_pict[idisp + 16];
    display_status_picts[idisp + 144] = mag_pict[idisp];    
  }
  if(agm.signal == SIGNAL_LF_MAG){
    display_status_picts[idisp + 16] = mag_lf_pict[idisp + 16];
    display_status_picts[idisp + 144] = mag_lf_pict[idisp];    
  }
  if(agm.state == STATE_STANDBY){
    display_status_picts[idisp + 32] = standby_pict[idisp + 16];
    display_status_picts[idisp + 160] = standby_pict[idisp];    
  }
  if(agm.state == STATE_ACTIVE){
    display_status_picts[idisp + 32] = active_pict[idisp + 16];
    display_status_picts[idisp + 160] = active_pict[idisp];    
  }

}
  LCD_WriteCommand(0xB3);
  LCD_WriteCommand(0x04);
  LCD_WriteCommand(0x10); 
  
  for(uint8_t idisp = 0; idisp < 128; idisp++){
    LCD_WriteData(display_status_picts[idisp]); 
  }
    
  LCD_WriteCommand(0xB2);
  LCD_WriteCommand(0x04);
  LCD_WriteCommand(0x10); 
  for(uint8_t idisp = 0; idisp < 128; idisp++){
    LCD_WriteData(display_status_picts[idisp+128]); 
  }  

}
void sleep_menu(uint8_t blink_pixel){
  oled_clear_string(0);
  char* str_blink = "   standby   ";
  char* str_blink_with_detect = "   detect   ";
  if(blink_pixel == 1){
    if(agm.state == STATE_ACTIVE){
      oled_text(str_blink_with_detect, 1);
      oled_clear_string(2);
      oled_clear_string(3);
      for(uint8_t idisp = 0; idisp <16;idisp++){
        if(agm.event == EVENT){
          display_detect_signal[idisp] = event_pict[idisp + 16];
          display_detect_signal[idisp + 16] = event_pict[idisp];  
        }
        if(agm.event == NO_EVENT){
          display_detect_signal[idisp] = null_pict[idisp + 16];
          display_detect_signal[idisp + 16] = null_pict[idisp];           
        }
      }
      LCD_WriteCommand(0xB3);
      LCD_WriteCommand(0x04);
      LCD_WriteCommand(0x10); 
      oled_start_column(20);  
      for(uint8_t idisp = 0; idisp < 16; idisp++){
        LCD_WriteData(display_detect_signal[idisp]); 
      }
        
      LCD_WriteCommand(0xB2);
      LCD_WriteCommand(0x04);
      LCD_WriteCommand(0x10); 
      oled_start_column(20);  
      
      for(uint8_t idisp = 0; idisp < 16; idisp++){
        LCD_WriteData(display_detect_signal[idisp+16]); 
      }    
    }
    else oled_text(str_blink, 1);
  }
  else{
    oled_clear_string(1);
    oled_clear_string(2);
    oled_clear_string(3);    
  }
        
  
}
void oled_option_menu(uint8_t active_element_state){
  

  
  for(uint8_t oi = 0; oi < 21; oi++){
    if(agm_option_menu.record_mode == 0)oled_buf[0][oi] = record_mode_mag[oi];//mag
    if(agm_option_menu.record_mode == 1)oled_buf[0][oi] = record_mode_lf[oi];//mag
    if(agm_option_menu.record_mode == 2)oled_buf[0][oi] = record_mode_mag_lf[oi];//mag
    
    if(oi < 17)oled_buf[1][oi] = sensitivity_mag[oi];
    else{
        if(agm_option_menu.sensitivity_mag == 10) oled_buf[1][oi] = digit_auto[oi-17];
        else {
          if(oi == 17)oled_buf[1][oi] = digit_char[agm_option_menu.sensitivity_mag];
          else oled_buf[1][oi] = ' ';
  
        }
    }
    if(oi < 17)oled_buf[2][oi] = sensitivity_lf[oi];
    else{
        if(agm_option_menu.sensitivity_lf == 10) oled_buf[2][oi] = digit_auto[oi-17];
        else {
          if(oi == 17)oled_buf[2][oi] = digit_char[agm_option_menu.sensitivity_lf];
          else oled_buf[2][oi] = ' ';
  
        }
    }      
    if(agm_option_menu.data_interface == 0)oled_buf[3][oi] = data_interface_none[oi];
    if(agm_option_menu.data_interface == 1)oled_buf[3][oi] = data_interface_usb[oi];
    if(agm_option_menu.data_interface == 2)oled_buf[3][oi] = data_interface_bl[oi];     
      
    if(agm_option_menu.gsm_gprs == 0)oled_buf[4][oi] = gsm_gprs_no[oi];
    if(agm_option_menu.gsm_gprs == 1)oled_buf[4][oi] = gsm_gprs_yes[oi];      

    if(agm_option_menu.gps_glonass == 0)oled_buf[5][oi] = gps_glonass_no[oi]; 
    if(agm_option_menu.gps_glonass == 1)oled_buf[5][oi] = gps_glonass_yes[oi];

    if(agm_option_menu.download_data == 0)oled_buf[6][oi] = download_data_no[oi];   
    if(agm_option_menu.download_data == 1)oled_buf[6][oi] = download_data_yes[oi];  
    
    if(agm_option_menu.erase_data == 0)oled_buf[7][oi] = erase_data_no[oi]; 
    if(agm_option_menu.erase_data == 1)oled_buf[7][oi] = erase_data_yes[oi]; 
    
    if(agm_option_menu.notch_filter == 0)oled_buf[8][oi] = notch_filter_50[oi]; 
    if(agm_option_menu.notch_filter == 1)oled_buf[8][oi] = notch_filter_60[oi];    
    
    }
  
  
  if(active_element_state == 2) oled_text_inv(oled_buf[0 + menu_ring_cnt], 0);
  if(active_element_state == 1) oled_text(oled_buf[0 + menu_ring_cnt], 0);
  if(active_element_state == 0) oled_clear_string(0);

  if(menu_ring_cnt < 6){
    //oled_text(oled_buf[0 + menu_ring_cnt], 0);
    oled_text(oled_buf[1 + menu_ring_cnt], 1);
    oled_text(oled_buf[2 + menu_ring_cnt], 2);
    oled_text(oled_buf[3 + menu_ring_cnt], 3);
  }
  if(menu_ring_cnt == 6){
    //oled_text(oled_buf[0 + menu_ring_cnt], 0);
    oled_text(oled_buf[1 + menu_ring_cnt], 1);
    oled_text(oled_buf[2 + menu_ring_cnt], 2);
    oled_text(oled_buf[0], 3);    
  }
  if(menu_ring_cnt == 7){
    //oled_text(oled_buf[0 + menu_ring_cnt], 0);
    oled_text(oled_buf[1 + menu_ring_cnt], 1);
    oled_text(oled_buf[0], 2);
    oled_text(oled_buf[1], 3);    
  }
  if(menu_ring_cnt == 8){
    
    oled_text(oled_buf[0], 1);
    oled_text(oled_buf[1], 2);
    oled_text(oled_buf[2], 3);    
  }  
  
  
                      
}   
void oled_clear_string(uint8_t string_num){
  LCD_WriteCommand(0xB0 | string_num);
  LCD_WriteCommand(0x04);
  LCD_WriteCommand(0x10);  
  for(uint16_t disp_i = 0; disp_i<128; disp_i++){
    
    LCD_WriteData(0x00);
    for(uint32_t i = 0; i < 500;i++) asm("nop");
  } 
  
}
void oled_clear(){
  
  LCD_WriteCommand(0xB0);
  LCD_WriteCommand(0x04);
  LCD_WriteCommand(0x10);  
  for(uint16_t disp_i = 0; disp_i<128; disp_i++){
    
    LCD_WriteData(0x00);
    for(uint32_t i = 0; i < 500;i++) asm("nop");
  }
  LCD_WriteCommand(0xB1);
  LCD_WriteCommand(0x04);
  LCD_WriteCommand(0x10);  
  for(uint16_t disp_i = 0; disp_i<128; disp_i++){
    
    LCD_WriteData(0x00);
    for(uint32_t i = 0; i < 500;i++) asm("nop");
  }
  LCD_WriteCommand(0xB2);
  LCD_WriteCommand(0x04);
  LCD_WriteCommand(0x10);  
  for(uint16_t disp_i = 0; disp_i<128; disp_i++){
    
    LCD_WriteData(0x00);
     for(uint32_t i = 0; i < 500;i++) asm("nop");
  }
  LCD_WriteCommand(0xB3);
  LCD_WriteCommand(0x04);
  LCD_WriteCommand(0x10);  
  for(uint16_t disp_i = 0; disp_i<128; disp_i++){
    
    LCD_WriteData(0x00);
    for(uint32_t i = 0; i < 500;i++) asm("nop");
  } 
   
}

void oled_logo(){
  LCD_WriteCommand(0xB0);
  LCD_WriteCommand(0x04);
  LCD_WriteCommand(0x10);  
  for(uint16_t disp_i = 0; disp_i<128; disp_i++){
    
    LCD_WriteData(display_logo[disp_i]);
    for(uint32_t i = 0; i < 500;i++) asm("nop");
  }
  LCD_WriteCommand(0xB1);
  LCD_WriteCommand(0x04);
  LCD_WriteCommand(0x10);  
  for(uint16_t disp_i = 0; disp_i<128; disp_i++){
    
    LCD_WriteData(display_logo[disp_i+128]);
    for(uint32_t i = 0; i < 500;i++) asm("nop");
  }  
  LCD_WriteCommand(0xB2);
  LCD_WriteCommand(0x04);
  LCD_WriteCommand(0x10);  
  for(uint16_t disp_i = 0; disp_i<128; disp_i++){
    
    LCD_WriteData(display_logo[disp_i+256]);
    for(uint32_t i = 0;i < 500;i++) asm("nop");
  }  
  LCD_WriteCommand(0xB3);
  LCD_WriteCommand(0x04);
  LCD_WriteCommand(0x10);  
  for(uint16_t disp_i = 0; disp_i<128; disp_i++){
    
    LCD_WriteData(display_logo[disp_i+384]);
    for(uint32_t i = 0; i < 500;i++) asm("nop");
  }  
}


/*



extern uint8_t lf_pict[], mag_pict[], mag_lf_pict[], usb_pict[], bluetooth_pict[], battery_empty_pict[], battery_onethird_pict[], battery_twothird_pict[], battery_full_pict[];
extern uint8_t gsm_disable_pict[], gsm_1_4_pict[], gsm_2_4_pict[], gsm_3_4_pict[], gsm_4_4_pict[], gsm_no_signal_pict[], gps_enable_pict[], gps_disable_pict[];
extern uint8_t event_pict[], standby_pict[], active_pict[], card_empty_pict[], card_half_pict[], card_full_pict[], null_pict[];
extern uint8_t display_status_picts[256];



  for(uint16_t idisp = 0; idisp < 16; idisp++){
    display_status_picts[idisp] = bluetooth_pict[idisp + 16];
    display_status_picts[idisp + 16] = mag_pict[idisp + 16];
    display_status_picts[idisp + 32] = standby_pict[idisp + 16];
    display_status_picts[idisp + 48] = event_pict[idisp + 16];
    display_status_picts[idisp + 64] = card_empty_pict[idisp + 16];
    display_status_picts[idisp + 80] = battery_twothird_pict[idisp + 16];
    display_status_picts[idisp + 96] = gsm_4_4_pict[idisp + 16];
    display_status_picts[idisp + 112] = gps_enable_pict[idisp + 16];
   
    display_status_picts[idisp + 128] = bluetooth_pict[idisp];
    display_status_picts[idisp + 144] = mag_pict[idisp];
    display_status_picts[idisp + 160] = standby_pict[idisp];
    display_status_picts[idisp + 176] = event_pict[idisp];
    display_status_picts[idisp + 192] = card_empty_pict[idisp];
    display_status_picts[idisp + 208] = battery_twothird_pict[idisp];
    display_status_picts[idisp + 224] = gsm_4_4_pict[idisp];
    display_status_picts[idisp + 240] = gps_enable_pict[idisp];
   
  }
  LCD_WriteCommand(0xB0);
  LCD_WriteCommand(0x04);
  LCD_WriteCommand(0x10);  
  for(uint16_t disp_i = 0; disp_i<128; disp_i++){
    
    LCD_WriteData(0x00);
    for(uint32_t i = 0; i < 2000;i++) asm("nop");
  }
  LCD_WriteCommand(0xB1);
  LCD_WriteCommand(0x04);
  LCD_WriteCommand(0x10);  
  for(uint16_t disp_i = 0; disp_i<128; disp_i++){
    
    LCD_WriteData(0x00);
    for(uint32_t i = 0; i < 2000;i++) asm("nop");
  }
  LCD_WriteCommand(0xB2);
  LCD_WriteCommand(0x04);
  LCD_WriteCommand(0x10);  
  for(uint16_t disp_i = 0; disp_i<128; disp_i++){
    
    LCD_WriteData(0x00);
     for(uint32_t i = 0; i < 2000;i++) asm("nop");
  }
  LCD_WriteCommand(0xB3);
  LCD_WriteCommand(0x04);
  LCD_WriteCommand(0x10);  
  for(uint16_t disp_i = 0; disp_i<128; disp_i++){
    
    LCD_WriteData(0x00);
    for(uint32_t i = 0; i < 2000;i++) asm("nop");
  }  
  
  
  for(uint16_t idisp = 0; idisp < 16; idisp++){
    display_status_picts[idisp] = bluetooth_pict[idisp + 16];
    display_status_picts[idisp + 16] = mag_pict[idisp + 16];
    display_status_picts[idisp + 32] = standby_pict[idisp + 16];
    display_status_picts[idisp + 48] = event_pict[idisp + 16];
    display_status_picts[idisp + 64] = card_empty_pict[idisp + 16];
    display_status_picts[idisp + 80] = battery_2_3_pict[idisp + 16];
    display_status_picts[idisp + 96] = gsm_4_4_pict[idisp + 16];
    display_status_picts[idisp + 112] = gps_enable_pict[idisp + 16];
   
    display_status_picts[idisp + 128] = bluetooth_pict[idisp];
    display_status_picts[idisp + 144] = mag_pict[idisp];
    display_status_picts[idisp + 160] = standby_pict[idisp];
    display_status_picts[idisp + 176] = event_pict[idisp];
    display_status_picts[idisp + 192] = card_empty_pict[idisp];
    display_status_picts[idisp + 208] = battery_2_3_pict[idisp];
    display_status_picts[idisp + 224] = gsm_4_4_pict[idisp];
    display_status_picts[idisp + 240] = gps_enable_pict[idisp];
   
  }
  
  LCD_WriteCommand(0xB3);
  LCD_WriteCommand(0x06);
  LCD_WriteCommand(0x10); 
  
  for(uint8_t idisp = 0; idisp < 128; idisp++){
    LCD_WriteData(display_status_picts[idisp]); 
  }
    
  
  LCD_WriteCommand(0xB2);
  LCD_WriteCommand(0x06);
  LCD_WriteCommand(0x10); 
  for(uint8_t idisp = 0; idisp < 128; idisp++){
    LCD_WriteData(display_status_picts[idisp+128]); 
  }
    
*/