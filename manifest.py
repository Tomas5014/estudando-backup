from pathlib import Path
import json
import time


def salvar_manifest(dados, destino):
    with open(destino, "w", encoding='utf-8') as arquivo:
        json.dump(
            dados,
            arquivo,
            indent=4,
            ensure_ascii=False,
        )


def listar_arquivos(origem):
    origem = Path(origem).expanduser().resolve()

    
    arquivos = []

    for caminho in origem.rglob("*"):       # Percorre recursivamente tudo que existe dentro dessa pasta

        if caminho.is_file():
            
            info = caminho.stat()
            caminho_relativo = caminho.relative_to(origem)

            arquivos.append({
                'nome': str(caminho_relativo), 
                'tamanho': info.st_size, 
                'modificacao': info.st_mtime
            })
    
    return arquivos

def gerar_manifest(origem, tipo_backup):

    origem = Path(origem).expanduser().resolve()
    arquivos = listar_arquivos(origem)
    
    manifest = {
        "tipo": tipo_backup,
        "origem": str(origem),
        "data": time.strftime("%d-%m-%Y %H:%M:%S"),
        "arquivos": arquivos
    }

    return manifest


def carregar_manifest(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    return dados
        
if __name__ == "__main__":
    
    manifest = gerar_manifest("~/testar-backup/arquivos-teste", "full")

    salvar_manifest(manifest, "manifest.json")

    manifest_carregado = carregar_manifest("manifest.json")

    print(manifest_carregado)