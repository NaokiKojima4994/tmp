#!/bin/bash

# 対象ディレクトリ（スペース区切りで指定）
DIRS="repo1 repo2 repo3"
# 対象ベースブランチ（スペース区切りで指定）
BASE_BRANCHES="main develop release"

for dir in $DIRS; do
  echo "=== ディレクトリ: $dir ==="
  if [ ! -d "$dir" ]; then
    echo "  ディレクトリが存在しません: $dir"
    continue
  fi

  cd "$dir" || continue
  git fetch --all

  for base in $BASE_BRANCHES; do
    echo "--- $dir / $base ---"
    # 比較対象ブランチがあるか確認
    branch_count=$(git branch -r --format='%(refname:short)' | grep -vE "/$base$" | wc -l)
    if [ "$branch_count" -eq 0 ]; then
      echo "（比較対象となるリモートブランチがありません）"
    else
      sh ../ex.sh "$base"
    fi
    echo
  done

  cd - >/dev/null
done
