# Evidências do laboratório

Participantes: **Alice Egg** e **Ruan Lucas**.

As imagens abaixo foram extraídas do documento fornecido pelos participantes e preservadas sem alterações. Elas registram diferentes etapas do desenvolvimento; algumas capturas são anteriores à implementação dos logs e do diagrama. Não são novas execuções realizadas para esta documentação.

[Baixar o roteiro original com os prints (.pdf)](roteiro-laboratorio-bully.pdf)

## Eleição inicial

P5 inicia a eleição e torna-se coordenador.

![P5 inicia a eleição e torna-se coordenador.](imagens/image1.png)

Consulta de status no P2, indicando P5 como coordenador.

![Consulta de status no P2, indicando P5 como coordenador.](imagens/image3.png)

## Falha do coordenador e eleição manual

Encerramento do P5 após a eleição inicial.

![Encerramento do P5 após a eleição inicial.](imagens/image5.png)

P2 envia ELECTION, recebe OK e recebe o anúncio do P4.

![P2 envia ELECTION, recebe OK e recebe o anúncio do P4.](imagens/image2.png)

P4 participa das eleições e assume a coordenação.

![P4 participa das eleições e assume a coordenação.](imagens/image7.png)

## Recuperação e várias falhas

P5 é reiniciado e inicia uma nova eleição.

![P5 é reiniciado e inicia uma nova eleição.](imagens/image8.png)

P2 é reiniciado, inicia eleição e recebe COORDINATOR:4.

![P2 é reiniciado, inicia eleição e recebe COORDINATOR:4.](imagens/image12.png)

Eleição iniciada no P1, com anúncio de P3 como coordenador.

![Eleição iniciada no P1, com anúncio de P3 como coordenador.](imagens/image4.png)

## Detecção automática com PING/PONG

P5 recebe mensagens PING dos demais processos.

![P5 recebe mensagens PING dos demais processos.](imagens/image6.png)

P2 recebe o anúncio de P5 e verifica o coordenador com PING/PONG.

![P2 recebe o anúncio de P5 e verifica o coordenador com PING/PONG.](imagens/image9.png)

Terminal do P5 durante o atendimento de mensagens PING.

![Terminal do P5 durante o atendimento de mensagens PING.](imagens/image13.png)

Terminal do P2 durante as verificações PING/PONG.

![Terminal do P2 durante as verificações PING/PONG.](imagens/image14.png)

P2 passa a verificar P4 após receber COORDINATOR:4.

![P2 passa a verificar P4 após receber COORDINATOR:4.](imagens/image17.png)

## Logs com horário

P4 detecta a ausência de resposta de P5, inicia eleição automaticamente, vence e registra os anúncios COORDINATOR.

![P4 detecta a ausência de resposta de P5, inicia eleição automaticamente, vence e registra os anúncios COORDINATOR.](imagens/image15.png)

## Diagrama textual automático

P5 apresenta o diagrama da eleição com iniciador, vitória e anúncios COORDINATOR.

![P5 apresenta o diagrama da eleição com iniciador, vitória e anúncios COORDINATOR.](imagens/image16.png)

## Capturas da implementação

Tratamento das mensagens PING, ELECTION e COORDINATOR.

![Tratamento das mensagens PING, ELECTION e COORDINATOR.](imagens/image10.png)

Método de monitoramento do coordenador.

![Método de monitoramento do coordenador.](imagens/image11.png)
