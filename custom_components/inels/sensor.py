"""Inelse sensor entity."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from typing import Any
from inelsmqtt.devices.sensor import Sensor

from inelsmqtt.const import (
    BATTERY,
    TEMP_IN,
    TEMP_OUT,
    TEMPERATURE,
    Element,
)
from inelsmqtt.devices import Device

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, TEMP_CELSIUS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_class import InelsBaseEntity
from .const import DEVICES, DOMAIN, ICON_BATTERY, ICON_TEMPERATURE


@dataclass
class InelsSensorEntityDescriptionMixin:
    """Mixin keys."""

    value: Callable[[Device], Any | None]


@dataclass
class InelsSensorEntityDescription(
    SensorEntityDescription, InelsSensorEntityDescriptionMixin
):
    """Class for describing inels entities."""


def __get_temperature(device: Device) -> float | None:
    """Get temperature."""
    return getattr(device.state, TEMPERATURE)


def __get_temperature_out(device: Device) -> float | None:
    """Get output temperature."""
    return getattr(device.state, TEMP_OUT)


def __get_temperature_in(device: Device) -> float | None:
    """Get inside temperature."""
    return getattr(device.state, TEMP_IN)


def _get_battery(device: Device) -> int | None:
    """Get battery level."""
    return getattr(device.state, BATTERY)


def __get_values(device: Any) -> Any | None:
    """Get value from the state"""
    return device.state.__dict__.get()


SENSOR_DESCRIPTION_RFTI_10B: tuple[InelsSensorEntityDescription, ...] = (
    InelsSensorEntityDescription(
        key="battery_level",
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        icon=ICON_BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        value=_get_battery,
    ),
    InelsSensorEntityDescription(
        key="temp_in",
        name="Temperature In",
        device_class=SensorDeviceClass.TEMPERATURE,
        icon=ICON_TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        value=__get_temperature_in,
    ),
    InelsSensorEntityDescription(
        key="temp_out",
        name="Temperature Out",
        device_class=SensorDeviceClass.TEMPERATURE,
        icon=ICON_TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        value=__get_temperature_out,
    ),
)

SENSOR_DESCRIPTION_RFTC_10_G: tuple[InelsSensorEntityDescription, ...] = (
    InelsSensorEntityDescription(
        key="battery_level",
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        icon=ICON_BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        value=_get_battery,
    ),
    InelsSensorEntityDescription(
        key="temperature",
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        icon=ICON_TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        value=__get_temperature,
    ),
)


def create_entities_description(device: Sensor) -> dict[InelsSensorEntityDescription]:
    """Based on the deivce will create entity description."""
    items: dict[InelsSensorEntityDescription] = []

    for feature in device.features:
        icon = None
        dev_class = None
        measurement = None

        if feature == BATTERY:
            icon = ICON_BATTERY
            dev_class = SensorDeviceClass.BATTERY
            measurement = PERCENTAGE
        elif feature in [TEMPERATURE, TEMP_IN, TEMP_OUT]:
            icon = ICON_TEMPERATURE
            dev_class = SensorDeviceClass.TEMPERATURE
            measurement = TEMP_CELSIUS

        items.append(
            InelsSensorEntityDescription(
                key=feature,
                name=feature,
                device_class=dev_class,
                native_unit_of_measurement=measurement,
                icon=icon,
                value=__get_values,
            )
        )

    return items


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load Inels switch.."""
    device_list: list[Sensor] = [
        dev
        for dev in hass.data[DOMAIN][config_entry.entry_id][DEVICES]
        if dev.device_type.value == Platform.SENSOR
    ]

    entities: list[InelsSensor] = []

    for device in device_list:
        if device.inels_type == Element.RFTI_10B:
            descriptions = SENSOR_DESCRIPTION_RFTI_10B
        elif device.inels_type == Element.RFTC_10_G:
            descriptions = SENSOR_DESCRIPTION_RFTC_10_G
        else:
            continue

        for description in descriptions:
            entities.append(InelsSensor(device, description=description))

    async_add_entities(entities, True)


class InelsSensor(InelsBaseEntity, SensorEntity):
    """The platform class required by Home Assistant."""

    entity_description: InelsSensorEntityDescription

    def __init__(
        self,
        device: Sensor,
        description: InelsSensorEntityDescription,
    ) -> None:
        """Initialize a sensor."""
        super().__init__(device=device)

        self.entity_description = description
        self._attr_unique_id = f"{self._attr_unique_id}-{description.key}"

        if description.name:
            self._attr_name = f"{self._attr_name}-{description.name}"

        value = self.entity_description.value(self._device)

        self._attr_native_value = value

    async def async_added_to_hass(self) -> None:
        """Add subscription of the data listenere."""
        self.async_on_remove(
            self._device.subscribe_listerner(self._attr_unique_id, self._callback)
        )

    def _callback(self, new_value: Any) -> None:
        """Refresh data."""
        val = self.entity_description.value(self._device)
        self._attr_native_value = val

        super()._callback(new_value)
