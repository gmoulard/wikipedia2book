import json
from pathlib import Path
from threading import RLock
from uuid import UUID

from app.models import Project


class JsonProjectStore:
    def __init__(self, directory: str | Path = "data/projects") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()

    def _project_path(self, project_id: str) -> Path | None:
        try:
            safe_id = str(UUID(project_id))
        except (ValueError, TypeError, AttributeError):
            return None
        return self.directory / f"{safe_id}.json"

    def list(self) -> list[Project]:
        with self._lock:
            projects = [
                Project.model_validate_json(path.read_text(encoding="utf-8"))
                for path in self.directory.glob("*.json")
            ]
        return sorted(projects, key=lambda project: project.updated_at, reverse=True)

    def get(self, project_id: str) -> Project | None:
        path = self._project_path(project_id)
        if path is None or not path.is_file():
            return None
        with self._lock:
            return Project.model_validate_json(path.read_text(encoding="utf-8"))

    def save(self, project: Project) -> Project:
        path = self._project_path(project.id)
        if path is None:
            raise ValueError("Identifiant de projet invalide.")
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = path.with_suffix(".tmp")
        data = json.dumps(project.model_dump(mode="json"), ensure_ascii=False, indent=2)
        with self._lock:
            temporary_path.write_text(data, encoding="utf-8")
            temporary_path.replace(path)
        return project

    def delete(self, project_id: str) -> bool:
        path = self._project_path(project_id)
        if path is None:
            return False
        with self._lock:
            try:
                path.unlink()
            except FileNotFoundError:
                return False
        return True
