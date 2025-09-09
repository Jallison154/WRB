/*
 * Seeed XIAO ESP32C3/ESP32S3 Audio Trigger Controller
 * Sends button press events to Raspberry Pi audio server
 * 
 * Hardware:
 * - Button 1: GPIO D0
 * - Button 2: GPIO D1
 * - Built-in LED: GPIO D2 (status indicator)
 * 
 * Network:
 * - WiFi connection to same network as Raspberry Pi
 * - HTTP POST requests to Pi audio server
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// Configuration - UPDATE THESE VALUES
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* pi_server = "http://192.168.1.100:8080";  // Pi's IP address

// XIAO Controller ID (1 or 2)
const int XIAO_ID = 1;  // Change this to 2 for the second XIAO

// Pin definitions
const int BUTTON1_PIN = D0;
const int BUTTON2_PIN = D1;
const int LED_PIN = D2;

// Button state tracking
bool button1_pressed = false;
bool button2_pressed = false;
bool last_button1_state = HIGH;
bool last_button2_state = HIGH;

// Debouncing
unsigned long last_debounce_time1 = 0;
unsigned long last_debounce_time2 = 0;
const unsigned long debounce_delay = 50;

// Network status
bool wifi_connected = false;
unsigned long last_connection_check = 0;
const unsigned long connection_check_interval = 30000; // 30 seconds

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("XIAO Audio Trigger Controller Starting...");
  Serial.println("XIAO ID: " + String(XIAO_ID));
  
  // Initialize pins
  pinMode(BUTTON1_PIN, INPUT_PULLUP);
  pinMode(BUTTON2_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  
  // Initial LED state
  digitalWrite(LED_PIN, LOW);
  
  // Connect to WiFi
  connectToWiFi();
  
  Serial.println("Setup complete!");
}

void loop() {
  // Check WiFi connection periodically
  if (millis() - last_connection_check > connection_check_interval) {
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("WiFi disconnected, attempting to reconnect...");
      connectToWiFi();
    }
    last_connection_check = millis();
  }
  
  // Read button states
  int button1_state = digitalRead(BUTTON1_PIN);
  int button2_state = digitalRead(BUTTON2_PIN);
  
  // Handle Button 1
  if (button1_state != last_button1_state) {
    if (millis() - last_debounce_time1 > debounce_delay) {
      if (button1_state == LOW && !button1_pressed) {
        button1_pressed = true;
        triggerAudio(1);
        Serial.println("Button 1 pressed - triggering audio");
      } else if (button1_state == HIGH) {
        button1_pressed = false;
      }
      last_debounce_time1 = millis();
    }
    last_button1_state = button1_state;
  }
  
  // Handle Button 2
  if (button2_state != last_button2_state) {
    if (millis() - last_debounce_time2 > debounce_delay) {
      if (button2_state == LOW && !button2_pressed) {
        button2_pressed = true;
        triggerAudio(2);
        Serial.println("Button 2 pressed - triggering audio");
      } else if (button2_state == HIGH) {
        button2_pressed = false;
      }
      last_debounce_time2 = millis();
    }
    last_button2_state = button2_state;
  }
  
  // LED status indicator
  if (wifi_connected) {
    digitalWrite(LED_PIN, HIGH);
  } else {
    // Blink LED when disconnected
    static unsigned long last_blink = 0;
    if (millis() - last_blink > 500) {
      digitalWrite(LED_PIN, !digitalRead(LED_PIN));
      last_blink = millis();
    }
  }
  
  delay(10); // Small delay for stability
}

void connectToWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    wifi_connected = true;
    Serial.println();
    Serial.println("WiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Pi server: ");
    Serial.println(pi_server);
  } else {
    wifi_connected = false;
    Serial.println();
    Serial.println("WiFi connection failed!");
  }
}

void triggerAudio(int button_id) {
  if (!wifi_connected) {
    Serial.println("Cannot trigger audio - WiFi not connected");
    return;
  }
  
  HTTPClient http;
  String url = String(pi_server) + "/trigger_audio";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  
  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["xiao_id"] = XIAO_ID;
  doc["button_id"] = button_id;
  
  String json_string;
  serializeJson(doc, json_string);
  
  Serial.println("Sending request to: " + url);
  Serial.println("Payload: " + json_string);
  
  int httpResponseCode = http.POST(json_string);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("HTTP Response Code: " + String(httpResponseCode));
    Serial.println("Response: " + response);
    
    if (httpResponseCode == 200) {
      Serial.println("Audio trigger successful!");
    } else {
      Serial.println("Audio trigger failed!");
    }
  } else {
    Serial.println("HTTP request failed!");
    Serial.println("Error: " + String(httpResponseCode));
  }
  
  http.end();
}

// Optional: Add status endpoint for debugging
void handleStatusRequest() {
  Serial.println("=== XIAO Status ===");
  Serial.println("XIAO ID: " + String(XIAO_ID));
  Serial.println("WiFi Status: " + String(wifi_connected ? "Connected" : "Disconnected"));
  Serial.println("IP Address: " + WiFi.localIP().toString());
  Serial.println("Button 1 State: " + String(digitalRead(BUTTON1_PIN) ? "HIGH" : "LOW"));
  Serial.println("Button 2 State: " + String(digitalRead(BUTTON2_PIN) ? "HIGH" : "LOW"));
  Serial.println("==================");
}
