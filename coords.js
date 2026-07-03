// coords.js — 주소 키워드 → 위경도 보정 테이블
// lotto-myungdang.html 과 같은 폴더에 위치해야 합니다.

const COORD_TABLE = [
  // 서울
  { kw:["강남구","역삼","삼성동","청담","논현"],        lat:37.504, lng:127.049 },
  { kw:["서초구","방배","반포","양재","서초동"],         lat:37.483, lng:127.009 },
  { kw:["송파구","잠실","가락","문정","석촌"],           lat:37.510, lng:127.113 },
  { kw:["마포구","공덕","홍대","합정","상암"],           lat:37.549, lng:126.948 },
  { kw:["종로구","광화문","관철","인사동","청진"],       lat:37.572, lng:126.980 },
  { kw:["중구","명동","충무로","을지로","신당"],         lat:37.561, lng:126.997 },
  { kw:["성북구","돈암","길음","정릉","석관"],           lat:37.592, lng:127.018 },
  { kw:["관악구","신림","봉천","낙성대"],                lat:37.474, lng:126.940 },
  { kw:["노원구","상계","중계","하계","공릉"],           lat:37.654, lng:127.056 },
  { kw:["영등포구","여의도","당산","문래","양평"],       lat:37.522, lng:126.910 },
  { kw:["강서구","화곡","마곡","발산","개화"],           lat:37.551, lng:126.849 },
  { kw:["구로구","구로","신도림","개봉"],                lat:37.495, lng:126.887 },
  { kw:["동대문구","청량리","회기","신설","이문"],       lat:37.574, lng:127.040 },
  { kw:["성동구","왕십리","금호","행당","옥수"],         lat:37.563, lng:127.036 },
  { kw:["광진구","건대","자양","중곡","구의"],           lat:37.538, lng:127.082 },
  { kw:["강동구","천호","길동","암사","명일"],           lat:37.530, lng:127.124 },
  { kw:["은평구","연신내","불광","갈현","응암"],         lat:37.602, lng:126.928 },
  { kw:["서대문구","신촌","홍제","남가좌","북가좌"],     lat:37.579, lng:126.936 },
  { kw:["중랑구","면목","상봉","망우","신내"],           lat:37.606, lng:127.093 },
  { kw:["도봉구","창동","방학","쌍문","도봉"],           lat:37.668, lng:127.047 },
  { kw:["강북구","수유","번동","미아","우이"],           lat:37.637, lng:127.026 },
  { kw:["양천구","목동","신정","신월"],                  lat:37.517, lng:126.867 },
  { kw:["동작구","사당","흑석","노량진","상도"],         lat:37.504, lng:126.940 },
  { kw:["용산구","이태원","한남","후암","청파"],         lat:37.532, lng:126.990 },
  // 경기
  { kw:["수원시","팔달","영통","권선","장안"],           lat:37.263, lng:127.029 },
  { kw:["성남시","분당","판교","야탑","이매"],           lat:37.360, lng:127.110 },
  { kw:["고양시","일산","덕양","화정","행신"],           lat:37.660, lng:126.832 },
  { kw:["용인시","기흥","수지","처인","동백"],           lat:37.234, lng:127.205 },
  { kw:["부천시","원미","소사","오정","송내"],           lat:37.503, lng:126.766 },
  { kw:["안양시","동안","만안","평촌","관양"],           lat:37.393, lng:126.957 },
  { kw:["남양주시","화도","별내","다산","진접"],         lat:37.636, lng:127.217 },
  { kw:["시흥시","정왕","신천","목감","은행"],           lat:37.380, lng:126.803 },
  { kw:["화성시","동탄","병점","봉담","향남"],           lat:37.200, lng:126.830 },
  { kw:["의정부시","호원","금오","가능","신곡"],         lat:37.738, lng:127.034 },
  { kw:["광주시","경안","초월","오포","퇴촌"],           lat:37.430, lng:127.255 },
  { kw:["하남시","미사","천현","위례"],                  lat:37.540, lng:127.215 },
  { kw:["파주시","금촌","운정","교하","문산"],           lat:37.760, lng:126.780 },
  { kw:["김포시","사우","장기","통진","양촌"],           lat:37.615, lng:126.716 },
  { kw:["광명시","철산","하안","소하","광명"],           lat:37.479, lng:126.866 },
  // 인천
  { kw:["남동구","구월","논현","만수","간석"],           lat:37.447, lng:126.731 },
  { kw:["부평구","부평","삼산","갈산","청천"],           lat:37.508, lng:126.722 },
  { kw:["계양구","계산","효성","작전","임학"],           lat:37.537, lng:126.738 },
  { kw:["연수구","송도","연수","청학","동춘"],           lat:37.410, lng:126.680 },
  { kw:["서구","검단","가정","석남","연희"],             lat:37.545, lng:126.676 },
  { kw:["미추홀구","주안","도화","용현","학익"],         lat:37.453, lng:126.705 },
  // 충청
  { kw:["대전","유성","서구","중구","동구","대덕"],      lat:36.355, lng:127.384 },
  { kw:["세종","조치원","소담","도담","어진"],           lat:36.480, lng:127.289 },
  { kw:["청주","상당","서원","청원","흥덕"],             lat:36.642, lng:127.489 },
  { kw:["천안","동남","서북","성정","불당"],             lat:36.815, lng:127.114 },
  { kw:["아산","온양","배방","탕정"],                    lat:36.789, lng:127.002 },
  { kw:["충주","칠금","연수","목행"],                    lat:36.991, lng:127.925 },
  // 전라
  { kw:["광주","동구","서구","남구","북구","광산"],      lat:35.160, lng:126.852 },
  { kw:["전주","완산","덕진","효자","인후"],             lat:35.802, lng:127.083 },
  { kw:["익산","영등","팔봉","어양","동산"],             lat:35.948, lng:126.958 },
  { kw:["여수","돌산","쌍봉","학동","오천"],             lat:34.761, lng:127.662 },
  { kw:["순천","해룡","조례","왕지","풍덕"],             lat:34.948, lng:127.487 },
  { kw:["목포","상동","옥암","죽교","원산"],             lat:34.812, lng:126.392 },
  // 경상
  { kw:["대구","중구","동구","서구","북구","달서","수성","달성"], lat:35.870, lng:128.601 },
  { kw:["부산","해운대","동래","사상","연제","수영","남구","북구","사하","금정","강서","기장"], lat:35.180, lng:129.075 },
  { kw:["울산","남구","북구","동구","중구","울주"],      lat:35.538, lng:129.311 },
  { kw:["창원","의창","성산","마산","진해"],             lat:35.234, lng:128.681 },
  { kw:["김해","장유","내외","삼방","부원"],             lat:35.228, lng:128.889 },
  { kw:["거제","고현","아주","장평","수월"],             lat:34.880, lng:128.621 },
  { kw:["진주","충무","상대","하대","초전"],             lat:35.180, lng:128.107 },
  { kw:["포항","북구","남구","죽도","두호"],             lat:36.019, lng:129.344 },
  { kw:["경주","황성","동천","성동","불국"],             lat:35.856, lng:129.225 },
  { kw:["구미","원평","도량","신평","비산"],             lat:36.119, lng:128.345 },
  { kw:["안동","옥동","태화","용상","율세"],             lat:36.574, lng:128.729 },
  // 강원
  { kw:["춘천","퇴계","효자","약사","후평"],             lat:37.881, lng:127.730 },
  { kw:["원주","단구","반곡","태장","무실"],             lat:37.342, lng:127.921 },
  { kw:["강릉","교동","포남","성남","홍제"],             lat:37.752, lng:128.876 },
  // 제주
  { kw:["제주시","연동","노형","아라","이도"],           lat:33.499, lng:126.531 },
  { kw:["서귀포","서홍","동홍","강정","대정"],           lat:33.253, lng:126.560 },
];

// ── 지오코딩 결과 캐시 (localStorage 영구 저장) ──────────────
// 값: {lat,lng} = 성공 / false = 실패(재시도 안 함) / undefined = 미조회
const GEO_CACHE_KEY = 'lottoGeoCacheV1';
let _geoCache = {};
try { _geoCache = JSON.parse(localStorage.getItem(GEO_CACHE_KEY)) || {}; } catch (e) {}

// 사전 지오코딩된 좌표 파일(coords_cache.json)을 읽어 캐시에 병합.
// 방문자 브라우저에서 지오코딩 API를 거의 호출하지 않게 됨.
async function loadCoordCache(url) {
  try {
    const res = await fetch(url);
    if (!res.ok) return 0;
    const data = await res.json();
    let merged = 0;
    for (const addr in data) {
      if (_geoCache[addr] === undefined) { _geoCache[addr] = data[addr]; merged++; }
    }
    return merged;
  } catch (e) {
    return 0; // 파일 없으면 기존 방식(브라우저 지오코딩)으로 동작
  }
}

let _geoSaveTimer = null;
function saveGeoCache() {
  clearTimeout(_geoSaveTimer);
  _geoSaveTimer = setTimeout(() => {
    try { localStorage.setItem(GEO_CACHE_KEY, JSON.stringify(_geoCache)); } catch (e) {}
  }, 800);
}

// 주소 정제: 도로명+건물번호까지만 남기고 뒤의 상세(호수 등) 제거
// "지하 2100" 같은 지하상가 표기도 허용
// 예) "인천 연수구 경원대로483번길 6 103호401-3 103호" → "인천 연수구 경원대로483번길 6"
function cleanAddr(addr) {
  const m = addr.match(/^(.+?(?:로|길)\s*(?:지하\s*)?\d+(?:-\d+)?)(?=\s|,|$)/);
  return m ? m[1] : addr;
}

/**
 * 주소 → 위경도 변환 (동기)
 * 1순위: 지오코딩 캐시 (정확한 좌표)
 * 2순위: COORD_TABLE 키워드 매칭 (구/동 중심점 근사치)
 * 3순위: 서울 시청 폴백
 */
function addrToLatLng(addr) {
  const cached = _geoCache[addr];
  if (cached && cached.lat) return { lat: cached.lat, lng: cached.lng };

  for (const entry of COORD_TABLE) {
    if (entry.kw.some(kw => addr.includes(kw))) {
      return { lat: entry.lat, lng: entry.lng };
    }
  }
  return { lat: 37.5665, lng: 126.9780 };
}

// 캐시에 있는 정확한 좌표를 store 목록에 반영
function applyGeoCache(list) {
  list.forEach(s => {
    const c = _geoCache[s.addr];
    if (c && c.lat) { s.lat = c.lat; s.lng = c.lng; }
  });
}

// ── 네이버 지오코더 비동기 큐 ────────────────────────────────
// 나중에 요청된 목록(= 지금 화면에 보이는 지점)이 큐 맨 앞에 오도록 재배치.
// 배치가 끝날 때마다 onUpdate(isDone) 콜백 → 핀을 점진적으로 정확하게 갱신.
const _geoQueue = [];
let _geoRunning = false;
let _geoOnUpdate = null;

function geocodeStores(storeList, onUpdate) {
  if (typeof naver === 'undefined' || !naver.maps) return;
  if (onUpdate) _geoOnUpdate = onUpdate;

  // geocoder 서브모듈은 maps.js 로드 후 비동기로 로드됨 → 준비될 때까지 재시도
  if (!naver.maps.Service) {
    setTimeout(() => geocodeStores(storeList), 500);
    return;
  }

  // 미조회 주소만, 주소 중복 제거
  const seen = new Set();
  const wanted = [];
  for (const s of storeList) {
    if (_geoCache[s.addr] !== undefined || seen.has(s.addr)) continue;
    seen.add(s.addr);
    wanted.push(s);
  }
  if (wanted.length === 0) return;

  // 이미 큐에 있던 동일 주소는 제거하고, 이번 요청분을 맨 앞에 배치
  const rest = _geoQueue.filter(s => !seen.has(s.addr));
  _geoQueue.length = 0;
  _geoQueue.push(...wanted, ...rest);

  if (!_geoRunning) runGeoQueue();
}

function runGeoQueue() {
  const BATCH = 40;
  const INTERVAL = 250;

  // 처리 도중 캐시가 채워진 항목은 건너뛰기
  while (_geoQueue.length && _geoCache[_geoQueue[0].addr] !== undefined) _geoQueue.shift();

  if (_geoQueue.length === 0) {
    _geoRunning = false;
    saveGeoCache();
    if (_geoOnUpdate) _geoOnUpdate(true);
    return;
  }

  _geoRunning = true;
  const batch = _geoQueue.splice(0, BATCH);
  let done = 0;
  let advanced = false;

  const advance = () => {
    if (advanced) return;
    advanced = true;
    saveGeoCache();
    if (_geoOnUpdate) _geoOnUpdate(false);
    setTimeout(runGeoQueue, INTERVAL);
  };

  batch.forEach(s => {
    naver.maps.Service.geocode({ query: cleanAddr(s.addr) }, (status, res) => {
      if (status === naver.maps.Service.Status.OK &&
          res.v2 && res.v2.addresses && res.v2.addresses.length > 0) {
        const loc = res.v2.addresses[0];
        const lat = parseFloat(loc.y);
        const lng = parseFloat(loc.x);
        _geoCache[s.addr] = { lat, lng };
        s.lat = lat;
        s.lng = lng;
      } else {
        _geoCache[s.addr] = false; // 실패 기록 → 매번 재시도하지 않음
      }
      done++;
      if (done === batch.length) advance();
    });
  });

  // 콜백이 안 오는 경우에도 큐가 멈추지 않도록 안전장치
  setTimeout(advance, 6000);
}
