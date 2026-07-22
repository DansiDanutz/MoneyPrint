# Curiosity — "Did You Know?" YouTube Channel Playbook

How we leverage MoneyPrinterTurbo (this repo) to run an automated faceless
YouTube channel producing short "Did you know?" videos about high tech,
fascinating people, and things most people don't know.

## What the tool gives us out of the box

Given just a topic ("Did you know octopuses have three hearts?"), it will:

1. **Write the script** with an LLM (Kimi, OpenAI, Gemini, DeepSeek, Ollama…)
2. **Extract search keywords** and download matching stock footage from
   Pexels / Pixabay / Coverr (free, HD)
3. **Generate voiceover** (Edge TTS free, or ElevenLabs/Azure for quality)
4. **Add subtitles** (styled: font, color, outline, position)
5. **Add background music** and render 9:16 (Shorts) or 16:9 HD video
6. **Publish directly** to YouTube Shorts / TikTok / Instagram (built-in
   cross-platform publishing)
7. Batch mode: generate several variants per topic, keep the best

It exposes a **WebUI** (Streamlit, `webui.bat`), an **API** (FastAPI,
`main.py`), and a **CLI** (`cli.py`) — the API is what we automate against.

## Channel format

- **Name idea**: "Curiosity — Did You Know?"
- **Format**: 25–45 second 9:16 Shorts, hook in the first 2 seconds
  ("Did you know…?"), 3 rapid facts or 1 deep fact, end with a question to
  drive comments ("Which one surprised you?")
- **Pillars** (rotate daily):
  1. High tech (AI, space, chips, robots)
  2. Remarkable people (inventors, record holders, unsung geniuses)
  3. Nature & science oddities
  4. History & "hidden world" facts (how things actually work)
- **Cadence**: 2–3 Shorts/day. Volume is the growth lever for Shorts.

## Setup (one-time, ~30 min)

1. `cp config.example.toml config.toml`
2. Get free API keys:
   - **Pexels** (footage): https://www.pexels.com/api/
   - **Pixabay** (fallback footage): https://pixabay.com/api/docs/
   - **LLM**: any provider in `config.toml` (Gemini has a free tier;
     Ollama runs local for zero cost)
3. Voice: start with **Edge TTS** (free). Upgrade to ElevenLabs once the
   channel earns — voice quality is the #1 perceived-quality factor.
4. Run `webui.bat` to test one video end-to-end, tune subtitle style and
   music once, then keep those settings as the channel's visual identity.

## Automation pipeline (our layer on top)

```
Topic list (Google Sheet / topics.txt)
        │
        ▼  daily cron (this laptop or a droplet)
Script: pick next topic → POST /api/v1/videos (MPT API)
        │
        ▼  poll task until done
Render output → upload via built-in YouTube publishing
        │
        ▼
Log result, mark topic used
```

- Run the MPT API in Docker (`docker-compose.yml`) on one of the droplets
  (memo/dexter/nano) so the laptop isn't tied up rendering.
- A small script (Python or n8n/Make scenario) feeds one topic per run.
- Topic generation is itself an LLM call: "Give me 30 'did you know' facts
  about <pillar> that most people don't know, verifiable, non-obvious" —
  bank 100+ topics per month in one sitting, fact-check the best ones.

## Quality rules (what separates this from AI slop)

- **Verify facts** before rendering — one wrong fact kills channel trust.
- **Custom scripts beat auto-scripts**: let the LLM draft, but enforce the
  hook formula (question → surprise → payoff) via the prompt.
- Consistent subtitle style + same intro sound = brand recognition.
- Batch-generate 2–3 variants per topic, publish the best footage match.
- Mind YouTube's "inauthentic content" policy: add original value via
  strong scripts and consistent voice/branding; pure unedited stock-slop
  gets demonetized.

## Monetization path

1. 0–1k subs: focus purely on hook quality and posting consistency
2. YouTube Partner Program (Shorts: 3M views/90 days or long-form route)
3. Affiliate links in descriptions (tech gadgets fit the niche)
4. Repurpose the same renders to TikTok + Instagram (built-in publishing)
