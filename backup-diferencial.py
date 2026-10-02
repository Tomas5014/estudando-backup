import time
import subprocess
from pathlib import Path

# CONSTROI O ARQUIVE E PATH DE BACKUP
def gera_backup (path_origem = '~/testar-backup/arquivos-teste/', path_destino = '~/testar-backup/backups/', exclude = ('*.log', '*.tmp', '.recycle')):
    # path_origem eh o diretorio dos arquivos que quero fazer backup
    # path_destino eh o diretorio onde o backup sera salvo
    # exclude sao arquivos e diretorios que nao quaro copiar
    path_destino = Path(path_destino).expanduser()
    path_origem = Path(path_origem).expanduser()
    date = (time.strftime("%Y-%m-%d"))
    opts = '-Cravzp'
    #opts = 'rvtl'
    excludes = (
        '--exclude="%s"' % item
        for item in exclude
    )
    # backup = 'rsync %s %s %s %s' % (opts, excludes, path_origem, path_destino)

    backup = ['rsync', opts]
    backup.extend(excludes)
    backup.extend([path_origem, path_destino])
    #print backup
    #sys.exit()
    return backup, path_destino

def gera_log(path_log = '/home/estagiario01/testar-backup/logs/'):
    path_log = Path(path_log).expanduser()
    date = (time.strftime("%Y-%m-%d"))
    logfile = '%s-backup-rsync.txt' % date
    path_log = path_log / logfile

    return path_log

def inicio(hora):
    inicio = "="*10 + "\n"
    inicio += "INÍCIO DO BACKUP\n"
    inicio += "Hora: " + hora + "\n"
    inicio += "="*10 + "\n"
    
    return inicio

def termino(dia_inicio, hora_inicio, path_backup, path_log):
    final = "FIM DO BACKUP\n"
    final += ("Início: " + dia_inicio + " - " + hora_inicio)
    final += ("\nLOG FILE: " + str(path_log))
    final += ("\nBACKUP FILE: " + str(path_backup))
    print(final)
    return final

def backup_clone ():
    # disk = '/dev/sdc'                                             # pode ser usado para desmontar o disco
    hora_inicio = time.strftime('%H:%M:%S')
    
    path_log = gera_log('/home/estagiario01/testar-backup/logs/')   # retorna o caminho para o local onde o log será salvo
    
    path_origem = '~/testar-backup/arquivos-teste/'
    path_destino = '~/testar-backup/backups/'
    exclude = ('*.log', '*.tmp', '.recycle')
    backup, path_backup = gera_backup(path_origem, path_destino, exclude)   # retorna um vetor com os parametro para fazer o backup "diferencial" via comando linux
    
    start = inicio(hora_inicio)

    # Printar o Banner
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

backup_clone()
    