import random
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import Button, END, Text

# Проверка на пересечение временных интервалов
def is_time_overlap(start1, end1, start2, end2):
    return max(start1, start2) <= min(end1, end2)

# Вычисление времени окончания маршрута
def calculate_route_end(start_time, route_duration):
    full_datetime = datetime.combine(datetime.today(), start_time) + route_duration
    return full_datetime.time()

# Генерация времени маршрутов
def generate_route_times():
    route_times = []
    for start_hour, end_hour in peak_hours:
        current_time = datetime.strptime(f"{start_hour}:00", "%H:%M")
        while current_time.hour < end_hour:
            route_times.append(current_time.time())
            current_time += traffic_route_time
    for start_hour, end_hour in non_peak_hours:
        current_time = datetime.strptime(f"{start_hour}:00", "%H:%M")
        while current_time.hour < end_hour:
            route_times.append(current_time.time())
            current_time += traffic_route_time
    return route_times

# Проверка соблюдения условий для водителей типа A
def validate_driver_A_schedule(schedule):
    for driver, routes in schedule.items():
        work_time = timedelta()
        for start, end in routes:
            route_duration = datetime.combine(datetime.today(), end) - datetime.combine(datetime.today(), start)
            work_time += route_duration
            if work_time > shift_duration_A - timedelta(hours=1):  # Учитываем час на обед
                return False
    return True

# Проверка условий для водителей типа B
def validate_driver_B_schedule(schedule):
    for driver, routes in schedule.items():
        for i in range(1, len(routes)):
            prev_end = routes[i-1][1]
            curr_start = routes[i][0]
            break_duration = datetime.combine(datetime.today(), curr_start) - datetime.combine(datetime.today(), prev_end)
            if break_duration < timedelta(minutes=15):
                return False
    return True

# Функция оценки пригодности
def fitness(schedule, driver_type):
    penalties = 0
    for driver, routes in schedule.items():
        for i in range(len(routes)):
            for j in range(i + 1, len(routes)):
                if is_time_overlap(
                    routes[i][0], routes[i][1], routes[j][0], routes[j][1]
                ):
                    penalties += 1
    if driver_type == "A" and not validate_driver_A_schedule(schedule):
        penalties += 10
    if driver_type == "B" and not validate_driver_B_schedule(schedule):
        penalties += 10
    return -penalties

# Создание популяции
def create_population(driver_list):
    population = []
    for _ in range(population_size):
        schedule = {driver: [] for driver in driver_list}
        for _ in range(num_routes):
            driver = random.choice(driver_list)
            start_time = random.choice(route_times)
            end_time = calculate_route_end(start_time, traffic_route_time)
            schedule[driver].append((start_time, end_time))
        population.append(schedule)
    return population

# Скрещивание
def crossover(parent1, parent2, driver_list):
    child = {driver: [] for driver in driver_list}
    for driver in driver_list:
        if random.random() > 0.5:
            child[driver] = parent1[driver]
        else:
            child[driver] = parent2[driver]
    return child

# Мутация
def mutate(schedule, driver_list):
    driver = random.choice(driver_list)
    if schedule[driver]:
        schedule[driver].pop(random.randint(0, len(schedule[driver]) - 1))  # Удаление случайного рейса
    start_time = random.choice(route_times)
    end_time = calculate_route_end(start_time, traffic_route_time)
    schedule[driver].append((start_time, end_time))
    return schedule

# Генетический алгоритм
def genetic_schedule(driver_list, driver_type):
    population = create_population(driver_list)
    for generation in range(max_generations):
        population = sorted(population, key=lambda x: fitness(x, driver_type), reverse=True)
        next_population = population[:10]  # Топ-10 лучших решений
        while len(next_population) < population_size:
            parent1 = random.choice(population[:50])
            parent2 = random.choice(population[:50])
            child = crossover(parent1, parent2, driver_list)
            if random.random() < 0.2:
                child = mutate(child, driver_list)
            next_population.append(child)
        population = next_population
    best_schedule = max(population, key=lambda x: fitness(x, driver_type))
    return best_schedule

# Отображение расписания
def display_schedule(schedule):
    schedule_text.delete(1.0, END)
    for driver, routes in schedule.items():
        schedule_text.insert(END, f"Водитель: {driver}\n")
        for start, end in routes:
            schedule_text.insert(END, f"  Рейс с {start.strftime('%H:%M')} до {end.strftime('%H:%M')}\n")
        schedule_text.insert(END, "\n")

# Генерация расписания для водителей типа A
def generate_schedule_A():
    try:
        global num_routes
        global route_times

        num_routes = int(num_routes_entry.get())
        route_times = generate_route_times()

        if not drivers_A:
            schedule_text.insert(END, "\nНет водителей типа A для создания расписания.\n")
            return

        best_schedule = genetic_schedule(drivers_A, "A")
        display_schedule(best_schedule)
    except ValueError:
        schedule_text.insert(END, "\nОшибка: Введите корректные параметры.\n")

# Генерация расписания для водителей типа B
def generate_schedule_B():
    try:
        global num_routes
        global route_times

        num_routes = int(num_routes_entry.get())
        route_times = generate_route_times()

        if not drivers_B:
            schedule_text.insert(END, "\nНет водителей типа B для создания расписания.\n")
            return

        best_schedule = genetic_schedule(drivers_B, "B")
        display_schedule(best_schedule)
    except ValueError:
        schedule_text.insert(END, "\nОшибка: Введите корректные параметры.\n")

# Пример данных
peak_hours = [(7, 9), (17, 19)]
non_peak_hours = [(6, 7), (9, 17), (19, 3)]
traffic_route_time = timedelta(minutes=70)
drivers_A = ["Driver_A1", "Driver_A2", "Driver_A3"]
drivers_B = ["Driver_B1", "Driver_B2"]
shift_duration_A = timedelta(hours=8)
shift_duration_B = timedelta(hours=24)
max_generations = 50
population_size = 100

# Создание интерфейса
root = tk.Tk()
root.title("Оптимальное расписание (генетического алгоритма)")
root.geometry("600x500")

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

num_routes_entry = tk.Entry(button_frame, width=10)
num_routes_entry.insert(0, "10")
num_routes_entry.pack(pady=5)

schedule_text = Text(root, width=70, height=15)
schedule_text.pack(pady=10)

generate_button_A = Button(button_frame, text="Сгенерировать расписание (Тип A)", command=generate_schedule_A)
generate_button_A.pack(pady=5)

generate_button_B = Button(button_frame, text="Сгенерировать расписание (Тип B)", command=generate_schedule_B)
generate_button_B.pack(pady=5)

root.mainloop()
