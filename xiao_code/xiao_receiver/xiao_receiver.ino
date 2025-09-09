#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>
#include <esp_sleep.h>
#include "driver/gpio.h"

// ---------- Pins (use Dx aliases) ----------
#define LED_PIN  D10               // status LED on header D10
const bool LED_ACTIVE_LOW = false; // set true if LED looks inverted

// ---------- Allowed Transmitter MACs (only these will be accepted) ----------
uint8_t ALLOWED_TX_MACS[][6] = {
  { 0x58,0x8C,0x81,0x9F,0x22,0xAC }, // <-- your TX1 MAC (58:8c:81:9f:22:ac)
  // Add more allowed transmitters as needed
};
const uint8_t NUM_ALLOWED_TXS = sizeof(ALLOWED_TX_MACS) / 6;

// ---------- Messages ----------
enum : uint8_t { MSG_PING=0xA0, MSG_ACK=0xA1, MSG_BTN=0xB0, MSG_BTN_HOLD=0xB1 };

// ---------- Link tracking ----------
struct TxLink {
  uint8_t mac[6];
  uint32_t lastPingMs;
  bool linked;
  uint8_t lastBtn1State;
  uint8_t lastBtn2State;
};
TxLink txLinks[10]; // Support up to 10 transmitters
uint8_t numTxLinks = 0;

// ---------- Button state tracking ----------
uint32_t lastBtnActivityMs = 0;

// ---------- MAC validation helper ----------
bool isAllowedTransmitter(const uint8_t* mac) {
  for (uint8_t i = 0; i < NUM_ALLOWED_TXS; i++) {
    if (memcmp(ALLOWED_TX_MACS[i], mac, 6) == 0) {
      return true;
    }
  }
  return false;
}

// ---------- LED helpers ----------
inline void ledWriteRaw(uint8_t v){ if(LED_ACTIVE_LOW) v = 255 - v; analogWrite(LED_PIN, v); }
inline void ledOn(){     ledWriteRaw(255); } // 100% when button received
inline void ledLinked(){ ledWriteRaw(64);  } // ~25% when linked
inline void ledOff(){    ledWriteRaw(0);   } // off

void showNoLinkDoubleBlink(uint32_t now){
  uint32_t t = now % 2000;
  if (t < 120) { ledOn();  return; }
  if (t < 240) { ledOff(); return; }
  if (t < 360) { ledOn();  return; }
  ledOff();
}

void ledTask(){
  uint32_t now = millis();
  bool anyLinked = false;
  bool recentActivity = (now - lastBtnActivityMs) < 1000; // 1 second after button press
  
  // Check if any transmitters are linked
  for (uint8_t i = 0; i < numTxLinks; i++) {
    if (txLinks[i].linked) {
      anyLinked = true;
      break;
    }
  }
  
  if (recentActivity) {
    ledOn();               // 100% when button activity received
  } else if (anyLinked) {
    ledLinked();           // 25% when linked
  } else {
    showNoLinkDoubleBlink(now);  // Double blink when no links (same as transmitter)
  }
}

// ---------- ESP-NOW helper functions ----------
void addPeer(const uint8_t mac[6], uint8_t channel=1){
  esp_now_peer_info_t p{};
  memcpy(p.peer_addr, mac, 6);
  p.channel = channel; 
  p.encrypt = false; 
  p.ifidx = WIFI_IF_STA;
  esp_now_del_peer(mac);
  esp_now_add_peer(&p);
}

void sendAck(const uint8_t* mac) {
  uint8_t ack = MSG_ACK;
  esp_err_t result = esp_now_send(mac, &ack, 1);
  if (result != ESP_OK) {
    Serial.printf("Failed to send ACK to %02X:%02X:%02X:%02X:%02X:%02X\n",
                 mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  }
}

// ---------- ESP-NOW handlers ----------
void onRecv(const esp_now_recv_info_t* info, const uint8_t* data, int len){
  if (!data || len <= 0) return;
  
  // Only accept messages from allowed transmitters
  if (!isAllowedTransmitter(info->src_addr)) {
    Serial.printf("Rejected message from unauthorized MAC: %02X:%02X:%02X:%02X:%02X:%02X\n",
                 info->src_addr[0], info->src_addr[1], info->src_addr[2],
                 info->src_addr[3], info->src_addr[4], info->src_addr[5]);
    return;
  }
  
  // Find or create transmitter link
  uint8_t txIndex = 255;
  for (uint8_t i = 0; i < numTxLinks; i++) {
    if (memcmp(txLinks[i].mac, info->src_addr, 6) == 0) {
      txIndex = i;
      break;
    }
  }
  
  if (txIndex == 255 && numTxLinks < 10) {
    txIndex = numTxLinks++;
    memcpy(txLinks[txIndex].mac, info->src_addr, 6);
    txLinks[txIndex].linked = false;
    txLinks[txIndex].lastPingMs = 0;
    txLinks[txIndex].lastBtn1State = 0;
    txLinks[txIndex].lastBtn2State = 0;
    
    // Add this transmitter as a peer automatically
    addPeer(info->src_addr, 1);
    Serial.printf("Authorized transmitter connected: %02X:%02X:%02X:%02X:%02X:%02X\n",
                 info->src_addr[0], info->src_addr[1], info->src_addr[2],
                 info->src_addr[3], info->src_addr[4], info->src_addr[5]);
  }
  
  if (txIndex == 255) return; // Too many transmitters
  
  uint32_t now = millis();
  
  switch (data[0]) {
    case MSG_PING:
      // Send ACK back
      sendAck(info->src_addr);
      txLinks[txIndex].lastPingMs = now;
      txLinks[txIndex].linked = true;
      break;
      
    case MSG_BTN:
      if (len >= 2) {
        uint8_t btnId = data[1];
        Serial.printf("RX: BTN%u from %02X:%02X:%02X:%02X:%02X:%02X\n", 
                     btnId, info->src_addr[0], info->src_addr[1], info->src_addr[2],
                     info->src_addr[3], info->src_addr[4], info->src_addr[5]);
        
        // Update button states for this transmitter
        if (btnId == 1) {
          txLinks[txIndex].lastBtn1State = 1;
        } else if (btnId == 2) {
          txLinks[txIndex].lastBtn2State = 1;
        }
        lastBtnActivityMs = now;
        
        // Send ACK back
        sendAck(info->src_addr);
      }
      break;
      
    case MSG_BTN_HOLD:
      if (len >= 2) {
        uint8_t btnId = data[1];
        Serial.printf("RX: BTN%u HOLD from %02X:%02X:%02X:%02X:%02X:%02X\n", 
                     btnId, info->src_addr[0], info->src_addr[1], info->src_addr[2],
                     info->src_addr[3], info->src_addr[4], info->src_addr[5]);
        
        lastBtnActivityMs = now;
        
        // Send ACK back
        sendAck(info->src_addr);
      }
      break;
  }
}

// ---------- Setup ----------
void setup(){
  Serial.begin(115200);
  delay(150);

  Serial.printf("Receiver starting...\n");
  Serial.printf("LED Pin: D10=%d\n", D10);
  Serial.printf("Allowed transmitters: %d\n", NUM_ALLOWED_TXS);
  for (uint8_t i = 0; i < NUM_ALLOWED_TXS; i++) {
    Serial.printf("  TX%d: %02X:%02X:%02X:%02X:%02X:%02X\n", i+1,
                 ALLOWED_TX_MACS[i][0], ALLOWED_TX_MACS[i][1], ALLOWED_TX_MACS[i][2],
                 ALLOWED_TX_MACS[i][3], ALLOWED_TX_MACS[i][4], ALLOWED_TX_MACS[i][5]);
  }

  // LED PWM
  pinMode(LED_PIN, OUTPUT);
  analogWriteResolution(LED_PIN, 8);     // 0..255
  analogWriteFrequency(LED_PIN, 2000);   // Hz
  ledOff();

  // WiFi/ESP-NOW init
  WiFi.mode(WIFI_STA);
  esp_wifi_set_promiscuous(true);
  esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);
  esp_wifi_set_promiscuous(false);

  if (esp_now_init() != ESP_OK){
    Serial.println("ESP-NOW init failed");
    while(true){ ledOn(); delay(120); ledOff(); delay(600); }
  }
  esp_now_register_recv_cb(onRecv);
  
  Serial.println("Receiver ready! Only accepting authorized transmitters.");
}

// ---------- Loop ----------
void loop(){
  uint32_t now = millis();
  
  // Update link status (4 second timeout)
  for (uint8_t i = 0; i < numTxLinks; i++) {
    txLinks[i].linked = (now - txLinks[i].lastPingMs) < 4000;
  }
  
  // Update LED
  ledTask();
  
  // Print status every 10 seconds
  static uint32_t lastStatusMs = 0;
  if (now - lastStatusMs >= 10000) {
    lastStatusMs = now;
    uint8_t linkedCount = 0;
    for(uint8_t i = 0; i < numTxLinks; i++) {
      if(txLinks[i].linked) linkedCount++;
    }
    Serial.printf("Status: %d transmitters, %d linked\n", numTxLinks, linkedCount);
  }
  
  delay(10);
}
