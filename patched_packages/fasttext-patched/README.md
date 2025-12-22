# FastText (NumPy 2.x Patched Version)

这是FastText的修补版本，修复了与NumPy 2.x的兼容性问题。

## 修复内容

### FastText.py - NumPy 2.x兼容性修复
- **问题**: `np.array(probs, copy=False)`在NumPy 2.x中已被弃用
- **修复**: 将`np.array(probs, copy=False)`改为`np.asarray(probs)`
- **影响**: 修改1行（第239行）

## 修改详情

**原始代码**:
```python
return labels, np.array(probs, copy=False)  # ❌ numpy 2.x已弃用copy参数
```

**修改后代码**:
```python
return labels, np.asarray(probs)  # ✅ 兼容numpy 1.x和2.x
```

## 安装

```bash
pip install fasttext-numpy2-patched-0.9.3.post1.tar.gz
# 或
pip install fasttext_numpy2_patched-0.9.3.post1-py3-none-any.whl
```

## 使用

使用方法与原版FastText完全相同。

## 原始项目

- GitHub: https://github.com/facebookresearch/fastText
- 原始版本: 0.9.3
- 修补版本: 0.9.3.post1

## 许可证

与原项目相同的许可证（MIT License）

## 修补者

Patrick - 2025-12-21

