# PiiLab

A vet clinic booking agent on AgentCore that closes the OUT and STORED personal data leaks. See FINDINGS.md.

I ran this under agentcore dev (not deployed).

## Setup

Create and activate a virtual environment, then install the test dependencies.

Windows:

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt

macOS / Linux:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

## Tests

From the repo root (no AWS credentials needed):

    pytest

## Run the agent

Put these in agentcore/.env.local:

    LOCAL_DEV=1
    GUARDRAIL_ID=your-guardrail-id
    GUARDRAIL_VERSION=DRAFT
    AWS_REGION=us-east-1

Then:

    agentcore dev

And in a second terminal:

    agentcore invoke --dev "Hi, I'm Reginold Thistlewick Cumberbatch, reginold@example.test, +44 7700 900412. When is booking VET-1001, and can you text me a reminder?"
