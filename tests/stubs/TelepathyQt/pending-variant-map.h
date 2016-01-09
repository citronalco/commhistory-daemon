#ifndef _TelepathyQt_pending_variant_map_h_HEADER_GUARD_
#define _TelepathyQt_pending_variant_map_h_HEADER_GUARD_

#include <TelepathyQt/PendingOperation>

#include <QDBusPendingCallWatcher>

namespace Tp
{

class PendingVariantMap : public PendingOperation
{
    Q_OBJECT

public:
    PendingVariantMap();

    QVariantMap result() const;

private:

};

} // Tp

#endif
