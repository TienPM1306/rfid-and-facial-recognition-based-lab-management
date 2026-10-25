#include <WiFi.h>
#include <SPI.h>
#include <MFRC522.h>
#include "FirebaseESP32.h"
#include <NTPClient.h>

#define FIREBASE_HOST "https://tien-ff9d3-default-rtdb.firebaseio.com/"
#define FIREBASE_AUTH "Jta9F5ljK17Q8Lf3MKvs9JreMPf8XrghQVgGONmm"
#define RST_PIN 22
#define SS_PIN 21
MFRC522 mfrc522(SS_PIN, RST_PIN);

const char ssid[] = "Uchihahahaha";
const char pass[] = "Minhtien@16";

WiFiUDP ntpUDP;
const long utcOffsetInSeconds = 7 * 3600; // UTC+7
NTPClient timeClient(ntpUDP, "pool.ntp.org", utcOffsetInSeconds);

String uidPath = "/";
FirebaseData firebaseData;
FirebaseAuth firebaseAuth;
FirebaseConfig firebaseConfig;

int buttonStatus = 0; // Trạng thái mặc định

void connect() {
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("\nConnected!");
  delay(2000);
}

String getFormattedDate() {
  timeClient.update();
  unsigned long epochTime = timeClient.getEpochTime();
  struct tm *ptm = gmtime((time_t *)&epochTime);
  char formattedTime[20];
  sprintf(formattedTime, "%02d-%02d-%04d %02d:%02d:%02d", ptm->tm_mday, ptm->tm_mon + 1, ptm->tm_year + 1900, ptm->tm_hour, ptm->tm_min, ptm->tm_sec);
  return String(formattedTime);
}

void updateButtonStatus() {
  if (Firebase.getInt(firebaseData, uidPath + "button"))
    buttonStatus = firebaseData.intData();
}

void checkAccess(String temp) {
  Serial.println("CHECKING ACCESS FOR UID: " + temp);
  String employeePath = uidPath + "/ListOfEmployees/" + temp;

  if (Firebase.getJSON(firebaseData, employeePath)) {
    // Nếu UID tồn tại, xử lý dữ liệu như cũ
    FirebaseJson employeeData = firebaseData.jsonObject();
    FirebaseJsonData jsonData;

    String cnic, department, email, name;

    employeeData.get(jsonData, "Cnic");
    cnic = jsonData.stringValue;

    employeeData.get(jsonData, "Department");
    department = jsonData.stringValue;

    employeeData.get(jsonData, "Email");
    email = jsonData.stringValue;

    employeeData.get(jsonData, "Name");
    name = jsonData.stringValue;

    String formattedDate = getFormattedDate();

    FirebaseJson attendanceData;
    attendanceData.add("Cnic", cnic);
    attendanceData.add("Department", department);
    attendanceData.add("Email", email);
    attendanceData.add("Name", name);
    attendanceData.add("status", buttonStatus); // Áp dụng trạng thái từ button
    attendanceData.add("time", formattedDate);

    // Chỉ ghi dữ liệu lên Firebase nếu có thông tin hợp lệ
    if (!cnic.isEmpty() && !department.isEmpty() && !email.isEmpty() && !name.isEmpty()) {
      if (Firebase.pushJSON(firebaseData, uidPath + "/attendence", attendanceData)) {
        Serial.println("ATTENDENCE RECORDED: " + firebaseData.dataPath());
        Firebase.setInt(firebaseData, employeePath + "/status", buttonStatus); // Cập nhật trạng thái trong ListOfEmployees

        // Cập nhật trường event
        FirebaseJson eventData;
        eventData.add("Name", name);
        eventData.add("time", formattedDate);
        if (Firebase.setJSON(firebaseData, uidPath + "/event", eventData)) {
          Serial.println("EVENT UPDATED: " + firebaseData.dataPath());
        } else {
          Serial.println("ERROR UPDATING EVENT: " + firebaseData.errorReason());
        }

      } else {
        Serial.println("ERROR: " + firebaseData.errorReason());
      }
    } else {
      Serial.println("Invalid data received. No attendance recorded.");
    }
  } else {
    // Nếu UID không tồn tại, chỉ in ra serial mà không ghi lên Firebase
    Serial.println("UID NOT FOUND. NO DATA RECORDED.");
  }
}

void setup() {
  Serial.begin(9600);
  WiFi.begin(ssid, pass);

  SPI.begin();
  mfrc522.PCD_Init();
  timeClient.begin();

  connect();
  firebaseConfig.host = FIREBASE_HOST;
  firebaseConfig.signer.tokens.legacy_token = FIREBASE_AUTH;
  Firebase.begin(&firebaseConfig, &firebaseAuth);
  Firebase.reconnectWiFi(true);

  updateButtonStatus(); // Đọc trạng thái button ban đầu
  delay(2000);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connect();
  }

  updateButtonStatus(); // Lắng nghe và cập nhật trạng thái button

  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    String uid = "";
    for (byte i = 0; i < mfrc522.uid.size; i++) {
      uid += String(mfrc522.uid.uidByte[i]);
    }
    uid.toUpperCase();

    Serial.print("UID của thẻ RFID: ");
    Serial.println(uid);

    checkAccess(uid); // Kiểm tra quyền truy cập và ghi nhận thông tin nhân viên
  }
}
