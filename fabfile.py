from fabric.api import hosts, roles, env, run, cd
from fabric.contrib.files import upload_template

env.hosts = [
  'ubuntu@nutsurv-dev.eocng.org',
  'ubuntu@nutsurv-staging.eocng.org',
  'ubuntu@nutsurv.eocng.org',
  'ubuntu@bigbuilder.eocng.org',
]

env.roledefs = {
    'dev': ['ubuntu@nutsurv-dev.eocng.org',],
    'staging': ['ubuntu@nutsurv-staging.eocng.org'],
    'production': ['ubuntu@nutsurv.eocng.org'],
    'build': ['ubuntu@bigbuilder.eocng.org'],
}

def echo():
    run('ls /')

@roles('build')
def build_dockerimage(branch_or_tag='develop'):

    with cd('~/build_setup/'):
      run('./update_env.sh')

    with cd('/home/ubuntu/build_setup/dockersetup/projects/nutsurv'):
      run('BRANCH={} ./run_build.sh'.format(branch_or_tag))
      run('docker push docker-registry.eocng.org/ehealthafrica/nutsurv:{}'.format(
        branch_or_tag))

@roles('dev')
def deploy(branch_or_tag=None):

    if env.host_string == 'ubuntu@nutsurv-dev.eocng.org':
        if branch_or_tag is None:
          branch_or_tag = 'develop'

    else:
        assert branch_or_tag.startswith('v'), "You can only deploy tags in this environment"

    run('docker pull docker-registry.eocng.org/ehealthafrica/nutsurv:{}'.format(
        branch_or_tag))

    run('docker stop nutsurvdeploy_web_1')

    upload_template(
        'docker-compose-deploy.yml.template',
        '~/nutsurv_deploy/docker-compose-deploy.yml',
        context={'branch_or_tag':branch_or_tag,}
    )

    with cd('~/nutsurv_deploy'):
        run('docker-compose -f ~/nutsurv_deploy/docker-compose-deploy.yml up -d web')

