"""
CarBuyingGuide Auto Post Generator
Generates SEO-optimized car buying and maintenance articles using OpenAI GPT API
and commits them to the blog repository.
"""

from openai import OpenAI
import datetime
import os
import random
import re

# High CPC keyword categories for car/auto niche
TOPIC_POOLS = {
    "car_buying": [
        "How to Negotiate the Best Car Price at a Dealership in {year}",
        "Best Time of Year to Buy a New Car and Save Thousands",
        "{number} Things You Should Never Say to a Car Dealer",
        "How to Buy a Car Online and Avoid Getting Scammed",
        "Leasing vs Buying a Car: Which Option Saves You More Money",
        "First Time Car Buyer Guide: Everything You Need to Know in {year}",
        "How to Get the Best Trade-In Value for Your Old Car",
    ],
    "car_maintenance": [
        "Car Maintenance Checklist Every Driver Should Follow",
        "{number} Car Maintenance Tasks You Can Do Yourself to Save Money",
        "How Often Should You Really Change Your Oil in {year}",
        "Warning Signs Your Car Needs Immediate Maintenance",
        "How to Make Your Car Last Over 200,000 Miles",
        "Seasonal Car Maintenance Tips for Every Climate",
        "The True Cost of Skipping Regular Car Maintenance",
    ],
    "car_insurance": [
        "How to Save Money on Car Insurance in {year}",
        "{number} Car Insurance Discounts You Might Be Missing",
        "Full Coverage vs Liability Only: What Car Insurance Do You Need",
        "How Your Credit Score Affects Your Car Insurance Rate",
        "Best Car Insurance Companies for Young Drivers in {year}",
        "How to Lower Your Car Insurance After an Accident",
        "Gap Insurance: Do You Really Need It for Your New Car",
    ],
    "electric_vehicles": [
        "Electric vs Gas Cars: Which Saves You More Money in {year}",
        "Best Affordable Electric Cars Under $35,000 in {year}",
        "How Much Does It Really Cost to Charge an Electric Car",
        "EV Tax Credits and Incentives You Should Know About in {year}",
        "The Pros and Cons of Buying an Electric Vehicle",
        "How Long Do Electric Car Batteries Last Before Replacement",
        "Best Hybrid Cars for Fuel Efficiency in {year}",
    ],
    "used_cars": [
        "Best Used Cars Under $15,000 That Are Reliable in {year}",
        "How to Check a Used Car Before Buying: Complete Inspection Guide",
        "{number} Red Flags When Buying a Used Car from a Private Seller",
        "Certified Pre-Owned vs Regular Used Cars: Is CPO Worth It",
        "Best Websites to Buy Used Cars Online in {year}",
        "How to Get a Vehicle History Report and What to Look For",
        "Most Reliable Used Car Brands That Last Over 10 Years",
    ],
    "car_finance": [
        "How to Get the Best Auto Loan Rate in {year}",
        "Should You Finance Through the Dealer or Your Bank",
        "How to Refinance Your Car Loan and Save Money",
        "What Credit Score Do You Need to Buy a Car in {year}",
        "How Much Car Can You Really Afford on Your Salary",
        "{number} Auto Loan Mistakes That Cost You Thousands",
        "Zero Percent Financing: Is It Really a Good Deal",
    ],
    "driving_tips": [
        "{number} Fuel-Saving Driving Tips That Actually Work",
        "How to Improve Your Gas Mileage and Save Money",
        "Road Trip Checklist: {number} Things to Do Before a Long Drive",
        "Defensive Driving Tips Every Driver Should Practice",
        "How to Drive in Snow and Ice Safely",
        "Best Apps for Drivers to Save Money on Gas in {year}",
        "How to Reduce Wear and Tear on Your Car",
    ],
}

SYSTEM_PROMPT = """You are an expert automotive writer for a blog called CarBuyingGuide.
Write SEO-optimized, informative, and engaging blog posts about cars.

Rules:
- Write in a friendly, conversational but authoritative tone
- Use short paragraphs (2-3 sentences max)
- Include practical, actionable advice
- Use headers (##) to break up sections
- Include bullet points and numbered lists where appropriate
- Write between 1200-1800 words
- Naturally include the main keyword 3-5 times
- Include a compelling introduction that hooks the reader
- End with a clear conclusion/call-to-action
- Do NOT include any AI disclaimers or mentions of being AI-generated
- Write as if you are a certified auto mechanic and car buying consultant sharing expertise
- Make content evergreen where possible
- Include specific numbers and examples
- Do NOT use markdown title (# Title) - just start with the content
"""


def pick_topic():
    """Select a random topic from the pools."""
    year = datetime.datetime.now().year
    number = random.choice([3, 5, 7, 10, 12, 15])
    category = random.choice(list(TOPIC_POOLS.keys()))
    title_template = random.choice(TOPIC_POOLS[category])
    title = title_template.format(year=year, number=number)
    return title, category


def generate_post_content(title, category):
    """Generate a blog post using OpenAI GPT API."""
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=4000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Write a comprehensive blog post with the title: \"{title}\"\n\nCategory: {category.replace('_', ' ')}\n\nRemember to write 1200-1800 words, use ## for section headers, and make it SEO-friendly.",
            },
        ],
    )

    return response.choices[0].message.content


def slugify(title):
    """Convert title to URL-friendly slug."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug)
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug


def get_repo_root():
    """Get the repository root directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(script_dir)


def get_existing_titles():
    """Get titles of existing posts to avoid duplicates."""
    posts_dir = os.path.join(get_repo_root(), '_posts')
    titles = set()
    if os.path.exists(posts_dir):
        for filename in os.listdir(posts_dir):
            if filename.endswith('.md'):
                title_part = filename[11:-3]
                titles.add(title_part)
    return titles


def create_post():
    """Generate and save a new blog post."""
    existing = get_existing_titles()

    # Try up to 10 times to find a non-duplicate topic
    for _ in range(10):
        title, category = pick_topic()
        slug = slugify(title)
        if slug not in existing:
            break
    else:
        # If all attempts hit duplicates, add a random suffix
        title, category = pick_topic()
        slug = slugify(title) + f"-{random.randint(100, 999)}"

    print(f"Generating post: {title}")
    print(f"Category: {category}")

    content = generate_post_content(title, category)

    # Create the post file
    today = datetime.datetime.now()
    date_str = today.strftime('%Y-%m-%d')
    filename = f"{date_str}-{slug}.md"

    posts_dir = os.path.join(get_repo_root(), '_posts')
    os.makedirs(posts_dir, exist_ok=True)

    filepath = os.path.join(posts_dir, filename)

    # Create frontmatter
    frontmatter = f"""---
layout: post
title: "{title}"
date: {today.strftime('%Y-%m-%d %H:%M:%S')} +0000
categories: [{category.replace('_', '-')}]
description: "{title} - Expert tips and advice for smart car buyers and owners."
---

{content}
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)

    print(f"Post saved: {filepath}")
    return filepath, filename

if __name__ == '__main__':
    # Every 5th post: generate a Gumroad promo post
    from promo_post import should_write_promo, create_promo_post
    if should_write_promo():
        print("Generating promotional post...")
        filepath, filename = create_promo_post()
    else:
        filepath, filename = create_post()
    print(f"Done! Post generated: {filename}")
