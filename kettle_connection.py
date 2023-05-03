import logging
import asyncio
from time import monotonic
from homeassistant.components import bluetooth
from bleak import BleakScanner, BleakClient
from .const import *
import traceback
import json
import math
from hwkitchen import HWSocket, Kettle
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)


class KettleConnection(DataUpdateCoordinator):
    def __init__(self, hass, username: str, password: str, kettle_id: str):
        super().__init__(
			hass,
			_LOGGER,
			name="Kettle Connection Coordinator",
		)
        self.hass = hass
        self._kettle_id = kettle_id
        self._ws_client = HWSocket(username, password)
        self._kettle = None
        
        self._auth_ok = False
        self._last_set_target = 0
        self._last_auth_ok = False
        self._target_boil_time = None
        self._status = None
        self._disposed = False

    async def start_listening(self):
        future = asyncio.get_event_loop().create_future()
        callback = lambda: (future.set_result(True))
        asyncio.create_task(self._ws_client.connect(callback))

        try:
            await asyncio.wait_for(future, timeout=60)
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout waiting for connection callback")

        self._kettle = await self._ws_client.subscribe_device(self._kettle_id, self._on_new_status)
        _LOGGER.error("Got kettle " + json.dumps(self._kettle.to_json()))

    async def _on_new_status(self, kettle: Kettle):
        # Get the latest status
        self._kettle = kettle
        self.async_set_updated_data(kettle)

    def get_kettle(self) -> Kettle:
        return self._kettle

    async def update(self):
        await self._ws_client.update(self._kettle)

    @property
    def available(self):
        return self._last_auth_ok

    @staticmethod
    def limit_temp(temp):
        if temp != None and temp > 100:
            return 100
        elif temp != None and temp < 40:
            return 40
        else:
            return temp

    async def set_target_temp(self, target_temp):
        """Set new temperature."""
        if target_temp < self.get_kettle().get_target_temperature():
            target_temp = 5 * math.floor(target_temp / 5)
        else:
            target_temp = 5 * math.ceil(target_temp / 5)

        self._kettle.set_target_temperature(self.limit_temp(target_temp))

    @property
    def connected(self):
        return True if self._kettle else False

    @property
    def boil_time(self):
        if not self._status: return None
        return self._status.boil_time

    async def set_boil_time(self, value):
        value = int(value)
        _LOGGER.info(f"Setting boil time to {value}")
        self._target_boil_time = value
        await self.update()

