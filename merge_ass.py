#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def time_to_seconds(t):
    """ASS 时间字符串 -> 秒数"""
    h, m, s = t.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)

def parse_ass_file(filepath):
    """
    解析 ASS 文件，返回：
        header: [Events] 之前的所有行（包含 [Script Info] 和 [V4+ Styles]）
        first_style_name: 第一个样式名
        dialogues: 所有 Dialogue 行解析后的字典列表（包含 _start_sec）
    """
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    # 找到 [Events] 的位置
    events_index = -1
    for i, line in enumerate(lines):
        if line.strip() == '[Events]':
            events_index = i
            break

    if events_index == -1:
        raise ValueError(f"{filepath} 中没有找到 [Events] 节")

    # 头部 = [Events] 之前的所有行（不含 [Events] 本身）
    header = lines[:events_index]

    # 提取第一个样式名
    first_style_name = None
    for line in header:
        if line.startswith('Style:'):
            # Style: name, ...
            parts = line.split(':', 1)[1].split(',')
            if parts:
                first_style_name = parts[0].strip()
                break
    if not first_style_name:
        first_style_name = 'Default'   # 容错

    # 解析 Events 部分
    event_format = None
    dialogues = []
    for line in lines[events_index:]:
        line = line.rstrip('\n')
        if not line:
            continue
        if line.startswith('Format:'):
            event_format = [x.strip() for x in line.split(':', 1)[1].split(',')]
        elif line.startswith('Dialogue:'):
            if event_format is None:
                continue
            parts = line.split(':', 1)[1].split(',', len(event_format)-1)
            if len(parts) == len(event_format):
                ev_dict = dict(zip(event_format, parts))
                start_str = ev_dict.get('Start', '').strip()
                if start_str:
                    ev_dict['_start_sec'] = time_to_seconds(start_str)
                dialogues.append(ev_dict)

    return header, first_style_name, dialogues


def merge_ass_files(file_list, output_path):
    """
    合并多个 ASS 文件：
      - 使用第一个文件的完整头部（[Script Info] + [V4+ Styles] 全部内容）
      - 所有 Dialogue 统一使用第一个样式名
      - 按开始时间排序
    """
    if len(file_list) < 2:
        raise ValueError("至少需要两个文件才能合并")

    # 解析第一个文件
    header, first_style_name, first_dialogues = parse_ass_file(file_list[0])

    all_dialogues = first_dialogues.copy()

    # 解析其余文件，强制使用第一个样式名
    for fpath in file_list[1:]:
        _, _, dialogues = parse_ass_file(fpath)
        for ev in dialogues:
            ev['Style'] = first_style_name
        all_dialogues.extend(dialogues)

    # 按开始时间排序（缺失的放最后）
    all_dialogues.sort(key=lambda x: x.get('_start_sec', 999999))

    # 构建输出
    out_lines = []

    # 1. 写入头部（原样）
    out_lines.extend(header)

    # 2. 写入 [Events] 节
    out_lines.append('[Events]')
    out_lines.append('Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text')

    # 3. 写入所有 Dialogue
    format_keys = ['Layer', 'Start', 'End', 'Style', 'Name', 'MarginL', 'MarginR', 'MarginV', 'Effect', 'Text']
    for ev in all_dialogues:
        values = []
        for key in format_keys:
            if key == 'Style':
                values.append(first_style_name)   # 强制使用第一个样式名
            else:
                values.append(ev.get(key, ''))
        out_lines.append(f"Dialogue: {','.join(values)}")

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out_lines))

    return output_path
