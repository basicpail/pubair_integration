"""The pubair component."""
from datetime import timedelta
import logging
from random import randrange

from pubair import PubAir

from homeassistant.core import Config, HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, API_KEY, CONF_UMDNAME

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: Config) -> bool:
    """Set up configured PubAir"""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, config_entry):
    """Set up PubAir as config entry."""
    coordinator = PubAirDataUpdateCoordinator(hass, config_entry)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    print(f"coordinator: {coordinator}")
    print(f"dir(hass): {dir(hass)}")
    #print(f"hass.data: {hass.data}")
    print(f"dir(config_entry): {dir(config_entry)}")
    print(f"config_entry.entry_id: {config_entry.entry_id}")
    #config_id는 최초 등록 할 때 생성되는 난수이고, 재등록 하기 전까지는 변하지 않음

    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "air_quality")
    )

    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(config_entry, "air_quality")
    hass.data[DOMAIN].pop(config_entry.entry_id)

    return True


class PubAirDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Pub Air data."""

    def __init__(self, hass, config_entry):
        """Initialize global PubAir data updater."""
        self._unsub_track_home = None
        self.airpollution = AirPubPollutionData(hass, config_entry.data)
        self.airpollution.init_data()

        update_interval = timedelta(minutes=randrange(10, 15))
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    async def _async_update_data(self):
        """Fetch data from Air Pub"""
        _LOGGER.info("function _async_update_data was called")
        print("_async_update_data was called")
        try:
            return await self.airpollution.fetch_data()
        except Exception as err:
            raise UpdateFailed(f"Update failed: {err}") from err


class AirPubPollutionData:
    """Keep data for AirPub airpollution entities."""

    def __init__(self, hass, config):
        """Initialise the weather entity data."""
        self.hass = hass
        self._config = config
        self.current_airpollution_data = {}
        self.current_station_data = {}

    def init_data(self):
        """Location data inialization - get the coordinates."""
        self._pubair_data = PubAir(
            API_KEY, self._config.get(CONF_UMDNAME), async_get_clientsession(self.hass)
        )

    async def fetch_data(self):
        """Fetch data from API - (current particulate matter)."""
        await self._pubair_data.fetching_data()
        self.current_airpollution_data = self._pubair_data.get_current_airpollution()[
            "response"
        ]["body"]["items"][0]
        self.current_station_data = self._pubair_data.get_station_information()
        return self
