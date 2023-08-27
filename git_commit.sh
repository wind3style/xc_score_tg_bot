#!/bin/bash

./ver_manager.py -a next_commit
git add version.txt

./ver_manager.py -a modify_py -s bin/xc_score_tg_bot.py
git add *

VER="`./ver_manager.py -a get_version_for_git`"
TEXT=""
END=""
MSG="$VER$TEXT$END"

echo "git commit -e -m $MSG"
git commit -e -m "$MSG"

git tag `./ver_manager.py -a get_version_for_git`

git push
git push --tags