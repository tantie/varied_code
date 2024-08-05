import librosa
import numpy as np
import pyworld as pw
import soundfile as sf
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import io
import soundfile as sf

# Функция для определения пола на основе F0
def determine_gender(f0):
    median_f0 = np.median(f0[f0 > 0])  # Берем медиану, исключая нули
    return "male" if median_f0 < 200 else "female"

# Функция для обработки аудио и получения сегментов с временными метками
def process_audio_and_get_segments(audio_data, fs, segment_length_sec=3.0):
    segment_length = int(segment_length_sec * fs)  # Длина сегмента в сэмплах
    segments = []

    for start in range(0, len(audio_data), segment_length):
        end = min(start + segment_length, len(audio_data))
        audio_segment = audio_data[start:end].astype(np.float64)

        # Анализируем сегмент на наличие голоса
        f0, sp, ap = pw.wav2world(audio_segment, fs)
        if len(f0) > 0 and np.any(f0 > 0):
            gender = determine_gender(f0)
            segments.append((audio_segment, gender))
            print(f"Segment {start}-{end}, Gender: {gender}")

    return segments

# Функция для распознавания и перевода текста
def recognize_and_translate(segment, fs):
    recognizer = sr.Recognizer()
    temp_filename = 'temp_audio.wav'
    sf.write(temp_filename, segment, fs)

    # Распознавание текста
    with sr.AudioFile(temp_filename) as source:
        try:
            audio_data = recognizer.record(source)
            original_text = recognizer.recognize_google(audio_data, language='ru-RU')
            print(f"Recognized text: {original_text}")
            # Перевод текста
            translator = GoogleTranslator(source='ru', target='en')
            translated_text = translator.translate(original_text)
            print(f"Translated text: {translated_text}")
        except sr.UnknownValueError:
            print("Не удалось распознать текст")
            translated_text = ""
        except sr.RequestError as e:
            print(f"Ошибка запроса; {e}")
            translated_text = ""

    os.remove(temp_filename)
    return translated_text

# Функция для синтеза и обработки переведенного текста
def synthesize_and_process(text, fs, gender):
    if not text:
        return np.array([], dtype=np.float64)

    tts = gTTS(text, lang='en')
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    english_audio_data, _ = sf.read(audio_fp)

    english_audio_data = english_audio_data.astype(np.float64)
    processed_segment = process_segment(english_audio_data, fs, gender)

    return processed_segment

# Обработка сегмента голоса
def process_segment(audio_segment, fs, gender):
    f0, sp, ap = pw.wav2world(audio_segment, fs)

    # Изменение тембра на основе пола
    f0_mod = f0 * 0.4 if gender == "male" else f0 * 0.9
    sp_mod = np.sqrt(sp) * 2.5

    processed_segment = pw.synthesize(f0_mod, sp_mod, ap, fs)
    processed_segment = np.clip(processed_segment, -1.0, 1.0)  # значения остаются в допустимом диапазоне

    return processed_segment

def main():
    audio_file_path = '123.wav'
    audio_data, fs = librosa.load(audio_file_path, sr=None)

    # Получение сегментов с временными метками
    segments = process_audio_and_get_segments(audio_data, fs)

    # Инициализация финального аудиомассива
    final_audio = np.array([], dtype=np.float64)

    # Обработка каждого сегмента
    for segment, gender in segments:
        translated_text = recognize_and_translate(segment, fs)
        processed_segment = synthesize_and_process(translated_text, fs, gender)
        final_audio = np.concatenate((final_audio, processed_segment))


    # Сохранение финального аудиофайла
    sf.write('processed_english_voice.wav', final_audio, fs)
    print("Файл с обработанным английским голосом сохранён как 'processed_english_voice.wav'.")

if __name__ == "__main__":
    main()

# Функция для замедления аудио путем изменения частоты дискретизации
def slow_down_audio(input_path, output_path, rate):
    # Загрузка аудиофайла
    audio, sr = librosa.load(input_path, sr=None)

    # Новый частоты дискретизации для замедления
    new_sr = int(sr * rate)

    # Сохранение аудио с новой частотой дискретизации
    sf.write(output_path, audio, new_sr)
    print(f"Файл с замедленным голосом сохранён как '{output_path}'.")

# Используем функцию для замедления аудио в два раза
slow_down_audio('processed_english_voice.wav', 'processed_english_voice_slowed.wav', rate=0.55)
