#include <esp_now.h>
#include <esp_wifi.h>
#include <esp_sleep.h>
#include "driver/gpio.h"

// ---------- Pins (use Dx aliases) ----------
#define LED_PIN  D10               // status LED on header D10
const bool LED_ACTIVE_LOW = false; // set true if LED looks inverted

// ---------- Pi Serial Communication ----------
// Direct serial connection to Pi (no WiFi needed)
// Pi will read from /dev/ttyUSB0 or similar

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

// ---------- Pi serial communication ----------
uint32_t piForwardCount = 0;
uint32_t piForwardFailures = 0;

// ---------- MAC validation helper ----------
bool isAllowedTransmitter(const uint8_t* mac) {
  for (uint8_t i = 0; i < NUM_ALLOWED_TXS; i++) {
    if (memcmp(ALLOWED_TX_MACS[i], mac, 6) == 0) {
      return true;
    }
  }
  return false;
}

// ---------- LED control ----------
void ledOn()  { analogWrite(LED_PIN, LED_ACTIVE_LOW ? 0 : 255); }
void ledOff() { analogWrite(LED_PIN, LED_ACTIVE_LOW ? 255 : 0); }
void ledLinked() { analogWrite(LED_PIN, LED_ACTIVE_LOW ? 200 : 64); } // 25%

void showNoLinkDoubleBlink(uint32_t now) {
  static uint32_t lastBlinkMs = 0;
  static bool blinkState = false;
  
  if (now - lastBlinkMs >= 200) { // 200ms blink
    blinkState = !blinkState;
    if (blinkState) {
      ledOn();
    } else {
      ledOff();
    }
    lastBlinkMs = now;
  }
}

// ---------- ESP-NOW helper functions ----------
void addPeer(const uint8_t mac[6], uint8_t channel=1){
  esp_now_peer_info_t p{};
  memcpy(p.peer_addr, mac, 6);
  p.channel = channel;
  p.ifidx = WIFI_IF_STA;
  p.encrypt = false;
  
  esp_err_t r = esp_now_add_peer(&p);
  if (r == ESP_OK) {
    Serial.printf("Added peer %02X:%02X:%02X:%02X:%02X:%02X on channel %d\n", 
                  mac[0], mac[1], mac[2], mac[3], mac[4], mac[5], channel);
  } else {
    Serial.printf("Failed to add peer: %d\n", r);
  }
}

// ---------- ESP-NOW callback ----------
void onRecv(const uint8_t* mac, const uint8_t* data, int len) {
  uint32_t now = millis();
  
  // Print received message for debugging
  Serial.printf("Received from %02X:%02X:%02X:%02X:%02X:%02X: ", 
                mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
  for (int i = 0; i < len; i++) {
    Serial.printf("%02X ", data[i]);
  }
  Serial.println();
  
  // Check if transmitter is allowed
  if (!isAllowedTransmitter(mac)) {
    Serial.println("Rejected: Unauthorized transmitter");
    return;
  }
  
  Serial.println("Accepted: Authorized transmitter");
  
  // Find or create link entry
  TxLink* link = nullptr;
  for (uint8_t i = 0; i < numTxLinks; i++) {
    if (memcmp(txLinks[i].mac, mac, 6) == 0) {
      link = &txLinks[i];
      break;
    }
  }
  
  if (!link) {
    if (numTxLinks < 10) {
      link = &txLinks[numTxLinks++];
      memcpy(link->mac, mac, 6);
      Serial.printf("Created new link for transmitter %d\n", numTxLinks);
    } else {
      Serial.println("Too many transmitters, ignoring");
      return;
    }
  }
  
  link->lastPingMs = now;
  link->linked = true;
  
  if (len >= 1) {
    uint8_t msgType = data[0];
    
    switch (msgType) {
      case MSG_PING:
        Serial.println("Received PING");
        // Send ACK back
        uint8_t ack[] = {MSG_ACK};
        esp_now_send(mac, ack, 1);
        break;
        
      case MSG_BTN:
        if (len >= 2) {
          uint8_t buttonId = data[1];
          Serial.printf("Received BTN: Button %d\n", buttonId);
          lastBtnActivityMs = now;
          forwardToPi(buttonId, false);
        }
        break;
        
      case MSG_BTN_HOLD:
        if (len >= 2) {
          uint8_t buttonId = data[1];
          Serial.printf("Received BTN_HOLD: Button %d\n", buttonId);
          lastBtnActivityMs = now;
          forwardToPi(buttonId, true);
        }
        break;
        
      default:
        Serial.printf("Unknown message type: 0x%02X\n", msgType);
        break;
    }
  }
}

// ---------- Pi serial communication functions ----------
void forwardToPi(uint8_t buttonId, bool isHold) {
  // Send simple command to Pi via serial
  // Format: "BTN<id>:<hold>\n"
  String command = "BTN" + String(buttonId) + ":" + (isHold ? "HOLD" : "PRESS") + "\n";
  
  Serial.print("Sending to Pi: " + command);
  Serial1.print(command);  // Send to Pi via Serial1 (hardware UART)
  
  piForwardCount++;
}

void printMacAddress() {
  uint8_t mac[6];
  esp_wifi_get_mac(WIFI_IF_STA, mac);
  Serial.printf("Receiver MAC: %02X:%02X:%02X:%02X:%02X:%02X\n", 
                mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

// ---------- Setup ----------
void setup(){
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("=== WRB XIAO Receiver Debug Version ===");
  printMacAddress();
  
  // LED setup
  pinMode(LED_PIN, OUTPUT);
  analogWriteResolution(LED_PIN, 8);     // 0..255
  analogWriteFrequency(LED_PIN, 2000);   // Hz
  ledOff();

  // Initialize Serial1 for Pi communication
  Serial1.begin(115200, SERIAL_8N1, D6, D7); // TX=D6, RX=D7
  
  // ESP-NOW init (WiFi not needed for serial communication)
  Serial.println("Initializing ESP-NOW...");
  esp_wifi_set_promiscuous(true);
  esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);
  esp_wifi_set_promiscuous(false);

  if (esp_now_init() != ESP_OK){
    Serial.println("ESP-NOW init failed");
    while(true){ ledOn(); delay(120); ledOff(); delay(600); }
  }
  esp_now_register_recv_cb(onRecv);
  
  Serial.println("Receiver ready! Only accepting authorized transmitters.");
  Serial.println("Serial communication to Pi enabled.");
  Serial.println("Waiting for transmitter messages...");
  
  // Print allowed transmitter MACs
  Serial.println("Allowed transmitters:");
  for (uint8_t i = 0; i < NUM_ALLOWED_TXS; i++) {
    Serial.printf("  %02X:%02X:%02X:%02X:%02X:%02X\n", 
                  ALLOWED_TX_MACS[i][0], ALLOWED_TX_MACS[i][1], ALLOWED_TX_MACS[i][2],
                  ALLOWED_TX_MACS[i][3], ALLOWED_TX_MACS[i][4], ALLOWED_TX_MACS[i][5]);
  }
}

// ---------- Loop ----------
void loop(){
  uint32_t now = millis();
  
  // Update link status (4 second timeout)
  for (uint8_t i = 0; i < numTxLinks; i++) {
    txLinks[i].linked = (now - txLinks[i].lastPingMs) < 4000;
  }
  
  // LED status
  bool recentActivity = (now - lastBtnActivityMs) < 1000;
  bool anyLinked = false;
  for (uint8_t i = 0; i < numTxLinks; i++) {
    if (txLinks[i].linked) {
      anyLinked = true;
      break;
    }
  }
  
  if (recentActivity) {
    ledOn();               // 100% when button activity received
  } else if (anyLinked) {
    ledLinked();           // 25% when linked (serial always connected)
  } else {
    showNoLinkDoubleBlink(now);  // Double blink when no links
  }
  
  // Print detailed status every 10 seconds
  static uint32_t lastStatusMs = 0;
  if (now - lastStatusMs >= 10000) {
    lastStatusMs = now;
    uint8_t linkedCount = 0;
    for(uint8_t i = 0; i < numTxLinks; i++) {
      if(txLinks[i].linked) linkedCount++;
    }
    Serial.printf("Status: %d transmitters, %d linked, Pi forwards: %d\n", 
                  numTxLinks, linkedCount, piForwardCount);
    
    // Print link details
    for (uint8_t i = 0; i < numTxLinks; i++) {
      Serial.printf("  Link %d: %02X:%02X:%02X:%02X:%02X:%02X - %s\n", 
                    i+1, txLinks[i].mac[0], txLinks[i].mac[1], txLinks[i].mac[2],
                    txLinks[i].mac[3], txLinks[i].mac[4], txLinks[i].mac[5],
                    txLinks[i].linked ? "LINKED" : "TIMEOUT");
    }
  }
  
  delay(10);
}
