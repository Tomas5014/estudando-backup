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
                'modificado': info.st_mtime
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

def indexar_arquivos(arquivos):
    indice = {}

    for arquivo in arquivos:
        indice[arquivo["nome"]] = arquivo

    return indice

def comparar_manifest(manifest_antigo, arquivos_atuais):
    arquivos_antigos = manifest_antigo["arquivos"]

    antigos = indexar_arquivos(arquivos_antigos)
    atuais = indexar_arquivos(arquivos_atuais)

    novos = []
    alterados = []
    removidos = []

    # Verifica se há arquivos alterados ou novos em atuais
    for nome, arquivo_atual in atuais.items():
        if nome not in antigos:
            novos.append(arquivo_atual)
        else:
            data_atual = arquivo_atual["modificado"]
            data_antiga = antigos[nome]["modificado"]
            tamanho_atual = arquivo_atual["tamanho"]
            tamanho_antigo = antigos[nome]["tamanho"]
            if((tamanho_antigo != tamanho_atual) or (data_antiga != data_atual)):
                alterados.append(arquivo_atual)

    # Verifica se há arquivos removidos em antigos.
    for nome, arquivo_antigo in antigos.items():
        if nome not in atuais:
            removidos.append(arquivo_antigo)

    return{
        "novos": novos,
        "alterados": alterados,
        "removidos": removidos,
    }


if __name__ == "__main__":
    
    # manifest = gerar_manifest("~/testar-backup/arquivos-teste", "full")

    # salvar_manifest(manifest, "manifest-2.json")

    manifesto_antigo = carregar_manifest("/home/estagiario01/repos/estudando-backup/manifest.json")
    manifesto_novo = carregar_manifest("/home/estagiario01/repos/estudando-backup/manifest-2.json")

    resultados = comparar_manifest(manifesto_antigo, manifesto_novo["arquivos"])

    print(resultados)