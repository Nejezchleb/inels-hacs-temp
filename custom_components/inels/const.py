"""Constants for the iNels integration."""
import logging

from homeassistant.const import Platform

DOMAIN = "inels"

BROKER_CONFIG = "inels_mqtt_broker_config"
BROKER = "inels_mqtt_broker"
DEVICES = "devices"

CONF_DISCOVERY_PREFIX = "discovery_prefix"

TITLE = "iNELS"
DESCRIPTION = ""
INELS_VERSION = 1
LOGGER = logging.getLogger(__package__)

DEFAULT_MIN_TEMP = 10.0  # °C
DEFAULT_MAX_TEMP = 50.0  # °C

ICON_TEMPERATURE = "mdi:thermometer"
ICON_BATTERY = "mdi:battery-50"
ICON_SWITCH = "mdi:power-socket-eu"
ICON_LIGHT = "mdi:lightbulb"
ICON_SHUTTER_CLOSED = "mdi:window-shutter"
ICON_SHUTTER_OPEN = "mdi:window-shutter-open"
ICON_BUTTON = "mdi:button-pointer"

ICON_WATER_HEATER_DICT = {
    "on": "mdi:valve-open",
    "off": "mdi:valve-closed",
}

ICONS = {
    Platform.SWITCH: ICON_SWITCH,
    Platform.SENSOR: ICON_TEMPERATURE,
    Platform.BUTTON: ICON_BUTTON,
    Platform.LIGHT: ICON_LIGHT,
}

MANUAL_SETUP = "manual"

BUTTON_PRESS_STATE = "press"
BUTTON_NO_ACTION_STATE = "no_action"
