from fabric.api import roles, env, run, cd, sudo
from fabric.contrib.files import upload_template

env.hosts = [
    'deploy@nutsurv-d.ie.nutsurv.eocng.org',
    'deploy@nutsurv-e.ie.nutsurv.eocng.org',
    'deploy@nutsurv-f.ie.nutsurv.eocng.org',
    'deploy@bigbuilder.eocng.org',
]

env.roledefs = {
    'dev': ['deploy@nutsurv-d.ie.nutsurv.eocng.org', ],
    'staging': ['deploy@nutsurv-e.ie.nutsurv.eocng.org'],
    'production': ['deploy@nutsurv-f.ie.nutsurv.eocng.org'],
    'build': ['ubuntu@bigbuilder.eocng.org'],
}


def echo():
    run('ls /')

def ensure_docker_compose():
    sudo('which docker-compose || pip install docker-compose')

@roles('build')
def build_dockerimage(branch_or_tag='develop'):

    with cd('~/build_setup/'):
        run('./update_env.sh')

    with cd('/home/ubuntu/build_setup/dockersetup/projects/nutsurv'):
        run('BRANCH={} ./run_build.sh'.format(branch_or_tag))
        run('docker push docker-registry.eocng.org/ehealthafrica/nutsurv:{}'.format(
            branch_or_tag))

@roles('dev', 'staging', 'production')
def deploy(branch_or_tag=None, do_stop=True):

    if env.host_string == 'ubuntu@nutsurv-dev.eocng.org':
        if branch_or_tag is None:
            branch_or_tag = 'develop'

    else:
        assert branch_or_tag, "Please specify a tag"

    run('docker pull docker-registry.eocng.org/ehealthafrica/nutsurv:{}'.format(
        branch_or_tag))

    if do_stop is True:
        stop_result = run('docker stop nutsurvdeploy_web_1', warn_only=True)

        if (stop_result
                and (stop_result != 'nutsurvdeploy_web_1')
                and ('no such' not in stop_result.lower())):
            assert False, stop_result

    run('test -d ~/nutsurv_deploy/ || mkdir ~/nutsurv_deploy/')
    ensure_docker_compose()
    upload_template(
        'docker-compose-deploy.yml.template',
        '~/nutsurv_deploy/docker-compose-deploy.yml',
        context={'branch_or_tag': branch_or_tag, }
    )


@roles('dev', 'staging', 'production')
def up():

    run('test -f ~/nutsurv_deploy/configuration.py')
    run('test -f ~/nutsurv_deploy/certs/cert.pem')
    run('test -f ~/nutsurv_deploy/certs/key.pem')

    ensure_docker_compose()
    with cd('~/nutsurv_deploy'):
        run('docker-compose -f ~/nutsurv_deploy/docker-compose-deploy.yml up -d web')

@roles('dev', 'staging', 'production')
def migrate():
    ensure_docker_compose()
    with cd('~/nutsurv_deploy'):
        run('docker-compose -f ~/nutsurv_deploy/docker-compose-deploy.yml run web python /opt/nutsurv/nutsurv/manage.py migrate')
        run('docker-compose -f ~/nutsurv_deploy/docker-compose-deploy.yml run web python /opt/nutsurv/nutsurv/manage.py createcachetable')

