from __future__ import annotations

import json
from pathlib import Path

from backend.db import SessionLocal, ensure_data_dir
from backend.models import Idea


def main() -> None:
    ensure_data_dir()
    db = SessionLocal()
    try:
        samples = [
            (
                "Mapa de cafeterías indie",
                "Un mapa interactivo de cafeterías independientes con reseñas de la comunidad.",
                ["mapas", "comunidad", "coffee"],
            ),
            (
                "Generador de paletas AI",
                "Herramienta que sugiere paletas de colores a partir de una imagen.",
                ["ia", "ux", "colores"],
            ),
            (
                "Radio de foco",
                "Una playlist infinita que minimiza distracciones según tu horario.",
                ["audio", "productividad"],
            ),
        ]
        for title, desc, tags in samples:
            idea = Idea(title=title, description=desc, tags_json=json.dumps(tags), likes=0)
            db.add(idea)
        db.commit()
        print("Seed completado ✅")
    finally:
        db.close()


if __name__ == "__main__":
    main()

