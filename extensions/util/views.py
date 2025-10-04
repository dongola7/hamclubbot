# Copyright (c) 2025, Blair Kitchen
# All rights reserved.
#
# See the file LICENSE for information on usage and redistribution
# of this file, and for a DISCLAIMER OF ALL WARRANTIES.

"""Implements common views for use in the discord bot"""

import discord

class YesNoConfirmationView(discord.ui.View):
    """Implements a simple yes/no confirmation view"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__selection = None

    @property
    def selection(self) -> str | None:
        """Returns the selection made by the user. None if no selection made before timeout"""
        return self.__selection

    @discord.ui.button(label="Yes")
    async def yes_callback(self, _button: discord.Button, _interaction: discord.Interaction):
        """Callback for handling the 'yes' button click"""
        self.__selection = "yes"
        self.stop()

    @discord.ui.button(label="No")
    async def no_callback(self, _button: discord.Button, _interaction: discord.Interaction):
        """Callback for handling the 'yes' button click"""
        self.__selection = "no"
        self.stop()
