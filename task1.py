import random
import time
from typing import List, Tuple, Any


class Node:
    def __init__(self, key, value):
        self.data = (key, value)
        self.next = None
        self.prev = None


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def push(self, key, value):
        new_node = Node(key, value)
        new_node.next = self.head
        if self.head:
            self.head.prev = new_node
        else:
            self.tail = new_node
        self.head = new_node
        return new_node

    def remove(self, node):
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        node.prev = None
        node.next = None

    def move_to_front(self, node):
        if node != self.head:
            self.remove(node)
            node.next = self.head
            self.head.prev = node
            self.head = node

    def remove_last(self):
        if self.tail:
            last = self.tail
            self.remove(last)
            return last
        return None


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.list = DoublyLinkedList()

    def get(self, key):
        if key in self.cache:
            node = self.cache[key]
            self.list.move_to_front(node)
            return node.data[1]
        return -1

    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.data = (key, value)
            self.list.move_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                last = self.list.remove_last()
                if last:
                    del self.cache[last.data[0]]
            new_node = self.list.push(key, value)
            self.cache[key] = new_node

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


def range_sum_no_cache(array: List[int], left: int, right: int) -> int:
    return sum(array[left : right + 1])


def update_no_cache(array: List[int], index: int, value: int):
    array[index] = value


LRU_CAPACITY = 1000
cache_instance = LRUCache(LRU_CAPACITY)


def range_sum_with_cache(array: List[int], left: int, right: int) -> int:
    key = (left, right)

    result = cache_instance.get(key)

    if result != -1:
        return result

    calculated_sum = sum(array[left : right + 1])

    cache_instance.put(key, calculated_sum)

    return calculated_sum


def update_with_cache(array: List[int], index: int, value: int):
    """Оновлює масив та інвалідує кеш."""

    array[index] = value

    cache_instance.invalidate_by_index(index)


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


def run_test(
    array: List[int], queries: List[Tuple[str, Any, Any]], use_cache: bool
) -> float:
    """Виконує всі запити та вимірює загальний час."""

    if use_cache:
        range_func = range_sum_with_cache
        update_func = update_with_cache
    else:
        range_func = range_sum_no_cache
        update_func = update_no_cache

    start_time = time.time()

    temp_array = array[:]

    for query in queries:
        op = query[0]

        if op == "Range":
            left, right = query[1], query[2]
            range_func(temp_array, left, right)

        elif op == "Update":
            index, value = query[1], query[2]
            update_func(temp_array, index, value)

    end_time = time.time()
    return end_time - start_time


if __name__ == "__main__":
    N = 100_000
    Q = 50_000

    initial_array = [random.randint(1, 100) for _ in range(N)]

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
    time_with_cache = run_test(array_for_cache, all_queries, use_cache=True)

    # --- ВИВЕДЕННЯ РЕЗУЛЬТАТІВ ---

    print("\n" + "=" * 40)
    print(" РЕЗУЛЬТАТИ ПОРІВНЯННЯ ПРОДУКТИВНОСТІ")
    print("=" * 40)

    if time_with_cache < time_no_cache:
        speedup = time_no_cache / time_with_cache
        speedup_text = f" (прискорення ×{speedup:.2f})"
    else:
        speedup_text = " (прискорення не виявлено)"

    print(f"Без кешу : {time_no_cache:8.2f} c")
    print(f"LRU-кеш : {time_with_cache:8.2f} c {speedup_text}")

    print("\n--- Додаткова інформація ---")
    update_count = sum(1 for q in all_queries if q[0] == "Update")
    range_count = Q - update_count
    print(f"Загальна кількість запитів Range: {range_count}")
    print(f"Загальна кількість запитів Update: {update_count}")
