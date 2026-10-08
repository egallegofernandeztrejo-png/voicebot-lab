# voicebot-lab

An end-to-end voicebot built step by step: a phone call goes through speech recognition, an LLM with tools and text to speech, and gets handed off to a human agent when needed. Every step is evaluated.

I've spent several years building IVR and voice channels in production. This repo is where I learn the generative AI side of the voicebot, in the open.

> **All data in this repo is synthetic.** No real calls, customers or business logic.

## Roadmap

| Phase | What | Status |
|---|---|---|
| 0 | Python warm-up: call analytics on a synthetic IVR dataset | ✅ Done |
| 1 | Text bot with an LLM: business rules, structured JSON output, function calling, escalation to a human | 🚧 In progress |
| 2 | Voice: Twilio → streaming STT → bot → TTS, with barge-in and transfer | ⏳ Planned |
| 3 | Evaluation: 30–50 test conversations, hallucinations, accuracy and latency, prompt A/B comparison | ⏳ Planned |

## Phase 0: call analytics

`stats.py` reads `data/llamadas.csv`, a dataset of 500 synthetic IVR calls, and reports:

- the overall outcome split (resolved in the IVR, transferred, abandoned),
- the outcome by call reason,
- the IVR resolution rate by number of speech-recognition failures,
- the average wait time before reaching an agent.

## Run it

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1    ·    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python stats.py
```

## Stack

Python · pandas. Coming next: an LLM API, Twilio, streaming STT/TTS.
