import discord
from datetime import datetime
from typing import List, Optional
import config

async def processar_arquivamento(bot: discord.Client, interaction: discord.Interaction, tipo_chave: str, nick_roblox: str, patente: str, motivo: str, imagens: List[discord.Attachment], responsavel: str = None, permissao: str = None):
    conf = config.TIPOS_ARQUIVO[tipo_chave]
    
    imagens_provas = [img for img in imagens if img and img.content_type and img.content_type.startswith('image/')]
    videos_provas = [img for img in imagens if img and img.content_type and img.content_type.startswith('video/')]
    
    valid_arquivos = imagens_provas + videos_provas
    
    if not valid_arquivos:
        if interaction.response.is_done():
            return await interaction.followup.send('Nenhuma imagem ou vídeo válido enviado. Por favor, envie ao menos uma prova.', ephemeral=True)
        else:
            return await interaction.response.send_message('Nenhuma imagem ou vídeo válido enviado. Por favor, envie ao menos uma prova.', ephemeral=True)

    if not interaction.response.is_done():
        await interaction.response.defer()

    channel = bot.get_channel(conf['canal_id'])
    if not channel:
        return await interaction.followup.send(
            f'Erro: Canal de destino para {tipo_chave} não encontrado.',
            ephemeral=True
        )

    embeds = []

    # =====================
    # EMBED PRINCIPAL
    # =====================
    main_embed = discord.Embed(
        title=conf['titulo'],
        color=conf['cor'],
        timestamp=datetime.now()
    )

    main_embed.set_author(
        name=f'Relator: {interaction.user.name}',
        icon_url=interaction.user.display_avatar.url
    )

    if tipo_chave == 'rebaixamento':
        campo_usuario = f'```{nick_roblox}```'
        campo_patente = f'```{patente}```'

        main_embed.add_field(
            name='👤 Usuario(s) (Roblox)',
            value=campo_usuario,
            inline=False
        )

        main_embed.add_field(
            name='Alteração de Patente',
            value=campo_patente,
            inline=False
        )
    elif tipo_chave == 'afastamento':
        dados = patente  # aqui estamos passando um dicionário

        main_embed.add_field(name="👤 Militar Afastado", value=f"```[{dados['patente']}] {dados['militar']}```", inline=False)
        main_embed.add_field(name="📅 Período", value=f"```{dados['tempo']}```", inline=True)
        main_embed.add_field(name="👮 Responsável (Ticket)", value=f"```{dados['resp_ticket']}```", inline=True)
        main_embed.add_field(name="🔗 Ticket", value=f"{dados['link_ticket']}", inline=False)
        main_embed.add_field(name="✅ Responsável (Aprovação)", value=f"```{dados['resp_aprovacao']}```", inline=True)
    elif tipo_chave == 'relacionamento':
        main_embed.add_field(
            name='👤 Usuários (Roblox)',
            value=f'```{nick_roblox}```',
            inline=False
        )
    elif tipo_chave == 'castigo':
        dados = patente

        main_embed.add_field(
           name='👤 Usuario(s) (Roblox)',
          value=f'```[{dados["patente"]}] {nick_roblox}```',
         inline=False
        )

        main_embed.add_field(
            name='⏳ Período do Castigo',
            value=f'```{dados["periodo"]}```',
            inline=True
        )

    else:
        campo_usuario = f'```[{patente}] {nick_roblox}```'

        main_embed.add_field(
        name='👤 Usuario(s) (Roblox)',
        value=campo_usuario,
        inline=False
        )

    if responsavel:
        main_embed.add_field(
            name='👮 Responsável:',
            value=f'```{responsavel}```',
            inline=True
        )

    if permissao:
        main_embed.add_field(
            name='✅ Permissão:',
            value=f'```{permissao}```',
            inline=True
        )

    main_embed.add_field(
        name='🆔 ID Relator',
        value=f'```{interaction.user.id}```',
        inline=True
    )

    main_embed.add_field(
        name='📝 Motivo do Registro',
        value=f'```{motivo}```',
        inline=False
    )

    # PRIMEIRA IMAGEM VIA URL (SEM DUPLICAÇÃO)
    if imagens_provas:
        main_embed.set_image(url=imagens_provas[0].url)

    main_embed.set_footer(text='Sistema de Arquivamento | Registro Oficial')
    embeds.append(main_embed)

    # =====================
    # OUTRAS IMAGENS
    # =====================
    if len(imagens_provas) > 1:
        for img in imagens_provas[1:]:
            extra_embed = discord.Embed(color=conf['cor'])
            extra_embed.set_image(url=img.url)
            embeds.append(extra_embed)

    # =====================
    # VIDEOS (CONTINUAM COMO ANEXO)
    # =====================
    files = []
    for i, vid in enumerate(videos_provas):
        file = await vid.to_file()
        clean_name = "".join(c for c in vid.filename if c.isalnum() or c in "._-")
        file.filename = f"video_{i}_{clean_name}"
        files.append(file)

    # Discord coloca anexos acima de embeds na mesma mensagem.
    # Enviamos os vídeos como uma resposta à mensagem do embed para ficarem abaixo.
    msg_embed = await channel.send(embeds=embeds)

    if files:
        await channel.send(content="🎥 **Vídeo(s) da Prova:**", files=files, reference=msg_embed)

    sucesso = discord.Embed(
        title='REGISTRO CONCLUIDO',
        description=f'O arquivamento de **{nick_roblox}** foi enviado para o canal de <#{conf["canal_id"]}>.',
        color=0x2ecc71
    )

    await interaction.followup.send(embed=sucesso, ephemeral=True)

def collect_images(*args):
    return [arg for arg in args if arg is not None]
