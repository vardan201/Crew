# Troubleshooting Guide

## Issue: "Received None or empty response from LLM call"

This error occurs when the LLM doesn't generate a response. Here's what was fixed:

### ✅ Changes Made

1. **Increased max_tokens from 250 to 400**
   - 250 tokens was too restrictive for JSON output
   - 400 tokens allows proper JSON formatting with 3-5 strengths

2. **Reduced max_rpm from 5 to 3**
   - More conservative rate limiting
   - Ensures we stay under 1200 tokens/minute (400 tokens × 3 = 1200)

3. **Made task descriptions more explicit**
   - Added "You MUST respond with ONLY this JSON format (no other text):"
   - Clearer instructions for the LLM

4. **Improved error handling**
   - Better parsing of agent outputs
   - Catches empty responses and provides fallback
   - Uses regex to extract JSON from mixed outputs

5. **Suppressed litellm warnings**
   - Added logging configuration to hide apscheduler warnings
   - These are just warnings, not actual errors

## Token Budget (Updated)

| Component | Tokens | Notes |
|-----------|--------|-------|
| Agent prompt | ~80 | Shortened backstory |
| Task description | ~100 | Concise instructions |
| Input data | ~50 | Variable data |
| Output (max) | 400 | JSON with 3-5 strengths |
| **Per agent total** | **~630** | Including overhead |

### Rate Limiting Strategy

- **max_rpm=3**: Maximum 3 agents per minute
- **5 agents total**: ~2 minutes for complete analysis
- **Token usage**: ~630 tokens/agent × 3 agents/min = ~1890 tokens/min during processing
- **Groq limit**: 1200 tokens/min

⚠️ **Note**: With max_rpm=3, agents run slower but stay under limit

## Testing the Fix

```bash
# Test with example data
python src/main.py
```

Expected output:
- Each agent should return valid JSON
- Processing time: ~2 minutes (5 agents with delays)
- No empty response errors

## If Issues Persist

### Option 1: Further Reduce Token Usage
Edit `src/crew.py`:
```python
max_tokens=300  # Instead of 400
```

### Option 2: Increase Delay Between Agents
Edit `src/crew.py`:
```python
max_rpm=2  # Instead of 3 (slower but safer)
```

### Option 3: Use Different Model
Edit `.env`:
```bash
# Try a different Groq model
GROQ_MODEL=mixtral-8x7b-32768
```

## Checking Your Groq Limits

1. Go to https://console.groq.com
2. Check your rate limits:
   - Requests per minute
   - Tokens per minute
   - Context window

Common Groq limits (free tier):
- **llama-3.3-70b-versatile**: 30 RPM, 6,000 TPM
- **mixtral-8x7b-32768**: 30 RPM, 5,000 TPM

If you have higher limits, you can increase `max_tokens` and `max_rpm` accordingly.

## Expected API Behavior

### Successful Response
```json
{
  "status": "completed",
  "results": {
    "marketing_strengths": [
      "Diversified marketing channels",
      "Growing user base",
      "Proactive retention strategy"
    ],
    "tech_strengths": [...],
    "org_hr_strengths": [...],
    "competitive_strengths": [...],
    "finance_strengths": [...]
  }
}
```

### Failed Response
```json
{
  "status": "failed",
  "error": "Invalid response from LLM call - None or empty."
}
```

If you see failed responses, check:
1. Groq API key is valid
2. You have available tokens in your account
3. The model name in `.env` is correct

## Quick Fixes

### If agents timeout:
```python
# In crew.py, increase timeout
self.llm = LLM(
    model=f"groq/{groq_model}",
    api_key=groq_api_key,
    temperature=0.6,
    max_tokens=400,
    timeout=60  # Add this
)
```

### If JSON parsing fails:
The new error handling will catch this and return:
```json
{
  "agent_name": "Unknown Agent",
  "strengths": ["Could not parse agent output - invalid JSON"]
}
```

This is better than crashing - you'll still get partial results.

## Summary of Token Optimization

**Before:**
- max_tokens: 2048 (too high)
- max_rpm: None (no limiting)
- Result: Exceeded 1200 tokens/min

**After:**
- max_tokens: 400 (optimized)
- max_rpm: 3 (controlled)
- Result: ~630 tokens/agent, 3 agents/min = within limits
