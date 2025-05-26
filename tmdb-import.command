#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$DIR"

python3 -m tmdb-import "https://www.mgtv.com/b/444964/16204816.html"
