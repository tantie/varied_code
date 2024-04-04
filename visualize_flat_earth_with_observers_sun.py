#не спрашивайте меня зачем

import numpy as np
import matplotlib.pyplot as plt

def visualize_flat_earth_with_observers_sun():
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111)

    # Создание диска для плоской Земли
    earth_radius = 1
    circle = plt.Circle((0, 0), earth_radius, color='lightblue', alpha=0.3)
    ax.add_artist(circle)

    # Позиции наблюдателей на плоской Земле
    observer_longs = [0, 90, -90, 180]  # Долготы наблюдателей
    for i, lon in enumerate(observer_longs):
        x = np.cos(np.radians(lon)) * 0.8  # Умножаем на 0.8, чтобы разместить наблюдателей внутри диска
        y = np.sin(np.radians(lon)) * 0.8
        ax.scatter(x, y, color='red', s=100, label='Observer' if i == 0 else "")

    # Солнце для летнего солнцестояния ближе к центру диска
    ax.scatter(0, 0.5, color='yellow', s=500, label='Summer Solstice Sun', alpha=1)
    # Солнце для зимнего солнцестояния дальше от центра, но всё ещё внутри диска
    ax.scatter(0, -0.5, color='orange', s=500, label='Winter Solstice Sun', alpha=1)

    # Настройки визуализации
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_aspect('equal', 'box')

    # Убираем дубликаты из легенды
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    plt.show()

visualize_flat_earth_with_observers_sun()
