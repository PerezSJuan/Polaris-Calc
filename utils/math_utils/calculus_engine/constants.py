import math


# ── Constantes matemáticas ─────────────────────────────────────────────────────

def euler_number() -> float:
    """
    Returns Euler's number e.

    e ≈ 2.718281828459045.

    Returns:
        The base of the natural logarithm.
    """
    return math.e


def pi() -> float:
    """
    Returns the mathematical constant π.

    π ≈ 3.141592653589793.

    Returns:
        The ratio of a circle's circumference to its diameter.
    """
    return math.pi


def golden_ratio() -> float:
    """
    Returns the golden ratio φ.

    φ = (1 + √5) / 2 ≈ 1.618033988749895.

    Returns:
        The golden ratio.
    """
    return (1 + math.sqrt(5)) / 2


def euler_mascheroni() -> float:
    """
    Returns the Euler–Mascheroni constant γ.

    γ ≈ 0.5772156649015329.

    Returns:
        The limit of (H_n − ln n) as n → ∞.
    """
    return 0.5772156649015329


def sqrt2() -> float:
    """
    Returns the square root of 2.

    √2 ≈ 1.4142135623730951.

    Returns:
        The square root of two.
    """
    return math.sqrt(2)


def sqrt3() -> float:
    """
    Returns the square root of 3.

    √3 ≈ 1.7320508075688772.

    Returns:
        The square root of three.
    """
    return math.sqrt(3)


def ln2() -> float:
    """
    Returns the natural logarithm of 2.

    ln 2 ≈ 0.6931471805599453.

    Returns:
        The natural logarithm of two.
    """
    return math.log(2)


def ln10() -> float:
    """
    Returns the natural logarithm of 10.

    ln 10 ≈ 2.302585092994046.

    Returns:
        The natural logarithm of ten.
    """
    return math.log(10)


# ── Constantes fundamentales de la física ──────────────────────────────────────

def speed_of_light() -> float:
    """
    Returns the speed of light in vacuum.

    c = 299 792 458 m·s⁻¹.

    Returns:
        The speed of light in m·s⁻¹.
    """
    return 299792458.0


def planck_constant() -> float:
    """
    Returns the Planck constant.

    h = 6.62607015 × 10⁻³⁴ J·s.

    Returns:
        The Planck constant in J·s.
    """
    return 6.62607015e-34


def reduced_planck_constant() -> float:
    """
    Returns the reduced Planck constant (ħ = h / 2π).

    ħ ≈ 1.054571817 × 10⁻³⁴ J·s.

    Returns:
        The reduced Planck constant in J·s.
    """
    return 1.0545718176461565e-34


def gravitational_constant() -> float:
    """
    Returns the Newtonian gravitational constant.

    G ≈ 6.67430 × 10⁻¹¹ m³·kg⁻¹·s⁻².

    Returns:
        The gravitational constant in m³·kg⁻¹·s⁻².
    """
    return 6.67430e-11


def elementary_charge() -> float:
    """
    Returns the elementary charge.

    e = 1.602176634 × 10⁻¹⁹ C.

    Returns:
        The elementary charge in C.
    """
    return 1.602176634e-19


def boltzmann_constant() -> float:
    """
    Returns the Boltzmann constant.

    k_B = 1.380649 × 10⁻²³ J·K⁻¹.

    Returns:
        The Boltzmann constant in J·K⁻¹.
    """
    return 1.380649e-23


def vacuum_permittivity() -> float:
    """
    Returns the vacuum electric permittivity.

    ε₀ ≈ 8.8541878128 × 10⁻¹² F·m⁻¹.

    Returns:
        The vacuum permittivity in F·m⁻¹.
    """
    return 8.8541878128e-12


def vacuum_permeability() -> float:
    """
    Returns the vacuum magnetic permeability.

    μ₀ = 4π × 10⁻⁷ H·m⁻¹ ≈ 1.25663706212 × 10⁻⁶ H·m⁻¹.

    Returns:
        The vacuum permeability in H·m⁻¹.
    """
    return 4e-7 * math.pi


def fine_structure_constant() -> float:
    """
    Returns the fine-structure constant.

    α ≈ 7.2973525693 × 10⁻³.

    Returns:
        The dimensionless fine-structure constant.
    """
    return 7.2973525693e-3


def rydberg_constant() -> float:
    """
    Returns the Rydberg constant.

    R_∞ ≈ 10 973 731.568160 m⁻¹.

    Returns:
        The Rydberg constant in m⁻¹.
    """
    return 10973731.568160


def stefan_boltzmann_constant() -> float:
    """
    Returns the Stefan–Boltzmann constant.

    σ ≈ 5.670374419 × 10⁻⁸ W·m⁻²·K⁻⁴.

    Returns:
        The Stefan–Boltzmann constant in W·m⁻²·K⁻⁴.
    """
    return 5.670374419e-8


# ── Constantes químicas ────────────────────────────────────────────────────────

def avogadro_constant() -> float:
    """
    Returns the Avogadro constant.

    N_A = 6.02214076 × 10²³ mol⁻¹.

    Returns:
        The Avogadro constant in mol⁻¹.
    """
    return 6.02214076e23


def gas_constant() -> float:
    """
    Returns the molar gas constant.

    R = 8.314462618 J·mol⁻¹·K⁻¹.

    Returns:
        The gas constant in J·mol⁻¹·K⁻¹.
    """
    return 8.314462618


def faraday_constant() -> float:
    """
    Returns the Faraday constant.

    F = e · N_A = 96 485.33212 C·mol⁻¹.

    Returns:
        The Faraday constant in C·mol⁻¹.
    """
    return 96485.33212


# ── Constantes atómicas y nucleares ────────────────────────────────────────────

def electron_mass() -> float:
    """
    Returns the electron rest mass.

    m_e ≈ 9.1093837015 × 10⁻³¹ kg.

    Returns:
        The electron mass in kg.
    """
    return 9.1093837015e-31


def proton_mass() -> float:
    """
    Returns the proton rest mass.

    m_p ≈ 1.67262192369 × 10⁻²⁷ kg.

    Returns:
        The proton mass in kg.
    """
    return 1.67262192369e-27


def neutron_mass() -> float:
    """
    Returns the neutron rest mass.

    m_n ≈ 1.67492749804 × 10⁻²⁷ kg.

    Returns:
        The neutron mass in kg.
    """
    return 1.67492749804e-27


def atomic_mass_unit() -> float:
    """
    Returns the unified atomic mass unit (dalton).

    u ≈ 1.66053906660 × 10⁻²⁷ kg.

    Returns:
        The atomic mass unit in kg.
    """
    return 1.66053906660e-27


def bohr_radius() -> float:
    """
    Returns the Bohr radius.

    a₀ ≈ 5.29177210903 × 10⁻¹¹ m.

    Returns:
        The Bohr radius in m.
    """
    return 5.29177210903e-11


def hartree_energy() -> float:
    """
    Returns the Hartree energy.

    E_h ≈ 4.3597447222071 × 10⁻¹⁸ J.

    Returns:
        The Hartree energy in J.
    """
    return 4.3597447222071e-18


def bohr_magneton() -> float:
    """
    Returns the Bohr magneton.

    μ_B ≈ 9.2740100783 × 10⁻²⁴ J·T⁻¹.

    Returns:
        The Bohr magneton in J·T⁻¹.
    """
    return 9.2740100783e-24


def nuclear_magneton() -> float:
    """
    Returns the nuclear magneton.

    μ_N ≈ 5.0507837461 × 10⁻²⁷ J·T⁻¹.

    Returns:
        The nuclear magneton in J·T⁻¹.
    """
    return 5.0507837461e-27


def electron_volt() -> float:
    """
    Returns the electronvolt in joules.

    eV = 1.602176634 × 10⁻¹⁹ J.

    Returns:
        The energy of one electronvolt in J.
    """
    return 1.602176634e-19


# ── Constantes astronómicas ────────────────────────────────────────────────────

def astronomical_unit() -> float:
    """
    Returns the astronomical unit.

    AU = 1.495978707 × 10¹¹ m.

    Returns:
        The astronomical unit in m.
    """
    return 1.495978707e11


def light_year() -> float:
    """
    Returns the light-year in metres.

    1 ly ≈ 9.4607304725808 × 10¹⁵ m.

    Returns:
        One light-year in m.
    """
    return 9.4607304725808e15


def parsec() -> float:
    """
    Returns the parsec in metres.

    1 pc ≈ 3.085677581491367 × 10¹⁶ m.

    Returns:
        One parsec in m.
    """
    return 3.085677581491367e16


def solar_mass() -> float:
    """
    Returns the solar mass.

    M_⊙ ≈ 1.98847 × 10³⁰ kg.

    Returns:
        The solar mass in kg.
    """
    return 1.98847e30


def solar_radius() -> float:
    """
    Returns the nominal solar radius.

    R_⊙ ≈ 6.957 × 10⁸ m.

    Returns:
        The solar radius in m.
    """
    return 6.957e8


def solar_luminosity() -> float:
    """
    Returns the solar luminosity.

    L_⊙ ≈ 3.828 × 10²⁶ W.

    Returns:
        The solar luminosity in W.
    """
    return 3.828e26


def hubble_constant() -> float:
    """
    Returns the Hubble constant in SI units (s⁻¹).

    H₀ ≈ 67.8 km·s⁻¹·Mpc⁻¹ ≈ 2.197 × 10⁻¹⁸ s⁻¹.

    Returns:
        The Hubble constant in s⁻¹.
    """
    return 2.197e-18


# ── Constantes geofísicas ──────────────────────────────────────────────────────

def speed_of_sound_air() -> float:
    """
    Returns the speed of sound in dry air at 20 °C.

    ≈ 343 m·s⁻¹.

    Returns:
        The speed of sound in m·s⁻¹.
    """
    return 343.0


def standard_gravity() -> float:
    """
    Returns the standard acceleration of free fall.

    g₀ = 9.80665 m·s⁻².

    Returns:
        The standard gravity in m·s⁻².
    """
    return 9.80665


def earth_mass() -> float:
    """
    Returns the Earth mass.

    M_⊕ ≈ 5.9722 × 10²⁴ kg.

    Returns:
        The Earth mass in kg.
    """
    return 5.9722e24


def earth_radius() -> float:
    """
    Returns the mean Earth radius.

    R_⊕ ≈ 6.371 × 10⁶ m.

    Returns:
        The Earth radius in m.
    """
    return 6.371e6


# ── Constantes electromagnéticas ───────────────────────────────────────────────

def magnetic_flux_quantum() -> float:
    """
    Returns the magnetic flux quantum.

    Φ₀ = h / (2e) ≈ 2.067833848 × 10⁻¹⁵ Wb.

    Returns:
        The magnetic flux quantum in Wb.
    """
    return 2.067833848e-15


def conductance_quantum() -> float:
    """
    Returns the conductance quantum.

    G₀ = 2e² / h ≈ 7.748091729 × 10⁻⁵ S.

    Returns:
        The conductance quantum in S.
    """
    return 7.748091729e-5


def von_klitzing_constant() -> float:
    """
    Returns the von Klitzing constant (quantum Hall resistance).

    R_K = h / e² ≈ 25 812.80745 Ω.

    Returns:
        The von Klitzing constant in Ω.
    """
    return 25812.80745


def characteristic_impedance_vacuum() -> float:
    """
    Returns the characteristic impedance of vacuum.

    Z₀ = μ₀c ≈ 376.730313412 Ω.

    Returns:
        The vacuum impedance in Ω.
    """
    return 376.730313412


# ── Constantes de radiación y cuántica ─────────────────────────────────────────

def compton_wavelength_electron() -> float:
    """
    Returns the Compton wavelength of the electron.

    λ_C = h / (m_e c) ≈ 2.42631023867 × 10⁻¹² m.

    Returns:
        The electron Compton wavelength in m.
    """
    return 2.42631023867e-12


def classical_electron_radius() -> float:
    """
    Returns the classical electron radius.

    r_e = e² / (4πε₀ m_e c²) ≈ 2.8179403262 × 10⁻¹⁵ m.

    Returns:
        The classical electron radius in m.
    """
    return 2.8179403262e-15


def thomson_cross_section() -> float:
    """
    Returns the Thomson scattering cross-section.

    σ_e = 8πr_e²/3 ≈ 6.652458732 × 10⁻²⁹ m².

    Returns:
        The Thomson cross-section in m².
    """
    return 6.652458732e-29


def planck_temperature() -> float:
    """
    Returns the Planck temperature.

    T_P = √(ħc⁵/Gk_B²) ≈ 1.416784 × 10³² K.

    Returns:
        The Planck temperature in K.
    """
    return 1.416784e32


def planck_length() -> float:
    """
    Returns the Planck length.

    ℓ_P = √(ħG/c³) ≈ 1.616255 × 10⁻³⁵ m.

    Returns:
        The Planck length in m.
    """
    return 1.616255e-35


def planck_mass() -> float:
    """
    Returns the Planck mass.

    m_P = √(ħc/G) ≈ 2.176434 × 10⁻⁸ kg.

    Returns:
        The Planck mass in kg.
    """
    return 2.176434e-8


def planck_time() -> float:
    """
    Returns the Planck time.

    t_P = √(ħG/c⁵) ≈ 5.391247 × 10⁻⁴⁴ s.

    Returns:
        The Planck time in s.
    """
    return 5.391247e-44
