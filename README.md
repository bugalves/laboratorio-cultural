# Laboratório Cultural - Backend (Django)

## 📌 Requisitos

Antes de iniciar, garantir que tens instalado:

* Python 3.10+
* Docker e Docker Compose
* Git

---

## 🚀 Setup do Projeto

### 1. Clonar o repositório

```bash
git clone <repo-url>
cd <nome-do-projeto>
```

---

### 2. Criar ambiente virtual

```bash
python -m venv venv
```

Ativar:

**Windows**

```bash
source /w/laboratorio-cultural/venv/Scripts/activate
source /(disk_id)/(path_to_project_dir)/venv/Scripts/activate
```

---

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## 🐳 Base de Dados (MySQL via Docker)

### 1. Subir o container

```bash
docker-compose up -d
```

Isto irá criar um container com:

* Nome: `laboratoriocultural_db`
* Base de dados: `laboratoriocultural_db`
* Porta: `3306`

---

### 2. Verificar se está a correr

```bash
docker ps
```

---

## ⚙️ Variáveis de Ambiente

Duplicar o ficheiro .env.example e trocar o nome para .env e preencher com as credenciais definidas no docker-compose.yml

```env
DATABASE_NAME=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_HOST=
DATABASE_PORT=
```

---

## 🧱 Migrações

Aplicar as migrações iniciais:

```bash
python manage.py migrate
```

## ▶️ Executar o servidor

```bash
python manage.py runserver
```

Aceder em:

```
http://127.0.0.1:8000/
```

---

## 🔄 Workflow de Desenvolvimento

### 1. Atualização ou criação de entidades

Sempre que existirem alterações nos modelos devem rodar o seguinte comando:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Instalação de novas dependências

Sempre que for necessário instalarem novas dependências devem rodar o seguinte comando:

```bash
pip freeze > requirements.txt
```

Como o Django não tem um gestor de pacotes que registe as dependências em uso nativamente, tem de ser feito manualmente.

---

## ⚠️ Notas Importantes

* Nunca enviar para o github:

  * `.env`
  * `venv/`
  * `db.sqlite3`

* Garantir que o Docker está a correr antes de iniciar o projeto

---

## 🧠 Estrutura do Projeto

* `config/` → configuração principal do Django
* `apps/` → aplicações do projeto
* `docker-compose.yml` → configuração da base de dados

---

## ✅ Estado esperado

Após setup completo:

* Django a correr localmente ✔
* MySQL ativo via Docker ✔
* Migrações aplicadas ✔

---

## 📌 Problemas comuns

### Erro na virtualização do container no Docker

* Confirmar que a virtualização da máquina está ativada (ativar na BIOS)

### Erro de ligação à base de dados

* Confirmar que o Docker está ativo
* Confirmar credenciais no `.env`

### Porta 3306 ocupada

* Verificar outros serviços MySQL locais ou alterar a porta deste serviço

---

## 👥 Nota

Cada membro do grupo deve correr o Docker localmente.
A base de dados **não é partilhada**, apenas a estrutura (via migrações).
