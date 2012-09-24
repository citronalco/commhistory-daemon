#!/usr/bin/python
#
# Copyright (C) 2008 Collabora Limited <http://www.collabora.co.uk>
# Copyright (C) 2008 Nokia Corporation
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from sys import argv
import xml.dom.minidom
import codecs
from getopt import gnu_getopt

from libtpcodegen import NS_TP, get_descendant_text, get_by_path
from libqt4codegen import binding_from_usage, extract_arg_or_member_info, format_docstring, gather_externals, gather_custom_lists, get_headerfile_cmd, get_qt4_name, qt4_identifier_escape

class Generator(object):
    def __init__(self, opts):
        try:
            self.group = opts.get('--group', '')
            self.headerfile = opts['--headerfile']
            self.implfile = opts['--implfile']
            self.namespace = opts['--namespace']
            self.typesnamespace = opts['--typesnamespace']
            self.realinclude = opts['--realinclude']
            self.prettyinclude = opts.get('--prettyinclude')
            self.extraincludes = opts.get('--extraincludes', None)
            self.mainiface = opts.get('--mainiface', None)
            self.must_define = opts.get('--must-define', None)
            self.dbus_proxy = opts.get('--dbus-proxy',
                    'Tp::DBusProxy')
            self.visibility = opts.get('--visibility', '')
            ifacedom = xml.dom.minidom.parse(opts['--ifacexml'])
            specdom = xml.dom.minidom.parse(opts['--specxml'])
        except KeyError, k:
            assert False, 'Missing required parameter %s' % k.args[0]

        self.hs = []
        self.bs = []
        self.ifacenodes = ifacedom.getElementsByTagName('node')
        self.spec, = get_by_path(specdom, "spec")
        self.custom_lists = gather_custom_lists(self.spec, self.typesnamespace)
        self.externals = gather_externals(self.spec)

    def __call__(self):
        # Output info header and includes
        self.h("""\
/*
 * This file contains D-Bus client proxy classes generated by qt4-client-gen.py.
 *
 * This file can be distributed under the same terms as the specification from
 * which it was generated.
 */
""")

        if self.must_define:
            self.h('\n')
            self.h('#ifndef %s\n' % self.must_define)
            self.h('#error %s\n' % self.must_define)
            self.h('#endif\n')

        self.h('\n')

        if self.extraincludes:
            for include in self.extraincludes.split(','):
                self.h('#include %s\n' % include)

        self.h("""
#include <QtGlobal>

#include <QString>
#include <QObject>
#include <QVariant>

#include <QDBusPendingReply>

#include <TelepathyQt/AbstractInterface>
#include <TelepathyQt/DBusProxy>
#include <TelepathyQt/Global>

namespace Tp
{
class PendingVariant;
class PendingOperation;
}

""")

        if self.must_define:
            self.b("""#define %s\n""" % (self.must_define))

        self.b("""#include "%s"

""" % self.realinclude)

        # Begin namespace
        for ns in self.namespace.split('::'):
            self.hb("""\
namespace %s
{
""" % ns)

        # Output interface proxies
        def ifacenodecmp(x, y):
            xname, yname = [self.namespace + '::' + node.getAttribute('name').replace('/', '').replace('_', '') + 'Interface' for node in x, y]

            if xname == self.mainiface:
                return -1
            elif yname == self.mainiface:
                return 1
            else:
                return cmp(xname, yname)

        self.ifacenodes.sort(cmp=ifacenodecmp)
        for ifacenode in self.ifacenodes:
            self.do_ifacenode(ifacenode)

        # End namespace
        self.hb(''.join(['}\n' for ns in self.namespace.split('::')]))

        # Add metatype declaration - otherwise QTBUG #2151 might be triggered
        for ifacenode in self.ifacenodes:
            classname = ifacenode.getAttribute('name').replace('/', '').replace('_', '') + 'Interface'
            self.h("Q_DECLARE_METATYPE(" + self.namespace + "::" + classname + "*)\n")

        # Write output to files
        (codecs.getwriter('utf-8')(open(self.headerfile, 'w'))).write(''.join(self.hs))
        (codecs.getwriter('utf-8')(open(self.implfile, 'w'))).write(''.join(self.bs))

    def do_ifacenode(self, ifacenode):
        # Extract info
        name = ifacenode.getAttribute('name').replace('/', '').replace('_', '') + 'Interface'
        iface, = get_by_path(ifacenode, 'interface')
        dbusname = iface.getAttribute('name')

        # Begin class, constructors
        self.h("""
/**
 * \\class %(name)s
%(headercmd)s\
%(groupcmd)s\
 *
 * Proxy class providing a 1:1 mapping of the D-Bus interface "%(dbusname)s."
 */
class %(visibility)s %(name)s : public Tp::AbstractInterface
{
    Q_OBJECT

public:
    /**
     * Returns the name of the interface "%(dbusname)s", which this class
     * represents.
     *
     * \\return The D-Bus interface name.
     */
    static inline QLatin1String staticInterfaceName()
    {
        return QLatin1String("%(dbusname)s");
    }

    /**
     * Creates a %(name)s associated with the given object on the session bus.
     *
     * \\param busName Name of the service the object is on.
     * \\param objectPath Path to the object on the service.
     * \\param parent Passed to the parent class constructor.
     */
    %(name)s(
        const QString& busName,
        const QString& objectPath,
        QObject* parent = 0
    );

    /**
     * Creates a %(name)s associated with the given object on the given bus.
     *
     * \\param connection The bus via which the object can be reached.
     * \\param busName Name of the service the object is on.
     * \\param objectPath Path to the object on the service.
     * \\param parent Passed to the parent class constructor.
     */
    %(name)s(
        const QDBusConnection& connection,
        const QString& busName,
        const QString& objectPath,
        QObject* parent = 0
    );
""" % {'name' : name,
       'headercmd' : get_headerfile_cmd(self.realinclude, self.prettyinclude),
       'groupcmd' : self.group and (' * \\ingroup %s\n' % self.group),
       'dbusname' : dbusname,
       'visibility': self.visibility,
       })

        self.b("""
%(name)s::%(name)s(const QString& busName, const QString& objectPath, QObject *parent)
    : Tp::AbstractInterface(busName, objectPath, staticInterfaceName(), QDBusConnection::sessionBus(), parent)
{
}

%(name)s::%(name)s(const QDBusConnection& connection, const QString& busName, const QString& objectPath, QObject *parent)
    : Tp::AbstractInterface(busName, objectPath, staticInterfaceName(), connection, parent)
{
}
""" % {'name' : name})

        # Construct from DBusProxy subclass
        self.h("""
    /**
     * Creates a %(name)s associated with the same object as the given proxy.
     *
     * \\param proxy The proxy to use. It will also be the QObject::parent()
     *               for this object.
     */
    %(name)s(%(dbus_proxy)s *proxy);
""" % {'name' : name,
       'dbus_proxy' : self.dbus_proxy})

        self.b("""
%(name)s::%(name)s(%(dbus_proxy)s *proxy)
    : Tp::AbstractInterface(proxy, staticInterfaceName())
{
}
""" % {'name' : name,
       'dbus_proxy' : self.dbus_proxy})

        # Main interface
        mainiface = self.mainiface or 'Tp::AbstractInterface'

        if mainiface != self.namespace + '::' + name:
            self.h("""
    /**
     * Creates a %(name)s associated with the same object as the given proxy.
     * Additionally, the created proxy will have the same parent as the given
     * proxy.
     *
     * \\param mainInterface The proxy to use.
     */
    explicit %(name)s(const %(mainiface)s& mainInterface);

    /**
     * Creates a %(name)s associated with the same object as the given proxy.
     * However, a different parent object can be specified.
     *
     * \\param mainInterface The proxy to use.
     * \\param parent Passed to the parent class constructor.
     */
    %(name)s(const %(mainiface)s& mainInterface, QObject* parent);
""" % {'name' : name,
       'mainiface' : mainiface})

            self.b("""
%(name)s::%(name)s(const %(mainiface)s& mainInterface)
    : Tp::AbstractInterface(mainInterface.service(), mainInterface.path(), staticInterfaceName(), mainInterface.connection(), mainInterface.parent())
{
}

%(name)s::%(name)s(const %(mainiface)s& mainInterface, QObject *parent)
    : Tp::AbstractInterface(mainInterface.service(), mainInterface.path(), staticInterfaceName(), mainInterface.connection(), parent)
{
}
""" % {'name' : name,
       'mainiface' : mainiface})

        # Properties
        has_props = False
        for prop in get_by_path(iface, 'property'):
            # Skip tp:properties
            if not prop.namespaceURI:
                self.do_prop(prop)
                has_props = True

        self.h("""
    /**
     * Request all of the DBus properties on the interface.
     *
     * \\return A pending variant map which will emit finished when the properties have
     *          been retrieved.
     */
    Tp::PendingVariantMap *requestAllProperties() const
    {
        return internalRequestAllProperties();
    }
""")

        # Methods
        methods = get_by_path(iface, 'method')

        if methods:
            self.h("""
public Q_SLOTS:\
""")

            for method in methods:
                self.do_method(method)

        # Signals
        signals = get_by_path(iface, 'signal')

        if signals:
            self.h("""
Q_SIGNALS:\
""")

            for signal in signals:
                self.do_signal(signal)

        # invalidated handler (already a slot in the superclass)
        # we can't just use disconnect(this, NULL, NULL, NULL) because
        # (a) that would disconnect QObject::destroyed() and other non-D-Bus
        # signals, and (b) QtDBus doesn't support that usage anyway (it needs
        # specific signals in order to remove its signal match rules)
        self.h("""
protected:
    virtual void invalidate(Tp::DBusProxy *, const QString &, const QString &);
""")

        self.b("""
void %(name)s::invalidate(Tp::DBusProxy *proxy,
        const QString &error, const QString &message)
{
""" % {'name' : name})

        for signal in signals:
            self.do_signal_disconnect(signal)

        self.b("""
    Tp::AbstractInterface::invalidate(proxy, error, message);
}
""")

        # Close class
        self.h("""\
};
""")

    def do_prop(self, prop):
        name = prop.getAttribute('name')
        access = prop.getAttribute('access')
        gettername = name
        settername = None

        sig = prop.getAttribute('type')
        tptype = prop.getAttributeNS(NS_TP, 'type')
        binding = binding_from_usage(sig, tptype, self.custom_lists, (sig, tptype) in self.externals, self.typesnamespace)

        if 'write' in access:
            settername = 'set' + name

        if 'read' in access:
            self.h("""
    /**
     * Asynchronous getter for the remote object property "%(name)s" of type %(val)s.
     *
%(docstring)s\
     *
     * \\return A pending variant which will emit finished when the property has been
     *          retrieved.
     */
    inline Tp::PendingVariant *%(gettername)s() const
    {
        return internalRequestProperty(QLatin1String("%(name)s"));
    }
""" % {'name' : name,
       'docstring' : format_docstring(prop, '     * ').replace('*/',
           '&#42;&#47;'),
       'val' : binding.val,
       'name' : name,
       'gettername' : 'requestProperty' + name})

        if 'write' in access:
            self.h("""
    /**
     * Asynchronous setter for the remote object property "%(name)s" of type %(type)s.
     *
%(docstring)s\
     *
     * \\return A pending operation which will emit finished when the property has been
     *          set.
     */
    inline Tp::PendingOperation *%(settername)s(%(type)s newValue)
    {
        return internalSetProperty(QLatin1String("%(name)s"), QVariant::fromValue(newValue));
    }
""" % {'name' : name,
       'docstring' : format_docstring(prop, '     * ').replace('*/',
           '&#42;&#47;'),
       'type' : binding.val,
       'name' : name,
       'settername' : 'setProperty' + name})

    def do_method(self, method):
        name = method.getAttribute('name')
        args = get_by_path(method, 'arg')
        argnames, argdocstrings, argbindings = extract_arg_or_member_info(args, self.custom_lists, self.externals, self.typesnamespace, '     *     ')

        inargs = []
        outargs = []

        for i in xrange(len(args)):
            if args[i].getAttribute('direction') == 'out':
                outargs.append(i)
            else:
                inargs.append(i)
                assert argnames[i] != None, 'No argument name for input argument at index %d for method %s' % (i, name)

        rettypes = ', '.join([argbindings[i].val for i in outargs])
        params = ', '.join([argbindings[i].inarg + ' ' + argnames[i] for i in inargs])
        if params:
            params += ', int timeout = -1'
        else:
            params = 'int timeout = -1'

        self.h("""
    /**
     * Begins a call to the D-Bus method "%s" on the remote object.
%s\
     *
     * Note that \\a timeout is ignored as of now. It will be used once
     * http://bugreports.qt.nokia.com/browse/QTBUG-11775 is fixed.
     *
""" % (name, format_docstring(method, '     * ')))

        for i in inargs:
            if argdocstrings[i]:
                self.h("""\
     *
     * \\param %s
%s\
""" % (argnames[i], argdocstrings[i]))

        self.h("""\
     * \\param timeout The timeout in milliseconds.
""")

        for i in outargs:
            if argdocstrings[i]:
                self.h("""\
     *
     * \\return
%s\
""" % argdocstrings[i])

        self.h("""\
     */
    inline QDBusPendingReply<%(rettypes)s> %(name)s(%(params)s)
    {
        if (!invalidationReason().isEmpty()) {
            return QDBusPendingReply<%(rettypes)s>(QDBusMessage::createError(
                invalidationReason(),
                invalidationMessage()
            ));
        }
""" % {'rettypes' : rettypes,
       'name' : name,
       'params' : params})

        if inargs:
            self.h("""
        QDBusMessage callMessage = QDBusMessage::createMethodCall(this->service(), this->path(),
                this->staticInterfaceName(), QLatin1String("%s"));
        callMessage << %s;
        return this->connection().asyncCall(callMessage, timeout);
    }
""" % (name, ' << '.join(['QVariant::fromValue(%s)' % argnames[i] for i in inargs])))
        else:
            self.h("""
        QDBusMessage callMessage = QDBusMessage::createMethodCall(this->service(), this->path(),
                this->staticInterfaceName(), QLatin1String("%s"));
        return this->connection().asyncCall(callMessage, timeout);
    }
""" % name)

    def do_signal(self, signal):
        name = signal.getAttribute('name')
        argnames, argdocstrings, argbindings = extract_arg_or_member_info(get_by_path(signal, 'arg'), self.custom_lists, self.externals, self.typesnamespace, '     *     ')

        self.h("""
    /**
     * Represents the signal "%s" on the remote object.
%s\
""" % (name, format_docstring(signal, '     * ')))

        for i in xrange(len(argnames)):
            assert argnames[i] != None, 'Name missing from argument at index %d for signal %s' % (i, name)
            if argdocstrings[i]:
                self.h("""\
     *
     * \\param %s
%s\
""" % (argnames[i], argdocstrings[i]))

        self.h("""\
     */
    void %s(%s);
""" % (name, ', '.join(['%s %s' % (binding.inarg, name) for binding, name in zip(argbindings, argnames)])))

    def do_signal_disconnect(self, signal):
        name = signal.getAttribute('name')
        _, _, argbindings = extract_arg_or_member_info(get_by_path(signal, 'arg'), self.custom_lists, self.externals, self.typesnamespace, '     *     ')

        self.b("""\
    disconnect(this, SIGNAL(%s(%s)), NULL, NULL);
""" % (name, ', '.join([binding.inarg for binding in argbindings])))

    def h(self, str):
        self.hs.append(str)

    def b(self, str):
        self.bs.append(str)

    def hb(self, str):
        self.h(str)
        self.b(str)


if __name__ == '__main__':
    options, argv = gnu_getopt(argv[1:], '',
            ['group=',
             'namespace=',
             'typesnamespace=',
             'headerfile=',
             'implfile=',
             'ifacexml=',
             'specxml=',
             'realinclude=',
             'prettyinclude=',
             'extraincludes=',
             'mainiface=',
             'must-define=',
             'dbus-proxy=',
             'visibility='])

    Generator(dict(options))()
