#include "jarvisTts.h"
#include "../settings/jarvissettings.h"
#include <QDebug>
#include <QDir>
#include <QDateTime>
#include <QRegularExpression>
#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QJsonDocument>
#include <QJsonObject>
#include <QTimer>

JarvisTts::JarvisTts(JarvisSettings *settings, QObject *parent)
    : QObject(parent), m_settings(settings)
{
    m_networkManager = new QNetworkAccessManager(this);
    m_player = new QMediaPlayer(this);
    m_audioOutput = new QAudioOutput(this);
    m_player->setAudioOutput(m_audioOutput);

    connect(m_player, &QMediaPlayer::playbackStateChanged, this, [this](QMediaPlayer::PlaybackState state) {
        if (state == QMediaPlayer::StoppedState) {
            m_speaking = false;
            emit speakingChanged();
        }
    });

    onTtsVolumeChanged();
}

bool JarvisTts::isMuted() const
{
    return m_settings->ttsMuted();
}

void JarvisTts::toggleMute()
{
    m_settings->setTtsMuted(!m_settings->ttsMuted());
}

void JarvisTts::speak(const QString &text)
{
    if (m_settings->ttsMuted()) return;

    QString cleanText = text;
    cleanText.remove(QRegularExpression(QStringLiteral("[*_`#]")));

    // OMEGA API CALL FOR TTS
    QNetworkRequest request(QUrl(m_settings->llmServerUrl() + QStringLiteral("/v1/audio/speech")));
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    request.setTransferTimeout(180000);

    QJsonObject json;
    json["input"] = cleanText;
    json["voice"] = m_settings->currentVoiceName();

    m_speaking = true;
    emit speakingChanged();

    QNetworkReply *reply = m_networkManager->post(request, QJsonDocument(json).toJson());
    connect(reply, &QNetworkReply::finished, this, [this, reply]() {
        if (reply->error() == QNetworkReply::NoError) {
            QByteArray audioData = reply->readAll();
            QString tempFile = QDir::tempPath() + QStringLiteral("/jarvis_tts_omega_%1.mp3").arg(QDateTime::currentMSecsSinceEpoch());

            QFile file(tempFile);
            if (file.open(QIODevice::WriteOnly)) {
                file.write(audioData);
                file.close();

                m_player->setSource(QUrl::fromLocalFile(tempFile));
                m_player->play();
            } else {
                m_speaking = false;
                emit speakingChanged();
            }
        } else {
            qWarning() << "[JARVIS] TTS API Error:" << reply->errorString();
            m_speaking = false;
            emit speakingChanged();
        }
        reply->deleteLater();
    });
}

void JarvisTts::stop()
{
    if (m_player->playbackState() == QMediaPlayer::PlayingState) {
        m_player->stop();
    }
    m_speaking = false;
    emit speakingChanged();
}

void JarvisTts::onTtsRateChanged()
{
    // OMEGA API decides rate natively or via config, handled backend-side
}

void JarvisTts::onTtsPitchChanged()
{
    // OMEGA API decides pitch natively
}

void JarvisTts::onTtsVolumeChanged()
{
    m_audioOutput->setVolume(m_settings->ttsVolume() / 100.0);
}

void JarvisTts::onVoiceActivated(const QString &voiceId, const QString &onnxPath)
{
    // Just save the ID to use in the API call
}
