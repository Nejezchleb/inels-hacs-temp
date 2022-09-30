"""Support for iNELS buttons."""
from __future__ import annotations

from typing import Any
from dataclasses import dataclass

from inelsmqtt.devices import Device

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
    ButtonDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory

from .base_class import InelsBaseEntity
from .const import (
    DEVICES,
    DOMAIN,
    ICON_BUTTON,
    BUTTON_PRESS_STATE,
    BUTTON_NO_ACTION_STATE,
)


@dataclass
class InelsButtonDescription(ButtonEntityDescription):
    """A class that describes button entity."""


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load Inels water heater from config entry."""
    device_list: list[Device] = hass.data[DOMAIN][config_entry.entry_id][DEVICES]

    entities = []

    for device in device_list:
        if device.device_type == Platform.BUTTON:
            index = 1
            val = device.get_value()
            if val.ha_value is not None:
                while index <= val.ha_value.amount:
                    entities.append(
                        InelsButton(
                            device=device,
                            description=InelsButtonDescription(
                                key=f"{index}",
                                name=f"btn {index}",
                                icon=ICON_BUTTON,
                                entity_category=EntityCategory.CONFIG,
                            ),
                        )
                    )
                    index += 1

    async_add_entities(entities)


class InelsButton(InelsBaseEntity, ButtonEntity):
    """Button switch can be toogled using with MQTT."""

    entity_description: InelsButtonDescription
    _attr_device_class: ButtonDeviceClass = ButtonDeviceClass.RESTART

    def __init__(self, device: Device, description: InelsButtonDescription) -> None:
        """Initialize a button."""
        super().__init__(device=device)
        self.entity_description = description

        self._attr_unique_id = f"{self._attr_unique_id}-{description.key}"

        if description.name:
            self._attr_name = f"{self._attr_name}-{description.name}"

    def __process_state(self) -> None:
        """Process state button life cycle."""
        state = (
            BUTTON_PRESS_STATE
            if self._device.values.ha_value.pressing
            else BUTTON_NO_ACTION_STATE
        )

        self.hass.states.set(
            f"{Platform.BUTTON}.{self._device_id}_btn_{self._device.values.ha_value.number}",
            state,
        )
        self.async_write_ha_state()

    def _callback(self, new_value: Any) -> None:
        super()._callback(new_value)
        self.__process_state()

    async def async_press(self) -> None:
        """Press the button."""
