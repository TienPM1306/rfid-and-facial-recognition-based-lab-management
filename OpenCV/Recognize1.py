import cv2
import numpy as np
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import base64

# Kết nối Firebase
cred = credentials.Certificate("E:/hoctap/HK8/Doan2/OpenCV/venv/tien-ff9d3-firebase-adminsdk-3lej2-c3d03a0f6d.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://tien-ff9d3-default-rtdb.firebaseio.com/"
})

# Đường dẫn tới file huấn luyện và model nhận diện khuôn mặt
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('E:/hoctap/HK8/Doan2/OpenCV/venv/test/trainer/trainer.yml')

cascadePath = "E:/hoctap/HK8/Doan2/OpenCV/venv/test/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

face_detector = cv2.CascadeClassifier('E:/hoctap/HK8/Doan2/OpenCV/venv/test/haarcascade_frontalface_default.xml')


# Danh sách tên theo ID
names = ['0', 'Tien', '2', '3', '4', '5']

font = cv2.FONT_HERSHEY_SIMPLEX
save_path = "E:/hoctap/HK8/Doan2/OpenCV/venv/test/images"
if not os.path.exists(save_path):
    os.makedirs(save_path)

number_counters = {}
unknown_counter = 0  # Biến mới theo dõi số thứ tự ảnh "Unknown"

# Biến lưu giá trị trước đó của trường "event"
previous_event_value = None

# Hàm chuyển ảnh thành chuỗi Base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        # Đọc ảnh dưới dạng byte và mã hóa nó thành Base64
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_image

# Hàm xử lý khi có thay đổi trong trường "event"
def handle_event_change(event_snapshot):
    global previous_event_value, unknown_counter  # Sử dụng biến toàn cục để lưu giá trị trước đó và số thứ tự Unknown

    try:
        # Thử lấy dữ liệu sự kiện từ snapshot bằng cách sử dụng .data()
        event_data = event_snapshot.data  # Thay vì .val(), thử dùng .data()

        if event_data is None:
            print("[INFO] Không có dữ liệu sự kiện.")
            return

        # Lấy thông tin tên và thời gian từ sự kiện
        name_from_event = event_data.get("Name", "unknown")
        time_from_event = event_data.get("time", datetime.now().strftime("%d-%m-%Y %H:%M:%S"))

        # Kiểm tra xem giá trị của trường "event" có thay đổi không
        current_event_value = f"{name_from_event}_{time_from_event}"

        # Nếu giá trị trước đó khác giá trị hiện tại, mới thực hiện lệnh chụp ảnh
        if previous_event_value != current_event_value:
            print(f"[INFO] Sự kiện thay đổi: {current_event_value}. Mở webcam để chụp ảnh...")

            # Mở webcam
            cap = cv2.VideoCapture(0)

            ret, frame = cap.read()

            if ret:
                # Chuyển ảnh sang ảnh xám để nhận diện khuôn mặt
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Phát hiện khuôn mặt trong ảnh
                faces = face_detector.detectMultiScale(gray, 1.3, 2)

                if len(faces) > 0:
                    # Sắp xếp các khuôn mặt theo diện tích (diện tích = w * h)
                    faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                    
                    # Lấy khuôn mặt lớn nhất (khuôn mặt có diện tích lớn nhất)
                    x, y, w, h = faces[0]
                    
                    # Vẽ hình chữ nhật xung quanh khuôn mặt lớn nhất
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 4)

                    # Cắt khuôn mặt lớn nhất ra khỏi ảnh
                    face_image = frame[y:y + h, x:x + w]

                    # Nhận diện khuôn mặt (recognition)
                    id, confidence = recognizer.predict(gray[y:y + h, x:x + w])

                    if confidence <= 50:
                        # Nếu nhận diện thành công, lấy tên người nhận diện
                        recognized_name = names[id]
                        print(confidence)
                    else:
                        # Nếu không nhận diện được, đặt tên là "Unknown"
                        recognized_name = f"Unknown_{unknown_counter}"
                        print(confidence)
                        unknown_counter += 1  # Tăng số thứ tự cho Unknown
                    
                    # Tạo tên file cho ảnh khuôn mặt
                    filename = f"{recognized_name}_{number_counters.get(recognized_name, 0)}.jpg"
                    filepath = os.path.join(save_path, filename)
                    
                    # Lưu ảnh khuôn mặt vào file
                    cv2.imwrite(filepath, face_image)

                    # Cập nhật số lượng ảnh đã lưu cho người này (hoặc "Unknown")
                    number_counters[recognized_name] = number_counters.get(recognized_name, 0) + 1

                    # Mã hóa ảnh thành Base64 và gửi lên Firebase
                    encoded_image = encode_image_to_base64(filepath)
                    db.reference("pic").push({
                        "Name": recognized_name,
                        "time": time_from_event,
                        "image_url": encoded_image
                    })

                    print(f"[INFO] Đã lưu ảnh và cập nhật vào Firebase với ảnh đã mã hóa.")
                else:
                    print("[INFO] Không phát hiện khuôn mặt trong ảnh.")

            cap.release()
            cv2.destroyAllWindows()

            # Cập nhật giá trị trước đó để so sánh lần sau
            previous_event_value = current_event_value
        else:
            print("[INFO] Giá trị trường 'event' không thay đổi. Không cần chụp ảnh.")

    except Exception as e:
        print(f"Lỗi khi xử lý sự kiện: {e}")

# Lấy giá trị trường "event" từ Firebase ngay khi chương trình bắt đầu để gán cho previous_event_value
def initialize_previous_event_value():
    global previous_event_value
    event_ref = db.reference("event")
    event_data = event_ref.get()

    if event_data is not None:
        name_from_event = event_data.get("Name", "unknown")
        time_from_event = event_data.get("time", datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
        previous_event_value = f"{name_from_event}_{time_from_event}"
        print(f"[INFO] Giá trị trường 'event' ban đầu: {previous_event_value}")
    else:
        print("[INFO] Không có dữ liệu trường 'event' trong Firebase.")

# Khởi tạo giá trị trước đó
initialize_previous_event_value()

# Lắng nghe thay đổi trong trường "event"
event_ref = db.reference("event")
event_ref.listen(handle_event_change)
