"""HWSwitch."""
import logging

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.dispatcher import async_dispatcher_send, async_dispatcher_connect
from homeassistant.const import *
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback

from .const import *
from hwkitchen import KettleStatus

_LOGGER = logging.getLogger(__name__)


SWITCH_MAIN = "switch"
SWITCH_BBT = "boil before target"
SWITCH_KW = "keep warm"


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the HWKettle entry."""
    async_add_entities([
        HWSwitch(hass, entry, SWITCH_MAIN),
        HWSwitch(hass, entry, SWITCH_BBT),
        HWSwitch(hass, entry, SWITCH_KW),
    ])


class HWSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a HWKettle switch device."""

    def __init__(self, hass, entry, switch_type):
        """Initialize the switch device."""
        self.hass = hass
        self.entry = entry
        self.switch_type = switch_type
        super().__init__(self.kettle)

    @property
    def kettle(self):
        return self.hass.data[DOMAIN][self.entry.entry_id][DATA_CONNECTION]

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_{self.switch_type}"

    @property
    def name(self):
        """Name of the entity."""
        return (FRIENDLY_NAME + " " + self.entry.data.get(CONF_FRIENDLY_NAME, "")).strip() + " " + self.switch_type 

    @property
    def icon(self):
        if self.switch_type == SWITCH_MAIN:
            return "mdi:kettle-steam"
        if self.switch_type == SWITCH_BBT:
            return "mdi:chart-sankey"
        if self.switch_type == SWITCH_KW:
            return "mdi:heat-wave"

    @property
    def device_class(self):
        return SwitchDeviceClass.SWITCH

    @property
    def device_info(self):
        return self.hass.data[DOMAIN][DATA_DEVICE_INFO]()

    @property
    def should_poll(self):
        return False

    @property
    def available(self):        
        return True

    @property
    def entity_category(self):
        if self.switch_type == SWITCH_MAIN:
            return None
        if self.switch_type == SWITCH_BBT:
            return EntityCategory.CONFIG
        if self.switch_type == SWITCH_KW:
            return EntityCategory.CONFIG

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        if self.switch_type == SWITCH_MAIN:
            return self.kettle.get_kettle().get_status() == KettleStatus.HEATING_TO_TARGET
        if self.switch_type == SWITCH_BBT:
            return self.kettle.get_kettle().get_boil_before_target()
        if self.switch_type == SWITCH_KW:
            return self.kettle.get_kettle().get_keep_warm_enabled()

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        if self.switch_type == SWITCH_MAIN:
            self.kettle.get_kettle().start()
        if self.switch_type == SWITCH_BBT:
            self.kettle.get_kettle().set_boil_before_target(True)
        if self.switch_type == SWITCH_KW:
            self.kettle.get_kettle().set_keep_warm_enabled(True)

        await self.kettle.update()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        if self.switch_type == SWITCH_MAIN:
            self.kettle.get_kettle().stop()
        if self.switch_type == SWITCH_BBT:
            self.kettle.get_kettle().set_boil_before_target(False)
        if self.switch_type == SWITCH_KW:
            self.kettle.get_kettle().set_keep_warm_enabled(False)

        await self.kettle.update()
