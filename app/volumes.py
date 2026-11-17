# This file is part of Wikipedia2Book
# <https://github.com/gmoulard/wikipedia2book>.
# Copyright (c) 2026 Guillaume Moulard.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass

from app.book_builder import pdf_label
from app.models import Article, Project, UploadedDocument

BookItem = Article | UploadedDocument


@dataclass
class Slot:
    kind: str
    anchor: str
    item: BookItem | None = None
    chapter_id: str = ""
    chapter_articles: int = 0


def selected_items(project: Project) -> list[BookItem]:
    return [item for item in project.main_articles + project.discovered_articles + project.uploaded_documents if item.selected]


# NE PAS modifier sans aligner buildOrgSlots, volumeStarts, articleSegments et planVolumes dans app.js : l'interface et l'API doivent découper les mêmes volumes.
def content_slots(project: Project, items: list[BookItem]) -> list[Slot]:
    by_key = {item.key: item for item in items}
    ordered = [by_key[key] for key in project.article_order if key in by_key]
    seen = {item.key for item in ordered}
    ordered.extend(item for item in items if item.key not in seen)
    chapter_of = {key: chapter.id for chapter in project.chapters for key in chapter.article_keys}
    chapter_ids = {chapter.id for chapter in project.chapters}
    members: dict[str, list[BookItem]] = {chapter.id: [] for chapter in project.chapters}
    unassigned: list[BookItem] = []
    for item in ordered:
        chapter_id = chapter_of.get(item.key)
        (members[chapter_id] if chapter_id in chapter_ids else unassigned).append(item)
    chapter_slots: list[Slot] = []
    for chapter in project.chapters:
        chapter_slots.append(Slot("chapter", f"chapter:{chapter.id}", chapter_id=chapter.id, chapter_articles=len(members[chapter.id])))
        chapter_slots.extend(Slot("article", item.key, item, chapter.id) for item in members[chapter.id])
    unassigned_slots = [Slot("article", item.key, item) for item in unassigned]
    if project.chapters and unassigned and not project.unassigned_first:
        unassigned_slots.insert(0, Slot("unassigned", "chapter:"))
    return unassigned_slots + chapter_slots if project.unassigned_first else chapter_slots + unassigned_slots


# NE PAS compter une coupure sur le premier élément ou sur un chapitre sans article : elle ne séparerait aucun article.
def volume_starts(project: Project, slots: list[Slot]) -> list[int]:
    starts: set[int] = set()
    anchors = [slot.anchor for slot in slots]
    for position in project.volume_breaks:
        anchor = position.removeprefix("before:")
        if anchor not in anchors:
            continue
        index = anchors.index(anchor)
        slot = slots[index]
        if index > 0 and not (slot.kind == "chapter" and not slot.chapter_articles):
            starts.add(index)
    return sorted(starts)


def article_segments(project: Project, slots: list[Slot]) -> list[list[Slot]]:
    bounds = [0, *volume_starts(project, slots), len(slots)]
    segments = []
    for start, end in zip(bounds, bounds[1:]):
        articles = [slot for slot in slots[start:end] if slot.kind == "article"]
        if articles:
            segments.append(articles)
    return segments


def counts_toward_limit(item: BookItem) -> bool:
    return isinstance(item, Article)


# NE PAS couper un chapitre tant qu'il tient dans un volume : la coupure se fait entre deux chapitres, et à l'intérieur d'un chapitre seulement s'il dépasse la limite à lui seul.
def plan_volumes(limit: int, slots: list[Slot]) -> list[list[BookItem]]:
    units: list[tuple[str, list[BookItem]]] = []
    for slot in slots:
        if units and units[-1][0] == slot.chapter_id:
            units[-1][1].append(slot.item)
        else:
            units.append((slot.chapter_id, [slot.item]))
    volumes: list[list[BookItem]] = []
    current: list[BookItem] = []
    count = 0
    for _, items in units:
        if count + sum(map(counts_toward_limit, items)) > limit and current:
            volumes.append(current)
            current, count = [], 0
        for item in items:
            if counts_toward_limit(item) and count >= limit and current:
                volumes.append(current)
                current, count = [], 0
            current.append(item)
            count += counts_toward_limit(item)
    if current:
        volumes.append(current)
    return volumes


# NE PAS faire passer le découpage automatique avant les coupures de l'utilisateur : elles délimitent d'abord les volumes, puis chaque volume encore trop gros est découpé.
def book_volumes(project: Project, limit: int | None) -> list[list[BookItem]]:
    segments = article_segments(project, content_slots(project, selected_items(project)))
    return [volume for segment in segments for volume in (plan_volumes(limit, segment) if limit else [[slot.item for slot in segment]])]


def default_title(project: Project) -> str:
    ordered = [slot.item for slot in content_slots(project, selected_items(project)) if slot.kind == "article"]
    first = next((item for item in ordered if isinstance(item, Article)), ordered[0] if ordered else None)
    return first.title if first else ""


def volume_project(project: Project, items: list[BookItem], index: int, total: int, language: str) -> Project:
    keys = {item.key for item in items}
    copy = project.model_copy(deep=True)
    copy.uploaded_documents = [document for document in copy.uploaded_documents if document.key in keys]
    for article in copy.main_articles + copy.discovered_articles:
        article.selected = article.key in keys
    title = (project.book_title or default_title(project) or project.name)[:170]
    copy.book_title = pdf_label(language, "volume_title", title=title, index=str(index + 1), count=str(total))[:200]
    if index > 0:
        copy.introduction = ""
    if index < total - 1:
        copy.conclusion = ""
    return copy
