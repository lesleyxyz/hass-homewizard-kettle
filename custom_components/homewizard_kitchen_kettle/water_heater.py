"""HWWaterHeater."""
import logging
from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.helpers.dispatcher import async_dispatcher_send, async_dispatcher_connect
from homeassistant.const import *
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import callback
from hwkitchen import KettleStatus
from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities, discovery_info=None):
    """Set up the HWWaterHeater entry."""
    async_add_entities([HWWaterHeater(hass, entry)])


class HWWaterHeater(CoordinatorEntity, WaterHeaterEntity):
    """Representation of a HWWaterHeater water_heater device."""

    def __init__(self, hass, entry):
        """Initialize the water_heater device."""
        self.hass = hass
        self.entry = entry
        super().__init__(self.kettle)

    @property
    def kettle(self):
        return self.hass.data[DOMAIN][self.entry.entry_id][DATA_CONNECTION]

    @property
    def unique_id(self):
        return self.entry.entry_id

    @property
    def name(self):
        """Name of the entity."""
        return (FRIENDLY_NAME + " " + self.entry.data.get(CONF_FRIENDLY_NAME, "")).strip()

    @property
    def icon(self):
        return "mdi:kettle"

    @property
    def device_class(self):
        return None

    @property
    def device_info(self):
        return self.hass.data[DOMAIN][DATA_DEVICE_INFO]()

    @property
    def should_poll(self):
        return False

    @property
    def assumed_state(self):
        return False

    @property
    def available(self):
        return True if self.kettle.get_kettle() else False

    @property
    def entity_category(self):
        return None

    @property
    def supported_features(self):
        return WaterHeaterEntityFeature.TARGET_TEMPERATURE | WaterHeaterEntityFeature.OPERATION_MODE

    @property
    def temperature_unit(self):
        return UnitOfTemperature.CELSIUS

    @property
    def min_temp(self):
        return 40

    @property
    def max_temp(self):
        return 100

    @property
    def precision(self) -> float:
        return 5

    @property
    def operation_list(self):
        return ["Off", "On"]

    @property
    def extra_state_attributes(self):
        kettle = self.kettle.get_kettle()
        return {
            **kettle.to_json().get("state", {}),
            "version": kettle.get_version(),
            "name": kettle.get_name(),
            "model": kettle.get_model(),
        }

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self.kettle.get_kettle().get_status() == KettleStatus.HEATING_TO_TARGET

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        self.kettle.get_kettle().start()
        await self.kettle.update()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        self.kettle.get_kettle().stop()
        await self.kettle.update()

    @property
    def current_temperature(self):
        return self.kettle.get_kettle().get_current_temperature()

    @property
    def target_temperature(self):
        return self.kettle.get_kettle().get_target_temperature()

    @property
    def current_operation(self):
        map = {
            KettleStatus.ON: "Idle",
            KettleStatus.HEATING_TO_TARGET: "Heating",
            KettleStatus.FINISHED_HEATING_TO_TARGET: "Heated",
            KettleStatus.KEEPING_WARM: "Keeping warm",
        }
        return map.get(self.kettle.get_kettle().get_status(), "Unknown")

    async def async_set_temperature(self, **kwargs):
        """Set new target temperatures."""
        target_temperature = kwargs.get(ATTR_TEMPERATURE)
        await self.kettle.set_target_temp(target_temperature)
        await self.kettle.update()

    async def async_set_operation_mode(self, operation_mode):
        """Set new operation mode."""
        if operation_mode == "Off":
            self.kettle.get_kettle().stop()
        elif operation_mode == "On":
            self.kettle.get_kettle().start()
        await self.kettle.update()
