#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from datetime import timedelta
from collections import OrderedDict


def time_to_seconds(t):
    """将 ASS 时间字符串 (0:00:00.00) 转换为秒数（浮点数）"""
    h, m, s = t.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def seconds_to_time(sec):
    """将秒数转换为 ASS 时间字符串"""
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:06.2f}".replace('.', ',')


def parse_ass_file(filepath):
    """
    解析 ASS 文件，返回：
        script_info: list of lines (Script Info 部分)
        styles: dict {style_name: dict_of_attributes}
        events: list of dict (每个事件包含所有字段)
    """
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    script_info = []
    styles = {}
    events = []
    current_section = None

    style_format = None   # 解析 Styles 部分的 Format 行
    event_format = None   # 解析 Events 部分的 Format 行

    for line in lines:
        line = line.rstrip('\n')
        if not line:
            continue

        # 检测节标题
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1].strip()
            if current_section == 'Script Info':
                script_info.append(line)   # 保留 [Script Info] 行
            elif current_section == 'V4+ Styles':
                script_info.append(line)   # 保留节标题
            elif current_section == 'Events':
                script_info.append(line)   # 保留节标题
            continue

        # 根据当前节处理
        if current_section == 'Script Info':
            script_info.append(line)
        elif current_section == 'V4+ Styles':
            if line.startswith('Format:'):
                style_format = [x.strip() for x in line.split(':', 1)[1].split(',')]
                script_info.append(line)   # 保留 Format 行
            elif line.startswith('Style:'):
                if style_format is None:
                    continue
                parts = line.split(':', 1)[1].split(',')
                if len(parts) != len(style_format):
                    continue
                style_dict = dict(zip(style_format, parts))
                name = style_dict.get('Name', '').strip()
                if name:
                    styles[name] = style_dict
                script_info.append(line)   # 保留样式行
        elif current_section == 'Events':
            if line.startswith('Format:'):
                event_format = [x.strip() for x in line.split(':', 1)[1].split(',')]
                script_info.append(line)
            elif line.startswith('Dialogue:'):
                if event_format is None:
                    continue
                # 分割：Dialogue: + 逗号分隔，但文本可能含逗号，限制分割次数为 len(event_format)
                parts = line.split(':', 1)[1].split(',', len(event_format)-1)
                if len(parts) != len(event_format):
                    continue
                event_dict = dict(zip(event_format, parts))
                # 转换时间
                start = event_dict.get('Start', '').strip()
                end = event_dict.get('End', '').strip()
                if start and end:
                    event_dict['_start_sec'] = time_to_seconds(start)
                    event_dict['_end_sec'] = time_to_seconds(end)
                events.append(event_dict)

    return script_info, styles, events


def merge_styles(styles_list):
    """
    合并多个样式字典，若重名且属性不同则重命名并返回映射字典 {旧名: 新名}
    返回 (merged_styles, rename_map)
    """
    merged = {}
    rename_map = {}   # 原样式名 -> 新样式名
    # 先收集所有样式，检查重名
    all_names = []
    for styles in styles_list:
        all_names.extend(styles.keys())

    # 统计重名
    name_count = {}
    for name in all_names:
        name_count[name] = name_count.get(name, 0) + 1

    # 对于每个样式，如果重名且属性不同，则重命名
    for styles in styles_list:
        for name, attrs in styles.items():
            if name not in merged:
                merged[name] = attrs
                rename_map[name] = name
            else:
                # 比较属性是否相同
                if merged[name] != attrs:
                    # 重命名
                    new_name = name
                    suffix = 1
                    while new_name in merged or new_name in rename_map.values():
                        new_name = f"{name}_{suffix}"
                        suffix += 1
                    merged[new_name] = attrs
                    rename_map[name] = new_name
    return merged, rename_map


def merge_ass_files(file_list, output_path):
    """
    合并多个 ASS 文件，按时间顺序排序弹幕，生成新的 ASS 文件。
    file_list: 输入文件路径列表
    output_path: 输出文件路径
    """
    if not file_list:
        raise ValueError("文件列表为空")

    # 解析所有文件
    all_script_infos = []
    all_styles = []
    all_events = []
    for f in file_list:
        script_info, styles, events = parse_ass_file(f)
        all_script_infos.append(script_info)
        all_styles.append(styles)
        all_events.append(events)

    # 使用第一个文件的 Script Info 作为基础
    base_script_info = all_script_infos[0] if all_script_infos else []

    # 合并样式
    merged_styles, rename_map = merge_styles(all_styles)

    # 合并事件，并更新样式引用
    merged_events = []
    for events, styles in zip(all_events, all_styles):
        for ev in events:
            # 如果样式名需要重命名，则更新
            style_name = ev.get('Style', '').strip()
            if style_name in rename_map:
                ev['Style'] = rename_map[style_name]
            merged_events.append(ev)

    # 按开始时间排序
    merged_events.sort(key=lambda x: x.get('_start_sec', 0))

    # 构建输出内容
    output_lines = []

    # 写入 Script Info
    for line in base_script_info:
        output_lines.append(line)

    # 写入 Styles 部分（保留 Format 行，然后写入所有样式）
    # 需要找到 Styles 的 Format 行，如果不存在则创建默认
    style_format_line = None
    for line in base_script_info:
        if line.startswith('Format:') and 'Style' in line:
            style_format_line = line
            break
    if not style_format_line:
        # 默认格式
        style_format_line = 'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding'
    output_lines.append(style_format_line)

    # 写入每个样式
    for name, attrs in merged_styles.items():
        # 按 Format 顺序构建行
        format_keys = [x.strip() for x in style_format_line.split(':', 1)[1].split(',')]
        # 确保 Name 是第一个
        ordered_values = []
        for key in format_keys:
            if key in attrs:
                ordered_values.append(attrs[key])
            else:
                # 如果缺失，用空字符串
                ordered_values.append('')
        # 若 attrs 中有额外键（通常没有）
        style_line = f"Style: {','.join(ordered_values)}"
        output_lines.append(style_line)

    # 写入 Events 部分
    # 找到 Event Format 行
    event_format_line = None
    for line in base_script_info:
        if line.startswith('Format:') and 'Layer' in line:
            event_format_line = line
            break
    if not event_format_line:
        event_format_line = 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text'
    output_lines.append(event_format_line)

    # 写入所有 Dialogue
    format_keys = [x.strip() for x in event_format_line.split(':', 1)[1].split(',')]
    for ev in merged_events:
        # 构建顺序列表
        values = []
        for key in format_keys:
            if key == 'Start' or key == 'End':
                # 时间需要转换回字符串（但我们已经存了原始字符串）
                # 因为 ev 中存储的是原始字符串，直接取
                val = ev.get(key, '')
                values.append(val)
            else:
                val = ev.get(key, '')
                values.append(val)
        # 注意：Text 字段可能包含逗号，但我们按顺序拼接，最后一段是 Text，允许逗号
        # 我们直接用逗号连接，但文本内部逗号会被视为分隔符，但 ASS 规范要求文本可以包含逗号，
        # 但解析时我们限制分割次数，生成时直接全部用逗号连接，文本作为最后一个字段，不受影响。
        dialogue_line = f"Dialogue: {','.join(values)}"
        output_lines.append(dialogue_line)

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

    return output_path