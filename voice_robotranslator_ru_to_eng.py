import librosa
import numpy as np
import pyworld as pw
import soundfile as sf
from pydub import AudioSegment
from scipy.signal import lfilter
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS

# Функция для добавления эффекта задержки
def add_delay(sound, delay_time, decay_factor):
    delay_samples = int(delay_time * sound.frame_rate)
    sound_array = np.array(sound.get_array_of_samples(), dtype=np.float64)
    delay = np.zeros(delay_samples)
    sound_with_delay = np.concatenate((sound_array, delay))
    
    for i in range(delay_samples, len(sound_with_delay)):
        sound_with_delay[i] += decay_factor * sound_with_delay[i - delay_samples]
    
    return sound._spawn(sound_with_delay.astype(np.int16))

# Функция для биткршинга
def bitcrush(audio, bit_depth):
    max_val = float(2**(bit_depth - 1) - 1)
    audio *= max_val
    audio = np.round(audio) / max_val
    return audio

# Конвертация MP3 в WAV для распознавания
audio = AudioSegment.from_mp3('/content/drive/MyDrive/123.mp3')
audio.export('/content/drive/MyDrive/123_converted.wav', format='wav')

# Распознавание речи
recognizer = sr.Recognizer()
audio_file_path = '/content/drive/MyDrive/123_converted.wav'

with sr.AudioFile(audio_file_path) as source:
    audio_data = recognizer.record(source)
    original_text = recognizer.recognize_google(audio_data, language='ru-RU')  # Распознавание на русском языке

print(f"Распознанный текст: {original_text}")

# Перевод текста на английский с использованием deep_translator
translator = GoogleTranslator(source='ru', target='en')
translated_text = translator.translate(original_text)

print(f"Переведенный текст: {translated_text}")

# Преобразование текста в аудио на английском
tts = gTTS(translated_text, lang='en')
tts.save('/content/drive/MyDrive/translated_english.wav')

# Загрузка созданного английского WAV файла
filename = '/content/drive/MyDrive/translated_english.wav'
x, fs = librosa.load(filename, sr=None)  # sr=None сохраняет исходную частоту дискретизации

# Преобразование аудиоданных в тип double (np.float64)
x = x.astype(np.float64)

# Анализ звука с помощью World Vocoder
f0, sp, ap = pw.wav2world(x, fs)  # Извлечение характеристик голоса

# Применение вокодера и изменение тембра
f0_mod = f0 * 0.5  # Уменьшение тона
sp_mod = np.sqrt(sp) * 1.5  # Изменение спектральных характеристик

# Синтез речи с изменёнными характеристиками
y = pw.synthesize(f0_mod, sp_mod, ap, fs)

# Применение биткршинга для создания роботизированного эффекта
y = bitcrush(y, 16)  # Уменьшение битности до 16 бит

# Сохранение изменённого аудио
sf.write('/content/drive/MyDrive/robot_voice_english.wav', y, fs)

# Чтение и добавление эффекта задержки и реверберации
robot_voice = AudioSegment.from_wav('/content/drive/MyDrive/robot_voice_english.wav')
#robot_voice = add_delay(robot_voice, delay_time=0.1, decay_factor=0.5)

# Сохранение финального файла с роботизированным голосом на английском
robot_voice.export('/content/drive/MyDrive/robot_voice_final_english.wav', format='wav')

print("Файл на английском сохранён как 'robot_voice_final_english.wav' в Google Drive.")
