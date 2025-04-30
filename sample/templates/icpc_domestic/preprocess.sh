
while read line; do
  line=${line//\'/'\''}  # Replace single quote with typographic single quote
  line=${line//\"/'\"'}  # Replace double quote with typographic double quote
  line=${line//\\</\&lt;}  # Replace \< with &lt;
  line=${line//\\>/\&gt;}  # Replace \> with &gt;
  echo "$line"
done
