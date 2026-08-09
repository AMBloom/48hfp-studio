"""Quiz logic engine for the Filmmaker Personality Quiz in 48HFP-Studio."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class QuizOption:
    """Represents a single answer choice in a quiz question."""

    text: str
    weights: Dict[str, int] = field(default_factory=dict)


@dataclass
class QuizQuestion:
    """Represents a multiple-choice question in the onboarding quiz."""

    id: int
    prompt: str
    category: str  # "atmospheric" or "on-set"
    options: List[QuizOption]


@dataclass
class ArchetypeInfo:
    """Metadata details for a director archetype."""

    slug: str
    director_name: str
    title: str
    quote: str
    visual_style: str
    thematic_core: str


@dataclass
class QuizResult:
    """Result returned after tallying quiz responses."""

    winner_slug: str
    winner_info: ArchetypeInfo
    scores: Dict[str, int]


ARCHETYPE_LIBRARY: Dict[str, ArchetypeInfo] = {
    "wes_anderson": ArchetypeInfo(
        slug="wes_anderson",
        director_name="Wes Anderson",
        title="The Architect of Symmetrical Whimsy",
        quote="I want to try not to repeat myself. But then it seems I frequently do in my films.",
        visual_style="Rigid 90-degree center framing, pastel color blocking, whip-pans, and snap zooms.",
        thematic_core="Whimsical order masking deep familial grief, eccentric dysfunction, and nostalgic longing.",
    ),
    "wong_kar_wai": ArchetypeInfo(
        slug="wong_kar_wai",
        director_name="Wong Kar-wai",
        title="The Poet of Urban Yearning",
        quote="To love someone who doesn't love you back is like holding a candle in the rain.",
        visual_style="Step-printed slow-shutter motion, rain-slicked neon streetscapes, and mirror reflections.",
        thematic_core="Fleeting urban encounters, unrequited love, memory, and the bittersweet passage of time.",
    ),
    "david_lynch": ArchetypeInfo(
        slug="david_lynch",
        director_name="David Lynch",
        title="The Master of Dream Logic & Subconscious Dread",
        quote="Ideas are like fish. If you want to catch little fish, you can stay in the shallow water.",
        visual_style="High-contrast chiaroscuro, flickering practical lights, crimson curtains, and hypnotic tracking glides.",
        thematic_core="Surreal dream logic, industrial dark ambient soundscapes, and the dark underbelly of innocence.",
    ),
    "bong_joon_ho": ArchetypeInfo(
        slug="bong_joon_ho",
        director_name="Bong Joon-ho",
        title="The Virtuoso of Social Satire & Genre Collisions",
        quote="Cinema is an art form that can convey human dignity even when capturing desperate struggle.",
        visual_style="Kinetic multi-plane camera blocking, sharp vertical architecture, and sudden tonal genre shifts.",
        thematic_core="Sharp class critique, systemic inequality, and tragicomic human desperation.",
    ),
    "denis_villeneuve": ArchetypeInfo(
        slug="denis_villeneuve",
        director_name="Denis Villeneuve",
        title="The Visionary of Monolithic Scale & Existential Awe",
        quote="Directing is about creating space where the magic can happen.",
        visual_style="Brutalist architectural scale, sweeping wide vistas, desaturated palettes, and sub-bass audio.",
        thematic_core="Human insignificance against vast institutional or cosmic scales, destiny, and moral gravity.",
    ),
    "nicolas_winding_refn": ArchetypeInfo(
        slug="nicolas_winding_refn",
        director_name="Nicolas Winding Refn",
        title="The Stylist of Neon Hypnosis & Mythic Violence",
        quote="I don't believe in boundaries. I believe in emotion.",
        visual_style="Saturated neon pinks and blues, glacial tracking shots, silent stares, and synthwave scores.",
        thematic_core="Mythic stoic archetypes, the intoxication of beauty and violence, and silent knight codes.",
    ),
    "celine_sciamma": ArchetypeInfo(
        slug="celine_sciamma",
        director_name="Céline Sciamma",
        title="The Painter of Intimate Gazes & Tacit Bond",
        quote="In cinema, to look is to give attention, and to give attention is an act of love.",
        visual_style="Patient observant mid-shots, natural daylight, flickering firelight, and organic soundscapes.",
        thematic_core="Female agency, the reciprocity of looking, memory as resistance, and unspoken emotional bonds.",
    ),
    "jordan_peele": ArchetypeInfo(
        slug="jordan_peele",
        director_name="Jordan Peele",
        title="The Architect of Social Allegory & Uncanny Horror",
        quote="The worst monster is the monster that is us.",
        visual_style="Creeping slow zoom-ins, uncomfortable character framing, subverted pop music, and stark night contrast.",
        thematic_core="Systemic trauma, double consciousness, subterranean conspiracies, and horror hiding in plain sight.",
    ),
    "alfonso_cuaron": ArchetypeInfo(
        slug="alfonso_cuaron",
        director_name="Alfonso Cuarón",
        title="The Virtuoso of Bravura Sequence Takes",
        quote="Every shot is a choice between truth and illusion.",
        visual_style="Extended uninterrupted sequence shots, 360-degree handheld tracking, deep-focus spatial geography.",
        thematic_core="Personal human resilience and empathy enduring amidst chaotic physical or historical turmoil.",
    ),
    "lars_von_trier": ArchetypeInfo(
        slug="lars_von_trier",
        director_name="Lars von Trier",
        title="The Provocateur of Unfiltered Realism & Endurance",
        quote="A film should be like a stone in your shoe.",
        visual_style="Dogme 95 handheld camera immediacy, jump cuts, raw available light, and diegetic sound only.",
        thematic_core="Provocative psychological endurance, martyrdom, and stripping away all cinematic comfort.",
    ),
    "paul_thomas_anderson": ArchetypeInfo(
        slug="paul_thomas_anderson",
        director_name="Paul Thomas Anderson",
        title="The Sculptor of Volatile Ambition & American Epics",
        quote="I like characters who are larger than life, fighting for their place in the world.",
        visual_style="Sweeping steadicam tracking shots, rich film grain warmth, jittery percussion, and ensemble dialogue.",
        thematic_core="Obsessive visionaries, surrogate family dynamics, fierce rivalries, and sweeping era portraits.",
    ),
    "greta_gerwig": ArchetypeInfo(
        slug="greta_gerwig",
        director_name="Greta Gerwig",
        title="The Champion of Witty Ambition & Nostalgic Voice",
        quote="I want to make films about female ambition that feel cinematic and joyfully alive.",
        visual_style="Warm golden-hour sunlight, rapid overlapping dialogue, rhythmic editing, and cozy tableaux.",
        thematic_core="Self-determination, female ambition, mother-daughter bonds, and the nostalgia of youth.",
    ),
}


QUIZ_QUESTIONS: List[QuizQuestion] = [
    QuizQuestion(
        id=1,
        prompt="How do you establish the mood in your film's opening 30 seconds?",
        category="atmospheric",
        options=[
            QuizOption(
                text="A perfectly centered, symmetrical wide shot of a meticulous room with pastel walls.",
                weights={"wes_anderson": 5, "paul_thomas_anderson": 1},
            ),
            QuizOption(
                text="A slow handheld glide through rain-slicked neon alleys with step-printed slow motion.",
                weights={"wong_kar_wai": 5, "nicolas_winding_refn": 2},
            ),
            QuizOption(
                text="A towering, brutalist architectural structure looming over a silent desert landscape.",
                weights={"denis_villeneuve": 5, "david_lynch": 1},
            ),
            QuizOption(
                text="Overlapping, fast-paced dialogue between two close friends eating breakfast.",
                weights={"greta_gerwig": 5, "celine_sciamma": 1},
            ),
        ],
    ),
    QuizQuestion(
        id=2,
        prompt="What camera movement best captures a critical emotional turning point?",
        category="atmospheric",
        options=[
            QuizOption(
                text="A sweeping 360-degree continuous tracking shot that never cuts away.",
                weights={"alfonso_cuaron": 5, "paul_thomas_anderson": 2},
            ),
            QuizOption(
                text="An unfiltered, shaky handheld jump-cut that feels raw and unscripted.",
                weights={"lars_von_trier": 5, "bong_joon_ho": 1},
            ),
            QuizOption(
                text="A slow, hypnotic push-in on an actor's face as the background blurs away.",
                weights={"celine_sciamma": 5, "wong_kar_wai": 2},
            ),
            QuizOption(
                text="A sudden, whip-pan snap zoom directly onto a character's shocked expression.",
                weights={"wes_anderson": 5, "bong_joon_ho": 2},
            ),
        ],
    ),
    QuizQuestion(
        id=3,
        prompt="What lighting style dominates your visual palette?",
        category="atmospheric",
        options=[
            QuizOption(
                text="High-contrast, saturated neon pinks and electric blues against pitch blackness.",
                weights={"nicolas_winding_refn": 5, "wong_kar_wai": 1},
            ),
            QuizOption(
                text="Flickering practical tungsten bulbs and dark chiaroscuro shadows with red curtains.",
                weights={"david_lynch": 5, "jordan_peele": 1},
            ),
            QuizOption(
                text="Soft, golden-hour window sunlight bathing cozy interior spaces.",
                weights={"greta_gerwig": 5, "celine_sciamma": 2},
            ),
            QuizOption(
                text="Monochromatic, volumetric shafts of light cutting through dusty, overcast skies.",
                weights={"denis_villeneuve": 5, "alfonso_cuaron": 1},
            ),
        ],
    ),
    QuizQuestion(
        id=4,
        prompt="What sound dominates your film's tensest sequence?",
        category="atmospheric",
        options=[
            QuizOption(
                text="A low, unsettling industrial hum coupled with a buzzing fluorescent light.",
                weights={"david_lynch": 5, "jordan_peele": 2},
            ),
            QuizOption(
                text="Pulsating synthwave basslines and heavy rhythmic breathing.",
                weights={"nicolas_winding_refn": 5, "wong_kar_wai": 1},
            ),
            QuizOption(
                text="Raw, unedited ambient room tone with zero background music.",
                weights={"lars_von_trier": 5, "celine_sciamma": 2},
            ),
            QuizOption(
                text="A sudden, shocking tonal drop from jaunty orchestral music into dead silence.",
                weights={"bong_joon_ho": 5, "jordan_peele": 2},
            ),
        ],
    ),
    QuizQuestion(
        id=5,
        prompt="What core philosophy drives your central conflict?",
        category="atmospheric",
        options=[
            QuizOption(
                text="Societal structures and class inequality dictate human desperation.",
                weights={"bong_joon_ho": 5, "jordan_peele": 2},
            ),
            QuizOption(
                text="Hidden historical trauma and social anxiety manifest as subterranean conspiracies.",
                weights={"jordan_peele": 5, "david_lynch": 2},
            ),
            QuizOption(
                text="Growing up means balancing fierce personal ambition with love for family roots.",
                weights={"greta_gerwig": 5, "paul_thomas_anderson": 1},
            ),
            QuizOption(
                text="Reckless, larger-than-life visionaries clash in an epic battle of wills and obsession.",
                weights={"paul_thomas_anderson": 5, "alfonso_cuaron": 1},
            ),
        ],
    ),
    QuizQuestion(
        id=6,
        prompt="Your main actor is struggling to find the right emotion for a key scene. How do you direct them?",
        category="on-set",
        options=[
            QuizOption(
                text="Give them strict physical cues and deadpan timing—let the frame and dialogue do the work.",
                weights={"wes_anderson": 5, "greta_gerwig": 1},
            ),
            QuizOption(
                text="Whisper an ambiguous, enigmatic phrase about a dream and let them improvise.",
                weights={"david_lynch": 5, "wong_kar_wai": 2},
            ),
            QuizOption(
                text="Push them into raw, unglamorized physical vulnerability until all artificial acting drops away.",
                weights={"lars_von_trier": 5, "celine_sciamma": 1},
            ),
            QuizOption(
                text="Walk them through the spatial geometry of the shot and how their body moves relative to the camera.",
                weights={"alfonso_cuaron": 5, "denis_villeneuve": 2},
            ),
        ],
    ),
    QuizQuestion(
        id=7,
        prompt="How do you handle dialogue during an intense conversation?",
        category="on-set",
        options=[
            QuizOption(
                text="Witty, overlapping, rapid-fire chatter where characters interrupt each other constantly.",
                weights={"greta_gerwig": 5, "paul_thomas_anderson": 2},
            ),
            QuizOption(
                text="Minimal dialogue—let long silent gazes and subtle body language carry the subtext.",
                weights={"celine_sciamma": 5, "nicolas_winding_refn": 2},
            ),
            QuizOption(
                text="Poetic voiceover monologues echoing over rain-soaked urban montages.",
                weights={"wong_kar_wai": 5, "david_lynch": 1},
            ),
            QuizOption(
                text="Deadpan, perfectly timed delivery with zero emotion expressed on surface faces.",
                weights={"wes_anderson": 5, "lars_von_trier": 1},
            ),
        ],
    ),
    QuizQuestion(
        id=8,
        prompt="You are running 45 minutes behind schedule with 10 minutes of sunlight left. What do you do?",
        category="on-set",
        options=[
            QuizOption(
                text="Pivot to a single, uninterrupted long tracking shot that captures the entire scene in one master take.",
                weights={"alfonso_cuaron": 5, "paul_thomas_anderson": 2},
            ),
            QuizOption(
                text="Embrace natural lighting and intimate close-ups of actors' expressions, cutting all unnecessary coverage.",
                weights={"celine_sciamma": 5, "lars_von_trier": 2},
            ),
            QuizOption(
                text="Stick strictly to the pre-drawn storyboard grid—exact camera positions are non-negotiable.",
                weights={"wes_anderson": 5, "denis_villeneuve": 2},
            ),
            QuizOption(
                text="Lean into the chaos and throw in a sudden genre shift or dark comedic twist.",
                weights={"bong_joon_ho": 5, "jordan_peele": 2},
            ),
        ],
    ),
    QuizQuestion(
        id=9,
        prompt="What location setting inspires your story the most?",
        category="on-set",
        options=[
            QuizOption(
                text="A stark, brutalist concrete bunker or desolate alien-like desert landscape.",
                weights={"denis_villeneuve": 5, "nicolas_winding_refn": 1},
            ),
            QuizOption(
                text="A sprawling period backdrop filled with eccentric, ambitious oilmen, cult leaders, or showmen.",
                weights={"paul_thomas_anderson": 5, "alfonso_cuaron": 1},
            ),
            QuizOption(
                text="A seemingly peaceful suburban neighborhood hiding a terrifying secret underneath.",
                weights={"jordan_peele": 5, "david_lynch": 2},
            ),
            QuizOption(
                text="A rain-drenched noodle bar in a crowded, neon-lit alleyway.",
                weights={"wong_kar_wai": 5, "nicolas_winding_refn": 2},
            ),
        ],
    ),
    QuizQuestion(
        id=10,
        prompt="What feeling do you want the audience to walk away with when the credits roll?",
        category="on-set",
        options=[
            QuizOption(
                text="A sense of awe at the vastness of the universe and the weight of human destiny.",
                weights={"denis_villeneuve": 5, "alfonso_cuaron": 2},
            ),
            QuizOption(
                text="Hypnotic, visceral thrill and aesthetic intoxication from color and rhythm.",
                weights={"nicolas_winding_refn": 5, "wong_kar_wai": 1},
            ),
            QuizOption(
                text="A provocative, unsettling shock that forces them to question societal morality.",
                weights={"lars_von_trier": 5, "jordan_peele": 2},
            ),
            QuizOption(
                text="A bittersweet smile, feeling deeply understood and connected to human warmth.",
                weights={"greta_gerwig": 5, "celine_sciamma": 2},
            ),
        ],
    ),
]


class QuizEngine:
    """Core calculation engine for evaluating quiz responses and identifying the winning director archetype."""

    @staticmethod
    def get_archetype_info(slug: str) -> Optional[ArchetypeInfo]:
        """Return ArchetypeInfo metadata for a given director slug."""
        return ARCHETYPE_LIBRARY.get(slug)

    @staticmethod
    def calculate_result(answers: Dict[int, int]) -> QuizResult:
        """Calculate score tally across selected options and return the winning QuizResult.

        Args:
            answers: Dictionary mapping question_id (1-based) to selected option index (0-based).
        """
        scores: Dict[str, int] = {slug: 0 for slug in ARCHETYPE_LIBRARY.keys()}

        for q in QUIZ_QUESTIONS:
            selected_idx = answers.get(q.id)
            if selected_idx is not None and 0 <= selected_idx < len(q.options):
                opt = q.options[selected_idx]
                for slug, weight in opt.weights.items():
                    if slug in scores:
                        scores[slug] += weight

        # Sort directors by score descending, with deterministic tie-breaking by slug
        sorted_scores = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        winner_slug = sorted_scores[0][0] if sorted_scores else "wes_anderson"
        winner_info = ARCHETYPE_LIBRARY.get(winner_slug, ARCHETYPE_LIBRARY["wes_anderson"])

        return QuizResult(
            winner_slug=winner_slug,
            winner_info=winner_info,
            scores=scores,
        )
