"""
데이터 시각화
분석 결과를 그래프와 차트로 시각화합니다.
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import pandas as pd
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from analyzer import RedditAnalyzer

# 한글 폰트 설정 시도
try:
    # Linux의 경우
    plt.rcParams['font.family'] = 'DejaVu Sans'
except:
    pass

plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
sns.set_style("whitegrid")
sns.set_palette("husl")


class DataVisualizer:
    def __init__(self, analyzer: RedditAnalyzer):
        """
        시각화 도구 초기화

        Args:
            analyzer: RedditAnalyzer 인스턴스
        """
        self.analyzer = analyzer

    def plot_keyword_analysis(self, save_path: str = None):
        """키워드 분석 그래프 생성"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))

        # 게시물 키워드
        post_keywords = self.analyzer.analyze_keywords_in_posts().head(15)
        axes[0].barh(post_keywords['keyword'], post_keywords['count'], color='steelblue')
        axes[0].set_xlabel('Count', fontsize=12)
        axes[0].set_title('Top Keywords in Posts (What shop owners ask about)', fontsize=14, fontweight='bold')
        axes[0].invert_yaxis()

        # 댓글 키워드
        comment_keywords = self.analyzer.analyze_keywords_in_comments().head(15)
        axes[1].barh(comment_keywords['keyword'], comment_keywords['count'], color='coral')
        axes[1].set_xlabel('Count', fontsize=12)
        axes[1].set_title('Top Keywords in Comments (What advice they receive)', fontsize=14, fontweight='bold')
        axes[1].invert_yaxis()

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ 키워드 분석 그래프 저장: {save_path}")

        plt.close()

    def plot_engagement_analysis(self, save_path: str = None):
        """참여도 분석 그래프 생성"""
        engagement = self.analyzer.analyze_comment_engagement()

        if engagement.empty:
            print("⚠ 참여도 데이터가 없습니다.")
            return

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # 1. 게시물 점수 vs 댓글 수
        axes[0, 0].scatter(engagement['post_score'], engagement['num_comments'], alpha=0.6, color='steelblue')
        axes[0, 0].set_xlabel('Post Score', fontsize=11)
        axes[0, 0].set_ylabel('Number of Comments', fontsize=11)
        axes[0, 0].set_title('Post Score vs Number of Comments', fontsize=12, fontweight='bold')

        # 2. 댓글 수 분포
        axes[0, 1].hist(engagement['num_comments'], bins=20, color='coral', edgecolor='black')
        axes[0, 1].set_xlabel('Number of Comments', fontsize=11)
        axes[0, 1].set_ylabel('Frequency', fontsize=11)
        axes[0, 1].set_title('Distribution of Comments per Post', fontsize=12, fontweight='bold')

        # 3. 평균 댓글 점수 분포
        axes[1, 0].hist(engagement['avg_comment_score'], bins=20, color='lightgreen', edgecolor='black')
        axes[1, 0].set_xlabel('Average Comment Score', fontsize=11)
        axes[1, 0].set_ylabel('Frequency', fontsize=11)
        axes[1, 0].set_title('Distribution of Average Comment Scores', fontsize=12, fontweight='bold')

        # 4. 총 댓글 점수 vs 댓글 수
        axes[1, 1].scatter(engagement['num_comments'], engagement['total_comment_score'], alpha=0.6, color='purple')
        axes[1, 1].set_xlabel('Number of Comments', fontsize=11)
        axes[1, 1].set_ylabel('Total Comment Score', fontsize=11)
        axes[1, 1].set_title('Comments Count vs Total Score', fontsize=12, fontweight='bold')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ 참여도 분석 그래프 저장: {save_path}")

        plt.close()

    def plot_top_contributors(self, save_path: str = None):
        """상위 기여자 그래프 생성"""
        contributors = self.analyzer.get_top_contributors()

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # 총 댓글 수
        axes[0].barh(contributors['author'], contributors['total_comments'], color='steelblue')
        axes[0].set_xlabel('Total Comments', fontsize=12)
        axes[0].set_title('Top Contributors by Comment Count', fontsize=14, fontweight='bold')
        axes[0].invert_yaxis()

        # 총 점수
        axes[1].barh(contributors['author'], contributors['total_score'], color='coral')
        axes[1].set_xlabel('Total Score', fontsize=12)
        axes[1].set_title('Top Contributors by Total Score', fontsize=14, fontweight='bold')
        axes[1].invert_yaxis()

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ 상위 기여자 그래프 저장: {save_path}")

        plt.close()

    def plot_time_distribution(self, save_path: str = None):
        """시간대별 게시물 분포 그래프 생성"""
        posts_df = self.analyzer.posts_df.copy()
        posts_df['hour'] = posts_df['created_utc'].dt.hour
        posts_df['day_of_week'] = posts_df['created_utc'].dt.day_name()

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        # 시간대별 분포
        hour_counts = posts_df['hour'].value_counts().sort_index()
        axes[0].bar(hour_counts.index, hour_counts.values, color='steelblue', edgecolor='black')
        axes[0].set_xlabel('Hour of Day (UTC)', fontsize=12)
        axes[0].set_ylabel('Number of Posts', fontsize=12)
        axes[0].set_title('Posts by Hour of Day', fontsize=14, fontweight='bold')
        axes[0].set_xticks(range(0, 24, 2))

        # 요일별 분포
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = posts_df['day_of_week'].value_counts().reindex(day_order)
        axes[1].bar(range(len(day_counts)), day_counts.values, color='coral', edgecolor='black')
        axes[1].set_xlabel('Day of Week', fontsize=12)
        axes[1].set_ylabel('Number of Posts', fontsize=12)
        axes[1].set_title('Posts by Day of Week', fontsize=14, fontweight='bold')
        axes[1].set_xticks(range(len(day_order)))
        axes[1].set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ 시간대별 분포 그래프 저장: {save_path}")

        plt.close()

    def plot_question_categories(self, save_path: str = None):
        """질문 카테고리 분석 그래프 생성"""
        questions = self.analyzer.analyze_common_questions()

        if not questions:
            print("⚠ 질문 카테고리 데이터가 없습니다.")
            return

        df = pd.DataFrame(questions)
        category_counts = df['category'].value_counts()

        fig, ax = plt.subplots(figsize=(10, 6))

        # 카테고리별 빈도
        colors = plt.cm.Set3(range(len(category_counts)))
        bars = ax.bar(range(len(category_counts)), category_counts.values, color=colors, edgecolor='black')

        ax.set_xlabel('Question Category', fontsize=12)
        ax.set_ylabel('Count', fontsize=12)
        ax.set_title('Common Question Categories', fontsize=14, fontweight='bold')
        ax.set_xticks(range(len(category_counts)))
        ax.set_xticklabels(category_counts.index, rotation=45, ha='right')

        # 값 표시
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=10)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ 질문 카테고리 그래프 저장: {save_path}")

        plt.close()

    def create_summary_dashboard(self, save_path: str = None):
        """종합 대시보드 생성"""
        stats = self.analyzer.get_basic_statistics()

        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # 통계 정보 텍스트
        ax_text = fig.add_subplot(gs[0, :])
        ax_text.axis('off')

        summary_text = f"""
        REDDIT r/reviewmyshopify ANALYSIS SUMMARY

        Total Posts: {stats['total_posts']}  |  Total Comments: {stats['total_comments']}  |  Avg Comments/Post: {stats['avg_comments_per_post']:.1f}
        Avg Post Score: {stats['avg_post_score']:.1f}  |  Avg Comment Score: {stats['avg_comment_score']:.1f}  |  Avg Upvote Ratio: {stats['avg_upvote_ratio']:.1%}
        Date Range: {stats['date_range']['from'].strftime('%Y-%m-%d')} to {stats['date_range']['to'].strftime('%Y-%m-%d')}
        """

        ax_text.text(0.5, 0.5, summary_text, ha='center', va='center',
                    fontsize=12, family='monospace',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        # 게시물 키워드 TOP 10
        ax1 = fig.add_subplot(gs[1, 0])
        post_keywords = self.analyzer.analyze_keywords_in_posts().head(10)
        ax1.barh(range(len(post_keywords)), post_keywords['count'].values, color='steelblue')
        ax1.set_yticks(range(len(post_keywords)))
        ax1.set_yticklabels(post_keywords['keyword'].values, fontsize=9)
        ax1.set_xlabel('Count', fontsize=10)
        ax1.set_title('Keywords in Posts (TOP 10)', fontsize=11, fontweight='bold')
        ax1.invert_yaxis()

        # 댓글 키워드 TOP 10
        ax2 = fig.add_subplot(gs[1, 1])
        comment_keywords = self.analyzer.analyze_keywords_in_comments().head(10)
        ax2.barh(range(len(comment_keywords)), comment_keywords['count'].values, color='coral')
        ax2.set_yticks(range(len(comment_keywords)))
        ax2.set_yticklabels(comment_keywords['keyword'].values, fontsize=9)
        ax2.set_xlabel('Count', fontsize=10)
        ax2.set_title('Keywords in Comments (TOP 10)', fontsize=11, fontweight='bold')
        ax2.invert_yaxis()

        # 상위 기여자
        ax3 = fig.add_subplot(gs[1, 2])
        contributors = self.analyzer.get_top_contributors(top_n=10)
        ax3.barh(range(len(contributors)), contributors['total_score'].values, color='lightgreen')
        ax3.set_yticks(range(len(contributors)))
        ax3.set_yticklabels(contributors['author'].values, fontsize=9)
        ax3.set_xlabel('Total Score', fontsize=10)
        ax3.set_title('Top Contributors (TOP 10)', fontsize=11, fontweight='bold')
        ax3.invert_yaxis()

        # 참여도 분석
        engagement = self.analyzer.analyze_comment_engagement()
        if not engagement.empty:
            # 게시물 점수 vs 댓글 수
            ax4 = fig.add_subplot(gs[2, 0])
            ax4.scatter(engagement['post_score'], engagement['num_comments'], alpha=0.6, color='purple')
            ax4.set_xlabel('Post Score', fontsize=10)
            ax4.set_ylabel('Comments', fontsize=10)
            ax4.set_title('Post Score vs Comments', fontsize=11, fontweight='bold')

            # 댓글 수 분포
            ax5 = fig.add_subplot(gs[2, 1])
            ax5.hist(engagement['num_comments'], bins=15, color='orange', edgecolor='black')
            ax5.set_xlabel('Comments per Post', fontsize=10)
            ax5.set_ylabel('Frequency', fontsize=10)
            ax5.set_title('Comment Distribution', fontsize=11, fontweight='bold')

            # 평균 댓글 점수
            ax6 = fig.add_subplot(gs[2, 2])
            ax6.hist(engagement['avg_comment_score'], bins=15, color='lightblue', edgecolor='black')
            ax6.set_xlabel('Avg Comment Score', fontsize=10)
            ax6.set_ylabel('Frequency', fontsize=10)
            ax6.set_title('Avg Comment Score Distribution', fontsize=11, fontweight='bold')

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ 종합 대시보드 저장: {save_path}")

        plt.close()

    def generate_all_visualizations(self, output_dir: str = None):
        """모든 시각화 생성"""
        if output_dir is None:
            output_dir = config.OUTPUT_DIR

        os.makedirs(output_dir, exist_ok=True)

        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        print("\n📊 시각화 생성 중...\n")

        self.plot_keyword_analysis(f"{output_dir}/keywords_{timestamp}.png")
        self.plot_engagement_analysis(f"{output_dir}/engagement_{timestamp}.png")
        self.plot_top_contributors(f"{output_dir}/contributors_{timestamp}.png")
        self.plot_time_distribution(f"{output_dir}/time_distribution_{timestamp}.png")
        self.plot_question_categories(f"{output_dir}/question_categories_{timestamp}.png")
        self.create_summary_dashboard(f"{output_dir}/dashboard_{timestamp}.png")

        print(f"\n✓ 모든 시각화 저장 완료: {output_dir}/")


def main():
    """시각화 도구 실행"""
    import glob

    # 가장 최근 데이터 파일 찾기
    data_files = glob.glob(os.path.join(config.DATA_DIR, 'reddit_data_*.json'))
    if not data_files:
        print("✗ 데이터 파일을 찾을 수 없습니다. 먼저 크롤러를 실행하세요.")
        return

    latest_file = max(data_files, key=os.path.getctime)
    print(f"📊 데이터 시각화 시작: {latest_file}")

    # 분석기 생성
    analyzer = RedditAnalyzer(latest_file)

    # 시각화 도구 생성 및 실행
    visualizer = DataVisualizer(analyzer)
    visualizer.generate_all_visualizations()


if __name__ == "__main__":
    main()
