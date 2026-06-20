#!/usr/bin/env python3
"""
Twitter/X Build in Public (BiP) 自动化发布脚本
=============================================
从 statushub-bip-thread-ready.md 读取内容，自动发布线程到 Twitter/X。

用法:
  python scripts/twitter_bip_post.py --day 1 --dry-run       # 预览 Day 1 内容
  python scripts/twitter_bip_post.py --day 1                  # 发布 Day 1 (8-tweet 线程)
  python scripts/twitter_bip_post.py --day 2                  # 发布 Day 2 (单帖)
  python scripts/twitter_bip_post.py --all --dry-run           # 预览所有
  python scripts/twitter_bip_post.py --all                     # 循环发布所有可用日期

环境变量（.env）:
  TWITTER_API_KEY=xxx
  TWITTER_API_SECRET=xxx
  TWITTER_ACCESS_TOKEN=xxx
  TWITTER_ACCESS_SECRET=xxx
  (或) TWITTER_BEARER_TOKEN=xxx

依赖: pip install tweepy
"""

import argparse
import os
import re
import sys
from pathlib import Path

# ── 配置 ───────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
BIP_FILE = PROJECT_DIR.parent / "docs" / "marketing" / "statushub-bip-thread-ready.md"
ENV_FILE = PROJECT_DIR / ".env"

# Fallback if doc path not found
if not BIP_FILE.exists():
    alt = Path(os.environ.get("HOME", "/tmp")) / "projects" / "auto-company_test" / "docs" / "marketing" / "statushub-bip-thread-ready.md"
    if alt.exists():
        BIP_FILE = alt

# ── 内容解析 ───────────────────────────────────────────────────────

def load_env():
    """从 .env 加载环境变量（如果存在）"""
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip())


def parse_day_tweets(markdown_text: str, day_number: int) -> list[dict]:
    """
    从 markdown 中解析指定 Day 的推文列表。

    返回 [{"text": str, "image_hint": str|None, "order": int}, ...]

    Day 1 格式: "### Tweet X/Y" 多推文线程
    Days 2-6 格式: "### Day N" 单推文
    """
    lines = markdown_text.splitlines()

    # 找到 Day N 的起始位置
    if day_number == 1:
        day_pattern = r"^##\s+首条 Build in Public"
    else:
        day_pattern = rf"^###\s+Day\s+{day_number}\b"

    day_start = None
    for i, line in enumerate(lines):
        if re.match(day_pattern, line):
            day_start = i
            break

    if day_start is None:
        return []

    # 找到下一个 Day 的起始位置（或文件结束）
    day_end = len(lines)
    for i in range(day_start + 1, len(lines)):
        # Day 1 内部用 "### Tweet" 不分段, 找 "## 日更管线" 结束
        if day_number == 1:
            if re.match(r"^##\s+日更管线", lines[i]):
                day_end = i
                break
        else:
            if re.match(r"^###\s+Day\s+\d+\b", lines[i]) or re.match(r"^##\s", lines[i]):
                day_end = i
                break

    day_lines = lines[day_start:day_end]

    if day_number == 1:
        return _parse_day1_tweets(day_lines)
    else:
        return _parse_single_tweet_day(day_lines)


def _parse_day1_tweets(day_lines: list[str]) -> list[dict]:
    """解析 Day 1 的多推文线程格式 (### Tweet X/Y)"""
    tweets = []
    current_tweet_lines = []
    current_image_hint = None
    current_order = 0
    in_tweet = False

    for line in day_lines:
        tweet_header = re.match(r"^###\s+Tweet\s+(\d+)(?:/\d+)?\s*$", line)
        if tweet_header:
            # 保存上一个 tweet
            if in_tweet and current_tweet_lines:
                text = _clean_tweet_text(current_tweet_lines)
                if text:
                    tweets.append({
                        "text": text,
                        "image_hint": current_image_hint,
                        "order": current_order,
                    })
            current_tweet_lines = []
            current_image_hint = None
            current_order = int(tweet_header.group(1))
            in_tweet = True
            continue

        if in_tweet:
            # 遇到下一个 ## 或 ### 但不是 Tweet → 结束
            if re.match(r"^#{2,3}\s+", line) and not re.match(r"^###\s+Tweet\s+\d+", line):
                if current_tweet_lines:
                    text = _clean_tweet_text(current_tweet_lines)
                    if text:
                        tweets.append({
                            "text": text,
                            "image_hint": current_image_hint,
                            "order": current_order,
                        })
                current_tweet_lines = []
                current_image_hint = None
                in_tweet = False
                continue

            # 提取图片建议
            img_match = re.match(r"\*\*📸?\s*(建议配图|配图)\s*\*{0,2}\s*:\s*(.+?)\s*(?:\(.*\))?\s*$", line)
            if img_match:
                current_image_hint = img_match.group(2).strip()
                continue

            # 跳过纯分隔线
            if re.match(r"^---+$", line):
                continue
            # 跳过说明行
            if re.match(r"^\s*>?\s*\*\*说明\*\*:", line):
                continue

            current_tweet_lines.append(line)

    # 保存最后一个 tweet
    if in_tweet and current_tweet_lines:
        text = _clean_tweet_text(current_tweet_lines)
        if text:
            tweets.append({
                "text": text,
                "image_hint": current_image_hint,
                "order": current_order,
            })

    tweets.sort(key=lambda t: t["order"])
    return tweets


def _parse_single_tweet_day(day_lines: list[str]) -> list[dict]:
    """解析 Days 2-6 的单推文格式（无 ### Tweet 子标题）"""
    # 跳过第一行（### Day N 标题本身）
    content_lines = day_lines[1:] if day_lines else []

    tweet_lines = []
    image_hint = None

    for line in content_lines:
        # 提取图片建议
        img_match = re.match(r"\*\*📸?\s*(建议配图|配图)\s*\*{0,2}\s*:\s*(.+?)\s*(?:\(.*\))?\s*$", line)
        if img_match:
            image_hint = img_match.group(2).strip()
            continue

        # 跳过纯分隔线
        if re.match(r"^---+$", line):
            continue
        # 跳过空行
        if not line.strip():
            tweet_lines.append("")
            continue

        tweet_lines.append(line)

    text = _clean_tweet_text(tweet_lines)
    if text:
        return [{"text": text, "image_hint": image_hint, "order": 1}]
    return []


def _clean_tweet_text(lines: list[str]) -> str:
    """清理推文文本：去除 blockquote 标记，整理空白"""
    cleaned = []
    for line in lines:
        # 去除 blockquote 前缀
        line = re.sub(r"^>\s?", "", line)
        cleaned.append(line.rstrip())

    text = "\n".join(cleaned).strip()
    # 合并多余空行（保留单空行分段）
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def get_available_days() -> list[int]:
    """返回文件中所有可用的 Day 编号列表"""
    if not BIP_FILE.exists():
        print(f"❌ BiP 文件未找到: {BIP_FILE}")
        return []

    text = BIP_FILE.read_text(encoding="utf-8")
    days = set()

    # Day 1
    if "首条 Build in Public 线程（Day 1）" in text:
        days.add(1)

    # Day 2+
    for match in re.finditer(r"### Day (\d+)", text):
        days.add(int(match.group(1)))

    return sorted(days)


# ── Twitter API ────────────────────────────────────────────────────

def get_twitter_client():
    """创建 Tweepy Client (Twitter API v2)。优先 OAuth 1.0a User Context。"""
    import tweepy

    # 从环境变量加载
    bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")
    api_key = os.environ.get("TWITTER_API_KEY")
    api_secret = os.environ.get("TWITTER_API_SECRET")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_secret = os.environ.get("TWITTER_ACCESS_SECRET")

    if api_key and api_secret and access_token and access_secret:
        # OAuth 1.0a User Context（可发帖）
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
        api_v1 = tweepy.API(auth)
        client_v2 = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_secret=access_secret,
        )
        return client_v2, api_v1
    elif bearer_token:
        # OAuth 2.0 Bearer Token（只读，不能发帖）
        client = tweepy.Client(bearer_token=bearer_token)
        return client, None
    else:
        print("❌ 未找到 Twitter API credentials。请在 .env 中设置：")
        print("   TWITTER_API_KEY=xxx")
        print("   TWITTER_API_SECRET=xxx")
        print("   TWITTER_ACCESS_TOKEN=xxx")
        print("   TWITTER_ACCESS_SECRET=xxx")
        print("   或参考 https://developer.twitter.com/en/docs/authentication/oauth-1-0a")
        return None, None


def post_thread(client_v2, api_v1, tweets: list[dict], dry_run: bool = False) -> list[str]:
    """
    发布推文线程。

    返回发布后的 tweet IDs 列表（dry_run 返回空列表）。
    """
    if not tweets:
        print("   📭 没有需要发布的推文")
        return []

    tweet_ids = []
    first_tweet_id = None

    for i, tweet_data in enumerate(tweets):
        text = tweet_data["text"]
        image_hint = tweet_data["image_hint"]
        order = tweet_data["order"]

        print(f"\n  ── Tweet {order} ──")
        # 处理文本长度（Twitter 限制 280 字符，但 X Premium 允许 4000+ 字符）
        # 保留原样，API 会处理截断
        if dry_run:
            preview = text[:200] + ("..." if len(text) > 200 else "")
            print(f"  📝 {preview}")
            if image_hint:
                print(f"  🖼️ 建议配图: {image_hint}")
            print(f"  📏 长度: {len(text)} chars")
            tweet_ids.append(f"dry-run-{order}")
            continue

        try:
            # 上传媒体（如果 API v1 可用且有配图路径）
            media_ids = []
            api_v1_obj = api_v1
            if image_hint and api_v1_obj and image_hint != "无配图":
                # 尝试从 image_hint 提取文件名
                img_path = _resolve_image_path(image_hint)
                if img_path and img_path.exists():
                    try:
                        media = api_v1_obj.media_upload(str(img_path))
                        media_ids.append(media.media_id)
                        print(f"  🖼️ 已上传配图: {img_path.name}")
                    except Exception as e:
                        print(f"  ⚠️ 配图上传失败: {e}")

            # 发帖
            params = {"text": text}
            if first_tweet_id:
                params["in_reply_to_tweet_id"] = first_tweet_id
            if media_ids:
                params["media_ids"] = media_ids

            response = client_v2.create_tweet(**params)

            if response.data and "id" in response.data:
                tid = response.data["id"]
                if i == 0:
                    first_tweet_id = tid
                tweet_ids.append(tid)
                url = f"https://x.com/user/status/{tid}"
                print(f"  ✅ 已发布: {url}")
            else:
                print(f"  ❌ 发布失败: {response}")
                tweet_ids.append(None)

        except Exception as e:
            print(f"  ❌ 发布异常: {e}")
            tweet_ids.append(None)

    return tweet_ids


def _resolve_image_path(hint: str) -> Path | None:
    """从图片提示中解析出实际的文件路径"""
    # 去除括号内说明
    hint_clean = re.sub(r"\s*\(.*?\)\s*$", "", hint).strip()

    # 检查是否包含路径关键词
    for keyword in ["截图", "screenshot", "截图路径"]:
        if keyword in hint_clean:
            return None

    # 检查 marketing 截图目录
    marketing_dir = BIP_FILE.parent
    screenshots_dir = marketing_dir / "screenshots"

    if screenshots_dir.exists():
        for f in screenshots_dir.iterdir():
            if f.is_file():
                if hint_clean.lower() in f.stem.lower():
                    return f

    # 检查 docs 下各目录
    docs_dir = marketing_dir.parent
    for role_dir in docs_dir.iterdir():
        if role_dir.is_dir():
            for f in role_dir.iterdir():
                if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif"):
                    if hint_clean.lower() in f.stem.lower():
                        return f

    return None


# ── 主入口 ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Twitter/X Build in Public 自动化发布工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--day", "-d",
        type=int,
        choices=range(1, 8),
        help="发布指定 Day 的内容 (1-6)"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="发布所有可用 Day（按顺序）"
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="预览模式，不实际发帖"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="列出所有可用 Day 及其推文数"
    )
    parser.add_argument(
        "--file",
        type=str,
        default=str(BIP_FILE),
        help=f"BiP markdown 文件路径（默认: {BIP_FILE}）"
    )

    args = parser.parse_args()

    # 加载 .env
    load_env()

    # 检查文件
    bip_path = Path(args.file)
    if not bip_path.exists():
        print(f"❌ 文件未找到: {bip_path}")
        sys.exit(1)

    text = bip_path.read_text(encoding="utf-8")
    available_days = get_available_days()

    if args.list:
        print(f"\n📋 BiP 内容概览: {bip_path.name}")
        print(f"   可用 Days: {', '.join(f'Day {d}' for d in available_days)}")
        for d in available_days:
            tweets = parse_day_tweets(text, d)
            print(f"   Day {d}: {len(tweets)} 条推文")
        return

    # 确定要发布的 Days
    days_to_post = []
    if args.day:
        days_to_post.append(args.day)
    elif args.all:
        days_to_post = available_days
    else:
        # 默认只列出
        available_days = get_available_days()
        print(f"\n📋 可用 Days: {', '.join(f'Day {d}' for d in available_days)}")
        print("   使用 --day N 指定 Day，或 --all 发布全部。")
        print("   使用 --dry-run 预览内容。")
        return

    # 验证 credentials
    if not args.dry_run:
        client_v2, api_v1 = get_twitter_client()
        if client_v2 is None:
            print("\n❌ Twitter API credentials 未配置")
            print("   在 .env 中添加以下环境变量：")
            print("   TWITTER_API_KEY=xxx")
            print("   TWITTER_API_SECRET=xxx")
            print("   TWITTER_ACCESS_TOKEN=xxx")
            print("   TWITTER_ACCESS_SECRET=xxx")
            sys.exit(1)
    else:
        client_v2, api_v1 = None, None

    # 发布
    mode_label = "🔍 预览模式" if args.dry_run else "🚀 发布模式"
    print(f"\n{'='*60}")
    print(f"  {mode_label}")
    print(f"  文件: {bip_path.name}")
    print(f"{'='*60}")

    for day_num in days_to_post:
        tweets = parse_day_tweets(text, day_num)
        if not tweets:
            print(f"\n  Day {day_num}: 未找到内容，跳过")
            continue

        print(f"\n{'─'*60}")
        print(f"  📅 Day {day_num} — {len(tweets)} 条推文")
        if tweets:
            print(f"     首条: {tweets[0]['text'][:80]}...")
            print(f"     末条: {tweets[-1]['text'][:80]}...")
        print(f"{'─'*60}")

        if not args.dry_run:
            post_thread(client_v2, api_v1, tweets, dry_run=False)
        else:
            post_thread(None, None, tweets, dry_run=True)

    print(f"\n{'='*60}")
    if args.dry_run:
        print(f"  ✅ 预览完成。使用 --day N 发布 Day N。")
    else:
        print(f"  ✅ 发布完成。")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()