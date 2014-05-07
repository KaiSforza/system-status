cat << EOF
Installing gawk and htop for administrative purposes...
$(apt-get -qq install gawk htop || yum install -y -q gawk htop || \
  echo "...but we don't know the package manager here.")
---------------------------------------------------------------------------
Hostname: $(hostname)
---------------------------------------------------------------------------
$(/sbin/ip  a | awk '/inet/ && !/^global|^lo/ {
                       gsub(/\/.*/,"",$2)
                       if ($NF !~ /link/ && $0  !~ /host/)
                         print $NF "\t" $2
                     }')
---------------------------------------------------------------------------
$(uptime)
$(w -h)
---------------------------------------------------------------------------
$(df -h -x tmpfs -x devtmpfs)

$(df -i -x tmpfs -x devtmpfs)
---------------------------------------------------------------------------
Memory used: $(awk -v memused=$(free -m | awk \ '/buffers\/cache/ {print $3}') \
  'END { \
  memtotal =  $1
  upperlimit = (memtotal * 0.9)
  lowerlimit = (memtotal *  0.7)
  if (lowerlimit < memused && memused <  upperlimit)
    printf("\033[1;33m%dMB\033[0m/%dMB", memused, memtotal)
  else if (memused > upperlimit )
    printf("\033[1;31m%dMB\033[0m/%dMB", memused, memtotal)
  else
    printf("\033[1;32m%dMB\033[0m/%dMB", memused, memtotal)
  }' \
   <<< $(free -m | awk '/^Mem/ {print $2}'))
---------------------------------------------------------------------------
Connection Summary:
$(ss -s | head -2)
---------------------------------------------------------------------------
Connection Concentration:
IN (top 3)::
$(netstat -utn | \
  awk '/^A|ESTABLISHED|TIME_WAIT/ && !/^Ac/ \
       {gsub(".*:", "", $4)
       print $4}' \
       | sort -n | uniq -c | sort -rn | head -3 )
OUT (top 3)::
$(netstat -utn | \
  awk '/^A|ESTABLISHED|TIME_WAIT/ && !/^Ac/ \
       {gsub(".*:", "", $5)
       print $5}' \
       | sort -n | uniq -c | sort -rn | head -3 )
---------------------------------------------------------------------------
$(
ss -plnt | gawk '
  BEGIN { printf("%-15s%-7s%-7s%s\n", "Listening", "Recv-Q", "Send-Q", "Processes") }
  !/Recv-Q/ {
  gsub("users:\\(\\(", "", $6)
  gsub("\\)\\)$", "", $6)
  gsub("\"", "", $6)
  split($6, a, "\\),\\(")
  printf("%-15s%-7s%-7s%s", $4, $2, $3, a[1])
  if(length(a) > 1)
    printf(",  %s", a[2])
  if(length(a) > 2)
    printf(" [and %d more]", length(a))
  printf("\n")
  }'
)
---------------------------------------------------------------------------
EOF
