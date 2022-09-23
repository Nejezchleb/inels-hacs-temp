"""Inels switch entity."""
from __future__ import annotations

from typing import Any

from inelsmqtt.devices import Device

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
    device_list = hass.data[DOMAIN][config_entry.entry_id][DEVICES]

    async_add_entities(
        [
            InelsSwitch(device)
            for device in device_list
            if device.device_type == Platform.SWITCH
        ],
    )


class InelsSwitch(InelsBaseEntity, SwitchEntity):
    """The platform class required by Home Assistant."""

    def __init__(self, device: Device) -> None:
        """Initialize a switch."""
        super().__init__(device=device)

    @property
    def is_on(self) -> bool:
        """Return true if switch is on."""
        return self._device.state

    @property
    def icon(self) -> str | None:
        """Switch icon."""
        return ICON_SWITCH

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
