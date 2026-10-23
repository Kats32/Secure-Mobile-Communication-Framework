# Presentation deliverables

- `Secure_Mobile_Communication_Framework_BTP.pptx` — final 28-slide deck.
- `PRESENTATION_IMAGE_CAPTIONS.md` — slide captions and detailed attack-result explanations.
- `PROJECT_EXPLANATION.md` and `PROJECT_EXPLANATION.pdf` — project overview in editable and shareable formats.
- `build_btp_presentation.py` — source script for rebuilding the deck.
- `capture_attack_results.py` and `attack_results/` — isolated current-GUI captures used by the deck.
- `export_project_explanation.py` — refreshes the explanation PDF from its Markdown source.

The builder reads the source report, BTP template, and architecture diagrams from the project root and writes the PowerPoint into this folder. Run from the repository root:

```bash
python presentation/build_btp_presentation.py
```

To refresh the three attack-result screenshots, run `python presentation/capture_attack_results.py`. It creates a temporary account and server under a temporary directory, then saves the current dialogs under `attack_results/`.
