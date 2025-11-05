"""
데이터 분석기
수집된 Reddit 데이터를 분석하여 인사이트를 도출합니다.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter
import re
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class RedditAnalyzer:
    def __init__(self, data_path: str):
        """
        분석기 초기화

        Args:
            data_path: JSON 데이터 파일 경로
        """
        with open(data_path, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)

        self.posts_df = self._create_posts_dataframe()
        self.comments_df = self._create_comments_dataframe()

    def _create_posts_dataframe(self) -> pd.DataFrame:
        """게시물 데이터프레임 생성"""
        posts = []
        for post in self.raw_data:
            posts.append({
                'post_id': post['id'],
                'title': post['title'],
                'author': post['author'],
                'selftext': post['selftext'],
                'url': post['url'],
                'score': post['score'],
                'upvote_ratio': post['upvote_ratio'],
                'num_comments': post['num_comments'],
                'created_utc': datetime.fromtimestamp(post['created_utc']),
                'permalink': post['permalink'],
                'link_flair_text': post['link_flair_text'],
            })

        df = pd.DataFrame(posts)
        return df

    def _create_comments_dataframe(self) -> pd.DataFrame:
        """댓글 데이터프레임 생성"""
        comments = []
        for post in self.raw_data:
            for comment in post['comments']:
                comments.append({
                    'post_id': post['id'],
                    'comment_id': comment['id'],
                    'author': comment['author'],
                    'body': comment['body'],
                    'score': comment['score'],
                    'created_utc': datetime.fromtimestamp(comment['created_utc']),
                    'is_submitter': comment['is_submitter'],
                })

        df = pd.DataFrame(comments)
        return df

    def get_basic_statistics(self) -> dict:
        """기본 통계 정보 반환"""
        stats = {
            'total_posts': len(self.posts_df),
            'total_comments': len(self.comments_df),
            'avg_comments_per_post': self.posts_df['num_comments'].mean(),
            'avg_post_score': self.posts_df['score'].mean(),
            'avg_comment_score': self.comments_df['score'].mean(),
            'avg_upvote_ratio': self.posts_df['upvote_ratio'].mean(),
            'date_range': {
                'from': self.posts_df['created_utc'].min(),
                'to': self.posts_df['created_utc'].max(),
            },
        }
        return stats

    def extract_urls_from_posts(self) -> pd.DataFrame:
        """게시물에서 Shopify URL 추출"""
        shopify_urls = []

        for _, post in self.posts_df.iterrows():
            urls = []

            # 게시물 URL에서
            if 'myshopify.com' in post['url'] or any(
                domain in post['url']
                for domain in ['.com', '.net', '.store', '.shop']
            ):
                urls.append(post['url'])

            # 게시물 본문에서 URL 추출
            text = f"{post['title']} {post['selftext']}"
            found_urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
            urls.extend(found_urls)

            if urls:
                shopify_urls.append({
                    'post_id': post['post_id'],
                    'urls': list(set(urls)),
                    'num_urls': len(set(urls)),
                })

        return pd.DataFrame(shopify_urls)

    def analyze_keywords_in_posts(self) -> pd.DataFrame:
        """게시물에서 주요 키워드 분석"""
        keyword_counts = {keyword: 0 for keyword in config.ANALYSIS_KEYWORDS}

        for _, post in self.posts_df.iterrows():
            text = f"{post['title']} {post['selftext']}".lower()
            for keyword in config.ANALYSIS_KEYWORDS:
                if keyword.lower() in text:
                    keyword_counts[keyword] += 1

        df = pd.DataFrame(list(keyword_counts.items()), columns=['keyword', 'count'])
        df = df.sort_values('count', ascending=False)
        return df

    def analyze_keywords_in_comments(self) -> pd.DataFrame:
        """댓글에서 주요 키워드 분석 (쇼핑몰 운영자들이 받는 조언)"""
        keyword_counts = {keyword: 0 for keyword in config.ANALYSIS_KEYWORDS}

        for _, comment in self.comments_df.iterrows():
            text = comment['body'].lower()
            for keyword in config.ANALYSIS_KEYWORDS:
                if keyword.lower() in text:
                    keyword_counts[keyword] += 1

        df = pd.DataFrame(list(keyword_counts.items()), columns=['keyword', 'count'])
        df = df.sort_values('count', ascending=False)
        return df

    def analyze_comment_engagement(self) -> pd.DataFrame:
        """댓글 참여도 분석"""
        # 게시물별 댓글 통계
        engagement = []

        for _, post in self.posts_df.iterrows():
            post_comments = self.comments_df[self.comments_df['post_id'] == post['post_id']]

            if len(post_comments) > 0:
                engagement.append({
                    'post_id': post['post_id'],
                    'post_score': post['score'],
                    'num_comments': len(post_comments),
                    'avg_comment_score': post_comments['score'].mean(),
                    'max_comment_score': post_comments['score'].max(),
                    'total_comment_score': post_comments['score'].sum(),
                })

        df = pd.DataFrame(engagement)
        return df

    def find_helpful_comments(self, min_score: int = 5) -> pd.DataFrame:
        """높은 점수를 받은 유용한 댓글 찾기"""
        helpful_comments = self.comments_df[self.comments_df['score'] >= min_score].copy()
        helpful_comments = helpful_comments.sort_values('score', ascending=False)
        return helpful_comments

    def analyze_common_questions(self) -> list:
        """자주 나오는 질문 패턴 분석"""
        question_keywords = []

        for _, post in self.posts_df.iterrows():
            text = f"{post['title']} {post['selftext']}".lower()

            # 질문 패턴 찾기
            patterns = {
                'feedback_request': ['feedback', 'review', 'thoughts', 'opinions', 'roast', 'critique'],
                'improvement_question': ['improve', 'better', 'fix', 'change', 'optimize'],
                'conversion_question': ['convert', 'conversion', 'sales', 'sell'],
                'design_question': ['design', 'look', 'appearance', 'theme', 'layout'],
                'traffic_question': ['traffic', 'visitors', 'customers'],
            }

            for category, keywords in patterns.items():
                if any(kw in text for kw in keywords):
                    question_keywords.append({
                        'post_id': post['post_id'],
                        'category': category,
                        'title': post['title'],
                        'score': post['score'],
                        'num_comments': post['num_comments'],
                    })

        return question_keywords

    def get_top_contributors(self, top_n: int = 10) -> pd.DataFrame:
        """가장 많이 도움을 준 사용자 분석"""
        # 댓글 작성자별 통계
        contributor_stats = self.comments_df.groupby('author').agg({
            'comment_id': 'count',
            'score': ['sum', 'mean'],
        }).reset_index()

        contributor_stats.columns = ['author', 'total_comments', 'total_score', 'avg_score']
        contributor_stats = contributor_stats.sort_values('total_score', ascending=False).head(top_n)

        return contributor_stats

    def save_analysis_results(self, output_dir: str = None):
        """분석 결과를 CSV 파일로 저장"""
        if output_dir is None:
            output_dir = config.OUTPUT_DIR

        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # 1. 기본 통계
        stats = self.get_basic_statistics()
        with open(f"{output_dir}/basic_stats_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=str)

        # 2. 게시물 키워드 분석
        post_keywords = self.analyze_keywords_in_posts()
        post_keywords.to_csv(f"{output_dir}/post_keywords_{timestamp}.csv", index=False, encoding='utf-8-sig')

        # 3. 댓글 키워드 분석
        comment_keywords = self.analyze_keywords_in_comments()
        comment_keywords.to_csv(f"{output_dir}/comment_keywords_{timestamp}.csv", index=False, encoding='utf-8-sig')

        # 4. 참여도 분석
        engagement = self.analyze_comment_engagement()
        if not engagement.empty:
            engagement.to_csv(f"{output_dir}/engagement_{timestamp}.csv", index=False, encoding='utf-8-sig')

        # 5. 유용한 댓글
        helpful = self.find_helpful_comments()
        if not helpful.empty:
            helpful.to_csv(f"{output_dir}/helpful_comments_{timestamp}.csv", index=False, encoding='utf-8-sig')

        # 6. 상위 기여자
        contributors = self.get_top_contributors()
        contributors.to_csv(f"{output_dir}/top_contributors_{timestamp}.csv", index=False, encoding='utf-8-sig')

        print(f"✓ 분석 결과 저장 완료: {output_dir}/")
        return timestamp


def main():
    """분석기 실행"""
    import glob

    # 가장 최근 데이터 파일 찾기
    data_files = glob.glob(os.path.join(config.DATA_DIR, 'reddit_data_*.json'))
    if not data_files:
        print("✗ 데이터 파일을 찾을 수 없습니다. 먼저 크롤러를 실행하세요.")
        return

    latest_file = max(data_files, key=os.path.getctime)
    print(f"📊 데이터 분석 시작: {latest_file}\n")

    # 분석 실행
    analyzer = RedditAnalyzer(latest_file)

    # 기본 통계
    stats = analyzer.get_basic_statistics()
    print("=== 기본 통계 ===")
    print(f"총 게시물 수: {stats['total_posts']}")
    print(f"총 댓글 수: {stats['total_comments']}")
    print(f"게시물당 평균 댓글 수: {stats['avg_comments_per_post']:.2f}")
    print(f"평균 게시물 점수: {stats['avg_post_score']:.2f}")
    print(f"평균 댓글 점수: {stats['avg_comment_score']:.2f}")
    print(f"평균 추천 비율: {stats['avg_upvote_ratio']:.2%}\n")

    # 게시물 키워드 분석
    print("=== 게시물에서 자주 언급되는 키워드 TOP 10 ===")
    post_keywords = analyzer.analyze_keywords_in_posts()
    print(post_keywords.head(10).to_string(index=False))
    print()

    # 댓글 키워드 분석
    print("=== 댓글(조언)에서 자주 언급되는 키워드 TOP 10 ===")
    comment_keywords = analyzer.analyze_keywords_in_comments()
    print(comment_keywords.head(10).to_string(index=False))
    print()

    # 상위 기여자
    print("=== 가장 많이 도움을 준 사용자 TOP 10 ===")
    contributors = analyzer.get_top_contributors()
    print(contributors.to_string(index=False))
    print()

    # 결과 저장
    timestamp = analyzer.save_analysis_results()
    print(f"\n✓ 분석 완료! 결과는 {config.OUTPUT_DIR}/ 폴더에 저장되었습니다.")


if __name__ == "__main__":
    main()
