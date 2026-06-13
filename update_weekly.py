#!/usr/bin/env python3
"""
로또 당첨판매점 주간 업데이트 스크립트 — fullayer.com 기반
============================================================
매주 토요일 21:10 이후 실행 → 1페이지(최신 회차)만 수집 → HTML 자동 재주입

cron 등록 (리눅스/Mac):
    crontab -e
    10 21 * * 6 /usr/bin/python3 /경로/update_weekly.py >> /경로/lotto.log 2>&1

Windows 작업 스케줄러:
    트리거: 매주 토요일 21:10
    동작  : python update_weekly.py

실행 옵션:
    python update_weekly.py           # 토요일 21:10 이후에만 실행
    python update_weekly.py --force   # 시간 무관 강제 실행
"""

import json, time, datetime, sys, random, logging, re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

OUTPUT_FILE = Path(__file__).parent / "lotto_stores.json"
BASE_URL    = "https://www.fullayer.com/lottowinstore/fo/lottowinstorelist"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer":         "https://www.fullayer.com/lottowinstore/fo/lottowinstorelist",
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Connection":      "keep-alive",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def is_after_draw() -> bool:
    n = datetime.datetime.now()
    return n.weekday() == 5 and (n.hour > 21 or (n.hour == 21 and n.minute >= 10))


def init_session():
    session = requests.Session()
    try:
        session.get(BASE_URL, headers=HEADERS, timeout=15)
    except Exception:
        pass
    return session


def fetch_page(session, page_no: int) -> list[dict]:
    resp = session.get(
        BASE_URL,
        params={"pageNo": page_no, "rank": "1"},
        headers=HEADERS,
        timeout=15,
    )
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")
    rows = soup.select("table tbody tr")
    results = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue
        drw_el   = cols[0].find("a")
        drw_no   = int(drw_el.text.strip()) if drw_el else 0
        name_el  = cols[1].find("a")
        name     = name_el.text.strip() if name_el else cols[1].text.strip()
        kind     = cols[2].text.strip()
        rank     = cols[3].text.strip()
        addr     = cols[5].text.strip()
        store_id = ""
        if name_el and name_el.get("href"):
            m = re.search(r"/(\d+)$", name_el["href"])
            if m:
                store_id = m.group(1)
        if rank not in ("1", "1등"):
            continue
        if not name or not addr or len(addr) < 4:
            continue
        results.append({"round": drw_no, "name": name, "addr": addr,
                        "type": kind, "storeId": store_id})
    return results


def aggregate(data: dict):
    store_map: dict[str, dict] = {}
    for drw_str, winners in data["rounds"].items():
        drw_int = int(drw_str)
        for w in winners:
            key = f"{w['name']}|{w['addr']}"
            if key not in store_map:
                store_map[key] = {
                    "name": w["name"], "addr": w["addr"],
                    "wins": 0, "rounds": [], "lastRound": 0,
                    "type": w.get("type", "자동"),
                    "storeId": w.get("storeId", ""),
                }
            store_map[key]["wins"] += 1
            store_map[key]["rounds"].append(drw_int)
            if drw_int > store_map[key]["lastRound"]:
                store_map[key]["lastRound"] = drw_int
            if not store_map[key]["storeId"] and w.get("storeId"):
                store_map[key]["storeId"] = w["storeId"]
    for v in store_map.values():
        v["prize"]  = round(v["wins"] * 29.5)
        v["rounds"] = sorted(set(v["rounds"]))
    data["stores"] = store_map


def main():
    force = "--force" in sys.argv
    log.info("=== 로또 주간 업데이트 시작 ===")

    if not is_after_draw() and not force:
        log.warning("토요일 21:10 이전입니다. --force 로 강제 실행하세요.")
        sys.exit(0)

    if not OUTPUT_FILE.exists():
        log.error("lotto_stores.json 없음 → crawl_all.py 를 먼저 실행하세요.")
        sys.exit(1)

    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    saved_latest = data.get("meta", {}).get("latestRound", 0)
    session      = init_session()

    # 1~3페이지에서 최신 회차 데이터 수집 (신규 회차가 1페이지에 추가됨)
    new_count = 0
    for page_no in range(1, 4):
        rows = fetch_page(session, page_no)
        if not rows:
            break

        for r in rows:
            drw_str = str(r["round"])
            # 이미 수집된 회차 데이터는 신규 항목만 추가
            if int(r["round"]) <= saved_latest:
                # 기존 회차라도 해당 판매점이 없으면 추가
                existing = {f"{w['name']}|{w['addr']}"
                            for w in data["rounds"].get(drw_str, [])}
                key = f"{r['name']}|{r['addr']}"
                if key in existing:
                    continue

            if drw_str not in data["rounds"]:
                data["rounds"][drw_str] = []
            existing = {f"{w['name']}|{w['addr']}" for w in data["rounds"][drw_str]}
            key = f"{r['name']}|{r['addr']}"
            if key not in existing:
                data["rounds"][drw_str].append(r)
                new_count += 1

        # 모두 기존 데이터면 중단
        latest_in_page = max(r["round"] for r in rows)
        if latest_in_page <= saved_latest and page_no >= 2:
            break

        time.sleep(random.uniform(2.0, 3.0))

    aggregate(data)
    latest_round = max((int(k) for k in data["rounds"] if data["rounds"][k]), default=0)
    data["meta"] = {
        "lastUpdated":  datetime.datetime.now().isoformat(),
        "latestRound":  latest_round,
        "totalRounds":  len(data["rounds"]),
        "totalStores":  len(data["stores"]),
        "source":       BASE_URL,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    log.info(f"=== 업데이트 완료: {new_count}건 추가, 최신 {latest_round}회 ===")
    log.info(f"    lotto_stores.json 이 자동으로 갱신되었습니다.")
    log.info(f"    브라우저를 새로고침하면 최신 데이터가 반영됩니다.")


if __name__ == "__main__":
    main()
