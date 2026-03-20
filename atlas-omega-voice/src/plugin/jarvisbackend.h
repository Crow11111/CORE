#pragma once

#include <QObject>
#include <QQmlEngine>
#include <QString>
#include <QStringList>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QTimer>
#include <QJsonArray>
#include <QVariantList>
#include <QVariantMap>
#include <QDateTime>
#include <vector>
#include <atomic>

class JarvisSettings;
class JarvisTts;
class JarvisAudio;
class JarvisSystem;
class JarvisCommands;

class JarvisBackend : public QObject
{
    Q_OBJECT
    QML_ELEMENT
    QML_SINGLETON

    // Core properties
    Q_PROPERTY(QString lastResponse READ lastResponse NOTIFY lastResponseChanged)
    Q_PROPERTY(bool listening READ isListening NOTIFY listeningChanged)
    Q_PROPERTY(bool processing READ isProcessing NOTIFY processingChanged)
    Q_PROPERTY(bool wakeWordActive READ isWakeWordActive NOTIFY wakeWordActiveChanged)
    Q_PROPERTY(bool connected READ isConnected NOTIFY connectedChanged)
    Q_PROPERTY(QString statusText READ statusText NOTIFY statusTextChanged)
    Q_PROPERTY(QStringList chatHistory READ chatHistory NOTIFY chatHistoryChanged)
    Q_PROPERTY(double audioLevel READ audioLevel NOTIFY audioLevelChanged)
    Q_PROPERTY(bool speaking READ isSpeaking NOTIFY speakingChanged)
    Q_PROPERTY(bool ttsMuted READ isTtsMuted NOTIFY ttsMutedChanged)

    // Voice command mode
    Q_PROPERTY(bool voiceCommandMode READ isVoiceCommandMode NOTIFY voiceCommandModeChanged)
    Q_PROPERTY(QString lastTranscription READ lastTranscription NOTIFY lastTranscriptionChanged)

    // System monitoring
    Q_PROPERTY(double cpuUsage READ cpuUsage NOTIFY systemStatsChanged)
    Q_PROPERTY(double memoryUsage READ memoryUsage NOTIFY systemStatsChanged)
    Q_PROPERTY(double memoryTotalGb READ memoryTotalGb NOTIFY systemStatsChanged)
    Q_PROPERTY(double memoryUsedGb READ memoryUsedGb NOTIFY systemStatsChanged)
    Q_PROPERTY(int cpuTemp READ cpuTemp NOTIFY systemStatsChanged)
    Q_PROPERTY(QString uptime READ uptime NOTIFY systemStatsChanged)
    Q_PROPERTY(QString hostname READ hostname CONSTANT)
    Q_PROPERTY(QString kernelVersion READ kernelVersion CONSTANT)

    // Date/Time
    Q_PROPERTY(QString currentTime READ currentTime NOTIFY currentTimeChanged)
    Q_PROPERTY(QString currentDate READ currentDate NOTIFY currentTimeChanged)
    Q_PROPERTY(QString greeting READ greeting NOTIFY currentTimeChanged)

    // Reminders/Timers
    Q_PROPERTY(QVariantList activeReminders READ activeReminders NOTIFY remindersChanged)

    // Settings properties (delegated to JarvisSettings, exposed for config QML)
    Q_PROPERTY(QString llmServerUrl READ llmServerUrl NOTIFY llmServerUrlChanged)
    Q_PROPERTY(QString currentModelName READ currentModelName NOTIFY currentModelNameChanged)
    Q_PROPERTY(QString currentVoiceName READ currentVoiceName NOTIFY currentVoiceNameChanged)
    Q_PROPERTY(QVariantList availableLlmModels READ availableLlmModels NOTIFY availableLlmModelsChanged)
    Q_PROPERTY(QVariantList availableTtsVoices READ availableTtsVoices NOTIFY availableTtsVoicesChanged)
    Q_PROPERTY(double downloadProgress READ downloadProgress NOTIFY downloadProgressChanged)
    Q_PROPERTY(bool downloading READ isDownloading NOTIFY downloadingChanged)
    Q_PROPERTY(QString downloadStatus READ downloadStatus NOTIFY downloadStatusChanged)
    Q_PROPERTY(int maxHistoryPairs READ maxHistoryPairs NOTIFY maxHistoryPairsChanged)
    Q_PROPERTY(int wakeBufferSeconds READ wakeBufferSeconds NOTIFY wakeBufferSecondsChanged)
    Q_PROPERTY(int voiceCmdMaxSeconds READ voiceCmdMaxSeconds NOTIFY voiceCmdMaxSecondsChanged)
    Q_PROPERTY(bool autoStartWakeWord READ autoStartWakeWord NOTIFY autoStartWakeWordChanged)
    Q_PROPERTY(QString personalityPrompt READ personalityPrompt NOTIFY personalityPromptChanged)

    // Commands
    Q_PROPERTY(QVariantList commandMappings READ commandMappings NOTIFY commandMappingsChanged)

public:
    explicit JarvisBackend(QObject *parent = nullptr);
    ~JarvisBackend() override;

    // Core getters
    [[nodiscard]] QString lastResponse() const { return m_lastResponse; }
    [[nodiscard]] bool isListening() const;
    [[nodiscard]] bool isProcessing() const { return m_processing; }
    [[nodiscard]] bool isWakeWordActive() const;
    [[nodiscard]] bool isConnected() const { return m_connected; }
    [[nodiscard]] QString statusText() const { return m_statusText; }
    [[nodiscard]] QStringList chatHistory() const { return m_chatHistory; }
    [[nodiscard]] double audioLevel() const;
    [[nodiscard]] bool isSpeaking() const;
    [[nodiscard]] bool isTtsMuted() const;

    // Voice command
    [[nodiscard]] bool isVoiceCommandMode() const;
    [[nodiscard]] QString lastTranscription() const;

    // System monitoring (delegated)
    [[nodiscard]] double cpuUsage() const;
    [[nodiscard]] double memoryUsage() const;
    [[nodiscard]] double memoryTotalGb() const;
    [[nodiscard]] double memoryUsedGb() const;
    [[nodiscard]] int cpuTemp() const;
    [[nodiscard]] QString uptime() const;
    [[nodiscard]] QString hostname() const;
    [[nodiscard]] QString kernelVersion() const;

    // Date/Time (delegated)
    [[nodiscard]] QString currentTime() const;
    [[nodiscard]] QString currentDate() const;
    [[nodiscard]] QString greeting() const;

    // Reminders
    [[nodiscard]] QVariantList activeReminders() const { return m_activeReminders; }

    // Settings (delegated)
    [[nodiscard]] QString llmServerUrl() const;
    [[nodiscard]] QString currentModelName() const;
    [[nodiscard]] QString currentVoiceName() const;
    [[nodiscard]] QVariantList availableLlmModels() const;
    [[nodiscard]] QVariantList availableTtsVoices() const;
    [[nodiscard]] double downloadProgress() const;
    [[nodiscard]] bool isDownloading() const;
    [[nodiscard]] QString downloadStatus() const;
    [[nodiscard]] int maxHistoryPairs() const;
    [[nodiscard]] int wakeBufferSeconds() const;
    [[nodiscard]] int voiceCmdMaxSeconds() const;
    [[nodiscard]] bool autoStartWakeWord() const;
    [[nodiscard]] QString personalityPrompt() const;

    // Commands (delegated)
    [[nodiscard]] QVariantList commandMappings() const;

    // Core invokables
    Q_INVOKABLE void sendMessage(const QString &message);
    Q_INVOKABLE void toggleWakeWord();
    Q_INVOKABLE void speak(const QString &text);
    Q_INVOKABLE void stopSpeaking();
    Q_INVOKABLE void clearHistory();
    Q_INVOKABLE void checkConnection();

    // Voice command
    Q_INVOKABLE void startVoiceCommand();
    Q_INVOKABLE void stopVoiceCommand();

    // Reminders
    Q_INVOKABLE void addReminder(const QString &text, int secondsFromNow);
    Q_INVOKABLE void removeReminder(int index);

    // TTS control
    Q_INVOKABLE void setTtsRate(double rate);
    Q_INVOKABLE void setTtsPitch(double pitch);
    Q_INVOKABLE void setTtsVolume(double volume);
    Q_INVOKABLE void toggleTtsMute();

    // Settings invokables
    Q_INVOKABLE void setLlmServerUrl(const QString &url);
    Q_INVOKABLE void downloadLlmModel(const QString &modelId);
    Q_INVOKABLE void downloadTtsVoice(const QString &voiceId);
    Q_INVOKABLE void setActiveLlmModel(const QString &modelId);
    Q_INVOKABLE void setActiveTtsVoice(const QString &voiceId);
    Q_INVOKABLE void setMaxHistoryPairs(int pairs);
    Q_INVOKABLE void setWakeBufferSeconds(int seconds);
    Q_INVOKABLE void setVoiceCmdMaxSeconds(int seconds);
    Q_INVOKABLE void setAutoStartWakeWord(bool enabled);
    Q_INVOKABLE void setPersonalityPrompt(const QString &prompt);
    Q_INVOKABLE void cancelDownload();
    Q_INVOKABLE void openUrl(const QString &url);
    Q_INVOKABLE void testVoice(const QString &voiceId);
    Q_INVOKABLE void fetchMoreModels();
    Q_INVOKABLE void fetchMoreVoices();

    // Commands invokables
    Q_INVOKABLE void addCommand(const QString &phrase, const QString &action, const QString &type);
    Q_INVOKABLE void removeCommand(int index);
    Q_INVOKABLE void updateCommand(int index, const QString &phrase, const QString &action, const QString &type);
    Q_INVOKABLE void resetCommandsToDefaults();

signals:
    void lastResponseChanged();
    void listeningChanged();
    void processingChanged();
    void wakeWordActiveChanged();
    void connectedChanged();
    void statusTextChanged();
    void chatHistoryChanged();
    void audioLevelChanged();
    void speakingChanged();
    void wakeWordDetected();
    void responseReceived(const QString &response);
    void errorOccurred(const QString &error);
    void voiceCommandModeChanged();
    void lastTranscriptionChanged();
    void systemStatsChanged();
    void currentTimeChanged();
    void remindersChanged();
    void reminderTriggered(const QString &text);
    void ttsMutedChanged();
    void llmServerUrlChanged();
    void currentModelNameChanged();
    void currentVoiceNameChanged();
    void downloadProgressChanged();
    void downloadingChanged();
    void downloadStatusChanged();
    void maxHistoryPairsChanged();
    void wakeBufferSecondsChanged();
    void voiceCmdMaxSecondsChanged();
    void autoStartWakeWordChanged();
    void personalityPromptChanged();
    void commandMappingsChanged();
    void availableLlmModelsChanged();
    void availableTtsVoicesChanged();

private slots:
    void onLlmReplyFinished(QNetworkReply *reply);
    void onHealthCheckFinished(QNetworkReply *reply);
    void checkReminders();
    void onVoiceCommandTranscribed(const QString &text);

private:
    void sendToLlm(const QString &userMessage);
    void setStatus(const QString &status);
    void addToChatHistory(const QString &role, const QString &message);
    QJsonArray buildConversationContext() const;
    void connectModuleSignals();

    // Action parsing and execution
    void parseAndExecuteActions(const QString &responseText);
    void executeRunCommand(const QString &command);
    void executeOpenTerminal(const QString &command);
    void executeWriteFile(const QString &path, const QString &content);
    void executeOpenApp(const QString &app);
    void executeTypeText(const QString &text);
    QString stripActionsFromResponse(const QString &responseText) const;
    QString expandPath(const QString &path) const;

    // Module instances (owned)
    JarvisSettings *m_settings{nullptr};
    JarvisTts *m_tts{nullptr};
    JarvisAudio *m_audio{nullptr};
    JarvisSystem *m_system{nullptr};
    JarvisCommands *m_commands{nullptr};

    // Network
    QNetworkAccessManager *m_networkManager{nullptr};
    QTimer *m_healthCheckTimer{nullptr};
    QTimer *m_reminderTimer{nullptr};

    // Core state
    QString m_lastResponse;
    QString m_statusText;
    QStringList m_chatHistory;
    std::atomic<bool> m_processing{false};
    std::atomic<bool> m_connected{false};

    // Conversation
    struct ChatMessage {
        QString role;
        QString content;
    };
    std::vector<ChatMessage> m_conversationHistory;

    // Reminders
    struct Reminder {
        QString text;
        QDateTime triggerTime;
    };
    std::vector<Reminder> m_reminders;
    QVariantList m_activeReminders;
};
