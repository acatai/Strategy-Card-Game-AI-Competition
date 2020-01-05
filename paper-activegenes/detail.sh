cat $1/detail-*.txt \
  | grep -v '^#' \
  | awk -F '|' '
    function cmp_field(i1, v1, i2, v2) {
      gsub(/ /, "", i1)
      gsub(/ /, "", i2)
      return (i1 < i2) ? -1 : (i1 != i2)
    }

    BEGIN {
      PROCINFO["sorted_in"] = "cmp_field"
    }

    {
      if (1 == NR) {
        for (i = 1; i <= NF; i += 1) {
          printf "%27s|", $i
        }
        printf "\n"
      }

      if (!($1 ~ "^ +$")) {
        gsub(/ /, "", $1)
        nums[$1] += 1
        for (i = 2; i <= NF; i += 1) {
          sum1[$1][i] += $i
          sum2[$1][i] += $i ^ 2
        }
      }
    }

    END {
      for (p in nums) {
        printf "%-27s|", p
        for (i = 2; i <= NF; i += 1) {
          if (sum1[p][i] == 0) {
            printf "                         - |"
          } else {
            printf "             %5.2f ± %5.2f |", sum1[p][i] / nums[p], sqrt((sum2[p][i] - sum1[p][i] ^ 2 / nums[p]) / nums[p])
          }
        }
        printf "\n"
      }
    }
  ' \
  | tee $1/detail.txt
