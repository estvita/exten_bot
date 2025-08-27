import os
import psycopg2
from celery import shared_task
from opensipscli import cli
from opensipscli.args import OpenSIPSCLIArgs
from django.conf import settings

def execute_opensips_command(command_list):
    """Execute command through OpenSIPS CLI """
    config_path = getattr(settings, 'OPENSIPS_CLI_CONF', '/etc/opensips/opensips-cli.cfg')
    os.environ['OPENSIPS_CLI_CONF'] = config_path
    
    my_args = OpenSIPSCLIArgs(command=command_list, config=config_path)
    opensipscli = cli.OpenSIPSCLI(options=my_args)
    ret_code = opensipscli.cmdloop()
    return ret_code

@shared_task(bind=True)
def manage_sip_user(self, action, bot_id, domain, password=None):
    command_list = ["user", action, f"{bot_id}@{domain}", password]
    ret_code = execute_opensips_command(command_list)
    if ret_code is not True:
        raise RuntimeError(f"OpenSIPSCLI code {ret_code}")
    return True

@shared_task(bind=True)
def manage_registrant(self, action, username, domain, password=None):
    """
    Manage registrant records in the OpenSIPS database
    action: 'add' or 'delete'
    """
    try:
        # Connect to the OpenSIPS database
        conn = psycopg2.connect(settings.OPENSIPS_DB_URL)
        cursor = conn.cursor()
        
        if action == 'add':
            # Add record to the registrant table
            cursor.execute("""
                INSERT INTO registrant (registrar, aor, username, password, binding_uri, state, expiry)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                f"sip:{domain}",
                f"sip:{username}@{domain}",
                username,
                password,
                f"sip:{username}@{domain}",
                0,
                3600
            ))
            print(f"INFO: Successfully added registrant {username}@{domain}")
            
        elif action == 'delete':
            # Delete record from the registrant table
            cursor.execute("""
                DELETE FROM registrant 
                WHERE username = %s AND registrar = %s
            """, (username, f"sip:{domain}"))
            print(f"INFO: Successfully deleted registrant {username}@{domain}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Reload registrations through OpenSIPS CLI
        try:
            command_list = ["mi", "reg_reload"]
            ret_code = execute_opensips_command(command_list)
            print(f"INFO: reg_reload result for {username}@{domain}: {ret_code}")
                
        except Exception as e:
            print(f"WARNING: Failed to execute reg_reload command: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to manage registrant {username}@{domain}: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise RuntimeError(f"Registrant management failed: {str(e)}")
