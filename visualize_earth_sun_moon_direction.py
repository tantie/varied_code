# упрощенная модель/пример того, как можно найти положение солнца по координатам, дате и времени

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime, timezone
import pvlib

def plot_earth_sun_moon_direction(latitude, longitude, date, time):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Генерация сферы для Земли
    u, v = np.mgrid[0:2*np.pi:100j, 0:np.pi:50j]
    earth_x = np.cos(u)*np.sin(v)
    earth_y = np.sin(u)*np.sin(v)
    earth_z = np.cos(v)

    # Визуализация Земли
    ax.plot_surface(earth_x, earth_y, earth_z, color='blue', edgecolors='k', alpha=0.3)

    # Убедитесь, что время в UTC для корректных расчетов
    time_utc = time.replace(tzinfo=timezone.utc)

    # Расчет положения Солнца с учетом времени и даты
    solartime = pvlib.solarposition.get_solarposition(time_utc, latitude, longitude)
    azimuth = solartime['azimuth'].values[0]
    elevation = solartime['elevation'].values[0]

    # Вывод координат Солнца
    print(f"Sun Azimuth: {azimuth} degrees")
    print(f"Sun Elevation: {elevation} degrees")

    # Расчет "азимута" и "высоты" для Луны упрощенный вариант не привязаный к реальности, для визуализации
    moon_azimuth = (azimuth + 180) % 360  # Гарантируем, что значение остается в пределах 0-360
    moon_elevation = elevation  # предполагаем, что высота Луны аналогична Солнцу

    # Вывод координат Луны
    print(f"Moon Azimuth: {moon_azimuth} degrees")
    print(f"Moon Elevation: {moon_elevation} degrees")

    # Расчет положения Солнца для визуализации
    sun_distance = 2.0  # Абстрактное расстояние до Солнца для визуализации
    sun_x = sun_distance * np.sin(np.radians(elevation)) * np.sin(np.radians(azimuth))
    sun_y = sun_distance * np.sin(np.radians(elevation)) * np.cos(np.radians(azimuth))
    sun_z = sun_distance * np.cos(np.radians(elevation))

    # Отображение Солнца как точки
    ax.scatter(sun_x, sun_y, sun_z, color='yellow', s=100, edgecolors='black', alpha=1)

    # Добавление Луны, позиция противоположна Солнцу
    moon_distance = 1.7  # Абстрактное расстояние до Луны для визуализации
    moon_x = -sun_x * moon_distance / sun_distance
    moon_y = -sun_y * moon_distance / sun_distance
    moon_z = -sun_z * moon_distance / sun_distance

    # Отображение Луны как точки
    ax.scatter(moon_x, moon_y, moon_z, color='gray', s=50, edgecolors='black', alpha=1)

    # Настройка диапазонов осей
    ax.set_xlim([-2, 2])
    ax.set_ylim([-2, 2])
    ax.set_zlim([-2, 2])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()

# Пример использования с координатами Лос-Анджелеса и текущим временем в UTC
plot_earth_sun_moon_direction(34.0522, -118.2437, '2023-10-03', datetime.now(timezone.utc))

# координаты Москвы 55.7558  37.6173
