import time
import random
from collections import OrderedDict
from typing import List, Dict, Tuple, Any, Callable


class LRUCache:
    """
    LRU Cache реалізований за допомогою OrderedDict для O(1) операцій.
    Ключем кешу є кортеж (L, R) - діапазон.
    """

    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: Tuple[int, int]) -> Any:
        """
        Пошук у кеші. Повертає значення або -1 (cache miss).
        """
        if key in self.cache:
            # Cache Hit: Перемістити ключ у кінець (Most Recently Used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return -1

    def put(self, key: Tuple[int, int], value: int):
        """
        Додавання нового значення.
        """
        self.cache[key] = value
        self.cache.move_to_end(key)

        # Керування ємністю
        if len(self.cache) > self.capacity:
            # Видалення найстарішого елемента (Least Recently Used)
            self.cache.popitem(last=False)

    def invalidate_by_index(self, index_to_invalidate: int):
        """
        Інвалідація: Видаляє всі діапазони (L, R) з кешу, що містять index_to_invalidate.
        Це виконується лінійним проходом по ключах.
        """
        keys_to_delete = []
        for L, R in self.cache.keys():
            # Перевіряємо, чи входить змінений індекс у кешований діапазон [L, R]
            if L <= index_to_invalidate <= R:
                keys_to_delete.append((L, R))

        for key in keys_to_delete:
            del self.cache[key]


# === 1. Функції БЕЗ кешування ===


def range_sum_no_cache(array: List[int], left: int, right: int) -> int:
    """Обчислює суму елементів array[left : right + 1] без кешування."""
    # Пряме обчислення суми Python
    return sum(array[left : right + 1])


def update_no_cache(array: List[int], index: int, value: int):
    """Оновлює елемент масиву без кешування."""
    array[index] = value


# === 2. Функції З LRU-кешем ===

# Ініціалізація кешу (глобальна змінна для простоти доступу)
# Ємність K = 1000
LRU_CAPACITY = 1000
cache_instance = LRUCache(LRU_CAPACITY)


def range_sum_with_cache(array: List[int], left: int, right: int) -> int:
    """Обчислює суму з використанням LRU-кешу."""
    key = (left, right)

    # 1. Спроба отримати з кешу (Cache Hit)
    result = cache_instance.get(key)

    if result != -1:
        return result  # Cache Hit

    # 2. Cache Miss: Обчислення
    calculated_sum = sum(array[left : right + 1])

    # 3. Збереження в кеш
    cache_instance.put(key, calculated_sum)

    return calculated_sum


def update_with_cache(array: List[int], index: int, value: int):
    """Оновлює масив та інвалідує кеш."""

    # 1. Оновлення основного масиву
    array[index] = value

    # 2. Інвалідація кешу: видалення всіх діапазонів, що містять змінений індекс
    cache_instance.invalidate_by_index(index)


# === 3. Генератор запитів (Згідно з ТЗ) ===


def make_queries(
    n, q, hot_pool=30, p_hot=0.95, p_update=0.03
) -> List[Tuple[str, Any, Any]]:
    hot = [
        (random.randint(0, n // 2), random.randint(n // 2, n - 1))
        for _ in range(hot_pool)
    ]
    queries = []
    for _ in range(q):
        if random.random() < p_update:  # ~3% запитів — Update
            idx = random.randint(0, n - 1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:  # ~97% — Range
            if random.random() < p_hot:  # 95% — «гарячі» діапазони
                left, right = random.choice(hot)
            else:  # 5% — випадкові діапазони
                left = random.randint(0, n - 1)
                right = random.randint(left, n - 1)
            queries.append(("Range", left, right))
    return queries


# === 4. Функція Виконання та Порівняння ===


def run_test(
    array: List[int], queries: List[Tuple[str, Any, Any]], use_cache: bool
) -> float:
    """Виконує всі запити та вимірює загальний час."""

    # Визначаємо, які функції використовувати
    if use_cache:
        range_func = range_sum_with_cache
        update_func = update_with_cache
    else:
        range_func = range_sum_no_cache
        update_func = update_no_cache

    start_time = time.time()

    # Створюємо копію масиву для безпечного виконання тесту
    temp_array = array[:]

    for query in queries:
        op = query[0]

        if op == "Range":
            left, right = query[1], query[2]
            # Викликаємо функцію, але ігноруємо результат, оскільки нам потрібен лише час
            range_func(temp_array, left, right)

        elif op == "Update":
            index, value = query[1], query[2]
            update_func(temp_array, index, value)

    end_time = time.time()
    return end_time - start_time


if __name__ == "__main__":
    # Параметри згідно з ТЗ
    N = 100_000
    Q = 50_000

    # Створення початкового масиву (строго додатні цілі числа)
    initial_array = [random.randint(1, 100) for _ in range(N)]

    # Генерація запитів
    all_queries = make_queries(N, Q)

    # --- ТЕСТ 1: БЕЗ КЕШУВАННЯ ---
    print("Запуск тестування БЕЗ LRU-кешу...")
    # Потрібно передати копію початкового масиву, оскільки запити Update змінюють його стан
    array_for_no_cache = initial_array[:]
    time_no_cache = run_test(array_for_no_cache, all_queries, use_cache=False)

    # --- ТЕСТ 2: З LRU-КЕШУВАННЯМ ---
    print("Запуск тестування З LRU-кешем...")
    # Потрібно передати іншу копію початкового масиву
    array_for_cache = initial_array[:]
    # Примітка: cache_instance ініціалізується глобально перед викликом
    time_with_cache = run_test(array_for_cache, all_queries, use_cache=True)

    # --- ВИВЕДЕННЯ РЕЗУЛЬТАТІВ ---

    print("\n" + "=" * 40)
    print(" РЕЗУЛЬТАТИ ПОРІВНЯННЯ ПРОДУКТИВНОСТІ")
    print("=" * 40)

    # Розрахунок прискорення
    if time_with_cache < time_no_cache:
        speedup = time_no_cache / time_with_cache
        speedup_text = f" (прискорення ×{speedup:.2f})"
    else:
        speedup_text = " (прискорення не виявлено)"

    print(f"Без кешу : {time_no_cache:8.2f} c")
    print(f"LRU-кеш : {time_with_cache:8.2f} c {speedup_text}")

    print("\n--- Додаткова інформація ---")
    # Щоб оцінити ефективність: підрахунок кількості інвалідацій (Update)
    update_count = sum(1 for q in all_queries if q[0] == "Update")
    range_count = Q - update_count
    print(f"Загальна кількість запитів Range: {range_count}")
    print(f"Загальна кількість запитів Update: {update_count}")
