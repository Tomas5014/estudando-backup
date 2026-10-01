import time
import subprocess

# CONSTROI O ARQUIVE E PATH DE BACKUP
def gera_backup (path_origem = '~/testar-backup/arquivos-teste/', path_destino = '~/testar-backup/backups/', exclude = ('*.log', '*.tmp', '.recycle')):
    # path_origem eh o diretorio dos arquivos que quero fazer backup
    # path_destino eh o diretorio onde o backup sera salvo
    # exclude sao arquivos e diretorios que nao quaro copiar
    
    date = (time.strftime("%Y-%m-%d"))
    opts = 'Cravzp'
    #opts = 'rvtl'
    excludes = ' '.join(
        '--exclude="%s"' % item
        for item in exclude
    )
    backup = 'rsync -%s %s %s %s' % (opts, excludes, path_origem, path_destino)

    #print backup
    #sys.exit()
    return backup

def gera_log(path_log = '/home/estagiario01/testar-backup/logs/'):
    date = (time.strftime("%Y-%m-%d"))
    logfile = '%s-backup-rsync.txt' % date
    path_log += logfile

    return path_log

def inicio(hora):
    inicio = "="*10 + "\n"
    inicio += "INÍCIO DO BACKUP\n"
    inicio += "Hora: " + hora + "\n"
    inicio += "="*10 + "\n"
    
    return inicio

def termino(dia_inicio, hora_inicio, backup, path_log):
    final = "FIM DO BACKUP\n"
    final += ("Início: " + dia_inicio + " - " + hora_inicio)
    final += ("\nLOG FILE: " + path_log)
    final += ("\nBACKUP FILE: " + backup)
    print(final)
    return final

def backup_clone ():
    # disk = '/dev/sdc'                                             # pode ser usado para desmontar o disco
    hora_inicio = time.strftime('%H:%M:%S')
    
    path_log = gera_log('/home/estagiario01/testar-backup/logs/')   # retorna o caminho para o local onde o log será salvo
    
    path_origem = '~/testar-backup/arquivos-teste/'
    path_destino = '~/testar-backup/backups/'
    exclude = ('*.log', '*.tmp', '.recycle')
    path_backup = gera_backup(path_origem, path_destino, exclude)   # retorna o comando linux para fazer o backup "diferencial"
    
    log = ' >> %s' %path_log
    start = inicio(hora_inicio)

    # Printar o Banner
    l = open(path_log, 'w')
    l.write(start)
    l.close()

    # Monta todos os discos presentes no fstab
    mount = 'mount -a'
    resultado_mount = subprocess.call(mount, shell=True)

    if resultado_mount != 0:
        print("Erro ao montar os discos!")
        return

    # Roda o backup
    resultado = subprocess.call(path_backup + log, shell=True)

    if resultado == 0:
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
    