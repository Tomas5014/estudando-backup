from pathlib import Path
import tarfile


def criar_backup_diferencial(origem, diferencas, destino):
    origem = Path(origem).expanduser().resolve()
    destino = Path(destino).expanduser().resolve()

    arquivos_backup = (diferencas["novos"] + diferencas["alterados"])

    with tarfile.open(destino, "w:gz") as arquivo_tar:
        for arquivo in arquivos_backup:

            caminho_completo = origem / arquivo["nome"]

            arquivo_tar.add(
                caminho_completo,
                arcname=arquivo["nome"]
            )

    return destino
