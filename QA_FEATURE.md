# Interactive Q&A Feature Guide

## Overview

The **Ask Follow-up Questions** feature allows you to have a conversation with the AI about its trading recommendation. The AI maintains full context of the analysis, recommendation, and your previous questions.

---

## How It Works

### 1. **Context Preservation**

When you ask a question, the AI has access to:

- ✅ **Trading Recommendation**
  - Buy/Sell/Hold decision
  - Entry price, stop loss, take profits
  - Position sizing
  - Confidence level

- ✅ **Market Analysis**
  - Current price and changes (24h, 7d, 30d)
  - Market cap and volume
  - Distance from ATH/ATL

- ✅ **Sentiment Analysis**
  - News sentiment score
  - Critical events detected
  - Article summaries

- ✅ **Risk Assessment**
  - Identified risk factors
  - Volatility metrics
  - Market conditions

- ✅ **Previous Questions**
  - Last 3 Q&As in the conversation
  - Maintains continuity
  - Can reference earlier answers

---

## Example Use Cases

### Use Case 1: Understanding the Reasoning

**Question:** "Why did you recommend buying now instead of waiting?"

**AI Response:** "Based on the current analysis:
1. Strong bullish sentiment (8.5/10) from recent institutional adoption news
2. Price has consolidated at $90,000 support level
3. Technical indicators showing upward momentum
4. Low risk environment with only minor concerns

However, if you prefer to wait:
- Watch for dip to $88,200 (2% lower) for better entry
- Monitor if sentiment remains positive
- Set price alerts at key levels

The 85% confidence suggests favorable conditions now, but scaled entry could reduce risk."

---

### Use Case 2: Risk Management Questions

**Question:** "What if the price drops 20% tomorrow? Should I sell or hold?"

**AI Response:** "A 20% drop to $72,000 would be significant and would:

1. **Trigger your stop loss** at $85,500 (5% loss)
   - Don't override this - capital preservation is key

2. **Signal invalidation** of the buy thesis
   - Such a drop indicates major negative catalyst
   - Could be regulatory news, hack, or macro event

3. **Action plan:**
   - Exit at stop loss automatically
   - Don't try to 'average down'
   - Reassess market conditions
   - Wait for stabilization before re-entering

4. **Position sizing protects you:**
   - 7.5% position × 5% loss = 0.375% portfolio impact
   - This is acceptable risk for the potential 15% gain

Always respect your stop losses - they're there for exactly this scenario."

---

### Use Case 3: Alternative Scenarios

**Question:** "How would your recommendation change if sentiment turns negative?"

**AI Response:** "If sentiment drops from current 8.5/10 to below 5/10 (neutral/bearish):

**My recommendation would likely change to HOLD or SELL:**

1. **At 4-5/10 (Neutral):**
   - Change to HOLD
   - Wait for clearer direction
   - Reduce position size to 5% if buying
   - Tighten stop loss to 3-4%

2. **Below 3/10 (Bearish):**
   - Change to SELL/AVOID
   - Exit existing positions
   - Move to stablecoins
   - Wait for sentiment recovery

**Triggers to watch:**
- Major regulatory crackdown news
- Exchange hack or security issues
- Macro market deterioration
- Technical breakdown below key support

The current recommendation is based on the positive sentiment. Always reassess if conditions change materially."

---

### Use Case 4: Entry Timing

**Question:** "Should I buy the full position now or scale in over time?"

**AI Response:** "For a 7.5% position, here's a smart scaling approach:

**Immediate Entry (40%):**
- Buy 3% position at current $90,000
- Captures move if price runs immediately
- Reduces regret if you miss the move

**Scaled Entries (60%):**
- 2.5% at $88,200 (2% dip) - LIMIT ORDER
- 2% at $86,400 (4% dip) - LIMIT ORDER

**Benefits:**
1. Average entry ~$88,600 if all fill
2. Reduces FOMO-driven mistakes
3. Protects against immediate reversal
4. Disciplined, plan-based entries

**If price runs without pulling back:**
- You still have 40% exposure
- Better to catch partial move than none
- Don't chase - stick to the plan

**Stop Loss:**
- Place at $85,500 for all entries
- Adjust as position builds

This balances urgency with discipline."

---

### Use Case 5: Understanding Technical Levels

**Question:** "Why is the stop loss specifically at $85,500?"

**AI Response:** "The $85,500 stop loss is strategically placed because:

**Technical Factors:**
1. **Recent Support Zone:** $86,000-$86,500 acted as support in the last 2 weeks
2. **5% Risk Level:** Aligns with BTC's typical volatility (10-15% daily swings)
3. **Round Number Buffer:** Just below $86,000 psychological level to avoid stop hunting

**Risk Management:**
4. **Position Sizing:** 7.5% position × 5% risk = 0.375% portfolio risk
5. **R/R Ratio:** Enables 1:3 risk/reward to first target at $94,500

**What it protects against:**
- Normal market noise and consolidation
- Minor pullbacks that don't invalidate the thesis
- Prevents emotional decision-making

**When to adjust:**
- If price moves to $92,000+, consider trailing stop to $87,500 (breakeven + fees)
- Never widen the stop - only tighten as price moves in your favor

The key is this level preserves capital while giving the trade room to work."

---

## Best Questions to Ask

### 📊 **Strategy Questions**
- "Why this entry level vs. waiting for a better price?"
- "How would you adjust if I'm more/less risk-averse?"
- "What's the best way to scale in/out?"
- "Should I use market or limit orders?"

### 🛡️ **Risk Management**
- "What if X happens?" (various scenarios)
- "How tight should my stop loss be?"
- "What position size for my risk tolerance?"
- "When should I cut losses vs. hold through?"

### 📰 **News & Events**
- "How would specific news affect this trade?"
- "What catalysts should I watch?"
- "How does sentiment impact the recommendation?"
- "What would invalidate this thesis?"

### ⏰ **Timing Questions**
- "Is timing critical or can I wait?"
- "What if I miss the entry?"
- "How long should I hold?"
- "When to take profits?"

### 🎯 **Technical Questions**
- "Why this stop loss level?"
- "What are the key support/resistance levels?"
- "How do you calculate target prices?"
- "What indicators did you consider?"

---

## Tips for Better Answers

### ✅ **DO:**
- Ask specific questions
- Reference the recommendation details
- Ask about alternative scenarios
- Request clarification on reasoning
- Ask "what if" questions

### ❌ **DON'T:**
- Ask vague questions like "What should I do?"
- Ignore the disclaimer (it's not financial advice)
- Expect predictions about exact prices
- Ask about unrelated cryptocurrencies
- Request illegal or unethical strategies

---

## Conversation Memory

The system remembers:
- ✅ **Last 3 Q&As** in the conversation
- ✅ **Full recommendation context**
- ✅ **Market conditions at analysis time**

The system DOES NOT remember:
- ❌ Questions from previous cryptocurrencies
- ❌ Questions from previous sessions (after refresh)
- ❌ Your personal positions or trades

**Tip:** Click "Clear History" to start fresh Q&A

---

## Example Full Conversation

**Recommendation:** BUY BTC @ $90,000, SL: $85,500, TP: $94,500

---

**Q1:** "Why buy now instead of waiting?"

**A1:** *[AI explains bullish setup, momentum, sentiment]*

---

**Q2:** "But what if it drops to $85,000 first?"

**A2:** *[AI discusses stop loss, risk management, invalidation]*

---

**Q3:** "Ok, so if I want to risk only 2% of my portfolio, what position size?"

**A3:** "If your portfolio is $10,000 and you want 2% max risk:
- Max risk: $200
- Risk per unit: $90,000 - $85,500 = $4,500
- Position size: $200 / $4,500 = 0.0044 BTC
- Dollar value: $396 position (3.96% of portfolio)

This gives you $200 risk if stopped out, or 2% portfolio impact."

---

**Q4:** "Thanks! One more thing - when should I take profits?"

**A4:** *[AI details profit-taking strategy at levels]*

---

## Technical Details

**Model Used:** Same as selected for main analysis (GPT-4o, etc.)

**Context Limit:** Last 3 Q&As + full recommendation context

**Response Time:** 2-5 seconds typically

**Cost:** ~$0.01-0.05 per question (depending on model)

---

## Privacy & Security

- ✅ Conversations are session-based (cleared on refresh)
- ✅ No data is stored permanently
- ✅ Your personal portfolio details are not shared
- ✅ Only current analysis context is used

---

## Troubleshooting

**Q&A not appearing?**
- Make sure you ran the full analysis first
- Check OPENAI_API_KEY is set
- Try refreshing the page

**Answers seem generic?**
- Ask more specific questions
- Reference specific numbers from the recommendation
- Provide more context in your question

**AI doesn't remember previous answers?**
- System remembers last 3 Q&As automatically
- If you need to reference earlier, include it in your question
- Click "Clear History" if context seems confused

---

**Use this feature to truly understand the AI's reasoning and make informed decisions!** 💡
