"""
    python3 backup-diferencial.py \
        ~/testar-backup/arquivos-teste/ \
        ~/testar-backup/backups/ \
        ~/testar-backup/logs/ \
        --exclude "*.log" "*.tmp" ".recycle"
"""

import time
import subprocess
from pathlib import Path
import argparse
from utils import inicio, termino, gera_log, validar_diretorios

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
        'log',
        help="Diretório onde os logs serão armazenados."
    )
    parser.add_argument(
        '-e',
        '--exclude',
        nargs='*',
        default=[],
        help='Arquivos ou diretórios que serão ignorados do backup.'
    )
    return parser.parse_args()

# Constroi o vetor para fazer o backup via subprocess.run()
def gera_backup (origem, destino, exclude):
    date = (time.strftime("%Y-%m-%d"))
    opts = '-Cravzp'

    # Monta o vetor
    backup = ['rsync', opts]
    for item in exclude:
        backup.append(f"--exclude={item}")
    backup.extend([origem, destino])
    return backup, destino


# Faz o backup "diferencial"
def backup_clone (origem, destino, exclude, destino_log):
    # disk = '/dev/sdc'                                             # pode ser usado para desmontar o disco
    hora_inicio = time.strftime('%H:%M:%S')

    # Transforma as strings em Path
    origem = Path(origem).expanduser().resolve()
    destino = Path(destino).expanduser().resolve()
    destino_log = Path(destino_log).expanduser().resolve()

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

    # Retorna um vetor com os parametro para fazer o backup "diferencial" via comando linux
    backup, path_backup = gera_backup(origem, destino, exclude)
    
    # Printar o Banner no arquivo de log
    start = inicio(hora_inicio)
    l = open(destino_log, 'w')
    l.write(start)
    l.close()

    # Monta todos os discos presentes no fstab
    mount = ['mount', '-a']
    resultado_mount = subprocess.run(mount)
    if resultado_mount.returncode != 0:
        print("Erro: falha ao montar os discos!")
        return

    # Roda o backup
    with open(destino_log, 'a') as log:
        resultado = subprocess.run(
            backup,
            stdout=log,
            stderr=log
        )

    #Verifica se o backup funcionou
    if resultado.returncode == 0:
        print("Backup realizado com sucesso!")
    else:
        print("Erro ao realizar o backup!")

    # Printa o final e relatorio
    dia_inicio = (time.strftime("%d-%m-%Y"))
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
    backup_clone(args.origem, args.destino, args.exclude, args.log)

