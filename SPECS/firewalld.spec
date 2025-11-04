Summary: A firewall daemon with D-Bus interface providing a dynamic firewall
Name: firewalld
Version: 1.3.4
Release: 15%{?dist}
URL:     http://www.firewalld.org
License: GPLv2+
Source0: https://github.com/firewalld/firewalld/releases/download/v%{version}/firewalld-%{version}.tar.bz2
Patch1: 0001-RHEL-only-Add-cockpit-by-default-to-some-zones.patch
Patch2: 0002-v1.4.0-test-atlocal-pass-EBTABLES-to-testsuite.patch
Patch3: 0003-v1.4.0-feat-direct-avoid-iptables-flush-if-using-nft.patch
Patch4: 0004-v1.4.0-test-direct-avoid-iptables-flush-if-using-nft.patch
Patch5: 0005-v2.0.0-feat-service-add-OpenTelemetry-OTLP-service.patch
Patch6: 0006-v2.1.0-feat-icmp-add-ICMPv6-Multicast-Listener-Disco.patch
Patch7: 0007-v2.1.0-fix-rich-validate-service-name-of-rich-rule.patch
Patch8: 0008-v2.1.0-improvement-nftables-do-not-track-rule-handle.patch
Patch9: 0009-v2.1.0-improvement-fw-make-set_policy-DROP-more-flex.patch
Patch10: 0010-v2.1.0-feat-fw-add-ReloadPolicy-option-in-firewalld..patch
Patch11: 0011-v2.2.0-test-functions-add-macro-CHECK_NFTABLES_FIB.patch
Patch12: 0012-v2.2.0-test-functions-add-macro-CHECK_NFTABLES_FIB_I.patch
Patch13: 0013-v2.2.0-test-rpfilter-use-CHECK-macros.patch
Patch14: 0014-v2.2.0-test-IPv6_rpfilter-verify-valid-values.patch
Patch15: 0015-v2.2.0-chore-IPv6_rpfilter-prepare-for-new-config-va.patch
Patch16: 0016-v2.2.0-feat-IPv6_rpfilter-support-loose-rpfilter.patch
Patch17: 0017-v2.2.0-feat-IPv6_rpfilter-support-loose-forward-rpfi.patch
Patch18: 0018-v2.2.0-feat-IPv6_rpfilter-support-strict-forward-rpf.patch
Patch19: 0019-v2.2.0-test-functions-start-firewalld-with-file-logg.patch
Patch20: 0020-v2.2.0-feat-nftables-table-ownership.patch
Patch21: 0021-v2.2.0-test-nftables-table-ownership.patch
Patch22: 0022-v2.2.0-chore-service-remove-Conflicts-with-nftables.patch
Patch23: 0023-v2.2.0-fix-service-update-highest-port-number-for-ce.patch
Patch24: 0024-v2.2.0-feat-service-x-rootd-file-server.patch
Patch25: 0025-v2.3.0-test-functions-fix-iptables-normalization-for.patch
Patch26: 0026-v2.4.0-test-add-scale-keyword-to-scale-tests.patch
Patch27: 0027-v2.4.0-fix-systemd-verify-firewalld-is-responsive-to.patch
Patch28: 0028-v2.4.0-fix-systemd-remove-unnecessary-comment.patch
Patch29: 0029-v2.4.0-test-nftables-table-owner-use-grep-instead-of.patch
Patch30: 0030-v2.4.0-chore-ipset-remove-set_supported_types.patch
Patch31: 0031-v2.4.0-fix-fw-start-remove-ipset-probe.patch
Patch32: 0032-v2.4.0-fix-systemd-allow-start-code-251-RUNNING_BUT_FAILED.patch
Patch33: 0033-v2.4.0-fix-policy-rich-verify-ipset-exists.patch
Patch34: 0034-v2.4.0-test-rich-rule-reference-invalid-ipset.patch
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
# must run automake since patches touch .am files
./autogen.sh
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
* Tue Jun 17 2025 Eric Garver <egarver@redhat.com> - 1.3.4-15
- fix(policy): rich: verify ipset exists

* Mon Jun 02 2025 Eric Garver <egarver@redhat.com> - 1.3.4-14
- fix(systemd): allow start code 251 (RUNNING_BUT_FAILED)

* Mon May 19 2025 Eric Garver <egarver@redhat.com> - 1.3.4-13
- fix(fw): start: remove ipset probe

* Mon May 19 2025 Eric Garver <egarver@redhat.com> - 1.3.4-12
- fix(systemd): verify firewalld is responsive to dbus

* Mon May 19 2025 Eric Garver <egarver@redhat.com> - 1.3.4-11
- test: add scale keyword to scale tests

* Mon May 19 2025 Eric Garver <egarver@redhat.com> - 1.3.4-10
- test(functions): fix iptables normalization for opt field

* Wed Nov 06 2024 Eric Garver <egarver@redhat.com> - 1.3.4-9
- feat(service): (x)rootd file server

* Wed Nov 06 2024 Eric Garver <egarver@redhat.com> - 1.3.4-8
- fix(service): update highest port number for ceph

* Mon Jul 01 2024 Eric Garver <egarver@redhat.com> - 1.3.4-7
- feat(nftables): table ownership

* Mon Jul 01 2024 Eric Garver <egarver@redhat.com> - 1.3.4-6
- feat(IPv6_rpfilter): support loose rpfilter
- feat(IPv6_rpfilter): support loose-forward rpfilter
- feat(IPv6_rpfilter): support strict-forward rpfilter 

* Mon Jul 01 2024 Eric Garver <egarver@redhat.com> - 1.3.4-5
- feat(fw): add ReloadPolicy option in firewalld.conf

* Mon Jul 01 2024 Eric Garver <egarver@redhat.com> - 1.3.4-4
- fix(rich): validate service name of rich rule

* Mon Jul 01 2024 Eric Garver <egarver@redhat.com> - 1.3.4-3
- feat(icmp): add ICMPv6 Multicast Listener Discovery (MLD) types

* Mon Jul 01 2024 Eric Garver <egarver@redhat.com> - 1.3.4-2
- feat(service): add OpenTelemetry (OTLP) service

* Thu Oct 26 2023 Eric Garver <egarver@redhat.com> - 1.3.4-1
- package rebase to v1.3.4

* Mon Apr 24 2023 Eric Garver <egarver@redhat.com> - 1.2.5-1
- package rebase to v1.2.5
- feat(direct): avoid iptables flush if using nftables backend

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
