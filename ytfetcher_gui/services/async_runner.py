from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from typing import Callable, Generic, Optional, TypeVar

T = TypeVar("T")


class AsyncTaskRunner(Generic[T]):
    """
    Tiện ích thực thi tác vụ blocking trong thread riêng và trả kết quả về Tkinter loop.
    """

    def __init__(self, tk_scheduler: Callable[[int, Callable[[], None]], None], max_workers: int = 2):
        self._scheduler = tk_scheduler
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="ytfetcher-gui")

    def submit(
        self,
        func: Callable[[], T],
        on_success: Callable[[T], None],
        on_error: Callable[[Exception], None],
    ) -> Future:
        future = self._executor.submit(func)

        def _callback(done_future: Future):
            try:
                result = done_future.result()
            except Exception as exc:  # noqa: BLE001
                self._scheduler(0, lambda: on_error(exc))
            else:
                self._scheduler(0, lambda: on_success(result))

        future.add_done_callback(_callback)
        return future

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)

