#!/bin/bash

# ==========================================
# 配置区
# ==========================================

# 强制 Python 子进程无缓冲输出（实时日志）
export PYTHONUNBUFFERED=1

DANMAKU_DIR="$HOME/danmaku2ass"

# 屏蔽UID（多个）
BLOCK_UIDS=(
    "332b440"
    "d1b8e352"
    "4bdefef2"
)

# 默认链接文件（自动适配当前用户）
DEFAULT_LINK_FILE="$HOME/danmaku2ass/links.txt"

# 从环境变量获取每次链接处理后的等待秒数（防风控），若未设置则默认为 0
SLEEP_SECONDS="${SLEEP_SECONDS:-0}"

# ==========================================

if [ ! -d "$DANMAKU_DIR" ]; then
    echo "❌ 未找到目录: $DANMAKU_DIR"
    exit 1
fi

cd "$DANMAKU_DIR" || exit 1

# ========= 提取 BV =========
extract_bvid() {
    local text="$1"

    if [[ "$text" =~ (BV[0-9A-Za-z]+) ]]; then
        echo "${BASH_REMATCH[1]}"
        return
    fi

    if [[ "$text" =~ av([0-9]+) ]]; then
        local avid="${BASH_REMATCH[1]}"
        curl -s "https://api.bilibili.com/x/web-interface/view?aid=$avid" | \
        python3 -u -c "import sys,json;print(json.load(sys.stdin)['data']['bvid'])" 2>/dev/null
        return
    fi

    if [[ "$text" =~ b23.tv ]]; then
        local final_url
        final_url=$(curl -Ls -o /dev/null -w "%{url_effective}" "$text")
        extract_bvid "$final_url"
        return
    fi

    echo ""
}

# ========= 提取 EP =========
extract_epid() {
    local text="$1"

    if [[ "$text" =~ ep([0-9]+) ]]; then
        echo "${BASH_REMATCH[1]}"
        return
    fi

    echo ""
}

# ========= UID过滤 =========
filter_blocked_uid() {
    local xmlfile="$1"

    python3 -u - "$xmlfile" "${BLOCK_UIDS[@]}" <<'PY'
import sys,re

xmlfile=sys.argv[1]
block=set(sys.argv[2:])

with open(xmlfile,'r',encoding='utf-8',errors='ignore') as f:
    data=f.read()

removed=0

pattern=re.compile(r'<d p="([^"]+)">(.*?)</d>',re.S)

def repl(m):
    global removed
    p=m.group(1).split(',')

    if len(p)>=7 and p[6] in block:
        removed+=1
        return ''
    return m.group(0)

newdata=pattern.sub(repl,data)

with open(xmlfile,'w',encoding='utf-8') as f:
    f.write(newdata)

print(f"🚫 已屏蔽 {removed} 条弹幕")
PY
}

# ========= 单任务 =========
process_single() {
    local INPUT="$1"

    echo
    echo "========================================"
    echo "🎬 正在处理：$INPUT"
    echo "========================================"

    local EP_ID
    EP_ID=$(extract_epid "$INPUT")

    local CID TITLE

    if [[ -n "$EP_ID" ]]; then
        echo "🔍 番剧 EP: $EP_ID"

        local INFO
        INFO=$(curl -s "https://api.bilibili.com/pgc/view/web/season?ep_id=$EP_ID")

        CID=$(echo "$INFO" | python3 -u -c "
import sys,json
try:
 d=json.load(sys.stdin)
 for ep in d['result']['episodes']:
  if str(ep['ep_id'])=='$EP_ID':
   print(ep['cid']);break
except:
 print('')
")

        TITLE=$(echo "$INFO" | python3 -u -c "
import sys,json,re
try:
 d=json.load(sys.stdin)
 season=d['result']['title']
 epi=''
 for ep in d['result']['episodes']:
  if str(ep['ep_id'])=='$EP_ID':
   epi=ep['title'];break
 print(re.sub(r'[\\\\/:*?\"<>|]','_',season+'_'+epi))
except:
 print('bilibili_anime')
")
    else
        local BVID
        BVID=$(extract_bvid "$INPUT")

        if [[ -z "$BVID" ]]; then
            echo "❌ 无法解析链接"
            return
        fi

        echo "✅ BV: $BVID"

        local JSON
        JSON=$(curl -s "https://api.bilibili.com/x/web-interface/view?bvid=$BVID")

        CID=$(echo "$JSON" | python3 -u -c "
import sys,json
try:
 print(json.load(sys.stdin)['data']['cid'])
except:
 print('')
")

        TITLE=$(echo "$JSON" | python3 -u -c "
import sys,json,re
try:
 t=json.load(sys.stdin)['data']['title']
 print(re.sub(r'[\\\\/:*?\"<>|]','_',t))
except:
 print('bilibili_video')
")
    fi

    if [[ -z "$CID" ]]; then
        echo "❌ 获取CID失败"
        return
    fi

    echo "📺 CID: $CID"
    echo "📝 标题: $TITLE"

    local TMP_XML
    TMP_XML=$(mktemp)

    echo "⬇️ 下载弹幕..."

    curl -L -s \
        -A "Mozilla/5.0" \
        -H "Referer: https://www.bilibili.com" \
        --compressed \
        -o "$TMP_XML" \
        "https://api.bilibili.com/x/v1/dm/list.so?oid=$CID"

    echo "🔍 过滤UID..."
    filter_blocked_uid "$TMP_XML"

    echo "🎨 转换ASS..."

    python3 -u danmaku2ass.py \
        -o "${TITLE}.ass" \
        -s 1920x1080 \
        -fs 30 \
        -dm 30 \
        -ds 10 \
        -p 540 \
        -r \
        "$TMP_XML"

    rm -f "$TMP_XML"

    echo "✅ 完成：${TITLE}.ass"
}

# ========= TXT入口 =========
LINK_FILE="${1:-$DEFAULT_LINK_FILE}"

if [[ ! -f "$LINK_FILE" ]]; then
    echo "❌ 找不到链接文件：$LINK_FILE"
    exit 1
fi

echo "🚀 B站弹幕转换工具（TXT批量+UID屏蔽）"
echo "📄 链接文件: $LINK_FILE"
echo "⏱️  链接间等待秒数: $SLEEP_SECONDS"
echo "========================================"

COUNT=1
while IFS= read -r LINK || [[ -n "$LINK" ]]; do
    [[ -z "$LINK" ]] && continue
    echo
    echo "===== 第 $COUNT 个任务 ====="
    process_single "$LINK"
    COUNT=$((COUNT+1))
    # 使用可配置的等待时间（防风控）
    sleep "$SLEEP_SECONDS"
done < "$LINK_FILE"

echo "🎉 弹幕下载与转换全部完成"