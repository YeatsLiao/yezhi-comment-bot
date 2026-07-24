#!/bin/bash

# 迁移脚本：将文章、封面图、配图按文章分文件夹整理

DATA_DIR="/workspace/yeats-comment-bot/data"

# 1. 处理文章文件
for article in "$DATA_DIR"/comment_*.md; do
    if [ -f "$article" ]; then
        # 提取文件名（不含路径和扩展名）
        basename=$(basename "$article" .md)
        
        # 创建文章文件夹
        mkdir -p "$DATA_DIR/$basename"
        
        # 移动文章到文件夹并重命名为 article.md
        mv "$article" "$DATA_DIR/$basename/article.md"
        
        echo "✓ 迁移文章: $basename/article.md"
    fi
done

# 2. 处理封面图
cd "$DATA_DIR/covers" || exit 1
for cover in cover_*.jpg; do
    if [ -f "$cover" ]; then
        # 提取基础名称（如 cover_20260528_xiaohongshu_wc）
        base=$(echo "$cover" | sed 's/\.jpg$//')
        
        # 提取日期和关键词部分（去掉 cover_ 前缀和版本号）
        folder=$(echo "$base" | sed 's/^cover_//' | sed 's/_v[0-9]*$//')
        
        # 检查对应的文章文件夹是否存在
        if [ -d "$DATA_DIR/comment_$folder" ]; then
            # 移动封面图
            mv "$cover" "$DATA_DIR/comment_$folder/"
            echo "✓ 迁移封面: $folder/$cover"
        else
            # 尝试匹配不带版本号的基础名称
            base_folder=$(echo "$folder" | sed 's/_[^_]*$//')
            if [ -d "$DATA_DIR/comment_$base_folder" ]; then
                mv "$cover" "$DATA_DIR/comment_$base_folder/"
                echo "✓ 迁移封面: $base_folder/$cover"
            else
                echo "⚠ 未找到匹配文件夹: $cover (folder: $folder)"
            fi
        fi
    fi
done

# 3. 处理配图
cd "$DATA_DIR/inline" || exit 1
for inline in *.jpg; do
    if [ -f "$inline" ]; then
        # 提取文章名（如 xhs_article_stadium_crowd -> 20260528_xiaohongshu_wc）
        # 根据命名规则匹配
        if [[ "$inline" == xhs_article_* ]]; then
            # 小红书文章配图
            target_folder="comment_20260528_xiaohongshu_wc"
        else
            # 其他配图，尝试从文件名推断
            target_folder=""
        fi
        
        if [ -n "$target_folder" ] && [ -d "$DATA_DIR/$target_folder" ]; then
            mv "$inline" "$DATA_DIR/$target_folder/"
            echo "✓ 迁移配图: $target_folder/$inline"
        else
            echo "⚠ 未找到匹配文件夹: $inline"
        fi
    fi
done

# 4. 清理空目录
rmdir "$DATA_DIR/covers" 2>/dev/null && echo "✓ 删除空目录: covers"
rmdir "$DATA_DIR/inline" 2>/dev/null && echo "✓ 删除空目录: inline"
rmdir "$DATA_DIR/images" 2>/dev/null && echo "✓ 删除空目录: images"

echo ""
echo "迁移完成！"
echo "新目录结构:"
find "$DATA_DIR" -maxdepth 2 -type d | head -20
