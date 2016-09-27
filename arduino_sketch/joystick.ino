int FirstShotX, FirstShotY;
int last_x, last_y, x, y;
void setup() {
        for(int i=0; i<19; i++) {
                pinMode(i, INPUT);
                digitalWrite(i, 1);
        }
        Serial.begin(115200);
        FirstShotX = 0;
        FirstShotY = 0;
        last_x = 0;
        last_y = 0;
        x = 0;
        y = 0;
}
void loop(){
        int i, someInt, flag = 0; for(i=4; i<11; i++)
        {
                someInt = digitalRead(i); if(someInt == 0)
                {
                        flag =1;
                        break;
                }
        }
        if(flag == 1) {
                switch(i) {
                case 4: Serial.println("C"); break;
                case 5: Serial.println("D"); break;
                case 6: Serial.println("E"); break;
                case 7: Serial.println("F"); break;
                case 8: Serial.println("E"); break;
                case 2: Serial.println("P"); break;
                case 3: Serial.println("K"); break;
                default: break;
                }
                flag=0;
        }
        int sensorValue = analogRead(A0);
        if(FirstShotX == 0)
        {
                FirstShotX = sensorValue;
                Serial.print("FirstShotX=");
                Serial.println(FirstShotX);
        }

        x = sensorValue - FirstShotX;
        if (abs(x - last_x)>1){
//          if (x != last_x){
          Serial.print("X=");
          Serial.println(x);
          last_x = x;
        }

        sensorValue = analogRead(A1);
        if(FirstShotY == 0)
        {
                FirstShotY = sensorValue;
                Serial.print("FirstShotY=");
                Serial.println(FirstShotY);
        }

        y = sensorValue - FirstShotY;
        if (abs(y -last_y)>1){
//          if (y != last_y){
          Serial.print("y=");
          Serial.println(y);
          last_y = y;
        }
        delay(10);
}

