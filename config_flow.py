"""Config flow to configure PubAir component."""
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from .const import CONF_UMDNAME, DOMAIN


class PubAirFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Met component."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Init PubAirFlowHandler."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=f"{DOMAIN}_" + user_input[CONF_UMDNAME], data=user_input
            )

        return await self._show_config_form()

    async def _show_config_form(
        self,
    ):
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_UMDNAME): str,
                }
            ),
            errors=self._errors,
        )