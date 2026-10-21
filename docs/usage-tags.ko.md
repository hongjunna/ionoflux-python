# SDK 요청 출처 태그(UTM) 명세

v0.1.2부터 IonoFlux Python SDK는 이용 통계에서 SDK 요청을 구분할 수 있도록 모든 요청에 고정 UTM 쿼리 파라미터를 붙입니다.

## 전송 값

| 파라미터 | 값 | 의미 |
|---|---|---|
| `utm_source` | `python` | 요청 언어/런타임이 Python |
| `utm_medium` | `sdk` | 공식 SDK를 통한 요청(직접 HTTP 호출과 구분) |
| `utm_content` | SDK 버전(예: `0.1.2`) | 버전별 채택률 확인 |

예: `GET https://ionoflux.runvia.app/v1/solar/flux?interval=1h&limit=100&utm_source=python&utm_medium=sdk&utm_content=0.1.2`

`User-Agent`도 `ionoflux-python/<SDK 버전>`으로 보냅니다(v0.1.1까지는 `0.1.0`으로 고정돼 있던 값을 실제 버전으로 교정).

## 규칙

- 값은 고정 상수이며 API 키·사용자·호스트·OS·Python 버전·환경 정보를 넣지 않습니다. API 키는 계속 `X-API-Key` 헤더로만 보내고 URL에는 넣지 않습니다.
- 인증 필요 엔드포인트와 공개 메타데이터(`sources()`, `data.status()`) 모두에 붙습니다.
- HTTPX `Client(params=...)` 기본 파라미터로 구현해 메서드별 쿼리(`interval`, `limit`, `category` 등)와 병합됩니다. SDK 공개 메서드는 `utm_*` 이름을 쓰지 않으므로 충돌하지 않습니다.
- 사용자 지정 `base_url`(스테이징 등)에도 동일하게 붙습니다. 끄는 옵션은 v0.1.2에 없습니다.
- 다른 언어 SDK를 추가할 때는 `utm_source`만 언어명으로 바꾸고 `utm_medium=sdk`, `utm_content=<버전>` 규칙을 유지합니다.
