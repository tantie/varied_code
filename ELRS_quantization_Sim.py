"""
ELRS Quantization Simulator

Описание:
    Скрипт симулирует передачу сигнала по протоколу, подобному ELRS,
    с квантованием дельты и отображением битового потока.

Функции:
    - Ручной и автоматический режим изменения сигнала (ползунок / рандом);
    - График оригинального и восстановленного сигнала;
    - Отображение текущей ошибки, переданной дельты и бинарного кода;
    - Интерфейс в одном окне (Tkinter + встроенный matplotlib).

Управление:
    - Переключатель режима (ручной / авто);
    - Ползунок значения сигнала (0–1023).

"""

import numpy as np
import matplotlib
matplotlib.use('TkAgg')

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Конфигурация
bits = 4
step = 1024 // (2 ** bits)
orig_val = 512
decoded_val = 512
manual_value = 512
control_mode = "manual"

time_history = []
orig_history = []
decoded_history = []

# Функция обновления графика
def update_plot():
    global orig_val, decoded_val, manual_value, control_mode
    frame = len(time_history)

    if control_mode == "auto":
        delta_random = np.random.randint(-250, 251)
        new_orig = np.clip(orig_val + delta_random, 0, 1023)
    else:
        new_orig = manual_value

    diff = new_orig - decoded_val
    step_size = step // 2 if abs(diff) < step else step
    quantized_delta = round(diff / step_size) * step_size
    new_decoded = np.clip(decoded_val + quantized_delta, 0, 1023)

    orig_val = new_orig
    decoded_val = new_decoded

    time_history.append(frame)
    orig_history.append(orig_val)
    decoded_history.append(decoded_val)

    line_orig.set_data(time_history, orig_history)
    line_decoded.set_data(time_history, decoded_history)

    ax_main.set_xlim(max(0, frame - 100), frame + 10)

    scatter_orig.set_offsets([[0, orig_val]])
    scatter_decoded.set_offsets([[1, decoded_val]])

    current_error = np.mean(np.abs(np.array(orig_history) - np.array(decoded_history)))
    quant_level = int((quantized_delta + 512) / step_size)
    binary_code = format(quant_level, f'0{bits + 2}b')

    info_text.set_text(
        f"errors on 1024: {current_error:.2f}\n"
        f"compression: {bits}/10 bits\n"
        f"quantized delta: {quantized_delta}\n"
        f"sent bits: {binary_code} ({len(binary_code)} bits)"
    )

    canvas.draw()
    root.after(100, update_plot)

# --- Интерфейс ---
root = tk.Tk()
root.title("ELRS compression test")
root.geometry("1000x800")

top_frame = ttk.Frame(root)
top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

def on_slider(val):
    global manual_value
    manual_value = int(float(val))
    slider_val_label.config(text=f"{manual_value}")

def switch_mode():
    global control_mode
    if control_mode == "manual":
        control_mode = "auto"
        mode_button.config(text="Режим: авто")
    else:
        control_mode = "manual"
        mode_button.config(text="Режим: ручной")

mode_button = ttk.Button(top_frame, text="Режим: ручной", command=switch_mode)
mode_button.pack(side=tk.LEFT, padx=5)

ttk.Label(top_frame, text="Значение сигнала (0–1023):").pack(side=tk.LEFT, padx=5)
slider = ttk.Scale(top_frame, from_=0, to=1023, orient='horizontal', command=on_slider, length=300)
slider.set(512)
slider.pack(side=tk.LEFT, padx=5)

slider_val_label = ttk.Label(top_frame, text="512")
slider_val_label.pack(side=tk.LEFT)

# --- matplotlib внутри окна ---
fig, (ax_main, ax_scatter) = plt.subplots(2, 1, figsize=(10, 6))

line_orig, = ax_main.plot([], [], label='Original', color='blue')
line_decoded, = ax_main.plot([], [], label='Restored', color='red', linestyle='--')
ax_main.set_xlim(0, 100)
ax_main.set_ylim(0, 1023)
ax_main.set_title('Signal History')
ax_main.set_xlabel('Step')
ax_main.set_ylabel('Value')
ax_main.legend()
ax_main.grid(True)

info_text = ax_main.text(0.02, 0.88, "", transform=ax_main.transAxes, fontsize=11,
                         bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))

ax_scatter.set_xlim(-0.5, 1.5)
ax_scatter.set_ylim(0, 1023)
ax_scatter.set_xticks([0, 1])
ax_scatter.set_xticklabels(['Original', 'Restored'])
ax_scatter.set_title('Current Values')
ax_scatter.grid(True)

scatter_orig = ax_scatter.scatter(0, orig_val, s=200, color='blue')
scatter_decoded = ax_scatter.scatter(1, decoded_val, s=200, color='red')

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Запуск обновлений
root.after(100, update_plot)
root.mainloop()
