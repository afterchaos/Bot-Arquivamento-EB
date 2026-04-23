import json
import os
import discord
from discord import app_commands

PERMISSIONS_FILE = 'permissions.json'

# Adicione os IDs das contas do Discord que terão acesso total ao bot (sem precisar de cargos).
# Substitua ou adicione seu ID na lista abaixo. Ex: [123456789012345678, 987654321098765432]
ADMIN_IDS = [1248667147635396662, 643244640937443338]

class PermissionsManager:
    def __init__(self):
        self.file_path = PERMISSIONS_FILE
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def _read_data(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def _write_data(self, data):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

    def add_role(self, guild_id: int, action: str, role_id: int) -> bool:
        """Adiciona um cargo a uma ação específica. Retorna True se adicionado, False se já existia."""
        data = self._read_data()
        guild_id_str = str(guild_id)

        if guild_id_str not in data:
            data[guild_id_str] = {}
        
        if action not in data[guild_id_str]:
            data[guild_id_str][action] = []
            
        if role_id in data[guild_id_str][action]:
            return False # O cargo já possui esta permissão
            
        data[guild_id_str][action].append(role_id)
        self._write_data(data)
        return True

    def remove_role(self, guild_id: int, action: str, role_id: int) -> bool:
        """Remove um cargo de uma ação específica. Retorna True se removido, False se não existia."""
        data = self._read_data()
        guild_id_str = str(guild_id)

        if guild_id_str in data and action in data[guild_id_str]:
            if role_id in data[guild_id_str][action]:
                data[guild_id_str][action].remove(role_id)
                self._write_data(data)
                return True
        return False

    def get_roles(self, guild_id: int, action: str) -> list[int]:
        """Retorna a lista de IDs de cargos permitidos para uma ação."""
        data = self._read_data()
        guild_id_str = str(guild_id)
        return data.get(guild_id_str, {}).get(action, [])

    def reset_permissions(self, guild_id: int):
        """Limpa todas as permissões configuradas para um servidor."""
        data = self._read_data()
        guild_id_str = str(guild_id)
        if guild_id_str in data:
            del data[guild_id_str]
            self._write_data(data)

# Instância única (Singleton)
permissions_db = PermissionsManager()

class MissingPermissionError(app_commands.AppCommandError):
    def __init__(self, action: str):
        self.action = action
        super().__init__(f"Permissão ausente para a ação: {action}")

def require_permission(action: str):
    async def predicate(interaction: discord.Interaction) -> bool:
        if not interaction.guild:
            return False
            
        if interaction.user.id in ADMIN_IDS:
            return True

        if interaction.user.guild_permissions.administrator:
            return True
        
        allowed_role_ids = permissions_db.get_roles(interaction.guild.id, action)

        if not allowed_role_ids:
            raise MissingPermissionError(action)

        user_role_ids = [role.id for role in interaction.user.roles]

        if any(role_id in user_role_ids for role_id in allowed_role_ids):
            return True

        raise MissingPermissionError(action)

    return app_commands.check(predicate)
