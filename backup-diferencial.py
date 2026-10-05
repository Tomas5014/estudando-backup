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
def gera_backup (path_origem, path_destino, exclude):
    date = (time.strftime("%Y-%m-%d"))
    opts = '-Cravzp'

    # Monta o vetor
    backup = ['rsync', opts]
    for item in exclude:
        backup.append(f"--exclude={item}")
    backup.extend([path_origem, path_destino])
    return backup, path_destino


# Gera o caminho para o log de backup
def gera_log(path_log):
    date = (time.strftime("%Y-%m-%d"))
    logfile = '%s-backup-rsync.txt' % date
    path_log = path_log / logfile
    return path_log


# Gera a mensagem de inicio do backup para o arquivo de log
def inicio(hora):
    inicio = "="*10 + "\n"
    inicio += "INÍCIO DO BACKUP\n"
    inicio += "Hora: " + hora + "\n"
    inicio += "="*10 + "\n"
    return inicio


# Gera e printa a mensagem de fim de backup
def termino(dia_inicio, hora_inicio, path_backup, path_log):
    final = "FIM DO BACKUP\n"
    final += ("Início: " + dia_inicio + " - " + hora_inicio)
    final += ("\nLOG FILE: " + str(path_log))
    final += ("\nBACKUP FILE: " + str(path_backup))
    print(final)
    return final


def verificar_existencia_diretorio (diretorio):
    if not diretorio.exists():
        return False
    return True

def verificar_se_eh_diretorio (diretorio):
    if not diretorio.is_dir():
        return False
    return True

# Faz o backup "diferencial"
def backup_clone (path_origem, path_destino, exclude, path_log):
    # disk = '/dev/sdc'                                             # pode ser usado para desmontar o disco
    hora_inicio = time.strftime('%H:%M:%S')

    # Transforma as strings em Path
    path_origem = Path(path_origem).expanduser()
    path_destino = Path(path_destino).expanduser()
    path_log = Path(path_log).expanduser()

    # Verificar a existencia e se de fato é diretório (origem):
    if(not( verificar_existencia_diretorio(path_origem))):
        print(f"Erro: origem não existe: {path_origem}")
        return False
    if not(verificar_se_eh_diretorio(path_origem)):
        print(f"Erro: origem não é um diretório: {path_origem}")
        return False

    # Verifica se existe e se não é diretório. Se não existe, vou criar o diretório.
    if(verificar_existencia_diretorio(path_destino) and 
    not verificar_se_eh_diretorio(path_destino)):
        print(f"Erro: destino não é um diretório: {path_destino}")
        return False
    if(verificar_existencia_diretorio(path_log) and 
    not verificar_se_eh_diretorio(path_log)):
        print(f"Erro: log não é um diretório: {path_log}")
        return False

    # Cria os diretórios de destino, caso necessário.
    path_destino.mkdir(parents=True, exist_ok=True)
    path_log.mkdir(parents=True, exist_ok=True)

    # Retorna o caminho para o local onde o log sera salvo
    path_log = gera_log(path_log)

    # Retorna um vetor com os parametro para fazer o backup "diferencial" via comando linux
    backup, path_backup = gera_backup(path_origem, path_destino, exclude)
    
    # Printar o Banner no arquivo de log
    start = inicio(hora_inicio)
    l = open(path_log, 'w')
    l.write(start)
    l.close()

    # Monta todos os discos presentes no fstab
    mount = ['mount', '-a']
    resultado_mount = subprocess.run(mount)
    if resultado_mount.returncode != 0:
        print("Erro: falha ao montar os discos!")
        return

    # Roda o backup
    with open(path_log, 'a') as log:
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
    final = termino(dia_inicio, hora_inicio, path_backup, path_log)
    r = open(path_log, 'a')
    r.write(final)
    r.close()


if (__name__ == "__main__"):
    # log = '/home/estagiario01/testar-backup/logs/'
    # origem = '~/testar-backup/arquivos-teste/'
    # destino = '~/testar-backup/backups/'
    # exclude = ('*.log', '*.tmp', '.recycle')
    args = receber_argumentos()
    backup_clone(args.origem, args.destino, args.exclude, args.log)

