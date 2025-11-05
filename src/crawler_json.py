"""
Reddit JSON API 크롤러 (인증 불필요)
Reddit의 공개 JSON 엔드포인트를 사용하여 데이터를 수집합니다.
"""

import requests
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class RedditJSONCrawler:
    def __init__(self):
        """Reddit JSON API 크롤러 초기화"""
        self.base_url = f"https://www.reddit.com/r/{config.SUBREDDIT_NAME}"
        self.headers = {
            'User-Agent': config.REDDIT_USER_AGENT,
        }
        print(f"✓ Reddit JSON API 크롤러 초기화 완료")

    def fetch_posts(self, limit: int = 100, after: str = None) -> tuple:
        """
        서브레딧에서 게시물 목록을 가져옵니다.

        Args:
            limit: 가져올 게시물 수 (최대 100)
            after: 페이지네이션용 after 토큰

        Returns:
            (posts, after_token) 튜플
        """
        url = f"{self.base_url}/new.json"
        params = {'limit': min(limit, 100)}

        if after:
            params['after'] = after

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            posts = data['data']['children']
            after_token = data['data'].get('after')

            return posts, after_token

        except requests.exceptions.RequestException as e:
            print(f"✗ 게시물 가져오기 오류: {e}")
            return [], None

    def fetch_comments(self, post_id: str) -> List[Dict]:
        """
        특정 게시물의 댓글을 가져옵니다.

        Args:
            post_id: 게시물 ID

        Returns:
            댓글 리스트
        """
        url = f"{self.base_url}/comments/{post_id}.json"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            # 첫 번째는 게시물, 두 번째는 댓글
            if len(data) < 2:
                return []

            comments_data = data[1]['data']['children']
            comments = []

            for comment_obj in comments_data:
                if comment_obj['kind'] == 't1':  # 댓글 타입
                    comment_data = comment_obj['data']
                    comments.append({
                        'id': comment_data.get('id', ''),
                        'author': comment_data.get('author', '[deleted]'),
                        'body': comment_data.get('body', ''),
                        'score': comment_data.get('score', 0),
                        'created_utc': comment_data.get('created_utc', 0),
                        'is_submitter': comment_data.get('is_submitter', False),
                    })

            return comments

        except requests.exceptions.RequestException as e:
            print(f"  ⚠ 댓글 가져오기 오류 (post_id: {post_id}): {e}")
            return []

    def crawl_subreddit(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        서브레딧에서 게시물과 댓글을 크롤링합니다.

        Args:
            limit: 가져올 게시물 수 (None이면 모두)

        Returns:
            게시물 데이터 리스트
        """
        posts_data = []
        after_token = None
        total_fetched = 0

        print(f"\n📥 r/{config.SUBREDDIT_NAME} 크롤링 시작...")
        print(f"   가져올 게시물 수: {limit if limit else '모두'}\n")

        while True:
            # 남은 개수 계산
            remaining = limit - total_fetched if limit else 100
            if remaining <= 0:
                break

            fetch_limit = min(remaining, 100)

            # 게시물 가져오기
            posts, after_token = self.fetch_posts(limit=fetch_limit, after=after_token)

            if not posts:
                break

            # 각 게시물 처리
            for post_obj in posts:
                post = post_obj['data']
                post_id = post.get('id', '')

                # 댓글 가져오기
                time.sleep(0.5)  # Rate limiting 방지
                comments = self.fetch_comments(post_id)

                # 게시물 데이터 구조화
                post_data = {
                    'id': post_id,
                    'title': post.get('title', ''),
                    'author': post.get('author', '[deleted]'),
                    'selftext': post.get('selftext', ''),
                    'url': post.get('url', ''),
                    'score': post.get('score', 0),
                    'upvote_ratio': post.get('upvote_ratio', 0),
                    'num_comments': post.get('num_comments', 0),
                    'created_utc': post.get('created_utc', 0),
                    'permalink': f"https://www.reddit.com{post.get('permalink', '')}",
                    'link_flair_text': post.get('link_flair_text'),
                    'comments': comments,
                }

                posts_data.append(post_data)
                total_fetched += 1

                if total_fetched % 10 == 0:
                    print(f"   처리 중... {total_fetched}개 게시물 수집 완료")

                if limit and total_fetched >= limit:
                    break

            # 다음 페이지가 없으면 종료
            if not after_token:
                break

        print(f"\n✓ 총 {len(posts_data)}개의 게시물 수집 완료")
        print(f"✓ 총 {sum(len(p['comments']) for p in posts_data)}개의 댓글 수집 완료\n")

        return posts_data

    def save_to_json(self, data: List[Dict[str, Any]], filename: str = None):
        """데이터를 JSON 파일로 저장합니다."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reddit_data_{timestamp}.json"

        filepath = os.path.join(config.DATA_DIR, filename)
        os.makedirs(config.DATA_DIR, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ 데이터 저장 완료: {filepath}")
        return filepath


def main():
    """크롤러 실행"""
    crawler = RedditJSONCrawler()

    # 데이터 수집
    posts = crawler.crawl_subreddit(limit=config.POST_LIMIT)

    # JSON 파일로 저장
    if posts:
        filepath = crawler.save_to_json(posts)
        print(f"\n총 {len(posts)}개의 게시물과 {sum(len(p['comments']) for p in posts)}개의 댓글을 수집했습니다.")
        print(f"저장 위치: {filepath}")
    else:
        print("\n수집된 데이터가 없습니다.")


if __name__ == "__main__":
    main()
