import random
import time
from collections import deque

user_requests = {}


class SlidingWindowRateLimiter:
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        self.user_requests = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        if user_id not in self.user_requests:
            return

        while self.user_requests[user_id] and (
            self.user_requests[user_id][0] <= (current_time - self.window_size)
        ):
            self.user_requests[user_id].popleft()

        if len(self.user_requests[user_id]) == 0:
            print("del")
            del self.user_requests[user_id]

    def can_send_message(self, user_id: str) -> bool:
        if (
            user_id in self.user_requests
            and len(self.user_requests[user_id]) >= self.max_requests
        ):
            print(f"Stop message from user: {user_id}")
            return False
        return True

    def record_message(self, user_id: str) -> bool:
        start_time = time.time()
        self._cleanup_window(user_id, start_time)
        if not self.can_send_message(user_id):
            return False
        else:
            self.user_requests.setdefault(user_id, deque()).append(start_time)
            return True

    def time_until_next_allowed(self, user_id: str) -> float:
        if user_id in self.user_requests and (
            self.user_requests[user_id][0] <= time.time() + self.window_size
        ):
            res = self.user_requests[user_id][0] - time.time() + self.window_size
            return res


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
