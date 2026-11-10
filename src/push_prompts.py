"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

DICAS DE IMPLEMENTAÇÃO:

- O push é feito pelo cliente do LangSmith:

      from langsmith import Client
      from langchain_core.prompts import ChatPromptTemplate

      client = Client()
      prompt = ChatPromptTemplate.from_messages([
          ("system", system_prompt),
          ("user", user_prompt),
      ])
      url = client.push_prompt(
          f"{username}/bug_to_user_story_v2",
          object=prompt,
          is_public=True,
          description="...",
          tags=[...],
      )

- `username` vem de USERNAME_LANGSMITH_HUB no .env e precisa ser o seu handle
  do Hub. Se você ainda não tem um handle, veja as instruções no .env.example.

- A variável do template precisa ser {bug_report}, que é a chave de entrada
  usada no dataset de avaliação.

- Use `load_yaml` de utils.py para ler o arquivo .yml.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()

FILE_NAME = "bug_to_user_story_v2"
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / f"{FILE_NAME}.yml"
REQUIRED_FIELDS = ("description", "system_prompt", "user_prompt")


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB")
    prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_data["system_prompt"]),
        ("user", prompt_data["user_prompt"]),
    ])

    tags = list(prompt_data.get("tags") or [])
    for technique in prompt_data.get("techniques_applied") or []:
        tag = str(technique).strip().lower().replace(" ", "-")
        if tag and tag not in tags:
            tags.append(tag)

    try:
        url = Client().push_prompt(
            f"{username}/{prompt_name}",
            object=prompt,
            is_public=True,
            description=prompt_data.get("description", ""),
            tags=tags,
        )
    except Exception as exc:
        print(f"❌ Falha ao publicar {username}/{prompt_name}: {exc}")
        return False

    print(f"✓ Prompt publicado: {url}")
    return True


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    if not isinstance(prompt_data, dict):
        return False, ["Prompt precisa ser um objeto YAML"]

    for field in REQUIRED_FIELDS:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")

    system_prompt = str(prompt_data.get("system_prompt", "")).strip()
    user_prompt = str(prompt_data.get("user_prompt", "")).strip()

    if not system_prompt:
        errors.append("system_prompt está vazio")
    if not user_prompt:
        errors.append("user_prompt está vazio")
    if "TODO" in system_prompt or "TODO" in user_prompt:
        errors.append("prompt ainda contém TODOs")

    combined = f"{system_prompt}\n{user_prompt}"
    if "{bug_report}" not in combined:
        errors.append("O template precisa da variável {bug_report}")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("Pushing prompt to LangSmith")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")
    print(f"Prompt: {username}/{FILE_NAME}")
    print(f"Origem: {PROMPT_PATH}")

    data = load_yaml(str(PROMPT_PATH))
    if not data or FILE_NAME not in data:
        print(f"❌ Chave '{FILE_NAME}' não encontrada em {PROMPT_PATH}")
        return 1

    prompt_data = data[FILE_NAME]
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    if not push_prompt_to_langsmith(FILE_NAME, prompt_data):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
