import sqlite3

class DataBase():
  def __init__(self, name = "system.db") -> None:  # Cria um banco de dados de nome system.db (definico como default) no SQLite3
    self.name = name

  def conecta(self):
    self.connection = sqlite3.connect(self.name)

  def close_connection(self):  
    try:
      self.connection.close()
    except:
      pass

  def create_table_users(self):
    try:
      cursor = self.connection.cursor()
      cursor.execute("""
        create table if not exists users(
          id integer not null primary key autoincrement,
          name text not null,
          user text unique not null,
          password text not null,
          access text not null
        );
      """)
    except AttributeError:
      print("Faça a conexão")    

  def insert_user(self, name, user, password, access):
    try:
      cursor = self.connection.cursor()
      cursor.execute("""
        insert into users(name, user, password, access) values(?,?,?,?)
      """, (name, user, password, access) )
      self.connection.commit()
    except AttributeError:
      print("Faça a conexão")

  def check_user(self, user, password):

    #print("Entrei em check_user()") # debug
    try:
      cursor = self.connection.cursor()
      # Obs : Poderia ter usado a cláusula where no SQL para filtrar os registros
      #       de uma vez ao invés de fazer um loop por todos os registros testá-los um a um
      cursor.execute("""
        select * from users
      """)

      #print("Executei 'select * from users'") # debug

      #for linha in cursor.fetchall:
      for linha in cursor.fetchall():
        #print("users loop...") # debug
        # Mostrando os campos da tabela
        #print(f"linha[0] = {linha[0]}, linha[1] = {linha[1]}, linha[2] = {linha[2]}, linha[3] = {linha[3]}, linha[4] = {linha[4]}")
        if linha[2].upper() == user.upper() and linha[3] == password and linha[4] == "Administrador":
          return "adm"
          #break  # encerra o loop ao encontrar o usuario na lista
        elif linha[2].upper() == user.upper() and linha[3] == password and linha[4] == "Usuário": 
          return "usr"
          #break  # encerra o loop ao encontrar o usuario na lista
        else:
          continue # Continua no loop for
      return "sem acesso"
    except:
      pass  

  def insert_data(self, full_dataset):
    cursor = self.connection.cursor()
    campos_tabela = (
        'NFe', 'serie', 'data_emissao', 'chave', 'cnpj_emitente', 'nome_emitente', 
        'valorNfe', 'itemNota', 'cod', 'qntd', 'descricao', 'unidade_medida', 'valorProd',
        'data_importacao', 'usuario', 'data_saida'
    )

    qntd = ','.join(map(str, '?'*16))  # é o mesmo que fazer qntd = '?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?'
    query = f""" insert into notas {campos_tabela} values ({qntd})"""

    try:
      for nota in full_dataset:
        cursor.execute(query, tuple(nota))
        self.connection.commit()
    except sqlite3.IntegrityError:
      print('Nota já existe no banco !')

  def create_table_nfe(self):
    try:
      cursor = self.connection.cursor()
      cursor.execute(f"""
        create table if not exists notas(
          NFe text,
          serie text,
          data_emissao text,
          chave text,
          cnpj_emitente text,
          nome_emitente text,
          valorNfe text,
          itemNota text,
          cod text,
          qntd text,
          descricao text,
          unidade_medida text,
          valorProd text,
          data_importacao text,
          usuario text,
          data_saida text,

          primary key (chave, NFe, itemNota)
        );
      """)
    except AttributeError:
      print("Faça a conexão")    

  def update_estoque(self, data_saida, user, notas):
    try:
      cursor = self.connection.cursor()
      for nota in notas:
        cursor.execute(f"""
          update notas set 
          data_saida = '{data_saida}', 
          usuario = '{user}'
          where Nfe = '{nota}'
        """)
        self.connection.commit()
    except AttributeError:
      print("Faça a conexão para alterar campos")


  def update_estorno(self, notas):
    try:
      cursor = self.connection.cursor()
      for nota in notas:
        cursor.execute(f"""
          update notas set 
          data_saida = '', 
          usuario = ''
          where Nfe = '{nota}'
        """)
        self.connection.commit()
    except AttributeError:
      print("Faça a conexão para alterar campos")


# Rotina principal
if __name__ == "__main__":

  db = DataBase()
  db.conecta()
  db.create_table_users()
  db.create_table_nfe()
  db.close_connection()

