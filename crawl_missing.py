#!/usr/bin/env python3
"""
빠진 회차만 골라 크롤링하는 스크립트 — fullayer.com 기반
============================================================
lotto_stores.json 에서 데이터가 없는 회차를 찾아, 그 회차만
회차 지정 조회(ltws_count 파라미터)로 수집합니다.

실행:
    python crawl_missing.py            # 빠진 회차 전부 시도
    python crawl_missing.py 1224 1228  # 특정 회차만 지정

참고:
- 사이트에 데이터가 아예 없는 옛날 회차(예: 250회 부근)는 0건으로 나옴.
  이런 회차는 "확인됨(빈 회차)"로 기록해서 다음 실행 때 다시 시도하지 않음.
  (단, 최신 10회차 이내는 아직 안 올라왔을 수 있으므로 기록하지 않고 넘어감)
"""

import json, time, datetime, sys, random, io, logging
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from update_weekly import aggregate, HEADERS, BASE_URL, OUTPUT_FILE

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

RECENT_WINDOW = 10  # 이 범위 안의 회차는 0건이어도 "빈 회차"로 확정하지 않음


def fetch_round(session, drw_no: int) -> list[dict]:
    """특정 회차의 1등 당첨판매점 목록을 조회"""
    resp = session.get(
        BASE_URL,
        params={"ltws_count": str(drw_no), "ltws_rank": "1"},
        headers=HEADERS,
        timeout=15,
    )
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")
    results = []
    for row in soup.select("table tbody tr"):
        cols = row.find_all("td")
        if len(cols) < 6:
            continue
        drw_el = cols[0].find("a")
        drw = int(drw_el.text.strip()) if drw_el else int(cols[0].get_text(strip=True) or 0)
        if drw != drw_no:  # 회차 필터가 무시된 응답 방어
            continue
        rank = cols[3].get_text(strip=True)
        if rank not in ("1", "1등"):
            continue
        name_el = cols[1].find("a")
        name = name_el.text.strip() if name_el else cols[1].get_text(strip=True)
        addr = cols[5].get_text(strip=True)
        if not name or not addr or len(addr) < 4:
            continue
        store_id = ""
        if name_el and name_el.get("href"):
            import re
            m = re.search(r"/(\d+)$", name_el["href"])
            if m:
                store_id = m.group(1)
        results.append({"round": drw, "name": name, "addr": addr,
                        "type": cols[2].get_text(strip=True), "storeId": store_id})
    return results


def main():
    log.info("=== 빠진 회차 크롤링 시작 ===")

    if not OUTPUT_FILE.exists():
        log.error("lotto_stores.json 없음")
        sys.exit(1)

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    latest = max((int(k) for k, v in data["rounds"].items() if v), default=0)

    args = [int(a) for a in sys.argv[1:] if a.isdigit()]
    if args:
        targets = args
    else:
        targets = [r for r in range(1, latest + 1)
                   if not data["rounds"].get(str(r))
                   and str(r) not in data["rounds"]]  # []로 기록된 빈 회차는 재시도 안 함

    if not targets:
        log.info("빠진 회차 없음 — 종료")
        return

    log.info(f"대상 회차 {len(targets)}개: {targets[:20]}{' ...' if len(targets) > 20 else ''}")

    session = requests.Session()
    try:
        session.get(BASE_URL, headers=HEADERS, timeout=15)
    except Exception:
        pass

    added, empty = 0, []
    for i, drw in enumerate(targets, 1):
        try:
            rows = fetch_round(session, drw)
        except Exception as e:
            log.warning(f"{drw}회 조회 실패: {e} — 건너뜀")
            continue

        if rows:
            key_set = {f"{w['name']}|{w['addr']}" for w in data["rounds"].get(str(drw), [])}
            bucket = data["rounds"].setdefault(str(drw), [])
            n = 0
            for r in rows:
                k = f"{r['name']}|{r['addr']}"
                if k not in key_set:
                    bucket.append(r)
                    key_set.add(k)
                    n += 1
            added += n
            log.info(f"[{i}/{len(targets)}] {drw}회: {n}건 추가")
        else:
            empty.append(drw)
            # 최신 회차 근처가 아니면 "확인된 빈 회차"로 기록 → 재시도 방지
            if drw <= latest - RECENT_WINDOW:
                data["rounds"][str(drw)] = []
            log.info(f"[{i}/{len(targets)}] {drw}회: 데이터 없음")

        time.sleep(random.uniform(1.5, 2.5))

    aggregate(data)
    latest_round = max((int(k) for k, v in data["rounds"].items() if v), default=0)
    data["meta"] = {
        "lastUpdated":  datetime.datetime.now().isoformat(),
        "latestRound":  latest_round,
        "totalRounds":  sum(1 for v in data["rounds"].values() if v),
        "totalStores":  len(data["stores"]),
        "source":       BASE_URL,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    log.info(f"=== 완료: {added}건 추가, 데이터 없는 회차 {len(empty)}개 ===")
    if empty:
        log.info(f"    데이터 없음: {empty[:30]}{' ...' if len(empty) > 30 else ''}")


if __name__ == "__main__":
    main()
