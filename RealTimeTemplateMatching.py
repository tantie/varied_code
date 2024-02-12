import cv2
import numpy as np

# Инициализируем камеру
cap = cv2.VideoCapture(0)  # Используйте 0 для основной камеры

template = None
template_w, template_h = 0, 0

while True:
    ret, frame = cap.read()  # Читаем кадр с камеры
    if not ret:
        print("Не удалось захватить изображение с камеры.")
        break

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Преобразование в градации серого

    # При нажатии на клавишу '1', сохраняем текущий кадр как новый шаблон
    if cv2.waitKey(1) & 0xFF == ord('1'):
        template = gray_frame.copy()
        cv2.imwrite('frame.jpg', template)
        template_w, template_h = template.shape[::-1]
        print("Шаблон обновлен.")

    if template is not None:
        # Сравниваем frame с видеопотоком
        result = cv2.matchTemplate(gray_frame, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val > 0.8:  # Коэфицент совпадения
            top_left = max_loc
            bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(frame, "Check", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            print("Check")

    cv2.imshow('Video Stream', frame)  # Показываем видеопоток

    # Выход по нажатию клавиши 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
