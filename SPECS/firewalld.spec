Summary: A firewall daemon with D-Bus interface providing a dynamic firewall
Name: firewalld
Version: 1.2.1
Release: 1%{?dist}
URL:     http://www.firewalld.org
License: GPLv2+
Source0: https://github.com/firewalld/firewalld/releases/download/v%{version}/firewalld-%{version}.tar.gz
Patch1: 0001-RHEL-only-Add-cockpit-by-default-to-some-zones.patch
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
Requires: iptables, ebtables, ipset
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

%package -n firewall-applet
Summary: Firewall panel applet
Requires: %{name} = %{version}-%{release}
Requires: firewall-config = %{version}-%{release}
Requires: hicolor-icon-theme
Requires: python3-qt5-base
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
Requires: hicolor-icon-theme
Requires: gtk3
Requires: python3-gobject
Requires: NetworkManager-libnm
Requires: dbus-x11
Recommends: polkit

%description -n firewall-config
The firewall configuration application provides an configuration interface for 
firewalld.

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

%prep
%autosetup -p1

%build
%configure --enable-sysconfig --enable-rpmmacros PYTHON="%{__python3} %{py3_shbang_opts}"
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

# remove unhandle firewalld-test subpackage
rm -rf %{buildroot}%{_datadir}/firewalld/testsuite

%find_lang %{name} --all-name

%post
%systemd_post firewalld.service

%preun
%systemd_preun firewalld.service

%postun
%systemd_postun_with_restart firewalld.service 

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
%attr(0750,root,root) %dir %{_sysconfdir}/firewalld
%config(noreplace) %{_sysconfdir}/firewalld/firewalld.conf
%config(noreplace) %{_sysconfdir}/firewalld/lockdown-whitelist.xml
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
%{_sysconfdir}/logrotate.d/firewalld

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
%{_rpmconfigdir}/macros.d/macros.firewalld

%files -n firewall-applet
%{_bindir}/firewall-applet
%defattr(0644,root,root)
%{_sysconfdir}/xdg/autostart/firewall-applet.desktop
%dir %{_sysconfdir}/firewall
%{_sysconfdir}/firewall/applet.conf
%{_datadir}/icons/hicolor/*/apps/firewall-applet*.*
%{_mandir}/man1/firewall-applet*.1*

%files -n firewall-config
%{_bindir}/firewall-config
%defattr(0644,root,root)
%{_datadir}/firewalld/firewall-config.glade
%{_datadir}/firewalld/gtk3_chooserbutton.py*
%{_datadir}/firewalld/gtk3_niceexpander.py*
%{_datadir}/applications/firewall-config.desktop
%{_datadir}/metainfo/firewall-config.appdata.xml
%{_datadir}/icons/hicolor/*/apps/firewall-config*.*
%{_datadir}/glib-2.0/schemas/org.fedoraproject.FirewallConfig.gschema.xml
%{_mandir}/man1/firewall-config*.1*

%changelog
* Mon Nov 07 2022 Eric Garver <egarver@redhat.com> - 1.2.1-1
- package rebase to v1.2.1

* Wed Aug 03 2022 Eric Garver <egarver@redhat.com> - 1.1.1-3
- fix(runtimeToPermanent): errors for interfaces not in zone

* Fri Jul 15 2022 Eric Garver <egarver@redhat.com> - 1.1.1-2
- test(functions): normalize iptables ipv6-icmp/icmpv6

* Mon May 16 2022 Eric Garver <egarver@redhat.com> - 1.1.1-1
- package rebase to v1.1.1

* Mon Nov 22 2021 Eric Garver <egarver@redhat.com> - 1.0.0-4
- fix(firewalld): check capng_apply() return code

* Mon Nov 22 2021 Eric Garver <egarver@redhat.com> - 1.0.0-3
- fix(firewalld): keep linux capability CAP_SYS_MODULE

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 1.0.0-2
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Mon Jul 26 2021 Eric Garver <egarver@redhat.com> - 1.0.0-1
- package rebase to v1.0.0

* Mon Jun 07 2021 Eric Garver <egarver@redhat.com> - 1.0.0-0.3.alpha
- remove dead symlink (firewalld.conf) left over from old package versions
  before installing new file

* Tue Jun 01 2021 Eric Garver <egarver@redhat.com> - 1.0.0-0.2.alpha
- fix missing policy kit symlink

* Tue May 25 2021 Eric Garver <egarver@redhat.com> - 1.0.0-0.1.alpha
- package rebase to v1.0.0-alpha
