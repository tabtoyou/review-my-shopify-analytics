"""
쇼핑몰 정보 추출기 (웹 스크래핑 포함)
Reddit 게시물에서 쇼핑몰 정보를 추출하고, 실제 웹사이트를 방문하여 추가 정보를 수집합니다.
"""

import re
import json
from urllib.parse import urlparse
import pandas as pd
from typing import List, Dict, Any, Optional
import os
import sys
import requests
from bs4 import BeautifulSoup
import time

# problem_classifier import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.problem_classifier import ProblemClassifier, PROBLEM_CATEGORIES


class ShopInfoExtractor:
    def __init__(self, data_path: str):
        """
        쇼핑몰 정보 추출기 초기화

        Args:
            data_path: Reddit 데이터 JSON 파일 경로
        """
        with open(data_path, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        # 문제 분류기 초기화
        self.classifier = ProblemClassifier(data_path)

    def extract_urls_from_text(self, text: str) -> List[str]:
        """텍스트에서 URL 추출"""
        # URL 패턴
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)

        # myshopify.com 도메인이 아닌 경우도 추출
        domain_pattern = r'(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?)'
        domains = re.findall(domain_pattern, text)

        # 도메인을 URL 형식으로 변환
        for domain in domains:
            if domain not in text:
                urls.append(f"https://{domain}")

        return list(set(urls))

    def extract_email_from_text(self, text: str) -> str:
        """텍스트에서 이메일 추출"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ""

    def get_domain_name(self, url: str) -> str:
        """URL에서 도메인 이름 추출"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            # www. 제거
            domain = domain.replace('www.', '')
            # myshopify.com에서 스토어 이름 추출
            if 'myshopify.com' in domain:
                store_name = domain.replace('.myshopify.com', '')
                return store_name
            return domain.split('.')[0] if domain else ""
        except:
            return ""

    def clean_url(self, url: str) -> str:
        """
        URL 정리 및 정규화
        - Markdown 형식 제거
        - 괄호, 대괄호 제거
        - 개별 페이지를 홈페이지로 변환
        - 쿼리 파라미터 제거
        """
        try:
            # 1. Markdown 링크 형식 제거: [text](url) → url
            if '](http' in url:
                # [text](url) 형식에서 url 부분만 추출
                url = url.split('](')[1] if '](http' in url else url

            # 2. 괄호, 대괄호 제거
            url = url.rstrip(')')
            url = url.rstrip(']')
            url = url.lstrip('[')

            # 3. URL 파싱
            parsed = urlparse(url)

            # 4. 개별 페이지를 홈페이지로 변환
            path = parsed.path

            # /products/, /collections/, /blogs/, /pages/ 등은 제거
            unwanted_paths = ['/products/', '/collections/', '/blogs/', '/pages/', '/apps/']
            for unwanted in unwanted_paths:
                if unwanted in path:
                    path = '/'
                    break

            # /s/, /p/ 같은 단축 경로도 제거
            if path.startswith('/s/') or path.startswith('/p/'):
                path = '/'

            # 5. 깨끗한 URL 재구성
            if not parsed.scheme:
                # scheme이 없으면 https 추가
                url = f"https://{url}"
                parsed = urlparse(url)

            clean = f"{parsed.scheme}://{parsed.netloc}{path}"
            clean = clean.rstrip('/')

            return clean

        except Exception as e:
            # 정리 실패 시 원본 반환 (최소한 괄호는 제거)
            return url.rstrip(')').rstrip(']')

    def fetch_page_content(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        웹페이지 HTML 가져오기

        Args:
            url: 웹페이지 URL
            timeout: 타임아웃 (초)

        Returns:
            HTML 콘텐츠 또는 None
        """
        try:
            response = self.session.get(url, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  ⚠ 페이지 가져오기 실패 ({url}): {str(e)[:50]}")
            return None

    def extract_email_from_page(self, html: str) -> str:
        """
        HTML에서 이메일 추출

        Args:
            html: HTML 콘텐츠

        Returns:
            이메일 주소 또는 빈 문자열
        """
        if not html:
            return ""

        soup = BeautifulSoup(html, 'html.parser')

        # 1. mailto: 링크에서 찾기
        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.I))
        if mailto_links:
            email = mailto_links[0]['href'].replace('mailto:', '').split('?')[0]
            if '@' in email:
                return email.strip()

        # 2. 텍스트에서 이메일 패턴 찾기
        text = soup.get_text()
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)

        # 일반적인 이메일 제외 (privacy, noreply 등)
        valid_emails = [
            email for email in emails
            if not any(exclude in email.lower() for exclude in
                      ['privacy', 'noreply', 'no-reply', 'example', 'test', 'wixpress', 'shopify'])
        ]

        return valid_emails[0] if valid_emails else ""

    def find_email_from_common_pages(self, base_url: str) -> str:
        """
        Contact Us, About Us 등 일반적인 페이지에서 이메일 찾기

        Args:
            base_url: 웹사이트 기본 URL

        Returns:
            발견된 이메일 주소 또는 빈 문자열
        """
        # 시도할 페이지 경로들 (우선순위 순)
        contact_paths = [
            '/contact',
            '/contact-us',
            '/contactus',
            '/contact_us',
            '/about',
            '/about-us',
            '/aboutus',
            '/about_us',
            '/pages/contact',
            '/pages/contact-us',
            '/pages/about',
            '/pages/about-us',
        ]

        base_url = base_url.rstrip('/')

        for path in contact_paths:
            try:
                page_url = f"{base_url}{path}"
                html = self.fetch_page_content(page_url, timeout=8)

                if html:
                    email = self.extract_email_from_page(html)
                    if email:
                        return email

                # Rate limiting (각 페이지 사이 0.5초)
                time.sleep(0.5)

            except Exception as e:
                continue

        return ""

    def get_shopify_product_count(self, url: str) -> int:
        """
        Shopify 스토어의 상품 수 가져오기 (/products.json API 사용)

        Args:
            url: Shopify 스토어 URL

        Returns:
            상품 수
        """
        try:
            products_url = f"{url.rstrip('/')}/products.json?limit=1"
            response = self.session.get(products_url, timeout=10)
            response.raise_for_status()

            data = response.json()

            # 전체 상품 수를 정확히 알려면 모든 페이지를 순회해야 하지만,
            # 여기서는 간단히 첫 페이지의 상품 수만 확인
            # 더 정확하게 하려면 페이지네이션 필요

            # 간단한 방법: 최대 250개까지 한 번에 가져오기
            products_url = f"{url.rstrip('/')}/products.json?limit=250"
            response = self.session.get(products_url, timeout=10)
            data = response.json()

            return len(data.get('products', []))

        except Exception as e:
            return 0

    def extract_categories_from_page(self, html: str, url: str) -> str:
        """
        HTML에서 카테고리/도메인 정보 추출

        Args:
            html: HTML 콘텐츠
            url: 웹사이트 URL

        Returns:
            카테고리 문자열
        """
        if not html:
            return ""

        soup = BeautifulSoup(html, 'html.parser')
        categories = set()

        # 1. 메타 태그에서 카테고리 찾기
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            keywords = meta_keywords['content'].split(',')
            categories.update([k.strip() for k in keywords[:5]])

        # 2. 메타 디스크립션에서 키워드 추출
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc = meta_desc['content'].lower()
            # 일반적인 카테고리 키워드
            common_categories = [
                'fashion', 'clothing', 'jewelry', 'accessories', 'beauty', 'cosmetics',
                'home', 'decor', 'furniture', 'art', 'craft', 'handmade',
                'electronics', 'gadgets', 'tech', 'fitness', 'health', 'wellness',
                'food', 'beverage', 'coffee', 'tea', 'organic',
                'kids', 'baby', 'toys', 'pet', 'sports', 'outdoor',
                'books', 'education', 'gifts', 'vintage', 'sustainable'
            ]
            for cat in common_categories:
                if cat in desc:
                    categories.add(cat.title())

        # 3. 네비게이션 메뉴에서 카테고리 찾기
        nav_links = soup.find_all(['nav', 'header'])
        for nav in nav_links:
            links = nav.find_all('a', limit=10)
            for link in links:
                text = link.get_text().strip()
                if text and len(text) < 30 and not text.lower().startswith('http'):
                    # 일반적인 네비게이션 텍스트 제외
                    if text.lower() not in ['home', 'about', 'contact', 'cart', 'search', 'login', 'signup']:
                        categories.add(text)

        # 상위 5개만 반환
        return ', '.join(list(categories)[:5]) if categories else ""

    def is_valid_shop_url(self, url: str) -> bool:
        """
        쇼핑몰 URL인지 검증

        Args:
            url: 검증할 URL

        Returns:
            유효한 쇼핑몰 URL이면 True
        """
        # 제외할 패턴들
        invalid_patterns = [
            'apps.shopify.com',      # Shopify 앱 스토어
            'community.shopify.com', # Shopify 커뮤니티
            'help.shopify.com',      # Shopify 헬프
            'linkedin.com',
            'facebook.com',
            'instagram.com',
            'twitter.com',
            'youtube.com',
            'tiktok.com',
            'pinterest.com',
        ]

        url_lower = url.lower()
        return not any(pattern in url_lower for pattern in invalid_patterns)

    def extract_shop_info_with_scraping(self) -> List[Dict[str, Any]]:
        """
        모든 게시물에서 쇼핑몰 정보 추출 (웹 스크래핑 포함)
        """
        shops = []

        print(f"📊 {len(self.raw_data)}개의 게시물에서 쇼핑몰 정보 추출 중...\n")

        for idx, post in enumerate(self.raw_data, 1):
            # 텍스트 결합
            text = f"{post.get('title', '')} {post.get('selftext', '')} {post.get('url', '')}"

            # URL 추출
            urls = self.extract_urls_from_text(text)

            # Reddit 링크 필터링 (실제 쇼핑몰 URL만)
            shop_urls = [
                url for url in urls
                if 'reddit.com' not in url and
                   'redd.it' not in url and
                   len(url) > 10
            ]

            if not shop_urls:
                continue

            # 첫 번째 URL을 주 사이트로 사용 (정리 및 검증)
            main_url = self.clean_url(shop_urls[0])

            # URL 유효성 검증 (SNS, 앱 스토어 등 제외)
            if not self.is_valid_shop_url(main_url):
                print(f"  [{idx}/{len(self.raw_data)}] 건너뛰기: {main_url} (유효하지 않은 URL)")
                continue
            domain_name = self.get_domain_name(main_url)
            # 초기 Shopify 감지 (URL 기반)
            is_shopify = "myshopify.com" in main_url or ".myshopify.com" in main_url

            print(f"  [{idx}/{len(self.raw_data)}] 처리 중: {domain_name}... ", end='', flush=True)

            # 웹 스크래핑으로 추가 정보 수집
            email = ""
            product_count = 0
            categories = ""

            try:
                html = self.fetch_page_content(main_url, timeout=10)

                if html:
                    # 이메일 추출 (메인 페이지)
                    email = self.extract_email_from_page(html)

                    # 메인 페이지에서 이메일을 못 찾으면 Contact/About 페이지 시도
                    if not email:
                        email = self.find_email_from_common_pages(main_url)

                    # 카테고리 추출
                    categories = self.extract_categories_from_page(html, main_url)

                    # 모든 URL에 대해 Shopify products.json 시도
                    # (커스텀 도메인을 사용하는 Shopify 스토어 감지)
                    product_count = self.get_shopify_product_count(main_url)

                    # products.json이 성공하면 Shopify 스토어로 확인
                    if product_count > 0:
                        is_shopify = True

                    print(f"✓ (이메일: {bool(email)}, 상품: {product_count}, 카테고리: {bool(categories)})")
                else:
                    print("✗ (페이지 가져오기 실패)")

            except Exception as e:
                print(f"✗ (오류: {str(e)[:30]})")

            # Rate limiting
            time.sleep(1)  # 각 요청 사이 1초 대기

            # 쇼핑몰 타입 결정 (products.json 성공 여부 반영)
            shop_type = "Shopify" if is_shopify else "E-commerce"

            # 게시물 문제 분류
            problem_categories = self.classifier.classify_post(post)
            primary_problem = problem_categories[0] if problem_categories else "Unclassified"
            all_problems = ", ".join(problem_categories[:3]) if problem_categories else ""

            # 사업 기회 매핑
            business_opportunity = ""
            if primary_problem in PROBLEM_CATEGORIES:
                business_opportunity = PROBLEM_CATEGORIES[primary_problem]['business_opportunity']

            shop_info = {
                'No': idx,
                'DTC Name': domain_name.title() if domain_name else "",
                'Location': "",  # Reddit에서 추출 어려움
                'Website': main_url,
                'Type': shop_type,
                'Categories': categories,
                'Product Count': product_count if product_count > 0 else "",
                '# of Employees': "",  # 웹사이트에서 추출 어려움
                'Source': f"Reddit r/reviewmyshopify - {post.get('permalink', '')}",
                'Contact Type': "Email" if email else "",
                'Email': email,
                'Linkedin': "",  # Reddit에서 추출 어려움
                'Post Title': post.get('title', ''),
                'Post Score': post.get('score', 0),
                'Num Comments': post.get('num_comments', 0),
                'Primary Problem': primary_problem,
                'All Problems': all_problems,
                'Business Opportunity': business_opportunity,
            }

            shops.append(shop_info)

        return shops

    def save_to_csv(self, output_path: str = None) -> str:
        """쇼핑몰 정보를 CSV로 저장"""
        shops = self.extract_shop_info_with_scraping()

        if not shops:
            print("\n⚠ 추출된 쇼핑몰 정보가 없습니다.")
            return None

        df = pd.DataFrame(shops)

        if output_path is None:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"output/shop_info_enhanced_{timestamp}.csv"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print(f"\n✓ 쇼핑몰 정보 저장 완료: {output_path}")
        print(f"  총 {len(shops)}개의 쇼핑몰 정보 추출")
        print(f"  이메일 수집: {len([s for s in shops if s['Email']])}개")
        print(f"  상품 수 확인: {len([s for s in shops if s['Product Count']])}개")
        print(f"  카테고리 확인: {len([s for s in shops if s['Categories']])}개")

        return output_path


def main():
    """쇼핑몰 정보 추출 실행"""
    import glob

    # 가장 최근 데이터 파일 찾기
    data_files = glob.glob('data/reddit_data_*.json')
    if not data_files:
        print("✗ 데이터 파일을 찾을 수 없습니다.")
        return

    latest_file = max(data_files, key=os.path.getctime)
    print(f"📊 쇼핑몰 정보 추출 시작: {latest_file}\n")

    extractor = ShopInfoExtractor(latest_file)
    output_path = extractor.save_to_csv()

    if output_path:
        # 결과 미리보기
        df = pd.read_csv(output_path)
        print("\n=== 추출된 쇼핑몰 정보 (샘플) ===")
        print(df[['No', 'DTC Name', 'Email', 'Categories', 'Product Count']].head(10).to_string(index=False))


if __name__ == "__main__":
    main()
