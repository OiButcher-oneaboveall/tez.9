
import numpy as np
import random

START_HOUR = 6
cities = ["Rafineri", "Gürpınar", "Yenikapı", "Selimiye", "İçerenköy", "Tophane", "Alibeyköy", "İstinye"]
num_cities = len(cities)
distance_matrix = np.random.randint(10, 50, size=(num_cities, num_cities))
risk_matrix = np.random.rand(num_cities, num_cities)
speed_hourly_matrix = np.random.randint(60, 100, size=(num_cities, 12))
service_times = {i: random.randint(5, 15) for i in range(1, num_cities)}
time_windows = {i: (6, 12) if i % 2 == 1 else (12, 18) for i in range(1, num_cities)}

def get_speed(city_idx, hour_idx):
    idx = hour_idx - START_HOUR
    try:
        return speed_hourly_matrix[city_idx][idx]
    except:
        return 90

def compute_piecewise_travel_time(from_city, to_city, hour, minute, distance):
    remaining = distance
    total_min = 0
    while remaining > 0:
        speed = min(get_speed(from_city, hour), get_speed(to_city, hour))
        rem_time = 60 - minute
        max_dist = speed * (rem_time / 60)
        if remaining <= max_dist:
            t = (remaining / speed) * 60
            total_min += t
            minute += t
            hour += int(minute // 60)
            minute %= 60
            break
        else:
            total_min += rem_time
            remaining -= max_dist
            hour += 1
            minute = 0
    return total_min, int(hour), int(minute)

def evaluate_route(route, max_risk=1.5):
    hour, minute = START_HOUR, 0
    total_dist = total_time = total_risk = 0
    log = []
    for i in range(len(route)-1):
        a, b = route[i], route[i+1]
        dist = distance_matrix[a][b]
        travel_min, hour, minute = compute_piecewise_travel_time(a, b, hour, minute, dist)
        total_dist += dist
        total_time += travel_min
        total_risk += risk_matrix[a][b]

        arr_time_min = hour * 60 + minute
        wait = 0
        if b != 0 and b in time_windows:
            earliest, latest = time_windows[b]
            earliest_min, latest_min = earliest * 60, latest * 60
            if arr_time_min < earliest_min:
                wait = earliest_min - arr_time_min
                total_time += wait
                minute += wait
                hour += int(minute // 60)
                minute %= 60
            elif arr_time_min > latest_min:
                return float('inf'), float('inf'), float('inf'), []

        service = service_times.get(b, 0)
        total_time += service
        minute += service
        hour += int(minute // 60)
        minute %= 60

        log.append({
            "from": cities[a],
            "to": cities[b],
            "arrival": f"{int((arr_time_min + wait)//60):02}:{int((arr_time_min + wait)%60):02}",
            "departure": f"{hour:02}:{minute:02}",
            "service": service,
            "wait": wait
        })

        if hour >= 18 or total_risk > max_risk:
            return float('inf'), float('inf'), float('inf'), []

    return total_dist, total_time, total_risk, log

def run_ga(pop_size=50, generations=100, max_risk=1.5):
    def init_population():
        pop = []
        for _ in range(pop_size):
            indiv = list(range(1, num_cities))
            random.shuffle(indiv)
            pop.append([0] + indiv + [0])
        return pop

    def fitness(route):
        _, _, risk, _ = evaluate_route(route, max_risk)
        return float('inf') if risk > max_risk else sum(distance_matrix[route[i]][route[i+1]] for i in range(len(route)-1))

    def selection(pop):
        return min(random.sample(pop, 5), key=fitness)

    def crossover(p1, p2):
        s, e = sorted(random.sample(range(1, len(p1)-1), 2))
        child = [None] * len(p1)
        child[s:e] = p1[s:e]
        pointer = 1
        for g in p2[1:-1]:
            if g not in child:
                while child[pointer] is not None:
                    pointer += 1
                child[pointer] = g
        child[0] = child[-1] = 0
        return child

    def mutate(route, rate=0.02):
        for i in range(1, len(route)-2):
            if random.random() < rate:
                j = random.randint(1, len(route)-2)
                route[i], route[j] = route[j], route[i]

    population = init_population()
    for _ in range(generations):
        new_pop = []
        for _ in range(pop_size):
            p1 = selection(population)
            p2 = selection(population)
            child = crossover(p1, p2)
            mutate(child)
            new_pop.append(child)
        population = new_pop

    valid = [r for r in population if fitness(r) != float('inf')]
    if valid:
        best = min(valid, key=fitness)
        d, t, r, log = evaluate_route(best, max_risk)
        return best, d, t, r, log
    else:
        return None, None, None, None, []
