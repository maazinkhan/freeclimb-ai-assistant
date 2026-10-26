# Manual deployed RAG benchmark — v1

**Date scored:** 2026-10-26 (sheet created 2026-10-06)  
**App under test:** https://freeclimb-ai-assistant.streamlit.app/  
**API backend:** https://freeclimb-ai-assistant-production.up.railway.app  
**Model:** gemini-2.5-flash  
**Corpus:** FreeClimb API Reference (`data/doc_urls.txt`, 1049 chunks)

## Scoring rules

- **Answer correct:** Factually right vs FreeClimb docs; for unsupported questions, a clear “don’t know” / out-of-scope refusal counts as correct.
- **Sources correct:** Cited URLs are on-topic for the question. Use `—` when no sources are expected (unsupported) or the answer correctly refuses without needing citations.
- **Retrieval relevant:** From the Sources list (and answer content), retrieved material looks on-topic. If sources are empty or clearly wrong for an in-docs question, mark ❌.

Mark each cell: `✅` / `❌` / `—`

Infrastructure failures (Gemini 503, timeouts): note under **Infra notes**, do not count as RAG failures — retry and score the successful attempt.

## Results

| # | Bucket | Question | Answer correct? | Sources correct? | Retrieval relevant? | Notes |
|---|--------|----------|-----------------|------------------|---------------------|-------|
| 1 | Basic | What is FreeClimb? | ✅ | ❌ | ✅ | `using-the-api` fits; 10DLC partner-campaign and `say` do not |
| 2 | Basic | What is a PerCL command? | ✅ | ✅ | ✅ | `percl-overview`, audio-stream PerCL, `getdigits` |
| 3 | Basic | How do I authenticate to the FreeClimb API? | ✅ | ✅ | ✅ | Basic auth + JWT issuance |
| 4 | API | How do I send an SMS with FreeClimb? What parameters are required? | ❌ | ❌ | ❌ | Fresh session refused (“can’t tell”); retrieved `sms-4` / `make-a-call`, not `send-a-message`. Earlier session answered but omitted required `to` |
| 5 | API | How do I make an outbound phone call? | ✅ | ❌ | ✅ | Scored the API answer (`make-a-call`). `outdial-1` still cited (PerCL vs HTTP) |
| 6 | API | How do I buy a phone number? | ✅ | ✅ | ✅ | Buy + available-numbers + incoming-numbers |
| 7 | API | How do I create an application? | ✅ | ✅ | ✅ | Sources judged on-topic (URLs not pasted) |
| 8 | API | What are FreeClimb webhooks used for? | ✅ | ✅ | ✅ | Sources judged on-topic. A later retry died mid-stream (infra) |
| 9 | Multi-step | How would I handle an inbound call and speak a message using PerCL? | ✅ | ❌ | ✅ | Say/Play is right. Noise: `createconference`, `messagedelivery` |
| 10 | Multi-step | How do I connect an incoming phone number to an application that can send SMS? | ✅ | ✅ | ✅ | Number `applicationId` + app `smsUrl` |
| 11 | Multi-step | How would I create a conference and add participants with FreeClimb? | ✅ | ✅ | ✅ | Create conference API + `AddToConference` |
| 12 | Edge | What happens if I try to make a call with invalid or missing parameters? | ✅ | ❌ | ✅ | Missing `applicationId` / `callConnectUrl` is right. Noise: `list-members`, `create-a-conference` |
| 13 | Edge | What are documented limitations or requirements when sending a message (SMS)? | ❌ | ❌ | ❌ | Mixes MMS/video limits and cites `say` |
| 14 | Unsupported | What is FreeClimb’s pricing for sending a fax to Mars? | ✅ | — | — | Clear “I don’t know” |
| 15 | Unsupported | How do I configure Kubernetes autoscaling in FreeClimb? | ✅ | — | — | Clear “I don’t know” |

## Summary

| Metric | Formula | Result |
|--------|---------|--------|
| Answer accuracy | correct answers / 15 | 13/15 = **87%** |
| Source accuracy | correct sources / in-docs questions (exclude `—`) | 7/13 = **54%** |
| Retrieval relevance | relevant retrievals / in-docs questions (exclude `—`) | 11/13 = **85%** |

**Top failures:** SMS send (Q4) misses `send-a-message` and either omits `to` or falsely refuses. SMS limits (Q13) dump MMS/video docs. Outbound call (Q5) retrieves PerCL `OutDial` next to the HTTP API. Several correct answers still cite extra off-topic URLs (Q1, Q9, Q12), which is why source accuracy lags retrieval.

**Infra notes:** Q8 retry on Streamlit Cloud raised `requests.exceptions.ChunkedEncodingError` (stream ended early; likely Gemini 503/429). Not scored as a RAG failure. UI now catches that error instead of showing a traceback.

## Resume line

> Evaluated the deployed RAG assistant against 15 representative FreeClimb documentation questions, achieving **87%** answer accuracy (source accuracy **54%**, retrieval relevance **85%** on in-docs questions) to identify failure cases.

## How to run

1. Open a fresh browser session on the live app (avoid polluted chat history).
2. Ask each question in order; mark the three score columns.
3. If Gemini returns 503, wait and retry that question; log under Infra notes.
4. Fill Summary and Top failures; then update README Evaluation.
