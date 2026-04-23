import discord
from discord.ext import commands
from discord import app_commands
from utils.permissions import permissions_db, ADMIN_IDS

class PermissionsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Grupo de comandos /permissao
    permissao = app_commands.Group(
        name="permissao",
        description="Gerencie as permissões de acesso aos comandos do bot.",
        # default_permissions removido para permitir que os donos usem sem admin, checado via interaction_check abaixo
    )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Check customizado que aplica a todo o cog (comandos de /permissao)
        if interaction.user.id in ADMIN_IDS:
            return True
        if await self.bot.is_owner(interaction.user):
            return True
        if interaction.user.guild_permissions.administrator:
            return True
            
        # Lança um erro se não tiver permissão para usar /permissao
        raise app_commands.CheckFailure("Acesso Negado: Você precisa ser um Administrador do servidor ou dono do bot para gerenciar permissões.")


    acoes_choices = [
        app_commands.Choice(name="Arquivar Registros (exílio, castigo, etc)", value="arquivar_registros"),
        app_commands.Choice(name="Editar Registros", value="editar_registros")
    ]

    @permissao.command(name="adicionar", description="Concede permissão de uma ação para um cargo.")
    @app_commands.describe(acao="O tipo de ação", cargo="O cargo a receber permissão")
    @app_commands.choices(acao=acoes_choices)
    async def adicionar(self, interaction: discord.Interaction, acao: str, cargo: discord.Role):
        sucesso = permissions_db.add_role(interaction.guild.id, acao, cargo.id)
        
        if sucesso:
            embed = discord.Embed(
                title="✅ Permissão Concedida",
                description=f"O cargo {cargo.mention} agora possui permissão para: **{acao.replace('_', ' ').title()}**.",
                color=0x2ecc71
            )
        else:
            embed = discord.Embed(
                title="⚠️ Permissão Já Existente",
                description=f"O cargo {cargo.mention} já possui a permissão para: **{acao.replace('_', ' ').title()}**.",
                color=0xf1c40f
            )
            
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @permissao.command(name="remover", description="Remove a permissão de uma ação de um cargo.")
    @app_commands.describe(acao="O tipo de ação", cargo="O cargo a perder permissão")
    @app_commands.choices(acao=acoes_choices)
    async def remover(self, interaction: discord.Interaction, acao: str, cargo: discord.Role):
        sucesso = permissions_db.remove_role(interaction.guild.id, acao, cargo.id)
        
        if sucesso:
            embed = discord.Embed(
                title="🗑️ Permissão Removida",
                description=f"O cargo {cargo.mention} perdeu a permissão para: **{acao.replace('_', ' ').title()}**.",
                color=0xe74c3c
            )
        else:
            embed = discord.Embed(
                title="⚠️ Permissão Não Encontrada",
                description=f"O cargo {cargo.mention} não possuía permissão para: **{acao.replace('_', ' ').title()}**.",
                color=0xf1c40f
            )
            
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @permissao.command(name="listar", description="Lista todos os cargos que possuem permissão para as ações.")
    async def listar(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📋 Lista de Permissões",
            description="Abaixo estão as permissões configuradas no servidor.",
            color=0x3498db
        )
        
        tem_alguma = False
        for choice in self.acoes_choices:
            role_ids = permissions_db.get_roles(interaction.guild.id, choice.value)
            if role_ids:
                tem_alguma = True
                roles_mentions = [f"<@&{r_id}>" for r_id in role_ids]
                embed.add_field(
                    name=f"🔹 {choice.name}",
                    value=" ".join(roles_mentions),
                    inline=False
                )
                
        if not tem_alguma:
            embed.description = "Não há nenhuma permissão customizada configurada ainda.\nApenas Administradores do servidor podem executar os comandos protegidos no momento."
            
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @permissao.command(name="resetar", description="Remove TODAS as configurações de permissão do bot neste servidor.")
    async def resetar(self, interaction: discord.Interaction):
        permissions_db.reset_permissions(interaction.guild.id)
        embed = discord.Embed(
            title="🔄 Permissões Resetadas",
            description="Todas as permissões foram limpas. Agora os comandos estão restritos apenas para Administradores do servidor até que novas permissões sejam configuradas.",
            color=0x95a5a6
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(PermissionsCog(bot))
