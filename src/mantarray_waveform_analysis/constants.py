# -*- coding: utf-8 -*-
"""Global constants."""
import uuid

CENTIMILLISECONDS_PER_SECOND = 100000
TWITCH_PERIOD_UUID = uuid.UUID("6e0cd81c-7861-4c49-ba14-87b2739d65fb")
AMPLITUDE_UUID = uuid.UUID("89cf1105-a015-434f-b527-4169b9400e26")
AUC_UUID = uuid.UUID("e7b9a6e4-c43d-4e8b-af7e-51742e252030")
WIDTH_UUID = uuid.UUID("c4c60d55-017a-4783-9600-f19606de26f3")
WIDTH_VALUE_UUID = uuid.UUID("05041f4e-c77d-42d9-a2ae-8902f912e9ac")
WIDTH_RISING_COORDS_UUID = uuid.UUID("2a16acb6-4df7-4064-9d47-5d27ea7a98ad")
WIDTH_FALLING_COORDS_UUID = uuid.UUID("26e5637d-42c9-4060-aa5d-52209b349c84")

PRIOR_PEAK_INDEX_UUID = uuid.UUID("80df90dc-21f8-4cad-a164-89436909b30a")
PRIOR_VALLEY_INDEX_UUID = uuid.UUID("72ba9466-c203-41b6-ac30-337b4a17a124")
SUBSEQUENT_PEAK_INDEX_UUID = uuid.UUID("7e37325b-6681-4623-b192-39f154350f36")
SUBSEQUENT_VALLEY_INDEX_UUID = uuid.UUID("fd47ba6b-ee4d-4674-9a89-56e0db7f3d97")

BESSEL_BANDPASS_UUID = uuid.UUID("0ecf0e52-0a29-453f-a6ff-46f5ec3ae783")
BESSEL_LOWPASS_10_UUID = uuid.UUID("7d64cac3-b841-4912-b734-c0cf20a81e7a")

# GMR conversion factors
MIDSCALE_CODE = 0x800000
RAW_TO_SIGNED_CONVERSION_VALUE = 2 ** 23  # subtract this value from raw hardware data

# REFERENCE_VOLTAGE = 3.3

# ADC_GAIN = 32

MIN_NUMBER_PEAKS = 3
