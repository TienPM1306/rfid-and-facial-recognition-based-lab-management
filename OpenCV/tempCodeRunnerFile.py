     # # Lưu ảnh khuôn mặt
                # face_image = frame[y:y + h, x:x + w]
                # filename = f"{recognized_name}_{number_counters.get(recognized_name, 0)}.jpg"
                # filepath = os.path.join(save_path, filename)
                # cv2.imwrite(filepath, face_image)
                # number_counters[recognized_name] = number_counters.get(recognized_name, 0) + 1

                # # Mã hóa ảnh thành Base64
                # encoded_image = encode_image_to_base64(filepath)

                # # Cập nhật vào Firebase Realtime Database với chuỗi Base64
                # db.reference("pic").push({
                #     "Name": recognized_name,
                #     "time": time_from_event,
                #     "image_url": encoded_image  # Lưu chuỗi Base64 vào Firebase
                # })