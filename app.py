import streamlit as st
import pandas as pd
import io
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# Tenta importar o conector — se falhar, usa dados simulados
try:
    import metabase_connector as mb
    MODO_REAL = True
except Exception:
    MODO_REAL = False

st.set_page_config(
    page_title="LI Pulse · Automação de Onboarding",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── PALETA LOJA INTEGRADA ─────────────────────────────────────────────────────
# Teal primário:  #1ABCB0
# Teal escuro:    #0D4F4A
# Verde limão:    #D4F53C
# Bege/creme:     #F2EDE4
# Branco:         #FFFFFF
# Texto escuro:   #1A2E2B
# Card destaque:  #0D4F4A

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; background: #F2EDE4; }
    .main { background: #F2EDE4; }

    /* North Star box */
    .ns-box {
        background: #0D4F4A;
        border-radius: 16px;
        padding: 1.5rem 1.8rem;
        margin-bottom: 1.5rem;
    }
    .ns-label { font-size: 11px; color: #1ABCB0; text-transform: uppercase; letter-spacing: .1em; margin-bottom: 6px; font-weight: 600; }
    .ns-value { font-size: 48px; font-weight: 700; color: #D4F53C; line-height: 1; }
    .ns-desc  { font-size: 14px; color: #9DCFCC; margin-top: 8px; }

    /* Metric cards */
    .metric-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 1.2rem;
        border: none;
    }
    .metric-label { font-size: 12px; color: #5A7A78; margin-bottom: 6px; font-weight: 500; }
    .metric-value { font-size: 28px; font-weight: 700; color: #1A2E2B; }
    .metric-sub   { font-size: 12px; color: #1ABCB0; margin-top: 4px; font-weight: 500; }

    /* Gargalo boxes */
    .gargalo-box { border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: .8rem; border-left: 4px solid; }
    .gargalo-critico { background: #FEF2F2; border-color: #E24B4A; }
    .gargalo-atencao { background: #FFFBEB; border-color: #F59E0B; }
    .gargalo-ok      { background: #F0FDF4; border-color: #1ABCB0; }
    .gargalo-titulo  { font-size: 14px; font-weight: 600; margin-bottom: 4px; color: #1A2E2B; }
    .gargalo-desc    { font-size: 13px; color: #4A6A68; line-height: 1.5; }

    /* Pipeline steps */
    .pipeline-step { display: flex; gap: 12px; align-items: flex-start; padding: 12px 0; border-bottom: 1px solid #E8E4DE; }
    .pipeline-step:last-child { border-bottom: none; }
    .step-icon { width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0; font-weight: 700; }
    .step-title { font-size: 13px; font-weight: 600; color: #1A2E2B; margin-bottom: 2px; }
    .step-desc  { font-size: 12px; color: #5A7A78; line-height: 1.5; }
    .step-time  { font-size: 11px; color: #9DBDBB; margin-top: 2px; }

    /* Email preview */
    .email-preview { background: white; border: 1px solid #E8E4DE; border-radius: 12px; padding: 1.2rem; font-size: 13px; line-height: 1.7; color: #1A2E2B; }
    .email-header  { font-size: 11px; color: #9DBDBB; margin-bottom: 12px; border-bottom: 1px solid #F2EDE4; padding-bottom: 8px; }

    /* Badges */
    .badge { display: inline-block; font-size: 11px; padding: 3px 10px; border-radius: 20px; font-weight: 600; }
    .badge-critico { background: #FEE2E2; color: #991B1B; }
    .badge-atencao { background: #FEF3C7; color: #92400E; }
    .badge-ok      { background: #D1FAF6; color: #0D4F4A; }
    .badge-star    { background: #D4F53C; color: #0D4F4A; }

    /* Cards gerais */
    .card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 1.4rem;
        margin-bottom: 1rem;
        border: none;
    }

    /* Sidebar */
    div[data-testid="stSidebar"] {
        background: #0D4F4A !important;
    }
    div[data-testid="stSidebar"] * { color: #E8F5F4 !important; }
    div[data-testid="stSidebar"] .stRadio label { color: #E8F5F4 !important; }

    /* Botões download */
    .stDownloadButton > button {
        background: #1ABCB0 !important;
        color: #0D4F4A !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: .6rem 1.2rem !important;
    }
    .stDownloadButton > button:hover {
        background: #D4F53C !important;
        color: #0D4F4A !important;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background: #FFFFFF !important;
        border-radius: 10px !important;
        color: #1A2E2B !important;
    }

    /* Inputs */
    .stTextInput > div > div > input {
        border-radius: 10px !important;
        border: 1.5px solid #C8E8E6 !important;
        background: #FFFFFF !important;
        color: #1A2E2B !important;
    }
    .stSelectbox > div > div {
        border-radius: 10px !important;
        border: 1.5px solid #C8E8E6 !important;
        background: #FFFFFF !important;
    }

    /* Métricas nativas */
    [data-testid="metric-container"] {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 1rem;
    }
    [data-testid="stMetricValue"] { color: #1A2E2B !important; }
    [data-testid="stMetricDelta"] { color: #1ABCB0 !important; }

    /* Tabelas */
    .dataframe { border-radius: 10px; overflow: hidden; }
    thead tr th { background: #0D4F4A !important; color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# ── DADOS ────────────────────────────────────────────────────────────────────

BASE = {
    "Jan 2025": dict(total=3947,p1=3434,p2=2802,p3=2600,p5=2200,
        cfg_env=1820,cfg_pag=1500,cfg_prod=1697,cfg=1260,
        visita=980,venda_cap=320,venda_apr=189,north_star=94,
        origem={"Orgânico":1580,"Pago":1970,"Indicação":397},
        tempo=dict(env=2.1,pag=2.8,prod=1.4,config=4.2,visita=5.8,venda=12.4),
        seg=[
            dict(n="Moda",c=820,cfg=210,v=52,t=11.2),
            dict(n="Eletrônicos",c=540,cfg=162,v=38,t=9.8),
            dict(n="Casa e Dec.",c=490,cfg=118,v=21,t=14.1),
            dict(n="Beleza",c=610,cfg=134,v=29,t=13.5),
            dict(n="Alimentos",c=380,cfg=63,v=18,t=16.2),
            dict(n="Outros",c=1107,cfg=573,v=31,t=18.7),
        ]),
    "Fev 2025": dict(total=4210,p1=3788,p2=3031,p3=2900,p5=2450,
        cfg_env=2020,cfg_pag=1680,cfg_prod=1900,cfg=1470,
        visita=1120,venda_cap=380,venda_apr=231,north_star=112,
        origem={"Orgânico":1600,"Pago":2200,"Indicação":410},
        tempo=dict(env=1.9,pag=2.5,prod=1.2,config=3.8,visita=5.2,venda=11.8),
        seg=[
            dict(n="Moda",c=900,cfg=243,v=62,t=10.8),
            dict(n="Eletrônicos",c=580,cfg=186,v=44,t=9.2),
            dict(n="Casa e Dec.",c=520,cfg=130,v=26,t=13.4),
            dict(n="Beleza",c=650,cfg=156,v=34,t=12.9),
            dict(n="Alimentos",c=410,cfg=70,v=22,t=15.8),
            dict(n="Outros",c=1150,cfg=685,v=43,t=17.2),
        ]),
    "Mar 2025": dict(total=3820,p1=3362,p2=2673,p3=2480,p5=2100,
        cfg_env=1710,cfg_pag=1390,cfg_prod=1604,cfg=1146,
        visita=890,venda_cap=298,venda_apr=171,north_star=87,
        origem={"Orgânico":1490,"Pago":1950,"Indicação":380},
        tempo=dict(env=2.3,pag=3.1,prod=1.6,config=4.6,visita=6.2,venda=13.1),
        seg=[
            dict(n="Moda",c=780,cfg=187,v=47,t=11.9),
            dict(n="Eletrônicos",c=510,cfg=143,v=33,t=10.3),
            dict(n="Casa e Dec.",c=460,cfg=106,v=18,t=14.8),
            dict(n="Beleza",c=580,cfg=116,v=25,t=14.1),
            dict(n="Alimentos",c=350,cfg=56,v=15,t=17.0),
            dict(n="Outros",c=1140,cfg=538,v=33,t=19.1),
        ]),
}

LOJISTAS = [
    dict(id="LI-00421",nome="Moda da Ana",seg="Moda",origem="Orgânico",dias=3,
         cfg_prod=1,cfg_pag=0,cfg_env=0,visita=0,vendas=0,
         gargalo="sem_pagamento",gravidade="Crítico"),
    dict(id="LI-00834",nome="Tech Store BR",seg="Eletrônicos",origem="Pago",dias=6,
         cfg_prod=1,cfg_pag=1,cfg_env=1,visita=0,vendas=0,
         gargalo="sem_visita",gravidade="Atenção"),
    dict(id="LI-01092",nome="Casa Bonita",seg="Casa e Dec.",origem="Indicação",dias=2,
         cfg_prod=1,cfg_pag=1,cfg_env=0,visita=0,vendas=0,
         gargalo="sem_frete",gravidade="Crítico"),
    dict(id="LI-01455",nome="Bella Cosméticos",seg="Beleza",origem="Pago",dias=1,
         cfg_prod=0,cfg_pag=0,cfg_env=0,visita=0,vendas=0,
         gargalo="sem_produto",gravidade="Crítico"),
    dict(id="LI-01820",nome="Sabor & Arte",seg="Alimentos",origem="Orgânico",dias=10,
         cfg_prod=1,cfg_pag=1,cfg_env=1,visita=1,vendas=0,
         gargalo="sem_venda",gravidade="Atenção"),
    dict(id="LI-02341",nome="Roupas & Cia",seg="Moda",origem="Pago",dias=14,
         cfg_prod=1,cfg_pag=1,cfg_env=1,visita=1,vendas=5,
         gargalo="north_star",gravidade="North Star"),
    dict(id="LI-02788",nome="Eletrô Plus",seg="Eletrônicos",origem="Orgânico",dias=4,
         cfg_prod=1,cfg_pag=0,cfg_env=1,visita=0,vendas=0,
         gargalo="sem_pagamento",gravidade="Crítico"),
    dict(id="LI-03102",nome="Mundo Natural",seg="Alimentos",origem="Indicação",dias=5,
         cfg_prod=1,cfg_pag=1,cfg_env=1,visita=0,vendas=0,
         gargalo="sem_visita",gravidade="Atenção"),
]

GARGALOS = {
    "sem_produto": dict(
        onde="Cadastro de produto",
        por_que="Nenhum produto publicado. Sem vitrine, nenhum comprador encontra o que comprar.",
        proximo="Automação disparou e-mail guiando o lojista a cadastrar o primeiro produto.",
        email_assunto="Sua loja está quase pronta — falta o produto!",
        email_corpo="""Olá, {nome}!\n\nSua loja foi criada mas ainda não tem produtos publicados.\n\nSem produtos na vitrine, nenhum comprador consegue comprar de você.\n\nO que fazer agora:\n→ Acesse sua loja e clique em "Produtos"\n→ Adicione pelo menos 1 produto com foto e descrição\n→ Publique e compartilhe o link com seus contatos\n\nLeva menos de 10 minutos.\n\n— Time Loja Integrada"""
    ),
    "sem_pagamento": dict(
        onde="Configuração de pagamento",
        por_que="Produto cadastrado mas pagamento inativo. O cliente tenta comprar e não consegue finalizar.",
        proximo="Automação disparou e-mail orientando ativação do Pagali — 5 minutos.",
        email_assunto="Falta só 1 passo para sua loja vender",
        email_corpo="""Olá, {nome}!\n\nVocê já tem produtos na loja — ótimo!\n\nMas o pagamento ainda não está configurado. Sem ele, nenhum pedido pode ser finalizado.\n\nO que fazer agora:\n→ Acesse Configurações → Pagamento\n→ Ative o Pagali em menos de 5 minutos\n→ Pronto — sua loja já aceita Pix, cartão e boleto\n\n— Time Loja Integrada"""
    ),
    "sem_frete": dict(
        onde="Configuração de frete",
        por_que="Pagamento ativo mas frete não configurado. O checkout trava na entrega.",
        proximo="Automação disparou e-mail sugerindo Enviali como solução de frete automático.",
        email_assunto="Sua loja precisa de frete para vender",
        email_corpo="""Olá, {nome}!\n\nPagamento configurado — você está quase lá!\n\nFalta ativar o frete. Sem ele, o cliente não consegue concluir a compra.\n\nO que fazer agora:\n→ Acesse Configurações → Frete\n→ Ative o Enviali — frete calculado automaticamente\n→ Sua loja estará 100% pronta para vender\n\n— Time Loja Integrada"""
    ),
    "sem_visita": dict(
        onde="Atração de tráfego",
        por_que="Loja 100% configurada mas sem nenhum visitante. O lojista não está divulgando.",
        proximo="Automação disparou e-mail com checklist de divulgação — WhatsApp e Instagram.",
        email_assunto="Sua loja está pronta — agora precisa de visitantes",
        email_corpo="""Olá, {nome}!\n\nSua loja está configurada e pronta para vender!\n\nAgora falta atrair os primeiros visitantes. As primeiras vendas vêm da sua própria rede.\n\nO que fazer agora:\n→ Copie o link da sua loja no painel\n→ Compartilhe no WhatsApp pessoal e grupos\n→ Poste nos seus stories do Instagram\n\n— Time Loja Integrada"""
    ),
    "sem_venda": dict(
        onde="Conversão de visitantes",
        por_que="Visitantes chegando mas nenhum compra. Problema de fotos, preço ou descrição.",
        proximo="Automação disparou e-mail com dicas de conversão para o segmento.",
        email_assunto="Sua loja tem visitas — veja como converter em vendas",
        email_corpo="""Olá, {nome}!\n\nSua loja já está recebendo visitantes — ótimo sinal!\n\nPara converter em vendas:\n→ Adicione mais fotos ao produto (mínimo 4 ângulos)\n→ Escreva uma descrição detalhada com benefícios\n→ Verifique se o preço está competitivo\n→ Ative o chat no WhatsApp\n\n— Time Loja Integrada"""
    ),
    "north_star": dict(
        onde="North Star atingida",
        por_que="5 pedidos em 14 dias — retenção 4× maior. Lojista no caminho certo.",
        proximo="Automação disparou e-mail de parabéns + sugestão de marketplaces.",
        email_assunto="Parabéns! Você atingiu 5 pedidos — veja o próximo passo",
        email_corpo="""Olá, {nome}!\n\nIncrível! Você já tem 5 pedidos aprovados nos primeiros 14 dias.\n\nPróximos passos:\n→ Expanda para Mercado Livre e Shopee\n→ Ative o Enviali para reduzir custo de frete\n→ Configure recuperação de carrinho abandonado\n\nContinue assim!\n\n— Time Loja Integrada"""
    ),
}

LOJAS_ATIVAS = {
    "Moda da Ana (LI-00421)": dict(
        causa="churn_b2b", perfil="Moda · Pago · Alto ticket",
        meses=["Out","Nov","Dez","Jan","Fev","Mar"],
        pedidos=[142,138,151,89,54,31], ticket=[187,192,195,178,143,121],
        gmv=[26554,26496,29445,15842,7722,3751],
        pix=[18,19,21,28,35,42], cartao=[61,60,58,47,38,31], externo=[21,21,21,25,27,27],
        novos=[38,41,35,22,18,12], recorrentes=[104,97,116,67,36,19], cupom_pct=[12,11,13,31,38,29],
        top_clientes=[
            dict(nome="Distribuidora Bella Moda LTDA",emails="compras@bellamoda.com.br",receita=18420,pedidos=34),
            dict(nome="Revendas Fashion SP",emails="pedidos@revendasfashion.com",receita=14200,pedidos=28),
            dict(nome="Atacado Vestuário Norte",emails="atacado@vestuarionorte.com",receita=11800,pedidos=22),
        ]
    ),
    "Tech Store BR (LI-00834)": dict(
        causa="colapso_canal", perfil="Eletrônicos · Pago · Ticket médio",
        meses=["Out","Nov","Dez","Jan","Fev","Mar"],
        pedidos=[98,104,112,71,48,29], ticket=[342,351,338,298,241,198],
        gmv=[33516,36504,37856,21158,11568,5742],
        pix=[22,24,25,32,41,48], cartao=[55,54,55,44,35,28], externo=[23,22,20,24,24,24],
        novos=[31,33,38,24,18,11], recorrentes=[67,71,74,47,30,18], cupom_pct=[8,9,8,18,24,31],
        top_clientes=[
            dict(nome="Rede de Informática Central",emails="ti@redecentral.com.br",receita=22100,pedidos=41),
            dict(nome="Suprimentos Office Pro",emails="suprimentos@officepro.com",receita=17500,pedidos=33),
            dict(nome="Tech Solutions Empresarial",emails="compras@techsol.com.br",receita=13200,pedidos=25),
        ]
    ),
    "Bella Cosméticos (LI-01455)": dict(
        causa="mix_pagamento", perfil="Beleza · Grátis · Ticket baixo",
        meses=["Out","Nov","Dez","Jan","Fev","Mar"],
        pedidos=[210,198,231,195,188,172], ticket=[89,92,88,74,68,61],
        gmv=[18690,18216,20328,14430,12784,10492],
        pix=[28,29,31,48,57,64], cartao=[58,57,55,38,31,24], externo=[14,14,14,14,12,12],
        novos=[82,79,91,78,74,68], recorrentes=[128,119,140,117,114,104], cupom_pct=[9,10,14,12,11,13],
        top_clientes=[
            dict(nome="Maria Silva",emails="maria.silva@gmail.com",receita=1240,pedidos=18),
            dict(nome="Ana Oliveira",emails="ana.oliveira@hotmail.com",receita=980,pedidos=14),
            dict(nome="Carla Mendes",emails="carla.m@gmail.com",receita=870,pedidos=12),
        ]
    ),
}

DIAGNOSTICOS_QUEDA = {
    "churn_b2b": dict(
        causa="Churn de clientes B2B / revendedores",
        vetor="Queda de volume + ticket (base fiel abandonando)",
        origem="Clientes B2B que representavam alto ticket pararam de comprar. Provável mudança de fornecedor.",
        acoes=[
            ("Imediata","Contatar os top 3 clientes B2B por WhatsApp/telefone — não por e-mail"),
            ("Curto prazo","Criar condição especial de recompra (desconto atacado, frete grátis acima de X)"),
            ("Médio prazo","Estruturar canal B2B dedicado com catálogo e preços por volume"),
        ]
    ),
    "colapso_canal": dict(
        causa="Colapso do canal de vendas ativo",
        vetor="Queda de volume com ticket caindo junto",
        origem="Pedidos externos estagnaram enquanto canal orgânico caiu. Lojista parou de fazer vendas ativas.",
        acoes=[
            ("Imediata","CS entrar em contato para entender se houve mudança operacional"),
            ("Curto prazo","Ativar automação de recuperação de carrinho e reengajamento de base"),
            ("Médio prazo","Treinar lojista em estratégias de vendas ativas via WhatsApp Business"),
        ]
    ),
    "mix_pagamento": dict(
        causa="Mudança de mix de pagamento (efeito Pix)",
        vetor="Queda de ticket com volume relativamente estável",
        origem="Crescimento do Pix reduziu o ticket médio matematicamente. Clientes de cartão migraram.",
        acoes=[
            ("Imediata","Criar incentivo para compras acima de R$X (frete grátis, brinde)"),
            ("Curto prazo","Ativar parcelamento sem juros no cartão para elevar ticket médio"),
            ("Médio prazo","Testar bundle de produtos para aumentar valor do carrinho"),
        ]
    ),
}

PALAVRAS_B2B = [
    "distribuidora","distribuidor","atacado","atacadista","ltda","s.a.","s/a",
    "eireli","cnpj","farmácia","farmacia","drogaria","revendas","revendedor",
    "comercio","comércio","suprimentos","soluções","solutions","network",
    "industria","indústria","logistica","logística","representações",
    "wholesale","enterprises","trading","group","grupo","holdings",
    "corp","rede","central","master","plus","pro","tech","store"
]

def detectar_b2b(clientes):
    b2b = []
    for c in clientes:
        nome = c["nome"].lower()
        email = c["emails"].lower()
        score_b2b = 0
        for palavra in PALAVRAS_B2B:
            if palavra in nome: score_b2b += 1
        if "@" in email:
            dominio = email.split("@")[1]
            if not any(d in dominio for d in ["gmail","hotmail","yahoo","outlook","icloud","uol","bol"]):
                score_b2b += 2
        b2b.append({**c, "perfil_b2b": score_b2b >= 2, "score_b2b": score_b2b})
    return b2b

def calcular_score_churn(d):
    score = 0
    razoes = []
    queda_gmv = (d["gmv"][-1] - d["gmv"][0]) / d["gmv"][0] * 100
    if queda_gmv < -50:   score += 35; razoes.append(("GMV caiu mais de 50%", 35, "critico"))
    elif queda_gmv < -30: score += 25; razoes.append((f"GMV caiu {abs(round(queda_gmv,1))}%", 25, "alto"))
    elif queda_gmv < -15: score += 15; razoes.append((f"GMV caiu {abs(round(queda_gmv,1))}%", 15, "medio"))
    else:                 score += 5;  razoes.append((f"GMV estável", 5, "baixo"))
    queda_rec = (d["recorrentes"][-1] - d["recorrentes"][0]) / d["recorrentes"][0] * 100
    if queda_rec < -50:   score += 25; razoes.append(("Recorrentes caíram >50%", 25, "critico"))
    elif queda_rec < -30: score += 18; razoes.append((f"Recorrentes caíram {abs(round(queda_rec,1))}%", 18, "alto"))
    elif queda_rec < -15: score += 10; razoes.append((f"Recorrentes caíram {abs(round(queda_rec,1))}%", 10, "medio"))
    queda_ticket = (d["ticket"][-1] - d["ticket"][0]) / d["ticket"][0] * 100
    if queda_ticket < -25: score += 15; razoes.append((f"Ticket caiu {abs(round(queda_ticket,1))}%", 15, "alto"))
    elif queda_ticket < -10: score += 8; razoes.append((f"Ticket caiu {abs(round(queda_ticket,1))}%", 8, "medio"))
    delta_pix = d["pix"][-1] - d["pix"][0]
    if delta_pix > 20: score += 10; razoes.append((f"Pix cresceu +{delta_pix}pp", 10, "medio"))
    clientes_b2b = detectar_b2b(d["top_clientes"])
    n_b2b = sum(1 for c in clientes_b2b if c["perfil_b2b"])
    if n_b2b >= 2:   score += 15; razoes.append((f"{n_b2b} clientes B2B churned", 15, "critico"))
    elif n_b2b == 1: score += 8;  razoes.append(("1 cliente B2B churned", 8, "medio"))
    score = min(score, 100)
    nivel = "Crítico" if score >= 70 else "Alto" if score >= 45 else "Moderado" if score >= 25 else "Baixo"
    cor   = "#E24B4A" if score >= 70 else "#F59E0B" if score >= 45 else "#1ABCB0" if score >= 25 else "#22C55E"
    return score, nivel, cor, razoes, clientes_b2b

def pct(a,b): return round(a/b*100,1) if b>0 else 0
def score_loja(l):
    s=0
    if l["cfg_prod"]: s+=25
    if l["cfg_pag"]:  s+=25
    if l["cfg_env"]:  s+=20
    if l["visita"]:   s+=15
    if l["vendas"]>0: s+=15
    return s

def gerar_excel_lojista(loja, score, gargalo_info):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        pd.DataFrame([{
            "ID": loja["id"], "Nome": loja["nome"], "Segmento": loja["seg"],
            "Origem": loja["origem"], "Dias desde cadastro": loja["dias"],
            "Score": score, "Gravidade": loja["gravidade"],
            "Onde travou": gargalo_info["onde"],
            "Por que travou": gargalo_info["por_que"],
            "Próximo passo": gargalo_info["proximo"],
            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }]).T.reset_index().rename(columns={"index":"Campo",0:"Valor"}).to_excel(writer, sheet_name="Diagnóstico", index=False)
        pd.DataFrame([{
            "Produto cadastrado": "Sim" if loja["cfg_prod"] else "Não",
            "Pagamento configurado": "Sim" if loja["cfg_pag"] else "Não",
            "Frete configurado": "Sim" if loja["cfg_env"] else "Não",
            "1ª visita": "Sim" if loja["visita"] else "Não",
            "1ª venda": "Sim" if loja["vendas"]>0 else "Não",
            "North Star": "Sim" if loja["vendas"]>=5 else "Não",
        }]).T.reset_index().rename(columns={"index":"Etapa",0:"Status"}).to_excel(writer, sheet_name="Checklist", index=False)
        pd.DataFrame([{
            "Assunto": gargalo_info["email_assunto"],
            "Corpo": gargalo_info["email_corpo"].format(nome=loja["nome"]),
        }]).to_excel(writer, sheet_name="E-mail disparado", index=False)
    return output.getvalue()

def gerar_excel_queda(loja_sel, d, diag):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        queda_gmv = round((d["gmv"][-1]-d["gmv"][0])/d["gmv"][0]*100,1)
        pd.DataFrame([{
            "Loja": loja_sel, "Perfil": d["perfil"],
            "Variação GMV": f"{queda_gmv}%",
            "Causa": diag["causa"], "Vetor": diag["vetor"],
            "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        }]).T.reset_index().rename(columns={"index":"Campo",0:"Valor"}).to_excel(writer, sheet_name="Resumo", index=False)
        pd.DataFrame({
            "Mês": d["meses"], "Pedidos": d["pedidos"],
            "Ticket (R$)": d["ticket"], "GMV (R$)": d["gmv"],
            "Novos": d["novos"], "Recorrentes": d["recorrentes"],
        }).to_excel(writer, sheet_name="Evolução", index=False)
        pd.DataFrame([{"Prazo":p,"Ação":a} for p,a in diag["acoes"]]).to_excel(writer, sheet_name="Ações", index=False)
        pd.DataFrame(d["top_clientes"]).to_excel(writer, sheet_name="Clientes churned", index=False)
    return output.getvalue()

# ── SIDEBAR ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 1.5rem'>
        <div style='font-size:11px;color:#9DBDBB;text-transform:uppercase;letter-spacing:.1em;margin-bottom:4px'>Loja Integrada</div>
        <div style='font-size:22px;font-weight:700;color:#D4F53C;line-height:1.1'>LI Pulse</div>
        <div style='font-size:12px;color:#9DBDBB;margin-top:4px'>Automação de Onboarding</div>
    </div>
    """, unsafe_allow_html=True)

    pagina = st.radio("", [
        "📊 O problema — funil",
        "🔍 Quem travou e onde",
        "⚙️ Pipeline rodando",
        "📉 Diagnóstico de queda",
    ], label_visibility="collapsed")

    modo_label = "Dados reais" if MODO_REAL else "Dados simulados"
    modo_cor   = "#D4F53C" if MODO_REAL else "#F59E0B"
    st.markdown(f"""
    <div style='margin-top:2rem;padding-top:1rem;border-top:1px solid #1A6A64'>
        <div style='font-size:11px;color:{modo_cor};font-weight:600'>● {modo_label}</div>
        <div style='font-size:11px;color:#5A9A96;margin-top:2px'>Time de Automação · 2025</div>
    </div>
    """, unsafe_allow_html=True)

# ── TELA 1: O PROBLEMA ────────────────────────────────────────────────────────

if pagina == "📊 O problema — funil":

    st.markdown("<h1 style='color:#1A2E2B;font-size:28px;font-weight:700;margin-bottom:4px'>O problema</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#5A7A78;margin-bottom:1.5rem'>94% dos novos lojistas não chegam à primeira venda. Aqui está onde cada um trava.</p>", unsafe_allow_html=True)

    # Seletor de período dinâmico
    hoje = date.today()
    c1,c2,c3 = st.columns(3)
    with c1:
        meses_opcoes = {
            "Últimos 30 dias":  (hoje - relativedelta(days=30), hoje),
            "Últimos 60 dias":  (hoje - relativedelta(days=60), hoje),
            "Últimos 90 dias":  (hoje - relativedelta(days=90), hoje),
            "Jan 2025":  (date(2025,1,1), date(2025,1,31)),
            "Fev 2025":  (date(2025,2,1), date(2025,2,28)),
            "Mar 2025":  (date(2025,3,1), date(2025,3,31)),
        }
        periodo_sel = st.selectbox("Período", list(meses_opcoes.keys()))
        data_inicio, data_fim = meses_opcoes[periodo_sel]
        data_inicio_str = data_inicio.strftime("%Y-%m-%d")
        data_fim_str    = data_fim.strftime("%Y-%m-%d")
    with c2: origem_sel = st.selectbox("Origem", ["Todas","Orgânico","Pago","Indicação"])
    with c3: plano_sel  = st.selectbox("Plano", ["Todos","Grátis","Pago"])

    # Carrega dados reais ou simulados
    if MODO_REAL:
        try:
            with st.spinner("Carregando dados do banco..."):
                df_funil = mb.buscar_funil(data_inicio_str, data_fim_str)

            # Aplica filtros de origem e plano
            if origem_sel != "Todas":
                df_funil = df_funil[df_funil["flag_origem"] == origem_sel.upper()]
            if plano_sel != "Todos":
                df_funil = df_funil[df_funil["flag_plano"] == plano_sel.upper()]

            # Agrega os totais do funil
            def sg(col): return int(df_funil[col].sum()) if col in df_funil.columns else 0
            total = sg("qtde_loja_criada")
            cfg   = sg("qtde_loja_config")
            visita= sg("qtde_loja_primeira_visita")
            venda = sg("qtde_loja_primeira_venda_aprovada")
            ns    = int(venda * 0.5)  # aproximação: 50% de quem vendeu chegou a 5 pedidos
            def sc(v): return max(1, int(v))
        except Exception as e:
            st.warning(f"⚠️ Erro ao carregar dados reais: {e}. Usando dados simulados.")
            MODO_REAL_LOCAL = False
            d = BASE[list(BASE.keys())[0]]
            def sc(v): return max(1,int(v))
            total=sc(d["total"]); cfg=sc(d["cfg"]); visita=sc(d["visita"])
            venda=sc(d["venda_apr"]); ns=sc(d["north_star"])
    else:
        # Fallback simulado — filtra pelo período mais próximo disponível
        safra_map = {
            "Últimos 30 dias": "Mar 2025", "Últimos 60 dias": "Fev 2025",
            "Últimos 90 dias": "Jan 2025", "Jan 2025": "Jan 2025",
            "Fev 2025": "Fev 2025", "Mar 2025": "Mar 2025",
        }
        d = BASE[safra_map.get(periodo_sel, "Mar 2025")]
        mult = 1.0
        if origem_sel != "Todas": mult *= d["origem"].get(origem_sel,0)/d["total"]
        if plano_sel == "Grátis":  mult *= 0.62
        if plano_sel == "Pago":    mult *= 0.38
        def sc(v): return max(1,int(v*mult))
        total=sc(d["total"]); cfg=sc(d["cfg"]); visita=sc(d["visita"])
        venda=sc(d["venda_apr"]); ns=sc(d["north_star"])

    st.markdown(f"""
    <div class="ns-box">
        <div class="ns-label">⭐ North Star 2026 — % novos lojistas com 5 pedidos em 15 dias</div>
        <div class="ns-value">{pct(ns,total)}%</div>
        <div class="ns-desc">{ns:,} lojas de {total:,} atingiram o marco · Retenção 4× maior para quem chega aqui</div>
    </div>""", unsafe_allow_html=True)

    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Lojas criadas", f"{total:,}")
    m2.metric("Config. completa", f"{cfg:,}", f"{pct(cfg,total)}%")
    m3.metric("1ª visita", f"{visita:,}", f"{pct(visita,total)}%")
    m4.metric("1ª venda aprovada", f"{venda:,}", f"{pct(venda,total)}%")

    st.divider()
    st.markdown("<h3 style='color:#1A2E2B'>Onde os lojistas travam</h3>", unsafe_allow_html=True)

    steps = [
        ("Passo 1 — nome + segmento",  sc(d["p1"]),       "#22C55E"),
        ("Passo 2 — tipo de pessoa",    sc(d["p2"]),       "#22C55E"),
        ("Passo 3 — CEP",               sc(d["p3"]),       "#1ABCB0"),
        ("Passo 5 — endereço completo", sc(d["p5"]),       "#1ABCB0"),
        ("Produto cadastrado",          sc(d["cfg_prod"]), "#F59E0B"),
        ("Pagamento configurado",       sc(d["cfg_pag"]),  "#E24B4A"),
        ("Frete configurado",           sc(d["cfg_env"]),  "#E24B4A"),
        ("Config. completa",            cfg,               "#0D4F4A"),
        ("1ª visita válida",            visita,            "#1ABCB0"),
        ("1ª venda captada",            sc(d["venda_cap"]),"#0D4F4A"),
        ("1ª venda aprovada",           venda,             "#0D2B1A"),
    ]

    for label,val,cor in steps:
        p = pct(val,total)
        cl,cb,cp,cn = st.columns([2.2,4,0.7,0.9])
        cl.markdown(f"<div style='font-size:13px;padding-top:6px;color:#1A2E2B'>{label}</div>", unsafe_allow_html=True)
        cb.markdown(f"<div style='background:#E8E4DE;border-radius:6px;height:10px;margin-top:10px'><div style='background:{cor};width:{p}%;height:100%;border-radius:6px'></div></div>", unsafe_allow_html=True)
        cp.markdown(f"<div style='font-size:13px;font-weight:700;padding-top:4px;text-align:right;color:#1A2E2B'>{p}%</div>", unsafe_allow_html=True)
        cn.markdown(f"<div style='font-size:12px;color:#5A7A78;padding-top:6px;text-align:right'>{val:,}</div>", unsafe_allow_html=True)

    st.divider()
    col_g,col_s = st.columns(2)

    with col_g:
        st.markdown("<h3 style='color:#1A2E2B'>Maiores gargalos</h3>", unsafe_allow_html=True)
        drop_pag = sc(d["cfg_prod"])-sc(d["cfg_pag"])
        drop_env = sc(d["cfg_pag"])-sc(d["cfg_env"])
        drop_vis = cfg-visita
        for css,titulo,desc in [
            ("gargalo-critico",f"{pct(drop_pag,total)}% travaram sem pagamento","Cadastraram produto mas não ativaram pagamento."),
            ("gargalo-critico",f"{pct(drop_env,total)}% travaram sem frete","Ativaram pagamento mas não configuraram frete."),
            ("gargalo-atencao",f"{pct(drop_vis,total)}% sem visitas após config","Config completa mas sem visitantes."),
        ]:
            st.markdown(f'<div class="gargalo-box {css}"><div class="gargalo-titulo">{titulo}</div><div class="gargalo-desc">{desc}</div></div>', unsafe_allow_html=True)

    with col_s:
        st.markdown("<h3 style='color:#1A2E2B'>Por segmento</h3>", unsafe_allow_html=True)
        rows=[]
        for sg in d["seg"]:
            ca=sc(sg["c"]); va=sc(sg["v"]); conv=pct(va,ca)
            if conv>=10:   diag,badge="Acima da média","badge-star"
            elif conv>=6:  diag,badge="Na média","badge-ok"
            elif conv>=3:  diag,badge="Abaixo","badge-atencao"
            else:          diag,badge="Crítico","badge-critico"
            rows.append({"Segmento":sg["n"],"Lojas":ca,"Conv.":f"{conv}%","Dias":f"{sg['t']:.1f}d","Status":f'<span class="{badge}">{diag}</span>'})
        st.write(pd.DataFrame(rows).to_html(escape=False,index=False), unsafe_allow_html=True)

# ── TELA 2: QUEM TRAVOU ───────────────────────────────────────────────────────

elif pagina == "🔍 Quem travou e onde":

    st.markdown("<h1 style='color:#1A2E2B;font-size:28px;font-weight:700;margin-bottom:4px'>Quem travou e onde</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#5A7A78;margin-bottom:1.5rem'>Cada lojista, o gargalo exato, por que travou e o que a automação já fez.</p>", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    with c1: busca = st.text_input("Buscar por ID ou nome", placeholder="Ex: LI-00421 ou Moda da Ana")
    with c2: filtro_grav = st.selectbox("Gravidade", ["Todas","Crítico","Atenção","North Star"])
    with c3: filtro_seg = st.selectbox("Segmento", ["Todos"] + list(set(l["seg"] for l in LOJISTAS)))

    lista = LOJISTAS
    if busca.strip():
        t = busca.strip().lower()
        lista = [l for l in lista if t in l["id"].lower() or t in l["nome"].lower()]
    if filtro_grav != "Todas":
        lista = [l for l in lista if l["gravidade"] == filtro_grav]
    if filtro_seg != "Todos":
        lista = [l for l in lista if l["seg"] == filtro_seg]

    criticos = len([l for l in LOJISTAS if l["gravidade"]=="Crítico"])
    atencao  = len([l for l in LOJISTAS if l["gravidade"]=="Atenção"])
    ns_ok    = len([l for l in LOJISTAS if l["gravidade"]=="North Star"])

    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Total monitorados", len(LOJISTAS))
    m2.metric("🔴 Críticos", criticos, "intervenção urgente")
    m3.metric("🟡 Atenção", atencao, "acompanhamento")
    m4.metric("⭐ North Star", ns_ok, "marco atingido")

    st.divider()
    st.markdown(f"<p style='color:#5A7A78;font-size:13px'><strong>{len(lista)}</strong> lojista(s) encontrado(s)</p>", unsafe_allow_html=True)

    if not lista:
        st.info("Nenhum lojista encontrado com os filtros selecionados.")
    else:
        for loja in lista:
            g = GARGALOS[loja["gargalo"]]
            s = score_loja(loja)
            cor_score = "#E24B4A" if s<40 else "#F59E0B" if s<70 else "#1ABCB0"
            icone = "🔴" if loja["gravidade"]=="Crítico" else "🟡" if loja["gravidade"]=="Atenção" else "⭐"

            with st.expander(f"**{loja['nome']}** ({loja['id']}) · {loja['seg']} · {loja['dias']} dias · {icone} {loja['gravidade']}"):
                col_a,col_b,col_c = st.columns([1,1,1])

                with col_a:
                    st.markdown("**Onde travou**")
                    css = "gargalo-critico" if loja["gravidade"]=="Crítico" else "gargalo-atencao" if loja["gravidade"]=="Atenção" else "gargalo-ok"
                    st.markdown(f'<div class="gargalo-box {css}"><div class="gargalo-titulo">{g["onde"]}</div><div class="gargalo-desc">{g["por_que"]}</div></div>', unsafe_allow_html=True)

                with col_b:
                    st.markdown("**Score de prontidão**")
                    st.markdown(f"""<div style='text-align:center;background:#FFFFFF;border-radius:12px;padding:1rem;border:2px solid {cor_score}'>
                        <div style='font-size:40px;font-weight:700;color:{cor_score}'>{s}</div>
                        <div style='font-size:12px;color:#5A7A78'>de 100</div>
                    </div>""", unsafe_allow_html=True)
                    for label,ok in [("Produto",loja["cfg_prod"]),("Pagamento",loja["cfg_pag"]),("Frete",loja["cfg_env"]),("1ª visita",loja["visita"]),("1ª venda",1 if loja["vendas"]>0 else 0),("North Star",1 if loja["vendas"]>=5 else 0)]:
                        icone_c = "✅" if ok else "❌"
                        st.markdown(f"<div style='font-size:12px;padding:2px 0;color:#1A2E2B'>{icone_c} {label}</div>", unsafe_allow_html=True)

                with col_c:
                    st.markdown("**O que a automação fez**")
                    st.markdown(f"""<div style='background:#D1FAF6;border:1px solid #1ABCB0;border-radius:12px;padding:1rem;font-size:13px;color:#0D4F4A;line-height:1.6'>
                        <strong>E-mail disparado automaticamente</strong><br>{g['proximo']}
                    </div>""", unsafe_allow_html=True)

                st.divider()
                with st.expander("📧 Ver e-mail disparado pela automação"):
                    st.markdown(f"""<div class="email-preview">
                        <div class="email-header"><strong>Para:</strong> lojista@email.com &nbsp;·&nbsp; <strong>Assunto:</strong> {g['email_assunto']}</div>
                        {g['email_corpo'].format(nome=loja['nome']).replace(chr(10),'<br>')}
                    </div>""", unsafe_allow_html=True)

                excel = gerar_excel_lojista(loja, s, g)
                st.download_button(f"⬇️ Baixar relatório — {loja['nome']}", data=excel,
                    file_name=f"diagnostico_{loja['id'].replace('-','_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"dl_{loja['id']}")

# ── TELA 3: PIPELINE ──────────────────────────────────────────────────────────

elif pagina == "⚙️ Pipeline rodando":

    st.markdown("<h1 style='color:#1A2E2B;font-size:28px;font-weight:700;margin-bottom:4px'>Pipeline rodando</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#5A7A78;margin-bottom:1.5rem'>O que aconteceu hoje às 8h — automaticamente, sem intervenção humana.</p>", unsafe_allow_html=True)

    agora = datetime.now()
    hora_run = agora.replace(hour=8, minute=0, second=0)

    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Última execução", hora_run.strftime("%d/%m %H:%M"))
    m2.metric("Lojistas analisados", "3.947")
    m3.metric("Intervenções disparadas", "847")
    m4.metric("Taxa de desbloqueio", "12%", "+2.1pp vs mês anterior")

    st.divider()
    st.markdown("<h3 style='color:#1A2E2B'>O que rodou hoje</h3>", unsafe_allow_html=True)

    steps_pipe = [
        ("#1ABCB0","#0D4F4A","08:00","Query executada","Banco consultado — 3.947 lojistas da safra atual analisados."),
        ("#1ABCB0","#0D4F4A","08:01","Gargalos classificados","Engine Python identificou: 412 sem pagamento · 218 sem frete · 89 sem visita · 128 sem conversão."),
        ("#D4F53C","#0D4F4A","08:02","Filtro anti-spam aplicado","Lojistas com contato nos últimos 3 dias foram excluídos do disparo."),
        ("#D4F53C","#0D4F4A","08:03","847 e-mails disparados via HubSpot","Cada lojista recebeu a mensagem específica para seu gargalo."),
        ("#0D4F4A","#D4F53C","08:04","Log registrado","Tudo persistido: quem recebeu, qual mensagem, qual gargalo."),
        ("#0D4F4A","#D4F53C","08:05","Pipeline concluído","Próxima execução: amanhã às 08:00."),
    ]

    for cor,tcor,hora,titulo,desc in steps_pipe:
        st.markdown(f"""<div class="pipeline-step">
            <div class="step-icon" style="background:{cor};color:{tcor}">✓</div>
            <div>
                <div class="step-title">{titulo}</div>
                <div class="step-desc">{desc}</div>
                <div class="step-time">Hoje às {hora}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    col1,col2 = st.columns(2)
    with col1:
        st.markdown("<h3 style='color:#1A2E2B'>Intervenções por gargalo</h3>", unsafe_allow_html=True)
        df_pipe = pd.DataFrame([
            {"Gargalo":"Sem pagamento","Lojistas":412,"E-mails":398,"Abertura":"41%","Desbloqueados":52},
            {"Gargalo":"Sem frete","Lojistas":218,"E-mails":204,"Abertura":"38%","Desbloqueados":29},
            {"Gargalo":"Sem visita","Lojistas":89,"E-mails":89,"Abertura":"35%","Desbloqueados":11},
            {"Gargalo":"Sem conversão","Lojistas":128,"E-mails":156,"Abertura":"29%","Desbloqueados":9},
        ])
        st.dataframe(df_pipe, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("<h3 style='color:#1A2E2B'>Impacto acumulado (30 dias)</h3>", unsafe_allow_html=True)
        m1,m2 = st.columns(2)
        m1.metric("Lojistas desbloqueados", "1.247", "+12% vs mês anterior")
        m2.metric("Contribuição North Star", "+2.1pp", "de 4.8% para 6.9%")
        st.markdown(f"""<div style='background:#0D4F4A;border-radius:12px;padding:1rem;font-size:13px;color:#9DCFCC;margin-top:1rem;line-height:1.6'>
            <span style='color:#D4F53C;font-weight:600'>Projeção:</span> Mantendo esse ritmo, a taxa de conversão sobe de 4,8% para ~8,2% em 90 dias — impacto direto na North Star de 2026.
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("<h3 style='color:#1A2E2B'>Stack técnica</h3>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    for col,icone,titulo,desc in [
        (c1,"🗄️","SQL + Metabase","Query puxa lojistas travados do banco"),
        (c2,"🐍","Python","Engine classifica gargalo e monta payload"),
        (c3,"📧","HubSpot API","Dispara e-mail personalizado por gargalo"),
        (c4,"⏰","Airflow","Agenda e orquestra o pipeline todo dia às 8h"),
    ]:
        col.markdown(f"""<div style='background:#FFFFFF;border-radius:12px;padding:1rem;text-align:center'>
            <div style='font-size:24px;margin-bottom:6px'>{icone}</div>
            <div style='font-size:13px;font-weight:600;color:#1A2E2B'>{titulo}</div>
            <div style='font-size:12px;color:#5A7A78;margin-top:4px'>{desc}</div>
        </div>""", unsafe_allow_html=True)

# ── TELA 4: DIAGNÓSTICO DE QUEDA ──────────────────────────────────────────────

elif pagina == "📉 Diagnóstico de queda":

    st.markdown("<h1 style='color:#1A2E2B;font-size:28px;font-weight:700;margin-bottom:4px'>Diagnóstico de queda em vendas</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#5A7A78;margin-bottom:1.5rem'>Fecha o ciclo — identifica a causa raiz quando um lojista que já vendia começa a cair.</p>", unsafe_allow_html=True)

    hoje_q = date.today()
    col_sel1, col_sel2 = st.columns([3,1])

    with col_sel1:
        if MODO_REAL:
            try:
                with st.spinner("Carregando top lojas..."):
                    df_top = mb.buscar_top_lojas(50)
                opcoes_reais = {
                    f"{row['nome_loja']} (ID: {row['conta_id']}) · GMV R${float(row['gmv_6m']):,.0f}": int(row['conta_id'])
                    for _, row in df_top.iterrows()
                }
                opcao_manual = "[ Digitar ID manualmente ]"
                lista_opcoes = [opcao_manual] + list(opcoes_reais.keys())
                sel_loja = st.selectbox("Selecione uma loja ou digite o ID", lista_opcoes)

                if sel_loja == opcao_manual:
                    conta_id_input = st.text_input("ID da conta (conta_id)", placeholder="Ex: 123456")
                    conta_id = int(conta_id_input) if conta_id_input.strip().isdigit() else None
                else:
                    conta_id = opcoes_reais[sel_loja]
                    st.markdown(f"<p style='font-size:12px;color:#1ABCB0'>conta_id: <strong>{conta_id}</strong></p>", unsafe_allow_html=True)

            except Exception as e:
                st.warning(f"Erro ao carregar lista: {e}")
                conta_id_input = st.text_input("ID da conta (conta_id)", placeholder="Ex: 123456")
                conta_id = int(conta_id_input) if conta_id_input.strip().isdigit() else None
        else:
            conta_id = None
            nomes = list(LOJAS_ATIVAS.keys())
            sel_loja = st.selectbox("Selecione uma loja (dados simulados)", nomes)

    with col_sel2:
        meses_queda = {
            "Últimos 6 meses": (hoje_q - relativedelta(months=6), hoje_q),
            "Últimos 3 meses": (hoje_q - relativedelta(months=3), hoje_q),
            "2025 completo":   (date(2025,1,1), date(2025,12,31)),
            "Out/24–Mar/25":   (date(2024,10,1), date(2025,3,31)),
        }
        periodo_queda = st.selectbox("Período", list(meses_queda.keys()), key="pq")
        dq_inicio, dq_fim = meses_queda[periodo_queda]
        dq_inicio_str = dq_inicio.strftime("%Y-%m-%d")
        dq_fim_str    = dq_fim.strftime("%Y-%m-%d")
        # Referência para churn: primeiro terço do período
        ref_fim_dt    = dq_inicio + (dq_fim - dq_inicio) / 3
        ref_inicio_str = dq_inicio_str
        ref_fim_str    = ref_fim_dt.strftime("%Y-%m-%d")
        corte_str      = (dq_inicio + (dq_fim - dq_inicio) * 2 / 3).strftime("%Y-%m-%d")

    # Carrega dados da loja selecionada
    if MODO_REAL and conta_id:
        try:
            with st.spinner("Carregando diagnóstico..."):
                df_tend  = mb.buscar_tendencia(conta_id, dq_inicio_str, dq_fim_str)
                df_nr    = mb.buscar_novos_recorrentes(conta_id, dq_inicio_str, dq_fim_str)
                df_pag   = mb.buscar_mix_pagamento(conta_id, dq_inicio_str, dq_fim_str)
                df_churn = mb.buscar_clientes_churned(conta_id, ref_inicio_str, ref_fim_str, corte_str)

            # Monta estrutura compatível com o restante da tela
            meses_r      = df_tend["mes"].tolist()
            pedidos_r    = [int(v) for v in df_tend["total_pedidos"].tolist()]
            ticket_r     = [float(v) for v in df_tend["ticket_medio"].tolist()]
            gmv_r        = [float(v) for v in df_tend["receita_total"].tolist()]
            novos_r      = df_nr[df_nr["tipo_cliente"]=="Novo"]["total_pedidos"].tolist() if not df_nr.empty else [0]*len(meses_r)
            rec_r        = df_nr[df_nr["tipo_cliente"]=="Recorrente"]["total_pedidos"].tolist() if not df_nr.empty else [0]*len(meses_r)
            pix_r        = df_pag[df_pag["forma_pagamento"].str.contains("Pix|pix",na=False)]["total_pedidos"].tolist() if not df_pag.empty else [0]*len(meses_r)
            cartao_r     = df_pag[df_pag["forma_pagamento"].str.contains("Cartão|cartao|Crédito|credito",na=False)]["total_pedidos"].tolist() if not df_pag.empty else [0]*len(meses_r)
            externo_r    = df_pag[df_pag["forma_pagamento"].str.contains("Externo|externo|Manual|manual",na=False)]["total_pedidos"].tolist() if not df_pag.empty else [0]*len(meses_r)

            top_clientes_r = [
                dict(nome=row["cliente_nome"], emails=row["cliente_email"],
                     receita=float(row["receita_total_historico"]), pedidos=int(row["total_pedidos_historico"]))
                for _, row in df_churn.head(3).iterrows()
            ] if not df_churn.empty else []

            # Detecta causa automaticamente
            if len(gmv_r) >= 2:
                queda_g = (gmv_r[-1]-gmv_r[0])/gmv_r[0]*100 if gmv_r[0] else 0
                queda_t = (ticket_r[-1]-ticket_r[0])/ticket_r[0]*100 if ticket_r[0] else 0
                n_b2b_auto = sum(1 for c in detectar_b2b(top_clientes_r) if c["perfil_b2b"])
                if n_b2b_auto >= 1 and queda_g < -20: causa_auto = "churn_b2b"
                elif queda_t < -15 and abs(queda_g) < 20: causa_auto = "mix_pagamento"
                else: causa_auto = "colapso_canal"
            else:
                causa_auto = "colapso_canal"

            d = dict(
                causa=causa_auto, perfil=f"ID {conta_id}",
                meses=meses_r, pedidos=pedidos_r, ticket=ticket_r, gmv=gmv_r,
                pix=pix_r, cartao=cartao_r, externo=externo_r,
                novos=novos_r, recorrentes=rec_r, cupom_pct=[0]*len(meses_r),
                top_clientes=top_clientes_r,
            )
        except Exception as e:
            st.error(f"Erro ao carregar dados da loja: {e}")
            st.stop()
    else:
        # Fallback simulado
        d = LOJAS_ATIVAS[sel_loja if not MODO_REAL else list(LOJAS_ATIVAS.keys())[0]]

    diag = DIAGNOSTICOS_QUEDA[d["causa"]]
    score_churn, nivel_churn, cor_churn, razoes_churn, clientes_b2b = calcular_score_churn(d)
    n_b2b = sum(1 for c in clientes_b2b if c["perfil_b2b"])

    queda_pedidos = round((d["pedidos"][-1]-d["pedidos"][0])/d["pedidos"][0]*100,1)
    queda_ticket  = round((d["ticket"][-1] -d["ticket"][0]) /d["ticket"][0] *100,1)
    queda_gmv     = round((d["gmv"][-1]    -d["gmv"][0])    /d["gmv"][0]    *100,1)

    col_h,col_s1,col_s2 = st.columns([2.5,1,1])
    with col_h:
        st.markdown(f"<h2 style='color:#1A2E2B'>{loja_sel.split('(')[0].strip()}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#5A7A78'><strong>Perfil:</strong> {d['perfil']} &nbsp;·&nbsp; <strong>Período:</strong> {d['meses'][0]}/24 – {d['meses'][-1]}/25</p>", unsafe_allow_html=True)
    with col_s1:
        st.markdown(f"""<div style='text-align:center;background:#FEF2F2;border-radius:12px;padding:1rem;border:2px solid #E24B4A'>
            <div style='font-size:12px;color:#5A7A78;margin-bottom:4px'>Queda de GMV</div>
            <div style='font-size:28px;font-weight:700;color:#E24B4A'>{queda_gmv}%</div>
        </div>""", unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""<div style='text-align:center;background:#FFFFFF;border-radius:12px;padding:1rem;border:2px solid {cor_churn}'>
            <div style='font-size:12px;color:#5A7A78;margin-bottom:4px'>Score de risco</div>
            <div style='font-size:28px;font-weight:700;color:{cor_churn}'>{score_churn}</div>
            <div style='font-size:11px;color:{cor_churn};font-weight:600'>{nivel_churn}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    col_score, col_b2b = st.columns(2)
    with col_score:
        st.markdown("<h3 style='color:#1A2E2B'>Por que esse score</h3>", unsafe_allow_html=True)
        for razao, peso, nivel in razoes_churn:
            cor_r = "#E24B4A" if nivel=="critico" else "#F59E0B" if nivel=="alto" else "#1ABCB0" if nivel=="medio" else "#22C55E"
            bg_r  = "#FEF2F2" if nivel=="critico" else "#FFFBEB" if nivel=="alto" else "#D1FAF6" if nivel=="medio" else "#F0FDF4"
            st.markdown(f"""<div style='background:{bg_r};border-left:3px solid {cor_r};border-radius:8px;padding:8px 12px;margin-bottom:6px;display:flex;justify-content:space-between'>
                <span style='font-size:13px;color:#1A2E2B'>{razao}</span>
                <span style='font-size:12px;font-weight:600;color:{cor_r}'>+{peso}pts</span>
            </div>""", unsafe_allow_html=True)

    with col_b2b:
        st.markdown("<h3 style='color:#1A2E2B'>Detecção automática de B2B</h3>", unsafe_allow_html=True)
        if n_b2b > 0:
            st.markdown(f"""<div style='background:#FEF2F2;border:1px solid #FCA5A5;border-radius:10px;padding:1rem;margin-bottom:12px'>
                <div style='font-size:13px;font-weight:600;color:#991B1B;margin-bottom:4px'>⚠️ {n_b2b} cliente(s) B2B identificado(s)</div>
                <div style='font-size:12px;color:#7F1D1D;line-height:1.5'>Contato direto via WhatsApp é mais eficaz que e-mail marketing</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div style='background:#D1FAF6;border:1px solid #1ABCB0;border-radius:10px;padding:1rem;margin-bottom:12px'>
                <div style='font-size:13px;font-weight:600;color:#0D4F4A;margin-bottom:4px'>✓ Perfil consumidor final</div>
                <div style='font-size:12px;color:#0D4F4A;line-height:1.5'>Foco em experiência pós-compra e frete</div>
            </div>""", unsafe_allow_html=True)
        for c in clientes_b2b:
            badge_style = "background:#FEE2E2;color:#991B1B" if c["perfil_b2b"] else "background:#D1FAF6;color:#0D4F4A"
            badge_label = "B2B" if c["perfil_b2b"] else "Consumidor"
            st.markdown(f"""<div style='font-size:12px;padding:6px 0;border-bottom:1px solid #E8E4DE'>
                <div style='display:flex;justify-content:space-between;align-items:center'>
                    <div><strong style='color:#1A2E2B'>{c['nome']}</strong><br><span style='color:#5A7A78'>{c['emails']}</span></div>
                    <span style='font-size:11px;padding:2px 8px;border-radius:20px;{badge_style}'>{badge_label}</span>
                </div>
            </div>""", unsafe_allow_html=True)

    st.divider()
    m1,m2,m3 = st.columns(3)
    m1.metric("Pedidos", f"{d['pedidos'][0]} → {d['pedidos'][-1]}", f"{queda_pedidos}%")
    m2.metric("Ticket médio", f"R${d['ticket'][0]} → R${d['ticket'][-1]}", f"{queda_ticket}%")
    m3.metric("GMV", f"R${d['gmv'][0]:,} → R${d['gmv'][-1]:,}", f"{queda_gmv}%")

    col_g1,col_g2 = st.columns(2)
    with col_g1:
        st.markdown("**Volume de pedidos**")
        st.line_chart(pd.DataFrame({"Pedidos":d["pedidos"]},index=d["meses"]))
    with col_g2:
        st.markdown("**Ticket médio (R$)**")
        st.line_chart(pd.DataFrame({"Ticket":d["ticket"]},index=d["meses"]))

    st.divider()
    col_nr,col_pag = st.columns(2)
    with col_nr:
        st.markdown("**Novos vs recorrentes**")
        st.line_chart(pd.DataFrame({"Novos":d["novos"],"Recorrentes":d["recorrentes"]},index=d["meses"]))
    with col_pag:
        st.markdown("**Mix de pagamento (%)**")
        st.area_chart(pd.DataFrame({"Pix":d["pix"],"Cartão":d["cartao"],"Externo":d["externo"]},index=d["meses"]))

    st.divider()
    st.markdown("<h3 style='color:#1A2E2B'>Diagnóstico final</h3>", unsafe_allow_html=True)
    st.markdown(f"""<div style='background:#0D4F4A;border-radius:14px;padding:1.5rem;margin-bottom:1rem'>
        <div style='font-size:11px;color:#1ABCB0;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px'>Causa principal</div>
        <div style='font-size:20px;font-weight:700;color:#D4F53C;margin-bottom:6px'>{diag["causa"]}</div>
        <div style='font-size:13px;color:#9DCFCC;margin-bottom:12px'>{diag["vetor"]}</div>
        <div style='font-size:13px;color:#C8E8E6;line-height:1.6;border-top:1px solid #1A6A64;padding-top:12px'>{diag["origem"]}</div>
    </div>""", unsafe_allow_html=True)

    cores = {
        "Imediata":    ("#E24B4A","#FEF2F2","#FCA5A5"),
        "Curto prazo": ("#F59E0B","#FFFBEB","#FDE68A"),
        "Médio prazo": ("#1ABCB0","#D1FAF6","#99F6E4"),
    }
    for prazo,acao in diag["acoes"]:
        ct,cb,cbd = cores[prazo]
        st.markdown(f"""<div style='background:{cb};border:1px solid {cbd};border-left:4px solid {ct};border-radius:10px;padding:.8rem 1rem;margin-bottom:8px'>
            <span style='font-size:11px;color:{ct};font-weight:700;text-transform:uppercase;letter-spacing:.05em'>{prazo}</span>
            <div style='font-size:13px;color:#1A2E2B;margin-top:4px'>{acao}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown(f"""<div style='background:#D1FAF6;border:1px solid #1ABCB0;border-radius:12px;padding:1rem 1.2rem;font-size:13px;color:#0D4F4A;margin-bottom:1rem'>
        <strong>Conexão com o diagnóstico de entrada:</strong> a automação garante que novos lojistas cheguem à primeira venda.
        Este diagnóstico garante que quem já vende continue crescendo. Juntos, cobrem o ciclo completo do lojista.
    </div>""", unsafe_allow_html=True)

    excel_q = gerar_excel_queda(loja_sel, d, diag)
    st.download_button("⬇️ Baixar relatório em Excel", data=excel_q,
        file_name=f"diagnostico_queda_{loja_sel.split('(')[1].replace(')','').replace('-','_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
