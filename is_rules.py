"""IS-code layer for the M-Sand SDL.

GENERATED FILE - do not edit. Edit 00_is_codes_layer.ipynb and re-run its export cell.

Every value here was read from a frozen, hash-verified BIS PDF. Call
verify_sources() before trusting any of it, REGISTRY for status and caveats,
and unresolved() for what cannot bind as a hard constraint.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

try:
    STANDARDS_DIR = Path(__file__).resolve().parent / 'IS_codes'
except NameError:
    STANDARDS_DIR = Path('IS_codes')


"""S01 CODIFY — types, statuses and refusals."""




class Status(Enum):
    """May this rule be applied as a hard constraint?"""
    VERIFIED           = "verified"
    UNVERIFIED         = "unverified"
    CONFLICT           = "conflict"
    PROJECT_CONSTRAINT = "project_constraint"
    GUIDANCE           = "guidance"      # 'suggested' / 'recommended' / 'should': informs, never binds


class Confidence(Enum):
    """How legible was the printed source for this particular value?"""
    PRINT_CLEAN       = "print_clean"
    OCR_RECONSTRUCTED = "ocr_reconstructed"


class Domain(Enum):
    """Grade domain. Decides which chain of IS 10262 applies. Routed FIRST."""
    NOMINAL       = "A"   # M5, M7.5 — IS 456 Table 9, no design mix exists
    ORDINARY      = "B"   # M10-M60  — IS 10262 Section 2 (cl 5)
    HIGH_STRENGTH = "C"   # M65+     — IS 10262 Section 3 (cl 6)


class UseClass(Enum):
    """Three values, not two. IS 456 cl 6.1.2 and cl 6.1.3."""
    RCC                   = "rcc"
    PCC                   = "pcc"
    LEAN_SIMPLE_TEMPORARY = "cl_6_1_3"


class Exposure(Enum):
    MILD        = "mild"
    MODERATE    = "moderate"
    SEVERE      = "severe"
    VERY_SEVERE = "very_severe"
    EXTREME     = "extreme"


# ----------------------------------------------------------------- refusals
class MissingTableRow(LookupError):
    """The standard prints no row for this input. Never interpolate or extend."""


class UnverifiedRule(RuntimeError):
    """A rule was asked to bind as a hard constraint but its status forbids it."""


class OcrUnconfirmed(RuntimeError):
    """A value reconstructed from a damaged glyph was asked to bind unconfirmed."""


class AgreedBetweenParties(LookupError):
    """The standard deliberately prints no value: it delegates it to supplier-purchaser
    agreement. Not a gap in our reading -- a gap the code leaves on purpose."""


BINDING = frozenset({"verified", "project_constraint"})   # string values, see _v()


def _v(x) -> str:
    """Enum member OR its string value -> the string value.

    Notebooks re-run cells out of order. Re-running the cell that defines an Enum
    creates a NEW class whose members are not identical to the ones already used as
    dict keys elsewhere. Every table below is therefore keyed by the string value,
    and every cross-cell comparison goes through this. Re-run any cell, any order.
    """
    return x.value if isinstance(x, Enum) else str(x)


@dataclass(frozen=True)
class Rule:
    standard:   str
    clause:     str
    subject:    str
    status:     Status
    confidence: Confidence = Confidence.PRINT_CLEAN
    caveats:    tuple[str, ...] = ()

    def as_hard_constraint(self, *, allow_ocr: bool = False) -> "Rule":
        """Return self only if this rule may legally bind. Otherwise refuse, loudly."""
        if _v(self.status) not in BINDING:
            raise UnverifiedRule(
                f"{self.standard} {self.clause} ({self.subject}) is "
                f"{_v(self.status)} and cannot be used as a hard constraint."
            )
        if _v(self.confidence) == "ocr_reconstructed" and not allow_ocr:
            raise OcrUnconfirmed(
                f"{self.standard} {self.clause} ({self.subject}) was reconstructed "
                f"from a damaged glyph in the scanned copy. Confirm against a clean "
                f"print, or pass allow_ocr=True to proceed with that risk recorded."
            )
        return self


"""Frozen source manifest. A value may not be used if its source hash does not match."""


SOURCES = {
    "IS 456:2000": {
        "file":    "is.456.2000.pdf",
        "sha256":  "13d8a479c84f76d7c08b5df550b6bcfb87131785e306f42bc2faae1d91537b6b",
        "edition": "Fourth Revision, Tenth Reprint April 2007, including Amendments No. 1 and 2",
    },
    "IS 10262:2019": {
        "file":    "IS-10262-2019.pdf",
        "sha256":  "a7fe4d7e041101afdd25ea1a307f5fb436039d1137a85305bda3351023f582a2",
        "edition": "Second Revision",
    },
    "IS 383:2016": {
        "file":    "IS-383-2016.pdf",
        "sha256":  "efd39afe2b03f088e3896eba5c8bbac19f308b4f2b18502401e9078a7feff7dd",
        "edition": "Third Revision, January 2016",
        "note":    "Scanned image, no text layer. Readable only as page images.",
    },
    "IS 9103:1999": {
        "file":    "IS.9103.1999.pdf",
        "sha256":  "765253d87d3d70c048bd5eae7c995d3701d874c699ede3f5c123c7dd366e6b38",
        "edition": "-",
    },
    "IS 4926:2003": {
        "file":    "is.4926.2003.pdf",
        "sha256":  "b9b5d4e39ab03a9ec7c5af7b7da52f18478dedc85ffba847ba95107e02b53ad0",
        "edition": "Second Revision",
    },
    "IS 3812 (Part 1):2013": {
        "file":    "is.3812.1.2013.pdf",
        "sha256":  "f77c5d499bb301e677f2fec94d6450ee7a160f3f48986992125e6d7291ad2584",
        "edition": "Third Revision",
    },
    "IS 16714:2018": {
        "file":    "IS16714_2018.pdf",
        "sha256":  "00e30b04164ed9ee72bdca3a932026c120fa07e6a91681fda3f1d41b25d45fc2",
        "edition": "2018 (no revision number printed)",
    },
    "IS 1199 (Part 2):2018": {
        "file":    "IS1199_Part2_2018.pdf",
        "sha256":  "758e60080297b63766b0921e4bb5507d9b07fee1bd384281b44f3503b55780c5",
        "edition": "First Revision",
    },
    "IS 1489 (Part 1):1991": {
        "file":    "is.1489.1.1991.pdf",
        "sha256":  "db6f0fed643f3b19c5a1999f2848a42d0f4a98891ecbb5be55bd5123e7cb3592",
        "edition": "Third Revision, with Amendments No. 1 (1991), 2 (1993), 3 (2000), 4 (2005), 5 (2009)",
    },
    "IS 455:2015": {
        "file":    "IS_455_2015_amd1_reff2020.pdf",
        "sha256":  "6fff8cdefcc954b2a2f362a84a601e0b838730d86750f58be5da411b5692dacf",
        "edition": "Fifth Revision, Reaffirmed 2020, with Amendment No. 1 (June 2018)",
    },
    "IS 269:2015": {
        "file":    "IS_269_2015_reff2020.pdf",
        "sha256":  "f0d116e6fbd92c5ce4f6b55da3edfc07d4d0acc1bbfa10dd070156a5dafac18c",
        "edition": "Sixth Revision, Reaffirmed 2020",
    },
    "IS 516 (Part 1/Sec 1):2021": {
        "file":    "IS516_Part1_Sec1_2021.pdf",
        "sha256":  "beb6ea0619fe6b84e1887014009a23ffad18c3621c264e5bae447cfd394e25f1",
        "edition": "First Revision",
    },
    "IS 1199 (Part 1):2018": {
        "file":    "IS1199_Part1_2018.pdf",
        "sha256":  "99c4d12ca092d312dd21a97e278e6d4108fe021d3224bae9dae78fcae3767642",
        "edition": "First Revision",
    },
    "IS 1199 (Part 3):2018": {
        "file":    "IS1199_Part3_2018.pdf",
        "sha256":  "29d1dd5f56e4f16736e8734593d6e177382f9c598b88de70126ec892acd937d2",
        "edition": "First Revision",
    },
    "IS 1199 (Part 5):2018": {
        "file":    "IS1199_Part5_2018.pdf",
        "sha256":  "8338b0d7b5cbbc31105bc1748279a5637242daeb1d533261b8c67d3624e0261a",
        "edition": "First Revision",
    },
    "IS 2386 (Part 3):1963": {
        "file":    "is.2386.3.1963.pdf",
        "sha256":  "de6a863b18117a61664fc13944fff166361aed38f80cbb6cbca3a03964126c0c",
        "edition": "Reaffirmed 2002 (cover image), Eighth Reprint March 1997",
    },
}


class SourceState(Enum):
    OK       = "ok"          # byte-identical to the copy the values were read from
    MISSING  = "missing"     # wrong directory, or the file was moved
    MISMATCH = "mismatch"    # a DIFFERENT file is sitting under this name


def verify_sources(strict: bool = False) -> dict:
    """Hash every frozen PDF against the manifest.

    MISSING and MISMATCH are not the same failure. MISSING means you ran from the
    wrong directory. MISMATCH means the evidence changed under you, and no value in
    this layer can be trusted until you find out why.
    """
    out = {}
    for name, meta in SOURCES.items():
        p = STANDARDS_DIR / meta["file"]
        if not p.exists():
            out[name] = ("missing", str(p))
        else:
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            out[name] = (("ok", meta["edition"]) if h == meta["sha256"]
                         else ("mismatch", f"got {h[:16]}..."))
    if strict:
        bad = {k: v for k, v in out.items() if v[0] != "ok"}
        if bad:
            raise RuntimeError(f"source verification failed: {bad}")
    return out


if __name__ == "__main__":
    for _n, (_state, _detail) in verify_sources().items():
        print(f"{_state.upper():9s} {_n:16s} {_detail}")


"""IS 456 : 2000. Table 5, Table 6, cl 8.2.4.2, cl 6.1.1-6.1.3, cl 9.1.1."""

_CLEAN = Confidence.PRINT_CLEAN
_OCR   = Confidence.OCR_RECONSTRUCTED

# Table 5 (Clauses 6.1.2, 8.2.4.1, 9.1.2) — 20 mm nominal max size, normal weight.
#
# [IS] Values read from is.456.2000.pdf. The TEXT LAYER of this page is damaged
#      (S<->5, O<->0, ~<->5, J<->3, I<->1), which is why ten cells were once flagged
#      OCR_RECONSTRUCTED. v3 re-read every cell from a 400 dpi render of printed page 20:
#      all 30 are legible and equal the values below (Extreme/PCC '280' carries a stray
#      tick above the 2; the digits read 280). All cells are therefore PRINT_CLEAN.
# [IS] Note 1 — the MINIMUM is inclusive of fly ash / GGBS additions, conditional on
#      the pozzolana and slag limits of IS 1489 (Part 1) and IS 455 respectively.
#      Neither has been read -> see CAVEAT_TABLE5_NOTE1.
# [IS] Note 2 — minimum grade for plain concrete under mild exposure is not specified.
#
# Each cell is (value, Confidence).
# Keyed by STRING values, not Enum members -- see _v() above.
IS456_TABLE5 = {
    #              PLAIN/RCC: min_cement kg/m3,  max_free_wc,      min_grade
    "mild": {
        "pcc": ((220, _CLEAN), (0.60, _CLEAN), (None, _CLEAN)),   # Note 2
        "rcc": ((300, _CLEAN), (0.55, _CLEAN),   ("M20", _CLEAN)),
    },
    "moderate": {
        "pcc": ((240, _CLEAN), (0.60, _CLEAN), ("M15", _CLEAN)),
        "rcc": ((300, _CLEAN), (0.50, _CLEAN),   ("M25", _CLEAN)),
    },
    "severe": {
        "pcc": ((250, _CLEAN),   (0.50, _CLEAN),   ("M20", _CLEAN)),
        "rcc": ((320, _CLEAN), (0.45, _CLEAN),   ("M30", _CLEAN)),
    },
    "very_severe": {
        "pcc": ((260, _CLEAN), (0.45, _CLEAN), ("M20", _CLEAN)),
        "rcc": ((340, _CLEAN), (0.45, _CLEAN), ("M35", _CLEAN)),
    },
    "extreme": {
        "pcc": ((280, _CLEAN),   (0.40, _CLEAN), ("M25", _CLEAN)),
        "rcc": ((360, _CLEAN), (0.40, _CLEAN), ("M40", _CLEAN)),
    },
}

# [IS] Independently corroborated from IS 10262:2019 Annex A-7 and Annex B-5, which
#      both print "From Table 5 of IS 456, minimum cement content for 'severe'
#      exposure condition = 320 kg/m3". That cell is therefore PRINT_CLEAN.

# Table 6 (Clause 8.2.4.1) — adjustment to the Table 5 MINIMUM for other msa. [IS]
IS456_TABLE6_CEMENT_ADJUST = {10: +40, 20: 0, 40: -30}      # kg/m3

# ------------------------------------------------------------ cl 8.2.4.2
# [IS] Verbatim: "Cement content not including fly ash and ground granulated blast
#      furnace slag in excess of 450 kg/m3 should not be used unless special
#      consideration has been given in design to the increased risk of cracking due
#      to drying shrinkage in thin sections, or to early thermal cracking and to the
#      increased risk of damage due to alkali silica reactions."
IS456_CL_8_2_4_2_MAX_CEMENT = 450.0          # kg/m3, CEMENT ONLY, excluding fly ash + GGBS

# [IS] No IS limit on TOTAL cementitious. IS 10262:2019 Annex D (M70 example) uses
#      535 kg/m3 cementitious (428 OPC + 26.75 silica fume + 80.25 fly ash) and checks
#      only "maximum cement (OPC) content, 450 kg/m3 > 428 kg/m3. Hence OK."
#      IS 10262 cl 6.2.6 repeats: cement "not including any mineral admixtures".
#      So the project follows the IS limit only: cement <= 450, fly ash/GGBS excluded.

# [EI] The verb is "should not ... unless". Encoding it as a silent hard reject is
#      STRICTER than the code. It is implemented as a constraint with a documented
#      override that records the special consideration -- which is what the clause
#      itself contemplates.

# [IS] cl 6.1.1 — "The characteristic strength is defined as the strength of material
#      below which not more than 5 percent of the test results are expected to fall."
IS456_CL_6_1_1_FRACTILE = 0.05

# [IS] cl 9.2.2 — target mean = characteristic strength + 1.65 x standard deviation.
IS456_CL_9_2_2_MULTIPLIER = 1.65

# [IS] cl 6.1.2 — "The minimum grade of concrete for plain and reinforced concrete
#      shall be as per Table 5."
# [IS] cl 6.1.3 — "Concrete of grades lower than those given in Table 5 may be used
#      for plain concrete constructions, lean concrete, simple foundations,
#      foundation for masonry walls and other simple or temporary reinforced
#      concrete construction."
#      -> this is why UseClass has THREE values. M10-M20 are legal here and nowhere else.

# [IS] cl 9.1.1 — proportions shall be determined either by designing the mix
#      ('design mix concrete') or by adopting a nominal mix.

CAVEAT_TABLE5_NOTE1 = (
    "Table 5 Note 1 lets fly ash and GGBS be taken into account with respect to the cement "
    "content AND the water-cement ratio, 'if the suitability is established' and only within "
    "the pozzolana and slag limits of IS 1489 (Part 1) and IS 455. With no suitability "
    "evidence recorded the gate counts NO addition (see counted_additions). "
    "FLY ASH: IS 1489 (Part 1) as amended (Amendment No. 3, July 2000) caps the fly ash "
    "constituent at 35 percent; the gate counts added fly ash only up to that share, and "
    "for PPC it first deducts the fly ash already inside the cement (see countable_fly_ash). "
    "GGBS: IS 455:2015 cl 5 caps the granulated slag constituent at 70 percent; the gate "
    "counts added GGBS only up to that share of the Portland part (see countable_ggbs). "
    "Using fly ash AND GGBS together, or any addition to a blended cement, is an 'other "
    "combination' under IS 456 cl 5.1 and needs suitability data (see "
    "scm_combination_check)."
)


def table5_lookup(exposure: Exposure, use: UseClass, msa_mm: int,
                  *, allow_ocr: bool = False) -> dict:
    """IS 456 Table 5 + Table 6. Refuses OCR-reconstructed cells unless allowed."""
    exp_k, use_k = _v(exposure), _v(use)
    is_cl_6_1_3 = use_k == "cl_6_1_3"
    # [IS] cl 6.1.3 — Table 5's minimum GRADE does not bind for lean/simple/temporary
    #      work. The cement and w/c limits are not disapplied by cl 6.1.3; only the grade is.
    use_for_limits = "pcc" if is_cl_6_1_3 else use_k

    try:
        cem, wc, grade = IS456_TABLE5[exp_k][use_for_limits]
    except KeyError as e:
        raise MissingTableRow(
            f"IS 456 Table 5 has no row for exposure={exp_k!r} use={use_for_limits!r}. "
            f"Printed exposures: {sorted(IS456_TABLE5)}; uses: ['pcc', 'rcc'] "
            f"(plus 'cl_6_1_3', which takes the plain-concrete limits)."
        ) from e

    if msa_mm not in IS456_TABLE6_CEMENT_ADJUST:
        raise MissingTableRow(
            f"IS 456 Table 6 prints no adjustment for msa {msa_mm} mm "
            f"(printed rows: {sorted(IS456_TABLE6_CEMENT_ADJUST)})"
        )

    for value, conf in (cem, wc, grade):
        if _v(conf) == "ocr_reconstructed" and not allow_ocr:
            raise OcrUnconfirmed(
                f"IS 456 Table 5 cell for {exp_k}/{use_for_limits} "
                f"(value {value!r}) was reconstructed from a damaged glyph. "
                f"Confirm against a clean print, or pass allow_ocr=True."
            )

    return {
        "min_cement_kg_m3": cem[0] + IS456_TABLE6_CEMENT_ADJUST[msa_mm],
        "max_free_wc":      wc[0],
        "min_grade":        None if is_cl_6_1_3 else grade[0],
        "min_grade_disapplied_by": "IS 456 cl 6.1.3" if is_cl_6_1_3 else None,
        "caveats":          (CAVEAT_TABLE5_NOTE1,),
    }


"""IS 456 : 2000 as amended. cl 15.2.2, 15.3, 15.4, 16.1, 16.3, Table 8, Table 11,
cl 7.1, cl 9.3, Table 9, cl 10.2.2, cl 5.2.1.2 (Amd 2)."""
import math

# ------------------------------------------------------------ cl 15.2.2
# [IS] "The minimum frequency of sampling of concrete of each grade SHALL be ..."
#      (upper bound of the quantity band m3, number of samples). Above 50 m3:
#      "4 plus one additional sample for each additional 50 m3 or part thereof".
IS456_CL_15_2_2_SAMPLES = ((5, 1), (15, 2), (30, 3), (50, 4))
IS456_CL_15_2_2_ABOVE_50_EVERY_M3 = 50
# [IS] NOTE -- at least one sample from each shift. For a continuous production unit
#      such as an RMC plant, frequency MAY be agreed mutually (see IS 4926 cl 6.3.2).


def min_samples_is456(quantity_m3: float, shifts: int = 1) -> dict:
    """IS 456 cl 15.2.2 minimum number of samples for one grade."""
    if quantity_m3 <= 0:
        raise ValueError("quantity_m3 must be positive")
    # [EI] The table prints integer bands (1-5, 6-15 ...). A non-integer quantity in a
    #      gap (e.g. 5.4 m3) is put in the HIGHER band -- the conservative reading.
    n = None
    for upper, k in IS456_CL_15_2_2_SAMPLES:
        if quantity_m3 <= upper:
            n = k
            break
    if n is None:
        n = 4 + math.ceil((quantity_m3 - 50) / IS456_CL_15_2_2_ABOVE_50_EVERY_M3)
    return {"samples": max(n, shifts), "by_quantity": n, "shift_floor": shifts,
            "source": "IS 456 cl 15.2.2 (+ NOTE: at least one per shift)"}


# ------------------------------------------------------------ cl 15.3 / 15.4
# [IS] cl 15.3 (Amd 1: 'specimens' for 'samples'): three test specimens per sample.
IS456_CL_15_3_SPECIMENS_PER_SAMPLE = 3
# [IS] cl 15.4: sample result = average of three specimens. "The individual variation
#      should not be more than +/-15 percent of the average. If more, the test results
#      of the sample are invalid."
IS456_CL_15_4_MAX_INDIVIDUAL_VARIATION_PCT = 15.0


def sample_test_result(specimens_mpa: list) -> dict:
    """IS 456 cl 15.3 + cl 15.4. One SAMPLE result from its three specimens."""
    if len(specimens_mpa) != IS456_CL_15_3_SPECIMENS_PER_SAMPLE:
        raise ValueError(f"IS 456 cl 15.3: a sample has "
                         f"{IS456_CL_15_3_SPECIMENS_PER_SAMPLE} specimens; got "
                         f"{len(specimens_mpa)}")
    avg = sum(specimens_mpa) / len(specimens_mpa)
    dev = [abs(x - avg) / avg * 100.0 for x in specimens_mpa]
    # 1e-9 absorbs float noise so that EXACTLY 15 percent is valid ("not more than").
    valid = max(dev) <= IS456_CL_15_4_MAX_INDIVIDUAL_VARIATION_PCT + 1e-9
    return {"result_mpa": avg if valid else None, "average_mpa": avg, "valid": valid,
            "max_deviation_pct": max(dev), "source": "IS 456 cl 15.4"}


# ------------------------------------------------------------ Table 8
# [IS] Table 8 (cl 9.2.4.2 and Table 11) -- assumed standard deviation, N/mm2.
#      Printed rows stop at M50. NOT the same table as IS 10262 Table 2 (which runs
#      to M80): IS 456 Table 11 NOTE refers to THIS table.
IS456_TABLE8_STDDEV = {10: 3.5, 15: 3.5, 20: 4.0, 25: 4.0,
                       30: 5.0, 35: 5.0, 40: 5.0, 45: 5.0, 50: 5.0}
# [IS] Table 8 NOTE 2 -- where site control is fair, increase by 1 N/mm2.
IS456_TABLE8_FAIR_CONTROL_ADD = 1.0

# ------------------------------------------------------------ Table 11 (as amended)
# [IS] col 2 -- mean of 4 NON-OVERLAPPING consecutive results >=
#      max(fck + 0.825 x established S rounded to nearest 0.5, fck + margin).
# [IS] col 3 (Amd 1) -- any individual result >= fck - margin.
#      Margin: M15 -> 3 N/mm2; M20 or above -> 4 N/mm2. Table 11 prints NO M10 row.
IS456_TABLE11_K = 0.825
IS456_TABLE11_MARGIN = {"M15": 3.0, "M20_or_above": 4.0}
IS456_TABLE11_GROUP = 4
# [IS] cl 16.3 -- where the mean rate of sampling is not specified, four consecutive
#      results represent at most 60 m3.
IS456_CL_16_3_MAX_QUANTITY_M3 = 60.0


def _round_half(x: float) -> float:
    """'rounded off to nearest 0.5 N/mm2'. [EI] ties round UP (the code gives no rule)."""
    return math.floor(x * 2.0 + 0.5) / 2.0


def table11_limits(grade: str, *, established_s: Optional[float] = None,
                   site_control: str = "good") -> dict:
    """IS 456 Table 11 as amended by Amendment No. 1."""
    fck = grade_to_fck(grade)
    if fck == 15:
        margin, row = IS456_TABLE11_MARGIN["M15"], "M15"
    elif fck >= 20:
        margin, row = IS456_TABLE11_MARGIN["M20_or_above"], "M20 or above"
    else:
        raise MissingTableRow(f"IS 456 Table 11 prints rows for M15 and 'M20 or above' "
                              f"only; no row for {grade}.")
    if established_s is not None:
        s, s_basis = established_s, "established"
    else:
        # [IS] Table 11 NOTE -- absent an established S, Table 8 values may be assumed.
        if int(fck) not in IS456_TABLE8_STDDEV:
            raise MissingTableRow(
                f"No established S given and IS 456 Table 8 stops at M50; {grade} has no "
                f"assumed S there. Supply an established standard deviation.")
        s = IS456_TABLE8_STDDEV[int(fck)]
        if site_control == "fair":
            s += IS456_TABLE8_FAIR_CONTROL_ADD
        elif site_control != "good":
            raise ValueError("site_control must be 'good' or 'fair'")
        s_basis = f"assumed, IS 456 Table 8, {site_control} control"
    by_s = fck + _round_half(IS456_TABLE11_K * s)
    return {"row": row, "S": s, "S_basis": s_basis,
            "mean_of_4_min": max(by_s, fck + margin),
            "individual_min": fck - margin,
            "source": "IS 456 Table 11 (as amended, Amd 1)"}


def acceptance_is456(sample_results_mpa: list, grade: str, *,
                     established_s: Optional[float] = None,
                     site_control: str = "good") -> dict:
    """IS 456 cl 16.1 as amended: groups of four NON-OVERLAPPING consecutive results.

    Input is SAMPLE results (each the valid average of three specimens, cl 15.4), in
    the order the samples were taken -- not specimen strengths.
    """
    lim = table11_limits(grade, established_s=established_s, site_control=site_control)
    r = [float(x) for x in sample_results_mpa]
    n_groups = len(r) // IS456_TABLE11_GROUP
    groups = []
    for i in range(n_groups):
        g = r[i * IS456_TABLE11_GROUP:(i + 1) * IS456_TABLE11_GROUP]
        m = sum(g) / len(g)
        groups.append({"results": g, "mean": m, "ok": m >= lim["mean_of_4_min"]})
    leftover = r[n_groups * IS456_TABLE11_GROUP:]
    indiv_bad = [x for x in r if x < lim["individual_min"]]
    if n_groups == 0:
        mean_verdict = "not_assessable"          # fewer than 4 results
    else:
        mean_verdict = "pass" if all(g["ok"] for g in groups) else "fail"
    individual_verdict = "pass" if not indiv_bad else "fail"
    return {
        "limits": lim, "groups": groups,
        "leftover_not_in_a_group": leftover,
        "mean_criterion": mean_verdict,             # cl 16.1 (a)
        "individual_criterion": individual_verdict, # cl 16.1 (b)
        "individual_failures": indiv_bad,
        "complies": mean_verdict == "pass" and individual_verdict == "pass",
        "note": ("cl 16.3: individual criterion puts only the sampled batch at risk. "
                 "cl 16.4: non-compliance -> investigate structural adequacy (cl 17)."),
    }


# ------------------------------------------------------------ cl 7.1 (Amd 1 table)
# [IS] Amendment No. 1 replaced the informal table under cl 7.1. It prints DEGREE of
#      workability and SLUMP ranges by placing condition. It is GUIDANCE for choosing
#      a target slump -- it is not an acceptance criterion.
IS456_CL_7_1_WORKABILITY = {
    # key: (placing conditions as printed, degree, slump range mm or clause reference)
    "blinding_shallow_pavers": ("Blinding concrete; Shallow sections; Pavements using pavers",
                                "very low", "see 7.1.1"),
    "mass_light_rc_floors":    ("Mass concrete; Lightly reinforced sections in slabs, beams, "
                                "walls, columns; Floors; Hand placed pavements; Canal lining; "
                                "Strip footings", "low", (25, 75)),
    "heavily_reinforced":      ("Heavily reinforced sections in slabs, beams, walls, columns",
                                "medium", (50, 100)),
    "slipform_pumped":         ("Slipform work; Pumped concrete", "medium", (75, 100)),
    "trench_fill_piling":      ("Trench fill; In-situ piling", "high", (100, 150)),
    "tremie":                  ("Tremie concrete", "very high", "see 7.1.2"),
}
# [IS] cl 7.1.1 -- 'very low': compacting factor more appropriate than slump; a CF of
#      0.75 to 0.80 "is suggested".
IS456_CL_7_1_1_CF_SUGGESTED = (0.75, 0.80)
# [IS] cl 7.1.2 -- 'very high': measure by flow (see IS 9103). No flow value printed.


def workability_guidance(placing: str) -> dict:
    """IS 456 cl 7.1 (Amd 1). GUIDANCE ONLY -- never a hard constraint."""
    if placing not in IS456_CL_7_1_WORKABILITY:
        raise MissingTableRow(f"IS 456 cl 7.1 table has no placing key {placing!r}. "
                              f"Keys: {sorted(IS456_CL_7_1_WORKABILITY)}")
    text, degree, rng = IS456_CL_7_1_WORKABILITY[placing]
    out = {"placing": text, "degree": degree, "status": "guidance",
           "source": "IS 456 cl 7.1 (table as substituted by Amd 1)"}
    if rng == "see 7.1.1":
        out.update(measure="compacting factor", suggested=IS456_CL_7_1_1_CF_SUGGESTED,
                   clause="IS 456 cl 7.1.1")
    elif rng == "see 7.1.2":
        out.update(measure="flow (IS 9103)", suggested=None, clause="IS 456 cl 7.1.2")
    else:
        out.update(measure="slump mm", suggested=rng)
    return out


# ------------------------------------------------------------ cl 9.3 + Table 9
# [IS] cl 9.3 -- nominal mix may be used for M20 or LOWER. Per 50 kg cement:
#      total dry aggregate by mass MAX (kg), water MAX (litres).
IS456_TABLE9_NOMINAL = {"M5": (800, 60), "M7.5": (625, 45), "M10": (480, 34),
                        "M15": (330, 32), "M20": (250, 30)}
# [IS] Table 9 col 3 -- FA:CA by mass "generally 1:2 but subject to an upper limit of
#      1:1.5 and a lower limit of 1:2.5".
IS456_TABLE9_FA_CA = {"general": 2.0, "upper_limit": 1.5, "lower_limit": 2.5}
# [IS] Table 9 NOTE example -- Zone II sand: 1:1.5, 1:2, 1:2.5 for msa 10, 20, 40 mm.
IS456_TABLE9_ZONE_II_EXAMPLE = {10: 1.5, 20: 2.0, 40: 2.5}
# [IS] cl 9.3.1 -- if water must be increased, cement SHALL be increased
#      proportionately so the specified w/c is not exceeded.


def nominal_mix(grade: str) -> dict:
    """IS 456 cl 9.3 + Table 9. Domain A route, and optional for M10-M20."""
    g = str(grade).upper().replace(" ", "")
    if g not in IS456_TABLE9_NOMINAL:
        raise MissingTableRow(f"IS 456 Table 9 prints nominal mixes for "
                              f"{list(IS456_TABLE9_NOMINAL)} only (cl 9.3: M20 or lower); "
                              f"got {grade}.")
    agg, water = IS456_TABLE9_NOMINAL[g]
    return {"aggregate_kg_per_50kg_cement_max": agg, "water_l_per_50kg_cement_max": water,
            "implied_max_wc": water / 50.0, "fa_ca": IS456_TABLE9_FA_CA,
            "label": "NOMINAL MIX -- IS 456 Table 9, not a design mix",
            "source": "IS 456 cl 9.3, Table 9"}


# ------------------------------------------------------------ cl 10.2.2
# [IS] measuring-equipment accuracy: +/-2 percent of cement; +/-3 percent of
#      aggregate, admixtures and water. (IS 4926 Annex E adds mineral admixtures to
#      the 2 percent class -- see the IS 4926 cell.)
IS456_CL_10_2_2_TOL_PCT = {"cement": 2.0, "aggregate": 3.0, "admixture": 3.0, "water": 3.0}

# ------------------------------------------------------------ cl 5.2.1 (Amd 2)
# [IS] cl 5.2.1.1 -- fly ash conforming to IS 3812 (Part 1) ('Grade I' removed).
# [IS] cl 5.2.1.2 -- silica fume conforming to IS 15388. NOTE: "usually used in
#      proportion of 5 to 10 percent of the cement content". GUIDANCE (NOTE, 'usually').
IS456_CL_5_2_1_2_SILICA_FUME_USUAL_PCT = (5.0, 10.0)


"""IS 456 : 2000 cl 8.2.2.3, 8.2.2.4 + Table 4, 8.2.5.2 + Table 7, 8.2.5.3, 8.2.5.4, 8.2.8."""

# ------------------------------------------------------------ Table 4 (cl 8.2.2.4, 9.1.2)
# [IS] Sulphate class boundaries, SO3. col 3: total SO3 in soil, percent; col 4: SO3 in
#      2:1 water:soil extract, g/l; col 5: SO3 in ground water, g/l.
#      Class 1 is printed 'Traces (< 0.2)', 'Less than 1.0', 'Less than 0.3';
#      class 5 is printed 'More than 2.0 / 5.0 / 5.0'.
IS456_TABLE4_CLASS_LOWER = {          # lower bound of each class, per measurement
    "soil_total_pct":   {1: 0.0, 2: 0.2, 3: 0.5, 4: 1.0, 5: 2.0},
    "soil_extract_g_l": {1: 0.0, 2: 1.0, 3: 1.9, 4: 3.1, 5: 5.0},
    "groundwater_g_l":  {1: 0.0, 2: 0.3, 3: 1.2, 4: 2.5, 5: 5.0},
}

# [IS] Table 4 cols 6-8, 20 mm msa: cement type -> (min cement kg/m3, max free w/c).
#      OPC = ordinary Portland; PSC = Portland slag; PPC = Portland pozzolana;
#      SSC = supersulphated; SRC = sulphate resisting Portland.
#      A cement type absent from a class row is NOT PRINTED for that class.
IS456_TABLE4 = {
    1: {"OPC": (280, 0.55), "PSC": (280, 0.55), "PPC": (280, 0.55)},
    2: {"OPC": (330, 0.50), "PSC": (330, 0.50), "PPC": (330, 0.50),
        "SSC": (310, 0.50), "SRC": (310, 0.50)},
    3: {"SSC": (330, 0.50), "SRC": (330, 0.50), "PPC": (350, 0.45), "PSC": (350, 0.45)},
    4: {"SSC": (370, 0.45), "SRC": (370, 0.45)},
    5: {"SRC": (400, 0.40), "SSC": (400, 0.40)},     # 'with protective coatings'
}
IS456_TABLE4_MSA_MM = 20
# [IS] Note 1: cement content irrespective of grade of cement. Note 2: supersulphated
#      cement generally restricted above 40 degC. Note 4: col 6 [sic, the cement column]
#      values are 'the minimum recommended'; near the upper SO3 limit of a class, higher
#      cement is advised. Class 5 is printed 'with protective coatings'.


def sulphate_class(*, soil_total_pct: Optional[float] = None,
                   soil_extract_g_l: Optional[float] = None,
                   groundwater_g_l: Optional[float] = None) -> dict:
    """IS 456 Table 4 cols 3-5 -> class 1..5.

    [EI] A value exactly on a printed boundary ('0.2 to 0.5' after '< 0.2') goes to the
         more severe class. With more than one measurement, the most severe class governs.
    """
    given = {"soil_total_pct": soil_total_pct, "soil_extract_g_l": soil_extract_g_l,
             "groundwater_g_l": groundwater_g_l}
    given = {k: v for k, v in given.items() if v is not None}
    if not given:
        raise MissingTableRow("IS 456 Table 4: supply at least one SO3 measurement.")
    per = {}
    for k, v in given.items():
        per[k] = max(c for c, lo in IS456_TABLE4_CLASS_LOWER[k].items() if v >= lo)
    return {"class": max(per.values()), "per_measurement": per,
            "source": "IS 456 Table 4 cols 3-5", "boundary_rule": "[EI] boundary -> severer"}


def table4_lookup(cls: int, cement_type: str, msa_mm: int = 20) -> dict:
    """IS 456 Table 4 cols 6-8. Refuses a cement type the row does not print."""
    if msa_mm != IS456_TABLE4_MSA_MM:
        raise MissingTableRow(f"IS 456 Table 4 is printed for {IS456_TABLE4_MSA_MM} mm msa "
                              f"only; no adjustment rule is given for {msa_mm} mm.")
    row = IS456_TABLE4.get(int(cls))
    if row is None:
        raise MissingTableRow(f"IS 456 Table 4 has classes 1-5; got {cls}.")
    ct = str(cement_type).upper()
    if ct not in row:
        raise MissingTableRow(f"IS 456 Table 4 class {cls} prints no row for {ct}; "
                              f"permitted: {sorted(row)}.")
    mn, wc = row[ct]
    return {"min_cement_kg_m3": mn, "max_free_wc": wc, "class": int(cls),
            "protective_coating_required": int(cls) == 5,
            "source": "IS 456 Table 4 (cl 8.2.2.4)"}


# ------------------------------------------------------------ Table 7 (cl 8.2.5.2)
# [IS] "The total amount of chloride content (as Cl) in the concrete at the time of
#      placing shall be as given in Table 7." Max total acid soluble chloride, kg/m3.
IS456_TABLE7_CHLORIDE_MAX_KG_M3 = {
    "prestressed_or_steam_cured": 0.4,   # containing metal and steam cured / prestressed
    "embedded_metal": 0.6,               # RCC, or PCC containing embedded metal
    "no_embedded_metal": 3.0,            # no embedded metal or chloride-sensitive material
}


def total_chloride_kg_m3(masses_kg_m3: dict, chloride_pct_by_mass: dict) -> dict:
    """IS 456 cl 8.2.5.2: 'calculated from the mix proportions and the measured chloride
    contents of each of the constituents'. Every constituent with mass > 0 needs a value."""
    missing = [k for k, m in masses_kg_m3.items() if m > 0 and k not in chloride_pct_by_mass]
    total = sum(m * chloride_pct_by_mass.get(k, 0.0) / 100.0 for k, m in masses_kg_m3.items())
    return {"chloride_kg_m3": None if missing else total, "missing": missing,
            "source": "IS 456 cl 8.2.5.2"}


# ------------------------------------------------------------ cl 8.2.5.3
# [IS] "the total water-soluble sulphate content of the concrete mix, expressed as SO3,
#      should not exceed 4 percent by mass of the cement in the mix ... The 4 percent limit
#      does not apply to concrete made with supersulphated cement complying with IS 6909."
IS456_CL_8_2_5_3_SO3_MAX_PCT_OF_CEMENT = 4.0


def so3_pct_of_cement(masses_kg_m3: dict, so3_pct_by_mass: dict, cement_kg_m3: float) -> dict:
    """[EI] 'the cement in the mix' = the cement mass only (PPC counted whole); fly ash,
    GGBS and other additions are not cement. Stricter than counting the additions."""
    missing = [k for k, m in masses_kg_m3.items() if m > 0 and k not in so3_pct_by_mass]
    so3 = sum(m * so3_pct_by_mass.get(k, 0.0) / 100.0 for k, m in masses_kg_m3.items())
    return {"so3_pct_of_cement": None if missing else so3 / cement_kg_m3 * 100.0,
            "missing": missing, "source": "IS 456 cl 8.2.5.3"}


# ------------------------------------------------------------ cl 8.2.8
# [IS] "Concrete in sea-water or exposed directly along the sea-coast shall be at least
#      M 20 Grade in the case of plain concrete and M 30 in case of reinforced concrete."
IS456_CL_8_2_8_SEA_WATER_MIN_GRADE = {"pcc": "M20", "rcc": "M30"}

# ------------------------------------------------------------ cl 8.2.2.3
# [IS] Freezing and thawing under wet conditions, concrete below M 50: mean total air
#      content at delivery 'should be' 5 +/- 1 percent (20 mm) and 4 +/- 1 (40 mm).
#      Verb 'should' -> GUIDANCE.
IS456_CL_8_2_2_3_AIR_PCT = {20: (5.0, 1.0), 40: (4.0, 1.0)}
IS456_CL_8_2_2_3_BELOW_GRADE = 50


def freeze_thaw_air_guidance(grade: str, msa_mm: int) -> Optional[dict]:
    if grade_to_fck(grade) >= IS456_CL_8_2_2_3_BELOW_GRADE:
        return None
    if msa_mm not in IS456_CL_8_2_2_3_AIR_PCT:
        raise MissingTableRow(f"IS 456 cl 8.2.2.3 prints air content for "
                              f"{sorted(IS456_CL_8_2_2_3_AIR_PCT)} mm only.")
    mid, tol = IS456_CL_8_2_2_3_AIR_PCT[msa_mm]
    return {"air_pct": (mid - tol, mid + tol), "status": "guidance",
            "source": "IS 456 cl 8.2.2.3"}


# ------------------------------------------------------------ cl 8.2.5.4
# [IS] Damage from alkali-aggregate reaction needs all three together: high moisture,
#      high-alkali cement (or another alkali source), and a reactive aggregate. Where
#      service records are well established, no further precaution 'should be necessary'.
#      Precautions (one or more): a) non-reactive aggregate; b) low alkali OPC, total
#      alkali not more than 0.6 percent Na2O equivalent, with further advantage from fly
#      ash >= 20 percent or slag >= 50 percent as part replacement; c) reduce saturation;
#      d) limit cement content. GUIDANCE -- options, not a single binding limit.
IS456_CL_8_2_5_4_LOW_ALKALI_OPC_MAX_NA2O_EQ_PCT = 0.6
IS456_CL_8_2_5_4_FLY_ASH_MIN_PCT = 20.0
IS456_CL_8_2_5_4_SLAG_MIN_PCT = 50.0


"""IS 10262:2019 SECTION 2 — ordinary and standard grades, M10 to M60 (cl 5)."""

# Table 1 (cl 4.2) — value of X. [IS] Row iv is printed "M65 and above", open-ended.
IS10262_TABLE1_X = {10: 5.0, 15: 5.0,
                    20: 5.5, 25: 5.5,
                    30: 6.5, 35: 6.5, 40: 6.5, 45: 6.5, 50: 6.5, 55: 6.5, 60: 6.5}
IS10262_TABLE1_X_M65_AND_ABOVE = 8.0

# Table 2 (cl 4.2.1.3) — assumed standard deviation, N/mm2. [IS]
# Row iv ENUMERATES M65, M70, M75, M80 only. There is NO row above M80.
IS10262_TABLE2_STDDEV = {10: 3.5, 15: 3.5,
                         20: 4.0, 25: 4.0,
                         30: 5.0, 35: 5.0, 40: 5.0, 45: 5.0, 50: 5.0, 55: 5.0, 60: 5.0,
                         65: 6.0, 70: 6.0, 75: 6.0, 80: 6.0}

# [IS] Table 2 Note 1 — tabulated values assume GOOD site control. Where control is
#      fair, the values "shall be increased by 1 N/mm2".
IS10262_TABLE2_FAIR_CONTROL_ADD = 1.0

# [IS] cl 4.2.1.1 — a calculated (established) standard deviation requires NOT LESS
#      THAN 30 test results, recalculated after every change of mix proportioning.
IS10262_CL_4_2_1_1_MIN_RESULTS = 30
# [IS] cl 4.2.1.2.2 -- two groups (mixes) of consecutive results of the same grade may be
#      pooled: S = sqrt(((n1-1)s1^2 + (n2-1)s2^2) / (n1 + n2 - 2)), "where both n1 and n2
#      shall not be less than 10, and n1 + n2 shall not be less than 30".
IS10262_CL_4_2_1_2_2_MIN_PER_GROUP = 10
# [IS] cl 4.2.1.1 (b): after significant changes (materials source, mix proportioning,
#      equipment or technical control) S "shall be separately calculated for such batches".
# [IS] cl 4.2.1.1 (c): S "shall be checked every month subject to minimum 30 test results
#      to ensure that it is less than the value considered in mix design. If higher,
#      necessary modification shall be done in the mix."

# Table 3 (cl 5.2) — entrapped air, percent of concrete volume. [IS]
IS10262_TABLE3_AIR = {10: 1.5, 20: 1.0, 40: 0.8}

# Table 4 (cl 5.3) — water content kg/m3 at 50 mm slump, angular CA, SSD. [IS]
# NOTE: these are 208 / 186 / 165. The values 200 / 195 / 186 belong to TABLE 7,
# which is Section 3. Do not confuse them.
IS10262_TABLE4_WATER = {10: 208, 20: 186, 40: 165}

# [IS] cl 5.3 adjustments to the Table 4 value.
IS10262_CL_5_3_SHAPE_ADJUST_KG = {      # subtract, to produce the same workability
    "angular":                      0,
    "sub_angular":                -10,
    "gravel_some_crushed":        -15,
    "rounded_gravel":             -20,
}
IS10262_CL_5_3_SLUMP_PCT_PER_25MM = 3.0   # +/- 3 percent per 25 mm from 50 mm

# Table 5 (cl 5.5) — volume of CA per unit volume of total aggregate, at w/c 0.50. [IS]
# The printed column order is Zone IV, III, II, I -- RIGHT TO LEFT. Keyed by zone
# name here so the ordering cannot be misread.
IS10262_TABLE5_CA_VOLUME = {
    10: {"IV": 0.54, "III": 0.52, "II": 0.50, "I": 0.48},
    20: {"IV": 0.66, "III": 0.64, "II": 0.62, "I": 0.60},
    40: {"IV": 0.73, "III": 0.72, "II": 0.71, "I": 0.69},
}
# [IS] cl 5.5.1 — +0.01 per 0.05 DECREASE in w/c; -0.01 per 0.05 INCREASE.
IS10262_CL_5_5_1_CA_PER_005_WC = 0.01
# [IS] cl 5.5.2 — pumpable or congested reinforcement: reduce CA volume by up to 10 percent.
IS10262_CL_5_5_2_PUMPABLE_MAX_REDUCTION = 0.10
# [IS] Table 5 Note 3 — crushed or mixed sand normally needs LESS fine aggregate, so
#      the coarse aggregate volume "shall be suitably increased". No number is given.
#      Any numeric M-sand correction is therefore [PC], not [IS].
# [IS] Table 5 Note 4 — Zone IV "shall not be used in reinforced concrete unless tests
#      have been made to ascertain the suitability of proposed mix proportions".


"""IS 10262:2019 SECTION 3 — high strength concrete, M65 and above (cl 6)."""

# Table 6 (cl 6.2.3) — entrapped air. Different msa set from Table 3. [IS]
IS10262_TABLE6_AIR_HS = {10.0: 1.0, 12.5: 0.8, 20.0: 0.5}

# Table 7 (cl 6.2.4) — MAXIMUM water content kg/m3 at 50 mm slump. [IS]
IS10262_TABLE7_WATER_HS = {10.0: 200, 12.5: 195, 20.0: 186}
# [IS] cl 6.2.4 — +/- 3 percent per 25 mm slump, same as cl 5.3.

# Table 8 (cl 6.2.5) — recommended w/cm for high strength concrete made with HRWRA. [IS]
# Rows are TARGET compressive strength at 28 days, not characteristic strength.
IS10262_TABLE8_WCM = {
    #  target  10.0mm  12.5mm  20.0mm
    70:  {10.0: 0.36, 12.5: 0.35, 20.0: 0.33},
    75:  {10.0: 0.34, 12.5: 0.33, 20.0: 0.31},
    80:  {10.0: 0.32, 12.5: 0.31, 20.0: 0.29},
    85:  {10.0: 0.30, 12.5: 0.29, 20.0: 0.27},
    90:  {10.0: 0.28, 12.5: 0.27, 20.0: 0.26},
    100: {10.0: 0.26, 12.5: 0.25, 20.0: 0.24},
}
# [IS] Table 8 NOTE — the recommended w/cm are for 28-day cement strength 53 MPa and
#      above; for cement of other strength values, suitable adjustments may be made
#      by REDUCING the w/cm.

# Table 9 (cl 6.2.6) — recommended mineral admixture dosages,
# percent by mass of TOTAL CEMENTITIOUS materials. [IS]
IS10262_TABLE9_SCM_DOSAGE_PCT = {
    "fly_ash":      (15, 30),
    "ggbs":         (25, 50),
    "metakaoline":  (5, 15),
    "silica_fume":  (5, 10),
}

# Table 10 (cl 6.2.7) — CA volume per unit volume of total aggregate, at w/cm 0.30. [IS]
# There is NO Zone IV column in this table.
IS10262_TABLE10_CA_VOLUME_HS = {
    10.0: {"III": 0.56, "II": 0.54, "I": 0.52},
    12.5: {"III": 0.58, "II": 0.56, "I": 0.54},
    20.0: {"III": 0.68, "II": 0.66, "I": 0.64},
}
# [IS] cl 6.2.7 — pumpable: reduce by up to 5 percent (NOT the 10 percent of cl 5.5.2).
IS10262_CL_6_2_7_PUMPABLE_MAX_REDUCTION = 0.05

# [IS] cl 6.2.2 — msa generally restricted to 20 mm; for M80 and above,
#      10.0 to 12.5 mm may be preferable.
# [IS] cl 6.2.6 — if cement content (not including mineral admixtures) exceeds the
#      IS 456 maximum, special consideration in design is required.


"""IS 10262 : 2019 cl 2 (References), cl 3 (Terminology), cl 5.1 NOTE, cl 5.1.2.

These are the standards IS 10262 itself says form part of it. Each is mapped to what
is actually in the IS_codes folder, so a missing or wrong edition is visible here."""

# [IS] IS 10262 cl 2, as printed: IS No. -> edition cited.  status is OUR library state.
IS10262_CL2_REFERENCES = {
    "IS 269":           ("2015", "OPC (sixth revision)",
                         "encoded from IS_269_2015_reff2020.pdf (Tables 2 and 3)"),
    "IS 383":           ("2016", "Coarse and fine aggregates", "encoded"),
    "IS 456":           ("2000", "Plain and reinforced concrete", "encoded"),
    "IS 1199 (Part 6)": ("2018", "Tests on fresh self compacting concrete",
                         "in folder, not encoded (SCC out of scope)"),
    "IS 1489 (Part 1)": ("2015", "PPC, fly ash based (third revision)",
                         "encoded from the 1991 Third Revision + Amendments 1-5 [NV: "
                         "whether this equals the '2015' edition cited]"),
    "IS 1489 (Part 2)": ("2015", "PPC, calcined clay based (third revision)",
                         "in folder (1991), not encoded (calcined clay PPC not used)"),
    "IS 2386 (Part 3)": ("1963", "Specific gravity, voids, absorption, bulking",
                         "encoded as a test-method reference for the trial batch sheet"),
    "IS 3812 (Part 1)": ("2013", "Pulverized fuel ash", "encoded"),
    "IS 9103":          ("1999", "Concrete admixtures", "encoded"),
    "IS 15388":         ("2003", "Silica fume", "in folder, not encoded (not used)"),
    "IS 16714":         ("2018", "GGBS", "encoded"),
}

# [IS] cl 3.1 -- w/c = mass of mixing water / mass of cement, at SSD aggregate.
# [IS] cl 3.2 -- w/cm = mass of mixing water / (cement + fly ash or other cementitious
#      materials), at SSD aggregate.
# [IS] cl 5.1.2 -- "Where supplementary cementitious materials are used ... the w/cm
#      shall be calculated in accordance with Table 5 of IS 456" -- i.e. with the
#      Table 5 Note 1 limit on how much addition may be counted.
# [IS] cl 5.1 NOTE -- where w/c is at the upper durability limit, the water contributed
#      by admixtures shall also be considered.
# [IS] cl 5.1.1 NOTE -- "In case of water cement ratios on the upper limits of
#      durability clause, it is required that the water content contributed by the
#      admixtures, also be considered in the calculations and the final water cement
#      ratio shall be fixed accordingly."
# [EI] "On the upper limits" is not quantified. The gate therefore ALWAYS adds the
#      admixture's water to the free water for the IS 456 Table 5 w/c check. That is
#      never less strict than the clause.
# [IS] Annex A (PPC example) takes w/c on the PPC mass: 148 / 0.36 = 412 kg/m3 PPC,
#      checked against the Table 5 minimum of 320. So PPC counts whole as 'cement'.


def references_status() -> list:
    return [(k, v[0], v[2]) for k, v in IS10262_CL2_REFERENCES.items()]


"""Domain routing. Runs before anything else. M65 cannot reach the Section 2 chain."""

def grade_to_fck(grade: str) -> float:
    return float(str(grade).upper().lstrip("M"))


def route_domain(grade: str) -> Domain:
    """[IS] IS 10262 cl 1.2 / cl 6; IS 456 Table 9 and cl 9.1.1."""
    fck = grade_to_fck(grade)
    if fck < 10:
        # [IS] IS 10262 Table 1 and Table 2 both START at M10. M5 and M7.5 have no
        #      X and no assumed S. They appear only in IS 456 Table 9 as NOMINAL mixes.
        return Domain.NOMINAL
    if fck <= 60:
        return Domain.ORDINARY
    return Domain.HIGH_STRENGTH


def x_factor(grade: str) -> float:
    """IS 10262 Table 1 (cl 4.2)."""
    fck = int(grade_to_fck(grade))
    if fck in IS10262_TABLE1_X:
        return IS10262_TABLE1_X[fck]
    if fck >= 65:
        return IS10262_TABLE1_X_M65_AND_ABOVE      # row iv: "M65 and above"
    raise MissingTableRow(
        f"IS 10262 Table 1 prints no value of X for {grade}. The table starts at M10."
    )


def assumed_standard_deviation(grade: str, site_control: str = "good") -> float:
    """IS 10262 Table 2 (cl 4.2.1.3). Table 2 row iv stops at M80."""
    fck = int(grade_to_fck(grade))
    if fck not in IS10262_TABLE2_STDDEV:
        raise MissingTableRow(
            f"IS 10262 Table 2 prints no assumed standard deviation for {grade}. "
            f"Printed grades: M10-M60, then M65, M70, M75, M80 only."
        )
    s = IS10262_TABLE2_STDDEV[fck]
    if site_control == "fair":
        s += IS10262_TABLE2_FAIR_CONTROL_ADD     # Table 2 Note 1
    elif site_control != "good":
        raise ValueError("site_control must be 'good' or 'fair' (IS 10262 Table 2 Note 1)")
    return s


def target_mean_strength(grade: str, *, established_s: Optional[float] = None,
                         n_results: Optional[int] = None,
                         site_control: str = "good") -> dict:
    """Target mean strength.

    [IS] IS 456 cl 9.2.2  : f'ck = fck + 1.65 S
    [IS] IS 10262 cl 4.2  : f'ck = max(fck + 1.65 S, fck + X)
    [PC] DECLARED CONFLICT. The two clauses differ. IS 10262 is the later, more
         specific mix-proportioning document and its formula is the stricter of the
         two, so the project takes the maximum. This is a PROJECT_CONSTRAINT and is
         recorded as an interpretation, not as a clause.
    """
    fck = grade_to_fck(grade)
    if established_s is not None:
        # [IS] cl 4.2.1.1 — an established S needs not less than 30 results.
        if n_results is None or n_results < IS10262_CL_4_2_1_1_MIN_RESULTS:
            raise UnverifiedRule(
                f"IS 10262 cl 4.2.1.1 requires not less than "
                f"{IS10262_CL_4_2_1_1_MIN_RESULTS} test results for an established "
                f"standard deviation; got n_results={n_results}."
            )
        s, s_basis = established_s, "established (cl 4.2.1.1)"
    else:
        s, s_basis = assumed_standard_deviation(grade, site_control), \
                     f"assumed, Table 2, {site_control} control"

    by_s = fck + IS456_CL_9_2_2_MULTIPLIER * s
    by_x = fck + x_factor(grade)
    return {
        "target_mean": max(by_s, by_x),
        "fck": fck, "S": s, "S_basis": s_basis,
        "fck_plus_1_65S": by_s, "fck_plus_X": by_x,
        "binding": "1.65S" if by_s >= by_x else "X floor",
        "resolution": "[PC] max() per declared IS 456 cl 9.2.2 / IS 10262 cl 4.2 conflict",
    }


def established_standard_deviation(groups: list, grade: str) -> dict:
    """IS 10262 cl 4.2.1.1 + 4.2.1.2. Standard deviation from a plant's own record.

    `groups`: one or two lists of CONSECUTIVE sample results (N/mm2) of THIS grade, each
    result a valid IS 456 cl 15.4 sample (mean of three specimens). Two lists = two mixes of
    the same grade (cl 4.2.1.2.2). More than two groups is not provided for -> refused.
    [IS] cl 4.2.1 : S for each grade is calculated separately -- the caller passes one grade.
    [IS] cl 4.2.1.1 (b): after a significant change in production, the record restarts;
         the caller must pass only batches made after the last change.
    """
    grade_to_fck(grade)                                    # validates the grade string
    g = [[float(x) for x in grp] for grp in groups if len(grp)]
    if len(g) == 0:
        raise UnverifiedRule("IS 10262 cl 4.2.1.1: no test results supplied.")
    if len(g) > 2:
        raise UnverifiedRule("IS 10262 cl 4.2.1.2 defines one group (4.2.1.2.1) or two groups "
                             "(4.2.1.2.2) only; more than two groups is not provided for.")
    def sd1(x):                                            # cl 4.2.1.2.1, divisor n - 1
        m = sum(x) / len(x)
        return (sum((v - m) ** 2 for v in x) / (len(x) - 1)) ** 0.5
    n = [len(x) for x in g]
    if len(g) == 1:
        if n[0] < IS10262_CL_4_2_1_1_MIN_RESULTS:
            raise UnverifiedRule(f"IS 10262 cl 4.2.1.1 (a): not less than "
                                 f"{IS10262_CL_4_2_1_1_MIN_RESULTS} results; got {n[0]}.")
        S, clause = sd1(g[0]), "IS 10262 cl 4.2.1.1 (a) + 4.2.1.2.1"
    else:
        if min(n) < IS10262_CL_4_2_1_2_2_MIN_PER_GROUP or sum(n) < IS10262_CL_4_2_1_1_MIN_RESULTS:
            raise UnverifiedRule(f"IS 10262 cl 4.2.1.2.2: each group >= "
                                 f"{IS10262_CL_4_2_1_2_2_MIN_PER_GROUP} and total >= "
                                 f"{IS10262_CL_4_2_1_1_MIN_RESULTS}; got {n}.")
        s1, s2 = sd1(g[0]), sd1(g[1])
        S = (((n[0] - 1) * s1 ** 2 + (n[1] - 1) * s2 ** 2) / (sum(n) - 2)) ** 0.5
        clause = "IS 10262 cl 4.2.1.2.2 (two groups pooled)"
    return {"S": S, "n_results": sum(n), "groups": n, "grade": grade, "source": clause,
            "caveats": ("cl 4.2.1.1 (b): pass only batches made after the last significant change "
                        "(materials source, mix proportioning, equipment, technical control).",
                        "cl 4.2.1.1 (c): re-check every month on at least 30 results; if S rises "
                        "above the value used in design, the mix must be modified.")}


def standard_deviation_check(recent_results: list, s_used_in_design: float) -> dict:
    """IS 10262 cl 4.2.1.1 (c): monthly check on >= 30 recent results that S is LESS than the
    value considered in mix design; if higher, the mix must be modified."""
    x = [float(v) for v in recent_results]
    if len(x) < IS10262_CL_4_2_1_1_MIN_RESULTS:
        return {"outcome": Outcome.NOT_VERIFIED.value, "S_recent": None,
                "detail": f"cl 4.2.1.1 (c) needs >= {IS10262_CL_4_2_1_1_MIN_RESULTS} results; got {len(x)}"}
    m = sum(x) / len(x)
    s_recent = (sum((v - m) ** 2 for v in x) / (len(x) - 1)) ** 0.5
    ok = s_recent < s_used_in_design
    return {"outcome": (Outcome.PASS if ok else Outcome.FAIL).value, "S_recent": s_recent,
            "detail": (f"S of last {len(x)} results {s_recent:.2f} vs {s_used_in_design:.2f} used in design"
                       + ("" if ok else " -> IS 10262 cl 4.2.1.1 (c): modify the mix")),
            "source": "IS 10262 cl 4.2.1.1 (c)"}


def water_content(grade: str, msa_mm: float, target_slump_mm: float,
                  ca_shape: str = "angular") -> dict:
    """Water content. Section 2 uses Table 4; Section 3 uses Table 7. Never both."""
    domain = route_domain(grade)

    if _v(domain) == "A":
        raise MissingTableRow(
            f"{grade} is domain A (nominal). IS 10262 has no design-mix route below "
            f"M10; use IS 456 Table 9 nominal proportions and label them as such."
        )

    if _v(domain) == "B":
        table, clause, name = IS10262_TABLE4_WATER, "cl 5.3", "Table 4"
        shape_adj = IS10262_CL_5_3_SHAPE_ADJUST_KG[ca_shape]
    else:
        table, clause, name = IS10262_TABLE7_WATER_HS, "cl 6.2.4", "Table 7"
        shape_adj = 0            # [IS] Table 7 is already for angular, well-graded CA

    key = msa_mm if msa_mm in table else (int(msa_mm) if int(msa_mm) in table else None)
    if key is None:
        raise MissingTableRow(
            f"IS 10262 {name} ({clause}) prints no row for msa {msa_mm} mm. "
            f"Printed rows: {sorted(table)}. Do not interpolate."
        )

    base = table[key] + shape_adj
    steps = (target_slump_mm - 50.0) / 25.0
    water = base * (1.0 + IS10262_CL_5_3_SLUMP_PCT_PER_25MM / 100.0 * steps)
    return {"water_kg_m3": water, "base": table[key], "shape_adjust": shape_adj,
            "source": f"IS 10262 {name} ({clause})", "domain": domain.name}


def coarse_aggregate_volume(grade: str, msa_mm: float, sand_zone: str,
                            wc_ratio: float, pumpable: bool = False) -> dict:
    """CA volume fraction. Section 2 = Table 5 @ w/c 0.50; Section 3 = Table 10 @ 0.30."""
    domain = route_domain(grade)
    if _v(domain) == "A":
        raise MissingTableRow(f"{grade} is domain A (nominal); no CA volume table applies.")

    if _v(domain) == "B":
        table, base_wc, name, clause = IS10262_TABLE5_CA_VOLUME, 0.50, "Table 5", "cl 5.5"
        max_red = IS10262_CL_5_5_2_PUMPABLE_MAX_REDUCTION
    else:
        table, base_wc, name, clause = IS10262_TABLE10_CA_VOLUME_HS, 0.30, "Table 10", "cl 6.2.7"
        max_red = IS10262_CL_6_2_7_PUMPABLE_MAX_REDUCTION

    key = msa_mm if msa_mm in table else (int(msa_mm) if int(msa_mm) in table else None)
    if key is None:
        raise MissingTableRow(
            f"IS 10262 {name} ({clause}) prints no row for msa {msa_mm} mm. "
            f"Printed rows: {sorted(table)}."
        )
    if sand_zone not in table[key]:
        raise MissingTableRow(
            f"IS 10262 {name} prints no {sand_zone} column for msa {msa_mm} mm. "
            f"Printed zones: {list(table[key])}."
        )

    vol = table[key][sand_zone]
    # [IS] cl 5.5.1 — +0.01 per 0.05 DECREASE in w/c, -0.01 per 0.05 INCREASE.
    vol += IS10262_CL_5_5_1_CA_PER_005_WC * ((base_wc - wc_ratio) / 0.05)
    applied = 0.0
    if pumpable:
        applied = max_red
        vol *= (1.0 - applied)
    return {"ca_volume_fraction": vol, "table_value": table[key][sand_zone],
            "base_wc": base_wc, "pumpable_reduction": applied,
            "source": f"IS 10262 {name} ({clause})", "domain": domain.name}


def wcm_high_strength(target_mean: float, msa_mm: float) -> dict:
    """IS 10262 Table 8 (cl 6.2.5). Section 3 ONLY. Fig 1 does not apply here."""
    if msa_mm not in IS10262_TABLE8_WCM[70]:
        raise MissingTableRow(
            f"IS 10262 Table 8 prints no column for msa {msa_mm} mm. "
            f"Printed: {sorted(IS10262_TABLE8_WCM[70])}."
        )
    rows = sorted(IS10262_TABLE8_WCM)
    if target_mean > max(rows):
        raise MissingTableRow(
            f"IS 10262 Table 8 stops at target {max(rows)} N/mm2; got {target_mean}."
        )
    # [EI] The standard prints discrete rows and states no interpolation rule.
    #      We take the first row at or above the target, which is the conservative
    #      (lower w/cm) choice and reproduces the standard's own Annex D.
    row = next(r for r in rows if r >= target_mean)
    return {"wcm": IS10262_TABLE8_WCM[row][msa_mm], "row_used": row,
            "rule": "[EI] first printed row >= target; no interpolation"}


"""IS 383 : 2016. Table 2, Table 9, cl 6.3. Read from page images (no text layer)."""

# Table 2 row iii (cl 5.2.1) — materials finer than 75 micron, percent by mass, MAX.
# Test method IS 2386 (Part 1). [IS]
IS383_TABLE2_FINES_75UM_MAX = {
    "fine_uncrushed":     3.00,
    "fine_crushed":      15.00,      # "15.00 (for crushed sand)"
    "fine_mixed":        12.00,      # "12.00 (for mixed sand)"
    "fine_manufactured": 10.00,
    "coarse_uncrushed":   1.00,
    "coarse_crushed":     1.00,
    "coarse_manufactured": 1.00,
}
# [IS] Table 2 Note 1 — sands used for blending in mixed sand shall individually also
#      satisfy Table 2, and the UNCRUSHED sand used for blending shall not have
#      material finer than 75 micron more than 3.00 percent.
IS383_TABLE2_NOTE1_BLEND_UNCRUSHED_MAX = 3.00

# [IS] cl 3.1.2 vs cl 3.1.4 — CRUSHED SAND (3.1.2) is produced by crushing hard stone
#      or natural gravel: a NATURAL source. MANUFACTURED FINE AGGREGATE (3.1.4) is made
#      from OTHER THAN natural sources. Industry "M-sand" spans both; IS 383 does not.
#      Quarry-crushed sand therefore takes the 'fine_crushed' limit (15.00), NOT the
#      'fine_manufactured' limit (10.00), and IS 383 Table 3 does NOT apply to it.

# Table 9 (cl 6.3) — fine aggregate grading, percentage passing, (low, high). [IS]
IS383_TABLE9_FINE_GRADING = {
    "10mm":   {"I": (100, 100), "II": (100, 100), "III": (100, 100), "IV": (100, 100)},
    "4.75mm": {"I": (90, 100),  "II": (90, 100),  "III": (90, 100),  "IV": (95, 100)},
    "2.36mm": {"I": (60, 95),   "II": (75, 100),  "III": (85, 100),  "IV": (95, 100)},
    "1.18mm": {"I": (30, 70),   "II": (55, 90),   "III": (75, 100),  "IV": (90, 100)},
    "600um":  {"I": (15, 34),   "II": (35, 59),   "III": (60, 79),   "IV": (80, 100)},
    "300um":  {"I": (5, 20),    "II": (8, 30),    "III": (12, 40),   "IV": (15, 50)},
    "150um":  {"I": (0, 10),    "II": (0, 10),    "III": (0, 10),    "IV": (0, 15)},
}

# [IS] Table 9 Note 1 — "For crushed stone sands, the permissible limit on 150 micron
#      IS Sieve is increased to 20 percent. This does not affect the 5 percent
#      allowance permitted in 6.3 applying to other sieve sizes."
IS383_TABLE9_NOTE1_CRUSHED_150UM_MAX = 20.0

# [IS] cl 6.3 tolerance. THREE parts, all binding together:
IS383_CL_6_3_SINGLE_SIEVE_TOLERANCE = 5.0     # (a) <= 5 percent on any one sieve
IS383_CL_6_3_CUMULATIVE_TOLERANCE  = 10.0     # (b) cumulative <= 10 percent
IS383_CL_6_3_TOLERANCE_EXCLUDED = {           # (c) tolerance does NOT apply to:
    "sieve":            "600um",
    "zone_I_limit":     "coarse",             # the coarse limit of Grading Zone I
    "zone_IV_limit":    "finer",              # the finer limit of Grading Zone IV
}
# [EI] 600 micron is the only sieve whose zone ranges do not overlap, so it is the
#      sieve that actually assigns the zone. Excluding it from the tolerance is the
#      most consequential part of cl 6.3.

# [IS] Table 9 Note 4 — "It is recommended that fine aggregate conforming to Grading
#      Zone IV SHOULD NOT be used in reinforced concrete UNLESS tests have been made
#      to ascertain the suitability of proposed mix proportions."
# [EI] "recommended ... should not ... unless tests" is an ENGINEERING PREFERENCE with
#      a test-based override, not a hard prohibition. Encoded as relaxable.
IS383_ZONE_IV_IN_RC = Rule(
    "IS 383:2016", "Table 9 Note 4", "Zone IV fine aggregate in reinforced concrete",
    Status.PROJECT_CONSTRAINT,
    caveats=("[EI] Standard says 'recommended ... should not ... unless tests have "
             "been made'. Overridable with recorded test evidence.",),
)


def classify_sand_zone(passing_pct: dict, sand_type: str = "crushed",
                       use: UseClass = UseClass.RCC,
                       zone_iv_tests_done: bool = False) -> dict:
    """IS 383 cl 6.3 + Table 9, with the full three-part tolerance rule."""
    valid = {"crushed", "natural", "mixed", "manufactured"}
    if sand_type not in valid:
        raise ValueError(f"sand_type must be one of {sorted(valid)}")

    results = {}
    for zone in ("I", "II", "III", "IV"):
        breaches, tol_used, cumulative = [], [], 0.0
        for sieve, limits in IS383_TABLE9_FINE_GRADING.items():
            if sieve not in passing_pct:
                continue
            lo, hi = limits[zone]
            # Table 9 Note 1 — crushed stone sand only, 150 micron only.
            if sieve == "150um" and sand_type in ("crushed", "mixed"):
                hi = max(hi, IS383_TABLE9_NOTE1_CRUSHED_150UM_MAX)

            v = passing_pct[sieve]
            if lo <= v <= hi:
                continue

            dev = (lo - v) if v < lo else (v - hi)

            # cl 6.3 (c): tolerance excluded for 600um, and for the coarse limit of
            # Zone I / the finer limit of Zone IV.
            excluded = (
                sieve == IS383_CL_6_3_TOLERANCE_EXCLUDED["sieve"]
                or (zone == "I"  and v < lo)     # coarse limit of Zone I
                or (zone == "IV" and v > hi)     # finer limit of Zone IV
            )
            if excluded or dev > IS383_CL_6_3_SINGLE_SIEVE_TOLERANCE:
                breaches.append(f"{sieve}={v} outside [{lo},{hi}]"
                                + (" (tolerance not applicable, cl 6.3)" if excluded else ""))
                continue
            cumulative += dev
            tol_used.append(f"{sieve} by {dev:.1f}%")

        if cumulative > IS383_CL_6_3_CUMULATIVE_TOLERANCE:
            breaches.append(f"cumulative tolerance {cumulative:.1f}% exceeds "
                            f"{IS383_CL_6_3_CUMULATIVE_TOLERANCE}% (cl 6.3)")
        results[zone] = {"satisfied": not breaches, "breaches": breaches,
                         "tolerance_used": tol_used, "cumulative": cumulative}

    zones = [z for z, r in results.items() if r["satisfied"]]
    warnings = []
    if "IV" in zones and _v(use) == "rcc" and not zone_iv_tests_done:
        warnings.append(
            "Zone IV in reinforced concrete: IS 383 Table 9 Note 4 recommends against "
            "this unless suitability tests have been made. Not a prohibition. "
            "Set zone_iv_tests_done=True with recorded evidence to proceed."
        )
    return {"zones_satisfied": zones, "detail": results, "warnings": warnings,
            "feasible": bool(zones)}


def fines_75um_limit(sand_type: str) -> float:
    """IS 383 Table 2 row iii (cl 5.2.1). Crushed quarry sand is 'crushed', not
    'manufactured' -- see the cl 3.1.2 / cl 3.1.4 note above."""
    key = f"fine_{sand_type}"
    if key not in IS383_TABLE2_FINES_75UM_MAX:
        raise MissingTableRow(f"IS 383 Table 2 has no fine-aggregate column '{sand_type}'")
    return IS383_TABLE2_FINES_75UM_MAX[key]


"""IS 383 : 2016 cl 5.4 (mechanical), 5.5 (soundness); for fine aggregate also Table 9
grading and Table 2 fines (functions above). Read from page images (printed pp. 3-4)."""

# [IS] cl 5.4.1 crushing value: wearing surfaces 30 percent Max; other than wearing, if
#      above 30 percent the 'ten percent fines' test 'should be conducted', minimum load 50 kN.
IS383_CL_5_4_1_CRUSHING_WEARING_MAX = 30.0
IS383_CL_5_4_1_TEN_PCT_FINES_MIN_KN = 50.0
# [IS] cl 5.4.2 impact value, 'as an alternative to 5.4.1': 30 (wearing) / 45 (other).
IS383_CL_5_4_2_IMPACT_MAX = {"wearing": 30.0, "other": 45.0}
# [IS] cl 5.4.2 NOTE: grades M 65 and above -- crushing and impact value <= 22 percent.
IS383_CL_5_4_2_NOTE_M65_MAX = 22.0
# [IS] cl 5.4.3 Los Angeles abrasion value: 30 (wearing) / 50 (other).
IS383_CL_5_4_3_ABRASION_MAX = {"wearing": 30.0, "other": 50.0}
# [IS] cl 5.5.1 soundness: only 'for concrete liable to be exposed to the action of frost';
#      limits 'set by agreement between the purchaser and the supplier'. The NOTE values
#      (loss after 5 cycles) are 'a general guide' -> GUIDANCE, never bound.
IS383_CL_5_5_1_GUIDE = {"fine":   {"na2so4": 10.0, "mgso4": 15.0},
                        "coarse": {"na2so4": 12.0, "mgso4": 18.0}}
# [IS] cl 5.5.2 slag aggregates: iron unsoundness <= 1 percent (tested when FeO >= 3.0
#      and S >= 1.0 percent); volumetric expansion ratio <= 2.0 percent.
IS383_CL_5_5_2 = {"iron_unsoundness_pct": 1.0, "volumetric_expansion_pct": 2.0}


def check_aggregate(kind: str, props: dict, *, grade: str, wearing_surface: bool = False,
                    frost: bool = False, agreed_soundness_loss_pct: Optional[float] = None,
                    soundness_salt: str = "na2so4", slag: bool = False,
                    use: str = "rcc") -> dict:
    """kind 'fine' or 'coarse'.
    coarse props: crushing_value, ten_pct_fines_kn, impact_value, abrasion_value.
    fine props:   passing_pct {sieve: %}, sand_type, fines_75um_pct.
    both:         soundness_loss_pct; slag: iron_unsoundness_pct, volumetric_expansion_pct."""
    if kind not in ("fine", "coarse"):
        raise ValueError("kind must be 'fine' or 'coarse'")
    res = {}
    if kind == "coarse":
        use_s = "wearing" if wearing_surface else "other"
        m65 = grade_to_fck(grade) >= 65
        cv, tf, iv = props.get("crushing_value"), props.get("ten_pct_fines_kn"), props.get("impact_value")
        # cl 5.4.1 / 5.4.2 are ALTERNATIVES: either route passing is enough.
        route1 = None
        if cv is not None:
            if m65:
                route1 = cv <= IS383_CL_5_4_2_NOTE_M65_MAX
            elif wearing_surface:
                route1 = cv <= IS383_CL_5_4_1_CRUSHING_WEARING_MAX
            else:
                route1 = (cv <= IS383_CL_5_4_1_CRUSHING_WEARING_MAX or
                          (tf is not None and tf >= IS383_CL_5_4_1_TEN_PCT_FINES_MIN_KN))
        route2 = None
        if iv is not None:
            lim = IS383_CL_5_4_2_NOTE_M65_MAX if m65 else IS383_CL_5_4_2_IMPACT_MAX[use_s]
            route2 = iv <= lim
        if route1 is None and route2 is None:
            res["strength_5_4_1_or_5_4_2"] = "not_tested"
        else:
            res["strength_5_4_1_or_5_4_2"] = "pass" if (route1 or route2) else "fail"
        res["abrasion_5_4_3"] = _judge(props.get("abrasion_value"), "max",
                                       IS383_CL_5_4_3_ABRASION_MAX[use_s])
    warnings = []
    if kind == "fine":
        st = props.get("sand_type", "crushed")
        if props.get("passing_pct"):
            z = classify_sand_zone(props["passing_pct"], st, use=use)
            res["grading_table9"] = "pass" if z["feasible"] else "fail"
            warnings += z["warnings"]
        else:
            res["grading_table9"] = "not_tested"
        res["fines_75um_table2"] = _judge(props.get("fines_75um_pct"), "max", fines_75um_limit(st))
    if frost:
        if agreed_soundness_loss_pct is None:
            res["soundness_5_5_1"] = "agreed_limit_missing"
        else:
            res["soundness_5_5_1"] = _judge(props.get("soundness_loss_pct"), "max",
                                            agreed_soundness_loss_pct)
    else:
        res["soundness_5_5_1"] = "not_required_no_frost"
    if slag:
        for k, lim in IS383_CL_5_5_2.items():
            res[k] = _judge(props.get(k), "max", lim)
    fails = [k for k, v in res.items() if v == "fail"]
    missing = [k for k, v in res.items() if v in ("not_tested", "agreed_limit_missing")]
    return {"kind": kind, "results": res, "fails": fails, "not_tested": missing,
            "conforms": False if fails else (None if missing else True), "warnings": warnings,
            "soundness_guide_pct": IS383_CL_5_5_1_GUIDE[kind][soundness_salt] if frost else None,
            "source": "IS 383:2016 cl 5.4, 5.5"}


"""IS 9103 : 1999."""

# [IS] IS 456 cl 5.5.1 — "Admixture, if used shall comply with IS 9103." No dosage cap
#      is stated there.
# [IS] IS 9103:1999 (read in full, with Amendments 1 and 2) prints NO numeric dosage
#      ceiling. cl 10.2 requires the MANUFACTURER to state the recommended dosage(s) and
#      the effect of under- and over-dosage; cl 1.3 requires the chloride content to be
#      declared ('superplasticizers are expected to be chloride free'). So the dosage
#      check compares against the manufacturer's declared range -- see the gate. IS 10262 Annex G gives TYPICAL doses (plasticisers
#      0.3-0.5 percent, superplasticisers 0.5-1.5 percent) as informative guidance,
#      not as limits.
IS9103_SP_DOSAGE_PCT_BINDER_MAX: Optional[float] = None      # UNVERIFIED

IS9103_DOSAGE_RULE = Rule(
    "IS 9103:1999", "-", "superplasticiser dosage ceiling", Status.UNVERIFIED,
    caveats=("[NV] No numeric cap read from source. If the project needs one, "
             "reclassify it as a PROJECT_CONSTRAINT and label it so -- never as a "
             "code requirement.",),
)


"""IS 4926 : 2003. cl 5.2.1.1, 5.2.2.1, 5.2.2.2, 6.2.1, 6.3.1, 6.3.2, Annex E E-1(a)."""
import math

# ------------------------------------------------------------ cl 6.2.1
# [IS] Tested on discharge from the producer's vehicle on site (or into the
#      purchaser's vehicle). Responsibility passes to the purchaser if discharge is
#      delayed more than 30 min through the purchaser's lack of preparedness.
# [IS] Slump: "+/-25 mm or +/-1/3 of the specified value, whichever is less."
IS4926_CL_6_2_1_SLUMP_TOL_MM = 25.0
IS4926_CL_6_2_1_SLUMP_TOL_FRACTION = 1.0 / 3.0
# [IS] Compacting factor: +/-0.03 where specified >= 0.90; +/-0.04 where < 0.90 but
#      > 0.80; +/-0.05 where <= 0.80.
IS4926_CL_6_2_1_CF_TOL = {"ge_0.90": 0.03, "lt_0.90_gt_0.80": 0.04, "le_0.80": 0.05}
IS4926_CL_6_2_1_PURCHASER_DELAY_MIN = 30


def slump_acceptance_band(specified_mm: float) -> dict:
    """IS 4926 cl 6.2.1. Acceptance band for MEASURED slump at discharge."""
    tol = min(IS4926_CL_6_2_1_SLUMP_TOL_MM,
              IS4926_CL_6_2_1_SLUMP_TOL_FRACTION * specified_mm)
    return {"low": specified_mm - tol, "high": specified_mm + tol, "tol_mm": tol,
            "where": "at discharge from the producer's vehicle",
            "source": "IS 4926 cl 6.2.1"}


def compacting_factor_band(specified: float) -> dict:
    """IS 4926 cl 6.2.1. Compacting factor tolerance."""
    if specified >= 0.90:
        tol = IS4926_CL_6_2_1_CF_TOL["ge_0.90"]
    elif specified > 0.80:
        tol = IS4926_CL_6_2_1_CF_TOL["lt_0.90_gt_0.80"]
    else:
        tol = IS4926_CL_6_2_1_CF_TOL["le_0.80"]
    return {"low": specified - tol, "high": specified + tol, "tol": tol,
            "source": "IS 4926 cl 6.2.1"}


def flow_acceptance_band(specified_mm: float) -> dict:
    """IS 4926 cl 6.2.1 prints NO flow tolerance -- deliberately."""
    raise AgreedBetweenParties(
        "IS 4926 cl 6.2.1: 'Acceptance criteria for spread (flow) are to be established "
        "between the supplier and the purchaser' (see IS 9103). Record the agreed band "
        "as a PROJECT_CONSTRAINT; do not invent one.")


# ------------------------------------------------------------ cl 5.2.1.1 / 5.2.2
# [IS] cl 5.2.1.1 -- the purchaser SHOULD plan to discharge a full load within 30 min
#      of arrival on site. GUIDANCE.
IS4926_CL_5_2_1_1_DISCHARGE_AFTER_ARRIVAL_MIN = 30
# [IS] cl 5.2.2.1 -- general requirement: discharged within 2 h of loading. A longer
#      period MAY be permitted with retarding admixtures, in cool humid weather, or
#      for chilled concrete.
IS4926_CL_5_2_2_1_MAX_TRANSPORT_MIN = 120
# [IS] cl 5.2.2.2 -- loading time starts at adding mixing water to the dry mix of cement
#      and aggregate, or adding cement to wet aggregate, whichever is applicable.


def transport_time_check(minutes_since_loading: float, *, retarder: bool = False,
                         cool_humid: bool = False, chilled: bool = False) -> dict:
    """IS 4926 cl 5.2.2.1 / 5.2.2.2. Clock starts per cl 5.2.2.2, not at batching end."""
    if minutes_since_loading <= IS4926_CL_5_2_2_1_MAX_TRANSPORT_MIN:
        outcome = "pass"
    elif retarder or cool_humid or chilled:
        outcome = "override_required"      # 'may be permitted' -- needs recorded permission
    else:
        outcome = "fail"
    return {"outcome": outcome, "minutes": minutes_since_loading,
            "limit_min": IS4926_CL_5_2_2_1_MAX_TRANSPORT_MIN,
            "source": "IS 4926 cl 5.2.2.1 (clock per cl 5.2.2.2)"}


# ------------------------------------------------------------ cl 6.3
# [IS] cl 6.3.1 -- strength compliance assessed against IS 456 -> acceptance_is456().
# [IS] cl 6.3.2 -- "Unless otherwise agreed ... SHOULD be one sample for every 50 m3 of
#      production or every 50 batches, whichever is the greater frequency. Three test
#      specimens ... at 28 days." 28-day compressive strength "shall alone be the
#      criteria for acceptance or rejection". Verb 'should' + 'unless agreed' -> GUIDANCE.
IS4926_CL_6_3_2_EVERY_M3 = 50
IS4926_CL_6_3_2_EVERY_BATCHES = 50
IS4926_CL_6_3_2_SPECIMENS = 3


def min_samples_is4926(production_m3: float, n_batches: int) -> dict:
    """IS 4926 cl 6.3.2 producer default. [EI] 'every 50' read as ceil(n/50)."""
    by_vol = math.ceil(production_m3 / IS4926_CL_6_3_2_EVERY_M3)
    by_bat = math.ceil(n_batches / IS4926_CL_6_3_2_EVERY_BATCHES)
    return {"samples": max(by_vol, by_bat, 1), "by_volume": by_vol, "by_batches": by_bat,
            "status": "guidance", "specimens_per_sample": IS4926_CL_6_3_2_SPECIMENS,
            "source": "IS 4926 cl 6.3.2 (default, 'unless otherwise agreed')"}


# ------------------------------------------------------------ Annex E, E-1(a)
# [IS] Weighing devices shall enable batching within: cement and mineral admixtures
#      +/-2 percent; aggregate, chemical admixtures and water +/-3 percent of the
#      quantity of the constituent being measured. Corroborated by IS 456 cl 10.2.2.
IS4926_ANNEX_E_TOL_PCT = {"cement": 2.0, "mineral_admixture": 2.0,
                          "aggregate": 3.0, "chemical_admixture": 3.0, "water": 3.0}


def batch_within_tolerance(rows: dict) -> dict:
    """rows = {name: (design_kg, actual_kg, kind)}, kind in IS4926_ANNEX_E_TOL_PCT.

    [EI] Annex E is an EQUIPMENT accuracy requirement. Applying it to recorded batch
         weights against design weights is our interpretation: it flags a batch whose
         actual quantities could not have come from a compliant weigh-batcher.
    """
    out, bad = {}, []
    for name, (design, actual, kind) in rows.items():
        if kind not in IS4926_ANNEX_E_TOL_PCT:
            raise MissingTableRow(f"IS 4926 Annex E has no class {kind!r}; classes: "
                                  f"{sorted(IS4926_ANNEX_E_TOL_PCT)}")
        if design == 0:
            dev = 0.0 if actual == 0 else float("inf")
        else:
            dev = abs(actual - design) / design * 100.0
        ok = dev <= IS4926_ANNEX_E_TOL_PCT[kind] + 1e-9
        out[name] = {"deviation_pct": dev, "tol_pct": IS4926_ANNEX_E_TOL_PCT[kind], "ok": ok}
        if not ok:
            bad.append(name)
    return {"ok": not bad, "out_of_tolerance": bad, "detail": out,
            "source": "IS 4926 Annex E E-1(a); IS 456 cl 10.2.2", "basis": "[EI]"}


"""IS 1199 (Part 2) : 2018 (First Revision). cl 4.1, 4.3.1, 4.3.3(p), 4.3.4, 4.7.1."""

# [IS] cl 4.3.1 -- the slump test 'is applicable to a range of consistency ... slumps
#      between 10 mm and 210 mm. Outside this range, other method ... should be considered'.
IS1199_2_SLUMP_RANGE_MM = (10.0, 210.0)
# [IS] cl 4.3.3 (p) / 4.3.4 -- measure to the nearest 5 mm; the test is valid only if it
#      yields a TRUE slump; sheared or collapsed -> repeat; two in a row -> invalid.
IS1199_2_SLUMP_RESOLUTION_MM = 5.0
# [IS] cl 4.7.1 -- flow table applicable for flow between 340 mm and 620 mm; not for SCC;
#      not suitable if the concrete segregates.
IS1199_2_FLOW_RANGE_MM = (340.0, 620.0)
# [IS] cl 4.1 -- these tests are not applicable where nominal maximum aggregate size
#      exceeds 40 mm, unless wet-sieved through a 40 mm screen.
IS1199_2_MAX_MSA_MM = 40.0


def slump_reading_valid(slump_mm: float, shape: str = "true", msa_mm: float = 20.0) -> dict:
    """shape: 'true', 'shear' or 'collapse'."""
    if msa_mm > IS1199_2_MAX_MSA_MM:
        return {"valid": False, "why": "msa > 40 mm without wet sieving (cl 4.1)"}
    if shape != "true":
        return {"valid": False, "why": f"{shape} slump is not a true slump (cl 4.3.4)"}
    lo, hi = IS1199_2_SLUMP_RANGE_MM
    if not lo <= slump_mm <= hi:
        return {"valid": False,
                "why": f"{slump_mm} mm outside the slump test range {lo:.0f}-{hi:.0f} mm (cl 4.3.1)"}
    return {"valid": True, "why": "", "source": "IS 1199 (Part 2):2018 cl 4.3"}


def flow_reading_valid(flow_mm: float, segregated: bool = False) -> dict:
    lo, hi = IS1199_2_FLOW_RANGE_MM
    if segregated:
        return {"valid": False, "why": "segregated (cl 4.7.1)"}
    if not lo <= flow_mm <= hi:
        return {"valid": False, "why": f"{flow_mm} mm outside {lo:.0f}-{hi:.0f} mm (cl 4.7.1)"}
    return {"valid": True, "why": "", "source": "IS 1199 (Part 2):2018 cl 4.7.1"}


"""IS 3812 (Part 1) : 2013. cl 3.2, 3.9, 6.1, 6.2, 7.1, 7.2, 8.2, Table 1, Table 2."""

# [IS] cl 3.2 / 3.9 -- calcareous if reactive CaO >= 10 percent; siliceous if < 10.
IS3812_REACTIVE_CAO_SPLIT_PCT = 10.0

# [IS] Table 1 chemical requirements, percent by mass: (kind, siliceous, calcareous)
IS3812_TABLE1 = {
    "sio2_al2o3_fe2o3": ("min", 70.0, 50.0),
    "sio2":             ("min", 35.0, 25.0),
    "reactive_silica":  ("min", 20.0, 20.0),   # footnote 1: tested only IF AGREED
    "mgo":              ("max",  5.0,  5.0),
    "so3":              ("max",  3.0,  3.0),
    "available_alkali_na2o": ("max", 1.5, 1.5),
    "chlorides":        ("max", 0.05, 0.05),
    "loi":              ("max",  5.0,  5.0),
}
IS3812_TABLE1_IF_AGREED = frozenset({"reactive_silica"})

# [IS] Table 2 physical requirements: (kind, limit)
IS3812_TABLE2 = {
    "blaine_m2_kg":           ("min", 320.0),
    "residue_45um_pct":       ("max", 34.0),    # footnote 1: OPTIONAL test
    "lime_reactivity_mpa":    ("min", 4.5),
    "comp_28d_pct_of_plain":  ("min", 80.0),    # 'not less than 80 percent of plain mortar'
    "autoclave_expansion_pct": ("max", 0.8),
}
IS3812_TABLE2_OPTIONAL = frozenset({"residue_45um_pct"})
# [IS] cl 6.2 -- in DRY condition, moisture shall not exceed 2.0 percent. The cl 6.1
#      chemical tests are nevertheless carried out on OVEN-DRY samples.
IS3812_CL_6_2_MOISTURE_MAX_PCT = 2.0
# [IS] cl 8.2 -- all other tests in the 'as supplied' condition (after beneficiation,
#      segregation or processing, if any).

# [IS] cl 7.2 Uniformity -- "In tests on individual samples, the specific surface,
#      particles retained on 45 micron IS Sieve (wet sieving) and lime reactivity value
#      shall not vary more than 15 percent from the average established from the tests
#      on the 10 preceding samples or of all preceding samples if less than 10."
IS3812_CL_7_2_UNIFORMITY_PCT = 15.0
IS3812_CL_7_2_WINDOW = 10
IS3812_CL_7_2_PROPERTIES = ("blaine_m2_kg", "residue_45um_pct", "lime_reactivity_mpa")


def _judge(value, kind: str, limit: float) -> str:
    if value is None:
        return "not_tested"
    return "pass" if (value >= limit if kind == "min" else value <= limit) else "fail"


def fly_ash_class(reactive_cao_pct: float) -> str:
    """IS 3812 (Part 1) cl 3.2 / 3.9."""
    return "calcareous" if reactive_cao_pct >= IS3812_REACTIVE_CAO_SPLIT_PCT else "siliceous"


def fly_ash_uniformity(history: list, current: dict) -> dict:
    """IS 3812 (Part 1) cl 7.2. history = earlier samples of the SAME source, oldest
    first, each a dict with IS3812_CL_7_2_PROPERTIES keys.

    [EI] The window is the last 10 samples in sequence; a sample that did not measure a
         property is skipped for that property's average. With no earlier sample the
         clause cannot be applied yet ('no_history' -- not a pass).
    """
    window = list(history)[-IS3812_CL_7_2_WINDOW:]
    res = {}
    for p in IS3812_CL_7_2_PROPERTIES:
        cur = current.get(p)
        prev = [h[p] for h in window if h.get(p) is not None]
        if cur is None:
            res[p] = {"outcome": ("optional_not_tested" if p in IS3812_TABLE2_OPTIONAL
                                  else "not_tested")}
            continue
        if not prev:
            res[p] = {"outcome": "no_history"}
            continue
        avg = sum(prev) / len(prev)
        dev = abs(cur - avg) / avg * 100.0
        res[p] = {"outcome": "pass" if dev <= IS3812_CL_7_2_UNIFORMITY_PCT + 1e-9 else "fail",
                  "deviation_pct": dev, "average": avg, "n_preceding": len(prev)}
    return {"results": res,
            "fails": [p for p, r in res.items() if r["outcome"] == "fail"],
            "source": "IS 3812 (Part 1):2013 cl 7.2"}


def check_fly_ash(props: dict, *, dry_supply: bool = True,
                  history: Optional[list] = None) -> dict:
    """Certificate check. props keys = IS3812_TABLE1 / IS3812_TABLE2 keys, plus
    'reactive_cao' (required, decides the class) and 'moisture_pct'.

    history -- earlier samples from the same source, for cl 7.2 uniformity. Without it
    the uniformity clause is NOT assessed, and 'conforms' is reported as None rather
    than True: a single certificate cannot show full conformity to this standard.
    """
    if props.get("reactive_cao") is None:
        raise MissingTableRow("IS 3812 (Part 1) Table 1 columns depend on the class; "
                              "supply 'reactive_cao' (cl 3.2 / 3.9).")
    cls = fly_ash_class(props["reactive_cao"])
    col = 1 if cls == "siliceous" else 2
    res = {}
    for k, row in IS3812_TABLE1.items():
        v = _judge(props.get(k), row[0], row[col])
        if v == "not_tested" and k in IS3812_TABLE1_IF_AGREED:
            v = "not_required_unless_agreed"
        res[k] = v
    for k, (kind, lim) in IS3812_TABLE2.items():
        v = _judge(props.get(k), kind, lim)
        if v == "not_tested" and k in IS3812_TABLE2_OPTIONAL:
            v = "optional_not_tested"
        res[k] = v
    if dry_supply:
        res["moisture_pct"] = _judge(props.get("moisture_pct"), "max",
                                     IS3812_CL_6_2_MOISTURE_MAX_PCT)
    uni = None
    if history is not None:
        uni = fly_ash_uniformity(history, props)
        for p, r in uni["results"].items():
            res[f"uniformity_{p}"] = r["outcome"]
    fails = [k for k, v in res.items() if v == "fail"]
    missing = [k for k, v in res.items() if v in ("not_tested", "no_history")]
    if fails:
        conforms = False
    elif missing or uni is None:
        conforms = None                      # cannot be shown either way yet
    else:
        conforms = True
    return {"class": cls, "results": res, "fails": fails, "not_tested": missing,
            "uniformity_assessed": uni is not None, "conforms": conforms,
            "source": "IS 3812 (Part 1):2013 Table 1, Table 2, cl 6.2, cl 7.2"}


"""IS 16714 : 2018. cl 4, 5.1, 5.2, 5.3, 6, Table 1, Table 2."""

# [IS] Table 1 chemical requirements, percent by mass: (kind, limit)
IS16714_TABLE1 = {
    "mno":               ("max", 5.5),
    "mgo":               ("max", 17.0),
    "sulphide_sulphur":  ("max", 2.0),
    "so3":               ("max", 3.0),
    "insoluble_residue": ("max", 3.0),
    "chloride":          ("max", 0.1),
    "loi":               ("max", 3.0),
}
# [IS] Table 1 rows viii-x, ratio MINIMA.
#   viii (CaO + MgO + Al2O3/3) / (SiO2 + 2 Al2O3/3)      >= 1.0
#   ix   (CaO + MgO + Al2O3) / SiO2                      >= 1.0
#   x    (CaO + CaS + MgO/2 + Al2O3) / (SiO2 + MnO)      >= 1.5, ONLY for MnO > 2.5 %
# [EI] row viii is printed 'AlO3'; read as Al2O3 (the only oxide that fits).
IS16714_RATIO_MIN = {"viii": 1.0, "ix": 1.0, "x": 1.5}
IS16714_RATIO_X_APPLIES_ABOVE_MNO = 2.5

# [IS] Table 2 physical requirements.
IS16714_TABLE2 = {
    "blaine_m2_kg":  ("min", 320.0),
    "sai_7d_pct":    ("min", 60.0),     # of control OPC 43 mortar (Note 2: 50/50 blend)
    "sai_28d_pct":   ("min", 75.0),
}
IS16714_CL_4_ADDITIVES_MAX_PCT = 1.0     # [IS] 'not more than 1.0 percent of additives'
IS16714_CL_5_2_MOISTURE_MAX_PCT = 1.0    # [IS] 'shall not exceed 1 percent by mass'
IS16714_CL_5_3_GLASS_MIN_PCT = 85.0      # [IS] 'not less than 85 percent'


def ggbs_ratios(*, cao: float, mgo: float, al2o3: float, sio2: float,
                mno: Optional[float] = None, cas: Optional[float] = None) -> dict:
    out = {"viii": (cao + mgo + al2o3 / 3.0) / (sio2 + 2.0 * al2o3 / 3.0),
           "ix":   (cao + mgo + al2o3) / sio2}
    if mno is not None and mno > IS16714_RATIO_X_APPLIES_ABOVE_MNO:
        if cas is None:
            out["x"] = None          # applies, but CaS not supplied
        else:
            out["x"] = (cao + cas + mgo / 2.0 + al2o3) / (sio2 + mno)
    return out


def check_ggbs(props: dict) -> dict:
    """Certificate check. Oxide keys: cao, mgo, al2o3, sio2, mno, cas."""
    res = {k: _judge(props.get(k), kind, lim) for k, (kind, lim) in IS16714_TABLE1.items()}
    if all(props.get(k) is not None for k in ("cao", "mgo", "al2o3", "sio2")):
        rat = ggbs_ratios(cao=props["cao"], mgo=props["mgo"], al2o3=props["al2o3"],
                          sio2=props["sio2"], mno=props.get("mno"), cas=props.get("cas"))
        for k, v in rat.items():
            res[f"ratio_{k}"] = _judge(v, "min", IS16714_RATIO_MIN[k])
    else:
        res["ratio_viii"] = res["ratio_ix"] = "not_tested"
    for k, (kind, lim) in IS16714_TABLE2.items():
        res[k] = _judge(props.get(k), kind, lim)
    res["additives_pct"] = _judge(props.get("additives_pct"), "max", IS16714_CL_4_ADDITIVES_MAX_PCT)
    res["moisture_pct"]  = _judge(props.get("moisture_pct"), "max", IS16714_CL_5_2_MOISTURE_MAX_PCT)
    res["glass_pct"]     = _judge(props.get("glass_pct"), "min", IS16714_CL_5_3_GLASS_MIN_PCT)
    fails = [k for k, v in res.items() if v == "fail"]
    missing = [k for k, v in res.items() if v == "not_tested"]
    return {"results": res, "fails": fails, "not_tested": missing,
            "conforms": (not fails and not missing),
            "source": "IS 16714:2018 Table 1, Table 2, cl 4, 5.2, 5.3"}


"""IS 456 cl 5.1 (cement types); IS 1489 (Part 1):1991 with Amendments 1-5:
cl 5 (Amd 3), Table 1, cl 7.1-7.5, cl 9.1, cl 9.2 Notes (Amd 4)."""

# [IS] IS 456 cl 5.1 lists, among others: OPC 33 (IS 269), 43 (IS 8112), 53 (IS 12269);
#      Portland slag (IS 455); PPC fly ash based (IS 1489 Part 1); PPC calcined clay
#      (IS 1489 Part 2); sulphate resisting (IS 12330). IS 10262:2019 cl 2 instead cites
#      IS 269:2015 for OPC.
CEMENT_TYPES = {
    "OPC": {"standard": "IS 269:2015", "state": "encoded"},
    "PPC": {"standard": "IS 1489 (Part 1)", "state": "encoded"},
    "PSC": {"standard": "IS 455:2015", "state": "encoded"},
    "SRC": {"standard": "IS 12330", "state": "not_in_library"},
    "SSC": {"standard": "IS 6909", "state": "not_in_library"},
}

# [IS] IS 1489 (Part 1) cl 5, last-but-one sentence as substituted by Amendment No. 3
#      (July 2000): fly ash constituent not less than 15 and not more than 35 percent by
#      mass of PPC. (The un-amended body text reads 10 and 25 -- superseded.)
IS1489_1_FLY_ASH_CONSTITUENT_PCT = (15.0, 35.0)
# [IS] cl 9.1 -- the manufacturer furnishes a certificate indicating the percentage of
#      fly ash, and states it does not vary more than +/-3 percent from that value.
IS1489_1_CL_9_1_DECLARED_TOL_PCT = 3.0

# [IS] Table 1 chemical requirements (percent by mass, Max). Insoluble material max is
#      x + 4.0 (100 - x)/100, x = declared fly ash percent.
IS1489_1_TABLE1 = {"loi": 5.0, "mgo": 6.0, "so3": 3.0}
# [IS] cl 7.1 fineness >= 300 m2/kg; cl 7.3 setting initial >= 30 min, final <= 600 min;
#      cl 7.4.1 mortar strength >= 16 / 22 / 33 MPa at 72 h / 168 h / 672 h;
#      cl 7.5 drying shrinkage <= 0.15 percent.
IS1489_1_CL_7_1_FINENESS_MIN = 300.0
IS1489_1_CL_7_3_SETTING_MIN = {"initial_min": 30.0, "final_max": 600.0}
IS1489_1_CL_7_4_STRENGTH_MIN = {"3d": 16.0, "7d": 22.0, "28d": 33.0}
IS1489_1_CL_7_5_SHRINKAGE_MAX = 0.15
# [IS] cl 7.2.1 SOUNDNESS, unaerated: Le Chatelier <= 10 mm, autoclave <= 0.8 percent.
#      cl 7.2.1.1: on failure, retest after 7-day aeration: <= 5 mm and <= 0.6 percent.
IS1489_1_CL_7_2_1 = {"le_chatelier_mm": 10.0, "autoclave_pct": 0.8}
IS1489_1_CL_7_2_1_1_AERATED = {"le_chatelier_mm": 5.0, "autoclave_pct": 0.6}
# [IS] cl 9.2 Notes (Amendment No. 4): total chloride in cement <= 0.1 percent;
#      <= 0.05 percent for prestressed concrete (if the purchaser requires).
IS1489_1_CL_9_2_CHLORIDE_MAX = {"general": 0.1, "prestressed": 0.05}


def _soundness(cert: dict, unaerated: dict, aerated: dict) -> dict:
    """Two-stage soundness: unaerated test, then the aerated retest for each failure."""
    out = {}
    for k in unaerated:
        v, va = cert.get(k), cert.get(f"{k}_aerated")
        if v is None:
            out[k] = "not_tested"
        elif v <= unaerated[k]:
            out[k] = "pass"
        elif va is None:
            out[k] = "fail_retest_after_aeration"
        else:
            out[k] = "pass_after_aeration" if va <= aerated[k] else "fail"
    return out


def check_ppc(cert: dict) -> dict:
    """IS 1489 (Part 1) certificate check. Keys: declared_fly_ash_pct, loi, mgo, so3,
    insoluble, blaine_m2_kg, initial_set_min, final_set_min, str_3d/7d/28d,
    drying_shrinkage_pct, le_chatelier_mm, autoclave_pct (+ '_aerated'), chloride_pct."""
    res = {}
    x = cert.get("declared_fly_ash_pct")
    lo, hi = IS1489_1_FLY_ASH_CONSTITUENT_PCT
    res["declared_fly_ash_pct"] = ("not_tested" if x is None else
                                   "pass" if lo <= x <= hi else "fail")
    for k, lim in IS1489_1_TABLE1.items():
        res[k] = _judge(cert.get(k), "max", lim)
    if x is not None:
        res["insoluble"] = _judge(cert.get("insoluble"), "max", x + 4.0 * (100.0 - x) / 100.0)
    else:
        res["insoluble"] = "not_tested"
    res["blaine_m2_kg"] = _judge(cert.get("blaine_m2_kg"), "min", IS1489_1_CL_7_1_FINENESS_MIN)
    res["initial_set_min"] = _judge(cert.get("initial_set_min"), "min",
                                    IS1489_1_CL_7_3_SETTING_MIN["initial_min"])
    res["final_set_min"] = _judge(cert.get("final_set_min"), "max",
                                  IS1489_1_CL_7_3_SETTING_MIN["final_max"])
    for age, lim in IS1489_1_CL_7_4_STRENGTH_MIN.items():
        res[f"str_{age}"] = _judge(cert.get(f"str_{age}"), "min", lim)
    res["drying_shrinkage_pct"] = _judge(cert.get("drying_shrinkage_pct"), "max",
                                         IS1489_1_CL_7_5_SHRINKAGE_MAX)
    res.update({f"soundness_{k}": v for k, v in
                _soundness(cert, IS1489_1_CL_7_2_1, IS1489_1_CL_7_2_1_1_AERATED).items()})
    res["chloride_pct"] = _judge(cert.get("chloride_pct"), "max",
                                 IS1489_1_CL_9_2_CHLORIDE_MAX["general"])
    fails = [k for k, v in res.items() if v.startswith("fail")]
    missing = [k for k, v in res.items() if v == "not_tested"]
    return {"cement_type": "PPC", "results": res, "fails": fails, "not_tested": missing,
            "conforms": False if fails else (None if missing else True),
            "source": "IS 1489 (Part 1):1991 + Amd 1-5"}


def check_cement(cement_type: str, cert: dict, opc_grade: Optional[str] = None) -> dict:
    """Route to the cement's own standard. Blocked types report, they never pass."""
    ct = str(cement_type).upper()
    if ct == "PPC":
        return check_ppc(cert)
    if ct == "OPC":
        if opc_grade is None:
            raise MissingTableRow("OPC conformity needs the grade: one of "
                                  f"{sorted(IS269_TABLE3_STRENGTH_MPA)} (IS 269:2015 cl 4)")
        return check_opc(cert, opc_grade)
    if ct == "PSC":
        return check_psc(cert)
    if ct not in CEMENT_TYPES:
        raise MissingTableRow(f"unknown cement type {cement_type!r}; known: {sorted(CEMENT_TYPES)}")
    meta = CEMENT_TYPES[ct]
    return {"cement_type": ct, "results": {}, "fails": [], "not_tested": ["all"],
            "conforms": None,
            "source": f"{meta['standard']} -- {meta['state'].upper()}: {meta.get('why', '')}"}


def countable_fly_ash(cement_kg_m3: float, fly_ash_kg_m3: float, cement_type: str = "OPC",
                      ppc_fly_ash_declared_pct: Optional[float] = None) -> dict:
    """How much ADDED fly ash may count toward the IS 456 Table 5 minimum and w/c (Note 1).

    [IS] Note 1: additions count 'as long as the maximum amounts taken into account do not
         exceed the limit of pozzolona ... specified in IS 1489 (Part 1)' = 35 percent.
    [EI] Total pozzolana share = (x.C + F)/(C + F) <= 35 percent, where x is the fly ash
         already inside the cement (0 for OPC). Hence counted F <= C (0.35 - x)/0.65.
    [EI] PPC with a certificate: x = declared + 3 (the cl 9.1 tolerance, worst case).
    [EI] PPC without a certificate (the GENERAL, plant-independent case): x = 35, the
         upper limit IS 1489 permits. Any PPC that conforms to IS 1489 is covered, so the
         result holds for every conforming PPC. With x = 35 no ADDED fly ash counts:
         PPC is taken whole as the cement, exactly as IS 10262 Annex A does.
    """
    ct = str(cement_type).upper()
    h = IS1489_1_FLY_ASH_CONSTITUENT_PCT[1] / 100.0

    def cap(x_pct):
        return max(cement_kg_m3 * (h - x_pct / 100.0) / (1.0 - h), 0.0)

    if ct == "OPC":
        c = min(fly_ash_kg_m3, cap(0.0))
        lo = hi = c
        basis = "OPC: no fly ash in the cement"
    elif ct == "PPC":
        if ppc_fly_ash_declared_pct is not None:
            x = min(ppc_fly_ash_declared_pct + IS1489_1_CL_9_1_DECLARED_TOL_PCT, h * 100.0)
            lo = hi = min(fly_ash_kg_m3, cap(x))
            basis = f"PPC declared {ppc_fly_ash_declared_pct}% +3 (cl 9.1) = {x}%"
        else:
            # GENERAL (not plant-specific) use: the standard's own upper limit, 35 %.
            x = IS1489_1_FLY_ASH_CONSTITUENT_PCT[1]
            lo = hi = min(fly_ash_kg_m3, cap(x))
            best = min(fly_ash_kg_m3, cap(IS1489_1_FLY_ASH_CONSTITUENT_PCT[0]))
            basis = (f"PPC at the IS 1489 upper limit {x:.0f}% (standard basis, no plant "
                     f"certificate); a 15% PPC would allow {best:.0f} kg")
    else:
        raise UnverifiedRule(f"fly ash counting for {ct} needs {CEMENT_TYPES.get(ct, {}).get('standard', '?')}, "
                             f"which is not encoded.")
    return {"counted_kg": lo, "counted_lo": lo, "counted_hi": hi, "decidable": abs(hi - lo) < 1e-9,
            "capped": fly_ash_kg_m3 > hi + 1e-9, "basis": basis,
            "source": "IS 456 Table 5 Note 1 + IS 1489 (Part 1) cl 5 (Amd 3), cl 9.1"}


# ============================================================== IS 269 : 2015 (OPC)
# [IS] IS 269:2015 (Sixth Revision, Reaffirmed 2020), cl 4 designations OPC 33, OPC 43,
#      OPC 43S, OPC 53, OPC 53S. Table 2 (cl 6.1) chemical; Table 3 (cl 7) physical.
# [IS] Table 2: LSF 0.66-1.02 (33, 43) / 0.80-1.02 (43S, 53, 53S); A/F >= 0.66;
#      insoluble residue <= 5.0 (2.0 for 43S, 53S); MgO <= 6.0 (5.0 for 43S, 53S);
#      SO3 <= 3.5; LOI <= 5.0 (33, 43) / 4.0 (43S, 53, 53S); chloride <= 0.1 (0.05 for
#      prestressed structures).
IS269_TABLE2_CHEM = {
    "OPC 33":  {"lsf": (0.66, 1.02), "af_min": 0.66, "ir": 5.0, "mgo": 6.0, "so3": 3.5, "loi": 5.0},
    "OPC 43":  {"lsf": (0.66, 1.02), "af_min": 0.66, "ir": 5.0, "mgo": 6.0, "so3": 3.5, "loi": 5.0},
    "OPC 43S": {"lsf": (0.80, 1.02), "af_min": 0.66, "ir": 2.0, "mgo": 5.0, "so3": 3.5, "loi": 4.0},
    "OPC 53":  {"lsf": (0.80, 1.02), "af_min": 0.66, "ir": 5.0, "mgo": 6.0, "so3": 3.5, "loi": 4.0},
    "OPC 53S": {"lsf": (0.80, 1.02), "af_min": 0.66, "ir": 2.0, "mgo": 5.0, "so3": 3.5, "loi": 4.0},
}
IS269_TABLE2_CHLORIDE_MAX = {"general": 0.1, "prestressed": 0.05}
# [IS] Table 3: fineness >= 225 m2/kg (370 for 43S, 53S); Le Chatelier <= 10 mm
#      (5 mm for 43S, 53S); autoclave <= 0.8 percent; initial set >= 30 min (60 for
#      43S, 53S); final set <= 600 min; compressive strength at 72 h / 168 h / 672 h:
#      33: 16 / 22 / 33-48;  43: 23 / 33 / 43-58;  43S: 23 / 37.5 / 43;
#      53: 27 / 37 / 53;     53S: 27 / 37.5 / 53.
# [IS] Note 1: on soundness failure, retest after 7-day aeration: <= 5 mm and <= 0.6 %.
IS269_TABLE3_PHYS = {
    "OPC 33":  {"blaine": 225.0, "le_chatelier_mm": 10.0, "autoclave_pct": 0.8, "initial_set": 30.0, "final_set": 600.0},
    "OPC 43":  {"blaine": 225.0, "le_chatelier_mm": 10.0, "autoclave_pct": 0.8, "initial_set": 30.0, "final_set": 600.0},
    "OPC 43S": {"blaine": 370.0, "le_chatelier_mm": 5.0,  "autoclave_pct": 0.8, "initial_set": 60.0, "final_set": 600.0},
    "OPC 53":  {"blaine": 225.0, "le_chatelier_mm": 10.0, "autoclave_pct": 0.8, "initial_set": 30.0, "final_set": 600.0},
    "OPC 53S": {"blaine": 370.0, "le_chatelier_mm": 5.0,  "autoclave_pct": 0.8, "initial_set": 60.0, "final_set": 600.0},
}
IS269_TABLE3_STRENGTH_MPA = {   # (3d min, 7d min, 28d min, 28d max or None)
    "OPC 33":  (16.0, 22.0, 33.0, 48.0),
    "OPC 43":  (23.0, 33.0, 43.0, 58.0),
    "OPC 43S": (23.0, 37.5, 43.0, None),
    "OPC 53":  (27.0, 37.0, 53.0, None),
    "OPC 53S": (27.0, 37.5, 53.0, None),
}
IS269_TABLE3_NOTE1_AERATED = {"le_chatelier_mm": 5.0, "autoclave_pct": 0.6}
# [IS] cl 11.1 (g) -- each bag shall be marked with the "Need for testing of cement more
#      than 3 months old to check conformity before its use". cl 11.1 (f): best before
#      date is 3 months from the date of packing.
IS269_CL_11_1_RETEST_AFTER_MONTHS = 3


def check_opc(cert: dict, grade: str, *, prestressed: bool = False) -> dict:
    """IS 269:2015 certificate check. grade: 'OPC 33' | 'OPC 43' | 'OPC 43S' | 'OPC 53' |
    'OPC 53S' (or 33/43/53). Keys as check_ppc, plus lsf, af_ratio, age_months and
    retested_after_age (True once fresh conformity data for the aged cement exist)."""
    g = str(grade).upper().replace("OPC", "").strip()
    key = f"OPC {g}"
    if key not in IS269_TABLE2_CHEM:
        raise MissingTableRow(f"IS 269:2015 has no designation {grade!r}; "
                              f"printed: {sorted(IS269_TABLE2_CHEM)}")
    ch, ph, st = IS269_TABLE2_CHEM[key], IS269_TABLE3_PHYS[key], IS269_TABLE3_STRENGTH_MPA[key]
    res = {}
    lsf = cert.get("lsf")
    res["lsf"] = ("not_tested" if lsf is None else
                  "pass" if ch["lsf"][0] <= lsf <= ch["lsf"][1] else "fail")
    res["af_ratio"] = _judge(cert.get("af_ratio"), "min", ch["af_min"])
    for k, lim in (("insoluble", ch["ir"]), ("mgo", ch["mgo"]), ("so3", ch["so3"]),
                   ("loi", ch["loi"])):
        res[k] = _judge(cert.get(k), "max", lim)
    res["chloride_pct"] = _judge(cert.get("chloride_pct"), "max",
                                 IS269_TABLE2_CHLORIDE_MAX["prestressed" if prestressed else "general"])
    res["blaine_m2_kg"] = _judge(cert.get("blaine_m2_kg"), "min", ph["blaine"])
    res["initial_set_min"] = _judge(cert.get("initial_set_min"), "min", ph["initial_set"])
    res["final_set_min"] = _judge(cert.get("final_set_min"), "max", ph["final_set"])
    for age, lim in zip(("3d", "7d", "28d"), st[:3]):
        res[f"str_{age}"] = _judge(cert.get(f"str_{age}"), "min", lim)
    if st[3] is not None and cert.get("str_28d") is not None and cert["str_28d"] > st[3]:
        res["str_28d"] = "fail"
    res.update({f"soundness_{k}": v for k, v in
                _soundness(cert, {"le_chatelier_mm": ph["le_chatelier_mm"],
                                  "autoclave_pct": ph["autoclave_pct"]},
                           IS269_TABLE3_NOTE1_AERATED).items()})
    # [IS] cl 11.1 (g) is a marking requirement: cement more than 3 months old is to be
    #      TESTED before use. It does not make the cement non-conforming, so it is a
    #      'retest_required' state that fresh conformity data clear -- never a fail.
    age = cert.get("age_months")
    res["age"] = ("not_tested" if age is None else
                  "pass" if age <= IS269_CL_11_1_RETEST_AFTER_MONTHS or cert.get("retested_after_age")
                  else "retest_required")
    fails = [k for k, v in res.items() if v.startswith("fail")]
    missing = [k for k, v in res.items() if v in ("not_tested", "retest_required")]
    return {"cement_type": key, "results": res, "fails": fails, "not_tested": missing,
            "conforms": False if fails else (None if missing else True),
            "source": "IS 269:2015 Tables 2 and 3, cl 11.1"}


# ============================================================== IS 455 : 2015 (PSC)
# [IS] IS 455:2015 cl 5 -- "The granulated slag constituent shall not be less than 25
#      percent and not more than 70 percent by mass of Portland slag cement."
#      cl 4.3 -- Portland cement for blending with slag shall conform to IS 269.
#      Amendment No. 1 (June 2018) changes only the Table 1 alkali note.
IS455_CL_5_SLAG_CONSTITUENT_PCT = (25.0, 70.0)
# [IS] Table 1 chemical (percent by mass, Max): insoluble 4.0, MgO 10.0, SO3 3.5,
#      sulphide sulphur 1.5, LOI 5.0, chloride 0.1 (0.05 prestressed).
IS455_TABLE1 = {"insoluble": 4.0, "mgo": 10.0, "so3": 3.5, "sulphide_s": 1.5, "loi": 5.0}
IS455_TABLE1_CHLORIDE_MAX = {"general": 0.1, "prestressed": 0.05}
# [IS] Table 2 physical: fineness >= 225 m2/kg; Le Chatelier <= 10 mm; autoclave <= 0.8 %
#      (aerated retest 5 mm / 0.6 %, Note 1); initial set >= 30 min, final <= 600 min;
#      strength >= 16 / 22 / 33 MPa at 72 h / 168 h / 672 h.
IS455_TABLE2 = {"blaine": 225.0, "initial_set": 30.0, "final_set": 600.0,
                "str": {"3d": 16.0, "7d": 22.0, "28d": 33.0}}
IS455_TABLE2_SOUNDNESS = {"le_chatelier_mm": 10.0, "autoclave_pct": 0.8}
IS455_TABLE2_NOTE1_AERATED = {"le_chatelier_mm": 5.0, "autoclave_pct": 0.6}


def check_psc(cert: dict) -> dict:
    """IS 455:2015 certificate check. Keys: declared_slag_pct, insoluble, mgo, so3,
    sulphide_s, loi, chloride_pct, blaine_m2_kg, initial_set_min, final_set_min,
    str_3d/7d/28d, le_chatelier_mm, autoclave_pct (+ '_aerated')."""
    res = {}
    x = cert.get("declared_slag_pct")
    lo, hi = IS455_CL_5_SLAG_CONSTITUENT_PCT
    res["declared_slag_pct"] = ("not_tested" if x is None else
                                "pass" if lo <= x <= hi else "fail")
    for k, lim in IS455_TABLE1.items():
        res[k] = _judge(cert.get(k), "max", lim)
    res["chloride_pct"] = _judge(cert.get("chloride_pct"), "max", IS455_TABLE1_CHLORIDE_MAX["general"])
    res["blaine_m2_kg"] = _judge(cert.get("blaine_m2_kg"), "min", IS455_TABLE2["blaine"])
    res["initial_set_min"] = _judge(cert.get("initial_set_min"), "min", IS455_TABLE2["initial_set"])
    res["final_set_min"] = _judge(cert.get("final_set_min"), "max", IS455_TABLE2["final_set"])
    for age, lim in IS455_TABLE2["str"].items():
        res[f"str_{age}"] = _judge(cert.get(f"str_{age}"), "min", lim)
    res.update({f"soundness_{k}": v for k, v in
                _soundness(cert, IS455_TABLE2_SOUNDNESS, IS455_TABLE2_NOTE1_AERATED).items()})
    fails = [k for k, v in res.items() if v.startswith("fail")]
    missing = [k for k, v in res.items() if v == "not_tested"]
    return {"cement_type": "PSC", "results": res, "fails": fails, "not_tested": missing,
            "conforms": False if fails else (None if missing else True),
            "source": "IS 455:2015 cl 5, Tables 1 and 2 (+ Amd 1)"}


def _portland_part(cement_kg_m3: float, cement_type: str,
                   ppc_fly_ash_declared_pct: Optional[float] = None,
                   psc_slag_declared_pct: Optional[float] = None) -> tuple:
    """[EI] The Portland-clinker part of the cement, worst case when undeclared.

    PPC: fly ash x = declared + 3 (IS 1489 cl 9.1) or the 35 percent upper limit.
    PSC: slag x = declared + 3 (IS 455 cl 5 homogeneity +/-3) or the 70 percent upper limit.
    """
    ct = str(cement_type).upper()
    if ct == "OPC":
        return cement_kg_m3, "OPC: all Portland"
    if ct == "PPC":
        x = (min(ppc_fly_ash_declared_pct + IS1489_1_CL_9_1_DECLARED_TOL_PCT,
                 IS1489_1_FLY_ASH_CONSTITUENT_PCT[1])
             if ppc_fly_ash_declared_pct is not None else IS1489_1_FLY_ASH_CONSTITUENT_PCT[1])
        return cement_kg_m3 * (1.0 - x / 100.0), f"PPC: Portland part at {x:.0f}% fly ash"
    if ct == "PSC":
        x = (min(psc_slag_declared_pct + 3.0, IS455_CL_5_SLAG_CONSTITUENT_PCT[1])
             if psc_slag_declared_pct is not None else IS455_CL_5_SLAG_CONSTITUENT_PCT[1])
        return cement_kg_m3 * (1.0 - x / 100.0), f"PSC: Portland part at {x:.0f}% slag"
    raise UnverifiedRule(f"Portland part of {ct} is not encoded")


def countable_ggbs(cement_kg_m3: float, ggbs_kg_m3: float, cement_type: str = "OPC",
                   ppc_fly_ash_declared_pct: Optional[float] = None,
                   psc_slag_declared_pct: Optional[float] = None) -> dict:
    """How much ADDED GGBS may count toward the IS 456 Table 5 minimum and w/c (Note 1).

    [IS] IS 456 Table 5 Note 1: additions count "as long as the maximum amounts taken
         into account do not exceed the limit of ... slag specified in ... IS 455".
    [IS] IS 455:2015 cl 5: slag not more than 70 percent by mass of PSC.
    [EI] Same reading as countable_fly_ash: the counted slag share of (Portland part +
         counted slag) may not exceed 70 percent, so counted G <= P x 0.70 / 0.30, where
         P is the Portland part of the cement (all of it for OPC; for PPC and PSC the
         clinker left after the declared or worst-case addition, see _portland_part).
         For PSC at the 70 percent upper limit nothing added counts.
    """
    ct = str(cement_type).upper()
    h = IS455_CL_5_SLAG_CONSTITUENT_PCT[1] / 100.0
    if ct == "PSC":
        x = (min(psc_slag_declared_pct + 3.0, h * 100.0)
             if psc_slag_declared_pct is not None else h * 100.0)
        cap = max(cement_kg_m3 * (h - x / 100.0) / (1.0 - h), 0.0)
        basis = f"PSC with {x:.0f}% slag already inside"
    else:
        p, basis = _portland_part(cement_kg_m3, ct, ppc_fly_ash_declared_pct)
        cap = p * h / (1.0 - h)
    c = min(ggbs_kg_m3, cap)
    return {"counted_kg": c, "counted_lo": c, "counted_hi": c, "decidable": True,
            "capped": ggbs_kg_m3 > cap + 1e-9, "cap_kg": cap, "basis": basis,
            "source": "IS 456 Table 5 Note 1 + IS 455:2015 cl 5"}


"""IS 456 : 2000 cl 5.1 (last paragraph), cl 5.2.1.1, cl 5.2.2."""

# [IS] cl 5.1, last paragraph -- "Other combinations of Portland cement with mineral
#      admixtures (see 5.2) of quality conforming with relevant Indian Standards laid
#      down may also be used in the manufacture of concrete provided that there are
#      satisfactory data on their suitability, such as performance tests on concrete
#      containing them."
# [IS] cl 5.2.1.1 -- "Fly ash conforming to Grade 1 of IS 3812 may be used as part
#      replacement of ordinary Portland cement provided uniform blending with cement is
#      ensured."
# [IS] cl 5.2.2 -- "Ground granulated blast furnace slag obtained by grinding granulated
#      blast furnace slag conforming to IS 12089 may be used as part replacement of
#      ordinary Portland cements provided uniform blending with cement is ensured."
# [IS] No clause of IS 456 or IS 10262 prints a numeric cap on the fly ash or GGBS share
#      for Section 2 concrete. IS 10262 cl 5.4.2: "The percentage of fly ash/GGBS to be
#      used has to be decided based on the project requirement and the quality of these
#      materials." IS 10262 Table 9 (15-30 / 25-50 %) is Section 3 GUIDANCE only.
# [NV] IS 16415 (composite cement, clinker + fly ash + slag) is NOT in the library.
#      NOT VERIFIED FROM PRIMARY STANDARD SOURCE -- it is not used.
IS456_CL_5_2_DIRECT_PERMISSIONS = {
    ("OPC", ("flyash",)): "IS 456 cl 5.2.1.1",
    ("OPC", ("ggbs",)):   "IS 456 cl 5.2.2",
}


def scm_combination(cement_type: str, fly_ash_kg_m3: float, ggbs_kg_m3: float,
                    other_scm_kg_m3: float = 0.0) -> tuple:
    """(cement type, sorted tuple of ADDED mineral admixtures) -- the key cl 5.1 judges."""
    added = tuple(sorted(n for n, v in (("flyash", fly_ash_kg_m3), ("ggbs", ggbs_kg_m3),
                                        ("other", other_scm_kg_m3)) if v and v > 0))
    return (str(cement_type).upper(), added)


# [IS] cl 5.2.1 -- "Pozzolanic materials conforming to relevant Indian Standards may be
#      used with the permission of the engineer-in-charge, provided uniform blending with
#      cement is ensured." Fly ash (cl 5.2.1.1) is a pozzolana; GGBS (cl 5.2.2) is not
#      under cl 5.2.1 and its clause has no permission phrase.
IS456_CL_5_2_1_PERMISSION_FOR = ("flyash",)


def counted_additions(cement_kg_m3: float, fly_ash_kg_m3: float, ggbs_kg_m3: float,
                      cement_type: str = "OPC", *,
                      ppc_fly_ash_declared_pct: Optional[float] = None,
                      psc_slag_declared_pct: Optional[float] = None,
                      suitability_evidence: Optional[str] = None) -> dict:
    """[IS] IS 456 Table 5 Note 1 -- the additions that may be taken into account with
    respect to cement content AND w/c: only 'if the suitability is established', and only
    within the IS 1489 (Part 1) / IS 455 limits (countable_fly_ash, countable_ggbs).
    [EI] 'Suitability established' is read as: suitability evidence recorded (the same
    record IS 456 cl 5.1 asks for). None recorded -> no addition counts (stricter)."""
    if (fly_ash_kg_m3 > 0 or ggbs_kg_m3 > 0) and not suitability_evidence:
        return {"flyash_kg": 0.0, "ggbs_kg": 0.0, "suitability_established": False,
                "basis": ("Table 5 Note 1: additions count only 'if the suitability is "
                          "established'; no evidence recorded, so none counted")}
    fa = (countable_fly_ash(cement_kg_m3, fly_ash_kg_m3, cement_type, ppc_fly_ash_declared_pct)
          if fly_ash_kg_m3 > 0 else {"counted_kg": 0.0, "basis": "no fly ash"})
    gg = (countable_ggbs(cement_kg_m3, ggbs_kg_m3, cement_type, ppc_fly_ash_declared_pct,
                         psc_slag_declared_pct)
          if ggbs_kg_m3 > 0 else {"counted_kg": 0.0, "basis": "no GGBS"})
    return {"flyash_kg": float(fa["counted_kg"]), "ggbs_kg": float(gg["counted_kg"]),
            "suitability_established": bool(suitability_evidence),
            "basis": f"fly ash: {fa['basis']}; GGBS: {gg['basis']}"}


def scm_combination_check(cement_type: str, fly_ash_kg_m3: float, ggbs_kg_m3: float,
                          other_scm_kg_m3: float = 0.0, *,
                          suitability_evidence: Optional[str] = None) -> dict:
    """IS 456 cl 5.1 / 5.2. Returns outcome 'pass' or 'override_required'.

    suitability_evidence: a short record of the performance tests on concrete made with
    THIS combination (for example 'plant Plant D, 256 batches with 28-day cubes').
    Supplying it is a human/plant decision; this function does not judge whether the
    data are 'satisfactory' -- it only refuses to proceed without any.
    """
    key = scm_combination(cement_type, fly_ash_kg_m3, ggbs_kg_m3, other_scm_kg_m3)
    ct, added = key
    if not added:
        return {"outcome": "pass", "combination": key, "clause": "IS 456 cl 5.1",
                "detail": f"{ct} with no mineral admixture added"}
    direct = IS456_CL_5_2_DIRECT_PERMISSIONS.get(key)
    if direct:
        return {"outcome": "pass", "combination": key, "clause": direct,
                "detail": f"{ct} + {'+'.join(added)}: permitted as part replacement of OPC ({direct})"
                          + ("; engineer-in-charge permission needed (cl 5.2.1)"
                             if set(added) & set(IS456_CL_5_2_1_PERMISSION_FOR) else "")}
    if suitability_evidence:
        return {"outcome": "pass", "combination": key, "clause": "IS 456 cl 5.1",
                "detail": (f"{ct} + {'+'.join(added)} is an 'other combination' [EI]; suitability "
                           f"data recorded: {suitability_evidence}")}
    return {"outcome": "override_required", "combination": key, "clause": "IS 456 cl 5.1",
            "detail": (f"{ct} + {'+'.join(added)} is an 'other combination' (IS 456 cl 5.1) [EI]. "
                       f"It may be used only with satisfactory data on its suitability, such "
                       f"as performance tests on concrete containing it. Record that evidence "
                       f"or remove the combination.")}


"""IS 10262:2019 cl 5.1, 5.8, 5.8.1, Annex A-10 Note, A-11, A-13, A-14, A-15;
IS 1199 (Part 1):2018 cl 6, 6.3, 6.4; IS 1199 (Part 2):2018 cl 4.3.2.1; IS 1199 (Part 3):2018
cl 4.2.1 + Table 1, 4.6.2; IS 1199 (Part 5):2018 cl 4.1.1, 7; IS 516 (Part 1/Sec 1):2021
cl 3.3, 3.4, 3.5.2, 3.6; IS 456:2000 cl 15.4; IS 2386 (Part 3):1963 cl 2, 5.5.1."""
import math

# ------------------------------------------------------------- IS 10262 cl 5.8
# [IS] cl 5.8 -- "The calculated mix proportions shall be checked by means of trial
#      batches. Workability of the trial mix No. 1 shall be measured. ... If the measured
#      workability of Trial Mix No. 1 is different from the stipulated value, the water
#      and/or admixture content shall be adjusted suitably. With this adjustment, the mix
#      proportion shall be recalculated keeping the free water-cement/water-cementitious
#      materials ratio at the pre-selected value, which will comprise Trial Mix No. 2. In
#      additional two more Trial Mixes No. 3 and 4 shall be made with the water content
#      same as Trial mix No. 2 and varying the free water-cement/cementitious materials
#      ratio by about +/- 10 percent of the pre-selected value, while satisfying the
#      workability requirements as well. Mix No. 2 to 4 normally provides sufficient
#      information, including the relationship between compressive strength and
#      water-cement ratio ... Additional field trials are recommended particularly for
#      workability requirements. The concrete for field trials shall be produced by
#      methods of actual concrete production."
IS10262_CL_5_8_WC_VARIATION = 0.10          # "about +/- 10 percent"
# [IS] Annex A-15 -- "Two more trials having variation of +/- 10 percent of water-cement
#      ratio in A-10 shall be carried out and a graph between three water-cement ratios
#      and their corresponding strengths shall be plotted ... However, durability
#      requirement shall be met."
# [EI] A-15's last sentence is applied to every trial: a +10 % trial that would exceed
#      the IS 456 Table 5 maximum free w/c is set AT that maximum instead, and says so.
# [IS] cl 5.8 -- Trials 3 and 4 use "the water content same as Trial mix No. 2". A trial
#      set computed before Trial 1 is cast assumes No. 1 needs no slump correction; if it
#      does, recompute 3 and 4 with the No. 2 water (layer0.trial_set(trial2_water_kg_m3=)).
# [EI] If the +10 % trial cannot move at least 2 percent away from the design w/cm, it
#      would duplicate Trial 2 and A-15's three-point graph could not be drawn; it is then
#      replaced by a -5 % trial, and says so.
IS10262_TRIAL_MIN_SEPARATION = 0.02          # [EI], see above
IS10262_TRIAL_FALLBACK_VARIATION = 0.05      # [EI], see above
# [IS] cl 5.8.1 -- the mix design report shall include:
IS10262_CL_5_8_1_REPORT = (
    "a) Period of testing (starting and ending date)",
    "b) Details of work/type of structure, if provided",
    "c) All the data provided for the mix design as per 4.1, and deviations from IS 456, if any",
    "d) Relevant test data of different materials for the purpose of mix proportioning",
    "e) Details of materials such as brand of cement, manufacturing date (week/year), "
    "percentage of pozzolana/slag, etc, as per manufacturers certificate; source of coarse "
    "and fine aggregates (if provided), etc",
    "f) Details of the trials conducted",
    "g) Recommended mix proportions",
)
# [IS] cl 5.1 -- "the relationship between strength and free water-cement ratio should
#      preferably be established for the materials actually to be used ... The final w/c
#      is arrived at, based on the results of all the trials".


def trial_wc_set(wc_design: float, wc_max: float) -> list:
    """IS 10262 cl 5.8 / A-15: three w/c values for Trial Mixes 2, 3, 4.

    Returns [(trial_no, w/c, note)]. Trial 3 = -10 %, Trial 4 = +10 %, capped at the IS 456
    Table 5 maximum ([EI] reading of A-15 'durability requirement shall be met')."""
    v = IS10262_CL_5_8_WC_VARIATION
    lo = wc_design * (1.0 - v)
    hi = wc_design * (1.0 + v)
    out = [(2, wc_design, "pre-selected w/c (Trial Mix No. 1, adjusted to No. 2 if the slump is off)"),
           (3, lo, "w/c -10 % (IS 10262 cl 5.8)")]
    if hi > wc_max + 1e-12:
        if wc_max < wc_design * (1.0 + IS10262_TRIAL_MIN_SEPARATION):
            w4 = wc_design * (1.0 - IS10262_TRIAL_FALLBACK_VARIATION)
            out.append((4, w4, f"w/c +10 % ({hi:.3f}) and even the Table 5 max {wc_max:.2f} sit within "
                               f"2 % of the design; replaced by w/c -5 % so three distinct points exist [EI]"))
        else:
            out.append((4, wc_max, f"w/c +10 % would be {hi:.3f} > IS 456 Table 5 max {wc_max:.2f}; "
                                   f"set at the maximum (A-15: durability requirement shall be met) [EI]"))
    else:
        out.append((4, hi, "w/c +10 % (IS 10262 cl 5.8)"))
    return out


# ------------------------------------------------------------- Annex A-10 Note / A-11
# [IS] A-10 NOTE -- "Aggregates shall be used in saturated surface dry condition. If
#      otherwise, when computing the requirement of mixing water, allowance shall be made
#      for the free (surface) moisture contributed by the fine and coarse aggregates. On
#      the other hand, if the aggregates are dry, the amount of mixing water shall be
#      increased by an amount equal to the moisture likely to be absorbed by the
#      aggregates. Necessary adjustments are also required to be made in mass of
#      aggregates. The surface water and percentage water absorption of aggregates shall
#      be determined according to IS 2386."
# [IS] A-11 -- dry mass = SSD mass / (1 + absorption/100); extra water = SSD - dry.


def aggregate_moisture_adjustment(ssd_kg: float, absorption_pct: float,
                                  moisture_pct: float) -> dict:
    """Mass to weigh and water correction for one aggregate, per IS 10262 A-10 / A-11.

    absorption_pct and moisture_pct are both percent of OVEN-DRY mass (IS 2386 Part 3
    cl 2 reports absorption that way). moisture_pct is the TOTAL moisture of the stock
    as weighed (0 for oven-dry). [NV] IS 2386 (Part 3) has no total-moisture method; it
    is the plant's oven-dry (or meter) reading. A surface moisture measured by IS 2386
    (Part 3) cl 5 is a percent of SSD mass -- convert it first with
    total_moisture_from_surface().

    [IS] A-11 is the special case moisture_pct = 0: weigh SSD/(1+a/100), add SSD - dry.
    [EI] General case, same mass balance: dry = SSD/(1+a/100); weigh dry x (1+m/100);
         water to ADD to the mixing water = SSD - weighed (negative = subtract the free
         surface water the aggregate brings in).
    """
    if ssd_kg < 0 or absorption_pct < 0 or moisture_pct < 0:
        raise ValueError("masses and percentages must be non-negative")
    dry = ssd_kg / (1.0 + absorption_pct / 100.0)
    weigh = dry * (1.0 + moisture_pct / 100.0)
    return {"weigh_kg": weigh, "dry_kg": dry, "water_adjust_kg": ssd_kg - weigh,
            "source": "IS 10262 Annex A-10 NOTE, A-11 (dry case printed; wet case [EI])"}


def total_moisture_from_surface(absorption_pct: float, surface_moisture_pct_of_ssd: float) -> float:
    """[IS] IS 2386 (Part 3) cl 5.5.1 gives surface moisture Ps as a percent of the SSD mass.
    [EI] Total moisture as a percent of dry mass, by the same mass balance:
         m = a + Ps x (1 + a/100)."""
    a, ps = float(absorption_pct), float(surface_moisture_pct_of_ssd)
    return a + ps * (1.0 + a / 100.0)


# [IS] A-13 -- "The total mass of coarse aggregate shall be divided into two fractions of
#      20 - 10 mm and 10 - 4.75 mm, in a suitable ratio, to satisfy the overall grading
#      requirements for 20 mm max size aggregate as per Table 7 of IS 383."
# [NV] IS 383 Table 7 (coarse grading) is not encoded in this layer. The split is
#      therefore an input (plant practice), and its Table 7 conformity is a lab check.
# [IS] A-14 -- "The slump shall be measured and the water content and dosage of
#      admixture shall be adjusted for achieving the required slump based on trial, if
#      required. The mix proportions shall be reworked for the actual water content and
#      checked for durability requirements."

# ------------------------------------------------------------- IS 1199 sampling / specimens
# [IS] IS 1199 (Part 1):2018 cl 6 -- "For samples to be used for strength test, a minimum
#      quantity of 0.02 m3 will be essential." cl 6.3 -- tests for slump, temperature and
#      air content are recommended to start within 5 min of obtaining the composite sample;
#      filling of strength specimens shall commence within 15 min. cl 6.4 -- temperature.
IS1199_1_CL_6_STRENGTH_SAMPLE_MIN_M3 = 0.02
IS1199_1_CL_6_FRESH_TESTS_START_MIN = 5       # recommended
IS1199_1_CL_6_SPECIMEN_FILL_START_MIN = 15
# [IS] IS 1199 (Part 2):2018 cl 4.3.2.1 slump mould: base 200 +/- 2, top 100 +/- 2,
#      height 300 +/- 2 mm.
IS1199_2_SLUMP_CONE_MM = (200.0, 100.0, 300.0)
# [IS] IS 1199 (Part 3):2018 cl 4.2.1 -- density container: smallest internal dimension
#      >= 4 x msa and >= 150 mm; volume >= 5 litre; 0.5 < dc/hc < 1.25; and "shall conform
#      to one of the sizes given in Table 1": up to 40 mm -- 250 mm dia x 280 mm high;
#      above 40 mm -- 350 x 285 mm. cl 4.6.2: volume of concrete per batch Vb = mT / rho.
IS1199_3_CONTAINER_MIN_L = 5.0
IS1199_3_CONTAINER_MIN_DIM_MM = 150.0
IS1199_3_TABLE1_MM = {"up_to_40": (250.0, 280.0), "above_40": (350.0, 285.0)}
# [IS] IS 1199 (Part 5):2018 cl 4.1.1 -- test specimens shall be 150 mm cubes; 100 mm
#      cubes may be used if the largest nominal aggregate size does not exceed 20 mm.
#      cl 7 -- in the mould at least 16 h and not longer than 3 days, at 27 +/- 3 deg C,
#      protected; then submerged in clean fresh water at 27 +/- 2 deg C (or a chamber at
#      27 +/- 2 deg C, RH >= 95 %) until just before testing.
IS1199_5_CUBE_MM = 150.0
IS1199_5_CL_7_MOULD_HOURS = (16, 72)
IS1199_5_CL_7_MOULD_TEMP_C = (27.0, 3.0)
IS1199_5_CL_7_CURE_TEMP_C = (27.0, 2.0)
# [IS] IS 516 (Part 1/Sec 1):2021 cl 3.3 -- recognized ages, "the most usual being 7 and
#      28 days"; 56 days, 90 days and one year recommended if greater ages are required.
#      cl 3.4 -- "At least three specimens shall be tested at each selected age."
#      cl 3.5.2 -- load increased continuously at 14 N/mm2/min.
#      cl 3.6 -- "Average of three values shall be taken as the representative of the
#      batch provided the individual variation is not more than +/- 15 percent of the
#      average. Otherwise repeat test shall be made, however if there is no further
#      sample, then the average of two closest values may be taken as the average
#      result." Strength expressed to the nearest 0.5 MPa.
# [IS] IS 456:2000 cl 15.4 -- for ACCEPTANCE samples: "Individual variation should not be
#      more than +/-15 percent of the average. If more, the test results of the sample are
#      invalid." Same +/-15 % band, different consequence (invalid vs repeat). Both are
#      reported by cube_set_result; which governs depends on whether the cubes are a lab
#      trial (IS 516) or an acceptance sample (IS 456) -- see the CONFLICT rule.
IS516_1_1_CL_3_3_AGES_DAYS = (7, 28)
IS516_1_1_CL_3_3_LATER_AGES_DAYS = (56, 90, 365)
IS516_1_1_CL_3_4_MIN_SPECIMENS = 3
IS516_1_1_CL_3_5_2_LOAD_RATE = 14.0           # N/mm2 per min
IS516_1_1_CL_3_6_SPREAD = 0.15
# [IS] IS 2386 (Part 3):1963 cl 2 -- specific gravity and water absorption;
#      cl 5 -- surface moisture in fine aggregate (displacement method).
IS2386_3_METHODS = {"specific_gravity_absorption": "IS 2386 (Part 3) cl 2",
                    "surface_moisture_fine": "IS 2386 (Part 3) cl 5"}


def cube_set_result(values_mpa: list) -> dict:
    """IS 516 (Part 1/Sec 1):2021 cl 3.4 + 3.6 -- one age of one batch."""
    v = [float(x) for x in values_mpa if x is not None]
    if len(v) < IS516_1_1_CL_3_4_MIN_SPECIMENS:
        return {"outcome": "not_verified", "result_mpa": None,
                "detail": f"{len(v)} specimens; cl 3.4 needs at least 3"}
    avg = sum(v) / len(v)
    spread_ok = all(abs(x - avg) <= IS516_1_1_CL_3_6_SPREAD * avg for x in v)
    if spread_ok:
        res, how = avg, "average of all"
    else:
        s = sorted(v)
        pairs = sorted(((abs(a - b), (a, b)) for i, a in enumerate(s) for b in s[i + 1:]))
        a, b = pairs[0][1]
        res, how = (a + b) / 2.0, "REPEAT TEST required (cl 3.6); if no further sample, mean of the two closest"
    return {"outcome": "pass" if spread_ok else "repeat_required",
            "result_mpa": round(res * 2.0) / 2.0, "individual_within_15pct": spread_ok,
            "is456_cl_15_4": "valid" if spread_ok else "INVALID as an acceptance sample",
            "detail": how, "source": "IS 516 (Part 1/Sec 1):2021 cl 3.4, 3.6; IS 456 cl 15.4"}


def slump_cone_volume_m3() -> float:
    d1, d2, h = (x / 1000.0 for x in IS1199_2_SLUMP_CONE_MM)
    r1, r2 = d1 / 2.0, d2 / 2.0
    return math.pi * h / 3.0 * (r1 * r1 + r1 * r2 + r2 * r2)


def trial_batch_volume(n_cubes: int, *, msa_mm: float, waste_frac: float = 0.25,
                       density_test: bool = True) -> dict:
    """Concrete needed for one trial batch: cubes + slump + density, plus a margin.

    [IS] cube 150 mm (IS 1199 Pt 5 cl 4.1.1); slump mould (IS 1199 Pt 2 cl 4.3.2.1);
         density container per IS 1199 Pt 3 Table 1 (cl 4.2.1); strength sample >= 0.02 m3
         (IS 1199 Pt 1 cl 6).
    [EI] the density concrete is not reused for cubes.
    [PC] waste_frac -- handling and remix margin; not an IS value.
    """
    cube = (IS1199_5_CUBE_MM / 1000.0) ** 3 * n_cubes
    strength_sample = max(cube, IS1199_1_CL_6_STRENGTH_SAMPLE_MIN_M3)
    dens = 0.0
    if density_test:
        d, h = IS1199_3_TABLE1_MM["up_to_40" if float(msa_mm) <= 40.0 else "above_40"]
        dens = math.pi * (d / 2000.0) ** 2 * (h / 1000.0)
    net = strength_sample + slump_cone_volume_m3() + dens
    gross = net * (1.0 + waste_frac)
    return {"cubes_m3": cube, "strength_sample_m3": strength_sample,
            "slump_m3": slump_cone_volume_m3(), "density_m3": dens, "net_m3": net,
            "batch_m3": math.ceil(gross * 200.0) / 200.0,     # round UP to 0.005 m3
            "waste_frac_pc": waste_frac}


REGISTRY: list[Rule] = [
    # --- IS 456 : 2000
    Rule("IS 456:2000", "Table 5",   "min cement / max free w/c / min grade by exposure",
         Status.VERIFIED, Confidence.PRINT_CLEAN,
         (CAVEAT_TABLE5_NOTE1, "All 30 cells re-read from a 400 dpi page render (v3).")),
    Rule("IS 456:2000", "Table 6, cl 8.2.4.1", "cement adjustment for msa", Status.VERIFIED),
    Rule("IS 456:2000", "cl 8.2.4.2", "max CEMENT 450 kg/m3 excluding fly ash and GGBS",
         Status.VERIFIED,
         caveats=("[EI] 'should not ... unless special consideration'. Implemented as a "
                  "constraint with a documented override, not a silent reject.",)),
    Rule("IS 456:2000", "cl 6.1.1",  "characteristic strength = 5 percent fractile", Status.VERIFIED),
    Rule("IS 456:2000", "cl 6.1.2",  "minimum grade per Table 5", Status.VERIFIED),
    Rule("IS 456:2000", "cl 6.1.3",  "lower grades permitted for plain/lean/simple/temporary",
         Status.VERIFIED),
    Rule("IS 456:2000", "cl 9.1.1",  "design mix vs nominal mix", Status.VERIFIED),
    Rule("IS 456:2000", "cl 9.2.2",  "target mean = fck + 1.65 S", Status.CONFLICT,
         caveats=("Conflicts with IS 10262 cl 4.2. Neither binds; the resolution is a "
                  "PROJECT_CONSTRAINT -- take the maximum.",)),
    # --- IS 10262 : 2019 Section 2
    Rule("IS 10262:2019", "Table 1, cl 4.2",     "value of X", Status.VERIFIED),
    Rule("IS 10262:2019", "Table 2, cl 4.2.1.3", "assumed standard deviation", Status.VERIFIED),
    Rule("IS 10262:2019", "cl 4.2.1.1",          "established S needs >= 30 results", Status.VERIFIED),
    Rule("IS 10262:2019", "cl 4.2.1.2.1 / 4.2.1.2.2", "S formula (n-1); two groups pooled, each >= 10, total >= 30",
         Status.VERIFIED),
    Rule("IS 10262:2019", "cl 4.2.1.1 (b), (c)", "S restarts after significant change; monthly check S < design S",
         Status.VERIFIED),
    Rule("IS 10262:2019", "Table 3, cl 5.2",     "entrapped air", Status.VERIFIED),
    Rule("IS 10262:2019", "Table 4, cl 5.3",     "water content, ORDINARY grades", Status.VERIFIED),
    Rule("IS 10262:2019", "Table 5, cl 5.5",     "CA volume by zone at w/c 0.50", Status.VERIFIED),
    Rule("IS 10262:2019", "cl 4.2",              "target mean = max(fck+1.65S, fck+X)",
         Status.CONFLICT, caveats=("See IS 456 cl 9.2.2.",)),
    # --- IS 10262 : 2019 Section 3
    Rule("IS 10262:2019", "Table 6, cl 6.2.3",   "entrapped air, HIGH STRENGTH", Status.VERIFIED),
    Rule("IS 10262:2019", "Table 7, cl 6.2.4",   "water content, HIGH STRENGTH", Status.VERIFIED),
    Rule("IS 10262:2019", "Table 8, cl 6.2.5",   "RECOMMENDED w/cm, HIGH STRENGTH (seed value)",
         Status.GUIDANCE),
    Rule("IS 10262:2019", "Table 9, cl 6.2.6",   "RECOMMENDED SCM dosages, HIGH STRENGTH",
         Status.GUIDANCE),
    Rule("IS 10262:2019", "Table 10, cl 6.2.7",  "CA volume at w/cm 0.30, HIGH STRENGTH", Status.VERIFIED),
    # --- IS 383 : 2016
    Rule("IS 383:2016", "Table 2 row iii, cl 5.2.1", "materials finer than 75 micron",
         Status.VERIFIED),
    Rule("IS 383:2016", "Table 9, cl 6.3",       "fine aggregate grading zones", Status.VERIFIED),
    Rule("IS 383:2016", "Table 9 Note 1",        "crushed sand 150 micron limit 20 percent",
         Status.VERIFIED),
    IS383_ZONE_IV_IN_RC,
    Rule("IS 383:2016", "cl 6.3",                "grading tolerance: 5 / cumulative 10 / exclusions",
         Status.VERIFIED),
    # --- IS 9103 : 1999
    IS9103_DOSAGE_RULE,
    # --- IS 456 : 2000 -- sampling, acceptance, workability, nominal mix (as amended)
    Rule("IS 456:2000", "cl 15.2.2",  "minimum sampling frequency by quantity", Status.VERIFIED,
         caveats=("[IS] NOTE: at least one sample per shift; RMC frequency MAY be agreed.",
                  "[EI] non-integer quantities in a band gap go to the higher band.")),
    Rule("IS 456:2000", "cl 15.3 (Amd 1)", "three specimens per sample", Status.VERIFIED),
    Rule("IS 456:2000", "cl 15.4",    "sample result = mean of 3; any specimen > +/-15 % -> invalid",
         Status.VERIFIED),
    Rule("IS 456:2000", "Table 8",    "assumed standard deviation (M10-M50) for Table 11",
         Status.VERIFIED),
    Rule("IS 456:2000", "cl 16.1 + Table 11 (Amd 1)",
         "acceptance: non-overlapping groups of 4 (col 2) and individual (col 3)",
         Status.VERIFIED,
         caveats=("[EI] 'rounded off to nearest 0.5' -- ties round up.",)),
    Rule("IS 456:2000", "cl 16.3",    "4 results represent <= 60 m3 if rate unspecified",
         Status.VERIFIED),
    Rule("IS 456:2000", "cl 7.1 (Amd 1 table)", "SUGGESTED slump by placing condition",
         Status.GUIDANCE),
    Rule("IS 456:2000", "cl 7.1.1",   "SUGGESTED compacting factor 0.75-0.80 (very low)",
         Status.GUIDANCE),
    Rule("IS 456:2000", "cl 9.3 + Table 9", "nominal mix proportions, M20 or lower",
         Status.VERIFIED),
    Rule("IS 456:2000", "cl 10.2.2",  "batching accuracy: cement 2 %, agg/admix/water 3 %",
         Status.VERIFIED),
    Rule("IS 456:2000", "cl 5.2.1.2 NOTE (Amd 2)", "silica fume USUALLY 5-10 % of cement",
         Status.GUIDANCE),
    # --- IS 4926 : 2003
    Rule("IS 4926:2003", "cl 6.2.1",  "slump tolerance: min(25 mm, 1/3 specified)", Status.VERIFIED),
    Rule("IS 4926:2003", "cl 6.2.1",  "compacting factor tolerance 0.03/0.04/0.05", Status.VERIFIED),
    Rule("IS 4926:2003", "cl 6.2.1",  "flow tolerance -- agreed between the parties",
         Status.UNVERIFIED,
         caveats=("The code prints no value on purpose. Bind only as a PROJECT_CONSTRAINT "
                  "recording the supplier-purchaser agreement.",)),
    Rule("IS 4926:2003", "cl 5.2.2.1 + 5.2.2.2", "discharge within 2 h of loading",
         Status.VERIFIED,
         caveats=("[IS] longer MAY be permitted with retarder, cool humid weather or "
                  "chilled concrete -> OVERRIDE_REQUIRED, not PASS.",)),
    Rule("IS 4926:2003", "cl 5.2.1.1", "purchaser SHOULD discharge within 30 min of arrival",
         Status.GUIDANCE),
    Rule("IS 4926:2003", "cl 6.3.2",  "producer sampling: 1 per 50 m3 or 50 batches",
         Status.GUIDANCE,
         caveats=("'Unless otherwise agreed ... should be'. The binding sampling rule is "
                  "IS 456 cl 15.2.2.",)),
    Rule("IS 4926:2003", "cl 6.3.2",  "28-day compressive strength alone decides acceptance",
         Status.VERIFIED),
    Rule("IS 4926:2003", "Annex E E-1(a)", "batching tolerance: cement+mineral 2 %, others 3 %",
         Status.VERIFIED,
         caveats=("[EI] equipment accuracy applied to recorded batch weights.",)),
    # --- IS 3812 (Part 1) : 2013
    Rule("IS 3812 (Part 1):2013", "cl 3.2 / 3.9", "siliceous < 10 % reactive CaO <= calcareous",
         Status.VERIFIED),
    Rule("IS 3812 (Part 1):2013", "Table 1", "fly ash chemical requirements", Status.VERIFIED,
         caveats=("Reactive silica is tested only if agreed (footnote 1).",)),
    Rule("IS 3812 (Part 1):2013", "Table 2", "fly ash physical requirements", Status.VERIFIED,
         caveats=("45 micron residue is an optional test (footnote 1).",)),
    Rule("IS 3812 (Part 1):2013", "cl 6.2", "moisture <= 2.0 % when supplied dry", Status.VERIFIED),
    Rule("IS 3812 (Part 1):2013", "cl 7.2",
         "uniformity: Blaine, 45 micron residue, lime reactivity within 15 % of last 10",
         Status.VERIFIED,
         caveats=("[EI] properties not measured in a preceding sample are skipped in "
                  "that property's average.",)),
    # --- IS 16714 : 2018
    Rule("IS 16714:2018", "Table 1", "GGBS chemical requirements incl. ratios viii-x",
         Status.VERIFIED,
         caveats=("[EI] row viii printed 'AlO3', read as Al2O3.",
                  "Ratio x applies only when MnO > 2.5 %.")),
    Rule("IS 16714:2018", "Table 2", "GGBS fineness and slag activity index", Status.VERIFIED),
    Rule("IS 16714:2018", "cl 4 / 5.2 / 5.3", "additives <= 1 %, moisture <= 1 %, glass >= 85 %",
         Status.VERIFIED),
    # --- IS 1489 (Part 1) : 1991
    Rule("IS 1489 (Part 1):1991", "cl 5 (Amd 3)", "fly ash constituent 15-35 % of PPC",
         Status.VERIFIED,
         caveats=("Used only to cap fly ash counted toward IS 456 Table 5 minimum "
                  "([EI] cap = cement x 35/65).",)),
    # --- IS 456 : 2000 clause 8 durability (v3, read from page renders)
    Rule("IS 456:2000", "Table 4, cl 8.2.2.4", "sulphate classes and cement-type limits",
         Status.VERIFIED,
         caveats=("Note 4: cement contents are 'the minimum recommended'.",
                  "[EI] boundary values go to the severer class; additions not counted.")),
    Rule("IS 456:2000", "Table 7, cl 8.2.5.2", "max acid-soluble chloride 0.4 / 0.6 / 3.0 kg/m3",
         Status.VERIFIED),
    Rule("IS 456:2000", "cl 8.2.5.3", "water-soluble SO3 <= 4 % of cement ('should')",
         Status.VERIFIED, caveats=("'should not exceed' -> OVERRIDE_REQUIRED, not FAIL [EI].",)),
    Rule("IS 456:2000", "cl 8.2.8", "sea water: min M20 plain, M30 reinforced", Status.VERIFIED),
    Rule("IS 456:2000", "cl 8.2.2.3", "freeze-thaw entrained air 5+/-1 (20 mm), 4+/-1 (40 mm)",
         Status.GUIDANCE),
    Rule("IS 456:2000", "cl 8.2.5.4", "AAR precautions incl. low-alkali OPC <= 0.6 % Na2Oeq",
         Status.GUIDANCE),
    Rule("IS 456:2000", "cl 5.1", "permitted cement types and their standards", Status.VERIFIED),
    # --- IS 10262 : 2019 terminology and references
    Rule("IS 10262:2019", "cl 2", "normative references (mapped to library)", Status.VERIFIED),
    Rule("IS 10262:2019", "cl 3.1, 3.2, 5.1.2", "w/c and w/cm definitions; w/cm per IS 456 Table 5",
         Status.VERIFIED),
    Rule("IS 10262:2019", "cl 5.1 NOTE", "count admixture water near the durability w/c limit",
         Status.VERIFIED),
    # --- IS 1489 (Part 1) : PPC conformity and soundness
    Rule("IS 1489 (Part 1):1991", "cl 7.2.1, 7.2.1.1", "PPC soundness 10 mm / 0.8 %; aerated 5 / 0.6",
         Status.VERIFIED),
    Rule("IS 1489 (Part 1):1991", "Table 1, cl 7.1-7.5", "PPC chemical and physical requirements",
         Status.VERIFIED),
    Rule("IS 1489 (Part 1):1991", "cl 9.1", "declared fly ash %, +/-3 %", Status.VERIFIED,
         caveats=("[EI] the gate uses declared + 3 as the worst case.",)),
    Rule("IS 1489 (Part 1):1991", "cl 9.2 Notes (Amd 4)", "chloride in cement <= 0.1 % (0.05 prestressed)",
         Status.VERIFIED),
    Rule("IS 1489 (Part 1)", "edition", "1991 + Amd 1-5 = the '2015' edition IS 10262 cites?",
         Status.UNVERIFIED,
         caveats=("[NV] IS 10262 cl 2 cites IS 1489 (Part 1):2015 '(third revision)'. The "
                  "folder copy is the 1991 Third Revision. Confirm against a BIS catalogue.",)),
    # --- IS 383 : 2016 aggregate quality
    Rule("IS 383:2016", "cl 5.4.1-5.4.3", "crushing / impact / abrasion; M65+ <= 22 %", Status.VERIFIED),
    Rule("IS 383:2016", "cl 5.5.1", "aggregate soundness: frost only, limits by agreement",
         Status.UNVERIFIED,
         caveats=("The code prints no binding number; the NOTE values 10/15/12/18 % are a "
                  "'general guide'. Bind only the agreed value, as a PROJECT_CONSTRAINT.",)),
    Rule("IS 383:2016", "cl 5.5.2", "slag: iron unsoundness <= 1 %, expansion <= 2.0 %",
         Status.VERIFIED),
    # --- IS 1199 (Part 2) : 2018 workability test validity
    Rule("IS 1199 (Part 2):2018", "cl 4.3.1, 4.3.4", "slump test valid 10-210 mm, true slump only",
         Status.VERIFIED),
    Rule("IS 1199 (Part 2):2018", "cl 4.7.1", "flow table valid 340-620 mm", Status.VERIFIED),
    Rule("IS 1199 (Part 2):2018", "cl 4.1", "tests not applicable above 40 mm msa", Status.VERIFIED),
    # --- IS 9103 : 1999 admixture declarations
    Rule("IS 9103:1999", "cl 10.2, cl 1.3", "manufacturer declares dosage range and chloride",
         Status.VERIFIED),
    # --- v4: IS 455 and IS 269 now read
    Rule("IS 455:2015", "cl 5", "slag constituent 25-70 % of PSC -> GGBS counting limit",
         Status.VERIFIED,
         caveats=("[EI] counted GGBS <= Portland part x 0.70/0.30 (countable_ggbs).",)),
    Rule("IS 455:2015", "Tables 1, 2", "PSC chemical and physical requirements", Status.VERIFIED),
    Rule("IS 269:2015", "Tables 2, 3", "OPC 33/43/43S/53/53S chemical, physical, soundness, strength",
         Status.VERIFIED),
    Rule("IS 269:2015", "cl 11.1 (f), (g)", "cement older than 3 months to be tested before use",
         Status.VERIFIED, caveats=("[EI] read from the mandatory bag marking text.",)),
    # --- v4: combinations of cement and mineral admixtures
    Rule("IS 456:2000", "cl 5.2.1.1, cl 5.2.2", "fly ash / GGBS as part replacement of OPC",
         Status.VERIFIED),
    Rule("IS 456:2000", "cl 5.1 (last para)", "other combinations need satisfactory suitability data",
         Status.VERIFIED,
         caveats=("[EI] Outcome OVERRIDE_REQUIRED until the evidence is recorded; this layer "
                  "does not judge whether the data are 'satisfactory'.",)),
    Rule("IS 16415", "-", "composite cement (clinker + fly ash + slag) composition", Status.UNVERIFIED,
         caveats=("[NV] Not in the library. NOT VERIFIED FROM PRIMARY STANDARD SOURCE. Not used.",)),
    Rule("IS 10262:2019", "cl 5.1.1 NOTE", "admixture water counted in w/c at the upper limit",
         Status.VERIFIED,
         caveats=("[EI] applied to every mix, which is never less strict than the clause.",)),
    # --- v4: trial mixes and laboratory tests
    Rule("IS 10262:2019", "cl 5.8, Annex A-14, A-15", "trial mixes 1-4; w/c +/- 10 % at the same water",
         Status.VERIFIED,
         caveats=("[EI] A +10 % trial above the Table 5 maximum is set at the maximum (A-15).",)),
    Rule("IS 10262:2019", "cl 5.8.1", "mix design report contents a) to g)", Status.VERIFIED),
    Rule("IS 10262:2019", "Annex A-10 NOTE, A-11", "SSD basis; moisture / absorption correction",
         Status.VERIFIED, caveats=("[EI] wet-aggregate case by the same mass balance.",)),
    Rule("IS 10262:2019", "Annex A-13", "20-10 / 10-4.75 coarse split to meet IS 383 Table 7",
         Status.VERIFIED, caveats=("[NV] IS 383 Table 7 itself is not encoded.",)),
    Rule("IS 1199 (Part 1):2018", "cl 6, 6.3, 6.4", "strength sample >= 0.02 m3; test timing; temperature",
         Status.VERIFIED),
    Rule("IS 1199 (Part 2):2018", "cl 4.3.2.1", "slump mould 200 / 100 / 300 mm", Status.VERIFIED),
    Rule("IS 1199 (Part 3):2018", "cl 4.2.1 + Table 1, 4.6.2", "density container 250 x 280 mm (<= 40 mm); volume per batch",
         Status.VERIFIED),
    Rule("IS 456:2000", "cl 5.2.1", "pozzolanas (fly ash) with the permission of the engineer-in-charge",
         Status.VERIFIED, caveats=("Reported NOT_VERIFIED (non-hard) until the permission is recorded.",)),
    Rule("IS 456:2000", "Table 5 Note 1", "additions counted only 'if the suitability is established'",
         Status.VERIFIED, caveats=("[EI] no suitability evidence recorded -> no addition counted.",)),
    Rule("IS 456:2000 / IS 516 (Part 1/Sec 1):2021", "cl 15.4 / cl 3.6",
         "+/-15 % cube spread: 'invalid' (IS 456) vs 'repeat, or two closest' (IS 516)", Status.CONFLICT,
         caveats=("[PC] lab trial cubes are reported per IS 516 cl 3.6; any sample used for ACCEPTANCE "
                  "follows IS 456 cl 15.4. cube_set_result reports both.",)),
    Rule("IS 1199 (Part 5):2018", "cl 4.1.1, cl 7", "150 mm cubes; mould 16 h-3 d at 27+/-3; water 27+/-2",
         Status.VERIFIED),
    Rule("IS 516 (Part 1/Sec 1):2021", "cl 3.3, 3.4, 3.5.2, 3.6",
         "ages 7/28 d; >= 3 specimens; 14 N/mm2/min; +/-15 % rule; nearest 0.5 MPa", Status.VERIFIED),
    Rule("IS 2386 (Part 3):1963", "cl 2, cl 5.5.1", "SG and absorption (% dry); surface moisture of fine aggregate (% SSD)",
         Status.VERIFIED, caveats=("[NV] no total-moisture method in Part 3; total moisture is the plant's reading.",)),
    Rule("PROJECT", "-", "volume closure tolerance 0.01 m3 on the absolute-volume sum",
         Status.PROJECT_CONSTRAINT,
         caveats=("[PC] IS 10262 cl 5.7 gives the METHOD (aggregate volume = unit volume minus "
                  "the other absolute volumes, entrapped air excluded); it prints no tolerance.",)),
    Rule("PROJECT", "-", "trial batch margin over the IS 1199 test quantities", Status.PROJECT_CONSTRAINT,
         caveats=("[PC] 25 % by default; see trial_batch_volume().",)),
    # --- project resolutions
    Rule("PROJECT", "-", "target mean strength = max of the two clause formulae",
         Status.PROJECT_CONSTRAINT,
         caveats=("[PC] Resolves the declared IS 456 cl 9.2.2 / IS 10262 cl 4.2 conflict.",)),
]


def unresolved() -> list[Rule]:
    """Everything that SHOULD bind but cannot yet: unverified, conflicting, or resting on
    a reconstructed glyph. GUIDANCE is excluded -- it is non-binding by design."""
    return [r for r in REGISTRY
            if _v(r.status) != "guidance"
            and (_v(r.status) not in BINDING or _v(r.confidence) == "ocr_reconstructed")]


def registry_report() -> None:
    from collections import Counter
    print(f"{len(REGISTRY)} rules: " +
          ", ".join(f"{k}={v}" for k, v in Counter(_v(r.status) for r in REGISTRY).items()))
    print("\nCannot bind, or binds only with allow_ocr=True:")
    for r in unresolved():
        flag = "OCR" if _v(r.confidence) == "ocr_reconstructed" else _v(r.status).upper()
        print(f"  [{flag:10s}] {r.standard:22s} {r.clause:28s} {r.subject}")
    guide = [r for r in REGISTRY if _v(r.status) == "guidance"]
    print(f"\nGuidance -- informs, never binds ({len(guide)}):")
    for r in guide:
        print(f"  [GUIDANCE  ] {r.standard:22s} {r.clause:28s} {r.subject}")


class Outcome(Enum):
    PASS              = "pass"
    FAIL              = "fail"
    NOT_VERIFIED      = "not_verified"
    OVERRIDE_REQUIRED = "override_required"
    GUIDANCE          = "guidance"          # informs; never fails a mix


# Checks whose NOT_VERIFIED means 'the mix itself could not be judged'. An optimiser must
# reject such a mix (fail-safe). Material-certificate checks are reported separately.
HARD_MIX_CHECKS = frozenset({"maximum cement", "minimum binder", "maximum free w/c",
                             "minimum grade", "volume closure", "sulphate (Table 4)",
                             "sea water minimum grade", "mineral admixture combination"})

# [PC] Numerical tolerance on the absolute-volume sum. IS 10262 cl 5.7 gives the method
#      and no tolerance; see the PROJECT rule in REGISTRY.
VOLUME_CLOSURE_TOL_M3 = 0.01


def compliance_gate(*, cement_kg_m3: float, fly_ash_kg_m3: float, ggbs_kg_m3: float,
                    other_scm_kg_m3: float, grade: str, exposure: Exposure, use: UseClass,
                    msa_mm: int,
                    free_water_kg_m3: Optional[float] = None,
                    free_wc: Optional[float] = None,
                    cement_type: str = "OPC",
                    ppc_fly_ash_declared_pct: Optional[float] = None,
                    sulphate_class_: Optional[int] = None,
                    chloride_kg_m3: Optional[float] = None,
                    chloride_category: Optional[str] = None,
                    so3_pct_of_cement_: Optional[float] = None,
                    sea_water: bool = False,
                    freeze_thaw: bool = False,
                    volume_closure_m3: Optional[float] = None,
                    admixture_kg_m3: Optional[float] = None,
                    admixture_dosage_range_pct: Optional[tuple] = None,
                    scm_pct_of_binder: Optional[dict] = None,
                    special_consideration_recorded: bool = False,
                    admixture_water_kg_m3: Optional[float] = None,
                    combination_suitability_evidence: Optional[str] = None,
                    psc_slag_declared_pct: Optional[float] = None,
                    engineer_permission_recorded: bool = False,
                    allow_ocr: bool = False) -> dict:
    """Every durability check on one mix. Returns a verdict per clause.

    Give FREE WATER in kg/m3 (free_water_kg_m3). The gate then forms w/c itself over the
    binder that IS 456 Table 5 Note 1 lets it count. A bare ratio (free_wc) is accepted
    only for OPC with no additions, where the denominator cannot be ambiguous.
    """
    checks = []
    ct = str(cement_type).upper()
    cementitious = cement_kg_m3 + fly_ash_kg_m3 + ggbs_kg_m3 + other_scm_kg_m3
    domain = route_domain(grade)
    use_k = _v(use)

    # 1 -- maximum CEMENT. IS 456 cl 8.2.4.2. Excludes fly ash and GGBS.
    note_ppc = ""
    if ct == "PPC":
        note_ppc = (" [EI] PPC counted whole as cement (stricter reading)." +
                    (f" Clinker part ~{cement_kg_m3 * (1 - ppc_fly_ash_declared_pct / 100):.0f}."
                     if ppc_fly_ash_declared_pct is not None else ""))
    if cement_kg_m3 <= IS456_CL_8_2_4_2_MAX_CEMENT:
        checks.append(("IS 456 cl 8.2.4.2", "maximum cement", Outcome.PASS,
                       f"cement {cement_kg_m3:.0f} <= {IS456_CL_8_2_4_2_MAX_CEMENT:.0f} kg/m3 "
                       f"(fly ash and GGBS excluded).{note_ppc}"))
    elif special_consideration_recorded:
        checks.append(("IS 456 cl 8.2.4.2", "maximum cement", Outcome.PASS,
                       f"cement {cement_kg_m3:.0f} exceeds 450 kg/m3; special "
                       f"consideration recorded, as the clause contemplates"))
    else:
        checks.append(("IS 456 cl 8.2.4.2", "maximum cement", Outcome.OVERRIDE_REQUIRED,
                       f"cement {cement_kg_m3:.0f} > 450 kg/m3. The clause says 'should "
                       f"not be used UNLESS special consideration has been given in "
                       f"design'. Record it, or reduce the cement.{note_ppc}"))

    # counted binder, IS 456 Table 5 Note 1 + IS 1489 (Part 1)
    try:
        fa = countable_fly_ash(cement_kg_m3, fly_ash_kg_m3, ct, ppc_fly_ash_declared_pct)
    except UnverifiedRule as e:
        fa = None
        fa_err = str(e)
    # [IS] IS 456 Table 5 Note 1 -- additions count only 'if the suitability is
    #      established', and only within IS 1489 (Part 1) / IS 455:2015 cl 5.
    try:
        ca_ = counted_additions(cement_kg_m3, fly_ash_kg_m3, ggbs_kg_m3, ct,
                                ppc_fly_ash_declared_pct=ppc_fly_ash_declared_pct,
                                psc_slag_declared_pct=psc_slag_declared_pct,
                                suitability_evidence=combination_suitability_evidence)
        gg_counted = ca_["ggbs_kg"]
        if fa is not None:
            fa = {**fa, "counted_lo": ca_["flyash_kg"], "counted_hi": ca_["flyash_kg"],
                  "basis": fa["basis"] + ("" if ca_["suitability_established"]
                                          else "; NOT counted: suitability not established (Note 1)")}
    except UnverifiedRule as e:
        gg_counted = 0.0
    # [EI] other SCM (silica fume, metakaolin) has no Note 1 limit to count against;
    #      it is NOT counted. Stricter than counting it.
    base = cement_kg_m3 + gg_counted

    # [IS] IS 456 cl 5.1 / 5.2 -- is this cement + addition combination permitted?
    cmb = scm_combination_check(ct, fly_ash_kg_m3, ggbs_kg_m3, other_scm_kg_m3,
                                suitability_evidence=combination_suitability_evidence)
    checks.append((cmb["clause"], "mineral admixture combination",
                   Outcome.PASS if cmb["outcome"] == "pass" else Outcome.OVERRIDE_REQUIRED,
                   cmb["detail"]))
    # [IS] cl 5.2.1 -- pozzolanas with the permission of the engineer-in-charge.
    if fly_ash_kg_m3 > 0:
        checks.append(("IS 456 cl 5.2.1", "engineer-in-charge permission (pozzolana)",
                       Outcome.PASS if engineer_permission_recorded else Outcome.NOT_VERIFIED,
                       "recorded" if engineer_permission_recorded else
                       "fly ash may be used 'with the permission of the engineer-in-charge' -- "
                       "record it before casting"))

    # [IS] IS 10262 cl 5.1.1 NOTE -- admixture water joins the free water for the w/c check.
    w_adm = float(admixture_water_kg_m3 or 0.0)
    if free_water_kg_m3 is not None:
        free_water_kg_m3 = free_water_kg_m3 + w_adm

    # 2, 3, 4 -- Table 5 durability limits.
    try:
        lim = table5_lookup(exposure, use, msa_mm, allow_ocr=allow_ocr)
    except OcrUnconfirmed as e:
        checks.append(("IS 456 Table 5", "minimum binder", Outcome.NOT_VERIFIED, str(e)))
        lim = None
    if lim is not None:
        mn = lim["min_cement_kg_m3"]
        if fa is None:
            checks.append(("IS 456 Table 5 + Note 1", "minimum binder", Outcome.NOT_VERIFIED, fa_err))
            checks.append(("IS 456 Table 5 + Note 1", "maximum free w/c", Outcome.NOT_VERIFIED, fa_err))
        else:
            lo_b, hi_b = base + fa["counted_lo"], base + fa["counted_hi"]
            if lo_b >= mn:
                oc = Outcome.PASS
            elif hi_b < mn:
                oc = Outcome.FAIL
            else:
                oc = Outcome.NOT_VERIFIED
            checks.append(("IS 456 Table 5 + Table 6 + Note 1", "minimum binder", oc,
                           f"counted binder {lo_b:.0f}" + (f"-{hi_b:.0f}" if hi_b > lo_b + 0.5 else "")
                           + f" vs min {mn:.0f} kg/m3 (fly ash: {fa['basis']}"
                           + (f"; GGBS counted {gg_counted:.0f} of {ggbs_kg_m3:.0f}" if ggbs_kg_m3 else "")
                           + f"). CAVEAT: {CAVEAT_TABLE5_NOTE1}"))
            # w/c over the counted binder
            wmax = lim["max_free_wc"]
            additions = fly_ash_kg_m3 + ggbs_kg_m3 + other_scm_kg_m3
            if free_water_kg_m3 is not None:
                wc_hi, wc_lo = free_water_kg_m3 / lo_b, free_water_kg_m3 / hi_b
                if wc_hi <= wmax:
                    oc = Outcome.PASS
                elif wc_lo > wmax:
                    oc = Outcome.FAIL
                else:
                    oc = Outcome.NOT_VERIFIED
                checks.append(("IS 456 Table 5 + Note 1; IS 10262 cl 5.1.1 NOTE, 5.1.2", "maximum free w/c", oc,
                               f"free water {free_water_kg_m3:.1f}"
                               + (f" (incl. {w_adm:.1f} from admixture)" if w_adm else "")
                               + f" / counted binder -> w/c "
                               f"{wc_hi:.3f}" + (f" (best case {wc_lo:.3f})" if wc_hi > wc_lo + 1e-6 else "")
                               + f" vs max {wmax:.2f}"))
            elif free_wc is not None and additions == 0 and ct == "OPC":
                checks.append(("IS 456 Table 5", "maximum free w/c",
                               Outcome.PASS if free_wc <= wmax else Outcome.FAIL,
                               f"w/c {free_wc:.3f} vs max {wmax:.2f} (OPC, no additions)"))
            else:
                checks.append(("IS 456 Table 5 + Note 1", "maximum free w/c", Outcome.NOT_VERIFIED,
                               "give free_water_kg_m3: with PPC or additions a bare ratio hides "
                               "how much fly ash / GGBS was counted in the denominator"))
        if lim["min_grade"] is None:
            checks.append(("IS 456 cl 6.1.3", "minimum grade", Outcome.PASS,
                           lim["min_grade_disapplied_by"] or
                           "no minimum grade printed (Table 5 Note 2, plain/mild)"))
        else:
            ok = grade_to_fck(grade) >= grade_to_fck(lim["min_grade"])
            checks.append(("IS 456 cl 6.1.2", "minimum grade",
                           Outcome.PASS if ok else Outcome.FAIL,
                           f"{grade} vs minimum {lim['min_grade']} for "
                           f"{_v(exposure)}/{use_k}"))

    # 5 -- sulphate attack. IS 456 Table 4, only if a class is given.
    if sulphate_class_ is not None:
        try:
            t4 = table4_lookup(sulphate_class_, ct, msa_mm)
            wc4 = (free_water_kg_m3 / cement_kg_m3) if free_water_kg_m3 is not None else None
            ok_c = cement_kg_m3 >= t4["min_cement_kg_m3"]
            if wc4 is None:
                oc = Outcome.NOT_VERIFIED if ok_c else Outcome.FAIL
            else:
                oc = Outcome.PASS if (ok_c and wc4 <= t4["max_free_wc"]) else Outcome.FAIL
            checks.append(("IS 456 Table 4", "sulphate (Table 4)", oc,
                           f"class {sulphate_class_}, {ct}: cement {cement_kg_m3:.0f} vs min "
                           f"{t4['min_cement_kg_m3']}; w/c on cement "
                           f"{'n/a' if wc4 is None else f'{wc4:.3f}'} vs max {t4['max_free_wc']} "
                           "[EI: additions not counted -- Table 4 names cement types only]"
                           + ("; protective coating required (class 5)" if t4["protective_coating_required"] else "")))
        except MissingTableRow as e:
            checks.append(("IS 456 Table 4", "sulphate (Table 4)", Outcome.FAIL, str(e)))

    # 6 -- chloride. IS 456 Table 7 (material data needed).
    cat = chloride_category or ("embedded_metal" if use_k == "rcc" else "embedded_metal")
    if chloride_kg_m3 is None:
        checks.append(("IS 456 Table 7", "chloride (Table 7)", Outcome.NOT_VERIFIED,
                       "needs measured chloride of every constituent (cl 8.2.5.2)"))
    else:
        cmax = IS456_TABLE7_CHLORIDE_MAX_KG_M3[cat]
        checks.append(("IS 456 Table 7", "chloride (Table 7)",
                       Outcome.PASS if chloride_kg_m3 <= cmax else Outcome.FAIL,
                       f"{chloride_kg_m3:.3f} vs max {cmax} kg/m3 ({cat})"))

    # 7 -- sulphate in the mix. IS 456 cl 8.2.5.3 ('should not exceed').
    if so3_pct_of_cement_ is None:
        checks.append(("IS 456 cl 8.2.5.3", "SO3 in mix", Outcome.NOT_VERIFIED,
                       "needs water-soluble SO3 of every constituent"))
    elif ct == "SSC":
        checks.append(("IS 456 cl 8.2.5.3", "SO3 in mix", Outcome.PASS,
                       "4 percent limit does not apply to supersulphated cement (IS 6909)"))
    else:
        ok = so3_pct_of_cement_ <= IS456_CL_8_2_5_3_SO3_MAX_PCT_OF_CEMENT
        checks.append(("IS 456 cl 8.2.5.3", "SO3 in mix",
                       Outcome.PASS if ok else Outcome.OVERRIDE_REQUIRED,
                       f"{so3_pct_of_cement_:.2f}% of cement vs 4% ('should not exceed')"))

    # 8 -- sea water. IS 456 cl 8.2.8 ('shall be at least').
    if sea_water:
        g = IS456_CL_8_2_8_SEA_WATER_MIN_GRADE["rcc" if use_k == "rcc" else "pcc"]
        ok = grade_to_fck(grade) >= grade_to_fck(g)
        checks.append(("IS 456 cl 8.2.8", "sea water minimum grade",
                       Outcome.PASS if ok else Outcome.FAIL, f"{grade} vs {g}"))

    # 9 -- freezing and thawing. IS 456 cl 8.2.2.3 (GUIDANCE).
    if freeze_thaw:
        gd = freeze_thaw_air_guidance(grade, msa_mm)
        checks.append(("IS 456 cl 8.2.2.3", "entrained air", Outcome.GUIDANCE,
                       "grade M50 or above: no air requirement printed" if gd is None
                       else f"air content should be {gd['air_pct'][0]}-{gd['air_pct'][1]} %"))

    # 10 -- design vs nominal. IS 456 cl 9.1.1.
    checks.append(("IS 456 cl 9.1.1", "design mix required", Outcome.PASS,
                   f"{grade} routed to domain {domain.name}; nominal proportions are a "
                   f"separate route under IS 456 Table 9"))

    # 11 -- volume closure. IS 10262 cl 5.7 method; tolerance [PC].
    if volume_closure_m3 is None:
        checks.append(("IS 10262 cl 5.7", "volume closure", Outcome.NOT_VERIFIED,
                       "no absolute-volume sum supplied"))
    else:
        ok = abs(volume_closure_m3 - 1.0) <= VOLUME_CLOSURE_TOL_M3
        checks.append(("IS 10262 cl 5.7 (method) + [PC] tolerance", "volume closure",
                       Outcome.PASS if ok else Outcome.FAIL,
                       f"volumes sum to {volume_closure_m3:.4f} m3 (target 1.000 incl. entrapped "
                       f"air; +/-{VOLUME_CLOSURE_TOL_M3} m3 is a project tolerance)"))

    # 12 -- SCM dosage, Section 3 only. IS 10262 Table 9 (RECOMMENDED).
    if _v(domain) == "C":
        if scm_pct_of_binder is None:
            checks.append(("IS 10262 Table 9", "SCM dosage", Outcome.NOT_VERIFIED,
                           "no SCM percentages supplied for a high-strength mix"))
        else:
            bad = [f"{k} {v}% outside {IS10262_TABLE9_SCM_DOSAGE_PCT[k]}"
                   for k, v in scm_pct_of_binder.items()
                   if k in IS10262_TABLE9_SCM_DOSAGE_PCT
                   and not (IS10262_TABLE9_SCM_DOSAGE_PCT[k][0] <= v
                            <= IS10262_TABLE9_SCM_DOSAGE_PCT[k][1])]
            checks.append(("IS 10262 Table 9", "SCM dosage",
                           Outcome.OVERRIDE_REQUIRED if bad else Outcome.PASS,
                           ("; ".join(bad) + " -- Table 9 dosages are RECOMMENDED; "
                            "record the justification to proceed") if bad
                           else "within recommended ranges"))
    else:
        checks.append(("IS 10262 Table 9", "SCM dosage", Outcome.PASS,
                       "not applicable outside Section 3"))

    # 13 -- admixture conformity. IS 456 cl 5.5.1 -> IS 9103 (certificate matter).
    checks.append(("IS 456 cl 5.5.1", "admixture complies with IS 9103", Outcome.NOT_VERIFIED,
                   "conformity is a supplier-certificate matter; not checkable from the mix"))

    # 14 -- admixture dosage vs the manufacturer's declared recommendation, IS 9103 cl 10.2.
    if admixture_kg_m3 is None or admixture_dosage_range_pct is None:
        checks.append(("IS 9103 cl 10.2", "admixture dosage", Outcome.NOT_VERIFIED,
                       "IS 9103 prints no numeric cap; it requires the manufacturer to state "
                       "the recommended dosage (cl 10.2). Supply that range."))
    else:
        pct = admixture_kg_m3 / cementitious * 100.0
        lo, hi = admixture_dosage_range_pct
        checks.append(("IS 9103 cl 10.2", "admixture dosage",
                       Outcome.PASS if lo <= pct <= hi else Outcome.OVERRIDE_REQUIRED,
                       f"{pct:.2f}% of binder vs manufacturer range {lo}-{hi}% "
                       "(a departure to justify, not an IS limit)"))

    failed = [c for c in checks if c[2] in (Outcome.FAIL, Outcome.OVERRIDE_REQUIRED)]
    hard_nv = [c[1] for c in checks if c[2] is Outcome.NOT_VERIFIED and c[1] in HARD_MIX_CHECKS]
    return {
        "pass": not failed,
        "decided": (not failed) and not hard_nv,
        "hard_not_verified": hard_nv,
        "checks": [{"clause": c[0], "check": c[1], "outcome": c[2].value, "detail": c[3]}
                   for c in checks],
        "n_not_verified": sum(1 for c in checks if c[2] is Outcome.NOT_VERIFIED),
        "cement_kg_m3": cement_kg_m3, "cementitious_kg_m3": cementitious,
        "cement_type": ct,
    }
