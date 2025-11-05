"""
메인 실행 파일
Reddit 크롤링, 분석, 시각화를 한 번에 실행합니다.
"""

import os
import sys
import argparse
from datetime import datetime

# src 모듈 import
from src.crawler import RedditCrawler
from src.analyzer import RedditAnalyzer
from src.visualizer import DataVisualizer
import config


def print_banner():
    """배너 출력"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║       Reddit r/reviewmyshopify Analyzer                       ║
    ║       Shopify 쇼핑몰 리뷰 데이터 수집 및 분석 도구             ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def run_crawler(limit: int = None):
    """크롤러 실행"""
    print("\n" + "="*70)
    print("STEP 1: 데이터 크롤링")
    print("="*70)

    crawler = RedditCrawler()
    posts = crawler.crawl_subreddit(limit=limit)

    if posts:
        filepath = crawler.save_to_json(posts)
        print(f"\n✓ {len(posts)}개의 게시물과 {sum(len(p['comments']) for p in posts)}개의 댓글 수집 완료")
        return filepath
    else:
        print("\n✗ 데이터 수집 실패")
        return None


def run_analyzer(data_path: str):
    """분석기 실행"""
    print("\n" + "="*70)
    print("STEP 2: 데이터 분석")
    print("="*70)

    analyzer = RedditAnalyzer(data_path)

    # 기본 통계
    stats = analyzer.get_basic_statistics()
    print("\n📊 기본 통계")
    print("-" * 70)
    print(f"  총 게시물 수: {stats['total_posts']}")
    print(f"  총 댓글 수: {stats['total_comments']}")
    print(f"  게시물당 평균 댓글 수: {stats['avg_comments_per_post']:.2f}")
    print(f"  평균 게시물 점수: {stats['avg_post_score']:.2f}")
    print(f"  평균 댓글 점수: {stats['avg_comment_score']:.2f}")
    print(f"  평균 추천 비율: {stats['avg_upvote_ratio']:.2%}")
    print(f"  데이터 수집 기간: {stats['date_range']['from'].strftime('%Y-%m-%d')} ~ {stats['date_range']['to'].strftime('%Y-%m-%d')}")

    # 키워드 분석
    print("\n🔍 게시물 키워드 분석 (쇼핑몰 운영자들이 궁금해하는 것)")
    print("-" * 70)
    post_keywords = analyzer.analyze_keywords_in_posts()
    print(post_keywords.head(10).to_string(index=False))

    print("\n💬 댓글 키워드 분석 (쇼핑몰 운영자들이 받는 조언)")
    print("-" * 70)
    comment_keywords = analyzer.analyze_keywords_in_comments()
    print(comment_keywords.head(10).to_string(index=False))

    # 상위 기여자
    print("\n👥 가장 많이 도움을 준 사용자 TOP 10")
    print("-" * 70)
    contributors = analyzer.get_top_contributors()
    print(contributors.to_string(index=False))

    # 결과 저장
    timestamp = analyzer.save_analysis_results()
    print(f"\n✓ 분석 결과 CSV 파일 저장 완료")

    return analyzer, timestamp


def run_visualizer(analyzer: RedditAnalyzer):
    """시각화 도구 실행"""
    print("\n" + "="*70)
    print("STEP 3: 데이터 시각화")
    print("="*70)

    visualizer = DataVisualizer(analyzer)
    visualizer.generate_all_visualizations()

    print("\n✓ 모든 그래프 생성 완료")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='Reddit r/reviewmyshopify 데이터 분석 도구')
    parser.add_argument('--crawl', action='store_true', help='데이터 크롤링 실행')
    parser.add_argument('--analyze', action='store_true', help='데이터 분석 실행')
    parser.add_argument('--visualize', action='store_true', help='데이터 시각화 실행')
    parser.add_argument('--all', action='store_true', help='모든 단계 실행 (크롤링, 분석, 시각화)')
    parser.add_argument('--limit', type=int, default=config.POST_LIMIT, help='크롤링할 게시물 수')

    args = parser.parse_args()

    print_banner()

    # 인자가 없으면 전체 실행
    if not (args.crawl or args.analyze or args.visualize or args.all):
        args.all = True

    if args.all:
        # 전체 파이프라인 실행
        print("\n🚀 전체 프로세스 시작: 크롤링 → 분석 → 시각화\n")

        # 1. 크롤링
        data_path = run_crawler(limit=args.limit)
        if not data_path:
            print("\n✗ 크롤링 실패로 프로세스 중단")
            return

        # 2. 분석
        analyzer, timestamp = run_analyzer(data_path)

        # 3. 시각화
        run_visualizer(analyzer)

        # 완료 메시지
        print("\n" + "="*70)
        print("✓ 모든 작업 완료!")
        print("="*70)
        print(f"\n📁 결과 파일 위치:")
        print(f"  - 원본 데이터: {data_path}")
        print(f"  - 분석 결과 (CSV): {config.OUTPUT_DIR}/")
        print(f"  - 시각화 그래프 (PNG): {config.OUTPUT_DIR}/")
        print()

    else:
        # 개별 단계 실행
        if args.crawl:
            data_path = run_crawler(limit=args.limit)

        if args.analyze:
            import glob
            data_files = glob.glob(os.path.join(config.DATA_DIR, 'reddit_data_*.json'))
            if not data_files:
                print("✗ 데이터 파일을 찾을 수 없습니다. 먼저 --crawl을 실행하세요.")
                return
            latest_file = max(data_files, key=os.path.getctime)
            analyzer, timestamp = run_analyzer(latest_file)

        if args.visualize:
            import glob
            data_files = glob.glob(os.path.join(config.DATA_DIR, 'reddit_data_*.json'))
            if not data_files:
                print("✗ 데이터 파일을 찾을 수 없습니다. 먼저 --crawl을 실행하세요.")
                return
            latest_file = max(data_files, key=os.path.getctime)
            analyzer = RedditAnalyzer(latest_file)
            run_visualizer(analyzer)


if __name__ == "__main__":
    main()
