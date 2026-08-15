# 🎬 48HFP-Studio
![Version](https://img.shields.io/badge/version-v3.0.0-blue.svg) ![UI](https://img.shields.io/badge/UI-Textual-lightgrey.svg) ![AI](https://img.shields.io/badge/AI-Gemini%203.7%20Flash-orange.svg) ![Data](https://img.shields.io/badge/Data-Pandas-green.svg)

**48HFP-Studio** is a terminal-native AI co-pilot designed to streamline pre-production for short film festivals like the 48 Hour Film Project. Built entirely for the terminal using Textual and powered by the Google Gemini API, this tool orchestrates everything from your initial Friday Night Kickoff Draw to a finalized script, CSV shot list, and rendered pre-vis storyboards.

---

## ✨ Features

*   **Terminal-Native Interface**: A fast, keyboard-navigable Terminal User Interface (TUI) featuring split-pane workspaces, pop-up modals, and syntax-highlighted viewers.
*   **The Friday Night Draw Wizard**: Instantly capture your festival requirements, including primary/secondary genres, character traits, required props, and verbatim dialogue lines.
*   **Tri-Split Constraint Management**: Build and toggle Logistical Constraints (locations, cast), Directorial Visions (visual economy, lighting, audio), and Thematic Frameworks (core philosophy, emotional arcs).
*   **Filmmaker Personality Quiz**: Take a 10-question interactive quiz to discover your Director Archetype (from Wes Anderson to Jordan Peele) and automatically prime your creative constraints.
*   **Iterative Treatment Generator**: Generate a 6-part film treatment complete with a Festival Compliance Checklist ensuring your film fits the strict 4-to-7 minute runtime.
*   **The Screenplay Engine**: Seamlessly adapt your treatment into a production-ready short film script, exported safely in pure `.fountain` markup.
*   **StudioBinder Shot Lists**: Automatically break your screenplay down into a structured, scene-by-scene camera shot list, rendered natively in a `DataTable` and exported to `.csv` via `pandas`.
*   **Pre-Vis Storyboards**: Utilize the `gemini-3.1-flash-lite-image` model to automatically generate 16:9 monochrome, Hollywood-style storyboard sketches for every shot in your shot list.
*   **Safe-Write Versioning**: All outputs (treatments, screenplays, and shot lists) are automatically saved to your active workspace using a zero-padded, non-overwrite versioning system (e.g., `v01`, `v02`).

---

## 🚀 Installation

Ensure you have Python 3.12+ installed.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/AMBloom/48hfp-studio.git](https://github.com/AMBloom/48hfp-studio.git)
   cd 48hfp-studio
   ```

2. **Install dependencies:**
   The project relies on `google-genai`, `textual`, `pydantic`, `pandas`, and `pyyaml`.
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Environment:**
   You must have a valid Gemini API Key to use the generative features.
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   export GEMINI_MODEL="gemini-3.7-flash"
   ```
   *Alternatively, you can configure your API settings directly inside the application's TUI via the `[S] Settings` menu, which will automatically persist to a local `.env` file.*

---

## 🎮 Usage

Launch the main Terminal User Interface (TUI):
```bash
48hfp
```

### Navigating the TUI

*   `[W] Workspace Manager`: Initialize a new project directory to safely store your assets.
*   `[P] Profile Setup`: Onboard your team's cast, crew, and available gear.
*   `[D] Friday Draw`: Record your festival requirements immediately after kickoff.
*   `[G] Generate Treatment`: Compile your constraints and run the LLM inference engine.
*   `[S] Generate Screenplay`: Adapt the active treatment into a `.fountain` screenplay.
*   `[T] Generate Shot List`: Extract a StudioBinder formatted breakdown.
*   `[O] Load Drafts`: Browse and reload any previously saved treatments, scripts, or shot lists.

### CLI Commands

For fast operations outside the TUI, you can use the CLI subcommands:

*   `48hfp workspace init <path>`: Create a new portable project workspace.
*   `48hfp config setup`: Run the interactive team onboarding wizard.
*   `48hfp draw wizard`: Run the interactive Friday Night Draw wizard.
*   `48hfp constraints list`: View all active logistical and creative constraints.
*   `48hfp info`: View current system status, loaded workspace, and profile state.

---

## 📁 Workspace Architecture

When you initialize a project workspace, the application automatically builds the following directory structure to keep your short film strictly organized:

```text
your_workspace/
├── profile.yaml             # Your team's cast, crew, and gear roster
├── draw.yaml                # The required festival elements
├── constraints/             # Saved YAML files for locations and creative direction
├── outputs/                 # Versioned markdown film treatments
├── screenplays/             # Versioned .fountain screenplays
├── assets/                  # Exported .csv shot lists
└── storyboards/             # Generated .png pre-vis storyboard frames
```

---

## ©️ Ownership, Authorship, and License

**48HFP-Studio** is authored and maintained by Andrew Bloom.

**License & Usage Terms:**
This software is provided free of charge and is open for personal and commercial use, subject to the following conditions:

* **Software Attribution**: You are free to use, modify, and distribute the application itself, provided that explicit attribution is given to the original author.
* **Derivative Works**: The author makes no claim of copyright or ownership over any derivative works generated using this application. All generated creative assets (including film treatments, screenplays, shot lists, storyboards, and the finalized films) belong entirely and exclusively to the user.
* **Credit Requirement**: If you utilize 48HFP-Studio during the pre-production or production phase of a film, you are required to provide attribution within the project's final credits. (e.g., *"Pre-production AI Co-Pilot: 48HFP-Studio by Andrew Bloom"* or similar).
