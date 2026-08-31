# AI Provider

CodeGate utilizes LiteLLM to interface with AI models.

## Current Configuration
- **Provider:** Groq via LiteLLM
- **Primary Model:** `groq/openai/gpt-oss-120b` (or equivalent open-source model available on Groq)
- **Fallback Model:** `groq/openai/gpt-oss-20b`

Model availability is provider-dependent. Configuration uses generic environment variables.
