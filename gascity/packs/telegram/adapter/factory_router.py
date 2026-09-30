"""Project routing for the software factory: desks, topics, and gated replies.

One rig is one project, and each project has its own Gas City conversation
whose id is the rig name. Every roster member gets a topic named after the
project in their desk — a Telegram supergroup with Topics where the bot is an
admin — and all project traffic lands in those topics. A topic is closed while
the agents work and reopened only when an agent asks that person something;
a message that arrives while nothing is being asked is refused here rather
than forwarded, so nobody is left believing a stray remark reached the agent.
People without a desk get the same conversation in their bot's DM, with the
same gate applied on this side since a DM cannot be closed.

The router decides only who to ask and whether a reply is expected. What is
asked, and what the answer means, belongs to the agents.
"""

from __future__ import annotations

import html
import hashlib
import json
import logging
import os
import re
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import github_delivery as gd
import weaver_client as wc

log = logging.getLogger("factory")

PROVIDER = "telegram"
CONVERSATION_KIND = "room"
SCOPE_ID = "city"

APPROVE_PREFIX = "a:"
REJECT_PREFIX = "r:"

# Protocol lines the pack's agents open a message with. Everything else is a
# note for the whole roster.
QUESTIONS_TAG = "QUESTIONS:"
APPROVAL_TAG = "APPROVAL_NEEDED:"
DELIVER_TAG = "DELIVER:"

# What the bridge sends back to the agent when it was asked to publish and
# cannot. DELIVERY_UNAVAILABLE means no credential is configured at all;
# DELIVERY_FAILED means it tried and GitHub or git refused.
DELIVERY_UNAVAILABLE = (
    "DELIVERY_UNAVAILABLE: this bridge has no GitHub token, so it cannot "
    "publish. The repository is complete in its rig."
)
DeliveryError = gd.DeliveryError


def esc(text: str) -> str:
    """Escape text for Telegram's HTML parse mode."""
    return html.escape(text, quote=False)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RosterError(ValueError):
    """A project roster names someone or something the bridge cannot route to."""


class WeaverRegistrationError(RuntimeError):
    """A requested Weaver link could not be established."""


# --- Model ---------------------------------------------------------------------


@dataclass
class Roster:
    """Who is on a project and what each person is responsible for."""

    members: dict[str, list[str]]
    admins: list[str]

    @classmethod
    def from_doc(cls, doc: dict[str, Any], known_users: set[str]) -> "Roster":
        members = {name: list(resps) for name, resps in (doc.get("members") or {}).items()}
        if not members:
            raise RosterError("roster has no members")
        unknown = sorted(set(members) - known_users)
        if unknown:
            raise RosterError(f"roster names people missing from responsibilities.json: {', '.join(unknown)}")
        admins = [name for name in (doc.get("admins") or []) if name in members]
        return cls(members=members, admins=admins or list(members)[:1])

    def holders(self, responsibility: str) -> list[str]:
        return [name for name, resps in self.members.items() if responsibility in resps]

    def to_doc(self) -> dict[str, Any]:
        return {"members": self.members, "admins": self.admins}


@dataclass
class Project:
    """One rig, its workflow, its people, and where each of them is reached."""

    name: str
    rig: str
    workflow_id: str
    roster: Roster
    # user -> {"chat_id": desk supergroup, "thread_id": topic}
    topics: dict[str, dict[str, int]] = field(default_factory=dict)
    # user -> {"kind": "question" | "approval", "asked_at": iso}
    awaiting: dict[str, dict[str, str]] = field(default_factory=dict)
    phase: str | None = None
    reported_closed: list[str] = field(default_factory=list)
    # Weaver phases whose approval has already been delivered to Gas City.
    forwarded_weaver_approvals: list[str] = field(default_factory=list)
    # Phases whose terminal summary must remain Weaver's latest assistant turn.
    weaver_terminal_summaries: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=now_iso)
    # The extmsg account the bridge registered as; every project shares it.
    account_id: str = "factory"
    # Optional Dyad/Weaver app mirrored and delegated through the bridge.
    weaver_app_id: int | None = None

    def conversation(self) -> dict[str, str]:
        return {
            "provider": PROVIDER,
            "account_id": self.account_id,
            "conversation_id": self.rig,
            "scope_id": SCOPE_ID,
            "kind": CONVERSATION_KIND,
        }

    def to_doc(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "rig": self.rig,
            "workflow_id": self.workflow_id,
            "account_id": self.account_id,
            "weaver_app_id": self.weaver_app_id,
            "roster": self.roster.to_doc(),
            "topics": self.topics,
            "awaiting": self.awaiting,
            "phase": self.phase,
            "reported_closed": self.reported_closed,
            "forwarded_weaver_approvals": self.forwarded_weaver_approvals,
            "weaver_terminal_summaries": self.weaver_terminal_summaries,
            "created_at": self.created_at,
        }

    @classmethod
    def from_doc(cls, doc: dict[str, Any], known_users: set[str]) -> "Project":
        return cls(
            name=doc["name"],
            rig=doc["rig"],
            workflow_id=doc["workflow_id"],
            roster=Roster.from_doc(doc["roster"], known_users),
            topics={u: {"chat_id": int(t["chat_id"]), "thread_id": int(t["thread_id"])} for u, t in (doc.get("topics") or {}).items()},
            awaiting=dict(doc.get("awaiting") or {}),
            phase=doc.get("phase"),
            reported_closed=list(doc.get("reported_closed") or []),
            forwarded_weaver_approvals=list(
                doc.get("forwarded_weaver_approvals") or []
            ),
            weaver_terminal_summaries=list(
                doc.get("weaver_terminal_summaries") or []
            ),
            created_at=doc.get("created_at") or now_iso(),
            account_id=doc.get("account_id") or "factory",
            weaver_app_id=doc.get("weaver_app_id"),
        )


class ProjectStore:
    """Projects on disk, one JSON file each, written atomically."""

    def __init__(self, directory: str) -> None:
        self.directory = directory
        os.makedirs(directory, exist_ok=True)

    def _path(self, name: str) -> str:
        return os.path.join(self.directory, f"{name}.json")

    def save(self, project: Project) -> None:
        target = self._path(project.name)
        tmp = f"{target}.tmp.{os.getpid()}"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(project.to_doc(), fh, indent=2, sort_keys=True)
        os.replace(tmp, target)

    def load_all(self, known_users: set[str] | None = None) -> list[Project]:
        projects = []
        for entry in sorted(os.listdir(self.directory)):
            if not entry.endswith(".json"):
                continue
            with open(os.path.join(self.directory, entry), encoding="utf-8") as fh:
                doc = json.load(fh)
            projects.append(Project.from_doc(doc, known_users if known_users is not None else set((doc.get("roster") or {}).get("members") or {})))
        return projects


@dataclass
class PendingApproval:
    """One open approval on a project and the votes cast on it."""

    project: str
    responsibility: str
    title: str
    detail: str
    required: int
    asked: list[str]
    weaver_phase: str
    approvals: set[str] = field(default_factory=set)
    resolved: bool = False
    # (user, chat_id, message_id) so every copy can lose its buttons on resolve.
    messages: list[tuple[str, int, int]] = field(default_factory=list)


# --- Parsing ---------------------------------------------------------------------


def parse_publish(text: str) -> tuple[str, str, str]:
    """Classify one agent message: (kind, subject, body).

    kind is questions | approval | deliver | note. For questions the subject
    is the responsibility and the body the numbered rounds; for approval the
    subject is the responsibility and the body "title | detail"; for deliver
    the subject is the visibility.
    """
    stripped = text.strip()
    if stripped.startswith(QUESTIONS_TAG):
        head, _, body = stripped[len(QUESTIONS_TAG):].partition("\n")
        return "questions", head.strip(), body.strip()
    if stripped.startswith(APPROVAL_TAG):
        parts = [p.strip() for p in stripped[len(APPROVAL_TAG):].split("|")]
        return "approval", parts[0], " | ".join(parts[1:])
    if stripped.startswith(DELIVER_TAG):
        return "deliver", stripped[len(DELIVER_TAG):].strip(), ""
    return "note", "", stripped


PROJECT_PREFIX = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9_.-]*)\s*:\s*(.*)$", re.DOTALL)


# --- Router -----------------------------------------------------------------------


class FactoryRouter:
    """Routes project traffic between agents and the people on the roster."""

    def __init__(self, users: dict[str, dict[str, Any]], responsibilities: dict[str, dict[str, Any]],
                 account_id: str, tg: Any, gc: Any, store: ProjectStore,
                 delivery: gd.GitHubDelivery | None = None,
                 weaver: wc.WeaverClient | None = None) -> None:
        self.users = users
        self.responsibilities = responsibilities
        self.account_id = account_id
        self.tg = tg
        self.gc = gc
        self.store = store
        self.delivery = delivery
        self.weaver = weaver
        self.lock = threading.RLock()
        self.pending: dict[str, PendingApproval] = {}
        self.projects: dict[str, Project] = {p.name: p for p in store.load_all(set(users))}

    # --- lookups ---

    def project_for_conversation(self, conversation_id: str) -> Project | None:
        with self.lock:
            for project in self.projects.values():
                if project.rig == conversation_id:
                    return project
        return None

    def project_for_topic(self, chat_id: int, thread_id: int | None) -> tuple[Project, str] | None:
        if thread_id is None:
            return None
        with self.lock:
            for project in self.projects.values():
                for user, topic in project.topics.items():
                    if topic["chat_id"] == chat_id and topic["thread_id"] == thread_id:
                        return project, user
        return None

    def _desk(self, user: str) -> int | None:
        desk = self.users.get(user, {}).get("desk_chat_id")
        return int(desk) if desk else None

    def _dm(self, user: str) -> int:
        return int(self.users[user]["telegram_id"])

    def snapshot(self) -> list[dict[str, Any]]:
        with self.lock:
            return [p.to_doc() for p in self.projects.values()]

    # --- lifecycle ---

    def register(self, name: str, rig: str, workflow_id: str, roster: dict[str, Any],
                 weaver_app_id: int | None = None) -> Project:
        """Create the project's topics (or DM intros) and remember it."""
        project = Project(name=name, rig=rig, workflow_id=workflow_id,
                          roster=Roster.from_doc(roster, set(self.users)), account_id=self.account_id,
                          weaver_app_id=weaver_app_id)
        with self.lock:
            if name in self.projects:
                raise KeyError(f"project {name!r} already exists; use restart")
            if weaver_app_id is not None:
                if self.weaver is None:
                    raise WeaverRegistrationError(
                        "project requested a Weaver app, but WEAVER_BASE_URL and "
                        "WEAVER_API_KEY are not configured on the bridge"
                    )
                try:
                    self.weaver.link(weaver_app_id, name)
                except wc.WeaverError as exc:
                    raise WeaverRegistrationError(str(exc)) from exc
            self._open_rooms(project)
            self.projects[name] = project
            self.store.save(project)
        return project

    def restart(self, name: str, workflow_id: str) -> Project:
        """Throw the project's topics away, make fresh ones, forget open asks."""
        with self.lock:
            old = self.projects[name]
            for user, topic in old.topics.items():
                try:
                    self.tg.delete_forum_topic(user, topic["chat_id"], topic["thread_id"])
                except Exception:
                    log.exception("deleting topic for %s in project %s", user, name)
            for approval_id, pending in list(self.pending.items()):
                if pending.project == name:
                    del self.pending[approval_id]
            project = Project(name=name, rig=old.rig, workflow_id=workflow_id, roster=old.roster,
                              account_id=self.account_id, weaver_app_id=old.weaver_app_id,
                              forwarded_weaver_approvals=list(old.forwarded_weaver_approvals),
                              weaver_terminal_summaries=list(old.weaver_terminal_summaries))
            self._open_rooms(project)
            self.projects[name] = project
            self.store.save(project)
        return project

    def _open_rooms(self, project: Project) -> None:
        intro = (
            f"<b>{esc(project.name)}</b> is starting. Agents will ask here when they need "
            "you; until then the room stays closed."
        )
        for user in project.roster.members:
            desk = self._desk(user)
            if desk is None:
                self.tg.send(user, self._dm(user), intro)
                continue
            thread_id = self.tg.create_forum_topic(user, desk, project.name)
            project.topics[user] = {"chat_id": desk, "thread_id": thread_id}
            self.tg.send(user, desk, intro, thread_id=thread_id)
            self.tg.close_forum_topic(user, desk, thread_id)

    # --- delivery primitives ---

    def _send(self, project: Project, user: str, text: str, buttons: list | None = None) -> tuple[int, int]:
        topic = project.topics.get(user)
        if topic:
            message_id = self.tg.send(user, topic["chat_id"], text, buttons, thread_id=topic["thread_id"])
            return topic["chat_id"], message_id
        chat = self._dm(user)
        return chat, self.tg.send(user, chat, text, buttons)

    def _open(self, project: Project, user: str, kind: str) -> None:
        topic = project.topics.get(user)
        if topic:
            self.tg.reopen_forum_topic(user, topic["chat_id"], topic["thread_id"])
        project.awaiting[user] = {"kind": kind, "asked_at": now_iso()}

    def _close(self, project: Project, user: str) -> None:
        project.awaiting.pop(user, None)
        topic = project.topics.get(user)
        if topic:
            self.tg.close_forum_topic(user, topic["chat_id"], topic["thread_id"])

    def _broadcast(self, project: Project, text: str) -> None:
        for user in project.roster.members:
            try:
                self._send(project, user, text)
            except Exception:
                log.exception("broadcasting to %s in %s", user, project.name)

    def _label(self, responsibility: str) -> str:
        spec = self.responsibilities.get(responsibility, {})
        icon = spec.get("icon", "")
        name = spec.get("name", responsibility.replace("_", " "))
        return f"{esc(icon)} <b>{esc(name)}</b>".strip()

    # --- agent -> humans ---

    def on_publish(self, project: Project, text: str, session_id: str) -> None:
        """Deliver one agent message to the right people on the project."""
        kind, subject, body = parse_publish(text)
        with self.lock:
            weaver_phase = self._weaver_phase(project.phase)
            mirror_content = self._weaver_publish_content(
                kind, subject, body, weaver_phase, text,
            )
            if mirror_content is not None:
                self._mirror(
                    project, weaver_phase, "assistant", mirror_content,
                    self._idempotency_key(
                        "publish", project.name, session_id, text,
                    ),
                )
            if kind == "questions":
                self._ask_questions(project, subject, body)
            elif kind == "approval":
                self._ask_approval(project, subject, body)
            elif kind == "deliver":
                self._deliver(project, subject, session_id)
            else:
                self._broadcast(project, esc(body))
            self.store.save(project)

    @staticmethod
    def _weaver_publish_content(kind: str, subject: str, body: str,
                                phase: str, original: str) -> str | None:
        """Render protocol messages as summaries only on the Weaver side."""
        if kind == "deliver":
            # Completion depends on the publish result, which _deliver mirrors.
            return None
        heading = None
        label = None
        if kind == "approval" and phase == "discovery" and subject == "requirements":
            heading = "Discovery"
            label = "Requirements approval requested"
        elif kind == "approval" and phase == "implementation" and subject == "code_review":
            heading = "Implementation"
            label = "Code review requested"
        if heading is None or label is None:
            return original
        title, _, detail = body.partition(" | ")
        title = " ".join(title.split()) or "Review the completed phase"
        detail = " ".join(detail.split()) or "The phase is ready for approval."
        return (
            f"## {heading} summary\n"
            f"- {label}: {title}\n"
            f"- {detail}"
        )

    def _recipients(self, project: Project, responsibility: str) -> tuple[list[str], str]:
        holders = project.roster.holders(responsibility)
        if holders:
            return holders, ""
        note = (
            f"The agent asked for <b>{esc(responsibility)}</b>, but nobody on this project "
            "holds that responsibility. As an admin, please answer in their place or fix roster.json."
        )
        return list(project.roster.admins), note

    def _ask_questions(self, project: Project, responsibility: str, body: str) -> None:
        recipients, note = self._recipients(project, responsibility)
        header = f"{self._label(responsibility)} — questions\n\n" if not note else note + "\n\n"
        for user in recipients:
            self._open(project, user, "question")
            self._send(project, user, header + esc(body) + "\n\n<i>Reply here. The room closes again once you have answered.</i>")

    def _ask_approval(self, project: Project, responsibility: str, body: str) -> None:
        title, _, detail = body.partition(" | ")
        recipients, note = self._recipients(project, responsibility)
        spec = self.responsibilities.get(responsibility, {})
        required = int(spec.get("required_count", 2)) if spec.get("requires_multiple") else 1
        required = min(required, len(recipients)) or 1
        approval_id = uuid.uuid4().hex[:12]
        pending = PendingApproval(
            project.name, responsibility, title.strip(), detail.strip(),
            required, recipients, self._weaver_phase(project.phase),
        )
        self.pending[approval_id] = pending
        message = (
            (note + "\n\n" if note else "") +
            f"{self._label(responsibility)}\n\n<b>{esc(pending.title)}</b>\n{esc(pending.detail)}\n\n"
            f"<i>Approvals needed: {required}</i>"
        )
        buttons = [[
            {"text": "Approve", "callback_data": f"{APPROVE_PREFIX}{approval_id}"},
            {"text": "Reject", "callback_data": f"{REJECT_PREFIX}{approval_id}"},
        ]]
        for user in recipients:
            self._open(project, user, "approval")
            try:
                chat, message_id = self._send(project, user, message, buttons)
            except Exception:
                log.exception("delivering approval %s to %s", approval_id, user)
                continue
            pending.messages.append((user, chat, message_id))

    def _deliver(self, project: Project, visibility: str, session_id: str) -> None:
        if self.delivery is None:
            for admin in project.roster.admins:
                self._send(project, admin, (
                    f"The agent asked to deliver <b>{esc(project.name)}</b> ({esc(visibility)}), but this "
                    "bridge has no GitHub token. The repository is complete in its rig."
                ))
            self._inbound(project, DELIVERY_UNAVAILABLE, "bridge", "bridge")
            return
        try:
            url = self.delivery.publish(project.name, visibility)
        except gd.DeliveryError as exc:
            for admin in project.roster.admins:
                self._send(project, admin, f"Delivery of <b>{esc(project.name)}</b> failed: {esc(str(exc))}")
            self._inbound(project, f"DELIVERY_FAILED: {exc}", "bridge", "bridge")
            return
        for admin in project.roster.admins:
            self._send(project, admin, (
                f"Delivered <b>{esc(project.name)}</b>.\n<a href=\"{esc(url)}\">{esc(url)}</a>"
            ))
        summary = (
            "## Delivery summary\n"
            f"- Published {project.name} as {visibility}.\n"
            f"- URL: {url}"
        )
        mirrored = self._mirror(
            project, "delivery", "assistant", summary,
            self._idempotency_key(
                "delivery", project.name, session_id, summary,
            ),
        )
        if mirrored:
            project.weaver_terminal_summaries.append("delivery")
        self._inbound(project, f"DELIVERED: {url}", "bridge", "bridge")

    def _inbound(self, project: Project, text: str, actor_id: str, actor_name: str) -> bool:
        try:
            self.gc.send_inbound(text, actor_id, actor_name, conversation=project.conversation())
            return True
        except Exception:
            log.exception("sending inbound for project %s", project.name)
            return False

    # --- humans -> agent ---

    def on_message(self, user: str, chat_id: int, thread_id: int | None, text: str) -> bool:
        """Forward a human message if an agent is waiting for it. Returns whether handled."""
        with self.lock:
            located = self.project_for_topic(chat_id, thread_id)
            if located:
                project, owner = located
                if owner != user:
                    self._send(project, user, "This room belongs to someone else on the project.")
                    return True
                return self._answer(project, user, text)
            if thread_id is not None or chat_id != self._dm(user):
                return False
            return self._answer_by_dm(user, text)

    def _answer_by_dm(self, user: str, text: str) -> bool:
        waiting = [p for p in self.projects.values() if user in p.awaiting and user not in p.topics]
        if not waiting:
            return False
        match = PROJECT_PREFIX.match(text)
        if match and match.group(1) in self.projects:
            named = self.projects[match.group(1)]
            if user in named.awaiting:
                return self._answer(named, user, match.group(2).strip())
        if len(waiting) == 1:
            return self._answer(waiting[0], user, text)
        names = ", ".join(sorted(p.name for p in waiting))
        self.tg.send(user, self._dm(user), (
            f"Several projects are waiting on you: <b>{esc(names)}</b>. Start your reply with the "
            "project name and a colon, e.g. <code>bakery: ...</code>"
        ))
        return True

    def _answer(self, project: Project, user: str, text: str) -> bool:
        if user not in project.awaiting:
            self._send(project, user, (
                "The agent is not waiting on you right now, so this was not forwarded. "
                "This room opens when it has a question for you."
            ))
            return True
        display = self.users[user].get("telegram_username", user)
        if not self._inbound(project, text, user, display):
            self._send(project, user, "Could not reach the agent; your answer was not delivered. Try again shortly.")
            return True
        self._close(project, user)
        self._send(project, user, "Passed to the agent. The room is closed until it needs you again.")
        self.store.save(project)
        return True

    def on_button(self, user: str, callback_id: str, approval_id: str, approved: bool) -> bool:
        """Record a vote on a project approval. Returns whether the id was ours."""
        with self.lock:
            pending = self.pending.get(approval_id)
            if pending is None:
                return False
            project = self.projects.get(pending.project)
            if project is None:
                return False
            if pending.resolved:
                self.tg.answer_callback(user, callback_id, "Already decided.")
                return True
            if user not in pending.asked:
                self.tg.answer_callback(user, callback_id, "Not your responsibility.")
                return True
            if not approved:
                pending.resolved = True
                outcome = f"REJECTED by {user}"
                note = f"Rejected by {user}. Say why in this room."
            else:
                pending.approvals.add(user)
                remaining = pending.required - len(pending.approvals)
                if remaining > 0:
                    self.tg.answer_callback(user, callback_id, f"Recorded. {remaining} more needed.")
                    return True
                pending.resolved = True
                voters = ", ".join(sorted(pending.approvals))
                outcome = f"APPROVED by {voters}"
                note = f"Approved by {voters}."

            self.tg.answer_callback(user, callback_id, note)
            for voter, chat, message_id in pending.messages:
                try:
                    self.tg.edit(voter, chat, message_id, f"<b>{esc(pending.title)}</b>\n{esc(pending.detail)}\n\n{esc(note)}")
                except Exception:
                    log.exception("updating approval message for %s", voter)
            self._inbound(project, f"{outcome} — for: {pending.title}", user,
                          self.users[user].get("telegram_username", user))
            for asked in pending.asked:
                if not approved and asked == user:
                    # The rejecting reviewer owes a reason; keep their room open for it.
                    project.awaiting[asked] = {"kind": "question", "asked_at": now_iso()}
                    continue
                self._close(project, asked)
            self.store.save(project)
            return True

    # --- Weaver -> agent approvals ---

    def poll_weaver_approvals(self) -> None:
        """Poll every linked app once and forward newly approved phases."""
        if self.weaver is None:
            return
        with self.lock:
            projects = list(self.projects.values())
        for project in projects:
            if project.weaver_app_id is None:
                continue
            try:
                state = self.weaver.state(project.weaver_app_id)
                approved = state.get("approvedPhases") or []
                if not isinstance(approved, list):
                    raise wc.WeaverError("Weaver factory-state has invalid approvedPhases")
                for phase in ("discovery", "implementation", "delivery"):
                    if phase in approved:
                        self._forward_weaver_approval(project, phase)
            except Exception:
                # One unavailable or malformed app must not stop polling the
                # other projects, nor kill the bridge's long-running thread.
                log.exception("polling Weaver approvals for project %s", project.name)

    def _forward_weaver_approval(self, project: Project, phase: str) -> bool:
        """Forward one phase approval. Return true once durably consumed."""
        responsibility = {
            "discovery": "requirements",
            "implementation": "code_review",
        }.get(phase)
        with self.lock:
            if phase in project.forwarded_weaver_approvals:
                return True
            if responsibility is None:
                # Delivery has no corresponding in-workflow approval request.
                project.forwarded_weaver_approvals.append(phase)
                self.store.save(project)
                return True
            pending = next((
                approval for approval in self.pending.values()
                if approval.project == project.name
                and approval.responsibility == responsibility
                and approval.weaver_phase == phase
                and not approval.resolved
            ), None)
            if pending is None:
                # The publish may not have arrived yet (or may be replayed
                # after a bridge restart). Leave the phase retryable.
                return False
            outcome = f"APPROVED by Weaver — for: {pending.title}"
            if not self._inbound(project, outcome, "weaver", "Weaver"):
                return False

            # Gas City accepted the turn. From here on this approval is
            # consumed even if a Telegram edit fails.
            pending.approvals.add("Weaver")
            pending.resolved = True
            note = "Approved by Weaver."
            for asked in pending.asked:
                self._close(project, asked)
            project.forwarded_weaver_approvals.append(phase)
            self.store.save(project)
            for voter, chat, message_id in pending.messages:
                try:
                    self.tg.edit(
                        voter, chat, message_id,
                        f"<b>{esc(pending.title)}</b>\n"
                        f"{esc(pending.detail)}\n\n{esc(note)}",
                    )
                except Exception:
                    log.exception("updating Weaver-approved message for %s", voter)
            return True

    # --- event stream ---

    def on_event(self, event: dict[str, Any]) -> None:
        """Turn workflow lifecycle events into phase notes for the roster."""
        kind = event.get("type", "")
        with self.lock:
            if kind == "execution.step_started":
                project = self._project_for_run(event.get("run_id", ""))
                if project is None:
                    return
                step = event.get("step_id", "")
                project.phase = step
                step_name = self._step_name(step)
                self._broadcast(project, f"\N{BLACK RIGHT-POINTING TRIANGLE} Working on <b>{esc(step_name)}</b>")
                self._mirror(
                    project, self._weaver_phase(step), "system",
                    f"Working on {step_name}",
                    self._event_idempotency_key(project, event),
                )
                self.store.save(project)
            elif kind in ("bead.updated", "bead.closed"):
                payload = event.get("payload") or {}
                # The SSE stream wraps the snapshot as {"bead": {...}}; the
                # on-disk log carries it bare. Accept both.
                if isinstance(payload.get("bead"), dict):
                    payload = payload["bead"]
                if payload.get("status") != "closed":
                    return
                metadata = payload.get("metadata") or {}
                project = self._project_for_run(metadata.get("gc.root_bead_id", ""))
                if project is None:
                    return
                bead_id = payload.get("id", "")
                if bead_id in project.reported_closed:
                    return
                project.reported_closed.append(bead_id)
                title = payload.get("title") or self._step_name(metadata.get("gc.step_ref", ""))
                self._broadcast(project, f"\N{CHECK MARK} Done: <b>{esc(title)}</b>")
                self._mirror(
                    project, self._weaver_phase(metadata.get("gc.step_ref") or project.phase),
                    "system", f"Done: {title}",
                    self._event_idempotency_key(project, event),
                )
                self.store.save(project)

    @staticmethod
    def _weaver_phase(step_id: str | None) -> str:
        step = (step_id or "").rsplit(".", 1)[-1]
        if step == "discover":
            return "discovery"
        if step in ("verification-doc", "deliver"):
            return "delivery"
        if step in ("write-tests", "implement", "review"):
            return "implementation"
        # A publish can precede the first lifecycle cue; discovery is the only
        # open phase at that point and is therefore the safe deterministic home.
        return "discovery"

    @staticmethod
    def _idempotency_key(kind: str, project: str, identity: str, content: str) -> str:
        digest = hashlib.sha256(
            f"{kind}\0{project}\0{identity}\0{content}".encode("utf-8")
        ).hexdigest()
        return f"gas-city:{kind}:{digest}"

    def _event_idempotency_key(self, project: Project, event: dict[str, Any]) -> str:
        identity = str(event.get("seq") or event.get("id") or "")
        canonical = json.dumps(event, sort_keys=True, separators=(",", ":"))
        return self._idempotency_key("event", project.name, identity, canonical)

    def _mirror(self, project: Project, phase: str, role: str, content: str,
                idempotency_key: str) -> bool:
        """Best-effort mirror; Telegram and workflow routing remain authoritative."""
        if (
            project.weaver_app_id is None
            or self.weaver is None
            or phase in project.weaver_terminal_summaries
        ):
            return False
        try:
            self.weaver.post_message(
                project.weaver_app_id, phase, idempotency_key, role, content,
            )
            return True
        except wc.WeaverError:
            log.exception("mirroring %s project %s to Weaver", role, project.name)
            return False

    def _project_for_run(self, run_id: str) -> Project | None:
        if not run_id:
            return None
        for project in self.projects.values():
            if project.workflow_id == run_id:
                return project
        return None

    @staticmethod
    def _step_name(step_id: str) -> str:
        return step_id.rsplit(".", 1)[-1].replace("-", " ") if step_id else "the next step"
