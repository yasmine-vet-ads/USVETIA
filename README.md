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
