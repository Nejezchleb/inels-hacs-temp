"""Inels switch entity."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from inelsmqtt.devices.switch import Switch

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_class import InelsBaseEntity
from .const import DEVICES, DOMAIN, ICON_SWITCH


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load Inels switch.."""
    device_list: list[Switch] = [
        dev
        for dev in hass.data[DOMAIN][config_entry.entry_id][DEVICES]
        if dev.device_type.value == Platform.SWITCH
    ]

    switches = [InelsSwitch(device) for device in device_list]

    async_add_entities(switches)


class InelsSwitch(InelsBaseEntity, SwitchEntity):
    """The platform class required by Home Assistant."""

    def __init__(self, device: Switch) -> None:
        """Initialize a switch."""
        super().__init__(device=device)

        self._state_attrs = {}
        self.set_state_attrs(self._device.features)

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        state = self._device.state

        return state.on

    @property
    def icon(self) -> str | None:
        """Switch icon."""
        return ICON_SWITCH

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Extra attributes if exists."""
        if self._state_attrs is None:
            return super().extra_state_attributes
        return self._state_attrs

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the switch to turn off."""
        if not self._device.is_available:
            return None
        await self.hass.async_add_executor_job(self._device.set_ha_value, False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the switch to turn on."""
        if not self._device.is_available:
            return None
        await self.hass.async_add_executor_job(self._device.set_ha_value, True)

    def set_state_attrs(self, features: dict[str, Any]) -> None:
        """Set state attributes."""
        if features is None:
            return

        for feature in features:
            self._state_attrs[feature] = self._device.state.__dict__.get(feature)

    def _callback(self, new_value: Any) -> None:
        """Get callback data from the broker."""
        self.set_state_attrs(self._device.features)

        super()._callback(new_value)
