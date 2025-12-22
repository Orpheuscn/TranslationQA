# 清理 Git 仓库大文件

## 问题

当前 `.git` 文件夹大小为 **1.6GB**，主要原因是 `labse_onnx/model.onnx` 文件（1.8GB）被提交到了 git 历史中。

## 解决方案

### 方案 1: 使用 BFG Repo-Cleaner（推荐）

BFG 是一个快速、简单的工具，专门用于清理 git 仓库中的大文件。

#### 步骤

1. **安装 BFG**

```bash
# macOS
brew install bfg

# 或者下载 jar 文件
# https://rtyley.github.io/bfg-repo-cleaner/
```

2. **备份仓库**

```bash
cd /Users/patrick/Developing
cp -r 语义对齐 语义对齐_backup
```

3. **运行 BFG 清理**

```bash
cd /Users/patrick/Developing/语义对齐

# 删除所有大于 10MB 的文件
bfg --strip-blobs-bigger-than 10M

# 或者删除特定文件
bfg --delete-files model.onnx
bfg --delete-files tokenizer.json
bfg --delete-files vocab.txt
```

4. **清理 reflog 和垃圾回收**

```bash
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

5. **检查仓库大小**

```bash
du -sh .git
```

6. **强制推送（如果已推送到远程）**

```bash
# ⚠️ 警告：这会重写远程仓库历史
git push --force
```

---

### 方案 2: 使用 git filter-branch

如果没有 BFG，可以使用 git 内置的 `filter-branch` 命令。

#### 步骤

1. **备份仓库**

```bash
cd /Users/patrick/Developing
cp -r 语义对齐 语义对齐_backup
```

2. **删除文件历史**

```bash
cd /Users/patrick/Developing/语义对齐

# 删除 labse_onnx 文件夹的所有历史
git filter-branch --force --index-filter \
  "git rm -rf --cached --ignore-unmatch labse_onnx/model.onnx labse_onnx/tokenizer.json labse_onnx/vocab.txt" \
  --prune-empty --tag-name-filter cat -- --all
```

3. **清理 reflog 和垃圾回收**

```bash
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

4. **检查仓库大小**

```bash
du -sh .git
```

5. **强制推送（如果已推送到远程）**

```bash
# ⚠️ 警告：这会重写远程仓库历史
git push --force
```

---

### 方案 3: 重新开始（最简单）

如果仓库还没有推送到远程，或者不介意丢失历史，可以重新初始化仓库。

#### 步骤

1. **备份当前代码**

```bash
cd /Users/patrick/Developing
cp -r 语义对齐 语义对齐_backup
```

2. **删除 .git 文件夹**

```bash
cd /Users/patrick/Developing/语义对齐
rm -rf .git
```

3. **重新初始化 git**

```bash
git init
git add .
git commit -m "Initial commit - 重新初始化仓库，移除大文件"
```

4. **检查仓库大小**

```bash
du -sh .git
# 应该只有几 MB
```

---

## 预防措施

### 1. 更新 .gitignore

已经更新 `.gitignore` 文件，添加了：

```gitignore
# LaBSE ONNX 模型文件（太大，不应提交到 git）
labse_onnx/
!labse_onnx/.gitkeep

# CSV 输出文件
*.csv
!example.csv
```

### 2. 使用 Git LFS（可选）

如果确实需要版本控制大文件，可以使用 Git Large File Storage (LFS)。

```bash
# 安装 Git LFS
brew install git-lfs
git lfs install

# 跟踪大文件
git lfs track "labse_onnx/*.onnx"
git lfs track "labse_onnx/*.json"
git add .gitattributes
git commit -m "Add Git LFS tracking"
```

### 3. 提交前检查

在提交前检查文件大小：

```bash
# 查看将要提交的文件大小
git ls-files -s | awk '{print $4, $2}' | sort -k2 -n | tail -20

# 或者使用 git-sizer
brew install git-sizer
git-sizer
```

---

## 推荐方案

**对于当前情况，推荐使用方案 3（重新开始）**，因为：

1. ✅ 最简单、最快速
2. ✅ 不需要安装额外工具
3. ✅ 彻底清理所有大文件
4. ✅ 仓库历史不重要（项目还在开发中）

**如果需要保留 git 历史，使用方案 1（BFG）**。

---

## 执行后的预期结果

- `.git` 文件夹大小：从 **1.6GB** 降到 **< 10MB**
- 仓库克隆速度：大幅提升
- GitHub/GitLab 推送：不会因为文件过大而失败

---

## 注意事项

⚠️ **重要警告**：

1. 清理 git 历史会**重写所有提交**，改变 commit hash
2. 如果已经推送到远程，需要**强制推送** (`git push --force`)
3. 其他协作者需要**重新克隆**仓库
4. 务必**先备份**仓库再操作

---

## 参考资料

- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [Git LFS](https://git-lfs.github.com/)
- [Git filter-branch 文档](https://git-scm.com/docs/git-filter-branch)

