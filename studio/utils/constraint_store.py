"""Storage utility for Logistical, Directorial, Thematic, and Idea Constraint Sets using PyYAML."""

from pathlib import Path
from typing import List, Optional, Tuple
import yaml

from studio.models.constraints import (
    CharacterDetail,
    ConstraintType,
    DirectorialVision,
    IdeaSeed,
    LogisticalConstraint,
    ThematicFramework,
)
from studio.utils.global_state import get_workspace_root


def get_constraints_base_dir() -> Path:
    """Return constraints base path dynamically relative to active workspace or working directory."""
    return get_workspace_root() / "constraints"


def get_logistical_dir() -> Path:
    """Return logistical constraints directory path."""
    return get_constraints_base_dir() / "logistical"


def get_directorial_dir() -> Path:
    """Return directorial vision constraints directory path."""
    return get_constraints_base_dir() / "directorial"


def get_thematic_dir() -> Path:
    """Return thematic framework constraints directory path."""
    return get_constraints_base_dir() / "thematic"


def get_ideas_dir() -> Path:
    """Return idea seeds constraints directory path."""
    return get_constraints_base_dir() / "ideas"


def ensure_constraints_dirs() -> None:
    """Ensure constraint directories exist."""
    get_logistical_dir().mkdir(parents=True, exist_ok=True)
    get_directorial_dir().mkdir(parents=True, exist_ok=True)
    get_thematic_dir().mkdir(parents=True, exist_ok=True)
    get_ideas_dir().mkdir(parents=True, exist_ok=True)


# --- Logistical Constraints ---


def save_logistical_constraint(constraint: LogisticalConstraint) -> Path:
    """Save a LogisticalConstraint object to YAML."""
    ensure_constraints_dirs()
    constraint.update_timestamp()
    file_path = get_logistical_dir() / f"{constraint.name}.yaml"
    data = constraint.model_dump()
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return file_path


def load_logistical_constraint(name: str) -> Optional[LogisticalConstraint]:
    """Load a LogisticalConstraint object by set name slug."""
    slug = name.strip().lower().replace(" ", "_")
    file_path = get_logistical_dir() / f"{slug}.yaml"
    if not file_path.exists():
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or not isinstance(data, dict):
            return None
        return LogisticalConstraint.model_validate(data)
    except Exception:
        return None


def list_logistical_constraints() -> List[LogisticalConstraint]:
    """List all available LogisticalConstraint sets."""
    ensure_constraints_dirs()
    results: List[LogisticalConstraint] = []
    for file_path in sorted(get_logistical_dir().glob("*.yaml")):
        c = load_logistical_constraint(file_path.stem)
        if c:
            results.append(c)
    return results


def delete_logistical_constraint(name: str) -> bool:
    """Delete a LogisticalConstraint set file by name."""
    slug = name.strip().lower().replace(" ", "_")
    file_path = get_logistical_dir() / f"{slug}.yaml"
    if file_path.exists():
        file_path.unlink()
        return True
    return False


# --- Directorial Vision Constraints ---


def save_directorial_vision(constraint: DirectorialVision) -> Path:
    """Save a DirectorialVision object to YAML."""
    ensure_constraints_dirs()
    constraint.update_timestamp()
    file_path = get_directorial_dir() / f"{constraint.name}.yaml"
    data = constraint.model_dump()
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return file_path


def load_directorial_vision(name: str) -> Optional[DirectorialVision]:
    """Load a DirectorialVision object by set name slug."""
    slug = name.strip().lower().replace(" ", "_")
    file_path = get_directorial_dir() / f"{slug}.yaml"
    if not file_path.exists():
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or not isinstance(data, dict):
            return None
        return DirectorialVision.model_validate(data)
    except Exception:
        return None


def list_directorial_visions() -> List[DirectorialVision]:
    """List all available DirectorialVision sets."""
    ensure_constraints_dirs()
    results: List[DirectorialVision] = []
    for file_path in sorted(get_directorial_dir().glob("*.yaml")):
        c = load_directorial_vision(file_path.stem)
        if c:
            results.append(c)
    return results


def delete_directorial_vision(name: str) -> bool:
    """Delete a DirectorialVision set file by name."""
    slug = name.strip().lower().replace(" ", "_")
    file_path = get_directorial_dir() / f"{slug}.yaml"
    if file_path.exists():
        file_path.unlink()
        return True
    return False


# --- Thematic Framework Constraints ---


def save_thematic_framework(constraint: ThematicFramework) -> Path:
    """Save a ThematicFramework object to YAML."""
    ensure_constraints_dirs()
    constraint.update_timestamp()
    file_path = get_thematic_dir() / f"{constraint.name}.yaml"
    data = constraint.model_dump()
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return file_path


def load_thematic_framework(name: str) -> Optional[ThematicFramework]:
    """Load a ThematicFramework object by set name slug."""
    slug = name.strip().lower().replace(" ", "_")
    file_path = get_thematic_dir() / f"{slug}.yaml"
    if not file_path.exists():
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or not isinstance(data, dict):
            return None
        return ThematicFramework.model_validate(data)
    except Exception:
        return None


def list_thematic_frameworks() -> List[ThematicFramework]:
    """List all available ThematicFramework sets."""
    ensure_constraints_dirs()
    results: List[ThematicFramework] = []
    for file_path in sorted(get_thematic_dir().glob("*.yaml")):
        c = load_thematic_framework(file_path.stem)
        if c:
            results.append(c)
    return results


def delete_thematic_framework(name: str) -> bool:
    """Delete a ThematicFramework set file by name."""
    slug = name.strip().lower().replace(" ", "_")
    file_path = get_thematic_dir() / f"{slug}.yaml"
    if file_path.exists():
        file_path.unlink()
        return True
    return False


# --- Idea Seed Constraints ---


def save_idea_seed(constraint: IdeaSeed) -> Path:
    """Save an IdeaSeed object to YAML."""
    ensure_constraints_dirs()
    constraint.update_timestamp()
    file_path = get_ideas_dir() / f"{constraint.name}.yaml"
    data = constraint.model_dump()
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return file_path


def load_idea_seed(name: str) -> Optional[IdeaSeed]:
    """Load an IdeaSeed object by set name slug."""
    slug = name.strip().lower().replace(" ", "_")
    file_path = get_ideas_dir() / f"{slug}.yaml"
    if not file_path.exists():
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not data or not isinstance(data, dict):
            return None
        return IdeaSeed.model_validate(data)
    except Exception:
        return None


def list_idea_seeds() -> List[IdeaSeed]:
    """List all available IdeaSeed sets."""
    ensure_constraints_dirs()
    results: List[IdeaSeed] = []
    for file_path in sorted(get_ideas_dir().glob("*.yaml")):
        c = load_idea_seed(file_path.stem)
        if c:
            results.append(c)
    return results


def delete_idea_seed(name: str) -> bool:
    """Delete an IdeaSeed set file by name."""
    slug = name.strip().lower().replace(" ", "_")
    file_path = get_ideas_dir() / f"{slug}.yaml"
    if file_path.exists():
        file_path.unlink()
        return True
    return False


# --- Seeding Defaults ---


def seed_default_constraints() -> Tuple[Optional[Path], Optional[Path], Optional[Path], Optional[Path]]:
    """Seed default starter constraint sets for all categories if none exist, including all 12 director archetypes."""
    ensure_constraints_dirs()
    logistical_path = None
    directorial_path = None
    thematic_path = None
    ideas_path = None

    logistical_setups = [
        LogisticalConstraint(
            name="upper_middle_class_residence",
            locations=["Interior", "Suburbs", "Day/Night"],
            sub_locations=["Open-concept Kitchen", "Master Bathroom", "Living Room"],
            location_details="Large windows providing ample natural bounce light, high ceilings. The bathroom features a modern one-piece continuous mold toilet without a detachable tank.",
            available_set_dressing=["Stainless steel appliances", "Minimalist wall art", "Large kitchen island"],
        ),
        LogisticalConstraint(
            name="shabby_apartment",
            locations=["Interior", "Urban", "Day/Night"],
            sub_locations=["Galley Kitchen", "Fire Escape", "Cramped Bedroom"],
            location_details="Thin walls with potential audio bleed, uneven practical lighting, exposed radiators, and tight corners for camera placement.",
            available_set_dressing=["Piles of unopened mail", "Mismatched coffee mugs", "Fading, sunken couch"],
        ),
        LogisticalConstraint(
            name="public_park_sports_court",
            locations=["Exterior", "Park", "Day"],
            sub_locations=["Basketball Court", "Park Bench", "Parking Lot"],
            location_details="Variable weather and lighting conditions, uncontrolled background extras, ambient wind, and distant traffic noise.",
            available_set_dressing=["Chainlink fences", "A parked 2022 Honda Accord 2.0T Sport sedan", "Abandoned basketball"],
        ),
        LogisticalConstraint(
            name="office_building",
            locations=["Interior", "Commercial", "Day/Night"],
            sub_locations=["Cubicle Farm", "Breakroom", "Elevator Bank"],
            location_details="Harsh, flat fluorescent overhead lighting, repetitive geometric lines, and the constant quiet hum of an HVAC system.",
            available_set_dressing=["Water cooler", "Stacks of printer paper", "Ergonomic rolling chairs"],
        ),
        LogisticalConstraint(
            name="college_lecture_hall",
            locations=["Interior", "Campus", "Day/Night"],
            sub_locations=["Podium", "Back Row", "Hallway"],
            location_details="Highly echoey acoustics requiring tight mic placement, large projector screens, and often a lack of natural windows.",
            available_set_dressing=["Expansive whiteboards", "Scattered abandoned notebooks", "Podium microphone"],
        ),
        LogisticalConstraint(
            name="local_museum_or_gallery",
            locations=["Interior", "Civic", "Day"],
            sub_locations=["Main Exhibit Hall", "Lobby", "Gift Shop"],
            location_details="Hardwood or polished concrete floors, highly controlled directional spotlighting, and hushed acoustics.",
            available_set_dressing=["Display pedestals", "Velvet stanchion ropes", "Framed canvases"],
        ),
    ]

    for setup in logistical_setups:
        if not load_logistical_constraint(setup.name):
            p = save_logistical_constraint(setup)
            if logistical_path is None:
                logistical_path = p


    if not list_idea_seeds():
        default_idea = IdeaSeed(
            name="late_night_visitor",
            description="An unexpected arrival disrupts a fragile quiet night.",
            inciting_incident="Two long-lost acquaintances reunite under suspicious circumstances during a citywide power outage.",
            complications="A lost key, hidden motives, and a sudden knock at the back door.",
            ending_targets="A tense standoff resolving in an unexpected gesture of forgiveness.",
        )
        ideas_path = save_idea_seed(default_idea)

    # Mass Seed all 12 Director Archetype Constraint Pairs
    director_archetypes = [
        {
            "slug": "wes_anderson",
            "dir": DirectorialVision(
                name="wes_anderson",
                description="Meticulous symmetrical composition, pastel color palettes, snap zooms, and deadpan theatricality.",
                visual_economy="Rigid center-frame camera positioning, whip pans, snap zooms, flat 90-degree angles.",
                lighting_color="Saturated pastel tones, vibrant primary colors, warm tungsten diegetic glow.",
                audio_landscape="Upbeat vintage vinyl folk or baroque harpsichord contrasting deadpan dialogue delivery.",
            ),
            "them": ThematicFramework(
                name="wes_anderson",
                description="Whimsical melancholy, eccentric family dysfunction, obsessive order masking deep grief.",
                core_philosophy="Emotional vulnerability concealed beneath hyper-curated, nostalgic order.",
                emotional_arc="Estranged relatives or quirky allies unite in a staged endeavor to cope with shared loss.",
                world_rules="Diorama-like world where adulthood is child-like and children possess solemn adult wisdom.",
            ),
        },
        {
            "slug": "wong_kar_wai",
            "dir": DirectorialVision(
                name="wong_kar_wai",
                description="Step-printed motion, neon-drenched nightscapes, handheld intimacy, and urban yearning.",
                visual_economy="Slow-shutter step-printing, lingering reflections in mirrors/rain, intimate close-ups.",
                lighting_color="Neon reds and greens, ambient sodium-vapor streetlights, melancholic shadowplay.",
                audio_landscape="Dreamy lounge jazz, Latin ballads, and inner monologue voiceovers echoing through urban noise.",
            ),
            "them": ThematicFramework(
                name="wong_kar_wai",
                description="Fleeting human connections, unrequited love, passage of time, and urban loneliness.",
                core_philosophy="Limerence and memory—people are ships passing in the night, forever changed by brief encounters.",
                emotional_arc="Two lonely souls orbit each other in close proximity without ever fully aligning.",
                world_rules="Sultry, rain-soaked metropolis where expired canned goods and forgotten phone numbers hold eternal weight.",
            ),
        },
        {
            "slug": "david_lynch",
            "dir": DirectorialVision(
                name="david_lynch",
                description="Surreal dream logic, uncanny industrial dark ambient soundscapes, flickering lights, and dual identities.",
                visual_economy="Slow hypnotic camera glides, unsettling static stares, disorienting framing.",
                lighting_color="High-contrast chiaroscuro, flickering neon, deep crimson curtains, unsettling warm glows.",
                audio_landscape="Industrial machinery hums, wind drones, flickering bulb buzzes, eerie 1950s torch ballads.",
            ),
            "them": ThematicFramework(
                name="david_lynch",
                description="The rotting subconscious beneath tranquil small-town innocence.",
                core_philosophy="Reality is a fragile veil over cosmic dread and surreal subconscious desires.",
                emotional_arc="An innocent investigation spirals down a rabbit hole into fragmented identity and nightmarish revelation.",
                world_rules="Small-town Americana where dreams bleeding into waking life are accepted as fundamental truths.",
            ),
        },
        {
            "slug": "bong_joon_ho",
            "dir": DirectorialVision(
                name="bong_joon_ho",
                description="Kinetic camera blocking, sudden genre shifts, sharp spatial verticality, and social satire.",
                visual_economy="Dynamic multi-plane tracking shots, precise actor ensemble blocking, geometric spatial hierarchy.",
                lighting_color="Contrasting basements vs sunlit high-rises, cool rainy blues vs warm domestic golds.",
                audio_landscape="Sharp abrupt transitions from jaunty classical strings to chaotic realistic sound effects.",
            ),
            "them": ThematicFramework(
                name="bong_joon_ho",
                description="Sharp class critique, systemic inequality, and tragicomic human desperation.",
                core_philosophy="Social structures dictate human behavior; tragedy and comedy are two sides of the same coin.",
                emotional_arc="Resourceful underdogs plot an ambitious scheme that collapses under systemic pressure.",
                world_rules="Vertical architecture determines status; unexpected chaotic twists shatter all calculated plans.",
            ),
        },
        {
            "slug": "denis_villeneuve",
            "dir": DirectorialVision(
                name="denis_villeneuve",
                description="Brutalist architectural scale, monolithic shadows, bass-heavy atmospheric scoring, and existential dread.",
                visual_economy="Monolithic wide shots rendering humans tiny, slow deliberate camera creeping.",
                lighting_color="Desaturated stark grays, dusty orange hazes, piercing volumetric light beams.",
                audio_landscape="Sub-bass room shakes, metallic resonant drones, sparse tactical silence.",
            ),
            "them": ThematicFramework(
                name="denis_villeneuve",
                description="The burden of destiny, human insignificance, and moral compromise in vast systems.",
                core_philosophy="Confronting cosmic or institutional scales tests the limit of human free will and morality.",
                emotional_arc="A stoic protagonist uncovers an overwhelming truth that alters their fundamental purpose.",
                world_rules="Imposing environments and rigid institutions overpower individual desires.",
            ),
        },
        {
            "slug": "nicolas_winding_refn",
            "dir": DirectorialVision(
                name="nicolas_winding_refn",
                description="High-contrast neon synthwave, hypnotic violence, minimal dialogue, and ultra-stylized atmosphere.",
                visual_economy="Glacial tracking shots, long silent stares, sudden bursts of kinetic action.",
                lighting_color="Saturated neon magenta, electric blue, stark shadow silhouettes.",
                audio_landscape="Pulsating retro synthwave, heavy reverb, spatial audio design with minimal speech.",
            ),
            "them": ThematicFramework(
                name="nicolas_winding_refn",
                description="Mythic archetypes, silent stoicism, and the intoxicating allure of violence and beauty.",
                core_philosophy="Silence speaks louder than words; action and aesthetic define soul and fate.",
                emotional_arc="A quiet lone knight crosses moral boundaries to protect an innocent soul.",
                world_rules="Glossy underworld operating on primal codes of honor, sacrifice, and retribution.",
            ),
        },
        {
            "slug": "celine_sciamma",
            "dir": DirectorialVision(
                name="celine_sciamma",
                description="Intimate natural lighting, lingering artistic gazes, female agency, and tactile emotional honesty.",
                visual_economy="Patient, observant mid-shots, fluid character-focused tracking, meaningful eye contact.",
                lighting_color="Soft natural window daylight, flickering firelight, rich organic earth tones.",
                audio_landscape="Subtle organic soundscapes, natural breathing, acoustic resonances, absence of manipulative scoring.",
            ),
            "them": ThematicFramework(
                name="celine_sciamma",
                description="Female intimacy, artistic creation, memory as resistance, and unspoken emotional bonds.",
                core_philosophy="Looking is an act of reciprocity; genuine connection transcends social constraints.",
                emotional_arc="Two individuals build a shared language of glances that culminates in profound mutual understanding.",
                world_rules="Private safe spaces allow authentic selves to blossom away from patriarchal scrutiny.",
            ),
        },
        {
            "slug": "jordan_peele",
            "dir": DirectorialVision(
                name="jordan_peele",
                description="Subterranean psychological horror, social allegory, uncanny humor, and escalating paranoia.",
                visual_economy="Creeping zoom-ins, uncomfortable character framing, double-take background reveals.",
                lighting_color="Stark night lighting, unsettling shadows, stark primary accents against dark environments.",
                audio_landscape="Subverted pop songs, ominous choral arrangements, tense rhythmic silence.",
            ),
            "them": ThematicFramework(
                name="jordan_peele",
                description="Systemic trauma, double consciousness, exploitation, and the horrors hiding in plain sight.",
                core_philosophy="Societal anxieties and historical trauma manifest as physical monsters and conspiracies.",
                emotional_arc="An observant protagonist senses something wrong, uncovers a hidden horror, and fights for survival.",
                world_rules="Familiar everyday settings conceal sinister subterranean networks or spectator traps.",
            ),
        },
        {
            "slug": "alfonso_cuaron",
            "dir": DirectorialVision(
                name="alfonso_cuaron",
                description="Extended bravura long takes, immersive handheld tracking, spatial geography, and human resilience.",
                visual_economy="Fluid uninterrupted sequence shots, wide deep-focus compositions, 360-degree camera sweeps.",
                lighting_color="Naturalistic bounce light, atmospheric weather phenomena, realistic daylight tones.",
                audio_landscape="Immersive 3D directional sound design, ambient environmental audio, authentic dialogue overlap.",
            ),
            "them": ThematicFramework(
                name="alfonso_cuaron",
                description="Personal human survival set against overwhelming historical or physical turmoil.",
                core_philosophy="Human connection and empathy are the ultimate anchors in a chaotic universe.",
                emotional_arc="A vulnerable character endures a harrowing physical journey to rediscover hope and purpose.",
                world_rules="The environment is a living, unpredictable participant in every scene.",
            ),
        },
        {
            "slug": "lars_von_trier",
            "dir": DirectorialVision(
                name="lars_von_trier",
                description="Dogme 95 raw handheld camera, stark chapter titles, psychological distress, and uncompromising realism.",
                visual_economy="Unfiltered handheld camera movement, jump cuts, naturalistic framing, documentary immediacy.",
                lighting_color="Available natural/practical lighting, raw uncorrected color balance, harsh shadows.",
                audio_landscape="Diegetic sound only, harsh abrupt cuts, zero non-diegetic orchestral scoring.",
            ),
            "them": ThematicFramework(
                name="lars_von_trier",
                description="Provocative psychological endurance, martyrdom, moral hypocrisy, and human suffering.",
                core_philosophy="Truth is found by stripping away cinematic illusion and pushing characters to extremes.",
                emotional_arc="An idealist protagonist's selflessness is tested and brutalized by rigid societal hypocrisy.",
                world_rules="Forgiving rules do not exist; actions have immediate, unglamorized consequences.",
            ),
        },
        {
            "slug": "paul_thomas_anderson",
            "dir": DirectorialVision(
                name="paul_thomas_anderson",
                description="Period authenticity, sweeping tracking shots, character rivalries, and rhythmic orchestral energy.",
                visual_economy="Energetic steadicam tracking shots, intimate wide-angle close-ups, theatrical character blocking.",
                lighting_color="Rich celluloid film grain warmth, deep ambers, moody natural window light.",
                audio_landscape="Jittery percussion, lush orchestral arrangements, overlapping ensemble dialogue.",
            ),
            "them": ThematicFramework(
                name="paul_thomas_anderson",
                description="Ambitious visionaries, surrogate family bonds, obsession, and volatile character dynamics.",
                core_philosophy="Flawed, larger-than-life personalities build empire or identity while craving belonging.",
                emotional_arc="Two forceful personalities collide in a fierce duel of wills before reaching a strange catharsis.",
                world_rules="Expansive historical eras shaped by eccentric, relentless individuals.",
            ),
        },
        {
            "slug": "greta_gerwig",
            "dir": DirectorialVision(
                name="greta_gerwig",
                description="Witty overlapping dialogue, warm nostalgic color tones, coming-of-age self-discovery, and literary framing.",
                visual_economy="Lively character-driven framing, rhythmic cutting matching speech cadence, theatrical tableau compositions.",
                lighting_color="Warm golden-hour sunlight, vibrant pastel accents, cozy domestic interiors.",
                audio_landscape="Brisk classical or indie acoustic scores, energetic natural chatter, musical speech patterns.",
            ),
            "them": ThematicFramework(
                name="greta_gerwig",
                description="Self-determination, female ambition, mother-daughter dynamics, and nostalgia for youth.",
                core_philosophy="Growing up means reconciling fierce independence with deep love for where you came from.",
                emotional_arc="A headstrong young protagonist navigates ambition and relationship friction to embrace their true voice.",
                world_rules="Warm, articulate worlds where emotional intelligence and humor conquer hardship.",
            ),
        },
    ]

    for archetype in director_archetypes:
        slug = archetype["slug"]
        if not load_directorial_vision(slug):
            p = save_directorial_vision(archetype["dir"])
            if directorial_path is None:
                directorial_path = p
        if not load_thematic_framework(slug):
            p = save_thematic_framework(archetype["them"])
            if thematic_path is None:
                thematic_path = p

    return logistical_path, directorial_path, thematic_path, ideas_path


