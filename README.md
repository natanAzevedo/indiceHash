## 🚀 Iniciando o Projeto

Para rodar o projeto, você pode iniciar o frontend (Next.js) e o backend (Flask) de forma integrada ou manualmente. A integração é recomendada para desenvolvimento, pois executa ambos simultaneamente.

### Opção 1: Início Integrado (Recomendado)
1. Navegue para a pasta `front`.
2. Instale as dependências: `npm install`.
3. Inicie o modo de desenvolvimento: `npm run dev` (roda Next.js com Turbopack e o Flask na pasta pai `../`).
4. Ou, para produção: `npm run build` seguido de `npm run start` (compila e roda Next.js com o Flask).

Isso usa os scripts do `package.json` para executar ambos em paralelo via `concurrently`:

```json
"scripts": {
  "dev": "concurrently \"next dev --turbopack\" \"(cd ../ && flask --app api run)\"",
  "build": "next build --turbopack",
  "start": "concurrently \"next start\" \"(cd ../ && flask --app api run)\"",
  "lint": "eslint"
}
```

## 📋 Requisitos Principais

### ✅ 1. Interface Gráfica (1,0 ponto)
- [X] Criar interface gráfica obrigatória
- [X] Ilustrar estruturas de dados
- [X] Mostrar funcionamento do índice hash
- [X] Incluir campo para entrada da chave de busca
- [X] Exibir resultado da busca e número da página
- [X] Mostrar registros durante table scan

### ✅ 2. Funcionalidades Principais

#### 2.1 Construção do Índice
- [X] Implementar carregamento do arquivo de dados
- [X] Dividir dados em páginas conforme tamanho especificado
- [X] Criar buckets com base no cálculo NB
- [X] Aplicar função hash para mapear chaves

#### 2.2 Busca por Tupla
- [X] Implementar busca usando índice construído
- [X] Aplicar função hash na chave fornecida
- [X] Localizar e ler página correspondente
- [X] Exibir resultado na interface

#### 2.3 Table Scan
- [X] Implementar botão para table scan
- [X] Percorrer páginas sequencialmente
- [X] Listar registros até encontrar a chave
- [X] Calcular e exibir custo de leitura

### ✅ 3. Entidades/Estruturas (POO)

#### 3.1 Classe Tupla
- [X] Implementar representação de linha da tabela
- [X] Incluir valor da chave de busca
- [X] Incluir dados da linha

#### 3.2 Classe Tabela (1,5 pontos)
- [X] Implementar container para todas as tuplas
- [X] Carregar dados do arquivo
- [X] Organizar tuplas em estrutura adequada

#### 3.3 Classe Página (1,0 + 1,0 pontos)
- [X] Implementar entrada para tamanho da página
- [X] Calcular quantidade de páginas necessárias
- [X] Representar divisão física da tabela
- [X] Gerenciar alocação de tuplas por página

#### 3.4 Classe Bucket (0,5 pontos)
- [X] Implementar mapeamento chave → endereço da página
- [X] Calcular quantidade de buckets (NB > NR/FR)
- [X] Definir tamanho dos buckets (FR)

#### 3.5 Função Hash (1,0 ponto)
- [X] Projetar e implementar função hash
- [X] Mapear chave de busca → endereço do bucket
- [X] Documentar escolha da função

### ✅ 4. Parâmetros de Configuração

#### 4.1 Arquivo de Dados
- [X] Usar arquivo com 466 mil palavras em inglês
- [X] Source: https://github.com/dwyl/english-words
- [X] Processar uma palavra por linha como chave única

#### 4.2 Configurações Dinâmicas
- [x] Tamanho da página (entrada do usuário)
- [x] Número de buckets (calculado: NB > NR/FR)
- [x] Tamanho dos buckets (FR)
- [x] Campo para chave de busca

### ✅ 5. Tratamento de Problemas

#### 5.1 Resolução de Colisões
- [x] Implementar algoritmo para tratar colisões
- [x] Calcular taxa de colisões (0,5 pontos)
- [x] Exibir estatística na interface

#### 5.2 Overflow de Buckets
- [x] Implementar algoritmo para resolver overflow
- [x] Calcular taxa de overflows (0,5 pontos)
- [x] Exibir estatística na interface

### ✅ 6. Funcionalidades de Pesquisa (2,0 pontos)
- [x] Implementar busca por chave usando índice
- [x] Retornar tupla e número da página
- [x] Calcular e mostrar custo (acessos a disco)
- [x] Validar funcionamento completo

### ✅ 7. Estatísticas e Métricas (0,5 pontos)
- [x] Calcular estimativa de custo para busca indexada
- [x] Calcular custo do table scan (páginas lidas)
- [x] Exibir todas as métricas na interface
- [x] Comparar eficiência entre métodos

### ✅ 8. Table Scan Completo (0,5 pontos)
- [x] Implementar percurso sequencial
- [x] Mostrar progresso na interface
- [x] Calcular custo total
- [x] Comparar com busca indexada

## 🔄 Fluxo de Funcionamento

### Etapa 1: Preparação
- [x] Carregar arquivo de dados em memória
- [x] Dividir linhas em páginas conforme tamanho

### Etapa 2: Construção do Índice
- [x] Criar NB buckets de tamanho FR
- [x] Aplicar função hash em cada tupla
- [x] Armazenar mapeamento chave → endereço da página

### Etapa 3: Busca
- [x] Receber chave de busca do usuário
- [x] Aplicar função hash para encontrar página
- [x] Ler página e buscar tupla
- [x] Exibir resultado e custo

### Etapa 4: Table Scan
- [x] Ativar botão após entrada da chave
- [x] Percorrer páginas sequencialmente
- [x] Mostrar progresso até encontrar chave
- [x] Exibir custo total do scan

## 📊 Critérios de Avaliação

| Critério | Pontos | Status |
|----------|---------|---------|
| Interface gráfica | 1,0 | [ ] |
| Carga de dados nas páginas | 1,5 | [x] |
| Entrada para tamanho da página | 1,0 | [x] |
| Cálculo da quantidade de páginas | 1,0 | [x] |
| Função hash | 1,0 | [x] |
| Cálculo da quantidade de buckets | 0,5 | [x] |
| Funcionamento com pesquisa | 2,0 | [x] |
| Taxa de colisões | 0,5 | [x] |
| Taxa de overflows | 0,5 | [x] |
| Table scan | 0,5 | [x] |
| Estimativa de custo | 0,5 | [x] |
| **TOTAL** | **10,0** | 9,0 (falta interface) |

## 🚀 Próximos Passos

### Sprint 1: Estruturas Básicas
- [x] Definir arquitetura do projeto
- [x] Implementar classes básicas (Tupla, Página, Bucket)
- [x] Criar interface gráfica inicial

### Sprint 2: Core do Sistema
- [x] Implementar função hash
- [x] Desenvolver carregamento de dados
- [x] Construir índice hash

### Sprint 3: Funcionalidades de Busca
- [x] Implementar busca indexada
- [x] Desenvolver table scan
- [x] Calcular estatísticas

### Sprint 4: Refinamentos
- [x] Tratar colisões e overflows
- [X] Finalizar interface
- [X] Preparar apresentação

## 📝 Notas Importantes
- Interface gráfica é **obrigatória**
- Usar **POO** como padrão
- Arquivo de dados: 466 mil palavras inglesas
- Apresentação obrigatória para a equipe
