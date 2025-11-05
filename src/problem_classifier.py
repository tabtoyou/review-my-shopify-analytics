"""
구체적인 문제 분류기
쇼핑몰 운영자들의 질문을 구체적이고 액션 가능한 카테고리로 분류합니다.
각 카테고리는 실제 사업 기회로 연결될 수 있습니다.
"""

import json
import pandas as pd
from typing import List, Dict, Any
import re


# 구체적인 문제 카테고리 정의 (사업 기회 중심)
PROBLEM_CATEGORIES = {
    # 1. Product Presentation (제품 표현)
    "Product Photography Issues": {
        "keywords": ["photo", "image", "picture", "visual", "photography", "quality", "lighting"],
        "patterns": ["better photos", "improve images", "photo quality", "product shots"],
        "business_opportunity": "Product Photography Service / AI Photo Enhancement Tool"
    },
    "Product Description Problems": {
        "keywords": ["description", "copy", "content", "writing", "text", "details"],
        "patterns": ["better descriptions", "product copy", "write better", "describe"],
        "business_opportunity": "Copywriting Service / AI Description Generator"
    },
    "Product Selection Strategy": {
        "keywords": ["product selection", "niche", "what to sell", "product choice", "inventory"],
        "patterns": ["what products", "which items", "product ideas"],
        "business_opportunity": "Product Research Tool / Niche Finding Service"
    },

    # 2. Conversion Optimization (전환율 최적화)
    "Checkout Process Issues": {
        "keywords": ["checkout", "cart", "payment", "purchase", "buy button"],
        "patterns": ["checkout flow", "cart abandonment", "checkout page", "payment process"],
        "business_opportunity": "Checkout Optimization Service / One-Click Checkout Tool"
    },
    "Trust & Credibility Problems": {
        "keywords": ["trust", "credibility", "authentic", "legitimate", "scam", "reviews", "testimonial"],
        "patterns": ["build trust", "look legit", "seem real", "trust signals"],
        "business_opportunity": "Trust Badge Service / Review Management Platform"
    },
    "Value Proposition Unclear": {
        "keywords": ["value proposition", "unique", "differentiation", "why buy", "benefit"],
        "patterns": ["what makes", "why choose", "stand out", "different from"],
        "business_opportunity": "Brand Positioning Consulting / Value Prop Generator"
    },
    "Pricing Strategy Issues": {
        "keywords": ["price", "pricing", "cost", "expensive", "cheap", "affordable"],
        "patterns": ["pricing strategy", "how much", "price point", "too expensive"],
        "business_opportunity": "Dynamic Pricing Tool / Pricing Strategy Consulting"
    },

    # 3. User Experience (사용자 경험)
    "Mobile Responsiveness": {
        "keywords": ["mobile", "phone", "responsive", "tablet", "device"],
        "patterns": ["mobile version", "on phone", "mobile friendly", "responsive design"],
        "business_opportunity": "Mobile Optimization Service / Responsive Theme Builder"
    },
    "Page Speed & Performance": {
        "keywords": ["speed", "slow", "loading", "performance", "lag", "fast"],
        "patterns": ["load time", "site speed", "too slow", "loading speed"],
        "business_opportunity": "Performance Optimization Service / CDN Setup"
    },
    "Navigation & UX Flow": {
        "keywords": ["navigation", "menu", "find", "search", "browse", "ui", "ux"],
        "patterns": ["hard to find", "can't navigate", "menu structure", "user flow"],
        "business_opportunity": "UX Audit Service / Navigation Optimization Tool"
    },
    "Visual Design & Branding": {
        "keywords": ["design", "theme", "color", "font", "layout", "look", "aesthetic"],
        "patterns": ["design looks", "color scheme", "visual design", "brand identity"],
        "business_opportunity": "Design Service / Shopify Theme Customization"
    },

    # 4. Traffic & Marketing (트래픽 및 마케팅)
    "SEO & Organic Traffic": {
        "keywords": ["seo", "google", "search", "organic", "ranking", "traffic"],
        "patterns": ["seo optimization", "google ranking", "organic traffic", "search visibility"],
        "business_opportunity": "SEO Service / Keyword Research Tool"
    },
    "Content Marketing Strategy": {
        "keywords": ["content", "blog", "article", "story", "engagement"],
        "patterns": ["content strategy", "blog posts", "content marketing"],
        "business_opportunity": "Content Creation Service / Blog Automation Tool"
    },
    "Social Proof & Reviews": {
        "keywords": ["social proof", "review", "testimonial", "rating", "feedback"],
        "patterns": ["customer reviews", "social proof", "testimonials", "ratings"],
        "business_opportunity": "Review Collection Platform / Social Proof Widgets"
    },
    "Ad Campaign & Conversion": {
        "keywords": ["ads", "facebook", "instagram", "advertising", "campaign", "roas"],
        "patterns": ["ad performance", "facebook ads", "ad campaign"],
        "business_opportunity": "Ad Management Service / ROAS Optimization Tool"
    },

    # 5. Operations & Logistics (운영 및 물류)
    "Shipping & Fulfillment": {
        "keywords": ["shipping", "delivery", "fulfillment", "shipping cost", "free shipping"],
        "patterns": ["shipping strategy", "delivery time", "shipping costs"],
        "business_opportunity": "Shipping Optimization Tool / Fulfillment Service"
    },
    "Return & Refund Policy": {
        "keywords": ["return", "refund", "policy", "guarantee", "exchange"],
        "patterns": ["return policy", "refund process", "money back"],
        "business_opportunity": "Return Management Platform / Policy Template Service"
    },
    "Customer Support & Communication": {
        "keywords": ["support", "customer service", "help", "contact", "email", "chat"],
        "patterns": ["customer support", "customer service", "contact us"],
        "business_opportunity": "Chatbot Service / Customer Support Platform"
    },

    # 6. Email & Retention (이메일 및 고객 유지)
    "Email Marketing": {
        "keywords": ["email", "newsletter", "email marketing", "subscriber"],
        "patterns": ["email campaigns", "email list", "newsletter"],
        "business_opportunity": "Email Marketing Automation / Template Service"
    },
    "Customer Retention": {
        "keywords": ["retention", "repeat", "loyal", "comeback", "churn"],
        "patterns": ["repeat customers", "customer retention", "loyalty program"],
        "business_opportunity": "Loyalty Program Platform / Retention Tool"
    },
}


class ProblemClassifier:
    def __init__(self, data_path: str):
        """
        문제 분류기 초기화

        Args:
            data_path: Reddit 데이터 JSON 파일 경로
        """
        with open(data_path, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)

    def classify_post(self, post: Dict) -> List[str]:
        """
        게시물을 분석하여 해당하는 문제 카테고리 반환

        Args:
            post: 게시물 데이터

        Returns:
            해당하는 카테고리 리스트
        """
        text = f"{post.get('title', '')} {post.get('selftext', '')}".lower()
        matched_categories = []

        for category, config in PROBLEM_CATEGORIES.items():
            # 키워드 매칭
            keyword_matches = sum(1 for kw in config['keywords'] if kw in text)

            # 패턴 매칭
            pattern_matches = sum(1 for pattern in config['patterns'] if pattern in text)

            # 매칭 점수
            score = keyword_matches + (pattern_matches * 2)  # 패턴에 더 높은 가중치

            if score > 0:
                matched_categories.append((category, score))

        # 점수 순으로 정렬
        matched_categories.sort(key=lambda x: x[1], reverse=True)

        return [cat for cat, score in matched_categories]

    def classify_all_posts(self) -> pd.DataFrame:
        """
        모든 게시물 분류 및 통계 생성

        Returns:
            분류 결과 데이터프레임
        """
        results = []

        for post in self.raw_data:
            categories = self.classify_post(post)

            if categories:
                result = {
                    'post_id': post.get('id', ''),
                    'title': post.get('title', ''),
                    'primary_problem': categories[0] if categories else 'Unclassified',
                    'all_problems': ', '.join(categories[:3]),  # Top 3
                    'num_problems': len(categories),
                    'score': post.get('score', 0),
                    'num_comments': post.get('num_comments', 0),
                    'permalink': post.get('permalink', ''),
                }
                results.append(result)

        return pd.DataFrame(results)

    def get_problem_statistics(self) -> pd.DataFrame:
        """
        문제 카테고리별 통계

        Returns:
            카테고리별 통계 데이터프레임
        """
        category_counts = {cat: 0 for cat in PROBLEM_CATEGORIES.keys()}
        category_comments = {cat: [] for cat in PROBLEM_CATEGORIES.keys()}

        for post in self.raw_data:
            categories = self.classify_post(post)
            for category in categories:
                category_counts[category] += 1
                category_comments[category].append(post.get('num_comments', 0))

        stats = []
        for category, count in category_counts.items():
            if count > 0:
                stats.append({
                    'Problem Category': category,
                    'Frequency': count,
                    'Avg Comments': sum(category_comments[category]) / len(category_comments[category]) if category_comments[category] else 0,
                    'Business Opportunity': PROBLEM_CATEGORIES[category]['business_opportunity'],
                })

        df = pd.DataFrame(stats)
        df = df.sort_values('Frequency', ascending=False)
        return df

    def get_business_opportunities(self) -> pd.DataFrame:
        """
        사업 기회 분석 (문제 빈도 기반)

        Returns:
            사업 기회 데이터프레임
        """
        stats = self.get_problem_statistics()

        # 비즈니스 기회 우선순위 계산
        stats['Priority Score'] = stats['Frequency'] * stats['Avg Comments']
        stats = stats.sort_values('Priority Score', ascending=False)

        return stats[['Problem Category', 'Frequency', 'Business Opportunity', 'Priority Score']]


def main():
    """문제 분류 실행"""
    import glob
    import os

    # 가장 최근 데이터 파일 찾기
    data_files = glob.glob('data/reddit_data_*.json')
    if not data_files:
        print("✗ 데이터 파일을 찾을 수 없습니다.")
        return

    latest_file = max(data_files, key=os.path.getctime)
    print(f"📊 문제 분류 시작: {latest_file}\n")

    classifier = ProblemClassifier(latest_file)

    # 통계 출력
    stats = classifier.get_problem_statistics()
    print("=== 문제 카테고리별 통계 ===")
    print(stats.to_string(index=False))

    print("\n=== 사업 기회 우선순위 ===")
    opportunities = classifier.get_business_opportunities()
    print(opportunities.head(10).to_string(index=False))

    # CSV 저장
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    stats.to_csv(f'output/problem_categories_{timestamp}.csv', index=False, encoding='utf-8-sig')
    opportunities.to_csv(f'output/business_opportunities_{timestamp}.csv', index=False, encoding='utf-8-sig')

    print(f"\n✓ 결과 저장 완료: output/ 폴더")


if __name__ == "__main__":
    main()
