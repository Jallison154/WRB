/*
 * Seeed XIAO ESP32C3/ESP32S3 Audio Trigger Controller V2
 * Supports both Pi communication and direct XIAO-to-XIAO communication
 * 
 * Hardware:
 * - Button 1: GPIO D0
 * - Button 2: GPIO D1
 * - Built-in LED: GPIO D2 (status indicator)
 * 
 * Communication:
 * - HTTP POST to Pi for audio playback
 * - Direct HTTP communication with other XIAO
 * - WiFi connection to same network
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <WebServer.h>

// Configuration - UPDATE THESE VALUES
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* pi_server = "http://192.168.1.100:8080";  // Pi's IP address

// XIAO Controller ID (1 or 2)
const int XIAO_ID = 1;  // Change this to 2 for the second XIAO

// Other XIAO IP addresses
const char* xiao1_ip = "192.168.1.101";
const char* xiao2_ip = "192.168.1.102";
const int xiao_communication_port = 8081;

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

// Web server for XIAO-to-XIAO communication
WebServer server(xiao_communication_port);

// Communication mode
enum CommMode {
  COMM_PI_ONLY,      // Only send to Pi
  COMM_XIAO_ONLY,    // Only send to other XIAO
  COMM_BOTH          // Send to both Pi and other XIAO
};

CommMode communication_mode = COMM_BOTH;  // Default: send to both

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("XIAO Audio Trigger Controller V2 Starting...");
  Serial.println("XIAO ID: " + String(XIAO_ID));
  
  // Initialize pins
  pinMode(BUTTON1_PIN, INPUT_PULLUP);
  pinMode(BUTTON2_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  
  // Initial LED state
  digitalWrite(LED_PIN, LOW);
  
  // Connect to WiFi
  connectToWiFi();
  
  // Setup web server for XIAO-to-XIAO communication
  setupWebServer();
  
  Serial.println("Setup complete!");
  Serial.println("Communication mode: " + String(communication_mode));
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
  
  // Handle web server requests
  server.handleClient();
  
  // Read button states
  int button1_state = digitalRead(BUTTON1_PIN);
  int button2_state = digitalRead(BUTTON2_PIN);
  
  // Handle Button 1
  if (button1_state != last_button1_state) {
    if (millis() - last_debounce_time1 > debounce_delay) {
      if (button1_state == LOW && !button1_pressed) {
        button1_pressed = true;
        handleButtonPress(1);
        Serial.println("Button 1 pressed");
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
        handleButtonPress(2);
        Serial.println("Button 2 pressed");
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
    Serial.print("XIAO communication port: ");
    Serial.println(xiao_communication_port);
  } else {
    wifi_connected = false;
    Serial.println();
    Serial.println("WiFi connection failed!");
  }
}

void setupWebServer() {
  // Endpoint for receiving button triggers from other XIAO
  server.on("/xiao_trigger", HTTP_POST, handleXiaoTrigger);
  
  // Endpoint for status
  server.on("/status", HTTP_GET, handleStatus);
  
  // Endpoint for changing communication mode
  server.on("/set_mode", HTTP_POST, handleSetMode);
  
  server.begin();
  Serial.println("XIAO-to-XIAO web server started on port " + String(xiao_communication_port));
}

void handleXiaoTrigger() {
  if (server.hasArg("plain")) {
    String body = server.arg("plain");
    
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, body);
    
    if (!error) {
      int xiao_id = doc["xiao_id"];
      int button_id = doc["button_id"];
      
      Serial.println("Received trigger from XIAO" + String(xiao_id) + " Button" + String(button_id));
      
      // Forward to Pi for audio playback
      if (communication_mode == COMM_XIAO_ONLY || communication_mode == COMM_BOTH) {
        triggerAudioOnPi(xiao_id, button_id);
      }
      
      server.send(200, "application/json", "{\"status\":\"success\"}");
    } else {
      server.send(400, "application/json", "{\"error\":\"Invalid JSON\"}");
    }
  } else {
    server.send(400, "application/json", "{\"error\":\"No data\"}");
  }
}

void handleStatus() {
  StaticJsonDocument<200> doc;
  doc["xiao_id"] = XIAO_ID;
  doc["wifi_connected"] = wifi_connected;
  doc["ip_address"] = WiFi.localIP().toString();
  doc["communication_mode"] = communication_mode;
  doc["button1_state"] = digitalRead(BUTTON1_PIN);
  doc["button2_state"] = digitalRead(BUTTON2_PIN);
  
  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

void handleSetMode() {
  if (server.hasArg("plain")) {
    String body = server.arg("plain");
    
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, body);
    
    if (!error) {
      int mode = doc["mode"];
      if (mode >= 0 && mode <= 2) {
        communication_mode = (CommMode)mode;
        Serial.println("Communication mode changed to: " + String(mode));
        server.send(200, "application/json", "{\"status\":\"success\",\"mode\":" + String(mode) + "}");
      } else {
        server.send(400, "application/json", "{\"error\":\"Invalid mode\"}");
      }
    } else {
      server.send(400, "application/json", "{\"error\":\"Invalid JSON\"}");
    }
  } else {
    server.send(400, "application/json", "{\"error\":\"No data\"}");
  }
}

void handleButtonPress(int button_id) {
  Serial.println("Handling button " + String(button_id) + " press");
  
  // Send to Pi if enabled
  if (communication_mode == COMM_PI_ONLY || communication_mode == COMM_BOTH) {
    triggerAudioOnPi(XIAO_ID, button_id);
  }
  
  // Send to other XIAO if enabled
  if (communication_mode == COMM_XIAO_ONLY || communication_mode == COMM_BOTH) {
    sendToOtherXiao(XIAO_ID, button_id);
  }
}

void triggerAudioOnPi(int xiao_id, int button_id) {
  if (!wifi_connected) {
    Serial.println("Cannot trigger audio on Pi - WiFi not connected");
    return;
  }
  
  HTTPClient http;
  String url = String(pi_server) + "/trigger_audio";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  
  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["xiao_id"] = xiao_id;
  doc["button_id"] = button_id;
  
  String json_string;
  serializeJson(doc, json_string);
  
  Serial.println("Sending to Pi: " + url);
  Serial.println("Payload: " + json_string);
  
  int httpResponseCode = http.POST(json_string);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("Pi Response Code: " + String(httpResponseCode));
    Serial.println("Pi Response: " + response);
  } else {
    Serial.println("Pi request failed: " + String(httpResponseCode));
  }
  
  http.end();
}

void sendToOtherXiao(int xiao_id, int button_id) {
  if (!wifi_connected) {
    Serial.println("Cannot send to other XIAO - WiFi not connected");
    return;
  }
  
  // Determine target XIAO IP
  String target_ip;
  if (XIAO_ID == 1) {
    target_ip = xiao2_ip;
  } else {
    target_ip = xiao1_ip;
  }
  
  HTTPClient http;
  String url = "http://" + target_ip + ":" + String(xiao_communication_port) + "/xiao_trigger";
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");
  
  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["xiao_id"] = xiao_id;
  doc["button_id"] = button_id;
  
  String json_string;
  serializeJson(doc, json_string);
  
  Serial.println("Sending to other XIAO: " + url);
  Serial.println("Payload: " + json_string);
  
  int httpResponseCode = http.POST(json_string);
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("XIAO Response Code: " + String(httpResponseCode));
    Serial.println("XIAO Response: " + response);
  } else {
    Serial.println("XIAO request failed: " + String(httpResponseCode));
  }
  
  http.end();
}

// Utility function to change communication mode
void setCommunicationMode(CommMode mode) {
  communication_mode = mode;
  Serial.println("Communication mode set to: " + String(mode));
}

// Utility function to get other XIAO status
void checkOtherXiaoStatus() {
  if (!wifi_connected) return;
  
  String target_ip;
  if (XIAO_ID == 1) {
    target_ip = xiao2_ip;
  } else {
    target_ip = xiao1_ip;
  }
  
  HTTPClient http;
  String url = "http://" + target_ip + ":" + String(xiao_communication_port) + "/status";
  
  http.begin(url);
  int httpResponseCode = http.GET();
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("Other XIAO status: " + response);
  } else {
    Serial.println("Failed to get other XIAO status: " + String(httpResponseCode));
  }
  
  http.end();
}
