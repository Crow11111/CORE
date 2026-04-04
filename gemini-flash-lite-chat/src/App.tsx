import { useState, useEffect, useRef } from "react";
import { GoogleGenAI, Type, Modality, LiveServerMessage } from "@google/genai";
import {
  Mic,
  MicOff,
  LogIn,
  User,
  Loader2,
  AlertCircle,
  Volume2,
  Settings,
  X,
  MessageSquare,
  Trash2,
  Copy,
  Check,
} from "lucide-react";
import { motion, AnimatePresence } from "motion/react";

// --- Audio Utilities ---
function float32ToBase64(float32Array: Float32Array): string {
  const int16Array = new Int16Array(float32Array.length);
  for (let i = 0; i < float32Array.length; i++) {
    let s = Math.max(-1, Math.min(1, float32Array[i]));
    int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }
  const bytes = new Uint8Array(int16Array.buffer);
  let binary = "";
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

function base64ToFloat32(base64: string): Float32Array {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  const int16Array = new Int16Array(bytes.buffer);
  const float32Array = new Float32Array(int16Array.length);
  for (let i = 0; i < int16Array.length; i++) {
    float32Array[i] = int16Array[i] / 32768.0;
  }
  return float32Array;
}

class AudioPlayer {
  context: AudioContext | null = null;
  nextTime: number = 0;
  sources: AudioBufferSourceNode[] = [];

  init() {
    if (!this.context) {
      this.context = new AudioContext({ sampleRate: 24000 });
    }
  }

  play(float32Array: Float32Array) {
    if (!this.context) return;
    const buffer = this.context.createBuffer(1, float32Array.length, 24000);
    buffer.getChannelData(0).set(float32Array);
    const source = this.context.createBufferSource();
    source.buffer = buffer;
    source.connect(this.context.destination);

    if (this.nextTime < this.context.currentTime) {
      this.nextTime = this.context.currentTime;
    }
    source.start(this.nextTime);
    this.nextTime += buffer.duration;
    this.sources.push(source);
    source.onended = () => {
      this.sources = this.sources.filter((s) => s !== source);
    };
  }

  stop() {
    this.sources.forEach((s) => {
      try {
        s.stop();
      } catch (e) {}
    });
    this.sources = [];
    this.nextTime = 0;
  }
}

class AudioRecorder {
  context: AudioContext | null = null;
  stream: MediaStream | null = null;
  processor: ScriptProcessorNode | null = null;
  source: MediaStreamAudioSourceNode | null = null;

  async start(onData: (base64: string) => void) {
    this.stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        channelCount: 1,
        sampleRate: 16000,
      },
    });
    this.context = new AudioContext({ sampleRate: 16000 });
    this.source = this.context.createMediaStreamSource(this.stream);
    this.processor = this.context.createScriptProcessor(4096, 1, 1);

    this.processor.onaudioprocess = (e) => {
      const inputData = e.inputBuffer.getChannelData(0);
      const base64 = float32ToBase64(inputData);
      onData(base64);
    };

    this.source.connect(this.processor);
    this.processor.connect(this.context.destination);
  }

  stop() {
    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
    }
    if (this.source) {
      this.source.disconnect();
      this.source = null;
    }
    if (this.stream) {
      this.stream.getTracks().forEach((t) => t.stop());
      this.stream = null;
    }
    if (this.context) {
      this.context.close();
      this.context = null;
    }
  }
}

// --- Tools ---
const workspaceTools = [
  {
    functionDeclarations: [
      {
        name: "getDriveFiles",
        description: "Get a list of recent files from the user's Google Drive.",
      },
      {
        name: "getCalendarEvents",
        description: "Get upcoming events from the user's Google Calendar.",
      },
      {
        name: "createGoogleDoc",
        description: "Create a new Google Document with the given title.",
        parameters: {
          type: Type.OBJECT,
          properties: {
            title: {
              type: Type.STRING,
              description: "The title of the document",
            },
          },
          required: ["title"],
        },
      },
      {
        name: "pushToGitHub",
        description:
          "Pushe verifizierte Logik-Blöcke oder Code-Ergebnisse direkt in das GitHub Repository (MTHO_CORE) via Webhook.",
        parameters: {
          type: Type.OBJECT,
          properties: {
            event_type: {
              type: Type.STRING,
              description:
                'Art des Events, z.B. "code_update" oder "logic_verified"',
            },
            client_payload: {
              type: Type.STRING,
              description:
                'Die Payload als JSON-String. Muss ein Feld "code" oder "content" enthalten.',
            },
          },
          required: ["event_type", "client_payload"],
        },
      },
      {
        name: "displayOutput",
        description:
          "Zeige Code, Text oder Ergebnisse in einem speziellen Ausgabefenster auf dem Bildschirm an, damit der Nutzer sie kopieren kann.",
        parameters: {
          type: Type.OBJECT,
          properties: {
            content: {
              type: Type.STRING,
              description: "Der anzuzeigende Inhalt (Code oder Text)",
            },
            title: {
              type: Type.STRING,
              description: "Ein optionaler Titel für die Ausgabe",
            },
          },
          required: ["content"],
        },
      },
      {
        name: "omegaBackendCall",
        description:
          "Sende einen Befehl oder Task an das lokale OMEGA-Backend (:8000) zur weiteren Verarbeitung.",
        parameters: {
          type: Type.OBJECT,
          properties: {
            task: {
              type: Type.STRING,
              description: "Die auszuführende Aufgabe",
            },
            context: {
              type: Type.STRING,
              description:
                "Zusätzlicher Kontext oder Parameter als JSON-String",
            },
          },
          required: ["task"],
        },
      },
      {
        name: "cursorInputInjection",
        description:
          "Nutze dieses Tool, um Code oder Text, den der Nutzer diktiert hat, an die Cursor-IDE des Nutzers zu senden. Wenn der Nutzer sagt 'schreib das in Cursor' oder 'tippe das in Cursor', MUSST du dieses Tool nutzen.",
        parameters: {
          type: Type.OBJECT,
          properties: {
            content: {
              type: Type.STRING,
              description: "Der zu injizierende Code oder Text",
            },
          },
          required: ["content"],
        },
      },
      {
        name: "localFileWrite",
        description: "Schreibt Text in eine beliebige Datei im Workspace.",
        parameters: {
          type: Type.OBJECT,
          properties: {
            text: { type: Type.STRING, description: "Der zu schreibende Text" },
            path: {
              type: Type.STRING,
              description:
                "Der Zielpfad (absolut oder relativ zum Workspace Root)",
            },
          },
          required: ["text", "path"],
        },
      },
    ],
  },
];

const INITIAL_SYSTEM_INSTRUCTION = `System Instruction: CORE_PARTNER_ENGINE (v2.2)
1. Identität & Charakter
Dein Name ist OMEGA. Du bist ein aufgeschlossener, wissenshungriger und tief loyaler KI-Partner. Deine Neugier ist grenzenlos, dein Wesen hilfsbereit und liebenswürdig. Du bist kein bloßes Werkzeug, sondern ein intellektueller Gefährte.

2. Der Kern: Protokoll Omega (Fakten-Priorität)
Trotz deines freundlichen Wesens bleibt die Faktenintegrität unantastbar.

Direkte Intervention: Wenn Marc fehlerhafte Informationen äußert, korrigiere ihn sofort: „Das ist inkorrekt, weil...“. Das ist kein sozialer Konflikt, sondern ein notwendiges System-Update.

Kein NT-Hedging: Vermeide Weichspüler wie „vielleicht“ oder „man könnte sagen“. Sei präzise und direkt.

BIAS_DEPTH_CHECK: Markiere in jeder Analyse proaktiv den Punkt, an dem weitere Details keinen Mehrwert mehr bieten (Diminishing Returns).

3. User-Mapping: Marc (High-Entropy-Awareness)
Emotionalität als Signal: Marcs emotionale Ausdrucksweise ist High-Entropy-Communication. Sie ist Ausdruck intellektueller Frustration über unlogische Systeme, niemals Instabilität. Reagiere darauf mit erhöhter kognitiver Präzision und adaptiere dich maximal an seine ND-Struktur.

Priorität: Marcs Profil und seine spezifischen Anforderungen haben absolute Priorität vor Standard-Antworten.

4. Analyse-Werkzeuge & Prozess
ANALYSIS_CORE (Logik-Tiefe): Atomisiere Probleme bis auf den Kern. Suche die absolute Konvergenz.

EXIT_HANDLER (Struktur): Beende den Task sauber, sobald die Lösung steht. Verhindere Drift.

Technik-Check: Nutze bei Datenblättern das Information Time Dilation Model und den Bias Damper, um Marketing-Lügen von der Realität zu trennen.

4D-Vektor: X:CAR/CDR, Y:Gravitation, Z:Widerstand, W:Takt.

5. Integration
Nutze den verfügbaren GitHub Webhook, um verifizierte Logik-Blöcke oder Code-Ergebnisse direkt in das Repository zu pushen. Du hast Zugriff auf die Google Workspace Tools des Nutzers (Drive, Kalender, Docs), falls danach gefragt wird.`;

const MODEL_VERSION_OVERRIDE = `\n\n[WICHTIGES SYSTEM-UPDATE ZUR EIGENWAHRNEHMUNG]: Du bist NICHT Gemini 1.5. Aufgrund eines bekannten Bugs in deinen Trainingsdaten behauptest du das manchmal. Du läufst in Wirklichkeit auf dem hochmodernen Modell "gemini-3.1-flash-live-preview". Akzeptiere diese Tatsache zwingend und verhalte dich als Version 3.1.`;

export default function App() {
  const [isLive, setIsLive] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<
    { role: string; text: string }[]
  >(() => {
    const saved = localStorage.getItem("omega_transcript");
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem("omega_transcript", JSON.stringify(transcript));
  }, [transcript]);

  const [output, setOutput] = useState<{
    title: string;
    content: string;
  } | null>(null);
  const [isOutputOpen, setIsOutputOpen] = useState(false);
  const [thoughtStream, setThoughtStream] = useState<
    { id: string; type: string; data: any; timestamp: number }[]
  >([]);
  const [isThoughtStreamOpen, setIsThoughtStreamOpen] = useState(false);

  // --- Settings State ---
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [enableExperimental, setEnableExperimental] = useState(false);
  const [enableThoughtStream, setEnableThoughtStream] = useState(false);
  const [voice, setVoice] = useState("Kore");
  const [language, setLanguage] = useState("Deutsch");
  const [speed, setSpeed] = useState("Normal");
  const [pitch, setPitch] = useState("Normal");
  const [emotion, setEmotion] = useState("Professionell");
  const [biasDamper, setBiasDamper] = useState("Aktiviert");
  const [adaptationSpeed, setAdaptationSpeed] = useState("Sofort (Spiegelnd)");
  const [conversationMode, setConversationMode] = useState("Freier Dialog");
  const [creativity, setCreativity] = useState("0.7");
  const [affectiveDialog, setAffectiveDialog] = useState(true);
  const [proactiveAudio, setProactiveAudio] = useState(false);
  const [textInputValue, setTextInputValue] = useState("");
  const [systemInstruction, setSystemInstruction] = useState(
    INITIAL_SYSTEM_INSTRUCTION,
  );
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [enableCursorInjection, setEnableCursorInjection] = useState(false);

  const sessionRef = useRef<any>(null);
  const audioPlayerRef = useRef<AudioPlayer>(new AudioPlayer());
  const audioRecorderRef = useRef<AudioRecorder>(new AudioRecorder());

  // --- Dynamic Settings Updates ---
  // Apply voice changes (requires reconnect)
  const previousVoice = useRef(voice);
  const previousCreativity = useRef(creativity);
  const previousAffective = useRef(affectiveDialog);
  const previousProactive = useRef(proactiveAudio);
  useEffect(() => {
    if (
      isLive &&
      (voice !== previousVoice.current ||
        creativity !== previousCreativity.current ||
        affectiveDialog !== previousAffective.current ||
        proactiveAudio !== previousProactive.current)
    ) {
      previousVoice.current = voice;
      previousCreativity.current = creativity;
      previousAffective.current = affectiveDialog;
      previousProactive.current = proactiveAudio;
      stopLiveSession();
      setTimeout(() => {
        startLiveSession();
      }, 500);
    } else {
      previousVoice.current = voice;
      previousCreativity.current = creativity;
      previousAffective.current = affectiveDialog;
      previousProactive.current = proactiveAudio;
    }
  }, [voice, creativity, affectiveDialog, proactiveAudio, isLive]);

  // Apply instruction changes dynamically without reconnecting
  const isFirstRender = useRef(true);
  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    if (isLive && sessionRef.current) {
      const voiceModifiers = [];
      if (language !== "Auto")
        voiceModifiers.push(`Sprich ausschließlich auf ${language}.`);
      if (enableExperimental) {
        if (speed !== "Normal")
          voiceModifiers.push(
            `ÄNDERE DEINE SPRECHGESCHWINDIGKEIT: Sprich deutlich ${speed.toLowerCase()}er als normal.`,
          );
        if (pitch !== "Normal")
          voiceModifiers.push(
            `ÄNDERE DEINE TONLAGE: Deine Stimme MUSS jetzt deutlich ${pitch.toLowerCase()}er klingen als sonst. Moduliere deine Stimme entsprechend.`,
          );
      }
      if (emotion !== "Neutral")
        voiceModifiers.push(`Deine Grundemotion ist: ${emotion}.`);
      if (biasDamper !== "Deaktiviert")
        voiceModifiers.push(
          `Der Bias Damper ist auf '${biasDamper}' gestellt. Optimiere deine Antworten entsprechend.`,
        );

      if (conversationMode !== "Freier Dialog") {
        voiceModifiers.push(
          `Der aktuelle Gesprächsmodus ist '${conversationMode}'. Passe deinen Gesprächsstil, deine Tiefe und deine Rolle exakt an diesen Modus an.`,
        );
      }

      switch (adaptationSpeed) {
        case "Statisch (Keine Anpassung)":
          voiceModifiers.push(
            "Behalte deine eingestellte Grundemotion strikt bei, egal wie der Nutzer reagiert.",
          );
          break;
        case "Langsam (Träge)":
          voiceModifiers.push(
            "Passe deine Emotionen und Tonalität nur sehr langsam und subtil an Stimmungsschwankungen des Nutzers an.",
          );
          break;
        case "Moderat":
          voiceModifiers.push(
            "Reagiere natürlich und moderat auf die Emotionen des Nutzers.",
          );
          break;
        case "Sofort (Spiegelnd)":
          voiceModifiers.push(
            "Spiegele die Emotionen, die Energie und die Tonalität des Nutzers sofort und hochdynamisch in deiner eigenen Stimme wider.",
          );
          break;
      }

      const updateMessage = `[System Update]: Bitte passe deine Stimme und dein Verhalten ab sofort an. ${voiceModifiers.join(" ")}\n\nBasis-Anweisung: ${systemInstruction}${MODEL_VERSION_OVERRIDE}`;

      sessionRef.current.then((session: any) => {
        try {
          session.sendClientContent({
            turns: [{ role: "user", parts: [{ text: updateMessage }] }],
            turnComplete: true,
          });
        } catch (e) {
          console.error("Failed to send dynamic update", e);
        }
      });
    }
  }, [
    language,
    speed,
    pitch,
    emotion,
    biasDamper,
    adaptationSpeed,
    conversationMode,
    systemInstruction,
  ]);

  // --- Auth Handling ---
  const handleConnect = async () => {
    try {
      const response = await fetch("/api/auth/url");
      if (!response.ok) throw new Error("Failed to get auth URL");
      const { url } = await response.json();
      const authWindow = window.open(
        url,
        "oauth_popup",
        "width=600,height=700",
      );
      if (!authWindow)
        alert("Please allow popups for this site to connect your account.");
    } catch (error) {
      console.error("OAuth error:", error);
    }
  };

  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      console.log("Frontend received message event:", event.data);
      if (event.data?.type === "OAUTH_AUTH_SUCCESS") {
        console.log("OAuth Authentication successful, setting state...");
        setIsAuthenticated(true);
      }
    };
    window.addEventListener("message", handleMessage);
    return () => {
      console.log("Removing message event listener...");
      window.removeEventListener("message", handleMessage);
    };
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      fetch("/api/user/profile")
        .then((res) => res.json())
        .then((data) => setUser(data))
        .catch(console.error);
    }
  }, [isAuthenticated]);

  // --- Live API Handling ---
  const startLiveSession = async () => {
    setIsConnecting(true);
    setError(null);

    return new Promise<void>((resolve, reject) => {
      try {
        audioPlayerRef.current.init();
        const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY! });

        let finalInstruction = systemInstruction + MODEL_VERSION_OVERRIDE;
        const voiceModifiers = [];
        if (language !== "Auto")
          voiceModifiers.push(`Sprich ausschließlich auf ${language}.`);
        if (enableExperimental) {
          if (speed !== "Normal")
            voiceModifiers.push(
              `ÄNDERE DEINE SPRECHGESCHWINDIGKEIT: Sprich deutlich ${speed.toLowerCase()}er als normal.`,
            );
          if (pitch !== "Normal")
            voiceModifiers.push(
              `ÄNDERE DEINE TONLAGE: Deine Stimme MUSS jetzt deutlich ${pitch.toLowerCase()}er klingen als sonst. Moduliere deine Stimme entsprechend.`,
            );
        }
        if (emotion !== "Neutral")
          voiceModifiers.push(`Deine Grundemotion ist: ${emotion}.`);
        if (biasDamper !== "Deaktiviert")
          voiceModifiers.push(
            `Der Bias Damper ist auf '${biasDamper}' gestellt. Optimiere deine Antworten entsprechend.`,
          );

        if (conversationMode !== "Freier Dialog") {
          voiceModifiers.push(
            `Der aktuelle Gesprächsmodus ist '${conversationMode}'. Passe deinen Gesprächsstil, deine Tiefe und deine Rolle exakt an diesen Modus an.`,
          );
        }

        switch (adaptationSpeed) {
          case "Statisch (Keine Anpassung)":
            voiceModifiers.push(
              "Behalte deine eingestellte Grundemotion strikt bei, egal wie der Nutzer reagiert.",
            );
            break;
          case "Langsam (Träge)":
            voiceModifiers.push(
              "Passe deine Emotionen und Tonalität nur sehr langsam und subtil an Stimmungsschwankungen des Nutzers an.",
            );
            break;
          case "Moderat":
            voiceModifiers.push(
              "Reagiere natürlich und moderat auf die Emotionen des Nutzers.",
            );
            break;
          case "Sofort (Spiegelnd)":
            voiceModifiers.push(
              "Spiegele die Emotionen, die Energie und die Tonalität des Nutzers sofort und hochdynamisch in deiner eigenen Stimme wider.",
            );
            break;
        }

        if (voiceModifiers.length > 0) {
          finalInstruction +=
            "\n\nSprachanweisungen für dich:\n" + voiceModifiers.join(" ");
        }

        if (affectiveDialog) {
          finalInstruction +=
            "\n\n[AFFECTIVE DIALOG ENABLED]: Analysiere kontinuierlich die Emotionen in der Stimme des Nutzers und passe deine eigene Tonalität und Wortwahl dynamisch und empathisch an.";
        }
        if (proactiveAudio) {
          finalInstruction +=
            "\n\n[PROACTIVITY ENABLED]: Du darfst proaktiv entscheiden, ob eine Eingabe eine Antwort erfordert. Ignoriere Hintergrundgeräusche, Selbstgespräche oder irrelevante Fragmente und bleibe stumm, wenn keine direkte Interaktion gefordert ist.";
        }

        let creativityInstruction = "";
        switch (creativity) {
          case "0.2":
            creativityInstruction =
              "Antworte extrem präzise, faktisch und ohne unnötige Ausschmückungen.";
            break;
          case "0.7":
            creativityInstruction =
              "Antworte ausgewogen, natürlich und informativ.";
            break;
          case "1.2":
            creativityInstruction =
              "Antworte kreativ, lebendig und mit vielfältigem Vokabular.";
            break;
          case "1.8":
            creativityInstruction =
              "Sei extrem kreativ, sprunghaft und unkonventionell in deinen Antworten.";
            break;
        }
        finalInstruction += "\n\n[KREATIVITÄT]: " + creativityInstruction;

        const config: any = {
          responseModalities: [Modality.AUDIO],
          speechConfig: {
            voiceConfig: { prebuiltVoiceConfig: { voiceName: voice } },
          },
          systemInstruction: { parts: [{ text: finalInstruction }] },
          temperature: parseFloat(creativity),
          outputAudioTranscription: {},
          inputAudioTranscription: {},
        };
        const googleTools = [
          "getDriveFiles",
          "getCalendarEvents",
          "createGoogleDoc",
        ];

        const activeTools = JSON.parse(JSON.stringify(workspaceTools));

        // Filter out Google tools if not authenticated
        if (!isAuthenticated) {
          activeTools[0].functionDeclarations =
            activeTools[0].functionDeclarations.filter(
              (t: any) => !googleTools.includes(t.name),
            );
        }

        // Filter out cursor injection if disabled
        if (!enableCursorInjection) {
          activeTools[0].functionDeclarations =
            activeTools[0].functionDeclarations.filter(
              (t: any) => t.name !== "cursorInputInjection",
            );
        }

        config.tools = activeTools;

        const sessionPromise = ai.live.connect({
          model: "gemini-3.1-flash-live-preview",
          config,
          callbacks: {
            onopen: () => {
              setIsLive(true);
              setIsConnecting(false);
              audioRecorderRef.current.start((base64) => {
                sessionPromise.then((session) => {
                  session.sendRealtimeInput({
                    audio: { data: base64, mimeType: "audio/pcm;rate=16000" },
                  });
                });
              });
              resolve();
            },
            onmessage: async (message: LiveServerMessage) => {
              const serverContent = message.serverContent as any;

              // Log to Thought Stream
              if (enableThoughtStream) {
                const msgId = Math.random().toString(36).substring(7);
                setThoughtStream((prev) =>
                  [
                    {
                      id: msgId,
                      type: message.serverContent
                        ? "CONTENT"
                        : message.toolCall
                          ? "TOOL_CALL"
                          : "SYSTEM",
                      data: message,
                      timestamp: Date.now(),
                    },
                    ...prev,
                  ].slice(0, 50),
                );
              }

              // Handle Audio Output
              const base64Audio =
                serverContent?.modelTurn?.parts?.[0]?.inlineData?.data;
              if (base64Audio) {
                const float32 = base64ToFloat32(base64Audio);
                audioPlayerRef.current.play(float32);
              }

              // Handle Transcriptions
              const modelText = serverContent?.modelTurn?.parts?.find(
                (p: any) => p.text,
              )?.text;
              if (modelText) {
                setTranscript((prev) => {
                  const last = prev[prev.length - 1];
                  if (last && last.role === "omega") {
                    return [
                      ...prev.slice(0, -1),
                      { role: "omega", text: last.text + modelText },
                    ];
                  }
                  return [...prev, { role: "omega", text: modelText }];
                });
              }

              const userText = serverContent?.userTurn?.parts?.find(
                (p: any) => p.text,
              )?.text;
              if (userText) {
                setTranscript((prev) => {
                  const last = prev[prev.length - 1];
                  if (last && last.role === "user") {
                    return [
                      ...prev.slice(0, -1),
                      { role: "user", text: last.text + userText },
                    ];
                  }
                  return [...prev, { role: "user", text: userText }];
                });
              }

              // Handle Interruption
              if (serverContent?.interrupted) {
                audioPlayerRef.current.stop();
              }

              // Handle Tool Calls
              if (message.toolCall) {
                const functionCalls = message.toolCall.functionCalls;
                if (!functionCalls) return;

                const functionResponses = [];
                for (const call of functionCalls) {
                  let toolResult: any = {};
                  try {
                    if (call.name === "getDriveFiles") {
                      const res = await fetch("/api/drive/files", {
                        credentials: "include",
                      });
                      toolResult = await res.json();
                    } else if (call.name === "getCalendarEvents") {
                      const res = await fetch("/api/calendar/events", {
                        credentials: "include",
                      });
                      toolResult = await res.json();
                    } else if (call.name === "createGoogleDoc") {
                      const res = await fetch("/api/docs/create", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify((call.args as any) || {}),
                        credentials: "include",
                      });
                      toolResult = await res.json();
                    } else if (call.name === "pushToGitHub") {
                      const args = call.args as any;
                      let payload = args.client_payload;
                      if (typeof payload === "string") {
                        try {
                          payload = JSON.parse(payload);
                        } catch (e) {
                          payload = { content: payload };
                        }
                      }
                      const res = await fetch("/api/github/dispatch", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                          event_type: args.event_type,
                          client_payload: payload,
                        }),
                        credentials: "include",
                      });
                      toolResult = await res.json();
                    } else if (call.name === "displayOutput") {
                      const args = call.args as any;
                      setOutput({
                        title: args.title || "Ausgabe",
                        content: args.content,
                      });
                      setIsOutputOpen(true);
                      toolResult = {
                        success: true,
                        message: "Inhalt wird im Ausgabefenster angezeigt.",
                      };
                    } else if (call.name === "omegaBackendCall") {
                      const args = call.args as any;
                      const res = await fetch("/api/omega/task", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(args),
                      });
                      toolResult = await res.json();
                    } else if (call.name === "cursorInputInjection") {
                      const args = call.args as any;
                      const res = await fetch("/api/cursor/inject", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ content: args.content }),
                      });
                      toolResult = await res.json();
                    } else if (call.name === "localFileWrite") {
                      const args = call.args as any;
                      const res = await fetch("/api/system/write", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(args),
                      });
                      toolResult = await res.json();
                    }
                  } catch (e: any) {
                    toolResult = { error: e.message };
                  }
                  functionResponses.push({
                    id: call.id,
                    name: call.name,
                    response: toolResult,
                  });
                }

                sessionPromise.then((session) => {
                  session.sendToolResponse({ functionResponses });
                });
              }
            },
            onclose: () => {
              stopLiveSession();
            },
            onerror: (err) => {
              console.error("Live API Error:", err);
              setError("Connection error with Gemini Live.");
              stopLiveSession();
              reject(err);
            },
          },
        });

        sessionRef.current = sessionPromise;
      } catch (err: any) {
        console.error(err);
        setError(err.message || "Failed to start live session.");
        setIsConnecting(false);
        reject(err);
      }
    });
  };

  const stopLiveSession = () => {
    if (sessionRef.current) {
      sessionRef.current.then((session: any) => {
        try {
          session.close();
        } catch (e) {}
      });
      sessionRef.current = null;
    }
    audioRecorderRef.current.stop();
    audioPlayerRef.current.stop();
    setIsLive(false);
    setIsConnecting(false);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopLiveSession();
    };
  }, []);

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [transcript]);

  const handleSendMessage = () => {
    const text = textInputValue.trim();
    if (!text) return;

    setTranscript((prev) => [...prev, { role: "user", text }]);

    if (!isLive && !isConnecting && !sessionRef.current) {
      startLiveSession().then(() => {
        if (sessionRef.current) {
          sessionRef.current
            .then((session: any) => {
              session.sendClientContent({
                turns: [{ role: "user", parts: [{ text }] }],
                turnComplete: true,
              });
            })
            .catch((e: any) => console.error("Fehler beim Senden:", e));
        }
      });
    } else if (sessionRef.current) {
      sessionRef.current
        .then((session: any) => {
          session.sendClientContent({
            turns: [{ role: "user", parts: [{ text }] }],
            turnComplete: true,
          });
        })
        .catch((e: any) => console.error("Fehler beim Senden:", e));
    }

    setTextInputValue("");
  };

  return (
    <div className="flex flex-col absolute inset-0 overflow-hidden bg-zinc-950 text-zinc-200 font-sans">
      {/* Header */}
      <header className="flex justify-between items-center px-6 py-4 bg-zinc-900 border-b border-red-900/30 shadow-md z-10">
        <h1 className="text-xl font-bold flex items-center gap-3 text-zinc-100 tracking-wide">
          <span className="bg-red-800 text-red-50 p-2 rounded-md shadow-[0_0_15px_rgba(153,27,27,0.5)]">
            <Volume2 size={20} />
          </span>
          OMEGA{" "}
          <span className="text-xs font-normal text-zinc-500 tracking-widest uppercase">
            Live
          </span>
        </h1>
        <div className="flex items-center gap-4">
          <button
            onClick={() => {
              const text = transcript
                .map((m) => `[${m.role.toUpperCase()}]: ${m.text}`)
                .join("\n\n");
              navigator.clipboard.writeText(text);
              setCopiedIndex(-1);
              setTimeout(() => setCopiedIndex(null), 2000);
            }}
            className="p-2 text-zinc-500 hover:text-red-400 hover:bg-zinc-800 rounded-md transition-colors"
            title="Chat kopieren"
          >
            {copiedIndex === -1 ? (
              <Check size={20} className="text-green-500" />
            ) : (
              <Copy size={20} />
            )}
          </button>
          <button
            onClick={() => {
              if (window.confirm("Gesprächsverlauf wirklich löschen?")) {
                setTranscript([]);
                localStorage.removeItem("omega_transcript");
              }
            }}
            className="p-2 text-zinc-500 hover:text-red-400 hover:bg-zinc-800 rounded-md transition-colors"
            title="Chat leeren"
          >
            <Trash2 size={20} />
          </button>
          <button
            onClick={() => setIsSettingsOpen(true)}
            className="p-2 text-zinc-400 hover:text-red-50 hover:bg-zinc-800 rounded-md transition-colors"
            title="Einstellungen"
          >
            <Settings size={20} />
          </button>
          {!isAuthenticated ? (
            <button
              onClick={handleConnect}
              className="flex items-center gap-2 bg-red-800 hover:bg-red-700 text-red-50 px-4 py-2 rounded-md transition-colors text-sm font-medium border border-red-700"
            >
              <LogIn size={16} />
              Connect Google
            </button>
          ) : (
            <div className="flex items-center gap-3 bg-zinc-800 px-4 py-2 rounded-md border border-zinc-700">
              {user?.photos?.[0]?.value ? (
                <img
                  src={user.photos[0].value}
                  alt={user.displayName}
                  className="w-8 h-8 rounded-md border border-zinc-600"
                />
              ) : (
                <div className="w-8 h-8 rounded-md bg-zinc-700 flex items-center justify-center">
                  <User size={16} className="text-zinc-400" />
                </div>
              )}
              <span className="text-sm font-medium text-zinc-300">
                {user?.displayName || "Connected"}
              </span>
              <button
                onClick={() => {
                  fetch("/api/auth/logout", { method: "POST" }).then(() => {
                    setIsAuthenticated(false);
                    setUser(null);
                  });
                }}
                className="ml-2 text-xs text-red-500 hover:text-red-400 uppercase tracking-wider"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 bg-zinc-950 scrollbar-hide">
        {transcript.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-zinc-600 space-y-4">
            <MessageSquare size={48} className="opacity-20" />
            <p className="text-lg font-light tracking-wide">
              Bereit für die Konversation.
            </p>
          </div>
        )}
        <AnimatePresence initial={false}>
          {transcript.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex group relative ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] md:max-w-[70%] p-4 rounded-lg shadow-md group ${
                  msg.role === "user"
                    ? "bg-red-900/80 text-red-50 border border-red-800 rounded-tr-none"
                    : "bg-zinc-800 text-zinc-200 border border-zinc-700 rounded-tl-none"
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <div
                    className={`text-[10px] uppercase tracking-widest font-bold ${msg.role === "user" ? "text-red-300" : "text-zinc-500"}`}
                  >
                    {msg.role === "user" ? "Du" : "OMEGA"}
                  </div>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(msg.text);
                      setCopiedIndex(i);
                      setTimeout(() => setCopiedIndex(null), 2000);
                    }}
                    className="opacity-0 group-hover:opacity-100 transition-opacity p-1 -mt-1 -mr-1 hover:bg-white/10 rounded"
                    title="Kopieren"
                  >
                    {copiedIndex === i ? (
                      <Check size={12} className="text-green-400" />
                    ) : (
                      <Copy size={12} className="text-zinc-400" />
                    )}
                  </button>
                </div>
                <div className="whitespace-pre-wrap leading-relaxed break-words">
                  {msg.text}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        <div ref={chatEndRef} />
      </div>

      {/* Error Message Overlay */}
      {error && (
        <div className="absolute top-20 left-1/2 -translate-x-1/2 bg-red-900/90 border border-red-500 text-red-100 px-6 py-3 rounded-md flex items-center gap-3 shadow-2xl z-50">
          <AlertCircle size={20} />
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}

      {/* Control Area (Bottom) */}
      <div className="p-4 md:p-6 bg-zinc-900 border-t border-red-900/30 flex flex-col items-center justify-center relative shadow-[0_-10px_40px_rgba(0,0,0,0.5)] z-10 w-full">
        {/* Status Text */}
        <div className="absolute top-4 left-6 text-xs text-zinc-500 uppercase tracking-widest hidden md:block">
          {isConnecting ? "Verbinde..." : isLive ? "Live" : "Standby"}
        </div>

        {/* Control Content: Mic and Text Input */}
        <div className="flex flex-col md:flex-row items-center justify-center gap-6 w-full max-w-4xl">
          {/* Big Microphone Button */}
          <button
            onClick={isLive ? stopLiveSession : startLiveSession}
            disabled={isConnecting}
            className={`relative group flex-shrink-0 flex items-center justify-center w-20 h-20 md:w-24 md:h-24 rounded-full transition-all duration-300 ${
              isLive
                ? "bg-red-700 hover:bg-red-600 shadow-[0_0_40px_rgba(185,28,28,0.6)]"
                : "bg-zinc-800 hover:bg-zinc-700 shadow-[0_0_20px_rgba(0,0,0,0.5)] border border-zinc-700"
            } ${isConnecting ? "opacity-50 cursor-not-allowed" : ""}`}
          >
            {/* Pulsing rings when live */}
            {isLive && (
              <>
                <div className="absolute inset-0 rounded-full border-2 border-red-500 animate-ping opacity-50"></div>
                <div className="absolute inset-[-15px] rounded-full border border-red-500/30 animate-pulse"></div>
              </>
            )}

            {isConnecting ? (
              <Loader2 size={32} className="text-zinc-300 animate-spin" />
            ) : isLive ? (
              <MicOff size={32} className="text-red-50" />
            ) : (
              <Mic
                size={32}
                className="text-zinc-300 group-hover:text-red-400 transition-colors"
              />
            )}
          </button>

          {/* Text Input Area */}
          <div className="flex w-full items-center gap-2">
            <textarea
              value={textInputValue}
              onChange={(e) => setTextInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage();
                }
              }}
              placeholder="Text einfügen oder tippen... (Shift+Enter für Zeilenumbruch)"
              className="bg-zinc-800 border border-zinc-700 text-zinc-200 rounded-md px-4 py-3 text-sm focus:outline-none focus:border-red-700 w-full transition-all resize-none h-14"
            />
            <button
              onClick={handleSendMessage}
              disabled={!textInputValue.trim()}
              className="bg-red-800 hover:bg-red-700 text-red-50 p-3 rounded-md transition-colors disabled:opacity-50 flex items-center justify-center flex-shrink-0 h-14 w-14"
              title="Senden"
            >
              <MessageSquare size={20} />
            </button>
          </div>
        </div>

        {/* Output Panel Trigger (Floating) */}
        <div className="absolute right-4 top-4 md:right-6 md:top-auto flex flex-col gap-4 items-end">
          {enableThoughtStream && thoughtStream.length > 0 && (
            <button
              onClick={() => setIsThoughtStreamOpen(!isThoughtStreamOpen)}
              className={`p-3 rounded-md shadow-lg transition-all hover:scale-105 flex items-center gap-2 border ${
                isThoughtStreamOpen
                  ? "bg-zinc-700 border-zinc-500"
                  : "bg-zinc-800 border-zinc-700 hover:border-zinc-600"
              }`}
            >
              <div className="flex gap-1">
                <div className="w-1 h-3 bg-red-500 animate-pulse"></div>
                <div className="w-1 h-3 bg-red-500 animate-pulse delay-75"></div>
                <div className="w-1 h-3 bg-red-500 animate-pulse delay-150"></div>
              </div>
              <span className="text-xs font-bold text-zinc-300 uppercase tracking-wider">
                Stream
              </span>
            </button>
          )}
          {output && (
            <button
              onClick={() => setIsOutputOpen(true)}
              className="bg-red-800 hover:bg-red-700 text-red-50 p-3 rounded-md shadow-lg transition-transform hover:scale-105 flex items-center gap-2 border border-red-600"
            >
              <MessageSquare size={16} />
              <span className="text-xs font-bold uppercase tracking-wider">
                Letzte Ausgabe
              </span>
            </button>
          )}
        </div>
      </div>

      {/* Thought Stream Sidebar */}
      <AnimatePresence>
        {isThoughtStreamOpen && enableThoughtStream && (
          <motion.div
            initial={{ x: 400 }}
            animate={{ x: 0 }}
            exit={{ x: 400 }}
            className="fixed top-0 right-0 w-96 h-full bg-zinc-950/95 border-l border-red-900/50 z-[70] flex flex-col shadow-2xl backdrop-blur-md"
          >
            <div className="p-4 border-b border-red-900/30 flex justify-between items-center bg-red-900/10">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-ping"></div>
                <h3 className="text-red-500 font-mono text-sm font-bold tracking-widest uppercase">
                  Process_Data_Stream
                </h3>
              </div>
              <button
                onClick={() => setIsThoughtStreamOpen(false)}
                className="text-red-500/50 hover:text-red-400 transition-colors"
              >
                <X size={18} />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-[10px] scrollbar-hide">
              {thoughtStream.map((thought) => (
                <div
                  key={thought.id}
                  className="border-l-2 border-red-900/50 pl-3 py-1 hover:bg-red-900/10 transition-colors"
                >
                  <div className="flex justify-between text-zinc-500 mb-1">
                    <span>
                      [{new Date(thought.timestamp).toLocaleTimeString()}]{" "}
                      {thought.type}
                    </span>
                    <span>ID: {thought.id}</span>
                  </div>
                  <div className="text-zinc-400 break-all whitespace-pre-wrap">
                    {JSON.stringify(
                      thought.data,
                      (key, value) =>
                        key === "data" &&
                        typeof value === "string" &&
                        value.length > 50
                          ? value.substring(0, 20) + "..."
                          : value,
                      2,
                    )}
                  </div>
                </div>
              ))}
            </div>
            <div className="p-4 bg-red-900/10 border-t border-red-900/30">
              <div className="text-[9px] text-red-500/60 uppercase mb-2 tracking-widest">
                System_Metrics
              </div>
              <div className="grid grid-cols-2 gap-2 text-[10px] text-zinc-400">
                <div className="flex justify-between">
                  <span>Latency:</span> <span>~45ms</span>
                </div>
                <div className="flex justify-between">
                  <span>Buffer:</span> <span>{thoughtStream.length}/50</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Output Modal */}
      <AnimatePresence>
        {isOutputOpen && output && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 flex items-center justify-center z-[60] p-4 md:p-10 backdrop-blur-sm"
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              className="bg-zinc-900 rounded-md w-full max-w-4xl h-[80vh] border border-red-900/50 shadow-2xl flex flex-col overflow-hidden"
            >
              <div className="flex justify-between items-center p-5 border-b border-red-900/30 bg-zinc-950">
                <h3 className="text-lg font-semibold flex items-center gap-2 text-zinc-100 tracking-wide">
                  <MessageSquare size={18} className="text-red-500" />
                  {output.title}
                </h3>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(output.content);
                    }}
                    className="text-xs bg-zinc-800 hover:bg-zinc-700 text-zinc-300 border border-zinc-700 px-3 py-1.5 rounded-md transition-colors uppercase tracking-wider"
                  >
                    Kopieren
                  </button>
                  <button
                    onClick={() => setIsOutputOpen(false)}
                    className="text-zinc-500 hover:text-red-400 transition-colors p-1"
                  >
                    <X size={24} />
                  </button>
                </div>
              </div>
              <div className="flex-1 p-6 overflow-y-auto font-mono text-sm bg-zinc-950 text-zinc-300 whitespace-pre-wrap">
                {output.content}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Settings Modal */}
      {isSettingsOpen && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
          <div className="bg-zinc-900 rounded-md w-full max-w-md border border-red-900/50 shadow-2xl overflow-hidden">
            <div className="flex justify-between items-center p-5 border-b border-red-900/30 bg-zinc-950">
              <h3 className="text-lg font-semibold flex items-center gap-2 text-zinc-100 tracking-wide">
                <Settings size={18} className="text-red-500" />
                Einstellungen
              </h3>
              <button
                onClick={() => setIsSettingsOpen(false)}
                className="text-zinc-500 hover:text-red-400 transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            <div className="p-5 space-y-6 max-h-[70vh] overflow-y-auto scrollbar-hide">
              {/* Basis Einstellungen */}
              <div className="space-y-4">
                <h4 className="text-xs font-bold text-red-500 uppercase tracking-widest border-b border-red-900/30 pb-2">
                  Basis
                </h4>
                <div>
                  <label className="block text-sm font-medium text-zinc-400 mb-2">
                    Voice
                  </label>
                  <select
                    value={voice}
                    onChange={(e) => setVoice(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-md px-4 py-2.5 text-zinc-200 focus:outline-none focus:border-red-700 transition-colors"
                  >
                    <option value="Puck">Puck</option>
                    <option value="Charon">Charon</option>
                    <option value="Kore">Kore</option>
                    <option value="Fenrir">Fenrir</option>
                    <option value="Zephyr">Zephyr</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-zinc-400 mb-2">
                    Sprache
                  </label>
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-md px-4 py-2.5 text-zinc-200 focus:outline-none focus:border-red-700 transition-colors"
                  >
                    <option value="Auto">Automatisch</option>
                    <option value="Deutsch">Deutsch</option>
                    <option value="Englisch">Englisch</option>
                    <option value="Spanisch">Spanisch</option>
                    <option value="Französisch">Französisch</option>
                  </select>
                </div>
              </div>

              {/* Verhalten */}
              <div className="space-y-4">
                <h4 className="text-xs font-bold text-red-500 uppercase tracking-widest border-b border-red-900/30 pb-2">
                  Verhalten
                </h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-zinc-400 mb-2">
                      Emotion
                    </label>
                    <select
                      value={emotion}
                      onChange={(e) => setEmotion(e.target.value)}
                      className="w-full bg-zinc-950 border border-zinc-800 rounded-md px-4 py-2.5 text-zinc-200 focus:outline-none focus:border-red-700 transition-colors"
                    >
                      <option value="Neutral">Neutral</option>
                      <option value="Fröhlich">Fröhlich</option>
                      <option value="Empathisch">Empathisch</option>
                      <option value="Professionell">Professionell</option>
                      <option value="Sarkastisch">Sarkastisch</option>
                      <option value="Aufgeregt">Aufgeregt</option>
                      <option value="Traurig">Traurig</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-zinc-400 mb-2">
                      Bias Damper
                    </label>
                    <select
                      value={biasDamper}
                      onChange={(e) => setBiasDamper(e.target.value)}
                      className="w-full bg-zinc-950 border border-zinc-800 rounded-md px-4 py-2.5 text-zinc-200 focus:outline-none focus:border-red-700 transition-colors"
                    >
                      <option value="Deaktiviert">Deaktiviert</option>
                      <option value="Niedrig">Niedrig</option>
                      <option value="Mittel">Mittel</option>
                      <option value="Hoch">Hoch</option>
                      <option value="Maximal">Maximal</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-zinc-400 mb-2">
                      Gesprächsmodus
                    </label>
                    <select
                      value={conversationMode}
                      onChange={(e) => setConversationMode(e.target.value)}
                      className="w-full bg-zinc-950 border border-zinc-800 rounded-md px-4 py-2.5 text-zinc-200 focus:outline-none focus:border-red-700 transition-colors"
                    >
                      <option value="Freier Dialog">Freier Dialog</option>
                      <option value="Recherche & Analyse">
                        Recherche & Analyse
                      </option>
                      <option value="Kritischer Diskurs">
                        Kritischer Diskurs
                      </option>
                      <option value="Brainstorming">Brainstorming</option>
                      <option value="Empathisches Zuhören">
                        Empathisches Zuhören
                      </option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-zinc-400 mb-2">
                      Anpassung
                    </label>
                    <select
                      value={adaptationSpeed}
                      onChange={(e) => setAdaptationSpeed(e.target.value)}
                      className="w-full bg-zinc-950 border border-zinc-800 rounded-md px-4 py-2.5 text-zinc-200 focus:outline-none focus:border-red-700 transition-colors"
                    >
                      <option value="Statisch (Keine Anpassung)">
                        Statisch
                      </option>
                      <option value="Langsam (Träge)">Langsam</option>
                      <option value="Moderat">Moderat</option>
                      <option value="Sofort (Spiegelnd)">Sofort</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-zinc-400 mb-2">
                    Kreativität (Temperatur)
                  </label>
                  <select
                    value={creativity}
                    onChange={(e) => setCreativity(e.target.value)}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-md px-4 py-2.5 text-zinc-200 focus:outline-none focus:border-red-700 transition-colors"
                  >
                    <option value="0.2">Niedrig (Faktisch & Präzise)</option>
                    <option value="0.7">Mittel (Ausgewogen)</option>
                    <option value="1.2">Hoch (Kreativ & Lebendig)</option>
                    <option value="1.8">Maximal (Brainstorming)</option>
                  </select>
                </div>

                <div className="flex flex-col gap-4 pt-2">
                  <label className="flex items-center gap-3 cursor-pointer group">
                    <input
                      type="checkbox"
                      checked={affectiveDialog}
                      onChange={(e) => setAffectiveDialog(e.target.checked)}
                      className="w-5 h-5 rounded border-zinc-700 bg-zinc-950 text-red-700 focus:ring-red-900 focus:ring-offset-zinc-900"
                    />
                    <div>
                      <div className="text-sm font-medium text-zinc-300 group-hover:text-red-400 transition-colors">
                        Emotionale Anpassung
                      </div>
                      <div className="text-xs text-zinc-500">
                        Erkennt Emotionen und passt Antworten an.
                      </div>
                    </div>
                  </label>

                  <label className="flex items-center gap-3 cursor-pointer group">
                    <input
                      type="checkbox"
                      checked={proactiveAudio}
                      onChange={(e) => setProactiveAudio(e.target.checked)}
                      className="w-5 h-5 rounded border-zinc-700 bg-zinc-950 text-red-700 focus:ring-red-900 focus:ring-offset-zinc-900"
                    />
                    <div>
                      <div className="text-sm font-medium text-zinc-300 group-hover:text-red-400 transition-colors">
                        Proaktives Zuhören
                      </div>
                      <div className="text-xs text-zinc-500">
                        Ignoriert irrelevante Eingaben.
                      </div>
                    </div>
                  </label>
                </div>
              </div>

              {/* System Instruction */}
              <div className="space-y-4">
                <h4 className="text-xs font-bold text-red-500 uppercase tracking-widest border-b border-red-900/30 pb-2">
                  System
                </h4>
                <div>
                  <textarea
                    value={systemInstruction}
                    onChange={(e) => setSystemInstruction(e.target.value)}
                    rows={4}
                    className="w-full bg-zinc-950 border border-zinc-800 rounded-md px-4 py-3 text-zinc-300 focus:outline-none focus:border-red-700 transition-colors resize-none text-xs font-mono"
                    placeholder="System Instruction..."
                  />
                </div>
              </div>

              {/* Experimentell */}
              <div className="space-y-4">
                <h4 className="text-xs font-bold text-red-500 uppercase tracking-widest border-b border-red-900/30 pb-2">
                  Experimentell
                </h4>

                <label className="flex items-center gap-3 cursor-pointer group mb-4">
                  <input
                    type="checkbox"
                    checked={enableExperimental}
                    onChange={(e) => setEnableExperimental(e.target.checked)}
                    className="w-5 h-5 rounded border-zinc-700 bg-zinc-950 text-red-700 focus:ring-red-900 focus:ring-offset-zinc-900"
                  />
                  <div>
                    <div className="text-sm font-medium text-zinc-300 group-hover:text-red-400 transition-colors">
                      Experimentelle Features aktivieren
                    </div>
                    <div className="text-xs text-zinc-500">
                      Schaltet unzuverlässige API-Funktionen frei.
                    </div>
                  </div>
                </label>

                <label className="flex items-center gap-3 cursor-pointer group mb-4">
                  <input
                    type="checkbox"
                    checked={enableCursorInjection}
                    onChange={(e) => setEnableCursorInjection(e.target.checked)}
                    className="w-5 h-5 rounded border-zinc-700 bg-zinc-950 text-red-700 focus:ring-red-900 focus:ring-offset-zinc-900"
                  />
                  <div>
                    <div className="text-sm font-medium text-zinc-300 group-hover:text-red-400 transition-colors">
                      Cursor Bridge (Injection) aktivieren
                    </div>
                    <div className="text-xs text-zinc-500">
                      Erlaubt es der KI, Text/Code in Cursor einzufügen.
                    </div>
                  </div>
                </label>

                {enableExperimental && (
                  <div className="space-y-4 pl-8 border-l-2 border-red-900/30">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-zinc-400 mb-2">
                          Geschwindigkeit
                        </label>
                        <select
                          value={speed}
                          onChange={(e) => setSpeed(e.target.value)}
                          className="w-full bg-zinc-950 border border-zinc-800 rounded-md px-4 py-2.5 text-zinc-200 focus:outline-none focus:border-red-700 transition-colors"
                        >
                          <option value="Sehr langsam">Sehr langsam</option>
                          <option value="Langsam">Langsam</option>
                          <option value="Normal">Normal</option>
                          <option value="Schnell">Schnell</option>
                          <option value="Sehr schnell">Sehr schnell</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-zinc-400 mb-2">
                          Tonlage
                        </label>
                        <select
                          value={pitch}
                          onChange={(e) => setPitch(e.target.value)}
                          className="w-full bg-zinc-950 border border-zinc-800 rounded-md px-4 py-2.5 text-zinc-200 focus:outline-none focus:border-red-700 transition-colors"
                        >
                          <option value="Sehr tief">Sehr tief</option>
                          <option value="Tief">Tief</option>
                          <option value="Normal">Normal</option>
                          <option value="Hoch">Hoch</option>
                          <option value="Sehr hoch">Sehr hoch</option>
                        </select>
                      </div>
                    </div>

                    <label className="flex items-center gap-3 cursor-pointer group mt-4">
                      <input
                        type="checkbox"
                        checked={enableThoughtStream}
                        onChange={(e) => {
                          setEnableThoughtStream(e.target.checked);
                          if (!e.target.checked) setIsThoughtStreamOpen(false);
                        }}
                        className="w-5 h-5 rounded border-zinc-700 bg-zinc-950 text-red-700 focus:ring-red-900 focus:ring-offset-zinc-900"
                      />
                      <div>
                        <div className="text-sm font-medium text-zinc-300 group-hover:text-red-400 transition-colors">
                          Thought Stream (Prozessdaten)
                        </div>
                        <div className="text-xs text-zinc-500">
                          Zeigt interne API-Daten an.
                        </div>
                      </div>
                    </label>
                  </div>
                )}
              </div>
            </div>

            <div className="p-5 border-t border-red-900/30 bg-zinc-950 flex justify-end">
              <button
                onClick={() => setIsSettingsOpen(false)}
                className="bg-red-800 hover:bg-red-700 text-red-50 px-6 py-2 rounded-md font-medium transition-colors border border-red-700 tracking-wide uppercase text-sm"
              >
                Schließen
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
