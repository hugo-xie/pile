from json import load as loadjson
from fabric.api import task, run, sudo, put
from fabric.context_managers import prefix, cd
from urllib.parse import urlparse

default_pip_mirror = 'http://mirrors.ustc.edu.cn/pypi/web/simple/'

required_libs = [
    'python3',
    'python3-dev',
    'git',
    'curl',
    'build-essential',
    'libffi6',
    'libffi-dev'
]

def get_pip_cmd(args, use_pip3=True, mirror=default_pip_mirror):
    pip = 'pip3' if use_pip3 else 'pip'
    if mirror and 'install' in args and '-i' not in args:
        host = urlparse(mirror).netloc
        mirror_arg_idx = args.index('install') + 1
        args[mirror_arg_idx:mirror_arg_idx] = ('-i', mirror,'--trusted-host', host)
    args.insert(0, pip)
    return ' '.join(args)

def get_public_ip():
    return run('curl -s "https://api.ipify.org"')

def install_libs():
    sudo('apt-get update')
    sudo('apt-get -y install %s' % ' '.join('"'+lib+'"' for lib in required_libs))
    put('get-pip.py', '/tmp/get-pip.py')
    sudo('python3 /tmp/get-pip.py')
    sudo(get_pip_cmd(['install', '--upgrade', 'virtualenv']))

def update_sudoers():
    sudo('''echo 'Defaults  env_keep += "DATABASE_URL"' > '/etc/sudoers.d/20_keep_dburl' ''')

def setup_iptables():
    rule_path = '/tmp/iptables.rule'
    put('iptables.rule.tmpl', rule_path)

    mgnt_ip = web_ip = get_public_ip()
    sudo('iptables -F')
    sudo('ip6tables -F')
    

    run('''sed -i -e 's/<MGNT-IP>/{mgnt_ip}/g' -e 's/<WEB-IP>/{web_ip}/g' "{rule_path}"'''.format(
        web_ip=web_ip,
        mgnt_ip=mgnt_ip,
        rule_path=rule_path
    ))

    # prevent from showing dpkg selection window
    sudo('echo iptables-persistent iptables-persistent/autosave_v4 boolean true | sudo debconf-set-selections')
    sudo('echo iptables-persistent iptables-persistent/autosave_v6 boolean true | sudo debconf-set-selections')
    sudo('iptables-restore < /tmp/iptables.rule')
    # keep iptables after reboot
    sudo('apt-get install iptables-persistent')

def import_ssh_key():
    run('mkdir -p ~/.ssh')
    run('[[ -f ~/.ssh/config ]] && mv -f ~/.ssh/config ~/.ssh/config.backup || true')
    run('[[ -f ~/.ssh/deploy_key_rsa ]] && mv -f ~/.ssh/deploy_key_rsa ~/.ssh/deploy_key_rsa.backup || true')
    put('deploy_key_rsa', '~/.ssh/', mode=0o400)
    put('ssh_config', '~/.ssh/config', mode=0o400)
    # test key
    run('ssh -T git@bitbucket.org')

def clone_fresh_repo():
    run('rm -rf ~/charger-web-backend')
    run('git clone git@bitbucket.org:huangloong/charger-web-backend.git ~/charger-web-backend')

def pull_repo():
    run('git pull')

def install_pip_libs():
    with prefix('source venv/bin/activate'):
        run(get_pip_cmd(['install', '--upgrade', '-r', 'requirements.txt']))
        # gevent python 3 is still in rc state
        # FIXME remove this line immediately when gevent python 3 stable!
        run(get_pip_cmd(['install', '--upgrade', '--pre', 'gevent']))

def setup_venv():
    run('virtualenv -p python3 venv')

@task
def write_production_config(environ_json):
    production_file = 'application/production.py'
    with open(environ_json, 'r') as envfp, cd('~/charger-web-backend'):
        environ = loadjson(envfp)
        for k,v in environ.items():
            run(r'''sed -i -e 's/^\(%s *=.*\)$/# \1/' "%s"''' % (k, production_file))
            run(r'''echo "%s = %s" >> "%s"''' % (k, repr(v).replace('"', r'\"'), production_file))

@task
def setup_logger():
    sudo("mkdir -p /var/log/api && chown $SUDO_USER '/var/log/api'")
    put('apiserver', '/etc/logrotate.d/apiserver', mode=0o600, use_sudo=True)
    sudo("chown root:root '/etc/logrotate.d/apiserver'")

@task
def start():
    with cd('~/charger-web-backend'):
        sudo('source venv/bin/activate && ./runproduct.sh ; sleep 3 ;')

@task
def stop():
    with cd('~/charger-web-backend'):
        # ignore PID not exist error
        sudo('kill `cat gunicorn.pid` ; true ; sleep 3 ;')

@task
def restart():
    stop()
    start()

@task
def status():
    run('ps aux | grep charger-web-backend')

@task
def clone_new():
    clone_fresh_repo()
    with cd('~/charger-web-backend'):
        setup_venv()
        install_pip_libs()
        #start()
@task
def first_install():
    install_libs()
    update_sudoers()
    setup_logger()
    setup_iptables()
    import_ssh_key()
    clone_new()

@task(default=True)
def update():
    with cd('~/charger-web-backend'):
        stop()
        pull_repo()
        # upgrade pip libraries in case new libs added
        install_pip_libs()
        start()

