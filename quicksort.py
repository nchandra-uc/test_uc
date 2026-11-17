def quicksort(items):
    """Return a new list sorted with quicksort. The input list is unchanged."""
    result = list(items)
    _quicksort(result, 0, len(result) - 1)
    return result


def _quicksort(items, low, high):
    if low >= high:
        return
    pivot_index = _partition(items, low, high)
    _quicksort(items, low, pivot_index - 1)
    _quicksort(items, pivot_index + 1, high)


def _partition(items, low, high):
    """Lomuto partition: last element is the pivot.

    Values less than the pivot move left; greater-or-equal values stay right.
    """
    pivot = items[high]
    i = low
    for j in range(low, high):
        if items[j] < pivot:
            items[i], items[j] = items[j], items[i]
            i += 1
    items[i], items[high] = items[high], items[i]
    return i


if __name__ == "__main__":
    sample = [3, 1, 4, 1, 5, 9, 2, 6]
    print(quicksort(sample))
