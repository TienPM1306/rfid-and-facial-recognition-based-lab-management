import cv2
import numpy as np
from PIL import Image
import os

# Đảm bảo thư mục chứa trainer1 tồn tại
trainer_path = 'E:/hoctap/HK8/Doan2/OpenCV/venv/test'
if not os.path.exists(trainer_path):
    os.makedirs(trainer_path)

path = 'E:/hoctap/HK8/Doan2/OpenCV/venv/test/dataset1'

recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier('E:/hoctap/HK8/Doan2/OpenCV/venv/test/haarcascade_frontalface_default.xml')

def getImagesAndLabels(path):
    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
    faceSamples = []
    ids = []

    for imagePath in imagePaths:
        PIL_img = Image.open(imagePath).convert('L')
        img_numpy = np.array(PIL_img, 'uint8')

        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_numpy)

        for(x,y,w,h) in faces:
            faceSamples.append(img_numpy[y:y+h,x:x+w])
            ids.append(id)
    return faceSamples, ids

print("\n [INFO] đang training dữ liệu...")
faces, ids = getImagesAndLabels(path)
recognizer.train(faces, np.array(ids))

# Lưu mô hình nhận diện khuôn mặt
recognizer.write('E:/hoctap/HK8/Doan2/OpenCV/venv/test/trainer.yml')  # Sử dụng định dạng .yml
print("\n [INFO] {0} Khuôn mặt được train. Thoát".format(len(np.unique(ids))))
