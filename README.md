# 📊 Log Data Classifier & Step Quality Analyzer (Portable)

로그 데이터를 자동으로 파싱하여 **4단계 계층(업체 > Model > Step > Pass/Fail)**으로 자동 분류하고, **공정 단계별 품질 및 결함 특징을 심층 분석**하여 **인터랙티브 웹 대시보드(HTML Report)**로 출력해주는 포터블 프로그램입니다.

---

## 🌟 주요 특징

1. **포터블(Portable) 단독 실행 지원**:
   - 파이썬이 설치되지 않은 윈도우 PC에서도 `LogDataAnalyzer_Portable.exe`를 더블클릭하여 즉시 실행 가능합니다.
   - 친절한 데스크톱 그래픽 인터페이스(GUI) 및 자동화용 커맨드라인(CLI)을 모두 지원합니다.
2. **엄격한 4단계 계층 분류**:
   - **1순위 (업체)**: `Vendor_A`, `Vendor_B`, `Vendor_C`, `Vendor_D`
   - **2순위 (Model)**: `Model_A (8")`, `Model_B (15"/24")`, `Model_C (12.1")`, `Model_D (13.3")`
   - **3순위 (Step)**: `Step03_Sensor_FPC_Assy`, `Step04_Touch_Panel_Assy`, `Step05_Touch_Panel_Assy_Pekotti`, `Module_Assy`, `Sensor_FPC_Assy`, `Touchpanel_Assy`
   - **4순위 (Pass/Fail)**: `PASS`, `FAIL`
3. **단계별 품질 및 결함 특징 심층 분석**:
   - 공정 단계별 Pass/Fail 수량, 양품률(Yield), 불량률(Defect Rate) 실시간 집계
   - 실패 검사 항목(Failed Sub-steps TOP 랭킹) 및 결함 원인 파레토(Pareto) 분석
   - 검사 소요 시간(평균/Pass/Fail) 비교 분석
   - 단계별 공정 특징 및 엔지니어링 인사이트(Insights) 자동 도출
4. **미려한 독립형 웹 대시보드 리포트 (`output/report.html`)**:
   - 외부 인터넷 연결 없이 사내 폐쇄망/클린룸에서도 100% 동작하는 인라인 SVG 차트(도넛, 바, 파레토) 탑재
   - 실시간 검색/필터링 가능한 1,152건 개별 로그 탐색기 및 엑셀용 CSV 다운로드 기능
   - 보고용 인쇄(Print/PDF) 최적화 스타일링

---

## 📁 실행 방법

### 방법 1: 포터블 실행 파일 (추천)
- 프로젝트 폴더의 **`LogDataAnalyzer_Portable.exe`** 를 더블클릭합니다.
- GUI 창에서 입력 Data 폴더와 출력 Output 폴더를 확인 후 **[🚀 분류 및 분석 시작]** 버튼을 클릭합니다.
- 처리가 완료(약 3초 소요)되면 자동으로 브라우저에 **웹 리포트**가 열립니다.

### 방법 2: 커맨드라인(CLI) 실행
```bash
# 기본 실행 (Data -> output 자동 처리 후 브라우저 리포트 오픈)
.\LogDataAnalyzer_Portable.exe

# 옵션 지정 실행
.\LogDataAnalyzer_Portable.exe --data ./Data --output ./output --no-gui
```

### 방법 3: 파이썬 소스로 직접 실행
```bash
python main.py
# 또는 CLI
python main.py --no-gui
```

---

## 📊 데이터 분석 결과 요약 (1,152건)

### 1. 종합 품질 현황
| 구분 | 수량 (건) | 비율 (%) | 비고 |
| :--- | :---: | :---: | :--- |
| **총 검사 수량** | **1,152** | 100.0% | 4개 업체군, 5개 모델, 6개 공정 단계 |
| **합격 (PASS)** | **540** | **46.88%** | 전체 양품 수량 |
| **불합격 (FAIL)** | **612** | **53.12%** | 결함 분석용 타겟 샘플군 포함 |

### 2. 업체군(Vendor)별 품질 현황
| 업체 구분 | 총 수량 | PASS | FAIL | 양품률 (%) | 불량률 (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Vendor_A** | 274 | 272 | 2 | 98.9% | 0.73% |
| **Vendor_B** | 117 | 117 | 0 | 100.0% | 0.00% |
| **Vendor_C** | 119 | 113 | 6 | 95.0% | 5.04% |
| **Vendor_D** | 642 | 38 | 604 | 5.9% | 94.08% |

---

## 🔬 공정 단계(Step)별 세부 특징 및 결함 분석

### 1. `Step03_Sensor_FPC_Assy` (Vendor_D 13.3" CTP 열압 공정)
- **수량 현황**: 총 591건 | PASS: 30건 | **FAIL: 561건 (불량률 94.92%)**
- **평균 검사시간**: 19.6초
- **주요 실패 서브스텝 TOP 5**:
  1. `8. Baseline`: 473건 (84.3%)
  2. `6. Self Test Pin Leakage`: 82건 (14.6%)
  3. `2. Device Firmware Revision`: 6건
  4. `9. Untouched Deltas`: 2건
  5. `3. Device ID`: 1건
- **공정 특징 및 인사이트**:
  - 센서 FPC를 터치패널에 열압(Heat-press) 직후 수행하는 1차 검사 단계입니다.
  - 열압 공정의 압력/온도 편차 및 ACF 접합 정렬 오차로 인해 전극 저항이 기준치를 벗어나는 **Baseline Out-of-Spec**이 압도적 다수를 차지합니다.
  - 전극 간 미세 단락으로 인한 **Pin Leakage(누설전류)** 불량도 다수 발생하여 열압 지그의 압력 밸런스 재교정이 필요합니다.

### 2. `Step04_Touch_Panel_Assy` (Vendor_D 13.3" 터치패널 1차 결합)
- **수량 현황**: 총 42건 | PASS: 8건 | **FAIL: 34건 (불량률 80.95%)**
- **평균 검사시간**: 18.3초
- **주요 실패 서브스텝**:
  1. `6. Self Test Pin Leakage`: 22건 (64.7%)
  2. `8. Baseline`: 12건 (35.3%)
- **공정 특징 및 인사이트**:
  - 1차 Touch Panel Assembly 후 주요 결함을 검출하는 공정입니다.
  - 조립 스트레스로 인한 인터페이스 핀 누설 전류 및 Baseline Sensor Pin Open 결함이 집중 검출되었습니다.

### 3. `Step05_Touch_Panel_Assy_Pekotti` (Vendor_D 13.3" 터치패널 2차 결합)
- **수량 현황**: 총 9건 | PASS: 0건 | **FAIL: 9건 (불량률 100.0%)**
- **평균 검사시간**: 17.9초
- **주요 실패 서브스텝**: `8. Baseline` (5건), `6. Self Test Pin Leakage` (4건)
- **공정 특징 및 인사이트**:
  - 고난도 조립 공정품으로, 이전 단계의 잔류 결함 및 2차 조립 시 전극 손상이 주된 원인입니다.

### 4. `Sensor_FPC_Assy` (Vendor_B 15" & 24" 센서)
- **수량 현황**: 총 117건 (15": 43건, 24": 74건) | **PASS: 117건 (양품률 100.0%)** | FAIL: 0건
- **평균 검사시간**: 16.8초
- **공정 특징 및 인사이트**:
  - 전수 100% 양품으로 공정이 극히 안정적입니다.
  - **특이사항**: 대화면(24인치) 모델의 경우 `9. Baseline > Failed (Warning)`이 70건 감지되었습니다. 최종 Pass 판정이지만 센서 면적 확대에 따른 신호 노이즈 마진을 예방 차원에서 모니터링할 필요가 있습니다.

### 5. `Module_Assy` (Vendor_C 12.1" 완성 모듈)
- **수량 현황**: 총 119건 | PASS: 113건 | **FAIL: 6건 (불량률 5.04%)**
- **평균 검사시간**: 45.0초
- **주요 실패 원인**:
  1. `10. Untouched Deltas`: 5건 (83.3%)
  2. `1. Scan Barcode`: 1건 (16.7%)
- **공정 특징 및 인사이트**:
  - 95%의 높은 양품률을 유지하고 있습니다.
  - 주요 불량인 `Untouched Deltas`는 디스플레이 및 본딩 결합 후 발생하는 기생 정전용량(Parasitic Capacitance) 오프셋 드리프트가 원인입니다.

### 6. `Touchpanel_Assy` (Vendor_A 8" 센서 패널)
- **수량 현황**: 총 274건 | PASS: 272건 | **FAIL: 2건 (불량률 0.73%)**
- **평균 검사시간**: 75.8초
- **주요 실패 원인**: `2. Device Firmware Revision` 통신/버전 불일치
- **공정 특징 및 인사이트**:
  - 99%에 육박하는 초고수율 공정입니다. 불량 2건은 센서 자체 결함이 아닌 검사 지그 펌웨어 버전 불일치로 판명되었습니다.

---

## 📂 출력 디렉토리 계층 구조 예시 (`output/`)

```text
output/
├── report.html                                    <-- 📊 인터랙티브 웹 대시보드 리포트
├── Vendor_A/                                     <-- 1. 업체 (Vendor)
│   └── 8_Inch_Model_A/                           <-- 2. Model
│       └── Touchpanel_Assy/                      <-- 3. Step
│           ├── PASS/  (272 files)                <-- 4. Pass / Fail
│           └── FAIL/  (2 files)
├── Vendor_B/
│   ├── 15_Inch_Model_B/
│   │   └── Sensor_FPC_Assy/
│   │       └── PASS/  (43 files)
│   └── 24_Inch_Model_B/
│       └── Sensor_FPC_Assy/
│           └── PASS/  (74 files)
├── Vendor_C/
│   └── 12.1_Inch_Model_C/
│       └── Module_Assy/
│           ├── PASS/  (113 files)
│           └── FAIL/  (6 files)
└── Vendor_D/
    └── 13.3_Inch_Model_D/
        ├── Step03_Sensor_FPC_Assy/
        │   ├── PASS/  (30 files)
        │   └── FAIL/  (561 files)
        ├── Step04_Touch_Panel_Assy/
        │   ├── PASS/  (8 files)
        │   └── FAIL/  (34 files)
        └── Step05_Touch_Panel_Assy_Pekotti/
            └── FAIL/  (9 files)
```
