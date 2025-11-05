"""
쇼핑몰 정보 추출기
Reddit 게시물에서 쇼핑몰 정보를 추출하고 CSV로 저장합니다.
"""

import re
import json
from urllib.parse import urlparse
import pandas as pd
from typing import List, Dict, Any
import os


class ShopInfoExtractor:
    def __init__(self, data_path: str):
        """
        쇼핑몰 정보 추출기 초기화

        Args:
            data_path: Reddit 데이터 JSON 파일 경로
        """
        with open(data_path, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)

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
        """URL 정리 (쿼리 파라미터 제거 등)"""
        try:
            parsed = urlparse(url)
            clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            return clean.rstrip('/')
        except:
            return url

    def extract_shop_info(self) -> List[Dict[str, Any]]:
        """모든 게시물에서 쇼핑몰 정보 추출"""
        shops = []

        for idx, post in enumerate(self.raw_data, 1):
            # 텍스트 결합
            text = f"{post.get('title', '')} {post.get('selftext', '')} {post.get('url', '')}"

            # URL 추출
            urls = self.extract_urls_from_text(text)

            # 이메일 추출
            email = self.extract_email_from_text(text)

            # Reddit 링크 필터링 (실제 쇼핑몰 URL만)
            shop_urls = [
                url for url in urls
                if 'reddit.com' not in url and
                   'redd.it' not in url and
                   len(url) > 10
            ]

            if shop_urls:
                # 첫 번째 URL을 주 사이트로 사용
                main_url = self.clean_url(shop_urls[0])
                domain_name = self.get_domain_name(main_url)

                # 쇼핑몰 타입 추측
                shop_type = "Shopify" if "myshopify.com" in main_url else "E-commerce"

                shop_info = {
                    'No': idx,
                    'DTC Name': domain_name.title() if domain_name else "",
                    'Location': "",  # Reddit에서 추출 어려움
                    'Website': main_url,
                    'Type': shop_type,
                    '# of Employees': "",  # Reddit에서 추출 어려움
                    'Source': f"Reddit r/reviewmyshopify - {post.get('permalink', '')}",
                    'Contact Type': "Email" if email else "",
                    'Email': email,
                    'Linkedin': "",  # Reddit에서 추출 어려움
                    'Post Title': post.get('title', ''),
                    'Post Score': post.get('score', 0),
                    'Num Comments': post.get('num_comments', 0),
                }

                shops.append(shop_info)

        return shops

    def save_to_csv(self, output_path: str = None) -> str:
        """쇼핑몰 정보를 CSV로 저장"""
        shops = self.extract_shop_info()

        if not shops:
            print("⚠ 추출된 쇼핑몰 정보가 없습니다.")
            return None

        df = pd.DataFrame(shops)

        if output_path is None:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"output/shop_info_{timestamp}.csv"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print(f"✓ 쇼핑몰 정보 저장 완료: {output_path}")
        print(f"  총 {len(shops)}개의 쇼핑몰 정보 추출")

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
    shops = extractor.extract_shop_info()

    # 결과 미리보기
    if shops:
        print("\n=== 추출된 쇼핑몰 정보 (샘플) ===")
        df = pd.DataFrame(shops)
        print(df[['No', 'DTC Name', 'Website', 'Type', 'Email']].head(10))

        # CSV 저장
        extractor.save_to_csv()


if __name__ == "__main__":
    main()
