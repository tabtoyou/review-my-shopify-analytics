"""
설정 파일
Reddit API 설정 및 기타 프로젝트 설정
"""

import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Reddit API 설정
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'ReviewMyShopify Analyzer v1.0')

# 크롤링 설정
SUBREDDIT_NAME = 'reviewmyshopify'
POST_LIMIT = 100  # 가져올 게시물 수 (None이면 모두)

# 데이터 저장 경로
DATA_DIR = 'data'
OUTPUT_DIR = 'output'

# 분석 키워드
ANALYSIS_KEYWORDS = [
    # 디자인 관련
    'design', 'layout', 'ui', 'ux', 'theme', 'template', 'color', 'font',
    # 기능 관련
    'navigation', 'checkout', 'payment', 'shipping', 'cart', 'search',
    # 콘텐츠 관련
    'product', 'description', 'image', 'photo', 'video', 'content',
    # 마케팅 관련
    'marketing', 'seo', 'traffic', 'conversion', 'sales', 'pricing', 'price',
    # 성능 관련
    'speed', 'loading', 'performance', 'mobile', 'responsive',
    # 신뢰도 관련
    'trust', 'credibility', 'review', 'testimonial', 'social proof',
]
