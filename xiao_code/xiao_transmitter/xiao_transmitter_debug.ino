#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>
#include <esp_sleep.h>
#include "driver/gpio.h"   // <-- needed for gpio_wakeup_enable()

// ---------- Pins (use Dx aliases) ----------
#define LED_PIN  D10               // status LED on header D10
const bool LED_ACTIVE_LOW = false; // set true if LED looks inverted

#define BTN1_PIN D1                // button 1 on header D1 -> GND
#define BTN2_PIN D2                // button 2 on header D2 -> GND
const bool USE_BTN2 = true;
const bool BTN_ACTIVE_LOW = true;  // true = button to GND with INPUT_PULLUP

// ---------- Peer (Receiver) MAC ----------
uint8_t RX_MAC[] = { 0x58,0x8C,0x81,0x9E,0x30,0x10 }; // <-- your RX MAC (58:8c:81:9e:30:10)

// ---------- Messages ----------
enum : uint8_t { MSG_PING=0xA0, MSG_ACK=0xA1, MSG_BTN=0xB0, MSG_BTN_HOLD=0xB1 };

// ---------- Link / timing ----------
uint32_t lastAckMs = 0;
bool linked = false;

// ---------- Power policy ----------
const bool     ENABLE_SLEEP     = false; // Disable sleep for debugging
const uint32_t IDLE_LIGHT_MS    = 5UL  * 60UL * 1000UL;  // 5 minutes
const uint32_t IDLE_DEEP_MS     = 15UL * 60UL * 1000UL;  // 15 minutes

// ---------- Button state ----------
uint8_t btn1State = HIGH;
uint8_t btn2State = HIGH;
uint32_t btn1PressMs = 0;
uint32_t btn2PressMs = 0;
bool btn1Held = false;
bool btn2Held = false;

// ---------- Hold detection ----------
const uint32_t HOLD_DELAY_MS = 500; // 500ms hold delay

// ---------- Light-sleep blinking parameters ----------
const uint32_t BLINK_PERIOD_MS = 5000;    // 5 second on/off cycle
const uint8_t  BLINK_BRIGHTNESS = 13;     // ~5% of 255 (13/255 ≈ 5%)

// ---------- LED control ----------
void ledOn()  { analogWrite(LED_PIN, LED_ACTIVE_LOW ? 0 : 255); }
void ledOff() { analogWrite(LED_PIN, LED_ACTIVE_LOW ? 255 : 0); }
void ledStandby() { analogWrite(LED_PIN, LED_ACTIVE_LOW ? 242 : BLINK_BRIGHTNESS); } // 5%

// ---------- ESP-NOW callbacks ----------
void onSend(const uint8_t* mac, esp_now_send_status_t status) {
  Serial.printf("Send status: %s\n", status == ESP_NOW_SEND_SUCCESS ? "SUCCESS" : "FAIL");
}

void onRecv(const uint8_t* mac, const uint8_t* data, int len) {
  Serial.printf("Received from %02X:%02X:%02X:%02X:%02X:%02X: ", 
                mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  for (int i = 0; i < len; i++) {
    Serial.printf("%02X ", data[i]);
  }
  Serial.println();
  
  if (len >= 1 && data[0] == MSG_ACK) {
    lastAckMs = millis();
    linked = true;
    Serial.println("Received ACK - Link established!");
  }
}

// ---------- Button handling ----------
void handleButton(uint8_t pin, uint8_t& state, uint32_t& pressMs, bool& held, uint8_t buttonId) {
  uint8_t newState = digitalRead(pin);
  
  if (newState != state) {
    state = newState;
    
    if (state == LOW) { // Button pressed
      pressMs = millis();
      held = false;
      Serial.printf("Button %d PRESSED\n", buttonId);
      
      // Send button press immediately
      uint8_t msg[] = {MSG_BTN, buttonId};
      esp_now_send(RX_MAC, msg, 2);
      Serial.printf("Sent BTN message for button %d\n", buttonId);
      
    } else { // Button released
      uint32_t holdTime = millis() - pressMs;
      Serial.printf("Button %d RELEASED after %dms\n", buttonId, holdTime);
      
      if (held) {
        // Send hold release (optional)
        Serial.printf("Button %d hold completed\n", buttonId);
      }
    }
  }
  
  // Check for hold
  if (state == LOW && !held && (millis() - pressMs) >= HOLD_DELAY_MS) {
    held = true;
    Serial.printf("Button %d HELD (500ms+)\n", buttonId);
    
    // Send hold message
    uint8_t msg[] = {MSG_BTN_HOLD, buttonId};
    esp_now_send(RX_MAC, msg, 2);
    Serial.printf("Sent BTN_HOLD message for button %d\n", buttonId);
  }
}

// ---------- Power management ----------
void enterLightSleep() {
  Serial.println("Entering light sleep...");
  ledOff();
  
  // Configure wake-up sources
  gpio_wakeup_enable((gpio_num_t)BTN1_PIN, GPIO_INTR_LOW_LEVEL);
  if (USE_BTN2) {
    gpio_wakeup_enable((gpio_num_t)BTN2_PIN, GPIO_INTR_LOW_LEVEL);
  }
  
  esp_sleep_enable_gpio_wakeup();
  esp_light_sleep_start();
  
  Serial.println("Woke from light sleep");
  ledOn();
  delay(100);
  ledOff();
}

void enterDeepSleep() {
  Serial.println("Entering deep sleep...");
  ledOff();
  
  // Configure wake-up sources
  gpio_wakeup_enable((gpio_num_t)BTN1_PIN, GPIO_INTR_LOW_LEVEL);
  if (USE_BTN2) {
    gpio_wakeup_enable((gpio_num_t)BTN2_PIN, GPIO_INTR_LOW_LEVEL);
  }
  
  esp_sleep_enable_gpio_wakeup();
  esp_deep_sleep_start();
}

// ---------- Setup ----------
void setup(){
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("=== WRB XIAO Transmitter Debug Version ===");
  
  // Print MAC address
  uint8_t mac[6];
  esp_wifi_get_mac(WIFI_IF_STA, mac);
  Serial.printf("Transmitter MAC: %02X:%02X:%02X:%02X:%02X:%02X\n", 
                mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  
  // Print target receiver MAC
  Serial.printf("Target Receiver MAC: %02X:%02X:%02X:%02X:%02X:%02X\n", 
                RX_MAC[0], RX_MAC[1], RX_MAC[2], RX_MAC[3], RX_MAC[4], RX_MAC[5]);
  
  // LED setup
  pinMode(LED_PIN, OUTPUT);
  analogWriteResolution(LED_PIN, 8);
  analogWriteFrequency(LED_PIN, 2000);
  ledOff();
  
  // Button setup
  pinMode(BTN1_PIN, INPUT_PULLUP);
  if (USE_BTN2) {
    pinMode(BTN2_PIN, INPUT_PULLUP);
  }
  
  // WiFi/ESP-NOW init
  WiFi.mode(WIFI_STA);
  esp_wifi_set_promiscuous(true);
  esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);
  esp_wifi_set_promiscuous(false);
  
  if (esp_now_init() != ESP_OK) {
    Serial.println("ESP-NOW init failed");
    while(true) { ledOn(); delay(120); ledOff(); delay(600); }
  }
  
  esp_now_register_send_cb(onSend);
  esp_now_register_recv_cb(onRecv);
  
  // Add receiver as peer
  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, RX_MAC, 6);
  peerInfo.channel = 1;
  peerInfo.ifidx = WIFI_IF_STA;
  peerInfo.encrypt = false;
  
  esp_err_t result = esp_now_add_peer(&peerInfo);
  if (result == ESP_OK) {
    Serial.println("Successfully added receiver peer");
  } else {
    Serial.printf("Failed to add peer: %d\n", result);
  }
  
  Serial.println("Transmitter ready! Press buttons to send messages.");
  Serial.println("Sending periodic PING messages to establish link...");
}

// ---------- Loop ----------
void loop(){
  uint32_t now = millis();
  
  // Handle buttons
  handleButton(BTN1_PIN, btn1State, btn1PressMs, btn1Held, 1);
  if (USE_BTN2) {
    handleButton(BTN2_PIN, btn2State, btn2PressMs, btn2Held, 2);
  }
  
  // Send periodic PING to maintain link
  static uint32_t lastPingMs = 0;
  if (now - lastPingMs >= 2000) { // Every 2 seconds
    lastPingMs = now;
    
    uint8_t ping[] = {MSG_PING};
    esp_now_send(RX_MAC, ping, 1);
    Serial.println("Sent PING");
    
    // Check link status
    if (now - lastAckMs > 5000) { // 5 second timeout
      linked = false;
      Serial.println("Link lost - no ACK received");
    }
  }
  
  // LED status
  if (btn1State == LOW || btn2State == LOW) {
    ledOn(); // 100% when button pressed
  } else if (linked) {
    ledStandby(); // 5% when linked
  } else {
    // Blink when not linked
    static uint32_t lastBlinkMs = 0;
    static bool blinkState = false;
    
    if (now - lastBlinkMs >= 500) {
      blinkState = !blinkState;
      if (blinkState) {
        ledOn();
      } else {
        ledOff();
      }
      lastBlinkMs = now;
    }
  }
  
  // Print status every 10 seconds
  static uint32_t lastStatusMs = 0;
  if (now - lastStatusMs >= 10000) {
    lastStatusMs = now;
    Serial.printf("Status: Linked=%s, LastACK=%dms ago\n", 
                  linked ? "YES" : "NO", now - lastAckMs);
  }
  
  delay(10);
}
