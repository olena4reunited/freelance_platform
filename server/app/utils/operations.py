def time_incrementing(time_prev: int = 0, time_s: int = 1) -> tuple[int]:
    return (time_s, time_prev + time_s)
