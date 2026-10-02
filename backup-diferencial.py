import time
import subprocess
from pathlib import Path


# Constroi o vetor para fazer o backup via subprocess.run()
def gera_backup (path_origem, path_destino, exclude):    
    date = (time.strftime("%Y-%m-%d"))
    opts = '-Cravzp'
    excludes = (
        '--exclude="%s"' % item
        for item in exclude
    )

    # Monta o vetor
    backup = ['rsync', opts]
    backup.extend(excludes)
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


# Faz o backup "diferencial"
def backup_clone (path_origem, path_destino, exclude, path_log):
    # disk = '/dev/sdc'                                             # pode ser usado para desmontar o disco
    hora_inicio = time.strftime('%H:%M:%S')

    # Transforma as strings em Path
    path_origem = Path(path_origem).expanduser()
    path_destino = Path(path_destino).expanduser()
    path_log = Path(path_log).expanduser()

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
    log = '/home/estagiario01/testar-backup/logs/'
    origem = '~/testar-backup/arquivos-teste/'
    destino = '~/testar-backup/backups/'
    exclude = ('*.log', '*.tmp', '.recycle')
    backup_clone(origem, destino, exclude, log)
    