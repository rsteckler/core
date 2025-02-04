"""Support for Magic Home select."""
from __future__ import annotations

from flux_led.aio import AIOWifiLedBulb
from flux_led.base_device import DeviceType
from flux_led.protocol import PowerRestoreState

from homeassistant import config_entries
from homeassistant.components.select import SelectEntity
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import FluxLedUpdateCoordinator
from .entity import FluxBaseEntity, FluxEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Flux selects."""
    coordinator: FluxLedUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    device = coordinator.device
    entities: list[
        FluxPowerStateSelect
        | FluxOperatingModesSelect
        | FluxWiringsSelect
        | FluxICTypeSelect
    ] = []
    name = entry.data[CONF_NAME]
    unique_id = entry.unique_id

    if device.device_type == DeviceType.Switch:
        entities.append(FluxPowerStateSelect(coordinator.device, entry))
    if device.operating_modes:
        entities.append(
            FluxOperatingModesSelect(
                coordinator, unique_id, f"{name} Operating Mode", "operating_mode"
            )
        )
    if device.wirings:
        entities.append(
            FluxWiringsSelect(coordinator, unique_id, f"{name} Wiring", "wiring")
        )
    if device.ic_types:
        entities.append(
            FluxICTypeSelect(coordinator, unique_id, f"{name} IC Type", "ic_type")
        )

    if entities:
        async_add_entities(entities)


def _human_readable_option(const_option: str) -> str:
    return const_option.replace("_", " ").title()


class FluxPowerStateSelect(FluxBaseEntity, SelectEntity):
    """Representation of a Flux power restore state option."""

    _attr_icon = "mdi:transmission-tower-off"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        device: AIOWifiLedBulb,
        entry: config_entries.ConfigEntry,
    ) -> None:
        """Initialize the power state select."""
        super().__init__(device, entry)
        self._attr_name = f"{entry.data[CONF_NAME]} Power Restored"
        if entry.unique_id:
            self._attr_unique_id = f"{entry.unique_id}_power_restored"
        self._name_to_state = {
            _human_readable_option(option.name): option for option in PowerRestoreState
        }
        self._attr_options = list(self._name_to_state)
        self._async_set_current_option_from_device()

    @callback
    def _async_set_current_option_from_device(self) -> None:
        """Set the option from the current power state."""
        restore_states = self._device.power_restore_states
        assert restore_states is not None
        assert restore_states.channel1 is not None
        self._attr_current_option = _human_readable_option(restore_states.channel1.name)

    async def async_select_option(self, option: str) -> None:
        """Change the power state."""
        await self._device.async_set_power_restore(channel1=self._name_to_state[option])
        self._async_set_current_option_from_device()
        self.async_write_ha_state()


class FluxConfigSelect(FluxEntity, SelectEntity):
    """Representation of a flux config entity that updates."""

    _attr_entity_category = EntityCategory.CONFIG


class FluxICTypeSelect(FluxConfigSelect):
    """Representation of Flux ic type."""

    _attr_icon = "mdi:chip"

    @property
    def options(self) -> list[str]:
        """Return the available ic types."""
        assert self._device.ic_types is not None
        return self._device.ic_types

    @property
    def current_option(self) -> str | None:
        """Return the current ic type."""
        return self._device.ic_type

    async def async_select_option(self, option: str) -> None:
        """Change the ic type."""
        await self._device.async_set_device_config(ic_type=option)


class FluxWiringsSelect(FluxConfigSelect):
    """Representation of Flux wirings."""

    _attr_icon = "mdi:led-strip-variant"

    @property
    def options(self) -> list[str]:
        """Return the available wiring options based on the strip protocol."""
        assert self._device.wirings is not None
        return self._device.wirings

    @property
    def current_option(self) -> str | None:
        """Return the current wiring."""
        return self._device.wiring

    async def async_select_option(self, option: str) -> None:
        """Change the wiring."""
        await self._device.async_set_device_config(wiring=option)


class FluxOperatingModesSelect(FluxConfigSelect):
    """Representation of Flux operating modes."""

    @property
    def options(self) -> list[str]:
        """Return the current operating mode."""
        assert self._device.operating_modes is not None
        return self._device.operating_modes

    @property
    def current_option(self) -> str | None:
        """Return the current operating mode."""
        return self._device.operating_mode

    async def async_select_option(self, option: str) -> None:
        """Change the ic type."""
        await self._device.async_set_device_config(operating_mode=option)
        # reload since we need to reinit the device
        self.hass.async_create_task(
            self.hass.config_entries.async_reload(self.coordinator.entry.entry_id)
        )
