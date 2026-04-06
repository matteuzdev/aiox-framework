"""Setup OAuth do Gemini para geracao de imagens.

Este script configura a autenticacao OAuth do Gemini
para que voce possa usar o Nano Banana 2 sem custo extra,
usando sua cota existente do plano Gemini.

Uso:
  python setup_gemini_oauth.py
"""

import os
import sys
import json
import webbrowser
import time
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("ERRO: google-genai nao instalado.")
    print("Rode: pip install google-genai")
    sys.exit(1)


def check_api_key():
    """Verifica se ja existe uma API key configurada."""
    # Verifica variavel de ambiente
    api_key = os.environ.get("GOOGLE_API_KEY")
    if api_key:
        print("[OK] GOOGLE_API_KEY encontrada no ambiente.")
        return api_key

    # Verifica arquivo de config do Google
    config_dir = Path.home() / ".config" / "generative-ai"
    if config_dir.exists():
        for f in config_dir.iterdir():
            if f.suffix == ".json":
                try:
                    data = json.loads(f.read_text())
                    if "api_key" in data:
                        print(f"[OK] API key encontrada em {f}")
                        return data["api_key"]
                except Exception:
                    pass

    return None


def try_connect(api_key):
    """Testa se a API key funciona."""
    try:
        client = genai.Client(api_key=api_key)
        # Lista modelos para verificar autenticacao
        models = list(client.models.list())
        model_names = [m.name for m in models[:5]]
        print(f"[OK] Conectado ao Gemini!")
        print(f"     Modelos disponiveis: {', '.join(model_names)}")

        # Verifica se ha modelo de geracao de imagem
        image_models = [m for m in models if "image" in m.name.lower() or "flash" in m.name.lower()]
        if image_models:
            print(f"     Modelos de imagem: {image_models[0].name}")
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao conectar: {e}")
        return False


def get_api_key_from_browser():
    """Orienta o usuario a obter a API key do Google AI Studio."""
    print()
    print("=" * 60)
    print("CONFIGURAR CHAVE DO GEMINI")
    print("=" * 60)
    print()
    print("Para usar o Nano Banana 2 com sua conta Gemini:")
    print()
    print("1. Acesse: https://aistudio.google.com/apikey")
    print("2. Faca login com sua conta Google (a do seu plano Gemini)")
    print("3. Clique em 'Create API Key'")
    print("4. Copie a chave gerada")
    print()
    print("Abrindo o navegador...")
    print()

    webbrowser.open("https://aistudio.google.com/apikey")

    api_key = input("Cole sua API key aqui: ").strip()
    if not api_key:
        print("Nenhuma chave fornecida. Abortando.")
        return None

    return api_key


def save_api_key(api_key):
    """Salva a API key no ambiente e no arquivo de config."""
    # Salva no arquivo de config do Google
    config_dir = Path.home() / ".config" / "generative-ai"
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = config_dir / "google_api_key.json"
    config_file.write_text(
        json.dumps({"api_key": api_key}, indent=2),
        encoding="utf-8",
    )
    print(f"[OK] Chave salva em {config_file}")

    # Sugere setx para persistir no Windows
    print()
    print("Para tornar permanente no Windows, rode no terminal:")
    print(f'  setx GOOGLE_API_KEY "{api_key}"')
    print()
    print("Ou defina no .env do projeto:")
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        content = env_path.read_text(encoding="utf-8")
        if "GOOGLE_API_KEY" not in content:
            with open(env_path, "a", encoding="utf-8") as f:
                f.write(f"\nGOOGLE_API_KEY={api_key}\n")
            print(f"[OK] GOOGLE_API_KEY adicionada ao .env")
    else:
        env_path.write_text(f"GOOGLE_API_KEY={api_key}\n", encoding="utf-8")
        print(f"[OK] .env criado com GOOGLE_API_KEY")


def main():
    print("=" * 60)
    print("KONIG SYSTEMS — Gemini OAuth Setup")
    print("=" * 60)
    print()

    # Tenta chave existente
    api_key = check_api_key()
    if api_key:
        print("Testando chave existente...")
        if try_connect(api_key):
            print()
            print("Sua chave do Gemini ja esta configurada e funcionando!")
            print("Voce pode rodar: python generate_carousels_gemini.py")
            return

    # Precisa de nova chave
    print("Nenhuma chave do Gemini encontrada.")
    print()

    api_key = get_api_key_from_browser()
    if not api_key:
        sys.exit(1)

    print("\nTestando nova chave...")
    if try_connect(api_key):
        save_api_key(api_key)
        print()
        print("=" * 60)
        print("SETUP CONCLUIDO!")
        print("=" * 60)
        print()
        print("Agora voce pode gerar carrosseis com Nano Banana 2:")
        print("  python generate_carousels_gemini.py")
        print()
        print("Ou gerar um carousel especifico:")
        print("  python generate_carousels_gemini.py --post 1")
    else:
        print()
        print("ERRO: A chave nao funcionou. Verifique se:")
        print("1. A chave foi copiada corretamente")
        print("2. Sua conta Google tem acesso ao Gemini")
        print("3. A API de geracao de imagens esta habilitada")
        sys.exit(1)


if __name__ == "__main__":
    main()
