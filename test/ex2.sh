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
    # ex.shを同じディレクトリに配置しておくか、絶対パスに変更してください
    sh ../ex.sh "$base"
    echo
  done

  cd - >/dev/null
done
