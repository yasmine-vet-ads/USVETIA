# Us.Vet IA

Projeto acadêmico, experimental e demonstrativo para análise multimodal assistida de imagens ultrassonográficas veterinárias com API generativa.

## Escopo desta etapa

Esta versão cria a estrutura inicial do banco de dados interno do sistema em SQLite. Não há interface, chamada a APIs externas durante a configuração local, ingestão de imagens reais ou resultados de análise neste repositório.

A amostra planejada do estudo é retrospectiva e composta por 115 exames ultrassonográficos veterinários:

- 15 exames piloto para testes iniciais;
- 100 exames principais para processamento e avaliação descritiva.

## Estrutura

```text
data/
  input/      # reservado para arquivos locais não versionados
  db/         # reservado para bancos SQLite locais não versionados
  exemplos/  # reservado para exemplos anonimizados ou sintéticos futuros
docs/         # documentação do projeto
src/          # utilitários Python do banco de dados
sql/          # schema SQL
tests/        # testes automatizados
```

## Regras de privacidade e segurança

- Não inserir dados clínicos reais neste repositório.
- Não inserir imagens reais neste repositório.
- Não inserir nomes de tutores, pacientes, clínicas ou profissionais.
- Não criar resultados fictícios de análise.
- Não chamar API externa nesta etapa de estruturação local.
- Não criar interface Streamlit nesta etapa.

## Banco de Dados - Versão Acadêmica Interna

O banco usado nesta fase é **SQLite**. O arquivo local será criado em:

```text
data/db/usvet_ia.db
```

Esse arquivo representa um banco local de trabalho e **não deve ser enviado ao GitHub**. Bancos preenchidos, imagens reais e planilhas com dados reais também não devem ser versionados, pois podem conter informações sensíveis e exigem anonimização e controle de privacidade.

O Us.Vet IA é um projeto **acadêmico, experimental e assistivo**. O sistema não emite diagnóstico autônomo, não substitui a avaliação clínica e não promete validação diagnóstica. Qualquer saída futura de IA deve ser tratada como sugestão estruturada revisável, com **revisão obrigatória por médico-veterinário**.

### Comandos principais

```bash
pip install -r requirements.txt
python src/database.py
python src/importar_planilha.py
python src/seed_prompts.py
pytest
```

### Tabelas do banco

| Tabela | Função |
| --- | --- |
| `exames` | Armazena metadados anonimizados dos exames ultrassonográficos veterinários. |
| `imagens` | Registra imagens vinculadas aos exames, incluindo caminhos locais e status de anonimização. |
| `selecao_amostra` | Guarda critérios de curadoria, qualidade, anonimização e inclusão/exclusão da amostra. |
| `prompts` | Armazena versões de prompts e schemas JSON planejados para uso assistivo futuro. |
| `analises_api` | Registra metadados de execuções futuras de análise assistida por API, sem conter diagnóstico autônomo. |
| `respostas_json` | Armazena respostas estruturadas futuras em JSON e campos de validação técnica. |
| `revisoes` | Registra revisões humanas futuras das respostas, reforçando a necessidade de avaliação veterinária. |

### Fluxo resumido

```text
Planilha de curadoria → Banco SQLite → Upload de imagens → Análise API → Resposta JSON → Revisão humana → Dashboard.
```

## Uso local

Instale as dependências de desenvolvimento e inicialize o banco SQLite local:

```bash
pip install -r requirements.txt
python src/database.py
```

O banco será criado em `data/db/usvet_ia.db`, caminho ignorado pelo Git.

## Testes

```bash
pytest
```
