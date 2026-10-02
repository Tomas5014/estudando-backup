import time
import subprocess
from pathlib import Path
import tarfile
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
    return parser.parse_args()


# Constroi o arquivo e path de backup e rotorna
def gera_backup(origem, destino):
    date = (time.strftime("%Y-%m-%d"))
    nome_arquivo_backup = '%s-backup-full.tar.gz' % date
    path_destino = destino / nome_arquivo_backup                # Operador "/" junta caminhos
    backup = ['tar', 'czvf', path_destino, origem]
    return backup, path_destino


# Gera o caminho para o log de backup
def gera_log(destino):
    date = (time.strftime("%Y-%m-%d"))
    logfile = '%s-backup-full.txt' % date
    path_log = destino / logfile
    return path_log


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


# Verifica a integridade do arquivo tar.gz gerado
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
def backup_full(origem, destino, destino_log):
    # disk = '/dev/sdb'       # Define onde esta a particao que sera usada para guardar o backup

    # Transformar string em Path
    origem = Path(origem).expanduser()
    destino = Path(destino).expanduser()
    destino_log = Path(destino_log).expanduser()

    hora_inicio = time.strftime("%H:%M:%S")
    path_log = gera_log(destino_log)
    backup, path_backup = gera_backup(origem, destino)
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


if (__name__ == "__main__"):
    # origem = '~/testar-backup/arquivos-teste/'
    # destino = '~/testar-backup/backups/'
    # log = '/home/estagiario01/testar-backup/logs/'
    args = receber_argumentos()
    backup_full(args.origem, args.destino, args.log)