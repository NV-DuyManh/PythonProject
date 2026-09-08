# AI Provider Configuration

CodeGate uses AI to perform deep code reviews, identifying bugs, security flaws, and maintainability issues that deterministic static analysis cannot catch.

CodeGate utilizes **LiteLLM** under the hood, allowing it to connect to virtually any LLM provider (OpenAI, Anthropic, Google, Groq, Azure, AWS Bedrock, Ollama, etc.).

By default, CodeGate is configured and tested against **Groq**, due to its extremely low latency which is ideal for blocking Pull Request workflows.

## Primary Configuration (Groq)

To use the recommended Groq configuration:

1. Obtain an API key from the [Groq Cloud Console](https://console.groq.com/).
2. Open your `.env` file and set the key:

```env
GROQ_API_KEY=gsk_your_api_key_here
```

CodeGate's default model settings in `compose.codegate.yml` are pre-configured for Groq:
- `CONFIG.MODEL=groq/openai/gpt-oss-120b` (Primary)
- `CONFIG.FALLBACK_MODELS=["groq/openai/gpt-oss-20b"]` (Fallback)

## Alternative Providers

If you wish to use a different provider (e.g., OpenAI), you must provide the API key and update the model string.

### Example: OpenAI

1. Add your OpenAI key to the `.env` file:
```env
OPENAI_API_KEY=sk-your_api_key_here
```

2. Update your `compose.codegate.yml` (or `.env` if exported) to point to OpenAI models:
```env
CONFIG.MODEL=openai/gpt-4o
CONFIG.FALLBACK_MODELS=["openai/gpt-4-turbo"]
```

### Local Models (Ollama)

You can run CodeGate completely offline using Ollama:

1. Ensure Ollama is running and accessible from the Docker network.
2. Set the model config in your environment:
```env
CONFIG.MODEL=ollama/llama3
```

## Token Limits and Budgeting

CodeGate automatically calculates token budgets based on the model specified. It dynamically compresses large Pull Request diffs to fit within the model's context window. 

If you are using a custom or local model, you may need to explicitly define its context window:

```env
CONFIG.CUSTOM_MODEL_MAX_TOKENS=8192
```

## Privacy & Security

CodeGate sends your Pull Request diffs and descriptions to the configured AI provider. **No repository secrets or historical code (beyond the PR context) are sent.**
Ensure your organization's security policy permits sending code to your chosen AI provider. Use local models (like Ollama) for strict compliance environments.
