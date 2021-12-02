
def datetime_range(start, end, delta):
    current = start
    while current < end:
        yield current
        current += delta