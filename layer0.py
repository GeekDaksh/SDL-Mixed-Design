"""Layer 0 - deterministic IS mix design for the RMC SDL.

GENERATED FILE - do not edit. Edit 09_layer0_design_engine.ipynb and re-run its export cell.

Composes is_rules.py only. It adds no standards constants of its own.
Every mix it returns carries a compliance_gate verdict; use .decided, not .pass.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, asdict, replace
from enum import Enum
from typing import Optional

import is_rules as IS

print("is_rules loaded.")
src = IS.verify_sources()
def _src_ok(v):
    # verify_sources returns (state, note); accept only an explicit ok state.
    state = v[0] if isinstance(v, (tuple, list)) else v
    return str(getattr(state, "name", state)).lower() == "ok"


bad = {k: v for k, v in src.items() if not _src_ok(v)}
if bad:
    print(f"SOURCE VERIFICATION: {len(bad)} of {len(src)} standards did NOT verify:")
    for k, v in bad.items():
        print(f"   - {k}: {getattr(v, 'name', v)}")
    print("   Layer 0 still runs, but until these verify every value it returns is")
    print("   NOT VERIFIED FROM PRIMARY STANDARD SOURCE. Fix before any trial is cast.")
else:
    print(f"source verification: all {len(src)} standards OK")


def _source_status():
    """Did every standard verify against its frozen, hash-checked source?

    is_rules.verify_sources() returns {standard: (state, note)}. A mix designed from
    constants that failed verification is NOT VERIFIED FROM PRIMARY STANDARD SOURCE,
    and MixDesign.decided refuses it. Printing a warning and carrying on -- which is
    what this notebook did before -- lets an unverified mix look identical to a
    verified one in the returned object.
    """
    try:
        src = IS.verify_sources()
    except Exception as e:
        return False, (f"verify_sources() raised {type(e).__name__}: {e}",)

    def ok(v):
        st = v[0] if isinstance(v, (tuple, list)) else v
        return str(getattr(st, "name", st)).lower() == "ok"

    bad = tuple(sorted(k for k, v in src.items() if not ok(v)))
    return (not bad), bad


class Provenance(Enum):
    """How a value entered the system. Never silently filled."""

    DERIVED_FROM_STANDARD = "derived_from_standard"
    STANDARD_DEFAULT = "standard_default"
    ENGINEER_INPUT = "engineer_input"
    MATERIAL_SPECIFIC = "material_specific"
    PLANT_SPECIFIC = "plant_specific"
    EXPERIMENTALLY_DETERMINED = "experimentally_determined"
    ASSUMED = "assumed"


class ValidationLevel(Enum):
    """How far a mix has actually got. Set by 13_trial_loop, never by a model.

    Every mix this system has produced so far is COMPUTATIONALLY_COMPLIANT.
    Printing this on every output is what stops a proposal being read as an
    approved mix.
    """

    COMPUTATIONALLY_COMPLIANT = 1
    LAB_VALIDATED = 2
    TRIAL_BATCH_VALIDATED = 3
    PRODUCTION_VALIDATED = 4


@dataclass(frozen=True)
class Valued:
    """A number that remembers where it came from."""

    value: float
    provenance: Provenance
    source: str

    def __float__(self) -> float:
        return float(self.value)

    def __repr__(self) -> str:
        return f"{self.value:g} [{self.provenance.value}: {self.source}]"


@dataclass(frozen=True)
class MaterialState:
    """What the plant is made of today. Hashed; every proposal records the hash."""

    cement_type: str = "OPC"
    cement_grade: Optional[int] = None          # 33 / 43 / 53
    cement_sg: float = 3.15
    flyash_sg: Optional[float] = None           # MATERIAL_SPECIFIC -- from the certificate
    ggbs_sg: Optional[float] = None             # MATERIAL_SPECIFIC -- from the certificate
    cement_28d_strength: Optional[float] = None
    sand_type: str = "crushed"                  # M-sand
    sand_sg: float = 2.65
    sand_absorption_pct: Optional[float] = None
    sand_passing_600um: Optional[float] = None  # the zone discriminator
    sand_full_grading: Optional[tuple] = None   # ((sieve, pct), ...) if the full sieve set exists
    ca_sg: float = 2.74
    ca_shape: str = "angular"
    ca_absorption_pct: Optional[float] = None
    msa_mm: Optional[float] = None              # ENGINEER/MATERIAL input. Never assumed.
    scms_available: tuple = ("flyash", "ggbs")
    admixture_sg: float = 1.08
    admixture_solids_pct: Optional[float] = None
    admixture_dosage_range_pct: Optional[tuple] = None   # from the manufacturer, IS 9103 cl 10.2
    # [IS] IS 1489 (Part 1) cl 9.1 -- the PPC certificate's declared fly ash percent. None ->
    #      the gate takes the 35 percent upper limit (worst case, plant-independent).
    ppc_fly_ash_declared_pct: Optional[float] = None
    # [IS] IS 456 cl 5.1 -- an 'other combination' (e.g. PPC + fly ash, OPC + fly ash + GGBS)
    #      needs satisfactory suitability data. A short record of that evidence, or None.
    combination_suitability_evidence: Optional[str] = None
    # [IS] IS 10262 Annex A-13 -- coarse aggregate split 20-10 mm : 10-4.75 mm. PLANT input;
    #      its IS 383 Table 7 conformity is a lab check ([NV] Table 7 not encoded).
    ca_split_20_10: Optional[tuple] = None

    def sand_zone(self) -> dict:
        """[IS] IS 383:2016 Table 9 + cl 6.3 -- assign the grading zone.

        cl 6.3 withholds the 5 percent single-sieve tolerance AT 600 um
        (IS383_CL_6_3_TOLERANCE_EXCLUDED), so the 600 um passing value alone
        assigns the zone -- there is nothing to fit and no fallback band.

        The four printed bands are disjoint and, AT WHOLE PERCENT, exhaustive over
        the printed range. They are NOT contiguous over the reals: Table 9 is
        printed in whole percent, so a reading strictly between two bands falls in
        a gap for which BIS states no rule. Such a reading is REFUSED, not rounded.

        Bands are read from is_rules; none are written here.
        """
        if self.sand_passing_600um is None:
            raise IS.MissingTableRow(
                "sand zone cannot be assigned: 600 um passing not supplied. "
                "NOT VERIFIED FROM PRIMARY STANDARD SOURCE -- do not assume Zone II."
            )
        assert IS.IS383_CL_6_3_TOLERANCE_EXCLUDED["sieve"] == "600um", (
            "is_rules no longer excludes 600 um from the cl 6.3 tolerance; "
            "the unique-assignment argument must be re-derived before use."
        )
        bands = IS.IS383_TABLE9_FINE_GRADING["600um"]
        p = float(self.sand_passing_600um)
        hit = [z for z, (lo, hi) in bands.items() if lo <= p <= hi]
        if len(hit) != 1:
            lo_all = min(b[0] for b in bands.values())
            hi_all = max(b[1] for b in bands.values())
            if p < lo_all or p > hi_all:
                why = (f"{p} percent is outside the whole printed range "
                       f"{lo_all}-{hi_all}: the sand conforms to NO IS 383 Table 9 zone.")
            else:
                why = (f"{p} percent falls in a printed GAP between adjacent bands. "
                       f"Table 9 is printed in whole percent and BIS states no rule for "
                       f"a fractional value between bands. "
                       f"NOT VERIFIED FROM PRIMARY STANDARD SOURCE -- this is refused "
                       f"rather than rounded. Rounding it is an engineering decision that "
                       f"must be recorded against this material, not made here.")
            raise IS.MissingTableRow(
                f"600 um passing: {why} Printed bands {dict(bands)}. "
                f"cl 6.3 withholds the 5 percent tolerance at 600 um, so this cannot be "
                f"resolved by tolerance."
            )
        out = {"zone": hit[0], "passing_600um": p,
               "band": bands[hit[0]],
               "source": "IS 383:2016 Table 9 (600 um row) + cl 6.3",
               "status": "verified"}

        # If the full grading is available, cross-check with the tolerance rule.
        if self.sand_full_grading:
            full = IS.classify_sand_zone(dict(self.sand_full_grading), sand_type=self.sand_type,
                                         use=IS.UseClass.RCC)
            out["full_grading_zones_satisfied"] = full["zones_satisfied"]
            out["full_grading_warnings"] = full.get("warnings", [])
            if hit[0] not in full["zones_satisfied"]:
                out["status"] = "conflict"
                out["conflict"] = (
                    f"600 um assigns Zone {hit[0]} but the full grading satisfies "
                    f"{full['zones_satisfied']}. Do not proceed on the 600 um value alone."
                )
        return out

    def state_hash(self) -> str:
        import hashlib
        blob = repr(sorted(asdict(self).items())).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()[:12]


@dataclass(frozen=True)
class Requirement:
    """A customer order. Input to Layer 0."""

    grade: str                                  # "M30"
    target_slump_mm: float
    exposure: "IS.Exposure"
    use: "IS.UseClass"
    pumpable: bool = False
    # [PC] What FRACTION of the cl 5.5.2 allowance to apply. cl 5.5.2 permits a
    #      reduction of the Table 5 coarse volume "up to 10 percent"; taking the full
    #      10 percent is a project choice, not a standards derivation, so it is a knob.
    pumpable_reduction_frac: float = 1.0
    # [IS] cl 5.3 permits the calculated water to be reduced by chemical admixture
    #      (5-10 percent WRA, 20-30 percent and above for superplasticizers). The
    #      MAGNITUDE is not fixed by the standard -- Annex C-6 took 23 percent "based on
    #      trial data". It must therefore be supplied, measured or fitted. None means
    #      "not supplied", and design_mix REFUSES if an admixture is dosed without it.
    water_reduction_pct: Optional[float] = None
    # PLANT-SPECIFIC input. [IS] IS 10262 cl 5.3 names temperature as a water-demand
    # driver. None -> the response model is evaluated at its training median and the
    # candidate says so.
    concrete_temp_c: Optional[float] = None
    sea_water: bool = False
    freeze_thaw: bool = False
    sulphate_class: Optional[int] = None
    # [IS] IS 456 cl 5.2.1 -- fly ash (a pozzolana) is used "with the permission of the
    #      engineer-in-charge". Recorded per order; the gate reports it until it is True.
    engineer_permission_recorded: bool = False
    established_s: Optional[float] = None       # plant standard deviation, if established
    n_results_for_s: Optional[int] = None       # how many results it came from

    def __post_init__(self):
        if self.target_slump_mm < 0:
            raise ValueError("target slump cannot be negative")
        if not (0.0 <= self.pumpable_reduction_frac <= 1.0):
            raise ValueError("pumpable_reduction_frac is a fraction of the cl 5.5.2 "
                             "allowance and must lie in [0, 1]")
        if self.water_reduction_pct is not None and not (0.0 <= self.water_reduction_pct < 100.0):
            raise ValueError("water_reduction_pct must lie in [0, 100)")


def permitted_fine_fraction_band(state: MaterialState, req: Requirement,
                                 wc_ratio: float) -> dict:
    """[IS] The band of fine-aggregate volume fractions the standard permits.

    IS 10262 : 2019 Table 5 (cl 5.5) gives the coarse aggregate volume per unit
    volume of total aggregate at w/c 0.50, by zone and nominal maximum size.
    cl 5.5.1 adjusts it by 0.01 per 0.05 change in w/c.
    cl 5.5.2 permits a reduction of the Table 5 coarse volume by UP TO 10 percent
    for pumped concrete or congested reinforcement.
    Table 5 Note 3: crushed or mixed sand normally needs LESSER fine aggregate, in
    which case the coarse volume shall be INCREASED.

    So fine fraction is a band, not a point:
        upper bound  = 1 - (adjusted CA volume x 0.90)     [cl 5.5.2 fully applied]
        nominal      = 1 - (adjusted CA volume)            [Table 5 + cl 5.5.1]
        lower bound  = nominal, or lower under Note 3      [magnitude not stated -> [EI]]

    Returns the band and refuses rather than guessing when a row is missing.
    """
    zone = state.sand_zone()
    zone_name = zone["zone"]
    if zone.get("status") == "conflict":
        raise IS.MissingTableRow(zone["conflict"])

    nominal = IS.coarse_aggregate_volume(req.grade, state.msa_mm, zone_name,
                                         wc_ratio, pumpable=False)
    reduced = IS.coarse_aggregate_volume(req.grade, state.msa_mm, zone_name,
                                         wc_ratio, pumpable=True)

    ca_nom = nominal["ca_volume_fraction"]
    ca_red = reduced["ca_volume_fraction"]          # cl 5.5.2 applied in FULL

    return {
        "zone": zone_name,
        "zone_status": zone.get("status"),
        "ca_volume_nominal": ca_nom,
        "ca_volume_min": ca_red,                      # cl 5.5.2 fully applied
        "fine_frac_nominal": 1.0 - ca_nom,
        "fine_frac_max": 1.0 - ca_red,                # most fine the code allows
        "fine_frac_min": 1.0 - ca_nom,                # Note 3 can go lower; magnitude [EI]
        "source_nominal": nominal["source"] + " + cl 5.5.1",
        "source_reduced": nominal["source"] + " + cl 5.5.1 + cl 5.5.2",
        "note3": ("[EI] Table 5 Note 3 permits LESS fine aggregate for crushed sand and a "
                  "correspondingly increased coarse volume, but states no magnitude. The "
                  "lower bound is therefore not quantified by the standard."),
    }


def fine_fraction_compliance(observed_fine_frac: float, band: dict) -> dict:
    """Is an observed fine fraction inside what Table 5 + cl 5.5.2 permit?

    Used on the training data in notebook 10 and on every candidate in notebook 11.
    An observation above fine_frac_max uses more fine aggregate than the standard
    permits at that zone, msa and w/c. It is flagged, never silently fitted.
    """
    hi = band["fine_frac_max"]
    inside = observed_fine_frac <= hi + 1e-9
    return {
        "inside": inside,
        "observed": observed_fine_frac,
        "permitted_max": hi,
        "excess": max(0.0, observed_fine_frac - hi),
        "verdict": "ok" if inside else "above IS 10262 Table 5 + cl 5.5.2 maximum",
    }


@dataclass(frozen=True)
class MixDesign:
    """A complete, code-checked mix. Never leaves Layer 0 without a gate verdict."""

    cement_kg_m3: float
    flyash_kg_m3: float
    ggbs_kg_m3: float
    water_kg_m3: float
    admixture_kg_m3: float
    coarse_agg_kg_m3: float
    fine_agg_kg_m3: float

    binder_kg_m3: float
    wc_ratio: float                 # water / TOTAL binder -- NOT the ratio IS 456 governs
    wc_counted: float               # water / COUNTED binder -- the governed one, cl Table 5 Note 1
    target_mean_strength: float
    ca_volume_fraction: float
    fine_frac_of_agg: float         # VOLUME fraction -- IS 10262 Table 5 is a volume table
    air_fraction: float
    volume_closure_m3: float

    grade: str
    target_slump_mm: float
    msa_mm: float
    sand_zone: str
    state_hash: str
    water_before_reduction_kg_m3: float
    water_reduction_pct: float
    sources_verified: bool
    sources_unverified: tuple = ()
    admixture_water_kg_m3: float = 0.0
    counted_binder_kg_m3: float = 0.0
    validation_level: ValidationLevel = ValidationLevel.COMPUTATIONALLY_COMPLIANT
    gate: dict = field(default_factory=dict)
    provenance: dict = field(default_factory=dict)

    @property
    def decided(self) -> bool:
        """The only property that may be used to accept a mix.

        Requires BOTH that every durability check decided AND that every standard
        it rests on verified against its frozen source. A mix designed from
        unverified constants is NOT VERIFIED FROM PRIMARY STANDARD SOURCE and may
        not be accepted, whatever the gate says.
        """
        return bool(self.gate.get("decided")) and self.sources_verified

    @property
    def cementitious_kg_m3(self) -> float:
        return self.cement_kg_m3 + self.flyash_kg_m3 + self.ggbs_kg_m3

    @property
    def fine_mass_frac_of_agg(self) -> float:
        """Fine aggregate as a MASS fraction of total aggregate.

        This is how the training datasets define `fine_frac_of_agg`, so it is what the
        response models must be given. `fine_frac_of_agg` on this object is the VOLUME
        fraction Table 5 works in. Feeding the volume value to a model trained on mass
        shifts every candidate by about +0.008.
        """
        return self.fine_agg_kg_m3 / (self.fine_agg_kg_m3 + self.coarse_agg_kg_m3)


SOURCES_OK, SOURCES_BAD = _source_status()


def _require_printed_msa(msa_mm, table, what):
    """[PC] Fail-safe: a nominal maximum size must BE a printed row, not round to one.

    is_rules falls back to int(msa) when the float key misses, which would design a
    20.6 mm mix off the 20 mm row and record it as 20.6. That is interpolation by
    another name, and the standard prints no rule for it.
    """
    if msa_mm is None:
        raise IS.MissingTableRow(
            "nominal maximum size of aggregate was not supplied. It is a key into "
            "IS 456 Tables 5 and 6 and IS 10262 Tables 3, 4 and 5 and must never be "
            "assumed. Supply MaterialState.msa_mm."
        )
    m = float(msa_mm)
    if m not in table and not (m.is_integer() and int(m) in table):
        raise IS.MissingTableRow(
            f"msa {msa_mm} mm is not a printed row of {what}. Printed rows: "
            f"{sorted(table)}. Do not interpolate or truncate."
        )
    return m


def design_mix(req: Requirement, state: MaterialState, *,
               binder_kg_m3: Optional[float] = None,
               flyash_frac: float = 0.0,
               ggbs_frac: float = 0.0,
               admixture_pct_of_binder: float = 0.0,
               wc_ratio: Optional[float] = None) -> MixDesign:
    """Turn a requirement into one complete, gate-checked mix.

    binder_kg_m3, the SCM fractions and the admixture dose are the three free knobs.
    Everything else is computed from the standards.

    Supplying BOTH binder_kg_m3 and wc_ratio is refused: water is fixed by cl 5.3,
    so the two over-determine the mix and one of them would be silently discarded.
    """
    prov = {}

    if flyash_frac < 0.0 or ggbs_frac < 0.0 or admixture_pct_of_binder < 0.0:
        raise ValueError("fractions and dosages must be non-negative; got "
                         f"flyash {flyash_frac}, ggbs {ggbs_frac}, "
                         f"admixture {admixture_pct_of_binder}")
    if flyash_frac + ggbs_frac >= 1.0:
        raise ValueError("SCM fractions must leave some cement")
    if binder_kg_m3 is not None and wc_ratio is not None:
        raise ValueError(
            "supply binder_kg_m3 OR wc_ratio, not both: water is fixed by IS 10262 "
            "cl 5.3, so binder and w/c determine each other and one would be discarded."
        )
    if binder_kg_m3 is not None and binder_kg_m3 <= 0:
        raise ValueError("binder must be positive")

    msa = _require_printed_msa(state.msa_mm, IS.IS10262_TABLE4_WATER, "IS 10262 Table 4")
    _require_printed_msa(msa, IS.IS10262_TABLE3_AIR, "IS 10262 Table 3")

    # ---- 1. [IS] IS 10262 cl 4.2 -- target mean strength -------------------
    tms = IS.target_mean_strength(req.grade, established_s=req.established_s,
                                  n_results=req.n_results_for_s)
    f_target = tms["target_mean"]
    prov["target_mean_strength"] = (Provenance.DERIVED_FROM_STANDARD,
                                    f"IS 10262 cl 4.2 / IS 456 cl 9.2.2 -- binding {tms['binding']}")

    # ---- 2. [IS] IS 456 Table 5 -- durability envelope ---------------------
    t5 = IS.table5_lookup(req.exposure, req.use, int(msa))
    max_wc = t5["max_free_wc"]
    min_binder = t5["min_cement_kg_m3"]
    prov["max_free_wc"] = (Provenance.DERIVED_FROM_STANDARD, "IS 456 Table 5")
    prov["min_binder"] = (Provenance.DERIVED_FROM_STANDARD, "IS 456 Table 5")

    if wc_ratio is not None and wc_ratio > max_wc + 1e-12:
        raise ValueError(f"w/c {wc_ratio} exceeds IS 456 Table 5 maximum {max_wc} "
                         f"for {req.exposure.name}/{req.use.name}")

    # ---- 3. [IS] IS 10262 Table 4 + cl 5.3 -- water ------------------------
    w = IS.water_content(req.grade, msa, req.target_slump_mm, ca_shape=state.ca_shape)
    water_gross = w["water_kg_m3"]

    # [IS] cl 5.3 -- the calculated water MAY be reduced by chemical admixture.
    #      The standard gives ranges (5-10 percent WRA, 20-30 percent and above for
    #      superplasticizers) but fixes no value; Annex C-6 took 23 percent from trial
    #      data. So the magnitude is supplied, never assumed.
    red = req.water_reduction_pct
    if admixture_pct_of_binder > 0.0 and red is None:
        raise ValueError(
            "an admixture is dosed but Requirement.water_reduction_pct was not supplied. "
            "IS 10262 cl 5.3 permits the calculated water to be reduced by chemical "
            "admixture but states no single value (5-10 percent for water reducers, "
            "20-30 percent and above for superplasticizers; Annex C-6 used 23 percent "
            "from trial data). Designing at 0 percent reduction puts the mix at a water "
            "content no real batch uses. Supply a measured or fitted value."
        )
    red = 0.0 if red is None else float(red)
    water = water_gross * (1.0 - red / 100.0)
    prov["water_kg_m3"] = (
        Provenance.DERIVED_FROM_STANDARD if red == 0.0 else Provenance.EXPERIMENTALLY_DETERMINED,
        w["source"] + " + cl 5.3 shape adjust"
        + (f"; cl 5.3 admixture reduction {red:.2f}% [supplied]" if red else ""))

    # ---- 4. [IS] cl 5.4 -- binder ------------------------------------------
    if binder_kg_m3 is None and wc_ratio is not None:
        binder_kg_m3 = max(water / wc_ratio, min_binder)
        prov["binder_kg_m3"] = (Provenance.ENGINEER_INPUT,
                                "IS 10262 cl 5.4 water/(w/cm), floored at IS 456 Table 5 minimum")
    elif binder_kg_m3 is None:
        # [IS] cl 5.1.1 -- the w/c is the LOWER of the strength value and the durability
        #      limit; its NOTE adds the admixture's water; cl 5.1.2 forms w/cm over the
        #      binder IS 456 Table 5 Note 1 lets count. Every term is proportional to the
        #      binder at fixed SCM shares and dose, so the binder that puts the COUNTED w/c
        #      exactly on the Table 5 maximum has a closed form:
        #         (water + a.B) / (k.B) = max_wc  ->  B = water / (k.max_wc - a)
        #      k = counted binder per kg of binder, a = admixture water per kg of binder.
        c1 = 1.0 - flyash_frac - ggbs_frac
        ca1 = IS.counted_additions(c1, flyash_frac, ggbs_frac, state.cement_type,
                                   ppc_fly_ash_declared_pct=state.ppc_fly_ash_declared_pct,
                                   suitability_evidence=state.combination_suitability_evidence)
        k = c1 + ca1["flyash_kg"] + ca1["ggbs_kg"]
        a = admixture_pct_of_binder / 100.0 * (
            1.0 - float(state.admixture_solids_pct) / 100.0
            if state.admixture_solids_pct is not None else 1.0)
        if k * max_wc - a <= 0:
            raise ValueError("no binder can bring the counted w/c to the Table 5 maximum "
                             "at these SCM shares and admixture dose")
        binder_kg_m3 = max(water / (k * max_wc - a), min_binder)
        prov["binder_kg_m3"] = (
            Provenance.STANDARD_DEFAULT,
            "IS 10262 cl 5.1.1 (+NOTE) / 5.1.2 / 5.4: binder putting the counted w/c on the "
            "IS 456 Table 5 maximum, floored at the Table 5 minimum")
    else:
        prov["binder_kg_m3"] = (Provenance.ENGINEER_INPUT, "search knob")
    wc_total = water / binder_kg_m3
    prov["wc_ratio"] = (Provenance.DERIVED_FROM_STANDARD,
                        "water (cl 5.3) / TOTAL binder -- see wc_counted for the governed ratio")

    # ---- 5. SCM split; [IS] IS 456 cl 8.2.4.2 caps CEMENT only -------------
    flyash = binder_kg_m3 * flyash_frac
    ggbs = binder_kg_m3 * ggbs_frac
    cement = binder_kg_m3 - flyash - ggbs
    prov["cement_kg_m3"] = (Provenance.DERIVED_FROM_STANDARD,
                            "binder minus SCM; ceiling IS 456 cl 8.2.4.2 (cement only)")

    # [IS] IS 456 Table 5 Note 1 -- only part of the fly ash COUNTS toward the binder
    #      the w/c is formed over. This is the ratio the code actually governs.
    admixture = binder_kg_m3 * admixture_pct_of_binder / 100.0
    # [IS] IS 10262 cl 5.1.1 NOTE -- water contributed by the admixture is counted in the
    #      w/c check. [EI] With no declared solids content the whole admixture mass is
    #      taken as water (worst case).
    if admixture > 0 and state.admixture_solids_pct is not None:
        adm_water = admixture * (1.0 - float(state.admixture_solids_pct) / 100.0)
        adm_water_src = f"admixture x (1 - {state.admixture_solids_pct:.1f}% solids)"
    else:
        adm_water = admixture
        adm_water_src = "solids not declared: whole admixture taken as water [EI]"

    # [IS] IS 456 Table 5 Note 1 + IS 1489 (Part 1) cl 5 + IS 455:2015 cl 5 -- only part of
    #      the fly ash and GGBS COUNTS toward the binder the w/c is formed over.
    #      Note 1 also counts them only 'if the suitability is established'.
    cadd = IS.counted_additions(cement, flyash, ggbs, state.cement_type,
                                ppc_fly_ash_declared_pct=state.ppc_fly_ash_declared_pct,
                                suitability_evidence=state.combination_suitability_evidence)
    counted_binder = cement + cadd["flyash_kg"] + cadd["ggbs_kg"]
    wc_counted = ((water + adm_water) / counted_binder if counted_binder > 0
                  else float("inf"))
    prov["wc_counted"] = (Provenance.DERIVED_FROM_STANDARD,
                          "IS 456 Table 5 Note 1 + IS 1489 (Part 1) cl 5 + IS 455:2015 cl 5 ("
                          + cadd["basis"] + "); IS 10262 cl 5.1.1 NOTE (" + adm_water_src + ")")
    prov["admixture_kg_m3"] = (Provenance.ENGINEER_INPUT, "search knob, IS 9103 cl 10.2 range")

    # ---- 6. [IS] IS 10262 Table 3 -- entrapped air -------------------------
    air = IS.IS10262_TABLE3_AIR[msa if msa in IS.IS10262_TABLE3_AIR else int(msa)] / 100.0
    prov["air_fraction"] = (Provenance.DERIVED_FROM_STANDARD, "IS 10262 Table 3")

    # ---- 7. [IS] Table 5 + cl 5.5.1 (+ 5.5.2) -- coarse aggregate volume ---
    band = permitted_fine_fraction_band(state, req, wc_total)
    if req.pumpable:
        # [PC] cl 5.5.2 permits a reduction "up to 10 percent". How much of that
        #      allowance to take is a PROJECT choice, not a standards derivation.
        f = req.pumpable_reduction_frac
        ca_vol_frac = band["ca_volume_nominal"] + f * (band["ca_volume_min"] - band["ca_volume_nominal"])
        prov["ca_volume_fraction"] = (
            Provenance.ENGINEER_INPUT,
            band["source_reduced"] + f" at {100*f:.0f}% of the cl 5.5.2 allowance [PC]")
    else:
        ca_vol_frac = band["ca_volume_nominal"]
        prov["ca_volume_fraction"] = (Provenance.DERIVED_FROM_STANDARD, band["source_nominal"])

    # ---- 8. [IS] cl 5.7 -- volume closure ----------------------------------
    if flyash > 0 and state.flyash_sg is None:
        raise ValueError("fly ash is used but MaterialState.flyash_sg was not supplied. "
                         "IS 3812 (Part 1) specifies fineness and chemistry, not a design "
                         "specific gravity -- it comes from the material certificate.")
    if ggbs > 0 and state.ggbs_sg is None:
        raise ValueError("GGBS is used but MaterialState.ggbs_sg was not supplied. "
                         "IS 16714 specifies fineness and chemistry, not a design specific "
                         "gravity -- it comes from the material certificate.")

    v_cement = cement / (state.cement_sg * 1000.0)
    v_flyash = flyash / (state.flyash_sg * 1000.0) if flyash > 0 else 0.0
    v_ggbs = ggbs / (state.ggbs_sg * 1000.0) if ggbs > 0 else 0.0
    v_water = water / 1000.0
    v_adm = admixture / (state.admixture_sg * 1000.0) if admixture > 0 else 0.0

    v_agg = (1.0 - air) - (v_cement + v_flyash + v_ggbs + v_water + v_adm)
    if v_agg <= 0:
        raise ValueError("no volume left for aggregate -- binder or water is too high")

    coarse = v_agg * ca_vol_frac * state.ca_sg * 1000.0
    fine = v_agg * (1.0 - ca_vol_frac) * state.sand_sg * 1000.0
    prov["coarse_agg_kg_m3"] = (Provenance.DERIVED_FROM_STANDARD, "IS 10262 cl 5.7")
    prov["fine_agg_kg_m3"] = (Provenance.DERIVED_FROM_STANDARD, "IS 10262 cl 5.7")

    # [PC] Closure recomputed INDEPENDENTLY from the returned masses and specific
    #      gravities. Summing the same v_agg that was just solved for would be
    #      identically 1.0 and could never detect a wrong specific gravity or a
    #      missing constituent -- and it feeds a HARD gate check.
    closure = (cement / (state.cement_sg * 1000.0)
               + (flyash / (state.flyash_sg * 1000.0) if flyash > 0 else 0.0)
               + (ggbs / (state.ggbs_sg * 1000.0) if ggbs > 0 else 0.0)
               + water / 1000.0
               + (admixture / (state.admixture_sg * 1000.0) if admixture > 0 else 0.0)
               + coarse / (state.ca_sg * 1000.0)
               + fine / (state.sand_sg * 1000.0)
               + air)

    # ---- 9. the gate --------------------------------------------------------
    gate = IS.compliance_gate(
        cement_kg_m3=cement, fly_ash_kg_m3=flyash, ggbs_kg_m3=ggbs, other_scm_kg_m3=0.0,
        grade=req.grade, exposure=req.exposure, use=req.use, msa_mm=int(msa),
        free_water_kg_m3=water, cement_type=state.cement_type,
        sulphate_class_=req.sulphate_class, sea_water=req.sea_water,
        freeze_thaw=req.freeze_thaw, volume_closure_m3=closure,
        admixture_kg_m3=admixture if admixture else None,
        admixture_dosage_range_pct=state.admixture_dosage_range_pct,
        ppc_fly_ash_declared_pct=state.ppc_fly_ash_declared_pct,
        admixture_water_kg_m3=adm_water,
        combination_suitability_evidence=state.combination_suitability_evidence,
        engineer_permission_recorded=req.engineer_permission_recorded,
    )

    return MixDesign(
        cement_kg_m3=cement, flyash_kg_m3=flyash, ggbs_kg_m3=ggbs, water_kg_m3=water,
        admixture_kg_m3=admixture, coarse_agg_kg_m3=coarse, fine_agg_kg_m3=fine,
        binder_kg_m3=binder_kg_m3, wc_ratio=wc_total, wc_counted=wc_counted,
        target_mean_strength=f_target,
        ca_volume_fraction=ca_vol_frac, fine_frac_of_agg=1.0 - ca_vol_frac,
        air_fraction=air, volume_closure_m3=closure,
        grade=req.grade, target_slump_mm=req.target_slump_mm, msa_mm=msa,
        sand_zone=band["zone"], state_hash=state.state_hash(),
        water_before_reduction_kg_m3=water_gross, water_reduction_pct=red,
        sources_verified=SOURCES_OK, sources_unverified=tuple(SOURCES_BAD),
        admixture_water_kg_m3=adm_water, counted_binder_kg_m3=counted_binder,
        gate=gate, provenance=prov,
    )


def _failing(m):
    return [c["check"] for c in m.gate["checks"]
            if c["outcome"] in ("fail", "override_required")] or (m.gate.get("hard_not_verified") or [])


def _nearest_decided(req, state, kw, b_ok, b_target, steps=40):
    """Bisect the binder from a decided design (b_ok) toward b_target. Every limit that
    can stop a trial (cement ceiling, Table 5 w/c and minimum binder) is monotone in the
    binder at fixed water, so the boundary is unique."""
    lo, hi, best = b_ok, b_target, None
    for _ in range(steps):
        mid = 0.5 * (lo + hi)
        m = design_mix(req, state, binder_kg_m3=mid, **kw)
        if m.decided:
            best, lo = m, mid
        else:
            hi = mid
    return best


def trial_set(req, state, *, binder_kg_m3, flyash_frac=0.0, ggbs_frac=0.0,
              admixture_pct_of_binder=0.0, trial2_water_kg_m3=None):
    """[IS] IS 10262 cl 5.8 + Annex A-14, A-15 -- three trial batches around one design.

    Trial 1/2 : the design (No. 1; becomes No. 2 after any slump correction)
    Trial 3   : same water as No. 2, w/cm x 0.90
    Trial 4   : same water as No. 2, w/cm x 1.10
    w/cm is water / total cementitious, IS 10262 cl 3.2. The SCM shares and the admixture
    percent are held, so only the binder moves -- exactly what cl 5.8 varies.

    trial2_water_kg_m3 -- [IS] cl 5.8: Trials 3 and 4 use the water of Trial No. 2. Before
    Trial 1 is cast that is the design water. If Trial 1 needed a water correction, pass
    the corrected water here: the w/cm is kept at the pre-selected value and the whole set
    is rebuilt around it.
    """
    kw = dict(flyash_frac=flyash_frac, ggbs_frac=ggbs_frac,
              admixture_pct_of_binder=admixture_pct_of_binder)
    base = design_mix(req, state, binder_kg_m3=binder_kg_m3, **kw)
    if trial2_water_kg_m3 is not None:
        # keep the pre-selected w/cm (cl 5.8) at the corrected water
        red = 100.0 * (1.0 - float(trial2_water_kg_m3) / base.water_before_reduction_kg_m3)
        req = replace(req, water_reduction_pct=red)
        base = design_mix(req, state, binder_kg_m3=float(trial2_water_kg_m3) / base.wc_ratio, **kw)
    if not base.decided:
        raise ValueError(f"the design itself is not decided ({_failing(base)}); "
                         f"no trial set can be built around it")
    v = IS.IS10262_CL_5_8_WC_VARIATION
    out = [{"trial_no": 1 if trial2_water_kg_m3 is None else 2,
            "role": "design (Trial Mix No. 1 -> No. 2 after any slump correction)",
            "wcm_target": base.wc_ratio, "mix": base,
            "note": "IS 10262 cl 5.8: measure workability first; if off, adjust water and/or "
                    "admixture keeping the pre-selected w/cm and recompute (= Trial No. 2); "
                    "Trials 3 and 4 then use the No. 2 water"}]
    for no, f, label in ((2, 1.0 - v, "-10 %"), (3, 1.0 + v, "+10 %")):
        wcm_t = base.wc_ratio * f
        m = design_mix(req, state, binder_kg_m3=base.water_kg_m3 / wcm_t, **kw)
        note = f"same water, w/cm {label} (IS 10262 cl 5.8)"
        if not m.decided:
            why = _failing(m)
            m2 = _nearest_decided(req, state, kw, base.binder_kg_m3, base.water_kg_m3 / wcm_t)
            if m2 is None:
                out.append({"trial_no": no + 1, "role": f"w/cm {label}", "wcm_target": wcm_t,
                            "mix": None, "note": f"REFUSED: {why} at every w/cm toward {label}"})
                continue
            note = (f"w/cm {label} would be {wcm_t:.3f} but fails {why}; set at the nearest "
                    f"compliant w/cm {m2.wc_ratio:.3f} [EI, after IS 10262 A-15: 'durability "
                    f"requirement shall be met']")
            m = m2
        # [EI] a 4th trial that cannot move 2 % from the design would duplicate it and A-15's
        #      three-point graph could not be drawn: use w/cm -5 % instead (is_rules
        #      IS10262_TRIAL_MIN_SEPARATION / IS10262_TRIAL_FALLBACK_VARIATION).
        if no == 3 and m.wc_ratio < base.wc_ratio * (1.0 + IS.IS10262_TRIAL_MIN_SEPARATION):
            w5 = base.wc_ratio * (1.0 - IS.IS10262_TRIAL_FALLBACK_VARIATION)
            m = design_mix(req, state, binder_kg_m3=base.water_kg_m3 / w5, **kw)
            note = (f"w/cm +10 % ({wcm_t:.3f}) is limited by IS 456 to within 2 % of the design, "
                    f"which would duplicate Trial 1/2; replaced by w/cm -5 % ({w5:.3f}) so three "
                    f"distinct w/cm values exist for the A-15 graph [EI]")
            label = "-5 % (replaces +10 %)"
            if not m.decided:
                out.append({"trial_no": no + 1, "role": label, "wcm_target": w5, "mix": None,
                            "note": f"REFUSED: {_failing(m)}"})
                continue
        out.append({"trial_no": no + 1, "role": f"w/cm {label}", "wcm_target": wcm_t,
                    "mix": m, "note": note})
    return out


def batch_sheet(mix, state, *, volume_m3, sand_moisture_pct, ca_moisture_pct,
                round_kg=0.01):
    """What the lab weighs for one batch. [IS] IS 10262 Annex A-10 NOTE, A-11, A-13.

    Design quantities are SSD (A-10 NOTE). The day's total moisture of each aggregate
    (percent of oven-dry mass, measured on the day) and its absorption (IS 2386 Part 3
    cl 2, from MaterialState) convert them to weighed masses and a corrected water.
    [IS] Annex A-10 / A-12 list the admixture separately from the mixing water.
    [EI] Its water is therefore NOT subtracted from the water to add; it enters only the
    w/c check (cl 5.1.1 NOTE).
    [PC] round_kg -- scale resolution; the admixture is rounded to 1 g.
    """
    if mix is None:
        raise ValueError("no mix to batch")
    if state.sand_absorption_pct is None or state.ca_absorption_pct is None:
        raise ValueError("IS 10262 Annex A-10 NOTE: water absorption of both aggregates "
                         "(IS 2386 Part 3 cl 2) is needed to batch from SSD quantities")
    V = float(volume_m3)
    fa = IS.aggregate_moisture_adjustment(mix.fine_agg_kg_m3 * V, state.sand_absorption_pct,
                                          sand_moisture_pct)
    ca = IS.aggregate_moisture_adjustment(mix.coarse_agg_kg_m3 * V, state.ca_absorption_pct,
                                          ca_moisture_pct)
    water = mix.water_kg_m3 * V + fa["water_adjust_kg"] + ca["water_adjust_kg"]
    r = lambda x: round(x / round_kg) * round_kg
    rows = [
        ("cement (" + state.cement_type + ")", mix.cement_kg_m3, r(mix.cement_kg_m3 * V)),
        ("fly ash", mix.flyash_kg_m3, r(mix.flyash_kg_m3 * V)),
        ("GGBS", mix.ggbs_kg_m3, r(mix.ggbs_kg_m3 * V)),
        ("water to add (corrected)", mix.water_kg_m3, r(water)),
        ("admixture", mix.admixture_kg_m3, round(mix.admixture_kg_m3 * V, 3)),
        ("fine aggregate (as weighed)", mix.fine_agg_kg_m3, r(fa["weigh_kg"])),
    ]
    if state.ca_split_20_10:
        a, b = state.ca_split_20_10
        tot = a + b
        rows += [("coarse 20-10 mm (as weighed)", mix.coarse_agg_kg_m3 * a / tot,
                  r(ca["weigh_kg"] * a / tot)),
                 ("coarse 10-4.75 mm (as weighed)", mix.coarse_agg_kg_m3 * b / tot,
                  r(ca["weigh_kg"] * b / tot))]
    else:
        rows += [("coarse aggregate (as weighed)", mix.coarse_agg_kg_m3, r(ca["weigh_kg"]))]
    return {"rows": [{"material": m_, "design_ssd_kg_m3": round(d, 2), "batch_kg": b_}
                     for m_, d, b_ in rows if d > 0],
            "volume_m3": V,
            "water_adjust_fine_kg": fa["water_adjust_kg"], "water_adjust_coarse_kg": ca["water_adjust_kg"],
            "sand_moisture_pct": sand_moisture_pct, "ca_moisture_pct": ca_moisture_pct,
            "sand_absorption_pct": state.sand_absorption_pct, "ca_absorption_pct": state.ca_absorption_pct,
            "source": "IS 10262 Annex A-10 NOTE, A-11, A-13; absorption/moisture per IS 2386 (Part 3)"}
