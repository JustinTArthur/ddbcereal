from timeit import timeit
print(timeit('isinstance("testing 1234", str)'))
print(timeit('isinstance("testing 1234", (str,))'))

print(timeit('isinstance("testing 1234", bytes)'))
print(timeit('isinstance("testing 1234", (bytes,))'))
