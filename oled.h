#include "stm32l4xx.h"
#include "main.h"

#define LCD_REG (*((volatile unsigned char *) 0x60000000))
#define LCD_RAM (*((volatile unsigned char *) 0x60000001))
#define LCD_WriteCommand(cmd) { LCD_REG = cmd; }
#define LCD_WriteData(data) { LCD_RAM = data; }
#define LCD_WriteCmd(cmd, data){LCD_REG=cmd;LCD_RAM=data;}


#define BATTERY_EMPTY 0
#define BATTERY_1_3 1
#define BATTERY_2_3 2
#define BATTERY_FULL 3

#define NO_CONNECTION 0
#define USB_CONNECTION 1
#define BLUETOOTH_CONNECTION 2

#define NO_EVENT 0
#define EVENT 1

#define GPS_WAIT_DATA 3
#define GPS_ERROR 2
#define GPS_OFF 0 
#define GPS_ON 1

#define GSM_DISABLE 0 
#define GSM_NO_CONNECTION 1
#define GSM_1_4 2
#define GSM_2_4 3
#define GSM_3_4 4
#define GSM_4_4 5

#define MEMORY_EMPTY 0
#define MEMORY_25_100 1
#define MEMORY_50_100 2
#define MEMORY_75_100 3
#define MEMORY_FULL 4

#define SIGNAL_LF 0
#define SIGNAL_MAG 1
#define SIGNAL_LF_MAG 2

#define STATE_STANDBY 0
#define STATE_ACTIVE 1

struct device_status_struct{
 uint16_t serial_number;
 uint8_t connection;
 uint8_t signal;
 uint8_t state;
 uint8_t event;
 uint8_t memory;
 uint8_t battery;
 uint8_t gsm;
 uint8_t gnss;
  
};
extern struct device_status_struct agm;


struct option_menu{
  uint8_t record_mode; //MAG - 0 LF - 1 MAG_LF - 2
  uint8_t sensitivity_mag;//AUTO - 10 0-9
  uint8_t sensitivity_lf;//AUTO - 10  0-9
  uint8_t data_interface;//BT - 2 USB - 1 NONE - 0
  uint8_t gsm_gprs;//Yes - 1 No - 0
  uint8_t gps_glonass;//Yes - 1 No - 0
  uint8_t download_data;//Yes - 1 No - 0
  uint8_t erase_data;//Yes - 1 No - 0
  uint8_t notch_filter;//50Hz - 0 60Hz - 1
};
extern struct option_menu agm_option_menu;


void oled_status_pict(uint8_t oled_icon_blink_state);
void oled_char(uint8_t data, char pos, char page);
void oled_text(char *str, char page);
void oled_set_brightness(uint8_t brightness);
void oled_enable();
void oled_disable();
void oled_start_column(char column);
void oled_init();
void oled_clear();
void oled_logo();
void oled_option_menu(uint8_t active_element_state);
void oled_clear_string(uint8_t string_num);
void sleep_menu(uint8_t blink_pixel);
void oled_text_inv(char *str, char page);
void oled_text_custom(char *str, char page, char inv_char_count);