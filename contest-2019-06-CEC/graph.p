set output 'graph.svg'
set terminal svg enhanced background rgb 'white' size 960,540
set grid mytics xtics lc rgb "gray" lw 1
set grid mytics ytics lc rgb "gray" lw 1
set key bottom outside center horizontal
set datafile separator ';'
set xrange [0:1750]
set yrange [0:100]
set xtics 250
set ytics 10

plot for [col=1:8] 'graph.data' using 0:col with lines lw 2 title columnhead
