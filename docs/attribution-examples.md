# 출처 표시 예시 / Attribution examples

**Proposed guidance / 초안, 미시행.** 아래 예시는 향후 승인된 API 정책을 구현하는 방법이지 현재 발급된 Required Notice·라이선스·계약이 아니다. 실제 사용한 공급자·라이선스·버전·조회 기간으로 대체한다. 상업 이용 허가를 대신하지 않으며 공식 제휴/보증을 암시하지 않는다.

## 1. 웹사이트

차트 옆 credit 또는 쉽게 찾을 수 있는 출처 페이지에 링크를 제공하는 안:

```html
<p>
  Data via <a href="https://ionoflux.runvia.app">IonoFlux</a>.
  Kp source: <a href="https://kp.gfz.de/en/about-kp">GFZ Helmholtz Centre for Geosciences</a>,
  <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a>.
  Hourly aggregation by this project; timestamps are UTC.
</p>
```

이 예시는 GFZ source를 선택한 경우다. SWPC 기본 Kp를 쓰면서 GFZ라고 표시하지 않는다. 데이터셋의 권장 인용·DOI가 있으면 추가하며 가공 내용도 실제 수행한 경우에만 표시한다.

## 2. 애플리케이션

데이터 화면의 출처 링크나 정보/데이터 출처 화면:

> 데이터 경유: IonoFlux — https://ionoflux.runvia.app  
> 사용 지표·제공자: [실제 source/attribution.name]  
> 제공자 URL·라이선스: [응답과 원 정책 링크]  
> 관측 시각·단위: [UTC 시각] / [unit]  
> 앱의 처리: [변경 없음 또는 실제 집계/보간 방법]

SDK를 앱에 포함해 재배포하면 향후 채택된 코드 라이선스·고지도 라이선스 화면/번들에서 별도로 전달한다. API 결과만 화면으로 보여 주는 것과 SDK 사본 재배포는 같은 행위가 아니다.

## 3. 논문

데이터·방법 절 문안 후보:

> 우주기상 자료는 IonoFlux(https://ionoflux.runvia.app)를 통해 조회하였다. 원 자료 제공자는 [실제 제공자]이며 [데이터셋/버전/DOI], [조회 기간·조회일], [원 라이선스]를 따른다. 시각은 UTC, [실제 단위]이며 [집계/보간·결측 처리]를 적용하였다.

English candidate:

> Space-weather data were accessed through IonoFlux (https://ionoflux.runvia.app). Original provider: [provider]; dataset/version/DOI: [identifier]; period/access date: [dates]; original terms: [license]. Times are UTC. Processing and missing-data handling: [actual methods].

SILSO를 사용한 경우 [공식 인용 안내](https://sidc.be/SILSO/citations)의 DOI와 본문/그림·참고문헌 지침을 별도로 따른다. IonoFlux에 존재하지 않는 DOI나 논문 제목·저자·발행연도를 만들어 citation 파일을 발급하지 않는다. 원시 데이터를 논문에 재배포하는 권리도 별도 확인한다.

## 4. Python 프로젝트·노트북

프로젝트 README 또는 비공개 연구 노트의 출처 절:

```text
IonoFlux API: https://ionoflux.runvia.app
SDK: ionoflux v0.1.0 (record the actual source commit/release used)
Dataset/provider: [series.data['metric'], series.data['source']]
Provider attribution and terms: [series.data['attribution']]
Coverage/unit/time basis: [requested period], [unit], UTC
Transformations and missing-data handling: [actual method]
```

위 표시는 실행 코드가 아닌 작성 예시다. 키·Authorization/X-API-Key 헤더·개인 호출부호·원본 응답을 README/노트북 출력에 넣지 않는다. 통계 응답에는 attribution이 없으므로 source를 출처 목록과 연결한다. SDK 코드를 복사하거나 포함해서 배포할 때는 승인된 라이선스/고지 전달을 따르고, 단순 pip 의존성 선언과 실제 사본 배포를 구분한다.

## 5. CSV·차트·스크린샷

CSV sidecar/데이터 설명서 또는 그림 캡션에 IonoFlux URL, 실제 제공자·원 라이선스, 관측/조회 UTC 기간, 단위, 가공 내용과 결측 처리 정보를 남긴다. 잘라낸 이미지에서도 출처를 찾을 수 있게 캡션/메타데이터를 함께 배포하는 안이다. 매 숫자·로그마다 서비스명을 출력하는 방식이나 데이터의 외부 공개 자체를 요구하지 않는다.

후보 코드 고지 문구는 licensing-review.ko.md에서 검토한다. 여기의 UI/논문 예시는 표준 PolyForm의 고지 보존만으로 모든 사용에 자동 강제된다고 설명하지 않는다.
