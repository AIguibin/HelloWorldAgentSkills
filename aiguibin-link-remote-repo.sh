#!/bin/bash

# 用法: ./git-link.sh <repo-url> [分支名]
# 示例: ./git-link.sh https://github.com/user/repo.git main

set -e  # 遇到错误立即退出

# ---------- 参数检查 ----------
if [ $# -lt 1 ]; then
    echo "错误：缺少仓库地址 (repo-url)"
    echo "用法: $0 <repo-url> [分支名]"
    echo "示例: $0 https://github.com/user/repo.git master"
    exit 1
fi

REPO_URL="$1"
BRANCH="${2:-master}"   # 默认分支名为 master

echo "==> 当前目录: $(pwd)"
echo "==> 远程仓库: $REPO_URL"
echo "==> 目标分支: $BRANCH"

# ---------- 初始化 Git（如需要） ----------
if [ -d ".git" ]; then
    echo "==> 目录已是 Git 仓库，将复用现有 .git"
else
    echo "==> 初始化 Git 仓库"
    git init
fi

# ---------- 设置远程仓库 origin ----------
# 检查是否已存在 origin 远程
if git remote | grep -q "^origin$"; then
    CURRENT_URL=$(git remote get-url origin)
    if [ "$CURRENT_URL" != "$REPO_URL" ]; then
        echo "==> 更新 origin 地址: $CURRENT_URL -> $REPO_URL"
        git remote set-url origin "$REPO_URL"
    else
        echo "==> origin 地址已正确，无需更改"
    fi
else
    echo "==> 添加远程仓库 origin"
    git remote add origin "$REPO_URL"
fi

# ---------- 确保本地分支名为指定分支 ----------
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || echo "")
if [ -n "$CURRENT_BRANCH" ] && [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    echo "==> 当前分支为 $CURRENT_BRANCH，将重命名为 $BRANCH"
    git branch -M "$BRANCH"
elif [ -z "$CURRENT_BRANCH" ]; then
    # 刚初始化的仓库可能没有分支，创建一个孤立分支
    echo "==> 创建分支 $BRANCH"
    git checkout --orphan "$BRANCH" 2>/dev/null || git branch "$BRANCH"
    git checkout "$BRANCH" 2>/dev/null || true
fi

# ---------- 添加并提交本地文件 ----------
echo "==> 添加当前目录所有文件到 Git"
git add .

# 检查是否有待提交的更改
if git diff --cached --quiet; then
    echo "==> 没有需要提交的文件（可能已经提交过）"
else
    echo "==> 创建初始提交"
    git commit -m "Initial commit from local folder"
fi

# ---------- 拉取远程内容（允许无关历史） ----------
# 先检查远程仓库是否有该分支（避免空仓库时 pull 报错）
if git ls-remote --heads origin "$BRANCH" | grep -q "refs/heads/$BRANCH"; then
    echo "==> 远程已存在分支 $BRANCH，将拉取并合并（允许无关历史）"
    # 使用 --allow-unrelated-histories 合并，不使用 rebase 以避免复杂冲突
    if ! git pull origin "$BRANCH" --allow-unrelated-histories --no-rebase; then
        echo "错误：拉取时发生合并冲突，请手动解决后执行 'git push -u origin $BRANCH'"
        exit 2
    fi
else
    echo "==> 远程仓库尚无分支 $BRANCH，跳过拉取步骤"
fi

# ---------- 推送到远程仓库 ----------
echo "==> 推送到远程仓库（建立追踪关系）"
git push -u origin "$BRANCH"

echo "✅ 完成！本地目录已成功关联到 $REPO_URL 的 $BRANCH 分支"