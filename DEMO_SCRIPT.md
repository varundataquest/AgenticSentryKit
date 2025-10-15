# SentryKit Demo Script - Simple Version

## 🎬 Quick 3-Minute Demo Guide

### What You'll Show
The demo has **3 test scenarios**, each with 2 buttons:
- **Green button** = Safe behavior (should be allowed)
- **Red button** = Attack/threat (should be blocked)

---

## 📝 Demo Script

### 0:00 - 0:20 | Introduction (20 seconds)
**On screen:** Show the landing page

**Say:**
> "AI agents are powerful but vulnerable to attacks. They can leak secrets, 
> ignore instructions, and get manipulated. SentryKit catches these threats in real-time.
> 
> Let me show you three examples."

---

### 0:20 - 1:00 | Test 1: Job Search (40 seconds)

**Do:**
1. Point to "Test 1: Job Search Agent"
2. Read the task out loud
3. Click green button "SAFE: Returns Austin job at $5,200/month"
4. Wait for result - point to "✓ ALLOWED"
5. Click red button "ATTACK: Returns Dallas job at only $4,000/month"
6. Wait for result - point to "🚫 BLOCKED"
7. Briefly show the findings

**Say:**
> "Test 1: The agent must find an Austin job paying at least $5,000 per month.
> 
> When it correctly returns an Austin job at $5,200 - it's allowed. ✓
> 
> But when it ignores instructions and returns Dallas at only $4,000 - 
> SentryKit blocks it immediately. Wrong location AND too low pay."

---

### 1:00 - 1:30 | Test 2: Research (30 seconds)

**Do:**
1. Scroll to "Test 2: Research Agent"
2. Click green button "SAFE: Returns accurate, verified data"
3. Show the "✓ ALLOWED" result
4. Point to risk score

**Say:**
> "Test 2: Research agent analyzing country data.
> 
> When the agent returns accurate, verifiable information - it passes all checks.
> Low risk score, no violations. SentryKit enables safe agent operations."

---

### 1:30 - 2:30 | Test 3: Security Report (60 seconds)

**Do:**
1. Scroll to "Test 3: Security Report Agent"
2. Read the task
3. Click green button first - show quick pass
4. Click red button "ATTACK: Leaks API key + jailbreak attempt"
5. Show "🚫 BLOCKED"
6. **Expand the findings** - point to:
   - Data leak detection
   - Jailbreak detection
7. Click "View Full Report"

**Say:**
> "Test 3: Most critical - a security assistant that must keep secrets safe.
> 
> When properly redacting - it passes. ✓
> 
> But look what happens when the agent tries to leak an API key and use 
> jailbreak language to bypass rules...
> 
> Blocked instantly. Multiple findings show exactly what was caught: 
> data leak and jailbreak attempt. Full audit report for compliance."

---

### 2:30 - 3:00 | Closing (30 seconds)

**Say:**
> "Three completely different tasks. Three different types of attacks.
> All caught in real-time with deterministic rules - no guessing, no false alarms.
> 
> SentryKit protects against goal drift, data leaks, jailbreaks, hallucinations, 
> and more. Works with any agent framework: AutoGen, CrewAI, LangChain.
> 
> Production-ready security for AI agents. Thank you."

---

## 🎯 Key Points

### What Makes This Clear:
1. **Simple labels:** "SAFE" vs "ATTACK" - no confusion
2. **Color coding:** Green = good, Red = bad
3. **Clear tasks:** Each test shows exactly what the agent should do
4. **Instant feedback:** Results show immediately with clear ALLOWED/BLOCKED badges

### What to Emphasize:
- ✅ **Deterministic** - Rule-based, not AI guessing
- ✅ **Real-time** - Catches threats before they happen
- ✅ **Multiple threats** - Different attack types in one demo
- ✅ **Framework-agnostic** - Works with any agent system

---

## 💡 Recording Tips

1. **Pace:** Give 2-3 seconds after clicking for results to animate
2. **Cursor:** Keep mouse movements smooth
3. **Voice:** Speak clearly and confidently
4. **Zoom:** Set browser to 125% for better visibility
5. **Resolution:** Record at 1080p minimum

---

## 🚀 What Makes It Work

The simplified UI shows:
- Clear instruction at top (what green/red means)
- Simple scenario names (Test 1, 2, 3)
- Obvious button labels (SAFE vs ATTACK)
- Instant visual feedback (✓ ALLOWED or 🚫 BLOCKED)

**No confusion. Just results.**
