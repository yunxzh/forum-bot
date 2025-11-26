#!/bin/bash

echo "=========================================="
echo "  修复所有 Python 文件的导入路径"
echo "=========================================="

# 定义需要修复的目录
DIRS=("backend" "core" "scheduler")

for dir in "${DIRS[@]}"; do
    echo ""
    echo "正在修复 $dir/ 目录..."
    
    # 查找所有 .py 文件
    find "$dir" -name "*.py" -type f | while read -r file; do
        echo "  处理: $file"
        
        # 备份原文件
        cp "$file" "$file.bak"
        
        # 修复导入路径
        sed -i 's/^from database\./from backend.database./g' "$file"
        sed -i 's/^from models\./from backend.models./g' "$file"
        sed -i 's/^from services\./from backend.services./g' "$file"
        sed -i 's/^from api\./from backend.api./g' "$file"
        
        # 修复括号内的导入
        sed -i 's/(database\./(backend.database./g' "$file"
        sed -i 's/(models\./(backend.models./g' "$file"
        sed -i 's/(services\./(backend.services./g' "$file"
        
        # 显示改动
        if ! diff -q "$file" "$file.bak" > /dev/null 2>&1; then
            echo "    ✅ 已修复"
        fi
    done
done

echo ""
echo "=========================================="
echo "  清理备份文件"
echo "=========================================="
find backend core scheduler -name "*.py.bak" -delete

echo ""
echo "=========================================="
echo "  ✅ 导入路径修复完成！"
echo "=========================================="
echo ""
echo "验证修复结果:"
echo "  grep -r \"^from database\\.\" backend/ core/ scheduler/"
echo "  grep -r \"^from models\\.\" backend/ core/ scheduler/"
echo "  grep -r \"^from services\\.\" backend/ core/ scheduler/"
echo ""
