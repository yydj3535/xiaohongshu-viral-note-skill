#!/usr/bin/env python3
"""小红书笔记自检打分：0-100 分，低于 85 分需修改重跑。"""
import re
import sys

BANNED = ["最", "第一", "首选", "顶级", "极致", "100%有效", "保证", "根治", "根除",
          "治疗", "治愈", "药效", "临床", "保本", "稳赚", "高回报", "零风险",
          "微信号", "加V", "加v", "私聊我买"]
INTERACTIVE_HINTS = ["评论区", "告诉我", "你们", "想看", "收藏", "点赞", "？", "?"]


def main(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    score = 100
    issues = []
    def deduct(points, msg):
        nonlocal score
        score -= points
        issues.append(f"-{points}分 {msg}")
    m = re.search(r"标题[:：]\s*(.+)", text)
    if not m:
        deduct(20, "未找到标题行")
    else:
        title = m.group(1).strip()
        if len(title) > 20:
            deduct(10, f"标题 {len(title)} 字，超过 20 字上限")
    body = re.sub(r"标题[:：].*\n?", "", text)
    body = re.sub(r"#\S+", "", body)
    body_len = len(re.sub(r"\s+", "", body))
    if body_len < 400:
        deduct(10, f"正文约 {body_len} 字，偏短（建议 400–800 字）")
    elif body_len > 900:
        deduct(5, f"正文约 {body_len} 字，偏长")
    tags = re.findall(r"#(\S+)", text)
    if len(tags) < 5:
        deduct(10, f"话题标签仅 {len(tags)} 个，建议 5–8 个")
    if not any(h in text for h in INTERACTIVE_HINTS):
        deduct(15, "未检测到互动引导句，必须补上")
    hits = [w for w in BANNED if w in text]
    if hits:
        deduct(30, f"命中违禁词：{', '.join(hits)}")
    if "封面文案" not in text:
        deduct(5, "缺少封面文案备选")
    score = max(score, 0)
    print(f"得分：{score} / 100")
    if issues:
        print("扣分项：")
        for i in issues:
            print(i)
    else:
        print("全部通过，无扣分项。")
    print("结论：" + ("可交付" if score >= 85 else "低于 85 分，修改后重新打分"))
    return 0 if score >= 85 else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
