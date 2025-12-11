DROP DATABASE IF EXISTS blog;

CREATE DATABASE blog;

USE blog;

CREATE TABLE usuario (
    idUsuario INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL,
    user VARCHAR(15) NOT NULL,
    senha VARCHAR(255) NOT NULL,
    foto VARCHAR(255),
    dataCadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ativo BOOLEAN NOT NULL DEFAULT 1
);

CREATE TABLE post(
    idPost INT PRIMARY KEY AUTO_INCREMENT,
    titulo VARCHAR(50) NOT NULL,
    conteudo TEXT NOT NULL,
    datapost TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    idUsuario INT,
    FOREIGN KEY (idUsuario) REFERENCES usuario(idUsuario)
    ON delete cascade
    ALTER TABLE post ADD COLUMN imagem VARCHAR(255) NULL;
);
CREATE TABLE comentario (
    idComentario INT PRIMARY KEY AUTO_INCREMENT,
    idPost INT NOT NULL,
    idUsuario INT NOT NULL,
    comentario TEXT NOT NULL,
    dataComentario DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idPost) REFERENCES post(idPost),
    FOREIGN KEY (idUsuario) REFERENCES usuario(idUsuario)
);


CREATE VIEW vw_total_posts AS
SELECT
    COUNT(*) AS total_posts
FROM post p
JOIN usuario u ON p.idUsuario = u.idUsuario
WHERE
    u.ativo = 1;

CREATE VIEW vw_usuarios AS
SELECT
    COUNT(*) AS total_usuarios
FROM usuario
WHERE
    ativo = 1;


ALTER TABLE usuario
ADD ativo BOOLEAN NOT NULL DEFAULT 1;
-- truncate post
-- delete from post where idpost = 1;

UPDATE usuario
SET foto = 'foto_de_perfil.jpg'
WHERE idUsuario = 1;



SELECT idUsuario, user, senha, ativo, nome FROM usuario WHERE user = %s

ALTER TABLE usuario ADD COLUMN foto_perfil VARCHAR(255) DEFAULT '/static/img/foto de perfil.jpg';