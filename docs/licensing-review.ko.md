# SDK 라이선스 확정 정책 및 검토 기록

**SDK 코드 정책 채택: 2026-10-20 / API 약관 초안은 미시행.** 사용자는 PolyForm Noncommercial License 1.0.0 원문과 그 기관 예외를 그대로 수용했다. 이전의 “후보·결정 보류” 상태는 이 결정으로 대체한다. 이 결정은 SDK LICENSE·문서·메타데이터 반영 승인이고, PR 병합·TestPyPI/PyPI 게시·API 약관 시행 승인은 아니다.

## 확정한 원칙

SDK 코드는 [공식 PolyForm Noncommercial 1.0.0](https://polyformproject.org/licenses/noncommercial/1.0.0)을 수정 없이 적용한다. 개인·취미 등 비상업 목적과 원문의 교육기관·공공연구기관 등 기관 허용 범위를 수용한다. 기관의 자금 출처·자금에 따른 의무만으로 표준 허용을 축소하지 않는다. 표준 밖의 상업적 SDK 사용은 별도 서면 계약으로 관리하며, 그 계약은 권리자가 실제 보유한 권한 범위에서 체결해야 한다.

SDK 사본 재배포의 라이선스·고지 보존과 API 접속·결과물의 출처 표시를 분리한다. API 약관은 기존 초안 상태를 유지하고 법률·공급자 권리 검토 및 최종 승인·통지/동의 절차를 거치기 전 시행하지 않는다. 제3자 데이터의 원 조건도 독립적으로 유지한다.

## 공식 원문 보존 근거

LICENSE는 공식 사이트 [plain text](https://polyformproject.org/licenses/noncommercial/1.0.0.txt)를 바이트 그대로 복사했다. SHA256:

`ffcca38841adb694b6f380647e15f17c446a4d1656fed51a1e2041d064c94cc8`

[공식 저장소 버전](https://github.com/polyformproject/polyform-licenses/blob/1.0.0/PolyForm-Noncommercial-1.0.0.md)과는 줄바꿈/공백 형식만 다르고 공백을 제외한 내용은 일치한다. 원문 속 예시 회사명은 표준의 설명용 예시일 뿐 IonoFlux 권리자 명의가 아니다. 이를 프로젝트 법인명으로 치환하거나 추가 제한을 본문에 삽입하지 않았다. `.gitattributes`는 LICENSE/NOTICE의 checkout 줄바꿈 변환을 막고, 배포 검사는 공식 LICENSE 해시를 확인한다.

SPDX 식별자는 [공식 SPDX 목록](https://spdx.org/licenses/PolyForm-Noncommercial-1.0.0.html)의 `PolyForm-Noncommercial-1.0.0`을 사용한다. pyproject의 license expression과 license-files를 명시하며 wheel/sdist에 LICENSE·NOTICE 원문과 해당 License-File 메타데이터를 포함한다.

## 권리자 명의·저작권 검토

직접 확인 가능한 사실은 저장소 소유자 계정 `hongjunna`, Git 기여 이력, 서비스명 IonoFlux와 사용자 승인이다. 저장소 관리권이나 author 표시만으로 법적 권리 귀속·고용/양도 관계까지 입증했다고 보지 않는다. 법인 등록명·권리자 실명·계약 서명권은 이 작업에서 확인되지 않았다. 따라서 임의의 법인명·copyright 연도/실명·메타데이터 author를 추가하지 않았다.

채택된 표준에는 프로젝트용 권리자 이름을 채워 넣어야 하는 필드가 없다. Required Notice는 아래의 사실로 확인된 서비스 식별 정보만 사용한다. 상업 계약 체결·외부 권리 보증 전에는 실제 권리자/대리권, 기여자 및 고용·양도 관계, 제3자 코드/의존성의 독립 라이선스를 별도로 확인한다. 미확정 법인명을 사용하지 않는 것은 SDK 표준 본문을 수정하거나 적용을 보류할 이유가 아니다.

## 실제 Required Notice

별도 NOTICE 파일에 다음 한 줄을 발급했다. 서비스 식별 고지이며 법인이나 copyright 소유권 주장을 만들지 않는다.

```text
Required Notice: IonoFlux (https://ionoflux.runvia.app)
```

SDK 사본을 전달할 때 표준이 요구하는 라이선스/공식 URL 및 plain-text 고지를 함께 전달한다. wheel은 `.dist-info/licenses/LICENSE`·`NOTICE`, sdist는 루트의 LICENSE·NOTICE에 넣고 메타데이터에도 선언한다. 배포 검사는 누락·변조·SPDX 불일치를 거부한다.

고지 보존은 백엔드에서 SDK만 실행하고 데이터·그림만 공개하는 경우의 모든 화면/논문 credit 의무를 자동으로 만들지 않는다. 그런 API 서비스 의무는 별도 약관에서 검토한다. 고지 문장에 화면 의무를 몰래 추가하거나 표준 본문에 제한을 더하지 않는다.

## 세 권리 층과 문의

| 층 | 현재 상태 | 적용·문의 범위 |
|---|---|---|
| SDK 코드 | PolyForm Noncommercial 1.0.0 채택 | 표준 목적·기관 허용, 사본 고지 보존. 범위 밖 상업 이용은 권한 있는 권리자의 별도 서면 계약 |
| API 서비스 | 기존 조건 유지, 새 초안 미시행 | IonoFlux 표시·상업 접속·한도·정지·동의 등을 별도 승인 후 관리 |
| 제3자 데이터 | 원 제공자 조건 유지 | source/attribution·인용·NC/변경/재배포 제한을 개별 확인 |

상업 이용 문의는 공식 서비스 https://ionoflux.runvia.app 를 통해 운영자에게 전달한다. 구체적인 계약 주체·승인 담당·문의 절차는 서면 계약 전에 확인한다. 공개 이슈 작성·유료 결제는 허가로 간주하지 않고 키/계약 기밀을 공개하지 않는다. SDK 라이선스가 다른 HTTP 클라이언트의 API 접속 권한이나 제3자 데이터의 상업 재허가를 대신하지 않는다.

## 기관 예외·상업 사례

이용 사례 문서의 SDK 열은 이제 채택된 표준의 예비 해석이다. 대학 산학 과제 등의 기관 허용을 일률적인 광고/수익 금지 안내로 축소하지 않는다. 별도 대학 영리 자회사나 일반 기업의 R&D를 교육기관으로 자동 취급하지도 않는다. 애매한 연구 목적·기관 성격과 법정 권리는 실제 사실관계로 검토한다. API 열은 여전히 미승인 운영 정책 제안이다.

비상업 제한은 [OSI 정의](https://opensource.org/osd)의 사업 분야 제한 금지와 맞지 않으므로 “OSI 오픈소스”라고 설명하지 않는다. 표준을 변형하는 안은 이번에 채택하지 않았다. [PolyForm 프로젝트 지침](https://github.com/polyformproject/polyform-licenses/blob/1.0.0/README.md)의 수정본 명칭 조건도 회피하지 않는다.

## 공급자 권리·시행 전 잔여

[GFZ](https://kp.gfz.de/en/about-kp), [SILSO](https://sidc.be/SILSO/citations), [CC BY](https://creativecommons.org/licenses/by/4.0/deed.en), [CC BY-NC](https://creativecommons.org/licenses/by-nc/4.0/deed.en)의 원 조건을 SDK 라이선스로 재정의하지 않는다. API 접속 계약으로 원 데이터에 이미 부여된 권리를 소급 제한하거나 IonoFlux가 갖지 않은 권리를 재허가한다고 약속하지 않는다.

상세한 법률·원 제공자 권리·동의/시행 검토 항목은 api-terms-preflight.ko.md에 정리했다. API 약관 최종 승인, 상업 계약 주체/권한, 패키지 계정·이름/Publisher 설정, PR 병합·각 외부 게시 승인은 별도 잔여다. SDK 라이선스 선택 자체는 더 이상 미결 항목이 아니다.
