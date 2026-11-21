# Chicken Sim! — Sistema de Registro e Transferência de Galinhas

Aplicação web desenvolvida com **Django**, **SQLite** e **Tailwind CSS** para gerenciar o registro de galinhas, propriedades rurais, raças, transferências e certidões.

O sistema possui dois perfis de acesso: **Cartório** e **Produtor**, com funcionalidades específicas para cada tipo de usuário.

## Funcionalidades

### Perfil Cartório

- Painel inicial com indicadores e atalhos para as principais operações.
- Cadastro e gerenciamento de produtores.
- Cadastro e gerenciamento de propriedades vinculadas aos produtores.
- Cadastro de galinhas, com validação para garantir a unicidade do número de registro.
- CRUD completo de raças.
- Análise de solicitações de transferência pendentes:
  - Aprovação com atualização atômica da propriedade responsável pela galinha.
  - Rejeição mediante justificativa obrigatória.
- Consulta ao histórico cronológico de transferências aprovadas.
- Emissão de certidões.

### Perfil Produtor

- Painel com acesso às próprias propriedades, galinhas e solicitações de transferência.
- Solicitação de transferência de galinhas para outra propriedade.
- Consulta ao histórico de transferências.
- Consulta às certidões das galinhas sob sua responsabilidade.

## Tecnologias utilizadas

- **Python 3.11+** — linguagem de programação (testado também com Python 3.13).
- **Django** — framework para desenvolvimento web.
- **SQLite** — banco de dados.
- **Tailwind CSS** — estilização da interface.
- **Gunicorn** — servidor WSGI.
- **WhiteNoise** — gerenciamento de arquivos estáticos em ambientes de publicação.

## Pré-requisitos

Antes de iniciar, certifique-se de ter instalado:

- Python 3.11 ou superior.
- `pip` (gerenciador de pacotes do Python).
- `venv` (módulo para criação de ambientes virtuais, incluído nas instalações padrão do Python).

## Como executar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/BurningVicky/chickenSim.git
cd chickenSim
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv .venv
```

No Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

### 3. Instale as dependências

Com o ambiente virtual ativado, execute:

```bash
pip install -r requirements.txt
```

### 4. Execute as migrações do banco de dados

```bash
python manage.py migrate
```

### 5. Crie o usuário do Cartório (`is_cartorio=True`)

Primeiro, crie um superusuário:

```bash
python manage.py createsuperuser
```

**Importante:** o comando `createsuperuser` não define `is_cartorio=True` automaticamente. Para que a conta tenha acesso ao painel do **Cartório** (`/cartorio/dashboard/`), é necessário ativar esse atributo manualmente.

#### Pelo Django Shell

Abra o shell do Django:

```bash
python manage.py shell
```

Em seguida, execute o código abaixo, substituindo `seu_usuario_cartorio` pelo nome de usuário criado:

```python
from django.contrib.auth import get_user_model

User = get_user_model()
usuario = User.objects.get(username="seu_usuario_cartorio")
usuario.is_cartorio = True
usuario.save()
```

Após salvar a alteração, a conta estará marcada como usuário do Cartório.

### 6. Inicie o servidor de desenvolvimento

```bash
python manage.py runserver
```

Após iniciar o servidor, acesse:

<http://127.0.0.1:8000/>

## Testes e verificações

Para verificar a configuração do projeto:

```bash
python manage.py check
```

Para executar os testes automatizados:

```bash
python manage.py test
```
