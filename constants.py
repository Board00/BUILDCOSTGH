from enum import Enum

class RegionEnum(str, Enum):
    ahafo = "Ahafo"
    bono = "Bono"
    bono_east = "Bono East"
    central = "Central"
    accra = "Greater Accra"
    ashanti = "Ashanti"
    eastern = "Eastern"
    north_east = "North East"
    northern = "Northern"
    oti = "Oti"
    savannah = "Savannah"
    upper_east = "Upper East"
    upper_west = "Upper West"
    volta = "Volta"
    western = "Western"
    western_north = "Western North"

class MaterialItemEnum(str, Enum):
    cement = "Cement"
    sand = "Sand"
    stones = "Stones"
    iron_rods = "Iron Rods"
    wood = "Wood"
    tiles = "Tiles"
    paint = "Paint"
    plumbing = "Plumbing Materials"
    electricals = "Electrical Materials"
from enum import Enum

class DistrictEnum(str, Enum):
    # CENTRAL DISTRICTS
    abura_asebu_kwamankese = "Abura/Asebu/Kwamankese"
    agona_east = "Agona East"
    agona_west = "Agona West"
    ajumako_enyan_essiam = "Ajumako Enyan Essiam"
    asikuma_odoben_brakwa = "Asikuma Odoben Brakwa"
    assin_central = "Assin Central"
    assin_north = "Assin North"
    assin_south = "Assin South"
    awutu_senya_east = "Awutu Senya East"
    awutu_senya_west = "Awutu Senya West"
    cape_coast_metropolitan = "Cape Coast Metropolitan"
    effutu = "Effutu"
    ekumfi = "Ekumfi"
    gomoa_east = "Gomoa East"
    gomoa_central = "Gomoa Central"
    gomoa_west = "Gomoa West"
    komenda_edina_eguafo_abirem = "Komenda/Edina/Eguafo/Abirem"
    mfantsiman = "Mfantsiman"
    twifo_atti_morkwa = "Twifo Atti-Morkwa"
    twifo_hemang_lower_denkyira = "Twifo Hemang Lower Denkyira"
    upper_denkyira_east = "Upper Denkyira East"
    upper_denkyira_west = "Upper Denkyira West"

# GREATER ACCRA DISTRICTS
    ablekuma_central = "Ablekuma Central"
    ablekuma_north = "Ablekuma North"
    ablekuma_west = "Ablekuma West"
    accra_metropolitan = "Accra Metropolitan"
    ada_east = "Ada East"
    ada_west = "Ada West"
    adentan = "Adentan"
    ashaiman = "Ashaiman"
    ayawaso_central = "Ayawaso Central"
    ayawaso_east = "Ayawaso East"
    ayawaso_north = "Ayawaso North"
    ayawaso_west = "Ayawaso West"
    ga_central = "Ga Central"
    ga_east = "Ga East"
    ga_north = "Ga North"
    ga_south = "Ga South"
    ga_west = "Ga West"
    korle_klottey = "Korle Klottey"
    kpone_katamanso = "Kpone Katamanso"
    krowor = "Krowor"
    la_dade_kotopon = "La Dade-Kotopon"
    la_nkwantanang_madina = "La Nkwantanang Madina"
    ledzokuku = "Ledzokuku"
    ningo_prampram = "Ningo-Prampram"
    okaikwei_north = "Okaikwei North"
    shai_osudoku = "Shai Osudoku"
    tema_metropolitan = "Tema Metropolitan"
    tema_west = "Tema West"

# AHANTI DISTRICTS
    adansi_asokwa = "Adansi Asokwa"
    adansi_north = "Adansi North"
    adansi_south = "Adansi South"
    afigya_kwabre_north = "Afigya Kwabre North"
    afigya_kwabre_south = "Afigya Kwabre South"
    ahafo_ano_north = "Ahafo Ano North"
    ahafo_ano_south_east = "Ahafo Ano South East"
    ahafo_ano_south_west = "Ahafo Ano South West"
    amansie_central = "Amansie Central"
    amansie_west = "Amansie West"
    amansie_south = "Amansie South"
    asante_akim_central = "Asante Akim Central"
    asante_akim_north = "Asante Akim North"
    asante_akim_south = "Asante Akim South"
    asokore_mampong = "Asokore Mampong"
    asokwa = "Asokwa"
    atwima_kwanwoma = "Atwima Kwanwoma"
    atwima_mponua = "Atwima Mponua"
    atwima_nwabiagya_north = "Atwima Nwabiagya North"
    atwima_nwabiagya_south = "Atwima Nwabiagya South"
    bekwai_municipal = "Bekwai Municipal"
    bosome_freho = "Bosome Freho"
    bosomtwe = "Bosomtwe"
    ejisu = "Ejisu"
    ejura_sekyedumase = "Ejura-Sekyedumase"
    kumasi_metropolitan = "Kumasi Metropolitan"
    kwabre_east = "Kwabre East"
    kwadaso = "Kwadaso"
    mampong_municipal = "Mampong Municipal"
    obuasi_east = "Obuasi East"
    obuasi_municipal = "Obuasi Municipal"
    offinso_municipal = "Offinso Municipal"
    offinso_north = "Offinso North"
    oforikrom = "Oforikrom"
    old_tafo = "Old Tafo"
    sekyere_afram_plains = "Sekyere Afram Plains"
    sekyere_central = "Sekyere Central"
    sekyere_east = "Sekyere East"
    sekyere_kumawu = "Sekyere Kumawu"
    sekyere_south = "Sekyere South"
    suame = "Suame"
    suame_municipal = "Suame Municipal"
    suame_north = "Suame North"


REGION_DISTRICTS = {
    RegionEnum.central: frozenset({
        "Abura/Asebu/Kwamankese", "Agona East", "Agona West",
        "Ajumako Enyan Essiam", "Asikuma Odoben Brakwa", "Assin Central",
        "Assin North", "Assin South", "Awutu Senya East", "Awutu Senya West",
        "Cape Coast Metropolitan", "Effutu", "Ekumfi", "Gomoa East",
        "Gomoa Central", "Gomoa West", "Komenda/Edina/Eguafo/Abirem",
        "Mfantsiman", "Twifo Atti-Morkwa", "Twifo Hemang Lower Denkyira",
        "Upper Denkyira East", "Upper Denkyira West",
    }),
    RegionEnum.accra: frozenset({
        "Ablekuma Central", "Ablekuma North", "Ablekuma West",
        "Accra Metropolitan", "Ada East", "Ada West", "Adentan", "Ashaiman",
        "Ayawaso Central", "Ayawaso East", "Ayawaso North", "Ayawaso West",
        "Ga Central", "Ga East", "Ga North", "Ga South", "Ga West",
        "Korle Klottey", "Kpone Katamanso", "Krowor", "La Dade-Kotopon",
        "La Nkwantanang Madina", "Ledzokuku", "Ningo-Prampram",
        "Okaikwei North", "Shai Osudoku", "Tema Metropolitan", "Tema West",
    }),
    RegionEnum.ashanti: frozenset({
        "Adansi Asokwa", "Adansi North", "Adansi South", "Afigya Kwabre North",
        "Afigya Kwabre South", "Ahafo Ano North", "Ahafo Ano South East",
        "Ahafo Ano South West", "Amansie Central", "Amansie West",
        "Amansie South", "Asante Akim Central", "Asante Akim North",
        "Asante Akim South", "Asokore Mampong", "Asokwa", "Atwima Kwanwoma",
        "Atwima Mponua", "Atwima Nwabiagya North", "Atwima Nwabiagya South",
        "Bekwai Municipal", "Bosome Freho", "Bosomtwe", "Ejisu",
        "Ejura-Sekyedumase", "Kumasi Metropolitan", "Kwabre East", "Kwadaso",
        "Mampong Municipal", "Obuasi East", "Obuasi Municipal",
        "Offinso Municipal", "Offinso North", "Oforikrom", "Old Tafo",
        "Sekyere Afram Plains", "Sekyere Central", "Sekyere East",
        "Sekyere Kumawu", "Sekyere South", "Suame", "Suame Municipal",
        "Suame North",
    }),
}



class BuildingTypeEnum(str, Enum):
    residential = "Residential"
    commercial = "Commercial"
    mixed_use = "Mixed-Use"
    industrial = "Industrial"


# -------------------------
# FINISHING LEVELS
# -------------------------
class FinishingEnum(str, Enum):
    basic = "Basic"
    standard = "Standard"
    premium = "Premium"
    luxury = "Luxury"

# -------------------------
# EXTRAS
# -------------------------
class ExtraEnum(str, Enum):
    fence = "Fence"
    gate = "Gate"
    borehole = "Borehole"
    septic_tank = "Septic Tank"
    garage = "Garage"
    boys_quarters = "Boys Quarters"
    solar_system = "Solar System"
