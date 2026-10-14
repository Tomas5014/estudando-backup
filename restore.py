import time
from pathlib import Path
import manifest
from utils import extrair_backup


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

    extrair_backup(caminho_backup_full, destino_restauracao)

    # Extrair o conteúdo da base diferencial na pasta
    if manifest_diferencial != None:
        caminho_backup_diferencial = path_backups / manifest_diferencial["arquivo_backup_diferencial"] 
        extrair_backup(caminho_backup_diferencial, destino_restauracao)

    # Remover todos os arquivos marcados como removidos nos manifestos diferencias
    if manifest_diferencial != None:
        remover_arquivos_restauracao(destino_restauracao, manifest_diferencial)

# Restauração concluida.

restore_diferencial("~/testar-backup/arquivos-teste/", "~/testar-backup/backups/")