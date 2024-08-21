/******************************************************************************
**
** This file is part of commhistory-daemon.
**
** Copyright (C) 2015 Jolla Ltd.
** Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
** Contact: Reto Zingg <reto.zingg@jolla.com>
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

#ifndef CONSTANTS_H
#define CONSTANTS_H

// Used to generate remoteaction strings
#define OBJECT_PATH QLatin1String("/")

#define COMM_HISTORY_DAEMON_SERVICE_NAME QLatin1String("org.nemomobile.CommHistory")
#define COMM_HISTORY_DAEMON_OBJECT_PATH  QLatin1String("/org/nemomobile/CommHistory")
#define COMM_HISTORY_DAEMON_INTERFACE    QLatin1String("org.nemomobile.CommHistoryIf")

#define ACCOUNT_PRESENCE_SERVICE_NAME    QLatin1String("org.nemomobile.AccountPresence")
#define ACCOUNT_PRESENCE_OBJECT_PATH     QLatin1String("/org/nemomobile/AccountPresence")
#define ACCOUNT_PRESENCE_INTERFACE       QLatin1String("org.nemomobile.AccountPresenceIf")

#define MESSAGING_SERVICE_NAME    QLatin1String("org.sailfishos.Messages")
#define MESSAGING_INTERFACE       QLatin1String("org.sailfishos.Messages")
#define SHOW_INBOX_METHOD         QLatin1String("showGroupsWindow")
#define START_CONVERSATION_METHOD QLatin1String("startConversation")
#define SEND_MESSAGE_METHOD       QLatin1String("sendMessage")

#define CALL_HISTORY_SERVICE_NAME QLatin1String("com.nokia.telephony.callhistory")
#define CALL_HISTORY_OBJECT_PATH  QLatin1String("/org/maemo/m")
#define CALL_HISTORY_INTERFACE    QLatin1String("com.nokia.MApplicationIf")
#define CALL_HISTORY_METHOD       QLatin1String("launch")
#define CALL_HISTORY_PARAMETER    QLatin1String("callHistory")

#define VOICEMAIL_INTERFACE    QLatin1String("com.nokia.telephony.callhistory")
#define VOICEMAIL_OBJECT_PATH  QLatin1String("/callhistory")
#define VOICEMAIL_METHOD       QLatin1String("voicemail")
#define REPLACE_TYPE           QLatin1String("sms-replace-number")

#define VOICECALL_SERVICE      QLatin1String("com.jolla.voicecall.ui")
#define VOICECALL_OBJECT_PATH  QLatin1String("/")
#define VOICECALL_INTERFACE    QLatin1String("com.jolla.voicecall.ui")
#define VOICECALL_DIAL_METHOD  QLatin1String("dial")

// Custom hints for identifying notifications
#define ACCOUNT_PATH_HINT   QLatin1String("x-org-nemomobile-qmlmessages.account.path")
#define CONTACT_ID_HINT     QLatin1String("x-org-nemomobile-qmlmessages.contact.id")

#define RING_ACCOUNT_PATH_PREFIX QLatin1String("/org/freedesktop/Telepathy/Account/ring/tel")

// This event type is used only locally (in NotificationManager) and is not defined in CommHistory::Event::EvenType enum.
#define VOICEMAIL_SMS_EVENT_TYPE 100

#endif //#define CONSTANTS_H
