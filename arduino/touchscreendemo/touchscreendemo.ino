// pokemon-master

#include <stdint.h>
#include "TouchScreen.h"

#define YP A2  // must be an analog pin
#define XM A3  // must be an analog pin
#define YM A0  // can be a digital pin
#define XP A1  // can be a digital pin

#define BEAM 7 // digital I/O pin for sensing hand waving

/*
 * For better pressure precision, we need to know the resistance
 * between X+ and X- Use any multimeter to read it
 * For the one we're using, its 300 ohms across the X plate
 */
TouchScreen ts = TouchScreen(XP, YP, XM, YM, 300);

// debounce counter for beam
uint8_t beamDebounceCounter = 0;


void setup(void)
{
    Serial.begin(9600);
    pinMode(BEAM, INPUT_PULLUP);
}


void loop(void)
{
    // BEAM goes low if IR beam is broken
    if (digitalRead(BEAM) == LOW)
    {
        if (beamDebounceCounter == 0)
        {
            Serial.println("!");
            beamDebounceCounter = 2; // 200ms debounce timer
        }
        else
        {
            beamDebounceCounter = 0;
        }
    }

    // a point object holds x y and z coordinates.
    TSPoint p = ts.getPoint();

    // we have some minimum pressure we consider 'valid'
    // pressure of 0 means no pressing!
    if (p.z > ts.pressureThreshhold)
    {
        // Send a JSON string with touch information.
        Serial.print("{\"X\": ");
        Serial.print(p.x);

        Serial.print(", \"Y\": ");
        Serial.print(p.y);

        Serial.print(", \"P\": ");
        Serial.print(p.z);

        Serial.println("}");
    }

    delay(100);
}
