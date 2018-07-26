%define name unixODBC
%define ver 2.3.6
# %define prefix /usr
# %define sysconfdir /etc

%define _unpackaged_files_terminate_build 0

Summary: ODBC driver manager and drivers for PostgreSQL, MySQL, etc.
Name: %{name}
Version: %ver
Release: 2%{?dist}
License: GPLv2+ and LGPLv2+
Group: Applications/Databases
URL: http://www.unixodbc.org/
# BuildRoot: /var/tmp/%{name}-%{ver}-root
# Docdir: %{prefix}/doc
# Prefix: %prefix

Source: %{name}-%{ver}.tar.gz
Source1: odbcinst.ini
Source2: odbc.ini

# Patch1: so-version-bump.patch

Conflicts: iodbc

BuildRequires: automake autoconf libtool libtool-ltdl-devel bison flex
BuildRequires: readline-devel

%description
unixODBC aims to provide a complete ODBC solution for the Linux platform.
All programs are GPL.
All libs are LGPL (except nn which is GPL?).

%package devel
Summary: Includes and static libraries for ODBC development
Group: Development/Libraries
Requires: %{name} = %{ver}

%description devel
unixODBC aims to provide a complete ODBC solution for the Linux platform.
All programs are GPL.
All libs are LGPL (except nn which is GPL?).
This package contains the include files and static libraries
for development.

# %package gui-qt
# Summary: ODBC configurator, Data Source browser and ODBC test tool based on Qt
# Group: Applications/Databases
# Requires: %{name} = %{ver}
# 
# %description gui-qt
# unixODBC aims to provide a complete ODBC solution for the Linux platform.
# All programs are GPL.
# All libs are LGPL (except nn which is GPL?).
# This package contains two Qt based GUI programs for unixODBC:
# ODBCConfig and DataManager

%prep
%setup -q
# %patch1 -p1

# export -n LANG LINGUAS LC_ALL
# if [ ! -f configure ]; then
	# CFLAGS="$RPM_OPT_FLAGS" ./autogen.sh $ARCH_FLAGS \
	# --sysconfdir=%{sysconfdir} --with-gnu-ld=yes --enable-threads=yes \
	# --enable-drivers=yes --enable-driverc=yes --enable-ltdllib
# else
	# CFLAGS="$RPM_OPT_FLAGS" ./configure $ARCH_FLAGS  \
	# --sysconfdir=%{sysconfdir} --enable-gui=no --with-gnu-ld=yes \
	# --enable-threads=yes --enable-drivers=yes --enable-driverc=yes \
	# --enable-ltdllib
# fi

%build

aclocal
automake --add-missing
autoconf

# unixODBC 2.2.14 is not aliasing-safe
CFLAGS="%{optflags} -fno-strict-aliasing -DDEFINE_CURSOR_LIB_VER"
CXXFLAGS="$CFLAGS"
export CFLAGS CXXFLAGS

%configure --with-gnu-ld=yes --enable-threads=yes \
	--enable-drivers=yes --enable-driverc=yes --enable-ltdllib
make all

# export -n LANG LINGUAS LC_ALL
# if [ "$SMP" != "" ]; then
	# (make "MAKE=make -k -j $SMP"; exit 0)
	# make
# else
	# make
# fi

%install
# [ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

# make prefix=$RPM_BUILD_ROOT%{prefix} sysconfdir=$RPM_BUILD_ROOT%{sysconfdir} install-strip
# mv $RPM_BUILD_ROOT%{prefix}/lib $RPM_BUILD_ROOT%{prefix}/lib64

make DESTDIR=$RPM_BUILD_ROOT install

install -m644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}
install -m644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}

# remove unpackaged files from the buildroot
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/libltdl.*
rm -rf $RPM_BUILD_ROOT%{_datadir}/libtool

# initialize lists of .so files
find $RPM_BUILD_ROOT%{_libdir} -name "*.so.*" | sed "s|^$RPM_BUILD_ROOT||" > base-so-list
find $RPM_BUILD_ROOT%{_libdir} -name "*.so"   | sed "s|^$RPM_BUILD_ROOT||" > devel-so-list

# move these to main package, they're often dlopened...
for lib in libodbc.so libodbcinst.so libodbcpsqlS.so libodbcmyS.so
do
    echo "%{_libdir}/$lib" >> base-so-list
    grep -v "/$lib$" devel-so-list > devel-so-list.x
    mv -f devel-so-list.x devel-so-list
done


%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

# %files
%files -f base-so-list
%defattr(-, root, root)

%doc AUTHORS COPYING ChangeLog NEWS README doc
%config(noreplace) %{sysconfdir}/odbc.ini
%config(noreplace) %{sysconfdir}/odbcinst.ini
%{_bindir}/dltest
%{_bindir}/slencheck
%{_bindir}/isql
%{_bindir}/iusql
%{_bindir}/odbcinst
%{_bindir}/odbc_config
%{_mandir}/man*/*
# %{_libdir}/libodbc.so*
# %{_libdir}/libodbccr.so*
# %{_libdir}/libodbcinst.so*
# %{prefix}/share/man/man1/dltest.1.gz
# %{prefix}/share/man/man1/isql.1.gz
# %{prefix}/share/man/man1/iusql.1.gz
# %{prefix}/share/man/man1/odbc_config.1.gz
# %{prefix}/share/man/man1/odbcinst.1.gz
# %{prefix}/share/man/man5/odbc.ini.5.gz
# %{prefix}/share/man/man5/odbcinst.ini.5.gz
# %{prefix}/share/man/man7/unixODBC.7.gz

# %files devel
%files devel -f devel-so-list
%defattr(-, root, root)

%{_includedir}/*
# %{prefix}/include/*
# %{prefix}/lib64/*.la

# %files gui-qt
# %defattr(-, root, root)

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

