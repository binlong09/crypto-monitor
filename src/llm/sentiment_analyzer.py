"""
LLM-based Sentiment Analysis for Crypto News
Uses OpenAI GPT to analyze news sentiment
"""

import os
from typing import Dict, List, Optional
from openai import OpenAI


class CryptoSentimentAnalyzer:
    """Analyze crypto news sentiment using LLM"""

    # Available models with cost estimates (per 1M tokens)
    MODELS = {
        'gpt-4o-mini': {'input': 0.15, 'output': 0.60, 'name': 'GPT-4o Mini (Fast & Cheap)'},
        'gpt-4o': {'input': 2.50, 'output': 10.00, 'name': 'GPT-4o (Balanced)'},
        'gpt-4-turbo': {'input': 10.00, 'output': 30.00, 'name': 'GPT-4 Turbo (Most Capable)'},
        'o1-mini': {'input': 3.00, 'output': 12.00, 'name': 'O1 Mini (Reasoning)'},
    }

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize sentiment analyzer

        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var
            model: Model to use (gpt-4o-mini, gpt-4o, gpt-4-turbo, o1-mini)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)

        # Validate and set model
        if model not in self.MODELS:
            print(f"Warning: Unknown model {model}, defaulting to gpt-4o-mini")
            model = "gpt-4o-mini"

        self.model = model
        print(f"Using model: {self.MODELS[model]['name']}")

    def analyze_article(self, title: str, summary: str, symbol: str) -> Dict:
        """
        Analyze sentiment of a single article

        Args:
            title: Article title
            summary: Article summary/content
            symbol: Crypto symbol (BTC, ETH)

        Returns:
            Dict with sentiment score, explanation, and flags
        """
        prompt = f"""Analyze this cryptocurrency news article and provide:

1. Sentiment score (-10 to +10):
   -10 = Extremely bearish
   0 = Neutral
   +10 = Extremely bullish

2. Brief explanation (1-2 sentences)

3. Flags for critical events:
   - Is this about a hack/exploit? (yes/no)
   - Is this about regulation/legal issues? (yes/no)
   - Is this about major adoption/partnership? (yes/no)
   - Is this about technical upgrade/development? (yes/no)

Article about {symbol}:
Title: {title}
Summary: {summary}

Respond in this exact format:
SCORE: [number]
EXPLANATION: [text]
HACK: [yes/no]
REGULATION: [yes/no]
ADOPTION: [yes/no]
TECH: [yes/no]
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a cryptocurrency market analyst providing objective sentiment analysis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )

            result_text = response.choices[0].message.content.strip()

            # Parse response
            lines = result_text.split('\n')
            parsed = {}

            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    parsed[key.strip()] = value.strip()

            # Extract sentiment data
            sentiment_score = float(parsed.get('SCORE', 0))
            explanation = parsed.get('EXPLANATION', 'Unable to analyze')

            flags = {
                'hack': parsed.get('HACK', 'no').lower() == 'yes',
                'regulation': parsed.get('REGULATION', 'no').lower() == 'yes',
                'adoption': parsed.get('ADOPTION', 'no').lower() == 'yes',
                'tech': parsed.get('TECH', 'no').lower() == 'yes'
            }

            # Determine sentiment label
            if sentiment_score >= 7:
                sentiment_label = 'Very Bullish'
            elif sentiment_score >= 3:
                sentiment_label = 'Bullish'
            elif sentiment_score <= -7:
                sentiment_label = 'Very Bearish'
            elif sentiment_score <= -3:
                sentiment_label = 'Bearish'
            else:
                sentiment_label = 'Neutral'

            return {
                'score': sentiment_score,
                'label': sentiment_label,
                'explanation': explanation,
                'flags': flags,
                'is_critical': any(flags.values())
            }

        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                'score': 0,
                'label': 'Unknown',
                'explanation': f'Error: {str(e)}',
                'flags': {'hack': False, 'regulation': False, 'adoption': False, 'tech': False},
                'is_critical': False
            }

    def analyze_news_batch(self, articles: List[Dict], symbol: str, max_articles: int = 10) -> List[Dict]:
        """
        Analyze sentiment for multiple articles

        Args:
            articles: List of article dicts with 'title' and 'summary'
            symbol: Crypto symbol (BTC, ETH)
            max_articles: Maximum number of articles to analyze

        Returns:
            List of articles with added sentiment data
        """
        analyzed_articles = []

        for i, article in enumerate(articles[:max_articles]):
            print(f"Analyzing article {i+1}/{min(len(articles), max_articles)}...")

            sentiment = self.analyze_article(
                title=article.get('title', ''),
                summary=article.get('summary', ''),
                symbol=symbol
            )

            analyzed_article = article.copy()
            analyzed_article['sentiment'] = sentiment

            analyzed_articles.append(analyzed_article)

        return analyzed_articles

    def get_overall_sentiment(self, analyzed_articles: List[Dict]) -> Dict:
        """
        Calculate overall sentiment from analyzed articles

        Args:
            analyzed_articles: Articles with sentiment data

        Returns:
            Dict with overall sentiment metrics
        """
        if not analyzed_articles:
            return {
                'avg_score': 0,
                'sentiment_label': 'Unknown',
                'num_articles': 0,
                'bullish_count': 0,
                'bearish_count': 0,
                'neutral_count': 0,
                'critical_count': 0
            }

        scores = [a['sentiment']['score'] for a in analyzed_articles]
        avg_score = sum(scores) / len(scores)

        bullish_count = sum(1 for s in scores if s >= 3)
        bearish_count = sum(1 for s in scores if s <= -3)
        neutral_count = len(scores) - bullish_count - bearish_count

        critical_count = sum(1 for a in analyzed_articles if a['sentiment']['is_critical'])

        # Overall label
        if avg_score >= 5:
            sentiment_label = 'Very Bullish'
        elif avg_score >= 2:
            sentiment_label = 'Bullish'
        elif avg_score <= -5:
            sentiment_label = 'Very Bearish'
        elif avg_score <= -2:
            sentiment_label = 'Bearish'
        else:
            sentiment_label = 'Neutral'

        return {
            'avg_score': avg_score,
            'sentiment_label': sentiment_label,
            'num_articles': len(analyzed_articles),
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'neutral_count': neutral_count,
            'critical_count': critical_count,
            'scores': scores
        }

    def generate_alert_summary(self, analyzed_articles: List[Dict], symbol: str) -> Optional[str]:
        """
        Generate alert summary for critical news

        Args:
            analyzed_articles: Articles with sentiment data
            symbol: Crypto symbol

        Returns:
            Alert message if critical news found, None otherwise
        """
        critical_articles = [a for a in analyzed_articles if a['sentiment']['is_critical']]

        if not critical_articles:
            return None

        # Categorize critical news
        hacks = [a for a in critical_articles if a['sentiment']['flags']['hack']]
        regulations = [a for a in critical_articles if a['sentiment']['flags']['regulation']]
        adoptions = [a for a in critical_articles if a['sentiment']['flags']['adoption']]
        tech = [a for a in critical_articles if a['sentiment']['flags']['tech']]

        alert_parts = [f"CRITICAL NEWS ALERT for {symbol}:"]

        if hacks:
            alert_parts.append(f"\n⚠️  {len(hacks)} SECURITY/HACK alert(s)")
        if regulations:
            alert_parts.append(f"\n⚖️  {len(regulations)} REGULATION alert(s)")
        if adoptions:
            alert_parts.append(f"\n🚀 {len(adoptions)} ADOPTION alert(s)")
        if tech:
            alert_parts.append(f"\n🔧 {len(tech)} TECH UPDATE alert(s)")

        alert_parts.append(f"\n\nTop critical articles:")
        for i, article in enumerate(critical_articles[:3], 1):
            alert_parts.append(f"\n{i}. {article['title']}")
            alert_parts.append(f"   Sentiment: {article['sentiment']['label']} ({article['sentiment']['score']:+.1f})")

        return ''.join(alert_parts)
