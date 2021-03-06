from fabric.api import *
import config
from contextlib import contextmanager as _contextmanager
from fabric.contrib.files import *

env.hosts = [config.HOST]
env.user = config.INSTALL_USER
env.password = config.INSTALL_USER_PW
env.colorize_errors = True



@_contextmanager
def virtualenv():
    with prefix(config.venv_activate):
        yield


def git():
    code_dir = config.CODE_DIR
    with settings(warn_only=True):
        run("git clone " + config.GIT_URL)
    with cd(code_dir + '/' + config.GIT_REPO_NAME):
        run("git pull")


def install():
    sudo('apt-get update')
    sudo('apt-get -y upgrade')
    with settings(prompts={
        "Press [ENTER] to continue or ctrl-c to cancel adding it": '',
        'Do you want to continue? [Y/n] ': 'Y'
    }):
        # this gcc is redundant in some images, but required in others. We
        # use a dev version of python since we have cutting edge tech
        sudo('apt-get install gcc')
        sudo('add-apt-repository ppa:deadsnakes/ppa')
        sudo('apt-get install python3.6-dev')
        sudo('apt-get update')
        sudo('apt-get -y install postgresql postgresql-contrib')
        sudo('apt-get -y install nginx')
        sudo('apt-get -y install supervisor')
        sudo('systemctl enable supervisor')
        sudo('systemctl start supervisor')
        run('wget https://bootstrap.pypa.io/get-pip.py')
        sudo('python3.6 get-pip.py')
        sudo('pip3.6 install virtualenv')


def update_basics():
    sudo('apt-get update')
    sudo('apt-get upgrade')



def create_application_user():
    run('adduser --system {}'.format(config.CONSUMER_USER))
    with settings(prompts={
        'Enter new UNIX password: ': config.CONSUMER_PASSWORD
        }):
        run('sudo passwd {}'.format(config.CONSUMER_USER))


def database_setup():
    user = config.CONSUMER_USER
    pw = config.DB_PASSWORD
    db = config.DB
    with settings(warn_only=True):
        result = sudo("""psql -c "CREATE USER {user} WITH ENCRYPTED PASSWORD '{pw}'" """.format(user=user, pw=pw), user='postgres')
        if result.return_code == 1:
            sudo("""psql -c "ALTER USER {user} WITH ENCRYPTED PASSWORD '{pw}'" """.format(user=user, pw=pw),
                 user='postgres')
        sudo('psql -c "CREATE DATABASE {db} WITH OWNER {user};"'.format(db=db, user=user), user='postgres')


def create_venv():
    with settings(warn_only=True):
        run('virtualenv venv -p python3.6')


def deploy_django():
    with settings(prompts={
        "Type 'yes' to continue, or 'no' to cancel: ": 'yes'
    }):
        run('pip3 install -r ' + config.GIT_REPO_NAME + '/requirements.txt --no-cache-dir')
        run('pip3 install psycopg2-binary')
        with cd(config.CODE_DIR + '/' + config.GIT_REPO_NAME):
            upload_template('files/consumer_env',
                            destination='.env')
            run('python manage.py migrate')
            run('python manage.py migrate locks')

            upload_template(
                filename='files/consumer_env',
                destination='.env')
            run('python manage.py collectstatic')
            run("""echo "from django.contrib.auth.models import User; User.objects.filter(email='{email}').delete(); User.objects.create_superuser(username='{user}', email='{email}', password='{password}')" | python manage.py shell""".format(
                email=config.SUPERUSER_EMAIL,
                user=config.SUPERUSER_NAME,
                password=config.SUPERUSER_PASSWORD
            ))


def update_django():
    with cd(config.CODE_DIR + '/' + config.GIT_REPO_NAME):
        with settings(prompts={
            "Type 'yes' to continue, or 'no' to cancel: ": 'yes'
        }):
            run('pip3 install -r ' + 'requirements.txt --no-cache-dir --upgrade')
            upload_template('files/consumer_env',
                            destination='.env')
            run('python manage.py migrate')
            run('python manage.py migrate locks')
            run('python manage.py collectstatic')
            run(
                """echo "from django.contrib.auth.models import User; User.objects.filter(email='{email}').delete(); User.objects.create_superuser(username='{user}', email='{email}', password='{password}')" | python manage.py shell""".format(
                    email=config.SUPERUSER_EMAIL,
                    user=config.SUPERUSER_NAME,
                    password=config.SUPERUSER_PASSWORD
                ))
            run("""python manage.py unlock all""")


def setup_gunicorn():
    upload_template(
        filename='files/gunicorn_start',
        destination='/srv/CIP'
    )
    run('chmod u+x /srv/CIP/gunicorn_start')
    with settings(warn_only=True):
        run('mkdir run logs')
        run('touch logs/gunicorn.log')


def update_gunicorn():
    upload_template(
        filename='files/gunicorn_start',
        destination='/srv/CIP'
    )
    run('chmod u+x /srv/CIP/gunicorn_start')


def setup_logfiles():
    with settings(warn_only=True):
        run('mkdir logs')
        run('touch logs/gunicorn.log')
        run('touch logs/binancebot.log')
        run('touch logs/bittrexbot.log')
        run('touch logs/gdaxbot.log')
        run('touch logs/bitfinexbot.log')


def chmod_commands():
    directory = os.fsencode('../commands/')
    for filename in os.listdir(directory):
        if filename.endswith(b'.sh'):
            file = '/srv/CIP/django-crypto-repo/commands/{}'.format(filename.decode('utf-8'))
            run('chmod u+x {}'.format(file))


def setup_supervisor():
    stop_supervisor()
    directory = os.fsencode('files/supervisor/')
    for filename in os.listdir(directory):
        if filename.endswith(b'.conf'):
            destination = '/etc/supervisor/conf.d/{}'.format(filename.decode("utf-8") )
            upload_template(
                'files/supervisor/' + filename.decode("utf-8"),
                destination=destination,
                use_sudo=True
            )
    start_supervisor()


def stop_supervisor():
    sudo('supervisorctl stop all')


def start_supervisor():
    sudo('supervisorctl reread')
    sudo('supervisorctl update')
    sudo('supervisorctl restart all')


def setup_nginx():
    upload_template(
        'files/nginx/repo_base',
        destination='/etc/nginx/sites-available/repo_base',
        use_sudo=True,
        context={
            'server_name': config.HOST
        }
    )
    with settings(warn_only=True):
        run('sudo ln -s /etc/nginx/sites-available/repo_base /etc/nginx/sites-enabled/repo_base')
        run('sudo rm /etc/nginx/sites-enabled/default')
    run('sudo service nginx restart')


def cleanup():
    with settings(promts={
        'Do you want to continue? [Y/n] ': 'Y'
    }):
        sudo('apt autoremove')


def initial_deploy():
    install()
    create_application_user()
    database_setup()
    with settings(warn_only=True):
        sudo('mkdir /srv/CIP')

    with cd(config.CODE_DIR):
        # with settings(user=config.CONSUMER_USER,
        #               prompts={
        #                   "Login password for 'uconsumer': ": config.CONSUMER_USER
        #     }):
        git()
        create_venv()
        with virtualenv():
            with settings(prompts={
                "Type 'yes' to continue, or 'no' to cancel: ": 'yes'
            }):
                deploy_django()
                setup_logfiles()
                setup_gunicorn()

    setup_nginx()
    setup_supervisor()
    cleanup()

def clear():
    with cd(config.CODE_DIR + '/' + config.GIT_REPO_NAME):
        with virtualenv():
            run('python manage.py flush')


def update():
    update_basics()
    with cd(config.CODE_DIR):
        git()
        with virtualenv():
            stop_supervisor()
            update_django()
            update_gunicorn()
            setup_supervisor()
            cleanup()




