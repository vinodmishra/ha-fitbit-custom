"""Services for the Fitbit integration."""

import datetime
import logging

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from fitbit_web_api.api import BodyApi

from .const import DOMAIN
from .coordinator import FitbitData
from .body_fat_calculator import Gender, calculate_body_fat

_LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Register services for Fitbit."""

    async def _get_body_api(hass: HomeAssistant) -> tuple[BodyApi, any]:
        """Get the body API and fitbit_api from the first available config entry."""
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("No Fitbit config entries found.")

        entry = entries[0]
        if not hasattr(entry, "runtime_data") or entry.runtime_data is None:
            raise HomeAssistantError("Fitbit integration not ready.")

        fitbit_data: FitbitData = entry.runtime_data
        fitbit_api = fitbit_data.api

        # We need the ApiClient
        client = await fitbit_api._async_get_fitbit_web_api()
        return BodyApi(client), fitbit_api

    async def log_body_measurements(call: ServiceCall) -> None:
        """Log body measurements (weight and/or fat)."""
        weight = call.data.get("weight")
        fat = call.data.get("fat")
        impedance = call.data.get("impedance")
        date = call.data.get("date", datetime.date.today())
        time = call.data.get("time", datetime.datetime.now().strftime("%H:%M:%S"))

        if isinstance(time, datetime.time):
            time = time.strftime("%H:%M:%S")

        body_api, fitbit_api = await _get_body_api(hass)

        if weight is not None:
            _LOGGER.debug("Logging weight: %s on %s at %s", weight, date, time)
            await fitbit_api._run_async(
                lambda: body_api.add_weight_log(weight=weight, var_date=date, time=time)
            )

        if fat is None and impedance is not None and weight is not None:
            # We need to calculate body fat
            height = None
            birth_date = None
            gender_str = None

            # Fetch missing info from profile
            try:
                profile = await fitbit_api.async_get_user_profile()
                height = getattr(profile, "height", 0)
                birth_date_val = getattr(profile, "date_of_birth", None)
                if birth_date_val:
                    if isinstance(birth_date_val, str):
                        birth_date = datetime.datetime.strptime(
                            birth_date_val, "%Y-%m-%d"
                        ).date()
                    elif isinstance(birth_date_val, datetime.date):
                        birth_date = birth_date_val
                    else:
                        birth_date = None
                gender_str = getattr(profile, "gender", None)
                if gender_str:
                    gender_str = gender_str.upper()
            except Exception as e:
                _LOGGER.warning(
                    "Could not fetch profile for body fat calculation: %s", e
                )

            if not all([height, birth_date, gender_str]):
                raise HomeAssistantError(
                    "Missing profile data for body fat calculation."
                )

            try:
                gender = Gender(gender_str)
            except ValueError:
                raise HomeAssistantError(
                    f"Invalid gender: {gender_str}. Must be MALE or FEMALE."
                )

            fat = calculate_body_fat(
                gender=gender,
                date_of_birth=birth_date,
                weight=weight,
                height=height,
                impedance=impedance,
            )

            if fat is None:
                raise HomeAssistantError(
                    "Body fat calculation returned None. Check input parameters."
                )

        if fat is not None:
            _LOGGER.debug("Logging body fat: %s on %s at %s", fat, date, time)
            await fitbit_api._run_async(
                lambda: body_api.add_body_fat_log(fat=fat, var_date=date, time=time)
            )

    hass.services.async_register(DOMAIN, "log_body_measurements", log_body_measurements)
