from flask import Flask, render_template, request, redirect, flash, session, url_for, jsonify
from database import *
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

load_dotenv()

secret_key = os.getenv("SECRET_KEY")
usuario_adm = os.getenv("USUARIO_ADM")
senha_adm = os.getenv("SENHA_ADM")

app = Flask(__name__)
app.secret_key = secret_key

app.config['UPLOAD_FOLDER_POSTS'] = 'static/uploads'
app.config['UPLOAD_FOLDER_POSTS'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'webm'}
@app.route('/')
def index():
    postagem = listar_postagens()
    return render_template('index.html', postagem = postagem)

@app.route('/novopost', methods=['GET', 'POST'])
def novopost():
    if request.method == 'GET':
        return redirect('/')
    else:
        titulo = request.form.get('titulo', '').strip()
        conteudo = request.form.get('conteudo', '').strip()
        idusuario = session.get('idUsuario') 
        
        if not titulo or not conteudo:
            flash("Preencha todos os campos!")
            return redirect('/')
        
        arquivo = request.files.get('imagem')
        nome_arquivo = None
        tipo_arquivo = 'imagem'
        
        if arquivo and arquivo.filename != '':
            nome_arquivo = secure_filename(arquivo.filename)
            # Verificar se é vídeo pela extensão
            extensao = os.path.splitext(nome_arquivo)[1].lower()
            
            # Lista de extensões de vídeo suportadas
            video_extensoes = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']
            
            if extensao in video_extensoes:
                tipo_arquivo = 'video'
            
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER_POSTS'], nome_arquivo))

        postagem = nova_postagem(titulo, conteudo, idusuario, nome_arquivo, tipo_arquivo)

        if postagem:
            flash("Postagem criada com sucesso!")
        else:
            flash("Erro ao criar nova postagem")
        return redirect('/')

@app.route('/editar-post/<int:idPost>', methods=['GET','POST'])
def editar_post(idPost):
    if 'user' not in session or 'admin' in session:
        return redirect('/')

   
    with conectar() as conexao:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(f"SELECT idUsuario FROM post WHERE idPost = {idPost}")
        autor = cursor.fetchone()
        if not autor or autor['idUsuario'] != session['idUsuario']:
            print("Tentativa de edição de post de outro usuário inválida!")
            return redirect('/')
        

    if request.method == 'GET':
        try:
            with conectar() as conexao:
                cursor = conexao.cursor(dictionary=True)
                cursor.execute(f"SELECT * FROM post WHERE idPost = {idPost}")
                post = cursor.fetchone()
                postagem = listar_postagens()
                return render_template('index.html', postagem = postagem, post=post)

        except mysql.connector.Error as erro:
            print(f"ERRO DE BANCO DE DADOS !: {erro}")
            flash("Houve um erro! Tente novamente mais tarde!")
            return redirect('/')
    if request.method == 'POST':
        titulo = request.form['titulo'].strip()
        conteudo = request.form['conteudo'].strip()

        if not titulo or not conteudo:
            flash("Preencha todos os campos!")
            return redirect(f'/editar-post/{idPost}')
        
        sucesso = atualizar_post (idPost, titulo, conteudo)
        if sucesso:
            flash("Post atualizado com sucesso!")
        else:
            flash("Houve um erro! Tente novamente mais tarde!")
        return redirect('/')    
@app.route('/excluir-post/<int:idPost>')
def excluir_post(idPost):
    if not session:
        print("Tentativa de exclusão de post de outro usuário inválida!")
        return redirect('/')
        
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            if "admin" not in session:
                cursor.execute(f"SELECT * FROM post WHERE idPost = {idPost}")
                autor_post = cursor.fetchone()
                if not autor_post or autor_post['idUsuario'] != session.get('idUsuario'):
                    print("Tentativa de exclusão de post de outro usuário inválida!")
                    return redirect('/')
                cursor.execute(f"DELETE FROM post WHERE idPost = {idPost}")
                conexao.commit()
                flash("Post excluido com sucesso!")
                if 'admin' in session:
                    return redirect('/dashboard')
                else:
                    return redirect('/')

    except mysql.connector.Error as erro:
        print(f"ERRO DE BANCO DE DADOS !: {erro}")
        flash("Houve um erro! Tente novamente mais tarde!")
        return redirect('/')    
    try:
        with conectar() as conexao:
                cursor = conexao.cursor()
                sql = "DELETE FROM post WHERE idPost = %s"
                cursor.execute(sql, (idPost,))
                conexao.commit()
                return redirect('/')
    except mysql.connector.Error as erro:
            print(f"ERRO DE BANCO DE DADOS !: {erro}")
            flash("Houve um erro! Tente novamente mais tarde!")
            return redirect('/')

@app.route('/login', methods =['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        usuario = request.form['user'].lower().strip()
        senha = request.form['senha'].strip()

        if not usuario or not senha :
            flash("Preencha todos os campos!")
            return redirect('/login')

        if usuario == usuario_adm and senha == senha_adm:
            session['admin'] = True
            return redirect('/dashboard')

        resultado, usuario_encontrado = verificar_usuario(usuario, senha)

        if resultado:
            if usuario_encontrado['senha'] == '1234':
                session['idUsuario'] = usuario_encontrado['idUsuario']
                return render_template('novasenha.html')

            session['user'] = usuario_encontrado['user']
            session['idUsuario'] = usuario_encontrado['idUsuario']
            session['foto_de_perfil'] = usuario_encontrado.get('foto') or 'default.png'
            session['nome'] = usuario_encontrado.get('nome') or usuario_encontrado['user']
        
            return redirect('/')
        else:
                flash("Usuario ou senha incorretos!")
                return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if not session or "admin" not in session:
        return redirect('/')

    post = listar_postagens()
    usuarios = listar_usuarios()
    total_posts, total_usuarios = totais()
    return render_template('dashboard.html', post=post, usuarios=usuarios, total_posts=total_posts, total_usuarios=total_usuarios)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/cadastro', methods =['GET','POST'])
def cadastro():
    if request.method == 'GET':
        return render_template('cadastro.html')

    elif request.method == 'POST':
        nome = request.form['nome'].strip()
        usuario = request.form['user'].lower().strip()
        senha = request.form['senha'].strip()   
        if not nome or not usuario or not senha :
            flash('Preencha todos os campos!')
            return redirect('/cadastro')
        senha_hash = generate_password_hash(senha)

        resultado, erro = adicionar_usuario (nome, usuario ,senha_hash)
        if resultado:   
                flash("Usuario cadastrado com sucesso!")
                return redirect ('/login')
        else:
            if erro.errno == 1062:
                flash("Esse user já existe! Tente outro.")
            else:
                flash("Erro ao cadastrar usuario!")
            return redirect('/cadastro')

@app.route('/usuario/excluir/<int:idUsuario>')
def excluir_usuario(idUsuario):
    if 'admin' not in session:
        return redirect('/')

        sucesso = deletar_usuario(idUsuario)

    if sucesso:
        flash("Usuario excluido com sucesso!")
    else:
        flash("Erro ao excluir usuario!")
    redirect('/dashboard')


@app.route('/usuario/status/<int:idUsuario>')
def status_usuario(idUsuario):
    if not session:
        return redirect('/')

    sucesso = alterar_status(idUsuario)

    if sucesso:
        flash("Status alterado com sucesso!")
    else:
        flash("Erro ao alterar status!")

    return redirect('/dashboard')

@app.route('/inicio')

@app.errorhandler(404)
def pagina_nao_encontrada(error):
    return render_template('erro404.html')

@app.route('/perfil')
def perfil():
    if "user" not in session and "admin" not in session:
        return redirect('/login')

    return render_template('user.html')
     
@app.route('/usuario/reset/<int:idUsuario>')
def reset(idUsuario):
    if 'admin' not in session:
        return redirect('/')

    sucesso = resetar_senha(idUsuario)
    if sucesso:
        flash("Senha resetada com sucesso!")
    else:
        flash("Erro ao resetar senha!")
    return redirect('/dashboard')

@app.route('/atualizar-foto', methods=['POST'])
def atualizar_foto():

    if "user" not in session and "admin" not in session:
        return redirect('/login')
    
    if 'foto' not in request.files:
        flash('Nenhum arquivo selecionado!')
        return redirect('/perfil')
    
    foto = request.files['foto']
    
    if foto.filename == '':
        flash('Nenhum arquivo selecionado!')
        return redirect('/perfil')
    
    if foto:
        try:
            # Obter a foto atual do usuário para excluir depois
            with conectar() as conexao:
                cursor = conexao.cursor(dictionary=True)
                cursor.execute("SELECT foto FROM usuario WHERE idUsuario = %s", (session['idUsuario'],))
                usuario = cursor.fetchone()
                foto_antiga = usuario['foto'] if usuario and usuario['foto'] else None
            
            # Gerar nome único para o arquivo
            extensao = os.path.splitext(foto.filename)[1]
            nome_arquivo = f"perfil_{session['idUsuario']}_{int(datetime.now().timestamp())}{extensao}"
            nome_arquivo = secure_filename(nome_arquivo)
            
            caminho_foto = os.path.join(app.config['UPLOAD_FOLDER_POSTS'], nome_arquivo)
            foto.save(caminho_foto)
            
            # Atualizar no banco de dados
            sucesso = atualizar_foto_perfil(session['idUsuario'], nome_arquivo)
            
            if sucesso:
                # Excluir foto antiga se não for a default e se existir
                if foto_antiga and foto_antiga != 'default.png':
                    caminho_foto_antiga = os.path.join(app.config['UPLOAD_FOLDER_POSTS'], foto_antiga)
                    if os.path.exists(caminho_foto_antiga):
                        os.remove(caminho_foto_antiga)
                
                # Atualizar na session
                session['foto_de_perfil'] = nome_arquivo
                flash('Foto de perfil atualizada com sucesso!')
            else:
                flash('Erro ao atualizar foto de perfil!')
                
        except Exception as e:
            print(f"Erro ao processar upload: {e}")
            flash('Erro ao processar a foto!')
    
    return redirect('/perfil')

@app.route('/usuario/novasenha', methods=['POST', 'GET'])
def novasenha():
    if "idUsuario" not in session:
        return redirect('/')

    if request.method == 'GET':
        return render_template('novasenha.html')
    
    if request.method == 'POST':
        senha = request.form['senha'].strip()
        confirmacao = request.form['confirmacao'].strip()

    
        if not senha or not confirmacao:
            flash('Preencha todos os campos!')
            return render_template('novasenha.html')
        if senha != confirmacao:
            flash('As senhas não coincidem!')
            return render_template('novasenha.html')
        if senha == '1234':
            flash('A nova senha não pode ser igual à senha padrão!')
            return render_template('novasenha.html')
        
        senha_hash = generate_password_hash(senha)
        idUsuario = session['idUsuario']
        sucesso = alterar_senha(senha_hash, idUsuario)
        if sucesso:
            flash('Senha alterada com sucesso!')
            if 'user' in session:
                return redirect('/perfil')
    
            return redirect('/login')
        else:
            flash('Erro ao alterar a senha!')
            return render_template('novasenha.html')

if __name__ == "__main__":
    app.run(debug=True)