/******************************************************************************
**
** This file is part of commhistory-daemon.
**
** Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
** Contact: Reto Zingg <reto.zingg@nokia.com>
**
** This library is free software; you can redistribute it and/or modify it
** under the terms of the GNU Lesser General Public License version 2.1 as
** published by the Free Software Foundation.
**
** This library is distributed in the hope that it will be useful, but
** WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
** or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
** License for more details.
**
** You should have received a copy of the GNU Lesser General Public License
** along with this library; if not, write to the Free Software Foundation, Inc.,
** 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
**
******************************************************************************/

#include <signal.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <unistd.h>

#include <QLocale>

// Our includes
#include <TelepathyQt/Debug>
#include "logger.h"
#include "notificationmanager.h"
#include "commhistoryservice.h"
#include "commhistoryifadaptor.h"
#include "accountpresenceservice.h"
#include "accountpresenceifadaptor.h"
#include "messagereviver.h"
#include "contactauthorizationlistener.h"
#include "connectionutils.h"
#include "lastdialedcache.h"
#include "accountoperationsobserver.h"
#include "fscleanup.h"
#include "mmshandler.h"
#include "mmshandler_adaptor.h"
#include "smartmessaging.h"
#include "debug.h"

Q_LOGGING_CATEGORY(lcCommhistoryd, "commhistoryd", QtWarningMsg)

using namespace RTComLogger;

namespace {
bool toggleDebug = false;

QLoggingCategory::CategoryFilter defaultCategoryFilter;

void categoryFilter(QLoggingCategory *category)
{
    defaultCategoryFilter(category);

    if (QString(category->categoryName()).startsWith("commhistoryd") && toggleDebug) {
        category->setEnabled(QtDebugMsg, true);
        category->setEnabled(QtInfoMsg, true);
    }
}

// handle SIGTERM to cleanup on exit
int sigtermFd[2];

void termSignalHandler(int)
{
    char a = 1;
    if (write(sigtermFd[0], &a, sizeof(a)) < 1) {
        qWarning("Failed to handle term signal.");
    }
}

void setupSigtermHandler()
{
    struct sigaction term;

    term.sa_handler = termSignalHandler;
    sigemptyset(&term.sa_mask);
    term.sa_flags = SA_RESTART;

    if (::sigaction(SIGTERM, &term, 0))
        qFatal("Failed setup SIGTERM signal handler");
}

}

Q_DECL_EXPORT int main(int argc, char **argv)
{
    if (argc > 1) {
        if (strcmp(argv[1], "-d") == 0) {
            toggleDebug = true;
        }
    }

    defaultCategoryFilter = QLoggingCategory::installFilter(categoryFilter);

    QCoreApplication app(argc, argv);
    qCDebug(lcCommhistoryd) << "Commhistoryd application created";

    if (::socketpair(AF_UNIX, SOCK_STREAM, 0, sigtermFd))
        qFatal("Couldn't create TERM socketpair");

    QSocketNotifier *snTerm = new QSocketNotifier(sigtermFd[1], QSocketNotifier::Read, &app);
    QObject::connect(snTerm, SIGNAL(activated(int)), &app, SLOT(quit()));
    setupSigtermHandler();

    QScopedPointer<QTranslator> engineeringEnglish(new QTranslator);
    engineeringEnglish->load("commhistoryd_eng_en", "/usr/share/translations");
    QScopedPointer<QTranslator> translator(new QTranslator);
    translator->load(QLocale(), "commhistoryd", "-", "/usr/share/translations");

    app.installTranslator(engineeringEnglish.data());
    app.installTranslator(translator.data());

    CommHistoryService *chService = CommHistoryService::instance();
    if (!chService->isRegistered()) {
        qCritical() << "CommHistoryService registration failed (already running or DBus not found), exiting";
        _exit(1);
    }
    new CommHistoryIfAdaptor(chService);
    qCDebug(lcCommhistoryd) << "CommHistoryService created";

    ConnectionUtils *utils = new ConnectionUtils(&app);

    // ContactAuthorizationListener needs to be updated with nemo-notifications and new UI handling
    //new ContactAuthorizationListener(utils, chService);

    AccountPresenceService *apService = new AccountPresenceService(utils->accountManager(), &app);
    if (!apService->isRegistered()) {
        qCritical() << "AccountPresenceService registration failed (already running or DBus not found), exiting";
        _exit(1);
    }
    new AccountPresenceIfAdaptor(apService);
    qCDebug(lcCommhistoryd) << "AccountPresenceService created";

    MessageReviver *reviver = new MessageReviver(utils, &app);
    qCDebug(lcCommhistoryd) << "Message reviver created, starting main loop";

    if (toggleDebug) {
        Tp::enableDebug(true);
        Tp::enableWarnings(true);
    }
    new Logger(utils->accountManager(),
               reviver,
               &app);
    qCDebug(lcCommhistoryd) << "Logger created";

    NotificationManager::instance();
    qCDebug(lcCommhistoryd) << "NotificationManager created";

    new LastDialedCache(&app);
    qCDebug(lcCommhistoryd) << "LastDialedCache created";

    // Init account operations observer to monitor account removals and to react to them.
    new AccountOperationsObserver(utils->accountManager(), &app);

    new MmsHandlerAdaptor(new MmsHandler(&app));
    new SmartMessaging(&app);
    new FsCleanup(&app);

    int result = app.exec();

    close(sigtermFd[0]);
    close(sigtermFd[1]);

    qCDebug(lcCommhistoryd) << "exit";

    return result;
}
