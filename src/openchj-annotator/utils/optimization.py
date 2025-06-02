import gc
import sys
from contextlib import contextmanager
from typing import Generator


class MemoryOptimizer:
    @staticmethod
    def optimize_memory():
        gc.collect()

    @staticmethod
    @contextmanager
    def memory_efficient_mode() -> Generator:
        old_threshold = gc.get_threshold()
        gc.set_threshold(700, 10, 10)

        try:
            yield
        finally:
            gc.set_threshold(*old_threshold)
            gc.collect()

    @staticmethod
    def get_memory_usage() -> int:
        import psutil

        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024

    @staticmethod
    def limit_memory(max_memory_mb: int):
        if sys.platform != "win32":  # Unix only
            import resource

            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            resource.setrlimit(resource.RLIMIT_AS, (max_memory_mb * 1024 * 1024, hard))


class ChunkProcessor:
    def __init__(self, chunk_size: int = 1024 * 1024):
        self.chunk_size = chunk_size

    def process_file_in_chunks(self, file_path: str, processor_func):
        with open(file_path, "r", encoding="utf-8") as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break

                if not chunk.endswith(("。", "．", "！", "？", "\n")):
                    next_char = f.read(1)
                    while next_char and next_char not in ("。", "．", "！", "？", "\n"):
                        chunk += next_char
                        next_char = f.read(1)
                    if next_char:
                        chunk += next_char

                yield processor_func(chunk)
