"""
    python3 backup-diferencial.py \
        ~/testar-backup/arquivos-teste/ \
        ~/testar-backup/backups/ \
        --exclude "*.log" "*.tmp" ".recycle"

    python3 backup-diferencial.py ~/testar-backup/arquivos-teste/ ~/testar-backup/backups/
                
"""

import time
import subprocess
from pathlib import Path
import argparse
from utils import inicio, termino, gera_log, validar_diretorios
import manifest
import tarfile

# Função para receber os argumentos via linha de comando
def receber_argumentos():
    parser = argparse.ArgumentParser(
        description='Sistema de Backup Full'
    )
    parser.add_argument(
        'origem',
        help="Diretório que será copiado."
    )
    parser.add_argument(
        'destino',
        help="Diretório onde o backup será armazenado."
    )
    parser.add_argument(
        '-e',
        '--exclude',
        nargs='*',
        default=[],
        help='Arquivos ou diretórios que serão ignorados do backup.'
    )
    return parser.parse_args()

def criar_backup_diferencial(origem, diferencas, destino):
    origem = Path(origem).expanduser().resolve()
    destino = Path(destino).expanduser().resolve()

    arquivos_backup = (diferencas["novos"] + diferencas["alterados"])

    with tarfile.open(destino, "w:gz") as arquivo_tar:
        for arquivo in arquivos_backup:

            caminho_completo = origem / arquivo["nome"]

            arquivo_tar.add(
                caminho_completo,
                arcname=arquivo["nome"]
            )

    return destino

# Faz o backup "diferencial"
def backup_clone (origem, destino, exclude):
    # disk = '/dev/sdc'                                             # pode ser usado para desmontar o disco
    hora_inicio = time.strftime('%H-%M-%S')
    dia_inicio = (time.strftime("%Y-%m-%d"))

    # Transforma as strings em Path
    origem = Path(origem).expanduser().resolve()
    destino = Path(destino).expanduser().resolve()
    destino_log = destino / "logs"

    # As necessidades dos três diretórios fornecidos pelo usuário (existência e se é diretório)
    validacao_diretorios, msg_erro = validar_diretorios(origem, destino, destino_log)
    if (validacao_diretorios == False):
        print(f"Erro: {msg_erro}")
        return False

    # Cria os diretórios de destino, caso necessário.
    destino.mkdir(parents=True, exist_ok=True)
    destino_log.mkdir(parents=True, exist_ok=True)

    # Retorna o caminho para o local onde o log sera salvo
    destino_log = gera_log(destino_log, "rsync")
    
    # Printar o Banner no arquivo de log
    start = inicio(hora_inicio)
    l = open(destino_log, 'w')
    l.write(start)
    l.close()

    arquivos_atuais = manifest.listar_arquivos(origem)
    caminho_manifest_full = manifest.encontrar_manifest_full_mais_recente(origem, destino)
    manifesto_full = manifest.carregar_manifest(caminho_manifest_full)
    diferencas = manifest.comparar_manifest(manifesto_full, arquivos_atuais)
    path_backup = destino / f"{dia_inicio}_{hora_inicio}-backup-diferencial.tar.gz"
    criar_backup_diferencial(origem, diferencas, path_backup)
    manifesto_diferencial = manifest.gerar_manifest_diferencial(origem, diferencas, manifesto_full["origem"], dia_inicio, hora_inicio)
    destino_manifesto = destino / f"{dia_inicio}_{hora_inicio}-manifesto-diferencial.json"
    manifest.salvar_manifest(manifesto_diferencial, destino_manifesto)

    # Printa o final e relatorio
    final = termino(dia_inicio, hora_inicio, path_backup, destino_log)
    r = open(destino_log, 'a')
    r.write(final)
    r.close()


if (__name__ == "__main__"):
    # log = '/home/estagiario01/testar-backup/logs/'
    # origem = '~/testar-backup/arquivos-teste/'
    # destino = '~/testar-backup/backups/'
    # exclude = ('*.log', '*.tmp', '.recycle')
    args = receber_argumentos()
    backup_clone(args.origem, args.destino, args.exclude)

