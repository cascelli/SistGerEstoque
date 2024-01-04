from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtSql import QSqlDatabase, QSqlTableModel
from PySide2.QtWidgets import (
  QApplication, 
  QMainWindow, 
  QWidget, 
  QMessageBox, 
  QFileDialog,
  QTreeWidgetItem
)

from ui_login import Ui_Login        # arquivo da janela de login
from ui_main import Ui_MainWindow    # arquivo da janela principal
from database import DataBase        # arquivo para comunicar com banco de dados
from xml_files import Read_xml       # arquivo para realizar leitura/parser de arquivos XML 
from os import access
from datetime import date            # data
import sys                           # acesso a rotinas do sistema operacional
import os                            # acesso a rotinas do sitema operacional
import sqlite3                       # banco de dados SQLITE3
import pandas as pd                  # preenchimento de tabelas, XML
import re                            # Expressoes regulares
import matplotlib.pyplot as plt      # lib de plotagem

# --- 
# Para gerar o executável : 
#  - Instalar a lib pyinstaller
#     pip install pyinstaller
#  - Criar um icone para a aplicação e colocar na pasta raiz do projeto (icone.ico) 
#  - Executar o comando :
#     pyinstaller.exe --onefile --windowed --icon=icone.ico main.py
#
# ---

# Converter arquivo login.ui para ui_login.py :
# pyside2-uic login.ui -o ui_login.py
class Login(QWidget, Ui_Login):

  def __init__(self) -> None:

    super(Login, self).__init__() # Inicia elementos da super classe QWidget

    self.tentativas = 0
    self.setupUi(self)
    self.setWindowTitle("Login do sistema")

    #appIcon = QIcon('_imgs/icone.ico') # Define o icone da aplicação
    appIcon = QIcon('_imgs/logo.PNG')   # Define o icone da aplicação
    self.setWindowIcon(appIcon)         # ativa o icone


    # Conecta ao sinal de clique de botão btn_login
    # self.btn_login.clicked.connect(self.open_system) # Chama metodo open_system ao clicar o botao de btn_login
    self.btn_login.clicked.connect(self.checkLogin) # Chama metodo checkLogin ao clicar o botao de btn_login

  # Teste inicial de validação - Removido e substituido pelo método checkLogin()
  # def open_system(self):
  #   if self.txt_password.text() == '123': # Texta se o password é 123
  #     self.w = MainWindow()               # Abre a tela MainWindow
  #     self.w.show()                       # Mostra MainWindow
  #     self.close()                        # Fecha a tela de login
  #   else:
  #     print('Senha inválida !')

  def checkLogin(self):
    self.users = DataBase() # Instancia a classe DataBase
    self.users.conecta()    # Conecta na tabela users

    # Verifica se o usuario existe e se passou senha correta
    autenticado = self.users.check_user(
      # self.txt_user.text().upper(), 
      self.txt_user.text(), 
      self.txt_password.text()
    ) 

    print ("User : " , self.txt_user.text().upper())
    print ("Password : " , self.txt_password.text())
    print("Autenticado : ", autenticado)

    if autenticado.lower() == "adm" or autenticado.lower() == "usr" :
      self.w = MainWindow(self.txt_user.text(), autenticado.lower())    # Abre a tela MainWindow passando o parametro autenticado
      self.w.show()                       # Mostra MainWindow
      self.close()                        # Fecha a tela de login
    else:
      if self.tentativas < 3 :
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Erro ao acessar")
        msg.setText(f"Login ou senha incorreto\n\nTentativa : {self.tentativas + 1} de 3")
        msg.exec_()
        self.tentativas += 1

      if self.tentativas == 3 :
        # ToDo : Implementar código para bloquaer usuario
        self.users.close_connection()
        sys.exit(0) # Encerra o sistema


# Converter arquivo ui_main.ui para ui_main.py :
# pyside2-uic ui_main.ui -o ui_main.py
class MainWindow(QMainWindow, Ui_MainWindow):

  def __init__(self, username, user) -> None:

    super(MainWindow, self).__init__() # Inicia os elementos da super classe QMainWindow
    self.setupUi(self)
    self.setWindowTitle("Sistema de gerenciamento")

    #appIcon = QIcon('_imgs/icone.ico') # Define o icone da aplicação
    appIcon = QIcon('_imgs/logo.PNG')   # Define o icone da aplicação
    self.setWindowIcon(appIcon)         # ativa o icone

    #self.user = user
    self.user = username

    # Testa se o usuario é administrador ou não
    if user.lower() == "usr" :
      self.btn_pg_cadastro.setVisible(False)

    # --- Páginas do sistema -----------
    # Usando funcao lambda para selecionar a pagina especifica do componente paginator
    self.btn_home.clicked.connect(lambda:self.Pages.setCurrentWidget(self.pg_home))
    self.btn_tables.clicked.connect(lambda:self.Pages.setCurrentWidget(self.pg_table))
    self.btn_contato.clicked.connect(lambda:self.Pages.setCurrentWidget(self.pg_contato))
    self.btn_sobre.clicked.connect(lambda:self.Pages.setCurrentWidget(self.pg_sobre))
    self.btn_pg_cadastro.clicked.connect(lambda:self.Pages.setCurrentWidget(self.pg_cadastro))
    self.btn_pg_import.clicked.connect(lambda:self.Pages.setCurrentWidget(self.pg_import))

    self.btn_cadastrar.clicked.connect(self.subscribe_user)

    # Arquivo XML
    self.btn_open_2.clicked.connect(self.open_path)
    self.btn_import.clicked.connect(self.import_xml_files)

    # Filtro de notas
    self.txt_filtro.textChanged.connect(self.update_filter)

    # Gerar saída e estorno
    self.btn_gerar.clicked.connect(self.gerar_saida)
    self.btn_estorno.clicked.connect(self.gerar_estorno)

    # Gera planilha do excel
    self.btn_excel.clicked.connect(self.excel_file)

    # Gera grafico do estoque
    self.btn_chart.clicked.connect(self.graphic)

    # abre tabela de estoque
    #self.table_estoque()
    # Abre tabelas
    self.reset_tables()

  def subscribe_user(self):

    # Verifica se as senhas foram digitadas iguais nos dois campos
    if self.txt_senha.text() != self.txt_senha_2.text():
      msg = QMessageBox()
      msg.setIcon(QMessageBox.Warning)
      msg.setWindowTitle("Senhas divergentes")
      msg.setText("As senhas informadas não conferem !\n\nCertifique-se que eleas sejam iguais.")
      msg.exec_()
      return None

    # Obtém os valores dos campos do novo registro a ser inserido no BD
    nome = self.txt_nome.text()
    user = self.txt_usuario.text()
    password = self.txt_senha.text()
    access = self.cb_perfil.currentText()

    # Insere registro no Banco de dados
    db = DataBase() # inicia conexão 
    db.conecta()    # Conecta ao database
    db.insert_user(nome, user, password, access)  # Insere o novo registro 
    db.close_connection() # fecha conexão

    # Envia mensagem de cadastro realizado
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Cadastro de usuário")
    msg.setText("Cadastro de usuário realizado com sucesso !")
    msg.exec_()

    # Limpa as variáveis dos campos do cadastro
    self.txt_nome.setText("")
    self.txt_usuario.setText("")
    self.txt_senha.setText("")
    self.txt_senha2.setText("")
    self.cb_perfil.setCurrentText("Usuário")

  def open_path(self):

    # -- Para linux ---
    # self.path = QFileDialog.getExistingDirectory(
    #   self, 
    #   str("Open Directory"),
    #   "/home",
    #   QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
    # )

    # -- Para Windows ---
    # Obtém o diretorio atual da aplicacao
    pastaApp=os.path.dirname(__file__)

    self.path = QFileDialog.getExistingDirectory(
      self, 
      str("Open Directory"),
      pastaApp,
      QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
    )

    self.txt_file.setText(self.path) # recebe o diretorio escolhido no QFileDialog

  def import_xml_files(self):

    xml = Read_xml(self.txt_file.text()) # le o xml do diretorio

    all = xml.all_files() # lê todos os arquivos xml do diretorio escolhido

    # Prepara a progressBar 
    # Ajusta o valor maximo para a quantidade de arquivos xml do diretorio
    self.progressBar.setMaximum(len(all))

    db = DataBase()
    db.conecta()

    cont = 1

    for i in all:
      self.progressBar.setValue(cont)
      fullDataSet = xml.nfe_data(i)
      db.insert_data(fullDataSet)
      cont += 1

    # Atualizar a tabela 


    msg = QMessageBox() 
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("Importação XML")
    msg.setText("Importação concluída !")
    msg.exec_()

    self.progressBar.setValue(0)

      

    db.close_connection()

  def table_estoque(self):
    # Altera o estilo da tabela
    #self.tw_estoque.setStyleSheet("color: #fff; font-size: 15px;")
    # Altera o estilo do cabeçalho
    #self.tw_estoque.setStyleSheet(u" QHeaderView{color: black};")
    # Juntando tudo numa instrucao só
    self.tw_estoque.setStyleSheet(u" QHeaderView{color: black; background-color: lightgray}; color: #fff; font-size: 10px; background-color: darkgreen;")


    # pip install pandas para alimentar tabelas
    # importar pandas e sqlite3

    # cria uma conexão ao banco de dados system.db do sqlite3
    cn = sqlite3.connect('system.db')

    # faz uma query ao banco de dados usando o pandas
    # obtem todas as notasque estao no estoque que não foram baixadas (data_saida = '')
    result = pd.read_sql_query("select * from notas where data_saida = ''", cn)

    # transforma o resultado em values em uma lista de dados para alimentar a tabela
    result = result.values.tolist()

    self.x = ""

    # cria um niveis na tabela para itens de uma mesma nota
    for i in result:
      # Faz o check para identificar a mesma nota e adicionar um nível

      # testa se o numero da nota fiscal (elemento i[0] da lista) é igual ao armazenado em self.x
      if i[0] == self.x :
        QTreeWidgetItem(self.campo, i)
      else:
        # adiciona o item a tabela
        self.campo = QTreeWidgetItem(self.tw_estoque, i)
        # adiciona um checkBox dentro da tabela, primeiro campo (0) 
        self.campo.setCheckState(0, QtCore.Qt.CheckState.Unchecked)  

      # atualiza self.x
      self.x = i[0]

    # ordena as notas
    self.tw_estoque.setSortingEnabled(True)

    # ajusta o tamanho das colunas de 1 a 15 de acordo com o seu conteúdo
    for i in range(1,15):
      self.tw_estoque.resizeColumnToContents(i)

  def table_saida(self):
    # Altera o estilo da tabela
    self.tw_saida.setStyleSheet(u" QHeaderView{color: black; background-color: lightgray}; color: #fff; font-size: 10px; background-color: darkgreen;")

    # cria uma conexão ao banco de dados system.db do sqlite3
    cn = sqlite3.connect('system.db')

    # faz uma query ao banco de dados usando o pandas
    # obtem todas as notasque estao no estoque que não foram baixadas (data_saida = '')
    result = pd.read_sql_query(
      """
        select NFe, serie, data_importacao, data_saida, usuario
         from notas where data_saida != ''
      """, 
      cn
    )

    # transforma o resultado em values em uma lista de dados para alimentar a tabela
    result = result.values.tolist()

    self.x = ""

    # cria um niveis na tabela para itens de uma mesma nota
    for i in result:
      # Faz o check para identificar a mesma nota e adicionar um nível

      # testa se o numero da nota fiscal (elemento i[0] da lista) é igual ao armazenado em self.x
      if i[0] == self.x :
        QTreeWidgetItem(self.campo, i)
      else:
        # adiciona o item a tabela
        self.campo = QTreeWidgetItem(self.tw_saida, i)
        # adiciona um checkBox dentro da tabela, primeiro campo (0) 
        self.campo.setCheckState(0, QtCore.Qt.CheckState.Unchecked)  

      # atualiza self.x
      self.x = i[0]

    # ordena as notas
    self.tw_saida.setSortingEnabled(True)

    # ajusta o tamanho das colunas de 1 a 15 de acordo com o seu conteúdo
    # ajusta o tamanho das colunas de 1 a 5 de acordo com o seu conteúdo
    #for i in range(1,15):
    for i in range(1,5):
      self.tw_saida.resizeColumnToContents(i)

  def table_geral(self):
    # - ALIMENTA TABELA DIRETO DO SQLITE ---
    # Altera o estilo da tabela
    self.tb_geral.setStyleSheet(u" QHeaderView{color: black; background-color: lightgray}; color: #fff; font-size: 10px; background-color: darkgreen;")

    # conecta ao database usando QSqlDatabase
    db = QSqlDatabase("QSQLITE")
    db.setDatabaseName("system.db")
    db.open()

    # cria modelo para tabela
    self.model = QSqlTableModel(db=db)
    self.tb_geral.setModel(self.model)
    self.model.setTable("notas")
    self.model.select()

  def reset_tables(self):
    # limpa o conteúdo das tabelas
    self.tw_estoque.clear()
    self.tw_saida.clear()

    # chama os metodos de preenchimento das tabelas
    self.table_saida()
    self.table_estoque()
    self.table_geral()

  def update_filter(self, s):
    # Expressao regular
    s = re.sub("[\W_]+", "", s)
    filter_str = 'Nfe like "%{}%"'.format(s)  # filtrando o campo Nfe
    self.model.setFilter(filter_str)

  def gerar_saida(self):
    self.checked_itens_out = []

    # Funcao recursiva que percorre a tabela e ve os itens que estão marcados e armazena em uma lista
    def recurse(parent_item):
      for i in range(parent_item.childCount()):
        child = parent_item.child(i)
        grand_children = child.childCount()
        if grand_children > 0 :
          recurse(child)
        if child.checkState(0) == QtCore.Qt.Checked:
          self.checked_itens_out.append(child.text(0))

    recurse(self.tw_estoque.invisibleRootItem()) # chama funcao recursiva 

    # Pergunta se o usuario realmente deseja fazer isso
    self.question("saida")

  def gerar_estorno(self):
    self.checked_itens = []

    # Funcao recursiva que percorre a tabela e ve os itens que estão marcados e armazena em uma lista
    def recurse(parent_item):
      for i in range(parent_item.childCount()):
        child = parent_item.child(i)
        grand_children = child.childCount()
        if grand_children > 0 :
          recurse(child)
        if child.checkState(0) == QtCore.Qt.Checked:
          self.checked_itens.append(child.text(0))

    recurse(self.tw_saida.invisibleRootItem()) # chama funcao recursiva 

    # Pergunta se o usuario realmente deseja fazer isso
    self.question("estorno")

  def question(self, table):

    msgBox = QMessageBox()

    if table == 'estorno':
      msgBox.setText("Deseja estornar as notas selecionadas ?")
      msgBox.setInformativeText("As selecionadas voltarão para o estoque.\nClique em 'yes' para continuar ou 'no' para cancelar")
      msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
      msgBox.setDetailedText(f"Notas : {self.checked_itens}")
    elif table == 'saida':
      msgBox.setText("Deseja gerar saída das notas selecionadas ?")
      msgBox.setInformativeText("As selecionadas serão baixadas do estoque.\nClique em 'yes' para continuar ou 'no' para cancelar")
      msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
      msgBox.setDetailedText(f"Notas : {self.checked_itens_out}")
    
    msgBox.setIcon(QMessageBox.Question)
    ret = msgBox.exec_()

    if ret == QMessageBox.Yes:
      if table == 'estorno':
        self.db = DataBase()
        self.db.conecta()
        self.db.update_estorno(self.checked_itens)
        self.db.close_connection()
        self.reset_tables()
      elif table == 'saida':
        data_saida = date.today()
        data_saida = data_saida.strftime('%d/%m/%Y')
        self.db = DataBase()
        self.db.conecta()
        self.db.update_estoque(data_saida, self.user, self.checked_itens_out)
        self.db.close_connection()
        self.reset_tables()

  def excel_file(self):

    # instalar dependencia do openpyxl
    # pip install openpyxl

    # gera planilha excel com as notas do bd
    cnx = sqlite3.connect('system.db')                                       # Conecta ao bd
    result = pd.read_sql_query("select * from notas", cnx)                   # seleciona os registros do bd
    result.to_excel("Resumo de notas.xlsx", sheet_name='notas', index=False) # salva para arquivo do excel

    # Mensagem
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setWindowTitle("Relatório de notas")
    msgBox.setText("Relatório gerado com sucesso")
    msgBox.exec_()

  def graphic(self):

    # lib grafica - instalacao : 
    # pip install matplotlib

    cnx = sqlite3.connect("system.db")
    estoque = pd.read_sql_query("select * from notas", cnx)
    saida = pd.read_sql_query("select * from notas where data_saida != '' ", cnx)

    estoque = len(estoque) # determina o tamanho do estoque
    saida = len(saida)     # determina o tamanho de saida

    labels = "Estoque", "Saídas"
    sizes = [estoque, saida]
    fig1, axl = plt.subplots()
    axl.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    axl.axis("equal")

    plt.show()




if __name__ == "__main__" :
  app = QApplication(sys.argv)
  window = Login()  # instancia o objewto da classe Login
  window.show()     # mostra o objeto (janela)
  app.exec_()         # Executa a aplicacao
  