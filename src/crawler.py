"""
Reddit 크롤러
/r/reviewmyshopify 서브레딧에서 게시물과 댓글을 수집합니다.
"""

import praw
import json
import os
from datetime import datetime
from typing import List, Dict, Any
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class RedditCrawler:
    def __init__(self):
        """Reddit API 클라이언트 초기화"""
        try:
            self.reddit = praw.Reddit(
                client_id=config.REDDIT_CLIENT_ID,
                client_secret=config.REDDIT_CLIENT_SECRET,
                user_agent=config.REDDIT_USER_AGENT
            )
            print(f"✓ Reddit API 연결 성공: {self.reddit.user.me() if config.REDDIT_CLIENT_ID else '읽기 전용 모드'}")
        except Exception as e:
            print(f"⚠ Reddit API 연결 실패 (읽기 전용 모드로 전환): {e}")
            self.reddit = praw.Reddit(
                client_id=config.REDDIT_CLIENT_ID or 'dummy',
                client_secret=config.REDDIT_CLIENT_SECRET or 'dummy',
                user_agent=config.REDDIT_USER_AGENT
            )

    def crawl_subreddit(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        서브레딧에서 게시물과 댓글을 크롤링합니다.

        Args:
            limit: 가져올 게시물 수 (None이면 모두)

        Returns:
            게시물 데이터 리스트
        """
        subreddit = self.reddit.subreddit(config.SUBREDDIT_NAME)
        posts_data = []

        print(f"\n📥 r/{config.SUBREDDIT_NAME} 크롤링 시작...")
        print(f"   가져올 게시물 수: {limit if limit else '모두'}\n")

        try:
            # 최신 게시물부터 가져오기
            for idx, submission in enumerate(subreddit.new(limit=limit), 1):
                post_data = self._extract_post_data(submission)
                posts_data.append(post_data)

                if idx % 10 == 0:
                    print(f"   처리 중... {idx}개 게시물 수집 완료")

            print(f"\n✓ 총 {len(posts_data)}개의 게시물 수집 완료\n")
            return posts_data

        except Exception as e:
            print(f"✗ 크롤링 오류: {e}")
            return posts_data

    def _extract_post_data(self, submission) -> Dict[str, Any]:
        """게시물에서 필요한 데이터를 추출합니다."""
        # 댓글 가져오기
        submission.comments.replace_more(limit=0)  # "더보기" 댓글 제거
        comments = []

        for comment in submission.comments.list():
            if isinstance(comment, praw.models.Comment):
                comments.append({
                    'id': comment.id,
                    'author': str(comment.author) if comment.author else '[deleted]',
                    'body': comment.body,
                    'score': comment.score,
                    'created_utc': comment.created_utc,
                    'is_submitter': comment.is_submitter,
                })

        # 게시물 데이터
        post_data = {
            'id': submission.id,
            'title': submission.title,
            'author': str(submission.author) if submission.author else '[deleted]',
            'selftext': submission.selftext,
            'url': submission.url,
            'score': submission.score,
            'upvote_ratio': submission.upvote_ratio,
            'num_comments': submission.num_comments,
            'created_utc': submission.created_utc,
            'permalink': f"https://www.reddit.com{submission.permalink}",
            'link_flair_text': submission.link_flair_text,
            'comments': comments,
        }

        return post_data

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
    crawler = RedditCrawler()

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
