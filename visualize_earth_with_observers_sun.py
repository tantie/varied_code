#не спрашивайте меня зачем
import numpy as np
import matplotlib.pyplot as plt

def rotate_about_y(x, y, z, theta):
    """Поворот точек вокруг оси Y."""
    theta_rad = np.radians(theta)
    cos_theta, sin_theta = np.cos(theta_rad), np.sin(theta_rad)

    x_rotated = cos_theta * x + sin_theta * z
    z_rotated = -sin_theta * x + cos_theta * z
    return x_rotated, y, z_rotated

def visualize_earth_with_observers_sun():
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')

    # Генерация сферы для Земли
    u, v = np.mgrid[0:2*np.pi:100j, 0:np.pi:50j]
    x = np.cos(u)*np.sin(v)
    y = np.sin(u)*np.sin(v)
    z = np.cos(v)

    # Наклон Земли
    earth_tilt = 23.5
    x_rotated, y_rotated, z_rotated = rotate_about_y(x, y, z, earth_tilt)

    # Визуализация наклоненной Земли
    ax.plot_surface(x_rotated, y_rotated, z_rotated, color='blue', edgecolors='k', alpha=0.3)

    # Позиции наблюдателей
    observer_lat = -60  # Широта наблюдателей
    observer_longs = [0, 90, -90, 180]  # Долготы наблюдателей
    for i, lon in enumerate(observer_longs):
        x = np.cos(np.radians(lon)) * np.cos(np.radians(observer_lat))
        y = np.sin(np.radians(lon)) * np.cos(np.radians(observer_lat))
        z = np.sin(np.radians(observer_lat))
        # Применяем наклон к координатам наблюдателей
        x_rotated, y_rotated, z_rotated = rotate_about_y(x, y, z, earth_tilt)
        ax.scatter(x_rotated, y_rotated, z_rotated, color='red', s=100, depthshade=True, label=f'Observer {i+1}' if i == 0 else "")

    # Солнце в летнее и зимнее солнцестояния
    # Расположение солнца выше и ниже Земли для визуализации солнцестояний
    ax.scatter([0], [0], [2], color='yellow', s=500, label='Summer Solstice Sun', alpha=1)
    ax.scatter([0], [0], [-2], color='orange', s=500, label='Winter Solstice Sun', alpha=1)

    # Наклон оси Земли
    tilt_line = np.linspace(-2, 2, 100)
    tilt_x = tilt_line * np.sin(np.radians(23.5))
    tilt_z = tilt_line * np.cos(np.radians(23.5))
    ax.plot(tilt_x, [0]*100, tilt_z, color='green', linewidth=2, label='Axis Tilt')


    # Настройки визуализации
    ax.set_xlim([-2, 2])
    ax.set_ylim([-2, 2])
    ax.set_zlim([-2, 2])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.view_init(elev=20, azim=-40)

    # Убираем дубликаты из легенды
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())

    plt.show()

visualize_earth_with_observers_sun()
