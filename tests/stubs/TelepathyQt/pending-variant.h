#ifndef _TelepathyQt_pending_variant_h_HEADER_GUARD_
#define _TelepathyQt_pending_variant_h_HEADER_GUARD_

#include <TelepathyQt/PendingOperation>
#include <QDBusPendingCallWatcher>

namespace Tp
{

    class PendingVariant : public PendingOperation
    {
        Q_OBJECT

    public:
        PendingVariant();

        QVariant result() const;

    private:

    };

} // Tp

#endif
