import time
import subprocess
from pathlib import Path
import tarfile

# Constrói o arquivo e path de backup e rotorna
def gera_backup(origem = '~/testar-backup/arquivos-teste/', destino = '~/testar-backup/backups/'):

    # expandir "~" para "/home/usuario/"
    origem = Path(origem).expanduser()
    destino = Path(destino).expanduser()

    date = (time.strftime("%Y-%m-%d"))
    
    # Define o nome do arquivo de backup
    backup_file = '%s-backup-full.tar.gz' % date
    
    # Define a pasta de origem e de destino do backup
    path_destino = destino / backup_file                # Operador "/" junta caminhos
    
    # backup = 'tar czvf %s %s' % (path_destino, origem)

    backup = ['tar', 'czvf', path_destino, origem]
    return backup, path_destino

# Constroi os logs do sistema - Aqui selecionamos o nome do backup e o arquivo de logs que iremos criar.
def gera_log(destino='/home/estagiario01/testar-backup/logs/'):
    date = (time.strftime("%Y-%m-%d"))
    destino = Path(destino).expanduser()
    logfile = '%s-backup-full.txt' % date # Cria o arquivo de Log
    path_log = destino / logfile    # Arquivo de log

    return path_log

# Gera a mensagem de inicio de backup para imprimir no inicio do log.
def inicio(hora):
    inicio = "="*16 + "\n"
    inicio += "INÍCIO DO BACKUP\n"
    inicio += "Hora: " + hora + "\n"
    inicio += "="*16 + "\n"
    
    return inicio

# Gera a mensagem de finalizacao para imprimir no fim do log e no terminal.
def termino(dia_inicio, hora_inicio, path_backup, path_log):
    final = "FIM DO BACKUP\n"
    final += ("Início: " + dia_inicio + " - " + hora_inicio)
    final += ("\nLOG FILE: " + str(path_log))
    final += ("\nBACKUP FILE: " + str(path_backup))
    print(final)
    return final

def verifica_backup (path_backup):
    try:
        with tarfile.open(str(path_backup), "r:gz") as arquivo:
            membros = arquivo.getmembers()

        if len(membros) > 0:
            print("Integridade do backup verificada com sucesso!")
            return True

        print("Erro: Backup está vazio.")
        return False
    except (tarfile.TarError, EOFError, OSError) as erro:
        print(f"Erro ao verificar o backup: {erro}")
        return False

# Cria os backups
def backup_full():
    disk = '/dev/sdb'       # Define onde esta a particao que sera usada para guardar o backup
    hora_inicio = time.strftime("%H:%M:%S")
    path_log = gera_log('/home/estagiario01/testar-backup/logs/')
    backup, path_backup = gera_backup('~/testar-backup/arquivos-teste/', '~/testar-backup/backups/')
    start = inicio(hora_inicio)

    # Printa o Banner
    l = open(path_log, 'w');
    l.write(start)
    l.close()

    # Monta todos os discos que estão no FSTAB
    mount = ['mount', '-a']
    resultado_mont = subprocess.run(mount)
    if (resultado_mont.returncode !=0):
        print("Erro: Falha ao montar discos.")
        return

    # Roda o backup
    with open(path_log, 'a') as log:
        resultado_backup = subprocess.run(
            backup,
            stdout=log,     # Imprime a saida, em caso de sucesso, no arquivo de log.
            stderr=log      # Imprime o erro, em caso de falha, no arquivo de log.
        )
    if (resultado_backup.returncode == 0):
        if path_backup.exists() and path_backup.stat().st_size > 0:
            
            if verifica_backup(path_backup):
                print("Backup realizado com sucesso!")
            else:
                print("Backup criado, mas falhou na verificação.")
    else:
        print("Erro: falha ao executar backup")

    # Printa o final e relatório
    dia_incio = (time.strftime("%d-%m-%Y"))
    final = termino(dia_incio, hora_inicio, path_backup, path_log)
    r = open(path_log, 'a')
    r.write(final)
    r.close()

# backup_full()
backup_full()