import discord
from discord.ext import commands
from discord import app_commands
import config
from utils.permissions import MissingPermissionError

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # Carrega todas as cogs
        extensions = [
            'cogs.permissions_cog',
            'cogs.general',
            'cogs.archiving'
        ]
        
        for extension in extensions:
            await self.load_extension(extension)
            print(f"Extensão {extension} carregada!")
        
        self.tree.on_error = self.on_app_command_error
        await self.tree.sync()
        print(f"Comandos slash sincronizados para {self.user}")

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CheckFailure):
            # Extraindo a original exception se estiver dentro de um CheckFailure
            original_error = getattr(error, 'original', error)
            
            if isinstance(original_error, MissingPermissionError) or isinstance(error, MissingPermissionError):
                action = getattr(original_error, 'action', getattr(error, 'action', 'desconhecida'))
                
                embed = discord.Embed(
                    title="⛔ Acesso Negado",
                    description=f"Você não possui os cargos necessários para utilizar esta ação: **{action.replace('_', ' ').title()}**.\n\nContate um administrador para solicitar acesso.",
                    color=0xe74c3c
                )
                
                if interaction.response.is_done():
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            else:
                # É um CheckFailure diferente
                msg = f"⛔ {str(error)}"
                if not interaction.response.is_done():
                    await interaction.response.send_message(msg, ephemeral=True)
                else:
                    await interaction.followup.send(msg, ephemeral=True)
                return
        
        # Erro genérico
        print(f"Erro no comando {interaction.command.name if interaction.command else 'desconhecido'}: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message(f"Ocorreu um erro ao processar o comando. Tente novamente.", ephemeral=True)
        else:
            await interaction.followup.send(f"Ocorreu um erro ao processar o comando. Tente novamente.", ephemeral=True)

bot = MyBot()

if __name__ == "__main__":
    bot.run(config.TOKEN)
