import random
import tkinter as tk
from tkinter import Button, END, Text

# Проверка пересечения времени
def is_time_overlap(start1, end1, routes):
    for start2, end2 in routes:
        if start1 <= end2 and start2 <= end1:
            return True  # Пересечение времени
    return False

# Проверка, входит ли маршрут в рабочее время водителя
def is_within_work_hours(start_time, end_time, work_start, work_end):
    return work_start <= start_time < work_end and work_start < end_time <= work_end

# Вычисление времени окончания маршрута
def calculate_route_end(start_time, route_duration):
    return start_time + route_duration

# Метод распределения маршрутов с учетом рабочего времени
def schedule_routes(driver_list, num_routes, traffic_route_time, work_hours):
    schedule = {driver: [] for driver in driver_list}  # Создаем расписание для каждого водителя
    all_routes = []

    # Генерация всех маршрутов
    for _ in range(num_routes):
        start_time = random.choice(route_times)
        end_time = calculate_route_end(start_time, traffic_route_time)
        all_routes.append((start_time, end_time))

    # Распределение маршрутов по кругу
    driver_index = 0  # Индекс текущего водителя
    for route in all_routes:
        assigned = False
        attempts = 0  # Для предотвращения бесконечного цикла
        while not assigned and attempts < len(driver_list):
            driver = driver_list[driver_index]
            work_start, work_end = work_hours[driver]
            if (
                not is_time_overlap(route[0], route[1], schedule[driver]) and
                is_within_work_hours(route[0], route[1], work_start, work_end)
            ):
                schedule[driver].append(route)
                assigned = True
            # Переходим к следующему водителю по кругу
            driver_index = (driver_index + 1) % len(driver_list)
            attempts += 1
        if not assigned:
            print(f"Маршрут с {route[0]} до {route[1]} невозможно распределить!")  # Для отладки

    return schedule

# Отображение расписания в текстовом поле
def display_schedule(schedule):
    schedule_text.delete(1.0, END)
    for driver, routes in schedule.items():
        schedule_text.insert(END, f"Водитель: {driver}\n")
        for start, end in routes:
            schedule_text.insert(END, f"  Рейс с {start}:00 до {end}:00\n")
        schedule_text.insert(END, "\n")

# Генерация расписания для водителей типа A
def generate_schedule_A():
    try:
        num_routes = int(num_routes_entry.get())
        if num_routes <= 0:
            schedule_text.insert(END, "\nОшибка: Количество маршрутов должно быть положительным числом.\n")
            return
        if not drivers_A:
            schedule_text.insert(END, "\nНет водителей типа A для создания расписания.\n")
            return

        work_hours_A = {driver: (8, 16) for driver in drivers_A}  # 8:00 до 16:00
        schedule = schedule_routes(drivers_A, num_routes, traffic_route_time, work_hours_A)
        display_schedule(schedule)
    except ValueError:
        schedule_text.insert(END, "\nОшибка: Введите корректное число маршрутов.\n")

# Генерация расписания для водителей типа B
def generate_schedule_B():
    try:
        num_routes = int(num_routes_entry.get())
        if num_routes <= 0:
            schedule_text.insert(END, "\nОшибка: Количество маршрутов должно быть положительным числом.\n")
            return
        if not drivers_B:
            schedule_text.insert(END, "\nНет водителей типа B для создания расписания.\n")
            return

        work_hours_B = {driver: (0, 24) for driver in drivers_B}  # 24 часа
        schedule = schedule_routes(drivers_B, num_routes, traffic_route_time, work_hours_B)
        display_schedule(schedule)
    except ValueError:
        schedule_text.insert(END, "\nОшибка: Введите корректное число маршрутов.\n")

# Пример данных
route_times = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]  # Времена маршрутов
traffic_route_time = 1  # Продолжительность маршрута в часах
drivers_A = ["Driver_A1", "Driver_A2", "Driver_A3"]
drivers_B = ["Driver_B1", "Driver_B2"]

# Создание интерфейса
root = tk.Tk()
root.title("Метод распределения маршрутов")
root.geometry("600x400")

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

num_routes_entry = tk.Entry(button_frame, width=10)
num_routes_entry.pack(pady=5)

schedule_text = Text(root, width=70, height=15)
schedule_text.pack(pady=10)

# Кнопки для запуска
generate_button_A = Button(button_frame, text="Сгенерировать расписание (A)", command=generate_schedule_A, bg="white", fg="#3D0071", font=("Helvetica", 12), relief="solid", bd=2)
generate_button_A.pack(pady=5, fill="x")

generate_button_B = Button(button_frame, text="Сгенерировать расписание (B)", command=generate_schedule_B, bg="white", fg="#3D0071", font=("Helvetica", 12), relief="solid", bd=2)
generate_button_B.pack(pady=5, fill="x")

root.mainloop()
