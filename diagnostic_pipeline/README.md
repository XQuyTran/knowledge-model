

## Local LLM setup via environment variables

For local testing, create environment variables before running the pipeline.

### Generic OpenAI-compatible endpoint

```bash
export LLM_API_BASE_URL=https://api.openai.com/v1
export LLM_API_KEY=replace-me
export LLM_MODEL=gpt-4.1-mini
export LLM_TIMEOUT_SECONDS=20
```

### Azure OpenAI endpoint

```bash
export AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
export AZURE_OPENAI_API_KEY=replace-me
export AZURE_OPENAI_DEPLOYMENT=your-deployment-name
export AZURE_OPENAI_API_VERSION=2026-01-01-preview
export LLM_MODEL=gpt-4.1-mini
export LLM_TIMEOUT_SECONDS=20
```

If `DiagnosticPipeline` is created without an explicit `llm_client`, it will automatically try to build one from the current environment variables.
