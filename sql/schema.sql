-- Schema SQLite inicial do projeto acadêmico USVETIA.
-- Esta etapa define apenas a estrutura do banco interno.
-- Não inserir dados reais, diagnósticos ou dados fictícios neste arquivo.

PRAGMA foreign_keys = ON;

-- Tabela exames: armazena metadados anonimizados de cada exame retrospectivo.
CREATE TABLE IF NOT EXISTS exames (
    id_exame INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_exame TEXT NOT NULL UNIQUE,
    grupo_amostra TEXT NOT NULL,
    data_exame TEXT,
    periodo_base TEXT,
    especie TEXT,
    sexo TEXT,
    idade TEXT,
    peso_kg REAL,
    orgao_regiao_principal TEXT,
    outros_orgaos_avaliados TEXT,
    tipo_caso TEXT,
    normal_ou_alterado TEXT,
    descricao_tecnica_associada TEXT,
    descricao_veterinaria TEXT,
    historico_resumido TEXT,
    quantidade_imagens INTEGER,
    status_processamento TEXT DEFAULT 'não iniciado',
    observacoes TEXT,
    data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Tabela imagens: registra arquivos de imagem vinculados a exames, incluindo status de anonimização.
CREATE TABLE IF NOT EXISTS imagens (
    id_imagem INTEGER PRIMARY KEY AUTOINCREMENT,
    id_exame INTEGER NOT NULL,
    codigo_exame TEXT NOT NULL,
    nome_arquivo TEXT NOT NULL,
    caminho_original TEXT,
    caminho_anonimizado TEXT,
    tipo_imagem TEXT DEFAULT 'ultrassom',
    resolucao TEXT,
    qualidade_imagem TEXT,
    descricao_imagem TEXT,
    orgao_regiao_associado TEXT,
    dados_identificaveis_na_imagem TEXT,
    anonimizada TEXT DEFAULT 'não',
    hash_arquivo TEXT,
    data_upload TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_exame) REFERENCES exames(id_exame)
);

-- Tabela selecao_amostra: documenta critérios de curadoria, anonimização e inclusão na amostra.
CREATE TABLE IF NOT EXISTS selecao_amostra (
    id_selecao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_exame INTEGER NOT NULL,
    codigo_exame TEXT NOT NULL,
    grupo_amostra TEXT NOT NULL,
    qualidade_imagem TEXT,
    clareza_diagnostica TEXT,
    dados_identificaveis_na_imagem TEXT,
    dados_identificaveis_no_texto TEXT,
    anonimizacao_possivel TEXT,
    status_anonimizacao TEXT,
    incluido_na_amostra TEXT,
    motivo_exclusao TEXT,
    prioridade_processamento TEXT,
    observacoes_curadoria TEXT,
    FOREIGN KEY (id_exame) REFERENCES exames(id_exame)
);

-- Tabela prompts: guarda versões de prompts e schemas JSON planejados para uso futuro.
CREATE TABLE IF NOT EXISTS prompts (
    id_prompt INTEGER PRIMARY KEY AUTOINCREMENT,
    versao TEXT NOT NULL,
    nome_prompt TEXT,
    texto_prompt TEXT NOT NULL,
    schema_json TEXT,
    finalidade TEXT,
    ativo TEXT DEFAULT 'sim',
    data_criacao TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Tabela analises_api: registra metadados de execuções futuras de análise, sem executar APIs nesta etapa.
CREATE TABLE IF NOT EXISTS analises_api (
    id_analise INTEGER PRIMARY KEY AUTOINCREMENT,
    id_exame INTEGER NOT NULL,
    id_prompt INTEGER NOT NULL,
    codigo_exame TEXT NOT NULL,
    modelo TEXT,
    modo_teste TEXT,
    quantidade_imagens_enviadas INTEGER,
    status_analise TEXT DEFAULT 'pendente',
    tokens_entrada INTEGER,
    tokens_saida INTEGER,
    custo_estimado REAL,
    tempo_processamento_segundos REAL,
    erro TEXT,
    data_envio TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_exame) REFERENCES exames(id_exame),
    FOREIGN KEY (id_prompt) REFERENCES prompts(id_prompt)
);

-- Tabela respostas_json: armazena respostas JSON futuras e campos de validação associados.
CREATE TABLE IF NOT EXISTS respostas_json (
    id_resposta INTEGER PRIMARY KEY AUTOINCREMENT,
    id_analise INTEGER NOT NULL,
    codigo_exame TEXT NOT NULL,
    resposta_json TEXT,
    json_valido TEXT,
    erro_validacao TEXT,
    achados_extraidos TEXT,
    sugestao_texto_revisavel TEXT,
    limitacoes TEXT,
    data_resposta TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_analise) REFERENCES analises_api(id_analise)
);

-- Tabela revisoes: registra avaliações humanas futuras das análises produzidas.
CREATE TABLE IF NOT EXISTS revisoes (
    id_revisao INTEGER PRIMARY KEY AUTOINCREMENT,
    id_analise INTEGER NOT NULL,
    codigo_exame TEXT NOT NULL,
    revisor TEXT,
    concordancia TEXT,
    omissoes TEXT,
    achados_nao_sustentados TEXT,
    qualidade_resposta TEXT,
    utilidade_organizacao TEXT,
    observacoes_revisao TEXT,
    data_revisao TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_analise) REFERENCES analises_api(id_analise)
);

CREATE INDEX IF NOT EXISTS idx_exames_codigo_exame ON exames(codigo_exame);
CREATE INDEX IF NOT EXISTS idx_imagens_codigo_exame ON imagens(codigo_exame);
CREATE INDEX IF NOT EXISTS idx_imagens_id_exame ON imagens(id_exame);
CREATE UNIQUE INDEX IF NOT EXISTS idx_selecao_amostra_codigo_exame ON selecao_amostra(codigo_exame);
CREATE UNIQUE INDEX IF NOT EXISTS idx_prompts_nome_versao ON prompts(nome_prompt, versao);
CREATE INDEX IF NOT EXISTS idx_analises_api_id_exame ON analises_api(id_exame);
CREATE INDEX IF NOT EXISTS idx_respostas_json_id_analise ON respostas_json(id_analise);
CREATE INDEX IF NOT EXISTS idx_revisoes_id_analise ON revisoes(id_analise);
