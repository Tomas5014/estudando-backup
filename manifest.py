from pathlib import Path
import json
import time


# Salva um manifest em um diretório destino
def salvar_manifest(dados, destino):
    with open(destino, "w", encoding='utf-8') as arquivo:
        json.dump(
            dados,
            arquivo,
            indent=4,
            ensure_ascii=False,
        )


# Retorna um dicionário dos arquivos de um diretório
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


# Gera um manifest para um backup full
def gerar_manifest_full(origem, data, hora):

    origem = Path(origem).expanduser().resolve()
    arquivos = listar_arquivos(origem)
    
    manifest = {
        "tipo": "backup_full",
        "origem": str(origem),
        "data": f"{data} {hora.replace("-",":")}",
        "arquivos": arquivos
    }

    return manifest


# Gera um manifest para um backup diferencial
def gerar_manifest_diferencial(origem, diferencas, base_full, data, hora):
    origem = Path(origem).expanduser().resolve()
    
    manifest = {
        "tipo": "diferencial",
        "base_full": str(base_full),
        "origem": str(origem),
        "data": f"{data} {hora.replace("-",":")}",
        "novos": diferencas["novos"],
        "alterados": diferencas["alterados"],
        "removidos": diferencas["removidos"],
    }
    return manifest


# Carrega o json do manifesto em um dicionário
def carregar_manifest(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    return dados

#Retorna um dicionário de arquivos onde o indicie é o nome do arquivo
# Essa função será usada para facilitar a busca de um arquivo pelo nome sem tem que percorre-lo.
def indexar_arquivos(arquivos):
    indice = {}

    for arquivo in arquivos:
        indice[arquivo["nome"]] = arquivo

    return indice


# Retorna todos os arquivos novos, modificados e removidos entre um manifesto 
# e arquivos de um diretório.
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

# Encontra o manifest do backup mais recente dentro do destino
def encontrar_manifest_full_mais_recente(origem, destino):
    destino = Path(destino).expanduser().resolve()
    origem = Path(origem).expanduser().resolve()

    candidatos = []

    for caminho in destino.glob("*-manifesto-full.json"):
        manifest = carregar_manifest(caminho)
        if(
            manifest["tipo"] == "backup_full"
            and Path(manifest["origem"]).resolve() == origem
        ):
            candidatos.append(caminho)

    if not candidatos: return None

    return max(
        candidatos,
        key=lambda caminho: caminho.stat().st_mtime
    )