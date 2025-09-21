import discord

class YesNoConfirmationView(discord.ui.View):
    """Implements a simple yes/no confirmation view"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__selection = None

    @property
    def selection(self) -> str | None:
        return self.__selection

    @discord.ui.button(label="Yes")
    async def yes_callback(self, button: discord.Button, interaction: discord.Interaction):
        self.__selection = "yes"
        self.stop()

    @discord.ui.button(label="No")
    async def no_callback(self, button: discord.Button, interaction: discord.Interaction):
        self.__selection = "no"
        self.stop()
