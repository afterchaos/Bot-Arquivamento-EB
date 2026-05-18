import discord
from datetime import datetime
from typing import List, Optional
import config

async def processar_arquivamento(bot: discord.Client, interaction: discord.Interaction, tipo_chave: str, nick_roblox: str, patente: str, motivo: str, imagens: List[discord.Attachment], responsavel: str = None, permissao: str = None, link: str = None):
    # Tenta garantir o defer se ainda não foi feito
    if not interaction.response.is_done():
        try:
            await interaction.response.defer(ephemeral=True)
        except Exception:
            pass

    conf = config.TIPOS_ARQUIVO[tipo_chave]
    
    imagens_provas = [img for img in imagens if img and img.content_type and img.content_type.startswith('image/')]
    videos_provas = [img for img in imagens if img and img.content_type and img.content_type.startswith('video/')]
    
    valid_arquivos = imagens_provas + videos_provas
    
    if not valid_arquivos and not link:
        try:
            return await interaction.followup.send('Nenhuma imagem, vídeo ou link enviado. Por favor, envie ao menos uma prova.', ephemeral=True)
        except Exception:
            return

    channel = bot.get_channel(conf['canal_id'])
    if not channel:
        try:
            return await interaction.followup.send(
                f'Erro: Canal de destino para {tipo_chave} não encontrado.',
                ephemeral=True
            )
        except Exception:
            return

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
        icon_url=interaction.user.display_avatar.url if interaction.user.display_avatar else None
    )

    if tipo_chave == 'rebaixamento':
        campo_usuario = f'```{nick_roblox}```'
        campo_patente = f'```{patente}```'

        main_embed.add_field(
            name='👤 Usuario(s) (Roblox)',
            value=campo_usuario[:1024],
            inline=False
        )

        main_embed.add_field(
            name='Alteração de Patente',
            value=campo_patente[:1024],
            inline=False
        )
    elif tipo_chave == 'afastamento':
        dados = patente  # aqui estamos passando um dicionário

        main_embed.add_field(name="👤 Militar Afastado", value=f"```[{dados['patente']}] {dados['militar']}```"[:1024], inline=False)
        main_embed.add_field(name="📅 Período", value=f"```{dados['tempo']}```"[:1024], inline=True)
        main_embed.add_field(name="👮 Responsável (Ticket)", value=f"```{dados['resp_ticket']}```"[:1024], inline=True)
        main_embed.add_field(name="🔗 Ticket", value=f"{dados['link_ticket']}"[:1024], inline=False)
        main_embed.add_field(name="✅ Responsável (Aprovação)", value=f"```{dados['resp_aprovacao']}```"[:1024], inline=True)
    elif tipo_chave == 'relacionamento':
        main_embed.add_field(
            name='👤 Usuários (Roblox)',
            value=f'```{nick_roblox}```'[:1024],
            inline=False
        )
    elif tipo_chave == 'castigo':
        dados = patente

        main_embed.add_field(
           name='👤 Usuario(s) (Roblox)',
          value=f'```[{dados["patente"]}] {nick_roblox}```'[:1024],
         inline=False
        )

        main_embed.add_field(
            name='⏳ Período do Castigo',
            value=f'```{dados["periodo"]}```'[:1024],
            inline=True
        )

    else:
        campo_usuario = f'```[{patente}] {nick_roblox}```'

        main_embed.add_field(
        name='👤 Usuario(s) (Roblox)',
        value=campo_usuario[:1024],
        inline=False
        )

    if responsavel:
        main_embed.add_field(
            name='👮 Responsável:',
            value=f'```{responsavel}```'[:1024],
            inline=True
        )

    if permissao:
        main_embed.add_field(
            name='✅ Permissão:',
            value=f'```{permissao}```'[:1024],
            inline=True
        )

    main_embed.add_field(
        name='🆔 ID Relator',
        value=f'```{interaction.user.id}```'[:1024],
        inline=True
    )

    limite = 1000
    partes_motivo = [motivo[i:i+limite] for i in range(0, len(motivo), limite)]
    
    for i, parte in enumerate(partes_motivo):
        nome_field = '📝 Motivo do Registro' if i == 0 else f'📝 Motivo do Registro (Parte {i+1})'
        main_embed.add_field(
            name=nome_field,
            value=f'```{parte}```',
            inline=False
        )

    if link:
        # Se o link for muito grande, truncamos para caber no field
        link_formatado = link if len(link) <= 1024 else link[:1021] + "..."
        main_embed.add_field(
            name='🔗 Link da Prova',
            value=link_formatado,
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
        for img in imagens_provas[1:10]: # Limite total de 10 embeds por mensagem no Discord
            extra_embed = discord.Embed(color=conf['cor'])
            extra_embed.set_image(url=img.url)
            embeds.append(extra_embed)

    # =====================
    # VIDEOS (CONTINUAM COMO ANEXO)
    # =====================
    MAX_VIDEO_SIZE = 25 * 1024 * 1024 # 25MB
    files = []
    videos_grandes = []
    
    for i, vid in enumerate(videos_provas):
        if vid.size > MAX_VIDEO_SIZE:
            videos_grandes.append(vid.filename)
            continue
        
        try:    
            file = await vid.to_file()
            clean_name = "".join(c for c in vid.filename if c.isalnum() or c in "._-")
            file.filename = f"video_{i}_{clean_name}"
            files.append(file)
        except Exception:
            videos_grandes.append(f"{vid.filename} (Erro ao processar)")

    # Discord coloca anexos acima de embeds na mesma mensagem.
    # Enviamos os vídeos como uma resposta à mensagem do embed para ficarem abaixo.
    try:
        msg_embed = await channel.send(embeds=embeds)

        if files:
            await channel.send(content="🎥 **Vídeo(s) da Prova:**", files=files, reference=msg_embed)
    except Exception as e:
        try:
            return await interaction.followup.send(f"❌ Erro ao enviar registro para o canal: {str(e)}", ephemeral=True)
        except Exception:
            return

    sucesso = discord.Embed(
        title='REGISTRO CONCLUIDO',
        description=f'O arquivamento de **{nick_roblox}** foi enviado para o canal de <#{conf["canal_id"]}>.',
        color=0x2ecc71
    )

    if videos_grandes:
        lista_videos = "\n".join([f"• `{v}`" for v in videos_grandes])
        sucesso.add_field(
            name="⚠️ Vídeos Ignorados (>25MB)",
            value=f"Os seguintes vídeos não foram enviados por excederem o limite:\n{lista_videos}",
            inline=False
        )

    try:
        await interaction.followup.send(embed=sucesso, ephemeral=True)
    except Exception:
        pass

def collect_images(*args):
    return [arg for arg in args if arg is not None]
