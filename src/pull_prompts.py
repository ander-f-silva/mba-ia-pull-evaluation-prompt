"""Baixa o prompt semente do LangSmith e salva em prompts/bug_to_user_story_v1.yml."""

import sys
from pathlib import Path

import yaml
from langsmith import Client
from utils import save_yaml, print_section_header

FILE_NAME = "bug_to_user_story_v1"
HANDLE_NAME = "leonanluppi"

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "prompts" / f"{FILE_NAME}.yml"


def pull_prompts_from_langsmith(prompt_id: str) -> list:
    client = Client()
    prompt = client.pull_prompt(
        prompt_id,
        dangerously_pull_public_prompt=True,
    )

    data = []
    for message in prompt.messages:
        role = message.__class__.__name__.removesuffix("MessagePromptTemplate").lower()
        data.append({role: message.prompt.template})

    return data


def build_prompt_file(messages: list) -> dict:
    """Preenche o template local com os textos vindos do LangSmith."""
    values = {}
    for message in messages:
        values.update(message)

    return {
        FILE_NAME: {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": values["system"],
            "user_prompt": values["human"],
            "version": "v1",
            "created_at": "2025-01-15",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }


def main():
    print_section_header("Pulling prompts from LangSmith")

    prompt_id = f"{HANDLE_NAME}/{FILE_NAME}"
    
    print(f"Prompt: {prompt_id}")
    print(f"Destino: {OUTPUT_PATH}")

    try:
        messages = pull_prompts_from_langsmith(prompt_id)
        data = build_prompt_file(messages)
       
        save_yaml(data, str(OUTPUT_PATH))
    except Exception as exc:
        print(f"❌ Falha ao baixar o prompt: {exc}")
        return 1

    print(f"✓ Prompt salvo em {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
