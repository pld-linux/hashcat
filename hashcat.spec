Summary:	Advanced password recovery utility
Summary(pl.UTF-8):	Zaawansowane narzędzie do odzyskiwania haseł
Name:		hashcat
Version:	8.0.0
Release:	1
License:	MIT, BSD, CC0 v1.0 or Apache v2.0, Public Domain
Group:		Applications/System
Source0:	https://hashcat.net/files/%{name}-%{version}.tar.gz
# Source0-md5:	20234925e1f061718007c08c38ac03de
# https://github.com/hashcat/hashcat/commit/694ddd0f2c93434536946791337d0f6085faee46
Patch0:		%{name}-argon2-brain-handshake.patch
# https://github.com/hashcat/hashcat/commit/0c39fad170911edb62f29f60147466abca7862e0
Patch1:		%{name}-racf-memory-factor.patch
URL:		https://hashcat.net/hashcat/
BuildRequires:	khronos-OpenCL-headers
BuildRequires:	rpmbuild(macros) >= 1.673
# hcstat2 (every mask attack and --benchmark) and compressed inputs are read
# through libraries loaded with dlopen(), which rpm cannot see
Requires:	ocl-icd-libOpenCL
Requires:	xz-libs
Requires:	zlib
Requires:	zstd
Suggests:	openssl
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# prebuilt ARM boot loader for the ZC706 FPGA board, host strip cannot read it
%define		_noautostrip	.*/fsbl\.elf

# LFLAGS given on the command line replaces upstream's, which add -s and
# strip everything before debuginfo is extracted; REPRO_TRY maps the build
# dir to "." in DWARF, so debugedit finds no sources
%define		make_opts	CC="%{__cc}" LFLAGS="%{rpmldflags}" REPRO_TRY= PREFIX=%{_prefix} LIBRARY_FOLDER=%{_libdir} SHARED_FOLDER=%{_libdir}/%{name} DOCUMENT_FOLDER=%{_docdir}/%{name}-%{version} MAINTAINER_MODE=1 USE_SYSTEM_OPENCL=1 RUST_CARGO=false

%description
hashcat is a password recovery utility supporting hundreds of hash
algorithms and several attack modes. It runs on CPUs, GPUs and other
accelerators through OpenCL, CUDA, HIP and Metal backends.

%description -l pl.UTF-8
hashcat to narzędzie do odzyskiwania haseł obsługujące setki
algorytmów skrótu i kilka trybów ataku. Działa na procesorach CPU,
GPU i innych akceleratorach poprzez interfejsy OpenCL, CUDA, HIP i
Metal.

%package devel
Summary:	Header files for hashcat plugin development
Summary(pl.UTF-8):	Pliki nagłówkowe do tworzenia wtyczek hashcata
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	khronos-OpenCL-headers

%description devel
Header files for building hashcat modules, bridges and feeds against
libhashcat.

%description devel -l pl.UTF-8
Pliki nagłówkowe do budowania wtyczek hashcata (modułów, mostków i
generatorów haseł do sprawdzenia) z użyciem biblioteki libhashcat.

%package tools
Summary:	Scripts extracting hashes for hashcat
Summary(pl.UTF-8):	Skrypty wydobywające skróty dla hashcata
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}

%description tools
Scripts extracting hashes in hashcat format from encrypted volumes,
wallets, password managers, keystores and other files.

%description tools -l pl.UTF-8
Skrypty wydobywające skróty w formacie hashcata z zaszyfrowanych
woluminów, portfeli kryptowalut, menedżerów haseł, magazynów kluczy i
innych plików.

%package -n bash-completion-%{name}
Summary:	bash-completion for hashcat
Summary(pl.UTF-8):	Bashowe uzupełnianie parametrów dla hashcata
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	bash-completion >= 1:2.0
BuildArch:	noarch

%description -n bash-completion-%{name}
bash-completion for hashcat.

%description -n bash-completion-%{name} -l pl.UTF-8
Bashowe uzupełnianie parametrów dla hashcata.

%prep
%setup -q
%patch -P0 -p1
%patch -P1 -p1

%{__rm} -r deps/OpenCL-Headers

%{__sed} -i -e '1s,^#!.*python3,#!%{__python3},' tools/*hashcat.py extra/fpga/zc706-sdboot/make_bootbin.py
%{__sed} -i -e '1s,^#!.*perl,#!%{__perl},' tools/*hashcat.pl
%{__sed} -i -e 's,^HASHCAT_ROOT=.*,HASHCAT_ROOT="%{_bindir}",' extra/tab_completion/hashcat.sh

%build
CFLAGS="%{rpmcflags} %{rpmcppflags}" \
%{__make} \
	%{make_opts}

%install
rm -rf $RPM_BUILD_ROOT

CFLAGS="%{rpmcflags} %{rpmcppflags}" \
%{__make} install \
	%{make_opts} \
	DESTDIR=$RPM_BUILD_ROOT

# keyed on file size and nanosecond mtime, which stripping and rpm do not
# keep; hashcat rebuilds it in the user's cache directory
%{__rm} $RPM_BUILD_ROOT%{_libdir}/%{name}/module_options.so.cache

find $RPM_BUILD_ROOT%{_libdir}/%{name} -name .gitkeep -delete

# installed 0644, which find-debuginfo skips
find $RPM_BUILD_ROOT%{_libdir}/%{name} -name '*.so' -exec chmod 755 {} +

install -D -p extra/tab_completion/hashcat.sh $RPM_BUILD_ROOT%{bash_compdir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%{_docdir}/%{name}-%{version}
%attr(755,root,root) %{_bindir}/hashcat
%{_libdir}/libhashcat.so.8
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/OpenCL
%{_libdir}/%{name}/Python
%dir %{_libdir}/%{name}/bridges
%{_libdir}/%{name}/bridges/*.so
%dir %{_libdir}/%{name}/bridges/subs
%dir %{_libdir}/%{name}/extra
%dir %{_libdir}/%{name}/extra/fpga
%{_libdir}/%{name}/extra/fpga/99-*.rules
%dir %{_libdir}/%{name}/extra/fpga/zc706-sdboot
%{_libdir}/%{name}/extra/fpga/zc706-sdboot/README.md
%{_libdir}/%{name}/extra/fpga/zc706-sdboot/build_fsbl.tcl
%{_libdir}/%{name}/extra/fpga/zc706-sdboot/fsbl.elf
%attr(755,root,root) %{_libdir}/%{name}/extra/fpga/zc706-sdboot/make_bootbin.py
%dir %{_libdir}/%{name}/feeds
%{_libdir}/%{name}/feeds/*.so
%dir %{_libdir}/%{name}/modules
%{_libdir}/%{name}/modules/*.so
%{_libdir}/%{name}/pcfg
%{_libdir}/%{name}/rules
%{_libdir}/%{name}/tunings
%{_libdir}/%{name}/hashcat.hcstat2

%files devel
%defattr(644,root,root,755)
%{_libdir}/libhashcat.so
%{_includedir}/hashcat

%files tools
%defattr(644,root,root,755)
%attr(755,root,root) %{_bindir}/*2hashcat.p[ly]
%attr(755,root,root) %{_bindir}/*_to_hashcat.p[ly]
%attr(755,root,root) %{_bindir}/*-to-hashcat.py

%files -n bash-completion-%{name}
%defattr(644,root,root,755)
%{bash_compdir}/%{name}
