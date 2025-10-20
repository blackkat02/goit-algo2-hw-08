import random
from typing import Dict, Any, Deque
import time
from collections import defaultdict, deque

user_requests = {}


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests_queue = deque([])

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        if user_id not in user_requests:
            return

        while (
            len(user_requests[user_id]) > 0
            and user_requests[user_id][0] >= time.time() + current_time
        ):
            self.requests_queue.popleft

        if len(user_requests[user_id]) == 0:
            del user_requests[user_id]

    def can_send_message(self, user_id: str) -> bool:
        print(user_id, "стоп")
        return False

    def record_message(self, user_id: str) -> bool:
        self._cleanup_window(user_id, self.window_size)
        if (
            user_id in user_requests
            and len(user_requests[user_id]) >= self.max_requests
        ):

            # if user_requests[user_id] >= self.max_requests:
            self.can_send_message(user_id)
            return False

        else:
            start_time = time.time()
            user_requests.setdefault(user_id, deque()).append(start_time)
            print(user_requests, self.requests_queue)
            return True

    def time_until_next_allowed(self, user_id: str) -> float:
        if (
            user_id in user_requests
            and (user_requests[user_id][0] + self.max_requests) >= time.time()
        ):
            end_time = user_requests[user_id][0] + self.max_requests
            res = end_time - time.time()
            return res
        else:
            return 0


# Демонстрація роботи
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(
            f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}"
        )
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))


if __name__ == "__main__":
    test_rate_limiter()
