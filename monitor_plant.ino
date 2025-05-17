#include <WiFi.h>
#include <ESPSupabase.h>
#include <HTTPClient.h>

#define SOIL_MOISTURE_PIN 34   // Analog pin for soil moisture sensor
#define THRESHOLD_MOISTURE 100 // Adjust based on your soil
#define PUMP_PIN 2             // Digital pin for pump

const char *ssid = "";
const char *password = "";

const char *supabaseUrl = "";
const char *supabaseKey = "";

const char *supabase_table_insert_endpoint = "";

Supabase supabase;
HTTPClient http;

bool is_pump_on = false;

void sendSoilMoisture()
{
    int soil_moisture = analogRead(SOIL_MOISTURE_PIN);
    int soil_moisture_percentage = map(soil_moisture, 1000, 4095, 100, 0);

    Serial.println("Soil Moisture (Raw): " + String(soil_moisture));
    Serial.println("Soil Moisture (%): " + String(soil_moisture_percentage));

    String jsonPayload = "{\"plant_name\":\"tomato\",\"soil_moisture\":" + String(soil_moisture) + "}";

    http.begin(String(supabaseUrl) + supabase_table_insert_endpoint);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("apikey", supabaseKey);
    http.addHeader("Authorization", "Bearer " + String(supabaseKey));
    http.addHeader("Prefer", "return=minimal");

    Serial.println("Sending JSON Payload: " + jsonPayload);
    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0)
    {
        Serial.printf("Data sent! Status: %d\n", httpResponseCode);
    }
    else
    {
        Serial.printf("Failed to send data: %s\n", http.errorToString(httpResponseCode).c_str());
    }

    String response = http.getString();
    Serial.println("Response: " + response);

    http.end();

    // Control pump
    if (is_pump_on || soil_moisture_percentage < THRESHOLD_MOISTURE)
    {
        digitalWrite(PUMP_PIN, HIGH);
        if (!is_pump_on)
        {
            Serial.println("Soil dry → Pump ON.");
        }
    }
    else
    {
        if (!is_pump_on)
        {
            digitalWrite(PUMP_PIN, LOW);
            Serial.println("Soil wet enough → Pump OFF.");
        }
    }

    Serial.println();
}

void setup()
{
    Serial.begin(9600);
    Serial.println("Smart Plant Monitor (Soil Moisture Only)");

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(1000);
        Serial.println("Connecting to Wi-Fi...");
    }

    Serial.println("Wi-Fi connected.");
    supabase.begin(supabaseUrl, supabaseKey);
    Serial.println("Connected to Supabase.");

    pinMode(PUMP_PIN, OUTPUT);
}

void loop()
{
    sendSoilMoisture();
    delay(4000);
}