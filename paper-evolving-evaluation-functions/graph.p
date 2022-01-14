set output 'graph.png'
set terminal png enhanced font 'monospace,13' background rgb 'white' size 864,600
set grid mytics xtics lc rgb 'gray' lw 1
set grid mytics ytics lc rgb 'gray' lw 1
set key bottom outside center horizontal samplen 2 spacing 0.75 width -1
set datafile separator ';'
# set xrange [0:72]
# set yrange [30:65]
# set format x ''
# set xtics 18
# set ytics 5
unset border

plot 'graph.data' using 0:8  with lines lc rgb hsv2rgb(0.5 / 4.0, 1, 1) lw 3 title "Linear-weak-op", \
     'graph.data' using 0:3  with lines lc rgb hsv2rgb(0.5 / 4.0, 1, 1) lw 3 title "BinaryTree-weak-op", \
     'graph.data' using 0:14 with lines lc rgb hsv2rgb(0.5 / 4.0, 1, 1) lw 3 title "Tree-weak-op", \
     'graph.data' using 0:10 with lines lc rgb hsv2rgb(1.5 / 4.0, 1, 1) lw 3 title "Linear-strong-op", \
     'graph.data' using 0:4  with lines lc rgb hsv2rgb(1.5 / 4.0, 1, 1) lw 3 title "BinaryTree-strong-op", \
     'graph.data' using 0:16 with lines lc rgb hsv2rgb(1.5 / 4.0, 1, 1) lw 3 title "Tree-strong-op", \
     'graph.data' using 0:11 with lines lc rgb hsv2rgb(2.5 / 4.0, 1, 1) lw 3 title "Linear-progressive", \
     'graph.data' using 0:5  with lines lc rgb hsv2rgb(2.5 / 4.0, 1, 1) lw 3 title "BinaryTree-progressive", \
     'graph.data' using 0:17 with lines lc rgb hsv2rgb(2.5 / 4.0, 1, 1) lw 3 title "Tree-progressive", \
     'graph.data' using 0:9  with lines lc rgb hsv2rgb(3.5 / 4.0, 1, 1) lw 3 title "Linear-from-Linear", \
     'graph.data' using 0:15 with lines lc rgb hsv2rgb(3.5 / 4.0, 1, 1) lw 3 title "Tree-from-Linear"
