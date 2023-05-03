"""HWKettle."""
import logging

from homeassistant.components.sensor import SensorEntity, SensorStateClass, SensorDeviceClass
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import *
from homeassistant.core import callback

from .const import *

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPE_CURRENT_TEMPERATURE = "current_temperature"
SENSOR_TYPE_TARGET_TEMPERATURE = "target_temperature"


async def async_setup_entry(hass, entry, async_add_entities):
	"""Set up the HWKettle entry."""
	async_add_entities([
		HWKettleSensor(hass, entry, SENSOR_TYPE_CURRENT_TEMPERATURE),
		HWKettleSensor(hass, entry, SENSOR_TYPE_TARGET_TEMPERATURE),
	])


class HWKettleSensor(CoordinatorEntity, SensorEntity):
	"""Representation of a HWKettle sensor device."""

	def __init__(self, hass, entry, sensor_type):
		"""Initialize the sensor device."""
		self.hass = hass
		self.entry = entry
		self.sensor_type = sensor_type
		super().__init__(self.kettle)

	@property
	def kettle(self):
		return self.hass.data[DOMAIN][self.entry.entry_id][DATA_CONNECTION]

	@property
	def unique_id(self):
		return f"{self.entry.entry_id}_{self.sensor_type}"

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
	def last_reset(self):
		return None

	@property
	def name(self):
		"""Name of the entity."""
		if self.sensor_type == SENSOR_TYPE_CURRENT_TEMPERATURE:
			return (FRIENDLY_NAME + " " + self.entry.data.get(CONF_FRIENDLY_NAME, "")).strip() + " current temperature"
		if self.sensor_type == SENSOR_TYPE_TARGET_TEMPERATURE:
			return (FRIENDLY_NAME + " " + self.entry.data.get(CONF_FRIENDLY_NAME, "")).strip() + " target temperature"

	@property
	def icon(self):
		if self.sensor_type == SENSOR_TYPE_CURRENT_TEMPERATURE:
			return "mdi:thermometer"
		if self.sensor_type == SENSOR_TYPE_TARGET_TEMPERATURE:
			return "mdi:thermometer"
		return None

	@property
	def available(self):
		return True

	@property
	def entity_category(self):
		return None

	@property
	def device_class(self):
		if self.sensor_type == SENSOR_TYPE_CURRENT_TEMPERATURE:
			return SensorDeviceClass.TEMPERATURE
		if self.sensor_type == SENSOR_TYPE_TARGET_TEMPERATURE:
			return SensorDeviceClass.TEMPERATURE
		return None

	@property
	def state_class(self):
		if self.sensor_type == SENSOR_TYPE_CURRENT_TEMPERATURE:
			return SensorStateClass.MEASUREMENT
		if self.sensor_type == SENSOR_TYPE_TARGET_TEMPERATURE:
			return SensorStateClass.MEASUREMENT

	@property
	def native_unit_of_measurement(self):
		if self.sensor_type == SENSOR_TYPE_CURRENT_TEMPERATURE:
			return UnitOfTemperature.CELSIUS
		if self.sensor_type == SENSOR_TYPE_TARGET_TEMPERATURE:
			return UnitOfTemperature.CELSIUS
		return None

	@property
	def native_value(self):
		if self.sensor_type == SENSOR_TYPE_CURRENT_TEMPERATURE:
			return self.kettle.get_kettle().get_current_temperature()
		if self.sensor_type == SENSOR_TYPE_TARGET_TEMPERATURE:
			return self.kettle.get_kettle().get_target_temperature()
