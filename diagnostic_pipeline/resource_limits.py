import os
import resource


def make_process_limiter(
    cpu_seconds: int = 3,
    memory_bytes: int = 512 * 1024 * 1024,
    file_size_bytes: int = 10 * 1024 * 1024,
    nofile: int = 64,
    nproc: int = 64,
):
    def _limit_child() -> None:
        os.setsid()
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        resource.setrlimit(resource.RLIMIT_FSIZE, (file_size_bytes, file_size_bytes))
        resource.setrlimit(resource.RLIMIT_NOFILE, (nofile, nofile))
        resource.setrlimit(resource.RLIMIT_NPROC, (nproc, nproc))
    return _limit_child
