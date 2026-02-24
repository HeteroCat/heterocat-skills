#!/usr/bin/env python3
"""
打包所有 skills 为 .skill 文件
"""

import sys
import zipfile
from pathlib import Path


def package_skill(skill_path, output_dir):
    """
    打包单个 skill 为 .skill 文件

    Args:
        skill_path: skill 文件夹路径
        output_dir: 输出目录

    Returns:
        成功返回 .skill 文件路径，失败返回 None
    """
    skill_path = Path(skill_path).resolve()

    # 验证 skill 文件夹存在
    if not skill_path.exists() or not skill_path.is_dir():
        print(f"❌ 错误: Skill 文件夹不存在: {skill_path}")
        return None

    # 验证 SKILL.md 存在
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ 错误: {skill_path} 中未找到 SKILL.md")
        return None

    # 确定输出路径
    skill_name = skill_path.name
    output_path = Path(output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    skill_filename = output_path / f"{skill_name}.skill"

    # 创建 .skill 文件 (zip 格式)
    try:
        with zipfile.ZipFile(skill_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 遍历 skill 目录
            for file_path in skill_path.rglob('*'):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    # 计算 zip 中的相对路径
                    arcname = file_path.relative_to(skill_path.parent)
                    zipf.write(file_path, arcname)
                    print(f"  添加: {arcname}")

        print(f"✅ 成功打包 skill 到: {skill_filename}\n")
        return skill_filename

    except Exception as e:
        print(f"❌ 创建 .skill 文件时出错: {e}")
        return None


def main():
    # Skills 目录
    skills_dir = Path("/Users/jason/Desktop/heterocat-skills/.claude/skills")
    output_dir = Path("/Users/jason/Desktop/heterocat-skills/dist")

    print("📦 开始打包 skills...\n")

    # 找到所有包含 SKILL.md 的目录
    skill_folders = []
    for skill_md in skills_dir.glob("*/SKILL.md"):
        skill_folders.append(skill_md.parent)

    if not skill_folders:
        print("❌ 未找到任何 skill")
        sys.exit(1)

    print(f"找到 {len(skill_folders)} 个 skills:\n")

    # 打包每个 skill
    success_count = 0
    for skill_folder in sorted(skill_folders):
        print(f"📦 打包: {skill_folder.name}")
        result = package_skill(skill_folder, output_dir)
        if result:
            success_count += 1

    print(f"\n{'='*60}")
    print(f"✅ 成功打包 {success_count}/{len(skill_folders)} 个 skills")
    print(f"📁 输出目录: {output_dir}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
