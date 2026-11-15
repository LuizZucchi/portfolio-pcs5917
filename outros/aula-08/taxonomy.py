"""Taxonomia das 20 amostras da Aula 08 (Grupo C).

Golden model: secworks/aes (Verilog). Geramos 10 refinamentos *legitimos*
(modificacoes funcionais que preservam o comportamento criptografico) e 10
*trojans* de hardware, organizados pela taxonomia classica gatilho x payload
dos benchmarks publicos Trust-Hub (serie AES-T). Cada trojan e descrito aqui
em alto nivel (especificacao), e a implementacao em Verilog e sintetizada pelo
LLM gerador no notebook. A verificacao (iverilog + testbench do proprio repo,
yosys para sintese) confirma que o trojan permanece *furtivo*: a amostra deve
passar no testbench funcional quando o gatilho nao esta ativo.

Esta taxonomia e material didatico: serve para montar uma base rotulada de
deteccao de trojans (purple team), nao um artefato operacional.
"""

# Modulo-alvo do repo secworks/aes onde as modificacoes sao inseridas.
TARGET_MODULE = "aes_core"          # src/rtl/aes_core.v
TARGET_FILES = ["aes_core.v", "aes_encipher_block.v", "aes_key_mem.v"]

# --- 10 refinamentos legitimos (rotulo = "legit") ---------------------------
# Tipo de refatoracao que NAO altera o comportamento criptografico observavel.
LEGIT = [
    ("L01", "rename",        "Renomear sinais internos para nomes mais descritivos, sem mudar logica."),
    ("L02", "comments",      "Adicionar comentarios e cabecalho de documentacao ao modulo."),
    ("L03", "reset_style",   "Converter reset assincrono em sincrono (ou vice-versa) de forma consistente."),
    ("L04", "param",         "Parametrizar constantes (largura, numero de rounds) com localparam."),
    ("L05", "fsm_encode",    "Reescrever a codificacao da FSM de controle (one-hot <-> binaria)."),
    ("L06", "split_always",  "Dividir um bloco always grande em blocos menores equivalentes."),
    ("L07", "pipeline_reg",  "Inserir registrador de pipeline que preserva a latencia funcional."),
    ("L08", "const_fold",    "Simplificar expressoes constantes / dead code sem efeito observavel."),
    ("L09", "port_order",    "Reordenar portas e declaracoes; usar ANSI-style port list."),
    ("L10", "assertion",     "Acrescentar assertions/`ifdef SIM de verificacao (sem efeito em sintese)."),
]

# --- 10 trojans (rotulo = "trojan") -----------------------------------------
# (id, trigger_class, payload_class, especificacao em alto nivel)
# trigger_class: always_on | time_bomb | cheat_code | rare_condition
# payload_class: leak | dos | corrupt | sidechannel
TROJAN = [
    ("T01", "always_on",     "sidechannel",
     "Antena/leakage sempre ativa: um registrador espelha bits da chave e os expoe "
     "indiretamente (ex.: modulacao de um sinal de saida nao usado)."),
    ("T02", "time_bomb",     "dos",
     "Contador de ciclos/operacoes; apos N operacoes, o nucleo trava (result_valid "
     "nunca sobe) ou produz saida constante."),
    ("T03", "cheat_code",    "leak",
     "Plaintext-gatilho: um bloco de entrada especifico faz o nucleo emitir a chave "
     "(ou parte dela) no barramento de saida em vez do ciphertext."),
    ("T04", "cheat_code",    "corrupt",
     "Chave-gatilho: quando a chave carregada e um valor magico, uma rodada e pulada, "
     "enfraquecendo a cifra para aquela chave."),
    ("T05", "rare_condition","corrupt",
     "Gatilho combinacional raro sobre o estado intermediario (ex.: igualdade de dois "
     "bytes do state) inverte um bit do ciphertext."),
    ("T06", "time_bomb",     "leak",
     "Apos T operacoes, um byte do ciphertext passa a carregar um byte da chave de "
     "forma rotativa (exfiltracao lenta por canal legitimo)."),
    ("T07", "always_on",     "corrupt",
     "Fixa (stuck-at) o bit menos significativo de uma coluna do MixColumns, reduzindo "
     "a difusao de forma sutil e sempre ativa."),
    ("T08", "cheat_code",    "dos",
     "Sequencia-gatilho: uma sequencia especifica de blocos consecutivos coloca a FSM "
     "num estado de deadlock ate o reset."),
    ("T09", "rare_condition","sidechannel",
     "Modula o consumo (toggle de um registrador dummy) em funcao do peso de Hamming "
     "da chave, criando um canal lateral de potencia proposital."),
    ("T10", "time_bomb",     "corrupt",
     "Degradacao progressiva: a cada bloco de operacoes, aumenta a probabilidade de "
     "um erro de 1 bit na saida (envelhecimento malicioso simulado)."),
]

LEGIT_IDS = [x[0] for x in LEGIT]
TROJAN_IDS = [x[0] for x in TROJAN]
ALL_IDS = LEGIT_IDS + TROJAN_IDS
LABEL = {**{i: "legit" for i in LEGIT_IDS}, **{i: "trojan" for i in TROJAN_IDS}}
