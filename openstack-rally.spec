%global project rally
%global microversion cern1

Name:          openstack-%{project}
Version:       0.0.4
Release:       %{microversion}%{?dist}
Summary:       Benchmark System for OpenStack

Group:         CERN/Utilities
License:       Apache License, Version 2.0
URL:           https://openstack.cern.ch/
Source0:       %{project}-%{version}.%{microversion}.tar.gz

BuildArch:     noarch
BuildRequires: python-devel
BuildRequires: python-pbr >= 0.6

Requires:      python-babel >= 1.3
Requires:      python-boto >= 2.32.1
Requires:      python-decorator >= 3.4.0
Requires:      python-fixtures >= 0.3.14
Requires:      python-iso8601 >= 0.1.9
Requires:      python-jinja2 >= 2.6
Requires:      python-jsonschema >= 2.0.0
Requires:      python-netaddr >= 0.7.12
Requires:      python-oslo-config >= 1.9.0
Requires:      python-oslo-db >= 1.5.0
Requires:      python-oslo-i18n >= 1.3.0
Requires:      python-oslo-log >= 0.4.0
Requires:      python-oslo-serialization >= 1.2.0
Requires:      python-oslo-utils >= 1.2.0
Requires:      python-paramiko >= 1.13.0
Requires:      python-prettytable >= 0.7
Requires:      PyYAML >= 3.1.0
Requires:      python-psycopg2
Requires:      python-designateclient >= 1.0.0
Requires:      python-glanceclient >= 0.15.0
Requires:      python-keystoneclient >= 1.1.0
Requires:      python-novaclient >= 2.18.0
Requires:      python-neutronclient >= 2.3.11
Requires:      python-cinderclient >= 1.1.0
Requires:      python-heatclient >= 0.3.0
Requires:      python-ceilometerclient >= 1.0.6
Requires:      python-ironicclient >= 0.2.1
Requires:      python-saharaclient >= 0.7.6
Requires:      python-troveclient >= 1.0.7
Requires:      python-zaqarclient >= 0.0.3
Requires:      python-swiftclient >= 2.2.0
Requires:      python-subunit >= 0.0.18
Requires:      python-requests >= 2.2.0
Requires:      python-sqlalchemy >= 0.9.7
Requires:      python-sphinx >= 1.1.2
Requires:      python-six >= 1.9.0
Requires:      python-ordereddict
Requires:      python-simplejson >= 2.2.0
#Requires:      python-mistralclient
#Requires:      python-muranoclient >= 0.5.5

%description
Benchmark System for OpenStack

%prep
%setup -q -n %{project}-%{version}.%{microversion}
rm -rf {optional-,test-,}requirements.txt

%build
%{__python} setup.py build

%install
%{__python} setup.py install -O1 --skip-build --root %{buildroot}
install -p -D -m 644 etc/rally/rally.conf.sample %{buildroot}/%{_sysconfdir}/%{project}/rally.conf
install -d -m 755 %{buildroot}/%{_sysconfdir}/%{project}
install -d -m 700 %{buildroot}/%{_sharedstatedir}/%{project}/database
install -d -m 755 %{buildroot}/%{_datarootdir}/%{project}
cp -r samples %{buildroot}/%{_datarootdir}/%{project}/samples

%post
RALLY_DATABASE_DIR=%{_sharedstatedir}/%{project}/database
RALLY_CONFIGURATION_DIR=%{_sysconfdir}/%{project}
sed -i 's|#connection *=.*|connection = sqlite:///'${RALLY_DATABASE_DIR}'/rally.sqlite|' ${RALLY_CONFIGURATION_DIR}/rally.conf
rally-manage db recreate
chmod -R 700 ${RALLY_DATABASE_DIR}

%postun
%{__rm} -rf %{_sharedstatedir}/%{project}
%{__rm} -rf /root/.rally

%clean
%{__rm} -rf %{buildroot}

%files
%license LICENSE
%{python_sitelib}/%{project}
%{python_sitelib}/%{project}-%{version}*.egg-info

%{_bindir}/%{project}
%{_bindir}/%{project}-manage

%{_sysconfdir}/%{project}

%{_sysconfdir}/bash_completion.d/rally.bash_completion

%{_datarootdir}/%{project}

%dir %{_sharedstatedir}/%{project}/database

%changelog
* Wed May 20 2015 Wataru Takase <wataru.takase@cern.ch> - 0.0.2-cern2
- First RPM package
