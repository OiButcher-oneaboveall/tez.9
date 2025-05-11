
import random
import numpy as np

# Şehir listesi
cities = ["Rafineri", "Gürpınar", "Yenikapı", "Selimiye", "İçerenköy", "Tophane", "Alibeyköy", "İstinye"]
num_cities = len(cities)

# Mesafe matrisi (km)
distance_matrix = np.array([
    [0, 66.8, 105, 123, 130, 106, 109, 113],
    [66.8, 0, 40.3, 57.8, 55.4, 41.5, 47.6, 52.1],
    [105, 40.3, 0, 18.5, 23.9, 6, 11.8, 24.8],
    [123, 57.8, 18.5, 0, 13.9, 17.8, 18.3, 19.1],
    [130, 55.4, 23.9, 13.9, 0, 18.5, 30.4, 23.2],
    [106, 41.5, 6, 17.8, 18.5, 0, 8, 21.7],
    [109, 47.6, 11.8, 18.3, 30.4, 8, 0, 14.4],
    [113, 52.1, 24.8, 19.1, 23.2, 21.7, 14.4, 0]
])

# Risk matrisi
risk_matrix = np.array([
    [0, 0.2, 0.4, 0.8, 0.9, 0.5, 0.5, 1.0],
    [0, 0, 0.1, 0.5, 0.4, 0.1, 0.1, 0.5],
    [0, 0.1, 0, 0.2, 0.2, 0.1, 0.1, 0.3],
    [0, 0.5, 0.2, 0, 0.1, 0.2, 0.2, 0.4],
    [0, 0.4, 0.1, 0.1, 0, 0.3, 0.3, 0.5],
    [0, 0.1, 0.1, 0.2, 0.3, 0, 0.1, 0.2],
    [0, 0.1, 0.1, 0.2, 0.3, 0.1, 0, 0.2],
    [0, 0.5, 0.2, 0.4, 0.5, 0.2, 0.2, 0]
])

# Saatlik hız matrisi (km/s)
speed_hourly_matrix = np.array([
    [90, 80, 70, 90, 80, 70, 90, 90, 80, 90, 70, 80],
    [80, 70, 80, 80, 70, 90, 80, 70, 70, 70, 90, 90],
    [70, 60, 90, 70, 90, 90, 70, 90, 90, 90, 90, 70],
    [60, 90, 60, 60, 60, 80, 60, 80, 90, 80, 80, 60],
    [90, 90, 90, 90, 90, 80, 90, 90, 90, 90, 90, 90],
    [80, 90, 80, 90, 70, 70, 80, 90, 70, 80, 80, 70],
    [90, 80, 90, 90, 80, 90, 90, 90, 90, 90, 90, 90],
    [70, 70, 90, 80, 90, 80, 70, 90, 90, 90, 90, 90]
])

service_times = {1: 30, 5: 33, 3: 32, 4: 31, 2: 40, 6: 29, 7: 20}
time_windows = {
    1: (6, 18), 2: (6, 18), 3: (12, 18), 4: (6, 18),
    5: (6, 12), 6: (12, 18), 7: (6, 12)
}

START_HOUR = 6

def get_speed(city_idx, hour_idx):
    idx = hour_idx - START_HOUR
    if (
        isinstance(speed_hourly_matrix, np.ndarray)
        and 0 <= city_idx < speed_hourly_matrix.shape[0]
        and 0 <= idx < speed_hourly_matrix.shape[1]
    ):
        return speed_hourly_matrix[city_idx, idx]
    else:
        return 90  # güvenli sabit hız


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
            hour += minute // 60
            minute %= 60
            break
        else:
            total_min += rem_time
            remaining -= max_dist
            hour += 1
            minute = 0
    return total_min, hour, minute

def evaluate_route(route, max_risk):
    arrival = [None] * num_cities
    departure = [None] * num_cities
    wait_times = [0] * num_cities
    hour = START_HOUR
    minute = 0
    total_dist = total_time = total_risk = 0
    log = []
    arrival[0] = departure[0] = hour * 60

    for i in range(len(route)-1):
        a, b = route[i], route[i+1]
        dist = distance_matrix[a][b]
        travel_min, hour, minute = compute_piecewise_travel_time(a, b, hour, minute, dist)
        total_dist += dist
        total_time += travel_min
        total_risk += risk_matrix[a][b]

        if b != 0:
            earliest, latest = time_windows[b]
            arr_min = hour * 60 + minute
            if arr_min < earliest * 60:
                wait = earliest * 60 - arr_min
                wait_times[b] = wait
                total_time += wait
                minute += wait
                hour += minute // 60
                minute %= 60
            elif arr_min > latest * 60:
                return float('inf'), float('inf'), float('inf'), []

        arrival[b] = hour * 60 + minute
        serv = service_times.get(b, 0)
        total_time += serv
        minute += serv
        hour += minute // 60
        minute %= 60
        departure[b] = hour * 60 + minute

        log.append({
            "from": cities[a], "to": cities[b],
            "arrival": f"{int(arrival[b]//60):02}:{int(arrival[b]%60):02}",
            "departure": f"{int(departure[b]//60):02}:{int(departure[b]%60):02}",
            "service": serv, "wait": wait_times[b]
        })

        if hour >= 18 or total_risk > max_risk:
            return float('inf'), float('inf'), float('inf'), []

    return total_dist, total_time, total_risk, log

def run_ga(pop_size=300, generations=500, max_risk=1.5):
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
