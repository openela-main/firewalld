Summary: A firewall daemon with D-Bus interface providing a dynamic firewall
Name: firewalld
Version: 2.4.3
Release: 4%{?dist}
URL:     http://www.firewalld.org
License: GPL-2.0-or-later
Source0: https://github.com/firewalld/firewalld/releases/download/v%{version}/firewalld-%{version}.tar.bz2
Patch1: 0001-RHEL-only-Add-cockpit-by-default-to-some-zones.patch
Patch2: 0002-v2.5.0-fix-firewall-cmd-handle-no-options-when-not-r.patch
Patch3: 0003-v2.5.0-test-integration-podman-strict-forward-ports-.patch
BuildArch: noarch
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: desktop-file-utils
BuildRequires: gettext
BuildRequires: intltool
# glib2-devel is needed for gsettings.m4
BuildRequires: glib2, glib2-devel
BuildRequires: systemd-units
BuildRequires: docbook-style-xsl
BuildRequires: libxslt
BuildRequires: iptables, ebtables, ipset
BuildRequires: python3-devel
BuildRequires: make
Recommends: iptables, ebtables, ipset
Suggests: iptables-nft
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires: firewalld-filesystem = %{version}-%{release}
Requires: python3-firewall  = %{version}-%{release}
Obsoletes: firewalld-selinux < 0.4.4.2-2
Conflicts: selinux-policy < 3.14.1-28
Conflicts: cockpit-ws < 173-2
Recommends: libcap-ng-python3

%description
firewalld is a firewall service daemon that provides a dynamic customizable 
firewall with a D-Bus interface.

%package -n python3-firewall
Summary: Python3 bindings for firewalld

%{?python_provide:%python_provide python3-firewall}

Requires: python3-dbus
Requires: python3-gobject-base
Requires: python3-nftables

%description -n python3-firewall
Python3 bindings for firewalld.

%package -n firewalld-filesystem
Summary: Firewalld directory layout and rpm macros

%description -n firewalld-filesystem
This package provides directories and rpm macros which
are required by other packages that add firewalld configuration files.

%package -n firewalld-test
Summary: Firewalld testsuite

%description -n firewalld-test
This package provides the firewalld testsuite.

%package -n firewall-applet
Summary: Firewall panel applet
Requires: %{name} = %{version}-%{release}
Requires: firewall-config = %{version}-%{release}
Requires: python3-firewall = %{version}-%{release}
Requires: hicolor-icon-theme
%if (0%{?fedora} >= 39 || 0%{?rhel} >= 10)
Requires: python3-pyqt6-base
%else
Requires: python3-qt5-base
%endif
Requires: python3-gobject
Requires: libnotify
Requires: NetworkManager-libnm
Requires: dbus-x11

%description -n firewall-applet
The firewall panel applet provides a status information of firewalld and also 
the firewall settings.

%package -n firewall-config
Summary: Firewall configuration application
Requires: %{name} = %{version}-%{release}
Requires: python3-firewall = %{version}-%{release}
Requires: hicolor-icon-theme
Requires: gtk3
Requires: python3-gobject
Requires: NetworkManager-libnm
Requires: dbus-x11
Recommends: polkit

%description -n firewall-config
The firewall configuration application provides an configuration interface for 
firewalld.

%prep
%autosetup -p1

%build
%configure --enable-sysconfig --enable-rpmmacros \
  --with-systemd-unitdir=%{_unitdir} \
  PYTHON="%{__python3} %{py3_shbang_opts}"
make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}
desktop-file-install --delete-original \
  --dir %{buildroot}%{_sysconfdir}/xdg/autostart \
  %{buildroot}%{_sysconfdir}/xdg/autostart/firewall-applet.desktop
desktop-file-install --delete-original \
  --dir %{buildroot}%{_datadir}/applications \
  %{buildroot}%{_datadir}/applications/firewall-config.desktop

install -d -m 755 %{buildroot}%{_prefix}/lib/firewalld/zones/

%py_byte_compile %{__python3} %{buildroot}%{_datadir}/firewalld/gtk3_*

%find_lang %{name} --all-name

%post
%systemd_post firewalld.service

%preun
%systemd_preun firewalld.service

%postun
%systemd_postun_with_restart firewalld.service

%pretrans -p <lua>
-- HACK: Old rpm versions had an untracked (%ghost) symlink for
-- /etc/firewalld/firewalld.conf. RPM won't handle replacing the symlink due to
-- "%config(noreplace)". As such, we remove the symlink here before attempting
-- to install the new version which is a real file. Only replace the symlink if
-- the target matches one of the previous package's expected targets.
--
-- Unfortunately this must be done in pretrans in order to occur before RPM
-- makes decisions about file replacement.
--
local old_package_symlinks = {"firewalld-standard.conf", "firewalld-server.conf",
                              "firewalld-workstation.conf"}
local symlink_target = posix.readlink("%{_sysconfdir}/firewalld/firewalld.conf")
for k,v in ipairs(old_package_symlinks) do
  if symlink_target == v then
    posix.unlink("%{_sysconfdir}/firewalld/firewalld.conf")
    break
  end
end

%files -f %{name}.lang
%doc COPYING README.md
%{_sbindir}/firewalld
%{_bindir}/firewall-cmd
%{_bindir}/firewall-offline-cmd
%dir %{_datadir}/bash-completion/completions
%{_datadir}/bash-completion/completions/firewall-cmd
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/_firewalld
%{_prefix}/lib/firewalld/icmptypes/*.xml
%{_prefix}/lib/firewalld/ipsets/README.md
%{_prefix}/lib/firewalld/policies/*.xml
%{_prefix}/lib/firewalld/services/*.xml
%{_prefix}/lib/firewalld/zones/*.xml
%{_prefix}/lib/firewalld/helpers/*.xml
%{_prefix}/lib/firewalld/xmlschema/check.sh
%{_prefix}/lib/firewalld/xmlschema/*.xsd
%attr(0750,root,root) %dir %{_sysconfdir}/firewalld
%config(noreplace) %{_sysconfdir}/firewalld/firewalld.conf
%attr(0750,root,root) %dir %{_sysconfdir}/firewalld/helpers
%attr(0750,root,root) %dir %{_sysconfdir}/firewalld/icmptypes
%attr(0750,root,root) %dir %{_sysconfdir}/firewalld/ipsets
%attr(0750,root,root) %dir %{_sysconfdir}/firewalld/policies
%attr(0750,root,root) %dir %{_sysconfdir}/firewalld/services
%attr(0750,root,root) %dir %{_sysconfdir}/firewalld/zones
%defattr(0644,root,root)
%config(noreplace) %{_sysconfdir}/sysconfig/firewalld
%{_unitdir}/firewalld.service
%config(noreplace) %{_datadir}/dbus-1/system.d/FirewallD.conf
%{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.desktop.policy.choice
%{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.server.policy.choice
%{_datadir}/polkit-1/actions/org.fedoraproject.FirewallD1.policy
%{_mandir}/man1/firewall*cmd*.1*
%{_mandir}/man1/firewalld*.1*
%{_mandir}/man5/firewall*.5*
%{_sysconfdir}/modprobe.d/firewalld-sysctls.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/firewalld

%files -n python3-firewall
%attr(0755,root,root) %dir %{python3_sitelib}/firewall
%attr(0755,root,root) %dir %{python3_sitelib}/firewall/__pycache__
%attr(0755,root,root) %dir %{python3_sitelib}/firewall/config
%attr(0755,root,root) %dir %{python3_sitelib}/firewall/config/__pycache__
%attr(0755,root,root) %dir %{python3_sitelib}/firewall/core
%attr(0755,root,root) %dir %{python3_sitelib}/firewall/core/__pycache__
%attr(0755,root,root) %dir %{python3_sitelib}/firewall/core/io
%attr(0755,root,root) %dir %{python3_sitelib}/firewall/core/io/__pycache__
%attr(0755,root,root) %dir %{python3_sitelib}/firewall/server
%attr(0755,root,root) %dir %{python3_sitelib}/firewall/server/__pycache__
%{python3_sitelib}/firewall/__pycache__/*.py*
%{python3_sitelib}/firewall/*.py*
%{python3_sitelib}/firewall/config/*.py*
%{python3_sitelib}/firewall/config/__pycache__/*.py*
%{python3_sitelib}/firewall/core/*.py*
%{python3_sitelib}/firewall/core/__pycache__/*.py*
%{python3_sitelib}/firewall/core/io/*.py*
%{python3_sitelib}/firewall/core/io/__pycache__/*.py*
%{python3_sitelib}/firewall/server/*.py*
%{python3_sitelib}/firewall/server/__pycache__/*.py*

%files -n firewalld-filesystem
%dir %{_prefix}/lib/firewalld
%dir %{_prefix}/lib/firewalld/helpers
%dir %{_prefix}/lib/firewalld/icmptypes
%dir %{_prefix}/lib/firewalld/ipsets
%dir %{_prefix}/lib/firewalld/policies
%dir %{_prefix}/lib/firewalld/services
%dir %{_prefix}/lib/firewalld/zones
%{_rpmmacrodir}/macros.firewalld

%files -n firewalld-test
%dir %{_datadir}/firewalld/testsuite
%{_datadir}/firewalld/testsuite/README.md
%{_datadir}/firewalld/testsuite/testsuite
%dir %{_datadir}/firewalld/testsuite/integration
%{_datadir}/firewalld/testsuite/integration/testsuite
%dir %{_datadir}/firewalld/testsuite/python
%{_datadir}/firewalld/testsuite/python/firewalld_config.py
%{_datadir}/firewalld/testsuite/python/firewalld_direct.py
%{_datadir}/firewalld/testsuite/python/firewalld_rich.py
%{_datadir}/firewalld/testsuite/python/firewalld_misc.py

%files -n firewall-applet
%{_bindir}/firewall-applet
%defattr(0644,root,root)
%config(noreplace) %{_sysconfdir}/xdg/autostart/firewall-applet.desktop
%dir %{_sysconfdir}/firewall
%config(noreplace) %{_sysconfdir}/firewall/applet.conf
%{_datadir}/icons/hicolor/*/apps/firewall-applet*.*
%{_mandir}/man1/firewall-applet*.1*

%files -n firewall-config
%{_bindir}/firewall-config
%defattr(0644,root,root)
%{_datadir}/firewalld/firewall-config.glade
%pycached %{_datadir}/firewalld/gtk3_chooserbutton.py
%pycached %{_datadir}/firewalld/gtk3_niceexpander.py
%{_datadir}/applications/firewall-config.desktop
%{_datadir}/metainfo/org.firewalld.firewall-config.metainfo.xml
%{_datadir}/icons/hicolor/*/apps/firewall-config*.*
%{_datadir}/glib-2.0/schemas/org.fedoraproject.FirewallConfig.gschema.xml
%{_mandir}/man1/firewall-config*.1*

%changelog
* Fri Jun 31 2026 Eric Garver <egarver@redhat.com> - 2.4.3-4
- test(integration): podman-strict-forward-ports: expect fail with netavark

* Fri Jun 31 2026 Eric Garver <egarver@redhat.com> - 2.4.3-3
- fix(firewall-cmd): handle no options when not running

* Fri Jun 26 2026 Eric Garver <egarver@redhat.com> - 2.4.3-2
- rebuild to bump NVR; no changes

* Wed Jun 24 2026 Eric Garver <egarver@redhat.com> - 2.4.3-1
- rebase package to v2.4.3

* Tue Jun 09 2026 Eric Garver <egarver@redhat.com> - 2.4.2-1
- rebase package to v2.4.2

* Fri Nov 07 2025 Eric Garver <egarver@redhat.com> - 2.4.0-1
- rebase package to v2.4.0

* Tue Jun 10 2025 Eric Garver <egarver@redhat.com> - 2.3.1-1
- rebase package to v2.3.1

* Wed Jan 15 2025 Eric Garver <egarver@redhat.com> - 2.3.0-2
- revert RHEL only patch to default StrictForwardPorts=yes

* Tue Nov 05 2024 Eric Garver <egarver@redhat.com> - 2.3.0-1
- rebase package to v2.3.0

* Tue Oct 29 2024 Troy Dawson <tdawson@redhat.com> - 2.2.1-2
- Bump release for October 2024 mass rebuild:
  Resolves: RHEL-64018

* Wed Jul 24 2024 Eric Garver <egarver@redhat.com> - 2.2.1-1
- rebase package to v2.2.1

* Fri Jul 12 2024 Eric Garver <egarver@redhat.com> - 2.2.0-2
- fix firewalld.conf when upgrading from old versions that had a symlink

* Fri Jul 12 2024 Eric Garver <egarver@redhat.com> - 2.2.0-1
- rebase package to v2.2.0

* Mon Jun 24 2024 Troy Dawson <tdawson@redhat.com> - 2.1.2-3
- Bump release for June 2024 mass rebuild

* Wed Apr 17 2024 Eric Garver <egarver@redhat.com> - 2.1.2-2
- fix missing policykit symlink

* Tue Apr 16 2024 Eric Garver <egarver@redhat.com> - 2.1.2-1
- rebase package to v2.1.2

* Mon Jan 29 2024 Eric Garver <eric@garver.life> - 2.1.1-1
- rebase package to v2.1.1
