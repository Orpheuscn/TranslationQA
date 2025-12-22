#!/usr/bin/env python3
"""
下载 LaBSE ONNX 模型文件

使用方法:
    python download_models.py
"""

import os
import sys
from pathlib import Path

def check_existing_files():
    """检查已存在的模型文件"""
    labse_dir = Path("labse_onnx")
    files = {
        'model.onnx': None,
        'tokenizer.json': None,
        'vocab.txt': None
    }
    
    print("🔍 检查现有模型文件...")
    all_exist = True
    
    for filename in files.keys():
        filepath = labse_dir / filename
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            files[filename] = size_mb
            print(f"  ✅ {filename}: {size_mb:.2f} MB")
        else:
            files[filename] = None
            print(f"  ❌ {filename}: 缺失")
            all_exist = False
    
    return all_exist, files

def download_from_huggingface():
    """从 Hugging Face 下载模型文件"""
    try:
        from huggingface_hub import hf_hub_download
        import shutil
    except ImportError:
        print("\n❌ 缺少 huggingface-hub 库")
        print("请先安装: pip install huggingface-hub")
        return False
    
    labse_dir = Path("labse_onnx")
    labse_dir.mkdir(exist_ok=True)
    
    files_to_download = [
        ("onnx/model.onnx", "model.onnx", "ONNX 模型"),
        ("tokenizer.json", "tokenizer.json", "分词器配置"),
        ("vocab.txt", "vocab.txt", "词汇表")
    ]
    
    print("\n📥 开始从 Hugging Face 下载模型文件...")
    print("⏳ 这可能需要几分钟时间，请耐心等待...\n")
    
    for hf_path, local_name, description in files_to_download:
        print(f"正在下载 {description} ({local_name})...")
        try:
            downloaded_path = hf_hub_download(
                repo_id="sentence-transformers/LaBSE",
                filename=hf_path,
                cache_dir=".cache"
            )
            
            target_path = labse_dir / local_name
            shutil.copy(downloaded_path, target_path)
            
            size_mb = target_path.stat().st_size / (1024 * 1024)
            print(f"  ✅ 下载完成: {size_mb:.2f} MB\n")
            
        except Exception as e:
            print(f"  ❌ 下载失败: {e}\n")
            return False
    
    return True

def main():
    print("=" * 60)
    print("LaBSE ONNX 模型下载工具")
    print("=" * 60)
    print()
    
    # 检查现有文件
    all_exist, files = check_existing_files()
    
    if all_exist:
        print("\n✅ 所有模型文件已存在！")
        print("\n如需重新下载，请先删除 labse_onnx/ 文件夹中的文件。")
        return 0
    
    # 询问是否下载
    print("\n是否从 Hugging Face 下载缺失的模型文件？")
    print("⚠️  注意: 模型文件总计约 1.8GB，下载可能需要较长时间。")
    
    response = input("\n继续下载？(y/n): ").strip().lower()
    
    if response != 'y':
        print("\n❌ 已取消下载。")
        print("\n你也可以手动下载模型文件，详见 labse_onnx/README.md")
        return 1
    
    # 下载模型
    success = download_from_huggingface()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 所有模型文件下载完成！")
        print("=" * 60)
        
        # 再次检查
        print()
        check_existing_files()
        
        print("\n现在可以运行应用了:")
        print("  python app.py")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ 模型下载失败")
        print("=" * 60)
        print("\n请尝试以下方法:")
        print("1. 检查网络连接")
        print("2. 使用代理或 VPN")
        print("3. 手动下载，详见 labse_onnx/README.md")
        return 1

if __name__ == "__main__":
    sys.exit(main())

