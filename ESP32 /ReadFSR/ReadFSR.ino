void setup() {
  pinMode(4,OUTPUT);
  Serial.begin(115200);
  Serial.println("Setup Done");
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.print("FSR Value: ");
  Serial.println(analogRead(4));
}
