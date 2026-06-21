#!/etc/profiles/per-user/tomasr/bin/zsh

set -euo pipefail

DIR="${1:-.}"

find "$DIR" -maxdepth 1 -type f | while read -r file; do
    filename=$(basename "$file")

    if [[ "$filename" == *.* ]]; then
        ext=".${filename##*.}"
    else
        ext=""
    fi

    date=$(date -d "@$(stat -c %Y "$file")" +%F)

    newname="${date}${ext}"

    n=1
    while [[ -e "$DIR/$newname" && "$filename" != "$newname" ]]; do
        newname="${date}_$n${ext}"
        ((n++))
    done

    mv -- "$file" "$DIR/$newname"
done
