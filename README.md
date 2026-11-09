# voicebot-lab

An end-to-end voicebot built step by step: a phone call goes through speech recognition, an LLM with tools and text to speech, and gets handed off to a human agent when needed. Every step is evaluated.

I've spent several years building IVR and voice channels in production. This repo is where I learn the generative AI side of the voicebot, in the open.

> **All data in this repo is synthetic.** No real calls, customers or business logic.

## Roadmap

| Phase | What | Status |
|---|---|---|
| 0 | Python warm-up: call analytics on a synthetic IVR dataset | ✅ Done |
| 1 | Text agent with an LLM: business rules, structured output, function calling, handoff to a human | ✅ Done |
| 2 | Voice: Twilio → streaming STT → agent → TTS, with barge-in and transfer | 🚧 Next |
| 3 | Evaluation: 30–50 test conversations, hallucinations, accuracy and latency, prompt A/B comparison | ⏳ Planned |

## Phase 1: text agent with tools

A customer-service agent for a fictional online shop ("Tienda Demo"), in Spanish, designed from the start to become a phone bot.

**What it does**

- Answers within a defined scope (order status, returns, payment issues) and declines everything else.
- **Looks up orders with function calling** (`consultar_pedido`). The model asks for the tool, my code runs it, and the answer to the customer is written only after the real result is back, so it never promises an action it hasn't taken.
- **Hands off to a human with context** (`transferir_a_agente`): a reason (customer request, angry customer, out of scope, unresolved) plus a short summary for the agent, so the customer doesn't have to repeat themselves. This is the same idea as the call data that travels with a transfer in an IVR.
- Replies in short, plain sentences with no formatting, because the text will be read aloud by a TTS.

**Design decisions**

- **The LLM proposes, the code decides.** Anything that must always hold lives in Python, not in the prompt. Example: the model kept adding the `PED-` prefix to order numbers even when told not to, so normalisation and validation moved into the tool itself (`PED-12345`, `12345` and `ped 12345` all resolve the same way).
- **Hard rules outside the model.** Two failed order lookups in a row trigger a transfer without asking the LLM, like the "N recognition failures → agent" rule in a classic IVR.
- **Resilience.** Primary and fallback model, request timeouts, limited retries, and a safe exit (transfer to an agent) if everything fails. A bug in a tool never crashes the conversation.
- **Model chosen with data, not by default.** `bench.py` measures mean and worst-case latency per model:

  | Model | Thinking level | Mean | Worst |
  |---|---|---|---|
  | gemini-3.8-flash | low | 22.1 s | 48.7 s |
  | gemini-flash-lite-latest | low | 0.6 s | 0.6 s |

  For voice, the worst case matters more than the mean: a 49-second silence on a phone call is a broken call. The faster model is the primary one; what it loses in reasoning quality will be measured in Phase 3.
- **A provider-agnostic layer** (`llm.py`) wraps the SDK, so the agent can switch LLM providers or compare models without touching the bot.

**Files**

| File | What it is |
|---|---|
| `bot.py` | The conversation loop, system prompt, handoff handling and hard rules |
| `llm.py` | LLM layer: config, fallback, latency logging, structured output, tool-calling loop |
| `herramientas.py` | Tools (order lookup, handoff), their declarations and the synthetic order data |
| `bench.py` | Latency benchmark (mean, min, max per model) |
| `stats.py` | Phase 0: analytics on `data/llamadas.csv` |

## Phase 0: call analytics

`stats.py` reads `data/llamadas.csv`, a dataset of 500 synthetic IVR calls, and reports the overall outcome split, the outcome by call reason, the IVR resolution rate by number of speech-recognition failures, and the average wait time before reaching an agent.

## Run it

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key" > .env
python bot.py
```

Try: `Mi pedido PED-48213 no ha llegado`, `mi pedido es el 55510`, `quiero hablar con una persona`.

## Stack

Python · Google Gemini API (`google-genai`) · Pydantic · pandas. Coming next: Twilio, streaming STT/TTS.