"""Support for Met.no weather service."""
import logging
import ctypes

import voluptuous as vol

from homeassistant.components.air_quality import AirQualityEntity

from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import (
    CONF_ELEVATION,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
    LENGTH_INCHES,
    LENGTH_KILOMETERS,
    LENGTH_MILES,
    LENGTH_MILLIMETERS,
    PRESSURE_HPA,
    PRESSURE_INHG,
    TEMP_CELSIUS,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from homeassistant.const import (
    TEMP_CELSIUS,
    PERCENTAGE,
    CONCENTRATION_PARTS_PER_MILLION,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_BILLION,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_HUMIDITY,
)

from .const import (
    DOMAIN,
    CONF_UMDNAME,
)

_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = (
    "RealTime Air Pollution Levels from apis.data.go.kr delivered by Air Korea."
)
DEFAULT_NAME = "Air Korea Open API"

MEASUREMENTS = [
    "particulate_matter_2_5",
    "particulate_matter_10",
    "sulphur_dioxide",
    "nitrogen_oxide",
    "carbon_monoxide",
    "ozone",
]

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add a weather entity from a config_entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    print(f"varsf(hass): {vars(hass)}")
    _LOGGER.info(f"coordinator: {coordinator}")
    print(f"coordinator: {coordinator}")
    print(f"config_entry: {config_entry}")
    print(f"config_entry.data: {config_entry.data}")

    entities = []
    for i,mesurement in enumerate(MEASUREMENTS):
        entities.append(PubAirWeather(coordinator, config_entry.data, True, mesurement,i))


    async_add_entities(entities)


class PubAirWeather(CoordinatorEntity, AirQualityEntity):
    """Implementation of a Met.no weather condition."""

    def __init__(self, coordinator, config, hourly, MEASUREMENTS,cnt):
        """Initialise the platform with a data instance and site."""
        super().__init__(coordinator)
        self._config = config
        self._hourly = hourly
        self._icon = "mdi:blur"
        self._data_type = MEASUREMENTS
        self._cnt = cnt #for debugging
        self._correction_value = 0
        
        print("init class!!!!!!!")

    #def listup_data(data):
    #     values = []

        
    @property
    def unique_id(self):
        """Return unique ID."""
        name_appendix = ""
        if self._hourly:
            name_appendix = "-hourly"

        return f"{self._config[CONF_UMDNAME]}{self._data_type}"

    @property
    def name(self):
        """Return the name of the sensor."""
        name = self._config.get(CONF_UMDNAME)
        name_appendix = ""
        if self._hourly:
            name_appendix = " Hourly123" #lovelace id

        if name is not None:
            return f"{name}{self._data_type}"

        return f"{DEFAULT_NAME}{self._data_type}"

    @property
    def icon(self):
        """Return the icon."""
        return self._icon

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        print(f"self._houly: {self._hourly}")
        return self._hourly


    @property
    def particulate_matter_2_5(self):
        pm2d5 = self.coordinator.data.current_airpollution_data["pm25Value"]
        try:
            return float(pm2d5)
        except Exception as e:
            print("error :",e )
            return float(self._correction_value)

    @property
    def particulate_matter_10(self):
        pm10 = self.coordinator.data.current_airpollution_data["pm10Value"]
        try:
            return float(pm10)
        except Exception as e:
            print("error :",e )
            return float(self._correction_value)

    @property
    def sulphur_dioxide(self):
        so2 = self.coordinator.data.current_airpollution_data["so2Value"]
        try:
            return float(so2)
        except Exception as e:
            print("error :",e )
            return float(self._correction_value)

    @property
    def nitrogen_oxide(self):
        no2 = self.coordinator.data.current_airpollution_data["no2Value"]
        try:
            return float(no2)
        except Exception as e:
            print("error :",e )
            return float(self._correction_value)

    @property
    def carbon_monoxide(self):
        co = self.coordinator.data.current_airpollution_data["coValue"]
        try:
            return float(co)
        except Exception as e:
            print("error :",e )
            return float(self._correction_value)

    @property
    def ozone(self):
        o3 = self.coordinator.data.current_airpollution_data["o3Value"]
        print("@property def ozone called")
        try:
            return float(o3)
        except Exception as e:
            print("error :",e )
            return float(self._correction_value)
    
    

    @property
    def state(self):
        if self._data_type == "particulate_matter_2_5":
            return self.particulate_matter_2_5

        elif self._data_type == "particulate_matter_10":
            return self.particulate_matter_10
        
        elif self._data_type == "sulphur_dioxide":
            return self.sulphur_dioxide

        elif self._data_type == "nitrogen_oxide":
            return self.nitrogen_oxide

        elif self._data_type == "carbon_monoxide":
            return self.carbon_monoxide
        
        elif self._data_type == "ozone":
            return self.ozone
    
    
    
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""

        if self._data_type == "particulate_matter_2_5":
            return CONCENTRATION_MICROGRAMS_PER_CUBIC_METER

        elif self._data_type == "particulate_matter_10":
            return CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
        
        elif self._data_type == "sulphur_dioxide":
            return CONCENTRATION_PARTS_PER_MILLION

        elif self._data_type == "nitrogen_oxide":
            return CONCENTRATION_PARTS_PER_MILLION

        elif self._data_type == "carbon_monoxide":
            return CONCENTRATION_PARTS_PER_MILLION
        
        elif self._data_type == "ozone":
            return CONCENTRATION_PARTS_PER_MILLION
        

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def device_info(self):
        """Device info."""
        return {
            "identifiers": {(DOMAIN,)},
            "manufacturer": "Air Korea",
            "model": "Real Time Air Pollution",
            "default_name": "Real Time Air Pollution",
            "entry_type": "service",
        }
