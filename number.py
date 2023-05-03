"""HWSwitch."""
import logging

from homeassistant.components.number import NumberDeviceClass, NumberEntity
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
        HWTemperatureNumber(hass, entry),
        HWKeepWarmTime(hass, entry),
    ])


class HWTemperatureNumber(CoordinatorEntity, NumberEntity):
    """Representation of a HWKettle switch device."""

    def __init__(self, hass, entry):
        """Initialize the switch device."""
        self.hass = hass
        self.entry = entry
        super().__init__(self.kettle)

    @property
    def kettle(self):
        return self.hass.data[DOMAIN][self.entry.entry_id][DATA_CONNECTION]

    @property
    def native_min_value(self):
        return 40

    @property
    def native_max_value(self):
        return 100

    @property
    def native_step(self):
        return 5

    @property
    def native_unit_of_measurement(self):
        return UnitOfTemperature.CELSIUS

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_target_temperature_number"

    @property
    def name(self):
        """Name of the entity."""
        return (FRIENDLY_NAME + " " + self.entry.data.get(CONF_FRIENDLY_NAME, "")).strip() + " Target Temperature"

    @property
    def icon(self):
        return "mdi:thermometer"

    @property
    def device_class(self):
        return NumberDeviceClass.TEMPERATURE

    @property
    def device_info(self):
        return self.hass.data[DOMAIN][DATA_DEVICE_INFO]()

    @property
    def should_poll(self):
        return False

    @property
    def native_value(self):        
        return self.kettle.get_kettle().get_target_temperature()

    async def async_set_native_value(self, value: float) -> None:
        self.kettle.get_kettle().set_target_temperature(value)
        await self.kettle.update()


class HWKeepWarmTime(CoordinatorEntity, NumberEntity):
    """Representation of a HWKettle switch device."""

    def __init__(self, hass, entry):
        """Initialize the switch device."""
        self.hass = hass
        self.entry = entry
        super().__init__(self.kettle)

    @property
    def kettle(self):
        return self.hass.data[DOMAIN][self.entry.entry_id][DATA_CONNECTION]

    @property
    def native_min_value(self):
        return 5

    @property
    def native_max_value(self):
        return 120

    @property
    def native_step(self):
        return 5

    @property
    def native_unit_of_measurement(self):
        return "m"

    @property
    def unique_id(self):
        return f"{self.entry.entry_id}_keep_warm_time_minutes"

    @property
    def name(self):
        """Name of the entity."""
        return (FRIENDLY_NAME + " " + self.entry.data.get(CONF_FRIENDLY_NAME, "")).strip() + " Keep Warm Time"

    @property
    def icon(self):
        return "mdi:timer-outline"

    @property
    def device_class(self):
        return "m"

    @property
    def device_info(self):
        return self.hass.data[DOMAIN][DATA_DEVICE_INFO]()

    @property
    def should_poll(self):
        return False

    @property
    def native_value(self):        
        return self.kettle.get_kettle().get_keep_warm_set_time()

    async def async_set_native_value(self, value: float) -> None:
        self.kettle.get_kettle().set_keep_warm_set_time(value)
        await self.kettle.update()
