set output 'graph.svg'
set terminal svg enhanced background rgb 'white' size 864,600
set grid mytics xtics lc rgb "gray" lw 1
set grid mytics ytics lc rgb "gray" lw 1
set key bottom outside center horizontal
set datafile separator ';'
set xrange [0:5000]
set yrange [0:100]
set xtics 1000
set ytics 10

# Colors based on rating.
set linetype  1 lc rgb hsv2rgb( 7 / 11.0, 1, 1)
set linetype  2 lc rgb hsv2rgb( 1 / 11.0, 1, 1)
set linetype  3 lc rgb hsv2rgb( 2 / 11.0, 1, 1)
set linetype  4 lc rgb hsv2rgb(11 / 11.0, 1, 1)
set linetype  5 lc rgb hsv2rgb( 3 / 11.0, 1, 1)
set linetype  6 lc rgb hsv2rgb( 6 / 11.0, 1, 1)
set linetype  7 lc rgb hsv2rgb( 9 / 11.0, 1, 1)
set linetype  8 lc rgb hsv2rgb(10 / 11.0, 1, 1)
set linetype  9 lc rgb hsv2rgb( 4 / 11.0, 1, 1)
set linetype 10 lc rgb hsv2rgb( 8 / 11.0, 1, 1)
set linetype 11 lc rgb hsv2rgb( 5 / 11.0, 1, 1)

plot for [col=1:11] 'graph.data' using 0:col with lines lw 2 title columnhead
