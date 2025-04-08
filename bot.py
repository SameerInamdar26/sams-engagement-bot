import asyncio
from playwright.async_api import async_playwright
import random
import time

fake_comments = [
    "Awesome video!", "Loved the content 🔥", "So underrated 😍",
    "Keep it up!", "Subbed instantly!", "Wow, this is amazing!",
    "What a masterpiece 🎬", "Brilliant stuff!", "Here before it blows up 🚀",
    "Can’t stop watching!", "🔥🔥🔥"
]

async def run_bot(url, actions, bot_id):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=random_user_agent()
        )
        page = await context.new_page()

        try:
            # Simulate fake login
            await page.goto("https://your-fake-website.com/login", timeout=60000)
            await page.fill('input[name="email"]', f"user{bot_id}@example.com")
            await page.fill('input[name="password"]', "password123")
            await page.click('button[type="submit"]')
            await asyncio.sleep(1)  # Simulate login delay

            print(f"✅ Bot {bot_id} logged in")

            # Go to the actual video URL
            await page.goto(url)

            if "view" in actions:
                await asyncio.sleep(random.uniform(3, 5))  # Simulate watch time

            if "like" in actions:
                await page.click('button.like-button')  # Adjust selector as per your site
                print(f"👍 Bot {bot_id} liked the video")

            if "subscribe" in actions:
                await page.click('button.subscribe-button')  # Adjust selector
                print(f"📥 Bot {bot_id} subscribed")

            if "comment" in actions:
                comment = random.choice(fake_comments)
                await page.fill('textarea.comment-box', comment)  # Adjust selector
                await page.click('button.post-comment')
                print(f"💬 Bot {bot_id} commented: {comment}")

            await asyncio.sleep(1)

        except Exception as e:
            print(f"❌ Bot {bot_id} failed: {str(e)}")

        finally:
            await context.close()
            await browser.close()

def random_user_agent():
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
        "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)"
    ]
    return random.choice(agents)
