#!/usr/bin/env gnuplot
# Plot bench.out (number of molecules vs time). Optional: add another file to compare with GenIce.
set xlabel "Number of molecules"
set ylabel "Time / msec"
set log xy
pl "bench.out" w linesp
# To compare with GenIce: pl "bench.out" w linesp, "/path/to/GenIce/tests/bench.out" w linesp, x
