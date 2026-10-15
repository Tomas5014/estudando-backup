import time
from pathlib import Path
import manifest
from utils import extrair_backup, calcular_hash


def verificar_existencia_diretorio (diretorio):
    return diretorio.exists()

def verificar_se_eh_diretorio (diretorio):
    return diretorio.is_dir()

# As necessidades dos três diretórios fornecidos pelo usuário (existência e se é diretório)
def validar_diretorio (path_backups):
    # Verificar a existencia e se de fato é diretório (pasta_backup):
    if(not verificar_existencia_diretorio(path_backups)):
        return False, f"destino de backup não existe: {path_backups}"
    
    if not(verificar_se_eh_diretorio(path_backups)):
        return False, f"destino de backup não é um diretório: {path_backups}"

    return True, None

# Faz a remoção dos arquivos contidos em "removidos" do manifest diferencial
def remover_arquivos_restauracao(destino_restauracao, manifest_diferencial):
    destino_restauracao = Path(destino_restauracao).expanduser().resolve()
    
    lista_removidos = manifest_diferencial["removidos"]
    
    for removido in lista_removidos:
        caminho_remover = (destino_restauracao / removido["nome"]).resolve()

        if not caminho_remover.is_relative_to(destino_restauracao):
            print(f"Erro: caminho inválido no manifesto: {removido['nome']}")
            return False

        if caminho_remover.exists() and caminho_remover.is_file():
            caminho_remover.unlink()

    return True


# Constroi o estado dicionário dos arquivos esperados na restauração indexado pelo nome
def construir_estado_esperado(manifest_full, manifest_diferencial=None):
    estado = manifest.indexar_arquivos(manifest_full["arquivos"])
    
    if manifest_diferencial == None:
        return estado

    for arquivo in manifest_diferencial["novos"]:
        estado[arquivo["nome"]] = arquivo

    for arquivo in manifest_diferencial["alterados"]:
            estado[arquivo["nome"]] = arquivo

    for arquivo in manifest_diferencial["removidos"]:
        estado.pop(arquivo["nome"], None)

    return estado

# Valida a restauração verificando se todos os arquivos gerados possuem o hash esperado
def validar_restauracao(destino_restauracao, estado_esperado):
    
    sucesso = True

    # Valida se todos os arquivos esperados estão presentes na restauração da forma como deveria
    for nome, arquivo in estado_esperado.items():
        caminho = destino_restauracao / nome
        if not caminho.exists():
            print(f"[ERRO] Arquivo ausente: {nome}")
            sucesso = False
            continue
        hash_restaurado = calcular_hash(caminho)
        if hash_restaurado == arquivo["hash"]:
            print(f"[OK]: {nome}")
        else:
            print(f"[ERRO] Hash deferente: {nome}")
            sucesso = False

    # Valida se não há nenhum arquivo além do esperado na restauração
    esperados = set(estado_esperado.keys())
    encontrados = set()
    
    for caminho in destino_restauracao.rglob("*"):
        if caminho.is_file():
            relativo = caminho.relative_to(destino_restauracao)

            encontrados.add(
                str(relativo)
            )

    extras = encontrados - esperados

    for nome in extras:
        print(f"[ERRO] Arquivo inesperado:{nome}")
        sucesso = False

    return sucesso

def restore_diferencial(origem, path_backups):
    
    # Capturar dia e hora do inicio do backup
    data_inicio = time.strftime('%Y-%m-%d')
    hora_inicio = time.strftime('%H-%M-%S')

    # Transformar as entradas em Path
    origem = Path(origem).expanduser().resolve()
    path_backups = Path(path_backups).expanduser().resolve()

    # As necessidades dos três diretórios fornecidos pelo usuário (existência e se é diretório)
    validacao_diretorios, msg_erro = validar_diretorio(path_backups)
    if (validacao_diretorios == False):
        print(f"Erro: {msg_erro}")
        return False
    
    # Encontrar o último backup full e salvar conteúdo em uma variável
    caminho_manifest_full = manifest.encontrar_manifest_full_mais_recente(origem, path_backups)

    if caminho_manifest_full is None:
        mensagem_ausencia_full = ("Erro: nenhum backup full encontrado para essa origem.")
        
        print(mensagem_ausencia_full)

        # with open(destino_log, "a", encoding="utf-8") as log:
        #     log.write(f"\n{mensagem_ausencia_full}\n")
        return False
    manifest_full = manifest.carregar_manifest(caminho_manifest_full)

    # Encontrar o útlimo diferencial feito após o último full e salvar o conteúdo no último full
    base_full = caminho_manifest_full.name
    caminho_manifest_diferencial = manifest.encontrar_manifest_diferencial_mais_recente(origem, path_backups, base_full)
    manifest_diferencial = None
    if caminho_manifest_diferencial != None:
            manifest_diferencial = manifest.carregar_manifest(caminho_manifest_diferencial)


    # Criar a pasta de restauração
    destino_restauracao = path_backups / f"restauracao-{data_inicio}-{hora_inicio}"
    destino_restauracao.mkdir(parents=True, exist_ok=True)


    # Extrair o conteudo da base full do manifesto na pasta
    caminho_backup_full = path_backups / manifest_full["arquivo_backup"]

    sucesso, erro = extrair_backup(caminho_backup_full, destino_restauracao)

    if not sucesso:
        print(f"Erro ao extrair backup Full: {erro}")
        return False

    # Extrair o conteúdo da base diferencial na pasta
    if manifest_diferencial != None:
        caminho_backup_diferencial = path_backups / manifest_diferencial["arquivo_backup_diferencial"] 
        
        sucesso, erro = extrair_backup(caminho_backup_diferencial, destino_restauracao)
        if not sucesso:
            print(f"Erro ao extrair backup Diferencial: {erro}")
            return False

    # Remover todos os arquivos marcados como removidos nos manifestos diferencias
    if manifest_diferencial != None:
        remover_arquivos_restauracao(destino_restauracao, manifest_diferencial)

    # Restauração concluida.

    # Validar restauração
    estado_esperado = construir_estado_esperado(manifest_full, manifest_diferencial)
    resultado = validar_restauracao(destino_restauracao, estado_esperado)

    if resultado:
        print("Restauração concluida e validada com sucesso.")
        return True
    else:
        print("Erro: restauração concluída, mas a validação falhou.")
        return False

restore_diferencial("~/testar-backup/arquivos-teste/", "~/testar-backup/backups/")