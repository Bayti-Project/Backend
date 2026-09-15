from apps.properties.models import Property

NEARBY_AREAS = {
    'beit_lahia': ['umm_al_nasr', 'jabalia_camp'],
    'umm_al_nasr': ['beit_lahia', 'jabalia_camp'],
    'jabalia_camp': ['umm_al_nasr', 'jabalia'],
    'jabalia': ['jabalia_camp', 'beit_hanoun'],
    'beit_hanoun': ['jabalia', 'gaza_city'],

    'gaza_city': ['shati_camp', 'beit_hanoun'],
    'shati_camp': ['gaza_city', 'mughraqa'],
    'mughraqa': ['shati_camp', 'juhr_al_dik'],
    'juhr_al_dik': ['mughraqa', 'zahra'],
    'zahra': ['juhr_al_dik', 'masdar'],

    'masdar': ['zahra', 'nuseirat'],
    'nuseirat': ['masdar', 'nuseirat_camp', 'bureij'],
    'nuseirat_camp': ['nuseirat', 'bureij'],
    'bureij': ['nuseirat_camp', 'zawayda'],
    'zawayda': ['bureij', 'maghazi'],
    'maghazi': ['zawayda', 'maghazi_camp'],
    'maghazi_camp': ['maghazi', 'wadi_salqa'],
    'wadi_salqa': ['maghazi_camp', 'deir_al_balah_camp'],
    'deir_al_balah_camp': ['wadi_salqa', 'deir_al_balah'],
    'deir_al_balah': ['deir_al_balah_camp', 'qarara'],

    'qarara': ['deir_al_balah', 'khan_younis_city'],
    'khan_younis_city': ['qarara', 'khan_younis_camp'],
    'khan_younis_camp': ['khan_younis_city', 'bani_suheila'],
    'bani_suheila': ['khan_younis_camp', 'abasan_kabira'],
    'abasan_kabira': ['bani_suheila', 'abasan_saghira'],
    'abasan_saghira': ['abasan_kabira', 'khuzaa'],
    'khuzaa': ['abasan_saghira', 'fukhari'],
    'fukhari': ['khuzaa', 'rafah_city'],

    'rafah_city': ['fukhari', 'rafah_camp'],
    'rafah_camp': ['rafah_city', 'nasr'],
    'nasr': ['rafah_camp', 'shawka'],
    'shawka': ['nasr'],
}


def get_nearby_areas(area_code):
    return NEARBY_AREAS.get(area_code, [])


ELECTRICITY_FIELD_MAP = {
    'solar': 'has_solar',
    'generator': 'has_generator_line',
    'main_grid': 'has_main_grid',
}

WATER_FIELD_MAP = {
    'tank': 'has_water_tank',
    'well': 'has_private_well',
}


class SearchValidationError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


def parse_decimal_param(params, key):
    raw = params.get(key)
    if raw is None or raw == '':
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        raise SearchValidationError(f"'{key}' must be a valid number.")
    if value < 0:
        raise SearchValidationError(f"'{key}' cannot be negative.")
    return value


def parse_int_param(params, key):
    raw = params.get(key)
    if raw is None or raw == '':
        return None
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise SearchValidationError(f"'{key}' must be a valid integer.")
    if value < 0:
        raise SearchValidationError(f"'{key}' cannot be negative.")
    return value


def parse_choice_param(params, key, valid_choices):
    raw = params.get(key)
    if raw is None or raw == '':
        return None
    if raw not in valid_choices:
        raise SearchValidationError(f"'{key}' has an invalid value.")
    return raw


def parse_multi_choice_param(params, key, field_map):
    raw = params.get(key)
    if raw is None or raw == '':
        return []
    values = [v.strip() for v in raw.split(',') if v.strip()]
    fields = []
    for v in values:
        if v not in field_map:
            raise SearchValidationError(f"'{key}' has an invalid value: '{v}'.")
        fields.append(field_map[v])
    return fields


def parse_area_param(params, governorate):
    area = params.get('area')
    if area is None or area == '':
        return None
    if area not in Property.AREA_TO_GOVERNORATE:
        raise SearchValidationError("'area' has an invalid value.")
    if governorate and Property.AREA_TO_GOVERNORATE[area] != governorate:
        raise SearchValidationError("'area' does not belong to the selected 'governorate'.")
    return area