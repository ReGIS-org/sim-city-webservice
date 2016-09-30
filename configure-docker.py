#!/usr/bin/env python

from __future__ import print_function

from simcityweb.cli import dialog, confirm, new_or_overwrite, choice_dialog
import pystache


def configure():
    ''' Configures the SIM-CITY webservice interactively. '''
    renderer = pystache.Renderer()

    webconfig = {}
    if confirm("Configure CouchDB"):
        webconfig['couchdb-url'] = dialog("CouchDB external URL")
        couchdb_passwd = ""
        while len(couchdb_passwd) < 8:
            couchdb_passwd = dialog(
                "CouchDB admin password (min. 8 characters)")

        couchdb_config = {'admin': 'admin', 'password': couchdb_passwd}

        if new_or_overwrite('docker/couchdb/local.ini'):
            with open('docker/couchdb/local.ini', 'w') as f:
                f.write(renderer.render_path(
                        'docker/couchdb/local.ini.template', couchdb_config
                        ))
                print(" => saved admins to docker/couchdb/local.ini")
            with open('couchdb.env', 'w') as f:
                f.write(renderer.render_path(
                        'docker/couchdb/couchdb.env.template', couchdb_config
                        ))
                print(" => saved CouchDB environment variables to "
                      "couchdb.env")

    # if confirm("Configure Osmium SSH"):
    #     key_path = 'docker/osmium/ssh_key'
    #     config_path = 'docker/osmium/ssh_config'
    #     known_hosts_path = 'docker/osmium/ssh_known_hosts'
    #     permissionUserRead = stat.S_IRUSR | stat.S_IWUSR
    #     if confirm("Generate SSH keys"):
    #         if new_or_overwrite(key_path):
    #             if os.path.exists(key_path):
    #                 os.remove(key_path)
    #             if os.path.exists(key_path + '.pub'):
    #                 os.remove(key_path + '.pub')
    #             subprocess.call(['ssh-keygen', '-N', '', '-f', key_path])
    #             os.chmod(key_path, permissionUserRead)
    #     elif new_or_overwrite(key_path, "Copy SSH keys"):
    #         if not os.path.exists(key_path):
    #             print("Copying SSH keys instead...")
    #         copied = False
    #         while not copied:
    #             try:
    #                 path = os.path.expanduser(
    #                     dialog("Path to SSH keys", "~/.ssh/id_rsa"))
    #                 shutil.copy(path, key_path)
    #                 os.chmod(key_path, permissionUserRead)
    #                 shutil.copy(path + '.pub', key_path + '.pub')
    #                 copied = True
    #             except IOError:
    #                 print("Cannot find file {} or {}.pub".format(path, path))
    #         print(" => copied {}(.pub) to docker/osmium/ssh_key(.pub)"
    #               .format(path))
    #     if confirm("Copy SSH config"):
    #         copied = False
    #         while not copied:
    #             try:
    #                 path = os.path.expanduser(
    #                     dialog("Path to SSH config", "~/.ssh/config"))
    #                 shutil.copy(path, config_path)
    #                 print(" => copied {} to docker/osmium/ssh_config"
    #                       .format(path))
    #                 copied = True
    #             except IOError:
    #                 print("Cannot find file {}".format(path))
    #     elif new_or_overwrite(config_path, "Clear SSH config"):
    #         open(config_path, 'w').close()
    #         print(" => cleared docker/osmium/ssh_config")
    #     if confirm("Copy SSH known hosts file"):
    #         copied = False
    #         while not copied:
    #             try:
    #                 path = os.path.expanduser(dialog(
    #                     "Path to SSH known hosts file",
    #                     "~/.ssh/known_hosts"))
    #                 shutil.copy(path, known_hosts_path)
    #                 copied = True
    #             except IOError:
    #                 print("Cannot find file {}".format(path))
    #     elif new_or_overwrite(known_hosts_path,
    #                           "Clear SSH known hosts"):
    #         open(known_hosts_path, 'w').close()

    xenon_config = {'launchers': []}
    # if confirm("Configure Osmium"):
    #     if new_or_overwrite('docker/osmium/joblauncher.yml'):
    #         while confirm("Configure new Osmium launcher"):
    #             launcher = {}
    #             launcher['name'] = dialog("Launcher name")
    #             launcher['scheduler'] = choice_dialog(
    #                 "Scheduler",
    #                 ['local', 'ssh', 'torque', 'slurm', 'gridengine'])
    #             launcher['scheduler-location'] = dialog(
    #                 "Scheduler location (user@host:port)")
    #             launcher['queue'] = dialog("Scheduler queue")
    #             launcher['sandbox'] = choice_dialog(
    #                 "Filesystem scheme", ['local', 'ssh', 'ftp', 'gridftp'],
    #                 default_response='ssh')
    #             launcher['sandbox-location'] = dialog(
    #                 "Filesystem location",
    #                 launcher['scheduler-location'])
    #             osmium_config['launchers'].append(launcher)

    #         try:
    #             osmium_config['default-launcher'] = choice_dialog(
    #                 'Default launcher',
    #                 [l['name'] for l in osmium_config['launchers']],
    #                 default_response=osmium_config['launchers'][0]['name'])
    #         except IndexError:
    #             osmium_config['default-launcher'] = 'none'

    #         with open('docker/osmium/joblauncher.yml', 'w') as f:
    #             f.write(renderer.render_path(
    #                 'docker/osmium/joblauncher.yml.template', osmium_config))
    #             print(" => saved Osmium config to "
    #                   "docker/osmium/joblauncher.yml")

    if confirm("Configure webservice"):
        if new_or_overwrite('docker/webservice/config.ini'):
            if 'couchdb-url' not in webconfig:
                webconfig['couchdb-url'] = dialog("CouchDB external URL")

            webconfig['user'] = dialog('CouchDB username')
            webconfig['password'] = dialog('CouchDB password')
            if confirm('Verify CouchDB SSL certificate'):
                webconfig['ssl-verify'] = 'true'
            else:
                webconfig['ssl-verify'] = 'false'

            webconfig['xenon-hosts'] = []
            idx = 0
            while confirm('Configure new Xenon host'):
                xenon_host = {}
                try:
                    # Schema defines what submission system the host uses.
                    xenon_host['name'] = dialog(
                        'Launcher name',
                        xenon_config['launchers'][idx]['name'])
                    idx += 1
                except IndexError:
                    xenon_host['name'] = dialog('Launcher name')
                xenon_host['script'] = dialog('Script to run', 'run.sh')
                xenon_host['host'] = dialog(
                    'Xenon queue url (including schema)')
                xenon_host['path'] = dialog(
                    'Path of runtime script', '~/sim-city-client/scripts')
                xenon_host['max_time'] = dialog(
                    'Maximum runtime (in minutes)', '60')
                xenon_host['ignore_version'] = confirm(
                    'Ignore the queue-system version?', False)
                webconfig['xenon-hosts'].append(xenon_host)

            webconfig['ssh-hosts'] = []
            while confirm('Configure new SSH host', default_response=False):
                ssh_host = {}
                ssh_host['name'] = dialog('Name')
                ssh_host['script'] = dialog('Submission script file')
                ssh_host['path'] = dialog(
                    'Path of submission script', '~/sim-city-client/scripts')
                ssh_host['host'] = dialog('Host (user@host)', ssh_host['name'])
                webconfig['ssh-hosts'].append(ssh_host)

            all_hosts = [h['name'] for h in (webconfig['xenon-hosts'] +
                                             webconfig['ssh-hosts'])]
            webconfig['default-host'] = choice_dialog(
                'Default host', all_hosts,
                default_response=all_hosts[0])

            with open('docker/webservice/config.ini', 'w') as f:
                f.write(renderer.render_path(
                    'docker/webservice/config.ini.template', webconfig))
                print(" => saved webservice config to "
                      "docker/webservice/config.ini")

if __name__ == '__main__':
    configure()
