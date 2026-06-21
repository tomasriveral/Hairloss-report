#!/etc/profiles/per-user/tomasr/bin/zsh bash

DIR="./Images"

for file in "$DIR"/*.png; do
    [ -e "$file" ] || continue

    name=$(basename "$file")

    if [[ ! "$name" =~ ^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])-[0-9]{2}[flt]\.png$ ]]; then
        echo "$name"
    fi
done
