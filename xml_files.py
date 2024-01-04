import os
import xml.etree.ElementTree as Et  # importa lib responsavel pelo parseamento de arquivo XML
from datetime import date


class Read_xml():
  def __init__(self, directory) -> None:
    self.directory = directory

  # Define um método que faz a leitura de todos os arquivos da pasta
  def all_files(self) :
    # percorre para cada arquivo no diretorio:
    # une o diretorio com o arquivo 
    return [ os.path.join(self.directory, arq) for arq in os.listdir(self.directory)
     if arq.lower().endswith(".xml")]  

  # faz leitura do XML
  def nfe_data(self, xml):
    root = Et.parse(xml).getroot()
    nsNFe = {"ns": "http://www.portalfiscal.inf.br/nfe"}

    # --- DADOS DA NFe -----
    # pega o número da nota nNF da NFe parseando entre as tags da NFe a partir da tag raiz do arquivo XML
    NFe = self.check_none(root.find("./ns:NFe/ns:infNFe/ns:ide/ns:nNF", nsNFe))

    # pega a serie da NFe
    serie = self.check_none(root.find("./ns:NFe/ns:infNFe/ns:ide/ns:serie", nsNFe))

    # pega a data de emissão da NFe
    data_emissao = self.check_none(root.find("./ns:NFe/ns:infNFe/ns:ide/ns:dhEmi", nsNFe))

    # Formata a data de emissao como dd/mm/aaaa
    data_emissao = f"{data_emissao[8:10]}/{data_emissao[5:7]}/{data_emissao[:4]}"


    # --- DADOS DO EMiTENTE da NFe -----
    chave = self.check_none(root.find("./ns:protNFe/ns:infProt/ns:chNFe", nsNFe))
    cnpj_emitente = self.check_none(root.find("./ns:NFe/ns:infNFe/ns:emit/ns:CNPJ", nsNFe))
    nome_emitente = self.check_none(root.find("./ns:NFe/ns:infNFe/ns:emit/ns:xNome", nsNFe))

    cnpj_emitente = self.format_cnpj(cnpj_emitente)

    valorNfe = self.check_none(root.find("./ns:NFe/ns:infNFe/ns:total/ns:ICMSTot/ns:vNF", nsNFe))

    data_importacao = date.today() # obtem a data atual
    data_importacao = data_importacao.strftime('%d/%m/%Y') # Formata a data atual em dd/mm/yyyy

    data_saida = ""  # define data_saida como vazio
    usuario = ''     # define usuario como zavio


    # --- item da nota -----------
    itemNota = 1
    notas = []

    # procura em todos os itens da nota do arquivo XML (pode haver mais de uma nota no arquivo XML)
    for item in root.findall("./ns:NFe/ns:infNFe/ns:det", nsNFe):
      cod = self.check_none(item.find(".ns:prod/ns:cProd", nsNFe))
      qntd = self.check_none(item.find(".ns:prod/ns:qCom", nsNFe))
      descricao = self.check_none(item.find(".ns:prod/ns:xProd", nsNFe))
      unidade_medida = self.check_none(item.find(".ns:prod/ns:uCom", nsNFe))
      valorProd = self.check_none(item.find(".ns:prod/ns:vProd", nsNFe))

      # cria uma lista com os dados do item
      dados = [ 
        NFe, serie, data_emissao, chave, cnpj_emitente, nome_emitente, 
        valorNfe, itemNota, cod, qntd, descricao, unidade_medida, valorProd,
        data_importacao, usuario, data_saida
      ] 
    
      # adiciona os itens da nota na variavel notas
      notas.append(dados)

      # incrementa o contador de itens da nota
      itemNota +=1

    return notas  # retorna a lista notas


  # verifica se não tem valor
  def check_none(self, var):
    if var == None:
      return ""
    else:
      try:
        return var.text.replace('.', ',')
      except: 
        return var.text


  # Formata o CNPJ
  def format_cnpj(self, cnpj):
    try: 
      cnpj = f'{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}'
      return cnpj
      
    except:
      return ""    




if __name__ == "__main__":
  # Especifica um diretorio especifico com arquivos xml a ser lido
  #xml = Read_xml('D:\\CFB-Cursos\\python\\PySide2-Qt-Pycharm\\xmls')

  # Obtém o diretorio atual da aplicacao
  pastaApp=os.path.dirname(__file__)

  # Especifica a pasta _xmls como o subdiretorio onde se localizam os arquivos XML a serem lidos
  xml = Read_xml(pastaApp + "\\notas")

  all = xml.all_files()

  for i in all:
    print("---------------------------------------------------------------------------------")
    result = xml.nfe_data(i) # processa cada arquivo
    print(result)            # imprime o resultado


