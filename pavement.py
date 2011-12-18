from paver.easy import *

@task
def test():
    sh('nosetests --with-gae')
    
@task
def deploy():
    sh('appcfg.py update .')
