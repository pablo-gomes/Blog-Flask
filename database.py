import mysql.connector
from werkzeug.security import check_password_hash

def conectar():
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="senai",
        database="blog"
    )
    if conexao.is_connected():
        print("Conectado ao banco de dados MySQL")

    return conexao

def listar_postagens():
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("SELECT p.*, u.user, u.foto, u.nome FROM post p  INNER JOIN usuario u ON u.idUsuario = p.IdUsuario where u.ativo = 1 ORDER BY idPost DESC")
            return cursor.fetchall()
    except mysql.connector.Error as erro:
        print(f"ERRO DE BANCO DE DADOS !: {erro}")
        return []

def nova_postagem(titulo, conteudo, idusuario, arquivo, tipo_arquivo='imagem'):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            if tipo_arquivo == 'video':
                sql = "INSERT INTO post (titulo, conteudo, idusuario, video, tipo_arquivo) VALUES (%s, %s, %s, %s, %s)"
            else:
                sql = "INSERT INTO post (titulo, conteudo, idusuario, imagem, tipo_arquivo) VALUES (%s, %s, %s, %s, %s)"
            
            cursor.execute(sql, (titulo, conteudo, idusuario, arquivo, tipo_arquivo))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BANCO DE DADOS !: {erro}")
        return False

def listar_usuarios():
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuario")
            return cursor.fetchall()
    except mysql.connector.Error as erro:
        print(f"ERRO DE BANCO DE DADOS !: {erro}")
        return []
    

def adicionar_usuario(nome,user,senha_hash):
        try:
            with conectar() as conexao:
                cursor = conexao.cursor()
                sql = "INSERT INTO usuario (nome, user, senha) VALUES (%s, %s, %s)"
                cursor.execute(sql, (nome, user, senha_hash))
                conexao.commit()
                return True, "OK"
        except mysql.connector.Error as erro:
            print(f"ERRO DE BANCO DE DADOS !: {erro}")
            return False, erro

def verificar_usuario(usuario, senha):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "SELECT idUsuario, user, senha, nome, foto FROM usuario WHERE user = %s;"
            cursor.execute(sql, (usuario,))
            usuario_encontrado = cursor.fetchone()
            
            if usuario_encontrado:
                if usuario_encontrado['senha'] == '1234' and senha == '1234':
                    return True, usuario_encontrado

                if check_password_hash(usuario_encontrado['senha'], senha):
                    print(usuario_encontrado['nome'])
                    return True, usuario_encontrado
            return False, None
    except mysql.connector.Error as erro:
            print(f"ERRO DE BANCO DE DADOS !: {erro}")
            return False, erro
def alterar_status(idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "SELECT ativo FROM usuario WHERE idUsuario = %s"
            cursor.execute(sql, (idUsuario,))
            status = cursor.fetchone()
           
           
            if status['ativo']:
                sql = "UPDATE usuario SET ativo = 0 WHERE idUsuario = %s"
            else:
                sql = "UPDATE usuario SET ativo = 1 WHERE idUsuario = %s"
            
            cursor.execute(sql, (idUsuario,))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BANCO DE DADOS !: {erro}")
        return False
def deletar_usuario(idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "DELETE FROM usuario WHERE idUsuario = %s"
            cursor.execute(sql, (idUsuario,))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BANCO DE DADOS !: {erro}")
        return False

def atualizar_post(titulo, conteudo, idPost):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "UPDATE post SET titulo = %s, conteudo = %s WHERE idPost = %s"
            cursor.execute(sql, (titulo, conteudo, idPost))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BANCO DE DADOS !: {erro}")
        return False
def totais():
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM vw_total_posts")
            total_posts = cursor.fetchone()
            cursor.execute("SELECT * FROM vw_usuarios")
            total_usuarios = cursor.fetchone()
            return total_posts, total_usuarios
    except mysql.connector.Error as erro:
        print(f"ERRO DE BANCO DE DADOS !: {erro}")
        return None, None

def resetar_senha(idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "UPDATE usuario SET senha = '1234' WHERE idUsuario = %s"
            cursor.execute(sql, (idUsuario,))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BANCO DE DADOS !: {erro}")
        return False


def atualizar_foto_perfil(idUsuario, nome_foto):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "UPDATE usuario SET foto = %s WHERE idUsuario = %s"
            cursor.execute(sql, (nome_foto, idUsuario))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        print(f"Erro ao atualizar foto de perfil: {erro}")
        conexao.rollback()
        return False

def alterar_senha(idUsuario, senha_hash):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "UPDATE usuario SET senha = %s WHERE idUsuario = %s"
            cursor.execute(sql, (idUsuario,senha_hash))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE BANCO DE DADOS !: {erro}")
        return False
    app.run(debug=True)
