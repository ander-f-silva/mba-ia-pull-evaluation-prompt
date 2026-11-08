"""Baixa o prompt semente do LangSmith e salva em prompts/bug_to_user_story_v1.yml."""

import sys
from pathlib import Path
from langsmith import Client
from utils import save_yaml, print_section_header

FILE_NAME = "bug_to_user_story_v1"
HANDLE_NAME = "leonanluppi"

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "prompts" / f"{FILE_NAME}.yml"

def pull_prompts_from_langsmith(prompt_id: str) -> dict:
    client = Client()
    prompt = client.pull_prompt(
        prompt_id,
        dangerously_pull_public_prompt=True,
    )

    data = {"system_prompt": "", "user_prompt": ""}
    for message in prompt.messages:
        template = message.prompt.template
        if "system" in message.__class__.__name__.lower():
            data["system_prompt"] = template
        else:
            data["user_prompt"] = template
    return data


def main():
    print_section_header("Pulling prompts from LangSmith")

    prompt_id = f"{HANDLE_NAME}/{FILE_NAME}"
    
    print(f"Prompt: {prompt_id}")
    print(f"Destino: {OUTPUT_PATH}")

    try:
        data = pull_prompts_from_langsmith(prompt_id)
        save_yaml(data, str(OUTPUT_PATH))
    except Exception as exc:
        print(f"❌ Falha ao baixar o prompt: {exc}")
        return 1

    print(f"✓ Prompt salvo em {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
