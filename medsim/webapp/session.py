"""Session management utilities for the interactive web application.

This module provides light-weight patient simulation logic that can be served
through a simple web API.  The implementation intentionally avoids invoking the
full LLM stack so that the demo can run locally without external dependencies.
"""

from __future__ import annotations

import copy
import json
import random
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from medsim.core.scenario import ScenarioMedQA


_DATASET_PATH = Path(__file__).resolve().parents[2] / "datasets" / "_medqa.jsonl"


class ScenarioRepository:
    """Utility wrapper that loads scenarios from disk and serves random entries."""

    def __init__(self, dataset_path: Path = _DATASET_PATH) -> None:
        if not dataset_path.exists():
            raise FileNotFoundError(
                f"Unable to locate MedQA dataset at {dataset_path}. "
                "Ensure the repository datasets are downloaded."
            )

        with dataset_path.open("r", encoding="utf-8") as handle:
            self._scenarios: List[ScenarioMedQA] = [
                ScenarioMedQA(json.loads(line)) for line in handle
            ]

        if not self._scenarios:
            raise RuntimeError("No scenarios were loaded from the MedQA dataset.")

    def random_scenario(self) -> Tuple[int, ScenarioMedQA]:
        """Return a random scenario and its index."""

        index = random.randrange(len(self._scenarios))
        return index, self._scenarios[index]


def _format_key(text: str) -> str:
    """Convert snake_case or camel-like keys into human friendly titles."""

    return text.replace("_", " ").replace("-", " ").strip().title()


def _format_list(values: Iterable[str]) -> str:
    items = [str(value) for value in values if value]
    return ", ".join(items)


@dataclass
class PatientConversationSession:
    """Stateful helper that emulates a patient for interactive exploration."""

    scenario: ScenarioMedQA
    scenario_id: int
    session_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    history: List[Dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        patient_info = self.scenario.patient_information()
        self._demographics: str = patient_info.get("Demographics", "Patient")
        symptoms = patient_info.get("Symptoms", {})
        self._primary_symptom: str = symptoms.get("Primary_Symptom", "a medical concern")
        self._secondary_symptoms: List[str] = list(symptoms.get("Secondary_Symptoms", []))

        self._objective: str = self.scenario.examiner_information()

        self._history_queue: List[str] = self._build_history_queue(patient_info)
        self._exam_summary: str = self._build_exam_summary(copy.deepcopy(self.scenario.physical_exams))
        self._test_summary: str = self._build_test_summary(copy.deepcopy(self.scenario.tests))

        self._shared_exam: bool = False
        self._shared_tests: bool = False

        # Pre-compute pleasant responses for repeated requests.
        self._cached_exam_response: str = (
            self._exam_summary if self._exam_summary else "I haven't had a formal examination yet."
        )
        self._cached_test_response: str = (
            self._test_summary if self._test_summary else "I haven't completed any diagnostic tests yet."
        )

        self._greeting: str = self._compose_greeting(patient_info)
        self._append_message("patient", self._greeting)

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------
    def _compose_greeting(self, patient_info: Dict[str, Any]) -> str:
        intro = [f"Hello doctor, I'm a {self._demographics}."]
        intro.append(f"My main concern is {self._primary_symptom}.")

        if self._history_queue:
            intro.append(self._history_queue.pop(0))

        return " ".join(intro)

    def _build_history_queue(self, patient_info: Dict[str, Any]) -> List[str]:
        queue: List[str] = []

        history = patient_info.get("History")
        if history:
            queue.append(history)

        if self._secondary_symptoms:
            queue.append(
                "Other symptoms I've noticed include "
                + _format_list(self._secondary_symptoms)
                + "."
            )

        past_medical = patient_info.get("Past_Medical_History")
        if past_medical:
            queue.append(f"In terms of past medical issues: {past_medical}")

        social_history = patient_info.get("Social_History")
        if social_history:
            queue.append(f"Socially, {social_history}")

        review_systems = patient_info.get("Review_of_Systems")
        if review_systems:
            queue.append(f"For the review of systems: {review_systems}")

        return queue

    def _build_exam_summary(self, exam_sections: Dict[str, Any]) -> str:
        if not exam_sections:
            return ""

        lines: List[str] = ["Here's what the physical examination noted:"]
        for section, details in exam_sections.items():
            if not details:
                continue

            section_name = _format_key(section)
            if isinstance(details, dict):
                inner = "; ".join(
                    f"{_format_key(key)} {value}" if isinstance(value, str) else f"{_format_key(key)}: {value}"
                    for key, value in details.items()
                    if value
                )
                if inner:
                    lines.append(f"• {section_name}: {inner}")
            elif isinstance(details, list):
                inner = _format_list(details)
                if inner:
                    lines.append(f"• {section_name}: {inner}")
            else:
                lines.append(f"• {section_name}: {details}")

        return "\n".join(lines)

    def _build_test_summary(self, tests: Dict[str, Any]) -> str:
        if not tests:
            return ""

        lines: List[str] = ["Here are the key test results I've received:"]
        for category, results in tests.items():
            category_name = _format_key(category)
            if isinstance(results, dict):
                inner = "; ".join(
                    f"{_format_key(name)} {value}" if isinstance(value, str) else f"{_format_key(name)}: {value}"
                    for name, value in results.items()
                    if value
                )
                if inner:
                    lines.append(f"• {category_name}: {inner}")
            elif isinstance(results, list):
                inner = _format_list(results)
                if inner:
                    lines.append(f"• {category_name}: {inner}")
            else:
                lines.append(f"• {category_name}: {results}")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def metadata(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "demographics": self._demographics,
            "chief_complaint": self._primary_symptom,
            "objective": self._objective,
            "progress": {
                "history_remaining": len(self._history_queue),
                "shared_exam": self._shared_exam,
                "shared_tests": self._shared_tests,
                "has_exam": bool(self._exam_summary),
                "has_tests": bool(self._test_summary),
            },
        }

    def _append_message(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})

    def register_doctor_message(self, message: str) -> None:
        self._append_message("doctor", message)

    def respond(self, doctor_message: str) -> str:
        doctor_message_lower = doctor_message.lower()

        if any(keyword in doctor_message_lower for keyword in {"thank", "appreciate"}):
            response = "You're welcome. Please let me know if you need anything else."
        elif any(keyword in doctor_message_lower for keyword in {"diagnosis", "disease", "condition"}):
            response = "I'm not sure what the diagnosis is yet—I'm hoping you can figure that out."
        elif self._should_share_tests(doctor_message_lower):
            response = self._cached_test_response
        elif self._should_share_exam(doctor_message_lower):
            response = self._cached_exam_response
        elif self._history_queue:
            response = self._history_queue.pop(0)
        else:
            response = "I think that's everything I can recall at the moment."

        self._append_message("patient", response)
        return response

    def _should_share_tests(self, doctor_message: str) -> bool:
        if not self._test_summary:
            return False

        keywords = {"test", "lab", "blood", "imaging", "scan", "result"}
        if any(keyword in doctor_message for keyword in keywords):
            self._shared_tests = True
            return True
        return False

    def _should_share_exam(self, doctor_message: str) -> bool:
        if not self._exam_summary:
            return False

        keywords = {"exam", "examination", "physical", "vital", "assessment", "examined"}
        if any(keyword in doctor_message for keyword in keywords):
            self._shared_exam = True
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {"history": self.history, "metadata": self.metadata()}

    def reveal_diagnosis(self) -> str:
        return self.scenario.diagnosis


class SessionManager:
    """Orchestrates conversation sessions for the web API."""

    def __init__(self, repository: ScenarioRepository | None = None) -> None:
        self._repository = repository or ScenarioRepository()
        self._sessions: Dict[str, PatientConversationSession] = {}

    def create_session(self) -> PatientConversationSession:
        scenario_id, scenario = self._repository.random_scenario()
        session = PatientConversationSession(scenario=scenario, scenario_id=scenario_id)
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> PatientConversationSession:
        try:
            return self._sessions[session_id]
        except KeyError as exc:
            raise KeyError(f"Unknown session_id: {session_id}") from exc

    def handle_message(self, session_id: str, message: str) -> Tuple[str, Dict[str, Any]]:
        session = self.get_session(session_id)
        session.register_doctor_message(message)
        reply = session.respond(message)
        return reply, session.to_dict()

    def reveal(self, session_id: str) -> str:
        session = self.get_session(session_id)
        return session.reveal_diagnosis()


__all__ = [
    "PatientConversationSession",
    "ScenarioRepository",
    "SessionManager",
]
