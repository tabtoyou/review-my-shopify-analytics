"""
샘플 데이터 생성 스크립트
실제 Reddit 데이터와 유사한 구조의 샘플 데이터를 생성합니다.
"""

import json
import random
from datetime import datetime, timedelta

# 샘플 게시물 제목과 내용
sample_posts = [
    {
        "title": "Please review my fashion store!",
        "selftext": "I just launched my clothing store at myshop.myshopify.com. Would love feedback on design and layout. Struggling with conversion rates.",
        "keywords": ["design", "layout", "conversion"]
    },
    {
        "title": "Roast my store - jewelry business",
        "selftext": "Looking for honest feedback on my jewelry store. Especially need help with product images and descriptions.",
        "keywords": ["product", "image", "description"]
    },
    {
        "title": "Need advice on checkout process",
        "selftext": "My customers are abandoning cart at checkout. What can I improve? Site is example-store.com",
        "keywords": ["checkout", "cart", "conversion"]
    },
    {
        "title": "How to improve mobile experience?",
        "selftext": "My store looks great on desktop but terrible on mobile. Any suggestions for responsive design?",
        "keywords": ["mobile", "responsive", "design"]
    },
    {
        "title": "First store - please be gentle!",
        "selftext": "Just started my dropshipping business. Would appreciate any feedback on my store design and product selection.",
        "keywords": ["design", "product"]
    },
    {
        "title": "SEO help needed for my store",
        "selftext": "Not getting any organic traffic. How can I improve my store's SEO? Running ads but need organic growth.",
        "keywords": ["seo", "traffic", "marketing"]
    },
    {
        "title": "Store review - handmade crafts",
        "selftext": "Selling handmade items. Need feedback on pricing and product photography.",
        "keywords": ["pricing", "image", "product"]
    },
    {
        "title": "Critique my homepage design",
        "selftext": "Redesigned my homepage. Does it look professional? Conversion rate is low.",
        "keywords": ["design", "conversion"]
    },
    {
        "title": "How to build trust with customers?",
        "selftext": "New store, no sales yet. How do I build credibility and trust?",
        "keywords": ["trust", "credibility"]
    },
    {
        "title": "Product page optimization tips?",
        "selftext": "My product pages need work. What elements are most important for conversions?",
        "keywords": ["product", "conversion"]
    },
]

# 샘플 댓글 템플릿
sample_comments = [
    {
        "templates": [
            "Your design looks good but I'd suggest improving the mobile responsiveness. The navigation menu is hard to use on phone.",
            "Great start! Consider adding more product images from different angles. Also, your descriptions are too short.",
            "The layout is clean but your call-to-action buttons aren't prominent enough. Make them bigger and use contrasting colors.",
            "Loading speed is critical. Your site takes too long to load. Optimize your images and consider a faster theme.",
            "Add customer reviews and testimonials to build trust. Social proof is essential for new stores.",
        ],
        "keywords": ["design", "mobile", "navigation", "image", "speed", "trust", "review"]
    },
    {
        "templates": [
            "Your pricing seems competitive. However, make your shipping costs clearer upfront to reduce cart abandonment.",
            "Consider offering free shipping threshold to increase average order value.",
            "The checkout process has too many steps. Simplify it to reduce friction.",
            "Add trust badges and secure payment icons near checkout button.",
        ],
        "keywords": ["pricing", "shipping", "checkout", "cart"]
    },
    {
        "templates": [
            "SEO basics: Add proper meta descriptions, optimize your product titles, and use alt tags on all images.",
            "Your site needs better content. Add a blog to improve SEO and engage customers.",
            "Focus on long-tail keywords specific to your niche. Don't compete with big brands on generic terms.",
        ],
        "keywords": ["seo", "content", "marketing"]
    },
    {
        "templates": [
            "Product photography needs improvement. Use natural lighting and show products in use, not just on white background.",
            "Your product descriptions should tell a story. Focus on benefits, not just features.",
            "Add a size guide and more detailed specifications. This reduces returns and increases confidence.",
        ],
        "keywords": ["product", "image", "description"]
    },
    {
        "templates": [
            "The overall design is decent but lacks personality. Add your brand story to connect with customers.",
            "Color scheme is good but consider using warmer tones to make it more inviting.",
            "Your font choices are hard to read. Stick to 2-3 fonts maximum and ensure good contrast.",
        ],
        "keywords": ["design", "color", "font"]
    },
]

def generate_sample_data(num_posts=50):
    """샘플 데이터 생성"""
    posts_data = []
    base_time = datetime.now() - timedelta(days=30)

    for i in range(num_posts):
        # 랜덤하게 게시물 선택
        post_template = random.choice(sample_posts)

        # 게시물 생성 시간 (최근 30일 내)
        post_time = base_time + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )

        # 댓글 생성
        num_comments = random.randint(3, 15)
        comments = []

        for j in range(num_comments):
            comment_template = random.choice(sample_comments)
            comment_text = random.choice(comment_template["templates"])

            comment_time = post_time + timedelta(
                hours=random.randint(1, 48),
                minutes=random.randint(0, 59)
            )

            comments.append({
                'id': f'comment_{i}_{j}',
                'author': f'helpful_user_{random.randint(1, 20)}',
                'body': comment_text,
                'score': random.randint(1, 25),
                'created_utc': comment_time.timestamp(),
                'is_submitter': False,
            })

        # 게시물 데이터
        post_data = {
            'id': f'post_{i}',
            'title': post_template['title'],
            'author': f'shop_owner_{i}',
            'selftext': post_template['selftext'],
            'url': f'https://example-store-{i}.myshopify.com',
            'score': random.randint(5, 50),
            'upvote_ratio': random.uniform(0.7, 0.98),
            'num_comments': len(comments),
            'created_utc': post_time.timestamp(),
            'permalink': f'/r/reviewmyshopify/comments/post_{i}/',
            'link_flair_text': random.choice(['Review Request', 'Feedback', 'Help', None]),
            'comments': comments,
        }

        posts_data.append(post_data)

    return posts_data


def main():
    """샘플 데이터 생성 및 저장"""
    print("📝 샘플 데이터 생성 중...\n")

    data = generate_sample_data(num_posts=50)

    # 저장
    import os
    os.makedirs('data', exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = f'data/reddit_data_{timestamp}.json'

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ 샘플 데이터 생성 완료!")
    print(f"  - 게시물 수: {len(data)}")
    print(f"  - 총 댓글 수: {sum(len(p['comments']) for p in data)}")
    print(f"  - 저장 위치: {filepath}\n")

    return filepath


if __name__ == "__main__":
    main()
