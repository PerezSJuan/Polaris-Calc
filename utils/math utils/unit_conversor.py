"""The utility module for unit conversion."""

# Standard SI Prefixes (Base 10)
prefixes = {
    "Y": 1e24,  # yotta
    "Z": 1e21,  # zetta
    "E": 1e18,  # exa
    "P": 1e15,  # peta
    "T": 1e12,  # tera
    "G": 1e9,  # giga
    "M": 1e6,  # mega
    "k": 1e3,  # kilo
    "h": 1e2,  # hecto
    "da": 1e1,  # deca
    "d": 1e-1,  # deci
    "c": 1e-2,  # centi
    "m": 1e-3,  # milli
    "u": 1e-6,  # micro ('u' used for ASCII compatibility)
    "n": 1e-9,  # nano
    "p": 1e-12,  # pico
    "f": 1e-15,  # femto
    "a": 1e-18,  # atto
    "z": 1e-21,  # zepto
    "y": 1e-24,  # yocto
}

# Default units grouped by physical dimension
default_units = {
    "Length": {
        "m": {
            "factor": 1.0,
            "use_prefixes": True,
        },  # Base unit for Meter (km, cm, mm will be detected)
        "in": {"factor": 0.0254, "use_prefixes": False},
        "ft": {"factor": 0.3048, "use_prefixes": False},
        "yd": {"factor": 0.9144, "use_prefixes": False},
        "mi": {"factor": 1609.344, "use_prefixes": False},
        "nmi": {"factor": 1852.0, "use_prefixes": False},
        "fur": {"factor": 201.168, "use_prefixes": False},
        "chain": {"factor": 20.1168, "use_prefixes": False},
        "rod": {"factor": 5.0292, "use_prefixes": False},
        "fathom": {"factor": 1.8288, "use_prefixes": False},
        "hand": {"factor": 0.1016, "use_prefixes": False},
        "li": {"factor": 500.0, "use_prefixes": False},
        "ly": {"factor": 9.46073e15, "use_prefixes": False},
        "au": {"factor": 1.495978707e11, "use_prefixes": False},
        "pc": {"factor": 3.08567758e16, "use_prefixes": False},
        "angstrom": {"factor": 1e-10, "use_prefixes": False},
        "mil": {"factor": 2.54e-5, "use_prefixes": False},
        "point": {"factor": 0.000352778, "use_prefixes": False},
        "pica": {"factor": 0.00423333, "use_prefixes": False},
    },
    "Mass": {
        "g": {
            "factor": 1.0,
            "use_prefixes": True,
        },  # Base for Grams (kg, mg, ug detected automatically)
        "ton": {
            "factor": 1e6,
            "use_prefixes": False,
        },  # Metric ton (fixed as 1e6 grams)
        "lb": {"factor": 453.59237, "use_prefixes": False},
        "oz": {"factor": 28.349523, "use_prefixes": False},
        "st": {"factor": 6350.29318, "use_prefixes": False},
        "slug": {"factor": 14593.9029, "use_prefixes": False},
        "gr": {"factor": 0.06479891, "use_prefixes": False},
        "carat": {"factor": 0.2, "use_prefixes": False},
        "amu": {"factor": 1.660539e-24, "use_prefixes": False},
        "ton_us": {"factor": 907184.74, "use_prefixes": False},
        "ton_uk": {"factor": 1016046.9088, "use_prefixes": False},
        "qtr": {"factor": 12700.58636, "use_prefixes": False},
        "cwt": {"factor": 45359.237, "use_prefixes": False},
    },
    "Time": {
        "s": {"factor": 1.0, "use_prefixes": False},
        "min": {"factor": 60.0, "use_prefixes": False},
        "h": {"factor": 3600.0, "use_prefixes": False},
        "day": {"factor": 86400.0, "use_prefixes": False},
        "week": {"factor": 604800.0, "use_prefixes": False},
        "year": {"factor": 31536000.0, "use_prefixes": False},
        "decade": {"factor": 315360000.0, "use_prefixes": False},
        "century": {"factor": 3.1536e9, "use_prefixes": False},
        "millennium": {"factor": 3.1536e10, "use_prefixes": False},
        "fortnight": {"factor": 1209600.0, "use_prefixes": False},
        "shake": {"factor": 1e-8, "use_prefixes": False},
        "jiffy": {"factor": 0.01, "use_prefixes": False},
    },
    "Temperature": {
        "K": {"factor": 1.0, "offset": 0.0, "use_prefixes": False},
        "C": {"factor": 1.0, "offset": 273.15, "use_prefixes": False},
        "F": {"factor": 5 / 9, "offset": 255.37222, "use_prefixes": False},
        "R": {"factor": 5 / 9, "offset": 0.0, "use_prefixes": False},
    },
    "Digital Storage": {
        "bit": {"factor": 0.125, "use_prefixes": False},
        "Kbit": {"factor": 0.125 * 1024.0, "use_prefixes": False},
        "Mbit": {"factor": 0.125 * 1024.0**2, "use_prefixes": False},
        "Gbit": {"factor": 0.125 * 1024.0**3, "use_prefixes": False},
        "Tbit": {"factor": 0.125 * 1024.0**4, "use_prefixes": False},
        "Pbit": {"factor": 0.125 * 1024.0**5, "use_prefixes": False},
        "Ebit": {"factor": 0.125 * 1024.0**6, "use_prefixes": False},
        "Zbit": {"factor": 0.125 * 1024.0**7, "use_prefixes": False},
        "Ybit": {"factor": 0.125 * 1024.0**8, "use_prefixes": False},
        "B": {
            "factor": 1.0,
            "use_prefixes": False,
        },  # Byte. Binary prefixes defined separately below.
        "KB": {
            "factor": 1024.0,
            "use_prefixes": False,
        },  # Fixed factors for Information
        "MB": {"factor": 1024.0**2, "use_prefixes": False},
        "GB": {"factor": 1024.0**3, "use_prefixes": False},
        "TB": {"factor": 1024.0**4, "use_prefixes": False},
        "PB": {"factor": 1024.0**5, "use_prefixes": False},
        "EB": {"factor": 1024.0**6, "use_prefixes": False},
        "ZB": {"factor": 1024.0**7, "use_prefixes": False},
        "YB": {"factor": 1024.0**8, "use_prefixes": False},
    },
    "Area": {
        "m2": {"factor": 1.0, "use_prefixes": True},
        "ha": {"factor": 10000.0, "use_prefixes": False},
        "ac": {"factor": 4046.856, "use_prefixes": False},
        "ft2": {"factor": 0.092903, "use_prefixes": False},
        "yd2": {"factor": 0.836127, "use_prefixes": False},
        "mi2": {"factor": 2.58999e6, "use_prefixes": False},
        "in2": {"factor": 0.00064516, "use_prefixes": False},
        "section": {"factor": 2.58999e6, "use_prefixes": False},
        "township": {"factor": 9.32396e7, "use_prefixes": False},
        "barn": {
            "factor": 1e-28,
            "use_prefixes": True,
        },  # Con prefijos (mbarn, µbarn, etc.)
        "are": {
            "factor": 100.0,
            "use_prefixes": True,
        },  # Con prefijos (hectare, decare, etc.)
    },
    "Volume": {
        "m3": {"factor": 1.0, "use_prefixes": True},
        "l": {"factor": 0.001, "use_prefixes": True},  # Litro con prefijos
        "gal": {"factor": 0.00378541, "use_prefixes": False},
        "gal_uk": {"factor": 0.00454609, "use_prefixes": False},
        "qt": {"factor": 0.000946353, "use_prefixes": False},
        "qt_uk": {"factor": 0.00113652, "use_prefixes": False},
        "pt": {"factor": 0.000473176, "use_prefixes": False},
        "pt_uk": {"factor": 0.000568261, "use_prefixes": False},
        "cup": {"factor": 0.000236588, "use_prefixes": False},
        "fl_oz": {"factor": 2.95735e-5, "use_prefixes": False},
        "fl_oz_uk": {"factor": 2.84131e-5, "use_prefixes": False},
        "tbsp": {"factor": 1.47868e-5, "use_prefixes": False},
        "tsp": {"factor": 4.92892e-6, "use_prefixes": False},
        "cc": {"factor": 1e-6, "use_prefixes": False},
        "ft3": {"factor": 0.0283168, "use_prefixes": False},
        "in3": {"factor": 1.6387e-5, "use_prefixes": False},
        "yd3": {"factor": 0.764555, "use_prefixes": False},
        "bbl": {"factor": 0.158987, "use_prefixes": False},
        "bushel": {"factor": 0.0352391, "use_prefixes": False},
        "cord": {"factor": 3.62456, "use_prefixes": False},
    },
    "Voltage": {
        "V": {"factor": 1.0, "use_prefixes": True},
    },
    "Current": {
        "A": {"factor": 1.0, "use_prefixes": True},
    },
    "Resistance": {
        "Ω": {"factor": 1.0, "use_prefixes": True},
        "Ohm": {"factor": 1.0, "use_prefixes": True},
    },
    "Energy": {
        "J": {"factor": 1.0, "use_prefixes": True},
        "cal": {"factor": 4.184, "use_prefixes": True},
        "Wh": {"factor": 3600.0, "use_prefixes": True},
        "eV": {"factor": 1.602176e-19, "use_prefixes": True},
        "BTU": {"factor": 1055.056, "use_prefixes": False},
        "therm": {"factor": 1.055056e8, "use_prefixes": False},
        "erg": {"factor": 1e-7, "use_prefixes": True},
        "foe": {"factor": 1e44, "use_prefixes": False},
        "ton_tnt": {"factor": 4.184e9, "use_prefixes": True},  # Con prefijos (kt, Mt)
    },
    "Power": {
        "W": {"factor": 1.0, "use_prefixes": True},
        "hp": {"factor": 745.69987, "use_prefixes": False},
        "hp_metric": {"factor": 735.49875, "use_prefixes": False},
        "hp_electric": {"factor": 746.0, "use_prefixes": False},
        "hp_boiler": {"factor": 9809.5, "use_prefixes": False},
        "cal/s": {"factor": 4.184, "use_prefixes": True},
        "BTU/h": {"factor": 0.293071, "use_prefixes": False},
        "ton_ref": {"factor": 3516.85, "use_prefixes": False},
        "dBm": {"factor": 0.001, "use_prefixes": False, "logarithmic": True},
        "dBW": {"factor": 1.0, "use_prefixes": False, "logarithmic": True},
    },
    "Pressure": {
        "Pa": {"factor": 1.0, "use_prefixes": True},
        "bar": {"factor": 100000.0, "use_prefixes": False},
        "atm": {"factor": 101325.0, "use_prefixes": False},
        "psi": {"factor": 6894.757, "use_prefixes": False},
        "torr": {"factor": 133.322, "use_prefixes": False},
        "mmHg": {"factor": 133.322, "use_prefixes": False},
        "inHg": {"factor": 3386.39, "use_prefixes": False},
        "cmH2O": {"factor": 98.0665, "use_prefixes": False},
        "inH2O": {"factor": 249.089, "use_prefixes": False},
        "psf": {"factor": 47.8803, "use_prefixes": False},
    },
    "Speed": {
        "m/s": {"factor": 1.0, "use_prefixes": True},
        "km/h": {"factor": 0.277778, "use_prefixes": False},
        "mph": {"factor": 0.44704, "use_prefixes": False},
        "kn": {"factor": 0.514444, "use_prefixes": False},
        "ft/s": {"factor": 0.3048, "use_prefixes": False},
        "c": {"factor": 299792458, "use_prefixes": False},
        "mach": {"factor": 343.0, "use_prefixes": False},
    },
    "Acceleration": {
        "m/s2": {"factor": 1.0, "use_prefixes": True},
        "g": {"factor": 9.80665, "use_prefixes": False},
        "ft/s2": {"factor": 0.3048, "use_prefixes": False},
        "Gal": {"factor": 0.01, "use_prefixes": True},
    },
    "Force": {
        "N": {"factor": 1.0, "use_prefixes": True},
        "lbf": {"factor": 4.44822, "use_prefixes": False},
        "kgf": {"factor": 9.80665, "use_prefixes": True},
        "dyn": {"factor": 1e-5, "use_prefixes": True},
        "pdl": {"factor": 0.138255, "use_prefixes": False},
        "kip": {"factor": 4448.22, "use_prefixes": False},
        "sn": {"factor": 1000.0, "use_prefixes": False},
    },
    "Angle": {
        "rad": {"factor": 1.0, "use_prefixes": True},
        "deg": {"factor": 0.0174532925, "use_prefixes": False},
        "grad": {"factor": 0.0157079633, "use_prefixes": False},
        "arcmin": {"factor": 0.000290888, "use_prefixes": False},
        "arcsec": {"factor": 4.84814e-6, "use_prefixes": False},
        "turn": {"factor": 6.28318531, "use_prefixes": False},
        "quadrant": {"factor": 1.57079633, "use_prefixes": False},
        "sextant": {"factor": 1.04719755, "use_prefixes": False},
    },
    "Solid Angle": {
        "sr": {"factor": 1.0, "use_prefixes": True},  # Steradian con prefijos
        "deg2": {"factor": 0.000304617, "use_prefixes": False},  # Square degree
        "sp": {"factor": 12.56637, "use_prefixes": False},  # Sphere
        "hemisphere": {"factor": 6.283185, "use_prefixes": False},
    },
    "Frequency": {
        "Hz": {"factor": 1.0, "use_prefixes": True},
        "rpm": {"factor": 1 / 60, "use_prefixes": False},
        "rps": {"factor": 1.0, "use_prefixes": False},
        "bpm": {"factor": 1 / 60, "use_prefixes": False},
    },
    "Electric Charge": {
        "C": {"factor": 1.0, "use_prefixes": True},
        "e": {"factor": 1.6021766e-19, "use_prefixes": False},
        "Ah": {"factor": 3600.0, "use_prefixes": True},
        "Faraday": {"factor": 96485.3329, "use_prefixes": False},
    },
    "Electric Capacitance": {
        "F": {"factor": 1.0, "use_prefixes": True},
    },
    "Inductance": {
        "H": {"factor": 1.0, "use_prefixes": True},
    },
    "Magnetic Flux": {
        "Wb": {"factor": 1.0, "use_prefixes": True},
        "Mx": {"factor": 1e-8, "use_prefixes": False},
    },
    "Magnetic Flux Density": {
        "T": {"factor": 1.0, "use_prefixes": True},
        "G": {"factor": 1e-4, "use_prefixes": True},
    },
    "Luminous Intensity": {
        "cd": {"factor": 1.0, "use_prefixes": True},
    },
    "Luminous Flux": {
        "lm": {"factor": 1.0, "use_prefixes": True},
    },
    "Illuminance": {
        "lx": {"factor": 1.0, "use_prefixes": True},
        "fc": {"factor": 10.7639, "use_prefixes": False},
        "ph": {"factor": 10000.0, "use_prefixes": False},
    },
    "Radioactivity": {
        "Bq": {"factor": 1.0, "use_prefixes": True},
        "Ci": {"factor": 3.7e10, "use_prefixes": True},
        "Rd": {"factor": 1e6, "use_prefixes": False},
    },
    "Absorbed Dose": {
        "Gy": {"factor": 1.0, "use_prefixes": True},
        "rad": {"factor": 0.01, "use_prefixes": True},
    },
    "Equivalent Dose": {
        "Sv": {"factor": 1.0, "use_prefixes": True},
        "rem": {"factor": 0.01, "use_prefixes": True},
    },
    "Catalytic Activity": {
        "kat": {"factor": 1.0, "use_prefixes": True},
        "U": {"factor": 1 / 16.67e-9, "use_prefixes": False},
    },
    "Information Rate": {
        "bps": {"factor": 1.0, "use_prefixes": True},  # Bits per second
        "Bps": {"factor": 8.0, "use_prefixes": True},  # Bytes per second
    },
    "Fuel Efficiency": {
        "km/L": {"factor": 1.0, "use_prefixes": True},
        "L/100km": {"factor": 100.0, "use_prefixes": False, "inverse": True},
        "mpg": {"factor": 0.425144, "use_prefixes": False},
        "mpg_uk": {"factor": 0.354006, "use_prefixes": False},
    },
    "Concentration": {
        "mol/L": {"factor": 1.0, "use_prefixes": True},  # Molaridad con prefijos
        "M": {"factor": 1.0, "use_prefixes": True},  # Molar
        "ppm": {"factor": 0.001, "use_prefixes": False},
        "ppb": {"factor": 1e-6, "use_prefixes": False},
        "ppt": {"factor": 1e-9, "use_prefixes": False},
        "%": {"factor": 0.01, "use_prefixes": False},
        "‰": {"factor": 0.001, "use_prefixes": False},
    },
    "Flow Rate": {
        "m3/s": {"factor": 1.0, "use_prefixes": True},
        "L/s": {"factor": 0.001, "use_prefixes": True},
        "gal/s": {"factor": 0.00378541, "use_prefixes": False},
        "CFM": {"factor": 0.000471947, "use_prefixes": False},
    },
    "Viscosity Dynamic": {
        "Pa·s": {"factor": 1.0, "use_prefixes": True},
        "P": {
            "factor": 0.1,
            "use_prefixes": True,
        },  # Poise con prefijos (cP = centipoise)
    },
    "Viscosity Kinematic": {
        "m2/s": {"factor": 1.0, "use_prefixes": True},
        "St": {
            "factor": 1e-4,
            "use_prefixes": True,
        },  # Stokes con prefijos (cSt = centistokes)
    },
    "Density": {
        "kg/m3": {"factor": 1.0, "use_prefixes": True},
        "g/cm3": {"factor": 1000.0, "use_prefixes": False},
        "g/mL": {"factor": 1000.0, "use_prefixes": False},
        "lb/ft3": {"factor": 16.0185, "use_prefixes": False},
        "lb/gal": {"factor": 119.826, "use_prefixes": False},
    },
    "Moment of Inertia": {
        "kg·m2": {"factor": 1.0, "use_prefixes": True},
        "lb·ft2": {"factor": 0.0421401, "use_prefixes": False},
    },
    "Torque": {
        "N·m": {"factor": 1.0, "use_prefixes": True},
        "lbf·ft": {"factor": 1.35582, "use_prefixes": False},
        "lbf·in": {"factor": 0.112985, "use_prefixes": False},
        "kgf·m": {"factor": 9.80665, "use_prefixes": True},
    },
    "Currency": {
        "USD": {"factor": 1.0, "use_prefixes": False, "type": "fiat"},
        "EUR": {"factor": 1.09, "use_prefixes": False, "type": "fiat"},
        "GBP": {"factor": 1.27, "use_prefixes": False, "type": "fiat"},
        "JPY": {"factor": 0.0067, "use_prefixes": False, "type": "fiat"},
        "CNY": {"factor": 0.14, "use_prefixes": False, "type": "fiat"},
        "CAD": {"factor": 0.74, "use_prefixes": False, "type": "fiat"},
        "AUD": {"factor": 0.67, "use_prefixes": False, "type": "fiat"},
        "CHF": {"factor": 1.12, "use_prefixes": False, "type": "fiat"},
        "INR": {"factor": 0.012, "use_prefixes": False, "type": "fiat"},
        "BRL": {"factor": 0.19, "use_prefixes": False, "type": "fiat"},
        "MXN": {"factor": 0.058, "use_prefixes": False, "type": "fiat"},
        "KRW": {"factor": 0.00075, "use_prefixes": False, "type": "fiat"},
        "RUB": {"factor": 0.011, "use_prefixes": False, "type": "fiat"},
        "ZAR": {"factor": 0.054, "use_prefixes": False, "type": "fiat"},
        "SGD": {"factor": 0.74, "use_prefixes": False, "type": "fiat"},
        "HKD": {"factor": 0.13, "use_prefixes": False, "type": "fiat"},
        "NZD": {"factor": 0.62, "use_prefixes": False, "type": "fiat"},
        "SEK": {"factor": 0.095, "use_prefixes": False, "type": "fiat"},
        "NOK": {"factor": 0.094, "use_prefixes": False, "type": "fiat"},
        "DKK": {"factor": 0.15, "use_prefixes": False, "type": "fiat"},
        "PLN": {"factor": 0.25, "use_prefixes": False, "type": "fiat"},
        "TRY": {"factor": 0.031, "use_prefixes": False, "type": "fiat"},
        "AED": {"factor": 0.27, "use_prefixes": False, "type": "fiat"},
        "SAR": {"factor": 0.27, "use_prefixes": False, "type": "fiat"},
        "ILS": {"factor": 0.27, "use_prefixes": False, "type": "fiat"},
        "THB": {"factor": 0.028, "use_prefixes": False, "type": "fiat"},
        "BTC": {"factor": 43000.0, "use_prefixes": False, "type": "crypto"},
        "ETH": {"factor": 2200.0, "use_prefixes": False, "type": "crypto"},
        "USDT": {"factor": 1.0, "use_prefixes": False, "type": "crypto"},
        "XAU": {"factor": 1950.0, "use_prefixes": False, "type": "commodity"},  # Gold
        "XAG": {"factor": 23.50, "use_prefixes": False, "type": "commodity"},  # Silver
        "SAT": {"factor": 0.00043, "use_prefixes": False, "type": "crypto"},  # Satoshi
    },
    "Typography": {
        "pt": {"factor": 0.000352778, "use_prefixes": False},
        "pc": {"factor": 0.00423333, "use_prefixes": False},
        "dd": {"factor": 0.000375, "use_prefixes": False},  # Didot point
        "cc": {"factor": 0.0045, "use_prefixes": False},  # Cicero
        "em": {"factor": 1.0, "use_prefixes": False, "relative": True},
        "ex": {"factor": 0.5, "use_prefixes": False, "relative": True},
        "rem": {"factor": 1.0, "use_prefixes": False, "relative": True},
    },
    "Navigation": {
        "cable": {"factor": 185.2, "use_prefixes": False},
        "league": {"factor": 5556.0, "use_prefixes": False},
        "link_gunter": {"factor": 0.201168, "use_prefixes": False},
        "point_nav": {"factor": 11.25, "use_prefixes": False},  # Compass point
    },
    "Astronomy": {
        "ly": {"factor": 9.46073e15, "use_prefixes": False},
        "pc": {
            "factor": 3.08567758e16,
            "use_prefixes": True,
        },  # Parsec con prefijos (kpc, Mpc)
        "au": {"factor": 1.495978707e11, "use_prefixes": False},
        "R_sun": {"factor": 6.96e8, "use_prefixes": False},
        "R_earth": {"factor": 6371000.0, "use_prefixes": False},
        "M_sun": {"factor": 1.9885e30, "use_prefixes": False},
        "M_earth": {"factor": 5.9722e24, "use_prefixes": False},
        "L_sun": {"factor": 3.828e26, "use_prefixes": False},
        "Jy": {"factor": 1e-26, "use_prefixes": True},  # Jansky
    },
    "Particle Physics": {
        "barn": {"factor": 1e-28, "use_prefixes": True},  # Barn con prefijos
    },
    "Chemical Amount": {
        "mol": {"factor": 1.0, "use_prefixes": True},
        "eq": {"factor": 1.0, "use_prefixes": True},  # Equivalent
        "osmole": {"factor": 1.0, "use_prefixes": True},  # Osmole
    },
    "Cooking": {
        "pinch": {"factor": 0.000000308, "use_prefixes": False},
        "dash": {"factor": 0.000000616, "use_prefixes": False},
        "smidgen": {"factor": 0.000000154, "use_prefixes": False},
        "drop": {"factor": 0.00000005, "use_prefixes": False},
        "stick_butter": {"factor": 0.113398, "use_prefixes": False},
    },
    "Textiles": {
        "tex": {"factor": 1e-6, "use_prefixes": True},  # Tex con prefijos (dtex)
        "den": {"factor": 1.11111e-7, "use_prefixes": False},  # Denier
        "Nm": {"factor": 0.001, "use_prefixes": False},  # Metric count
        "Ne": {"factor": 0.00059055, "use_prefixes": False},  # Cotton count
    },
    "Ratios": {
        "%": {"factor": 0.01, "use_prefixes": False},
        "‰": {"factor": 0.001, "use_prefixes": False},
        "‱": {"factor": 0.0001, "use_prefixes": False},
        "dozen": {"factor": 12.0, "use_prefixes": False},
        "gross": {"factor": 144.0, "use_prefixes": False},
        "score": {"factor": 20.0, "use_prefixes": False},
    },
    "Entropy": {
        "bit": {"factor": 1.0, "use_prefixes": True},
        "shannon": {"factor": 1.0, "use_prefixes": True},
        "nat": {"factor": 1.442695, "use_prefixes": False},
        "hartley": {"factor": 3.321928, "use_prefixes": False},
    },
    "Photometry": {
        "cd/m2": {"factor": 1.0, "use_prefixes": True},  # Luminance (nit)
        "nit": {"factor": 1.0, "use_prefixes": True},
        "sb": {"factor": 10000.0, "use_prefixes": False},  # Stilb
        "lambert": {"factor": 3183.1, "use_prefixes": False},
        "fl": {"factor": 3.426, "use_prefixes": False},  # Foot-lambert
    },
    "Colorimetry": {
        "K_temp": {"factor": 1.0, "use_prefixes": False},  # Kelvin (color temperature)
        "Mired": {"factor": 1e6, "use_prefixes": False},
    },
    "Digital Geometry": {
        "pixel": {"factor": 1.0, "use_prefixes": True},
        "ppi": {"factor": 39.3701, "use_prefixes": False},
        "dpi": {"factor": 39.3701, "use_prefixes": False},
    },
    "Geodesy": {
        "rad_earth": {"factor": 6371000.0, "use_prefixes": False},
        "deg_lat": {"factor": 111319.9, "use_prefixes": False},
        "mil_nato": {"factor": 0.000981748, "use_prefixes": False},
        "gon": {"factor": 0.01570796, "use_prefixes": False},
    },
}


def _get_base_unit_info(
    unit_symbol: str, unit_collection: dict = default_units
) -> dict:
    """Internal helper to find a unit in a unit collection dictionary."""
    for category, units in unit_collection.items():
        if unit_symbol in units:
            return units[unit_symbol]
    return None


def get_unit_info(unit_str: str, unit_collection: dict = default_units) -> dict:
    """Public helper to get unit information, supporting prefixes automatically."""
    # 1. Exact match (e.g., KB)
    info = _get_base_unit_info(unit_str, unit_collection)
    if info:
        return info

    # 2. Try prefix parsing (e.g., km)
    p, b, f = parse_unit_with_prefix(unit_str, unit_collection)
    if b:
        base_info = _get_base_unit_info(b, unit_collection)
        return {
            "factor": f,
            "use_prefixes": False,
            "base_unit": b,
            "prefix": p,
            "offset": base_info.get("offset", 0.0),
        }
    return None


def get_unit_type(unit_str: str, unit_collection: dict = default_units) -> str:
    """Get the physical dimension (category) of a unit, supporting prefixes."""
    # 1. Try exact match first
    for category, units in unit_collection.items():
        if unit_str in units:
            return category

    # 2. Try parsing with prefix
    _, base_unit, _ = parse_unit_with_prefix(unit_str, unit_collection)
    if base_unit:
        for category, units in unit_collection.items():
            if base_unit in units:
                return category
    return None


def parse_unit_with_prefix(
    unit_str: str, unit_collection: dict = default_units
) -> tuple:
    """Parse a unit string with an optional SI prefix."""
    # 1. Check for an exact match first
    unit_info = _get_base_unit_info(unit_str, unit_collection)
    if unit_info:
        return "", unit_str, unit_info["factor"]

    # 2. Check for SI prefix
    for prefix, value in prefixes.items():
        if unit_str.startswith(prefix):
            unit_name = unit_str[len(prefix) :]
            unit_info = _get_base_unit_info(unit_name, unit_collection)
            if unit_info and unit_info.get("use_prefixes", False):
                return prefix, unit_name, value * unit_info["factor"]

    return None, None, None


def convert_units(
    value: float, from_unit: str, to_unit: str, unit_collection: dict = default_units
) -> float:
    """Convert a value between two units of the same physical dimension."""
    p1, u1, f1 = parse_unit_with_prefix(from_unit, unit_collection)
    p2, u2, f2 = parse_unit_with_prefix(to_unit, unit_collection)

    if u1 is None or u2 is None:
        raise ValueError(f"Unknown unit: {from_unit if u1 is None else to_unit}")

    if from_unit == to_unit:
        return value

    type1 = get_unit_type(from_unit, unit_collection)
    type2 = get_unit_type(to_unit, unit_collection)

    if type1 != type2:
        raise ValueError(
            f"Dimensional mismatch: Cannot convert {type1} ({from_unit}) to {type2} ({to_unit})"
        )

    # Get internal data
    info1 = _get_base_unit_info(u1, unit_collection)
    info2 = _get_base_unit_info(u2, unit_collection)

    # 1. Transform from original unit to the internal base system (considering prefixes and offsets)
    base_val = (value * f1) + info1.get("offset", 0.0)

    # 2. Transform from base system to target unit
    conversion = (base_val - info2.get("offset", 0.0)) / f2

    return conversion


if __name__ == "__main__":
    while True:
        print("\n--- Unit Conversor Tester ---")
        print("Choose an option:")
        print("1. Parse unit")
        print("2. Convert units")
        print("Type 'exit' to quit.")

        choice = input().strip()
        if choice == "exit":
            break

        if choice == "1":
            unit = input("Enter unit (e.g., 'km'): ").strip()
            print(f"Parsing: {parse_unit_with_prefix(unit)}")
            print(f"Type: {get_unit_type(unit)}")
            print(f"Info: {get_unit_info(unit)}")
        elif choice == "2":
            try:
                val = float(input("Value: "))
                f = input("From unit: ").strip()
                t = input("To unit: ").strip()
                res = convert_units(val, f, t)
                print(f"Result: {val} {f} = {res} {t}")
            except ValueError as ve:
                print(f"Input Error: {ve}")
            except Exception as e:
                print(f"Error: {e}")
