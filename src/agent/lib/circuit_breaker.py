"""Circuit breaker for LLM calls."""
import os
import time
from threading import Lock

FAILURE_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))
RESET_TIMEOUT = float(os.getenv("CIRCUIT_BREAKER_TIMEOUT", "60"))


class CircuitBreaker:
    def __init__(self, threshold: int = FAILURE_THRESHOLD, reset_timeout: float = RESET_TIMEOUT):
        self.threshold = threshold
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time: float | None = None
        self._lock = Lock()

    @property
    def is_open(self) -> bool:
        with self._lock:
            if self.failures < self.threshold:
                return False
            if self.last_failure_time and (time.time() - self.last_failure_time) >= self.reset_timeout:
                self.failures = 0
                return False
            return True

    def record_success(self) -> None:
        with self._lock:
            self.failures = 0

    def record_failure(self) -> None:
        with self._lock:
            self.failures += 1
            self.last_failure_time = time.time()

    def execute(self, fn):
        """Run fn; if circuit is open, raise. On failure, record and re-raise."""
        if self.is_open:
            raise RuntimeError("Circuit breaker is OPEN. LLM calls temporarily disabled.")
        try:
            result = fn()
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise e


_llm_circuit = CircuitBreaker()


def get_llm_circuit() -> CircuitBreaker:
    return _llm_circuit
