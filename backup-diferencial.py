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
from utils import inicio, verificar_se_eh_diretorio, verificar_existencia_diretorio, termino, gera_log

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

    # Verificar a existencia e se de fato é diretório (origem):
    if(not( verificar_existencia_diretorio(origem))):
        print(f"Erro: origem não existe: {origem}")
        return False
    if not(verificar_se_eh_diretorio(origem)):
        print(f"Erro: origem não é um diretório: {origem}")
        return False

    # Verifica se existe e se não é diretório. Se não existe, vou criar o diretório.
    if(verificar_existencia_diretorio(destino) and 
    not verificar_se_eh_diretorio(destino)):
        print(f"Erro: destino não é um diretório: {destino}")
        return False
    if(verificar_existencia_diretorio(destino_log) and 
    not verificar_se_eh_diretorio(destino_log)):
        print(f"Erro: log não é um diretório: {destino_log}")
        return False

    # Verificar se um dos destinos é igual ou contido na origem.
    if (destino == origem):
        print("Erro: origem e destino não podem ser o mesmo diretório.")
        return False
    if (destino.is_relative_to(origem)):
        print("Erro: o destino não pode estar dentro do diretório de origem.")
        return False
    if (destino_log == origem):
        print("Erro: origem e log não podem ser o mesmo diretório")
        return False
    if(destino_log.is_relative_to(origem)):
        print("Erro: o diretório de logs nao pode estar dentro da origem.")

    # Cria os diretórios de destino, caso necessário.
    destino.mkdir(parents=True, exist_ok=True)
    destino_log.mkdir(parents=True, exist_ok=True)

    # Retorna o caminho para o local onde o log sera salvo
    destino_log = gera_log(destino_log)

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

