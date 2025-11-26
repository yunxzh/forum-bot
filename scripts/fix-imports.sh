#!/bin/bash

echo "修复所有导入路径..."

# 修复 backend/services/ 目录下的文件
for file in backend/services/*.py; do
    if [ -f "$file" ]; then
        echo "修复 $file"
        # 将 from database. 替换为 from backend.database.
        sed -i 's/from database\./from backend.database./g' "$file"
        # 将 from models. 替换为 from backend.models.
        sed -i 's/from models\./from backend.models./g' "$file"
    fi
done

# 修复 backend/api/ 目录下的文件
for file in backend/api/*.py; do
    if [ -f "$file" ]; then
        echo "修复 $file"
        sed -i 's/from database\./from backend.database./g' "$file"
        sed -i 's/from models\./from backend.models./g' "$file"
        sed -i 's/from services\./from backend.services./g' "$file"
    fi
done

# 修复 scheduler/ 目录下的文件
for file in scheduler/*.py; do
    if [ -f "$file" ]; then
        echo "修复 $file"
        sed -i 's/from database\./from backend.database./g' "$file"
        sed -i 's/from models\./from backend.models./g' "$file"
        sed -i 's/from services\./from backend.services./g' "$file"
    fi
done

echo "✅ 导入路径修复完成！"
