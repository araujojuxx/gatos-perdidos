# Gatos Perdidos (protótipo GBA)

Escolha Pudim, Coitadinho ou Olaf e atravesse a cidade até chegar em casa, onde a Ma espera.

## Controles
- **D-pad**: andar | **A**: pular | **START**: voltar ao menu
- No menu: **esquerda/direita** (ou L/R) escolhe o gato, **A** começa

## O que já tem
- Tela de seleção com os 3 gatos (cada um com cores e habilidade própria)
- Cidade noturna com rolagem, carros e sacadas para subir, cachorros patrulhando
- Corações de vida, checkpoints a cada 128 px, tela de chegada em casa (amanhecer)

## Como gerar o .gba
1. Instale o devkitARM (https://devkitpro.org/wiki/Getting_Started) e o Python 3.
2. Nesta pasta, rode: `make`
3. Sai o arquivo `gatosperdidos.gba`.

## Rodar nos consoles
- **Miyoo Mini Plus (OnionOS)**: copie o `.gba` para `Roms/GBA/`
- **R36S**: copie para a pasta `gba` do cartão de jogos (ArkOS/dArkOS)
- Para testar no PC antes: abra o `.gba` no mGBA ou no RetroArch

## Editar
- Arte, cores e fase estão em `gen_gfx.py` (rode `python3 gen_gfx.py` para refazer o `gfx.h`)
- Veja `previa_sprites.png` para os sprites

## Sem instalar nada: gerar o .gba pelo GitHub
1. Crie um repositório no GitHub e envie todo o conteúdo desta pasta (inclusive `.github`).
2. Abra a aba **Actions**, rode **Compilar GBA** (ou espere rodar sozinho).
3. Baixe o `gatosperdidos.gba` em **Artifacts**.

## Ou com Docker
`docker run --rm -v "$PWD":/src -w /src devkitpro/devkitarm make`
