#!/usr/bin/env python3
"""오후 랜덤 발행 게이트 — launchd 가 12:00~18:45 KST 동안 15분마다 부른다.

상태: ~/.ipe/queue/duskblocks/slot.json = {"date","time","prev_date","prev_time","published"}
- 오늘 날짜가 아니면 12:00~17:59 중 어제 시각의 '시'와 다른 시각을 새로 뽑는다(이전 값은 prev_* 로).
- 지금 >= time 이고 published=false 면 publish_next.py 를 돌리고, 성공하면 published=true.
"""
import fcntl
import json
import os
import random
import subprocess
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")
HERE = os.path.dirname(os.path.abspath(__file__))
QUEUE = os.environ.get("IPE_QUEUE_DIR") or os.path.expanduser("~/.ipe/queue/duskblocks")
HOURS = range(12, 18)  # 12:00 ~ 17:59


def pick_time(prev_time, rng=random):
    """12:00~17:59 중 prev_time 의 시(hour)와 다른 시각 'HH:MM'."""
    prev_hour = int(prev_time.split(":")[0]) if prev_time else None
    hours = [h for h in HOURS if h != prev_hour]
    return f"{rng.choice(hours):02d}:{rng.randrange(60):02d}"


def roll(slot, today, rng=random):
    """날짜가 바뀌었으면 슬롯을 굴린다. 같은 날이면 그대로."""
    if slot and slot.get("date") == today:
        return slot
    old = slot or {}
    # 발행 때 미리 뽑아 둔 오늘 시각(next_*)이 있으면 그대로 쓴다 — 어제와 다른 시(hour)는 그때 이미 보장.
    if old.get("next_date") == today and old.get("next_time"):
        t = old["next_time"]
    else:
        t = pick_time(old.get("time"), rng)
    return {"date": today, "time": t,
            "prev_date": old.get("date"), "prev_time": old.get("time"), "published": False}


def plan_next(slot, today, rng=random):
    """내일 시각을 미리 뽑아 slot 에 next_date·next_time 으로 적는다(확인용·내일 그대로 사용)."""
    tomorrow = (datetime.strptime(today, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    slot["next_date"] = tomorrow
    slot["next_time"] = pick_time(slot["time"], rng)
    return slot


def due(slot, now_hhmm):
    return (not slot["published"]) and now_hhmm >= slot["time"]


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def save(path, slot):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(slot, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)


def run(now, queue=QUEUE, rng=random, publish=None):
    """한 번 돈다. 반환: 'skip' | 'wait' | 'published' | 'failed'."""
    os.makedirs(queue, exist_ok=True)
    slot_path = os.path.join(queue, "slot.json")
    with open(os.path.join(queue, ".gate.lock"), "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        today = now.strftime("%Y-%m-%d")
        before = load(slot_path)
        slot = roll(before, today, rng)
        if slot is not before:
            save(slot_path, slot)
        if not due(slot, now.strftime("%H:%M")):
            return "skip" if slot["published"] else "wait"
        ok = (publish or default_publish)(today, now.strftime("%H:%M"), queue)
        if ok:
            slot["published"] = True
            plan_next(slot, today, rng)
            save(slot_path, slot)
            print(f"next: {slot['next_date']} {slot['next_time']} KST")
            return "published"
        return "failed"


def default_publish(date, hhmm, queue):
    r = subprocess.run([sys.executable, os.path.join(HERE, "publish_next.py"), "--date", date, "--time", hhmm, "--queue", queue])
    return r.returncode == 0


if __name__ == "__main__":
    try:
        print(run(datetime.now(KST)))
    except BlockingIOError:
        print("busy")
