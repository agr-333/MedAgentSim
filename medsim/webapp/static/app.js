const messagesEl = document.getElementById("messages");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const sendButton = document.getElementById("send-button");
const newSessionButton = document.getElementById("new-session");
const revealButton = document.getElementById("reveal-diagnosis");
const diagnosisEl = document.getElementById("diagnosis");

const scenarioIdEl = document.getElementById("scenario-id");
const scenarioDemographicsEl = document.getElementById("scenario-demographics");
const scenarioComplaintEl = document.getElementById("scenario-complaint");
const scenarioObjectiveEl = document.getElementById("scenario-objective");
const historyRemainingEl = document.getElementById("history-remaining");
const examStatusEl = document.getElementById("exam-status");
const testStatusEl = document.getElementById("test-status");

let sessionId = null;

function appendMessage(role, content) {
  const message = document.createElement("div");
  message.classList.add("message", role);
  message.textContent = content;
  messagesEl.appendChild(message);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function resetChat() {
  messagesEl.innerHTML = "";
  diagnosisEl.textContent = "";
}

function setLoading(isLoading) {
  chatInput.disabled = isLoading;
  sendButton.disabled = isLoading;
}

function updateMetadata(metadata) {
  if (!metadata) {
    return;
  }

  scenarioIdEl.textContent = metadata.scenario_id ?? "–";
  scenarioDemographicsEl.textContent = metadata.demographics ?? "–";
  scenarioComplaintEl.textContent = metadata.chief_complaint ?? "–";
  scenarioObjectiveEl.textContent = metadata.objective ?? "–";

  const progress = metadata.progress ?? {};
  historyRemainingEl.textContent = progress.history_remaining ?? 0;
  examStatusEl.textContent = progress.shared_exam ? "Yes" : "No";
  testStatusEl.textContent = progress.shared_tests ? "Yes" : "No";

  examStatusEl.classList.toggle("active", !!progress.shared_exam);
  testStatusEl.classList.toggle("active", !!progress.shared_tests);
}

async function createSession() {
  setLoading(true);
  try {
    const response = await fetch("/api/session", { method: "POST" });
    if (!response.ok) {
      throw new Error("Failed to start a session");
    }

    const data = await response.json();
    sessionId = data.session_id;
    resetChat();

    (data.session.history || []).forEach((entry) => {
      appendMessage(entry.role, entry.content);
    });

    updateMetadata(data.session.metadata);
    chatInput.focus();
  } catch (error) {
    console.error(error);
    alert("Unable to start a new scenario. Check the server logs for details.");
  } finally {
    setLoading(false);
  }
}

async function sendMessage(message) {
  if (!sessionId) {
    return;
  }

  setLoading(true);

  try {
    const response = await fetch("/api/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message }),
    });

    if (!response.ok) {
      throw new Error("Failed to send message");
    }

    const data = await response.json();
    appendMessage("patient", data.reply);
    updateMetadata(data.session.metadata);
  } catch (error) {
    console.error(error);
    alert("Message failed to send. Please try again.");
  } finally {
    setLoading(false);
  }
}

async function revealDiagnosis() {
  if (!sessionId) {
    return;
  }

  revealButton.disabled = true;
  try {
    const response = await fetch("/api/reveal", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId }),
    });

    if (!response.ok) {
      throw new Error("Failed to reveal diagnosis");
    }

    const data = await response.json();
    diagnosisEl.textContent = `Diagnosis: ${data.diagnosis}`;
  } catch (error) {
    console.error(error);
    alert("Unable to reveal the diagnosis.");
  } finally {
    revealButton.disabled = false;
  }
}

chatForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = chatInput.value.trim();
  if (!message) {
    return;
  }

  appendMessage("doctor", message);
  chatInput.value = "";
  sendMessage(message);
});

newSessionButton.addEventListener("click", () => {
  createSession();
});

revealButton.addEventListener("click", () => {
  revealDiagnosis();
});

window.addEventListener("DOMContentLoaded", () => {
  createSession();
});
