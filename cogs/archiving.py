import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, List
from datetime import datetime, timedelta
import config
from utils.permissions import require_permission
from utils.helpers import processar_arquivamento, collect_images

class EditModal(discord.ui.Modal):
    def __init__(self, message, tipo):
        super().__init__(title="Editar Registro")
        self.message = message
        self.tipo = tipo
        
        # Preenche os valores a partir do embed atual
        current_nick = ""
        current_motivo = ""
        embed = self.message.embeds[0]
        
        for field in embed.fields:
            if 'Usuario' in field.name or 'Usuário' in field.name or 'Militar' in field.name:
                current_nick = field.value.replace('```', '')
                if ']' in current_nick: # Remove [Patente] se estiver presente
                    current_nick = current_nick.split(']')[-1].strip()
            elif 'Motivo' in field.name:
                current_motivo = field.value.replace('```', '')

        self.nick_input = discord.ui.TextInput(
            label="Novo(s) Nick(s)",
            default=current_nick,
            placeholder="Ex: Player1 & Player2",
            required=True
        )
        self.motivo_input = discord.ui.TextInput(
            label="Novo Motivo",
            default=current_motivo,
            style=discord.TextStyle.paragraph,
            required=True
        )
        
        self.add_item(self.nick_input)
        self.add_item(self.motivo_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        new_embeds = [e.copy() for e in self.message.embeds]
        if not new_embeds:
            return await interaction.followup.send("Erro: Não foi possível encontrar o embed original.", ephemeral=True)
            
        main_embed = new_embeds[0]
        
        # Atualiza os campos apenas no embed principal
        found_nick = False
        found_motivo = False
        
        for i, field in enumerate(main_embed.fields):
            if 'Usuario' in field.name or 'Usuário' in field.name or 'Militar' in field.name:
                main_embed.set_field_at(i, name=field.name, value=f'```{self.nick_input.value}```', inline=field.inline)
                found_nick = True
            elif 'Motivo' in field.name:
                main_embed.set_field_at(i, name=field.name, value=f'```{self.motivo_input.value}```', inline=field.inline)
                found_motivo = True

        if not found_nick:
            main_embed.insert_field_at(0, name='👤 Usuario(s) (Roblox)', value=f'```{self.nick_input.value}```', inline=True)
        if not found_motivo:
            main_embed.add_field(name='📝 Motivo', value=f'```{self.motivo_input.value}```', inline=False)
        await self.message.edit(embeds=new_embeds)
        await interaction.followup.send(f"Registro editado com sucesso: {self.message.jump_url}", ephemeral=True)

class Archiving(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="exilio", description="Realiza o arquivamento de exílio")
    @require_permission("arquivar_registros")
    @app_commands.choices(patente=config.PATENTES_ESCOLHA)
    async def exilio(self, interaction: discord.Interaction, nick: str, patente: app_commands.Choice[str], responsavel: str, permissao: str, motivo: str, 
                     img1: discord.Attachment, img2: Optional[discord.Attachment] = None, img3: Optional[discord.Attachment] = None, 
                     img4: Optional[discord.Attachment] = None, img5: Optional[discord.Attachment] = None, img6: Optional[discord.Attachment] = None, 
                     img7: Optional[discord.Attachment] = None, img8: Optional[discord.Attachment] = None, img9: Optional[discord.Attachment] = None, 
                     img10: Optional[discord.Attachment] = None):
        await processar_arquivamento(self.bot, interaction, 'exilio', nick, patente.value, motivo, collect_images(img1, img2, img3, img4, img5, img6, img7, img8, img9, img10), responsavel, permissao)

    @app_commands.command(name="exilio_perm", description="Realiza o arquivamento de exílio permanente")
    @require_permission("arquivar_registros")
    @app_commands.choices(patente=config.PATENTES_ESCOLHA)
    async def exilio_perm(self, interaction: discord.Interaction, nick: str, patente: app_commands.Choice[str], responsavel: str, permissao: str, motivo: str, 
                          img1: discord.Attachment, img2: Optional[discord.Attachment] = None, img3: Optional[discord.Attachment] = None, 
                          img4: Optional[discord.Attachment] = None, img5: Optional[discord.Attachment] = None, img6: Optional[discord.Attachment] = None, 
                          img7: Optional[discord.Attachment] = None, img8: Optional[discord.Attachment] = None, img9: Optional[discord.Attachment] = None, 
                          img10: Optional[discord.Attachment] = None):
        await processar_arquivamento(self.bot, interaction, 'exilio_perm', nick, patente.value, motivo, collect_images(img1, img2, img3, img4, img5, img6, img7, img8, img9, img10), responsavel, permissao)

    @app_commands.command(name="castigo", description="Realiza o arquivamento de castigo")
    @require_permission("arquivar_registros")
    @app_commands.choices(patente=config.PATENTES_ESCOLHA)
    async def castigo(self, interaction: discord.Interaction, nick: str, patente: app_commands.Choice[str], responsavel: str, permissao: str, periodo: str, motivo: str, 
                      img1: discord.Attachment, img2: Optional[discord.Attachment] = None, img3: Optional[discord.Attachment] = None, 
                      img4: Optional[discord.Attachment] = None, img5: Optional[discord.Attachment] = None, img6: Optional[discord.Attachment] = None, 
                      img7: Optional[discord.Attachment] = None, img8: Optional[discord.Attachment] = None, img9: Optional[discord.Attachment] = None, 
                      img10: Optional[discord.Attachment] = None):
        dados_castigo = {
            "patente": patente.value,
            "periodo": periodo
        }
        await processar_arquivamento(self.bot, interaction, 'castigo', nick, dados_castigo, motivo, collect_images(img1, img2, img3, img4, img5, img6, img7, img8, img9, img10), responsavel, permissao)

    @app_commands.command(name="banimento", description="Realiza o arquivamento de banimento")
    @require_permission("arquivar_registros")
    @app_commands.choices(patente=config.PATENTES_ESCOLHA)
    async def banimento(self, interaction: discord.Interaction, nick: str, patente: app_commands.Choice[str], motivo: str, 
                        img1: discord.Attachment, img2: Optional[discord.Attachment] = None, img3: Optional[discord.Attachment] = None, 
                        img4: Optional[discord.Attachment] = None, img5: Optional[discord.Attachment] = None, img6: Optional[discord.Attachment] = None, 
                        img7: Optional[discord.Attachment] = None, img8: Optional[discord.Attachment] = None, img9: Optional[discord.Attachment] = None, 
                        img10: Optional[discord.Attachment] = None):
        await processar_arquivamento(self.bot, interaction, 'banimento', nick, patente.value, motivo, collect_images(img1, img2, img3, img4, img5, img6, img7, img8, img9, img10))

    @app_commands.command(name="rebaixamento", description="Realiza o arquivamento de rebaixamento")
    @require_permission("arquivar_registros")
    @app_commands.choices(patente_antiga=config.PATENTES_ESCOLHA, patente_nova=config.PATENTES_ESCOLHA)
    async def rebaixamento(self, interaction: discord.Interaction, nick: str, patente_antiga: app_commands.Choice[str], patente_nova: app_commands.Choice[str], motivo: str, 
                        img1: discord.Attachment, img2: Optional[discord.Attachment] = None, img3: Optional[discord.Attachment] = None, 
                        img4: Optional[discord.Attachment] = None, img5: Optional[discord.Attachment] = None, img6: Optional[discord.Attachment] = None, 
                        img7: Optional[discord.Attachment] = None, img8: Optional[discord.Attachment] = None, img9: Optional[discord.Attachment] = None, 
                        img10: Optional[discord.Attachment] = None):

        if patente_antiga.value not in config.HIERARQUIA_PATENTES or patente_nova.value not in config.HIERARQUIA_PATENTES:
            return await interaction.response.send_message(
                "❌ Erro interno: patente não configurada na hierarquia.",
                ephemeral=True
            )

        valor_antiga = config.HIERARQUIA_PATENTES[patente_antiga.value]
        valor_nova = config.HIERARQUIA_PATENTES[patente_nova.value]

        if valor_nova >= valor_antiga:
            return await interaction.response.send_message(
                f"❌ Rebaixamento inválido: `{patente_nova.value}` não é inferior a `{patente_antiga.value}`.",
                ephemeral=True
            )                
        await processar_arquivamento(self.bot, interaction, 'rebaixamento', nick, f"[{patente_antiga.value}] → [{patente_nova.value}]", motivo, collect_images(img1, img2, img3, img4, img5, img6, img7, img8, img9, img10))

    @app_commands.command(name="relacionamento", description="Realiza o arquivamento de relacionamento (2 pessoas)")
    @require_permission("arquivar_registros")
    async def relacionamento(self, interaction: discord.Interaction, nick1: str, nick2: str, motivo: str, 
                             img1: discord.Attachment, img2: Optional[discord.Attachment] = None, img3: Optional[discord.Attachment] = None, 
                             img4: Optional[discord.Attachment] = None, img5: Optional[discord.Attachment] = None, img6: Optional[discord.Attachment] = None, 
                             img7: Optional[discord.Attachment] = None, img8: Optional[discord.Attachment] = None, img9: Optional[discord.Attachment] = None, 
                             img10: Optional[discord.Attachment] = None):
        await processar_arquivamento(self.bot, interaction, 'relacionamento', f"{nick1} & {nick2}", "N/A", motivo, collect_images(img1, img2, img3, img4, img5, img6, img7, img8, img9, img10))

    @app_commands.command(name="afastamento", description="Realiza o arquivamento de afastamento")
    @require_permission("arquivar_registros")
    @app_commands.choices(patente=config.PATENTES_ESCOLHA)
    async def afastamento(
        self,
        interaction: discord.Interaction,
        militar: str,
        patente: app_commands.Choice[str],
        tempo: str,
        resp_ticket: str,
        resp_aprovacao: str,
        link_ticket: str,
        motivo: str,
        img1: discord.Attachment,
        img2: Optional[discord.Attachment] = None,
        img3: Optional[discord.Attachment] = None,
        img4: Optional[discord.Attachment] = None,
        img5: Optional[discord.Attachment] = None,
        img6: Optional[discord.Attachment] = None,
        img7: Optional[discord.Attachment] = None,
        img8: Optional[discord.Attachment] = None,
        img9: Optional[discord.Attachment] = None,
        img10: Optional[discord.Attachment] = None
    ):
        dados_afastamento = {
            "militar": militar,
            "patente": patente.value,
            "tempo": tempo,
            "resp_ticket": resp_ticket,
            "resp_aprovacao": resp_aprovacao,
            "link_ticket": link_ticket
        }

        await processar_arquivamento(
            self.bot,
            interaction,
            'afastamento',
            militar,
            dados_afastamento,
            motivo,
            collect_images(img1, img2, img3, img4, img5, img6, img7, img8, img9, img10)
        )

    @app_commands.command(name="editar_registro", description="Abre o painel para editar um registro existente")
    @require_permission("editar_registros")
    @app_commands.describe(tipo="Tipo do arquivamento", mensagem_id="ID da mensagem do log")
    @app_commands.choices(tipo=[
        app_commands.Choice(name="Exílio", value="exilio"),
        app_commands.Choice(name="Exílio Permanente", value="exilio_perm"),
        app_commands.Choice(name="Castigo", value="castigo"),
        app_commands.Choice(name="Banimento", value="banimento"),
        app_commands.Choice(name="Rebaixamento", value="rebaixamento"),
        app_commands.Choice(name="Afastamento", value="afastamento"),
        app_commands.Choice(name="Relacionamento", value="relacionamento")
    ])
    async def editar_registro(self, interaction: discord.Interaction, tipo: str, mensagem_id: str):
        conf = config.TIPOS_ARQUIVO[tipo]
        channel = self.bot.get_channel(conf['canal_id'])
        
        if not channel:
            return await interaction.response.send_message("Canal não encontrado.", ephemeral=True)
        
        try:
            message = await channel.fetch_message(int(mensagem_id))
        except Exception:
            return await interaction.response.send_message("Mensagem não encontrada. Verifique o ID e se o comando foi usado no tipo correto.", ephemeral=True)
        
        if not message.embeds:
            return await interaction.response.send_message("A mensagem selecionada não possui um embed.", ephemeral=True)

        await interaction.response.send_modal(EditModal(message, tipo))

    @app_commands.command(name="ficha", description="Consulta a ficha criminal de um usuário")
    async def ficha(self, interaction: discord.Interaction, nick: str):
        await interaction.response.defer()
        
        nick_procurado = nick.strip().lower()

        resultados = []

        for tipo_chave, info in config.TIPOS_ARQUIVO.items():
            canal = self.bot.get_channel(info['canal_id'])
            if not canal: continue
            
            async for message in canal.history(limit=1000):
                if message.embeds:
                    embed = message.embeds[0]
                    for field in embed.fields:
                        if 'Usuario' in field.name or 'Usuário' in field.name or 'Militar' in field.name:
                            content = field.value.replace('```', '').lower()    
                            if ']' in content:
                                content = content.split(']')[-1].strip()

                            nicks_in_field = [n.strip() for n in content.split('&')]

                            if nick_procurado in nicks_in_field:
                                data_brasil = message.created_at - timedelta(hours=3)
                                resultados.append({
                                    'tipo': info['titulo'].split('|')[-1].strip(),
                                    'url': message.jump_url,
                                    'data': data_brasil.strftime('%d/%m/%Y'),
                                    'cor': info['cor']
                                })
                                break

        if resultados:
            embed_final = discord.Embed(
                title=f"FICHA CRIMINAL: {nick.upper()}",
                description=f"Foram encontrados **{len(resultados)}** registros associados a este usuário.",
                color=0x2f3136,
                timestamp=datetime.now()
            )
            for idx, res in enumerate(resultados, 1):
                embed_final.add_field(
                    name=f"Registro #{idx} - {res['tipo']}",
                    value=f"Data: `{res['data']}`\n[Ver Provas e Detalhes]({res['url']})",
                    inline=False
                )
            embed_final.set_footer(text="Consulta realizada com sucesso", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=embed_final)
        else:
            await interaction.followup.send(embed=discord.Embed(
                title="❌ NADA ENCONTRADO",
                description=f"O usuário **{nick}** não possui registros em nossa base de dados.",
                color=0xe74c3c
            ))

async def setup(bot):
    await bot.add_cog(Archiving(bot))
