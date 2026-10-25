import cv2
import os
import numpy as np

# Khởi tạo webcam (sử dụng webcam mặc định, nếu có nhiều webcam, thay đổi chỉ mục 0 thành 1, 2, ...)
cap = cv2.VideoCapture(0)

# Tải model nhận diện khuôn mặt
face_detector = cv2.CascadeClassifier('E:/hoctap/HK8/Doan2/OpenCV/venv/test/haarcascade_frontalface_default.xml')

# Nhập ID khuôn mặt
face_id = input('\n Nhập ID khuôn mặt <return> ==> ')

print("\n [INFO] Đang chụp ảnh từ webcam...")

count = 0
capturing = True

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Không thể lấy ảnh từ webcam.")
        break

    # Lật ảnh để sửa lỗi bị ngược
    

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Chuyển sang ảnh xám
    faces = face_detector.detectMultiScale(gray, 1.3, 2)
    
    if len(faces) > 0:
        faces = sorted(faces, key=lambda f: f[2] * f[3])
        x, y, w, h = faces[-1]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 4)

        if count < 30:
            # Lưu ảnh đã cắt vào thư mục dataset
            cv2.imwrite("E:/hoctap/HK8/Doan2/OpenCV/venv/test/dataset1/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y + h, x:x + w])
            count += 1

    # Hiển thị khung hình
    cv2.imshow('Webcam', frame)

    if count >= 30 and capturing:
        print("Đã chụp đủ 30 ảnh! Nhấn ESC để thoát.")
        capturing = False

    # Nhấn phím ESC để thoát
    k = cv2.waitKey(1) & 0xFF
    if k == 27:  # ESC
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()

print("\n [INFO] Thoát...")
