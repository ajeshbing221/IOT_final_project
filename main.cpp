#include "LoRaWan_APP.h"
#include <Arduino.h>
#include "driver/temp_sensor.h"

// LoRaWAN Configuration
uint8_t devEui[] = {0x70, 0xB3, 0xD5, 0x7E, 0xD0, 0x06, 0xC2, 0x25};
bool overTheAirActivation = true;
uint8_t appEui[] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x07}; // you should set whatever your TTN generates. TTN calls this the joinEUI, they are the same thing. 

uint8_t appKey[] = {0x2A, 0x57, 0xBD, 0xA9, 0x3B, 0x50, 0xA2, 0x45, 0x3E, 0xFD, 0x8E, 0x9E, 0xBA, 0x17, 0x69, 0x4D};// you should set whatever your TTN generates 

//These are only used for ABP, for OTAA, these values are generated on the Nwk Server, you should not have to change these values
uint8_t nwkSKey[] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
uint8_t appSKey[] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
uint32_t devAddr =  (uint32_t)0x00000000;

/*LoraWan channelsmask*/
uint16_t userChannelsMask[6]={ 0xFF00,0x0000,0x0000,0x0000,0x0000,0x0000 };

/*LoraWan region, select in arduino IDE tools*/
LoRaMacRegion_t loraWanRegion = ACTIVE_REGION; // we define this as a user flag in the .ini file. 

/*LoraWan Class, Class A and Class C are supported*/
DeviceClass_t loraWanClass = CLASS_A;

/*the application data transmission duty cycle.  value in [ms].*/
uint32_t appTxDutyCycle = 15000; 

/*ADR enable*/
bool loraWanAdr = true;

// uint32_t license[4] = {};
/* Indicates if the node is sending confirmed or unconfirmed messages */
bool isTxConfirmed = true;

/* Application port */
uint8_t appPort = 1;
/*!
* Number of trials to transmit the frame, if the LoRaMAC layer did not
* receive an acknowledgment. The MAC performs a datarate adaptation,
* according to the LoRaWAN Specification V1.0.2, chapter 18.4, according
* to the following table:
*
* Transmission nb | Data Rate
* ----------------|-----------
* 1 (first)       | DR
* 2               | DR
* 3               | max(DR-1,0)
* 4               | max(DR-1,0)
* 5               | max(DR-2,0)
* 6               | max(DR-2,0)
* 7               | max(DR-3,0)
* 8               | max(DR-3,0)
*
* Note, that if NbTrials is set to 1 or 2, the MAC will not decrease
* the datarate, in case the LoRaMAC layer did not receive an acknowledgment
*/
uint8_t confirmedNbTrials = 8;

static const char *LOG_TAG = "TEMP_SENSOR";

void initTempSensor() 
{
    temp_sensor_config_t temp_sensor = TSENS_CONFIG_DEFAULT();
    temp_sensor.dac_offset = TSENS_DAC_L2;
    temp_sensor_set_config(temp_sensor);
    temp_sensor_start();
}

float readTemperature()
 {
    float temperature = 0;
    temp_sensor_read_celsius(&temperature);
    return temperature;
}

/* Prepares the payload of the frame */
static void prepareTxFrame(uint8_t port) 
{
	/*appData size is LORAWAN_APP_DATA_MAX_SIZE which is defined in "commissioning.h".
	*appDataSize max value is LORAWAN_APP_DATA_MAX_SIZE.
	*if enabled AT, don't modify LORAWAN_APP_DATA_MAX_SIZE, it may cause system hanging or failure.
	*if disabled AT, LORAWAN_APP_DATA_MAX_SIZE can be modified, the max value is reference to lorawan region and SF.
	*for example, if use REGION_CN470, 
	*the max value for different DR can be found in MaxPayloadOfDatarateCN470 refer to DataratesCN470 and BandwidthsCN470 in "RegionCN470.h".
	*/
    // This data can be changed, just make sure to change the datasize as well. 
    float temp = readTemperature();
    int16_t tempFixed = static_cast<int16_t>(temp * 100);
    appDataSize = 3;
    appData[0] = 0x07;
    appData[1] = (tempFixed >> 8) & 0xFF;  
    appData[2] = tempFixed & 0xFF;       
}

RTC_DATA_ATTR bool firstrun = true;

void setup() {
    Serial.begin(115200);
    Mcu.begin();
    initTempSensor(); //initializing sensor
    if(firstrun) {
        LoRaWAN.displayMcuInit();
        firstrun = false;
    }
    
    deviceState = DEVICE_STATE_INIT;
}

void loop() {
    switch(deviceState) {
        case DEVICE_STATE_INIT:
        {
#if(LORAWAN_DEVEUI_AUTO)
            LoRaWAN.generateDeveuiByChipID();
#endif
            LoRaWAN.init(loraWanClass, loraWanRegion);
            break;
        }
        case DEVICE_STATE_JOIN:
        {
            LoRaWAN.displayJoining();
            LoRaWAN.join();
            if (deviceState == DEVICE_STATE_SEND) {
                LoRaWAN.displayJoined();
            }
            break;
        }
        case DEVICE_STATE_SEND:
        {
            LoRaWAN.displaySending();
            prepareTxFrame(appPort);
            LoRaWAN.send();
            deviceState = DEVICE_STATE_CYCLE;
            break;
        }
        case DEVICE_STATE_CYCLE:
        {
            // Schedule next packet transmission
            txDutyCycleTime = appTxDutyCycle + randr(0, APP_TX_DUTYCYCLE_RND);
            LoRaWAN.cycle(txDutyCycleTime);
            deviceState = DEVICE_STATE_SLEEP;
            break;
        }
        case DEVICE_STATE_SLEEP:
        {
            LoRaWAN.displayAck();
            LoRaWAN.sleep(loraWanClass);
            break;
        }
        default:
        {
            deviceState = DEVICE_STATE_INIT;
            break;
        }
    }
}