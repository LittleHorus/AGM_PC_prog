/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    stm32l4xx_it.c
  * @brief   Interrupt Service Routines.
  ******************************************************************************
  *
  * COPYRIGHT(c) 2019 STMicroelectronics
  *
  * Redistribution and use in source and binary forms, with or without modification,
  * are permitted provided that the following conditions are met:
  *   1. Redistributions of source code must retain the above copyright notice,
  *      this list of conditions and the following disclaimer.
  *   2. Redistributions in binary form must reproduce the above copyright notice,
  *      this list of conditions and the following disclaimer in the documentation
  *      and/or other materials provided with the distribution.
  *   3. Neither the name of STMicroelectronics nor the names of its contributors
  *      may be used to endorse or promote products derived from this software
  *      without specific prior written permission.
  *
  * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
  * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
  * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
  * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
  * FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
  * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
  * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
  * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
  * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
  * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "stm32l4xx_it.h"
/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "oled.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN TD */

/* USER CODE END TD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
 
#define GNSS_GLL 3
#define GNSS_RMC 2
#define GNSS_OK  1
#define AGM_SLEEP_TIME 200000

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
/* USER CODE BEGIN PV */
unsigned int led_toggle = 0;
uint16_t adc_ch1, adc_ch2;
uint8_t adc_order = 0, adc_ready;
uint16_t adc_fetch_timeout = 10000;
float voltage_monitor = 0;
extern uint16_t gnss_startup_delay;
uint16_t display_refresh_timer = 0, main_menu_change_stings_cnt = 0;
uint8_t main_menu_string_state = 0;
uint8_t uart_rx_counter = 0;
extern uint8_t receiveBuffer[200];
extern struct device_status_struct agm;
uint8_t screen_type = 0;
uint8_t gain_update = 0;
extern uint16_t blink_active_param;
extern char menu_ring_cnt;
extern char menu_level;
char last_menu_level = 0;
uint16_t logo_delay = 60000;
uint8_t agm_logo_lock = 1;
uint32_t _agm_sleep_timer = 0;
uint8_t sleep_mode_state = 0;
uint16_t _sleep_blink = 0;
uint16_t buzzer_button_cnt = 0; 
uint8_t buzzer_button = 0;
extern uint8_t error_led_state;
uint16_t error_led_cnt = 0;
extern uint32_t card_watcher;
extern uint16_t keys_timer;
extern uint16_t key1_cnt;
extern uint8_t key1_prestate, key1_state, key1_press_cnt;
extern uint16_t key2_cnt;
extern uint8_t key2_prestate, key2_state, key2_press_cnt;
extern uint16_t key3_cnt;
extern uint8_t key3_prestate, key3_state, key3_press_cnt;

extern uint8_t key1_lock, key1_long_press_enable, key1_short_press_enable, key1_press_flag;
extern uint8_t key2_lock, key2_long_press_enable, key2_short_press_enable, key2_press_flag;
extern uint8_t key3_lock, key3_long_press_enable, key3_short_press_enable, key3_press_flag;
extern uint8_t buzzer_alarm;
uint8_t  uartRxBuf[100], uartTxBuf[100];
uint8_t  uartCntRx = 0, uartCntTx = 0;
extern uint32_t gps_update_data_timer;
extern uint16_t time_update_cnt;
extern uint8_t record_number;
char atCmdPowOn[11] = "AT+QGNSSC=1";
char atCmdRD[11] = "AT+QGNSSRD=";
char atGLL[10] = "\"NMEA/GLL\"";
char atRMC[10] = "\"NMEA/RMC\"";
char atCmdOk[2] = "AT";
extern char atCmdGLL[23];
uint16_t icon_blink_cnt = 0;
uint8_t icon_blink_state = 0;

extern uint8_t notch_filter_configure, adc_m_cnt;   
extern uint16_t adc_m[25];
extern uint16_t record_start_delay_cnt; 
extern uint8_t record_start_delay_done;

extern uint8_t gps_latch_done;
extern uint32_t gps_latch_timer;
uint32_t gnssTC = 40001, gnssRC = 0; // TC&RC - complete transfer data
uint8_t gnssHourBuf[2], gnssMinuteBuf[2], gnssSecBuf[2], gnssSubSecBuf[3];//time from gnss module
uint8_t gnssLatitudeDdBuf[2], gnssLatitudeMmBuf[6];
uint8_t gnssLongitudeDddBuf[3], gnssLongitudeMmBuf[6];
uint8_t gnssLatitudeDir = 0, gnssLongitudeDir = 0;// (N or S) & (W or E)
uint8_t gnssOpCode = 0, gnssPowRdy = 0;
uint16_t gnss_wait_wakeup_after_reset = 0; 
extern uint8_t gnss_reset_pulse_enable;
extern char gll_received;
extern uint8_t gps_oled_string[23];
extern uint8_t agm_standby_active_mode;
extern RTC_TimeTypeDef    sTime, recordTime;
extern RTC_DateTypeDef    DateToUpdate, recordDate;
extern RTC_TimeTypeDef    sTime_set;
extern RTC_DateTypeDef    DateToUpdate_set;
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
  
}extern agm_gps_status;



/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/* External variables --------------------------------------------------------*/
extern PCD_HandleTypeDef hpcd_USB_OTG_FS;
extern UART_HandleTypeDef huart2;
/* USER CODE BEGIN EV */

/* USER CODE END EV */

/******************************************************************************/
/*           Cortex-M4 Processor Interruption and Exception Handlers          */ 
/******************************************************************************/
/**
  * @brief This function handles Non maskable interrupt.
  */
void NMI_Handler(void)
{
  /* USER CODE BEGIN NonMaskableInt_IRQn 0 */

  /* USER CODE END NonMaskableInt_IRQn 0 */
  /* USER CODE BEGIN NonMaskableInt_IRQn 1 */

  /* USER CODE END NonMaskableInt_IRQn 1 */
}

/**
  * @brief This function handles Hard fault interrupt.
  */
void HardFault_Handler(void)
{
  /* USER CODE BEGIN HardFault_IRQn 0 */

  /* USER CODE END HardFault_IRQn 0 */
  while (1)
  {
    /* USER CODE BEGIN W1_HardFault_IRQn 0 */
    /* USER CODE END W1_HardFault_IRQn 0 */
  }
}

/**
  * @brief This function handles Memory management fault.
  */
void MemManage_Handler(void)
{
  /* USER CODE BEGIN MemoryManagement_IRQn 0 */

  /* USER CODE END MemoryManagement_IRQn 0 */
  while (1)
  {
    /* USER CODE BEGIN W1_MemoryManagement_IRQn 0 */
    /* USER CODE END W1_MemoryManagement_IRQn 0 */
  }
}

/**
  * @brief This function handles Prefetch fault, memory access fault.
  */
void BusFault_Handler(void)
{
  /* USER CODE BEGIN BusFault_IRQn 0 */

  /* USER CODE END BusFault_IRQn 0 */
  while (1)
  {
    /* USER CODE BEGIN W1_BusFault_IRQn 0 */
    /* USER CODE END W1_BusFault_IRQn 0 */
  }
}

/**
  * @brief This function handles Undefined instruction or illegal state.
  */
void UsageFault_Handler(void)
{
  /* USER CODE BEGIN UsageFault_IRQn 0 */

  /* USER CODE END UsageFault_IRQn 0 */
  while (1)
  {
    /* USER CODE BEGIN W1_UsageFault_IRQn 0 */
    /* USER CODE END W1_UsageFault_IRQn 0 */
  }
}

/**
  * @brief This function handles System service call via SWI instruction.
  */
void SVC_Handler(void)
{
  /* USER CODE BEGIN SVCall_IRQn 0 */

  /* USER CODE END SVCall_IRQn 0 */
  /* USER CODE BEGIN SVCall_IRQn 1 */

  /* USER CODE END SVCall_IRQn 1 */
}

/**
  * @brief This function handles Debug monitor.
  */
void DebugMon_Handler(void)
{
  /* USER CODE BEGIN DebugMonitor_IRQn 0 */

  /* USER CODE END DebugMonitor_IRQn 0 */
  /* USER CODE BEGIN DebugMonitor_IRQn 1 */

  /* USER CODE END DebugMonitor_IRQn 1 */
}

/**
  * @brief This function handles Pendable request for system service.
  */
void PendSV_Handler(void)
{
  /* USER CODE BEGIN PendSV_IRQn 0 */

  /* USER CODE END PendSV_IRQn 0 */
  /* USER CODE BEGIN PendSV_IRQn 1 */

  /* USER CODE END PendSV_IRQn 1 */
}

/**
  * @brief This function handles System tick timer.
  */
void SysTick_Handler(void)
{
  /* USER CODE BEGIN SysTick_IRQn 0 */

  /* USER CODE END SysTick_IRQn 0 */
  HAL_IncTick();
  /* USER CODE BEGIN SysTick_IRQn 1 */

  /* USER CODE END SysTick_IRQn 1 */
}

/******************************************************************************/
/* STM32L4xx Peripheral Interrupt Handlers                                    */
/* Add here the Interrupt Handlers for the used peripherals.                  */
/* For the available peripheral interrupt handler names,                      */
/* please refer to the startup file (startup_stm32l4xx.s).                    */
/******************************************************************************/

/**
  * @brief This function handles USART2 global interrupt.
  */
void USART2_IRQHandler(void)
{
  /* USER CODE BEGIN USART2_IRQn 0 */
/*
 if (USART2->ISR & USART_ISR_ORE) // Overrun Error
 USART2->ICR = USART_ICR_ORECF;
 if (USART2->ISR & USART_ISR_NE) // Noise Error
 USART2->ICR = USART_ICR_NCF;
 if (USART2->ISR & USART_ISR_FE) // Framing Error
 USART2->ICR = USART_ICR_FECF;
 
  if((USART2->ISR & USART_ISR_RXNE)  == USART_ISR_RXNE){
      
      uartRxBuf[uartCntRx] = USART2->RDR;
      if((uartRxBuf[uartCntRx] == 0x0A) && (uartRxBuf[uartCntRx-1] == 0x0D))  uartCntRx = 0;
      else uartCntRx++;
      if(uartCntRx >= 100)uartCntRx = 0;
       
  }
  
  if((USART2->ISR & USART_ISR_TXE) == USART_ISR_TXE){
    USART2->TDR = atCmdGLL[uartCntTx++];
    if(uartCntTx >= 23){
      uartCntTx = 0;
      __HAL_UART_DISABLE_IT(&huart2 , UART_IT_TXE);
      USART2->CR1 &= ~USART_CR1_TXEIE;
      gnssTC = 40000;
      
      __HAL_UART_CLEAR_FLAG(&huart2, UART_CLEAR_TCF);
    }
    
    __HAL_UART_CLEAR_IT(&huart2,UART_TXDATA_FLUSH_REQUEST);
  }
  
 */ 
  /* USER CODE END USART2_IRQn 0 */
  HAL_UART_IRQHandler(&huart2);
  /* USER CODE BEGIN USART2_IRQn 1 */

  //uint8_t x;
  //HAL_UART_Receive_IT(&huart2, &x, 1); // получаем символ  
  //receiveBuffer[uart_rx_counter++] = x;
  //if(x == '\n') uart_rx_counter = 0;
  
  
  /* USER CODE END USART2_IRQn 1 */
}

/**
  * @brief This function handles TIM7 global interrupt.
  */
void TIM7_IRQHandler(void)
{
  /* USER CODE BEGIN TIM7_IRQn 0 */
  //10kHz update frequency
  if(LL_TIM_IsActiveFlag_UPDATE(TIM7) == 1){
    
    if(gps_update_data_timer != 0)gps_update_data_timer--;
       
    /*
    if(gnss_startup_delay != 0)gnss_startup_delay--;
    if((gnss_reset_pulse_enable == 1) && (gnss_startup_delay == 0)){
      HAL_GPIO_WritePin(GSM_RST_GPIO_Port, GSM_RST_Pin, GPIO_PIN_RESET);
      gnss_reset_pulse_enable = 2;
      gnss_wait_wakeup_after_reset = 50000;
    }
    if(gnss_wait_wakeup_after_reset != 0) gnss_wait_wakeup_after_reset--;
    if((gnss_wait_wakeup_after_reset == 0) && (gnss_reset_pulse_enable == 2))gnssPowRdy = 1;
    */
    if(gps_latch_timer != 0)gps_latch_timer--;
    
    if((gps_latch_timer ==1180000) && (gps_latch_done == 0)){
      HAL_GPIO_WritePin(GPIOC, GPIO_PIN_2, GPIO_PIN_SET);
      //HAL_GPIO_WritePin(GPIOC, GPIO_PIN_2, GPIO_PIN_RESET);
    }
    
    if((gps_latch_timer ==5000) && (gps_latch_done == 0)){
      HAL_GPIO_WritePin(GPIOC, GPIO_PIN_2, GPIO_PIN_RESET);
      //HAL_GPIO_WritePin(GPIOC, GPIO_PIN_2, GPIO_PIN_SET);
    }
    if((gps_latch_timer ==1) && (gps_latch_done == 0)){
      
      HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+QGNSSC=1\r\n", 13);
      //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+QSCLK=0\r\n", 12);
      //HAL_UART_Transmit_IT(&huart2, (uint8_t*)"AT+CFUN=0\r\n", 11);
      //gps_latch_done = 0;
    }
    if(gnss_startup_delay != 0)gnss_startup_delay--;
    if(time_update_cnt != 0)time_update_cnt--;
    
    if(error_led_state == 2)HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET);
    if(error_led_state == 1){
      error_led_cnt++;
      if(error_led_cnt == 9800){
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET);
      }
      if(error_led_cnt >= 10000){
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET);
        error_led_cnt = 0;
      }
        
    }
    if(error_led_state == 0){
      error_led_cnt = 0;
    }
    if(record_start_delay_cnt == 1)record_start_delay_done = 1;
    if(record_start_delay_cnt != 0)record_start_delay_cnt--;
    //100ms - 10Hz sample rate for mag detector
    if(ADC1->ISR & ADC_ISR_EOC){
        
      if(adc_order == 0){
        adc_ch1 = ADC1->DR;
        gain_update = 1;
        
        if(notch_filter_configure == 1){
          adc_m[adc_m_cnt++] = adc_ch1;
          if(adc_m_cnt == 20){ adc_m_cnt = 0;
            notch_filter_configure = 0;
          }
        }

        if((adc_ready == 1)&&(adc_fetch_timeout == 0)&&(agm_standby_active_mode == 0x01)){
          if(record_start_delay_done == 1){
            threshold_buffer(adc_ch1, 100);
          }
          adc_fetch_timeout = 50;//5ms
        }
        adc_ready = 1;
        
        
      }
      if(adc_order == 1){
        adc_ch2 = ADC1->DR;
        
      }
        adc_order++;
        if(adc_order == 2) adc_order = 0;
        LL_ADC_REG_StartConversion(ADC1);
        CLEAR_BIT(ADC1->ISR, ADC_ISR_EOC);
        
        voltage_monitor = 3.116*((float)adc_ch2/4095)*3.3;  
        if(voltage_monitor < 1.6) agm.battery = BATTERY_EMPTY;
        if((voltage_monitor >= 1.6) && (voltage_monitor < 2.5))agm.battery = BATTERY_1_3;
        if((voltage_monitor >= 2.4) && (voltage_monitor < 3))agm.battery = BATTERY_2_3;
        if(voltage_monitor >= 2.9)agm.battery = BATTERY_FULL; 
    }//ADC
    if(adc_fetch_timeout !=0) adc_fetch_timeout--;
    
    
      //screen_type++;
      //if(screen_type > 2) screen_type = 1;
      //oled_clear();
      //display_refresh_timer = 60000; 
    
    
    icon_blink_cnt++;
    if(icon_blink_cnt >=1000){icon_blink_state = (icon_blink_state^1)&1;icon_blink_cnt = 0;}
    
    if(logo_delay != 0) logo_delay--;
    else agm_logo_lock = 0;
    if(agm_logo_lock == 0){
      if(menu_level != last_menu_level){
        oled_clear(); 
        display_refresh_timer = 60000;
        last_menu_level = menu_level;
      }
      if(menu_level == OPTION_MENU){
          display_refresh_timer++;
          if(display_refresh_timer>=1000){
            display_refresh_timer = 0;          
            oled_option_menu(2); //0-string show     
          }
      }
      if(menu_level == SUB_OPTION_MENU){
          display_refresh_timer++;
          if(display_refresh_timer>=1000){
            display_refresh_timer = 0;          
            if(blink_active_param < 5000)oled_option_menu(0);  
            if((blink_active_param >= 5000) &&(blink_active_param < 10000))oled_option_menu(1); 
          }
      }
      if(menu_level == STANDBY_MENU){
       _sleep_blink++;
       if(_sleep_blink == 9950)sleep_menu(1); 
       if(_sleep_blink >= 10000){
         sleep_menu(0);
         _sleep_blink = 0;
       }
      }
      if(menu_level == MAIN_MENU){
        main_menu_change_stings_cnt++;
        display_refresh_timer++;
        if((main_menu_change_stings_cnt >= 60000)&&(main_menu_string_state == 0)){main_menu_string_state = 1;main_menu_change_stings_cnt=0;}
        if((main_menu_change_stings_cnt >= 60000)&&(main_menu_string_state == 1)){main_menu_string_state = 0;main_menu_change_stings_cnt=0;}
        
        if(main_menu_string_state == 0){
          
          if(display_refresh_timer >= 10000){//update every 1sec
            display_refresh_timer = 0;
            oled_status_pict(icon_blink_state);// 3 and 4 rows
            char date_sting[23] = "001 00:00:00 00/00/00";
            char data_string_1[23] = "LST 00:00:00 00/00/00";
            //sprintf(date_sting, "00%d: 0%d:0%d:0%d 0%d/0%d/0%d", 1, sTime.Hours,sTime.Minutes,sTime.Seconds, DateToUpdate.Date,DateToUpdate.Month,DateToUpdate.Year);
            //sprintf(date_sting, "00%d: 0%d:0%d:0%d 0%d/0%d/0%d", 1, sTime.Hours,sTime.Minutes,sTime.Seconds, DateToUpdate.Date,DateToUpdate.Month,DateToUpdate.Year);
            
            date_sting[0] = (uint8_t)(0x30+agm.serial_number/100);
            date_sting[1] = (uint8_t)(0x30+(agm.serial_number/100)%10);
            date_sting[2] = (uint8_t) (0x30+agm.serial_number%10);
            
              date_sting[4] = (uint8_t)0x30u + (sTime.Hours/10);
              date_sting[5] = (uint8_t)0x30u + (sTime.Hours%10);  
              data_string_1[4] = (uint8_t)0x30u + (recordTime.Hours/10);
              data_string_1[5] = (uint8_t)0x30u + (recordTime.Hours%10);
              
              date_sting[7] = (uint8_t)0x30u + (sTime.Minutes/10);
              date_sting[8] = (uint8_t)0x30u + (sTime.Minutes%10);
              data_string_1[7] = (uint8_t)0x30u + (recordTime.Minutes/10);
              data_string_1[8] = (uint8_t)0x30u + (recordTime.Minutes%10);   

              
              date_sting[10] = (uint8_t)0x30u + (sTime.Seconds/10);
              date_sting[11] = (uint8_t)0x30u + (sTime.Seconds%10); 
              data_string_1[10] = (uint8_t)0x30u + (recordTime.Seconds/10);
              data_string_1[11] = (uint8_t)0x30u + (recordTime.Seconds%10);  

              date_sting[13] = (uint8_t)0x30u + (DateToUpdate.Date/10);
              date_sting[14] = (uint8_t)0x30u + (DateToUpdate.Date%10);
              data_string_1[13] = (uint8_t)0x30u + (recordDate.Date/10);
              data_string_1[14] = (uint8_t)0x30u + (recordDate.Date%10); 

              date_sting[16] = (uint8_t)0x30u + (DateToUpdate.Month/10);
              date_sting[17] = (uint8_t)0x30u + (DateToUpdate.Month%10);
              data_string_1[16] = (uint8_t)0x30u + (recordDate.Month/10);
              data_string_1[17] = (uint8_t)0x30u + (recordDate.Month%10);  

              date_sting[19] = (uint8_t)0x30u + (DateToUpdate.Year/10);
              date_sting[20] = (uint8_t)0x30u + (DateToUpdate.Year%10); 
              data_string_1[19] = (uint8_t)0x30u + (recordDate.Year/10);
              data_string_1[20] = (uint8_t)0x30u + (recordDate.Year%10);               

            oled_clear_string(0);
            //oled_text(date_sting, 0);
            oled_text_custom(date_sting, 0, 3);
            oled_clear_string(1);
            //oled_text(gps_oled_string, 1);
            oled_text_custom(data_string_1, 1, 3);
            //oled_text(data_string_1, 1);
            //oled_text_inv(data_string_1, 1); 

          }
        }//main_menu_string_state = 0 time
        if(main_menu_string_state == 1){  
          if(display_refresh_timer >= 10000){
            display_refresh_timer = 0;
            oled_status_pict(icon_blink_state);// 3 and 4 rows
            char date_string_0[23] = "001 00.000N  000.000W";
            char data_string_1[23] = "RECORDS    00/00.00% ";
            
            date_string_0[0] = (uint8_t)(0x30+agm.serial_number/100);
            date_string_0[1] = (uint8_t)(0x30+(agm.serial_number/100)%10);
            date_string_0[2] = (uint8_t)(0x30+agm.serial_number%10);            
            
            if(agm_gps_status.latitude_hi >= 10){
              date_string_0[4] = (uint8_t)(0x30u + agm_gps_status.latitude_hi/10);
              date_string_0[5] =(uint8_t)(0x30u + agm_gps_status.latitude_hi%10);
            }  
            if(agm_gps_status.latitude_hi < 10){
              date_string_0[4] = '0'; 
              date_string_0[5] = (uint8_t)(0x30u + (agm_gps_status.latitude_hi));
            }  

            if(agm_gps_status.latitude_lo >= 100){
              date_string_0[7] = (uint8_t)(0x30u + agm_gps_status.latitude_lo/100);
              date_string_0[8] = (uint8_t)(0x30u + (agm_gps_status.latitude_lo%100)/10);
              date_string_0[9] = (uint8_t)(0x30u + agm_gps_status.latitude_lo%10);
            }  
            if((agm_gps_status.latitude_lo >= 10)&&(agm_gps_status.latitude_lo < 100)){
              date_string_0[7] = '0';
              date_string_0[8] = (uint8_t)(0x30u + agm_gps_status.latitude_lo/10);
              date_string_0[9] = (uint8_t)(0x30u + agm_gps_status.latitude_lo%10);
            }            
            if(agm_gps_status.latitude_lo < 10){
              date_string_0[7] = '0';
              date_string_0[8] = '0';
              date_string_0[9] = (uint8_t)(0x30u + agm_gps_status.latitude_lo);
            } 
            if(agm_gps_status.latitude_direction != 0)date_string_0[10] = agm_gps_status.latitude_direction;
            else date_string_0[10] = 'N';

            uint8_t temp_longitude_hi = 0;
            if(agm_gps_status.longitude_hi >= 100){
              date_string_0[13] = (uint8_t)(0x30u + agm_gps_status.longitude_hi/100);
              temp_longitude_hi = (agm_gps_status.longitude_hi%100);
              date_string_0[14] = (uint8_t)(0x30u + temp_longitude_hi/10);
              date_string_0[15] = (uint8_t)(0x30u + agm_gps_status.longitude_hi%10);
            } 
            if((agm_gps_status.longitude_hi >= 10)&&(agm_gps_status.longitude_hi < 100)){
              date_string_0[13] = '0';
              date_string_0[14] = (uint8_t)(0x30u + (agm_gps_status.longitude_hi%100)/10);
              date_string_0[15] = (uint8_t)(0x30u + agm_gps_status.longitude_hi%10);
            }  
            if(agm_gps_status.longitude_hi < 10){
              date_string_0[13] = '0'; 
              date_string_0[14] = '0';
              date_string_0[15] = '0';//(uint8_t)(0x30u + agm_gps_status.longitude_hi);
            } 
            
            uint8_t temp_longitude = 0;
            if(agm_gps_status.longitude_lo >= 100){
              date_string_0[17] = (uint8_t)(0x30u + agm_gps_status.longitude_lo/100);
              temp_longitude = (agm_gps_status.longitude_lo%100);
              date_string_0[18] = (uint8_t)(0x30u + (temp_longitude)/10);
              date_string_0[19] = (uint8_t)(0x30u + temp_longitude%10);
            }  
            if((agm_gps_status.longitude_lo >= 10)&&(agm_gps_status.longitude_lo < 100)){
              date_string_0[17] = '0'; 
              date_string_0[18] = (uint8_t)(0x30u + agm_gps_status.longitude_lo/10);
              date_string_0[19] = (uint8_t)(0x30u + agm_gps_status.longitude_lo%10);
            }            
            if(agm_gps_status.longitude_lo < 10){
              date_string_0[17] = '0';
              date_string_0[18] = '0';
              date_string_0[19] = (uint8_t)(0x30u + agm_gps_status.longitude_lo);
            } 
            if(agm_gps_status.longitude_direction != 0)date_string_0[20] = agm_gps_status.longitude_direction;
            else date_string_0[20] = 'E';
            
            data_string_1[10] = (uint8_t)0x30 + record_number/100;
            data_string_1[11] = (uint8_t)0x30 + (record_number%100)/10;
            data_string_1[12] = (uint8_t)0x30 + record_number%10;
            
            data_string_1[14] = (uint8_t)0x30+((card_watcher*100)/262144)/10;
            data_string_1[15] = (uint8_t)0x30+((card_watcher*100)/262144)%10;
            data_string_1[17] = (uint8_t)0x30+((card_watcher*1000)/262144)/10;
            data_string_1[18] = (uint8_t)0x30+((card_watcher*10000)/262144)%10;
            oled_clear_string(0);
            //oled_text(gps_oled_string, 1);
            //oled_text_inv(date_string_0, 0);
            oled_text_custom(date_string_0, 0, 3);
            oled_clear_string(1);
            //oled_text(gps_oled_string, 1);   
            oled_text_custom(data_string_1, 1, 7);
            
            
            
          }
        }
      }

      blink_active_param++;
      if(blink_active_param >= 10000) blink_active_param = 0;
      
      if(_agm_sleep_timer<AGM_SLEEP_TIME)_agm_sleep_timer++;
      if(_agm_sleep_timer >= AGM_SLEEP_TIME)sleep_mode_state = 1;// { menu_level = STANDBY_MENU;LCD_WriteCommand(0x0f);}
      

      /*
      else { 
        if(menu_level == STANDBY_MENU){
          menu_level = MAIN_MENU;
          LCD_WriteCommand(0xff);
        }
      }
      */
      keys_timer++;
      if((KEY1_GPIO_Port->IDR & KEY1_Pin) == 0)key1_cnt++;
      if((KEY2_GPIO_Port->IDR & KEY2_Pin) == 0)key2_cnt++; 
      if((KEY3_GPIO_Port->IDR & KEY3_Pin) == 0)key3_cnt++; 

      if(keys_timer >= KEYS_RESPONSE_PERIOD){//default 100ms period | main.h |
        keys_timer = 0;
        
        if(key1_cnt > 0.7 * KEYS_RESPONSE_PERIOD){
          key1_state = 1;
          if(menu_level != MAIN_MENU)_agm_sleep_timer = 0;
          if((key1_state == 1) && (key1_prestate == 0)) key1_press_flag = 1; 
        }
        else key1_state = 0;
        
        if((key1_state == 0) && (key1_prestate == 1)){
          key1_press_flag = 0;
          key1_press_cnt = 0;
          if(key1_lock != 1){ key1_short_press_enable = 1; buzzer_button++; buzzer_alarm = 0;}
          key1_lock = 0;
        }
        if(key1_press_flag == 1) key1_press_cnt++;
        if(key1_press_cnt >= KEYS_LONG_PRESS){//1sec
          if(key1_lock != 1) { key1_long_press_enable = 1; buzzer_button++;buzzer_alarm = 0;}
           key1_lock = 1;//lock to prevent multiple activate
           }
        key1_cnt = 0;
        key1_prestate = key1_state;
        
        if(key2_cnt > 0.7 * KEYS_RESPONSE_PERIOD){
            key2_state = 1;
            if(menu_level != MAIN_MENU) _agm_sleep_timer = 0;
            if((key2_state == 1) && (key2_prestate == 0)) key2_press_flag = 1; 
        }
        else key2_state = 0;
        if((key2_state == 0) && (key2_prestate == 1)){
          key2_press_flag = 0;
          key2_press_cnt = 0;
          if(key2_lock != 1){key2_short_press_enable = 1;buzzer_button++;buzzer_alarm = 0;}
          key2_lock = 0;
        }
        if(key2_press_flag == 1) key2_press_cnt++;
            if(key2_press_cnt >= KEYS_LONG_PRESS){//2sec
              if(key2_lock != 1){ key2_long_press_enable = 1;buzzer_button++;buzzer_alarm = 0;}
              key2_lock = 1;//lock to prevent multiple activate
            }
        
        key2_cnt = 0;
        key2_prestate = key2_state;

        
        if(key3_cnt > 0.7 * KEYS_RESPONSE_PERIOD){
          key3_state = 1;
          if(menu_level != MAIN_MENU)_agm_sleep_timer = 0;
          if((key3_state == 1) && (key3_prestate == 0)) key3_press_flag = 1; 
        }
        else key3_state = 0;
        if((key3_state == 0) && (key3_prestate == 1)){
          key3_press_flag = 0;
          key3_press_cnt = 0;
          if(key3_long_press_enable != 1)key3_short_press_enable = 1;
          key3_lock = 0;
        }
        if(key3_press_flag == 1) key3_press_cnt++;
            if(key3_press_cnt >= KEYS_LONG_PRESS){//2sec
              if(key3_lock != 1) key3_long_press_enable = 1;
              key3_lock = 1;//lock to prevent multiple activate
            }
        
        key3_cnt = 0;
        key3_prestate = key3_state;      
      }
  
    }//logo_delay
    
    led_toggle++;
    if(led_toggle == 9500){
      //HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);    
      HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);
      
    }
    if(led_toggle >= 10000){
      //HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);
      HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);
      led_toggle = 0;
    }
      

    if((buzzer_button != 0)&&(buzzer_alarm == 0)){
    
      buzzer_button_cnt++;
      if(buzzer_button_cnt == 100)HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_13);
      if(buzzer_button_cnt >= 200){
        buzzer_button_cnt = 0;
        HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_13);
        buzzer_button--;
      }

    }
    else if(buzzer_alarm != 0){
    
      buzzer_button_cnt++;
      if(buzzer_button_cnt == 500)HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_13);
      if(buzzer_button_cnt >= 2000){
        buzzer_button_cnt = 0;
        HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_13);
      }

    }
    else{
      buzzer_button_cnt = 0;
      HAL_GPIO_WritePin(GPIOB, GPIO_PIN_13, GPIO_PIN_RESET);
      
    }
    LL_TIM_ClearFlag_UPDATE(TIM7);
    
  }
  
  /* USER CODE END TIM7_IRQn 0 */
  /* USER CODE BEGIN TIM7_IRQn 1 */

  /* USER CODE END TIM7_IRQn 1 */
}

/**
  * @brief This function handles USB OTG FS global interrupt.
  */
void OTG_FS_IRQHandler(void)
{
  /* USER CODE BEGIN OTG_FS_IRQn 0 */

  /* USER CODE END OTG_FS_IRQn 0 */
  HAL_PCD_IRQHandler(&hpcd_USB_OTG_FS);
  /* USER CODE BEGIN OTG_FS_IRQn 1 */

  /* USER CODE END OTG_FS_IRQn 1 */
}

/* USER CODE BEGIN 1 */

/* USER CODE END 1 */
/************************ (C) COPYRIGHT STMicroelectronics *****END OF FILE****/
