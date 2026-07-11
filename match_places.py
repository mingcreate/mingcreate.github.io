#!/usr/bin/env python3
"""
네이버 로컬 검색 API로 판매점 ↔ 네이버 플레이스 매칭
============================================================
등록된 업체는 "등록 상호"로 네이버 지도를 열 수 있게 매칭 테이블을 만듭니다.
결과: naver_places.json  { "판매점주소": {"q": "지도 검색어", "title": "등록 상호", "m": 거리m} }

준비 (1회):
  1. https://developers.naver.com/apps → 애플리케이션 등록 → 사용 API: "검색"
  2. 발급받은 키를 환경변수로 설정:
       PowerShell:  $env:NAVER_OPENAPI_ID='클라이언트ID'; $env:NAVER_OPENAPI_SECRET='시크릿'

실행:
  python match_places.py            # 전체 (이미 처리된 주소는 건너뜀 — 이어하기 가능)
  python match_places.py --limit 50 # 테스트로 50개만

무료 쿼터 25,000회/일 — 전체 4,400여 지점도 하루 안에 처리됩니다.
매칭 기준: 좌표 거리 150m 이내 + 상호 유사(포함 관계). 미등록 가판점은 매칭되지 않는 게 정상입니다.
"""

import json, os, re, sys, time, math
from pathlib import Path

import requests

HERE = Path(__file__).parent
STORES_FILE = HERE / "lotto_stores.json"
COORDS_FILE = HERE / "coords_cache.json"
OUT_FILE    = HERE / "naver_places.json"

API_URL = "https://openapi.naver.com/v1/search/local.json"
CLIENT_ID     = os.environ.get("NAVER_OPENAPI_ID", "")
CLIENT_SECRET = os.environ.get("NAVER_OPENAPI_SECRET", "")

MAX_DIST_M = 150   # 좌표 오차 허용 거리
INTERNET_KW = ["인터넷", "dhlottery", "복권닷컴", "온라인", "동행복권", "www.", "http", ".co.kr", ".com"]


def dist_m(lat1, lng1, lat2, lng2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def norm(s):
    """상호 비교용 정규화: 공백/특수문자 제거"""
    return re.sub(r"[^가-힣A-Za-z0-9]", "", s or "")


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s or "")


def name_similar(a, b):
    """한쪽이 다른 쪽을 포함하면 동일 업체로 간주 (2글자 이상)"""
    na, nb = norm(a), norm(b)
    if len(na) < 2 or len(nb) < 2:
        return False
    return na in nb or nb in na


def preflight(session):
    """키/권한 확인용 테스트 호출 — 실패 시 원인을 구체적으로 안내"""
    r = session.get(
        API_URL,
        params={"query": "복권", "display": 1},
        headers={"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET},
        timeout=10,
    )
    if r.status_code == 200:
        print("✓ API 키 확인 완료")
        return
    print(f"⚠ API 테스트 호출 실패: HTTP {r.status_code}")
    print(f"  응답: {r.text[:300]}")
    if r.status_code == 401:
        print("  → Client ID/Secret이 잘못되었습니다. 복사할 때 앞뒤 공백이나 따옴표가")
        print("    같이 들어가지 않았는지, ID와 Secret이 서로 바뀌지 않았는지 확인하세요.")
    elif r.status_code == 403:
        print("  → 애플리케이션에 '검색' API가 등록되지 않았습니다.")
        print("    developers.naver.com/apps → 내 애플리케이션 → API 설정에서 '검색' 추가")
    elif r.status_code == 429:
        print("  → 오늘 호출 한도(25,000회)를 초과했습니다. 내일 다시 실행하세요.")
    sys.exit(1)


def search_local(session, query):
    r = session.get(
        API_URL,
        params={"query": query, "display": 5},
        headers={"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET},
        timeout=10,
    )
    if r.status_code == 429:
        raise RuntimeError("API 쿼터 초과 — 내일 이어서 실행하세요 (이미 처리분은 저장됨)")
    r.raise_for_status()
    return r.json().get("items", [])


def main():
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    if not CLIENT_ID or not CLIENT_SECRET:
        print("⚠ 환경변수 NAVER_OPENAPI_ID / NAVER_OPENAPI_SECRET 를 설정하세요.")
        print("  발급: https://developers.naver.com/apps (사용 API: 검색)")
        sys.exit(1)

    limit = 0
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    data   = json.loads(STORES_FILE.read_text(encoding="utf-8"))
    coords = json.loads(COORDS_FILE.read_text(encoding="utf-8")) if COORDS_FILE.exists() else {}
    out    = json.loads(OUT_FILE.read_text(encoding="utf-8")) if OUT_FILE.exists() else {}

    stores = [
        s for s in data["stores"].values()
        if not any(kw in s["name"] or kw in s["addr"] for kw in INTERNET_KW)
    ]
    # 당첨 많은 순으로 (자주 노출되는 지점부터 매칭)
    stores.sort(key=lambda s: -s["wins"])

    targets = [s for s in stores if s["addr"] not in out]
    if limit:
        targets = targets[:limit]
    print(f"대상 {len(targets)}개 (전체 {len(stores)}, 기존 처리 {len(out)})")

    session = requests.Session()
    preflight(session)
    matched = 0
    try:
        for i, s in enumerate(targets, 1):
            addr_parts = s["addr"].split()
            gu = addr_parts[1] if len(addr_parts) > 1 else ""
            query = f"{s['name']} {addr_parts[0]} {gu}".strip()

            entry = {"q": "", "title": "", "m": -1}  # 기본값 = 매칭 실패 기록 (재시도 방지)
            try:
                items = search_local(session, query)
            except RuntimeError:
                raise
            except Exception as e:
                print(f"[{i}] {s['name']}: 요청 실패 {e} — 건너뜀(기록 안 함)")
                continue

            c = coords.get(s["addr"])
            for it in items:
                title = strip_tags(it.get("title", ""))
                if not name_similar(title, s["name"]):
                    continue
                # mapx/mapy = WGS84 * 1e7
                try:
                    plng = int(it["mapx"]) / 1e7
                    plat = int(it["mapy"]) / 1e7
                except (KeyError, ValueError):
                    continue
                # 좌표 검증이 불가능하면 매칭하지 않음 (동명 타업체 오매칭 방지)
                d = dist_m(c["lat"], c["lng"], plat, plng) if c and c.get("lat") else None
                if d is None or d > MAX_DIST_M:
                    continue
                entry = {"q": f"{title} {gu}".strip(), "title": title, "m": round(d)}
                matched += 1
                print(f"[{i}/{len(targets)}] ✓ {s['name']} → {title} ({entry['m']}m)")
                break

            out[s["addr"]] = entry
            if i % 50 == 0:
                OUT_FILE.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
                print(f"  … {i}개 처리, 매칭 {matched}개 (중간 저장)")
            time.sleep(0.12)  # 초당 10회 제한 준수
    finally:
        OUT_FILE.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")

    total_matched = sum(1 for v in out.values() if v.get("q"))
    print(f"완료: 이번에 {matched}개 매칭, 누적 {total_matched}/{len(out)}개")
    print(f"→ {OUT_FILE.name} 을 깃허브에 함께 올리면 등록 업체는 플레이스 카드로 연결됩니다.")


if __name__ == "__main__":
    main()
