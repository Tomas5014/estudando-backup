import time
from pathlib import Path


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
def gera_log(destino_log, tipo_backup):
    date = (time.strftime("%Y-%m-%d"))
    logfile = f"{date}-backup-{tipo_backup}.txt"
    destino_log = destino_log / logfile
    return destino_log

def verificar_existencia_diretorio (diretorio):
    return diretorio.exists()

def verificar_se_eh_diretorio (diretorio):
    return diretorio.is_dir()

# As necessidades dos três diretórios fornecidos pelo usuário (existência e se é diretório)
def validar_diretorios (origem, destino, destino_log):
    
    # Verificar a existencia e se de fato é diretório (origem):
    if(not verificar_existencia_diretorio(origem)):
        return False, f"origem não existe: {origem}"
    
    if not(verificar_se_eh_diretorio(origem)):
        return False, f"origem não é um diretório: {origem}"

    # Verifica se existe e se não é diretório. Se não existe, vou criar o diretório.
    if(verificar_existencia_diretorio(destino) and not verificar_se_eh_diretorio(destino)):
        return False, f"destino não é um diretório: {destino}"
    
    if(verificar_existencia_diretorio(destino_log) and not verificar_se_eh_diretorio(destino_log)):
        return False, f"log não é um diretório: {destino_log}"

    # Verificar se um dos destinos é igual ou contido na origem.
    if (destino == origem):
        return False, "origem e destino não podem ser o mesmo diretório."
    
    if (destino.is_relative_to(origem)):
        return False, "o destino não pode estar dentro do diretório de origem."
    
    if (destino_log == origem):
        return False, "origem e log não podem ser o mesmo diretório"
    
    if(destino_log.is_relative_to(origem)):
        return False, "o diretório de logs nao pode estar dentro da origem."

    return True, None

