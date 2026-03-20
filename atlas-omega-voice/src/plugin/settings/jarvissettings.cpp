#include "jarvissettings.h"

#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QNetworkRequest>
#include <QIODevice>
#include <QNetworkReply>
#include <QUrl>
#include <QProcessEnvironment>

namespace {
QString normalizeLlmBaseUrl(QString url)
{
    url = url.trimmed();
    while (url.endsWith(QLatin1Char('/'))) {
        url.chop(1);
    }
    const QString suf = QStringLiteral("/v1/chat/completions");
    if (url.endsWith(suf, Qt::CaseInsensitive)) {
        url.chop(suf.size());
    }
    while (url.endsWith(QLatin1Char('/'))) {
        url.chop(1);
    }
    return url;
}
} // namespace


JarvisSettings::JarvisSettings(QNetworkAccessManager *nam, QObject *parent)
    : QObject(parent)
    , m_networkManager(nam)
{
    loadSettings();
    populateModelList();
    populateVoiceList();
}

// ─────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────

QString JarvisSettings::jarvisDataDir() const
{
    const QString dir = QDir::homePath() + QStringLiteral("/.local/share/jarvis");
    QDir().mkpath(dir);
    return dir;
}

// ─────────────────────────────────────────────
// Persistence
// ─────────────────────────────────────────────

void JarvisSettings::loadSettings()
{
    // Optional: gleicher Name wie in OMEGA .env — in Plasma z. B. ~/.config/plasma-workspace/env/ setzen (kein Secret).
    const QString envUrl =
        QProcessEnvironment::systemEnvironment().value(QStringLiteral("CORE_API_URL")).trimmed();
    const QString defaultBase =
        envUrl.isEmpty() ? QStringLiteral("http://127.0.0.1:8000") : envUrl;

    m_llmServerUrl = m_settings.value(QStringLiteral("llm/serverUrl"), defaultBase).toString();
    m_currentModelName = m_settings.value(QStringLiteral("llm/modelName"),
                                           QStringLiteral("Qwen2.5-Coder-1.5B-Instruct")).toString();
    m_currentVoiceName = m_settings.value(QStringLiteral("tts/voiceName"),
                                           QStringLiteral("en_GB-alan-medium")).toString();
    m_maxHistoryPairs = m_settings.value(QStringLiteral("chat/maxHistoryPairs"), 20).toInt();
    m_wakeBufferSeconds = m_settings.value(QStringLiteral("audio/wakeBufferSeconds"), 2).toInt();
    m_voiceCmdMaxSeconds = m_settings.value(QStringLiteral("audio/voiceCmdMaxSeconds"), 8).toInt();
    m_autoStartWakeWord = m_settings.value(QStringLiteral("audio/autoStartWakeWord"), true).toBool();
    m_ttsRate = m_settings.value(QStringLiteral("tts/rate"), 0.05).toDouble();
    m_ttsPitch = m_settings.value(QStringLiteral("tts/pitch"), -0.1).toDouble();
    m_ttsVolume = m_settings.value(QStringLiteral("tts/volume"), 0.85).toDouble();
    m_ttsMuted = m_settings.value(QStringLiteral("tts/muted"), false).toBool();
    m_personalityPrompt = m_settings.value(QStringLiteral("chat/personalityPrompt")).toString();

    m_llmServerUrl = normalizeLlmBaseUrl(m_llmServerUrl);

    // Resolve piper model path from saved voice name
    const QString voicesDir = jarvisDataDir() + QStringLiteral("/piper-voices");
    const QString savedPath = voicesDir + QStringLiteral("/") + m_currentVoiceName + QStringLiteral(".onnx");
    if (QFile::exists(savedPath)) {
        m_piperModelPath = savedPath;
    } else {
        // Fallback search
        const QStringList fallbackPaths = {
            QDir::homePath() + QStringLiteral("/.local/share/jarvis/piper-voices/en_GB-alan-medium.onnx"),
            QStringLiteral("/usr/share/jarvis/piper-voices/en_GB-alan-medium.onnx"),
        };
        for (const auto &path : fallbackPaths) {
            if (QFile::exists(path)) { m_piperModelPath = path; break; }
        }
    }
}

void JarvisSettings::saveSettings()
{
    m_settings.setValue(QStringLiteral("llm/serverUrl"), m_llmServerUrl);
    m_settings.setValue(QStringLiteral("llm/modelName"), m_currentModelName);
    m_settings.setValue(QStringLiteral("tts/voiceName"), m_currentVoiceName);
    m_settings.setValue(QStringLiteral("chat/maxHistoryPairs"), m_maxHistoryPairs);
    m_settings.setValue(QStringLiteral("audio/wakeBufferSeconds"), m_wakeBufferSeconds);
    m_settings.setValue(QStringLiteral("audio/voiceCmdMaxSeconds"), m_voiceCmdMaxSeconds);
    m_settings.setValue(QStringLiteral("audio/autoStartWakeWord"), m_autoStartWakeWord);
    m_settings.setValue(QStringLiteral("tts/rate"), m_ttsRate);
    m_settings.setValue(QStringLiteral("tts/pitch"), m_ttsPitch);
    m_settings.setValue(QStringLiteral("tts/volume"), m_ttsVolume);
    m_settings.setValue(QStringLiteral("tts/muted"), m_ttsMuted);
    m_settings.setValue(QStringLiteral("chat/personalityPrompt"), m_personalityPrompt);
    m_settings.sync();
}

// ─────────────────────────────────────────────
// Setters
// ─────────────────────────────────────────────

void JarvisSettings::setLlmServerUrl(const QString &url)
{
    const QString normalized = normalizeLlmBaseUrl(url);
    if (m_llmServerUrl != normalized) {
        m_llmServerUrl = normalized;
        saveSettings();
        emit llmServerUrlChanged();
    }
}

void JarvisSettings::setCurrentModelName(const QString &name)
{
    if (m_currentModelName != name) {
        m_currentModelName = name;
        saveSettings();
        emit currentModelNameChanged();
    }
}

void JarvisSettings::setMaxHistoryPairs(int pairs)
{
    pairs = qBound(5, pairs, 100);
    if (m_maxHistoryPairs != pairs) {
        m_maxHistoryPairs = pairs;
        saveSettings();
        emit maxHistoryPairsChanged();
    }
}

void JarvisSettings::setWakeBufferSeconds(int seconds)
{
    seconds = qBound(1, seconds, 5);
    if (m_wakeBufferSeconds != seconds) {
        m_wakeBufferSeconds = seconds;
        saveSettings();
        emit wakeBufferSecondsChanged();
    }
}

void JarvisSettings::setVoiceCmdMaxSeconds(int seconds)
{
    seconds = qBound(3, seconds, 30);
    if (m_voiceCmdMaxSeconds != seconds) {
        m_voiceCmdMaxSeconds = seconds;
        saveSettings();
        emit voiceCmdMaxSecondsChanged();
    }
}

void JarvisSettings::setAutoStartWakeWord(bool enabled)
{
    if (m_autoStartWakeWord != enabled) {
        m_autoStartWakeWord = enabled;
        saveSettings();
        emit autoStartWakeWordChanged();
    }
}

void JarvisSettings::setPersonalityPrompt(const QString &prompt)
{
    if (m_personalityPrompt != prompt) {
        m_personalityPrompt = prompt;
        saveSettings();
        emit personalityPromptChanged();
    }
}

void JarvisSettings::setTtsRate(double rate)
{
    m_ttsRate = qBound(-1.0, rate, 1.0);
    saveSettings();
    emit ttsRateChanged();
}

void JarvisSettings::setTtsPitch(double pitch)
{
    m_ttsPitch = qBound(-1.0, pitch, 1.0);
    saveSettings();
    emit ttsPitchChanged();
}

void JarvisSettings::setTtsVolume(double volume)
{
    m_ttsVolume = qBound(0.0, volume, 1.0);
    saveSettings();
    emit ttsVolumeChanged();
}

void JarvisSettings::setTtsMuted(bool muted)
{
    if (m_ttsMuted != muted) {
        m_ttsMuted = muted;
        saveSettings();
        emit ttsMutedChanged();
    }
}

// ─────────────────────────────────────────────
// Model & Voice Lists
// ─────────────────────────────────────────────

void JarvisSettings::populateModelList()
{
    m_availableLlmModels = {
        QVariantMap{
            {QStringLiteral("id"), QStringLiteral("core-local-min")},
            {QStringLiteral("name"), QStringLiteral("CORE Local (Fast)")},
            {QStringLiteral("size"), QStringLiteral("Lokal")},
            {QStringLiteral("url"), QStringLiteral("")},
            {QStringLiteral("desc"), QStringLiteral("Qwen 2.5 1.5B (RTX 3050 OC)")}
        },
        QVariantMap{
            {QStringLiteral("id"), QStringLiteral("core-local-max")},
            {QStringLiteral("name"), QStringLiteral("CORE Local (Deep)")},
            {QStringLiteral("size"), QStringLiteral("Lokal")},
            {QStringLiteral("url"), QStringLiteral("")},
            {QStringLiteral("desc"), QStringLiteral("Qwen 2.5 14B (RTX 3050 OC - Slow/Intense)")}
        },
        QVariantMap{
            {QStringLiteral("id"), QStringLiteral("core-api-min")},
            {QStringLiteral("name"), QStringLiteral("CORE API (Fast)")},
            {QStringLiteral("size"), QStringLiteral("Cloud")},
            {QStringLiteral("url"), QStringLiteral("")},
            {QStringLiteral("desc"), QStringLiteral("Gemini 2.5 Flash (Google Cloud)")}
        },
        QVariantMap{
            {QStringLiteral("id"), QStringLiteral("core-api-max")},
            {QStringLiteral("name"), QStringLiteral("CORE API (Deep)")},
            {QStringLiteral("size"), QStringLiteral("Cloud")},
            {QStringLiteral("url"), QStringLiteral("")},
            {QStringLiteral("desc"), QStringLiteral("Gemini 2.5 Pro (Google Cloud)")}
        }
    };

    for (int i = 0; i < m_availableLlmModels.size(); ++i) {
        auto map = m_availableLlmModels[i].toMap();
        map[QStringLiteral("downloaded")] = true; // Immer true, weil sie via OMEGA bedient werden
        m_availableLlmModels[i] = map;
    }

    emit availableLlmModelsChanged();
}

void JarvisSettings::populateVoiceList()
{
    m_availableTtsVoices = {
        QVariantMap{

            {QStringLiteral("id"), QStringLiteral("de_DE-thorsten-high")},

            {QStringLiteral("name"), QStringLiteral("Thorsten (German Male)")},

            {QStringLiteral("lang"), QStringLiteral("Deutsch (DE)")},

            {QStringLiteral("url"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx")},

            {QStringLiteral("urlJson"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/high/de_DE-thorsten-high.onnx.json")},

            {QStringLiteral("desc"), QStringLiteral("Klare, sehr gute deutsche Männerstimme (Thorsten Müller)")}

        },

        QVariantMap{

            {QStringLiteral("id"), QStringLiteral("de_DE-kerstin-low")},

            {QStringLiteral("name"), QStringLiteral("Kerstin (German Female)")},

            {QStringLiteral("lang"), QStringLiteral("Deutsch (DE)")},

            {QStringLiteral("url"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/kerstin/low/de_DE-kerstin-low.onnx")},

            {QStringLiteral("urlJson"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/kerstin/low/de_DE-kerstin-low.onnx.json")},

            {QStringLiteral("desc"), QStringLiteral("Deutsche Frauenstimme")}

        },
        QVariantMap{
            {QStringLiteral("id"), QStringLiteral("en_GB-alan-medium")},
            {QStringLiteral("name"), QStringLiteral("Alan (British Male)")},
            {QStringLiteral("lang"), QStringLiteral("English (UK)")},
            {QStringLiteral("url"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx")},
            {QStringLiteral("urlJson"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json")},
            {QStringLiteral("desc"), QStringLiteral("Recommended — closest to J.A.R.V.I.S.")}
        },
        QVariantMap{
            {QStringLiteral("id"), QStringLiteral("en_GB-cori-high")},
            {QStringLiteral("name"), QStringLiteral("Cori (British Female)")},
            {QStringLiteral("lang"), QStringLiteral("English (UK)")},
            {QStringLiteral("url"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/cori/high/en_GB-cori-high.onnx")},
            {QStringLiteral("urlJson"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/cori/high/en_GB-cori-high.onnx.json")},
            {QStringLiteral("desc"), QStringLiteral("British female — F.R.I.D.A.Y. style")}
        },
        QVariantMap{
            {QStringLiteral("id"), QStringLiteral("en_US-joe-medium")},
            {QStringLiteral("name"), QStringLiteral("Joe (American Male)")},
            {QStringLiteral("lang"), QStringLiteral("English (US)")},
            {QStringLiteral("url"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/joe/medium/en_US-joe-medium.onnx")},
            {QStringLiteral("urlJson"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/joe/medium/en_US-joe-medium.onnx.json")},
            {QStringLiteral("desc"), QStringLiteral("Warm American male voice")}
        },
        QVariantMap{
            {QStringLiteral("id"), QStringLiteral("en_US-amy-medium")},
            {QStringLiteral("name"), QStringLiteral("Amy (American Female)")},
            {QStringLiteral("lang"), QStringLiteral("English (US)")},
            {QStringLiteral("url"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx")},
            {QStringLiteral("urlJson"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json")},
            {QStringLiteral("desc"), QStringLiteral("Clear American female voice")}
        },
        QVariantMap{
            {QStringLiteral("id"), QStringLiteral("en_GB-semaine-medium")},
            {QStringLiteral("name"), QStringLiteral("Semaine (British Multi)")},
            {QStringLiteral("lang"), QStringLiteral("English (UK)")},
            {QStringLiteral("url"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/semaine/medium/en_GB-semaine-medium.onnx")},
            {QStringLiteral("urlJson"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/semaine/medium/en_GB-semaine-medium.onnx.json")},
            {QStringLiteral("desc"), QStringLiteral("Expressive British voice")}
        },
    };

    const QString voicesDir = jarvisDataDir() + QStringLiteral("/piper-voices");
    QDir().mkpath(voicesDir);
    for (auto &v : m_availableTtsVoices) {
        auto map = v.toMap();
        const QString filename = map[QStringLiteral("id")].toString() + QStringLiteral(".onnx");
        map[QStringLiteral("downloaded")] = QFile::exists(voicesDir + QStringLiteral("/") + filename);
        map[QStringLiteral("active")] = (map[QStringLiteral("id")].toString() == m_currentVoiceName);
        v = map;
    }
}

// ─────────────────────────────────────────────
// Fetch More
// ─────────────────────────────────────────────

void JarvisSettings::fetchMoreModels()
{
    // Disabled in OMEGA CORE (Modelle via OMEGA-Router)
}

void JarvisSettings::fetchMoreVoices()
{
    const QStringList existingIds = [this]() {
        QStringList ids;
        for (const auto &v : std::as_const(m_availableTtsVoices))
            ids << v.toMap()[QStringLiteral("id")].toString();
        return ids;
    }();

    const QVariantList extra = {
        QVariantMap{
            {QStringLiteral("id"), QStringLiteral("en_GB-northern_english_male-medium")},
            {QStringLiteral("name"), QStringLiteral("Northern English Male")},
            {QStringLiteral("lang"), QStringLiteral("English (UK)")},
            {QStringLiteral("url"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/northern_english_male/medium/en_GB-northern_english_male-medium.onnx")},
            {QStringLiteral("urlJson"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/northern_english_male/medium/en_GB-northern_english_male-medium.onnx.json")},
            {QStringLiteral("desc"), QStringLiteral("Northern English accent — warm tone")}
        },
        QVariantMap{
            {QStringLiteral("id"), QStringLiteral("en_US-lessac-medium")},
            {QStringLiteral("name"), QStringLiteral("Lessac (American)")},
            {QStringLiteral("lang"), QStringLiteral("English (US)")},
            {QStringLiteral("url"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx")},
            {QStringLiteral("urlJson"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json")},
            {QStringLiteral("desc"), QStringLiteral("Professional American voice")}
        },
        QVariantMap{
            {QStringLiteral("id"), QStringLiteral("en_US-libritts_r-medium")},
            {QStringLiteral("name"), QStringLiteral("LibriTTS (American Multi)")},
            {QStringLiteral("lang"), QStringLiteral("English (US)")},
            {QStringLiteral("url"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts_r/medium/en_US-libritts_r-medium.onnx")},
            {QStringLiteral("urlJson"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts_r/medium/en_US-libritts_r-medium.onnx.json")},
            {QStringLiteral("desc"), QStringLiteral("Multi-speaker American voice")}
        },
        QVariantMap{
            {QStringLiteral("id"), QStringLiteral("en_US-ryan-medium")},
            {QStringLiteral("name"), QStringLiteral("Ryan (American Male)")},
            {QStringLiteral("lang"), QStringLiteral("English (US)")},
            {QStringLiteral("url"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/medium/en_US-ryan-medium.onnx")},
            {QStringLiteral("urlJson"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/medium/en_US-ryan-medium.onnx.json")},
            {QStringLiteral("desc"), QStringLiteral("Confident American male")}
        },
        QVariantMap{
            {QStringLiteral("id"), QStringLiteral("en_GB-jenny_dioco-medium")},
            {QStringLiteral("name"), QStringLiteral("Jenny (British Female)")},
            {QStringLiteral("lang"), QStringLiteral("English (UK)")},
            {QStringLiteral("url"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/jenny_dioco/medium/en_GB-jenny_dioco-medium.onnx")},
            {QStringLiteral("urlJson"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/jenny_dioco/medium/en_GB-jenny_dioco-medium.onnx.json")},
            {QStringLiteral("desc"), QStringLiteral("Soft-spoken British female")}
        },
        QVariantMap{
            {QStringLiteral("id"), QStringLiteral("de_DE-thorsten-medium")},
            {QStringLiteral("name"), QStringLiteral("Thorsten (German Male)")},
            {QStringLiteral("lang"), QStringLiteral("Deutsch")},
            {QStringLiteral("url"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx")},
            {QStringLiteral("urlJson"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/de/de_DE/thorsten/medium/de_DE-thorsten-medium.onnx.json")},
            {QStringLiteral("desc"), QStringLiteral("German male voice")}
        },
        QVariantMap{
            {QStringLiteral("id"), QStringLiteral("fr_FR-siwis-medium")},
            {QStringLiteral("name"), QStringLiteral("Siwis (French)")},
            {QStringLiteral("lang"), QStringLiteral("Français")},
            {QStringLiteral("url"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx")},
            {QStringLiteral("urlJson"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/siwis/medium/fr_FR-siwis-medium.onnx.json")},
            {QStringLiteral("desc"), QStringLiteral("French voice")}
        },
        QVariantMap{
            {QStringLiteral("id"), QStringLiteral("es_ES-davefx-medium")},
            {QStringLiteral("name"), QStringLiteral("DaveFX (Spanish)")},
            {QStringLiteral("lang"), QStringLiteral("Español")},
            {QStringLiteral("url"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx")},
            {QStringLiteral("urlJson"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json")},
            {QStringLiteral("desc"), QStringLiteral("Spanish male voice")}
        },
        QVariantMap{
            {QStringLiteral("id"), QStringLiteral("pl_PL-gosia-medium")},
            {QStringLiteral("name"), QStringLiteral("Gosia (Polish Female)")},
            {QStringLiteral("lang"), QStringLiteral("Polski")},
            {QStringLiteral("url"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/gosia/medium/pl_PL-gosia-medium.onnx")},
            {QStringLiteral("urlJson"), QStringLiteral("https://huggingface.co/rhasspy/piper-voices/resolve/main/pl/pl_PL/gosia/medium/pl_PL-gosia-medium.onnx.json")},
            {QStringLiteral("desc"), QStringLiteral("Polish female voice")}
        },
    };

    const QString voicesDir = jarvisDataDir() + QStringLiteral("/piper-voices");
    for (const auto &v : extra) {
        auto map = v.toMap();
        if (existingIds.contains(map[QStringLiteral("id")].toString())) continue;
        const QString filename = map[QStringLiteral("id")].toString() + QStringLiteral(".onnx");
        map[QStringLiteral("downloaded")] = QFile::exists(voicesDir + QStringLiteral("/") + filename);
        map[QStringLiteral("active")] = false;
        m_availableTtsVoices.append(map);
    }
}

void JarvisSettings::downloadLlmModel(const QString &modelId)
{
    if (m_downloading) return;

    QVariantMap targetModel;
    for (const auto &v : std::as_const(m_availableLlmModels)) {
        auto map = v.toMap();
        if (map[QStringLiteral("id")].toString() == modelId) {
            targetModel = map;
            break;
        }
    }
    if (targetModel.isEmpty()) return;

    const QString url = targetModel[QStringLiteral("url")].toString();
    const QString modelsDir = jarvisDataDir() + QStringLiteral("/models");
    QDir().mkpath(modelsDir);
    const QString filePath = modelsDir + QStringLiteral("/") + modelId + QStringLiteral(".gguf");

    if (QFile::exists(filePath)) {
        setActiveLlmModel(modelId);
        return;
    }

    m_downloading = true;
    m_downloadProgress = 0.0;
    m_downloadStatus = QStringLiteral("Downloading ") + targetModel[QStringLiteral("name")].toString() + QStringLiteral("...");
    emit downloadingChanged();
    emit downloadProgressChanged();
    emit downloadStatusChanged();

    QNetworkRequest request{QUrl(url)};
    request.setAttribute(QNetworkRequest::RedirectPolicyAttribute, QNetworkRequest::NoLessSafeRedirectPolicy);
    m_downloadReply = m_networkManager->get(request);

    auto *outFile = new QFile(filePath + QStringLiteral(".part"), this);
    outFile->open(QIODevice::WriteOnly);

    connect(m_downloadReply, &QNetworkReply::readyRead, this, [this, outFile]() {
        if (outFile->isOpen()) outFile->write(m_downloadReply->readAll());
    });

    connect(m_downloadReply, &QNetworkReply::downloadProgress, this, [this](qint64 received, qint64 total) {
        if (total > 0) {
            m_downloadProgress = static_cast<double>(received) / total;
            m_downloadStatus = QStringLiteral("Downloading... %1 / %2 MB")
                .arg(received / 1048576).arg(total / 1048576);
            emit downloadProgressChanged();
            emit downloadStatusChanged();
        }
    });

    connect(m_downloadReply, &QNetworkReply::finished, this, [this, outFile, filePath, modelId]() {
        outFile->close();
        outFile->deleteLater();

        if (m_downloadReply->error() == QNetworkReply::NoError) {
            QFile::rename(filePath + QStringLiteral(".part"), filePath);
            m_downloadStatus = QStringLiteral("Download complete!");
            setActiveLlmModel(modelId);
            populateModelList();
        } else {
            QFile::remove(filePath + QStringLiteral(".part"));
            m_downloadStatus = QStringLiteral("Download failed: ") + m_downloadReply->errorString();
        }

        m_downloading = false;
        m_downloadReply = nullptr;
        emit downloadingChanged();
        emit downloadStatusChanged();
    });
}

void JarvisSettings::downloadTtsVoice(const QString &voiceId)
{
    if (m_downloading) return;

    QVariantMap targetVoice;
    for (const auto &v : std::as_const(m_availableTtsVoices)) {
        auto map = v.toMap();
        if (map[QStringLiteral("id")].toString() == voiceId) {
            targetVoice = map;
            break;
        }
    }
    if (targetVoice.isEmpty()) return;

    const QString voicesDir = jarvisDataDir() + QStringLiteral("/piper-voices");
    QDir().mkpath(voicesDir);
    const QString onnxPath = voicesDir + QStringLiteral("/") + voiceId + QStringLiteral(".onnx");
    const QString jsonPath = onnxPath + QStringLiteral(".json");

    if (QFile::exists(onnxPath) && QFile::exists(jsonPath)) {
        setActiveTtsVoice(voiceId);
        return;
    }

    m_downloading = true;
    m_downloadProgress = 0.0;
    m_downloadStatus = QStringLiteral("Downloading voice: ") + targetVoice[QStringLiteral("name")].toString() + QStringLiteral("...");
    emit downloadingChanged();
    emit downloadProgressChanged();
    emit downloadStatusChanged();

    QNetworkRequest request{QUrl(targetVoice[QStringLiteral("url")].toString())};
    request.setAttribute(QNetworkRequest::RedirectPolicyAttribute, QNetworkRequest::NoLessSafeRedirectPolicy);
    m_downloadReply = m_networkManager->get(request);

    auto *outFile = new QFile(onnxPath + QStringLiteral(".part"), this);
    outFile->open(QIODevice::WriteOnly);

    connect(m_downloadReply, &QNetworkReply::readyRead, this, [this, outFile]() {
        if (outFile->isOpen()) outFile->write(m_downloadReply->readAll());
    });

    connect(m_downloadReply, &QNetworkReply::downloadProgress, this, [this](qint64 received, qint64 total) {
        if (total > 0) {
            m_downloadProgress = static_cast<double>(received) / total;
            m_downloadStatus = QStringLiteral("Downloading voice... %1 / %2 MB")
                .arg(received / 1048576).arg(total / 1048576);
            emit downloadProgressChanged();
            emit downloadStatusChanged();
        }
    });

    connect(m_downloadReply, &QNetworkReply::finished, this, [this, outFile, onnxPath, jsonPath, targetVoice, voiceId]() {
        outFile->close();
        outFile->deleteLater();

        if (m_downloadReply->error() == QNetworkReply::NoError) {
            QFile::rename(onnxPath + QStringLiteral(".part"), onnxPath);

            QNetworkRequest jsonReq{QUrl(targetVoice[QStringLiteral("urlJson")].toString())};
            jsonReq.setAttribute(QNetworkRequest::RedirectPolicyAttribute, QNetworkRequest::NoLessSafeRedirectPolicy);
            auto *jsonReply = m_networkManager->get(jsonReq);
            connect(jsonReply, &QNetworkReply::finished, this, [this, jsonReply, jsonPath, voiceId]() {
                if (jsonReply->error() == QNetworkReply::NoError) {
                    QFile jf(jsonPath);
                    if (jf.open(QIODevice::WriteOnly)) {
                        jf.write(jsonReply->readAll());
                        jf.close();
                    }
                }
                jsonReply->deleteLater();
                m_downloadStatus = QStringLiteral("Voice downloaded!");
                setActiveTtsVoice(voiceId);
                populateVoiceList();
                m_downloading = false;
                m_downloadReply = nullptr;
                emit downloadingChanged();
                emit downloadStatusChanged();
            });
        } else {
            QFile::remove(onnxPath + QStringLiteral(".part"));
            m_downloadStatus = QStringLiteral("Download failed: ") + m_downloadReply->errorString();
            m_downloading = false;
            m_downloadReply = nullptr;
            emit downloadingChanged();
            emit downloadStatusChanged();
        }
    });
}

void JarvisSettings::setActiveLlmModel(const QString &modelId)
{
    m_currentModelName = modelId;
    saveSettings();
    populateModelList();
    emit currentModelNameChanged();
}

void JarvisSettings::setActiveTtsVoice(const QString &voiceId)
{
    const QString voicesDir = jarvisDataDir() + QStringLiteral("/piper-voices");
    const QString onnxPath = voicesDir + QStringLiteral("/") + voiceId + QStringLiteral(".onnx");

    if (QFile::exists(onnxPath)) {
        m_piperModelPath = onnxPath;
        m_currentVoiceName = voiceId;
        saveSettings();
        populateVoiceList();
        emit currentVoiceNameChanged();
        emit voiceActivated(voiceId, onnxPath);
    }
}

void JarvisSettings::cancelDownload()
{
    if (m_downloadReply) {
        m_downloadReply->abort();
        m_downloadReply = nullptr;
    }
    m_downloading = false;
    m_downloadProgress = 0.0;
    m_downloadStatus = QStringLiteral("Download cancelled.");
    emit downloadingChanged();
    emit downloadProgressChanged();
    emit downloadStatusChanged();
}
