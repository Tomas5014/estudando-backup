import time

# Gera a mensagem de inicio do backup para o arquivo de log
def inicio(hora):
    inicio = "="*16 + "\n"
    inicio += "INÍCIO DO BACKUP\n"
    inicio += "Hora: " + hora + "\n"
    inicio += "="*16 + "\n"
    return inicio

# Gera e printa a mensagem de fim de backup
def termino(dia_inicio, hora_inicio, path_backup, path_log):
    final = "FIM DO BACKUP\n"
    final += ("Início: " + dia_inicio + " - " + hora_inicio)
    final += ("\nLOG FILE: " + str(path_log))
    final += ("\nBACKUP FILE: " + str(path_backup))
    print(final)
    return final

# Gera o caminho para o log de backup
def gera_log(destino_log):
    date = (time.strftime("%Y-%m-%d"))
    logfile = '%s-backup-rsync.txt' % date
    destino_log = destino_log / logfile
    return destino_log

def verificar_existencia_diretorio (diretorio):
    if not diretorio.exists():
        return False
    return True

def verificar_se_eh_diretorio (diretorio):
    if not diretorio.is_dir():
        return False
    return True