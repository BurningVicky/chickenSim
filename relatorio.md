# Relatório de Decisões Técnicas — Chicken Sim

Este documento registra as escolhas de arquitetura, modelagem, regras de negócio, limitações e aprendizados do desenvolvimento do **Chicken Sim** no teste técnico de Desenvolvedora Python/Django.

---

## 1. Modelagem
Estruturei o domínio em torno das entidades centrais previstas no teste: usuário com identificação de perfil (`is_cartorio`), `Raca`, `Propriedade`, `Animal` (galinha) e `Transferencia`.

- **Por que estruturei assim:** separei os conceitos de propriedade rural e galinhas para refletir que um produtor pode gerenciar mais de uma propriedade e que a posse de uma galinha muda ao longo do tempo por meio de transferências registradas. Em `Animal`, utilizei relacionamentos opcionais (`pai` e `mae` apontando para o próprio model) e `numero_registro` único para representar genealogia e identificação oficial.
- **Diferenças em relação à modelagem sugerida:** Foi utilizado `is_cartorio` em vez de usar apenas Grupos do Django ou um model de perfil separado, como sugerido na seção 8. Utilizando a dinstinção de perfil por atributo booleano `is_cartorio` no usuário.
Restrição NOT NULL em nascimento no campo de nascimento da galinha ficando como obrigatório no banco, o que exigiu incluilo no AnimalCartorioForm. Também foi adicionado nas views de transferencia um campo extra `observacao`.

---

## 2. Organização
O projeto foi organizado com Django e SQLite, utilizando URLs nomeadas, templates organizados por app e Class-Based Views (CBVs) nas operações principais de listagem, criação, atualização, exclusão e consulta.

- **Apps e responsabilidades:**
  - `cartorio`: concentra os models do domínio (`Animal`, `Propriedade`, `Raca`, `Transferencia`), mixins de permissão (`CartorioRequiredMixin`, `ProdutorRequiredMixin`), forms, views e templates do painel do cartório, do painel do produtor, do fluxo de transferências, do histórico e da certidão.
- **Uso de telas próprias vs. Django Admin:** priorizei telas próprias com Tailwind CSS para os fluxos operacionais de Cartório e Produtor (dashboards, cadastros, solicitação e análise de transferências, histórico e certidão), deixando o Django Admin apenas como apoio administrativo/manutenção, sem depender dele para o fluxo principal do usuário.

---

## 3. Regras e Validações
Além das regras listadas na seção 5 (`RN01`, `RN02` e `RN03`), apliquei validações adicionais no domínio para manter consistência de dados e rastreabilidade:

- **Número de registro único (`RN01`):** garantido na definição do campo no model/banco de dados e validado no formulário de cadastro da galinha.
- **Solicitação apenas de galinhas próprias (`RN02`):** garantida no `TransferenciaCreateForm` filtrando o queryset de `animal` pelas propriedades do produtor e validando em `clean()` que a galinha pertence a uma propriedade vinculada ao usuário solicitante e reforçada pela restrição de acesso da view (`ProdutorRequiredMixin`).
- **Atualização automática na aprovação (`RN03`):** executada em `TransferenciaDecidirView.form_valid` dentro de `transaction.atomic()`, atualizando `animal.propriedade_atual` para `transferencia.propriedade_destino` e registrando `data_decisao` e `status='aprovada'`.
- **Regras adicionais implementadas:**
  - **Destino distinto da origem e escolha restrita:** no `TransferenciaCreateForm`, bloqueio quando a propriedade de destino coincide com a propriedade atual da galinha e filtro do queryset de destino.
  - **Justificativa obrigatória na rejeição:** em `TransferenciaDecisaoForm` / `TransferenciaDecidirView`, exigência de motivo ao rejeitar uma transferência e limpeza de `motivo_rejeicao` quando aprovada.
  - **Bloqueio de reavaliação:** impedimento de alterar uma transferência que já saiu do status `pendente`.
  - **Obrigatoriedade de campos essenciais:** garantia de campos obrigatórios como `nascimento` no cadastro de galinhas para evitar falhas de integridade (`NOT NULL`) no banco.

---

## 4. Perfis e Isolamento
A distinção entre **Cartório** e **Produtor** utiliza a autenticação padrão do Django combinada ao atributo `is_cartorio` no usuário e a mixins (`CartorioRequiredMixin` e `ProdutorRequiredMixin`), além de `dashboard_router` para direcionar cada perfil após o login.

- **Isolamento de dados (`RNF02`):** nas views e querysets do produtor como `ProdutorDashboardView`, `TransferenciaCreateView` e `TransferenciaHistoricoListView`, os registros são filtrados pelo produtor logado (`propriedade_atual__in=propriedades_produtor`, `produtor=user` ou `solicitante=user`).
- **Acesso indevido por URL:** rotas exclusivas do cartório bloqueiam produtores via mixin/permissão, e em `AnimalCertidaoDetailView` há verificação explícita do vínculo do produtor com a propriedade atual da galinha, levantando `PermissionDenied` (403) quando um produtor tenta acessar a certidão de uma galinha que não é sua.

---

## 5. Transferências
O fluxo de transferência segue três etapas principais:

1. **Solicitação pelo produtor (`TransferenciaCreateView`):** o produtor seleciona uma galinha da sua posse e a propriedade de destino; na submissão válida, `propriedade_origem` é preenchida a partir de `animal.propriedade_atual`, `solicitante` recebe `self.request.user` e o registro entra com `status='pendente'`.
2. **Análise pelo cartório (`TransferenciaPendenteListView` e `TransferenciaDecidirView`):** o cartório lista as solicitações pendentes em ordem de solicitação e decide por aprovar ou rejeitar.
3. **Efetivação e histórico:** na aprovação, o update de `Animal.propriedade_atual` e da `Transferencia` ocorre dentro de `transaction.atomic()`. Transferências aprovadas passam a compor o histórico cronológico (`TransferenciaHistoricoListView` e `AnimalCertidaoDetailView`).

---

## 6. Alternativas Descartadas
- **Publicar no GitHub Pages:** descartei o GitHub Pages para hospedar a aplicação completa porque ele serve apenas arquivos estáticos, enquanto o projeto depende de backend Python/Django, sessão/autenticação, transações no banco e renderização server-side. Para publicação online de aplicação Django, o caminho adequado é uma plataforma com suporte a WSGI/Python como Render ou Railway.
Também descartei por conta de tempo limite, melhoras de UI/UX.

---

## 7. Limitações
- **O que ficou incompleto ou simplificado:** Migrations automaticos de seed, melhorias de UI/UX, e maior compatibilidade com dispositivos móveis.
- **O que eu faria com mais tempo:** Expandiria a cobertura de testes automatizados para todas as regras de negócio e de permissão/isolamento, revisaria a exibição genealógica completa na certidão, configuraria variáveis de ambiente para deploy em nuvem e adicionaria Docker/PostgreSQL.

---

## 8. Dificuldades e Aprendizados
- **O que foi mais difícil:** Mesmo não sendo uma stack(`Python`) desconhecida, a curva de aprendizado é bem desafiadora, esta é a primeira vez que utilizo `Django` e realmente construo uma aplicação em `Python` com algum propósito fora do meio acadêmico. Os primeiros dois dias praticamente foram absorvendo ao máximo de conteúdo e documentação sobre as stacks, me levando ao limite do consumo por hora de energéticos.
- **O que aprendi:** reforcei MUITO na prática a importância de alinhar os de campos entre `models.py`, `forms.py` e templates e verificar os retornos HTTP `200` vs. `302` vs. `403`/`404` durante o teste de cada rota.

---

## 9. Uso de Ferramentas de IA
Utilizei assistência de IA (Claude Code) durante o desenvolvimento como apoio para diagnosticar tracebacks, revisar trechos de views, forms e templates, e estruturar a documentação.
Com a utilização correta por desenvolvedoras, a IA é uma excelênte ferramenta de trabalho, aumentando exponêncialmente as iterações e entregas.

- **Como validei o resultado:** Não aceitei código sem leitura e teste, revisei intensamente cada sugestão aos models, URLs e regras do teste técnico, todo o código(com exceção dos templates/cartorio/) todos os códigos foram digitados a mão, mesmo os sugeridos por IA. Foram ajustados detalhes específicos do projeto e executei a aplicação no navegador(`Vivaldi`) e no terminal para conferir o comportamento de cada fluxo da aplicação.