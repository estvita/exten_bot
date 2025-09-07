import os
import MySQLdb
import subprocess
from urllib.parse import urlparse
from celery import shared_task
from django.conf import settings

def parse_mysql_url(mysql_url):
    # Пример: mysql://user:pass@host:3306/db
    res = urlparse(mysql_url)
    db_user = res.username
    db_pass = res.password
    db_host = res.hostname
    db_port = res.port or 3306
    db_name = res.path.lstrip('/')
    return db_host, db_user, db_pass, db_name, db_port

def execute_opensips_command(command_list):
    cmd = ['opensips-cli', '-x'] + command_list
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip() or result.stderr.strip() or ''

@shared_task(bind=True)
def manage_sip_user(self, action, bot_id, domain, password=None):
    command_list = ["user", action, f"{bot_id}@{domain}"]
    if password is not None:
        command_list.append(password)
    execute_opensips_command(command_list)
    return True

@shared_task(bind=True)
def manage_registrant(self, action, username, domain, password=None):
    """
    Manage registrant records in the OpenSIPS database
    action: 'add' or 'delete'
    """
    try:
        db_url = settings.OPENSIPS_DB_URL
        db_host, db_user, db_pass, db_name, db_port = parse_mysql_url(db_url)
        conn = MySQLdb.connect(
            host=db_host,
            user=db_user,
            passwd=db_pass,
            db=db_name,
            port=int(db_port),
            charset='utf8mb4'
        )
        cursor = conn.cursor()

        if action == 'add':
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
            cursor.execute("""
                DELETE FROM registrant 
                WHERE username = %s AND registrar = %s
            """, (username, f"sip:{domain}"))
            print(f"INFO: Successfully deleted registrant {username}@{domain}")

        conn.commit()
        cursor.close()
        conn.close()

        try:
            command_list = ["mi", "reg_reload"]
            execute_opensips_command(command_list)

        except Exception as e:
            print(f"WARNING: Failed to execute reg_reload command: {str(e)}")

        return True

    except Exception as e:
        print(f"ERROR: Failed to manage registrant {username}@{domain}: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise RuntimeError(f"Registrant management failed: {str(e)}")