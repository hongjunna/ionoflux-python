<a href="https://ionoflux.runvia.app"><img src="https://ionoflux.runvia.app/brand/icon-512.png" width="96" height="96" alt="IonoFlux official logo: sun and radio waves on a blue background"></a>

# IonoFlux Python SDK

[IonoFlux](https://ionoflux.runvia.app) 공식 동기 Python SDK입니다. 우주기상·태양·지자기 데이터, 경보와 공개 데이터 메타데이터를 조회하며 **Python 3.11 이상**을 지원합니다.

```sh
pip install ionoflux
```

[PyPI](https://pypi.org/project/ionoflux/) · [GitHub](https://github.com/hongjunna/ionoflux-python) · [English](https://github.com/hongjunna/ionoflux-python/blob/main/README.md) · [공식 사이트](https://ionoflux.runvia.app) · [릴리스](https://github.com/hongjunna/ionoflux-python/releases)

## Server 키 발급과 첫 조회

계정 페이지 https://ionoflux.runvia.app/account 에서 **Server 키**를 발급하고 `IONOFLUX_API_KEY` 환경변수에 저장하세요. Web 키는 일반 Python 요청에 403을 반환할 수 있습니다. 현재 Server 키도 service URL이 필요하며 웹사이트 없는 노트북·배치 사용자의 발급 안내는 기존 정책 내에서 확인해야 합니다. SDK는 키 발급이나 정책 우회를 수행하지 않습니다.

```sh
export IONOFLUX_API_KEY='your-server-key'
```

```python
from ionoflux import Client, RateLimitError

with Client() as client:
    try:
        current = client.space_weather.current()
        print(current.data)
        print(current.rate_limit.remaining)
    except RateLimitError as error:
        print(error.retry_after, error.rate_limit.reset_seconds)
```

명시적 `Client(api_key="...")`가 환경변수보다 우선합니다. `client.sources()`와 `client.data.status()`는 키 없이 가능합니다. 그 밖의 호출을 키 없이 하면 발급 페이지 링크(https://ionoflux.runvia.app/account)를 포함한 `ConfigurationError`가 발생합니다. 키를 코드·브라우저·공유 노트북 출력에 넣지 마세요.

## 실제 지원 범위

현재 우주기상 `space_weather.current()`, SFI `solar.flux()`, 흑점 `solar.sunspots(source=...)`, X-ray `solar.xray(band=...)`, 태양풍 `solar.wind(parameter=...)`, Kp `geomagnetic.kp(source=..., include_forecast=...)`, Ap `geomagnetic.ap()`, 10개 지표 `statistics(metric, start=..., end=..., source=...)`, 경보 `alerts.list(since=..., category=[...], limit=50)`, NOAA 척도 `alerts.scales()`, 출처 `sources()`, 데이터 현황/최신 행 `data.status(dataset=None)`를 제공합니다. 비동기 클라이언트·pandas/DataFrame 변환·TEC/MUF·전파 예측·관측소·WSPR/PSK 전용 조회는 제공하지 않으며 [후속 작업 #2](https://github.com/hongjunna/ionoflux-python/issues/2)에서 추적합니다.

응답은 `APIResponse`: `.data`는 원래 JSON(dict, 경보는 list), `.raw_body`는 원시 응답 bytes, `.status_code`, `.headers`는 한도/content-type 허용 목록, `.rate_limit`은 한도 정보입니다. JSON 필드·null·단위·출처·추가 필드는 그대로 보존하며 시각은 ISO 8601 문자열입니다. 중첩 값은 유연한 JSON 타입이며 도메인별 런타임 모델 검증·DataFrame 변환은 제공하지 않습니다.

```python
from datetime import UTC, datetime
from ionoflux import Client

with Client() as client:
    series = client.solar.flux(
        start=datetime(2026, 10, 1, tzinfo=UTC),
        end=datetime(2026, 10, 2, tzinfo=UTC),
        interval="1h",
        limit=100,
    )
    print(series.data["unit"], series.data["attribution"], series.data["data"])
```

시계열 공통 옵션은 start/end, interval(raw/1m/5m/1h/3h/1d/7d/1mo), limit(기본5000/최대10000)입니다. 날짜를 생략하면 엔드포인트별 서버 기본 기간을 따릅니다. `1mo`는 달력월이 아닌 30일이며 최신 limit개를 시간순으로 반환합니다. 자동 페이지네이션·전체 이력 다운로드는 없습니다. aware datetime만 허용하고 UTC 변환하며 명시 start/end는 순서와 최대3660일을 검증합니다. 조회 가능 기간과 실제 보유 기간은 다르므로 `data.status()`의 coverage·retention을 확인하세요.

## 오류·안정성

401 AuthenticationError, 403 PermissionDeniedError, 404 NotFoundError, 422 ValidationError, 429 RateLimitError, 5xx ServerError, 3xx RedirectError는 APIError 하위 예외입니다. 상태 코드·키 제거된 detail·rate_limit·retry_after를 제공하고 원래 요청 객체는 보관하지 않습니다. 네트워크 실패 TransportError, 잘못된 JSON ResponseError, 설정 오류 ConfigurationError, 로컬 입력 검증 ValueError를 구분합니다.

GET만 지원하고 연결 실패/timeout·읽기 실패/timeout·원격 프로토콜 오류와 502/503/504만 기본1회(설정0~3회) 재시도합니다. 총 backoff 최대1.75초, 429/일일 한도는 자동 재시도·대기하지 않습니다. 응답 디코딩/로컬 프로토콜 오류·pool timeout도 재시도하지 않습니다. 502/503/504라도 Retry-After가 있거나 남은 한도가0이면 ServerError를 즉시 반환합니다. `X-RateLimit-Reset`은 epoch가 아니라 UTC 자정까지 남은 초입니다. Retry-After는 문자열로 노출하며 호출 예산을 초과하지 않게 사용자가 판단합니다. timeout 기본10초는 HTTPX 작업별 제한으로 전체 wall-clock 제한은 아닙니다. 재시도도 한도에 포함될 수 있습니다.

base_url 기본값은 `https://ionoflux.runvia.app/v1`, 사용자 주소는 HTTPS·/v1 끝·계정/쿼리/fragment 없음 조건을 요구합니다. 세션 재사용·context manager를 지원하고 리다이렉트와 환경 proxy/netrc는 비활성화합니다. SDK는 키를 URL·로그·예외에 넣지 않으며 공개 메타 경로에는 키를 보내지 않습니다. 사용자 지정 transport/HTTP 디버그 로깅은 인증 헤더를 노출할 수 있으므로 기록하지 마세요.

IonoFlux 이용 통계를 위해 모든 요청에 고정 출처 태그 `utm_source=python&utm_medium=sdk&utm_content=<SDK 버전>`과 `User-Agent: ionoflux-python/<SDK 버전>` 헤더를 함께 보냅니다. 키·사용자·호스트·환경 정보는 포함하지 않습니다.

## 문서와 검증 범위

[전체 API 계약과 한계](https://github.com/hongjunna/ionoflux-python/blob/main/docs/api-contract.md) · [개발·설치 계획](https://github.com/hongjunna/ionoflux-python/blob/main/docs/development-plan.md) · [변경 이력](https://github.com/hongjunna/ionoflux-python/blob/main/CHANGELOG.md)

v0.1.0은 2026-10-20 정식 PyPI에 출시되었습니다. [출시 기록](https://github.com/hongjunna/ionoflux-python/releases/tag/python-v0.1.0)에 기존 산출물과 검증 근거를 보존합니다. 당시 Server 키로 순차 9회 실제 API 인수를 수행해 모두 200 및 필드/타입 검증을 통과했습니다([인수 범위](https://github.com/hongjunna/ionoflux-python/blob/main/docs/release-review.md)). 실제 403/429나 모든 공급자·엔드포인트 조합은 검증하지 않았으며 이번 문서 패치는 새 실 API 인수를 주장하지 않습니다.

Mock 테스트는 네트워크를 차단합니다. CI는 Linux Python 3.11~3.15, Windows/macOS 3.14와 최소 HTTPX 0.27.0에서 테스트하며 Ruff·mypy·README 렌더링·wheel/sdist 빌드와 각각의 새 환경 설치를 확인합니다. 게시 workflow는 GitHub Environment 수동 승인과 Trusted Publishing으로 보호되며 일반 PR CI는 게시하지 않습니다.

## SDK 코드 라이선스·API 이용 조건·데이터 권리

SDK 코드는 **[PolyForm Noncommercial License 1.0.0](https://github.com/hongjunna/ionoflux-python/blob/main/LICENSE)**
(SPDX: `PolyForm-Noncommercial-1.0.0`)을 따릅니다. 표준 본문은 수정하지 않았습니다.
개인·취미 등 비상업적 이용을 허용하고, 원문의 교육기관·공공연구기관 등 기관 허용 범위를
재원·관련 의무와 관계없이 그대로 수용합니다. 기업 지원 과제라는 이유만으로 교육기관의
SDK 사용을 표준 라이선스에서 제외하지 않습니다.

표준이 허용하는 범위를 벗어나는 상업적 SDK 이용은 권한 있는 권리자와의 별도 서면 허가
계약으로 관리합니다. 문의는 [공식 서비스](https://ionoflux.runvia.app)를 통해 운영자에게
연락해 주세요. 문의·결제·공개 이슈 작성만으로 허가가 성립하지 않으며 키나 계약의 비공개
정보를 공개 이슈에 올리지 마세요. 확인되지 않은 법인명·권리자 실명은 사용하지 않았습니다.

SDK 사본을 재배포할 때는 라이선스 본문(또는 공식 URL)과 [NOTICE](https://github.com/hongjunna/ionoflux-python/blob/main/NOTICE)의 다음
plain-text 고지를 함께 보존해야 합니다.

```text
Required Notice: IonoFlux (https://ionoflux.runvia.app)
```

API 접속·결과물의 IonoFlux 출처 표시는 별도 API 이용 조건의 영역입니다.
[API 약관 제안](https://github.com/hongjunna/ionoflux-python/blob/main/docs/api-terms-proposal.ko.md)은 **아직 최종 승인·시행되지 않은 초안**이며,
SDK 라이선스 채택만으로 기존 사이트 약관이나 화면/논문 출처 의무를 변경하지 않습니다.
소프트웨어 사본의 고지 보존을 모든 화면·산출물의 표시 의무로 확대하지 않습니다.

공급자의 원 라이선스·출처 조건은 독립적으로 유지됩니다. IonoFlux의 SDK 상업 허가나 API
이용 허가로 제3자의 NC·인용 조건이 해제되지 않습니다. 비상업 제한이 있으므로 OSI 의미의
오픈소스 라이선스라고 표시하지 않습니다.

[확정 정책·권리자 검토](https://github.com/hongjunna/ionoflux-python/blob/main/docs/licensing-review.ko.md) · [한영 이용 안내](https://github.com/hongjunna/ionoflux-python/blob/main/docs/readme-usage-draft.md) ·
[이용 사례](https://github.com/hongjunna/ionoflux-python/blob/main/docs/use-cases.ko.md) · [출처 예시](https://github.com/hongjunna/ionoflux-python/blob/main/docs/attribution-examples.md) ·
[API 약관 시행 전 검토](https://github.com/hongjunna/ionoflux-python/blob/main/docs/api-terms-preflight.ko.md)
