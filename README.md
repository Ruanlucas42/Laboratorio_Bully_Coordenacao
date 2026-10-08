# Laboratório Bully - Coordenação em Sistemas Distribuídos

Implementação didática do Algoritmo do Valentão (Bully) em Python 3, baseada no roteiro **Laboratório Prático - Coordenação em Sistemas Distribuídos**. Cinco processos se comunicam por sockets TCP para eleger um coordenador, detectar sua indisponibilidade e realizar novas eleições.

## Autores

- Alice Egg
- Ruan Lucas

## Como funciona

Ao iniciar uma eleição, um processo envia `ELECTION` a todos os processos com ID maior que o seu. Se receber `OK`, desiste e deixa os processos maiores continuarem a eleição. Se nenhum responder `OK`, torna-se coordenador e anuncia seu ID aos demais com `COORDINATOR:<ID>`.

Em condições normais de comunicação, o processo disponível com maior ID vence. Quando um processo maior retorna, ele pode assumir a coordenação ao iniciar uma nova eleição.

## Recursos implementados

- Comunicação TCP entre processos, com atendimento em threads.
- Eleição manual com `ELECTION`, `OK` e `COORDINATOR`.
- Monitoramento do coordenador por `PING`/`PONG`, com intervalo de 5 segundos entre verificações e timeout de socket de 2 segundos.
- Eleição automática quando o coordenador conhecido deixa de responder.
- Logs de eleição com horário no formato `HH:MM:SS`.
- Diagrama textual automático com início, mensagens, respostas, desistência e vencedor.

## Estrutura

```text
laboratorio-bully/
├── config.py       # IDs, endereços e portas dos processos
├── processo.py     # Servidor TCP, eleição, monitoramento e diagrama
└── README.md       # Documentação e roteiro de execução
```

## Requisitos e configuração

É necessário Python 3. O projeto utiliza apenas a biblioteca padrão; não é preciso instalar pacotes.

Os processos estão configurados em `config.py` para executar na mesma máquina:

| Processo | Endereço | Porta TCP |
| --- | --- | --- |
| P1 | 127.0.0.1 | 5001 |
| P2 | 127.0.0.1 | 5002 |
| P3 | 127.0.0.1 | 5003 |
| P4 | 127.0.0.1 | 5004 |
| P5 | 127.0.0.1 | 5005 |

As portas precisam estar livres. Execute apenas uma instância de cada ID. Para experimentar em máquinas diferentes, adapte os endereços em `config.py` em todas elas e permita a comunicação nas portas utilizadas.

## Execução

Abra cinco terminais na pasta do projeto e execute **um comando em cada terminal**:

```bash
python3 processo.py 1
python3 processo.py 2
python3 processo.py 3
python3 processo.py 4
python3 processo.py 5
```

Se o executável do Python 3 se chamar `python` no seu ambiente, substitua `python3` por `python`.

Espere todos os servidores exibirem a mensagem de que estão aguardando conexões. Depois, digite os comandos no prompt do processo:

| Comando | Ação |
| --- | --- |
| `eleicao` | Inicia uma eleição a partir desse processo. |
| `status` | Mostra o ID local e o coordenador conhecido. |
| `sair` | Encerra o processo. |

A primeira eleição precisa ser iniciada manualmente. Enquanto o coordenador for `None`, o monitoramento não inicia eleições. Após reiniciar um processo, use `eleicao` para que ele participe de uma nova eleição e descubra ou anuncie o coordenador.

## Experimentos

Os cenários abaixo são um roteiro de verificação. Os resultados descritos são esperados; não representam evidências de execução coletadas.

### 1. Eleição inicial

Com os cinco processos ativos, digite `eleicao` no P5. Como não há IDs maiores, P5 deve vencer e anunciar `COORDINATOR:5`. Confira o coordenador com `status` nos outros terminais.

### 2. Falha do coordenador

Digite `sair` no P5. Os demais processos que conhecem P5 como coordenador devem detectar a ausência de `PONG` e iniciar eleições automaticamente. Com P1 a P4 ativos, o vencedor esperado é P4.

Para observar a eleição manual do roteiro, também é possível digitar `eleicao` no P2 após encerrar P5. P2 consulta P3, P4 e P5; ao receber `OK` de um processo maior, desiste. O monitoramento pode iniciar outras eleições simultaneamente.

A detecção depende do intervalo de monitoramento e do tempo das tentativas de conexão; a troca de coordenador não é instantânea.

### 3. Recuperação do processo de maior ID

Execute novamente `python3 processo.py 5` e digite `eleicao` no P5. Ele deve recuperar a coordenação e anunciá-la aos demais.

### 4. Recuperação de um processo menor

Com P5 desligado e P4 como coordenador, encerre P2 e execute novamente `python3 processo.py 2`. Digite `eleicao` no P2. Enquanto P4 estiver disponível, P2 deve desistir e P4 deve continuar como coordenador.

### 5. Várias falhas

Deixe somente P1, P2 e P3 ativos. Digite `eleicao` no P1. O vencedor esperado é P3, o maior ID disponível.

## Logs e diagrama textual

Os registros com horário mostram o início da eleição, tentativas de envio de `ELECTION`, respostas `OK`, ausência de resposta, desistência, vitória e anúncios de `COORDINATOR`.

Exemplo ilustrativo de uma eleição iniciada pelo P4 com P5 desligado:

```text
+--- DIAGRAMA TEXTUAL DA ELEIÇÃO ---
| Visão local do processo P4
| Iniciador desta eleição local: P4
|
|  [14:20:00] P4 iniciou eleição
|    |
|    v
|  [14:20:00] P4 → P5 ELECTION
|    |
|    v
|  [14:20:00] P5 não respondeu OK
|    |
|    v
|  [14:20:00] P4 venceu a eleição
|    |
|    v
|  [14:20:00] P4 → P1 COORDINATOR
|    |
|    v
|  [14:20:00] P4 → P2 COORDINATOR
|    |
|    v
|  [14:20:00] P4 → P3 COORDINATOR
|    |
|    v
|  [14:20:00] P4 → P5 COORDINATOR
|    |
|    v
| Vencedor: P4
+---------------------------------
```

Cada terminal apresenta sua **visão local** da eleição. O iniciador indicado é o processo que iniciou aquela eleição local; não há rastreamento de um iniciador global entre as eleições desencadeadas em outros processos. Para observar toda a troca de mensagens, acompanhe os terminais em conjunto.

Quando um processo desiste sem ainda conhecer o vencedor, o diagrama informa que está aguardando `COORDINATOR`. Ao receber o anúncio, apresenta a versão atualizada. Se o anúncio chegar durante os envios, ele será incluído no diagrama apresentado ao término da eleição local.

Os registros de envio indicam tentativas, inclusive para processos desligados. A ordem e os horários variam devido à execução concorrente. Os eventos ficam em memória e são reiniciados a cada nova eleição local; não são gravados automaticamente em arquivo.

