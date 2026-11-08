import csv

def carregarDados(csv = "base.csv"):
    encomendas = []
    with open(csv, modo = "r", encoding = "utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            encomenda = {
                "numEtiqueta": linha["numEtiqueta"],
                "numCadastro": linha["numCadastro"],
                "embalagem": linha["embalagem"],
                "transportadora": linha["transportadora"],
                "destinatario": {
                    "nome": linha["destinatario_nome"],
                    "categoriaPublico": linha["destinatario_categoriaPublico"]
                },
                "status": linha["status"],
                "dataChegada": linha["dataChegada"],
                "retirada": {
                    "retiradoPor": linha.get("retirada_retiradoPor", ""),
                    "parentesco": linha.get("retirada_parentesco", ""),
                    "statusRetirada": linha.get("retirada_statusRetirada", "PENDENTE"),
                    "autorizacaoEmail": linha.get("retirada_autorizacaoEmail", "NAO"),
                    "dataRetirada": linha.get("retirada_dataRetirada", "")
                },
                "detalhamento": {
                    "observacoes": linha.get("detalhamento_observacoes", ""),
                    "dataPrevistaChegada": linha.get("detalhamento_dataPrevistaChegada", ""),
                    "palavraChave": linha.get("detalhamento_palavraChave", "")
                }
            }
            encomendas.append(encomenda)
    return encomendas