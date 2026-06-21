const statusEl = document.getElementById('status');
const speakerEl = document.getElementById('speaker');
const replyEl = document.getElementById('reply');
const promptEl = document.getElementById('prompt');
const moodEl = document.getElementById('mood');
const ttsEl = document.getElementById('tts');

let ttsEnabled = false;

function setStatus(text) {
  statusEl.textContent = text;
}

function speak(text) {
  if (!ttsEnabled || !('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1.02;
  utterance.pitch = 1.0;
  utterance.volume = 1.0;
  window.speechSynthesis.speak(utterance);
}

function handleEvent(event) {
  if (event.ttsEnabled !== undefined) {
    ttsEnabled = Boolean(event.ttsEnabled);
    ttsEl.textContent = `tts: ${ttsEnabled ? 'on' : 'off'}`;
  }

  if (event.type === 'status') {
    setStatus('online');
    replyEl.textContent = event.text || 'Ready.';
    promptEl.textContent = '';
    if (event.tts) speak(event.text || '');
    return;
  }

  if (event.type === 'reply') {
    setStatus('replying');
    speakerEl.textContent = `${event.username || 'A viewer'} asked`;
    replyEl.textContent = event.reply || '';
    promptEl.textContent = event.prompt ? `"${event.prompt}"` : '';
    moodEl.textContent = `mood: ${event.mood || 'normal'}`;
    if (event.tts) speak(event.reply || '');
  }
}

function connect() {
  const source = new EventSource('/events');

  source.onopen = () => {
    setStatus('connected');
  };

  source.onmessage = (message) => {
    try {
      handleEvent(JSON.parse(message.data));
    } catch (error) {
      console.error('Bad overlay event:', error, message.data);
    }
  };

  source.onerror = () => {
    setStatus('reconnecting');
  };
}

connect();
