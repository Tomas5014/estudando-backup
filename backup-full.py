import time
import subprocess

# Constrói o arquivo e path de backup e rotorna
def gera_backup(origem = '~/testar-backup/arquivos-teste/', destino = '~/testar-backup/backups/'):
    date = (time.strftime("%Y-%m-%d"))
    
    # Define o nome do arquivo de backup
    backup_file = '%s-backup-full.tar.gz' % date
    
    # Define a pasta de origem e de destino do backup
    path_destino = destino + backup_file
    
    backup = 'tar czvf %s %s' % (path_destino, origem)
    
    return backup

# Constroi os logs do sistema - Aqui selecionamos o nome do backup e o arquivo de logs que iremos criar.
def gera_log(destino='/home/estagiario01/testar-backup/logs/'):
    date = (time.strftime("%Y-%m-%d"))
    logfile = '%s-backup-full.txt' % date # Cria o arquivo de Log
    path_log = destino + logfile    # Arquivo de log

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

# Cria os backups
def backup_full():
    disk = '/dev/sdb'       # Define onde esta a particao que sera usada para guardar o backup
    hora_inicio = time.strftime("%H:%M:%S")
    path_log = gera_log()
    backup = gera_backup()
    log = ' >> %s' % path_log
    start = inicio(hora_inicio)

    # Printa o Banner
    l = open(path_log, 'w');
    l.write(start)
    l.close()

    # Monta todos os discos que estão no FSTAB
    mount = 'mount -a'
    subprocess.call(mount, shell=True)

    # Roda o backup
    subprocess.call(backup + log, shell=True)

    # Printa o final e relatório
    dia_incio = (time.strftime("%d-%m-%Y"))
    final = termino(dia_incio, hora_inicio, backup, path_log)
    r = open(path_log, 'a')
    r.write(final)
    r.close()

backup_full()