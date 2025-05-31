# SEO 감사 웹 애플리케이션

Simple SEO Audit tools for small websites that comprehensively analyzes a website's SEO and generates reports.

## 주요 기능

1. **웹 크롤링 및 텍스트 분석**: 웹사이트를 크롤링하여 텍스트 데이터를 추출하고, 키워드 밀도 분석과 지식 그래프를 생성합니다.
2. **기술적 SEO 검사**: robots.txt, sitemap.xml, 사이트 구조, Core Web Vitals, 리다이렉트, 표준 링크 설정, 메타 태그 등을 분석합니다.
3. **온페이지 SEO 분석**: 상위 20개 페이지를 식별하고 각 페이지의 SEO 요소를 분석합니다.
4. **한국어 보고서 생성**: 현재 상태, 잠재적 이슈 및 기회, 중요 오류, 개선 방안을 포함한 종합 보고서를 한국어로 생성합니다.
5. **시각적 프레젠테이션**: 최소한의 색상과 효과적인 차트를 사용하여 시각적 프레젠테이션을 디자인합니다.
6. **다운로드 기능**: 보고서를 PPTX 및 PDF 형식으로 다운로드할 수 있습니다.

## 설치 방법

### 필수 요구사항

- Python 3.8 이상
- pip (Python 패키지 관리자)
- 가상 환경 (권장)

### 설치 단계

1. 가상 환경 생성 및 활성화:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows
```

2. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

3. 데이터베이스 초기화:
```bash
python init_db.py
```

## 실행 방법

1. 애플리케이션 실행:
```bash
python src/main.py
```

2. 웹 브라우저에서 다음 URL로 접속:
```
http://localhost:5000
```

## 프로덕션 환경 배포

프로덕션 환경에서는 다음과 같은 WSGI 서버를 사용하는 것을 권장합니다:

### Gunicorn 사용 (Linux/Mac)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 'src.main:app'
```

### Waitress 사용 (Windows)

```bash
pip install waitress
waitress-serve --port=5000 src.main:app
```

## 디렉토리 구조

```
seo_audit/
├── src/                    # 소스 코드
│   ├── analyzer/           # 분석 모듈
│   ├── crawler/            # 크롤링 모듈
│   ├── models/             # 데이터 모델
│   ├── presentation/       # 프레젠테이션 모듈
│   ├── report/             # 보고서 생성 모듈
│   ├── static/             # 정적 파일
│   │   ├── charts/         # 차트 이미지
│   │   ├── presentations/  # 프레젠테이션 파일
│   │   ├── reports/        # 보고서 파일
│   │   └── uploads/        # 업로드 파일
│   ├── templates/          # HTML 템플릿
│   └── main.py             # 메인 애플리케이션
├── init_db.py              # 데이터베이스 초기화 스크립트
├── requirements.txt        # 필요한 패키지 목록
└── README.md               # 이 파일
```

## 문제 해결

### 500 에러 발생 시

1. 로그 확인:
```bash
tail -f seo_audit.log
```

2. 데이터베이스 권한 확인:
```bash
chmod 666 src/seo_audit.db
```

3. 필요한 디렉토리가 모두 생성되었는지 확인:
```bash
mkdir -p src/static/{uploads,reports,charts,presentations}
```

4. 의존성 패키지가 모두 설치되었는지 확인:
```bash
pip install -r requirements.txt
```

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.