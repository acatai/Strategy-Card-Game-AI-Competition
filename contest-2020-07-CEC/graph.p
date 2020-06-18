set output 'graph.svg'
set terminal svg enhanced font 'monospace,13' background rgb 'white' size 864,600
set grid mytics xtics lc rgb "gray" lw 1
set grid mytics ytics lc rgb "gray" lw 1
set key bottom outside center horizontal samplen 2 spacing 0.75 width -1
set datafile separator ';'
set yrange [0:100]
set ytics 10
unset border

# Colors based on rating.
set linetype  1 lc rgb hsv2rgb( 5 / 14.0, 0.25, 1)
set linetype  2 lc rgb hsv2rgb( 0 / 14.0, 0.25, 1)
set linetype  3 lc rgb hsv2rgb( 1 / 14.0, 0.25, 1)
set linetype  4 lc rgb hsv2rgb(11 / 14.0, 1, 1)
set linetype  5 lc rgb hsv2rgb(12 / 14.0, 1, 1)
set linetype  6 lc rgb hsv2rgb( 2 / 14.0, 0.25, 1)
set linetype  7 lc rgb hsv2rgb( 4 / 14.0, 0.25, 1)
set linetype  8 lc rgb hsv2rgb( 8 / 14.0, 0.25, 1)
set linetype  9 lc rgb hsv2rgb( 9 / 14.0, 0.25, 1)
set linetype 10 lc rgb hsv2rgb(10 / 14.0, 1, 1)
set linetype 11 lc rgb hsv2rgb( 3 / 14.0, 0.25, 1)
set linetype 12 lc rgb hsv2rgb( 7 / 14.0, 0.25, 1)
set linetype 13 lc rgb hsv2rgb( 6 / 14.0, 0.25, 1)

plot for [col=1:13] 'graph.data' using 0:col with lines lw 3 title columnhead
