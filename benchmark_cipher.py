import timeit
import sys
from cipher import decode_flexible_error_reporting

# Inputs to trigger the target code paths
# Ambiguity path (Line 156)
ambiguity_input = "Nidoking Geodude Shroomish Nidoking " * 250
# Error path (Line 164)
error_input = "Seaking " * 250

def benchmark():
    decode_flexible_error_reporting(ambiguity_input)
    decode_flexible_error_reporting(error_input)

if __name__ == "__main__":
    iterations = 1000
    repeats = 5
    print(f"Running benchmark with {iterations} iterations, {repeats} repeats...")
    t = timeit.Timer(benchmark)
    results = t.repeat(repeat=repeats, number=iterations)

    avg_time = sum(results) / (repeats * iterations)
    min_time = min(results) / iterations

    print(f"Average time per call: {avg_time:.6f} s")
    print(f"Minimum time per call: {min_time:.6f} s")
