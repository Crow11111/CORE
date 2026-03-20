#pragma once

#include <QObject>
#include <QString>
#include <QProcess>
#include <QTextToSpeech>
#include <atomic>
#include <QMediaPlayer>
#include <QAudioOutput>
#include <QNetworkAccessManager>

class JarvisSettings;

class JarvisTts : public QObject
{
    Q_OBJECT

public:
    explicit JarvisTts(JarvisSettings *settings, QObject *parent = nullptr);

    [[nodiscard]] bool isSpeaking() const { return m_speaking.load(); }
    [[nodiscard]] bool isMuted() const;

    void speak(const QString &text);
    void stop();
    void toggleMute();

    // Called when settings change
    void onTtsRateChanged();
    void onTtsPitchChanged();
    void onTtsVolumeChanged();
    void onVoiceActivated(const QString &voiceId, const QString &onnxPath);

signals:
    void speakingChanged();

private:
    JarvisSettings *m_settings{nullptr};
    
    QNetworkAccessManager *m_networkManager{nullptr};
    QMediaPlayer *m_player{nullptr};
    QAudioOutput *m_audioOutput{nullptr};
    
    std::atomic<bool> m_speaking{false};
};
