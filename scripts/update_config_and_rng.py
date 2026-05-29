"""Populate the CONFIG cell (cell 4) and RNGStreams cell (cell 44).

CONFIG contains every numeric/probabilistic parameter from the spec, plus the
M2 fitted parameters. RNGStreams gives one independent random.Random per
named source seeded deterministically from a master seed via
numpy.random.SeedSequence for high-quality independent streams.

The M3 Sampler class (cell 26) will read every distribution parameter from
CONFIG, and draw from its dedicated RNGStreams stream.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
NB_PATH = ROOT / "Queuechella_Simulation.ipynb"

CONFIG_SOURCE = '''\
"""CONFIG — every numeric / probabilistic parameter from the spec as named constants.

All values are read from a single ``CONFIG`` dict so partners can override any
parameter for an alternatives run by mutating ``CONFIG`` before instantiating
the simulation. The ``Sampler`` and ``Simulation`` classes draw all numerics
from this dict.

Alternatives mapping (partners flip these for the §17 alternatives review):
  Better kitchen team        ->  food_unsatisfied_prob = 0.1, food_choose_prob = 0.85
  Expanded security (+30%)   ->  stage_capacity_main = 260, stage_capacity_side = 130, stage_capacity_dj = 91
  Mainstream investment      ->  merch_band_shirt_prob = 0.8, genre_score_main = 4
  Photo + BodyArt expansion  ->  photo_servers = 4, bodyart_artists = 3
  Advertising                ->  arrival_rate_multiplier = 1.2
  Auto entry                 ->  entry_skip_scan = True
  Visitor gifts              ->  initial_satisfaction = 6.5
Budget cap: 1,000,000 NIS combined.
"""

# Numeric values that need to round-trip across cells live here. M2-fitted
# parameters are baked in at full precision so the notebook is order-independent.
CONFIG = {
    # ---- Festival schedule ----
    "festival_open_hour": 9.0,             # 09:00
    "festival_close_hour": 20.0,           # 20:00
    "festival_days": 2,
    # FriendsGroup arrival window: 09:00-13:00 (Day 1 only, per spec)
    "fg_arrival_start_hour": 9.0,
    "fg_arrival_end_hour": 13.0,
    # Couple arrival window: 10:00-16:00 (both days, per spec)
    "couple_arrival_start_hour": 10.0,
    "couple_arrival_end_hour": 16.0,
    # Single arrival window: 09:00-16:00 (both days, per spec)
    "single_arrival_start_hour": 9.0,
    "single_arrival_end_hour": 16.0,

    # ---- Visitor satisfaction ----
    "initial_satisfaction": 5.0,           # alternative: 6.5
    "satisfaction_min": 0.0,
    "satisfaction_max": 10.0,

    # ---- Arrival rates (per minute) ----
    # FriendsGroup: Gamma fit from M2 (alpha, scale=beta)
    "fg_arrival_alpha": 1.239321,          # M2 §5א MLE
    "fg_arrival_beta":  1.106439,          # M2 §5א MLE
    # Couple: Exp with mean 60 min per spec ("תוחלת של 60 בשעה")
    "couple_arrival_lambda": 1.0 / 60.0,   # 1 arrival per 60 min in expectation
    # Single: 500 expected arrivals in the 09:00-16:00 window (7 hours = 420 min).
    # See PLAN.md note: PLAN's denominator (11h) does not match the spec window.
    "single_arrival_lambda": 500.0 / (7.0 * 60.0),  # ≈ 1.190 per min
    "arrival_rate_multiplier": 1.0,        # alternative: 1.2 (advertising)

    # ---- Group sizing ----
    "fg_size_min": 3,                      # DiscreteUniform[3,6]
    "fg_size_max": 6,
    "couple_size": 2,
    "single_size": 1,

    # ---- Entry ----
    "entry_clerks": 5,
    "entry_skip_scan": False,              # alternative: True (auto entry)
    "entry_scan_low": 1.5,                 # U(1.5, 3) minutes
    "entry_scan_high": 3.0,
    "entry_security_mean": 2.0,            # Exp with mean 2 min

    # ---- MainStage (mainstream genre, G=3) ----
    "stage_capacity_main": 200,
    "main_show_break_min": 10.0,
    "main_show_mu":    45.902765,          # M2 §5ב MLE (minutes)
    "main_show_sigma":  8.927433,          # M2 §5ב MLE (minutes)
    "main_farthest_n": 10,                 # 10 farthest entities re-evaluated
    "main_farthest_leave_prob": 0.5,       # Bernoulli at 15-min checkpoint
    "main_farthest_check_after_min": 15.0,
    "genre_score_main": 3,                 # alternative: 4 (mainstream investment)

    # ---- SideStage (indie genre, G=2) ----
    "stage_capacity_side": 100,
    "side_show_break_min": 5.0,
    "side_show_low":  20.0,                # U(20, 30) minutes
    "side_show_high": 30.0,
    "genre_score_side": 2,

    # ---- DJstage (electronic genre, G=1) ----
    "stage_capacity_dj": 70,
    # DJ piecewise PDF support [20, 60]; A/R envelope U(20, 60).
    # NOTE: spec PDF is decreasing on [40,50] with a jump-up at x=40 from 1/30
    # to 1/15, so max f = 1/15 at x=40+ (not 1/30 as PLAN.md initially claimed).
    # Bounding constant c = M * (60-20) = (1/15) * 40 = 8/3.  Acceptance = 3/8 ≈ 0.375.
    "dj_stay_low":  20.0,
    "dj_stay_high": 60.0,
    "dj_stay_max_pdf": 1.0 / 15.0,         # M for acceptance-rejection
    "dj_stay_envelope_c": 8.0 / 3.0,       # M * (b-a); acceptance rate = 1/c
    "genre_score_dj": 1,

    # ---- PhotoStation (composition: identical to example's pool PDF) ----
    "photo_servers": 3,                    # alternative: 4 (photo+bodyart expansion)
    # CDF break points (computed once in M3 markdown derivation):
    #   F(2) = 1/4,  F(3) = 7/8
    "photo_cdf_break_low":  0.25,
    "photo_cdf_break_high": 0.875,
    "photo_satisfied_prob": 0.7,
    "photo_satisfied_bonus": 2.0,
    "photo_unsatisfied_penalty_prob": 0.5, # if unsatisfied, Bernoulli for penalty
    "photo_unsatisfied_penalty": 0.5,      # subtracted
    "photo_print_price": 30,               # NIS, paid on satisfied outcome

    # ---- ChargingStation ----
    "charging_chargers": 150,
    "charging_battery_mu": 40.0,           # N(40, 15) for battery % on arrival
    "charging_battery_sigma": 15.0,
    # Charge-time PDF: f(t) = (alpha / 40^alpha) * (40-t)^(alpha-1), alpha = 100/(100-b)
    # Inverse-CDF: t = 40 * (1 - U^(1/alpha))
    "charging_max_minutes": 40.0,

    # ---- MerchTent ----
    "merch_servers": 7,                    # 7 registers
    "merch_service_low":  2.0,             # U(2, 6) minutes
    "merch_service_high": 6.0,
    # Per-member item Bernoulli probabilities + prices (NIS)
    "merch_shirt_prob":      0.8, "merch_shirt_price":      100,
    "merch_hat_prob":        0.4, "merch_hat_price":         50,
    "merch_flag_prob":       0.9, "merch_flag_price":        40,
    "merch_band_shirt_prob": 0.3, "merch_band_shirt_price": 200,  # alt: 0.8

    # ---- BodyArt ----
    "bodyart_artists": 2,                  # alternative: 3
    "bodyart_break_after_n": 10,           # 15-min break per 10 drawings per artist
    "bodyart_break_min": 15.0,
    # Picture-type choice probabilities (mutually exclusive)
    "bodyart_glitter_choose_prob": 0.3,
    "bodyart_neon_choose_prob":    0.3,
    "bodyart_henna_choose_prob":   0.4,
    # Duration distributions
    "bodyart_glitter_mu":    15.0,         # N(15, 3)
    "bodyart_glitter_sigma":  3.0,
    "bodyart_neon_mean":     12.0,         # Exp mean=12
    "bodyart_henna_low":     17.0,         # U(17, 22)
    "bodyart_henna_high":    22.0,
    # Per-type satisfaction probabilities + bonuses
    "bodyart_glitter_satisfied_prob": 0.7, "bodyart_glitter_bonus": 0.8,
    "bodyart_neon_satisfied_prob":    0.6, "bodyart_neon_bonus":    1.2,
    "bodyart_henna_satisfied_prob":   0.8, "bodyart_henna_bonus":   0.7,

    # ---- Food court (active 13:00-15:00 window per spec) ----
    "food_window_start_hour": 13.0,
    "food_window_end_hour":   15.0,
    "food_choose_prob": 0.7,               # alternative: 0.85
    # Restaurant choice probabilities (sum to 1)
    "food_choice_pizza":  0.25,            # 1/4
    "food_choice_burger": 0.375,           # 3/8
    "food_choice_asian":  0.375,           # remainder
    # Prep times (cashier → kitchen)
    "food_prep_pizza_low":  4.0,  "food_prep_pizza_high":  6.0,   # U(4, 6)
    "food_prep_burger_low": 3.0,  "food_prep_burger_high": 4.0,   # U(3, 4)
    "food_prep_asian_low":  3.0,  "food_prep_asian_high":  7.0,   # U(3, 7)
    # Register service (one register per restaurant)
    "food_register_mu":    5.0,                                    # N(5, 1.5)
    "food_register_sigma": 1.5,
    # Meal duration after receiving the food
    "food_meal_low":  15.0, "food_meal_high": 35.0,                # U(15, 35)
    # Prices (NIS)
    "food_pizza_personal_price": 40,       # Single only
    "food_pizza_family_price":  100,       # Couple + FriendsGroup (3+ people)
    "food_burger_price":        100,
    "food_asian_price":          65,
    # Unsatisfied outcome
    "food_unsatisfied_prob": 0.4,          # alternative: 0.1
    "food_unsatisfied_penalty": 0.6,

    # ---- Show satisfaction outcome ----
    "show_satisfied_prob": 0.5,            # Bernoulli for good experience
    # On bad experience: -1 satisfaction. On good: score = (G-1)/2 + (T-1)/19
    "show_bad_experience_penalty": 1.0,
    "show_satisfaction_genre_divisor": 2,
    "show_satisfaction_time_divisor": 19,

    # ---- Wait tolerance / abandonment ----
    "wait_tolerance_fg":     15.0,         # minutes
    "wait_tolerance_couple": 20.0,
    "wait_tolerance_single": 20.0,
    "wait_penalty_fg":     2.0,            # satisfaction lost per member on abandonment
    "wait_penalty_couple": 1.5,
    "wait_penalty_single": 1.0,

    # ---- Lodging / revenue ----
    "ticket_price":             500,       # NIS
    "lodging_addon_price":      250,       # Couple stay-over flat fee
    "ticket_plus_lodging_price": 700,      # FG pre-purchase price
    "fg_lodging_prob": 0.7,                # P(FG stays overnight, decided at arrival)
    "couple_lodging_threshold": 7.0,       # at least one member's satisfaction > 7

    # ---- RNG ----
    "master_seed": 20260628,               # day before submission, for luck
}
'''

RNGSTREAMS_SOURCE = '''\
# M4 prereq for M3 — RNGStreams (Sampler accepts an instance at construction).
class RNGStreams:
    """One independent random.Random per named source.

    Each named stream is seeded deterministically from ``master_seed`` via
    numpy.random.SeedSequence so streams are statistically independent.
    Partners running alternatives can reseed only the streams an alternative
    touches via ``reseed(names, base_seed)`` to keep all other draws identical
    (Common Random Numbers for variance reduction).
    """

    STREAM_NAMES = (
        # Arrivals + group sizing
        "arrival_friends", "arrival_couple", "arrival_single", "friends_size",
        # Entry
        "entry_scan", "entry_security",
        # Stages
        "show_main", "show_side", "dj_stay",
        "farthest_ten_bernoulli",
        # PhotoStation
        "photo_duration", "photo_satisfied", "photo_unsatisfied_penalty",
        # ChargingStation
        "charging_battery", "charging_time",
        # MerchTent
        "merch_service", "merch_shirt", "merch_hat", "merch_flag", "merch_band_shirt",
        # BodyArt
        "bodyart_type", "bodyart_glitter", "bodyart_neon", "bodyart_henna",
        "bodyart_satisfied",
        # Show satisfaction outcome
        "show_satisfied",
        # Food court
        "food_choose", "food_restaurant",
        "food_prep_pizza", "food_prep_burger", "food_prep_asian",
        "food_register", "food_meal", "food_unsatisfied",
        # Day transitions / lodging
        "lodging_fg", "lodging_couple",
        # Itinerary
        "couple_choice", "itinerary_tiebreak",
    )

    def __init__(self, master_seed):
        self.master_seed = int(master_seed)
        seed_sequence = np.random.SeedSequence(self.master_seed)
        child_sequences = seed_sequence.spawn(len(self.STREAM_NAMES))
        self._streams = {
            name: random.Random(int(child.generate_state(1, dtype=np.uint64)[0]))
            for name, child in zip(self.STREAM_NAMES, child_sequences)
        }

    def __getitem__(self, name):
        return self._streams[name]

    def reseed(self, names, base_seed):
        """Reseed only the named streams. Used by partners for CRN across alternatives."""
        seed_sequence = np.random.SeedSequence(int(base_seed))
        child_sequences = seed_sequence.spawn(len(names))
        for name, child in zip(names, child_sequences):
            if name not in self._streams:
                raise KeyError(f"Unknown stream name: {name!r}")
            self._streams[name] = random.Random(int(child.generate_state(1, dtype=np.uint64)[0]))

    def __repr__(self):
        return f"RNGStreams(master_seed={self.master_seed}, n_streams={len(self._streams)})"
'''


def main():
    with NB_PATH.open() as f:
        nb = json.load(f)

    # Cell 4 = CONFIG
    nb["cells"][4]["source"] = CONFIG_SOURCE.splitlines(keepends=True)
    nb["cells"][4]["outputs"] = []
    nb["cells"][4]["execution_count"] = None

    # Cell 44 = RNGStreams
    nb["cells"][44]["source"] = RNGSTREAMS_SOURCE.splitlines(keepends=True)
    nb["cells"][44]["outputs"] = []
    nb["cells"][44]["execution_count"] = None

    with NB_PATH.open("w") as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
        f.write("\n")

    print(f"Updated CONFIG (cell 4): {len(CONFIG_SOURCE)} chars")
    print(f"Updated RNGStreams (cell 44): {len(RNGSTREAMS_SOURCE)} chars")


if __name__ == "__main__":
    main()
