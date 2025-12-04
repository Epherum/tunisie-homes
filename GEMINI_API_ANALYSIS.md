# Gemini 1.5 Flash API Analysis

## Your Use Case

### Initial Batch (Local Ollama)
- **100-200 listings**: Processed locally on your PC
- **Cost**: $0
- **No API calls needed**

### Ongoing User Uploads (Gemini Flash)
- **20 uploads/day** (user-submitted listings)
- **1 API call per upload** (image analysis + description generation)
- **600 requests/month** (20 × 30 days)

---

## Gemini 1.5 Flash Free Tier Limits

### Rate Limits
| Metric | Free Tier | Your Usage | Headroom |
|--------|-----------|------------|----------|
| **Requests per minute** | 15 RPM | ~0.01 RPM (avg) | **1,500x** buffer |
| **Requests per day** | 1,500 RPD | 20 RPD | **75x** buffer |
| **Requests per month** | 1,000,000 RPM | 600 RPM | **1,666x** buffer |

### Token Limits
| Metric | Free Tier | Per Request | Daily Total |
|--------|-----------|-------------|-------------|
| **Input tokens/min** | 1,000,000 TPM | ~5,000 tokens | 100,000 tokens |
| **Output tokens/min** | 4,000,000 TPM | ~1,000 tokens | 20,000 tokens |

**Typical Request Breakdown**:
- Image: ~3,000 tokens
- Text description: ~500 tokens
- Prompt: ~1,000 tokens
- Response: ~800 tokens
- **Total**: ~5,300 tokens

---

## Verdict: More Than Enough ✅

### Your Usage is Only 0.06% of Monthly Limit

```
600 requests/month ÷ 1,000,000 limit = 0.0006 = 0.06%
```

### Safety Margins

**Best Case** (even distribution):
- You could handle **50,000+ uploads/month** before hitting limits

**Worst Case** (burst traffic):
- 15 RPM limit = **21,600 requests/day** possible
- Your 20/day = **0.09%** of burst capacity

**Spike Scenario**:
- Black Friday event: 200 uploads in 1 hour
- 200 ÷ 60 = **3.3 RPM** (still 4.5x under limit)

---

## Cost Analysis

### If You Ever Exceed Free Tier

Gemini 1.5 Flash Paid Pricing:
- **Input**: $0.075 per 1M tokens
- **Output**: $0.30 per 1M tokens

**Your Monthly Cost** (if paid):
```
Input:  600 requests × 4,500 tokens = 2.7M tokens = $0.20
Output: 600 requests × 800 tokens = 480K tokens = $0.14
Total: $0.34/month
```

**Annual**: ~$4.00/year

---

## Comparison to Alternatives

| Service | Free Tier | Your Usage | Sufficient? |
|---------|-----------|------------|-------------|
| **Gemini Flash** | 1M req/month | 600/month | ✅ **Yes** (0.06%) |
| **OpenAI GPT-4o-mini** | $0 (no free tier) | 600/month | ❌ ~$5/month |
| **Claude Haiku** | $0 (no free tier) | 600/month | ❌ ~$2/month |
| **Ollama (Local)** | Unlimited | Unlimited | ✅ But requires GPU |

---

## Architecture Recommendation

### Hybrid Approach (Your Current Plan) ✅

**Initial Data (Scraped Listings)**:
- Use **Ollama Llama 3.2 Vision** (local, free, unlimited)
- Process 100-200 listings overnight
- No API costs
- No rate limits

**User Uploads (Real-time)**:
- Use **Gemini 1.5 Flash** via Vercel Actions
- Fast response (<2 seconds)
- 20 requests/day = 0.06% of quota
- Excellent user experience

### Why This is Optimal

1. **Cost**: $0/month (within free tier)
2. **Performance**: Ollama for batch, Gemini for real-time
3. **Reliability**: No rate limit worries
4. **Scalability**: Can handle 10x growth (200 uploads/day) and still be free

---

## Scaling Scenarios

### Growth Path

| Stage | Daily Uploads | Monthly Requests | Gemini Status | Monthly Cost |
|-------|---------------|------------------|---------------|--------------|
| **Launch** | 20 | 600 | Free | $0 |
| **Growing** | 100 | 3,000 | Free | $0 |
| **Popular** | 500 | 15,000 | Free | $0 |
| **Viral** | 2,000 | 60,000 | Free | $0 |
| **Enterprise** | 10,000 | 300,000 | Free | $0 |
| **Scale Limit** | 33,333 | 1,000,000 | Free (at limit) | $0 |
| **Beyond** | 50,000 | 1,500,000 | Paid | **$0.51/month** |

**Conclusion**: You'd need **33,000+ daily uploads** before paying anything.

---

## Rate Limit Handling

### Gemini Flash is Generous

**Your Traffic Pattern**:
- 20 uploads/day
- Spread over ~12 waking hours
- ~1.7 uploads/hour
- ~0.03 requests/minute

**Rate Limit**: 15 RPM

**Buffer**: You're using **0.2%** of rate limit capacity.

### What if You Get a Spike?

**Scenario**: Product Hunt launch, 500 uploads in 1 hour

```
500 uploads ÷ 60 minutes = 8.3 RPM
Limit: 15 RPM
Status: ✅ Still under limit
```

**Worst Case**: 1,000 uploads in 1 hour
```
1,000 ÷ 60 = 16.7 RPM
Limit: 15 RPM
Status: ⚠️ Would hit rate limit
Solution: Queue requests (Vercel Queue, Redis)
```

**Realistic Spike Handling**:
Implement a simple queue:
```typescript
// Vercel Action with rate limiting
const rateLimiter = new RateLimit({
  max: 10, // Process 10 at a time
  interval: 60000 // Per minute
});
```

---

## Monitoring Recommendations

### Track Usage in Database

Add to `AIAnalysis` model:
```sql
SELECT
  DATE(created_at) as date,
  COUNT(*) as requests,
  COUNT(*) FILTER (WHERE model_used = 'gemini-1.5-flash') as gemini_calls
FROM ai_analyses
WHERE model_used = 'gemini-1.5-flash'
  AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at);
```

### Set Alerts

**Warning Threshold**: 1,000 requests/day (still 500 under limit)
**Critical Threshold**: 1,400 requests/day (approaching limit)

### Dashboard Metrics

Monitor in Vercel:
- Daily Gemini API calls
- Average response time
- Error rate
- Cost projection

---

## Gemini Flash vs Flash-8B

### Flash (Recommended) ✅
- **Free Tier**: 1M requests/month
- **Speed**: ~2 seconds
- **Quality**: Excellent for real estate
- **Your Usage**: 0.06% of limit

### Flash-8B (Alternative)
- **Free Tier**: 4M requests/month
- **Speed**: ~1 second (faster)
- **Quality**: Slightly lower
- **Your Usage**: 0.015% of limit

**Verdict**: Use regular **Flash**. The quality difference matters for renovation scores, and you're nowhere near the limit anyway.

---

## API Key Security

### For Vercel Actions

Store in environment variables:
```bash
GEMINI_API_KEY=your_key_here
```

**DO NOT**:
- Commit to Git
- Expose in frontend code
- Share in screenshots

**DO**:
- Use Vercel environment variables
- Rotate keys quarterly
- Monitor usage in Google AI Studio

---

## Fallback Strategy

### If Free Tier Ever Runs Out (Unlikely)

**Option 1**: Upgrade to Paid ($0.34/month)
**Option 2**: Queue requests (delay by minutes)
**Option 3**: Switch to Ollama for user uploads (slower UX)
**Option 4**: Hybrid - free tier for images, skip description generation

**Recommended**: Just upgrade. $0.34/month is negligible.

---

## Final Recommendation

### ✅ Use Gemini 1.5 Flash for User Uploads

**Why**:
1. You're using **0.06%** of the free tier
2. You could **10x your traffic** and still be free
3. **Fast** (<2 seconds) for good UX
4. **Reliable** (Google's infrastructure)
5. **Cost**: $0/month, even at 10x growth

**When to Worry**:
- You're getting 33,000+ uploads/day
- You're approaching 1M requests/month
- Then pay **$0.51/month** (still negligible)

**Verdict**: Don't overthink it. Gemini Flash free tier is perfect for your use case. Focus on building the product.
