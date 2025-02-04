"""Tests for Climacell weather entity."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import patch

import pytest

from homeassistant.components.climacell.config_flow import (
    _get_config_schema,
    _get_unique_id,
)
from homeassistant.components.climacell.const import (
    ATTR_CLOUD_COVER,
    ATTR_PRECIPITATION_TYPE,
    ATTR_WIND_GUST,
    ATTRIBUTION,
    DOMAIN,
)
from homeassistant.components.weather import (
    ATTR_CONDITION_CLOUDY,
    ATTR_CONDITION_RAINY,
    ATTR_CONDITION_SNOWY,
    ATTR_CONDITION_SUNNY,
    ATTR_FORECAST,
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED,
    ATTR_WEATHER_HUMIDITY,
    ATTR_WEATHER_OZONE,
    ATTR_WEATHER_PRESSURE,
    ATTR_WEATHER_TEMPERATURE,
    ATTR_WEATHER_VISIBILITY,
    ATTR_WEATHER_WIND_BEARING,
    ATTR_WEATHER_WIND_SPEED,
    DOMAIN as WEATHER_DOMAIN,
)
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_FRIENDLY_NAME,
    PRESSURE_HPA,
    SPEED_KILOMETERS_PER_HOUR,
)
from homeassistant.core import HomeAssistant, State, callback
from homeassistant.helpers.entity_registry import async_get
from homeassistant.util import dt as dt_util

from .const import API_V3_ENTRY_DATA, API_V4_ENTRY_DATA

from tests.common import MockConfigEntry


@callback
def _enable_entity(hass: HomeAssistant, entity_name: str) -> None:
    """Enable disabled entity."""
    ent_reg = async_get(hass)
    entry = ent_reg.async_get(entity_name)
    updated_entry = ent_reg.async_update_entity(
        entry.entity_id, **{"disabled_by": None}
    )
    assert updated_entry != entry
    assert updated_entry.disabled is False


async def _setup(hass: HomeAssistant, config: dict[str, Any]) -> State:
    """Set up entry and return entity state."""
    with patch(
        "homeassistant.util.dt.utcnow",
        return_value=datetime(2021, 3, 6, 23, 59, 59, tzinfo=dt_util.UTC),
    ):
        data = _get_config_schema(hass)(config)
        config_entry = MockConfigEntry(
            domain=DOMAIN,
            data=data,
            unique_id=_get_unique_id(hass, data),
            version=1,
        )
        config_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()
        for entity_name in ("hourly", "nowcast"):
            _enable_entity(hass, f"weather.climacell_{entity_name}")
        await hass.async_block_till_done()
        assert len(hass.states.async_entity_ids(WEATHER_DOMAIN)) == 3

    return hass.states.get("weather.climacell_daily")


async def test_v3_weather(
    hass: HomeAssistant,
    climacell_config_entry_update: pytest.fixture,
) -> None:
    """Test v3 weather data."""
    hass.config.units.wind_speed_unit = SPEED_KILOMETERS_PER_HOUR
    hass.config.units.pressure_unit = PRESSURE_HPA

    weather_state = await _setup(hass, API_V3_ENTRY_DATA)
    assert weather_state.state == ATTR_CONDITION_SUNNY
    assert weather_state.attributes[ATTR_ATTRIBUTION] == ATTRIBUTION
    assert weather_state.attributes[ATTR_FORECAST] == [
        {
            ATTR_FORECAST_CONDITION: ATTR_CONDITION_SUNNY,
            ATTR_FORECAST_TIME: "2021-03-07T00:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 0,
            ATTR_FORECAST_TEMP: 7,
            ATTR_FORECAST_TEMP_LOW: -5,
        },
        {
            ATTR_FORECAST_CONDITION: ATTR_CONDITION_CLOUDY,
            ATTR_FORECAST_TIME: "2021-03-08T00:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 0,
            ATTR_FORECAST_TEMP: 10,
            ATTR_FORECAST_TEMP_LOW: -4,
        },
        {
            ATTR_FORECAST_CONDITION: ATTR_CONDITION_CLOUDY,
            ATTR_FORECAST_TIME: "2021-03-09T00:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 0,
            ATTR_FORECAST_TEMP: 19,
            ATTR_FORECAST_TEMP_LOW: 0,
        },
        {
            ATTR_FORECAST_CONDITION: ATTR_CONDITION_CLOUDY,
            ATTR_FORECAST_TIME: "2021-03-10T00:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 0,
            ATTR_FORECAST_TEMP: 18,
            ATTR_FORECAST_TEMP_LOW: 3,
        },
        {
            ATTR_FORECAST_CONDITION: ATTR_CONDITION_CLOUDY,
            ATTR_FORECAST_TIME: "2021-03-11T00:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 5,
            ATTR_FORECAST_TEMP: 20,
            ATTR_FORECAST_TEMP_LOW: 9,
        },
        {
            ATTR_FORECAST_CONDITION: ATTR_CONDITION_CLOUDY,
            ATTR_FORECAST_TIME: "2021-03-12T00:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0.0457, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 25,
            ATTR_FORECAST_TEMP: 20,
            ATTR_FORECAST_TEMP_LOW: 12,
        },
        {
            ATTR_FORECAST_CONDITION: ATTR_CONDITION_CLOUDY,
            ATTR_FORECAST_TIME: "2021-03-13T00:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 25,
            ATTR_FORECAST_TEMP: 16,
            ATTR_FORECAST_TEMP_LOW: 7,
        },
        {
            ATTR_FORECAST_CONDITION: ATTR_CONDITION_RAINY,
            ATTR_FORECAST_TIME: "2021-03-14T00:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(1.0744, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 75,
            ATTR_FORECAST_TEMP: 6,
            ATTR_FORECAST_TEMP_LOW: 3,
        },
        {
            ATTR_FORECAST_CONDITION: ATTR_CONDITION_SNOWY,
            ATTR_FORECAST_TIME: "2021-03-15T00:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(7.3050, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 95,
            ATTR_FORECAST_TEMP: 1,
            ATTR_FORECAST_TEMP_LOW: 0,
        },
        {
            ATTR_FORECAST_CONDITION: ATTR_CONDITION_CLOUDY,
            ATTR_FORECAST_TIME: "2021-03-16T00:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0.0051, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 5,
            ATTR_FORECAST_TEMP: 6,
            ATTR_FORECAST_TEMP_LOW: -2,
        },
        {
            ATTR_FORECAST_CONDITION: ATTR_CONDITION_CLOUDY,
            ATTR_FORECAST_TIME: "2021-03-17T00:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 0,
            ATTR_FORECAST_TEMP: 11,
            ATTR_FORECAST_TEMP_LOW: 1,
        },
        {
            ATTR_FORECAST_CONDITION: ATTR_CONDITION_CLOUDY,
            ATTR_FORECAST_TIME: "2021-03-18T00:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 5,
            ATTR_FORECAST_TEMP: 12,
            ATTR_FORECAST_TEMP_LOW: 6,
        },
        {
            ATTR_FORECAST_CONDITION: ATTR_CONDITION_CLOUDY,
            ATTR_FORECAST_TIME: "2021-03-19T00:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0.1778, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 45,
            ATTR_FORECAST_TEMP: 9,
            ATTR_FORECAST_TEMP_LOW: 5,
        },
        {
            ATTR_FORECAST_CONDITION: ATTR_CONDITION_RAINY,
            ATTR_FORECAST_TIME: "2021-03-20T00:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(1.2319, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 55,
            ATTR_FORECAST_TEMP: 5,
            ATTR_FORECAST_TEMP_LOW: 3,
        },
        {
            ATTR_FORECAST_CONDITION: ATTR_CONDITION_CLOUDY,
            ATTR_FORECAST_TIME: "2021-03-21T00:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0.0432, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 20,
            ATTR_FORECAST_TEMP: 7,
            ATTR_FORECAST_TEMP_LOW: 1,
        },
    ]
    assert weather_state.attributes[ATTR_FRIENDLY_NAME] == "ClimaCell - Daily"
    assert weather_state.attributes[ATTR_WEATHER_HUMIDITY] == 24
    assert weather_state.attributes[ATTR_WEATHER_OZONE] == 52.625
    assert weather_state.attributes[ATTR_WEATHER_PRESSURE] == 1028.12
    assert weather_state.attributes[ATTR_WEATHER_TEMPERATURE] == 7
    assert weather_state.attributes[ATTR_WEATHER_VISIBILITY] == 9.99
    assert weather_state.attributes[ATTR_WEATHER_WIND_BEARING] == 320.31
    assert weather_state.attributes[ATTR_WEATHER_WIND_SPEED] == 14.63
    assert weather_state.attributes[ATTR_CLOUD_COVER] == 100
    assert weather_state.attributes[ATTR_WIND_GUST] == 24.0758
    assert weather_state.attributes[ATTR_PRECIPITATION_TYPE] == "rain"


async def test_v4_weather(
    hass: HomeAssistant,
    climacell_config_entry_update: pytest.fixture,
) -> None:
    """Test v4 weather data."""
    hass.config.units.wind_speed_unit = SPEED_KILOMETERS_PER_HOUR
    hass.config.units.pressure_unit = PRESSURE_HPA

    weather_state = await _setup(hass, API_V4_ENTRY_DATA)
    assert weather_state.state == ATTR_CONDITION_SUNNY
    assert weather_state.attributes[ATTR_ATTRIBUTION] == ATTRIBUTION
    assert weather_state.attributes[ATTR_FORECAST] == [
        {
            ATTR_FORECAST_CONDITION: ATTR_CONDITION_SUNNY,
            ATTR_FORECAST_TIME: "2021-03-07T11:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 0,
            ATTR_FORECAST_TEMP: 8,
            ATTR_FORECAST_TEMP_LOW: -3,
            ATTR_FORECAST_WIND_BEARING: 239.6,
            ATTR_FORECAST_WIND_SPEED: pytest.approx(15.2727, abs=0.01),
        },
        {
            ATTR_FORECAST_CONDITION: "cloudy",
            ATTR_FORECAST_TIME: "2021-03-08T11:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 0,
            ATTR_FORECAST_TEMP: 10,
            ATTR_FORECAST_TEMP_LOW: -3,
            ATTR_FORECAST_WIND_BEARING: 262.82,
            ATTR_FORECAST_WIND_SPEED: pytest.approx(11.6517, abs=0.01),
        },
        {
            ATTR_FORECAST_CONDITION: "cloudy",
            ATTR_FORECAST_TIME: "2021-03-09T11:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 0,
            ATTR_FORECAST_TEMP: 19,
            ATTR_FORECAST_TEMP_LOW: 0,
            ATTR_FORECAST_WIND_BEARING: 229.3,
            ATTR_FORECAST_WIND_SPEED: pytest.approx(11.3459, abs=0.01),
        },
        {
            ATTR_FORECAST_CONDITION: "cloudy",
            ATTR_FORECAST_TIME: "2021-03-10T11:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 0,
            ATTR_FORECAST_TEMP: 18,
            ATTR_FORECAST_TEMP_LOW: 3,
            ATTR_FORECAST_WIND_BEARING: 149.91,
            ATTR_FORECAST_WIND_SPEED: pytest.approx(17.1234, abs=0.01),
        },
        {
            ATTR_FORECAST_CONDITION: "cloudy",
            ATTR_FORECAST_TIME: "2021-03-11T11:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 0,
            ATTR_FORECAST_TEMP: 19,
            ATTR_FORECAST_TEMP_LOW: 9,
            ATTR_FORECAST_WIND_BEARING: 210.45,
            ATTR_FORECAST_WIND_SPEED: pytest.approx(25.2506, abs=0.01),
        },
        {
            ATTR_FORECAST_CONDITION: "rainy",
            ATTR_FORECAST_TIME: "2021-03-12T11:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0.1219, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 25,
            ATTR_FORECAST_TEMP: 20,
            ATTR_FORECAST_TEMP_LOW: 12,
            ATTR_FORECAST_WIND_BEARING: 217.98,
            ATTR_FORECAST_WIND_SPEED: pytest.approx(19.7949, abs=0.01),
        },
        {
            ATTR_FORECAST_CONDITION: "cloudy",
            ATTR_FORECAST_TIME: "2021-03-13T11:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 25,
            ATTR_FORECAST_TEMP: 12,
            ATTR_FORECAST_TEMP_LOW: 6,
            ATTR_FORECAST_WIND_BEARING: 58.79,
            ATTR_FORECAST_WIND_SPEED: pytest.approx(15.6428, abs=0.01),
        },
        {
            ATTR_FORECAST_CONDITION: "snowy",
            ATTR_FORECAST_TIME: "2021-03-14T10:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(23.9573, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 95,
            ATTR_FORECAST_TEMP: 6,
            ATTR_FORECAST_TEMP_LOW: 1,
            ATTR_FORECAST_WIND_BEARING: 70.25,
            ATTR_FORECAST_WIND_SPEED: pytest.approx(26.1518, abs=0.01),
        },
        {
            ATTR_FORECAST_CONDITION: "snowy",
            ATTR_FORECAST_TIME: "2021-03-15T10:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(1.4630, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 55,
            ATTR_FORECAST_TEMP: 6,
            ATTR_FORECAST_TEMP_LOW: -1,
            ATTR_FORECAST_WIND_BEARING: 84.47,
            ATTR_FORECAST_WIND_SPEED: pytest.approx(25.5725, abs=0.01),
        },
        {
            ATTR_FORECAST_CONDITION: "cloudy",
            ATTR_FORECAST_TIME: "2021-03-16T10:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 0,
            ATTR_FORECAST_TEMP: 6,
            ATTR_FORECAST_TEMP_LOW: -2,
            ATTR_FORECAST_WIND_BEARING: 103.85,
            ATTR_FORECAST_WIND_SPEED: pytest.approx(10.7987, abs=0.01),
        },
        {
            ATTR_FORECAST_CONDITION: "cloudy",
            ATTR_FORECAST_TIME: "2021-03-17T10:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 0,
            ATTR_FORECAST_TEMP: 11,
            ATTR_FORECAST_TEMP_LOW: 1,
            ATTR_FORECAST_WIND_BEARING: 145.41,
            ATTR_FORECAST_WIND_SPEED: pytest.approx(11.6999, abs=0.01),
        },
        {
            ATTR_FORECAST_CONDITION: "cloudy",
            ATTR_FORECAST_TIME: "2021-03-18T10:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(0, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 10,
            ATTR_FORECAST_TEMP: 12,
            ATTR_FORECAST_TEMP_LOW: 5,
            ATTR_FORECAST_WIND_BEARING: 62.99,
            ATTR_FORECAST_WIND_SPEED: pytest.approx(10.5895, abs=0.01),
        },
        {
            ATTR_FORECAST_CONDITION: "rainy",
            ATTR_FORECAST_TIME: "2021-03-19T10:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(2.9261, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 55,
            ATTR_FORECAST_TEMP: 9,
            ATTR_FORECAST_TEMP_LOW: 4,
            ATTR_FORECAST_WIND_BEARING: 68.54,
            ATTR_FORECAST_WIND_SPEED: pytest.approx(22.3860, abs=0.01),
        },
        {
            ATTR_FORECAST_CONDITION: "snowy",
            ATTR_FORECAST_TIME: "2021-03-20T10:00:00+00:00",
            ATTR_FORECAST_PRECIPITATION: pytest.approx(1.2192, abs=0.01),
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: 33.3,
            ATTR_FORECAST_TEMP: 5,
            ATTR_FORECAST_TEMP_LOW: 2,
            ATTR_FORECAST_WIND_BEARING: 56.98,
            ATTR_FORECAST_WIND_SPEED: pytest.approx(27.9221, abs=0.01),
        },
    ]
    assert weather_state.attributes[ATTR_FRIENDLY_NAME] == "ClimaCell - Daily"
    assert weather_state.attributes[ATTR_WEATHER_HUMIDITY] == 23
    assert weather_state.attributes[ATTR_WEATHER_OZONE] == 46.53
    assert weather_state.attributes[ATTR_WEATHER_PRESSURE] == 1027.77
    assert weather_state.attributes[ATTR_WEATHER_TEMPERATURE] == 7
    assert weather_state.attributes[ATTR_WEATHER_VISIBILITY] == 13.12
    assert weather_state.attributes[ATTR_WEATHER_WIND_BEARING] == 315.14
    assert weather_state.attributes[ATTR_WEATHER_WIND_SPEED] == 15.02
    assert weather_state.attributes[ATTR_CLOUD_COVER] == 100
    assert weather_state.attributes[ATTR_WIND_GUST] == 20.3421
    assert weather_state.attributes[ATTR_PRECIPITATION_TYPE] == "rain"
