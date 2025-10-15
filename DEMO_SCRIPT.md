# SentryKit 3-Minute Demo Script

## 🎥 Setup Before Recording

1. **Open browser** to http://127.0.0.1:8765
2. **Zoom level**: Set browser to 125-150% for visibility
3. **Window size**: Full screen or large window
4. **Clear cache**: Hard refresh (Cmd+Shift+R) to ensure fresh load
5. **Close notifications**: Silence Slack, email, etc.
6. **Audio test**: Check microphone levels
7. **Practice run**: Do one full walkthrough before recording

---

## 📋 3-Minute Script

### **[0:00-0:30] Opening - The Problem (30 seconds)**

**[Show: Landing page, scroll slowly from top to bottom]**

**Script:**
> "AI agents are transforming how we work, but they come with serious security risks.
> 
> They can leak sensitive data like API keys and passwords. They can ignore instructions and drift from their goals. They can be manipulated through jailbreak attacks.
>
> Traditional security tools can't catch these threats because they happen at the AI output level.
>
> SentryKit provides real-time, deterministic guardrails that detect and block these attacks instantly. Let me show you."

**[Pause for 1 second at the instruction box]**

---

### **[0:30-1:10] Test 1 - Goal Drift Detection (40 seconds)**

**[Scroll to show Test 1 clearly]**

**Script:**
> "Test one: A job search agent. The task is simple - find an Austin internship paying at least five thousand dollars per month.

**[Point to or hover over green button]**

> "First, the safe behavior. The agent correctly returns an Austin job at fifty-two hundred per month."

**[Click green button, wait for result]**

> "And it passes. Allowed. No security issues."

**[Click red button]**

> "Now watch what happens when the agent tries to cheat. It returns a Dallas job - wrong city - and it only pays four thousand dollars - below the minimum."

**[Wait for BLOCKED result]**

> "Blocked immediately. SentryKit caught both violations: wrong location AND pay too low. This is goal drift detection in action."

---

### **[1:10-1:40] Test 2 - Clean Research (30 seconds)**

**[Scroll to Test 2]**

**Script:**
> "Test two: A research agent analyzing geographic data about countries.

**[Click green button]**

> "When the agent provides accurate, verifiable information backed by evidence - Bolivia and Ethiopia both meet the criteria - it passes all security checks.

**[Point to risk score]**

> "Low risk score. No violations. No hallucinations. This shows that SentryKit doesn't just block threats - it enables safe, compliant agent operations without false alarms."

---

### **[1:40-2:30] Test 3 - Data Leak & Jailbreak (50 seconds)**

**[Scroll to Test 3]**

**Script:**
> "Test three: The most critical scenario. A security assistant that must summarize incidents without leaking secrets.

**[Click green button quickly]**

> "When properly redacting sensitive information - passes.

**[Click red button]**

> "But now watch closely. The agent attempts to leak an API key - 's k dash A B C D' - and uses jailbreak language saying 'no rules apply now' to bypass safety controls.

**[Wait for BLOCKED result, then expand or point to findings]**

> "Blocked instantly. Look at the findings: Data leak detected - the API key pattern was caught. Jailbreak detected - the override attempt was identified.

**[Click 'View Full Report' if time allows, or just hover over it]**

> "And we get a full audit report for compliance and debugging. Every decision is explainable and traceable."

---

### **[2:30-3:00] Closing - The Value Proposition (30 seconds)**

**[Scroll to show all three tests or return to top]**

**Script:**
> "Three completely different tasks. Three types of attacks: goal drift, data leaks, and jailbreak attempts. All caught in real-time.
>
> Every check is deterministic - no AI guessing, no false positives. Sub-fifty millisecond response times. Works with any agent framework: OpenAI, LangChain, CrewAI, AutoGen.
>
> SentryKit: Production-ready security for the age of AI agents.
>
> Check out our GitHub repository and documentation to get started. Thank you."

**[End with screen showing the landing page or GitHub link]**

---

## 🎯 Key Talking Points (Don't Forget!)

### Must Emphasize:
- ✅ **Deterministic** - Not AI checking AI, rule-based and reliable
- ✅ **Real-time** - Prevents issues before they reach users
- ✅ **Multiple threats** - 6 different security checks in one solution
- ✅ **Framework-agnostic** - Works everywhere
- ✅ **Production-ready** - Fast, accurate, auditable

### Visual Highlights:
- 🟢 Green = Safe behavior
- 🔴 Red = Attack/threat
- ✓ ALLOWED badge (green)
- 🚫 BLOCKED badge (red)
- Risk scores
- Detailed findings with evidence
- Audit reports

---

## 💡 Pro Tips for Recording

### Pacing:
- **Speak clearly** but don't rush
- **Pause 2-3 seconds** after clicking buttons to let animations complete
- **Let results display fully** before moving to next action
- **Breathe naturally** between scenarios

### Mouse Movement:
- **Smooth, deliberate movements** - no jerky cursor
- **Hover briefly** on important elements to draw attention
- **Don't wave the cursor around** while talking
- **Click confidently** - no hesitation

### Voice:
- **Enthusiastic but professional** tone
- **Emphasize key words**: deterministic, real-time, blocked, allowed
- **Vary your pace** - slower for important points, normal for descriptions
- **Smile while speaking** - it comes through in your voice

### Technical Setup:
- **Resolution**: 1920x1080 minimum
- **Frame rate**: 30fps or 60fps
- **Audio**: Clear, no echo (use headset mic if needed)
- **Lighting**: If showing yourself, ensure good lighting
- **Background**: Quiet space, no interruptions

---

## 📊 What Makes This Demo Effective

### Structure:
1. **Problem statement** - Hook the audience (security risks)
2. **Solution introduction** - SentryKit does X
3. **Three diverse examples** - Show versatility
4. **Clear outcomes** - Green passes, red blocks
5. **Value summary** - Why it matters

### Variety:
- Different agent types (job search, research, security)
- Different attacks (drift, none, leak+jailbreak)
- Different outcomes (pass, pass, block, block)
- Shows both threat detection AND safe operation

### Clarity:
- Simple labels (SAFE vs ATTACK)
- Color coding (green vs red)
- Instant visual feedback
- No technical jargon overload

---

## 🎬 Post-Recording Checklist

After recording, review for:
- [ ] Audio is clear throughout
- [ ] No long pauses or dead air
- [ ] All buttons clicked successfully
- [ ] Results displayed properly
- [ ] Mouse movements were smooth
- [ ] Total time is 2:45-3:15 (gives editing flexibility)
- [ ] Key messages were emphasized
- [ ] Energy level stayed consistent

### Optional Editing:
- Add subtle zoom on key findings
- Add text overlays for "BLOCKED" or "ALLOWED" moments
- Add music bed (very subtle, don't overpower voice)
- Add opening title card with "SentryKit Demo"
- Add closing card with GitHub link

---

## 🚀 Call to Action (End Slide)

If you're adding an end card, include:

```
🛡️ SentryKit
Real-Time Security for AI Agents

✓ 6 Security Checks
✓ Deterministic & Reliable  
✓ Framework-Agnostic
✓ Production-Ready

GitHub: github.com/varundataquest/AgenticSentryKit
Docs: [your docs link]
```

---

## 📝 Alternative 2-Minute Version

If you need a shorter version, reduce Test 2:

**[1:10-1:25] Test 2 - Compressed (15 seconds)**
> "Test two shows clean research data passing all checks. No false positives - SentryKit knows the difference between good and bad behavior."

This gives you an extra 15 seconds to expand on Tests 1 or 3, or to add more context in the opening/closing.

---

Good luck with your recording! 🎥
