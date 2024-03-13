/* 
  * Team Id:        <GG_1742> 
  * Author List:    <Ankit Mandal, B Sai Sannidh Rayalu,Vikas Kumar,Shashwat Bokhad> 
  * Filename:       <final6.ino>  
  * Theme:          <GeoGuide> 
  * Functions:       <mainx(char mk), irprint(), irsetup(), buzz(int s), linefollow(), forward(), stp(), turnright(), turnleft(), turnright90(), turnleft90(), cnt(int s), uturn(), setup(), loop()> 
  * Global Variables: <in1, in2 ,in3, in4, irpinx, irpin1, irpin2, irpin3, irpin4, ena, enb, buzzled, ssid, password, port,  host, client, PWMFreq1, PWMChannel1, PWMResolution1, MAX_DUTY_CYCLE1, 
  *                    PWMFreq2, PWMChannel2, PWMResolution2, MAX_DUTY_CYCLE2, nd, m, l, r, l_, r_>
*/ 




#include <WiFi.h>

// WiFi credentials
const char* ssid = "Baka";                    //Enter your wifi hotspot ssid
const char* password =  "kuchnhihaii";               //Enter your wifi hotspot password
const uint16_t port = 8002;                           //port number used for communication
const char * host = "192.168.214.4";                   //Enter the ip address of your laptop after connecting it to wifi hotspot

WiFiClient client;


//defining pin numbers

// moter driver pins
#define in1 16
#define in2 4
#define in3 2
#define in4 15


//ir sensor pins
#define irpinx 19
#define irpin1 25
#define irpin2 33
#define irpin3 23
#define irpin4 22


//ENA pins for PWM signal for Motor A and B
#define ena 17
#define enb 5


#define buzzled 27
//global variables
// defining motor parameters for motor speed control


//motor1 setup
const int PWMFreq1 = 5000; /* 5 KHz */
const int PWMChannel1 = 0;
const int PWMResolution1 = 10;
const int MAX_DUTY_CYCLE1 = (int)(pow(2, PWMResolution1) - 1);


//motor2 setup
const int PWMFreq2 = 5000; /* 5 KHz */
const int PWMChannel2= 2;
const int PWMResolution2 = 10;
const int MAX_DUTY_CYCLE2 = (int)(pow(2, PWMResolution2) - 1);


int nd=673;// delay value for turning left,right at right angles

int m,l,r,l_,r_; // l(left sensor) m(middle sensor) r(right sensor) l_(leftmost sensor) r_(rightmost sensor)


/* 
  * Function Name:<mainx> 
  * Input:     <char> 
  * Output:    <None> 
  * Logic:     <Takes in char value mk and performs its required operation if char is R the performed operation is leftturn> 
  * Example Call:   < mainx("R");>  
*/ 
void mainx(char mk){  
    if(mk=='R'){
        turnright90();
    }
    else if(mk=='L'){
        turnleft90();
    }
    else if(mk=='U'){
        uturn();
    }
    else if(mk=='F'){
        forward();
    }
    else{
      return;
    }
}


/* 
  * Function Name:<irprint> 
  * Input:     <None> 
  * Output:    <None> 
  * Logic:     <Prints all the irsensor readings> 
  * Example Call:   <irprint();>  
*/ 
void irprint(){
  Serial.print(l_);
  Serial.print(" ");
  Serial.print(l);
  Serial.print(" ");
  Serial.print(m);
  Serial.print(" ");
  Serial.print(r);
  Serial.print(" ");
  Serial.print(r_);
  Serial.println();
}


/* 
  * Function Name:<irsetup()> 
  * Input:     <None> 
  * Output:    <None> 
  * Logic:     <initializes all the irsensors read values from the sensors pin> 
  * Example Call:   <irsetup();>  
*/ 
void irsetup(){
  l_=digitalRead(irpin1);
  l=digitalRead(irpin2);
  m=digitalRead(irpinx);
  r=digitalRead(irpin3);
  r_=digitalRead(irpin4);
}


/* 
  * Function Name:<buzz> 
  * Input:     <int s which takes in the second value which beeps the buzzer for s seconds> 
  * Output:    <Return value with description if any> 
  * Logic:     <it highs the buzzer pin for s seconds and then Lows the pin for another s seconds> 
  * Example Call:   <buzz(1); buzzer will bepp for 1 second>  
*/ 
void buzz(int s){
  digitalWrite(buzzled,HIGH);
  delay(s*1000);
  digitalWrite(buzzled,LOW);
  delay(s*1000);
  
}


/* 
  * Function Name:<linefollow> 
  * Input:     <None> 
  * Output:    <None> 
  * Logic:     <it checks all 5 ir sensors readings and computes the desired command for both motors to follow for line following> 
  * Example Call:   <linefollow();>  
*/ 
void linefollow(){
    //  3 IR Sensors + 2  IR 
    // a sensor value 0 for black and 1 for white
    if((l==0 && m==1 && r==1) || (l==0 && m==0 && r==1) || (l_==1 && r_==0)){
        turnright();
    }
    
    else if((l==1 && m==1 && r==0) || (l==1 && m==0 && r==0) || (l_==0 && r_==1)){
        turnleft();
    }
    
    else{
      forward();
    }
        
}


/* 
  * Function Name:<forward> 
  * Input:     <None> 
  * Output:    <None> 
  * Logic:     <it just turns on both DC motors at exact same speed in the same direction to perform the forward action> 
  * Example Call:   <forward();>  
*/ 
void forward(){
  cnt(890);
  Serial.println("forward");
  digitalWrite(in2, LOW);
  digitalWrite(in1, HIGH);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW); 
}


/* 
  * Function Name:<stp> 
  * Input:     <None> 
  * Output:    <None> 
  * Logic:     <it performs the stopping of motors by setting all motor pins to low> 
  * Example Call:   <stp();>  
*/
void stp(){
  Serial.println("stop");
  digitalWrite(in2, LOW);
  digitalWrite(in1, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
}


/* 
  * Function Name:<turnright> 
  * Input:     <None> 
  * Output:    <None> 
  * Logic:     <The function performs the task of turning right for the split seconds it is called> 
  * Example Call:   <turnright()>  
*/
void turnright(){
  cnt(MAX_DUTY_CYCLE1-75);
  Serial.println("right");
  digitalWrite(in2, HIGH);
  digitalWrite(in1, LOW);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW); 
}


/* 
  * Function Name:<turnleft> 
  * Input:     <None> 
  * Output:    <None> 
  * Logic:     <The function performs the task of turning left for the split seconds it is called> 
  * Example Call:   <turnleft()>  
*/
void turnleft(){
  cnt(MAX_DUTY_CYCLE2-75);
  Serial.println("left");
  digitalWrite(in2, LOW);
  digitalWrite(in1, HIGH);
  digitalWrite(in3, LOW);
  digitalWrite(in4,  HIGH); 
}


/* 
  * Function Name:<turnright90> 
  * Input:     <None> 
  * Output:    <None> 
  * Logic:     <The function performs the task of turning right at 90 degress> 
  * Example Call:   <turnright90()>  
*/
void turnright90(){
  turnright();
  delay(nd);
  stp();
  delay(nd);
}


/* 
  * Function Name:<turnleft90> 
  * Input:     <None> 
  * Output:    <None> 
  * Logic:     <The function performs the task of turning left at 90 degress> 
  * Example Call:   <turnleft90()>  
*/
void turnleft90(){
  turnleft();
  delay(nd);
  stp();
  delay(nd);
  
}


/* 
  * Function Name: <cnt> 
  * Input:         <None> 
  * Output:        <None> 
  * Logic:         <controls the speed of both moters equally for same speed> 
  * Example Call:  <cnt();>  
*/
void cnt(int s){
  ledcWrite(PWMChannel1, s);
  ledcWrite(PWMChannel2, s);
}


/* 
  * Function Name: <uturn> 
  * Input:         <None> 
  * Output:        <None> 
  * Logic:         <the function performs the task of turning the bot 180 degrees means a uturn> 
  * Example Call:  <uturn();>  
*/
void uturn(){
  turnleft();
  delay(nd*2+244);
  stp();
  delay(nd*2+244);
}


/* 
  * Function Name: <setup> 
  * Input:         <None> 
  * Output:        <None> 
  * Logic:         <The setup() function in Arduino is a special function that runs 
  * once when the Arduino board is powered up or reset. Its main purpose is to initialize variables, 
  * pin modes, libraries, and other settings needed for the program to function properly> 
  * Example Call:  <Called automatically by the Operating System>  
*/
void setup() {
    Serial.begin(115200);                          //Serial to print data on Serial Monitor
  
    //Connecting to wifi
    WiFi.begin(ssid, password);
  
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.println("...");
    }
   
    Serial.print("WiFi connected with IP: ");
    Serial.println(WiFi.localIP());
    
    //Motor pins as output
    pinMode(in1, OUTPUT);
    pinMode(in2, OUTPUT);
    pinMode(in3, OUTPUT);
    pinMode(in4, OUTPUT);

    // ir sensor pins as input
    pinMode(irpin1, INPUT);
    pinMode(irpin2, INPUT);
    pinMode(irpin3, INPUT);
    pinMode(irpin4, INPUT);

    //buzzer pin for output
    pinMode(buzzled, OUTPUT);

    //setting up channel and frequeincy for moter A nad B
    ledcSetup(PWMChannel1, PWMFreq1, PWMResolution1);
    ledcSetup(PWMChannel2, PWMFreq2, PWMResolution2);
    /* Attach the LED PWM Channel to the GPIO Pin */
    ledcAttachPin(ena, PWMChannel1);
    ledcAttachPin(enb, PWMChannel2);
    
    //Keeping all motors  and buzzer off initially
    digitalWrite(in1, LOW);
    digitalWrite(in2, LOW);
    digitalWrite(in3, LOW);
    digitalWrite(in4, LOW);

    digitalWrite(buzzled, LOW);

}


/* 
  * Function Name: <loop> 
  * Input:         <None> 
  * Output:        <None> 
  * Logic:         <It contains the main code logic and instructions that are executed repeatedly 
  * as long as the Arduino board is powered on. This function is responsible for controlling the 
  * behavior of the Arduino, processing inputs, performing calculations, and driving outputs based 
  * on the programmed logic. It runs in an infinite loop, allowing the Arduino to continuously perform 
  * its intended tasks.> 
  * Example Call:  <Called automatically by the Operating System>  
*/
void loop() {
   if (!client.connect(host, port)) {
    Serial.println("Connection to host failed"); 
    delay(200);
    return;
  }

  delay(6000);
  while(1){
      irsetup(); // SETTING UP IR SENSORS 
      linefollow(); // EXECUTING LINE FOLLOWING
      
      if(l==1 && m==1 && r==1){
          /*
           // the given coondition checks if the bot visited any node if the condition satisfy 
           the bot sends a signal 'N' to the host then the host with its path planning algorithm 
           tells the the bot where to move 'L' LEFT 'F' forward 'R' right 'U' uturn
           */
          delay(680);
          stp();
          char ms='X'; 
          while(ms!='R' && ms!='L' && ms!='U' && ms!='F'){
            /*
             if message recived from the host is inproper the bot request again to host for command until it recives a correct command
             (basiclly this deals with mesaage error handiling)
             */
            client.print('N');
            delay(100);
            ms=client.read();
          }
          mainx(ms); // evecuting the command recived
          Serial.println("NODE");  
          client.print("D"); // sending host conformation that mst is properly recived and exicuted
      }
      else{
        char ms = client.read(); 
        /*
         * it continuisly recives messages from the host if the bot get closed to the stopping point(event point) 
         * the host sends message 'k','W','E' for stoping bepping the buzzer and executing moter commands uturn ,forward
         * or if the bot has completed its run and the bot has returned to start end point its stops for infinite amount of time for thi message 'E'
         * is used
         */
        Serial.println(ms);
        if (ms=='K'){
            stp();
            buzz(1);//beppint the buzzer for 1 sec
            uturn();
        }
        else if(ms=='W'){
            stp();
            buzz(1);//beppint the buzzer for 1 sec
            forward();
        }
        else if(ms=='E'){
            stp();
            buzz(5);//beppint the buzzer for 5 sec
            while(1){
                stp();
            }
            
        }
        client.print("D");
      }

      delay(80);// delay for perfect synchronization b/w host and client for message transfer
      

  }
       
}
