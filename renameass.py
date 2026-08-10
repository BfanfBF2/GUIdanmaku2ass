#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

# 使用用户家目录自动适配
SOURCE_DIR = os.path.expanduser("~/danmaku2ass")
TARGET_ROOT = os.path.expanduser("~/Movies")
RULES_FILE = os.path.join(os.path.dirname(__file__), "rules.txt")


def load_rules():
    """从 rules.txt 加载规则，格式：关键词|目标模板"""
    rules = {}
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '|' not in line:
                    continue
                key, tmpl = line.split('|', 1)
                rules[key.strip()] = tmpl.strip()
    return rules


RULES = load_rules()


def get_ep(name):
    """从文件名提取集数，优先匹配'第X话'，其次匹配'_数字'"""
    # 匹配 "第X话"
    m = re.search(r'第\s*(\d+)\s*话', name)
    if m:
        return int(m.group(1))
    # 匹配 "_数字"（例如 _01, _12）
    m = re.search(r'_(\d+)', name)
    if m:
        return int(m.group(1))
    return None


def get_folder_name(template_str):
    """从模板中移除集数占位符，得到文件夹名"""
    folder = re.sub(r"\s-\s\{ep:02d\}", "", template_str)
    folder = re.sub(r"\[\{ep:02d\}\]", "", folder)
    return folder.strip()


def main():
    if not RULES:
        print("⚠️ rules.txt 为空或不存在，没有规则可匹配，跳过移动。")
        return

    # 确保目标根目录存在
    os.makedirs(TARGET_ROOT, exist_ok=True)

    for filename in os.listdir(SOURCE_DIR):
        if not filename.endswith(".ass"):
            continue

        ep_num = get_ep(filename)
        if ep_num is None:
            print(f"跳过（无集数）: {filename}")
            continue

        matched = False
        for keyword, tmpl in RULES.items():
            if keyword in filename:
                new_ass_name = tmpl.format(ep=ep_num) + ".ass"
                anime_folder = get_folder_name(tmpl)
                target_dir = os.path.join(TARGET_ROOT, anime_folder)

                if not os.path.isdir(target_dir):
                    print(f"警告：目标文件夹不存在 {target_dir}，跳过文件 {filename}")
                    matched = True
                    break

                src_path = os.path.join(SOURCE_DIR, filename)
                dst_path = os.path.join(target_dir, new_ass_name)
                os.rename(src_path, dst_path)

                print(f"原文件：{filename}")
                print(f"字幕新名：{new_ass_name}")
                print(f"移入：{target_dir}\n")
                matched = True
                break

        if not matched:
            print(f"无匹配规则，跳过：{filename}")


if __name__ == "__main__":
    main()