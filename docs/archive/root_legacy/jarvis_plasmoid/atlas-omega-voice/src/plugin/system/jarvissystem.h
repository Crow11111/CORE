#pragma once

#include <QObject>
#include <QString>
#include <QTimer>
#include <QVariantList>

class JarvisSystem : public QObject
{
    Q_OBJECT
    Q_PROPERTY(double cpuUsage READ cpuUsage NOTIFY systemStatsChanged)
    Q_PROPERTY(double memoryUsage READ memoryUsage NOTIFY systemStatsChanged)
    Q_PROPERTY(double memoryTotalGb READ memoryTotalGb NOTIFY systemStatsChanged)
    Q_PROPERTY(double memoryUsedGb READ memoryUsedGb NOTIFY systemStatsChanged)
    Q_PROPERTY(int cpuTemp READ cpuTemp NOTIFY systemStatsChanged)
    Q_PROPERTY(QString uptime READ uptime NOTIFY systemStatsChanged)
    Q_PROPERTY(QString hostname READ hostname NOTIFY systemStatsChanged)
    Q_PROPERTY(QString kernelVersion READ kernelVersion NOTIFY systemStatsChanged)
    Q_PROPERTY(QVariantList daemonStatus READ daemonStatus NOTIFY systemStatsChanged)
    Q_PROPERTY(QString currentTime READ currentTime NOTIFY currentTimeChanged)
    Q_PROPERTY(QString currentDate READ currentDate NOTIFY currentTimeChanged)
    Q_PROPERTY(QString greeting READ greeting NOTIFY currentTimeChanged)

public:
    explicit JarvisSystem(QObject *parent = nullptr);

    // System control
    Q_INVOKABLE void controlDaemon(const QString &name, const QString &action);

    // System monitoring getters
    [[nodiscard]] double cpuUsage() const { return m_cpuUsage; }
    [[nodiscard]] double memoryUsage() const { return m_memoryUsage; }
    [[nodiscard]] double memoryTotalGb() const { return m_memoryTotalGb; }
    [[nodiscard]] double memoryUsedGb() const { return m_memoryUsedGb; }
    [[nodiscard]] int cpuTemp() const { return m_cpuTemp; }
    [[nodiscard]] QString uptime() const { return m_uptime; }
    [[nodiscard]] QString hostname() const { return m_hostname; }
    [[nodiscard]] QString kernelVersion() const { return m_kernelVersion; }
    [[nodiscard]] QVariantList daemonStatus() const { return m_daemonStatus; }

    // Date/Time
    [[nodiscard]] QString currentTime() const { return m_currentTime; }
    [[nodiscard]] QString currentDate() const { return m_currentDate; }
    [[nodiscard]] QString greeting() const;

signals:
    void systemStatsChanged();
    void currentTimeChanged();

private slots:
    void updateSystemStats();
    void updateClock();

private:
    void initSystemMonitor();
    void readCpuUsage();
    void readMemoryUsage();
    void readCpuTemp();
    void readUptime();

    QTimer *m_systemStatsTimer{nullptr};
    QTimer *m_clockTimer{nullptr};

    double m_cpuUsage{0.0};
    double m_memoryUsage{0.0};
    double m_memoryTotalGb{0.0};
    double m_memoryUsedGb{0.0};
    int m_cpuTemp{0};
    QString m_uptime;
    QString m_hostname;
    QString m_kernelVersion;
    QVariantList m_daemonStatus;
    long long m_prevCpuTotal{0};
    long long m_prevCpuIdle{0};

    QString m_currentTime;
    QString m_currentDate;
};
