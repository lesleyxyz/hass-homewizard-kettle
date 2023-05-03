"""Config flow for HWKettle integration."""
import logging
import re
import secrets
import traceback
import sys
import asyncio
import subprocess
import voluptuous as vol
from homeassistant.const import *
from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from .const import *
from .kettle_connection import KettleConnection
from hwkitchen import HWSocket

_LOGGER = logging.getLogger(__name__)


class HWKettleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        """Get options flow for this handler."""
        return HWKettleConfigFlow(entry=entry)

    def __init__(self, entry = None):
        """Initialize a new HWKettleConfigFlow."""
        self.entry = entry
        self.config = {} if not entry else dict(entry.data.items())

    async def init_kettle_id(self, kettle_id: str):
        if kettle_id in self._async_current_ids():
            return False

        await self.async_set_unique_id(kettle_id)
        self.config[CONF_KETTLE_ID] = kettle_id

        return True

    async def async_step_user(self, user_input=None):
        """Handle the user step."""
        return await self.async_step_login()
   
    async def async_step_kettle_select(self, user_input=None):
        """Handle the kettle_select step."""
        errors = {}
        if user_input is not None:
            kettle_id = user_input[CONF_KETTLE_ID]
            self.config[CONF_KETTLE_ID] = kettle_id
            if not await self.init_kettle_id(kettle_id):
                # This kettle already configured
                return self.async_abort(reason='already_configured')

            # Continue to connect step
            return self.async_create_entry(
                title=kettle_id, data=self.config if not self.entry else {}
            )

        try:
            email = self.config[CONF_EMAIL]
            password = self.config[CONF_PASSWORD]
            ws_client = HWSocket(email, password)

            devices = await self.hass.async_add_executor_job(ws_client.get_devices)
            kettle_ids = [d.get("identifier") for d in devices.get("devices", [])]

            if len(kettle_ids) == 0:
                return self.async_abort(reason='kettle_not_found')

            schema = vol.Schema(
            {
                vol.Required(CONF_KETTLE_ID): vol.In(kettle_ids)
            })
        except Exception:
            _LOGGER.error(traceback.format_exc())
            return self.async_abort(reason='unknown')

        return self.async_show_form(
            step_id="kettle_select",
            errors=errors,
            data_schema=schema
        )

    async def async_step_login(self, user_input=None):
        """Handle the login step."""
        errors = {}
        if user_input is not None:
            try:
                email = user_input[CONF_EMAIL]
                password = user_input[CONF_PASSWORD]

                self.config[CONF_EMAIL] = email
                self.config[CONF_PASSWORD] = password

                rest_client = HWSocket(email, password)
                await self.hass.async_add_executor_job(rest_client.get_token)
                return await self.async_step_kettle_select()
            except Exception:
                _LOGGER.error(traceback.format_exc())
                return self.async_abort(reason='unknown')

        return self.async_show_form(
            step_id="login",
            errors=errors,
            data_schema=vol.Schema({
                vol.Required(CONF_EMAIL): cv.string,
                vol.Required(CONF_PASSWORD): cv.string
            })
        )  
