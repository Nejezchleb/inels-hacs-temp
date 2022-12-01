"""iNels light."""
from __future__ import annotations

from typing import Any, cast
from inelsmqtt.devices.light import Light

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_TRANSITION,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_class import InelsBaseEntity
from .const import DEVICES, DOMAIN, ICON_LIGHT


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load Inels lights from config entry."""
    device_list: list[Light] = [
        dev
        for dev in hass.data[DOMAIN][config_entry.entry_id][DEVICES]
        if dev.device_type.value == Platform.LIGHT
    ]

    lights = [InelsLight(device) for device in device_list]

    async_add_entities(lights)


class InelsLight(InelsBaseEntity, LightEntity):
    """Light class for HA."""

    def __init__(self, device: Light) -> None:
        """Initialize a light."""
        super().__init__(device=device)

        self._attr_supported_color_modes: set[ColorMode] = set()

        for feature in self._device.features:
            self._attr_supported_color_modes.add(feature)

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._device.state > 0

    @property
    def icon(self) -> str | None:
        """Light icon."""
        return ICON_LIGHT

    @property
    def brightness(self) -> int | None:
        """Light brightness."""
        if ATTR_BRIGHTNESS in self._device.features:
            return cast(int, self._device.state * 2.55)
        # there is not brightness feature presented
        return None

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Light to turn off."""
        if not self._device:
            return

        transition = None

        if ATTR_TRANSITION in kwargs:
            transition = int(kwargs[ATTR_TRANSITION]) / 0.065
            print(transition)
        else:
            await self.hass.async_add_executor_job(self._device.set_ha_value, 0)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Light to turn on."""
        if not self._device:
            return

        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(kwargs[ATTR_BRIGHTNESS] / 2.55)
            brightness = min(brightness, 100)

            await self.hass.async_add_executor_job(
                self._device.set_ha_value, brightness
            )
        else:
            await self.hass.async_add_executor_job(self._device.set_ha_value, 100)
