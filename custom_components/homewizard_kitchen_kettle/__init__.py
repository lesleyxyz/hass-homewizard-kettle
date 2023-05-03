"""Support for HWKettle."""
import logging
from .const import *
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import *
import homeassistant.helpers.event as ev
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity import DeviceInfo
from datetime import timedelta
from .kettle_connection import KettleConnection
import json

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.WATER_HEATER,
    Platform.SWITCH,
    Platform.NUMBER,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up HWKettle integration from a config entry."""
    if DOMAIN not in hass.data: hass.data[DOMAIN] = {}
    if entry.entry_id not in hass.data: hass.data[DOMAIN][entry.entry_id] = {}

    email = entry.data[CONF_EMAIL]
    password = entry.data[CONF_PASSWORD]
    kettle_id = entry.data[CONF_KETTLE_ID]

    kettle = KettleConnection(
        hass=hass,
        username=email,
        password=password,
        kettle_id=entry.data[CONF_KETTLE_ID],
    )
    await kettle.start_listening()

    hass.data[DOMAIN][entry.entry_id][DATA_CONNECTION] = kettle
    hass.data[DOMAIN][DATA_DEVICE_INFO] = lambda: device_info(entry)

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True


def device_info(entry):
    return DeviceInfo(
        name=(FRIENDLY_NAME + " " + entry.data.get(CONF_FRIENDLY_NAME, "")).strip(),
        manufacturer=MANUFACTORER,
        model=entry.data.get(CONF_KETTLE_ID, None),
        sw_version="?",
        identifiers={
            (DOMAIN, entry.data[CONF_KETTLE_ID])
        },
        connections={
            ("kettle_id", entry.data[CONF_KETTLE_ID])
        }
    )

