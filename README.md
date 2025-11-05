# Reddit r/reviewmyshopify 분석 도구

Reddit의 [r/reviewmyshopify](https://www.reddit.com/r/reviewmyshopify/) 서브레딧을 크롤링하고 분석하여, 쇼핑몰 운영자들이 어떤 것들을 궁금해하고, 어떤 조언을 받는지 정량적으로 분석하는 도구입니다.

## 📋 프로젝트 개요

r/reviewmyshopify는 Shopify 쇼핑몰을 운영하는 사람들이 자신의 쇼핑몰을 공유하고 피드백을 받는 커뮤니티입니다. 이 도구는 다음을 분석합니다:

- 쇼핑몰 운영자들이 **가장 많이 궁금해하는 것**
- 전문가들이 제공하는 **주요 조언 및 피드백**
- **어떤 답변이 높은 평가**를 받는지
- **커뮤니티 참여도** 및 활동 패턴
- **시간대별/요일별** 활동 분포

## 🎯 주요 기능

### 1. 데이터 크롤링 (`src/crawler.py`)
- Reddit API (PRAW)를 사용하여 게시물 및 댓글 수집
- 게시물 제목, 본문, URL, 점수, 댓글 등 모든 메타데이터 수집
- JSON 형식으로 데이터 저장

### 2. 데이터 분석 (`src/analyzer.py`)
- **키워드 분석**: 게시물과 댓글에서 자주 언급되는 키워드
- **참여도 분석**: 게시물 점수와 댓글 수의 상관관계
- **유용한 댓글 찾기**: 높은 점수를 받은 댓글 추출
- **질문 카테고리 분석**: 피드백 요청, 개선 질문, 전환율 등
- **상위 기여자 분석**: 가장 많이 도움을 준 사용자
- CSV 파일로 분석 결과 저장

### 3. 데이터 시각화 (`src/visualizer.py`)
- **키워드 분석 그래프**: 게시물 vs 댓글 키워드 비교
- **참여도 분석 그래프**: 점수, 댓글 수 분포
- **상위 기여자 그래프**: 댓글 수 및 총 점수 기준
- **시간대별 분포**: 시간대/요일별 게시물 활동
- **질문 카테고리 분석**: 어떤 질문이 많은지
- **종합 대시보드**: 모든 인사이트를 한눈에

## 🚀 설치 및 사용법

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd review-my-shopify-analytics

# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. Reddit API 설정 (선택사항)

Reddit API를 사용하려면 [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)에서 앱을 생성하세요.

1. "create another app..." 클릭
2. 이름 입력, "script" 선택
3. redirect uri에 `http://localhost:8080` 입력
4. client_id와 client_secret 복사

`.env` 파일 생성:

```bash
cp .env.example .env
```

`.env` 파일 편집:

```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=ReviewMyShopify Analyzer v1.0
```

> **참고**: Reddit API 설정이 없어도 읽기 전용 모드로 실행 가능합니다.

### 3. 실행

#### 전체 파이프라인 실행 (추천)

크롤링 → 분석 → 시각화를 한 번에 실행:

```bash
python main.py --all
```

게시물 수 제한:

```bash
python main.py --all --limit 50
```

#### 개별 단계 실행

**크롤링만 실행:**

```bash
python main.py --crawl
```

**분석만 실행:**

```bash
python main.py --analyze
```

**시각화만 실행:**

```bash
python main.py --visualize
```

## 📊 결과 파일

실행 후 다음 디렉토리에 결과가 저장됩니다:

### `data/` - 원본 데이터
- `reddit_data_YYYYMMDD_HHMMSS.json`: 크롤링된 원본 데이터

### `output/` - 분석 결과

**CSV 파일:**
- `basic_stats_*.json`: 기본 통계 정보
- `post_keywords_*.csv`: 게시물 키워드 분석
- `comment_keywords_*.csv`: 댓글 키워드 분석
- `engagement_*.csv`: 참여도 분석
- `helpful_comments_*.csv`: 유용한 댓글 목록
- `top_contributors_*.csv`: 상위 기여자 목록

**그래프 (PNG):**
- `keywords_*.png`: 키워드 분석 그래프
- `engagement_*.png`: 참여도 분석 그래프
- `contributors_*.png`: 상위 기여자 그래프
- `time_distribution_*.png`: 시간대별 분포
- `question_categories_*.png`: 질문 카테고리 분석
- `dashboard_*.png`: 종합 대시보드

## 📈 분석 인사이트 예시

이 도구를 통해 다음과 같은 인사이트를 얻을 수 있습니다:

1. **쇼핑몰 운영자들이 가장 많이 궁금해하는 주제**
   - 디자인, 레이아웃, 테마
   - 결제 프로세스
   - SEO 및 마케팅
   - 제품 설명 및 이미지

2. **전문가들이 자주 제공하는 조언**
   - 모바일 반응형 디자인
   - 페이지 로딩 속도
   - 신뢰도 향상 (리뷰, 소셜 프루프)
   - 네비게이션 개선

3. **높은 평가를 받는 답변의 특징**
   - 구체적이고 실행 가능한 조언
   - 전후 비교 예시 제공
   - 기술적 근거 제시

## 🛠 기술 스택

- **Python 3.7+**
- **PRAW**: Reddit API 클라이언트
- **Pandas**: 데이터 분석 및 처리
- **Matplotlib & Seaborn**: 데이터 시각화
- **python-dotenv**: 환경 변수 관리

## 📁 프로젝트 구조

```
review-my-shopify-analytics/
├── src/
│   ├── crawler.py       # Reddit 크롤러
│   ├── analyzer.py      # 데이터 분석기
│   └── visualizer.py    # 데이터 시각화
├── data/                # 크롤링 데이터 (JSON)
├── output/              # 분석 결과 (CSV, PNG)
├── config.py            # 설정 파일
├── main.py              # 메인 실행 파일
├── requirements.txt     # Python 의존성
├── .env.example         # 환경 변수 예시
├── .gitignore
└── README.md
```

## ⚙️ 설정 커스터마이징

`config.py` 파일에서 다음을 조정할 수 있습니다:

- `POST_LIMIT`: 크롤링할 게시물 수 (기본: 100)
- `ANALYSIS_KEYWORDS`: 분석할 키워드 목록
- `DATA_DIR`, `OUTPUT_DIR`: 데이터 저장 경로

## 🔍 사용 예시

```bash
# 최근 50개 게시물 분석
python main.py --all --limit 50

# 크롤링 후 나중에 분석
python main.py --crawl --limit 100
python main.py --analyze
python main.py --visualize
```

## 📝 라이선스

이 프로젝트는 교육 및 연구 목적으로 작성되었습니다. Reddit의 API 이용 약관을 준수하여 사용하세요.

## 🤝 기여

버그 리포트, 기능 제안, Pull Request를 환영합니다!

## 📧 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록해주세요.

---

**Made with ❤️ for Shopify entrepreneurs**
