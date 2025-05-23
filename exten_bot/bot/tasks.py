from celery import shared_task
from opensipscli import cli
from opensipscli.args import OpenSIPSCLIArgs


@shared_task(bind=True)
def manage_sip_user(self, action, bot_id, domain, password=None):
    command_list = ["user", action, f"{bot_id}@{domain}", password]
    my_args = OpenSIPSCLIArgs(command=command_list)
    opensipscli = cli.OpenSIPSCLI(options=my_args)
    ret_code = opensipscli.cmdloop()
    if ret_code is not True:
        raise RuntimeError(f"OpenSIPSCLI code {ret_code}")
    return True
