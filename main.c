/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * This notice applies to any and all portions of this file
  * that are not between comment pairs USER CODE BEGIN and
  * USER CODE END. Other portions of this file, whether 
  * inserted by the user or by software development tools
  * are owned by their respective copyright owners.
  *
  * Copyright (c) 2019 STMicroelectronics International N.V. 
  * All rights reserved.
  *
  * Redistribution and use in source and binary forms, with or without 
  * modification, are permitted, provided that the following conditions are met:
  *
  * 1. Redistribution of source code must retain the above copyright notice, 
  *    this list of conditions and the following disclaimer.
  * 2. Redistributions in binary form must reproduce the above copyright notice,
  *    this list of conditions and the following disclaimer in the documentation
  *    and/or other materials provided with the distribution.
  * 3. Neither the name of STMicroelectronics nor the names of other 
  *    contributors to this software may be used to endorse or promote products 
  *    derived from this software without specific written permission.
  * 4. This software, including modifications and/or derivative works of this 
  *    software, must execute solely and exclusively on microcontroller or
  *    microprocessor devices manufactured by or for STMicroelectronics.
  * 5. Redistribution and use of this software other than as permitted under 
  *    this license is void and will automatically terminate your rights under 
  *    this license. 
  *
  * THIS SOFTWARE IS PROVIDED BY STMICROELECTRONICS AND CONTRIBUTORS "AS IS" 
  * AND ANY EXPRESS, IMPLIED OR STATUTORY WARRANTIES, INCLUDING, BUT NOT 
  * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
  * PARTICULAR PURPOSE AND NON-INFRINGEMENT OF THIRD PARTY INTELLECTUAL PROPERTY
  * RIGHTS ARE DISCLAIMED TO THE FULLEST EXTENT PERMITTED BY LAW. IN NO EVENT 
  * SHALL STMICROELECTRONICS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
  * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
  * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, 
  * OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
  * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING 
  * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
  * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "usb_device.h"
#include "usbd_cdc.h"
#include "usbd_cdc_if.h" 
/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "oled.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */


void* p = (void *)0x60000001; 
void* adr = (void *)0x60000000; 

void* fram_adr = (void *)0x60020000;
#define WRITE_READ_ADDR     ((uint32_t)0x0020)
#define SRAM_BANK_ADDR                 ((uint32_t)0x64000000 )

extern uint8_t lf_pict[], mag_pict[], mag_lf_pict[], usb_pict[], bluetooth_pict[], battery_empty_pict[], battery_1_3_pict[], battery_2_3_pict[], battery_full_pict[];
extern uint8_t gsm_disable_pict[], gsm_1_4_pict[], gsm_2_4_pict[], gsm_3_4_pict[], gsm_4_4_pict[], gsm_no_signal_pict[], gps_enable_pict[], gps_disable_pict[];
extern uint8_t event_pict[], standby_pict[], active_pict[], card_empty_pict[], card_half_pict[], card_full_pict[], null_pict[];
extern uint8_t display_status_picts[256];
extern uint8_t display_detect_signal[256];
extern uint32_t _agm_sleep_timer;
extern uint8_t sleep_mode_state;
uint8_t buf_len = 30;
unsigned short* fram_address = (unsigned short *) 0x60000000;
uint8_t record_start = 0;
uint16_t temp_buf[100];
uint32_t usb_offset = 0;
uint32_t timer_value = 0;
uint8_t check_powerdown_gps = 0;
uint8_t uart_buf[100];
uint16_t gnss_startup_delay = 0;

uint8_t transmitBuffer[32];
uint8_t receiveBuffer[200], baudrate_status[100], gnss_power_status[50];

uint8_t rtc_lse_error = 0;

uint8_t usb_sending_data = 0;
uint8_t notch_filter_configure = 0, adc_m_cnt = 0;   
uint8_t notch_50Hz_value = 90, notch_60Hz_value = 51;
uint8_t notch_type = 0;
uint16_t adc_m[25];

uint16_t record_start_delay_cnt = 0; 
uint8_t record_start_delay_done = 0;
uint32_t temp_fram_address_cnt = 0;

uint8_t at_wakeup_try = 3;
uint8_t gps_latch_done = 0, gps_latch_cnt = 0;
uint32_t gps_latch_timer = 0;
uint8_t I2C_TxBuffer[10];
uint8_t I2C_TxBuffer_Notch[4];
extern uint8_t gain_update;
uint8_t result_gain_coef = 0;
char oled_buf[9][25];
char menu_ring_cnt = 0;
char menu_level = 3;
extern uint16_t logo_delay;
uint8_t agm_standby_active_mode = 0;
#define MODE_ACTIVE  1
#define MODE_STANDBY 0 
uint8_t gnss_reset_pulse_enable = 0;
uint8_t comma_cnt = 0, gps_date_offset = 0;
uint8_t gps_oled_string[23];

extern uint8_t  uartCntRx, uartCntTx;
char gll_received = 1;
uint32_t gps_update_data_timer = 0;
uint16_t time_update_cnt = 10000;
uint8_t error_led_state = 0;
uint32_t record_length_enough_cnt = 0;
uint8_t record_length_enough = 0;
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc1;

I2C_HandleTypeDef hi2c1;

RTC_HandleTypeDef hrtc;
RTC_HandleTypeDef RtcHandle;

UART_HandleTypeDef huart2;

SRAM_HandleTypeDef hsram1;
SRAM_HandleTypeDef hsram2;

/* USER CODE BEGIN PV */

uint8_t option_menu_active_element = 0;

uint8_t standby_press_cnt = 0;

uint16_t keys_timer = 0;
uint16_t key1_cnt = 0;
uint8_t key1_prestate = 0, key1_state = 0, key1_press_cnt = 0;
uint16_t key2_cnt = 0;
uint8_t key2_prestate = 0, key2_state = 0, key2_press_cnt = 0;
uint16_t key3_cnt = 0;
uint8_t key3_prestate = 0, key3_state = 0, key3_press_cnt = 0;

uint8_t key1_lock = 0, key1_long_press_enable = 0, key1_short_press_enable = 0, key1_press_flag = 0;
uint8_t key2_lock = 0, key2_long_press_enable = 0, key2_short_press_enable = 0, key2_press_flag = 0;
uint8_t key3_lock = 0, key3_long_press_enable = 0, key3_short_press_enable = 0, key3_press_flag = 0;


uint8_t fram_erase_event = 0, gps_event = 0, gsm_event = 0, notch_filter_event = 0;
uint8_t sensitivity_mag_event = 0;

uint8_t fram_gps_state = 0;

uint16_t sram_tx_buf[10];
uint16_t sram_rx_buf[10];

uint16_t temp_min_value = 4095, temp_max_value = 0;
uint16_t buf_tail = 0, buf_head = 0, temp_tail_sleep = 0;
uint8_t write_from_buf_cnt = 0;
uint8_t temp_fram_write_event = 0, buf_len_cnt = 0, record_number = 0;;
uint16_t recordHeader[20];
uint8_t record_state = 0, record_prestate = 0;
uint8_t mag_sens_auto_enable = 0;
uint8_t buff[10] = {0,};
uint8_t callback_rx_cnt = 0, uart_rx_buf_callback[100];
uint8_t gps_packet_receive_status = 0, gps_parser_flag = 0, pwrup_seq_done = 0, gnss_startup_state = 0, gps_cnt_status = 0;
uint16_t temp_recordCnt = 0;
struct gps_status_struct{
 uint8_t latitude_hi;
 uint16_t latitude_lo;
 uint8_t latitude_direction;
 uint16_t longitude_hi;
 uint16_t longitude_lo;
 uint8_t longitude_direction;
 uint8_t utc_time_hh;
 uint8_t utc_time_mm;
 uint8_t utc_time_ss;
 uint16_t utc_time_sss;//milisec
 uint8_t utc_date_day;
 uint8_t utc_date_month;
 uint8_t utc_date_year;
  
}agm_gps_status;

uint32_t backupReadData = 0, test_point = 0;

uint8_t buff_temp[200], buff_temp_cnt = 0;
uint8_t buzzer_alarm = 0;
extern unsigned int led_toggle;
extern uint8_t UserRxBufferFS[64];
extern uint8_t UserTxBufferFS[64];
uint16_t temp_dataRecord[2048];
uint32_t usb_block_offset = 0;
uint16_t usb_block_buf[20];
extern uint16_t adc_ch1, adc_ch2;
extern uint8_t ssd1306xled_font5x7[];
extern const uint8_t ssd1306xled_font6x8[];

struct device_status_struct agm;
struct option_menu agm_option_menu;
extern USBD_HandleTypeDef hUsbDeviceFS;
extern float voltage_monitor;

RTC_TimeTypeDef    sTime, recordTime;
RTC_DateTypeDef    DateToUpdate, recordDate;

RTC_TimeTypeDef    sTime_set;
RTC_DateTypeDef    DateToUpdate_set;


uint32_t _fram_address_cnt = 0, card_watcher =0;

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_FMC_Init(void);
static void MX_USART2_UART_Init(void);
static void MX_I2C1_Init(void);
static void MX_ADC1_Init(void);
static void MX_RTC_Init(void);
uint8_t CDC_Transmit_FS(uint8_t* Buf, uint16_t Len);
uint8_t rtc_Init();

static void calendarInit(void);
static void rtcInit(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */


/******************************************************************************/
void delay_nop(uint32_t delay){//delay in mcu ticks | replace by system timer cnt?
  for(uint32_t idelay = 0; idelay<delay; idelay++){
    asm("nop");
  }
}
/******************************************************************************/
void fram_write_buf(uint16_t *data, uint8_t buf_length){
  if(_fram_address_cnt < 262144){
    HAL_SRAM_WriteOperation_Disable( &hsram1); 
    for (uint8_t uwIndex = 0; uwIndex < buf_length; uwIndex++){
      *(__IO uint16_t*) (SRAM_BANK_ADDR + WRITE_READ_ADDR + 2*_fram_address_cnt++) = data[uwIndex];
    }  
    HAL_SRAM_WriteOperation_Enable( &hsram1);
  }
}
/******************************************************************************/
void fram_read_buf(uint16_t *data, uint8_t buf_length, uint32_t addr_offset){
  HAL_SRAM_WriteOperation_Disable( &hsram1); 
  for (uint8_t uwIndex = 0; uwIndex < buf_length; uwIndex++){
    data[uwIndex] = *(__IO uint16_t*) (SRAM_BANK_ADDR + WRITE_READ_ADDR + 2*uwIndex + addr_offset*2);//sram_rx_buf
  } 
  HAL_SRAM_WriteOperation_Enable( &hsram1);          
}
/******************************************************************************/
void fram_write_settings(uint16_t data, uint8_t setting_addr){
  HAL_SRAM_WriteOperation_Disable( &hsram1); 
    *(__IO uint16_t*) (SRAM_BANK_ADDR + 2*setting_addr) = data;
  HAL_SRAM_WriteOperation_Enable( &hsram1);
}
uint16_t fram_read_settings(uint8_t setting_addr){
  uint16_t rdata = 0;
  HAL_SRAM_WriteOperation_Disable( &hsram1); 
  rdata = *(__IO uint16_t*) (SRAM_BANK_ADDR + 2*setting_addr);//sram_rx_buf
  HAL_SRAM_WriteOperation_Enable( &hsram1);
  return rdata;
}
/******************************************************************************/
void fram_write_data(uint16_t data){
  HAL_SRAM_WriteOperation_Disable( &hsram1); 
    *(__IO uint16_t*) (SRAM_BANK_ADDR + WRITE_READ_ADDR + 2*_fram_address_cnt++) = data;
    card_watcher = _fram_address_cnt;
  HAL_SRAM_WriteOperation_Enable( &hsram1);
}
/******************************************************************************/
void threshold_buffer(uint16_t data_input, uint16_t threshold){	
	temp_buf[buf_head++] = data_input; 
        if(buf_head >= 30)buf_head = 0;
        if(buf_len_cnt<30){buf_len_cnt++;write_from_buf_cnt++;}
        if(buf_len_cnt>=30){            
          if(write_from_buf_cnt <30) write_from_buf_cnt++;
            
          temp_max_value = 0;
          temp_min_value = 4095;    
          for(uint8_t iminmax = 0; iminmax < 29; iminmax++){
            if(temp_buf[iminmax] > temp_max_value) temp_max_value = temp_buf[iminmax];
            if(temp_buf[iminmax] < temp_min_value) temp_min_value = temp_buf[iminmax];
          }
          //Exceed threshold? yes -> send from buff, no stop writing
          
          if((temp_max_value - temp_min_value) > threshold){
            if(write_from_buf_cnt >= 30){
              temp_fram_write_event = 1;
              if(record_state != 1)record_start = 1;
              record_state = 1;   
            }
            else{
              temp_fram_write_event = 1;
              record_state = 1; 
              record_start = 0;//no header, continue last record
              write_from_buf_cnt--;
            }
          }
          else{
            //if(write_from_buf_cnt <11)write_from_buf_cnt++;//increment counter, which indicates how much data write to fram
            //write_from_buf_cnt = 30;
            buzzer_alarm = 0;
            //HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, GPIO_PIN_RESET);//disable buzzer
            temp_fram_write_event = 0;
            //agm.event = 0;//no event
            record_state = 0;
          }
          
          if(temp_fram_write_event == 1){
             HAL_RTC_GetTime(&hrtc, &sTime, RTC_FORMAT_BIN); // RTC_FORMAT_BIN , RTC_FORMAT_BCD
             HAL_RTC_GetDate(&hrtc, &DateToUpdate, RTC_FORMAT_BIN);
             recordTime.Seconds = sTime.Seconds;
             recordTime.Minutes = sTime.Minutes;
             recordTime.Hours = sTime.Hours;
             recordDate.Date = DateToUpdate.Date;
             recordDate.Month = DateToUpdate.Month;
             recordDate.Year = DateToUpdate.Year;
             agm.event = EVENT;
             if(record_start == 1){
               record_length_enough_cnt = 5001;
               record_length_enough = 0;
               temp_fram_address_cnt = _fram_address_cnt;
               buzzer_alarm = 1;
               record_number++;
               recordHeader[0] = 0x0000;
               recordHeader[1] = 0xAA55;
               recordHeader[2] = record_number;
               recordHeader[3] = agm_option_menu.record_mode;
               recordHeader[4] = agm_gps_status.latitude_hi;
               recordHeader[5] = agm_gps_status.latitude_lo;
               recordHeader[6] = agm_gps_status.latitude_direction;
               recordHeader[7] = agm_gps_status.longitude_hi;
               recordHeader[8] = agm_gps_status.longitude_lo;
               recordHeader[9] = agm_gps_status.longitude_direction;
               recordHeader[10] = recordDate.Date;//agm_gps_status.utc_date_day;
               recordHeader[11] = recordDate.Month;//agm_gps_status.utc_date_month;
               recordHeader[12] = recordDate.Year;//agm_gps_status.utc_date_year;
               recordHeader[13] = recordTime.Hours;//agm_gps_status.utc_time_hh;
               recordHeader[14] = recordTime.Minutes;//agm_gps_status.utc_time_mm;
               recordHeader[15] = recordTime.Seconds;//agm_gps_status.utc_time_ss;
               recordHeader[16] = (uint8_t)(agm_gps_status.utc_time_sss>>8);
               
               fram_write_buf(recordHeader, 17);//write header at start of record
               
               for(uint8_t fram_i = 0; fram_i <29;fram_i++){
                    fram_write_data(temp_buf[buf_tail++]);
                    if(buf_tail >= 30) buf_tail = 0;
                    
               }
               
               
               //if(_fram_address_cnt <= (262144-WRITE_READ_ADDR))_fram_address_cnt++;
              record_start = 0;
             }
             if((record_start == 0)&&(write_from_buf_cnt<30)){
               buzzer_alarm = 1;//fix buzzer long record interrupt
               if(write_from_buf_cnt != 0){
                 for(uint8_t fram_i = 0; fram_i <write_from_buf_cnt;fram_i++){
                      fram_write_data(temp_buf[buf_tail++]);
                      if(buf_tail >= 30) buf_tail = 0;
                      
                 }               
               }
               fram_write_data(data_input);
               write_from_buf_cnt = 0;
             }
             if((record_start == 0)&&(write_from_buf_cnt==30)){
               fram_write_data(data_input);  
               
             }             
          }
          else {
            if(record_prestate == 1){
              for(uint8_t fram_i = 0; fram_i < 29;fram_i++){
                   fram_write_data(temp_buf[buf_tail++]);
                   if(buf_tail >= 30) buf_tail = 0;
                   write_from_buf_cnt = 0;
                   //write_from_buf_cnt--;
              }              
              fram_write_settings((uint16_t)(_fram_address_cnt>>16), 6);
              fram_write_settings((uint16_t)(_fram_address_cnt&0xffff), 7);
              fram_write_settings(record_number, 8);
              if((record_length_enough == 0)&&(record_length_enough_cnt != 0)){
                record_number -= 1;
                record_length_enough_cnt = 0;
                fram_write_settings(record_number, 8);
                _fram_address_cnt = temp_fram_address_cnt;
                fram_write_settings((uint16_t)(_fram_address_cnt>>16), 6);
                fram_write_settings((uint16_t)(_fram_address_cnt&0xffff), 7);                
              }
            }
             //need shift tail for except colisions
             temp_tail_sleep++;
             if(temp_tail_sleep > buf_len)buf_tail++;
          } 
          record_prestate = record_state;
        }	
}
/******************************************************************************/
void timer_init(){
  LL_APB1_GRP1_EnableClock(LL_APB1_GRP1_PERIPH_TIM7);
  LL_TIM_InitTypeDef TIM_InitStructure;
  LL_TIM_StructInit(&TIM_InitStructure);
  
  TIM_InitStructure.Autoreload = 99;
  TIM_InitStructure.ClockDivision = LL_TIM_CLOCKDIVISION_DIV1;
  TIM_InitStructure.CounterMode = LL_TIM_COUNTERMODE_UP;
  TIM_InitStructure.Prescaler = 47;//71  1MHz clk
  //TIM_InitStructure.RepetitionCounter = 0x00;
  LL_TIM_Init(TIM7, &TIM_InitStructure);
 
  LL_TIM_EnableUpdateEvent(TIM7);
  NVIC_SetPriority(TIM7_IRQn, NVIC_EncodePriority(NVIC_GetPriorityGrouping(),0, 0));
  LL_TIM_EnableIT_UPDATE(TIM7);
  NVIC_EnableIRQ(TIM7_IRQn); 
  //LL_TIM_SetUpdateSource(TIM7, LL_TIM_UPDATESOURCE_COUNTER);
  //LL_TIM_EnableARRPreload(TIM7);
  
  LL_TIM_EnableCounter(TIM7);
  //LL_TIM_DisableCounter(TIM7);
  /* TIM7 interrupt Init */ 
}
/******************************************************************************/
void I2C_SetNotchFreq(I2C_HandleTypeDef hi, uint8_t DEV_ADDR, uint8_t sizebuf){
    //while(HAL_I2C_Master_Transmit(&hi, (uint16_t)DEV_ADDR,(uint8_t*) &I2C_TxBuffer_Notch, (uint16_t)sizebuf, (uint32_t)1000)!= HAL_OK){
    //    if (HAL_I2C_GetError(&hi) == HAL_I2C_ERROR_AF)break;
        
        
    //}
    HAL_I2C_Master_Transmit(&hi, (uint16_t)DEV_ADDR,(uint8_t*) &I2C_TxBuffer_Notch, (uint16_t)sizebuf, (uint32_t)1000);
}
/******************************************************************************/
void I2C_ReadBuffer(I2C_HandleTypeDef hi, uint8_t DEV_ADDR, uint8_t sizebuf){
  while(HAL_I2C_Master_Receive(&hi, (uint16_t)DEV_ADDR, (uint8_t*) &I2C_TxBuffer, (uint16_t)sizebuf, (uint32_t)1000)!= HAL_OK)if (HAL_I2C_GetError(&hi) == HAL_I2C_ERROR_AF)break;
}
/******************************************************************************/
void I2C_WriteBuffer(I2C_HandleTypeDef hi, uint8_t DEV_ADDR, uint8_t sizebuf){
    //while(HAL_I2C_Master_Transmit(&hi, (uint16_t)DEV_ADDR,(uint8_t*) &I2C_TxBuffer, (uint16_t)sizebuf, (uint32_t)1000)!= HAL_OK){
    //    if (HAL_I2C_GetError(&hi) == HAL_I2C_ERROR_AF)break;
    //}
    HAL_I2C_Master_Transmit(&hi, (uint16_t)DEV_ADDR,(uint8_t*) &I2C_TxBuffer, (uint16_t)sizebuf, (uint32_t)1000);
}
/******************************************************************************/
void AFE_gain_auto(){
  I2C_TxBuffer[0] = 0x10;
  I2C_TxBuffer[1] = 202;
  uint8_t gain_find = 0;
  uint16_t gain_threshold = 200;
  
  while(gain_find != 1){
    I2C_TxBuffer[1] -= 2;  
    uint16_t gain_max_in_buf = 0;
    uint16_t gain_min_in_buf = 4095;
    uint16_t gain_databuf[20];
    
    I2C_WriteBuffer(hi2c1, 0x58, 2);
    for(uint16_t igain = 0; igain < 10000; igain++) asm("nop");
    for(uint8_t igain = 0; igain < 10; igain++){
      while(gain_update != 1);
      gain_update = 0;
      gain_databuf[igain] = adc_ch1;
      
      if(gain_databuf[igain] > gain_max_in_buf) gain_max_in_buf = gain_databuf[igain];
      if(gain_databuf[igain] < gain_min_in_buf) gain_min_in_buf = gain_databuf[igain];
      
      if(igain != 0) if(gain_max_in_buf - gain_min_in_buf > gain_threshold) gain_find = 1;
    }
    if(I2C_TxBuffer[1] <= 50) gain_find = 1;
  }
  I2C_TxBuffer[1] += 2;
  result_gain_coef = I2C_TxBuffer[1];
}
/******************************************************************************/
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart){
  if(huart == &huart2){
    HAL_UART_Receive_IT(&huart2, (uint8_t*)buff, 1);
    buff_temp[buff_temp_cnt++] = buff[0];
    if(buff_temp_cnt >= 200)buff_temp_cnt = 0;
    if((buff[0] == '$') || (gps_packet_receive_status == 1)){
      gps_packet_receive_status = 1;
      uart_rx_buf_callback[callback_rx_cnt++] = buff[0];
      
      if(uart_rx_buf_callback[callback_rx_cnt-1] == '*'){
        gps_packet_receive_status = 0;
        callback_rx_cnt = 0;
        gps_parser_flag = 1;
      }
    }
 
  }//usart2 callback 
}

void usb_tx(){
    if(((UserRxBufferFS[0] == 0x7f) && (UserRxBufferFS[1] == 0xaa))||(usb_sending_data == 1)){
      
      if(usb_sending_data == 1){
          usb_offset += 32;
          if(usb_offset>=temp_recordCnt)usb_sending_data = 0;
          //temp_recordCnt = fram_read_settings(7);
          fram_read_buf(temp_dataRecord, 32, usb_offset);

          for(uint8_t usb_i = 0; usb_i < 32; usb_i++){
            UserTxBufferFS[2*usb_i] = (uint8_t)(temp_dataRecord[usb_i]>>8);
            UserTxBufferFS[2*usb_i+1] = (uint8_t)temp_dataRecord[usb_i];
            
          }
          CDC_Transmit_FS(UserTxBufferFS, 64);
                 
      }
      
      else{ //(usb_sending_data == 0){
        if(UserRxBufferFS[3] == 0x01){//opCode for sending records data
          temp_recordCnt = fram_read_settings(7);
          usb_offset = 0;
          fram_read_buf(temp_dataRecord, 32, 0);
          UserTxBufferFS[0] = (uint8_t)(temp_recordCnt>>24);
          UserTxBufferFS[1] = (uint8_t)(temp_recordCnt>>16);
          UserTxBufferFS[2] = (uint8_t)(temp_recordCnt>>8);
          UserTxBufferFS[3] = (uint8_t)(temp_recordCnt&0xff);

          for(uint8_t usb_i = 0; usb_i < 30; usb_i++){//28
            UserTxBufferFS[2*usb_i+4] = (uint8_t)(temp_dataRecord[usb_i]>>8);
            UserTxBufferFS[2*usb_i+5] = (uint8_t)temp_dataRecord[usb_i];
            
          }
          
          //for(uint32_t i_usb = 0; i_usb<(2*temp_recordCnt);i_usb++){
          //  UserTxBufferFS[2*i_usb+4] = (uint8_t)(temp_dataRecord[i_usb]>>8);
          //  UserTxBufferFS[2*i_usb+5] = (uint8_t)(temp_dataRecord[i_usb]&0xff);
          //}
                
          CDC_Transmit_FS(UserTxBufferFS, 64);
          usb_sending_data = 1;
       
        }//opcode 0x01
        if(UserRxBufferFS[3] == 0x02){
          agm.serial_number = (UserRxBufferFS[4]<<8)|(UserRxBufferFS[5]);
          fram_write_settings(agm.serial_number, 10);
          
          //CDC_Transmit_FS(UserTxBufferFS, 2048);
        }
        if(UserRxBufferFS[3] == 0x03){
          //agm.serial_number = (UserRxBufferFS[4]<<8)|(UserRxBufferFS[5]);
          //fram_write_settings(agm.serial_number, 10);
          fram_erase_event = 1;
          //CDC_Transmit_FS(UserTxBufferFS, 2048);
        }
        if(UserRxBufferFS[3] == 0x04){
          notch_filter_event = 1; 
          if(UserRxBufferFS[4] == 0x00)agm_option_menu.notch_filter = 0;//50Hz
          if(UserRxBufferFS[4] == 0x01)agm_option_menu.notch_filter = 1;//60Hz
          //CDC_Transmit_FS(UserTxBufferFS, 2048);
        }  
        if(UserRxBufferFS[3] == 0x05){//utc timezone

          //CDC_Transmit_FS(UserTxBufferFS, 2048);
        }
        if(UserRxBufferFS[3] == 0x06){//afe configure

          I2C_TxBuffer_Notch[0] = 0x10;
          I2C_TxBuffer_Notch[1] = UserRxBufferFS[4];
          I2C_SetNotchFreq(hi2c1, 0x5e, 2);
          
          notch_filter_configure = 1;
          while(notch_filter_configure == 1);
          UserTxBufferFS[0] = 0x00;
          UserTxBufferFS[1] = 0x00;
          UserTxBufferFS[2] = 0xaa;
          UserTxBufferFS[3] = 0x5e;
          for(uint8_t notch_i = 0; notch_i < 20; notch_i++){
            
            UserTxBufferFS[2*notch_i+4] = (uint8_t)(adc_m[notch_i]>>8);
            UserTxBufferFS[2*notch_i+1+4] = (uint8_t)(adc_m[notch_i]&0xff);
          }
       
          CDC_Transmit_FS(UserTxBufferFS, 64);
        }
        if(UserRxBufferFS[3] == 0x07){//update notch filter potentiometr value
          if(UserRxBufferFS[4] == 0) notch_50Hz_value = UserRxBufferFS[5];//50Hz 
          if(UserRxBufferFS[4] == 1) notch_60Hz_value = UserRxBufferFS[5];//60Hz
          fram_write_settings(((notch_50Hz_value<<8)|(notch_60Hz_value)), 9);
          
        }
        if(UserRxBufferFS[3] == 0x08){
          if(UserRxBufferFS[4] == 0x00){
            
            temp_recordCnt = (fram_read_settings(6)<<16) | fram_read_settings(7);
            usb_offset = 0;
            usb_block_offset = 0;
            
            //fram_read_buf(temp_dataRecord, 32, 0);
            UserTxBufferFS[0] = (uint8_t)(temp_recordCnt>>24);
            UserTxBufferFS[1] = (uint8_t)(temp_recordCnt>>16);
            UserTxBufferFS[2] = (uint8_t)(temp_recordCnt>>8);
            UserTxBufferFS[3] = (uint8_t)(temp_recordCnt&0xff);
            UserTxBufferFS[4] = 0xf0;
            UserTxBufferFS[5] = 0xfe;            
            UserTxBufferFS[6] = (uint8_t)(temp_recordCnt>>24);
            UserTxBufferFS[7] = (uint8_t)(temp_recordCnt>>16);
            UserTxBufferFS[8] = (uint8_t)(temp_recordCnt>>8);
            UserTxBufferFS[9] = (uint8_t)(temp_recordCnt&0xff);
           
            CDC_Transmit_FS(UserTxBufferFS, 64); 
          }
          if(UserRxBufferFS[4] == 0x01){
            usb_block_offset += 20;
            fram_read_buf(usb_block_buf, 20, usb_block_offset);
            
            UserTxBufferFS[0] = (uint8_t)(usb_block_offset>>24);
            UserTxBufferFS[1] = (uint8_t)(usb_block_offset>>16);
            UserTxBufferFS[2] = (uint8_t)(usb_block_offset>>8);
            UserTxBufferFS[3] = (uint8_t)(usb_block_offset&0xff);
            UserTxBufferFS[4] = 0xf1;
            UserTxBufferFS[5] = 0xfe;
            
            usb_block_offset += 20;
            fram_read_buf(usb_block_buf, 20, usb_block_offset);
            for(uint8_t usb_i = 0; usb_i < 20; usb_i++){
              UserTxBufferFS[2*usb_i+6] = (uint8_t)(usb_block_buf[usb_i]>>8);
              UserTxBufferFS[2*usb_i+7] = (uint8_t)(usb_block_buf[usb_i]&0xff);
            }
 /*           
            uint16_t usbTxbufTemp[30];
            for(uint8_t iUsb = 0; iUsb<20; iUsb++){
              usbTxbufTemp[iUsb] = 2712; 
            }            
            for(uint8_t usb_i = 0; usb_i < 20; usb_i++){//28
              UserTxBufferFS[2*usb_i+6] = (uint8_t)(usbTxbufTemp[usb_i]>>8);//(uint8_t)(temp_dataRecord[usb_i]>>8);
              UserTxBufferFS[2*usb_i+7] = (uint8_t)(usbTxbufTemp[usb_i]&0xff);//(uint8_t)temp_dataRecord[usb_i];
              
            } 
*/            
            CDC_Transmit_FS(UserTxBufferFS, 64); 
          }

        }//usb small packed transfer
        if(UserRxBufferFS[3] == 0x09){

          
          //CDC_Transmit_FS(UserTxBufferFS, 2048);
        }        
        
        
        //clear start byte to prevent double proc
        UserRxBufferFS[0] = 0x00;
      
      }

    }//usb receive cmd
}

#if DEVICE_RTC_LSI 
 static int rtc_inited = 0; 
#endif 
 
static RTC_HandleTypeDef RtcHandle;
 
void rtc_init(void)
{
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_PeriphCLKInitTypeDef PeriphClkInitStruct = {0};
    uint32_t rtc_freq = 0;

    RtcHandle.Instance = RTC;
 
    // Enable Power clock
    __HAL_RCC_PWR_CLK_ENABLE();
 
    // Enable access to Backup domain
    HAL_PWR_EnableBkUpAccess();
 
    // Reset Backup domain
    __HAL_RCC_BACKUPRESET_FORCE();
    __HAL_RCC_BACKUPRESET_RELEASE();
 
 
    // Enable LSE Oscillator
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_LSI | RCC_OSCILLATORTYPE_LSE;
    RCC_OscInitStruct.PLL.PLLState   = RCC_PLL_NONE; // Mandatory, otherwise the PLL is reconfigured!
    RCC_OscInitStruct.LSEState       = RCC_LSE_ON; // External 32.768 kHz clock on OSC_IN/OSC_OUT
    RCC_OscInitStruct.LSIState       = RCC_LSI_OFF;
    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) == HAL_OK) { // Check if LSE has started correctly
        // Connect LSE to RTC
        PeriphClkInitStruct.PeriphClockSelection = RCC_PERIPHCLK_RTC;
        PeriphClkInitStruct.RTCClockSelection = RCC_RTCCLKSOURCE_LSE;
        HAL_RCCEx_PeriphCLKConfig(&PeriphClkInitStruct);
        rtc_freq = LSE_VALUE;
    }
    else {
      
    }

 
    // Enable RTC
    __HAL_RCC_RTC_ENABLE();
 
    RtcHandle.Init.HourFormat     = RTC_HOURFORMAT_24;
    RtcHandle.Init.AsynchPrediv   = 127;
    RtcHandle.Init.SynchPrediv    = (rtc_freq / 128) - 1;
    RtcHandle.Init.OutPut         = RTC_OUTPUT_DISABLE;
    RtcHandle.Init.OutPutPolarity = RTC_OUTPUT_POLARITY_HIGH;
    RtcHandle.Init.OutPutType     = RTC_OUTPUT_TYPE_OPENDRAIN;
 
    if (HAL_RTC_Init(&RtcHandle) != HAL_OK) {
        
    }
}
 
void rtc_free(void)
{
    // Enable Power clock
    __HAL_RCC_PWR_CLK_ENABLE();
 
    // Enable access to Backup domain
    HAL_PWR_EnableBkUpAccess();
 
    // Reset Backup domain
    __HAL_RCC_BACKUPRESET_FORCE();
    __HAL_RCC_BACKUPRESET_RELEASE();
 
    // Disable access to Backup domain
    HAL_PWR_DisableBkUpAccess();
 
    // Disable LSI and LSE clocks
    RCC_OscInitTypeDef RCC_OscInitStruct;
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_LSI | RCC_OSCILLATORTYPE_LSE;
    RCC_OscInitStruct.PLL.PLLState   = RCC_PLL_NONE;
    RCC_OscInitStruct.LSIState       = RCC_LSI_OFF;
    RCC_OscInitStruct.LSEState       = RCC_LSE_OFF;
    HAL_RCC_OscConfig(&RCC_OscInitStruct);
#if DEVICE_RTC_LSI
    rtc_inited = 0;
#endif
 
}
 
int rtc_isenabled(void)
{
#if DEVICE_RTC_LSI
    return rtc_inited;
#else
  if ((RTC->ISR & RTC_ISR_INITS) ==  RTC_ISR_INITS) return 1;
  else return 0;
#endif
 
}
 



/******************************************************************************/
int main(void)
{
  HAL_Init();
  SystemClock_Config();

  MX_GPIO_Init();
  MX_FMC_Init();
  MX_USART2_UART_Init();
  
  MX_ADC1_Init();
  //if(!(RTC->ISR & RTC_ISR_INITS))
  //MX_RTC_Init();

  
  //HAL_PWR_EnableBkUpAccess();
  
  //backupReadData = HAL_RTCEx_BKUPRead(&RtcHandle, RTC_BKP_DR1);
  /*
  if (backupReadData != 0x32F2)
  {
    rtcInit();

  }
  */
  rtcInit();
  //MX_RTC_Init();
  
  
  MX_I2C1_Init();
  //rtc_lse_error = rtc_Init();
  //if(!(*(volatile uint32_t *) (BDCR_RTCEN_BB)))__HAL_RCC_RTC_ENABLE();
  MX_USB_DEVICE_Init();

  _fram_address_cnt = fram_read_settings(6);
  _fram_address_cnt = (_fram_address_cnt<<16) + fram_read_settings(7);
  if(_fram_address_cnt > 262144) _fram_address_cnt = 0;
  card_watcher = _fram_address_cnt;
  record_number = fram_read_settings(8); 
  agm.serial_number = fram_read_settings(10);
  notch_50Hz_value = (uint8_t)(fram_read_settings(9)>>8);
  notch_60Hz_value = (uint8_t)(fram_read_settings(9)&0xff);
  notch_type = (uint8_t)(fram_read_settings(11)&0xff);
  fram_gps_state = (uint8_t)(fram_read_settings(11)>>8);
  if(agm.serial_number > 999) agm.serial_number = 1;
  timer_init();
  HAL_GPIO_WritePin(GSM_RST_GPIO_Port, GSM_RST_Pin, GPIO_PIN_RESET);//active power level
  HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_SET);//OLED reset pin
  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_2, GPIO_PIN_RESET);//DTR low to normal work MC60
  oled_init();
  oled_logo();
  logo_delay = 30000;
  //agm.serial_number = 0x01;
  agm.battery = BATTERY_FULL;
  agm.connection = NO_CONNECTION;
  agm.event = NO_EVENT;
  //agm.gnss = GPS_OFF;
  agm.gsm = GSM_DISABLE;
  agm.memory = MEMORY_EMPTY;
  agm.signal = SIGNAL_MAG;
  agm.state = STATE_STANDBY;
  

  agm_option_menu.record_mode = 0;
  agm_option_menu.sensitivity_mag = 1;
  agm_option_menu.sensitivity_lf = 10;
  agm_option_menu.data_interface = 0;
  //agm_option_menu.gps_glonass = 0;
  agm_option_menu.gsm_gprs = 0;
  agm_option_menu.notch_filter = 0;
  agm_option_menu.erase_data = 0;
  agm_option_menu.download_data = 0;
  
  LL_ADC_REG_StartConversion(ADC1);

  I2C_TxBuffer_Notch[0] = 0x10;
  if((notch_type == 0)||(notch_type == 0xff))I2C_TxBuffer_Notch[1] = notch_50Hz_value;//50Hz
  else I2C_TxBuffer_Notch[1] = notch_60Hz_value;//60Hz
  I2C_SetNotchFreq(hi2c1, 0x5e, 2);  
  
  agm_option_menu.sensitivity_mag = (uint8_t)(fram_read_settings(12));
  agm_option_menu.sensitivity_lf = (uint8_t)(fram_read_settings(12)>>8);
  if(agm_option_menu.sensitivity_lf == 0xff)agm_option_menu.sensitivity_lf = 0;
  if((agm_option_menu.sensitivity_mag != 10)&&(agm_option_menu.sensitivity_mag <11)) {
    I2C_TxBuffer[0] = 0x10;
    //G = 1,2,3,4,5,7,9,12,15,20
    if(agm_option_menu.sensitivity_mag == 0) I2C_TxBuffer[1] = 17;
    if(agm_option_menu.sensitivity_mag == 1) I2C_TxBuffer[1] = 13;
    if(agm_option_menu.sensitivity_mag == 2) I2C_TxBuffer[1] = 10;
    if(agm_option_menu.sensitivity_mag == 3) I2C_TxBuffer[1] = 9;
    if(agm_option_menu.sensitivity_mag == 4) I2C_TxBuffer[1] = 8;
    if(agm_option_menu.sensitivity_mag == 5) I2C_TxBuffer[1] = 7;
    if(agm_option_menu.sensitivity_mag == 6) I2C_TxBuffer[1] = 6;
    if(agm_option_menu.sensitivity_mag == 7) I2C_TxBuffer[1] = 5;
    if(agm_option_menu.sensitivity_mag == 8) I2C_TxBuffer[1] = 4;
    if(agm_option_menu.sensitivity_mag == 9) I2C_TxBuffer[1] = 3;
    
    I2C_WriteBuffer(hi2c1, 0x58, 2);    
  }
  else{
    agm_option_menu.sensitivity_mag = 0;
  }
  
  if(fram_gps_state == 0){
    agm_option_menu.gps_glonass = 0;
  }
  if(fram_gps_state == 1){
    
    agm_option_menu.gps_glonass = 1;
    gps_event = 1;
  }
  
  
  
  /*
  agm_option_menu.gps_glonass = (uint8_t)(fram_read_settings(13));
  agm_option_menu.gsm_gprs = (uint8_t)(fram_read_settings(13)>>8); 
  agm_option_menu.record_mode = (uint8_t)(fram_read_settings(14)>>8); 
  
  if(agm_option_menu.gps_glonass == 0xff) agm_option_menu.gps_glonass = 0;
  if(agm_option_menu.gsm_gprs == 0xff) agm_option_menu.gsm_gprs = 0;
  if(agm_option_menu.record_mode == 0xff) agm_option_menu.record_mode = 0;
  */
  
  //HAL_Delay(200);  
  //AFE_gain_auto();
  uint32_t usb_delay = 0;
  
  while (1){
    usb_delay++;
    if(usb_delay >= 1000){
      //CDC_Transmit_FS(UserTxBufferFS, 64);
      usb_delay =0;
      usb_tx();
    }
    
    if(sleep_mode_state == 1) if(menu_level == MAIN_MENU) menu_level = STANDBY_MENU;
    

    
    
    if(time_update_cnt == 0){
      HAL_RTC_GetTime(&RtcHandle, &sTime, RTC_FORMAT_BIN); // RTC_FORMAT_BIN , RTC_FORMAT_BCD
      HAL_RTC_GetDate(&RtcHandle, &DateToUpdate, RTC_FORMAT_BIN);
      time_update_cnt = 10000;
    }
        
    if(gps_parser_flag == 1){
      
      if((uart_rx_buf_callback[6] == ',')&&(uart_rx_buf_callback[7] != ',')&&(uart_rx_buf_callback[18] == 'A')){//&&((uart_rx_buf_callback[43] == 'E')||(uart_rx_buf_callback[43] == 'W'))){
        error_led_state = 0; 
        
        gps_oled_string[0] = uart_rx_buf_callback[0];
        gps_oled_string[1] = uart_rx_buf_callback[1];
        gps_oled_string[2] = uart_rx_buf_callback[2];
        gps_oled_string[3] = uart_rx_buf_callback[3];
        gps_oled_string[4] = uart_rx_buf_callback[4];
        gps_oled_string[5] = uart_rx_buf_callback[5];
        gps_oled_string[6] = uart_rx_buf_callback[6];
        gps_oled_string[7] = uart_rx_buf_callback[7];
        gps_oled_string[8] = uart_rx_buf_callback[8];
        gps_oled_string[9] = uart_rx_buf_callback[9];
        gps_oled_string[10] = uart_rx_buf_callback[10];
        gps_oled_string[11] = uart_rx_buf_callback[11];
        gps_oled_string[12] = uart_rx_buf_callback[12];
        gps_oled_string[13] = uart_rx_buf_callback[13];
        gps_oled_string[14] = uart_rx_buf_callback[14];
        gps_oled_string[15] = uart_rx_buf_callback[15];
        gps_oled_string[16] = uart_rx_buf_callback[16];
        gps_oled_string[17] = uart_rx_buf_callback[17];
        gps_oled_string[18] = uart_rx_buf_callback[18];
        gps_oled_string[19] = uart_rx_buf_callback[19];
        gps_oled_string[20] = uart_rx_buf_callback[20];
        gps_oled_string[21] = uart_rx_buf_callback[21];
        gps_oled_string[22] = uart_rx_buf_callback[22];
        
        for(uint8_t i_comma = 0; i_comma <60; i_comma++){
          if(uart_rx_buf_callback[i_comma] == ','){ comma_cnt++;
            if(comma_cnt == 9)gps_date_offset = i_comma;
          }          
        }
        comma_cnt = 0;
        
        //latitude
        agm_gps_status.latitude_hi = ((uart_rx_buf_callback[20]-0x30)*10) + (uart_rx_buf_callback[21]-0x30);//max value 90 
        agm_gps_status.latitude_lo = ((uart_rx_buf_callback[22]-0x30)*100 + (uart_rx_buf_callback[23]-0x30)*10 + (uart_rx_buf_callback[25]-0x30));
        agm_gps_status.latitude_direction = uart_rx_buf_callback[30];
        //longitude
        agm_gps_status.longitude_hi = ((uart_rx_buf_callback[32]-0x30)*100 + (uart_rx_buf_callback[33]-0x30)*10 + (uart_rx_buf_callback[34]-0x30));
        agm_gps_status.longitude_lo = ((uart_rx_buf_callback[35]-0x30)*100 + (uart_rx_buf_callback[36]-0x30)*10 + (uart_rx_buf_callback[38]-0x30));
        agm_gps_status.longitude_direction = uart_rx_buf_callback[43];
        //utc time
        agm_gps_status.utc_time_hh = ((uart_rx_buf_callback[7]-0x30)*10 + (uart_rx_buf_callback[8]-0x30));
        agm_gps_status.utc_time_mm = ((uart_rx_buf_callback[9]-0x30)*10 + (uart_rx_buf_callback[10]-0x30));
        agm_gps_status.utc_time_ss = ((uart_rx_buf_callback[11]-0x30)*10 + (uart_rx_buf_callback[12]-0x30));
        agm_gps_status.utc_time_sss = ((uart_rx_buf_callback[14]-0x30)*100 + (uart_rx_buf_callback[15]-0x30)*10 + (uart_rx_buf_callback[16]-0x30));

        if(uart_rx_buf_callback[55] == ','){
          agm_gps_status.utc_date_day = ((uart_rx_buf_callback[56]-0x30)*10 + (uart_rx_buf_callback[57]-0x30));
          agm_gps_status.utc_date_month = ((uart_rx_buf_callback[58]-0x30)*10 + (uart_rx_buf_callback[59]-0x30));
          agm_gps_status.utc_date_year = ((uart_rx_buf_callback[60]-0x30)*10 + (uart_rx_buf_callback[61]-0x30));
        }
        else{
          agm_gps_status.utc_date_day = ((uart_rx_buf_callback[gps_date_offset + 1]-0x30)*10 + (uart_rx_buf_callback[gps_date_offset+2]-0x30));
          agm_gps_status.utc_date_month = ((uart_rx_buf_callback[gps_date_offset+3]-0x30)*10 + (uart_rx_buf_callback[gps_date_offset+4]-0x30));
          agm_gps_status.utc_date_year = ((uart_rx_buf_callback[gps_date_offset+5]-0x30)*10 + (uart_rx_buf_callback[gps_date_offset+6]-0x30));
          }
        DateToUpdate_set.Date = agm_gps_status.utc_date_day;
        DateToUpdate_set.Month = agm_gps_status.utc_date_month;
        DateToUpdate_set.Year = agm_gps_status.utc_date_year;
        HAL_RTC_SetDate(&hrtc, &DateToUpdate_set, RTC_FORMAT_BIN); 
       
        sTime_set.Hours = agm_gps_status.utc_time_hh;
        sTime_set.Minutes = agm_gps_status.utc_time_mm;
        sTime_set.Seconds = agm_gps_status.utc_time_ss;
        HAL_RTC_SetTime(&hrtc, &sTime_set,  RTC_FORMAT_BIN);   
        
        agm.gnss = GPS_ON;
        
        gps_latch_cnt++;
        if(gps_latch_cnt >= 3){
          gps_latch_cnt = 0;
          gps_latch_done = 1;
        }
    }
     else if((uart_rx_buf_callback[6] == ',')&&(uart_rx_buf_callback[7] != ',')&&(uart_rx_buf_callback[18] == 'V')){
     error_led_state = 1;      
        gps_oled_string[0] = uart_rx_buf_callback[0];
        gps_oled_string[1] = uart_rx_buf_callback[1];
        gps_oled_string[2] = uart_rx_buf_callback[2];
        gps_oled_string[3] = uart_rx_buf_callback[3];
        gps_oled_string[4] = uart_rx_buf_callback[4];
        gps_oled_string[5] = uart_rx_buf_callback[5];
        gps_oled_string[6] = uart_rx_buf_callback[6];
        gps_oled_string[7] = uart_rx_buf_callback[7];
        gps_oled_string[8] = uart_rx_buf_callback[8];
        gps_oled_string[9] = uart_rx_buf_callback[9];
        gps_oled_string[10] = uart_rx_buf_callback[10];
        gps_oled_string[11] = uart_rx_buf_callback[11];
        gps_oled_string[12] = uart_rx_buf_callback[12];
        gps_oled_string[13] = uart_rx_buf_callback[13];
        gps_oled_string[14] = uart_rx_buf_callback[14];
        gps_oled_string[15] = uart_rx_buf_callback[15];
        gps_oled_string[16] = uart_rx_buf_callback[16];
        gps_oled_string[17] = uart_rx_buf_callback[17];
        gps_oled_string[18] = uart_rx_buf_callback[18];
        gps_oled_string[19] = uart_rx_buf_callback[19];
        gps_oled_string[20] = uart_rx_buf_callback[20];
        gps_oled_string[21] = uart_rx_buf_callback[21];
        gps_oled_string[22] = uart_rx_buf_callback[22];           
    }
    else error_led_state = 2; 
      gps_parser_flag = 0;
    }    
    
    if((pwrup_seq_done == 0) && (agm_option_menu.gps_glonass == 1)&&(menu_level != SUB_OPTION_MENU)){
      /*
      if(gnss_startup_state == 0){
        HAL_GPIO_WritePin(GSM_RST_GPIO_Port, GSM_RST_Pin, GPIO_PIN_RESET);
        if(gps_cnt_status == 0){ gnss_startup_delay = 1000; gps_cnt_status = 1;}
        if(gnss_startup_delay == 0){gnss_startup_state = 1; gps_cnt_status = 0;}
      }*/
      if(gnss_startup_state == 0){
        HAL_GPIO_WritePin(GSM_RST_GPIO_Port, GSM_RST_Pin, GPIO_PIN_SET);
        if(gps_cnt_status == 0){gnss_startup_delay = 20000;gps_cnt_status = 1;}
        if(gnss_startup_delay == 0){gnss_startup_state = 1;gps_cnt_status = 0;}
      }
      if(gnss_startup_state == 1){
        HAL_GPIO_WritePin(GSM_RST_GPIO_Port, GSM_RST_Pin, GPIO_PIN_RESET);
        pwrup_seq_done = 1;
        HAL_Delay(200);
        //AT+IPR=0
        HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT\r\n", 4);
        //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+IFC=0,0\r\n", 12);
        //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+QGNSSC=1\r\n", 13);
        //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT\r\n", 4);
        gps_update_data_timer = 30000;
        HAL_UART_Receive_IT(&huart2, (uint8_t*)buff, 1);
        agm.gnss = GPS_WAIT_DATA;
        at_wakeup_try = 3;
      } 
    }
    if((pwrup_seq_done == 1) && (agm_option_menu.gps_glonass == 0)&&(menu_level != SUB_OPTION_MENU)){
      /*
      if(gnss_startup_state == 2){
        HAL_GPIO_WritePin(GSM_RST_GPIO_Port, GSM_RST_Pin, GPIO_PIN_RESET);
        if(gps_cnt_status == 0){gnss_startup_delay = 1000;gps_cnt_status = 1;}
        if(gnss_startup_delay == 0){gnss_startup_state = 1;gps_cnt_status = 0;}
      }
      */
      if(gnss_startup_state == 1){
        HAL_GPIO_WritePin(GSM_RST_GPIO_Port, GSM_RST_Pin, GPIO_PIN_SET);
        if(gps_cnt_status == 0){gnss_startup_delay = 8000;gps_cnt_status = 1;}
        if(gnss_startup_delay == 0){gnss_startup_state = 0;gps_cnt_status = 0;}
      }
      if(gnss_startup_state == 0){
        HAL_GPIO_WritePin(GSM_RST_GPIO_Port, GSM_RST_Pin, GPIO_PIN_RESET);
        pwrup_seq_done = 0;
        gps_latch_timer = 0;
      } 
    }    
      
    if((gps_update_data_timer == 0) && (agm_option_menu.gps_glonass == 1) && (pwrup_seq_done == 1)&&(menu_level != SUB_OPTION_MENU)&&(gps_latch_timer == 0)){
      //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+CFUN=1\r\n", 11);
      //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+IFC=0,0\r\n", 12);
      if(at_wakeup_try == 3) {
        at_wakeup_try--;
        //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT\r\n", 4);
        //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+QSCLK=1\r\n", 12);
        HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+CFUN=1\r\n", 11);
      }
      else if(at_wakeup_try == 2) {
        at_wakeup_try--;
        //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT\r\n", 4);
        //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+CFUN=4\r\n", 11);
        HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+QSCLK=1\r\n", 12);
      }      
      else if(at_wakeup_try == 1) {
        at_wakeup_try--;
        //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT\r\n", 4);
        HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+QGNSSC=1\r\n", 13);
      }
      else if(at_wakeup_try == 0){
        //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+QGNSSC?\r\n", 12);
        //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+QGNSSC=1\r\n", 13);
        if(gps_latch_done == 0){
          HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+QGNSSRD=\"NMEA/RMC\"\r\n", 23);
          
          
          //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+QSCLK?\r\n", 11);
          //HAL_GPIO_WritePin(GPIOC, GPIO_PIN_2, GPIO_PIN_SET);
        }
        if(gps_latch_done == 1){
          //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+QSCLK=1\r\n", 12);
          HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+QGNSSC=0\r\n", 13);
          //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"$PMTK161,0*28\r\n", 15);
          //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+CFUN=4\r\n", 11);
          
          gps_latch_timer = 1200000;//2 min 
          gps_latch_done = 0;
          
        }
      }
      
      gps_update_data_timer = 15000;//3sec
 
    }
    /*
    if((gps_update_data_timer == 0) && (agm_option_menu.gps_glonass == 0) && (pwrup_seq_done == 0)&&(menu_level != SUB_OPTION_MENU)&&(check_powerdown_gps == 1)){
      //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+CFUN=1\r\n", 11);
      //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+IFC=0,0\r\n", 12);
      HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+QGNSSRD=\"NMEA/RMC\"\r\n", 23);
      gps_update_data_timer = 50000;//10sec
 
    }*/
    
    
    if((key1_long_press_enable == 1) && (key2_long_press_enable == 1)){
      //if(menu_level == STANDBY_MENU) menu_level = MAIN_MENU;
      //if(menu_level == MAIN_MENU) menu_level = STANDBY_MENU;
      //if(menu_level == OPTION_MENU) ;//default value of active submenu
      key1_long_press_enable = 0;
      key2_long_press_enable = 0;
      
      
      if(agm.state == STATE_STANDBY){
        if(mag_sens_auto_enable == 1)AFE_gain_auto();
        agm_standby_active_mode = MODE_ACTIVE;
        record_start_delay_cnt = 30001;//3sec
        agm.state = STATE_ACTIVE;
        _agm_sleep_timer = 170000;
        
      }
      else{
        record_start_delay_done = 0;
        agm_standby_active_mode = MODE_STANDBY;
        agm.state = STATE_STANDBY;        
      }
    }
    
    if((key1_long_press_enable == 1)&&(key2_press_flag == 0)){// && (key2_long_press_enable != 1)&&(key2_lock == 0)){  
      key1_long_press_enable = 0;
      if(menu_level == MAIN_MENU) menu_level = STANDBY_MENU;
      if(menu_level == OPTION_MENU)menu_level = MAIN_MENU;
      if(menu_level == SUB_OPTION_MENU)menu_level = OPTION_MENU;

    } 
    
  if((key2_long_press_enable == 1)&&(key1_press_flag == 0)){// && (key1_long_press_enable == 0)&&(key1_lock == 0)){  
      key2_long_press_enable = 0;
      if(menu_level == OPTION_MENU){
        menu_level = SUB_OPTION_MENU;
      }
      if(menu_level == MAIN_MENU){
        menu_level = OPTION_MENU;
      }      
    }    
    if((key1_short_press_enable == 1) && (key2_short_press_enable == 1)){
      agm.event = 0;
      key1_short_press_enable = 0;
      key2_short_press_enable = 0;
    }
    if(key2_short_press_enable == 1){//forward ++
      agm.event = 0;
      key2_short_press_enable = 0;
      
      sleep_mode_state++;
      if(sleep_mode_state >=2)sleep_mode_state = 0; 
      
      if(sleep_mode_state == 0) if(menu_level == STANDBY_MENU) menu_level = MAIN_MENU;
      if(sleep_mode_state == 1) if(menu_level == MAIN_MENU) menu_level = STANDBY_MENU;
      //if(menu_level == STANDBY_MENU){ _agm_sleep_timer = 0; menu_level = MAIN_MENU;}
      //if(menu_level == MAIN_MENU){ _agm_sleep_timer = 200000; menu_level = STANDBY_MENU;}
      
      if(menu_level == OPTION_MENU){
        menu_ring_cnt++;
        if(menu_ring_cnt > 8) menu_ring_cnt = 0;
      }
      //if(menu_level == STANDBY_MENU) standby_press_cnt++;
      //if(standby_press_cnt == 1) ;//activate display
      //if(standby_press_cnt == 2){
      //  menu_level = OPTION_MENU;
      //  standby_press_cnt = 0;
      //}
      //if(menu_level != STANDBY_MENU) standby_press_cnt = 0;
      
      
      if(menu_level == SUB_OPTION_MENU){
        if(menu_ring_cnt == 0) {
          agm_option_menu.record_mode++;
          if(agm_option_menu.record_mode > 2) agm_option_menu.record_mode = 0;
        }
        if(menu_ring_cnt == 1) {
          agm_option_menu.sensitivity_mag++;
          if(agm_option_menu.sensitivity_mag > 10) agm_option_menu.sensitivity_mag = 0;
          sensitivity_mag_event = 1;
        }
        if(menu_ring_cnt == 2) {
          agm_option_menu.sensitivity_lf++;
          if(agm_option_menu.sensitivity_lf > 10) agm_option_menu.sensitivity_lf = 0;
        }
        if(menu_ring_cnt == 3) {
          agm_option_menu.data_interface++;
          if(agm_option_menu.data_interface > 2) agm_option_menu.data_interface = 0;
        }
        if(menu_ring_cnt == 4) {
          agm_option_menu.gsm_gprs++;
          if(agm_option_menu.gsm_gprs > 1) agm_option_menu.gsm_gprs = 0;
          if(agm_option_menu.gsm_gprs == 0)agm.gsm = GSM_DISABLE;
          if(agm_option_menu.gsm_gprs == 1){
            if(gsm_event == 0)agm.gsm = GSM_NO_CONNECTION;
            gsm_event = 1;
          }
        }
        if(menu_ring_cnt == 5) {
          agm_option_menu.gps_glonass++;
          if(agm_option_menu.gps_glonass > 1) agm_option_menu.gps_glonass = 0;
          uint16_t temp_fram_notch_gps = 0;
          if(agm_option_menu.gps_glonass == 0){
            agm.gnss = GPS_OFF;
            check_powerdown_gps = 1;
            temp_fram_notch_gps = fram_read_settings(11);
            temp_fram_notch_gps &= 0x00ff;
            fram_write_settings((uint16_t)(temp_fram_notch_gps), 11);             
          }
          if(agm_option_menu.gps_glonass == 1){
            agm.gnss = GPS_ON;
            gps_event = 1;
            temp_fram_notch_gps = (0x00ff&fram_read_settings(11));
            temp_fram_notch_gps |= 0x100;
            fram_write_settings((uint16_t)(temp_fram_notch_gps), 11);             
            
          }          
        }
        if(menu_ring_cnt == 6) {
          agm_option_menu.download_data++;
          if(agm_option_menu.download_data > 1) agm_option_menu.download_data = 0;
        }
        if(menu_ring_cnt == 7) {
          agm_option_menu.erase_data++;
          if(agm_option_menu.erase_data > 1) agm_option_menu.erase_data = 0;
          if(agm_option_menu.erase_data == 1)fram_erase_event = 1;
          else fram_erase_event = 0;          
        }
        if(menu_ring_cnt == 8) {
          agm_option_menu.notch_filter++;
          if(agm_option_menu.notch_filter > 1) agm_option_menu.notch_filter = 0;
          notch_filter_event = 1;
        }       
      }
    }
    if(key1_short_press_enable == 1){//backward --
      agm.event = 0;
      key1_short_press_enable = 0;
      sleep_mode_state++;
      if(sleep_mode_state >=2)sleep_mode_state = 0; 
      
      if(sleep_mode_state == 0) if(menu_level == STANDBY_MENU) menu_level = MAIN_MENU;
      if(sleep_mode_state == 1) if(menu_level == MAIN_MENU) menu_level = STANDBY_MENU;
      //if(menu_level == STANDBY_MENU) menu_level = MAIN_MENU;
      //if(menu_level == MAIN_MENU) menu_level = STANDBY_MENU;
      
      if(menu_level == OPTION_MENU){
        if(menu_ring_cnt == 0) menu_ring_cnt = 9;
        menu_ring_cnt--;
      }
      
      if(menu_level == SUB_OPTION_MENU){
        if(menu_ring_cnt == 0){
          if(agm_option_menu.record_mode == 0) agm_option_menu.record_mode = 3;
          agm_option_menu.record_mode--;
        }
        if(menu_ring_cnt == 1){
          if(agm_option_menu.sensitivity_mag == 0) agm_option_menu.sensitivity_mag = 11;
          agm_option_menu.sensitivity_mag--;
          sensitivity_mag_event = 1;
        }
        if(menu_ring_cnt == 2){
          if(agm_option_menu.sensitivity_lf == 0) agm_option_menu.sensitivity_lf = 11;
          agm_option_menu.sensitivity_lf--;
        }
        if(menu_ring_cnt == 3){
          if(agm_option_menu.data_interface == 0) agm_option_menu.data_interface = 3;
          agm_option_menu.data_interface--;
        }
        if(menu_ring_cnt == 4){
          if(agm_option_menu.gsm_gprs == 0) agm_option_menu.gsm_gprs = 2;
          agm_option_menu.gsm_gprs--;
          
          if(agm_option_menu.gsm_gprs == 0)agm.gsm = GSM_DISABLE;
          if(agm_option_menu.gsm_gprs == 1){
            if(gsm_event == 0)agm.gsm = GSM_NO_CONNECTION;

            gsm_event = 1;
          }          
        }
        if(menu_ring_cnt == 5){
          if(agm_option_menu.gps_glonass == 0) agm_option_menu.gps_glonass = 2;
          agm_option_menu.gps_glonass--;
          uint16_t temp_fram_notch_gps = 0;
          if(agm_option_menu.gps_glonass == 0){
            agm.gnss = GPS_OFF;
            check_powerdown_gps = 1;
            temp_fram_notch_gps = (0x00ff&fram_read_settings(11));
            //temp_fram_notch_gps |= 0x0ff;
            fram_write_settings((uint16_t)(temp_fram_notch_gps), 11);            
            
          }
          if(agm_option_menu.gps_glonass == 1){
            agm.gnss = GPS_ON;
            
            temp_fram_notch_gps = (0x00ff&fram_read_settings(11));
            temp_fram_notch_gps |= 0x100;
            fram_write_settings((uint16_t)(temp_fram_notch_gps), 11);            
            gps_event = 1;
          }
          
        }
        if(menu_ring_cnt == 6){
          if(agm_option_menu.download_data == 0) agm_option_menu.download_data = 2;
          agm_option_menu.download_data--; 
        }
        if(menu_ring_cnt == 7){
          if(agm_option_menu.erase_data == 0) agm_option_menu.erase_data = 2;
          agm_option_menu.erase_data--;
          if(agm_option_menu.erase_data == 1)fram_erase_event = 1;
          else fram_erase_event = 0;
        }
        if(menu_ring_cnt == 8){
          if(agm_option_menu.notch_filter == 0) agm_option_menu.notch_filter = 2;
          agm_option_menu.notch_filter--;
          notch_filter_event = 1;
        }     
      }      
    } //short key 1 press
    
    
   if((fram_erase_event == 1)&&(menu_level != SUB_OPTION_MENU)){
    _fram_address_cnt = 0;
    card_watcher = 0;
    fram_write_settings((uint16_t)(_fram_address_cnt>>16), 6);
    fram_write_settings((uint16_t)(_fram_address_cnt&0xffff), 7);
    fram_erase_event = 0;
    record_number = 0;
    fram_write_settings(record_number, 8);
    agm_option_menu.erase_data = 0;
    agm.event = NO_EVENT;
    recordTime.Seconds = 0;
    recordTime.Minutes = 0;
    recordTime.Hours = 0;
    recordDate.Date = 0;
    recordDate.Month = 0;
    recordDate.Year = 0;    
  }  
  if((notch_filter_event == 1) && (menu_level != SUB_OPTION_MENU)){
    I2C_TxBuffer_Notch[0] = 0x10;
    if(agm_option_menu.notch_filter == 0){I2C_TxBuffer_Notch[1] = notch_50Hz_value;notch_type = 0;fram_write_settings((uint16_t)(notch_type), 11);}//50Hz
    if(agm_option_menu.notch_filter == 1){I2C_TxBuffer_Notch[1] = notch_60Hz_value;notch_type = 1;fram_write_settings((uint16_t)(notch_type), 11);}//60Hz
    I2C_SetNotchFreq(hi2c1, 0x5e, 2);      
    notch_filter_event = 0;
  }
  if((sensitivity_mag_event == 1) && (menu_level != SUB_OPTION_MENU)){
    if(agm_option_menu.sensitivity_mag == 0){I2C_TxBuffer[1] = 17;mag_sens_auto_enable = 0;fram_write_settings((uint16_t)(agm_option_menu.sensitivity_mag), 12);}//25;
    if(agm_option_menu.sensitivity_mag == 1){I2C_TxBuffer[1] = 13;mag_sens_auto_enable = 0;fram_write_settings((uint16_t)(agm_option_menu.sensitivity_mag), 12);}//50;
    if(agm_option_menu.sensitivity_mag == 2){I2C_TxBuffer[1] = 10;mag_sens_auto_enable = 0;fram_write_settings((uint16_t)(agm_option_menu.sensitivity_mag), 12);}//75;
    if(agm_option_menu.sensitivity_mag == 3){I2C_TxBuffer[1] = 9;mag_sens_auto_enable = 0;fram_write_settings((uint16_t)(agm_option_menu.sensitivity_mag), 12);}//100;
    if(agm_option_menu.sensitivity_mag == 4){I2C_TxBuffer[1] = 8;mag_sens_auto_enable = 0;fram_write_settings((uint16_t)(agm_option_menu.sensitivity_mag), 12);}//125;
    if(agm_option_menu.sensitivity_mag == 5){I2C_TxBuffer[1] = 7;mag_sens_auto_enable = 0;fram_write_settings((uint16_t)(agm_option_menu.sensitivity_mag), 12);}//150;
    if(agm_option_menu.sensitivity_mag == 6){I2C_TxBuffer[1] = 6;mag_sens_auto_enable = 0;fram_write_settings((uint16_t)(agm_option_menu.sensitivity_mag), 12);}//175;
    if(agm_option_menu.sensitivity_mag == 7){I2C_TxBuffer[1] = 5;mag_sens_auto_enable = 0;fram_write_settings((uint16_t)(agm_option_menu.sensitivity_mag), 12);}//200;
    if(agm_option_menu.sensitivity_mag == 8){I2C_TxBuffer[1] = 4;mag_sens_auto_enable = 0;fram_write_settings((uint16_t)(agm_option_menu.sensitivity_mag), 12);}//225;
    if(agm_option_menu.sensitivity_mag == 9){I2C_TxBuffer[1] = 3;mag_sens_auto_enable = 0;fram_write_settings((uint16_t)(agm_option_menu.sensitivity_mag), 12);}//250;
    if(agm_option_menu.sensitivity_mag == 10){mag_sens_auto_enable = 1;fram_write_settings((uint16_t)(agm_option_menu.sensitivity_mag), 12);}//autogain  AFE_gain_auto();
    if(mag_sens_auto_enable == 0){
      I2C_TxBuffer[0] = 0x10;
      I2C_WriteBuffer(hi2c1, 0x58, 2);  
    }
    sensitivity_mag_event = 0;
  }
  //HAL_SuspendTick();
  //HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
  //HAL_ResumeTick();
    }//while(1)
}//main
/******************************************************************************/
/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /**Initializes the CPU, AHB and APB busses clocks 
  */
  
  
    // Enable Power clock
    //__HAL_RCC_PWR_CLK_ENABLE();
 
    
    
    // Enable access to Backup domain
    //HAL_PWR_EnableBkUpAccess();
 
    
    
    // Reset Backup domain
    //__HAL_RCC_BACKUPRESET_FORCE();
    //__HAL_RCC_BACKUPRESET_RELEASE();  
  
/*  
if ((RTC->ISR & RTC_ISR_INITS) ==  RTC_ISR_INITS)
{

HAL_PWR_EnableBkUpAccess();
__HAL_RCC_BACKUPRESET_FORCE();
__HAL_RCC_BACKUPRESET_RELEASE(); 
}
*/

 
  
  
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_MSI;
  //RCC_OscInitStruct.HSEState = RCC_HSE_OFF;//HSE_BYPASS
  //RCC_OscInitStruct.LSEState = RCC_LSE_BYPASS;
  //RCC_OscInitStruct.LSIState = RCC_LSI_OFF;
  RCC_OscInitStruct.MSIState = RCC_MSI_ON;
  RCC_OscInitStruct.MSIClockRange = RCC_MSIRANGE_11;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_NONE;
  //RCC_OscInitStruct.PLL.PLLM = 6;
  //RCC_OscInitStruct.PLL.PLLN = 40;//24
  //RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV7;
  //RCC_OscInitStruct.PLL.PLLQ = RCC_PLLQ_DIV6;
  //RCC_OscInitStruct.PLL.PLLR = RCC_PLLR_DIV4;
  //__HAL_RCC_LSI_DISABLE();
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    //rtc_lse_error = 1;
    Error_Handler();
  }
  /**Initializes the CPU, AHB and APB busses clocks 
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_MSI;//RCC_SYSCLKSOURCE_MSI//RCC_SYSCLKSOURCE_PLLCLK
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_RTC|RCC_PERIPHCLK_USART2
                              |RCC_PERIPHCLK_I2C1|RCC_PERIPHCLK_USB
                              |RCC_PERIPHCLK_ADC;
  PeriphClkInit.Usart2ClockSelection = RCC_USART2CLKSOURCE_SYSCLK;
  PeriphClkInit.I2c1ClockSelection = RCC_I2C1CLKSOURCE_SYSCLK;
  PeriphClkInit.AdcClockSelection = RCC_ADCCLKSOURCE_SYSCLK;
  //PeriphClkInit.RTCClockSelection = RCC_RTCCLKSOURCE_LSE;
  PeriphClkInit.UsbClockSelection = RCC_USBCLKSOURCE_MSI;
  //PeriphClkInit.PLLSAI1.PLLSAI1Source = RCC_PLLSOURCE_MSI;
  //PeriphClkInit.PLLSAI1.PLLSAI1M = 1;
  //PeriphClkInit.PLLSAI1.PLLSAI1N = 12;//8
  //PeriphClkInit.PLLSAI1.PLLSAI1P = RCC_PLLP_DIV7;
  //PeriphClkInit.PLLSAI1.PLLSAI1Q = RCC_PLLQ_DIV2;
  //PeriphClkInit.PLLSAI1.PLLSAI1R = RCC_PLLR_DIV2;
  //PeriphClkInit.PLLSAI1.PLLSAI1ClockOut = RCC_PLLSAI1_48M2CLK|RCC_PLLSAI1_ADC1CLK;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
    rtc_lse_error = 1;
  }
  
 
  
  
  /**Configure the main internal regulator output voltage 
  */
  if (HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1) != HAL_OK)
  {
    Error_Handler();
  }

}

/**
  * @brief ADC1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC1_Init(void)
{

  /* USER CODE BEGIN ADC1_Init 0 */

  /* USER CODE END ADC1_Init 0 */

  ADC_MultiModeTypeDef multimode = {0};
  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC1_Init 1 */

  /* USER CODE END ADC1_Init 1 */
  /**Common config 
  */
  hadc1.Instance = ADC1;
  hadc1.Init.ClockPrescaler = ADC_CLOCK_ASYNC_DIV4;
  hadc1.Init.Resolution = ADC_RESOLUTION_12B;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.ScanConvMode = ADC_SCAN_ENABLE;
  hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  hadc1.Init.LowPowerAutoWait = DISABLE;
  hadc1.Init.ContinuousConvMode = DISABLE;
  hadc1.Init.NbrOfConversion = 2;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
  hadc1.Init.DMAContinuousRequests = DISABLE;
  hadc1.Init.Overrun = ADC_OVR_DATA_PRESERVED;
  hadc1.Init.OversamplingMode = DISABLE;
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }
  /**Configure the ADC multi-mode 
  */
  multimode.Mode = ADC_MODE_INDEPENDENT;
  if (HAL_ADCEx_MultiModeConfigChannel(&hadc1, &multimode) != HAL_OK)
  {
    Error_Handler();
  }
  /**Configure Regular Channel 
  */
  sConfig.Channel = ADC_CHANNEL_1;
  sConfig.Rank = ADC_REGULAR_RANK_1;
  sConfig.SamplingTime = ADC_SAMPLETIME_92CYCLES_5;
  sConfig.SingleDiff = ADC_SINGLE_ENDED;
  sConfig.OffsetNumber = ADC_OFFSET_NONE;
  sConfig.Offset = 0;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /**Configure Regular Channel 
  */
  sConfig.Channel = ADC_CHANNEL_2;
  sConfig.Rank = ADC_REGULAR_RANK_2;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC1_Init 2 */

  LL_ADC_StartCalibration(ADC1, LL_ADC_SINGLE_ENDED);
  while(LL_ADC_IsCalibrationOnGoing(ADC1))asm("nop");
  
  LL_ADC_Enable(ADC1);  
  /* USER CODE END ADC1_Init 2 */

}

/**
  * @brief I2C1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_I2C1_Init(void)
{

  /* USER CODE BEGIN I2C1_Init 0 */

  /* USER CODE END I2C1_Init 0 */

  /* USER CODE BEGIN I2C1_Init 1 */

  /* USER CODE END I2C1_Init 1 */
  hi2c1.Instance = I2C1;
  hi2c1.Init.Timing = 0x10808DD3;
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c1.Init.OwnAddress2 = 0;
  hi2c1.Init.OwnAddress2Masks = I2C_OA2_NOMASK;
  hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c1) != HAL_OK)
  {
    Error_Handler();
  }
  /**Configure Analogue filter 
  */
  if (HAL_I2CEx_ConfigAnalogFilter(&hi2c1, I2C_ANALOGFILTER_ENABLE) != HAL_OK)
  {
    Error_Handler();
  }
  /**Configure Digital filter 
  */
  if (HAL_I2CEx_ConfigDigitalFilter(&hi2c1, 0) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN I2C1_Init 2 */

  /* USER CODE END I2C1_Init 2 */

}

/**
  * @brief RTC Initialization Function
  * @param None
  * @retval None
  */

static void rtcInit(void){
  
  RtcHandle.Instance = RTC; 
  RtcHandle.Init.HourFormat = RTC_HOURFORMAT_24;
  RtcHandle.Init.AsynchPrediv = 127;
  RtcHandle.Init.SynchPrediv = 255;
  RtcHandle.Init.OutPut = RTC_OUTPUT_DISABLE;
  RtcHandle.Init.OutPutPolarity = RTC_OUTPUT_POLARITY_HIGH;
  RtcHandle.Init.OutPutType = RTC_OUTPUT_TYPE_OPENDRAIN;
  
  if (HAL_RTC_Init(&RtcHandle) != HAL_OK)
  {
    /* Initialization Error */
    Error_Handler();
    rtc_lse_error = 1;
  }

  /*##-2- Check if Data stored in BackUp register1: No Need to reconfigure RTC#*/
  /* Read the Back Up Register 1 Data */
  HAL_PWR_EnableBkUpAccess();
  //HAL_PWR_DisableBkUpAccess();
  __HAL_RTC_WRITEPROTECTION_DISABLE(&RtcHandle);
  //HAL_RTCEx_BKUPWrite(&RtcHandle, RTC_BKP_DR1, 0x32F2);
  backupReadData = HAL_RTCEx_BKUPRead(&RtcHandle, RTC_BKP_DR1);
  if (backupReadData != 0x32F2)
  {
    /* Configure RTC Calendar */
    calendarInit();
  }
else __HAL_RCC_CLEAR_RESET_FLAGS();  

  HAL_PWR_EnableBkUpAccess();
  //HAL_RTCEx_DeactivateTamper(&RtcHandle, RTC_TAMPER_1);
  //__HAL_RTC_TAMPER_CLEAR_FLAG(&RtcHandle, RTC_FLAG_TAMP1F);   
   
  //HAL_PWR_EnableBkUpAccess();
  HAL_RTCEx_BKUPWrite(&RtcHandle, RTC_BKP_DR2, 0x32F2);  
  //__HAL_RTC_WRITEPROTECTION_ENABLE(&RtcHandle); 
  
  HAL_PWR_DisableBkUpAccess();
  test_point = HAL_RTCEx_BKUPRead(&RtcHandle, RTC_BKP_DR2);

}
static void calendarInit(void){
  RTC_DateTypeDef sdatestructure;
  RTC_TimeTypeDef stimestructure;
  //__HAL_RCC_BACKUPRESET_FORCE();
  //__HAL_RCC_BACKUPRESET_RELEASE();
  
  __HAL_RTC_WRITEPROTECTION_DISABLE(&RtcHandle);
  /*##-1- Configure the Date #################################################*/
  /* Set Date: Tuesday February 18th 2014 */
  /*
  sdatestructure.Year = 0x20;
  sdatestructure.Month = RTC_MONTH_APRIL;
  sdatestructure.Date = 0x20;
  sdatestructure.WeekDay = RTC_WEEKDAY_MONDAY;
  
  if(HAL_RTC_SetDate(&RtcHandle,&sdatestructure,RTC_FORMAT_BCD) != HAL_OK)
  {

    Error_Handler();
  }
*/
  /*##-2- Configure the Time #################################################*/
  /* Set Time: 02:00:00 */
  

  
  stimestructure.Hours = 0x20;
  stimestructure.Minutes = 0x32;
  stimestructure.Seconds = 0x00;
  stimestructure.TimeFormat = RTC_HOURFORMAT_24;
  stimestructure.DayLightSaving = RTC_DAYLIGHTSAVING_NONE ;
  stimestructure.StoreOperation = RTC_STOREOPERATION_RESET;

  if (HAL_RTC_SetTime(&RtcHandle, &stimestructure, RTC_FORMAT_BCD) != HAL_OK)
  {
    /* Initialization Error */
    Error_Handler();
  }
  HAL_PWR_EnableBkUpAccess();
  //HAL_RTCEx_DeactivateTamper(&RtcHandle, RTC_TAMPER_1);
  //__HAL_RTC_TAMPER_CLEAR_FLAG(&RtcHandle, RTC_FLAG_TAMP1F);   
   
  //HAL_PWR_EnableBkUpAccess();
  HAL_RTCEx_BKUPWrite(&RtcHandle, RTC_BKP_DR1, 0x32F2);  
  //__HAL_RTC_WRITEPROTECTION_ENABLE(&RtcHandle); 
  HAL_RTCEx_EnableBypassShadow(&RtcHandle);
  HAL_PWR_DisableBkUpAccess();
}

static void MX_RTC_Init(void)
{

  /* USER CODE BEGIN RTC_Init 0 */

  /* USER CODE END RTC_Init 0 */

  RTC_TamperTypeDef sTamper = {0};

  /* USER CODE BEGIN RTC_Init 1 */

  /* USER CODE END RTC_Init 1 */
  /**Initialize RTC Only 
  */
  HAL_RTCEx_DeactivateTamper(&hrtc, RTC_TAMPER_1);
  __HAL_RTC_TAMPER_CLEAR_FLAG(&hrtc, RTC_FLAG_TAMP1F);   
  //__HAL_RTC_WRITEPROTECTION_DISABLE(&hrtc); 
  HAL_PWR_EnableBkUpAccess();
  //HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR0, 0x32F2);
  backupReadData = HAL_RTCEx_BKUPRead(&hrtc, RTC_BKP_DR1); 
  
if (backupReadData != 0x32F2){  
  __HAL_RTC_WRITEPROTECTION_DISABLE(&hrtc);
  
  RCC->APB1ENR1 |= RCC_APB1ENR1_PWREN;

  //__HAL_RTC_WRITEPROTECTION_ENABLE(&hrtc);  
  //__HAL_RCC_RTC_DISABLE();
  //__HAL_RCC_BACKUPRESET_FORCE();
  //__HAL_RCC_BACKUPRESET_RELEASE(); 
  //HAL_PWR_EnableBkUpAccess();
  
    // Enable Power clock
    //__HAL_RCC_PWR_CLK_ENABLE();
 
    // Enable access to Backup domain
    //HAL_PWR_EnableBkUpAccess();
 
    // Reset Backup domain
    //__HAL_RCC_BACKUPRESET_FORCE();
    //__HAL_RCC_BACKUPRESET_RELEASE();
 
    // Disable access to Backup domain
    //HAL_PWR_DisableBkUpAccess();   
    
  //__HAL_RCC_BKP_CLK_ENABLE();
  
  RCC->BDCR |= RCC_BDCR_LSEBYP;
  //Включаем LSE
  RCC->BDCR |= RCC_BDCR_LSEON;  
  // Ждем его готовности
  while (!(RCC->BDCR & RCC_BDCR_LSEON)){} 
  //Выбираем LSE в качестве источника (кварц 32768) 
  RCC->BDCR |= RCC_BDCR_RTCSEL_0;
  RCC->BDCR |= RCC_BDCR_LSCOSEL;
  RCC->BDCR &= ~RCC_BDCR_RTCSEL_1;
  //Включаем тактирование RTC
  RCC->BDCR |= RCC_BDCR_RTCEN; 
  HAL_RTC_WaitForSynchro(&hrtc);
  
  __HAL_RCC_RTC_ENABLE();

//}
  
  hrtc.Instance = RTC;
  hrtc.Init.HourFormat = RTC_HOURFORMAT_24;
  hrtc.Init.AsynchPrediv = 127;
  hrtc.Init.SynchPrediv = 255;
  hrtc.Init.OutPut = RTC_OUTPUT_DISABLE;
  hrtc.Init.OutPutRemap = RTC_OUTPUT_REMAP_NONE;
  hrtc.Init.OutPutPolarity = RTC_OUTPUT_POLARITY_HIGH;
  hrtc.Init.OutPutType = RTC_OUTPUT_TYPE_OPENDRAIN;
  if (HAL_RTC_Init(&hrtc) != HAL_OK)
  {
    Error_Handler();
  }
  /**Enable the RTC Tamper 1 
  */
  /*
  sTamper.Tamper = RTC_TAMPER_1;
  sTamper.Trigger = RTC_TAMPERTRIGGER_RISINGEDGE;
  sTamper.NoErase = RTC_TAMPER_ERASE_BACKUP_DISABLE;
  sTamper.MaskFlag = RTC_TAMPERMASK_FLAG_DISABLE;
  sTamper.Filter = RTC_TAMPERFILTER_DISABLE;
  sTamper.SamplingFrequency = RTC_TAMPERSAMPLINGFREQ_RTCCLK_DIV32768;
  sTamper.PrechargeDuration = RTC_TAMPERPRECHARGEDURATION_1RTCCLK;
  sTamper.TamperPullUp = RTC_TAMPER_PULLUP_ENABLE;
  sTamper.TimeStampOnTamperDetection = RTC_TIMESTAMPONTAMPERDETECTION_ENABLE;
  if (HAL_RTCEx_SetTamper(&hrtc, &sTamper) != HAL_OK)
  {
    Error_Handler();
  }*/
  /**Enable the reference Clock input 
  */
  if (HAL_RTCEx_SetRefClock(&hrtc) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN RTC_Init 2 */
  hrtc.State = HAL_RTC_STATE_READY;
  HAL_RTCEx_EnableBypassShadow(&hrtc);
  //HAL_PWR_DisableBkUpAccess();
  //HAL_RTCEx_DisableBypassShadow(&hrtc);
  /* USER CODE END RTC_Init 2 */
		//Проверяем тикают ли часики
                //if(RTC->ISR & RTC_ISR_INITS) return;
HAL_RTCEx_DeactivateTamper(&hrtc, RTC_TAMPER_1);
__HAL_RTC_TAMPER_CLEAR_FLAG(&hrtc, RTC_FLAG_TAMP1F);  

  __HAL_RTC_WRITEPROTECTION_DISABLE(&hrtc); 
  HAL_PWR_EnableBkUpAccess();
  HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR1, 0x32F2);
  //backupReadData = HAL_RTCEx_BKUPRead(&hrtc, RTC_BKP_DR0); 
  //__HAL_RTC_WRITEPROTECTION_ENABLE(&hrtc);
  
}
}

/**
  * @brief TIM7 Initialization Function
  * @param None
  * @retval None
  */


/**
  * @brief USART2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART2_UART_Init(void)
{

  /* USER CODE BEGIN USART2_Init 0 */

  /* USER CODE END USART2_Init 0 */

  /* USER CODE BEGIN USART2_Init 1 */
  __USART2_CLK_ENABLE();
  /* USER CODE END USART2_Init 1 */
  huart2.Instance = USART2;
  huart2.Init.BaudRate = 9600;
  huart2.Init.WordLength = UART_WORDLENGTH_8B;
  huart2.Init.StopBits = UART_STOPBITS_1;
  huart2.Init.Parity = UART_PARITY_NONE;
  huart2.Init.Mode = UART_MODE_TX_RX;
  huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart2.Init.OverSampling = UART_OVERSAMPLING_8;
  huart2.Init.OneBitSampling = UART_ONE_BIT_SAMPLE_ENABLE;//UART_ONE_BIT_SAMPLE_ENABLE UART_ONE_BIT_SAMPLE_DISABLE
  huart2.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_SWAP_INIT;
  huart2.AdvancedInit.Swap = UART_ADVFEATURE_SWAP_ENABLE;
  if (HAL_UART_Init(&huart2) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART2_Init 2 */
  
  HAL_NVIC_SetPriority(USART2_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(USART2_IRQn);
  
  __HAL_UART_ENABLE(&huart2);
  
  //NVIC_EnableIRQ(USART2_IRQn);
  //USART2->CR1 |= USART_CR1_RXNEIE;
  /* USER CODE END USART2_Init 2 */

}

/* FMC initialization function */
static void MX_FMC_Init(void)
{
  FMC_NORSRAM_TimingTypeDef Timing;

  /** Perform the SRAM1 memory initialization sequence
  */
  hsram1.Instance = FMC_NORSRAM_DEVICE;
  hsram1.Extended = FMC_NORSRAM_EXTENDED_DEVICE;
  /* hsram1.Init */
  hsram1.Init.NSBank = FMC_NORSRAM_BANK1;
  hsram1.Init.DataAddressMux = FMC_DATA_ADDRESS_MUX_DISABLE;
  hsram1.Init.MemoryType = FMC_MEMORY_TYPE_SRAM;
  hsram1.Init.MemoryDataWidth = FMC_NORSRAM_MEM_BUS_WIDTH_8;
  hsram1.Init.BurstAccessMode = FMC_BURST_ACCESS_MODE_DISABLE;
  hsram1.Init.WaitSignalPolarity = FMC_WAIT_SIGNAL_POLARITY_LOW;
  hsram1.Init.WaitSignalActive = FMC_WAIT_TIMING_BEFORE_WS;
  hsram1.Init.WriteOperation = FMC_WRITE_OPERATION_ENABLE;
  hsram1.Init.WaitSignal = FMC_WAIT_SIGNAL_DISABLE;
  hsram1.Init.ExtendedMode = FMC_EXTENDED_MODE_DISABLE;
  hsram1.Init.AsynchronousWait = FMC_ASYNCHRONOUS_WAIT_DISABLE;
  hsram1.Init.WriteBurst = FMC_WRITE_BURST_DISABLE;
  hsram1.Init.ContinuousClock = FMC_CONTINUOUS_CLOCK_SYNC_ONLY;
  hsram1.Init.PageSize = FMC_PAGE_SIZE_NONE;
  /* Timing */
  Timing.AddressSetupTime = 15;
  Timing.AddressHoldTime = 15;
  Timing.DataSetupTime = 255;
  Timing.BusTurnAroundDuration = 15;
  Timing.CLKDivision = 16;
  Timing.DataLatency = 17;
  Timing.AccessMode = FMC_ACCESS_MODE_A;
  /* ExtTiming */

  if (HAL_SRAM_Init(&hsram1, &Timing, NULL) != HAL_OK)
  {
    Error_Handler( );
  }

  /** Perform the SRAM2 memory initialization sequence
  */
  hsram2.Instance = FMC_NORSRAM_DEVICE;
  hsram2.Extended = FMC_NORSRAM_EXTENDED_DEVICE;
  /* hsram2.Init */
  hsram2.Init.NSBank = FMC_NORSRAM_BANK2;
  hsram2.Init.DataAddressMux = FMC_DATA_ADDRESS_MUX_DISABLE;
  hsram2.Init.MemoryType = FMC_MEMORY_TYPE_SRAM;
  hsram2.Init.MemoryDataWidth = FMC_NORSRAM_MEM_BUS_WIDTH_16;
  hsram2.Init.BurstAccessMode = FMC_BURST_ACCESS_MODE_DISABLE;
  hsram2.Init.WaitSignalPolarity = FMC_WAIT_SIGNAL_POLARITY_LOW;
  hsram2.Init.WaitSignalActive = FMC_WAIT_TIMING_BEFORE_WS;
  hsram2.Init.WriteOperation = FMC_WRITE_OPERATION_ENABLE;
  hsram2.Init.WaitSignal = FMC_WAIT_SIGNAL_DISABLE;
  hsram2.Init.ExtendedMode = FMC_EXTENDED_MODE_DISABLE;
  hsram2.Init.AsynchronousWait = FMC_ASYNCHRONOUS_WAIT_DISABLE;
  hsram2.Init.WriteBurst = FMC_WRITE_BURST_DISABLE;
  hsram2.Init.ContinuousClock = FMC_CONTINUOUS_CLOCK_SYNC_ONLY;
  hsram2.Init.PageSize = FMC_PAGE_SIZE_NONE;
  /* Timing */
  Timing.AddressSetupTime = 15;
  Timing.AddressHoldTime = 15;
  Timing.DataSetupTime = 200;
  Timing.BusTurnAroundDuration = 15;
  Timing.CLKDivision = 16;
  Timing.DataLatency = 17;
  Timing.AccessMode = FMC_ACCESS_MODE_A;
  /* ExtTiming */

  if (HAL_SRAM_Init(&hsram2, &Timing, NULL) != HAL_OK)
  {
    Error_Handler( );
  }

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOF_CLK_ENABLE();
  __HAL_RCC_GPIOH_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();
  __HAL_RCC_GPIOG_CLK_ENABLE();
  __HAL_RCC_GPIOE_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();
  HAL_PWREx_EnableVddIO2();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOC, DTR_Pin|DCD_Pin|RING_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOA, LED1_Pin|LED2_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOB, RES_Pin|NETLIGHT_Pin|BUZZER_Pin|GSM_RST_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pins : DTR_Pin DCD_Pin RING_Pin */
  GPIO_InitStruct.Pin = DTR_Pin|DCD_Pin|RING_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  GPIO_InitStruct.Pin = GPIO_PIN_6 | GPIO_PIN_7 | GPIO_PIN_8 | GPIO_PIN_9 | GPIO_PIN_10 | GPIO_PIN_11 | GPIO_PIN_12;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLDOWN;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);  
  GPIO_InitStruct.Pin = GPIO_PIN_6 | GPIO_PIN_7 | GPIO_PIN_8 | GPIO_PIN_9 | GPIO_PIN_10 | GPIO_PIN_11;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLDOWN;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOF, &GPIO_InitStruct);    
  GPIO_InitStruct.Pin = GPIO_PIN_6 | GPIO_PIN_7 | GPIO_PIN_8 | GPIO_PIN_13 | GPIO_PIN_10 | GPIO_PIN_11 | GPIO_PIN_12 | GPIO_PIN_14 | GPIO_PIN_15;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLDOWN;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOG, &GPIO_InitStruct);    
  /*Configure GPIO pins : LED1_Pin LED2_Pin */
  GPIO_InitStruct.Pin = LED1_Pin|LED2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /*Configure GPIO pin : DETECT_Pin */
  GPIO_InitStruct.Pin = DETECT_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(DETECT_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pins : RES_Pin NETLIGHT_Pin BUZZER_Pin GSM_RST_Pin */
  GPIO_InitStruct.Pin = RES_Pin|BUZZER_Pin|GSM_RST_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
  //RES_Pin NETLIGHT
  GPIO_InitStruct.Pin = NETLIGHT_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);  
  

  /*Configure GPIO pins : KEY1_Pin KEY2_Pin KEY3_Pin */
  GPIO_InitStruct.Pin = KEY1_Pin|KEY2_Pin|KEY3_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

}

/* USER CODE BEGIN 4 */
uint8_t rtc_Init(void)                                                                     // Инициализация модуля
  {
    uint8_t returned = 0;
    if (HAL_RTCEx_BKUPRead(&hrtc, RTC_BKP_DR0) != 0x32F2){ 
//{
//RCC_APB1PeriphClockCmd(RCC_APB1Periph_PWR, ENABLE);
//PWR_BackupAccessCmd(ENABLE);
//RCC_BackupResetCmd(ENABLE);
//RCC_BackupResetCmd(DISABLE);
//RCC_LSEConfig(RCC_LSE_ON);                                                            // Enable the LSE OSC
//while(RCC_GetFlagStatus(RCC_FLAG_LSERDY) == RESET){}                                  // Wait till LSE is ready
//RCC_RTCCLKConfig(RCC_RTCCLKSource_LSE);                                               // Select the RTC Clock Source
//RCC_RTCCLKCmd(ENABLE);
//RTC_StructInit(&RTC_InitStructure);
//RTC_InitStructure.RTC_HourFormat = RTC_HourFormat_24;
//RTC_InitStructure.RTC_AsynchPrediv = 127;
//RTC_InitStructure.RTC_SynchPrediv = 255;
//RTC_Init(&RTC_InitStructure);    

  uint32_t LSERDY_time_out = 0xFFFF;
  uint32_t ALRA_time_out   = 0xFFFF;
  
  
  RCC->APB1ENR1 |= RCC_APB1ENR1_PWREN;
  PWR->CR1 |= PWR_CR1_DBP;                                                                // Open access to Backup regs
//RCC->BDCR |= RCC_BDCR_BDRST;
//RCC->BDCR &= ~RCC_BDCR_BDRST;
  
  RCC->BDCR |= RCC_BDCR_LSEBYP;
  //RCC->BDCR |= RCC_BDCR_LSEON;
  
  while((!(RCC->BDCR & RCC_BDCR_LSERDY))&&(LSERDY_time_out != 0))                       // Проверка наличия клока LS (сопоставить поля с user manual)
    {
    LSERDY_time_out--;
    }
  if(LSERDY_time_out==0) returned = 1;                                                  // Бит 0 = 1 если нет LS клока
  
//RCC->BDCR |= RCC_BDCR_RTCSEL_0;
  RCC->BDCR = (RCC->BDCR & (~RCC_BDCR_RTCSEL)) | RCC_BDCR_RTCSEL_0;       
  RCC->BDCR |= RCC_BDCR_RTCEN;
  //RTC_WaitForSynchro();
  HAL_RTC_WaitForSynchro(&hrtc);
  RTC->WPR = 0xCA;                                                                      // Open access to RTC
  RTC->WPR = 0x53;                                                                      // Open access to RTC
  RTC->CR &= ~RTC_CR_FMT;                                                               // 24h format
  RTC->PRER |= 0xFF;
  RTC->PRER |= (uint32_t)(0x7F << 16);	
  //Alarm A Every 1 second
  //RTC->ISR = ~RTC_ISR_ALRAF; //STM32 is stuck
  //EXTI->PR = EXTI_PR_PR17;
  //EXTI->IMR |= EXTI_IMR_MR17;
  //EXTI->EMR &= ~EXTI_EMR_MR17;
  //EXTI->RTSR |= EXTI_RTSR_TR17;	
//  NVIC_EnableIRQ(RTC_Alarm_IRQn);
  RTC->CR &= ~RTC_CR_ALRAE;
  
  while((!(RTC->ISR & RTC_ISR_ALRAWF))&&(ALRA_time_out != 0))
    {
    ALRA_time_out--;
    }	
  if(ALRA_time_out==0) returned |= 2;                                                   // Бит 1 = 1 если не Alarm A update allowed;
  
  RTC->ALRMAR |= RTC_ALRMAR_MSK1 | RTC_ALRMAR_MSK2 | RTC_ALRMAR_MSK3 | RTC_ALRMAR_MSK4 | RTC_ALRMAR_SU_0;//Alarm every 1 second
  RTC->CR |= RTC_CR_ALRAE;
  RTC->CR |= RTC_CR_ALRAIE;
  RTC->WPR = 0xFF;                                                                      // Close access to RTC
  HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR2, 0x32F2);
//}
  
    }
    return returned;
  }
/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */

  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(char *file, uint32_t line)
{ 
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     tex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/

/*  
  HAL_GPIO_WritePin(GSM_RST_GPIO_Port, GSM_RST_Pin, GPIO_PIN_SET);
  
  gnss_startup_delay = 20000;//110ms
  gnss_reset_pulse_enable = 1;
  HAL_GPIO_WritePin(GSM_RST_GPIO_Port, GSM_RST_Pin, GPIO_PIN_SET);
  
  while(gnss_reset_pulse_enable != 2);
  gnss_startup_delay = 50000;
  while(gnss_startup_delay != 0);
  
  gnss_startup_delay = 2000;
  while(gnss_startup_delay != 0) asm("nop");
  HAL_GPIO_WritePin(GSM_RST_GPIO_Port, GSM_RST_Pin, GPIO_PIN_SET);
  gnss_startup_delay = 2000;
  while(gnss_startup_delay != 0) asm("nop");
  HAL_GPIO_WritePin(GSM_RST_GPIO_Port, GSM_RST_Pin, GPIO_PIN_RESET);
  */
  
  //HAL_GPIO_WritePin(GSM_RST_GPIO_Port, GSM_RST_Pin, GPIO_PIN_SET);
  //gnss_startup_delay = 5000;
  //while(gnss_startup_delay != 0) asm("nop");  
  
  /*
  HAL_GPIO_WritePin(GSM_RST_GPIO_Port, GSM_RST_Pin, GPIO_PIN_RESET);
  gnss_startup_delay = 2000;
  while(gnss_startup_delay != 0) asm("nop");
  HAL_GPIO_WritePin(GSM_RST_GPIO_Port, GSM_RST_Pin, GPIO_PIN_SET);
  gnss_startup_delay = 30000;
  while(gnss_startup_delay != 0) asm("nop");  
  HAL_GPIO_WritePin(GSM_RST_GPIO_Port, GSM_RST_Pin, GPIO_PIN_RESET);
 */


  /*
 HAL_SRAM_WriteOperation_Disable( &hsram1);//oled
  
  for (uint8_t uwIndex = 0; uwIndex < 6; uwIndex++)
  {
    *(__IO uint16_t*) (SRAM_BANK_ADDR + WRITE_READ_ADDR + 2*uwIndex) = sram_tx_buf[uwIndex];
  }    
  
  for (uint8_t uwIndex = 0; uwIndex < 6; uwIndex++)
  {
    sram_rx_buf[uwIndex] = *(__IO uint16_t*) (SRAM_BANK_ADDR + WRITE_READ_ADDR + 2*uwIndex);
  } 
  HAL_SRAM_WriteOperation_Enable( &hsram1);//oled
  */

 //LL_TIM_DisableCounter(TIM7);  
  /*
 HAL_SRAM_WriteOperation_Disable( &hsram1);//oled
  
  for (uint8_t uwIndex = 0; uwIndex < 6; uwIndex++)
  {
    *(__IO uint16_t*) (SRAM_BANK_ADDR + WRITE_READ_ADDR + 2*uwIndex) = sram_tx_buf[uwIndex];
  }    
  
  for (uint8_t uwIndex = 0; uwIndex < 6; uwIndex++)
  {
    sram_rx_buf[uwIndex] = *(__IO uint16_t*) (SRAM_BANK_ADDR + WRITE_READ_ADDR + 2*uwIndex);
  } 
  HAL_SRAM_WriteOperation_Enable( &hsram1);//oled
  */
  
//LL_TIM_EnableCounter(TIM7);


    /*
    //usb section
    if(((UserRxBufferFS[0] == 0x7f) && (UserRxBufferFS[1] == 0xaa))||(usb_sending_data == 1)){
     
      if(UserRxBufferFS[3] == 0x01){//opCode for sending records data
        //temp_recordCnt = fram_read_settings(6);
        temp_recordCnt = fram_read_settings(7);
        //if(temp_recordCnt >= 1024)temp_recordCnt = 1024;
        fram_read_buf(temp_dataRecord, 64, 0);
        UserTxBufferFS[0] = (uint8_t)(temp_recordCnt>>24);
        UserTxBufferFS[1] = (uint8_t)(temp_recordCnt>>16);
        UserTxBufferFS[2] = (uint8_t)(temp_recordCnt>>8);
        UserTxBufferFS[3] = (uint8_t)(temp_recordCnt&0xff);
        //UserTxBufferFS[4] = 0xaa;
        //UserTxBufferFS[5] = 0x55;
        //UserTxBufferFS[6] = 0x01;
        //UserTxBufferFS[7] = 0x02;
        for(uint8_t usb_i = 0; usb_i < 28; usb_i++){
          UserTxBufferFS[2*usb_i+4] = (uint8_t)(temp_dataRecord[usb_i]>>8);
          UserTxBufferFS[2*usb_i+5] = (uint8_t)(temp_dataRecord[usb_i]&0xff);
          
        }
        
        for(uint32_t i_usb = 0; i_usb<(2*temp_recordCnt);i_usb++){
          UserTxBufferFS[2*i_usb+4] = (uint8_t)(temp_dataRecord[i_usb]>>8);
          UserTxBufferFS[2*i_usb+5] = (uint8_t)(temp_dataRecord[i_usb]&0xff);
        }
        
        
        //USBD_CDC_SetTxBuffer(&hUsbDeviceFS, &UserTxBufferFS[0], 64);
        //USBD_CDC_TransmitPacket(&hUsbDeviceFS);        
        CDC_Transmit_FS(UserTxBufferFS, 64);
        //CDC_Transmit_FS(UserTxBufferFS, 64);
     
      }//opcode 0x01
      if(UserRxBufferFS[3] == 0x02){
        agm.serial_number = (UserRxBufferFS[4]<<8)|(UserRxBufferFS[5]);
        fram_write_settings(agm.serial_number, 10);
        
        //CDC_Transmit_FS(UserTxBufferFS, 2048);
      }
      if(UserRxBufferFS[3] == 0x03){
        //agm.serial_number = (UserRxBufferFS[4]<<8)|(UserRxBufferFS[5]);
        //fram_write_settings(agm.serial_number, 10);
        fram_erase_event = 1;
        //CDC_Transmit_FS(UserTxBufferFS, 2048);
      }
      if(UserRxBufferFS[3] == 0x04){
        notch_filter_event = 1; 
        if(UserRxBufferFS[4] == 0x00)agm_option_menu.notch_filter = 0;//50Hz
        if(UserRxBufferFS[4] == 0x01)agm_option_menu.notch_filter = 1;//60Hz
        //CDC_Transmit_FS(UserTxBufferFS, 2048);
      }  
      if(UserRxBufferFS[3] == 0x05){//utc timezone

        //CDC_Transmit_FS(UserTxBufferFS, 2048);
      }       
      
      //clear start byte to prevent double proc
      UserRxBufferFS[0] = 0x00;

    }//usb receive cmd
    */