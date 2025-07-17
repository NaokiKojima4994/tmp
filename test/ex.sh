#!/bin/bash

# 比較元ブランチを引数で指定（例: main）
BASE_BRANCH=$1

if [ -z "$BASE_BRANCH" ]; then
    echo "Usage: $0 <base-branch>"
    exit 1
fi

# リモート追跡ブランチ一覧を取得（origin/main除外）
for b in $(git branch -r --format='%(refname:short)' | grep -vE "/$BASE_BRANCH$"); do
    if git cherry "origin/$BASE_BRANCH" "$b" | grep -v '^-' > /dev/null; then
        echo "$b はorigin/$BASE_BRANCHに未マージコミットあり"
    else
        echo "$b はorigin/$BASE_BRANCHに全て含まれている（スカッシュも含む）"
    fi
done
